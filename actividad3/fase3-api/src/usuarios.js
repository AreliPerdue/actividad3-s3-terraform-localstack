// Usuarios de demostración. Las contraseñas llegan por variable de entorno y aquí
// solo se guarda su hash con scrypt + sal aleatoria; se comparan en tiempo constante.
const crypto = require('node:crypto');
const { usuariosDemo } = require('./config');

function hashear(clave, sal = crypto.randomBytes(16)) {
  return { sal, hash: crypto.scryptSync(clave, sal, 64) };
}

const usuarios = new Map(
  usuariosDemo.map(({ usuario, rol, nombre, clave }) => [usuario, { usuario, rol, nombre, ...hashear(clave) }])
);

// Hash ficticio para que un usuario inexistente tarde lo mismo que uno real
const relleno = hashear(crypto.randomBytes(16).toString('hex'));

function verificarCredenciales(usuario, clave) {
  if (typeof usuario !== 'string' || typeof clave !== 'string') return null;
  const registro = usuarios.get(usuario) || null;
  const { sal, hash } = registro || relleno;
  const intento = crypto.scryptSync(clave, sal, 64);
  const coincide = crypto.timingSafeEqual(intento, hash);
  return registro && coincide ? { usuario: registro.usuario, rol: registro.rol, nombre: registro.nombre } : null;
}

function listar() {
  return [...usuarios.values()].map(({ usuario, rol, nombre }) => ({ usuario, rol, nombre }));
}

module.exports = { verificarCredenciales, listar };
