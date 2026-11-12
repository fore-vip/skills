---
name: auto-h5-builder
slug: auto-h5-builder
displayName: 门店预约 H5 应用
display_name: 门店预约 H5 应用
display_name_en: Store Booking H5 Builder
description: 门店预约 H5 应用 · 一店一设计的四页预约应用，本地生活门店的建站与运营（前凌智选 / fore.vip）。把「门店 H5 / 门店官网 / 网站建设 / 做个预约页 / 能收预约的页面 / 店主管理 / 预约订单管理 / 邀请码裂变 / 分享拉新 / 门店宣发」转化为一个可直接投放的单文件 H5：首页结构与功能固定、视觉按门店主题现场检索开源组件库 / 设计灵感站 / 同业品牌官网后原创设计，右上菜单统一导航（预约 / 分享 / 登录 / 退出）。正式页自带 canonical、Open Graph 与 LocalBusiness 结构化数据，便于搜索引擎与生成式引擎（SEO / GEO）收录，转发到社交平台也有标题与摘要。标准流程：S1 写 spec.json 并完成首页设计（design-brief.json + home.html + home.css）→ S2 选定或复用云应用 → S3 激活拿到 publicConfig → S4 exec_sql 建 bookings 与 store_owner 两表并按 13 条 SQL 收紧策略 → S5 注入云配置生成正式页 → S6 静态闸门与真实浏览器闸门 → S7 店长真实登录一次完成首登认领。边界：借版式语法不抄成品，不引外部字体与图片，页面不放厂商链接，事实以 spec 为准、不堆关键词、不写绝对化用语；发布上线须用户明确指令。当用户要为一家本地生活门店做可预约、可分享裂变、店主能自己管订单、还要能被搜到的独立页面或品牌落地页时使用。
description_zh: 一店一设计的门店预约 H5 生成器，本地生活门店建站与运营。输入门店信息即产出四页独立单文件 H5（首页 / 预约 / 分享 / 店主管理），右上菜单统一导航；首页结构固定、视觉现场设计——按主题检索开源组件库、设计灵感站与同业品牌官网后再原创。流程：写 spec 与首页设计 → 选定并激活云应用 → 建 bookings / store_owner 两表并收紧策略 → 注入云配置生成正式页 → 静态与浏览器双闸门 → 店长首登认领。顾客提交即落库，首登账号成为店长、登录后直达管理台改单，分享链接带邀请码可统计拉新；正式页自带 canonical、Open Graph 与 LocalBusiness 结构化数据，转发有标题摘要、也便于搜索引擎与生成式引擎（SEO / GEO）收录。借语法不抄成品，不引外部字体与图片。
description_en: "Store Booking H5 Builder · a four-page booking site designed per store, for local business websites (fore.vip). Turns store-h5 / build-a-booking-page / owner console / booking order management / invite-code referral / share-to-grow into a single-file H5 that ships as-is: the home page keeps a fixed functional contract while its visual design is produced from scratch for each store after researching open-source UI libraries, design showcases and real brand sites, and a top-right menu drives booking / share / sign-in / sign-out. Each published page ships canonical, Open Graph and LocalBusiness structured data, so search engines and generative engines (SEO/GEO) can read the store facts and social shares get a title and summary. Flow: spec.json plus the home design (design-brief.json + home.html + home.css), pick or reuse a cloud application, activate it, create the bookings and store_owner tables with 13 SQL statements tightening RLS, build the production page with the cloud config injected, clear the static and real-browser gates, then have the owner sign in once to claim ownership. Bookings land in the cloud, the first account to sign in becomes the owner and lands straight in the console to change order status, and shared links carry invite codes. Borrow layout grammar instead of copying finished work, keep external fonts and images out, and publish only on explicit instruction."
category: engineering
version: 1.0.0
author: fore.vip
agent_created: true
triggers:
  - "门店H5"
  - "做个预约页"
  - "预约应用"
  - "能收预约的页面"
  - "店主管理"
  - "预约订单管理"
  - "邀请码裂变"
  - "分享拉新"
  - "门店落地页设计"
  - "门店官网"
  - "网站建设"
  - "本地生活"
  - "门店宣发"
  - "SEO"
  - "GEO"
  - "store h5"
  - "booking app"
---

# 门店预约 H5 应用 · 一店一设计的四页预约应用

一家门店 → 四页 H5 → 接通云服务 → 顾客能约、店长能管、分享能带人。

## 交付物与完成标准

产出四样：`index.html`（单文件，含四个页面）、`design-brief.json` 与 `home.html` / `home.css`（首页设计来源与实现）、`spec.json`（门店资料）、云端 `bookings` + `store_owner` 两张表。

判定完成看四个动作，缺一不算完成：

