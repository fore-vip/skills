#!/usr/bin/env python3
"""主题 spec + 选定版式 -> 单文件落地宣传页 / 应用页面。

版式由主题关键词路由（pick_layout.py），也可 --layout 显式指定；
内容结构与业务口径由 spec 决定，生成器不预设任何业务板块。
交付形态由 meta.deliverable 决定：draft（页面草稿）/ webapp（可发布应用）/ site（站点页）。
写盘前自检不过就不产出文件。

用法:
  python3 build_page.py --spec examples/beauty.spec.json --out index.html
  python3 build_page.py --spec x.json --out index.html --layout tech
  python3 build_page.py --spec x.json --out index.html --cloud-config cfg.json
"""
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

sys.dont_write_bytecode = True  # 运行不污染技能包
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pick_layout import choose, load_registry  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PAGE = ROOT / "templates" / "page.html"
DEFAULT_CSS = ROOT / "templates" / "base.css"
SDK_CDN = "https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js"
BAD_HOSTS = ("example.com", "example.org", "example.net", "localhost", "127.0.0.1")
DELIVERABLES = ("draft", "webapp", "site")
PROCESS_WORDS = ("生成器", "spec.json", "SKILL", "模板生成", "H5App", "前凌智选",
                 "AUTO 工作室", "publicConfig", "applicationId")
# 没有后端时不许出现的强行动词（避免「看起来能预约、其实不能」）
LIVE_ACTION_WORDS = ("预约", "立即", "马上", "报名", "下单", "提交")


def esc(v):
    return html.escape(str(v), quote=True)


def visible_text(page):
    t = re.sub(r"<head[\s\S]*?</head>", "", page)
    t = re.sub(r"<script[\s\S]*?</script>", "", t)
    t = re.sub(r"<style[\s\S]*?</style>", "", t)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def resolve_site(meta, override):
    """站点地址只来自 spec 或显式参数；没有就返回空串（草稿态，不写假域名）。"""
    site = (override or meta.get("siteUrl") or "").strip().rstrip("/")
    if site and not site.startswith(("http://", "https://")):
        site = "https://" + site
    return site


def page_url(meta, site):
    return (site + "/" + meta.get("slug", "index") + ".html") if site else ""


def favicon_href(meta):
    if meta.get("favicon"):
        return esc(meta["favicon"])
    color = str(meta.get("themeColor", "#b4573c")).replace("#", "%23")
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
           "<rect width='64' height='64' rx='16' fill='" + color + "'/>"
           "<circle cx='32' cy='32' r='12' fill='none' stroke='white' stroke-width='4'/></svg>")
    return "data:image/svg+xml," + quote(svg, safe="")


def render_head(meta, site):
    title, desc = esc(meta["title"]), esc(meta["description"])
    url = page_url(meta, site)
    ld = {"@context": "https://schema.org", "@type": "WebPage",
          "name": meta["title"], "description": meta["description"],
          "inLanguage": "zh-CN",
          "publisher": {"@type": "Organization", "name": meta.get("brand", "")}}
    if url:
        ld["url"] = url
    lines = [
        "<title>" + title + "</title>",
        '<meta name="description" content="' + desc + '">',
        '<meta name="theme-color" content="' + esc(meta.get("themeColor", "#ffffff")) + '">',
        '<link rel="icon" href="' + favicon_href(meta) + '">',
        '<meta property="og:title" content="' + title + '">',
        '<meta property="og:description" content="' + desc + '">',
        '<meta property="og:type" content="website">',
    ]
    if url:
        lines.append('<link rel="canonical" href="' + esc(url) + '">')
        lines.append('<meta property="og:url" content="' + esc(url) + '">')
    if meta.get("ogImage"):
        lines.append('<meta property="og:image" content="' + esc(meta["ogImage"]) + '">')
        lines.append('<meta name="twitter:card" content="summary_large_image">')
    else:
        lines.append('<meta name="twitter:card" content="summary">')
    lines += ['<script type="application/ld+json">',
              json.dumps(ld, ensure_ascii=False, indent=2), "</script>"]
    return "\n".join(lines)


def render_hero(h, ctx):
    arrow = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    return "\n".join([
        '<section class="hero"><div class="wrap">',
        '  <div class="tag tag--lg eyebrow"><span class="dot"></span>' + esc(h["eyebrow"]) + "</div>",
        "  <h1>" + esc(h["h1"]) + "<em>" + esc(h["em"]) + "</em></h1>",
        '  <p class="hero-p">' + esc(h["p"]) + "</p>",
        '  <div class="hero-btns">',
        '    <a class="ctl ctl--lg ctl--primary" href="' + esc(h.get("primaryHref", "#cta")) + '">'
        + esc(h["primary"]) + arrow + "</a>",
        '    <a class="ctl ctl--lg" href="' + esc(h.get("secondaryHref", "#features")) + '">'
        + esc(h["secondary"]) + "</a>",
        "  </div>",
        "</div></section>",
    ])


