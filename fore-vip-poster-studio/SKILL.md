---
name: poster-studio
description: 当用户要生成可实际发布的海报/服务图/封面（闲鱼、公众号、小红书等），且需要导出 PNG 时触发。先按极简排版设计哲学（Algorithmic Poster Philosophy）构建系统，**绘制前先确认是否加二维码（目标 URL）**，再用 show_widget 渲染内联 SVG 预览，并通过 scripts/render_poster.py（支持 --qr 落位二维码）生成高分 PNG（白底/黑字/单色强调，CJK 字体跨平台自适应）。适用于闲鱼服务海报、极简活动海报、作品集封面、品牌视觉图等"系统美学 + 可下载成品"的场景。
description_zh: 极简排版海报生成器。为可实际发布的海报、服务图与封面（闲鱼、公众号、小红书等）构建设计系统，绘制前先确认是否加入二维码及目标 URL，用 show_widget 渲染内联 SVG 预览，并导出高清 PNG（白底 / 黑字 / 单色强调，可选二维码，CJK 字体跨平台自适应）。适用于闲鱼服务海报、极简活动海报、作品集封面与品牌视觉图等「系统美学 + 可下载成品」场景。
description_en: "A minimalist, typography-driven poster generator. Builds a design system for publish-ready posters, service images and covers (Xianyu, WeChat, Xiaohongshu), asks upfront whether to include a QR code and its target URL, renders an inline SVG preview via show_widget, and exports a high-resolution PNG (white background, black type, single accent color, optional QR block, cross-platform CJK font handling). Built for systematic aesthetics plus a downloadable deliverable: service posters, minimal event posters, portfolio covers, brand visuals."
category: design
version: 1.0.1
author: fore.vip
---

# Poster Studio

极简、排版驱动的海报生成器。把"做一张海报"升级为"先定义设计系统，再产出可下载成品"。

本技能在 `algorithmic-poster-philosophy` 的设计哲学之上，补齐了**交付闭环**：除内联 SVG 预览外，额外产出高清 PNG（默认 2×，1200×1600 @ 3:4），可直接发布到闲鱼/小红书/公众号等平台；底部强调块可落位一枚二维码，用于扫码引流。

## 适用范围

- 平台服务图：闲鱼服务、微信小商店、小红书种草
- 极简活动/招募海报、作品集封面、品牌视觉图
- 任何需要"系统美学 + 可下载 PNG"的视觉产出

不适用：需要复杂插画、照片合成、品牌 IP 形象的重度设计（应改用语义化设计工具或 ImageGen）。

## 工作流

### STEP 1 — 收集 brief

绘制前一次性问清（缺省时给合理默认，不要反复追问）：

- **二维码（绘制前必问的一项）**：先问一句「要不要加二维码？加的话把目标 URL 发我」。默认建议加——线下物料、私域引流、扫码留资都靠它；用户明确说不要则跳过，按纯文字版出图。URL 必须指向合规落地页，占位/未上线链接不要用
- 平台 / 用途（决定比例与强调色，如闲鱼用 #ffe600）
- 主标题（title）
- 能力标签（tags，渲染为副标题，用 " / " 连接）
- CTA 文案（cta，1–2 行，落在底部强调块；**加二维码时每行 ≤ 8 个汉字**，否则会压到二维码）
- 顶部标识 meta / 品牌 brand（可选）
- 比例（默认 3:4；公众号封面可 1:1，竖版故事可 9:16）

### STEP 2 — 写设计哲学（内联 markdown）

遵循 5 段结构，每条规则必须可转化为参数，禁止空话：
1. **Concept** 核心概念（抽象但可操作）
2. **Visual Logic** 栅格 / 密度 / 留白策略
3. **System Behavior** 层级、对齐、节奏
4. **Parametric Thinking** 字号比、边距比、颜色数（≤2）、元素数（≤5）
5. **Emergence** 最终观感与情绪

### STEP 3 — 渲染成品

调用脚本生成 PNG（与可选 SVG 预览文件）：

```bash
python3 scripts/render_poster.py \
  --title "定制软件开发" \
  --tags 小程序 网站 后台 自动化脚本 \
  --cta "按需报价 · 源码交付 · 售后支持" "私聊获取专属方案 →" \
  --meta "闲鱼 · 软件开发服务" --brand "fore.vip" \
  --accent "#ffe600" --ratio 3:4 --scale 2 --out <输出目录> --name poster --svg \
  --qr "https://auto.fore.vip/index.html"
```

参数说明：`--scale` 控制清晰度（默认 2）；`--ratio` 支持 `3:4`/`1:1`/`9:16`；`--accent/--ink/--sub/--bg` 调色；`--svg` 同时写出预览 SVG；`--qr <URL>` 在底部强调块右侧落位二维码，省略则整行去掉、出纯文字版。

### STEP 4 — 内联预览 + 交付

- `show_widget` 渲染脚本产出的 SVG（viewBox 宽度需为 680，脚本按 `--ratio` 同步长宽）做内联预览。
- `present_files` 交付 PNG 成品。

## 设计系统（硬规则）

- **信息策略**：只留必要文字，最多 3 个信息块（主标题 / 副标题 / 元信息）
- **布局**：严格对齐或仅 1 次刻意偏离；强竖向阅读流；大量留白
- **字体**：标题大 / 副文中小 / 元信息小；1–2 种字体
- **颜色**：黑白灰或低饱和；除黑白外最多 2 色，且颜色服务层级而非装饰
- **元素**：画布上活跃元素 ≤ 5；无装饰图标/插画；允许仅强化结构的细线/几何块
- **二维码（可选，最多 1 枚）**：贴底部强调块右侧与 CTA 共区；白底方框 + 4 模块静区（不可省，省了扫不出）；模块边长取整数像素，保证缩放到任意尺寸都不糊；单色 ink 绘制，不叠品牌色；启用后 CTA 文案只占左侧可用宽度，脚本会按宽度自动缩字号兜底

## 工具与依赖

- 渲染依赖 **Python3 + Pillow**（`pip install Pillow`）。脚本自动探测 macOS / Windows / Linux 的 CJK 字体（PingFang / 微软雅黑 / Noto Sans CJK / 文泉驿），不依赖安装路径。
- 二维码为**可选能力**，需 `segno`（纯 Python，首选，`pip install segno`）或 `qrcode` 之一。两者都缺时脚本**不报错退出**：跳过二维码、其余照常输出，并在 stderr 提示安装命令。二维码在 PNG 与 SVG 中同步绘制，预览即成品。
- **跨平台提示**：WorkBuddy 跨平台客户端（iOS/Android/PC）若无本地 Python，则退化为「仅 show_widget 展示 SVG」，由用户在客户端导出/截图；SKILL 不假定运行时存在 python。

## 合规提醒（发布前）

- 服务类图片避免极限词（"最/第一/保证收益"），遵守平台规则与广告法
- 不要在首图画手机号/微信，用平台私信引导，降低导流判定风险
- 图内二维码存在平台风险：小红书 / 闲鱼对图内二维码识别严格，可能限流或折叠展示；发布前先确认目标平台当期规则，必要时退化为纯文字引导（线下物料、样张、名片场景不受此限）
- 二维码指向的落地页同样受广告法约束，不要用二维码把极限词绕到站外

## 触发词示例

"做张海报""生成海报""帮我出张服务图""闲鱼发图""转成 PNG 的海报""封面图""海报上加个二维码""海报放扫码"
