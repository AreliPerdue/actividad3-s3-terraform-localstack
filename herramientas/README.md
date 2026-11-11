# Herramientas de evidencias

Scripts con los que se generaron las capturas y el documento de entrega.

| Archivo | Para qué sirve |
|---|---|
| `cap.sh` | Ejecuta comandos en una carpeta del repo y guarda el prompt, el comando y la **salida real** en `evidencias/NOMBRE.txt`. Uso: `CAPDIR=actividad3/fase1-iac ./cap.sh A1-4-apply 'terraform apply tfplan'` |
| `render.py` | Convierte cada `evidencias/*.txt` (con colores ANSI) en una imagen con aspecto de ventana de Terminal (`capturas/*.png`) |
| `capturas-sitio.js` | Recorre el sitio web en un Chrome headless aislado (perfil temporal) y guarda capturas reales en `capturas-reales/`. Lee las claves de prueba de `actividad3/fase3-api/.env` y no las escribe en ningún lado |
| `generar_docx.py` | Arma el `.docx` de entrega con las capturas. Usa como plantilla la portada y los estilos de un documento anterior de la autora (`plantilla/portada.docx`, no se versiona) |
| `evidencias/` | Salidas reales de los comandos de la Actividad 3 (`A*`) y de la práctica de clase (números) |

Las carpetas `capturas/`, `capturas-reales/` y `plantilla/` se generan en local y están en `.gitignore`.

```bash
cd herramientas
python3 render.py                                   # evidencias/*.txt -> capturas/*.png
npm install && (set -a; source ../actividad3/fase3-api/.env; set +a; node capturas-sitio.js)
python3 generar_docx.py "Actividad 3.docx"          # requiere python-docx y plantilla/portada.docx
```
