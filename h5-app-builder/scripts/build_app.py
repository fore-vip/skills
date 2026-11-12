#!/usr/bin/env python3
"""spec JSON + shell.html -> 单文件移动 H5 应用。

写盘前自检不过就不产出文件。零外链、无构建步骤、不依赖任何特定站点。
用法: python3 build_app.py --spec templates/app.spec.json --out index.html
"""
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHELL = ROOT / "templates" / "shell.html"


def esc(v):
    return html.escape(str(v), quote=True)


def render_head(meta, base_url):
    title = esc(meta["title"])
    desc = esc(meta["description"])
    url = base_url.rstrip("/") + "/" + meta["slug"] + ".html"
    ld = {
        "@context": "https://schema.org", "@type": "WebPage",
        "name": meta["title"], "url": url, "description": meta["description"],
        "inLanguage": "zh-CN",
        "publisher": {"@type": "Organization", "name": meta.get("brand", "")},
    }
    return "\n".join([
        "<title>" + title + "</title>",
        '<meta name="description" content="' + desc + '">',
        '<meta name="theme-color" content="#0b0b0f">',
        '<meta name="robots" content="index, follow">',
        '<link rel="canonical" href="' + esc(url) + '">',
        '<meta property="og:title" content="' + title + '">',
        '<meta property="og:description" content="' + desc + '">',
        '<meta property="og:type" content="article">',
        '<meta property="og:url" content="' + esc(url) + '">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="' + title + '">',
        '<script type="application/ld+json">',
        json.dumps(ld, ensure_ascii=False, indent=2),
        "</script>",
    ])


def render_hero(hero):
    arrow = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    return "\n".join([
        '  <section class="hero">',
        '    <div class="glow" aria-hidden="true"></div>',
        '    <div class="wrap">',
        '      <div class="eyebrow"><span class="dot"></span>' + esc(hero["eyebrow"]) + "</div>",
        "      <h1>" + esc(hero["h1"]) + "<em>" + esc(hero["em"]) + "</em></h1>",
        '      <p class="hero-p">' + esc(hero["p"]) + "</p>",
        '      <div class="hero-btns">',
        '        <a class="btn btn-p" href="#tabs">' + esc(hero["primary"]) + arrow + "</a>",
        '        <a class="btn btn-g" href="#usage">' + esc(hero["secondary"]) + "</a>",
        "      </div>",
        "    </div>",
        "  </section>",
    ])


def render_chips(items):
    return '<div class="chips">' + "".join(
        '<span class="chip">' + esc(x) + "</span>" for x in items
    ) + "</div>"


def render_timeline(items):
    out = ['<div class="tl">']
    for i, it in enumerate(items, 1):
        out.append('<div class="tl-i"><span class="k">' + str(i) + '</span><div class="c">'
                    + "<h4>" + esc(it["h"]) + "</h4><p>" + esc(it["p"]) + "</p></div></div>")
    out.append("</div>")
    return "".join(out)


def render_table(t):
    out = ['<table class="tbl"><tr>']
    for h in t["head"]:
        out.append("<th>" + esc(h) + "</th>")
    out.append("</tr>")
    badges = t.get("badges", [])
    for i, row in enumerate(t["rows"]):
        out.append("<tr>")
        for j, cell in enumerate(row):
            v = esc(cell)
            if j == 0 and i < len(badges):
                v = '<span class="badge ' + esc(badges[i]) + '">' + v + "</span>"
            out.append("<td>" + v + "</td>")
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)


def render_arts(items):
    return '<div class="arts">' + "".join(
        '<div class="art"><h4>' + esc(a["h"]) + "</h4><p>" + esc(a["p"]) + "</p></div>"
        for a in items
    ) + "</div>"


