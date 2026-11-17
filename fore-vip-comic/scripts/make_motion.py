#!/usr/bin/env python3
"""四格漫画 → 动画 GIF（零 credits 路径）。

用法:
    python make_motion.py <spec.json|composite.png> [out.gif]

- 传入合成器的 spec.json：按 spec 的网格几何精确裁出每一格。
- 传入成品 PNG：按 2×2 均分裁格（适用于无标题区的图）。
效果：封面微推 → 逐格 Ken Burns → 格间交叉淡化。只依赖 Pillow。
"""

import json
import math
import sys
from PIL import Image

COVER_FRAMES, PANEL_FRAMES, FADE_FRAMES = 8, 12, 4
MS, MAX_W, ZOOM = 110, 900, 1.07


def grid_boxes(spec, w, h):
    margin, gap, title_h = spec.get("margin", 40), spec.get("gap", 30), spec.get("title_h", 210)
    n = len(spec.get("panels", [])) or 4
    cols = spec.get("cols", n)
    rows = math.ceil(n / cols)
    pw = (w - 2 * margin - gap * (cols - 1)) / cols
    ph = (h - title_h - margin - gap * (rows - 1)) / rows
    origins = [(margin + c * (pw + gap), title_h + r * (ph + gap))
               for r in range(rows) for c in range(cols)]
    return [(round(x), round(y), round(x + pw), round(y + ph)) for x, y in origins[:n]]


def ken_burns(img, frames, zoom):
    w, h = img.size
    out = []
    for i in range(frames):
        t = i / max(1, frames - 1)
        z = 1 + (zoom - 1) * t
        nw, nh = max(1, int(w / z)), max(1, int(h / z))
        dx = int((w - nw) * 0.5 * t)
        dy = int((h - nh) * 0.5 * (1 - t))
        out.append(img.crop((dx, dy, dx + nw, dy + nh)).resize((w, h), Image.Resampling.LANCZOS))
    return out


def crossfade(a, b, n):
    if b.size != a.size:
        b = b.resize(a.size, Image.Resampling.LANCZOS)
    return [Image.blend(a, b, (i + 1) / (n + 1)) for i in range(n)]


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法: python make_motion.py <spec.json|composite.png> [out.gif]")
    src = sys.argv[1]
    spec = {}
    if src.lower().endswith(".json"):
        with open(src, encoding="utf-8") as fh:
            spec = json.load(fh)
        image_path = spec.get("output")
    else:
        image_path = src
    if not image_path:
        raise SystemExit("spec 缺少 output（成品 PNG 路径）")

    im = Image.open(image_path).convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.Resampling.LANCZOS)
    scale = im.width / Image.open(image_path).width
    boxes = ([(round(x * scale), round(y * scale), round(x2 * scale), round(y2 * scale))
              for x, y, x2, y2 in grid_boxes(spec, round(im.width / scale), round(im.height / scale))]
             if spec else [(round(c * im.width / 2), round(r * im.height / 2),
                            round((c + 1) * im.width / 2), round((r + 1) * im.height / 2))
                           for r in range(2) for c in range(2)])

    frames, durations = [], []
    for f in ken_burns(im, COVER_FRAMES, 1.02):
        frames.append(f); durations.append(MS)
    panels = [im.crop(b) for b in boxes]
    for i, p in enumerate(panels):
        seq = ken_burns(p, PANEL_FRAMES, ZOOM)
        for f in seq:
            frames.append(f); durations.append(MS)
        if i + 1 < len(panels):
            for f in crossfade(seq[-1], panels[i + 1], FADE_FRAMES):
                frames.append(f); durations.append(MS // 2)

    out = sys.argv[2] if len(sys.argv) > 2 else (image_path.rsplit(".", 1)[0] + "-motion.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], durations=durations,
                   loop=0, optimize=True, disposal=2)
    print("saved", out, "frames:", len(frames), "seconds:", round(sum(durations) / 1000, 1))


if __name__ == "__main__":
    main()
