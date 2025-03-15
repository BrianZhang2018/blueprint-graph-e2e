variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for Neo4j instances"
  type        = list(string)
}

variable "sg_id" {
  description = "Security group ID for Neo4j instances"
  type        = string
}

variable "key_name" {
  description = "Name of the EC2 key pair for SSH access"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for Neo4j servers"
  type        = string
  default     = "r5.xlarge"
}

variable "cluster_size" {
  description = "Number of nodes in Neo4j cluster"
  type        = number
  default     = 3
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "neo4j_password" {
  description = "Password for Neo4j database"
  type        = string
  sensitive   = true
  default     = "changeme"  # This should be overridden in a secure way
} 