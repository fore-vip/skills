#!/usr/bin/env python3
"""spec + 模板 → 单文件门店 H5（首页 / 预约 / 分享 / 店主管理）

用法：
  python3 build_app.py --spec store.json --out index.html \
      --home-html home.html --home-css home.css
  python3 build_app.py --spec store.json --out index.html --home <目录>
  python3 build_app.py --spec store.json --out index.html \
      --home-html home.html --home-css home.css \
      --cloud-config /tmp/public-config.json --base-url https://xxx.example.com

不带 --cloud-config 时产出预览版：页面可看，提交按钮禁用并提示云端未接通。

首页没有内置版式：必须按 references/home-design.md 现场做设计，产出 home.html /
home.css 再注入。结构起点是 templates/home/skeleton.html / .css。
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import pathlib
import re
from html import escape as html_escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
STATUS_SET = ("pending", "confirmed", "done", "cancelled")


def fail(msg, code=2):
    print("[FAIL] " + msg)
    raise SystemExit(code)


def mix_with_white(hex_color, ratio=0.12):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        fail("store.brand 需要 6 位十六进制色值，收到：" + hex_color)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r = round(255 - (255 - r) * ratio)
    g = round(255 - (255 - g) * ratio)
    b = round(255 - (255 - b) * ratio)
    return "#%02x%02x%02x" % (r, g, b)


def darken(hex_color, strength=0.38):
    """往黑里压，用于深色首屏的渐变压暗端。"""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    k = 1 - strength
    return "#%02x%02x%02x" % (round(r * k), round(g * k), round(b * k))


def luminance(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    chans = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        chans.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def root_tokens(brand):
    """品牌色派生：浅色品牌自动改用深字与深底色，避免白字压浅黄这类不可读组合。"""
    lum = luminance(brand)
    light = lum > 0.30          # 白字对比不足 3:1 时改用深字
    deep = "#3d332e" if lum > 0.72 else darken(brand, 0.42)
    hero = darken(brand, 0.5) if light else brand   # 渐变亮端：浅色品牌压暗，保证白字可读
    ink = darken(brand, 0.45) if lum > 0.55 else brand  # 浅底上的品牌文字色
    return (
        ":root{\n"
        "  --brand:%s;--brand-soft:%s;--brand-wash:%s;--brand-deep:%s;--brand-hero:%s;--brand-ink:%s;--on-brand:%s;\n"
        "}\n" % (brand.lower(), mix_with_white(brand), mix_with_white(brand, 0.055), deep, hero, ink,
                  "#241d1a" if light else "#fff")
    )


def load_home(args):
    """首页设计与业务解耦：结构锚点必须齐，观感由调用方现场产出。"""
    if args.layout:
        fail("--layout 已废弃：首页不再有内置版式。\n"
             "  按 references/home-design.md 现场做设计，产出 home.html / home.css 后：\n"
             "  --home-html home.html --home-css home.css")

    html_path = css_path = None
    if args.home:
        base = pathlib.Path(args.home)
        html_path, css_path = base / "home.html", base / "home.css"
    if args.home_html:
        html_path = pathlib.Path(args.home_html)
    if args.home_css:
        css_path = pathlib.Path(args.home_css)

    if not html_path or not css_path:
        fail("首页要现场设计，构建时必须给设计文件：\n"
             "  --home-html <home.html> --home-css <home.css>   或   --home <目录>\n"
             "  结构起点：templates/home/skeleton.html / .css\n"
             "  做法与 brief 字段：references/home-design.md")

    for p in (html_path, css_path):
        if not p.is_file():
            fail("找不到首页设计文件：" + str(p))

    home_html = html_path.read_text(encoding="utf-8").strip()
    home_css = css_path.read_text(encoding="utf-8").strip()
    if not home_html:
        fail("首页 HTML 是空的：" + str(html_path))
    if not home_css:
        fail("首页 CSS 是空的：" + str(css_path))

    name = (args.home_name or html_path.stem).strip()
    if name in ("home", "index"):
        name = html_path.parent.name or "custom"
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,32}", name):
        fail("首页设计名只能用小写字母 / 数字 / 连字符（2–33 位），收到：" + name)

    if 'data-view="home"' not in home_html or 'id="view-home"' not in home_html:
        fail("首页设计文件必须是一段 section：<section ... data-view=\"home\" id=\"view-home\" "
             "data-home=\"%s\">，收到 %s" % (name, html_path))

    if "data-home=" in home_html:
        home_html = re.sub(r'data-home="[^"]*"', 'data-home="%s"' % name, home_html, count=1)
    else:
        home_html = home_html.replace('data-view="home"', 'data-view="home" data-home="%s"' % name, 1)

    hooks = {
        'id="svcList"': "服务列表容器（<ul id=\"svcList\">）",
        'id="storeInfo"': "到访信息容器（<div id=\"storeInfo\">）",
        'data-go="book"': "主按钮（立即预约 → #/book）",
    }
    missing = [label for hook, label in hooks.items() if hook not in home_html]
    if missing:
        fail("首页设计缺接线：\n  - " + "\n  - ".join(missing) +
             "\n  这三个锚点由 app.js 驱动，必须保留（见 references/home-design.md 第一节）")

    if "var(--brand" not in home_css:
        print("[warn] 首页 CSS 没用到品牌令牌 var(--brand…)，观感可能与门店脱节")

    return name, home_html, home_css, str(html_path)


def load_spec(path):
    try:
        spec = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("找不到 spec：" + str(path))
    except json.JSONDecodeError as e:
        fail("spec 不是合法 JSON：" + str(e))

    errs = []
    store = spec.get("store") or {}
    for key, label in (("name", "店名"), ("slogan", "一句话主张"), ("phone", "电话"),
                       ("address", "地址"), ("hours", "营业时间")):
        if not str(store.get(key, "")).strip():
            errs.append("store.%s（%s）不能为空" % (key, label))
    brand = str(store.get("brand", "#b4735a")).strip()
    if not re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", brand):
        errs.append("store.brand 需要 #RRGGBB 形式，收到：" + brand)
    services = spec.get("services") or []
    if not services:
        errs.append("services 至少给一项服务")
    for i, s in enumerate(services):
        for key in ("name", "price", "duration"):
            if not str(s.get(key, "")).strip():
                errs.append("services[%d].%s 不能为空" % (i, key))

    booking = spec.get("booking") or {}
    days = booking.get("days")
    if not isinstance(days, int) or not 1 <= days <= 30:
        errs.append("booking.days 需要 1–30 的整数")
    slots = booking.get("slots") or []
    if not slots:
        errs.append("booking.slots 至少给一个时段，例如 \"10:00\"")
    for s in slots:
        if not re.fullmatch(r"\d{1,2}:\d{2}", str(s)):
            errs.append("booking.slots 里有不合法的时段：" + str(s))

    admin = spec.get("admin") or {}
    if admin.get("login", "email") not in ("email", "phone"):
        errs.append("admin.login 只能是 email 或 phone")

    cloud = spec.get("cloud") or {}
    if cloud.get("bookings", "bookings") != "bookings":
        errs.append("cloud.bookings 固定为 bookings，与建表脚本一致")

    if errs:
        fail("spec 校验失败：\n  - " + "\n  - ".join(errs))
    return spec


def load_cloud_config(path):
    try:
        cfg = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("找不到云配置：" + str(path))
    except json.JSONDecodeError as e:
        fail("云配置不是合法 JSON：" + str(e))

    # 平台返回的结构可能是 {data:{...}} 或直接字段
    if isinstance(cfg.get("data"), dict):
        cfg = cfg["data"]
    need = ("endpoint", "publishableKey")
    missing = [k for k in need if not str(cfg.get(k, "")).strip()]
    if missing:
        fail("云配置缺少字段：" + ", ".join(missing))
    out = {
        "endpoint": cfg["endpoint"],
        "oauthRelayBaseUrl": cfg.get("oauthRelayBaseUrl", ""),
        "publishableKey": cfg["publishableKey"],
    }
    for banned in ("applicationId", "resourceId", "serviceRoleKey", "secretKey"):
        if banned in cfg:
            print("[warn] 云配置含 %s，已丢弃（不得进前端）" % banned)
    return out


def js_json(obj):
    text = json.dumps(obj, ensure_ascii=False, indent=None, separators=(",", ":"))
    return text.replace("</", "<\\/")


def price_range(services):
    nums = []
    for s in services or []:
        m = re.findall(r"\d+(?:\.\d+)?", str(s.get("price", "")))
        if m:
            nums.append(float(m[0]))
    if not nums:
        return ""
    lo, hi = min(nums), max(nums)
    return "¥%g" % lo if lo == hi else "¥%g-¥%g" % (lo, hi)


def opening_hours(text):
    m = re.search(r"(\d{1,2}:\d{2})\s*[–—\-~～至到]\s*(\d{1,2}:\d{2})", str(text or ""))
    if not m:
        return None
    return [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"],
        "opens": m.group(1),
        "closes": m.group(2),
    }]


def structured_data(base_url, spec):
    """LocalBusiness 结构化数据：给搜索引擎与生成式引擎（GEO）读的机器可读事实。"""
    store = spec["store"]
    node = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": store["name"],
        "description": store.get("slogan", ""),
        "url": base_url,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": store.get("address", ""),
            "addressCountry": "CN",
        },
        "potentialAction": {
            "@type": "ReserveAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": base_url + "#/book",
                "inLanguage": "zh-CN",
                "actionPlatform": [
                    "http://schema.org/DesktopWebPlatform",
                    "http://schema.org/MobileWebPlatform",
                ],
            },
        },
    }
    if store.get("phone"):
        node["telephone"] = str(store["phone"])
    rng = price_range(spec.get("services"))
    if rng:
        node["priceRange"] = rng
    hours = opening_hours(store.get("hours"))
    if hours:
        node["openingHoursSpecification"] = hours
    offers = []
    for s in (spec.get("services") or [])[:8]:
        price = re.findall(r"\d+(?:\.\d+)?", str(s.get("price", "")))
        offer = {
            "@type": "Offer",
            "itemOffered": {"@type": "Service", "name": s.get("name", "")},
            "priceCurrency": "CNY",
        }
        if price:
            offer["price"] = price[0]
        if s.get("desc"):
            offer["description"] = s["desc"]
        offers.append(offer)
    if offers:
        node["makesOffer"] = offers
    return node


def head_extra(base_url, spec):
    if not base_url:
        return ""
    store = spec["store"]
    title = "%s · 在线预约" % store["name"]
    lines = [
        '<link rel="canonical" href="%s">' % base_url,
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="%s">' % store["name"],
        '<meta property="og:locale" content="zh_CN">',
        '<meta property="og:title" content="%s">' % title,
        '<meta property="og:description" content="%s">' % store["slogan"],
        '<meta property="og:url" content="%s">' % base_url,
        '<script type="application/ld+json">%s</script>'
        % js_json(structured_data(base_url, spec)),
    ]
    return "\n".join(lines)


def home_block_of(html):
    """首页板块的边界：到下个视图（book）或 main 结束为止。
    设计里允许嵌套 section，所以不能按第一个 </section> 截断。"""
    m = re.search(r'data-view="home".*?(?=data-view="book"|</main>)', html, re.S)
    return m.group(0) if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--home", help="首页设计目录（内含 home.html / home.css）")
    ap.add_argument("--home-html", help="首页设计 HTML（含 data-view=\"home\" 的 section）")
    ap.add_argument("--home-css", help="首页设计 CSS")
    ap.add_argument("--home-name", help="设计名，默认取 home.html 的文件名")
    ap.add_argument("--layout", help=argparse.SUPPRESS)
    ap.add_argument("--cloud-config")
    ap.add_argument("--base-url", default="")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    store = spec["store"]
    admin = spec.get("admin") or {}
    login = admin.get("login", "email")
    brand = store.get("brand", "#b4735a")
    base_url = args.base_url.rstrip("/") + "/" if args.base_url else ""
    cfg = load_cloud_config(args.cloud_config) if args.cloud_config else None
    home_name, home_html, home_css, home_src = load_home(args)

    if cfg and not base_url:
        fail("接了云就必须给 --base-url，Origin 要对得上真实域名")

    css = (TPL / "app.css").read_text(encoding="utf-8")
    css = css.replace("__ROOT_TOKENS__", root_tokens(brand))
    css = css.rstrip() + "\n\n/* home:%s */\n%s" % (home_name, home_css.rstrip() + "\n")

    js = (TPL / "app.js").read_text(encoding="utf-8")
    html = (TPL / "app.html").read_text(encoding="utf-8").replace("<!--__HOME__-->", home_html.rstrip())

    sdk = ""
    if cfg:
        sdk = ('<script src="https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/'
               'lib/index.global.js"></script>')

    tokens = {
        "__CSS__": css,
        "__JS__": js,
        "__SPEC_JSON__": js_json(spec),
        "__CFG_JSON__": js_json(cfg) if cfg else "null",
        "__SDK__": sdk,
        "__HEAD_EXTRA__": head_extra(base_url, spec),
        "__TITLE__": "%s · 在线预约" % store["name"],
        "__DESC__": store["slogan"],
        "__THEME_COLOR__": store.get("brand", "#b4735a"),
        "__LOGO__": store["name"][:1],
        "__STORE_NAME__": store["name"],
        "__SLOGAN__": store["slogan"],
        "__HERO_SUB__": store.get("heroSub") or "点下方按钮选服务与时间，到店核销",
        "__INVITE_TITLE__": (spec.get("share") or {}).get("inviteTitle") or "邀请好友到店体验",
        "__SVC_COUNT__": str(len(spec["services"])),
        "__HOURS__": html_escape(store["hours"]),
        "__ADDRESS__": html_escape(store["address"]),
        "__PHONE__": html_escape(store["phone"]),
        "__LOGIN_LABEL__": "店主邮箱" if login == "email" else "店主手机号",
        "__LOGIN_PLACEHOLDER__": "owner@example.com" if login == "email" else "11 位手机号",
    }
    for key, value in tokens.items():
        html = html.replace(key, value)

    left = re.findall(r"__[A-Z][A-Z0-9_]*__", html)
    if left:
        fail("模板还有未替换的占位符：" + ", ".join(sorted(set(left))))

    for view in ("home", "book", "share", "admin"):
        if 'data-view="%s"' % view not in html:
            fail("生成结果缺视图：" + view)
    for status in STATUS_SET:
        if status + ":" not in html:
            fail("生成结果缺状态枚举：" + status)

    home_block = home_block_of(html)
    if 'data-home="%s"' % home_name not in home_block:
        fail("首页设计名没写进页面：" + home_name)
    for hook in ('id="svcList"', 'id="storeInfo"', 'data-go="book"'):
        if hook not in home_block:
            fail("首页设计 %s 缺接线：%s" % (home_name, hook))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    mode = "云模式（可收单）" if cfg else "预览模式（提交禁用）"
    print("[ok] %s  %.1f KB" % (out, out.stat().st_size / 1024))
    print("     门店=%s | 服务 %d 项 | 时段 %d 个 | %s" % (
        store["name"], len(spec["services"]), len(spec["booking"]["slots"]), mode))
    print("     首页设计=%s  ← %s" % (home_name, home_src))
    if base_url:
        print("     站点=%s | 分享链接带 ?ref=<邀请码>" % base_url)
    if not cfg:
        print("     下一步：python3 build_app.py --spec %s --out %s "
              "--cloud-config <publicConfig.json> --base-url <真实域名>" % (args.spec, args.out))


if __name__ == "__main__":
    main()
