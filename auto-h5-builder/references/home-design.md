# 首页：结构固定，视觉现场设计

首页不预置任何版式。技能只锁「结构契约」和「移动端底线」，观感由你在每次生成时，按这家店的主题去真实检索、提炼、实现。

固定一套皮，四家店长得一样，是这套范式最容易掉分的地方。所以这里没有 `templates/home/magazine.css` 这种东西——只有一份骨架和一份研究方法。

## 一、结构契约（不可改）

首页是一个 section，锚点齐全才能接到业务逻辑：

```html
<section class="view home" data-view="home" id="view-home" data-home="<设计名>">
  ...
  <h1>这家店的一句话主张</h1>                  <!-- 必须，首屏主张 -->
  <ul id="svcList"></ul>          <!-- 必须，JS 逐项填充 -->
  <div id="storeInfo"></div>      <!-- 必须，JS 填充营业时间/地址/电话（tel:） -->
  <button data-go="book">立即预约</button>   <!-- 必须，主 CTA -->
  <a href="#/share" data-go="share">分享</a> <!-- 建议，次入口 -->
</section>
```

- `#svcList` 必须是 `<ul>`（或 `<ol>`），JS 生成 `<li class="svc-item">`：`.svc-main > .svc-name / .svc-desc`，`.svc-meta > .svc-price / .svc-dur`。
- `#storeInfo` 里 JS 生成 `.info-row > .info-k / .info-v`，电话那一行是 `<a href="tel:…">`。
- 这两个容器里**不要写任何静态内容**，会被 JS 清空。
- 除了锚点，板块顺序、数量、图文组合、装饰、配色、字体、圆角、阴影、动效都由你定。
- `data-home` 写本次设计名（写在 `design-brief.json` 的 `design_name`，两边必须一致）。

内容来源只有 `spec`：店名、主张、服务、价目、时长、营业时间、地址、电话。不要编造评价、销量、资质、排名、合作品牌。

## 二、设计研究（生成前必做，不能凭记忆）

对主题先做判断，再决定去哪看。判断三件事：**行业**（面部护理 / 咖啡 / 健身 / 修车…）、**调性**（手艺感、效率、亲密、克制、热闹）、**价格带**（社区平价 / 中客单 / 高客单）。

然后**当场**用检索工具打开真实页面，三类来源各取所需：

| 来源类型 | 看什么 | 典型去处 |
|---|---|---|
| 开源社区 / 组件库 | 能落地的实现语法：网格、字号阶梯、卡片结构、CSS 技法 | Tailwind UI、shadcn/ui、Aceternity UI、Magic UI、DaisyUI、Uiverse、Flowbite、CSS-Tricks、CodePen |
| 主题站 / 灵感站 | 当代的构图与节奏：首屏构图、留白比例、图文关系 | Awwwards、Dribbble、Behance、Land-book、Lapa Ninja、Godly、Mobbin |
| 品牌官网 / 同业 | 这个品类的「可信长相」：信息顺序、措辞层级、图片风格 | 搜同行业真实门店/品牌官网，看 2–3 家 |

检索式模板（换成具体行业）：

- `beauty salon website design inspiration 2026`
- `coffee shop landing page awwwards`
- `spa booking site hero section design`
- `tailwind css hero section split layout`
- `neubrutalism / editorial / swiss grid landing page`（挑一个语汇深入看）
- `<行业> 门店 官网 首页`（中文同业，看信息顺序）

打开页面后**提炼语言，不搬代码**。要带走的是：首屏分几栏、标题与正文的字号比、色只用了几层、分隔靠线还是靠留白、装饰是几何图形还是纹理、动效是位移还是透明度。

不许写没打开过的链接进 brief。打不开就换一个，不猜 URL。

## 三、design-brief.json

研究结果落成文件，构建与验收都读它：

