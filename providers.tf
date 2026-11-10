terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

# Provider AWS apuntando SOLO a LocalStack.
# Credenciales ficticias + endpoint local: nada llega a AWS real.
provider "aws" {
  region     = var.region
  access_key = "test"
  secret_key = "test"

  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  # LocalStack atiende S3 con rutas tipo http://localhost:4566/<bucket>
  s3_use_path_style = true

  endpoints {
    s3 = var.localstack_endpoint
  }
}
