#!/usr/bin/env python3
"""通用手绘漫画合成器：读取 JSON 配置，输出拼版图 + 手绘感气泡 + 中文对白。

用法:
    python compose_comic.py <spec.json>

配置字段说明见 ../references/spec-format.md，最小示例见同目录 spec.example.json。
本脚本不依赖任何工作区路径，全部素材与输出路径均由 spec 提供。
"""

import json
import math
import random
import sys
from PIL import Image, ImageDraw, ImageFont

DEFAULT_FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
INK = (43, 39, 36)
RED = (198, 58, 52)


def hex_to_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def pick_font(path, size):
    """ttc 内含多字面，用像素密度探测自动挑最粗的那个。"""
    best, best_dark = 0, -1
    for idx in range(4):
        try:
            f = ImageFont.truetype(path, size, index=idx)
        except Exception:
            break
        probe = Image.new("L", (520, 160), 255)
        ImageDraw.Draw(probe).text((10, 20), "为什么 Why", font=f, fill=0)
        dark = sum(probe.histogram()[:128])
        if dark > best_dark:
            best, best_dark = idx, dark
    if best_dark < 0:
        raise SystemExit(f"无法加载字体: {path}")
    return ImageFont.truetype(path, size, index=best)


def jitter_ellipse(cx, cy, rx, ry, seed, jitter=4.0, n=240):
    rnd = random.Random(seed)
    return [(cx + (rx + rnd.uniform(-jitter, jitter)) * math.cos(2 * math.pi * i / n),
             cy + (ry + rnd.uniform(-jitter, jitter)) * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def jitter_round_rect(x0, y0, x1, y1, rad, seed, jitter=2.6, seg=30):
    rnd = random.Random(seed)

    def wobble(a, b, steps):
        return [(a[0] + (b[0] - a[0]) * (i / steps) + rnd.uniform(-jitter, jitter),
                 a[1] + (b[1] - a[1]) * (i / steps) + rnd.uniform(-jitter, jitter))
                for i in range(steps + 1)]

    pts = []
    pts += wobble((x0 + rad, y0), (x1 - rad, y0), seg)
    pts += wobble((x1 - rad, y0), (x1, y0 + rad), 6)
    pts += wobble((x1, y0 + rad), (x1, y1 - rad), seg)
    pts += wobble((x1, y1 - rad), (x1 - rad, y1), 6)
    pts += wobble((x1 - rad, y1), (x0 + rad, y1), seg)
    pts += wobble((x0 + rad, y1), (x0, y1 - rad), 6)
    pts += wobble((x0, y1 - rad), (x0, y0 + rad), seg)
    pts += wobble((x0, y0 + rad), (x0 + rad, y0), 6)
    return pts


def jitter_burst(cx, cy, rx, ry, seed, spikes=15, inner=0.80):
    rnd = random.Random(seed)
    pts = []
    for i in range(spikes * 2):
        a = math.pi * i / spikes - math.pi / 2
        k = (1.0 if i % 2 == 0 else inner) + rnd.uniform(-0.05, 0.05)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def shape_points(sh, cx, cy, rx, ry, seed):
    if sh == "ellipse":
        return jitter_ellipse(cx, cy, rx, ry, seed)
    if sh == "roundrect":
        return jitter_round_rect(cx - rx, cy - ry, cx + rx, cy + ry, min(rx, ry) * 0.45, seed)
    if sh == "burst":
        return jitter_burst(cx, cy, rx, ry, seed)
    raise SystemExit(f"未知气泡形状: {sh}（可选 ellipse / roundrect / burst）")


def avail_height(sh, rx, ry, block_w):
    """给定文字块宽度，返回该形状内可用的总高度。"""
    if sh == "ellipse":
        half = block_w / (2 * rx)
        if half >= 1:
            return 0.0
        return 2 * ry * math.sqrt(1 - half ** 2)
    if sh == "roundrect":
        return 2 * ry - 30
    return 2 * ry * 0.72


def tail_dot_in(rx, ry, sh, shape_cx, shape_cy, px, py):
    """校验尾巴基点是否落在气泡主体内部（否则三角形底边外露穿帮）。"""
    dx, dy = (px - shape_cx) / rx, (py - shape_cy) / ry
    d = dx * dx + dy * dy
    if sh == "roundrect":
        return abs(dx) <= 0.97 and abs(dy) <= 0.97
    return d < (0.97 if sh == "ellipse" else 0.93)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法: python compose_comic.py <spec.json>")
    with open(sys.argv[1], encoding="utf-8") as fh:
        spec = json.load(fh)

    font_path = spec.get("font", DEFAULT_FONT)
    crop_bottom = spec.get("crop_bottom", 100)
    margin = spec.get("margin", 40)
    gap = spec.get("gap", 30)
    title_h = spec.get("title_h", 210)
    cols = spec.get("cols", len(spec["panels"]))
    panels_spec = spec["panels"]
    rows = math.ceil(len(panels_spec) / cols)

    loaded = []
    for i, p in enumerate(panels_spec, 1):
        im = Image.open(p["image"]).convert("RGB")
        w, h = im.size
        im = im.crop((0, 0, w, h - crop_bottom))
        for patch in p.get("patches", []):
            im.paste(im.crop(tuple(patch["src"])), tuple(patch["dst"]))
        loaded.append(im)

    pw, ph = loaded[0].size
    canvas_w = margin * 2 + pw * cols + gap * (cols - 1)
    canvas_h = title_h + (ph + gap) * rows - gap + margin
    origins = [(margin + c * (pw + gap), title_h + r * (ph + gap))
               for r in range(rows) for c in range(cols)]

    paper = tuple(sum(im.crop((w - 300, 40, w - 100, 140)).resize((1, 1), Image.LANCZOS)
                       .getpixel((0, 0))[k] for im in loaded) // len(loaded) for k in range(3))
    canvas = Image.new("RGB", (canvas_w, canvas_h), paper)
    for im, org in zip(loaded, origins):
        canvas.paste(im, org)
    d = ImageDraw.Draw(canvas)

    f_title = pick_font(font_path, spec.get("title_size", 92))
    f_sub = pick_font(font_path, spec.get("subtitle_size", 36))

    title = spec.get("title", "")
    accent = spec.get("title_accent", "")
    ink = hex_to_rgb(spec.get("ink", "#2b2724"))
    red = hex_to_rgb(spec.get("accent", "#c63a34"))
    tx = margin + 6
    segs = [(title, ink)]
    if accent and accent in title:
        cut = title.index(accent)
        segs = [(title[:cut], ink), (accent, red), (title[cut + len(accent):], ink)]
    for text, col in segs:
        if text:
            d.text((tx, 50), text, font=f_title, fill=col, anchor="la")
            tx += d.textlength(text, font=f_title)
    if spec.get("subtitle"):
        d.text((margin + 10, 170), spec["subtitle"], font=f_sub,
               fill=hex_to_rgb(spec.get("subtitle_color", "#7a7164")), anchor="la")

    for idx, (p, (ox, oy)) in enumerate(zip(panels_spec, origins), 1):
        frame = p.get("frame")
        if frame is not False:
            fp = jitter_round_rect(ox, oy, ox + pw, oy + ph, 6, seed=ox + oy, jitter=2.2, seg=44)
            d.line(fp + [fp[0]], fill=hex_to_rgb(frame or "#4a433c"), width=3)
        b = p.get("bubble")
        if not b:
            continue

        sh = b.get("shape", "ellipse")
        ccx = ox + b["center"][0]
        ccy = oy + b["center"][1]
        rx, ry = b["rx"], b["ry"]
        outline = hex_to_rgb(b.get("outline", spec.get("ink", "#2b2724")))
        seed = b.get("seed", idx * 101)

        lines = b.get("lines", [])
        fonts = [pick_font(font_path, ln.get("size", 44)) for ln in lines]
        widths = [d.textlength(ln["text"], font=f) for ln, f in zip(lines, fonts)]
        block_w = max(widths) if widths else 0
        tops = [ln.get("dy", 0) - ln.get("size", 44) * 0.5 for ln in lines]
        bots = [ln.get("dy", 0) + ln.get("size", 44) * 0.5 for ln in lines]
        block_h = (max(bots) - min(tops)) if lines else 0

        oh = avail_height(sh, rx, ry, block_w)
        if block_w and oh < block_h:
            hint = (f"文字块宽 {block_w:.0f}px 已超过气泡宽度 {2 * rx:.0f}px，必须先加大 rx 或缩短文案"
                    if block_w >= 2 * rx else "请放宽 rx/ry、缩短文案或缩小字号")
            raise SystemExit(
                f"panel{idx}: 气泡装不下文案 —— 块宽 {block_w:.0f}px / 块高 {block_h:.0f}px，"
                f"该形状可用高仅 {oh:.0f}px；{hint}。")

        tip, b1, b2 = None, None, None
        if b.get("tail"):
            tip = (ox + b["tail"][0][0], oy + b["tail"][0][1])
            b1 = (ox + b["tail"][1][0], oy + b["tail"][1][1])
            b2 = (ox + b["tail"][2][0], oy + b["tail"][2][1])
            for k, base in enumerate((b1, b2), 1):
                if not tail_dot_in(rx, ry, sh, ccx, ccy, base[0], base[1]):
                    raise SystemExit(
                        f"panel{idx}: 尾巴基点{k} 的局部坐标 "
                        f"({b['tail'][k][0]}, {b['tail'][k][1]}) 落在气泡主体之外，"
                        "会露出三角形底边；请把它向气泡中心方向收。")
            d.polygon([tip, b1, b2], fill=(255, 255, 255))
            d.line([b1, tip], fill=outline, width=5, joint="curve")
            d.line([tip, b2], fill=outline, width=5, joint="curve")

        pts = shape_points(sh, ccx, ccy, rx, ry, seed)
        d.line(pts + [pts[0]], fill=(255, 255, 255), width=9, joint="curve")
        d.polygon(pts, fill=(255, 255, 255))
        d.line(pts + [pts[0]], fill=outline, width=5, joint="curve")

        for ln, font, w in zip(lines, fonts, widths):
            col = hex_to_rgb(ln.get("color", spec.get("ink", "#2b2724")))
            if ln.get("align", b.get("align", "center")) == "left":
                d.text((ccx - rx + 70, ccy + ln.get("dy", 0)), ln["text"],
                       font=font, fill=col, anchor="lm")
            else:
                d.text((ccx, ccy + ln.get("dy", 0)), ln["text"], font=font, fill=col, anchor="mm")
        print(f"panel{idx}: 块宽 {block_w:.0f}px 块高 {block_h:.0f}px 可用高 {oh:.0f}px")

    out_w = spec.get("out_width", 2400)
    if out_w and out_w != canvas_w:
        canvas = canvas.resize((out_w, round(canvas_h * out_w / canvas_w)), Image.LANCZOS)
    canvas.save(spec["output"])
    print("saved", spec["output"], canvas.size)


if __name__ == "__main__":
    main()