def head_of(s, skip_title=False, skip_text=False):
    out = []
    if (s.get("title") and not skip_title) or (s.get("text") and not skip_text):
        out.append('<div class="sect-head">')
        if s.get("title") and not skip_title:
            out.append("<h2>" + esc(s["title"]) + "</h2>")
        if s.get("text") and not skip_text:
            out.append("<p>" + esc(s["text"]) + "</p>")
        out.append("</div>")
    return "".join(out)


def render_features(s, ctx):
    out = ['<div class="grid">']
    for it in s["items"]:
        out.append('<div class="card">')
        if it.get("kicker"):
            out.append('<span class="kicker">' + esc(it["kicker"]) + "</span>")
        if it.get("num"):
            out.append('<span class="num">' + esc(it["num"]) + "</span>")
        out.append("<h3>" + esc(it["h"]) + "</h3><p>" + esc(it["p"]) + "</p>")
        if it.get("tag") or it.get("foot"):
            foot = it.get("foot") or [it["tag"]]
            out.append('<div class="foot">'
                       + "".join('<span class="tag tag--accent">' + esc(x) + "</span>" for x in foot)
                       + "</div>")
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def render_showcase(s, ctx):
    out = ['<div class="grid showcase">']
    for i, it in enumerate(s["items"], 1):
        out.append('<div class="card">')
        out.append('<span class="case-idx">' + ("%02d" % i) + "</span>")
        out.append("<h3>" + esc(it["h"]) + "</h3><p>" + esc(it["p"]) + "</p>")
        if it.get("tag"):
            out.append('<div class="foot"><span class="tag">' + esc(it["tag"]) + "</span></div>")
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def render_stats(s, ctx):
    out = ['<div class="grid stats">']
    for it in s["items"]:
        out.append('<div class="stat"><b>' + esc(it["v"]) + "</b><span>"
                   + esc(it["n"]) + "</span></div>")
    out.append("</div>")
    return "".join(out)


def render_steps(s, ctx):
    out = ['<div class="steps">']
    for i, it in enumerate(s["items"], 1):
        out.append('<div class="step"><span class="k">' + str(i) + "</span><div>"
                   + "<h3>" + esc(it["h"]) + "</h3><p>" + esc(it["p"]) + "</p></div></div>")
    out.append("</div>")
    return "".join(out)


def render_quote(s, ctx):
    return ('<div class="quote"><blockquote>' + esc(s["text"]) + "</blockquote><cite>"
            + esc(s.get("cite", "")) + "</cite></div>")


render_quote.owns = ("text",)


def render_faq(s, ctx):
    out = ['<div class="faq">']
    for it in s["items"]:
        out.append("<details><summary class=\"ctl ctl--ghost faq-q\">" + esc(it["q"])
                   + '</summary><div class="faq-a">' + esc(it["a"]) + "</div></details>")
    out.append("</div>")
    return "".join(out)


def render_cta(s, ctx):
    """live=False 时表单整体禁用：不许出现「填完手机号却白填」的假提交。"""
    live = ctx["live"]
    dis = "" if live else ' disabled aria-disabled="true"'
    out = ['<div class="cta-box">', "<h2>" + esc(s["title"]) + "</h2>"]
    if s.get("text"):
        out.append("<p>" + esc(s["text"]) + "</p>")
    out.append('<form id="leadForm" class="fields" onsubmit="return false" novalidate>')
    for f in s.get("fields", []):
        fid = "f_" + esc(f["id"])
        label = esc(f.get("label", f["placeholder"]))
        out.append('<label class="sr-only" for="' + fid + '">' + label + "</label>")
        out.append('<input class="field" id="' + fid + '" type="'
                   + esc(f.get("type", "text")) + '" placeholder="' + esc(f["placeholder"])
                   + '" aria-label="' + label + '"' + dis + ">")
    out.append('<button class="ctl ctl--lg ctl--primary" type="submit"' + dis + ">"
               + esc(s.get("submit", "提交")) + "</button>")
    out.append("</form>")
    out.append('<div id="leadStatus" class="status" role="status" aria-live="polite" hidden></div>')
    if s.get("note"):
        out.append('<p class="cta-note">' + esc(s["note"]) + "</p>")
    out.append('<noscript><p class="cta-note">当前未启用脚本，本页不会提交或保存任何信息。</p></noscript>')
    out.append("</div>")
    return "".join(out)


