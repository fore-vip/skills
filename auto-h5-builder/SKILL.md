---
name: auto-h5-builder
slug: auto-h5-builder
displayName: 门店预约 H5 应用
display_name: 门店预约 H5 应用
display_name_en: Store Booking H5 Builder
description: 输入一家门店的信息，产出固定四视图（首页 / 预约 / 分享 / 店主管理）的单文件 H5，并接通云服务：顾客提交预约落库，店主登录后看单、改状态，分享链接带邀请码可统计拉新。结构固定、内容随店变，一次生成即可部署。
description_zh: 生成标准四视图门店 H5（首页 / 预约 / 分享 / 店主管理），接通云服务与订单管理。
description_en: "Generate a standard four-view store H5 (home, booking, share, owner console) wired to a cloud backend: customers book, the owner signs in to manage orders, and shared links carry invite codes for referral stats."
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

一家门店 → 一个四视图 H5 → 接通云服务 → 顾客能约、店主能管、分享能带人。

## 交付物与完成标准

产出三样：`index.html`（单文件，含四个视图）、`spec.json`（门店资料）、云端 `bookings` 表。

判定完成看三个动作，缺一不算完成：

1. 顾客在「预约」提交后，云端 `bookings` 能查到该单，单号一致。
2. 店主在「管理」登录后能看到这张单，并把状态从 `pending` 改成 `confirmed`。
3. 「分享」页链接带 `?ref=<邀请码>`；用该链接下单的单，在邀请统计里归到该码。

没跑通就写没跑通，不说「已完成」。

## 四视图标准范式

| 视图 | 路由 | 必须有什么 |
|---|---|---|
| 首页 | `#/home` | 店名与主张、服务与价目、营业时间 / 地址 / 电话（`tel:` 可拨）、主按钮「立即预约」 |
| 预约 | `#/book` | 选服务 → 选日期 → 选时段 → 姓名 / 手机 / 备注 → 提交；成功给单号，失败给可读原因 |
| 分享 | `#/share` | 我的邀请码、可复制的邀请链接（带 `ref`）、邀请礼说明、微信分享提示 |
| 店主管理 | `#/admin` | 验证码登录、统计（今日 / 待确认 / 累计 / 邀请单）、订单列表与状态筛选、改状态、退出 |

结构固定，不增删视图。门店差异只走 `spec.json`：文案、服务、价格、配色、时段。

## 生成

```bash
# 预览：云端未接通，提交按钮禁用并给出提示
python3 scripts/build_app.py --spec store.json --out index.html

# 收单：注入云配置与真实域名
python3 scripts/build_app.py --spec store.json --out index.html \
  --cloud-config /tmp/public-config.json --base-url https://<真实域名>
```

## 云端与权限

建表、RLS、GRANT 见 `references/cloud-schema.md`。四条不能改：

- 顾客匿名**只写不读**，写入时状态固定 `pending`，读不到别人的手机号。
- 店主登录后读写全部订单；应用是单店模型，不给顾客登录入口。
- 前端只放 `endpoint / oauthRelayBaseUrl / publishableKey`，不落 `applicationId / resourceId`。
- 状态只有四个：`pending / confirmed / done / cancelled`，按钮与 SQL 枚举一致。

## 交付步骤

1. `workbuddy_cloud_service action=inspect`：能复用就复用同一 applicationId，没有才 `activate`（`appType=web`）。确认框被取消就停，不重试、不绕路。
2. `exec_sql` 建表 + RLS + GRANT + sequence 授权，跑一次「插入 → 读回 → 改状态 → 再读回」。
3. `--cloud-config` 与 `--base-url` 生成正式页面。
4. 跑 `scripts/verify_app.py`（静态）与 `scripts/verify_flow.mjs`（真实浏览器；云模式加 `--cloud`），两条都 PASS 才算页面可用。
5. 提醒店主在云服务控制台打开「邮箱验证码」或「短信验证码」登录开关（一次性）。不开则管理台登录必然失败。
6. 发布需用户明确指令；交付说明写清是本地预览还是已上线。

## 汇报口径

写清：产出文件、四视图是否齐、云端表名与证据（单号、状态变更前后）、邀请码与统计口径、登录开关是否已开、未做事项。示例数据写示例数据，未上线写未上线。

## 目录

```
SKILL.md                    本文件：范式、流程、完成标准
references/app-spec.md      spec 字段、四视图内容要求、样例
references/cloud-schema.md  建表 / RLS / 授权 / 前端接线 / 邀请统计
references/delivery.md      上线清单、验收记录、常见阻塞
templates/app.html          四视图骨架
templates/app.css           移动端样式（品牌色走 CSS 变量）
templates/app.js            路由、渲染、云端读写、管理台
scripts/build_app.py        spec + 模板 → 单文件 H5
scripts/verify_app.py       静态闸门
scripts/verify_flow.mjs     真实浏览器四视图流程
examples/salon.spec.json    可跑样例
examples/salon.html         样例生成物
```