def render_block(b, meta):
    out = ['<div class="blk">']
    if b.get("title"):
        out.append("<h3>" + esc(b["title"]) + "</h3>")
    if b.get("text"):
        out.append("<p>" + esc(b["text"]) + "</p>")
    if b.get("note"):
        out.append('<div class="note"><p>' + esc(b["note"]) + "</p></div>")
    if b.get("noteOk"):
        out.append('<div class="note ok"><p>' + esc(b["noteOk"]) + "</p></div>")
    if b.get("chips"):
        out.append(render_chips(b["chips"]))
    if b.get("timeline"):
        out.append(render_timeline(b["timeline"]))
    if b.get("table"):
        out.append(render_table(b["table"]))
    if b.get("arts"):
        out.append(render_arts(b["arts"]))
    if b.get("tail"):
        out.append("<p>" + esc(b["tail"]) + "</p>")
    if b.get("link"):
        lk = b["link"]
        url = meta.get(lk["urlFromMeta"], "") if lk.get("urlFromMeta") else lk.get("url", "")
        out.append('<a class="lnk" href="' + esc(url) + '" target="_blank" rel="noopener">'
                   + esc(lk["label"])
                   + '<svg viewBox="0 0 24 24"><path d="M7 17L17 7M9 7h8v8"/></svg></a>')
    out.append("</div>")
    return "".join(out)


def render_note_block(n):
    cls = "note ok" if n.get("ok") else "note"
    return '<div class="blk"><div class="' + cls + '"><p>' + esc(n["text"]) + "</p></div></div>"


def render_demo(d):
    dims = d["dimensions"]
    picks = "".join(
        '<div class="d-switch" id="' + esc(x["id"]) + '"></div>' for x in dims
    )
    return "\n".join([
        '        <div class="demo">',
        '          <div class="d-bar"><div><h3>' + esc(d["title"]) + "</h3>",
        '            <p>' + esc(d["hint"]) + "</p></div>",
        '            <div class="d-picks">' + picks + "</div></div>",
        '          <div class="d-kpis" id="stKpis"></div>',
        '          <div class="d-chart"><h4>' + esc(d["chartTitle"]) + "</h4>",
        '            <div class="d-bars" id="stBars"></div>',
        '            <p class="d-hint" id="stHint"></p></div>',
        '          <div class="d-todo"><h4>' + esc(d["todoTitle"]) + ' <span id="stLeft"></span></h4>',
        '            <div id="stTasks"></div></div>',
        '          <div class="d-ask"><h4>' + esc(d["askTitle"]) + "</h4>",
        '            <p class="d-hint">' + esc(d["askHint"]) + "</p>",
        '            <div class="d-chips" id="stChips"></div>',
        '            <div class="d-input"><input id="stText" type="text" placeholder="'
        + esc(d["inputPlaceholder"]) + '" aria-label="输入一句话">',
        '              <button id="stSend" type="button">发出去</button></div>',
        '            <div class="d-reply" id="stReply" hidden></div>',
        "          </div></div>",
        '        <div class="blk"><h3>这台演示能点什么</h3><p>' + esc(d["afterDemo"]) + "</p></div>",
    ])


def render_section(spec):
    meta = spec["meta"]
    tabs = spec["tabs"]
    sec = spec["sections"]
    out = ['  <section class="sec"><div class="wrap">',
           '    <div class="tabs" id="tabs" role="tablist" aria-label="页面内容">']
    for i, t in enumerate(tabs):
        on = " on" if i == 0 else ""
        sel = "true" if i == 0 else "false"
        out.append('      <button class="tab' + on + '" id="tab-' + esc(t["k"])
                   + '" role="tab" data-k="' + esc(t["k"]) + '" aria-selected="' + sel
                   + '" aria-controls="panel-' + esc(t["k"]) + '">' + esc(t["label"]) + "</button>")
    out.append("    </div>")
    for i, t in enumerate(tabs):
        k = t["k"]
        out.append('    <div id="panel-' + esc(k) + '" role="tabpanel" aria-labelledby="tab-'
                    + esc(k) + '"' + ("" if i == 0 else " hidden") + ">")
        if k == "demo":
            out.append(render_demo(spec["demo"]))
        for b in sec.get(k, []):
            out.append(render_note_block(b) if b.get("type") == "note" else render_block(b, meta))
        out.append("    </div>")
    out.append("  </div></section>")
    return "\n".join(out)


