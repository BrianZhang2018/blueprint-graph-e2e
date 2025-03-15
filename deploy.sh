#!/bin/bash
set -e

# Check if environment is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <environment> [command]"
  echo "Example: $0 dev plan"
  exit 1
fi

ENV=$1
COMMAND=${2:-apply}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if environment directory exists
if [ ! -d "$SCRIPT_DIR/terraform/environments/$ENV" ]; then
  echo "Environment '$ENV' not found in terraform/environments/"
  exit 1
fi

# Check if AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "AWS credentials not set. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
  exit 1
fi

# Create S3 bucket and DynamoDB table for Terraform state if they don't exist
BUCKET_NAME="blueprintgraph-terraform-state-$ENV"
TABLE_NAME="blueprintgraph-terraform-locks-$ENV"
REGION=$(grep -A 2 'backend "s3"' "$SCRIPT_DIR/terraform/environments/$ENV/backend.tf" | grep region | awk -F'"' '{print $2}')

echo "Checking if Terraform state bucket and DynamoDB table exist..."
if ! aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
  echo "Creating S3 bucket for Terraform state: $BUCKET_NAME"
  aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
  aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled
  aws s3api put-bucket-encryption --bucket "$BUCKET_NAME" --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
fi

if ! aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" 2>/dev/null; then
  echo "Creating DynamoDB table for Terraform state locking: $TABLE_NAME"
  aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region "$REGION"
fi

# Build and push Docker image if needed
if [ "$COMMAND" == "apply" ] || [ "$COMMAND" == "plan" ]; then
  echo "Do you want to build and push a new Docker image? (y/n)"
  read -r BUILD_IMAGE
  
  if [[ "$BUILD_IMAGE" =~ ^[Yy]$ ]]; then
    # Get ECR repository URL
    ECR_REPO=$(grep -A 1 'ecr_repository_url' "$SCRIPT_DIR/terraform/environments/$ENV/terraform.tfvars" | grep '=' | awk -F'=' '{print $2}' | tr -d ' "')
    
    if [ -z "$ECR_REPO" ]; then
      echo "ECR repository URL not found in terraform.tfvars. Using default format."
      ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      ECR_REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/blueprintgraph-$ENV"
    fi
    
    # Build Docker image
    echo "Building Docker image..."
    docker build -t "$ECR_REPO:latest" .
    
    # Login to ECR
    echo "Logging in to ECR..."
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_REPO"
    
    # Push Docker image
    echo "Pushing Docker image to ECR..."
    docker push "$ECR_REPO:latest"
  fi
fi

# Run Terraform
cd "$SCRIPT_DIR/terraform"

echo "Initializing Terraform..."
terraform init -backend-config="environments/$ENV/backend.tf"

echo "Running Terraform $COMMAND..."
terraform $COMMAND -var-file="environments/$ENV/terraform.tfvars"

if [ "$COMMAND" == "apply" ]; then
  echo "Deployment completed successfully!"
  echo "API Endpoint: $(terraform output -raw api_endpoint)"
  echo "Frontend URL: $(terraform output -raw frontend_url)"
fi 