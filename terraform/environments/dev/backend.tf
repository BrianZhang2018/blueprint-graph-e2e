terraform {
  backend "s3" {
    bucket         = "blueprintgraph-terraform-state-dev"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "blueprintgraph-terraform-locks-dev"
    encrypt        = true
  }
} 