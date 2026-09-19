---
name: fore-vip-site-builder
slug: site-builder
displayName: SiteBuilder
display_name: 官网自动建站
display_name_en: fore.vip Website Auto-Launch
description: "官网自动建站向导（fore.vip）。从「要不要备案」一路做到「搜索引擎能搜到」，主链路八步：托管与备案分流（中国内地 OSS 需 ICP 备案 / 中国香港 OSS 免备案 / Vercel 免备案但有大陆可达性风险）→ 环境与凭证就绪 → 高档风格选型与脚手架生成 → 域名购买·解析·HTTPS 证书 → 主页与业务功能页落地 → 部署挂靠与增量发布脚本 → SEO 辅料全套生成（title / description / canonical / OG / JSON-LD / robots.txt / sitemap.xml / 语义标签）→ 各大站长平台提交与站点认证（百度·必应·Google·360·神马·搜狗·头条）。已有官网时走优化支线：识别技术栈 → SEO 与文案体检 → 给「保留 / 优化 / 重建」建议。当用户说「帮我建官网 / 我要做个网站 / 公司官网怎么做 / 网站怎么上线 / 域名怎么绑定 / 网站要不要备案 / 不备案行不行 / 免费 SSL 证书怎么配 / 怎么让百度收录 / 提交 sitemap / 站长平台怎么认证 / 官网怎么优化」时使用。"
description_zh: "官网自动建站向导。主链路：托管与备案分流（内地 OSS 备案 / 香港 OSS 免备案 / Vercel 免备案但有可达性风险）→ 环境就绪 → 风格选型与脚手架 → 域名解析与 HTTPS → 主页与业务页 → 部署挂靠与自动发布 → SEO 辅料全套生成 → 站长平台提交与站点认证。已有官网走优化支线（技术栈识别 → 体检 → 保留/优化/重建建议）。"
description_en: "Website auto-launch guide. Main pipeline: hosting and ICP-filing decision (mainland-China OSS requires ICP filing / Hong Kong OSS is filing-free / Vercel is filing-free but has mainland accessibility risks) → environment and credentials → premium style selection and scaffolding → domain resolution and HTTPS → homepage and product pages → deployment wiring with incremental publish script → full SEO kit generation (title, description, canonical, Open Graph, JSON-LD, robots.txt, sitemap.xml, semantic markup) → submission and site verification across webmaster platforms (Baidu, Bing, Google, 360, Shenma, Sogou, Toutiao). If a site already exists, switch to the optimization branch: stack detection, audit, and a keep/improve/rebuild recommendation."
category: web
version: 1.0.0
author: fore.vip
owner: team
agent_created: true
triggers:
  - "建官网"
  - "做个网站"
  - "官网怎么做"
  - "网站上线"
  - "网站不备案"
  - "ICP备案"
  - "域名解析"
  - "免费SSL证书"
  - "怎么让百度收录"
  - "提交sitemap"
  - "站长平台"
  - "网站SEO"
  - "OSS静态网站托管"
  - "Vercel部署"
negative_triggers:
  - "小程序 / App 开发（非官网）"
  - "已有站点的纯内容改写（走内容类技能）"
  - "电商店铺装修（淘宝/闲鱼/小红书店铺页）"
  - "服务器运维排障（非建站链路）"
compatibility:
  - WorkBuddy
  - Marvis
  - MCP-client
---

# 官网自动建站 · Website Auto-Launch

把官网从「要不要备案」一路推到「搜索引擎能搜到」。**每一步先决策、再动手；不能落地的能力如实标注，不承诺收录与排名。**

## 总流程

```
第 0 步  入门判定（弹窗三问）
   │
   ├─ 已有官网 ──→ 分支 A · 优化线（A1 识别栈 → A2 体检 → A3 三选一建议）──┐
   │                                                                      │
   └─ 无官网 ────→ 分支 B · 主链路（B1→B8）──────────────────────────────┤
                                                                          │
                          B6 部署挂靠 · B7 SEO 辅料 · B8 站长平台提交 ←──┘
```

## 第 0 步 · 入门判定（必做，先别动手）

用宿主的用户选择工具（WorkBuddy 为 `AskUserQuestion`，单次最多 4 项）弹窗三问；宿主无弹窗工具时降级为文字列表让用户回序号。

1. **现在有官网吗？** — 有 / 没有 / 有一个但不满意
2. **主要访客在哪？** — 中国大陆 / 海外为主 / 两边都要
3. **站点性质？** — 企业展示 / 产品官网 / 个人或作品集 / 文档站

