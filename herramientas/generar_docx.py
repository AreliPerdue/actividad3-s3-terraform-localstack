"""Documento de la Actividad 3 con la portada, fuentes y estilo de la Actividad 2 de Areli (se usa como plantilla)."""
import sys, copy, re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

S = Path(__file__).resolve().parent
PNG, REAL = S / "capturas", S / "capturas-reales"
OUT = Path(sys.argv[1])
REPO = "https://github.com/AreliPerdue/actividad3-s3-terraform-localstack"
VERDE, AZUL = RGBColor(0x00, 0xB0, 0x50), RGBColor(0x00, 0x20, 0x60)
MORADO = AZUL  # compatibilidad con el contenido

# --- Plantilla: Actividad 2 (portada y estilos) ---
doc = Document(str(S / "plantilla" / "portada.docx"))  # Actividad 2 de la autora (no se versiona)
body = doc.element.body
els = list(body.iterchildren())
for el in els[12:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)
# "Actividad 2" -> "Actividad 3"
for t in els[11].iter(qn("w:t")):
    if t.text == "2":
        t.text = "3"
sec = doc.sections[0]
CW = Cm(15.24)  # ancho de imagen que usa la Actividad 2 (6 in)

ARIAL = "Arial"


def fuente(run, nombre=ARIAL, size=12, bold=None, italic=None, color=None):
    run.font.name = nombre
    rpr = run._element.get_or_add_rPr()
    rpr.get_or_add_rFonts().set(qn("w:cs"), nombre)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def nuevo(style="Normal (Web)", align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    return p


def outline(p, nivel):
    ppr = p._p.get_or_add_pPr()
    o = OxmlElement("w:outlineLvl")
    o.set(qn("w:val"), str(nivel))
    ppr.append(o)


H_OFF = 0
CRITERIOS = {
    "Fase 1": "Criterio 1 (25 pts): script.tf que crea un bucket con cifrado AES-256 y política explícita que bloquea todo acceso público, validado por línea de comandos.",
    "Fase 2": "Criterio 2 (20 pts): Dockerfile con versión inicial vulnerable, escaneo con Trivy, actualización a node:18 y reporte sin vulnerabilidades críticas.",
    "Fase 3": "Criterio 3 (25 pts): middleware de autenticación JWT que valida tokens en al menos 2 endpoints sensibles y resultado del escaneo con OWASP ZAP.",
    "Fase 4": "Criterio 4 (20 pts): archivo JSON con política IAM restringida a roles definidos, con acciones como s3:GetObject, y ejemplo de su uso aplicado.",
    "Fase 5": "Criterio 5 (10 pts): diagrama digital con flujo de datos que incluya S3, contenedores, API y autenticación.",
}


def H(text, level=1):
    global _titulo
    nivel = min(level + H_OFF, 3)
    if nivel == 1:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        outline(p, 0)
        fuente(p.add_run(text), "Arial Black", 14, bold=True, color=VERDE)
        clave = text.split(".")[0]
        if clave in CRITERIOS:
            c = doc.add_paragraph()
            c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            c.paragraph_format.space_after = Pt(8)
            fuente(c.add_run(CRITERIOS[clave]), "Arial Black", 12, bold=True, color=AZUL)
    else:
        p = doc.add_paragraph(style="Heading 2" if nivel == 2 else "Heading 3")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        fuente(p.add_run(text), ARIAL, 12, bold=True)
        p.runs[0].font.color.rgb = RGBColor(0, 0, 0)
    _titulo = text
    return p


doc.add_heading = H
_titulo = ""
_figura = [0]


def para(text="", bold=False, size=None, align=None, italic=False, after=None, color=None):
    p = nuevo(align=WD_ALIGN_PARAGRAPH.JUSTIFY if align is None else align)
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if text:
        fuente(p.add_run(text), ARIAL, size or 12, bold=bold, italic=italic, color=color)
    return p


def rich(parts, style=None):
    p = nuevo()
    for t, f in parts:
        r = p.add_run(t)
        if "c" in f:
            fuente(r, "Courier New", 11, bold="b" in f)
        else:
            fuente(r, ARIAL, 12, bold="b" in f)
    return p


def img(name, width=None, caption=None):
    path = next((d / f"{name}{ext}" for d in (PNG, REAL) for ext in (".png", ".jpg") if (d / f"{name}{ext}").exists()), None)
    if path is None:
        p = para(f"[Captura pendiente: {caption or name}]", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.runs[0].font.highlight_color = WD_COLOR_INDEX.YELLOW
        return
    p = nuevo(align=WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=min(width or CW, CW))
    _figura[0] += 1
    texto = caption or re.sub(r"^(\d+\.\d+|Paso \d+(\.\d+)?\.?)\s*", "", _titulo)
    c = nuevo(align=WD_ALIGN_PARAGRAPH.CENTER)
    fuente(c.add_run(f"Figura {_figura[0]}. {texto}."), ARIAL, 9, italic=True)


def step(title, desc, images, level=2):
    H(title, level=level)
    p = para(desc) if isinstance(desc, str) else rich(desc)
    p.paragraph_format.keep_together = True  # que la descripción no se parta entre páginas
    if images:
        p.paragraph_format.keep_with_next = True
    for im in images:
        if isinstance(im, tuple):
            img(*im)
        else:
            img(im)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


doc.add_page_break = page_break
doc.add_page_break()

# ===================== ACTIVIDAD 3 (fases de la rúbrica) =====================
import json as _json
LAB = S.parent / "actividad3"


def tabla(encabezados, filas, anchos):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, h in zip(t.rows[0].cells, encabezados):
        c.text = h
    for fila in filas:
        for c, v in zip(t.add_row().cells, fila):
            c.text = str(v)
    for r in t.rows:
        for i, c in enumerate(r.cells):
            c.width = Cm(anchos[i])
            for p in c.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9.5)
                    if r is t.rows[0]:
                        run.bold = True
    para()
    return t


def trivy(nombre):
    d = _json.load(open(LAB / "fase2-contenedores/reportes" / f"trivy-{nombre}.json"))
    v = [x for r in d.get("Results", []) for x in (r.get("Vulnerabilities") or [])]
    return sum(x["Severity"] == "CRITICAL" for x in v), sum(x["Severity"] == "HIGH" for x in v), \
        [x for x in v if x["Severity"] == "CRITICAL"]


doc.add_heading("Introducción", level=1)
para("En esta actividad armé, en mi computadora, una arquitectura pequeña pero completa y la fui asegurando capa por "
     "capa: un bucket S3 cifrado y cerrado al público definido con Terraform, un contenedor cuya imagen pasé de una "
     "versión vulnerable a una sin vulnerabilidades críticas (comprobado con Trivy), una API con sitio web que exige "
     "JWT en sus endpoints sensibles (probada con curl, en el navegador y con OWASP ZAP), un rol IAM de mínimo "
     "privilegio que la API usa para leer de S3, y el diagrama que conecta todo.")
para("Cada fase sigue el mismo orden: qué hice, la captura y qué demuestra. Todo corre contra LocalStack "
     "(http://localhost:4566), así que no se creó nada en AWS real.")
doc.add_heading("Entorno de trabajo", level=2)
tabla(["Componente", "Versión / detalle"], [
    ("Equipo", "MacBook Air M2 (arm64), 8 GB, macOS 26.6.2, zsh"),
    ("Nube simulada", "LocalStack 2026.10.6 (plan Hobby) con S3, IAM y STS en el puerto 4566"),
    ("IaC", "Terraform 1.17.1 con provider hashicorp/aws 6.72.0"),
    ("Contenedores", "Docker 29.9.2 (Docker Desktop) y Trivy 0.76.1"),
    ("AWS CLI", "2.34.16 con un perfil propio \"localstack\" (endpoint local y credenciales ficticias)"),
    ("API y sitio", "Node.js 18.20.8 en el contenedor, Express 5.3, jsonwebtoken 9.0.3, helmet 8.3, AWS SDK v3"),
    ("Pruebas de seguridad", "curl, Chrome headless para las capturas del sitio y OWASP ZAP 2.17.0"),
], [4.2, 12.4])
rich([("Repositorio: ", "b"), (REPO, ""), (" (carpeta ", ""), ("actividad3/", "c"), (", una subcarpeta por fase)", "")])

# ---------------- Fase 1 ----------------
doc.add_heading("Fase 1. Configuración segura en la nube con IaC", level=1)
para("El archivo script.tf crea el bucket actividad3-reportes-cifrados con cinco recursos: el bucket, el versionado, "
     "el cifrado AES-256 por defecto, el bloqueo de acceso público con sus cuatro opciones y una política de bucket "
     "explícita que niega cualquier acceso que no venga de la cuenta (lo que incluye las solicitudes anónimas) y "
     "cualquier solicitud sin HTTPS.")
step("1.1 Perfil de AWS CLI para LocalStack",
     [("Antes de empezar creé un perfil aparte, ", ""), ("localstack", "c"), (", con región us-east-1, credenciales ficticias y ", ""),
      ("endpoint_url = http://localhost:4566", "c"), (". No toqué mi perfil default. ", ""), ("get-caller-identity", "c"),
      (" responde la cuenta 000000000000, que es la de LocalStack: los comandos nunca salen a AWS real.", "")],
     ["A1-0-perfil-cli"])
step("1.2 Código de script.tf",
     [("El provider solo acepta el endpoint local (una validación rechaza cualquier otro). ", ""),
      ("sse_algorithm = \"AES256\"", "c"), (" activa el cifrado en reposo, ", ""), ("aws_s3_bucket_public_access_block", "c"),
      (" activa los cuatro bloqueos y ", ""), ("aws_s3_bucket_policy", "c"), (" agrega las dos negaciones explícitas.", "")],
     ["A1-1-codigo-a", "A1-1-codigo-b", "A1-1-codigo-c"])
step("1.3 Inicializar, validar y planear",
     "Terraform descargó el provider, el formato y la sintaxis son correctos, y el plan crea exactamente 5 recursos.",
     ["A1-2-init-validate", "A1-3-plan"])
step("1.4 Aplicar", [("Resultado: ", ""), ("Apply complete! Resources: 5 added, 0 changed, 0 destroyed.", "b")], ["A1-4-apply"])
step("1.5 Validación por línea de comandos: cifrado, bloqueo y versionado",
     [("Con el perfil ", ""), ("localstack", "c"), (": ", ""), ("SSEAlgorithm: AES256", "b"), (", los cuatro controles en ", ""),
      ("true", "b"), (" y el versionado en ", ""), ("Enabled", "b"), (".", "")], ["A1-5-cifrado-bloqueo"])
step("1.6 Validación por línea de comandos: política y estado público",
     [("get-bucket-policy", "c"), (" muestra la política explícita tal como la declaré y ", ""), ("get-bucket-policy-status", "c"),
      (" responde ", ""), ("IsPublic: false", "b"), (". El bucket está cifrado y no es público.", "")],
     ["A1-6-politica"])
para("Nota: en LocalStack Hobby las políticas no se hacen cumplir (la aplicación de IAM viene apagada), por eso la "
     "validación se hace sobre la configuración que reporta la API. En AWS real, estas dos negaciones bloquearían el "
     "acceso anónimo y el tráfico HTTP.", italic=True, size=10)

# ---------------- Fase 2 ----------------
c14, h14, crit14 = trivy("node14")
c18, h18, crit18 = trivy("node18-sin-endurecer")
cf, hf, _ = trivy("final-node18")
doc.add_heading("Fase 2. Protección de contenedores y escaneo con Trivy", level=1)
para("El contenedor es el de mi propia API (Fase 3). Lo construí tres veces para medir el efecto de cada cambio con "
     "Trivy (severidades HIGH y CRITICAL): primero con una base vulnerable, luego solo cambiando a node:18 y al final "
     "con node:18 endurecido. Los reportes completos están en actividad3/fase2-contenedores/reportes.")
step("2.1 Dockerfile inicial vulnerable (node:14)",
     "node:14 llegó a fin de soporte en abril de 2023 y su base Debian 10 ya no recibe parches. Además, esta versión "
     "corre como root y no tiene healthcheck. Usé la variante slim por el espacio disponible en mi disco.",
     ["A2-1-build-vulnerable"])
step("2.2 Escaneo de la imagen inicial",
     [("Trivy encontró ", ""), (f"{c14} vulnerabilidades críticas y {h14} altas", "b"),
      (" entre el sistema operativo y los paquetes de Node que vienen dentro de npm.", "")], ["A2-2-trivy-node14"])
tabla(["CVE", "Paquete", "Versión instalada", "Corregida en"],
      [(x["VulnerabilityID"], x["PkgName"], x["InstalledVersion"], x.get("FixedVersion") or "sin parche") for x in crit14],
      [3.6, 3.4, 5.0, 4.6])
step("2.3 Actualización a node:18 (solo cambiar la base)",
     [("Primero cambié únicamente la línea ", ""), ("FROM", "c"), (" a ", ""), ("node:18-alpine", "c"), (". El resultado mejoró, pero ", ""),
      (f"todavía quedaban {c18} críticas y {h18} altas", "b"),
      (": OpenSSL de la imagen base sin actualizar y el paquete tar que trae npm. Cambiar la versión no fue suficiente.", "")],
     ["A2-3-build-node18", "A2-4-trivy-node18"])
step("2.4 Dockerfile final: node:18 endurecido",
     [("Mantuve node:18, como pide la actividad, y endurecí la imagen: construcción en dos etapas con ", ""), ("npm ci --omit=dev", "c"),
      (", ", ""), ("apk upgrade", "c"), (" para aplicar los parches del sistema, eliminé npm/npx/yarn de la imagen final (la app no "
       "los necesita para ejecutarse y eran la fuente de los CVE de Node), usuario sin privilegios ", ""), ("node", "c"),
      (" y un ", ""), ("HEALTHCHECK", "c"), (".", "")], ["A2-5-build-final"])
step("2.5 Escaneo de la imagen final",
     [("Reporte final: ", ""), (f"{cf} críticas y {hf} altas", "b"), (". No se registra ninguna vulnerabilidad crítica.", "")],
     ["A2-6-trivy-final"])
tabla(["Imagen", "Base", "CRITICAL", "HIGH"], [
    ("reportes-api:vulnerable", "node:14-slim", c14, h14),
    ("reportes-api:node18", "node:18-alpine (sin cambios)", c18, h18),
    ("reportes-api:1.0 (final)", "node:18-alpine endurecida", cf, hf),
], [4.6, 5.6, 3.0, 3.0])
step("2.6 Ejecución segura del contenedor",
     [("Comprobé que la imagen corre Node 18 con el usuario ", ""), ("node", "c"), (" y sin npm. La levanté publicando el puerto solo en "
       "127.0.0.1, con sistema de archivos de solo lectura (", ""), ("--read-only", "c"), ("), sin capacidades de Linux (", ""),
      ("--cap-drop ALL", "c"), (") y con ", ""), ("no-new-privileges", "c"), (". El contenedor queda ", ""), ("healthy", "b"), (".", "")],
     ["A2-7-ejecutar"])

# ---------------- Fase 3 ----------------
doc.add_heading("Fase 3. Autenticación JWT en la API y sitio web", level=1)
para("Desarrollé una API con Express que también sirve un sitio web sencillo (inicio de sesión y panel). Hay un "
     "endpoint público de salud, uno de inicio de sesión y tres endpoints sensibles protegidos con JWT; dos de ellos "
     "además exigen el rol admin. El endpoint de reportes lee el archivo cifrado de S3 usando el rol IAM de la Fase 4.")
step("3.1 Dependencias", [("Express para el servidor, ", ""), ("jsonwebtoken", "c"), (" para firmar y verificar tokens, ", ""),
                          ("helmet", "c"), (" para cabeceras de seguridad y el AWS SDK para STS y S3.", "")], ["A3-1-dependencias"])
step("3.2 Middleware de autenticación",
     [("verificarToken", "c"), (" exige ", ""), ("Authorization: Bearer <token>", "c"), (" y valida la firma permitiendo solo ", ""),
      ("HS256", "c"), (" (evita tokens con ", ""), ("alg: none", "c"), ("), además del emisor, la audiencia y la expiración; si algo "
       "falla responde 401. ", ""), ("exigirRol", "c"), (" responde 403 cuando el rol no alcanza. El secreto viene de una variable "
       "de entorno de al menos 32 caracteres y las contraseñas se guardan con hash scrypt.", "")], ["A3-2-middleware"])
step("3.3 Endpoints protegidos",
     [("/api/perfil", "c"), (" usa ", ""), ("verificarToken", "c"), ("; ", ""), ("/api/usuarios", "c"), (" y ", ""),
      ("/api/reportes/:nombre", "c"), (" encadenan ", ""), ("verificarToken", "c"), (" y ", ""), ("exigirRol('admin')", "c"),
      (". El inicio de sesión tiene un límite de 5 intentos por minuto.", "")], ["A3-2b-rutas"])
step("3.4 Pruebas con curl",
     "Corrí 13 casos con un script que lee las claves de prueba del archivo .env y nunca las imprime.",
     ["A3-3-curl"])
tabla(["#", "Caso", "Resultado"], [
    ("1", "Clave incorrecta en /api/sesion", "401, no se emite token"),
    ("3-4", "Sin token / token inventado", "401"),
    ("5", "Lector en /api/perfil", "200"),
    ("6-7", "Lector en /api/usuarios y /api/reportes (solo admin)", "403"),
    ("8-9", "Admin en /api/usuarios y /api/reportes", "200 (el reporte llega desde S3 con cifrado AES256)"),
    ("10", "Firma alterada", "401"),
    ("11", "alg none con rol admin falsificado", "401"),
    ("12", "Token vencido", "401 \"Token expirado\""),
    ("13", "Token firmado con otro secreto", "401"),
], [1.4, 8.4, 6.8])
para("El payload del token solo tiene sub, rol, iat, exp, iss y aud (sin contraseñas ni datos sensibles) y dura 900 "
     "segundos (15 minutos).")
step("3.5 Sitio web: inicio de sesión",
     "La página de inicio de sesión envía las credenciales a POST /api/sesion. El token se guarda solo en memoria (no en "
     "localStorage) y todo lo que llega de la API se pinta con textContent.", [("W1-login", Cm(14))])
step("3.6 Sitio web: credenciales incorrectas", "La API responde 401 y el sitio lo muestra; no se emite ningún token.",
     [("W2-login-incorrecto", Cm(14))])
step("3.7 Sitio web: usuario lector",
     "El lector ve su perfil (200), pero las dos secciones de administración responden 403: está autenticado, pero su "
     "rol no le alcanza.", [("W3-lector-403", Cm(14))])
step("3.8 Sitio web: usuario admin",
     "Con el rol admin las dos secciones responden 200, y el reporte llega desde el bucket cifrado (AES256) a través del "
     "rol IAM de mínimo privilegio.", [("W4-admin-200", Cm(13))])

zap_json = LAB / "fase3-api/zap/reporte-zap.json"
doc.add_heading("3.9 Escaneo automatizado con OWASP ZAP", level=2)
if zap_json.exists():
    z = _json.load(open(zap_json))
    alertas = [a for s in z.get("site", []) for a in s.get("alerts", [])]
    riesgo = lambda a: a.get("riskdesc", "").split(" ")[0]
    cuenta = {k: sum(riesgo(a) == k for a in alertas) for k in ("High", "Medium", "Low", "Informational")}
    para("Automaticé OWASP ZAP 2.17.0 con zap/escanear-zap.sh: inicia ZAP en modo daemon, importa openapi.yaml "
         "(la definición de mis endpoints), recorre el sitio con la araña y lanza el escaneo activo contra "
         "http://localhost:3000. Al final lista las URLs evaluadas y genera los reportes HTML y JSON.")
    para("El primer escaneo encontró 4 alertas de riesgo medio: tres por la política CSP que helmet trae por defecto "
         "(comodín y 'unsafe-inline' en estilos, y una página 404 sin la directiva form-action) y la de sitio solo HTTP. "
         "Corregí la CSP declarándola completa y sin 'unsafe-inline' ni comodines, agregué una página 404 propia con las "
         "mismas cabeceras, reconstruí la imagen (Trivy siguió en 0 críticas) y repetí el escaneo:")
    para(f"Resultado final: {cuenta['High']} alertas de riesgo alto, {cuenta['Medium']} medio, {cuenta['Low']} bajo y "
         f"{cuenta['Informational']} informativas. La única media es \"HTTP Only Site\", esperable porque el laboratorio "
         f"corre en HTTP local; en producción se resuelve sirviendo la API detrás de HTTPS. ZAP evaluó las 13 URLs, "
         f"incluidos los cinco endpoints de la API; el 59 % de las respuestas fueron 4xx porque las rutas protegidas rechazan las peticiones sin token.")
    img("A3-4-zap")
    tabla(["Alerta", "Riesgo", "Instancias"],
          [(a["alert"], riesgo(a), a.get("count", len(a.get("instances", [])))) for a in
           sorted(alertas, key=lambda a: ["High", "Medium", "Low", "Informational"].index(riesgo(a)) if riesgo(a) in cuenta else 9)],
          [10.6, 3.0, 3.0])
    img("A3-5-zap-html", Cm(15), "Reporte HTML de ZAP")
else:
    para("[Pendiente: reporte de ZAP]")

# ---------------- Fase 4 ----------------
doc.add_heading("Fase 4. Política IAM restrictiva", level=1)
para("Definí el rol rol-lector-reportes, pensado para el contenedor de la API, y una política administrada que le "
     "permite una sola acción, s3:GetObject, y solo sobre los objetos de reportes/ del bucket de la Fase 1. No puede "
     "listar, escribir ni borrar. La política se adjunta exclusivamente a ese rol.")
step("4.1 Archivos JSON de la política",
     [("politica-lector.json", "c"), (" (permiso) y ", ""), ("confianza-rol.json", "c"),
      (" (quién puede asumir el rol: las tareas de ECS donde correría la API y la cuenta, para las pruebas).", "")], ["A4-1-politica"])
step("4.2 Creación con Terraform", "iam.tf crea el rol, la política y el adjunto (3 recursos).", ["A4-2-terraform"])
step("4.3 Política adjunta al rol", "La única política del rol es politica-solo-lectura-reportes, con s3:GetObject sobre reportes/*.",
     ["A4-3-adjunta"])
step("4.4 Ejemplo aplicado",
     [("ejemplo-uso.sh", "c"), (" asume el rol con STS (credenciales temporales de 15 minutos), confirma la identidad ", ""),
      ("assumed-role/rol-lector-reportes", "c"), (" y lee el reporte cifrado con s3:GetObject. Es el mismo flujo que usa la API "
       "en /api/reportes (Fase 3). Al intentar s3:PutObject con el mismo rol, LocalStack lo acepta porque el plan Hobby no "
       "aplica IAM; en AWS real sería AccessDenied, porque la política no incluye esa acción.", "")], ["A4-4-uso"])

# ---------------- Fase 5 ----------------
doc.add_heading("Fase 5. Diagrama de arquitectura segura", level=1)
para("Hice el diagrama en formato digital (SVG, en actividad3/fase5-diagrama). Incluye S3, el contenedor, la API, la "
     "autenticación JWT, IAM/STS y el flujo de datos numerado de una consulta de reporte.")
img("arquitectura-diagrama", None, "Figura 5. Arquitectura segura y flujo de datos")
para("Cada capa aporta un control distinto: en los datos, cifrado, bloqueo público y política explícita; en el acceso a "
     "la nube, un rol de mínimo privilegio con credenciales temporales; en la aplicación, JWT con roles, límite de "
     "intentos y cabeceras de seguridad; y en el contenedor, una imagen sin vulnerabilidades críticas que corre sin "
     "privilegios. Si una capa falla, las demás siguen protegiendo.")

# ---------------- Cierre de la actividad ----------------
doc.add_heading("Conclusión", level=1)
para("Lo más importante que aprendí es que cada control necesita una prueba. Declarar el cifrado y la política en "
     "Terraform no basta: hay que consultarlos (IsPublic: false, AES256) y, cuando el entorno lo permite, probar el "
     "comportamiento. Con los contenedores pasó algo parecido: subir a node:18 parecía la solución, pero Trivy mostró "
     "que seguían habiendo críticas hasta aplicar parches y quitar lo que la app no usa. En la API, las pruebas "
     "negativas (token alterado, alg none, vencido o firmado con otro secreto) fueron las que de verdad demostraron que "
     "el middleware valida y no solo revisa que exista un token.")
para("Limitaciones y mejoras para un entorno real:")
for t in ["LocalStack Hobby no aplica IAM ni las políticas de bucket: la negación de acciones (PutObject, acceso "
          "anónimo) debe confirmarse en AWS real o con ENFORCE_IAM en un plan que lo incluya.",
          "Los usuarios de la API son de demostración; en producción irían en una base de datos y el secreto JWT en un "
          "gestor de secretos, con rotación.",
          "Servir la API detrás de HTTPS (la política del bucket ya exige TLS) y agregar un escaneo autenticado de ZAP.",
          "Integrar Trivy y ZAP en un flujo de integración continua para detectar vulnerabilidades nuevas."]:
    doc.add_paragraph(t, style="List Bullet")

doc.add_heading("Manejo de información sensible en las evidencias", level=2)
para("Ninguna captura muestra el token de LocalStack, el secreto JWT ni las contraseñas de los usuarios de prueba: viven "
     "en archivos .env que están en .gitignore, y el script de pruebas los lee sin imprimirlos. Las credenciales de AWS "
     "son las ficticias de LocalStack (test/test).")

doc.add_heading("Cumplimiento de la rúbrica", level=2)
tabla(["Criterio", "Evidencia", "Resultado"], [
    ("1. IaC con cifrado y bloqueo de acceso (25 pts)", "Fase 1, 1.1 a 1.6",
     "script.tf: AES-256, bloqueo ×4 y política explícita; validado por CLI (IsPublic: false)"),
    ("2. Contenedores y Trivy (20 pts)", "Fase 2, 2.1 a 2.6",
     f"node:14 con {c14} críticas → node:18 endurecido con {cf} críticas"),
    ("3. JWT y OWASP ZAP (25 pts)", "Fase 3, 3.1 a 3.9", "Middleware en 3 endpoints sensibles, 13 pruebas y reporte de ZAP"),
    ("4. Política IAM restrictiva (20 pts)", "Fase 4, 4.1 a 4.4", "Solo s3:GetObject para rol-lector-reportes, con ejemplo aplicado"),
    ("5. Diagrama de arquitectura (10 pts)", "Fase 5", "S3, contenedor, API, autenticación e IAM con flujo de datos"),
], [5.0, 3.4, 8.2])

doc.add_heading("Repositorio y archivos de soporte", level=2)
rich([("Todo el código está en ", ""), (REPO, "b"), (":", "")])
for t in ["actividad3/fase1-iac: script.tf",
          "actividad3/fase2-contenedores: escanear.sh y reportes de Trivy (txt y json) de las tres imágenes",
          "actividad3/fase3-api: código de la API y del sitio, Dockerfile.vulnerable, Dockerfile.node18-sin-endurecer, "
          "Dockerfile, openapi.yaml, pruebas/probar-api.sh y reporte de ZAP (zap/reporte-zap.html)",
          "actividad3/fase4-iam: politica-lector.json, confianza-rol.json, iam.tf y ejemplo-uso.sh",
          "actividad3/fase5-diagrama: arquitectura.svg y arquitectura.png"]:
    doc.add_paragraph(t, style="List Bullet")
doc.add_page_break()

# ===================== ANEXO: práctica en clase =====================
doc.add_heading("Anexo. Práctica en clase: bucket S3 seguro con Terraform y LocalStack", level=1)
H_OFF = 1

# ---------------- Propósito ----------------
doc.add_heading("Propósito", level=1)
para("Construir un bucket S3 simulado con Terraform, declarar su cifrado AES-256 y los cuatro controles de "
     "bloqueo de acceso público, y verificar qué quedó realmente configurado y cómo se comporta el servicio. "
     "Todo corre en mi computadora con LocalStack (http://localhost:4566); no se usa AWS real.")
rich([("Repositorio público: ", "b"), (REPO, "")])
rich([("Datos del laboratorio: ", "b"), ("bucket ", ""), ("actividad3-seguro-local", "c"), (" · región ", ""),
      ("us-east-1", "c"), (" · endpoint ", ""), ("http://localhost:4566", "c"), (" · cifrado SSE-S3 AES256 · 3 recursos de Terraform.", "")])
para("Nota sobre las capturas: las de Docker Desktop y del navegador son capturas de pantalla. Las de la terminal "
     "muestran la salida real de cada comando, tal como se ejecutó en mi Mac.", italic=True, size=10)

# ---------------- 1. Registro ----------------
doc.add_heading("1. Registro gratuito en LocalStack", level=1)
step("1.1 Plan Hobby (Free)",
     "Entré a localstack.cloud/pricing, seleccioné LocalStack for AWS y elegí el plan Hobby — Free (no Base, Ultimate "
     "ni prueba de pago). Creé mi cuenta personal e inicié sesión. En Billing se ve mi suscripción activa: Hobby (AWS), "
     "de uso no comercial, sin pagar el plan Base.",
     [("hobby", None, "Suscripción Hobby activa, sin datos de cuenta ni token")])
step("1.2 Token de autenticación",
     [("Localicé mi token en app.localstack.cloud y lo guardé solo en un archivo ", ""), (".env", "c"),
      (" en mi computadora. Ese archivo está en ", ""), (".gitignore", "c"),
      (", así que nunca aparece en capturas, en el repositorio ni en este documento.", "")], [])

# ---------------- 2/3. Herramientas ----------------
doc.add_heading("2. Herramientas e instalación (macOS)", level=1)
step("2.1 Instalación con Homebrew",
     [("Mi Mac es Apple Silicon (arm64) con Docker Desktop. Instalé Terraform desde el tap oficial de HashiCorp con ", ""),
      ("brew install hashicorp/tap/terraform", "c"), ("; AWS CLI v2 ya lo tenía instalado con Homebrew.", "")],
     ["00-instalacion"])
step("2.2 Investigación: compatibilidad y virtualización",
     [("Según la documentación oficial de Docker, Docker Desktop para Mac soporta la versión actual de macOS y las dos "
       "anteriores, y pide al menos 4 GB de RAM, tanto en Apple silicon como en Intel. En Mac no hay que activar la "
       "virtualización en BIOS como en Windows (VT-x/AMD-V + WSL2): Docker Desktop corre una máquina virtual Linux "
       "ligera con el framework de virtualización de macOS. Mi equipo cumple: MacBook Air M2 (arm64), 8 GB de RAM, "
       "macOS 26.6.2 e hipervisor disponible (", ""), ("kern.hv_support = 1", "c"),
      ("). La VM de Docker tiene 8 CPUs y unos 4 GB, y la imagen de LocalStack es ", ""), ("linux/arm64", "c"),
      (", nativa para Apple silicon, así que no necesita emulación con Rosetta.", "")],
     ["00b-compatibilidad"])
step("2.3 Investigación: permisos",
     [("Mi usuario pertenece al grupo ", ""), ("admin", "c"),
      (", que es el que permite instalar Docker Desktop y Homebrew. En macOS no existe el grupo ", ""), ("docker", "c"),
      (" de Linux (allí hay que agregar al usuario y cerrar y abrir sesión): Docker Desktop crea el socket en mi carpeta "
       "personal (", ""), ("~/.docker/run/docker.sock", "c"), (") y enlaza ", ""), ("/var/run/docker.sock", "c"),
      (" hacia él, por eso puedo usar ", ""), ("docker", "c"), (" sin ", ""), ("sudo", "c"), (".", "")],
     ["00c-permisos"])
doc.add_heading("Comparación por sistema operativo", level=3)
t = doc.add_table(rows=1, cols=4)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for c, h in zip(t.rows[0].cells, ["", "Windows 10/11", "macOS (mi caso)", "Linux (Ubuntu/Debian)"]):
    c.text = h
for row in [("Docker", "Docker Desktop + WSL2", "Docker Desktop", "Docker Engine + Compose por APT"),
            ("Virtualización", "Activar VT-x/AMD-V en BIOS y WSL2", "Framework de virtualización de macOS (nada que activar)", "Nativo (contenedores en el kernel)"),
            ("Permisos", "Administrador para instalar", "Usuario admin; socket en ~/.docker", "Grupo docker y volver a iniciar sesión"),
            ("Terraform / AWS CLI", "Instaladores oficiales", "Homebrew (tap de HashiCorp)", "Repo APT de HashiCorp / curl")]:
    cells = t.add_row().cells
    for c, v in zip(cells, row):
        c.text = v
for r in t.rows:
    for i, c in enumerate(r.cells):
        c.width = [Cm(3.2), Cm(4.3), Cm(4.6), Cm(4.6)][i]
        for p in c.paragraphs:
            for run in p.runs:
                run.font.size = Pt(9.5)
                if i == 0 or r is t.rows[0]:
                    run.bold = True
para()

doc.add_heading("3. Verificar instalación y servicios", level=1)
step("3.1 Versiones de las herramientas",
     "Comprobé las versiones: Docker 29.9.2, Docker Compose v5.6.1, Terraform 1.17.1 y AWS CLI 2.34.16.",
     ["01-versiones"])
step("3.2 Servicio Docker activo y contenedores sin errores de permisos",
     [("Verifiqué que el motor de Docker responde (", ""), ("docker info", "c"),
      ("), que los procesos de Docker Desktop están corriendo y que ", ""), ("docker ps", "c"),
      (" lista contenedores sin errores de permisos. En macOS no hace falta el grupo ", ""), ("docker", "c"),
      (" de Linux: Docker Desktop gestiona el acceso al socket.", "")],
     ["02-docker-activo"])
step("3.3 Docker Desktop",
     "En Docker Desktop se ve el motor en estado \"Engine running\" y la imagen localstack/localstack descargada.",
     ["05-docker-imagen"])
step("3.4 Puerto 4566 libre",
     [("Con ", ""), ("lsof", "c"), (" confirmé que ningún proceso estaba usando el puerto 4566 antes de levantar LocalStack.", "")],
     ["03-puerto-4566"])

# ---------------- 5. Laboratorio ----------------
doc.add_heading("4. Desarrollo del laboratorio", level=1)
doc.add_heading("Fase A · Levantar LocalStack", level=2)
step("Paso 1. Directorio de trabajo exclusivo",
     [("Creé la carpeta ", ""), ("actividad3-s3-terraform-localstack", "c"),
      (" solo para este laboratorio; es también el repositorio de Git.", "")],
     ["04-directorio"], level=3)
step("Paso 2. Docker Compose",
     [("Escribí ", ""), ("compose.yaml", "c"), (": ejecuta LocalStack solo con S3 (", ""), ("SERVICES=s3", "c"),
      ("), publica el puerto 4566 únicamente en ", ""), ("127.0.0.1", "c"), (" y recibe el token por la variable de entorno ", ""),
      ("LOCALSTACK_AUTH_TOKEN", "c"), (". En el repo solo va ", ""), (".env.example", "c"), (" con un valor de ejemplo.", "")],
     ["05-code-compose"], level=3)
step("Paso 2.1 .gitignore",
     [("Para no publicar secretos excluí ", ""), (".env", "c"), (", los ", ""), ("*.tfstate", "c"), (", la carpeta ", ""),
      (".terraform/", "c"), (" y los planes guardados.", "")],
     ["05b-code-gitignore"], level=3)
step("Paso 2.2 Compose exige el token",
     [("Antes de crear el ", ""), (".env", "c"), (" probé ", ""), ("docker compose up -d", "c"),
      (": Compose se detiene porque la variable es obligatoria. Así el token nunca queda escrito en el código.", "")],
     ["06-compose-sin-token"], level=3)
step("Paso 3. Iniciar en segundo plano",
     [("Con el token ya en ", ""), (".env", "c"), (" (ignorado por Git) inicié LocalStack en segundo plano con ", ""),
      ("docker compose up -d", "c"), (".", "")],
     ["07-compose-up"], level=3)
step("Paso 3.1 Estado saludable y endpoint de salud",
     [("El contenedor aparece como ", ""), ("Up (healthy)", "c"), (" escuchando en ", ""), ("127.0.0.1:4566", "c"),
      (", y el endpoint ", ""), ("/_localstack/health", "c"), (" reporta ", ""), ("\"s3\": \"available\"", "c"),
      (". Tuve que ajustar el healthcheck porque la imagen no trae curl: ahora usa Python.", "")],
     ["07b-salud", "07c-docker-contenedor"], level=3)

doc.add_heading("Fase B · Definir con Terraform", level=2)
step("Paso 4. Provider AWS hacia LocalStack",
     [("En ", ""), ("providers.tf", "c"), (" configuré la región ", ""), ("us-east-1", "c"), (", credenciales ficticias (", ""),
      ("test", "c"), (") y el endpoint S3 ", ""), ("http://localhost:4566", "c"), (". En ", ""), ("variables.tf", "c"),
      (" agregué una validación que rechaza cualquier endpoint que no sea localhost:4566, para que las pruebas no apunten por error a AWS real.", "")],
     ["08a-code-providers-a", "08a-code-providers-b"], level=3)
step("Paso 5. Bucket, cifrado y bloqueo de acceso público",
     [("En ", ""), ("main.tf", "c"), (" definí los tres recursos: el bucket ", ""), ("actividad3-seguro-local", "c"),
      (", el cifrado SSE-S3 ", ""), ("AES256", "c"), (" y los cuatro controles de bloqueo (", ""),
      ("block_public_acls", "c"), (", ", ""), ("ignore_public_acls", "c"), (", ", ""), ("block_public_policy", "c"),
      (", ", ""), ("restrict_public_buckets", "c"), (").", "")],
     ["08b-code-main"], level=3)
step("Paso 6. Inicializar",
     [("terraform init", "c"), (" descargó el provider hashicorp/aws v6.72.0 y creó ", ""), (".terraform.lock.hcl", "c"),
      (" para fijar la versión.", "")],
     ["08-terraform-init"], level=3)
step("Paso 6.1 Validar",
     [("terraform fmt -check", "c"), (" confirmó el formato y ", ""), ("terraform validate", "c"), (" que la configuración es válida.", "")],
     ["09-terraform-validate"], level=3)
step("Paso 6.2 Revisar el plan",
     [("Revisé el plan antes de aplicar: crea exactamente ", ""), ("3 recursos", "b"),
      (" (bucket, cifrado AES256 y bloqueo público con los 4 controles en true) y no cambia ni destruye nada.", "")],
     ["10-terraform-plan-a", "10-terraform-plan-b"], level=3)
step("Paso 7. Aplicar",
     [("Apliqué el plan revisado con ", ""), ("terraform apply tfplan", "c"), (": ", ""),
      ("Apply complete! Resources: 3 added", "b"), (".", "")],
     ["11-terraform-apply"], level=3)
step("Paso 7.1 Verificar los recursos creados",
     [("terraform state list", "c"), (" muestra los tres recursos administrados y ", ""), ("terraform output", "c"),
      (" el nombre, ARN y algoritmo de cifrado.", "")],
     ["12-terraform-state"], level=3)

doc.add_heading("Fase C · Comprobar con AWS CLI", level=2)
step("Paso 8. Listado de buckets",
     [("Usé credenciales ficticias y siempre ", ""), ("--endpoint-url http://localhost:4566", "c"),
      (" de forma explícita. El bucket aparece en el listado.", "")],
     ["13-cli-buckets"], level=3)
step("Paso 8.1 Cifrado",
     [("get-bucket-encryption", "c"), (" responde ", ""), ("SSEAlgorithm: AES256", "b"), (".", "")],
     ["14-cli-cifrado"], level=3)
step("Paso 8.2 Los cuatro controles de bloqueo público",
     [("get-public-access-block", "c"), (" muestra los cuatro controles en ", ""), ("true", "b"), (".", "")],
     ["15-cli-bloqueo"], level=3)
step("Paso 9. Subir un archivo de prueba",
     [("Creé ", ""), ("prueba.txt", "c"), (" (sin información real), lo subí al bucket y aparece en el listado con 117 bytes. ", ""),
      ("head-object", "c"), (" confirma que el objeto quedó cifrado con AES256.", "")],
     ["16-cli-subida"], level=3)
step("Paso 10. Descarga anónima (sin firmar)",
     [("Intenté descargar el archivo sin firmar la solicitud (", ""), ("--no-sign-request", "c"), (" y ", ""), ("curl", "c"),
      ("). Resultado real: ", ""), ("PERMITIDA (HTTP 200)", "b"),
      (". En AWS real se rechazaría con 403 AccessDenied, porque no hay ninguna política ni ACL que dé acceso anónimo. "
       "LocalStack emula la API y guarda la configuración, pero según su documentación oficial la aplicación de IAM "
       "está desactivada por defecto y todas las APIs se pueden usar sin autenticación. Esa función se activa con "
       "ENFORCE_IAM=1 y solo viene en los planes Base y Ultimate, no en Hobby. Por eso lo trato como una limitación del "
       "simulador, no como una exposición real, hasta tener una validación independiente.", "")],
     ["17-cli-anonimo"], level=3)
step("Paso 11. Estado de la política del bucket",
     [("get-bucket-policy", "c"), (" devuelve ", ""), ("NoSuchBucketPolicy", "b"),
      (": el bucket no tiene política. Esto no confirma exposición pública; al contrario, no existe ninguna regla que "
       "otorgue acceso a \"Principal\": \"*\", y block_public_policy impediría agregar una política pública.", "")],
     ["18-cli-politica"], level=3)

doc.add_heading("Complementos", level=2)
step("Repositorio de Git",
     [("El repositorio tiene ", ""), ("compose.yaml", "c"), (", ", ""), ("providers.tf", "c"), (", ", ""), ("main.tf", "c"),
      (", variables, outputs, el script de verificación y un ", ""), ("README.md", "c"),
      (" con descripción, requisitos e instrucciones. Comprobé que ", ""), (".env", "c"), (" y el estado de Terraform están ignorados y no se versionan.", "")],
     ["20-git-local"], level=3)
step("Repositorio público en GitHub",
     [("Creé el repositorio público con ", ""), ("gh repo create --public", "c"), (" y subí la rama main. Después verifiqué "
      "sin iniciar sesión que la URL responde HTTP 200, que la visibilidad es PUBLIC y que solo están los archivos del "
      "laboratorio (sin .env ni tfstate): ", ""), (REPO, "b")],
     [("21-github-push", None, "Creación del repositorio y push"), ("22-github-publico", None, "Verificación de acceso público")],
      level=3)
step("Dashboard de LocalStack",
     "Abrí app.localstack.cloud en la misma Mac donde corre Docker, con la instancia localhost.localstack.cloud:4566. "
     "En el Resource Browser de S3 aparece el bucket actividad3-seguro-local en us-east-1 con el archivo prueba.txt "
     "(117 bytes), el mismo que subí con AWS CLI. Revisé también la pestaña Permissions: en el Dashboard solo ofrece "
     "editar la configuración CORS, y no muestra el cifrado ni el bloqueo de acceso público. Por eso esas configuraciones "
     "las verifiqué con AWS CLI (pasos 8.1 y 8.2). No envié ningún cambio de CORS, para que el bucket siga igual a lo "
     "declarado en Terraform.",
     [("dashboard", None, "Bucket y archivo en el Dashboard de LocalStack")], level=3)

# ---------------- Conclusión ----------------
doc.add_heading("Conclusión", level=1)
para("Esta práctica me dejó clara la diferencia entre tres cosas que parecen lo mismo:")
for t, d in [("Infraestructura declarada: ", "lo que escribí en Terraform (main.tf). Es la intención: un bucket con AES256 y los cuatro bloqueos."),
             ("Configuración consultada: ", "lo que la API responde cuando la consulto con AWS CLI. Aquí coincidió con lo declarado: AES256 y los cuatro controles en true."),
             ("Seguridad efectivamente aplicada: ", "lo que pasa de verdad cuando alguien intenta entrar. Aunque la configuración decía \"bloqueado\", la descarga anónima funcionó, porque LocalStack no hace cumplir las reglas de autorización como AWS.")]:
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(t)
    r.bold = True
    p.add_run(d)
para("Que algo esté declarado y que la API lo reporte no prueba que se cumpla. La seguridad hay que validarla con "
     "pruebas de comportamiento y, en un entorno real, con una validación independiente. Además, cuidé los secretos: "
     "el token solo vive en .env, nunca en el repositorio ni en las capturas, y ningún comando apuntó a AWS de producción.")

H_OFF = 0
doc.add_heading("Referencias", level=1)
for t, u in [("LocalStack · Precios y planes", "https://localstack.cloud/pricing"),
             ("LocalStack · Auth Token", "https://docs.localstack.cloud/aws/getting-started/auth-token/"),
             ("LocalStack · IAM Policy Enforcement", "https://docs.localstack.cloud/aws/capabilities/security-testing/iam-policy-enforcement/"),
             ("Docker · Instalar Docker Desktop en Mac", "https://docs.docker.com/desktop/setup/install/mac-install/"),
             ("Terraform · Instalación", "https://developer.hashicorp.com/terraform/install"),
             ("Terraform · Provider AWS (aws_s3_bucket_public_access_block)", "https://registry.terraform.io/providers/hashicorp/aws/latest/docs"),
             ("AWS CLI · Documentación", "https://docs.aws.amazon.com/cli/"),
             ("AWS · Políticas de bucket y bloqueo de acceso público en S3", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html"),
             ("AWS IAM · Mínimo privilegio y roles", "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"),
             ("Trivy · Documentación", "https://trivy.dev/latest/docs/"),
             ("Node.js · Calendario de versiones", "https://nodejs.org/en/about/previous-releases"),
             ("jsonwebtoken · Documentación", "https://github.com/auth0/node-jsonwebtoken"),
             ("OWASP ZAP · Documentación", "https://www.zaproxy.org/docs/")]:
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(t + ": ")
    r.bold = True
    p.add_run(u)


# --- Ajustes finales: todo el texto en Arial como la Actividad 2 ---
for p in doc.paragraphs[12:]:
    if p.style.name in ("List Bullet",):
        for r in p.runs:
            fuente(r, ARIAL, 12)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    fuente(r, ARIAL, 10.5, bold=(row is t.rows[0]))
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print("guardado", OUT, "figuras:", _figura[0])