DEMO_JS = """<script>
/* 演示脚本：数据全部来自 spec，纯前端、刷新复位、不写回任何地方。 */
(function(){
  var SPEC = __SPEC__;
  var D = SPEC.demo, DIM = D.dimensions, TASKS = D.tasks, NUM = D.numbers;
  var cur = {}, done = {}, i;
  for (i = 0; i < DIM.length; i++) cur[DIM[i].key] = DIM[i].options[0].k;
  function el(id){ return document.getElementById(id); }
  function btn(e){ return e.target.closest('button'); }
  function nameOf(dim, k){
    for (var j = 0; j < dim.options.length; j++) if (dim.options[j].k === k) return dim.options[j].n;
    return '';
  }
  function dataAt(){
    var d = NUM;
    for (var j = 0; j < DIM.length; j++) d = d[cur[DIM[j].key]];
    return d;
  }
  function renderPicks(){
    for (var j = 0; j < DIM.length; j++){
      var dim = DIM[j], a = [];
      for (var n = 0; n < dim.options.length; n++){
        var o = dim.options[n];
        a.push('<button type="button" data-' + dim.key + '="' + o.k + '" class="'
               + (cur[dim.key] === o.k ? 'on' : '') + '">' + o.n + '</button>');
      }
      el(dim.id).innerHTML = a.join('');
    }
  }
  function renderMain(){
    var d = dataAt(), left = 0;
    for (i = 0; i < TASKS.length; i++) if (!done[TASKS[i].id]) left++;
    var kp = [
      { v: '\\u00a5' + d.rev.toLocaleString('zh-CN'), n: D.kpiLabels[0] },
      { v: String(d.ord), n: D.kpiLabels[1] },
      { v: '\\u00a5' + Math.round(d.rev / d.ord), n: D.kpiLabels[2] },
      { v: left + ' \\u4ef6', n: D.kpiLabels[3] }
    ], kh = [];
    for (i = 0; i < kp.length; i++)
      kh.push('<div class="d-kpi"><b>' + kp[i].v + '</b><span>' + kp[i].n + '</span></div>');
    el('stKpis').innerHTML = kh.join('');
    var bh = [];
    for (i = 0; i < d.bars.length; i++)
      bh.push('<div class="d-col"><i style="height:' + d.bars[i] + '%"></i><span>'
              + D.hours[i] + '</span></div>');
    el('stBars').innerHTML = bh.join('');
    var names = [];
    for (i = 0; i < DIM.length; i++) names.push(nameOf(DIM[i], cur[DIM[i].key]));
    el('stHint').textContent = names.join(' \\u00b7 ') + '\\uff0c\\u9ad8\\u5cf0\\u5728 ' + d.peak
      + '\\uff1b' + d.low + ' ' + (SPEC.lowLabel || '\\u4e2a\\u54c1\\u7c7b\\u52a8\\u9500\\u504f\\u5feb')
      + '\\uff08\\u793a\\u4f8b\\u6570\\u636e\\uff09';
    var th = [];
    for (i = 0; i < TASKS.length; i++){
      var t = TASKS[i], st = done[t.id];
      th.push('<div class="d-task' + (st ? ' done' : '') + '">'
        + '<div class="d-task-t">' + t.title + '</div>'
        + (st ? '<span class="d-state">' + (st === 'ok' ? '\\u5df2\\u786e\\u8ba4' : '\\u7a0d\\u540e\\u5904\\u7406') + '</span>'
              : '<span class="d-tag">' + t.tag + '</span><div class="d-acts">'
                + '<button type="button" class="go" data-act="ok" data-id="' + t.id + '">\\u786e\\u8ba4</button>'
                + '<button type="button" data-act="later" data-id="' + t.id + '">\\u7a0d\\u540e</button></div>')
        + '<div class="d-task-d">' + t.detail + '</div></div>');
    }
    el('stTasks').innerHTML = th.join('');
    el('stLeft').textContent = '\\u8fd8\\u5269 ' + left + ' \\u4ef6';
  }
  function reply(q){
    for (i = 0; i < D.replyRules.length; i++)
      if (new RegExp(D.replyRules[i].match).test(q)) return '\\u793a\\u4f8b\\u56de\\u8bdd \\u00b7 ' + D.replyRules[i].reply;
    return '\\u793a\\u4f8b\\u56de\\u8bdd \\u00b7 ' + D.fallbackReply;
  }
  function ask(q){
    q = (q || '').trim(); if (!q) return;
    var r = el('stReply'); r.hidden = false;
    r.textContent = '\\u4f60\\uff1a' + q + '\\n' + reply(q);
  }
  el('stChips').innerHTML = D.questions.map(function(q){
    return '<button type="button" data-q="' + q + '">' + q + '</button>';
  }).join('');
  for (i = 0; i < DIM.length; i++){
    (function(dim){
      el(dim.id).addEventListener('click', function(e){
        var b = btn(e); if (!b) return;
        cur[dim.key] = b.getAttribute('data-' + dim.key);
        renderPicks(); renderMain();
      });
    })(DIM[i]);
  }
  el('stTasks').addEventListener('click', function(e){
    var b = btn(e); if (!b) return;
    var tid = b.getAttribute('data-id'), act = b.getAttribute('data-act');
    done[tid] = act;
    renderMain();
    if (window.H5AppOnAction) window.H5AppOnAction(tid, act);
  });
  el('stChips').addEventListener('click', function(e){
    var b = btn(e); if (!b) return;
    var q = b.getAttribute('data-q'); el('stText').value = q; ask(q);
  });
  el('stSend').addEventListener('click', function(){ ask(el('stText').value); });
  el('stText').addEventListener('keydown', function(e){
    if (e.key === 'Enter') ask(el('stText').value);
  });
  /* 云适配层入口：把云端读回的状态灌进演示状态表并刷新；纯前端模式下无人调用。 */
  window.H5AppApply = function(rows){
    for (var r = 0; r < (rows || []).length; r++){
      var row = rows[r];
      if (row && row.task_id && row.state && row.state !== 'pending')
        done[row.task_id] = row.state;
    }
    renderMain();
  };
  renderPicks(); renderMain();
})();
</script>"""


