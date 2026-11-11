# Actividad 3 · Fase 4 — Rol de mínimo privilegio: solo puede leer (s3:GetObject)
# los objetos de reportes/ del bucket de la Fase 1. Nada de listar, escribir ni borrar.

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
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    iam = "http://localhost:4566"
    sts = "http://localhost:4566"
  }
}

# Rol que usará el contenedor de la API (ECS) y que la cuenta puede asumir para pruebas
resource "aws_iam_role" "lector" {
  name               = "rol-lector-reportes"
  description        = "Solo lectura de reportes/ en actividad3-reportes-cifrados"
  assume_role_policy = file("${path.module}/confianza-rol.json")
}

# Política administrada con una sola acción y un solo recurso
resource "aws_iam_policy" "solo_lectura" {
  name        = "politica-solo-lectura-reportes"
  description = "Permite unicamente s3:GetObject sobre reportes/*"
  policy      = file("${path.module}/politica-lector.json")
}

# La política se adjunta exclusivamente a este rol
resource "aws_iam_role_policy_attachment" "lector" {
  role       = aws_iam_role.lector.name
  policy_arn = aws_iam_policy.solo_lectura.arn
}

output "rol_arn" {
  value = aws_iam_role.lector.arn
}

output "politica_arn" {
  value = aws_iam_policy.solo_lectura.arn
}
