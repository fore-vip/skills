#!/usr/bin/env python3
"""静态闸门：交付形态 + 主题口径 + 内容真实性 + 叙事 + 控件样式 + 资源与无障碍边界。

用法: python3 verify_static.py --spec examples/beauty.spec.json --page index.html [--cloud]
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SDK_CDN = "https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js"
BAD_HOSTS = ("example.com", "example.org", "example.net", "localhost", "127.0.0.1")
DELIVERABLES = ("draft", "webapp", "site")
FACT_SOURCES = ("user", "placeholder", "example")
LIVE_ACTION_WORDS = ("预约", "立即", "马上", "报名", "下单", "提交")
PROCESS_WORDS = ["生成器", "spec.json", "SKILL", "模板生成", "H5App", "前凌智选",
                 "AUTO 工作室", "publicConfig", "applicationId", "现场演示"]
OLD_CONTROL_CLASSES = ["btn-p", "btn-g", "hd-cta", "d-switch", "d-acts", "stChips", "class=\"tab\""]


def visible_text(page):
    t = re.sub(r"<head[\s\S]*?</head>", "", page)
    t = re.sub(r"<script[\s\S]*?</script>", "", t)
    t = re.sub(r"<style[\s\S]*?</style>", "", t)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--page", required=True)
    ap.add_argument("--cloud", action="store_true")
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    page = Path(a.page).read_text(encoding="utf-8")
    meta = spec["meta"]
    cloud = meta.get("cloud", {})
    deliverable = meta.get("deliverable", "")
    text = visible_text(page)
    css = "\n".join(re.findall(r"<style>([\s\S]*?)</style>", page))
    checks = []

    def ck(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # 1) 交付形态契约：这是「只设计了首页」的根治点
    ck("meta.deliverable 已声明且合法", deliverable in DELIVERABLES, deliverable)
    ck("meta.intent 记录了用户原话", bool(meta.get("intent", "").strip()),
       meta.get("intent", "")[:30])
    site = (meta.get("siteUrl") or "").strip().rstrip("/")
    host = urlparse(site).netloc if site else ""
    if deliverable in ("webapp", "site"):
        ck("非草稿形态有真实站点地址", bool(site) and not any(h in host for h in BAD_HOSTS),
           site or "(空)")
    else:
        ck("草稿态未写假域名", not any(h in page for h in BAD_HOSTS),
           "、".join([h for h in BAD_HOSTS if h in page]))

    # 2) head 元数据：域名一致、分享卡自洽、零意外外链
    url = (site + "/" + meta.get("slug", "index") + ".html") if site else ""
    canon = re.findall(r'<link rel="canonical" href="([^"]+)"', page)
    ogurl = re.findall(r'<meta property="og:url" content="([^"]+)"', page)
    ldm = re.search(r'<script type="application/ld\+json">([\s\S]*?)</script>', page)
    ldurl = ""
    if ldm:
        try:
            ldurl = json.loads(ldm.group(1)).get("url", "")
        except ValueError:
            pass
    if url:
        ck("canonical / og:url / ld+json.url 三处一致且等于站点地址",
           canon == [url] and ogurl == [url] and ldurl == url,
           "canonical=%s og=%s ld=%s" % (canon[:1], ogurl[:1], ldurl[:40]))
    else:
        ck("草稿态不写 canonical / og:url / ld+json.url", not (canon or ogurl or ldurl))
    ck("有 favicon", '<link rel="icon"' in page)
    ogimg = meta.get("ogImage", "")
    large = "summary_large_image" in page
    ck("分享卡类型与 og:image 自洽", bool(ogimg) == large,
       "og:image=%s / 大图卡=%s" % (bool(ogimg), large))
    abs_urls = re.findall(r'(?:href|src)=["\'](https?://[^"\']+)', page)
    allowed = {u for u in (url, ogimg) if u}
    bad_urls = [u for u in abs_urls
                if u not in allowed and not (a.cloud and u == SDK_CDN)]
    ck("无未登记的绝对外链", not bad_urls, "、".join(bad_urls[:2]))

    # 3) 主题口径与内容真实性
    required = meta.get("requiredTerms", [])
    missing = [w for w in required if w not in text]
    ck("主题必备词全部出现（%d 个）" % len(required), not missing,
       "缺少: " + "、".join(missing) if missing else "")
    forbidden = meta.get("forbiddenTerms", []) + PROCESS_WORDS
    leaked = [w for w in forbidden if w in text]
    ck("主题禁用词与制作过程词均未出现（%d 个）" % len(forbidden), not leaked,
       "残留: " + "、".join(leaked[:6]) if leaked else "")
    leaked_raw = [w for w in PROCESS_WORDS if w in page]
    ck("脚本注释/变量里也无制作过程词", not leaked_raw, "、".join(leaked_raw[:4]))
    dis = meta.get("disclaimer", "")
    ck("口径声明出现在正文", bool(dis) and dis in text, dis[:24])
    facts = meta.get("facts")
    fact_ok = isinstance(facts, list) and all(
        isinstance(f, dict) and f.get("key") and "value" in f and f.get("source") in FACT_SOURCES
        for f in facts)
    ck("业务事实清单完整且来源合法", fact_ok,
       "%d 条" % (len(facts) if isinstance(facts, list) else 0))
    examples = [f for f in (facts or []) if isinstance(f, dict) and f.get("source") == "example"]
    demo_ok = (not examples) or (meta.get("factReview") is True
                                and any(w in dis for w in ("示例", "演示")))
    ck("业务事实清单齐备，示例事实已评审并标注", bool(facts) and demo_ok,
       "%d 条事实 / 示例 %d 条 / factReview=%s"
       % (len(facts or []), len(examples), meta.get("factReview")))
    repeats = [s.get("text", "")[:24] for s in spec["sections"]
               if len(s.get("text", "")) >= 12 and text.count(s["text"]) > 1]
    ck("区块说明没有重复渲染", not repeats, "、".join(repeats[:3]))
    bad_assert = [x.get("name", "") for x in spec.get("assertions", [])
                  if any(w in str(x.get("expect", "")) for w in ("没有发送", "不会保存", "未开放"))]
    ck("未把「业务不可用」写成 PASS 断言", not bad_assert, "、".join(bad_assert[:3]))

    # 4) 叙事顺序
    ids = re.findall(r'<section class="sect" id="([^"]+)"', page)
    want = [s.get("id", s["type"]) for s in spec["sections"]]
    ck("区块渲染顺序与 spec 完全一致", ids == want,
       "渲染=" + "/".join(ids) + " 期望=" + "/".join(want))
    ck("首屏 hero 在全部区块之前", page.find('class="hero"') < page.find('class="sect"'))
    ck("行动区 cta 存在且不在第一个区块", "cta" in want and want.index("cta") > 0,
       "cta 位置=" + str(want.index("cta") if "cta" in want else -1))

    # 5) 表单能力与 CTA 承诺必须一致
    has_form = "<form" in page
    live = bool(cloud.get("needed"))
    ck("云能力与 --cloud 参数一致", live == a.cloud,
       "spec.cloud.needed=%s / --cloud=%s" % (live, a.cloud))
    if has_form:
        ctrls = re.findall(r"<(?:input|button)\b[^>]*>", page)
        if not live:
            ck("无后端时表单控件整体禁用", all("disabled" in x for x in ctrls),
               "未禁用 %d 个" % len([x for x in ctrls if "disabled" not in x]))
            ck("无后端时有 noscript 降级提示", "<noscript>" in page)
        else:
            ck("有后端时表单可提交", all("disabled" not in x for x in ctrls))
        labels = [meta.get("ctaLabel", ""), spec["hero"].get("primary", "")]
        cta_sec = next((s for s in spec["sections"] if s["type"] == "cta"), {})
        labels.append(cta_sec.get("submit", ""))
        if not live:
            risky = [x for x in labels if any(w in x for w in LIVE_ACTION_WORDS)]
            ck("无后端时 CTA 不承诺强行动作", not risky, "、".join(risky[:3]))
        else:
            ck("有后端时 CTA 允许行动词", True)

    # 6) 控件样式一致性（静态）
    ck("存在唯一 .ctl 基类与 .ctl.is-on 选中态",
       ".ctl{" in css and ".ctl.is-on{" in css and ".ctl.on{" not in css)
    ck("无旧版控件类残留", not [c for c in OLD_CONTROL_CLASSES if c in page],
       "、".join([c for c in OLD_CONTROL_CLASSES if c in page]))
    ck("无内联样式与 JS 内联写样式",
       'style="' not in page and "style.cssText" not in page and ".style." not in page)
    buttons = re.findall(r"<(?:button|summary)\b[^>]*>", page)
    bad_btn = [b for b in buttons if "ctl" not in b]
    ck("所有可点控件统一带 ctl 类（%d 个）" % len(buttons), not bad_btn,
       "例外 " + str(len(bad_btn)) + ": " + str(bad_btn[:2]))
    inputs = re.findall(r"<input\b[^>]*>", page)
    bad_in = [i for i in inputs if "field" not in i]
    ck("所有输入框统一为 .field（%d 个）" % len(inputs), not bad_in, str(bad_in[:2]))
    ctl_blocks = re.findall(r"\.ctl[^{]*\{([^}]*)\}", css)
    hardcoded = []
    for b in ctl_blocks:
        hardcoded += [x for x in re.findall(r"\b\d+(?:\.\d+)?px\b", b) if x != "1px"]
        hardcoded += re.findall(r"#[0-9a-fA-F]{3,8}\b", b)
        hardcoded += re.findall(r"\brgba?\(", b)
    ck(".ctl 系列规则不含硬编码尺寸/色值", not hardcoded, "、".join(hardcoded[:6]))
    token_block = re.findall(r":root\{(__TOKENS__|[^}]*--[^}]*)\}", css)
    ck("版式 token 以 :root 变量集中覆盖", len(token_block) >= 2,
       "检测到 %d 个变量块" % len(token_block))
    body_layout = re.search(r'<body data-layout="([^"]+)"', page)
    actual_layout = body_layout.group(1) if body_layout else ""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pick_layout import choose
    expected = choose(meta.get("topic", meta["title"]), override=meta.get("layoutId") or None)
    ck("页面版式与主题路由结果一致", bool(actual_layout) and actual_layout == expected["id"],
       "页面=" + actual_layout + " 路由=" + expected["id"] + "（" + expected["name"] + "）")

    # 7) 无障碍与资源边界
    ck("输入框均有可读名称", all(("aria-label=" in i or 'id="f_' in i) for i in inputs))
    ck("状态容器带 role 与 aria-live",
       'role="status"' in page and "aria-live=" in page)
    ck("装饰图标带 aria-hidden", 'aria-hidden="true"' in page)
    ck("焦点态用实线描边而非半透明阴影", "outline:var(--focus-w)" in css)
    ck("窄屏导航不被 display:none 抹掉",
       not re.search(r"\.hd-nav\s+\.nav-link\s*\{[^}]*display\s*:\s*none", css))
    srcs = [s.strip().strip('"').strip("'")
            for s in re.findall(r"<script[^>]*\ssrc=([^\s>]+)", page)]
    if a.cloud:
        ck("云模式仅加载白名单 SDK", srcs == [SDK_CDN], str(srcs))
        for needle in ("createWorkBuddyCloud", "endpoint: CFG.endpoint",
                       "publishableKey: CFG.publishableKey",
                       "oauthRelayBaseUrl: CFG.oauthRelayBaseUrl"):
            ck("云接线 " + needle, needle in page)
        ck("前端未泄漏管理侧标识", "applicationId" not in page and "resourceId" not in page)
    else:
        ck("纯前端零外部脚本", not srcs, str(srcs))
    ck("无外部样式与远程图片",
       not re.search(r'<link[^>]+rel=.stylesheet|<img[^>]+src=.https?://', page))

    for name, ok, detail in checks:
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))
    bad = [c for c in checks if not c[1]]
    print("RESULT " + ("ALL PASS (%d)" % len(checks) if not bad
                       else "FAIL (%d/%d)" % (len(bad), len(checks))))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
