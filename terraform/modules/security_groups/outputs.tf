output "alb_sg_id" {
  description = "The ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "app_sg_id" {
  description = "The ID of the application security group"
  value       = aws_security_group.app.id
}

output "neo4j_sg_id" {
  description = "The ID of the Neo4j security group"
  value       = aws_security_group.neo4j.id
} 