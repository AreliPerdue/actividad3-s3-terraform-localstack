# Actividad 3 · Ciberseguridad (Terraform + LocalStack)

Este repositorio tiene dos partes:

1. **[Actividad 3](actividad3/README.md)** (carpeta `actividad3/`): bucket S3 cifrado con política explícita
   (`script.tf`), escaneo de contenedores con Trivy (node:14 → node:18 sin vulnerabilidades críticas), API con
   autenticación JWT y sitio web probados con curl y OWASP ZAP, rol IAM de mínimo privilegio y diagrama de arquitectura.
2. **Práctica en clase** (raíz del repo, descrita abajo): el laboratorio base de LocalStack con S3.

`compose.yaml` levanta LocalStack con S3, IAM y STS para ambas partes. En [`herramientas/`](herramientas/README.md)
están los scripts con los que se generaron las evidencias (salidas reales de cada comando, capturas del sitio y el
documento de entrega).

## Dónde encontrar qué

| Criterio de la rúbrica | Archivos | Evidencia y resultado |
|---|---|---|
| 1. IaC con cifrado y bloqueo de acceso | [`actividad3/fase1-iac/script.tf`](actividad3/fase1-iac/script.tf) | AES-256, bloqueo ×4, versionado y política explícita · `IsPublic: false` ([salida](herramientas/evidencias/A1-6-politica.txt)) |
| 2. Contenedores y Trivy | [`Dockerfile.vulnerable`](actividad3/fase3-api/Dockerfile.vulnerable) · [`Dockerfile.node18-sin-endurecer`](actividad3/fase3-api/Dockerfile.node18-sin-endurecer) · [`Dockerfile`](actividad3/fase3-api/Dockerfile) · [`escanear.sh`](actividad3/fase2-contenedores/escanear.sh) | [Reportes de Trivy](actividad3/fase2-contenedores/reportes): node:14 con 4 críticas → node:18 endurecido con **0 críticas y 0 altas** |
| 3. JWT y OWASP ZAP | [`src/autenticacion.js`](actividad3/fase3-api/src/autenticacion.js) (middleware) · [`src/servidor.js`](actividad3/fase3-api/src/servidor.js) (rutas) · [`public/`](actividad3/fase3-api/public) (sitio web) · [`pruebas/probar-api.sh`](actividad3/fase3-api/pruebas/probar-api.sh) · [`zap/escanear-zap.sh`](actividad3/fase3-api/zap/escanear-zap.sh) | [13 pruebas con curl](herramientas/evidencias/A3-3-curl.txt) · [reporte de ZAP](actividad3/fase3-api/zap/reporte-zap.html): 0 altas |
| 4. Política IAM restrictiva | [`politica-lector.json`](actividad3/fase4-iam/politica-lector.json) · [`confianza-rol.json`](actividad3/fase4-iam/confianza-rol.json) · [`iam.tf`](actividad3/fase4-iam/iam.tf) · [`ejemplo-uso.sh`](actividad3/fase4-iam/ejemplo-uso.sh) | Solo `s3:GetObject` sobre `reportes/*` · [ejemplo aplicado](herramientas/evidencias/A4-4-uso.txt) |
| 5. Diagrama de arquitectura | [`arquitectura.svg`](actividad3/fase5-diagrama/arquitectura.svg) · [`arquitectura.png`](actividad3/fase5-diagrama/arquitectura.png) | S3, contenedor, API, JWT e IAM con flujo de datos |
| Práctica en clase (anexo) | [`compose.yaml`](compose.yaml) · [`providers.tf`](providers.tf) · [`main.tf`](main.tf) · [`scripts/verificar.sh`](scripts/verificar.sh) | Ver la sección de abajo |

Instrucciones paso a paso para reproducir la Actividad 3: [`actividad3/README.md`](actividad3/README.md).

---

## Práctica en clase · Bucket S3 seguro con Terraform + LocalStack

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

En macOS: Docker Desktop desde [docker.com](https://docs.docker.com/desktop/setup/install/mac-install/), y con Homebrew
`brew install hashicorp/tap/terraform awscli`.

| Sistema | Docker | Virtualización | Permisos |
|---|---|---|---|
| Windows 10/11 | Docker Desktop + WSL2 | Activar VT-x/AMD-V en BIOS | Administrador para instalar |
| macOS | Docker Desktop (Apple silicon o Intel, ≥ 4 GB RAM) | Framework de macOS, nada que activar | Usuario admin; sin grupo `docker` |
| Linux | Docker Engine + Compose (APT) | Nativa | Agregar usuario al grupo `docker` y volver a iniciar sesión |

Probado en una MacBook Air M2 (arm64, 8 GB, macOS 26.6). La imagen de LocalStack es `linux/arm64`, nativa.

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

Ejecutado el 10 de noviembre de 2026 con LocalStack 2026.10.6, Terraform 1.17.1 y provider AWS 6.72.0.

| Prueba | Resultado |
|---|---|
| Contenedor | `Up (healthy)`, puerto `127.0.0.1:4566`, `"s3": "available"` |
| `terraform plan` | `Plan: 3 to add, 0 to change, 0 to destroy` |
| `terraform apply` | `Apply complete! Resources: 3 added` |
| Cifrado | `SSEAlgorithm: AES256` (y el objeto subido reporta `ServerSideEncryption: AES256`) |
| Bloqueo de acceso público | Los 4 controles en `true` |
| Subida de `prueba.txt` | Aparece en `s3 ls` (117 bytes) |
| Descarga anónima (`--no-sign-request` y `curl`) | **Permitida** (HTTP 200) |
| `get-bucket-policy` | `NoSuchBucketPolicy` |

### Resultado del acceso anónimo

La descarga **sin firmar** del objeto funcionó (`aws --no-sign-request` y `curl` devolvieron el
contenido, HTTP 200), aunque los cuatro controles de bloqueo están en `true`.

En AWS real esta solicitud se rechazaría con `403 AccessDenied`: el bucket no tiene ninguna
política ni ACL que dé acceso a usuarios anónimos. En LocalStack, según su
[documentación](https://docs.localstack.cloud/aws/capabilities/security-testing/iam-policy-enforcement/),
**la aplicación de IAM está desactivada por defecto** y todas las APIs se pueden usar sin
autenticación. Se activa con `ENFORCE_IAM=1`, pero esa función es de los planes Base y Ultimate,
no del Hobby. LocalStack emula la API y guarda la configuración, pero no hace cumplir las reglas
de autorización. Por eso este resultado se trata como una **limitación del simulador**, no como
una exposición real, hasta tener una validación independiente.

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
