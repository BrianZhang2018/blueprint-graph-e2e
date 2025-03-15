terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # This will be configured in environments/<env>/backend.tf
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  vpc_name       = "${var.project_name}-${var.environment}"
  vpc_cidr       = var.vpc_cidr
  azs            = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  environment    = var.environment
  project_name   = var.project_name
}

# Security Groups
module "security_groups" {
  source = "./modules/security_groups"
  
  vpc_id        = module.vpc.vpc_id
  environment   = var.environment
  project_name  = var.project_name
}

# EC2 instances for Neo4j (if using self-managed)
module "neo4j" {
  source = "./modules/neo4j"
  
  count         = var.use_neo4j_aura ? 0 : 1
  
  vpc_id        = module.vpc.vpc_id
  subnet_ids    = module.vpc.private_subnet_ids
  sg_id         = module.security_groups.neo4j_sg_id
  key_name      = var.ec2_key_name
  instance_type = var.neo4j_instance_type
  cluster_size  = var.neo4j_cluster_size
  
  environment   = var.environment
  project_name  = var.project_name
}

# ECR Repository for Docker images
module "ecr" {
  source = "./modules/ecr"
  
  repository_name = "${var.project_name}-${var.environment}"
}

# ECS Cluster and Services for FastAPI backend
module "ecs" {
  source = "./modules/ecs"
  
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  public_subnet_ids     = module.vpc.public_subnet_ids
  app_sg_id             = module.security_groups.app_sg_id
  alb_sg_id             = module.security_groups.alb_sg_id
  
  ecr_repository_url    = module.ecr.repository_url
  container_image_tag   = var.container_image_tag
  
  neo4j_uri             = var.use_neo4j_aura ? var.neo4j_aura_uri : "bolt://${module.neo4j[0].private_dns}:7687"
  neo4j_user            = var.neo4j_user
  neo4j_password        = var.neo4j_password
  
  api_container_cpu     = var.api_container_cpu
  api_container_memory  = var.api_container_memory
  api_desired_count     = var.api_desired_count
  
  environment           = var.environment
  project_name          = var.project_name
}

# S3 and CloudFront for React frontend
module "frontend" {
  source = "./modules/frontend"
  
  domain_name     = var.domain_name
  environment     = var.environment
  project_name    = var.project_name
  api_endpoint    = module.ecs.api_endpoint
}

# CloudWatch Alarms and Dashboards
module "monitoring" {
  source = "./modules/monitoring"
  
  ecs_cluster_name     = module.ecs.cluster_name
  ecs_service_name     = module.ecs.service_name
  api_target_group_arn = module.ecs.target_group_arn
  
  environment          = var.environment
  project_name         = var.project_name
} 