```jsonc
{
  "design_name": "linen-warm",              // 与页面 data-home 一致
  "design_family": "editorial-serif",       // 本次语汇，用于避免连续几家店撞风格
  "researched_at": "2026-11-13",            // 本次检索日期
  "theme_keywords": ["社区面部护理", "安静", "手艺感", "中客单"],
  "references": [
    { "url": "https://…", "site": "Awwwards", "source_type": "showcase",
      "borrow": "首屏左侧竖排小字标 + 右侧满幅色块，标题只占 6 字宽" },
    { "url": "https://…", "site": "Tailwind UI", "source_type": "open-source",
      "borrow": "价目用 dl + 虚线引导线右对齐数字" },
    { "url": "https://…", "site": "某同业品牌官网", "source_type": "brand",
      "borrow": "到访信息压成三行小字放在首屏底部，不单独开板块" }
  ],
  "tokens": {
    "palette": ["#b4735a", "#f6efe7", "#241d1a"],
    "type": { "display": "serif 34/1.24", "body": "sans 15/1.75" },
    "radius": "2px（按钮也直角）",
    "shape": "细横线 + 序号，无卡片阴影",
    "motion": "只做 opacity 120ms，不做位移动画"
  },
  "structure_idea": "首屏一句话 + 服务编号清单 + 到访三行压底，不做到访卡片",
  "originality": "只借鉴版式语法与信息顺序；未复制任何 CSS/HTML/图片/字体文件"
}
```

硬要求（闸门会查）：

- `references` ≥3 条，`source_type` 至少覆盖两类，其中必须有 `open-source` 或 `showcase`。
- 每条都要 `url`（真实打开过）+ `borrow`（具体到「哪一处、借什么」，不能写「参考了风格」）。
- 域名至少两个不同的站，不能三条都指向同一站。
- `design_name` 与页面 `data-home` 一致；`researched_at` 是本次生成日期。
- `originality` 写清没抄什么。

## 四、从 brief 到 CSS

1. **令牌先行**：先用 `--brand`（来自 spec）派生强调层级，再定中性色阶（底/卡/线/正文/次要/弱）。全页颜色不超过 4 个家族。
2. **字号阶梯**：移动端首屏标题 26–40px，正文 14–16px，辅助 11–13px。层级差靠字号 + 字重 + 颜色，不靠五种颜色。
3. **间距节奏**：一套 4 的倍数间距（8/12/16/24/32/48），板块之间只用两档值，别每块各写一个数。
4. **图形语汇挑一种并贯彻**：全细线 / 全直角 / 全圆角 / 单侧粗边 / 网点纹理。混用就是没有语汇。
5. **动效克制**：只做 `opacity` 或 `transform` ≤160ms 的微反馈，且必须在 `@media (prefers-reduced-motion: reduce)` 下关掉。
6. **字体只用系统栈**：不能引外部字体文件（页面要离线可开、微信内秒开）。语气差异靠 `serif` / `sans` / `ui-monospace` 三档 + 字重 + 字距 + `text-transform` 做出来。
7. **装饰自己画**：CSS 渐变、`border`、`conic-gradient`、内联 SVG、`data:` 背景。不引外链图片，不用 emoji 当图标。

## 五、移动端与可读性底线

- 390 × 844 下首屏（含顶栏）必须看到「立即预约」，按钮高度 ≥44px、宽 ≥屏宽 55%。
- 不出横向滚动条；长店名、长服务名、长地址都要能换行不溢出（`min-width:0`、`word-break:auto-phrase`）。
- 正文与背景对比度 ≥4.5:1，大字 ≥3:1。浅色品牌（如 `#f5c542`）上不要压白字。
- 触控目标 ≥44×44，相邻目标间距 ≥8px。
- 页面顶部与底部留 `env(safe-area-inset-*)`，不贴边。

## 六、反模式

- ❌ 复刻本技能早期的四套版式（magazine / poster / split / quiet）——已废弃，别当模板翻出来用。
- ❌ 通用 SaaS 风：紫色渐变 + 玻璃卡片 + 三个圆角图标 + "Trusted by" 一排灰 logo。门店不需要。
- ❌ 满屏 emoji 当图标、当分隔符。
- ❌ 用外链图片撑首屏（离线打不开、微信里加载慢、还可能是别人版权图）。
- ❌ 把服务做成需要横向滚动的卡片轮播——顾客要一眼看到价目。
- ❌ 为了"设计感"把「立即预约」推到第二屏。
- ❌ 同一批生成的多家店共用一套 CSS，只换品牌色。

## 七、连续生成时不许撞风格

一次会话里做第二家店，`design_family` 必须和上一家不同（例如上一家 `editorial-serif`，这家换 `swiss-grid` / `poster-type` / `soft-organic` / `utility-label`）。同一家店复跑可以沿用同一份 brief。

## 八、自检

生成后先自己看一遍截图，再跑闸门。闸门查得到结构、来源、尺寸，查不到「好不好看」——这件事只能你自己负责：

- 遮住店名，这页还像不像"随便哪个模板"？像就重做首屏。
- 首屏有没有一句具体的话（这家店独有的），而不是「专业 · 贴心 · 值得信赖」？
- 关掉图片和动画，信息还完整吗？