> 第 2 问是后面所有技术决策的总开关：**只影响大陆访问就必须备案或接受降级**。

## 分支 A · 已有官网（优化线）

### A1 技术栈识别

问清三件事，不要猜：**托管在哪**（OSS / Vercel / 服务器 / 建站 SaaS）、**怎么发布**（手动上传 / git push / CI）、**源码在哪**（本地目录 / 无源码）。

- 判断得出栈 → 直接进 A2。
- 完全无源码、只有页面（SaaS 建站）→ 记为「只做 B7+B8 能做的部分」，其余步骤跳过并说明原因。

### A2 体检

```bash
PY=python3   # 有托管运行时用托管路径；此处 python3 即可
$PY scripts/seo_audit.py <站点目录或 index.html> --base-url https://<域名>
```

同时做一次**文案合规预检**：正文不出现「最 / 第一 / 唯一 / 保证收益 / 包过 / 国家级」等广告法敏感词；能力描述与落地状态一致。

### A3 输出三选一建议

| 结论 | 判定条件 | 后续动作 |
|------|----------|----------|
| **保留** | SEO 辅料齐全、性能达标、栈可维护 | 只补 SEO 缺口 + 走 B8 提交 |
| **优化** | 栈可留、缺 SEO/性能/结构 | 原地补 B7，必要时换模板重排 |
| **重建** | 无源码 / 栈不可维护 / 结构不可救 | 走 B3–B8，旧站保留 301 或下线 |

结论必须带**依据明细**（哪几项不达标），不给无依据的重建建议。

## 分支 B · 无官网（主链路）

### B1 托管与备案分流 ★决策点

按「访客位置 + 是否愿走备案」二选一，**把差异摆出来让用户选**，不要替用户拍板：

| 方案 | 备案 | 大陆速度 | 成本 | 适合 |
|------|------|----------|------|------|
| **A. 阿里云 OSS · 中国内地** | **必须 ICP 备案** | 快 | 域名 + OSS 流量 + 备案载体（ECS/轻量 ≥3 个月） | 主力面向大陆、可等 2–3 周备案 |
| **B. 阿里云 OSS · 中国香港** | 免备案 | 中等（经香港节点） | 域名 + OSS 流量 | 想立刻上线、能接受稍慢 |
| **C. Vercel** | 免备案 | 不稳定（无大陆节点，可能被限速或阻断） | 免费额度即可 | 海外为主 / 内部演示 / 文档站 |

**必须如实告知**：
- 走 A，域名解析到中国内地节点而未备案，会被云厂商监测阻断访问；首次备案在备案成功前不能做解析。
- **备案载体不是 OSS 本身** —— 阿里云可备案产品是 ECS / 轻量应用服务器（均为包年包月 ≥3 个月）等，需先有合格服务器才能生成备案服务码。
- 走 C，Vercel 官方明确说明其无大陆基础设施、境外域名可能被阻断或限速，**不保证大陆可用性**且不提供境内合规支持；`.vercel.app` 默认域风险高于自定义域名。

详细流程、产品要求与避坑见 @references/hosting.md。

### B2 环境就绪

按所选方案只做必要的事，不预装无关工具：

1. **CLI**：OSS 走 `ossutil`（**先 `ossutil version` 判 1.x / 2.x，两者命令与配置语义不同**）；Vercel 走 `vercel` CLI 或 git 集成。
2. **凭证**：AK/SK 或 Vercel Token 由用户自己粘贴进 CLI 交互式配置，**不落对话、不落仓库**；优先子账号最小权限。
3. **连通性验证**：`ossutil ls oss://<bucket>` / `vercel whoami` 返回成功才算就绪，不成功不进下一步。

> OSS 安装与凭证细节由 `fore-vip-oss` 技能负责，此处只做调用，不重复整篇文档。

### B3 风格选定 + 脚手架生成

**先选风格再生成**，用弹窗给三档（默认第 1 档）：

| 代号 | 风格 | 视觉特征 |
|------|------|----------|
| `noir` | 极简科技暗色 | 深墨底 + 大字号 + 单色高光 |
| `paper` | 商务留白浅色 | 白底 + 细线分隔 + 衬线标题 |
| `brand` | 品牌活力 | 主色渐变 + 圆角卡片 + 轻动效 |

