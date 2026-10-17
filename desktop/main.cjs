const { app, BrowserWindow, dialog, shell, Menu } = require('electron');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const readline = require('node:readline');
let server, window, origin, quitting = false;
const root = path.resolve(__dirname, '..');
const development = app.getVersion().includes('-');
app.setName(development ? 'Paperloom Dev' : 'Paperloom');
if (development) app.setPath('userData', path.join(app.getPath('appData'), 'Paperloom Dev'));
if (process.env.PAPERLOOM_PROFILE) app.setPath('userData', path.resolve(process.env.PAPERLOOM_PROFILE));
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => { if (window) { window.restore(); window.show(); window.focus(); } });
  app.whenReady().then(start).catch(error => {
    dialog.showErrorBox('Paperloom 실행 오류', error.message);
    app.quit();
  });
}
function external(url) {
  try { if (['https:', 'http:'].includes(new URL(url).protocol)) shell.openExternal(url).catch(() => {}); } catch {}
}
async function start() {
  const data = app.isPackaged ? path.join(app.getPath('userData'), 'data') : path.join(root, 'data');
  fs.mkdirSync(data, { recursive: true });
  const seed = path.join(process.resourcesPath, 'seed');
  if (app.isPackaged && !fs.existsSync(path.join(data, 'library.sqlite3'))) {
    if (fs.existsSync(path.join(seed, 'pdfs'))) fs.cpSync(path.join(seed, 'pdfs'), path.join(data, 'pdfs'), { recursive: true });
    fs.copyFileSync(path.join(seed, 'library.sqlite3'), path.join(data, 'library.sqlite3.tmp'));
    fs.renameSync(path.join(data, 'library.sqlite3.tmp'), path.join(data, 'library.sqlite3'));
  }
  const researchRuns = path.join(process.resourcesPath, 'research-seed-runs');
  if (app.isPackaged && fs.existsSync(researchRuns)) fs.cpSync(researchRuns, path.join(data, 'research', 'runs'), { recursive: true, force: false, errorOnExist: false });
  const executable = app.isPackaged
    ? path.join(process.resourcesPath, 'backend', process.platform === 'win32' ? 'paperloom-server.exe' : 'paperloom-server')
    : path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  const portFile = path.join(app.getPath('userData'), 'server-port.json');
  let preferredPort = 0;
  try { const saved = JSON.parse(fs.readFileSync(portFile, 'utf8')); if (Number.isInteger(saved) && saved > 0 && saved < 65536) preferredPort = saved; } catch {}
  const log = fs.openSync(path.join(app.getPath('userData'), 'server.log'), 'a');
  server = spawn(executable, app.isPackaged ? [] : [path.join(root, 'app.py')], {
    env: { ...process.env, PAPERLOOM_DATA: data, PORT: String(preferredPort), PAPERLOOM_PORT_FALLBACK: '1', PYTHONUNBUFFERED: '1' },
    stdio: ['ignore', 'pipe', log], windowsHide: true,
  });
  fs.closeSync(log);
  origin = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('서버 시작 시간이 초과되었습니다.')), 30000);
    const lines = readline.createInterface({ input: server.stdout });
    lines.on('line', line => {
      const match = line.match(/^Paperloom → (http:\/\/127\.0\.0\.1:\d+)$/);
      if (match) { clearTimeout(timer); fs.writeFileSync(portFile, JSON.stringify(Number(new URL(match[1]).port))); resolve(match[1]); }
    });
    server.once('error', error => { clearTimeout(timer); reject(error); });
    server.once('exit', code => {
      clearTimeout(timer);
      reject(new Error(`서버가 종료되었습니다 (${code}).`));
      if (origin && !quitting) { dialog.showErrorBox('Paperloom', '서버가 종료되었습니다. 앱을 다시 실행하세요.'); app.quit(); }
    });
  });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { role: 'fileMenu' }, { role: 'editMenu' }, { role: 'viewMenu' }, { role: 'windowMenu' },
    { label: '라이브러리', submenu: [{ label: '데이터 폴더 열기', click: () => shell.openPath(data) }] },
  ]));
  await createWindow();
  app.on('activate', () => { if (!window) createWindow(); });
}
async function createWindow() {
  window = new BrowserWindow({ width: 1440, height: 960, minWidth: 960, minHeight: 640,
    title: 'Paperloom', backgroundColor: '#f8f7f4', show: false,
    webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true },
  });
  window.webContents.session.setPermissionRequestHandler((_wc, _permission, callback) => callback(false));
  window.webContents.setWindowOpenHandler(({ url }) => { external(url); return { action: 'deny' }; });
  window.webContents.on('will-navigate', (event, url) => {
    if (new URL(url).origin !== origin) { event.preventDefault(); external(url); }
  });
  window.on('closed', () => { window = null; });
  await window.loadURL(origin);
  window.show();
}
app.on('window-all-closed', () => app.quit());
app.on('before-quit', event => {
  if (quitting) return;
  quitting = true;
  if (server && server.exitCode === null && server.signalCode === null) {
    event.preventDefault();
    const timer = setTimeout(() => { server.kill('SIGKILL'); app.exit(); }, 3000);
    server.once('exit', () => { clearTimeout(timer); app.exit(); });
    server.kill();
  }
});
