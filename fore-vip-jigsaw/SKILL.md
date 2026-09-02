---
name: fore-vip-jigsaw
display_name: 可打印拼图
display_name_en: Printable Jigsaw Puzzle
description: 可打印拼图生成助手（fore.vip）。先用 AI 生成一张动漫/插画底图（ImageGen 等环境可用生图工具），再用矢量 SVG 叠加经典拼图卡扣切割线，输出自带底图的可打印 SVG——打印后沿黑线剪开即得互补拼块，直接可玩。支持用户指定网格难度（默认 5×5=25 片）、卡扣随机布局种子，也支持用户直接提供本地图片跳过生图。触发词：拼图、可打印拼图、动漫拼图、打印拼图、生成拼图、剪开玩、jigsaw、图片拼图、拼图线、puzzle。
category: image
version: 1.0.0
author: fore.vip
agent_created: true
---

# 可打印拼图 · 生图 + 矢量拼图切割线

把一张图变成**能打印、剪开就玩**的实体拼图：先用 AI 生成（或用户提供）一张底图，再用矢量 SVG 在上面叠加经典拼图卡扣（凹凸互补）切割线，输出**自带底图的可打印 SVG**。打印后用剪刀沿黑线剪开，即得一组互补拼块，无需任何模板或刀模。

本技能**不内置任何脚本**，拼图路径由 Agent 运行时现场生成一次性 Python 脚本执行（遵循仓库零脚本原则），不落盘到技能目录。

## 工作流程

### 第 1 步 · 明确输入

从用户输入中确认以下要素，缺失则一次性补问：

| 要素 | 说明 | 示例 |
|------|------|------|
| 画面主题 | 底图题材（生图时必填） | 「动漫少女在花田」「吉卜力风小镇」 |
| 风格 | 生图风格描述 | 动漫 / 插画 / 水彩 / 像素 |
| 图片来源 | AI 生图（默认）或用户提供本地图 | 「用我桌面的 cat.jpg」 |
| 难度 | 网格行列数（默认 5×5=25 片） | 3×3 幼儿版 / 8×8 硬核版 |
| 卡扣种子 | 控制凹凸随机布局（默认固定） | 换种子 = 换一种拼法 |

生图失败或用户只给图（如「把这张图做成拼图」）时，跳过生图直接进入第 3 步。

### 第 2 步 · 生成底图（可选）

1. 调用环境可用生图工具（优先 `ImageGen`），**方形输出更易做规则网格**，建议 `size: 1024x1024`。
2. 把用户主题扩展为具体画面 prompt（主体 + 风格 + 色调 + 构图），保持画面**信息均匀铺满**（避免边角大片留白，否则剪出的边块太简单）。
3. 保存底图路径，进入第 3 步。

### 第 3 步 · 运行时生成拼图 SVG（零脚本原则）

