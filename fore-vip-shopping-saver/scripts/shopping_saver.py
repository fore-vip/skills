#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购物超省 · 聚合脚本  (fore-vip-shopping-saver)

从用户配置的多个购物 / 导购 / 联盟接口 (providers.json) 汇聚商品信息，
规范化到统一数据模型，按「质量评分 / 价格 / 券后价」排序，
生成自包含的优雅 HTML 列表（无封面图或跨域图片自动占位）。

设计原则：
- 仅使用 Python 标准库，无第三方依赖（urllib / json / argparse / re ...）。
- 通用 key-based HTTP 适配器：覆盖只需 apikey (+secret) 的接口（聚推客 / 折淘客 / 多数导购 API）。
- 自定义适配器钩子：签名类开放平台（淘宝联盟 / 京东联盟 / 拼多多）可放一个 custom 适配器文件接管"请求"阶段，
  响应解析仍走统一的 items_path + fields 映射，无需改脚本。
- 密钥不写死：支持 providers.json 的 secrets 段，或环境变量 ${ENV}；推荐用环境变量避免落盘泄露。

用法：
  python3 shopping_saver.py --keyword "iPhone 15" [--config providers.json] \
                            [--sort score|price|coupon] [--limit 30] [--output result.html]
"""
import argparse
import datetime
import html
import importlib.util
import json
import os
import re
import sys
import urllib.parse
import urllib.request

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 无图 / 跨域占位图（自包含 data-URI SVG，避免外链依赖）
PLACEHOLDER = "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">'
    '<rect width="400" height="400" fill="#f1f3f5"/>'
    '<text x="50%" y="50%" font-family="sans-serif" font-size="30" fill="#adb5bd" '
    'text-anchor="middle" dominant-baseline="middle">无商品图</text>'
    "</svg>"
)


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------
def resolve_path(obj, path):
    """按点 / 方括号路径取值，如 'a.b[0].c'。取不到返回 None。"""
    if not path:
        return obj
    cur = obj
    for tok in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        if tok.startswith("[") and tok.endswith("]"):
            try:
                idx = int(tok[1:-1])
            except ValueError:
                return None
            if isinstance(cur, list) and 0 <= idx < len(cur):
                cur = cur[idx]
            else:
                return None
        else:
            if isinstance(cur, dict) and tok in cur:
                cur = cur[tok]
            else:
                return None
    return cur


def resolve_template(value, ctx):
    """递归替换 {keyword} 与 ${ENV}（ENV 优先取 secrets 段，回退环境变量）。"""
    if isinstance(value, str):
        value = value.replace("{keyword}", ctx.get("keyword", ""))
        value = re.sub(
            r"\$\{([A-Za-z0-9_]+)\}",
            lambda m: (ctx.get("secrets") or {}).get(m.group(1))
            or os.environ.get(m.group(1), ""),
            value,
        )
        return value
    if isinstance(value, dict):
        return {k: resolve_template(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_template(v, ctx) for v in value]
    return value


def to_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").replace("¥", "").replace("￥", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 请求阶段（适配器）
# ---------------------------------------------------------------------------
def do_generic(provider, ctx):
    """通用 key-based 适配器：按 request 段构造并发送 HTTP 请求，返回解析后的 JSON。"""
    req = provider.get("request", {})
    method = (req.get("method") or "GET").upper()
    url = resolve_template(req.get("url"), ctx)
    headers = resolve_template(req.get("headers") or {}, ctx)
    query = resolve_template(req.get("query") or {}, ctx)
    body = resolve_template(req.get("body"), ctx)

    if method == "GET":
        if query:
            qs = urllib.parse.urlencode(query)
            url = url + ("&" if "?" in url else "?") + qs
        r = urllib.request.Request(url, headers=headers)
    else:
        r = urllib.request.Request(url, method=method, headers=headers)
        if body is not None:
            r.add_header("Content-Type", "application/json")
            r.data = json.dumps(body).encode("utf-8")

    with urllib.request.urlopen(r, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_custom_adapter(path):
    fp = path if os.path.isabs(path) else os.path.join(SKILL_DIR, path)
    if not os.path.exists(fp):
        raise FileNotFoundError("custom adapter not found: " + fp)
    spec = importlib.util.spec_from_file_location("custom_adapter", fp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_provider(provider, ctx):
    """执行单个 provider 的请求阶段，返回解析后的响应 JSON（失败返回 None 并继续）。"""
    adapter = provider.get("adapter", "generic")
    try:
        if not adapter or adapter == "generic":
            return do_generic(provider, ctx)
        if adapter.startswith("custom:"):
            mod = load_custom_adapter(adapter.split(":", 1)[1])
            fn = getattr(mod, "request", None)
            if not callable(fn):
                raise AttributeError("custom adapter 必须定义 request(keyword, provider, ctx)")
            return fn(keyword=ctx["keyword"], provider=provider, ctx=ctx)
        raise ValueError("unknown adapter: " + str(adapter))
    except Exception as e:  # 单 provider 失败不应中断整体
        print(f"[warn] provider {provider.get('name')} 请求失败: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# 响应解析 + 规范化
# ---------------------------------------------------------------------------
def extract_items(resp, provider):
    if not resp:
        return []
    items_path = provider.get("response", {}).get("items_path")
    items = resolve_path(resp, items_path) if items_path else resp
    if items is None:
        return []
    if isinstance(items, dict):
        items = [items]
    return items if isinstance(items, list) else []


def normalize(item, provider, ctx):
    fields = provider.get("response", {}).get("fields", {})
    rec = {
        "source": provider.get("name", ""),
        "title": None,
        "image": None,
        "sku_images": [],
        "price": None,
        "coupon_amount": None,
        "coupon_url": None,
        "score": None,
        "product_url": None,
    }
    for out_key, spec in fields.items():
        if isinstance(spec, str) and spec.startswith("const:"):
            val = resolve_template(spec[6:], ctx)
        else:
            val = resolve_path(item, spec)
        rec[out_key] = val

    rec["price"] = to_float(rec["price"])
    rec["coupon_amount"] = to_float(rec["coupon_amount"])
    rec["score"] = to_float(rec["score"])

    if rec["sku_images"] is None:
        rec["sku_images"] = []
    elif not isinstance(rec["sku_images"], list):
        rec["sku_images"] = [rec["sku_images"]]

    if rec["price"] is not None and rec["coupon_amount"]:
        rec["price_after_coupon"] = round(rec["price"] - rec["coupon_amount"], 2)
    elif rec["price"] is not None:
        rec["price_after_coupon"] = rec["price"]
    else:
        rec["price_after_coupon"] = None
    return rec


# ---------------------------------------------------------------------------
# 排序
# ---------------------------------------------------------------------------
def sort_key(r, mode):
    price = r["price"] if r["price"] is not None else float("inf")
    pac = r["price_after_coupon"] if r["price_after_coupon"] is not None else price
    score = r["score"] if r["score"] is not None else 0.0
    if mode == "price":
        return (price,)
    if mode == "coupon":
        return (pac,)
    # 默认：质量评分降序 → 券后价升序
    return (-score, pac)


# ---------------------------------------------------------------------------
# HTML 渲染
# ---------------------------------------------------------------------------
def render_card(r):
    title = html.escape(r["title"] or "未命名商品", quote=True)
    source = html.escape(r.get("source") or "", quote=True)

    img = r["image"]
    img_src = PLACEHOLDER if not img else img
    img_tag = (
        f'<img src="{html.escape(img_src, True)}" referrerpolicy="no-referrer" '
        f'loading="lazy" onerror="this.onerror=null;this.src=\'{PLACEHOLDER}\'">'
    )

    score_html = ""
    if r["score"] is not None:
        score_html = f'<span class="score">评分 {r["score"]:g}</span>'

    price_html = ""
    if r["price_after_coupon"] is not None:
        price_html += f'<span class="now">¥{r["price_after_coupon"]:g}</span>'
        if r["coupon_amount"] and r["price"] is not None:
            price_html += f'<span class="was">¥{r["price"]:g}</span>'
    elif r["price"] is not None:
        price_html += f'<span class="now">¥{r["price"]:g}</span>'
    else:
        price_html += '<span class="now muted">价格待查</span>'

    coupon_html = ""
    if r["coupon_amount"]:
        amt = r["coupon_amount"]
        if r["coupon_url"]:
            coupon_html = (
                f'<a class="coupon" href="{html.escape(r["coupon_url"], True)}" '
                f'target="_blank" rel="noopener">领券 ¥{amt:g}</a>'
            )
        else:
            coupon_html = f'<span class="coupon">券 ¥{amt:g}</span>'

    buy_html = ""
    if r["product_url"]:
        buy_html = (
            f'<a class="buy" href="{html.escape(r["product_url"], True)}" '
            f'target="_blank" rel="noopener">去购买</a>'
        )

    return f"""<article class="card">
  <div class="thumb">{img_tag}</div>
  <div class="body">
    <h3 class="title">{title}</h3>
    <div class="meta"><span class="src">{source}</span>{score_html}</div>
    <div class="price">{price_html}{coupon_html}</div>
    {buy_html}
  </div>
