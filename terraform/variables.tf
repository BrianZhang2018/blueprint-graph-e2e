variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "blueprintgraph"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# Neo4j Configuration
variable "use_neo4j_aura" {
  description = "Whether to use Neo4j Aura (true) or self-managed Neo4j (false)"
  type        = bool
  default     = false
}

variable "neo4j_aura_uri" {
  description = "URI for Neo4j Aura (if using Aura)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "neo4j_user" {
  description = "Username for Neo4j database"
  type        = string
  default     = "neo4j"
}

variable "neo4j_password" {
  description = "Password for Neo4j database"
  type        = string
  sensitive   = true
}

variable "neo4j_instance_type" {
  description = "EC2 instance type for Neo4j servers (if self-managed)"
  type        = string
  default     = "r5.xlarge"
}

variable "neo4j_cluster_size" {
  description = "Number of nodes in Neo4j cluster (if self-managed)"
  type        = number
  default     = 3
}

variable "ec2_key_name" {
  description = "Name of EC2 key pair for SSH access to Neo4j instances"
  type        = string
  default     = ""
}

# Application Configuration
variable "container_image_tag" {
  description = "Tag for the container image to deploy"
  type        = string
  default     = "latest"
}

variable "api_container_cpu" {
  description = "CPU units for the API container (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "api_container_memory" {
  description = "Memory for the API container in MiB"
  type        = number
  default     = 2048
}

variable "api_desired_count" {
  description = "Desired number of API containers"
  type        = number
  default     = 2
}

# Frontend Configuration
variable "domain_name" {
  description = "Domain name for the application (e.g., blueprintgraph.example.com)"
  type        = string
  default     = ""
} 