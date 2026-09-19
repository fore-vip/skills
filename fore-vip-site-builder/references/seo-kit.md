# SEO 辅料清单与生成规范

> 目标：让搜索引擎**能抓、能懂、能索引**。不涉及排名技巧，只保证基础件齐全且正确。

## 目录

- [1. 每页必备（head）](#1-每页必备head)
- [2. 全站必备（根目录）](#2-全站必备根目录)
- [3. 语义与内容结构](#3-语义与内容结构)
- [4. 结构化数据（JSON-LD）](#4-结构化数据json-ld)
- [5. 性能与可达性](#5-性能与可达性)
- [6. 自检清单](#6-自检清单)

---

## 1. 每页必备（head）

按此顺序写，顺序不影响解析但影响可读性与维护。

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>主关键词 · 品牌名</title>
  <meta name="description" content="一句话说清这里提供什么、给谁、有什么不同。">
  <link rel="canonical" href="https://example.com/this-page">
  <meta name="robots" content="index,follow,max-image-preview:large">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="品牌名">
  <meta property="og:title" content="主关键词 · 品牌名">
  <meta property="og:description" content="同一句话，可与 description 一致。">
  <meta property="og:url" content="https://example.com/this-page">
  <meta property="og:image" content="https://example.com/og-cover.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="zh_CN">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
</head>
```

### 取值口径

| 项 | 规范 | 说明 |
|----|------|------|
| `lang` | `zh-CN` / `en` | 只写主语言；中文站不需要 `hreflang` |
| `<title>` | **≤ 30 个汉字**（约 60 字符） | 格式：`主关键词 · 品牌名`；**每页不同** |
| `description` | **70–150 个汉字** | 自然句子，含核心词，**不要堆关键词**；每页不同 |
| `canonical` | **绝对 URL，每页指向自身** | 重复内容页（带 `?` 参数的）指向规范页；www 与裸域二选一为规范域 |
| `og:image` | **1200×630 PNG/JPG**，绝对 URL | 图内文字占画面 ≤ 1/3，缩略图上要能认出来 |
| `robots` | 默认 `index,follow` | 仅供内部/未完成页用 `noindex`；**别用 `robots.txt` 来屏蔽页面**（那是禁止抓取，不是禁止索引） |

---

## 2. 全站必备（根目录）

### 2.1 `robots.txt`

```
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

- 必须**公网可访问**（`200`），不能因对象权限返回 `403`。
- `Sitemap:` 用**绝对 URL**；多份 sitemap 就写多行。
- 不要写 `Disallow: /` —— 那是全站禁止抓取。

### 2.2 `sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-09-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/features</loc>
    <lastmod>2026-09-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

硬规则：

- **只收录能公开访问、且 `robots` 允许索引的页面**。已删除页、`noindex` 页、测试页一律不写。
- `<loc>` 必须是**绝对 URL**，且与 `canonical` 一致。
- `<lastmod>` 用 `YYYY-MM-DD` 或完整 ISO 8601；**内容实际改动才更新**，不能每次发布都刷成今天。
- 单个 sitemap 上限 **50,000 条 URL / 50 MB（未压缩）**，超出拆分并写 sitemap index。
- **sitemap 必须与实际页面同步** —— 这是发布闸门：新增页面要补、改动页面刷 `lastmod`、删除页面要去掉。不同步就中止发布。

> `init_site.py` 会生成 `sync_sitemap.py` 并在 `deploy.sh` 里做 fail-closed 检查。

### 2.3 图标

| 文件 | 规格 | 用途 |
|------|------|------|
| `favicon.ico` | 32×32（含 16×16） | 浏览器标签页 |
| `apple-touch-icon.png` | 180×180 | iOS 添加到主屏 |

---

## 3. 语义与内容结构

- **一个页面只有一个 `<h1>`**，内容 = 页面主题，不是品牌名堆叠。
- 标题层级**不跳号**：`h1 → h2 → h3`，不要 `h1` 直接跳 `h3`。
- 用语义标签：`<header>` `<nav>` `<main>` `<article>` `<section>` `<footer>`。整站套一层 `<div>` 是常见降级。
- 每个 `<img>` 都要 `alt`：有信息含义的写清内容，纯装饰的写 `alt=""`（空值不算缺失）。
- 链接锚文本要有意义 —— 「点击这里」等于没写。
- 正文可读性：段落 ≤ 4 行，关键数字/结论**加粗**，多用小标题分段。
- 面向普通访客的可见文案**不出现技术黑话与内部路径**；技术信息只进 `<head>` 的 meta 与 JSON-LD。

---

## 4. 结构化数据（JSON-LD）

放在 `<head>` 内 `<script type="application/ld+json">`，**每页只放与该页最相关的一类**，多类共存用 `@graph`。

### 4.1 组织 / 站点（主页）

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "品牌名",
  "url": "https://example.com/",
  "logo": "https://example.com/logo.png",
  "description": "一句话业务描述",
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer service",
    "email": "hello@example.com"
  }
}
```

### 4.2 产品 / 服务页

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名",
  "description": "产品一句话说明",
  "brand": { "@type": "Brand", "name": "品牌名" },
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CNY",
    "price": "128",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/product"
  }
}
```

> `price` 必须与实际一致。**不要为了展示富摘要写不实价格或虚假评分** —— 会被人工处罚。

### 4.3 常见问题页

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题原文？",
      "acceptedAnswer": { "@type": "Answer", "text": "答案原文。" }
    }
  ]
}
```

硬规则：

- JSON-LD 内容必须**与页面可见内容一致**，不能只存在于结构化数据里（隐藏内容换富摘要属违规）。
- `@type` 按站点性质选：企业站 `Organization`、产品页 `Product`、问答区 `FAQPage`、文章页 `Article`、面包屑 `BreadcrumbList`。
- 写完用 `seo_audit.py` 验证 JSON 可解析，再用 Google Rich Results Test 或 Schema Markup Validator 复验。

---

## 5. 性能与可达性

| 项 | 做法 | 为什么 |
|----|------|--------|
| 字体 | **自托管**（`woff2` + `font-display: swap`） | 引 Google Fonts 在大陆可能整站卡住 |
| 第三方脚本 | 尽量不用；必须用时自托管或选国内可达的 CDN | 境外分析/统计脚本会拖慢甚至阻断渲染 |
| 图片 | 指定 `width`/`height`、`loading="lazy"`（首屏图除外）、`decoding="async"` | 防布局抖动（CLS），提升 LCP |
| CSS | 保持在 1–2 个文件内，关键样式内联或提前加载 | 减少请求链 |
| JS | 非必要不用；用时加 `defer` | 静态官网通常可以零 JS |
| 响应式 | 移动优先，断点 ≥ 3 档（如 480 / 768 / 1024） | 百度以移动端为主要评估口径 |
| 可访问性 | 对比度 ≥ 4.5:1、焦点可见、可键盘操作 | 兼顾无障碍与基础体验分 |

> 若站点在国内且图片多，接 CDN + 图片处理（如七牛 `imageView2`、阿里云 OSS 图片处理）比直接传原图更划算。

---

## 6. 自检清单

```bash
$PYTHON scripts/seo_audit.py <站点目录> --base-url https://example.com --strict
```

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | `title` | 存在、非空、≤ 60 字符（含【待填】时降级为 WARN） |
| 2 | `description` | 存在、30–300 字符（同上） |
| 3 | `lang` | 已声明 |
| 4 | `viewport` | 含 `width=device-width` |
| 5 | `canonical` | 存在且为绝对 URL |
| 6 | `og:*` | `og:title` / `og:description` / `og:image` / `og:url` 齐全 |
| 7 | `twitter:card` | 存在 |
| 8 | JSON-LD | 存在且可解析 |
| 9 | `h1` | **恰好 1 个** |
| 10 | 标题层级 | 不跳号 |
| 11 | `img alt` | 无缺失（`alt=""` 合规） |
| 12 | 占位符 | 正文无 `{{...}}` / `TODO` / `FIXME` |
| 13 | 草稿标记 | 无 `【待填：…】`（非 strict 仅告警） |
| 14 | 备案 | `--require-icp` 时页脚含 ICP 备案号 |
| 15 | `robots.txt` | 存在且含 `Sitemap:` |
| 16 | `sitemap.xml` | 存在、`<loc>` 全为绝对 URL、与实际页面**双向**一致 |
| 17 | 跨页唯一性 | 各页 `title` 互不相同 |

**退出码 0 = 可发布；1 = 有硬伤，闸门拦截。**
