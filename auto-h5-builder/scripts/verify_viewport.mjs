#!/usr/bin/env node
/**
 * 真实视口闸门：CDP 强制视口（--window-size 会被夹到 500，不可信）。
 * ① 计算样式一致性（页内所有 .ctl 的圆角/高度/字号/主色必须统一）
 * ② spec.assertions 业务交互断言（只在主视口跑，换主题只改 spec）
 * ③ 默认双视口 390 + 1280：窄屏导航入口必须保留，桌面不能横向溢出
 * ④ 截图按「首屏 + 每个 section + 页尾」逐段输出，覆盖全页
 * 用法: node verify_viewport.mjs --spec examples/beauty.spec.json --url http://127.0.0.1:8767/index.html
 */
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';

const argv = process.argv.slice(2);
const arg = k => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : undefined; };
const SPEC = resolve(arg('--spec') || 'examples/beauty.spec.json');
const URL = arg('--url') || 'http://127.0.0.1:8765/index.html';
const HEIGHT = Number(arg('--height') || 844);
const WIDTHS = (arg('--widths') || (arg('--width') ? String(arg('--width')) : '390,1280'))
  .split(',').map(s => Number(s.trim())).filter(Boolean);
const SHOT_PREFIX = arg('--shots') || '/tmp/h5app';
const CHROME = arg('--chrome') || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = Number(arg('--port') || 9223);
const WAIT = Number(arg('--wait') || 1500);
const PROFILE = '/tmp/chrome-cdp-h5app-' + PORT;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const spec = JSON.parse(readFileSync(SPEC, 'utf8'));
const assertions = spec.assertions || [];
if (!assertions.length) { console.log('[FAIL] spec 里没有 assertions'); process.exit(1); }
if (!WIDTHS.length) { console.log('[FAIL] 没有有效视口宽度'); process.exit(1); }

rmSync(PROFILE, { recursive: true, force: true });
const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars', '--no-first-run',
  '--remote-debugging-port=' + PORT, '--user-data-dir=' + PROFILE,
  '--window-size=1400,900', 'about:blank'
], { stdio: 'ignore' });

