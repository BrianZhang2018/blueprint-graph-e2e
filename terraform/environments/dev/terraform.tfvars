aws_region = "us-east-1"
environment = "dev"
project_name = "blueprintgraph"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnet_cidrs = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

# Neo4j Configuration
use_neo4j_aura = false  # Set to true if using Neo4j Aura
neo4j_instance_type = "r5.xlarge"
neo4j_cluster_size = 3
ec2_key_name = "blueprintgraph-dev"  # Replace with your EC2 key pair name

# Application Configuration
container_image_tag = "latest"
api_container_cpu = 1024  # 1 vCPU
api_container_memory = 2048  # 2 GB
api_desired_count = 2

# Frontend Configuration
domain_name = ""  # Leave empty for CloudFront default domain 