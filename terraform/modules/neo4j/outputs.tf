output "private_ips" {
  description = "Private IP addresses of Neo4j instances"
  value       = aws_instance.neo4j_core[*].private_ip
}

output "private_dns" {
  description = "Private DNS names of Neo4j instances"
  value       = aws_instance.neo4j_core[*].private_dns
}

output "instance_ids" {
  description = "IDs of Neo4j instances"
  value       = aws_instance.neo4j_core[*].id
}

output "backup_bucket" {
  description = "S3 bucket for Neo4j backups"
  value       = aws_s3_bucket.neo4j_backup.bucket
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for Neo4j alerts"
  value       = aws_sns_topic.neo4j_alerts.arn
} 