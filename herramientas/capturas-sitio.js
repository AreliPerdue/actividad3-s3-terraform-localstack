// Recorre el sitio en un Chrome headless aislado (perfil temporal) y guarda capturas reales.
const puppeteer = require('puppeteer-core');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');

const OUT = path.join(__dirname, 'capturas-reales');
fs.mkdirSync(OUT, { recursive: true });
const URL = 'http://localhost:3000/';
const { CLAVE_DEMO_ADMIN, CLAVE_DEMO_LECTOR } = process.env;

(async () => {
  const perfil = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-capturas-'));
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    userDataDir: perfil,
    args: ['--no-first-run', '--no-default-browser-check'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1100, height: 760, deviceScaleFactor: 1.5 });
  const shot = async (n) => { await new Promise((r) => setTimeout(r, 400)); await page.screenshot({ path: path.join(OUT, `${n}.png`), fullPage: true }); console.log('ok', n); };
  const login = async (u, c) => {
    await page.$eval('#usuario', (e) => (e.value = ''));
    await page.$eval('#clave', (e) => (e.value = ''));
    await page.type('#usuario', u);
    await page.type('#clave', c);
    await page.$eval('#form-login button', (b) => b.click());
  };

  await page.goto(URL, { waitUntil: 'networkidle0' });
  if (process.argv[2] !== 'admin') {
  await shot('W1-login');

  await login('admin', 'clave-equivocada');
  await page.waitForFunction(() => document.querySelector('#msg-login').textContent.includes('HTTP'));
  await page.$eval('#clave', (e) => (e.value = '')); // no dejar nada escrito en la captura
  await shot('W2-login-incorrecto');

  await login('lector', CLAVE_DEMO_LECTOR);
  await page.waitForSelector('#vista-panel:not(.oculto)');
  await page.waitForFunction(() => document.querySelector('#perfil').textContent.includes('HTTP'));
  await page.$eval('#ver-usuarios', (b) => b.click());
  await page.$eval('#ver-reporte', (b) => b.click());
  await page.waitForFunction(() => document.querySelector('#estado-reporte').textContent.includes('HTTP'));
  await shot('W3-lector-403');

  await page.$eval('#salir', (b) => b.click());
  }
  await login('admin', CLAVE_DEMO_ADMIN);
  await page.waitForSelector('#vista-panel:not(.oculto)');
  await page.$eval('#ver-usuarios', (b) => b.click());
  await page.$eval('#ver-reporte', (b) => b.click());
  await page.waitForFunction(() => document.querySelector('#estado-reporte').textContent.includes('HTTP'));
  await shot('W4-admin-200');

  await browser.close();
  fs.rmSync(perfil, { recursive: true, force: true });
})().catch((e) => { console.error(e); process.exit(1); });
