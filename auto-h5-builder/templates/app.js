/* 门店 H5 运行时：四视图路由 + 云端读写 + 店主管理台 */
(function () {
  'use strict';

  var SPEC = window.APP_SPEC || {};
  var CFG = window.APP_CFG || null;
  var STORE = SPEC.store || {};
  var BOOKING = SPEC.booking || {};
  var SHARE = SPEC.share || {};
  var TABLE = (SPEC.cloud && SPEC.cloud.bookings) || 'bookings';
  var LOGIN = (SPEC.admin && SPEC.admin.login) || 'email';

  var STATUS = { pending: '待确认', confirmed: '已确认', done: '已完成', cancelled: '已取消' };
  var ACTIONS = {
    pending: [['confirmed', '确认预约'], ['cancelled', '取消']],
    confirmed: [['done', '标记完成'], ['cancelled', '取消']],
    cancelled: [['pending', '恢复待确认']],
    done: []
  };
  var CODE_KEY = 'auto-h5.code';
  var REF_KEY = 'auto-h5.ref';

  var cloud = null;
  var session = null;
  var orders = [];
  var filter = 'all';
  var pendingOtp = null;
  var picked = { service: '', date: '', time: '' };
  var bookReady = false;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function readable(err) {
    if (!err) return '未知错误';
    return err.message || err.error_description || err.hint || String(err);
  }
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function isoDay(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function todayIso() { return isoDay(new Date()); }

  /* ---------- 邀请码 ---------- */
  function myCode() {
    var c = null;
    try { c = localStorage.getItem(CODE_KEY); } catch (e) { c = null; }
    if (!c) {
      c = 'CH-' + Math.random().toString(36).slice(2, 6).toUpperCase();
      try { localStorage.setItem(CODE_KEY, c); } catch (e) { /* 隐私模式忽略 */ }
    }
    return c;
  }
  function captureRef() {
    var ref = null;
    try { ref = new URLSearchParams(location.search).get('ref'); } catch (e) { ref = null; }
    if (ref && /^[A-Za-z0-9-]{2,16}$/.test(ref)) {
      try { localStorage.setItem(REF_KEY, ref); } catch (e) { /* 忽略 */ }
      return ref;
    }
    try { return localStorage.getItem(REF_KEY) || ''; } catch (e) { return ''; }
  }
  function shareUrl(code) {
    return location.origin + location.pathname + '?ref=' + encodeURIComponent(code) + '#/home';
  }

  /* ---------- 云端 ---------- */
  function client() {
    if (cloud) return cloud;
    if (!CFG) throw new Error('云端还没接通');
    if (!window.WorkBuddyCloud) throw new Error('云端组件没加载出来，检查网络后刷新');
    cloud = window.WorkBuddyCloud.createWorkBuddyCloud({
      endpoint: CFG.endpoint,
      oauthRelayBaseUrl: CFG.oauthRelayBaseUrl,
      publishableKey: CFG.publishableKey
    });
    return cloud;
  }

  /* ---------- 路由 ---------- */
  var VIEWS = ['home', 'book', 'share', 'admin'];
  function currentView() {
    var m = /^#\/([a-z]+)/.exec(location.hash || '');
    return m && VIEWS.indexOf(m[1]) >= 0 ? m[1] : 'home';
  }
  function route() {
    var v = currentView();
    VIEWS.forEach(function (name) {
      var sec = $('#view-' + name);
      if (sec) sec.hidden = name !== v;
    });
    $$('.tab').forEach(function (t) {
      t.classList.toggle('is-on', t.getAttribute('data-tab') === v);
    });
    window.scrollTo(0, 0);
    if (v === 'book') renderBook();
    if (v === 'share') renderShare();
    if (v === 'admin') enterAdmin();
  }

  /* ---------- 首页 ---------- */
  function renderHome() {
    var list = $('#svcList');
    list.textContent = '';
    (SPEC.services || []).forEach(function (s) {
      var li = el('li', 'svc-item');
      var main = el('div', 'svc-main');
      main.appendChild(el('div', 'svc-name', s.name));
      if (s.desc) main.appendChild(el('div', 'svc-desc', s.desc));
      var meta = el('div', 'svc-meta');
      meta.appendChild(el('div', 'svc-price', s.price));
      meta.appendChild(el('div', 'svc-dur', s.duration));
      li.appendChild(main);
      li.appendChild(meta);
      list.appendChild(li);
    });

    var info = $('#storeInfo');
    info.textContent = '';
    [['营业时间', STORE.hours], ['地址', STORE.address], ['电话', STORE.phone]].forEach(function (row) {
      var r = el('div', 'info-row');
      r.appendChild(el('span', 'info-k', row[0]));
      var v = el('span', 'info-v');
      if (row[0] === '电话' && row[1]) {
        var a = el('a', '', row[1]);
        a.href = 'tel:' + row[1];
        v.appendChild(a);
      } else {
        v.textContent = row[1] || '—';
      }
      r.appendChild(v);
      info.appendChild(r);
    });
  }

  /* ---------- 预约 ---------- */
  function nextDays(n) {
    var wd = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    var base = new Date();
    base.setHours(0, 0, 0, 0);
    var out = [];
    for (var i = 0; i < n; i++) {
      var d = new Date(base.getTime() + i * 86400000);
      out.push({
        iso: isoDay(d),
        label: i === 0 ? '今天' : i === 1 ? '明天' : wd[d.getDay()],
        day: (d.getMonth() + 1) + '/' + d.getDate()
      });
    }
    return out;
  }
  function syncChips(wrap, target) {
    $$('.chip', wrap).forEach(function (c) { c.classList.remove('is-on'); });
    target.classList.add('is-on');
  }
  function renderBook() {
    if (!bookReady) {
      var svcWrap = $('#svcChips');
      (SPEC.services || []).forEach(function (s, i) {
        var b = el('button', 'chip', s.name);
        b.type = 'button';
        b.onclick = function () { picked.service = s.name; syncChips(svcWrap, b); };
        svcWrap.appendChild(b);
        if (i === 0) { picked.service = s.name; b.classList.add('is-on'); }
      });

      var dateWrap = $('#dateChips');
      nextDays(BOOKING.days || 7).forEach(function (d, i) {
        var b = el('button', 'chip chip--date');
        b.type = 'button';
        b.appendChild(el('span', 'chip-k', d.label));
        b.appendChild(el('span', 'chip-d', d.day));
        b.onclick = function () { picked.date = d.iso; syncChips(dateWrap, b); };
        dateWrap.appendChild(b);
        if (i === 0) { picked.date = d.iso; b.classList.add('is-on'); }
      });

      var slotWrap = $('#slotGrid');
      (BOOKING.slots || []).forEach(function (t) {
        var b = el('button', 'chip', t);
        b.type = 'button';
        b.onclick = function () { picked.time = t; syncChips(slotWrap, b); };
        slotWrap.appendChild(b);
      });
      bookReady = true;
    }

    if (!CFG) {
      var hint = $('#cloudHint');
      hint.hidden = false;
      hint.textContent = '预览版：云端尚未接通，提交按钮暂不可用。接好云服务后重新生成即可收单。';
      $('#btnSubmit').disabled = true;
    }
  }
  function resetBooking() {
    $('#doneCard').hidden = true;
    $('#bookForm').hidden = false;
    $('#formHint').textContent = '';
    $('#fName').value = '';
    $('#fPhone').value = '';
    $('#fNote').value = '';
  }
  function formHint(msg, isWarn) {
    var h = $('#formHint');
    h.className = isWarn ? 'hint hint--warn' : 'hint';
    h.textContent = msg || '';
  }
  async function submitBooking(ev) {
    ev.preventDefault();
    var name = $('#fName').value.trim();
    var phone = $('#fPhone').value.trim();
    var note = $('#fNote').value.trim();
    if (!picked.service) return formHint('先选一个服务', true);
    if (!picked.date) return formHint('先选日期', true);
    if (!picked.time) return formHint('先选时段', true);
    if (!name) return formHint('填一下怎么称呼您', true);
    if (!/^1\d{10}$/.test(phone)) return formHint('手机号要 11 位、以 1 开头', true);

    var btn = $('#btnSubmit');
    btn.disabled = true;
    btn.textContent = '提交中…';
    formHint('');

    var code = 'B' + Date.now().toString(36).toUpperCase().slice(-6) + Math.floor(Math.random() * 90 + 10);
    var row = {
      code: code,
      customer_name: name,
      phone: phone,
      service: picked.service,
      slot_date: picked.date,
      slot_time: picked.time,
      note: note || null,
      invite_code: captureRef() || null,
      status: 'pending'
    };

    try {
      var res = await client().database.from(TABLE).insert(row);
      if (res && res.error) throw res.error;
      $('#doneCode').textContent = code;
      $('#doneCard').hidden = false;
      $('#bookForm').hidden = true;
    } catch (err) {
      formHint('没提交成功：' + readable(err) + '。可以重试，或直接拨打门店电话。', true);
    } finally {
      btn.disabled = false;
      btn.textContent = '提交预约';
    }
  }

  /* ---------- 分享 ---------- */
  function renderShare() {
    var code = myCode();
    $('#inviteCode').textContent = code;
    $('#inviteReward').textContent = SHARE.inviteReward || '';
    $('#shareLink').textContent = shareUrl(code);
    $('#posterText').textContent = SHARE.posterText || '';
  }
  async function copyLink() {
    var link = shareUrl(myCode());
    var tip = $('#copyHint');
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(link);
      } else {
        var t = el('textarea');
        t.value = link;
        t.style.position = 'fixed';
        t.style.opacity = '0';
        document.body.appendChild(t);
        t.select();
        document.execCommand('copy');
        document.body.removeChild(t);
      }
      tip.textContent = '链接已复制，去微信粘贴给好友即可。';
    } catch (e) {
      tip.textContent = '复制失败，请长按上方链接手动复制。';
    }
  }

  /* ---------- 店主管理 ---------- */
  function loginHint(msg) { $('#loginHint').textContent = msg || ''; }
  function loginFail(err) {
    var msg = readable(err);
    if (/per minute|rate limit|too many/i.test(msg)) {
      return '请求太频繁：同一邮箱每分钟只能发一次，请稍后再试。';
    }
    if (/未开启|disabled|not enabled/i.test(msg)) {
      return '店主登录还没开通：到云服务控制台打开邮箱/短信验证码登录后再试（' + msg + '）';
    }
    return msg;
  }
  async function enterAdmin() {
    if (!CFG) {
      loginHint('预览版没有云配置，管理台无法登录。生成正式页面后可用。');
      return;
    }
    try {
      var res = await client().auth.getSession();
      var s = res && res.data ? (res.data.session || res.data) : null;
      session = s && (s.user || s.access_token) ? s : null;
      if (session) return showAdmin();
      $('#authPanel').hidden = false;
      $('#adminPanel').hidden = true;
    } catch (err) {
      loginHint(readable(err));
    }
  }
  async function sendCode() {
    var v = $('#fLogin').value.trim();
    if (LOGIN === 'phone' && !/^1\d{10}$/.test(v)) return loginHint('请输入正确的 11 位手机号');
    if (LOGIN === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) return loginHint('请输入正确的邮箱');
    loginHint('发送中…');
    try {
      var res = LOGIN === 'phone'
        ? await client().auth.sendOtp({ phone: v })
        : await client().auth.sendOtp({ email: v });
      if (res.error) throw res.error;
      pendingOtp = { value: v, verificationId: res.data.verificationId, isExistingUser: res.data.isExistingUser };
      loginHint('验证码已发送，10 分钟内有效');
    } catch (err) {
      loginHint(loginFail(err));
    }
  }
  async function submitLogin(ev) {
    ev.preventDefault();
    var token = $('#fCode').value.trim();
    if (!pendingOtp) return loginHint('先点「获取验证码」');
    if (!token) return loginHint('填一下收到的验证码');
    var payload = {
      verificationId: pendingOtp.verificationId,
      isExistingUser: pendingOtp.isExistingUser,
      token: token
    };
    if (LOGIN === 'phone') payload.phone = pendingOtp.value; else payload.email = pendingOtp.value;
    loginHint('登录中…');
    try {
      var res = await client().auth.verifyOtp(payload);
      if (res.error) throw res.error;
      pendingOtp = null;
      session = res.data && (res.data.session || res.data);
      showAdmin();
    } catch (err) {
      loginHint(loginFail(err));
    }
  }
  async function logout() {
    try { await client().auth.signOut(); } catch (e) { /* 忽略 */ }
    session = null;
    orders = [];
    $('#adminPanel').hidden = true;
    $('#authPanel').hidden = false;
    loginHint('');
  }
  function showAdmin() {
    loginHint('');
    $('#authPanel').hidden = true;
    $('#adminPanel').hidden = false;
    renderTabs();
    loadOrders();
  }
  function renderTabs() {
    var wrap = $('#statusTabs');
    wrap.textContent = '';
    [['all', '全部'], ['pending', '待确认'], ['confirmed', '已确认'], ['done', '已完成'], ['cancelled', '已取消']]
      .forEach(function (pair) {
        var b = el('button', 'chip', pair[1]);
        b.type = 'button';
        if (filter === pair[0]) b.classList.add('is-on');
        b.onclick = function () { filter = pair[0]; renderTabs(); renderOrders(); };
        wrap.appendChild(b);
      });
  }
  function renderStats() {
    var today = orders.filter(function (o) { return o.slot_date === todayIso(); }).length;
    var pending = orders.filter(function (o) { return o.status === 'pending'; }).length;
    var invited = orders.filter(function (o) { return !!o.invite_code; }).length;
    var box = $('#stats');
    box.textContent = '';
    [['今日', today], ['待确认', pending], ['累计', orders.length], ['邀请单', invited]].forEach(function (p) {
      var card = el('div', 'stat');
      card.appendChild(el('b', '', String(p[1])));
      card.appendChild(el('span', '', p[0]));
      box.appendChild(card);
    });
  }
  function renderOrders() {
    var list = $('#orderList');
    list.textContent = '';
    var rows = filter === 'all' ? orders : orders.filter(function (o) { return o.status === filter; });
    if (!rows.length) {
      list.appendChild(el('p', 'hint', '这个状态下还没有订单。'));
      return;
    }
    rows.forEach(function (o) {
      var card = el('div', 'order');
      var top = el('div', 'o-top');
      top.appendChild(el('span', 'o-name', o.customer_name || '顾客'));
      top.appendChild(el('span', 'tag tag--' + (o.status || 'pending'), STATUS[o.status] || o.status));
      card.appendChild(top);
      card.appendChild(el('p', 'o-line', (o.service || '') + ' · ' + (o.slot_date || '') + ' ' + (o.slot_time || '')));
      var phone = el('p', 'o-line');
      var tel = el('a', '', o.phone || '');
      tel.href = 'tel:' + (o.phone || '');
      phone.appendChild(tel);
      card.appendChild(phone);
      if (o.note) card.appendChild(el('p', 'o-line', '备注：' + o.note));
      if (o.invite_code) card.appendChild(el('p', 'o-line', '邀请码 ' + o.invite_code));
      card.appendChild(el('p', 'hint', '单号 ' + (o.code || '—')));

      var acts = ACTIONS[o.status] || [];
      if (acts.length) {
        var bar = el('div', 'o-actions');
        acts.forEach(function (a) {
          var b = el('button', 'ghost' + (a[0] === 'cancelled' ? '' : ' ghost--solid'), a[1]);
          b.type = 'button';
          b.onclick = function () { setStatus(o.id, a[0]); };
          bar.appendChild(b);
        });
        card.appendChild(bar);
      }
      list.appendChild(card);
    });
  }
  async function loadOrders() {
    $('#adminHint').textContent = '加载中…';
    try {
      var res = await client().database.from(TABLE)
        .select('*').order('created_at', { ascending: false }).limit(200);
      if (res.error) throw res.error;
      orders = res.data || [];
      $('#adminHint').textContent = orders.length ? '' : '还没有预约，先把页面分享出去。';
      renderStats();
      renderOrders();
    } catch (err) {
      $('#adminHint').textContent = '读不到订单：' + readable(err);
    }
  }
  async function setStatus(id, next) {
    $('#adminHint').textContent = '正在更新…';
    try {
      var res = await client().database.from(TABLE).update({ status: next }).eq('id', id);
      if (res.error) throw res.error;
      await loadOrders();
    } catch (err) {
      $('#adminHint').textContent = '改状态失败：' + readable(err);
    }
  }

  /* ---------- 启动 ---------- */
  function boot() {
    captureRef();
    renderHome();
    renderShare();

    document.addEventListener('click', function (e) {
      var trigger = e.target && e.target.closest ? e.target.closest('[data-go]') : null;
      if (!trigger) return;
      var v = trigger.getAttribute('data-go');
      if (v === 'book') resetBooking();
      location.hash = '#/' + v;
    });

    $('#bookForm').addEventListener('submit', submitBooking);
    $('#loginForm').addEventListener('submit', submitLogin);
    $('#btnSendCode').addEventListener('click', sendCode);
    $('#btnLogout').addEventListener('click', logout);
    $('#btnRefresh').addEventListener('click', loadOrders);
    $('#btnCopy').addEventListener('click', copyLink);
    window.addEventListener('hashchange', route);

    route();
    window.__APP_READY = true;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
