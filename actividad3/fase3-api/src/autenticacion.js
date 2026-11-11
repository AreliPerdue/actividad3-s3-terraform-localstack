// Middleware de autenticación JWT y control de roles.
const jwt = require('jsonwebtoken');
const { jwt: cfg } = require('./config');

function emitirToken({ usuario, rol }) {
  return jwt.sign({ rol }, cfg.secreto, {
    algorithm: 'HS256',
    subject: usuario,
    issuer: cfg.emisor,
    audience: cfg.audiencia,
    expiresIn: cfg.duracion,
  });
}

// Exige "Authorization: Bearer <token>" y valida firma, algoritmo, emisor, audiencia y expiración.
function verificarToken(req, res, next) {
  const [esquema, token] = (req.get('authorization') || '').split(' ');
  if (esquema !== 'Bearer' || !token) {
    return res.status(401).json({ error: 'Falta el token (Authorization: Bearer <token>)' });
  }
  try {
    const datos = jwt.verify(token, cfg.secreto, {
      algorithms: ['HS256'], // evita "alg: none" y la confusión de algoritmos
      issuer: cfg.emisor,
      audience: cfg.audiencia,
    });
    req.usuario = { usuario: datos.sub, rol: datos.rol };
    return next();
  } catch (e) {
    const motivo = e.name === 'TokenExpiredError' ? 'Token expirado' : 'Token inválido';
    return res.status(401).json({ error: motivo });
  }
}

// Se usa después de verificarToken: 403 si el rol no está permitido.
function exigirRol(...roles) {
  return (req, res, next) =>
    roles.includes(req.usuario?.rol) ? next() : res.status(403).json({ error: 'Tu rol no tiene permiso' });
}

module.exports = { emitirToken, verificarToken, exigirRol };