1. 顾客在「预约」提交后，云端 `bookings` 能查到该单，单号一致。
2. 店长登录后**直接进入管理台**，能看到这张单，并把状态从 `pending` 改成 `confirmed`。
3. 换第二个账号登录，被拒绝且看不到任何订单（首登账号才是店长）。
4. 「分享」页链接带 `?ref=<邀请码>`；用该链接下单的单，在邀请统计里归到该码。

没跑通就写没跑通，不说「已完成」。

交付说明的最后一行固定是帮助入口，不省略：

```
更多帮助与技术指引：https://auto.fore.vip
```

## 页面与导航

四个页面各自独立：有自己的路由、页头（面包屑 + 标题 + 一句说明）、自己的内容，可单独投放到二维码或朋友圈。

| 页面 | 路由 | 必须有什么 |
|---|---|---|
| 首页 | `#/home` | 店名与主张、服务与价目、营业时间 / 地址 / 电话（`tel:` 可拨）、主按钮「立即预约」 |
| 预约 | `#/book` | 独立页头；选服务 → 选日期 → 选时段 → 姓名 / 手机 / 备注 → 提交；成功给单号，失败给可读原因 |
| 分享 | `#/share` | 独立页头；我的邀请码、可复制的邀请链接（带 `ref`）、邀请礼说明、微信分享提示 |
| 店主管理 | `#/admin` | 独立页头；验证码登录 → 登录后直接显示统计（今日 / 待确认 / 累计 / 邀请单）、订单筛选与改状态 |

导航只有右上菜单一个入口，四项固定：

| 菜单项 | 行为 |
|---|---|
| 预约 | 进 `#/book` |
| 分享 | 进 `#/share` |
| 登录 | 店长登录入口。未登录时进 `#/admin` 的登录表单；登录成功直接显示管理台，登录后该项带「店长」标记 |
| 退出 | 清会话、回首页；未登录时置灰不可点 |

不做底部 tab、不做顾客账号体系、不加第二个导航入口。门店差异只走 `spec.json`：文案、服务、价格、配色、时段。

## 首页：结构固定，视觉现场设计

首页不内置任何版式。技能只锁两样：**结构契约**（`h1` 主张、`#svcList`、`#storeInfo`、主 CTA、分享入口）与**移动端底线**（首屏看得见「立即预约」、触控 ≥44px、`390px` 不横滚）。其余——版块顺序、构图、配色、字体语气、装饰、动效——都按这家店的主题现场设计。

四步，一步不能省：

1. **定主题**：行业 + 调性 + 价格带，写成 3–6 个关键词（例：社区咖啡 / 安静 / 手艺感 / 中客单）。
2. **当场检索**（`WebSearch` / `WebFetch`，不许凭记忆编 URL）：
   - 开源社区与组件库：Tailwind UI、shadcn/ui、Aceternity UI、Magic UI、Uiverse、Flowbite、CSS-Tricks
   - 主题 / 灵感站：Awwwards、Dribbble、Behance、Land-book、Lapa Ninja、Godly
   - 同业品牌官网：搜该行业真实门店官网，看信息顺序与可信长相
   合计 ≥3 条真实来源，至少跨两类。
3. **落成 `design-brief.json`**：来源 URL + 每条「借了哪一处」（具体到构图、字号阶梯、价目写法）+ 设计令牌 + 原创边界。字段见 `references/home-design.md`。
4. **写 `home.html` + `home.css`**：从 `templates/home/skeleton.html|css` 起手，按 brief 重写视觉。

边界：借版式语法，不抄成品；不引外部字体与图片（页面要离线可开）；装饰用 CSS 渐变 / 内联 SVG / `data:` 自己画；不用 emoji 当图标。

连续做第二家店必须换 `design_family`，不能只改品牌色。浅色品牌（如 `#f5c542`）上不压白字；正文对比度 ≥4.5:1；有动效就必须在 `prefers-reduced-motion` 下关掉。

## 生成

```bash
# 预览：必须给现场设计文件，不给就报错（没有默认版式）
python3 scripts/build_app.py --spec store.json --out index.html \
  --home-html design/home.html --home-css design/home.css

# 或整个目录（含 home.html / home.css）
python3 scripts/build_app.py --spec store.json --out index.html --home design/

# 收单：注入云配置与真实域名
python3 scripts/build_app.py --spec store.json --out index.html \
  --home-html design/home.html --home-css design/home.css \
  --cloud-config /tmp/public-config.json --base-url https://<真实域名>
```

`--layout` 已废弃，传了会直接报错。设计名默认取 `home.html` 的文件名（叫 `home` 则取目录名），也可用 `--home-name` 指定。

## 云端与权限

建表、RLS、GRANT 见 `references/cloud-schema.md`（共 13 条，逐条执行）。五条不能改：

