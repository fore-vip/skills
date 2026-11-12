#!/usr/bin/env node
/**
 * 真实浏览器闸门：390×844 走完四视图，验证结构与交互真的成立。
 *
 * 用法：
 *   node verify_flow.mjs --spec examples/salon.spec.json --url http://127.0.0.1:8767/salon.html
 *   node verify_flow.mjs --spec out/spec.json --url https://xxx.example.com/ --cloud
 *
 * --cloud 时要求提交能落库并给出单号；不加则要求提交按钮禁用且有可见提示。
 */
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';

const argv = process.argv.slice(2);
const arg = k => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : undefined; };
const flag = k => argv.includes(k);
const SPEC = resolve(arg('--spec') || 'examples/salon.spec.json');
const URL_ARG = arg('--url') || 'http://127.0.0.1:8767/salon.html';
const WIDTH = Number(arg('--width') || 390);
const HEIGHT = Number(arg('--height') || 844);
const SHOT_PREFIX = arg('--shots') || '/tmp/store-h5';
const CHROME = arg('--chrome') || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = Number(arg('--port') || 9333);
const CLOUD = flag('--cloud');
const PROFILE = '/tmp/chrome-cdp-store-' + PORT;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const spec = JSON.parse(readFileSync(SPEC, 'utf8'));
const services = spec.services || [];
const checks = [];
const shots = [];

rmSync(PROFILE, { recursive: true, force: true });
const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars', '--no-first-run',
  '--remote-debugging-port=' + PORT, '--user-data-dir=' + PROFILE,
  '--window-size=1200,900', 'about:blank',
], { stdio: 'ignore' });

