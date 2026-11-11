const path = require('node:path');
const express = require('express');
const helmet = require('helmet');
const { puerto } = require('./config');
const { verificarCredenciales, listar } = require('./usuarios');
const { emitirToken, verificarToken, exigirRol } = require('./autenticacion');
const { leerReporte } = require('./reportes');

const app = express();
app.disable('x-powered-by');
// Cabeceras de seguridad. La CSP se define completa y sin 'unsafe-inline' ni comodines
// (corrección tras el primer escaneo de OWASP ZAP).
app.use(
  helmet({
    contentSecurityPolicy: {
      useDefaults: false,
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'"],
        imgSrc: ["'self'"],
        connectSrc: ["'self'"],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        baseUri: ["'self'"],
        formAction: ["'self'"],
        frameAncestors: ["'none'"],
      },
    },
  })
);
app.use(express.json({ limit: '10kb' }));
app.use(express.static(path.join(__dirname, '..', 'public'), { index: 'index.html' }));

// Límite simple de intentos de inicio de sesión por IP (5 por minuto)
const intentos = new Map();
function limitarIntentos(req, res, next) {
  const ahora = Date.now();
  const lista = (intentos.get(req.ip) || []).filter((t) => ahora - t < 60_000);
  if (lista.length >= 5) return res.status(429).json({ error: 'Demasiados intentos, espera un minuto' });
  lista.push(ahora);
  intentos.set(req.ip, lista);
  return next();
}

// --- Públicos ---
app.get('/api/salud', (req, res) => res.json({ estado: 'ok' }));

app.post('/api/sesion', limitarIntentos, (req, res) => {
  const usuario = verificarCredenciales(req.body?.usuario, req.body?.clave);
  if (!usuario) return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
  return res.json({ token: emitirToken(usuario), expiraEn: 900, rol: usuario.rol, nombre: usuario.nombre });
});

// --- Sensibles: requieren JWT válido ---
app.get('/api/perfil', verificarToken, (req, res) => res.json({ usuario: req.usuario.usuario, rol: req.usuario.rol }));

app.get('/api/usuarios', verificarToken, exigirRol('admin'), (req, res) => res.json(listar()));

app.get('/api/reportes/:nombre', verificarToken, exigirRol('admin'), async (req, res) => {
  try {
    res.json(await leerReporte(req.params.nombre));
  } catch (e) {
    const status = e.status || (e.name === 'NoSuchKey' ? 404 : 502);
    res.status(status).json({ error: status === 404 ? 'Reporte no encontrado' : e.status ? e.message : 'No se pudo leer S3' });
  }
});

// Rutas de API desconocidas: JSON en lugar de la página de error de Express
app.use('/api', (req, res) => res.status(404).json({ error: 'No existe' }));
// Cualquier otra ruta: 404 propio, así también lleva las cabeceras de helmet
app.use((req, res) => res.status(404).type('text/plain').send('No encontrado'));
app.use((err, req, res, next) => res.status(err.status || 500).json({ error: 'Solicitud no válida' }));

app.listen(puerto, () => console.log(`API de reportes escuchando en el puerto ${puerto}`));
