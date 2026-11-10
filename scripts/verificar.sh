#!/usr/bin/env bash
# Comprueba con AWS CLI lo que quedó configurado en LocalStack.
# Todas las llamadas usan credenciales ficticias y el endpoint local.
set -u

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
EP="http://localhost:4566"
BUCKET="${1:-actividad3-seguro-local}"

titulo() { printf '\n== %s ==\n' "$1"; }

titulo "Salud de LocalStack"
curl -s "$EP/_localstack/health"; echo

titulo "Buckets"
aws --endpoint-url "$EP" s3api list-buckets --query 'Buckets[].Name'

titulo "Cifrado"
aws --endpoint-url "$EP" s3api get-bucket-encryption --bucket "$BUCKET"

titulo "Bloqueo de acceso público (4 controles)"
aws --endpoint-url "$EP" s3api get-public-access-block --bucket "$BUCKET"

titulo "Objetos"
aws --endpoint-url "$EP" s3 ls "s3://$BUCKET/"

titulo "Descarga anónima (sin firmar)"
aws --endpoint-url "$EP" --no-sign-request s3 cp "s3://$BUCKET/prueba.txt" - \
  && echo "-> PERMITIDA por LocalStack" || echo "-> DENEGADA"

titulo "Política del bucket"
aws --endpoint-url "$EP" s3api get-bucket-policy --bucket "$BUCKET" 2>&1 || true
