output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "api_endpoint" {
  description = "The endpoint URL for the API"
  value       = module.ecs.api_endpoint
}

output "frontend_url" {
  description = "The URL for the frontend application"
  value       = module.frontend.cloudfront_domain_name
}

output "neo4j_endpoint" {
  description = "The endpoint for the Neo4j database"
  value       = var.use_neo4j_aura ? var.neo4j_aura_uri : (length(module.neo4j) > 0 ? "bolt://${module.neo4j[0].private_dns}:7687" : "No Neo4j deployed")
  sensitive   = true
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "cloudwatch_dashboard_url" {
  description = "URL for the CloudWatch dashboard"
  value       = module.monitoring.dashboard_url
} 