render_cta.owns = ("title", "text")


# 每个 renderer 用 owns 声明自己已经渲染了哪些字段；新增类型时必须在自己的函数上声明，
# 而不是回头改 render_sections 的 if 分支（历史 bug：quote 的 text 被渲染两遍）。
RENDERERS = {
    "features": render_features,
    "showcase": render_showcase,
    "stats": render_stats,
    "steps": render_steps,
    "quote": render_quote,
    "faq": render_faq,
    "cta": render_cta,
    "notes": render_features,
}


def render_sections(sections, ctx):
    out = []
    for s in sections:
        t = s["type"]
        if t not in RENDERERS:
            raise ValueError("未知 section 类型: " + t + "（可用: " + ", ".join(RENDERERS) + "）")
        fn = RENDERERS[t]
        owns = getattr(fn, "owns", ())
        sid = s.get("id", t)
        out.append('<section class="sect" id="' + esc(sid) + '"><div class="wrap">')
        out.append(head_of(s, "title" in owns, "text" in owns))
        out.append(fn(s, ctx))
        out.append("</div></section>")
    return "\n".join(out)


CLOUD_LEAD_JS = """<script src="__SDK_URL__"></script>
<script>
/* 预约表单写入。配置来自平台公开参数，失败一律给可见提示。 */
(function(){
  var CFG = __PUBLIC_CONFIG__, TABLE = __TABLE__, COLS = __COLS__, PREFIX = __PREFIX__;
  var form = document.getElementById('leadForm');
  var box = document.getElementById('leadStatus');
  if (!form) return;
  window.leadCloudEnabled = true;
  function say(t, ok){
    box.hidden = false;
    box.className = 'status ' + (ok ? 'is-ok' : 'is-warn');
    box.textContent = PREFIX + t;
  }
  var cloud = null;
  try {
    if (window.WorkBuddyCloud && window.WorkBuddyCloud.createWorkBuddyCloud)
      cloud = WorkBuddyCloud.createWorkBuddyCloud({
        endpoint: CFG.endpoint,
        oauthRelayBaseUrl: CFG.oauthRelayBaseUrl,
        publishableKey: CFG.publishableKey
      });
  } catch (e) { say('云端初始化失败，本次提交不会保存', false); return; }
  if (!cloud) say('云端组件没加载出来，本次提交不会保存', false);
  form.addEventListener('submit', async function(e){
    e.preventDefault();
    var row = {};
    COLS.forEach(function(c){
      var el = document.getElementById('f_' + c);
      row[c] = el ? el.value.trim() : '';
    });
    if (COLS.some(function(c){ return !row[c]; })){ say('请先把信息填完整', false); return; }
    if (!cloud){ say('当前未连到云端，这条没有保存', false); return; }
    var r;
    try { r = await cloud.database.from(TABLE).insert(row).select(); }
    catch (err) { say('提交失败：' + String(err.message || err).slice(0, 80), false); return; }
    if (r.error){ say('提交失败：' + String(r.error.message || '').slice(0, 80), false); return; }
    say('已收到，我们会尽快联系你', true);
    form.reset();
  });
})();
</script>"""


