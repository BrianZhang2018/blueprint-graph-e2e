# Get the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM role for EC2 instances
resource "aws_iam_role" "neo4j" {
  name = "${var.project_name}-${var.environment}-neo4j-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-neo4j-role"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# IAM instance profile
resource "aws_iam_instance_profile" "neo4j" {
  name = "${var.project_name}-${var.environment}-neo4j-profile"
  role = aws_iam_role.neo4j.name
}

# Policy for S3 access (for backups)
resource "aws_iam_policy" "neo4j_s3" {
  name        = "${var.project_name}-${var.environment}-neo4j-s3-policy"
  description = "Policy for Neo4j to access S3 for backups"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::${var.project_name}-${var.environment}-neo4j-backup",
          "arn:aws:s3:::${var.project_name}-${var.environment}-neo4j-backup/*"
        ]
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "neo4j_s3" {
  role       = aws_iam_role.neo4j.name
  policy_arn = aws_iam_policy.neo4j_s3.arn
}

# S3 bucket for Neo4j backups
resource "aws_s3_bucket" "neo4j_backup" {
  bucket = "${var.project_name}-${var.environment}-neo4j-backup"
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-neo4j-backup"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# Neo4j core instances
resource "aws_instance" "neo4j_core" {
  count         = var.cluster_size
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  subnet_id     = var.subnet_ids[count.index % length(var.subnet_ids)]
  
  vpc_security_group_ids      = [var.sg_id]
  key_name                    = var.key_name
  iam_instance_profile        = aws_iam_instance_profile.neo4j.name
  associate_public_ip_address = false
  
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 100
    delete_on_termination = true
    encrypted             = true
  }
  
  ebs_block_device {
    device_name           = "/dev/sdf"
    volume_type           = "gp3"
    volume_size           = 200
    delete_on_termination = true
    encrypted             = true
  }
  
  user_data = <<-EOF
    #!/bin/bash
    # Install necessary packages
    yum update -y
    yum install -y java-11-amazon-corretto wget

    # Add Neo4j repository
    rpm --import https://debian.neo4j.com/neotechnology.gpg.key
    cat <<REPO > /etc/yum.repos.d/neo4j.repo
    [neo4j]
    name=Neo4j RPM Repository
    baseurl=https://yum.neo4j.com/stable/5
    enabled=1
    gpgcheck=1
    REPO

    # Install Neo4j Enterprise
    yum install -y neo4j-enterprise

    # Configure Neo4j
    cat <<CONF > /etc/neo4j/neo4j.conf
    # Network configuration
    dbms.default_listen_address=0.0.0.0
    dbms.default_advertised_address=$(hostname -i)
    dbms.connector.bolt.enabled=true
    dbms.connector.bolt.listen_address=0.0.0.0:7687
    dbms.connector.http.enabled=true
    dbms.connector.http.listen_address=0.0.0.0:7474
    dbms.connector.https.enabled=true
    dbms.connector.https.listen_address=0.0.0.0:7473

    # Causal Clustering configuration
    dbms.mode=CORE
    causal_clustering.minimum_core_cluster_size_at_formation=3
    causal_clustering.minimum_core_cluster_size_at_runtime=2
    causal_clustering.initial_discovery_members=${join(",", formatlist("%s:5000", aws_instance.neo4j_core[*].private_ip))}
    causal_clustering.discovery_listen_address=0.0.0.0:5000
    causal_clustering.transaction_listen_address=0.0.0.0:6000
    causal_clustering.raft_listen_address=0.0.0.0:7000

    # Memory configuration
    dbms.memory.heap.initial_size=4G
    dbms.memory.heap.max_size=8G
    dbms.memory.pagecache.size=4G

    # Security
    dbms.security.auth_enabled=true
    dbms.security.procedures.unrestricted=apoc.*
    CONF

    # Set initial password
    neo4j-admin set-initial-password ${var.neo4j_password}

    # Install APOC plugin
    mkdir -p /var/lib/neo4j/plugins
    wget -P /var/lib/neo4j/plugins https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/5.13.0/apoc-5.13.0-core.jar

    # Start Neo4j
    systemctl enable neo4j
    systemctl start neo4j
  EOF
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-neo4j-core-${count.index}"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
    Role        = "neo4j-core"
  }
}

# CloudWatch alarm for Neo4j instance status
resource "aws_cloudwatch_metric_alarm" "neo4j_status" {
  count               = var.cluster_size
  alarm_name          = "${var.project_name}-${var.environment}-neo4j-status-${count.index}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1
  alarm_description   = "This alarm monitors Neo4j instance status"
  
  dimensions = {
    InstanceId = aws_instance.neo4j_core[count.index].id
  }
  
  alarm_actions = [aws_sns_topic.neo4j_alerts.arn]
  ok_actions    = [aws_sns_topic.neo4j_alerts.arn]
}

# SNS topic for Neo4j alerts
resource "aws_sns_topic" "neo4j_alerts" {
  name = "${var.project_name}-${var.environment}-neo4j-alerts"
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-neo4j-alerts"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
} 