#!/usr/bin/env bash
# Ejemplo aplicado de la política: la API asume rol-lector-reportes y lee un reporte.
# Usa el perfil "localstack" (endpoint http://localhost:4566, credenciales ficticias).
set -euo pipefail
B=actividad3-reportes-cifrados
ROL=arn:aws:iam::000000000000:role/rol-lector-reportes
EP=http://localhost:4566

echo "1) Asumir el rol (credenciales temporales de STS)"
read -r AK SK ST EXP < <(aws sts assume-role --profile localstack --role-arn "$ROL" \
  --role-session-name api-reportes --duration-seconds 900 \
  --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken,Expiration]' --output text)
echo "   sesion valida hasta $EXP"

como_rol() { AWS_ACCESS_KEY_ID=$AK AWS_SECRET_ACCESS_KEY=$SK AWS_SESSION_TOKEN=$ST \
  aws --endpoint-url "$EP" --region us-east-1 "$@"; }

echo "2) Identidad con la que se hacen las llamadas"
como_rol sts get-caller-identity --query Arn --output text

echo "3) s3:GetObject sobre reportes/resumen.txt (PERMITIDO por la politica)"
como_rol s3api get-object --bucket "$B" --key reportes/resumen.txt /tmp/resumen-leido.txt \
  --query '{Cifrado:ServerSideEncryption,Bytes:ContentLength}' --output text
cat /tmp/resumen-leido.txt

echo "4) s3:PutObject con el mismo rol (NO esta en la politica)"
if como_rol s3api put-object --bucket "$B" --key reportes/intruso.txt --body /tmp/resumen-leido.txt >/dev/null 2>&1; then
  echo "   LocalStack lo acepto: en el plan Hobby no aplica IAM (ENFORCE_IAM). En AWS real: AccessDenied."
  como_rol s3api delete-object --bucket "$B" --key reportes/intruso.txt >/dev/null 2>&1 || true
else
  echo "   Denegado (AccessDenied), como se espera."
fi
rm -f /tmp/resumen-leido.txt