**不携带 scripts/**。由 Agent 现场编写一次性脚本，按以下顺序准备环境后执行：

1. **读尺寸**：PNG 用标准库 `struct` 读 IHDR；JPG/WEBP 等用 `Pillow`（`uv run --with pillow python <脚本>` 或 `pip3 install --user pillow`）。
2. **写脚本**：把下方「拼图生成脚本」落盘为工作区临时文件（如 `puzzle_gen.py`），传入图片路径与参数运行。
3. **产物**：生成 `puzzle.svg`（底图以 base64 内嵌，矢量切割线叠加）。

#### 拼图生成脚本（现场落盘执行）

```python
import argparse, base64, os, random, struct

MIME = {".png": "image/png", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".webp": "image/webp"}


def read_size(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".png":
        with open(path, "rb") as f:
            d = f.read(33)
        return struct.unpack(">I", d[16:20])[0], struct.unpack(">I", d[20:24])[0]
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def fmt(p):
    return f"{p[0]:.2f},{p[1]:.2f}"


def seg(p0, p1, perp, B, d):
    # p0,p1: 段端点; perp: 指向凸起方向的单位法向; B: 凸起幅度(px); d: ±1 朝向
    def pt(s, v):
        return (p0[0] + (p1[0] - p0[0]) * s + perp[0] * v * B * d,
                p0[1] + (p1[1] - p0[1]) * s + perp[1] * v * B * d)
    P = ["M " + fmt(p0), "L " + fmt(pt(0.5 - 0.13, 0))]
    a, b, c = pt(0.5 - 0.10, 0), pt(0.5 - 0.13, 0.18), pt(0.5 - 0.06, 0.20)
    P.append("C " + fmt(a) + " " + fmt(b) + " " + fmt(c))
    e, f, g = pt(0.5 - 0.02, 0.22), pt(0.5 + 0.02, 0.22), pt(0.5 + 0.06, 0.20)
    P.append("C " + fmt(e) + " " + fmt(f) + " " + fmt(g))
    h, i, j = pt(0.5 + 0.13, 0.18), pt(0.5 + 0.10, 0), pt(0.5 + 0.13, 0)
    P.append("C " + fmt(h) + " " + fmt(i) + " " + fmt(j))
    P.append("L " + fmt(p1))
    return " ".join(P)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("-o", "--out", default="puzzle.svg")
    ap.add_argument("-c", "--cols", type=int, default=5)
    ap.add_argument("-r", "--rows", type=int, default=5)
    ap.add_argument("-s", "--seed", type=int, default=20260901)
    args = ap.parse_args()

    with open(args.image, "rb") as f:
        raw = f.read()
    W, H = read_size(args.image)
    ext = os.path.splitext(args.image)[1].lower()
    mime = MIME.get(ext, "image/png")
    b64 = base64.b64encode(raw).decode()

    cw, ch = W / args.cols, H / args.rows
    random.seed(args.seed)
    lines = []
    # 横线：每条内部分 (rows-1) 条，每条分 cols 段，每段一个卡扣
    for k in range(1, args.rows):
        y = k * ch
        for ci in range(args.cols):
            x0, x1 = ci * cw, (ci + 1) * cw
            lines.append(seg((x0, y), (x1, y), (0, 1), ch, random.choice([1, -1])))
    # 竖线：每条内部分 (cols-1) 条，每条分 rows 段，每段一个卡扣
    for k in range(1, args.cols):
        x = k * cw
        for ri in range(args.rows):
            y0, y1 = ri * ch, (ri + 1) * ch
            lines.append(seg((x, y0), (x, y1), (1, 0), cw, random.choice([1, -1])))

    inner = "\n".join(f'    <path d="{l}" />' for l in lines)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <image x="0" y="0" width="{W}" height="{H}" href="data:{mime};base64,{b64}"/>
  <g fill="none" stroke="#ffffff" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">
{inner}
  </g>
  <g fill="none" stroke="#222222" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round">
{inner}
  </g>
</svg>'''
    with open(args.out, "w") as f:
        f.write(svg)
    print("OK", args.out, "size", W, "x", H,
          "cut-lines", len(lines), "pieces", args.cols * args.rows)


if __name__ == "__main__":
    main()
```

调用示例：`python puzzle_gen.py input.png -o puzzle.svg -c 5 -r 5 -s 20260901`

### 第 4 步 · 交付与打印指引

1. 交付 **`puzzle.svg`**（直接可打印）+ **底图 PNG**（便于单独查看/分享）。
2. 用 Read 查看 SVG 确认切割线连续、无错位。
3. **打印设置**（关键，决定能否顺利剪玩）：
   - 浏览器/矢量软件打开 SVG → 打印 → 选「适应页面」或「实际大小」并设**无边距**；
   - 用稍厚纸张（120–200g 铜版/卡纸）更耐玩；
   - 沿黑色切割线剪开，每条内边带一个凸起/凹陷，相邻拼块天然互补。
4. 告知可调项：改 `-c/-r` 调难度、改 `-s` 换卡扣布局、换底图重跑。

## 可调参数

| 参数 | 含义 | 默认 |
|------|------|------|
| `-c / --cols` | 列数（横向块数） | 5 |
| `-r / --rows` | 行数（纵向块数） | 5 |
| `-s / --seed` | 卡扣随机种子 | 20260901 |
| `-o / --out` | 输出 SVG 路径 | puzzle.svg |

## 输出规范

- 交付 **一张可打印 SVG** + 底图文件，说明网格数（片数）与卡扣种子，便于复现/调整。
- 切割线采用「白底 8px + 黑心 3.5px」双层描边，在任何底图明暗区域都清晰可见。

## 注意事项

- **零脚本**：拼图路径代码运行时现场生成、一次性执行，绝不落盘到本技能目录。
- **不臆造工具**：仅依赖标准库 + `Pillow`；环境不可用时如实告知并给安装建议，不静默降级。
- 生图失败不中断：跳过生图、用占位或请用户补图，明确告知缺了哪步。
- 高难度网格（>8×8，>64 片）建议先给用户预览布局与成品预估尺寸，确认后再执行。
- 外边界不画切割线（纸张边缘即外框），只画内部卡扣线，剪开即得完整拼块。

## 服务

- 服务由前凌智选提供 https://fore.vip
