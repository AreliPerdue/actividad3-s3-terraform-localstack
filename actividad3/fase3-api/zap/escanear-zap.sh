#!/usr/bin/env bash
# Escaneo automatizado con OWASP ZAP (modo daemon + API REST):
# importa openapi.yaml, araña el sitio, hace escaneo activo y genera reportes HTML y JSON.
# Requiere ZAP instalado (macOS: /Applications/ZAP.app) y la API corriendo en http://localhost:3000.
set -euo pipefail
cd "$(dirname "$0")"
ZAP_SH=${ZAP_SH:-/Applications/ZAP.app/Contents/Java/zap.sh}
OBJETIVO=${OBJETIVO:-http://localhost:3000}
PUERTO=8095; API="http://127.0.0.1:$PUERTO"
HOME_ZAP=$(mktemp -d)

zap() { curl -s "$API/$1"; }
valor() { python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
esperar() { # ruta-de-estado
  while :; do p=$(zap "$1" | valor status); printf '\r   progreso: %s%%' "$p"; [ "$p" = 100 ] && break; sleep 2; done; echo
}

echo "1) Iniciando ZAP $("$ZAP_SH" -cmd -version 2>/dev/null | tail -1) en modo daemon"
"$ZAP_SH" -daemon -host 127.0.0.1 -port $PUERTO -dir "$HOME_ZAP" -config api.disablekey=true >/dev/null 2>&1 &
until zap JSON/core/view/version/ >/dev/null 2>&1 && [ -n "$(zap JSON/core/view/version/)" ]; do sleep 2; done

echo "2) Importando la definición OpenAPI de la API"
zap "JSON/openapi/action/importFile/?file=$PWD/../openapi.yaml&target=$OBJETIVO" >/dev/null

echo "3) Araña (spider) sobre $OBJETIVO"
id=$(zap "JSON/spider/action/scan/?url=$OBJETIVO" | valor scan); esperar "JSON/spider/view/status/?scanId=$id"

echo "4) Escaneo activo"
id=$(zap "JSON/ascan/action/scan/?url=$OBJETIVO&recurse=true" | valor scan); esperar "JSON/ascan/view/status/?scanId=$id"
while [ "$(zap JSON/pscan/view/recordsToScan/ | valor recordsToScan)" != 0 ]; do sleep 1; done

echo "5) URLs evaluadas"
zap "JSON/core/view/urls/?baseurl=$OBJETIVO" | python3 -c "import json,sys; [print('   ', u) for u in sorted(set(json.load(sys.stdin)['urls']))]"

zap OTHER/core/other/htmlreport/ > reporte-zap.html
zap OTHER/core/other/jsonreport/ > reporte-zap.json
echo "6) Resumen de alertas"
python3 - reporte-zap.json <<'PY'
import json, sys
z = json.load(open(sys.argv[1]))
alertas = [a for s in z["site"] for a in s["alerts"]]
orden = ["High", "Medium", "Low", "Informational"]
cuenta = {k: sum(a["riskdesc"].startswith(k) for a in alertas) for k in orden}
print("   " + " | ".join(f"{k}: {v}" for k, v in cuenta.items()))
for a in sorted(alertas, key=lambda a: orden.index(a["riskdesc"].split()[0])):
    print(f"   {a['riskdesc'].split()[0]:<14}{a['count']:>3}  {a['alert']}")
PY
echo "Reportes: zap/reporte-zap.html y zap/reporte-zap.json"
zap JSON/core/action/shutdown/ >/dev/null; rm -rf "$HOME_ZAP"
