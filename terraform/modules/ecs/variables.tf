variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "app_sg_id" {
  description = "Security group ID for the application"
  type        = string
}

variable "alb_sg_id" {
  description = "Security group ID for the ALB"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "container_image_tag" {
  description = "Tag for the container image to deploy"
  type        = string
  default     = "latest"
}

variable "neo4j_uri" {
  description = "URI for Neo4j database"
  type        = string
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

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
} 