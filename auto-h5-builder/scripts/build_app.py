#!/usr/bin/env python3
"""spec + 模板 → 单文件门店 H5（首页 / 预约 / 分享 / 店主管理）

用法：
  python3 build_app.py --spec store.json --out index.html
  python3 build_app.py --spec store.json --out index.html \
      --cloud-config /tmp/public-config.json --base-url https://xxx.example.com

不带 --cloud-config 时产出预览版：页面可看，提交按钮禁用并提示云端未接通。
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import pathlib
import re

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


def head_extra(base_url, spec):
    if not base_url:
        return ""
    store = spec["store"]
    title = "%s · 在线预约" % store["name"]
    lines = [
        '<link rel="canonical" href="%s">' % base_url,
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="%s">' % title,
        '<meta property="og:description" content="%s">' % store["slogan"],
        '<meta property="og:url" content="%s">' % base_url,
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cloud-config")
    ap.add_argument("--base-url", default="")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    store = spec["store"]
    admin = spec.get("admin") or {}
    login = admin.get("login", "email")
    base_url = args.base_url.rstrip("/") + "/" if args.base_url else ""
    cfg = load_cloud_config(args.cloud_config) if args.cloud_config else None

    if cfg and not base_url:
        fail("接了云就必须给 --base-url，Origin 要对得上真实域名")

    css = (TPL / "app.css").read_text(encoding="utf-8")
    css = css.replace("--brand:#b4735a", "--brand:" + store.get("brand", "#b4735a").lower())
    css = css.replace("--brand-soft:#f8ece6", "--brand-soft:" + mix_with_white(store.get("brand", "#b4735a")))

    js = (TPL / "app.js").read_text(encoding="utf-8")
    html = (TPL / "app.html").read_text(encoding="utf-8")

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
        "__INVITE_TITLE__": (spec.get("share") or {}).get("inviteTitle") or "邀请好友来做护理",
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

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    mode = "云模式（可收单）" if cfg else "预览模式（提交禁用）"
    print("[ok] %s  %.1f KB" % (out, out.stat().st_size / 1024))
    print("     门店=%s | 服务 %d 项 | 时段 %d 个 | %s" % (
        store["name"], len(spec["services"]), len(spec["booking"]["slots"]), mode))
    if base_url:
        print("     站点=%s | 分享链接带 ?ref=<邀请码>" % base_url)
    if not cfg:
        print("     下一步：python3 build_app.py --spec %s --out %s "
              "--cloud-config <publicConfig.json> --base-url <真实域名>" % (args.spec, args.out))


if __name__ == "__main__":
    main()