let ws, seq = 0, failed = false;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, resolve);
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('超时 ' + method)); } }, 15000);
  });
}
async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
  return r.result.result.value;
}
async function shot(width, name) {
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(SHOT_PREFIX + '-' + width + '-' + name + '.png', Buffer.from(r.result.data, 'base64'));
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

const STYLE_PROBE = `(() => {
  const cs = e => getComputedStyle(e);
  const all = [...document.querySelectorAll('.ctl')];
  const navs = [...document.querySelectorAll('.hd-nav .nav-link')];
  const uniq = a => [...new Set(a)];
  const h = { lg: [], md: [], sm: [] };
  all.forEach(e => {
    const k = e.classList.contains('ctl--lg') ? 'lg' : e.classList.contains('ctl--sm') ? 'sm' : 'md';
    h[k].push(cs(e).height);
  });
  return JSON.stringify({
    count: all.length,
    radii: uniq(all.map(e => cs(e).borderRadius)),
    fontSizes: uniq(all.map(e => cs(e).fontSize)),
    heights: { lg: uniq(h.lg), md: uniq(h.md), sm: uniq(h.sm) },
    primaryBg: uniq(all.filter(e => e.classList.contains('ctl--primary')).map(e => cs(e).backgroundColor)),
    fieldHeights: uniq([...document.querySelectorAll('.field')].map(e => cs(e).height)),
    fieldRadii: uniq([...document.querySelectorAll('.field')].map(e => cs(e).borderRadius)),
    inlineStyles: document.querySelectorAll('[style]').length,
    navTotal: navs.length,
    navVisible: navs.filter(e => cs(e).display !== 'none').length,
    overflow: document.documentElement.scrollWidth + '/' + innerWidth,
    layout: document.body.getAttribute('data-layout')
  });
})()`;

const checks = [];
const shotNames = [];

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

  for (let wi = 0; wi < WIDTHS.length; wi++) {
    const W = WIDTHS[wi];
    const primary = wi === 0;
    const tag = W + 'px';
    await send('Emulation.setDeviceMetricsOverride',
      { width: W, height: HEIGHT, deviceScaleFactor: 1, mobile: W <= 720 });
    if (primary) {
      await send('Page.navigate', { url: URL });
      await sleep(WAIT);
    } else {
      await sleep(700);
    }
    const s = JSON.parse(await evalJs(STYLE_PROBE));
    checks.push([tag + ' 视口回读', await evalJs('innerWidth + "x" + innerHeight'),
      (await evalJs('innerWidth')) === W]);
    checks.push([tag + ' 无横向溢出', s.overflow, Number(s.overflow.split('/')[0]) <= W]);
    checks.push([tag + ' 导航入口全部可见', s.navVisible + '/' + s.navTotal,
      s.navTotal > 0 && s.navVisible === s.navTotal]);
    checks.push([tag + ' 页内圆角统一（' + s.layout + '）', s.radii.join(','), s.radii.length === 1]);
    checks.push([tag + ' 字号仅用三档 token', s.fontSizes.join(','), s.fontSizes.length <= 3]);
    checks.push([tag + ' 三档高度各自统一',
      [s.heights.lg, s.heights.md, s.heights.sm].map(x => x.length).join('/'),
      s.heights.lg.length <= 1 && s.heights.md.length <= 1 && s.heights.sm.length <= 1]);
    checks.push([tag + ' 主色按钮底色统一', s.primaryBg.join(','), s.primaryBg.length === 1]);
    checks.push([tag + ' 输入框与控件同高同圆角',
      s.fieldHeights.join(',') + ' / ' + s.fieldRadii.join(','),
      s.fieldHeights.length <= 1 && s.fieldHeights[0] === s.heights.md[0]
      && s.fieldRadii.length <= 1 && s.fieldRadii[0] === s.radii[0]]);
    checks.push([tag + ' 页面零内联样式', s.inlineStyles, s.inlineStyles === 0]);

    if (primary) {
      for (const a of assertions) {
        if (a.click) await evalJs('document.querySelector(' + JSON.stringify(a.click) + ').click()');
        if (a.hash) { await evalJs('location.hash=' + JSON.stringify(a.hash)); await sleep(150); }
        const fills = a.fills || (a.fill ? [a.fill] : []);
        for (const f of fills) {
          await evalJs('(function(){var e=document.querySelector(' + JSON.stringify(f.sel) + ');'
            + 'if(e){e.value=' + JSON.stringify(f.value) + ';'
            + 'e.dispatchEvent(new Event("input",{bubbles:true}));}})()');
        }
        const value = await evalJs(a.eval);
        checks.push([tag + ' ' + a.name, String(value).slice(0, 60), judge(a.op, value, a.expect)]);
      }
      // 逐区块截图：首屏 + 每个 section 锚点 + 页尾，保证没有一段没被目视
      await evalJs('window.scrollTo(0,0)'); await sleep(200);
      await shot(W, 'hero'); shotNames.push(W + '-hero');
      for (const sec of spec.sections) {
        const id = sec.id || sec.type;
        await evalJs('(function(){var e=document.getElementById(' + JSON.stringify(id)
          + ');if(e)e.scrollIntoView({block:"start"});})()');
        await sleep(180);
        await shot(W, id); shotNames.push(W + '-' + id);
      }
      await evalJs('window.scrollTo(0, document.body.scrollHeight)'); await sleep(200);
      await shot(W, 'bottom'); shotNames.push(W + '-bottom');
    } else {
      await evalJs('window.scrollTo(0,0)'); await sleep(200);
      await shot(W, 'hero'); shotNames.push(W + '-hero');
      await evalJs('window.scrollTo(0, document.body.scrollHeight)'); await sleep(200);
      await shot(W, 'bottom'); shotNames.push(W + '-bottom');
    }
  }

  for (const [name, value, ok] of checks) {
    console.log((ok ? 'PASS ' : 'FAIL ') + name + ' :: ' + value);
    if (!ok) failed = true;
  }
  console.log('截图(' + shotNames.length + '): ' + shotNames.join(', '));
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
