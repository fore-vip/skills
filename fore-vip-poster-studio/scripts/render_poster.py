#!/usr/bin/env python3
"""海报渲染器：根据参数生成高分 PNG（及可选 SVG 预览）。

设计来源：algorithmic-poster-philosophy —— 极简、排版驱动、单色强调、CJK 自适应。
依赖：Pillow (pip install Pillow)。无需联网。CJK 字体按操作系统自动探测，不依赖安装路径。
可选：二维码渲染需 segno（纯 Python，首选）或 qrcode 之一；两者都没有则跳过二维码、其余照常。

用法示例：
  python3 render_poster.py --title "定制软件开发" \
      --tags 小程序 网站 后台 自动化脚本 \
      --cta "按需报价 · 源码交付 · 售后支持" "私聊获取专属方案 →" \
      --meta "闲鱼 · 软件开发服务" --brand "fore.vip" --accent "#ffe600" \
      --ratio 3:4 --scale 2 --out . --name poster --svg \
      --qr "https://auto.fore.vip"
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.stderr.write("缺少依赖 Pillow，请先执行: pip install Pillow\n")
    sys.exit(2)


# (regular_path, regular_index, bold_path, bold_index)
FONT_PAIRS = [
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0,
     "/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/System/Library/Fonts/PingFang.ttc", 0,
     "/System/Library/Fonts/PingFang.ttc", 0),
    ("C:/Windows/Fonts/msyh.ttc", 0,
     "C:/Windows/Fonts/msyhbd.ttf", 0),
    ("C:/Windows/Fonts/simhei.ttf", 0,
     "C:/Windows/Fonts/simhei.ttf", 0),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 0,
     "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0,
     "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0,
     "/System/Library/Fonts/Supplemental/Songti.ttc", 0),
]


def resolve_fonts():
    reg = bold = None
    for rp, ri, bp, bi in FONT_PAIRS:
        if os.path.exists(rp):
            reg = reg or (rp, ri)
        if os.path.exists(bp):
            bold = bold or (bp, bi)
        if reg and bold:
            break
    if not reg:
        sys.stderr.write("未找到可用的 CJK 字体，无法渲染中文。\n")
        sys.exit(3)
    bold = bold or reg
    return reg, bold


def load_font(path, idx, size):
    try:
        return ImageFont.truetype(path, size, index=idx)
    except Exception:
        return ImageFont.truetype(path, size, index=0)


# 归一化布局（基于 600x800 逻辑画布，y 为基线）
def layout():
    return {
        "margin": 0.10,
        "top_meta_y": 0.0975,
        "brand_y": 0.095,
        "title_y": 0.39,
        "bar": {"x": 0.10, "y": 0.43, "w": 0.50, "h": 0.0138},
        "subtitle_y": 0.49,
        "block": {"y": 0.825, "h": 0.175},
        "cta1_y": 0.89,
        "cta2_y": 0.9525,
        # 二维码：贴底部强调块右侧，静区 4 模块，边长上限取块高 76%
        "qr": {"pad_modules": 4, "max_h_ratio": 0.76},
        "fs": {
            "top_meta": 0.025, "brand": 0.019, "title": 0.0825,
            "subtitle": 0.03, "cta1": 0.0275, "cta2": 0.0375,
        },
    }


def compute(W, H, spec, L):
    m = L["margin"] * W
    def x(f):
        return f * W
    def y(f):
        return f * H
    def fs(k):
        return L["fs"][k] * H
    return {
        "margin": m,
        "m_right": (1 - L["margin"]) * W,
        "top_meta": (m, y(L["top_meta_y"]), fs("top_meta")),
        "brand": ((1 - L["margin"]) * W, y(L["brand_y"]), fs("brand")),
        "title": (m, y(L["title_y"]), fs("title")),
        "bar": (x(L["bar"]["x"]), y(L["bar"]["y"]),
                L["bar"]["w"] * W, L["bar"]["h"] * H),
        "subtitle": (m, y(L["subtitle_y"]), fs("subtitle")),
        "block": (0, y(L["block"]["y"]), W, L["block"]["h"] * H),
        "cta1": (m, y(L["cta1_y"]), fs("cta1")),
        "cta2": (m, y(L["cta2_y"]), fs("cta2")),
    }


def qr_matrix(url):
    """返回二维码模块矩阵（1=黑 / 0=白，不含静区）；无可用库或 url 为空时返回 None。"""
    if not url:
        return None
    try:
        import segno
        return [[1 if v else 0 for v in row] for row in segno.make(url, error="m").matrix]
    except ImportError:
        pass
    try:
        import qrcode
        q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
        q.add_data(url)
        q.make(fit=True)
        return [[1 if v else 0 for v in row] for row in q.get_matrix()]
    except ImportError:
        return None


def qr_geometry(W, H, L, n):
    """二维码落位：白底方块（含静区）+ 整数模块边长，保证缩放后不糊、可扫。"""
    pad = L["qr"]["pad_modules"]
    box_h = L["block"]["h"] * H
    block_y = L["block"]["y"] * H
    mod = max(2, int((box_h * L["qr"]["max_h_ratio"]) // (n + 2 * pad)))
    side = mod * (n + 2 * pad)
    x0 = (1 - L["margin"]) * W - side
    y0 = block_y + int((box_h - side) / 2)
    return {
        "matrix": None, "n": n, "mod": mod, "pad": pad,
        "white": (x0, y0, side),
        "text_right": x0 - 0.5 * L["margin"] * W,
    }


def est_width(s, size):
    """粗略估算文本宽度（CJK 全宽 ≈ 1em，其余 ≈ 0.55em），用于 PNG / SVG 一致的排版保护。"""
    return sum(size * (1.0 if ord(ch) >= 0x2000 else 0.55) for ch in s)


def fit_size(s, size, max_w):
    """文案按可用宽度收敛字号（下限 62%），仅在有二维码挤占右侧时启用。"""
    if max_w is None:
        return size
    w = est_width(s, size)
    if w <= max_w:
        return size
    scaled = size * max_w / w
    if scaled < size * 0.62:
        sys.stderr.write(
            f"提示：CTA 文案「{s}」超过二维码左侧可用宽度，已压到最小字号，建议缩短到 8 字以内。\n")
        return size * 0.62
    return scaled


def render_png(path, W, H, spec, L, reg, bold, colors, qr):
    img = Image.new("RGB", (W, H), colors["bg"])
    d = ImageDraw.Draw(img)
    c = compute(W, H, spec, L)

    reg_f = lambda s: load_font(reg[0], reg[1], s)
    bold_f = lambda s: load_font(bold[0], bold[1], s)

    if spec["meta"]:
        d.text(c["top_meta"][:2], spec["meta"], font=reg_f(c["top_meta"][2]),
               fill=colors["ink"], anchor="ls")
    if spec["brand"]:
        d.text(c["brand"][:2], spec["brand"], font=reg_f(c["brand"][2]),
               fill=colors["sub"], anchor="rs")

    d.text(c["title"][:2], spec["title"], font=bold_f(c["title"][2]),
           fill=colors["ink"], anchor="ls")

    bx, by, bw, bh = c["bar"]
    d.rectangle([bx, by, bx + bw, by + bh], fill=colors["accent"])

    if spec["subtitle"]:
        d.text(c["subtitle"][:2], spec["subtitle"], font=reg_f(c["subtitle"][2]),
               fill=colors["sub"], anchor="ls")

    blk = c["block"]
    d.rectangle([blk[0], blk[1], blk[0] + blk[2], blk[1] + blk[3]], fill=colors["accent"])

    max_w = None
    if qr:
        qx, qy, side = qr["white"]
        d.rectangle([qx, qy, qx + side - 1, qy + side - 1], fill="#ffffff")
        mod, pad, n, grid = qr["mod"], qr["pad"], qr["n"], qr["matrix"]
        ox, oy = qx + pad * mod, qy + pad * mod
        for r in range(n):
            row, start = grid[r], None
            for i in range(n + 1):
                on = i < n and row[i]
                if on and start is None:
                    start = i
                elif not on and start is not None:
                    d.rectangle([ox + start * mod, oy + r * mod,
                                 ox + i * mod - 1, oy + (r + 1) * mod - 1],
                                fill=colors["ink"])
                    start = None
        max_w = qr["text_right"] - c["cta1"][0]

    if spec["cta"]:
        lines = spec["cta"]
        if len(lines) >= 1:
            d.text(c["cta1"][:2], lines[0],
                   font=reg_f(fit_size(lines[0], c["cta1"][2], max_w)),
                   fill=colors["ink"], anchor="ls")
        if len(lines) >= 2:
            d.text(c["cta2"][:2], lines[1],
                   font=bold_f(fit_size(lines[1], c["cta2"][2], max_w)),
                   fill=colors["ink"], anchor="ls")
    img.save(path, "PNG")


def render_svg(path, spec, L, colors, qr, svg_w=680, ratio=(3, 4)):
    a, b = ratio
    svg_h = int(svg_w * b / a)
    W, H = svg_w, svg_h
    c = compute(W, H, spec, L)
    fam = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif"

    # 注意：SVG 中 y 为基线，text-anchor 用于 brand
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    parts.append(f'<rect width="{W}" height="{H}" fill="{colors["bg"]}"/>')
    if spec["meta"]:
        x, y, s = c["top_meta"]
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
                     f'font-size="{s:.1f}" font-weight="700" fill="{colors["ink"]}" '
                     f'letter-spacing="2">{spec["meta"]}</text>')
    if spec["brand"]:
        x, y, s = c["brand"]
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="end" '
                     f'font-family="{fam}" font-size="{s:.1f}" fill="{colors["sub"]}">'
                     f'{spec["brand"]}</text>')
    x, y, s = c["title"]
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
                 f'font-size="{s:.1f}" font-weight="900" fill="{colors["ink"]}" '
                 f'letter-spacing="2">{spec["title"]}</text>')
    bx, by, bw, bh = c["bar"]
    parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                 f'height="{bh:.1f}" fill="{colors["accent"]}"/>')
    if spec["subtitle"]:
        x, y, s = c["subtitle"]
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
                     f'font-size="{s:.1f}" font-weight="400" fill="{colors["sub"]}">'
                     f'{spec["subtitle"]}</text>')
    blk = c["block"]
    parts.append(f'<rect x="0" y="{blk[1]:.1f}" width="{W}" height="{blk[3]:.1f}" '
                 f'fill="{colors["accent"]}"/>')

    max_w = None
    if qr:
        qx, qy, side = qr["white"]
        parts.append(f'<rect x="{qx:.1f}" y="{qy:.1f}" width="{side:.1f}" '
                     f'height="{side:.1f}" fill="#ffffff"/>')
        mod, pad, n = qr["mod"], qr["pad"], qr["n"]
        ox, oy = qx + pad * mod, qy + pad * mod
        seg = []
        for r, row in enumerate(qr["matrix"]):
            start = None
            for i in range(n + 1):
                on = i < n and row[i]
                if on and start is None:
                    start = i
                elif not on and start is not None:
                    seg.append(f'M{ox + start * mod:.1f} {oy + r * mod:.1f}'
                               f'h{(i - start) * mod:.1f}v{mod:.1f}'
                               f'h-{(i - start) * mod:.1f}z')
                    start = None
        parts.append(f'<path d="{"".join(seg)}" fill="{colors["ink"]}"/>')
        max_w = qr["text_right"] - c["cta1"][0]

    if spec["cta"]:
        if len(spec["cta"]) >= 1:
            x, y, s = c["cta1"]
            s = fit_size(spec["cta"][0], s, max_w)
            parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
                         f'font-size="{s:.1f}" font-weight="400" fill="{colors["ink"]}">'
                         f'{spec["cta"][0]}</text>')
        if len(spec["cta"]) >= 2:
            x, y, s = c["cta2"]
            s = fit_size(spec["cta"][1], s, max_w)
            parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
                         f'font-size="{s:.1f}" font-weight="900" fill="{colors["ink"]}">'
                         f'{spec["cta"][1]}</text>')
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--tags", nargs="*", default=[])
    p.add_argument("--cta", nargs="*", default=[])
    p.add_argument("--meta", default="")
    p.add_argument("--brand", default="")
    p.add_argument("--accent", default="#ffe600")
    p.add_argument("--ink", default="#141414")
    p.add_argument("--sub", default="#5a5a5a")
    p.add_argument("--bg", default="#ffffff")
    p.add_argument("--ratio", default="3:4")
    p.add_argument("--scale", type=int, default=2)
    p.add_argument("--out", default=".")
    p.add_argument("--name", default="poster")
    p.add_argument("--svg", action="store_true")
    p.add_argument("--qr", default="", help="二维码内容（URL）；留空则不绘制二维码")
    args = p.parse_args()

    a, b = (int(v) for v in args.ratio.split(":"))
    base_h = 800 * args.scale
    W = int(base_h * a / b)
    H = base_h

    spec = {
        "title": args.title,
        "subtitle": " / ".join(args.tags) if args.tags else "",
        "cta": args.cta,
        "meta": args.meta,
        "brand": args.brand,
    }
    colors = {"bg": args.bg, "ink": args.ink, "sub": args.sub, "accent": args.accent}
    L = layout()
    reg, bold = resolve_fonts()

    qr = None
    if args.qr:
        grid = qr_matrix(args.qr)
        if grid is None:
            sys.stderr.write(
                "未找到二维码库（segno / qrcode），已跳过二维码绘制。安装：pip install segno\n")
        else:
            qr = qr_geometry(W, H, L, len(grid))
            qr["matrix"] = grid
            print(f"QR: {args.qr} ({len(grid)}x{len(grid)} 模块)")

    os.makedirs(args.out, exist_ok=True)
    png_path = os.path.join(args.out, f"{args.name}.png")
    render_png(png_path, W, H, spec, L, reg, bold, colors, qr)
    print("PNG:", png_path, f"{W}x{H}")

    if args.svg:
        svg_path = os.path.join(args.out, f"{args.name}.svg")
        render_svg(svg_path, spec, L, colors, qr, 680, (a, b))
        print("SVG:", svg_path)


if __name__ == "__main__":
    main()