</article>"""


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>购物超省 · {keyword}</title>
<style>
:root{{
  --bg:#f6f7f9; --card:#fff; --ink:#1f2329; --sub:#8a9099;
  --accent:#e53e3e; --accent-soft:#fff1f0; --line:#eceef1; --radius:16px;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  line-height:1.5;padding:32px 20px 60px;}}
.wrap{{max-width:1100px;margin:0 auto;}}
header h1{{font-size:24px;margin:0 0 6px;font-weight:700;letter-spacing:.5px;}}
header p{{margin:0;color:var(--sub);font-size:14px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px;margin-top:26px;}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;
  display:flex;flex-direction:column;transition:transform .15s ease,box-shadow .15s ease;}}
.card:hover{{transform:translateY(-3px);box-shadow:0 10px 28px rgba(17,24,39,.10);}}
.thumb{{aspect-ratio:1/1;background:#f1f3f5;overflow:hidden;}}
.thumb img{{width:100%;height:100%;object-fit:cover;display:block;}}
.body{{padding:14px 15px 16px;display:flex;flex-direction:column;gap:9px;flex:1;}}
.title{{font-size:15px;font-weight:600;margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:44px;}}
.meta{{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--sub);}}
.src{{background:var(--accent-soft);color:var(--accent);padding:2px 8px;border-radius:999px;font-weight:600;}}
.score{{color:var(--sub);}}
.price{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-top:auto;}}
.now{{color:var(--accent);font-size:20px;font-weight:800;}}
.now.muted{{color:var(--sub);font-size:14px;font-weight:600;}}
.was{{color:var(--sub);font-size:13px;text-decoration:line-through;}}
.coupon{{background:linear-gradient(135deg,#ff7a45,#e53e3e);color:#fff;font-size:12px;font-weight:700;padding:3px 9px;border-radius:8px;text-decoration:none;}}
.buy{{display:block;text-align:center;background:var(--ink);color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:9px 0;border-radius:10px;}}
.buy:hover{{opacity:.9;}}
.empty{{color:var(--sub);text-align:center;padding:60px 0;}}
footer{{margin-top:34px;color:var(--sub);font-size:12px;text-align:center;}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>购物超省 · {keyword}</h1>
    <p>共 {total} 条 · 排序：{sort} · 来源 {src} · 生成于 {date}</p>
  </header>
  <div class="grid">
{cards}
  </div>
  <footer>数据来自已配置的购物 / 导购 / 联盟接口；价格与优惠券以平台实时为准，图片受防盗链限制时显示占位图。</footer>
</div>
</body>
</html>"""