let ws, seq = 0, failed = false;
const pending = new Map();
function send(method, params = {}) {
  return new Promise((res, rej) => {
    const id = ++seq;
    pending.set(id, res);
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error('超时 ' + method)); } }, 15000);
  });
}
async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails.exception || r.result.exceptionDetails));
  return r.result.result.value;
}
async function shot(name) {
  await sleep(320);
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(SHOT_PREFIX + '-' + name + '.png', Buffer.from(r.result.data, 'base64'));
  shots.push(name);
}
async function endpoint() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch('http://127.0.0.1:' + PORT + '/json/list');
      if (r.ok) {
        const page = (await r.json()).find(t => t.type === 'page');
        if (page) return page.webSocketDebuggerUrl;
      }
    } catch (_) { /* 等 Chrome */ }
    await sleep(250);
  }
  throw new Error('CDP 未就绪');
}
const add = (name, value, ok) => checks.push([name, String(value).slice(0, 70), !!ok]);

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
  await send('Emulation.setDeviceMetricsOverride', { width: WIDTH, height: HEIGHT, deviceScaleFactor: 1, mobile: true });
  await send('Page.navigate', { url: URL_ARG });

  for (let i = 0; i < 40; i++) {
    if (await evalJs('window.__APP_READY === true')) break;
    await sleep(150);
  }
  add('应用启动完成', await evalJs('window.__APP_READY === true'), await evalJs('window.__APP_READY === true'));
  add('视口回读', await evalJs('innerWidth + "x" + innerHeight'), (await evalJs('innerWidth')) === WIDTH);

  /* ① 首页 */
  add('首页默认可见', await evalJs('!document.getElementById("view-home").hidden'),
    await evalJs('!document.getElementById("view-home").hidden'));
  add('首页店名', await evalJs('document.querySelector(".bname").textContent'),
    (await evalJs('document.querySelector(".bname").textContent')).trim() === spec.store.name);
  add('首页服务条数', await evalJs('document.querySelectorAll("#svcList li").length'),
    (await evalJs('document.querySelectorAll("#svcList li").length')) === services.length);
  add('首页可拨电话', await evalJs('!!document.querySelector("#storeInfo a[href^=\\"tel:\\"]")'),
    await evalJs('!!document.querySelector("#storeInfo a[href^=\\"tel:\\"]")'));
  add('首页无横向溢出', await evalJs('document.documentElement.scrollWidth + "/" + innerWidth'),
    (await evalJs('document.documentElement.scrollWidth')) <= WIDTH);
  await shot('home');

  /* ② 预约 */
  await evalJs('document.querySelector(\'.tab[data-tab="book"]\').click()');
  await sleep(350);
  add('进入预约视图', await evalJs('!document.getElementById("view-book").hidden'),
    await evalJs('!document.getElementById("view-book").hidden'));
  add('默认选中服务与日期', await evalJs('[document.querySelectorAll("#svcChips .is-on").length, document.querySelectorAll("#dateChips .is-on").length].join("/")'),
    (await evalJs('document.querySelectorAll("#svcChips .is-on").length')) === 1
    && (await evalJs('document.querySelectorAll("#dateChips .is-on").length')) === 1);
  add('时段可选', await evalJs('document.querySelectorAll("#slotGrid .chip").length'),
    (await evalJs('document.querySelectorAll("#slotGrid .chip").length')) === (spec.booking.slots || []).length);

  await evalJs('document.querySelectorAll("#slotGrid .chip")[3].click()');
  await evalJs('(function(){var n=document.getElementById("fName");n.value="测试顾客";n.dispatchEvent(new Event("input",{bubbles:true}));})()');
  await evalJs('(function(){var p=document.getElementById("fPhone");p.value="13900000000";p.dispatchEvent(new Event("input",{bubbles:true}));})()');

  if (CLOUD) {
    await evalJs('document.getElementById("btnSubmit").click()');
    for (let i = 0; i < 40; i++) {
      if (await evalJs('!document.getElementById("doneCard").hidden')) break;
      await sleep(250);
    }
    const code = await evalJs('document.getElementById("doneCode").textContent');
    add('提交后有单号', code, /^B[A-Z0-9]{6,}/.test(String(code)));
    add('失败提示为空', await evalJs('document.getElementById("formHint").textContent'),
      !(await evalJs('document.getElementById("formHint").textContent')).trim());
  } else {
    add('预览版提交按钮禁用', await evalJs('document.getElementById("btnSubmit").disabled'),
      await evalJs('document.getElementById("btnSubmit").disabled'));
    add('预览版云端提示可见', await evalJs('document.getElementById("cloudHint").textContent.slice(0,20)'),
      !(await evalJs('document.getElementById("cloudHint").hidden')));
  }
  await shot('book');

  /* ③ 分享 */
  await evalJs('document.querySelector(\'.tab[data-tab="share"]\').click()');
  await sleep(300);
  const link = String(await evalJs('document.getElementById("shareLink").textContent'));
  const code = String(await evalJs('document.getElementById("inviteCode").textContent'));
  add('分享链接带 ref', link, link.includes('?ref='));
  add('邀请码格式', code, /^CH-[A-Z0-9]{4}$/.test(code));
  add('邀请链接用的是我的码', link, link.includes('ref=' + encodeURIComponent(code)));
  add('邀请文案非空', String(await evalJs('document.getElementById("inviteReward").textContent')).slice(0, 20),
    !!String(await evalJs('document.getElementById("inviteReward").textContent')).trim());
  await shot('share');

  /* ④ 店主管理 */
  await evalJs('document.querySelector(\'.tab[data-tab="admin"]\').click()');
  await sleep(400);
  add('进入管理视图', await evalJs('!document.getElementById("view-admin").hidden'),
    await evalJs('!document.getElementById("view-admin").hidden'));
  add('登录面板可见', await evalJs('!document.getElementById("authPanel").hidden'),
    await evalJs('!document.getElementById("authPanel").hidden'));
  add('登录入口有验证码按钮', await evalJs('!!document.getElementById("btnSendCode")'),
    await evalJs('!!document.getElementById("btnSendCode")'));
  if (!CLOUD) {
    add('预览版管理台有说明', String(await evalJs('document.getElementById("loginHint").textContent')).slice(0, 20),
      String(await evalJs('document.getElementById("loginHint").textContent')).includes('预览版'));
  }
  await shot('admin');

  /* ⑤ 邀请参数落地 */
  await send('Page.navigate', { url: URL_ARG + (URL_ARG.includes('?') ? '&' : '?') + 'ref=CH-TEST#/book' });
  for (let i = 0; i < 40; i++) {
    if (await evalJs('window.__APP_READY === true')) break;
    await sleep(150);
  }
  add('带 ref 进入后记住邀请码', await evalJs('localStorage.getItem("auto-h5.ref")'),
    (await evalJs('localStorage.getItem("auto-h5.ref")')) === 'CH-TEST');

  for (const [name, value, ok] of checks) {
    console.log((ok ? 'PASS ' : 'FAIL ') + name + ' :: ' + value);
    if (!ok) failed = true;
  }
  console.log('截图(' + shots.length + '): ' + shots.join(', '));
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
