# Actividad 3 · Fase 1 — Bucket S3 cifrado y sin acceso público, definido como código.
# Todo apunta a LocalStack (http://localhost:4566); nada llega a AWS real.

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region                      = var.region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    s3  = var.endpoint
    iam = var.endpoint
    sts = var.endpoint
  }
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "endpoint" {
  type    = string
  default = "http://localhost:4566"
  validation {
    condition     = can(regex("^http://(localhost|127\\.0\\.0\\.1):4566$", var.endpoint))
    error_message = "Solo se permite LocalStack en localhost:4566."
  }
}

variable "bucket" {
  type    = string
  default = "actividad3-reportes-cifrados"
}

variable "cuenta" {
  description = "ID de cuenta de LocalStack (en AWS real sería la cuenta propia)"
  type        = string
  default     = "000000000000"
}

# 1) Bucket
resource "aws_s3_bucket" "reportes" {
  bucket        = var.bucket
  force_destroy = true
  tags = {
    Actividad     = "3"
    Clasificacion = "interna"
  }
}

# 2) Versionado: conserva versiones anteriores si un objeto se sobrescribe o borra
resource "aws_s3_bucket_versioning" "reportes" {
  bucket = aws_s3_bucket.reportes.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 3) Cifrado en reposo AES-256 (SSE-S3) para todo objeto nuevo
resource "aws_s3_bucket_server_side_encryption_configuration" "reportes" {
  bucket = aws_s3_bucket.reportes.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4) Bloqueo de acceso público: las cuatro opciones activadas
resource "aws_s3_bucket_public_access_block" "reportes" {
  bucket                  = aws_s3_bucket.reportes.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

# 5) Política explícita del bucket: niega todo acceso que no venga de la cuenta
#    (incluye solicitudes anónimas) y toda solicitud sin cifrado en tránsito.
resource "aws_s3_bucket_policy" "reportes" {
  bucket = aws_s3_bucket.reportes.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "NegarAccesoPublicoYExterno"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.reportes.arn, "${aws_s3_bucket.reportes.arn}/*"]
        Condition = { StringNotEquals = { "aws:PrincipalAccount" = var.cuenta } }
      },
      {
        Sid       = "NegarSolicitudesSinHTTPS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.reportes.arn, "${aws_s3_bucket.reportes.arn}/*"]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      }
    ]
  })
  # El bloqueo público debe existir antes de la política
  depends_on = [aws_s3_bucket_public_access_block.reportes]
}

output "bucket" {
  value = aws_s3_bucket.reportes.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.reportes.arn
}
