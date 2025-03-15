variable "domain_name" {
  description = "Domain name for the application (e.g., blueprintgraph.example.com)"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "api_endpoint" {
  description = "The endpoint URL for the API"
  type        = string
} 