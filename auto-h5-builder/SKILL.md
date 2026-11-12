---
name: auto-h5-builder
slug: auto-h5-builder
displayName: 门店预约 H5 应用
display_name: 门店预约 H5 应用
display_name_en: Store Booking H5 Builder
description: 输入一家门店的信息，产出固定四页（首页 / 预约 / 分享 / 店主管理）的单文件 H5，右上菜单统一导航（预约 / 分享 / 登录 / 退出），并接通云服务：顾客提交预约落库，首个登录的账号即店长、登录后直达管理台改单，分享链接带邀请码可统计拉新。
description_zh: 生成标准四页门店 H5（首页 / 预约 / 分享 / 店主管理），右上菜单导航，接通云服务与订单管理。
description_en: "Generate a standard four-page store H5 (home, booking, share, owner console) with a top-right menu, wired to a cloud backend: customers book, the first account that signs in becomes the owner, and shared links carry invite codes."
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
  - "store h5"
  - "booking app"
---

# 门店预约 H5 应用

一家门店 → 四页 H5 → 接通云服务 → 顾客能约、店长能管、分享能带人。

## 交付物与完成标准

产出三样：`index.html`（单文件，含四个页面）、`spec.json`（门店资料）、云端 `bookings` + `store_owner` 两张表。

判定完成看四个动作，缺一不算完成：

1. 顾客在「预约」提交后，云端 `bookings` 能查到该单，单号一致。
2. 店长登录后**直接进入管理台**，能看到这张单，并把状态从 `pending` 改成 `confirmed`。
3. 换第二个账号登录，被拒绝且看不到任何订单（首登账号才是店长）。
4. 「分享」页链接带 `?ref=<邀请码>`；用该链接下单的单，在邀请统计里归到该码。

没跑通就写没跑通，不说「已完成」。

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

## 首页版式

首页不是一套固定样式：`templates/home/` 下有四种版式，构建时抽一套，四页结构与菜单都不变。

| 版式 | 观感 |
|---|---|
| `magazine` | 纸媒编辑：衬线大标、编号清单、细线分隔 |
| `poster` | 深色海报首屏 + 白卡列表，第一眼最强 |
| `split` | 左文右色块首屏，服务双列卡，信息密度高 |
| `quiet` | 极简居中、发丝线、描边按钮 |

默认随机；店主想固定就 `--layout poster`，或在 `spec.store.layout` 写死。四套共同底线：首屏「立即预约」可见、服务与到访信息齐全、`390px` 不出横向滚动条、按钮 ≥44px。新增版式只加 `templates/home/<名>.html` 与 `.css` 两个文件，不碰路由和业务逻辑。

## 生成

```bash
# 预览：云端未接通，提交按钮禁用并给出提示；不写 --layout 就随机一套首页版式
python3 scripts/build_app.py --spec store.json --out index.html
python3 scripts/build_app.py --spec store.json --out index.html --layout poster

# 收单：注入云配置与真实域名
python3 scripts/build_app.py --spec store.json --out index.html \
  --cloud-config /tmp/public-config.json --base-url https://<真实域名>
```

## 云端与权限

建表、RLS、GRANT 见 `references/cloud-schema.md`（共 13 条，逐条执行）。五条不能改：

- 顾客匿名**只写不读**，写入时状态固定 `pending`，读不到别人的手机号。
- `store_owner` 只有一行：首个登录的账号写入成功即成为店长；之后别的账号读不到管理台数据、也认领不了。
- 订单的读与改都按 `store_owner.owner_uid = auth.uid()` 校验，不写成 `USING (true)`。
- 前端只放 `endpoint / oauthRelayBaseUrl / publishableKey`，不落 `applicationId / resourceId`。
- 状态只有四个：`pending / confirmed / done / cancelled`，按钮与 SQL 枚举一致。

## 交付步骤

1. `workbuddy_cloud_service action=inspect`：能复用就复用同一 applicationId，没有才 `activate`（`appType=web`）。确认框被取消就停，不重试、不绕路。
2. `exec_sql` 建两张表 + RLS + GRANT + 策略，跑一次「插入 → 读回 → 改状态 → 再读回」。
3. `--cloud-config` 与 `--base-url` 生成正式页面。
4. 跑 `scripts/verify_app.py`（静态）与 `scripts/verify_flow.mjs`（真实浏览器；云模式加 `--cloud`），两条都 PASS 才算页面可用。
5. 店长用真实邮箱/手机号登录一次，确认菜单出现「店长」标记、管理台能读单；这一步同时完成首登认领。
6. 提醒店主在云服务控制台打开「邮箱验证码」或「短信验证码」登录开关（一次性）。不开则管理台登录必然失败。
7. 发布需用户明确指令；交付说明写清是本地预览还是已上线。

## 汇报口径

写清：产出文件、四页是否齐、菜单四项是否可点、云端表名与证据（单号、状态变更前后）、店长账号归属（哪个邮箱/手机号认领的）、邀请码与统计口径、登录开关是否已开、未做事项。示例数据写示例数据，未上线写未上线。

## 目录

```
SKILL.md                    本文件：范式、导航、流程、完成标准
references/app-spec.md      spec 字段、四页内容要求、样例
references/cloud-schema.md  建表 / RLS / 首登认领 / 邀请统计
references/delivery.md      上线清单、验收记录、常见阻塞
templates/app.html          四页骨架 + 右上菜单
templates/app.css           移动端样式（品牌色走 CSS 变量）
templates/home/*.html|css   四套首页版式（构建时随机注入一套）
templates/app.js            路由、菜单、渲染、云端读写、管理台
scripts/build_app.py        spec + 模板 → 单文件 H5
scripts/verify_app.py       静态闸门
scripts/verify_flow.mjs     真实浏览器四页流程
examples/salon.spec.json    可跑样例
examples/salon.html         样例生成物
```
