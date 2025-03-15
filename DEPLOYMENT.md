# Blueprint Graph Deployment Guide

This document provides instructions for deploying the Blueprint Graph application to AWS using Terraform.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Terraform installed (version 1.0.0 or later)
- Docker installed (for building and pushing container images)

## Deployment Architecture

The Blueprint Graph application is deployed with the following components:

1. **Database Layer**: Neo4j graph database

   - Self-managed Neo4j cluster on EC2 instances
   - Option to use Neo4j Aura (managed service)

2. **Application Layer**: FastAPI backend

   - Containerized application running on ECS Fargate
   - Auto-scaling based on CPU and memory utilization
   - Load balancing with Application Load Balancer

3. **Frontend Layer**: React UI

   - Static assets hosted on S3
   - Content delivery with CloudFront

4. **Monitoring**: CloudWatch dashboards and alarms

## Deployment Steps

### 1. Configure Environment Variables

Set up your AWS credentials:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 2. Configure Environment Settings

Review and update the environment configuration in `terraform/environments/dev/terraform.tfvars`:

- Update `aws_region` if needed
- Set `use_neo4j_aura` to `true` if you want to use Neo4j Aura instead of self-managed Neo4j
- If using Neo4j Aura, set `neo4j_aura_uri` to your Aura connection string
- Update `ec2_key_name` to your EC2 key pair name
- Adjust instance types and counts as needed

### 3. Deploy the Infrastructure

Use the deployment script to deploy the infrastructure:

```bash
./deploy.sh dev
```

This will:

- Create the necessary S3 bucket and DynamoDB table for Terraform state
- Build and push the Docker image for the FastAPI backend
- Deploy the infrastructure using Terraform

### 4. Upload Frontend Assets

After the infrastructure is deployed, build and upload the React frontend:

```bash
cd ui
npm run build
aws s3 sync build/ s3://blueprintgraph-dev-frontend/
```

### 5. Verify Deployment

After deployment, the script will output:

- API Endpoint URL
- Frontend URL (CloudFront distribution domain)

Verify that both endpoints are accessible.

## Updating the Deployment

To update the deployment:

1. Make your changes to the application code
2. Run the deployment script again:

```bash
./deploy.sh dev
```

## Cleaning Up

To destroy the infrastructure when no longer needed:

```bash
./deploy.sh dev destroy
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Issues**:

   - Check security group rules
   - Verify Neo4j password in SSM Parameter Store

2. **ECS Service Deployment Failures**:

   - Check CloudWatch Logs for container errors
   - Verify container health check is passing

3. **CloudFront Distribution Issues**:
   - Check S3 bucket policy
   - Verify CloudFront origin access control settings

### Logs and Monitoring

- ECS container logs are available in CloudWatch Logs
- CloudWatch dashboard provides metrics for the application
- CloudWatch alarms will trigger notifications for critical issues

## Security Considerations

- All sensitive information (e.g., Neo4j password) is stored in SSM Parameter Store
- All traffic between components is encrypted
- Security groups restrict access to only necessary ports
- S3 bucket for frontend assets is not publicly accessible (accessed via CloudFront)