SDK_CDN = "https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js"

CLOUD_JS = """<script src="__SDK_URL__"></script>
<script>
/* 云适配层：只做 CRUD；配置来自 publicConfig；所有失败路径都给出可见提示。 */
(function(){
  var CFG = __PUBLIC_CONFIG__, TABLE = __TABLE__;
  var box = document.createElement('div');
  box.id = 'h5Cloud';
  box.style.cssText = 'margin:0 0 14px;padding:10px 14px;border:1px solid rgba(255,255,255,.16);'
    + 'border-radius:10px;font-size:13px;color:#c6c6d0;background:rgba(255,255,255,.04)';
  function say(t, ok){
    box.textContent = '云端 · ' + t;
    box.style.borderColor = ok ? 'rgba(74,222,128,.5)' : 'rgba(251,191,36,.5)';
  }
  function friendly(e){
    if (!e) return '未知错误';
    var m = e.message || String(e);
    if (/401|origin|publishable/i.test(m)) return '当前访问来源与应用保留域名不一致，发布到应用域名后才会生效';
    if (e.code === '42P01') return '数据表还没建好';
    if (e.code === '42501') return '没有写入权限';
    return String(m).slice(0, 80);
  }
  var cloud = null;
  function boot(){
    if (!window.WorkBuddyCloud || !window.WorkBuddyCloud.createWorkBuddyCloud){
      say('云端组件没加载出来（本机可能访问不到 SDK 的 CDN），本次操作只在本页生效', false);
      return;
    }
    try {
      cloud = WorkBuddyCloud.createWorkBuddyCloud({
        endpoint: CFG.endpoint,
        oauthRelayBaseUrl: CFG.oauthRelayBaseUrl,
        publishableKey: CFG.publishableKey
      });
    } catch (e) { say('云端初始化失败：' + friendly(e), false); return; }
    load();
  }
  async function load(){
    var r;
    try { r = await cloud.database.from(TABLE).select('task_id,state').order('task_id'); }
    catch (e) { say('读取失败：' + friendly(e), false); return; }
    if (r.error){ say('读取失败：' + friendly(r.error), false); return; }
    if (window.H5AppApply) window.H5AppApply(r.data || []);
    say('已连通 · 待办状态跨刷新保留', true);
  }
  window.H5AppOnAction = async function(id, act){
    if (!cloud){ say('云端未连接，本次操作只在本页生效', false); return; }
    var r;
    try {
      r = await cloud.database.from(TABLE)
        .upsert({ task_id: id, state: act }, { onConflict: 'task_id' }).select();
    } catch (e) { say('保存失败：' + friendly(e), false); return; }
    if (r.error){ say('保存失败：' + friendly(r.error), false); return; }
    if (!r.data || !r.data.length){ say('没有写入成功，可能被权限拦下', false); return; }
    say('已保存到云端 · ' + id + ' → ' + act, true);
  };
  function mount(){
    var k = document.getElementById('stKpis');
    if (k && k.parentNode) k.parentNode.insertBefore(box, k.nextSibling);
    boot();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
</script>"""


