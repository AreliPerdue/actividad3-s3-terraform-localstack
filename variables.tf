variable "region" {
  description = "Región simulada"
  type        = string
  default     = "us-east-1"
}

variable "localstack_endpoint" {
  description = "Endpoint local de LocalStack"
  type        = string
  default     = "http://localhost:4566"

  validation {
    condition     = can(regex("^http://(localhost|127\\.0\\.0\\.1):4566$", var.localstack_endpoint))
    error_message = "El endpoint debe ser LocalStack en localhost:4566, nunca AWS real."
  }
}

variable "bucket_name" {
  description = "Nombre del bucket S3"
  type        = string
  default     = "actividad3-seguro-local"
}
