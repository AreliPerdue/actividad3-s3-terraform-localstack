// Configuración leída solo de variables de entorno: ningún secreto vive en el código.
function requerida(nombre, minimo = 1) {
  const valor = process.env[nombre];
  if (!valor || valor.length < minimo) {
    console.error(`Falta la variable ${nombre} (mínimo ${minimo} caracteres). Revisa el archivo .env`);
    process.exit(1);
  }
  return valor;
}

module.exports = {
  puerto: Number(process.env.PUERTO || 3000),
  jwt: {
    secreto: requerida('JWT_SECRETO', 32),
    emisor: 'api-reportes-actividad3',
    audiencia: 'sitio-reportes',
    duracion: '15m',
  },
  usuariosDemo: [
    { usuario: 'admin', rol: 'admin', nombre: 'Administradora de reportes', clave: requerida('CLAVE_DEMO_ADMIN', 12) },
    { usuario: 'lector', rol: 'lector', nombre: 'Usuario de consulta', clave: requerida('CLAVE_DEMO_LECTOR', 12) },
  ],
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    endpoint: process.env.AWS_ENDPOINT || 'http://localhost:4566',
    bucket: process.env.BUCKET_REPORTES || 'actividad3-reportes-cifrados',
    rolLector: process.env.ROL_LECTOR_ARN || 'arn:aws:iam::000000000000:role/rol-lector-reportes',
  },
};
