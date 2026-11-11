// El token vive solo en memoria (no en localStorage): si se recarga la página, hay que volver a entrar.
let token = null;
const $ = (id) => document.getElementById(id);

async function api(ruta, opciones = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const r = await fetch(ruta, { ...opciones, headers });
  let cuerpo = {};
  try { cuerpo = await r.json(); } catch { /* sin cuerpo */ }
  return { status: r.status, cuerpo };
}

function mostrar(id, texto, tipo) {
  const el = $(id);
  el.textContent = texto; // textContent: nunca se interpreta HTML que venga de la API
  el.className = `mensaje ${tipo || ''}`;
}

function entrar(datos) {
  token = datos.token;
  $('quien').textContent = `${datos.nombre} · rol: ${datos.rol}`;
  $('sesion').classList.remove('oculto');
  $('vista-login').classList.add('oculto');
  $('vista-panel').classList.remove('oculto');
  cargarPerfil();
}

function salir() {
  token = null;
  ['perfil', 'usuarios', 'reporte'].forEach((id) => { $(id).textContent = ''; });
  ['estado-usuarios', 'estado-reporte', 'msg-login'].forEach((id) => mostrar(id, ''));
  $('sesion').classList.add('oculto');
  $('vista-panel').classList.add('oculto');
  $('vista-login').classList.remove('oculto');
  $('form-login').reset();
}

async function cargarPerfil() {
  const { status, cuerpo } = await api('/api/perfil');
  $('perfil').textContent = `HTTP ${status}\n${JSON.stringify(cuerpo, null, 2)}`;
}

async function consultar(ruta, salida, estado) {
  const { status, cuerpo } = await api(ruta);
  if (status === 200) {
    mostrar(estado, `HTTP 200 · acceso permitido`, 'ok');
    $(salida).textContent = JSON.stringify(cuerpo, null, 2);
  } else {
    mostrar(estado, `HTTP ${status} · ${cuerpo.error || 'error'}`, 'error');
    $(salida).textContent = '';
  }
}

$('form-login').addEventListener('submit', async (e) => {
  e.preventDefault();
  const { status, cuerpo } = await api('/api/sesion', {
    method: 'POST',
    body: JSON.stringify({ usuario: $('usuario').value.trim(), clave: $('clave').value }),
  });
  if (status === 200) entrar(cuerpo);
  else mostrar('msg-login', `HTTP ${status} · ${cuerpo.error || 'error'}`, 'error');
});

$('salir').addEventListener('click', salir);
$('ver-usuarios').addEventListener('click', () => consultar('/api/usuarios', 'usuarios', 'estado-usuarios'));
$('ver-reporte').addEventListener('click', () => consultar('/api/reportes/resumen.txt', 'reporte', 'estado-reporte'));