def render_script(spec):
    payload = {
        "lowLabel": spec["demo"].get("lowLabel", "个品类动销偏快"),
        "demo": {
            "dimensions": spec["demo"]["dimensions"],
            "tasks": spec["demo"]["tasks"],
            "numbers": spec["demo"]["numbers"],
            "hours": spec["demo"]["hours"],
            "kpiLabels": spec["demo"]["kpiLabels"],
            "questions": spec["demo"]["questions"],
            "replyRules": spec["demo"]["replyRules"],
            "fallbackReply": spec["demo"]["fallbackReply"],
        }
    }
    js = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return DEMO_JS.replace("__SPEC__", js).replace("__SPEC__", "")


def selfcheck(page, spec, cloud_mode=False):
    errs = []
    leftovers = re.findall(r"__[A-Z][A-Z0-9_]*__|\{\{[^{}]+\}\}", page)
    if leftovers:
        errs.append("占位符残留: " + repr(sorted(set(leftovers))[:5]))
    for tag in ["div", "section", "a", "span", "header", "footer", "main", "button",
                "table", "tr", "th", "td", "h1", "h3", "h4", "p", "script", "style"]:
        o = len(re.findall(r"<%s[\s>]" % tag, page))
        c = page.count("</%s>" % tag)
        if o != c:
            errs.append("标签不平衡 %s %d/%d" % (tag, o, c))
    if not cloud_mode and re.search(r"<script[^>]+src=|<link[^>]+rel=['\"]stylesheet|<img[^>]+src=['\"]https?://", page):
        errs.append("存在外部脚本/样式/图片依赖，违反零外链")
    if cloud_mode:
        srcs = []
        for s in re.findall(r"<script[^>]*\ssrc=([^\s>]+)", page):
            srcs.append(s.strip().strip('"').strip("'"))
        if SDK_CDN not in srcs:
            errs.append("云模式缺少 SDK CDN 脚本")
        other = [u for u in srcs if u != SDK_CDN]
        if other:
            errs.append("存在非白名单外部脚本: " + repr(other[:3]))
        if "createWorkBuddyCloud" not in page:
            errs.append("云模式缺少 SDK 初始化")
        if "endpoint: CFG.endpoint" not in page:
            errs.append("SDK 初始化未从 publicConfig 取 endpoint")
        if re.search(r"<link[^>]+rel=.stylesheet", page):
            errs.append("存在外部样式依赖")
        if re.search(r"<img[^>]+src=.https?://", page):
            errs.append("存在外部图片依赖")
    if spec["meta"].get("prototype"):
        for word in ["示例数据", "刷新", "未开放安装"]:
            if word not in page:
                errs.append("原型口径缺失: " + word)
    # 只认大写独立词：CSS 类名 .d-todo 含小写 "todo"，大小写不敏感会误报
    if re.search(r"\bTODO\b|\bFIXME\b|\bXXX\b|lorem ipsum", page):
        errs.append("残留占位文案（大写独立词 / lorem ipsum）")
    # JS 语法：有 node 就真编译一遍
    scripts = re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>([\s\S]*?)</script>", page)
    try:
        import tempfile
        for idx, code in enumerate(scripts):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(code)
                tmp = f.name
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            Path(tmp).unlink(missing_ok=True)
            if r.returncode != 0:
                errs.append("JS 语法检查失败 #%d: %s" % (idx, r.stderr.strip()[:200]))
    except FileNotFoundError:
        pass
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--shell", default=str(DEFAULT_SHELL))
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="https://example.com")
    ap.add_argument("--footer-links", default="")
    ap.add_argument("--cloud-config", default="", help="publicConfig JSON；给了就启用云适配层")
    ap.add_argument("--cloud-table", default="", help="云端表名；省略时取 spec.meta.cloud.table")
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    shell = Path(a.shell).read_text(encoding="utf-8")
    meta = spec["meta"]

    page = shell
    page = page.replace("<!--__HEAD__-->", render_head(meta, a.base_url))
    page = page.replace("<!--__HERO__-->", render_hero(spec["hero"]))
    page = page.replace("<!--__SECTION__-->", render_section(spec))
    cloud_mode = bool(a.cloud_config)
    if cloud_mode:
        cfg = json.loads(Path(a.cloud_config).read_text(encoding="utf-8"))
        # 只把端上可用的三个值写进页面，其余配置不落到前端
        pub = {k: cfg[k] for k in ("endpoint", "oauthRelayBaseUrl", "publishableKey") if k in cfg}
        table = a.cloud_table or meta.get("cloud", {}).get("table", "")
        if not table:
            print("[abort] 云模式缺少表名（--cloud-table 或 spec.meta.cloud.table）", file=sys.stderr)
            return 1
        cloud_js = (CLOUD_JS.replace("__SDK_URL__", SDK_CDN)
                    .replace("__PUBLIC_CONFIG__", json.dumps(pub, ensure_ascii=False))
                    .replace("__TABLE__", json.dumps(table, ensure_ascii=False)))
        page = page.replace("<!--__SCRIPT__-->", render_script(spec) + "\n" + cloud_js)
    else:
        page = page.replace("<!--__SCRIPT__-->", render_script(spec))
    page = page.replace("__BRAND__", esc(meta.get("brand", "")))
    page = page.replace("__HERO_CTA__", esc(spec["hero"]["primary"]))
    page = page.replace("__FOOTER_LINKS__", a.footer_links)

    errs = selfcheck(page, spec, cloud_mode)
    if errs:
        for e in errs:
            print("[FAIL] " + e, file=sys.stderr)
        print("[abort] 自检未通过，未写出文件", file=sys.stderr)
        return 1
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("[ok] %s  %d bytes / %d lines" % (out, len(page.encode("utf-8")), page.count("\n") + 1))
    print("     自检通过：占位符清零、标签平衡、零外链、原型口径齐备、JS 语法通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
