#!/usr/bin/env node
/**
 * 真实视口交互断言：CDP 强制 390x844（--window-size 会被夹到 500，不可信）。
 * 断言从 spec.assertions 读，换业务只改 spec。
 * 用法: node verify_viewport.mjs --spec templates/app.spec.json --url http://127.0.0.1:8765/index.html
 */
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';

const argv = process.argv.slice(2);
const arg = k => {
  const i = argv.indexOf(k);
  return i >= 0 ? argv[i + 1] : undefined;
};
const SPEC = resolve(arg('--spec') || 'templates/app.spec.json');
const URL = arg('--url') || 'http://127.0.0.1:8765/index.html';
const WIDTH = Number(arg('--width') || 390);
const HEIGHT = Number(arg('--height') || 844);
const SHOT_PREFIX = arg('--shots') || '/tmp/h5app';
const CHROME = arg('--chrome') || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = Number(arg('--port') || 9223);
const PROFILE = '/tmp/chrome-cdp-h5app-' + PORT;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const spec = JSON.parse(readFileSync(SPEC, 'utf8'));
const assertions = spec.assertions || [];
if (!assertions.length) { console.log('[FAIL] spec 里没有 assertions'); process.exit(1); }

rmSync(PROFILE, { recursive: true, force: true });
const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars', '--no-first-run',
  '--remote-debugging-port=' + PORT, '--user-data-dir=' + PROFILE,
  '--window-size=800,900', 'about:blank'
], { stdio: 'ignore' });

let ws, seq = 0, failed = false;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, resolve);
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending.has(id)) { pending.delete(id); reject(new Error('超时 ' + method)); }
    }, 15000);
  });
}
async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
  return r.result.result.value;
}
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(SHOT_PREFIX + '-' + name + '.png', Buffer.from(r.result.data, 'base64'));
}
async function endpoint() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch('http://127.0.0.1:' + PORT + '/json/list');
      if (r.ok) {
        const page = (await r.json()).find(t => t.type === 'page');
        if (page) return page.webSocketDebuggerUrl;
      }
    } catch (_) { /* 等 Chrome 就绪 */ }
    await sleep(250);
  }
  throw new Error('CDP 未就绪');
}

function judge(op, value, expect) {
  switch (op) {
    case 'includes': return String(value).includes(String(expect));
    case 'equals': return String(value) === String(expect);
    case 'true': return value === true;
    case 'lteWidth': return Number(String(value).split('/')[0]) <= Number(expect);
    default: throw new Error('未知断言 op: ' + op);
  }
}

try {
  const url = await endpoint();
  ws = new WebSocket(url);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: WIDTH, height: HEIGHT, deviceScaleFactor: 1, mobile: true });
  await send('Page.navigate', { url: URL });
  await sleep(1500);

  const checks = [];
  const vp = await evalJs('innerWidth + "x" + innerHeight');
  checks.push(['视口回读', vp, vp === WIDTH + 'x' + HEIGHT]);

  for (const a of assertions) {
    if (a.click) await evalJs('document.querySelector(' + JSON.stringify(a.click) + ').click()');
    if (a.hash) { await evalJs('location.hash=' + JSON.stringify(a.hash)); await sleep(150); }
    const value = await evalJs(a.eval);
    checks.push([a.name, String(value).slice(0, 60), judge(a.op, value, a.expect)]);
  }

  await evalJs('location.hash="#' + spec.tabs[0].k + '"; window.scrollTo(0,0)');
  await sleep(180);
  await shot('hero');
  await evalJs('window.scrollTo(0, 620)');
  await sleep(200);
  await shot('demo');
  const usage = spec.tabs.find(t => t.k === 'usage');
  if (usage) {
    await evalJs('location.hash="#usage"; window.scrollTo(0, 560)');
    await sleep(200);
    await shot('usage');
  }

  for (const [name, value, ok] of checks) {
    console.log((ok ? 'PASS ' : 'FAIL ') + name + ' :: ' + value);
    if (!ok) failed = true;
  }
  console.log('截图: ' + SHOT_PREFIX + '-{hero,demo,usage}.png');
  console.log(failed ? 'RESULT FAIL' : 'RESULT ALL PASS (' + checks.length + ')');
} catch (e) {
  console.log('ERROR ' + (e && e.message ? e.message : String(e)));
  failed = true;
} finally {
  if (ws) { try { ws.close(); } catch (_) {} }
  try { chrome.kill('SIGKILL'); } catch (_) {}
  rmSync(PROFILE, { recursive: true, force: true });
}
process.exit(failed ? 1 : 0);
