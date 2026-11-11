#!/bin/zsh
# Pruebas de la autenticación JWT con curl. Lee las claves de demostración de ../.env
# y nunca las imprime.
set -uo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a
URL=${URL:-http://localhost:3000}

linea() { printf '%-3s %-36s %-30s -> HTTP %s  %s\n' "$1" "$2" "$3" "$4" "$5"; }
pedir() { # metodo ruta token -> "codigo|cuerpo"
  local auth=(); [ -n "${3:-}" ] && auth=(-H "Authorization: Bearer $3")
  local r; r=$(curl -s -w '\n%{http_code}' -X "$1" "${auth[@]}" "$URL$2")
  printf '%s|%s' "$(tail -n1 <<<"$r")" "$(sed '$d' <<<"$r" | head -c 70)"
}
caso() { local res; res=$(pedir "$3" "$4" "${5:-}"); linea "$1" "$2" "$3 $4" "${res%%|*}" "${res#*|}"; }
login() { curl -s -X POST "$URL/api/sesion" -H 'Content-Type: application/json' \
  -d "{\"usuario\":\"$1\",\"clave\":\"$2\"}"; }
token_de() { python3 -c 'import json,sys; print(json.load(sys.stdin).get("token",""))'; }

echo "== Inicio de sesión =="
r=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL/api/sesion" -H 'Content-Type: application/json' -d '{"usuario":"admin","clave":"incorrecta-123"}')
linea 1 "Clave incorrecta" "POST /api/sesion" "$r" "(no se emite token)"
T_LECTOR=$(login lector "$CLAVE_DEMO_LECTOR" | token_de)
T_ADMIN=$(login admin "$CLAVE_DEMO_ADMIN" | token_de)
linea 2 "Login correcto (lector y admin)" "POST /api/sesion" "200" "tokens recibidos (${#T_LECTOR} y ${#T_ADMIN} caracteres)"

echo "== Endpoints sensibles =="
caso 3 "Sin token" GET /api/perfil
caso 4 "Token inventado" GET /api/usuarios "esto.no.es-un-jwt"
caso 5 "Lector: su perfil" GET /api/perfil "$T_LECTOR"
caso 6 "Lector: lista de usuarios (admin)" GET /api/usuarios "$T_LECTOR"
caso 7 "Lector: reporte en S3 (admin)" GET /api/reportes/resumen.txt "$T_LECTOR"
caso 8 "Admin: lista de usuarios" GET /api/usuarios "$T_ADMIN"
caso 9 "Admin: reporte en S3" GET /api/reportes/resumen.txt "$T_ADMIN"

echo "== Manipulación del token =="
ALTERADO="${T_ADMIN%?}$( [ "${T_ADMIN: -1}" = A ] && echo B || echo A )"
caso 10 "Firma alterada (1 caracter)" GET /api/usuarios "$ALTERADO"
PAYLOAD_ADMIN=$(python3 -c 'import base64,json,time; print(base64.urlsafe_b64encode(json.dumps({"sub":"lector","rol":"admin"}).encode()).decode().rstrip("="))')
CABECERA_NONE=$(printf '{"alg":"none","typ":"JWT"}' | base64 | tr '+/' '-_' | tr -d '=')
caso 11 "alg none + rol admin falsificado" GET /api/usuarios "$CABECERA_NONE.$PAYLOAD_ADMIN."
VENCIDO=$(JWT_SECRETO="$JWT_SECRETO" node -e '
  const jwt=require("jsonwebtoken");
  process.stdout.write(jwt.sign({rol:"admin",iat:Math.floor(Date.now()/1000)-3600},process.env.JWT_SECRETO,
  {algorithm:"HS256",subject:"admin",issuer:"api-reportes-actividad3",audience:"sitio-reportes",expiresIn:"15m"}))')
caso 12 "Token vencido (emitido hace 1 h)" GET /api/usuarios "$VENCIDO"
OTRO=$(node -e 'const jwt=require("jsonwebtoken");process.stdout.write(jwt.sign({rol:"admin"},"otro-secreto-que-no-es-el-del-servidor",{subject:"admin",issuer:"api-reportes-actividad3",audience:"sitio-reportes"}))')
caso 13 "Firmado con otro secreto" GET /api/usuarios "$OTRO"

echo "== Contenido del token de admin (payload decodificado) =="
python3 -c '
import base64,json,sys
p=sys.argv[1].split(".")[1]; d=json.loads(base64.urlsafe_b64decode(p+"="*(-len(p)%4)))
print(json.dumps(d,ensure_ascii=False)); print("vigencia:", d["exp"]-d["iat"], "segundos")' "$T_ADMIN"
