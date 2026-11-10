# Actividad 3 · Bucket S3 seguro con Terraform + LocalStack

Laboratorio de **Infraestructura como Código (IaC)**: con Terraform se declara un bucket S3
**simulado** en LocalStack, con cifrado **SSE-S3 (AES-256)** y los **cuatro controles** de
bloqueo de acceso público. Después se comprueba con AWS CLI qué quedó realmente configurado.

> ⚠️ Todo corre en `http://localhost:4566`. No se usa AWS real ni se necesita una cuenta de AWS.

```
Terraform  ──►  LocalStack :4566 (Docker, solo localhost)  ──►  Bucket S3
(código)        simula AWS                                      · actividad3-seguro-local
                                                                · cifrado AES256
                                                                · bloqueo público ×4
```

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `compose.yaml` | Levanta LocalStack con S3, puerto 4566 **solo en 127.0.0.1**, token por variable de entorno y healthcheck. |
| `providers.tf` | Provider AWS con región `us-east-1`, credenciales ficticias (`test`) y endpoint S3 local. |
| `variables.tf` | Región, endpoint (validado: solo acepta `localhost:4566`) y nombre del bucket. |
| `main.tf` | Los 3 recursos: bucket, cifrado AES256 y bloqueo de acceso público. |
| `outputs.tf` | Muestra nombre, ARN y algoritmo de cifrado al aplicar. |
| `.terraform.lock.hcl` | Fija la versión del provider para que el laboratorio sea reproducible. |
| `scripts/verificar.sh` | Corre todas las consultas de AWS CLI contra LocalStack. |
| `prueba.txt` | Archivo de prueba (sin información real) para subir al bucket. |
| `.env.example` | Plantilla del `.env` donde va el token. El `.env` real **no se sube**. |

## Requisitos

| Herramienta | Versión usada | Comprobar |
|---|---|---|
| Docker Desktop / Engine | 29.9 | `docker --version` |
| Docker Compose v2 | 5.6 | `docker compose version` |
| Terraform | 1.17 | `terraform version` |
| AWS CLI v2 | 2.34 | `aws --version` |
| Cuenta LocalStack **Hobby (gratis)** | — | token en [app.localstack.cloud](https://app.localstack.cloud) |

En macOS: Docker Desktop desde [docker.com](https://docs.docker.com/desktop/), y con Homebrew
`brew install hashicorp/tap/terraform awscli`.

## Cómo ejecutarlo

### 1. Token de LocalStack (privado)

```bash
cp .env.example .env
# edita .env y pega tu token: LOCALSTACK_AUTH_TOKEN=...
```

`.env` está en `.gitignore`. Nunca pegues el token en el código, en capturas ni en GitHub.

### 2. Levantar LocalStack

```bash
docker compose up -d
docker compose ps                                 # debe decir (healthy)
curl -s http://localhost:4566/_localstack/health  # "s3": "available" o "running"
```

### 3. Terraform

```bash
terraform init
terraform validate
terraform plan -out=tfplan      # Plan: 3 to add, 0 to change, 0 to destroy
terraform apply tfplan
terraform state list
```

### 4. Verificar con AWS CLI

Siempre con credenciales ficticias y el endpoint local explícito:

```bash
export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1
EP=http://localhost:4566

aws --endpoint-url $EP s3api list-buckets
aws --endpoint-url $EP s3api get-bucket-encryption     --bucket actividad3-seguro-local
aws --endpoint-url $EP s3api get-public-access-block   --bucket actividad3-seguro-local
aws --endpoint-url $EP s3 cp prueba.txt s3://actividad3-seguro-local/
aws --endpoint-url $EP s3 ls s3://actividad3-seguro-local/
aws --endpoint-url $EP --no-sign-request s3 cp s3://actividad3-seguro-local/prueba.txt -   # acceso anónimo
aws --endpoint-url $EP s3api get-bucket-policy         --bucket actividad3-seguro-local    # NoSuchBucketPolicy
```

O todo junto: `./scripts/verificar.sh`

### 5. Dashboard

En [app.localstack.cloud](https://app.localstack.cloud) → **Resource Browser → S3**, con el endpoint
`http://localhost:4566`, en la misma computadora donde corre Docker.

### 6. Limpiar

```bash
terraform destroy
docker compose down
```

## Resultados e interpretación

| Prueba | Resultado |
|---|---|
| `terraform plan` | 3 recursos por crear |
| Cifrado | `SSEAlgorithm: AES256` |
| Bloqueo de acceso público | Los 4 controles en `true` |
| Descarga anónima (`--no-sign-request`) | Ver [resultados](#resultado-del-acceso-anónimo) |
| `get-bucket-policy` | `NoSuchBucketPolicy` |

### Resultado del acceso anónimo

_Se completa al ejecutar el laboratorio._

### `NoSuchBucketPolicy`

Significa que el bucket **no tiene política de bucket**. No es una señal de exposición pública:
sin política no hay ninguna regla que otorgue acceso a `"Principal": "*"`, y además
`block_public_policy` impediría agregar una política pública.

### Declarado vs. consultado vs. aplicado

- **Declarado:** lo que dice el código de Terraform (`main.tf`).
- **Consultado:** lo que la API de S3 (aquí, LocalStack) responde que tiene configurado.
- **Efectivamente aplicado:** lo que de verdad pasa cuando alguien intenta acceder.

Que algo esté declarado y que la API lo reporte no prueba que se cumpla: LocalStack es un
simulador y no replica todas las reglas de autorización de AWS (por defecto no evalúa IAM).
Por eso la seguridad se valida con pruebas de comportamiento, y en AWS real con una validación
independiente.

## Seguridad

- No se publican tokens, contraseñas, `.env` ni `*.tfstate` (ver `.gitignore`).
- Credenciales ficticias `test/test`; ningún comando apunta a AWS de producción.
- El puerto 4566 solo escucha en `127.0.0.1`.
- No se usa información confidencial real.
