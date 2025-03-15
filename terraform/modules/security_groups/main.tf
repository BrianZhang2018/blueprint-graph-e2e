# Security group for the Application Load Balancer
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Security group for the ALB"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic from anywhere"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS traffic from anywhere"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-alb-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# Security group for the API application
resource "aws_security_group" "app" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Security group for the API application"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow traffic from ALB to API"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# Security group for Neo4j
resource "aws_security_group" "neo4j" {
  name        = "${var.project_name}-${var.environment}-neo4j-sg"
  description = "Security group for Neo4j database"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 7687
    to_port         = 7687
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Allow Bolt protocol traffic from API"
  }
  
  ingress {
    from_port       = 7474
    to_port         = 7474
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Allow HTTP traffic from API"
  }
  
  ingress {
    from_port       = 7473
    to_port         = 7473
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Allow HTTPS traffic from API"
  }
  
  # Allow Neo4j instances to communicate with each other for clustering
  ingress {
    from_port       = 5000
    to_port         = 6000
    protocol        = "tcp"
    self            = true
    description     = "Allow Neo4j cluster communication"
  }
  
  # SSH access for management
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # In production, restrict this to your management IPs
    description = "Allow SSH access"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-neo4j-sg"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
} 