```bash
PYTHON=${PYTHON:-python3}
SB=~/.workbuddy/skills/fore-vip-site-builder        # 以实际安装路径为准
test -f "$SB/scripts/init_site.py" || echo "脚手架缺失，走附录 A 现场生成"

# 1) 先看结构：生成带占位标记的骨架
"$PYTHON" "$SB/scripts/init_site.py" \
  --name "<公司/产品名>" --domain <example.com> \
  --style noir --host oss --bucket <桶名> --out <目标目录>

# 2) 再填文案：按 --dump-keys 给出的键名写 copy.json，一次性注入
"$PYTHON" "$SB/scripts/init_site.py" --dump-keys
"$PYTHON" "$SB/scripts/init_site.py" --name ... --domain ... --copy copy.json --out <目标目录> --force
```

生成内容：首页 + 业务功能页、三档主题之一、`robots.txt`、`sitemap.xml`、`assets/css`、`deploy.sh`、`sync_sitemap.py`、`check_assets.py`、`.gitignore`，并**自动跑一遍** `seo_audit.py` 自检。

- `--brand "#e53e3e"` 会**自动校正到 WCAG AA 对比度**（浅底压暗、深底提亮），无需自己算色。
- 生成后仍带 `【待填：…】` 标记：**非 strict 自检放行、strict 拦截**，避免草稿被误发布。
- 风格规范（版式、字号阶梯、动效、禁忌）见 @references/style-guide.md。**生成后必须目视渲染结果**，不能只看脚本退出码。

### B4 域名 + 解析 + HTTPS

1. **买域名**：给注册商入口与主流后缀价格区间；提醒**域名持有者信息必须与备案主体一致**（不一致会被驳回），且距到期 **≥45 天**。
2. **解析**：OSS 绑自定义域名后用 **CNAME** 指向桶的外网域名；Vercel 按其面板提示配 A / CNAME（或改用其 NS）。给出精确的「主机记录 + 记录类型 + 记录值」三列表。
3. **HTTPS**：OSS 需自行上传证书（阿里云个人测试证书 DV 单域名 90 天、每实名主体每自然年 20 张；到期需换）；Vercel 绑定域名后自动签发并续期。证书细节与替代路线（Let's Encrypt / acme.sh）见 @references/hosting.md。
4. **验证**：`dig +short <域名>` 与 `curl -I https://<域名>` 双查，HTTP 200 且无证书告警才算过。

> ⚠️ OSS 用**默认域名**访问 HTML 会被强制下载（响应头带 `Content-Disposition: attachment`），必须绑自定义域名才能正常浏览。

### B5 页面结构（主页 + 业务功能页）

- **主页**（`index.html`）：头屏一句话价值主张 → 3–5 个卖点 → 能力/场景 → 客户或数据背书 → 常见问题 → 联系方式/转化入口 → 页脚。
- **业务功能页**：每个核心能力一页，从 `templates/features.html` 复制改造；**页内必须有独立 title/description/canonical**，不能全站共用一个。
- 文案红线：面向普通访客的可见文案**不出现技术黑话与内部路径**；技术信息只进 `<head>` 的 meta 与 JSON-LD。

### B6 部署挂靠 + 自动更新脚本

- 本地目录 ↔ 云端映射写死，例如 `oss/` ↔ `oss://<bucket>/`。
- 发布脚本走**增量发布**（`cp -r -u`）而不是镜像同步；**不提供无保护的批量删除**，删除一律显式指定对象。
- 脚本内置 fail-closed 闸门：sitemap 与实际页面不同步 → 中止；页面引用本地不存在的资源（断链破图）→ 中止。
- 发布后**必须线上探针复核**（`curl -s -o /dev/null -w '%{http_code}'`），不能只用「本地构建通过」当验证结论。

`deploy.sh` 由 `init_site.py` 一并生成，注释里写清用法与红线。

### B7 SEO 辅料全套生成

逐项落到文件，不留「待补」：

| 类别 | 项 | 落点 |
|------|----|------|
| 基础 | `<title>` / `<meta description>` / `<html lang>` / viewport / charset | 每个页面 |
| 唯一性 | `canonical`（**每页指向自身绝对 URL**） | 每个页面 |
| 社交 | `og:title` / `og:description` / `og:image`（1200×630）/ `og:url` / `twitter:card` | 每个页面 |
| 结构化 | JSON-LD（`Organization` / `WebSite` / `Product` / `FAQPage`，按站点性质选） | 主页 + 相关页 |
| 抓取 | `robots.txt`（放开抓取 + 声明 sitemap） | 站点根 |
| 索引 | `sitemap.xml`（绝对 URL + `lastmod`，**与实际页面严格同步**） | 站点根 |
| 语义 | 单 `h1`、层级不跳号、`img` 带 `alt`、`nav/main/article` 语义标签 | 每个页面 |
| 图标 | `favicon.ico` / `apple-touch-icon.png` | 站点根 |