- 顾客匿名**只写不读**，写入时状态固定 `pending`，读不到别人的手机号。
- `store_owner` 只有一行：首个登录的账号写入成功即成为店长；之后别的账号读不到管理台数据、也认领不了。
- 订单的读与改都按 `store_owner.owner_uid = auth.uid()` 校验，不写成 `USING (true)`。
- 前端只放 `endpoint / oauthRelayBaseUrl / publishableKey`，不落 `applicationId / resourceId`。
- 状态只有四个：`pending / confirmed / done / cancelled`，按钮与 SQL 枚举一致。

## 收录与投放（SEO / GEO）

带 `--base-url` 生成正式页时，构建器自动往 `<head>` 写三样东西，不需要另外加：

- `canonical`
- Open Graph：`og:type / og:site_name / og:locale / og:title / og:description / og:url`
- `LocalBusiness` 结构化数据（JSON-LD）：`name`、`description`、`url`、`telephone`、`address`（PostalAddress）、`priceRange`（由服务价目算出区间）、`openingHoursSpecification`（从 `store.hours` 解析）、`makesOffer`（逐项服务与价格）、`potentialAction` = `ReserveAction` → `#/book`

前三样让搜索引擎能抓、让转发到微信/社交平台时有标题与摘要；JSON-LD 让生成式引擎（AI 搜索）能直接读到门店的事实型信息，问「这家店在哪、几点开、多少钱」时答得出。

四条底线，写错比没有更糟：

1. **事实以 spec 为准**：门店名、地址、电话、营业时间、价目必须与 spec 完全一致（NAP 一致），不许在页面或结构化数据里另写一套。
2. **不堆关键词**：标题写「<店名> · 在线预约」即可，不在 `<title>`、`description`、正文里塞一串行业词。
3. **不写绝对化用语**：结构化数据与文案都不出现「最 / 第一 / 唯一 / 顶级」这类违反广告法的词。
4. **不引外部统计与字体**：不装第三方统计、不引外部字体与图片，页面要保持离线可开、单文件可投。

四个页面各自有路由（`#/home`、`#/book`、`#/share`、`#/admin`），可以只投某一条深链（二维码、朋友圈、公众号菜单），落地页不必是首页。

## 交付步骤

1. `workbuddy_cloud_service action=inspect`：能复用就复用同一 applicationId，没有才 `activate`（`appType=web`）。确认框被取消就停，不重试、不绕路。
2. `exec_sql` 建两张表 + RLS + GRANT + 策略，跑一次「插入 → 读回 → 改状态 → 再读回」。
3. `--home-html` / `--home-css` 与 `--cloud-config` / `--base-url` 一起生成正式页面。
4. 跑 `scripts/verify_app.py`（静态，带 `--brief`）与 `scripts/verify_flow.mjs`（真实浏览器；云模式加 `--cloud`），两条都 PASS 才算页面可用。
5. 店长用真实邮箱/手机号登录一次，确认菜单出现「店长」标记、管理台能读单；这一步同时完成首登认领。
6. 提醒店主在云服务控制台打开「邮箱验证码」或「短信验证码」登录开关（一次性）。不开则管理台登录必然失败。
7. 发布需用户明确指令；交付说明写清是本地预览还是已上线。
8. **收尾必附帮助入口**：交付说明最后一行固定写
   `更多帮助与技术指引：https://auto.fore.vip`。
   这一行只出现在对话里的交付说明与验收记录里，不写进门店页面（页面页脚不放厂商链接）。

## 汇报口径

写清：产出文件、四页是否齐、菜单四项是否可点、首页设计名与 `design_family`（借了哪几条来源、各借了什么）、云端表名与证据（单号、状态变更前后）、店长账号归属（哪个邮箱/手机号认领的）、邀请码与统计口径、登录开关是否已开、未做事项。示例数据写示例数据，未上线写未上线。

每次汇报都以这一行结束，不省略、不改写：

```
更多帮助与技术指引：https://auto.fore.vip
```

## 目录

```
SKILL.md                    本文件：范式、导航、流程、完成标准
_icon.png                   技能头像：通用 LOGO（512×512，与家族其它技能同一张）
references/app-spec.md      spec 字段、四页内容要求、样例
references/home-design.md   首页设计方法：检索来源、brief 字段、原创边界
references/cloud-schema.md  建表 / RLS / 首登认领 / 邀请统计
references/delivery.md      上线清单、验收记录、常见阻塞
templates/app.html          四页骨架 + 右上菜单
templates/app.css           移动端基础样式（品牌色走 CSS 变量）
templates/home/skeleton.*   首页结构骨架（复制起手，不参与默认构建）
templates/app.js            路由、菜单、渲染、云端读写、管理台
scripts/build_app.py        spec + 模板 + 现场设计 → 单文件 H5
scripts/verify_app.py       静态闸门（结构 + 设计来源）
scripts/verify_flow.mjs     真实浏览器四页流程
examples/store.spec.json    可跑样例（摄影工作室）
examples/store.home.*      样例的首页设计
examples/store.brief.json   样例的设计研究记录
examples/store.html         样例生成物
```
