#!/usr/bin/env bash
# Escanea una imagen con Trivy (HIGH y CRITICAL), guarda el reporte completo y muestra un resumen.
# Uso: ./escanear.sh <imagen> <nombre-del-reporte>
set -euo pipefail
IMAGEN=$1; NOMBRE=$2
mkdir -p reportes
trivy image --quiet --scanners vuln --severity HIGH,CRITICAL --format json -o "reportes/trivy-$NOMBRE.json" "$IMAGEN"
trivy convert --quiet --format table -o "reportes/trivy-$NOMBRE.txt" "reportes/trivy-$NOMBRE.json"
python3 - "reportes/trivy-$NOMBRE.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
tc = th = 0
print(f"{'Objetivo':<44}{'CRITICAL':>9}{'HIGH':>7}")
for r in d.get("Results", []):
    v = r.get("Vulnerabilities") or []
    c = sum(x["Severity"] == "CRITICAL" for x in v); h = sum(x["Severity"] == "HIGH" for x in v)
    tc += c; th += h
    print(f"{r['Target'][:43]:<44}{c:>9}{h:>7}")
print(f"{'TOTAL':<44}{tc:>9}{th:>7}")
crit = [x for r in d.get("Results", []) for x in (r.get("Vulnerabilities") or []) if x["Severity"] == "CRITICAL"]
for x in crit:
    print(f"  CRITICAL {x['VulnerabilityID']:<16} {x['PkgName']:<14} {x['InstalledVersion']:<26} corregida en: {x.get('FixedVersion') or 'sin parche'}")
PY
echo "Reporte completo: reportes/trivy-$NOMBRE.txt"
