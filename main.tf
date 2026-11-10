# 1) Bucket S3
resource "aws_s3_bucket" "seguro" {
  bucket        = var.bucket_name
  force_destroy = true # permite "terraform destroy" aunque tenga archivos (solo laboratorio)

  tags = {
    Proyecto = "actividad3"
    Entorno  = "localstack"
  }
}

# 2) Cifrado del lado del servidor SSE-S3 (AES-256)
resource "aws_s3_bucket_server_side_encryption_configuration" "seguro" {
  bucket = aws_s3_bucket.seguro.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 3) Los cuatro controles de bloqueo de acceso público
resource "aws_s3_bucket_public_access_block" "seguro" {
  bucket = aws_s3_bucket.seguro.id

  block_public_acls       = true # rechaza ACL públicas nuevas
  ignore_public_acls      = true # ignora ACL públicas existentes
  block_public_policy     = true # rechaza políticas de bucket públicas
  restrict_public_buckets = true # limita el acceso si ya hay una política pública
}