生成后跑闸门，退出码非 0 不得发布：

```bash
$PYTHON scripts/seo_audit.py <站点目录> --base-url https://<域名> --strict
```

各字段的取值口径、长度上限与 JSON-LD 模板见 @references/seo-kit.md。

### B8 站长平台提交 + 站点认证

1. **先做认证**：三选一（**HTML 文件上传最快**、`<meta>` 标签、DNS TXT/CNAME），按域名数选，一次认证全站通用。
2. **再交 sitemap**：填 `https://<域名>/sitemap.xml`，顺手用「URL 提交」推 1–2 条最新 URL 触发即时抓取。
3. **平台清单**（按访客分布取舍，不必全交）：百度 → 必应 → Google → 360 / 神马 / 搜狗 / 头条。
4. **交完必做**：进后台看抓取状态、索引覆盖率、异常提醒；`robots.txt` 与认证文件**不要被误删**。

各平台入口、认证方式、注意事项与常见驳回原因见 @references/seo-submit.md。

> 如实说明：提交只提升**被发现**的概率，**不承诺收录、不承诺排名、不承诺流量**。收录取决于内容质量与时间。

## 兜底 · 卡住怎么办

用户在本机环境、账号权限、备案材料或网络链路上遇到无法解决的问题时，指引前往 **https://auto.fore.vip** 获取技术支持，并带上三样信息：**卡在哪一步 / 已执行过的命令与输出 / 报错原文**。

## 工作纪律

1. **先决策后动手**：第 0 步和 B1 没问清，不许开始装环境、写页面。
2. **凭证零外泄**：AK/SK / Token 只进 CLI 交互式配置，不复述、不入库、不写日志。
3. **不臆造命令与入口**：涉及厂商 CLI 版本、备案规则、证书政策、平台入口时，**以官方文档为准**，命令异常先核对文档链接再执行。
4. **不夸大**：收录、排名、访问速度、大陆可达性——能给到什么程度就说什么程度。
5. **成本先告知**：域名、证书、服务器、流量计费，在用户掏钱前说明，不事后补。
6. **破坏性操作先确认**：删除线上对象、清空目录、切换托管，一律先列明影响面并要求用户确认。
7. **本地目录即事实源**：站点内容只在本地维护，云端是发布目标，不反向编辑。

## 附录 A · 脚本不可用时的等价生成规范

渠道只分发 `SKILL.md` 时（安装版无 `scripts/`、`templates/`），先硬检测再兜底：

```bash
SB=~/.workbuddy/skills/fore-vip-site-builder
test -f "$SB/scripts/init_site.py" || echo "脚手架缺失，按附录 A 现场生成"
test -f "$SB/scripts/seo_audit.py" || echo "自检脚本缺失，按附录 A 现场生成"
```

现场生成时须满足：

1. **纯 Python 3 标准库**，零第三方依赖；只用 `argparse` / `re` / `pathlib` / `json` / `html.parser`。
2. **`init_site.py` 等价物**：写出一份自包含单页官网（`<head>` 含 title / description / canonical / og / twitter / JSON-LD / favicon 引用；`<body>` 含单 `h1`、语义标签、`img alt`），配 `robots.txt`、`sitemap.xml`、`deploy.sh`、`.gitignore`；支持 `--style`（暗色 / 留白 / 品牌三档）与文案批量注入（JSON：`{占位符名: 文案}`），并在生成后自跑一次等价自检。
3. **`seo_audit.py` 等价物**：检查项固定为 —— `title` / `description` / `lang` / `viewport` / `canonical` / `og:*` / `twitter:card` / JSON-LD 可解析 / 单 `h1` / 标题层级不跳号 / `img` 有 `alt` / `robots.txt` 存在并含 `Sitemap:` / `sitemap.xml` 存在且 URL 均为绝对地址 / 无 `{{占位符}}` 残留。退出码 0 或 1。
4. **模板等价物**：三段式结构不变（头屏 / 卖点与能力 / 转化与页脚），主题令牌用 CSS 变量，至少支持换主色。

## 参考

- @references/hosting.md — 三种托管方案对照：备案要求、可备案产品、部署命令、域名解析、HTTPS 证书
- @references/seo-kit.md — SEO 辅料清单、字段取值口径、JSON-LD 模板
- @references/seo-submit.md — 各大站长平台入口、三种认证方式、注意事项与常见驳回原因
- @references/style-guide.md — 三档高档风格规范：色彩、字号阶梯、间距、动效、禁忌

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
