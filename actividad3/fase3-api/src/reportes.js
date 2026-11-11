// Lee reportes del bucket cifrado asumiendo el rol de mínimo privilegio (solo s3:GetObject).
const { STSClient, AssumeRoleCommand } = require('@aws-sdk/client-sts');
const { S3Client, GetObjectCommand } = require('@aws-sdk/client-s3');
const { aws } = require('./config');

const base = { region: aws.region, endpoint: aws.endpoint };
const sts = new STSClient(base);

async function clienteConRol() {
  const { Credentials: c } = await sts.send(
    new AssumeRoleCommand({ RoleArn: aws.rolLector, RoleSessionName: 'api-reportes', DurationSeconds: 900 })
  );
  return new S3Client({
    ...base,
    forcePathStyle: true,
    credentials: { accessKeyId: c.AccessKeyId, secretAccessKey: c.SecretAccessKey, sessionToken: c.SessionToken },
  });
}

async function leerReporte(nombre) {
  if (!/^[a-z0-9-]+\.txt$/.test(nombre)) throw Object.assign(new Error('Nombre no válido'), { status: 400 });
  const s3 = await clienteConRol();
  const r = await s3.send(new GetObjectCommand({ Bucket: aws.bucket, Key: `reportes/${nombre}` }));
  return { nombre, cifrado: r.ServerSideEncryption, contenido: await r.Body.transformToString() };
}

module.exports = { leerReporte };