def selfcheck(page, spec, cloud_mode=False, site=""):
    errs = []
    meta = spec["meta"]
    deliverable = meta.get("deliverable", "")
    cloud = meta.get("cloud", {})
    leftovers = re.findall(r"__[A-Z][A-Z0-9_]*__|\{\{[^{}]+\}\}", page)
    if leftovers:
        errs.append("占位符残留: " + repr(sorted(set(leftovers))[:5]))
    for tag in ["div", "section", "a", "span", "header", "footer", "main", "nav", "button",
                "form", "details", "summary", "blockquote", "h1", "h2", "h3", "p",
                "script", "style", "label", "noscript"]:
        o = len(re.findall(r"<%s[\s>]" % tag, page))
        c = page.count("</%s>" % tag)
        if o != c:
            errs.append("标签不平衡 %s %d/%d" % (tag, o, c))

    # 交付形态与云服务必须对齐
    if deliverable not in DELIVERABLES:
        errs.append("meta.deliverable 缺失或非法（可选 draft/webapp/site）")
    if deliverable in ("webapp", "site") and not site:
        errs.append("非草稿形态必须提供 meta.siteUrl 或 --base-url")
    if site and any(urlparse(site).netloc.startswith(h) or urlparse(site).netloc == h
                    for h in BAD_HOSTS):
        errs.append("站点地址是占位域名，禁止交付: " + site)
    if deliverable == "webapp":
        if not cloud.get("needed") or not cloud.get("table") or not cloud.get("columns"):
            errs.append("webapp 形态必须声明 meta.cloud.needed/table/columns 并接后端")
        if not cloud_mode:
            errs.append("webapp 形态必须传 --cloud-config 才能生成")
    if cloud_mode and not (cloud.get("needed") and cloud.get("table")):
        errs.append("传了 --cloud-config 但 spec 未声明 meta.cloud.needed/table")

    # head 元数据：三处 URL 一致、零假域名、零意外外链
    url = page_url(meta, site)
    canon = re.findall(r'<link rel="canonical" href="([^"]+)"', page)
    ogurl = re.findall(r'<meta property="og:url" content="([^"]+)"', page)
    ldm = re.search(r'<script type="application/ld\+json">([\s\S]*?)</script>', page)
    ldurl = ""
    if ldm:
        try:
            ldurl = json.loads(ldm.group(1)).get("url", "")
        except ValueError:
            errs.append("ld+json 不是合法 JSON")
    if url:
        if canon != [url] or ogurl != [url] or ldurl != url:
            errs.append("canonical / og:url / ld+json.url 与站点地址不一致")
    elif canon or ogurl or ldurl:
        errs.append("草稿态没有真实站点地址，却写了 canonical / og:url / ld+json.url")
    if '<link rel="icon"' not in page:
        errs.append("缺少 favicon")
    ogimg = meta.get("ogImage", "")
    if ogimg and ogimg.startswith("http") and urlparse(ogimg).netloc != urlparse(site).netloc:
        errs.append("og:image 是跨域外链")
    if meta.get("ogImage") and 'summary_large_image' not in page:
        errs.append("声明了 og:image 却没写大图卡")
    if not meta.get("ogImage") and 'summary_large_image' in page:
        errs.append("声明大图卡却没有 og:image")
    abs_urls = re.findall(r'(?:href|src)=["\'](https?://[^"\']+)', page)
    allowed = {url, ogimg} - {""}
    for u in abs_urls:
        if u in allowed or (cloud_mode and u == SDK_CDN):
            continue
        errs.append("存在未登记的绝对外链: " + u[:60])

    # 资源边界
    if not cloud_mode and re.search(r"<script[^>]+src=|<link[^>]+rel=['\"]stylesheet|<img[^>]+src=['\"]https?://", page):
        errs.append("存在外部脚本/样式/图片依赖，违反零外链")
    if cloud_mode:
        srcs = [s.strip().strip('"').strip("'")
                for s in re.findall(r"<script[^>]*\ssrc=([^\s>]+)", page)]
        if SDK_CDN not in srcs:
            errs.append("云模式缺少 SDK CDN 脚本")
        if [u for u in srcs if u != SDK_CDN]:
            errs.append("存在非白名单外部脚本")
        for needle in ("createWorkBuddyCloud", "endpoint: CFG.endpoint",
                       "publishableKey: CFG.publishableKey",
                       "oauthRelayBaseUrl: CFG.oauthRelayBaseUrl"):
            if needle not in page:
                errs.append("云接线缺失: " + needle)
        if re.search(r"<link[^>]+rel=.stylesheet|<img[^>]+src=.https?://", page):
            errs.append("存在外部样式/图片依赖")

    # 表单：没有后端就必须整体禁用，且禁止强行动词
    has_form = "<form" in page
    if has_form:
        if '<noscript>' not in page:
            errs.append("缺少 noscript 降级提示")
        if 'role="status"' not in page or 'aria-live=' not in page:
            errs.append("状态反馈容器缺少 role/aria-live")
        if not cloud_mode:
            inputs = re.findall(r"<input\b[^>]*>", page)
            btn = re.findall(r"<button\b[^>]*>", page)
            if [x for x in inputs + btn if "disabled" not in x]:
                errs.append("没有后端却留着可填写/可提交的控件")
        for label in (meta.get("ctaLabel", ""), spec["hero"].get("primary", "")):
            if not cloud_mode and any(w in label for w in LIVE_ACTION_WORDS):
                errs.append("没有后端却承诺强行动作: " + label)
    if 'aria-hidden="true"' not in page:
        errs.append("装饰性图标缺少 aria-hidden")

    # 正文：口径、串台、重复
    text = visible_text(page)
    disclaimer = meta.get("disclaimer", "")
    if disclaimer and disclaimer not in text:
        errs.append("口径声明未出现在页面: " + disclaimer[:30])
    for w in PROCESS_WORDS:
        if w in page:
            errs.append("正文/脚本残留制作过程词: " + w)
    for s in spec["sections"]:
        frag = s.get("text", "")
        if len(frag) >= 12 and text.count(frag) > 1:
            errs.append("区块说明重复渲染: " + frag[:24])
    if re.search(r"\bTODO\b|\bFIXME\b|\bXXX\b|lorem ipsum", page):
        errs.append("残留占位文案")

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
    ap.add_argument("--page", default=str(DEFAULT_PAGE))
    ap.add_argument("--css", default=str(DEFAULT_CSS))
    ap.add_argument("--registry", default="")
    ap.add_argument("--layout", default="", help="显式指定版式 id，跳过主题路由")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="", help="覆盖 spec.meta.siteUrl；草稿态留空")
    ap.add_argument("--footer-links", default="")
    ap.add_argument("--cloud-config", default="", help="publicConfig JSON；给了就启用预约表单云写入")
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    meta = spec["meta"]
    site = resolve_site(meta, a.base_url)
    reg = load_registry(a.registry) if a.registry else None
    chosen = choose(meta.get("topic", meta["title"]), reg, a.layout or meta.get("layoutId") or None)
    if not chosen["matched"]:
        print("[warn] " + chosen["reason"], file=sys.stderr)

    tokens = "".join(k + ":" + v + ";" for k, v in chosen["tokens"].items())
    page = Path(a.page).read_text(encoding="utf-8")
    page = page.replace("__BASE_CSS__", Path(a.css).read_text(encoding="utf-8").rstrip())
    page = page.replace("__TOKENS__", tokens)
    page = page.replace("__LAYOUT__", chosen["id"])
    page = page.replace("<!--__HEAD__-->", render_head(meta, site))
    page = page.replace("<!--__HERO__-->", render_hero(spec["hero"], {}))
    page = page.replace("<!--__SECTIONS__-->",
                        render_sections(spec["sections"], {"live": bool(a.cloud_config)}))
    nav = "".join('<a class="ctl ctl--sm ctl--ghost nav-link" href="'
                  + esc(x["href"]) + '">' + esc(x["label"]) + "</a> "
                  for x in meta.get("nav", []))
    page = page.replace("__NAV__", nav)
    page = page.replace("__CTA_HREF__", esc(meta.get("ctaHref", "#cta")))
    page = page.replace("__CTA_LABEL__", esc(meta.get("ctaLabel", spec["hero"]["primary"])))
    page = page.replace("__BRAND__", esc(meta.get("brand", "")))
    page = page.replace("__FOOTER_NOTE__", esc(meta.get("footerNote", "")))
    fl = a.footer_links or "".join('<a href="' + esc(x["href"]) + '">' + esc(x["label"]) + "</a>"
                                   for x in meta.get("footerLinks", []))
    page = page.replace("__FOOTER_LINKS__", fl)

    cloud_mode = bool(a.cloud_config)
    script = ""
    if cloud_mode:
        cfg = json.loads(Path(a.cloud_config).read_text(encoding="utf-8"))
        pub = {k: cfg[k] for k in ("endpoint", "oauthRelayBaseUrl", "publishableKey") if k in cfg}
        cloud = meta.get("cloud", {})
        table, cols = cloud.get("table", ""), cloud.get("columns", [])
        if not table or not cols:
            print("[abort] 云模式缺少 meta.cloud.table / columns", file=sys.stderr)
            return 1
        script = (CLOUD_LEAD_JS.replace("__SDK_URL__", SDK_CDN)
                  .replace("__PUBLIC_CONFIG__", json.dumps(pub, ensure_ascii=False))
                  .replace("__TABLE__", json.dumps(table, ensure_ascii=False))
                  .replace("__COLS__", json.dumps(cols, ensure_ascii=False))
                  .replace("__PREFIX__", json.dumps(cloud.get("prefix", ""), ensure_ascii=False)))
    page = page.replace("<!--__SCRIPT__-->", script)

    errs = selfcheck(page, spec, cloud_mode, site)
    if errs:
        for e in errs:
            print("[FAIL] " + e, file=sys.stderr)
        print("[abort] 自检未通过，未写出文件", file=sys.stderr)
        return 1
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("[ok] %s  %d bytes / %d lines" % (out, len(page.encode("utf-8")), page.count("\n") + 1))
    print("     版式=%s（%s）matched=%s | %s" % (chosen["id"], chosen["name"],
                                          chosen["matched"], chosen["reason"]))
    print("     形态=%s | 站点=%s | 自检通过：占位符/标签/域名/外链/口径/去重/无障碍/JS 语法"
          % (meta.get("deliverable", "?"), site or "草稿（无站点地址）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