def render_html(recs, args, counts):
    if recs:
        cards = "\n".join(render_card(r) for r in recs)
    else:
        cards = '<p class="empty">未从已配置来源获取到商品，请检查 providers 配置或换关键词。</p>'
    src_line = " · ".join(f"{k}×{v}" for k, v in counts.items()) or "无"
    sort_label = {"score": "质量评分", "price": "价格升序", "coupon": "券后价升序"}[args.sort]
    return TEMPLATE.format(
        keyword=html.escape(args.keyword, True),
        total=len(recs),
        sort=sort_label,
        src=src_line,
        cards=cards,
        date=datetime.date.today().isoformat(),
    )


# ---------------------------------------------------------------------------
# 配置发现
# ---------------------------------------------------------------------------
def find_config(explicit):
    candidates = []
    if explicit:
        candidates.append(explicit)
    env = os.environ.get("SHOPPING_SAVER_CONFIG")
    if env:
        candidates.append(env)
    candidates.append(os.path.expanduser("~/.workbuddy/fore-vip-shopping-saver/providers.json"))
    candidates.append(os.path.join(SKILL_DIR, "config", "providers.json"))
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def default_output(keyword):
    safe = re.sub(r"[^\w一-龥-]+", "_", keyword).strip("_") or "result"
    return f"购物超省_{safe}_{datetime.date.today().isoformat()}.html"


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="购物超省 · 商品聚合脚本")
    ap.add_argument("--keyword", required=True, help="商品名称关键词")
    ap.add_argument("--config", help="providers.json 路径（默认按 SHOPPING_SAVER_CONFIG / ~/.workbuddy / <skill>/config 顺序查找）")
    ap.add_argument("--sort", choices=["score", "price", "coupon"], default="score")
    ap.add_argument("--limit", type=int, default=30, help="输出条数上限")
    ap.add_argument("--output", help="HTML 输出路径（默认 购物超省_<关键词>_<日期>.html）")
    args = ap.parse_args()

    cfg_path = find_config(args.config)
    if not cfg_path:
        print("ERROR: 未找到 providers.json 配置。请先按 references/providers.md 配置 ≥3 个来源。", file=sys.stderr)
        sys.exit(2)

    with open(cfg_path, encoding="utf-8") as f:
        config = json.load(f)
    ctx = {"keyword": args.keyword, "secrets": config.get("secrets", {}) or {}}

    providers = [p for p in config.get("providers", []) if p.get("enabled", True)]
    if len(providers) < 3:
        print(f"[warn] 仅配置 {len(providers)} 个来源，任务要求至少 3 个。", file=sys.stderr)

    all_recs, counts = [], {}
    for p in providers:
        resp = run_provider(p, ctx)
        items = extract_items(resp, p)
        recs = [normalize(it, p, ctx) for it in items]
        recs = [r for r in recs if r.get("title") or r.get("product_url")]  # 丢弃空记录
        counts[p.get("name", "?")] = len(recs)
        all_recs.extend(recs)

    all_recs.sort(key=lambda r: sort_key(r, args.sort))
    if args.limit and args.limit > 0:
        all_recs = all_recs[: args.limit]

    out = args.output or default_output(args.keyword)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render_html(all_recs, args, counts))

    print(json.dumps({
        "keyword": args.keyword,
        "sort": args.sort,
        "sources_tried": len(providers),
        "per_source": counts,
        "total": len(all_recs),
        "output": out,
        "top3": [r["title"] for r in all_recs[:3]],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
