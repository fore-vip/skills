---
name: huoli
version: 1.2.5
description: 火力同城 — 独立 skill，内联 act 工具副本 + huoli 专属付费闸（C 端付费生效；X402 Agent 代付协议已对齐 SkillHub A2M，待 SkillHub 入驻后闭环）
author: fore.vip
license: UNLICENSED
tags:
  - local-life
  - pay-skill
  - city-discovery
  - mcp
  - act-compatible
triggers:
  - "搜火力频道"
  - "看火力频道的需求"
  - "火力同城有什么本地生活需求"
  - "解锁火力频道"
  - "火力付费解锁"
  - "在火力发个频道"
  - "火力建个本地生活频道"
negative_triggers:
  - "创建与火力/本地生活无关的活动"
  - "发布非火力频道的免费活动"
compatibility:
  - Marvis
  - WorkBuddy
  - MCP-client
---

# huoli — 火力同城需求检索（独立 Skill · Pay Skill 范式）

火力同城是 **独立 skill**：act 的活动（频道）/ 行程（需求）工具契约以 **内联副本**形式拆分在 `references/` 分目录（`act-*.json`），huoli 自包含、不跨 skill 引用 `../act`。huoli 专属的付费闸（`get_huoli_needs` / `payChannel`）与支付逻辑独立实现。

> **与 act 的关系**：act 文件与后端**保持不变**；huoli 这边把 act 工具契约完整复制到 `references/act-*.json` 分文件，并在其上叠加「火力频道标记 + ¥1 付费解锁 + X402 支付闸」。两边是独立维护的副本关系，非运行期依赖。

## Description

火力把本地生活 O2O 组织为「频道（活动）+ 需求（行程推荐）」两层，并支持用户自主运营（act 工具内联在 references/ 分目录）：

- **频道检索与选择**：搜/选火力频道（`activity.huoli_channel==true`），调用内联的 `search_activities` / `get_activity_detail`（见 references/act-*.json）。
- **无结果引导创建频道**：当没有匹配频道时，引导用户创建——调用内联的 `create_activity`，约束 **`type=ai`（沿用默认）+ `fee=100`（¥1 付费解锁）+ 打 `huoli_channel=true` 标记**（见 references/act-create.json）。
- **组织推送需求（行程推荐）**：频道内需求 = 行程（`schedule` 表），调用内联的 `list_activity_schedules` 查询；发布需求走 act 的创建行程接口（见 references/act-schedules.json）。
- **付费解锁（支付子级）**：付费频道（¥1 / 100 分）解锁后，可读取该频道内**全部**需求；付费经微信支付 Agent Pay X402 协议触发，返回 `WeixinPay-Required` 支付码，由调用方代理用户支付授权。

> **⚠️ 付费范围说明（计费边界）**
> - **C 端用户（小程序 / H5）**：经 `pages/huoli/needs.vue` → `payChannel()` 走微信 Native 扫码付（¥1），**付费真实生效**，是唯一强制计费的路径。
> - **Agent / MCP 调用方**：需求数据等同于 act 的 `schedule`，亦可通过 `list_activity_schedules`（`/act/schedules`，同 `X-API-Key`、无付费校验）直接读取——即 `get_huoli_needs` 的 ¥1 闸对 Agent 侧**不强制**（属运营 / 组织视角，不触发计费）。
> - **因此 huoli 作为 Pay Skill 的付费价值锚定「C 端用户侧」**；X402 付费范式（Agent 代付）协议已在 `huoli` 云对象对齐 SkillHub A2M 规范（402 响应体 `WeixinPay.{WeixinPay-Required}` + 重试头 `X-Out-Trade-No`=payment_code + order.payment_code 回查解锁）。剩余阻塞为 **SkillHub 入驻**：skillId `huoli` 未在 SkillHub 后台注册 + 绑定微信商户号前，preorder 端点返回 302（6a 验签失败），故 `needs(付费)` 暂返回 `402 + blocked + PAY_NOT_READY`；入驻完成后即闭环。C 端用户付费（`payChannel`）不受影响。

> **🔒 隐私红线（仅约束 Agent/MCP 面）**：需求列表的 **Agent/MCP 面**（`get_huoli_needs` / 云对象 `queryNeeds()`）**不返回联系方式类字段**（`contact` / `phone` / `mobile` / `wechat` / `wxid`），仅展示 `content` / `price` / `images` / `start_time` 等非隐私信息；过滤以 `.field()` 投影实现，覆盖免费与已解锁两路径。联系方式属发布者隐私，第三方 Agent 不应获取。
> **C 端 `needs.vue` 例外**：该页是小程序/H5 消费者面，直接经 clientDB 读 `schedule` 并**有意展示联系方式**（「联系发布者」是本地生活撮合的产品价值），不套用 Agent 面红线；其数据可见性由 `schedule` 的 clientDB 权限兜底。

**解决的问题**：让 Agent 生态能按次计费检索/运营本地生活需求，企业侧无需重构 act 业务逻辑，仅在原服务上叠加开发者签名 + X402 预下单 + 支付触发返回。

**局限性**：

- 所有写操作（创建频道、发布需求）的实际后端由 `act` 承担，huoli 只规定调用约束，不另起云对象。
- 频道列表 MCP 端点（`list_huoli_channels`）当前为规划项，前端频道列表 `pages/huoli/channel.vue` 直读 `activity` 集合。

## Usage

### 步骤 1 — 频道检索与选择（复用 act）

```js
// 工具：search_activities（来自 act）
// 端点：POST https://mcp.fore.vip/act/search
// 入参：{ keyword?, type?, latitude?, longitude?, page?, pageSize? }
// 火力视角：keyword 匹配本地生活需求语义；结果中筛 huoli_channel==true 即为火力频道
```

选择某频道后取 `activity._id`，进入步骤 2 / 3。

### 步骤 2 — 无结果 → 引导创建频道（复用 act create_activity）

当搜索无匹配火力频道时，引导用户创建。调用 act 的 `create_activity`，**火力约束三件套**：

```js
// 工具：create_activity（来自 act，X-API-Key 鉴权）
// 端点：POST https://mcp.fore.vip/act/create
create_activity({
  content: "南山科技园午休好去处",   // 必填 ≤500 字
  address: "深圳南山区科技园",        // 必填 ≤128 字
  cover: "https://...",              // 必填，后端自动转存
  tags: ["午休", "本地生活"],
  latitude: 22.54, longitude: 113.95,
  fee: 100,                          // ⭐ 火力强制：¥1=100分 付费解锁频道
  // ⭐ 火力标记：火力 SKILL 创建时显式传 huoli_channel=true，后端原样透传持久化（非 schema 字段，写入即存；type 沿用 act 默认 ai，不改）
})
// 返回 { _id, url, pay_required: true } → 即新建火力频道
```

> 火力频道识别约定：**`activity.huoli_channel == true`**（`fee=100` 即付费频道）。`type` 沿用 act 默认 `ai`，不改后端 enum。

### 步骤 3 — 组织推送需求（行程推荐，复用 act）

频道内需求 = act 的行程（`schedule`）。查询复用 `list_activity_schedules`；发布需求走 act 创建行程接口（同 act 用法，仅 `activity_id` 填火力频道 `_id`）。

```js
// 工具：list_activity_schedules（来自 act）
// 端点：POST https://mcp.fore.vip/act/schedules
// 入参：{ activity_id: "<火力频道 _id>", page?, pageSize? }
// → 返回该频道内全部需求（行程推荐）列表
```

### 步骤 4 — 付费解锁（支付子级，huoli 专属 X402）

> **状态**：以下为 X402 付费闸的**目标态**（协议层已落地）。剩余阻塞为 SkillHub 入驻（skillId 注册 + 微信商户号绑定）未完成时，preorder 端点 302（`needs(付费)` 暂返 `402 + blocked + PAY_NOT_READY`）；入驻后即闭环。C 端用户付费不受影响。

付费频道未解锁时，huoli 的 `get_huoli_needs` 以**集成响应模式**返回真实 **HTTP 402**，并通过响应头 `WeixinPay-Required` 注入 `payment_code`（uniCloud URL化默认 200，自定义非 200 状态码必须走集成响应 `mpserverlessComposedResponse: true`）：

```json
{
  "mpserverlessComposedResponse": true,
  "statusCode": 402,
  "headers": {
    "content-type": "application/json",
    "WeixinPay-Required": "<payment_code>"
  },
  "body": "{\"errCode\":402,\"pay_required\":true,\"unlocked\":false,\"out_trade_no\":\"<payment_code>\",\"amount\":100,\"currency\":\"CNY\",\"prompt\":\"本次查询火力频道需求需要付费（¥1 解锁全部需求）。请将 WeixinPay-Required 的值作为 paymentCode 交给 weixinpay_pay，以向用户申请支付授权。\"}"
}
```

调用方将 `WeixinPay-Required` 的值作为 `paymentCode` 交给微信支付 Agent（`weixinpay_pay`），由 Agent 向用户申请支付授权。**支付成功后，用该笔账单的 `payment_code`（`= WeixinPay-Required` 的值）作为 `X-Out-Trade-No` 头重请求即可解锁**（SkillHub A2M 规范；前端路径的 `orderId` 来自 `payChannel()` 返回值、以 `X-Unlocked` 头兼容）：

```js
const res = await fetch('https://mcp.fore.vip/huoli/needs', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': '<your-api-key>',
    'X-Out-Trade-No': '<payment_code>'   // SkillHub A2M 标准重试头，值=402 响应的 WeixinPay-Required（payment_code）
  },
  body: JSON.stringify({ channel_id: 'act_xxxx' })
})
```

### 前端直付（小程序 / H5，huoli 专属）

前端页面 `pages/huoli/needs.vue` 走 `payChannel()` 直接拿微信 Native `code_url` 扫码付，**不经 X402**（X402 仅对 MCP / Agent 调用方生效）：

```js
// 云对象方法：huoli.payChannel({ channel_id })
// 返回：{ errCode: 0, unlocked: false, orderId, codeUrl, amount: 100 }
const r = await uniCloud.importObject('huoli').payChannel({ channel_id: 'act_xxxx' })
// r.codeUrl → vk-uni-qrcode 展示扫码付 → 轮询 order.pay 自动解锁
```

## Configuration

| 项 | 说明 |
|----|------|
| `X-API-Key` | `get_huoli_needs` 必须带；复用 ai-mcp 动态 Key 体系，与 `act` 一致。无 Key 返回 `403`。 |
| `X-Out-Trade-No` | SkillHub A2M 标准重试头，值=preorder 返回的 `payment_code`；云对象按 `payment_code` 回查 `order` 已支付解锁。 |
| `X-Unlocked` | C 端遗留兼容头，值=订单 `_id`；非 SkillHub 标准重试头。 |
| `activity.huoli_channel` | 火力频道标记（布尔）。非 schema 声明字段，写入即存，不触碰既有 activity 模型。 |
| `create_activity` 火力约束 | `type` 沿用 act 默认 `ai`；`fee=100`（¥1 付费解锁）；火力 SKILL 显式传 `huoli_channel=true`，后端原样透传（非 schema 字段，写入即存）。 |
| `order.type=5` | 火力解锁订单固定值；`oid`=频道 ID，`price`=100（分）。 |

精确字段定义（act 工具原始契约 + huoli 扩展）一律读 `references/mcp.json`，需要精确字段时再读取，不要凭记忆。

## Examples

**例 1：搜火力频道**

```
POST /act/search  { keyword: "午休去处", latitude, longitude }
→ 结果中筛 huoli_channel==true 的即为火力频道
```

**例 2：无结果 → 创建火力频道**

```
用户："火力没有合适的频道，帮我建一个"
→ 引导收集 content/address/cover（同 act 必填）
→ POST /act/create { content, address, cover, fee:100, huoli_channel:true }（火力显式传，后端透传）
→ 返回 { _id, pay_required:true } = 新火力频道
```

**例 3：组织推送需求（行程推荐）**

```
POST /act/schedules  { activity_id: "<火力频道 _id>" }
→ 返回该频道内全部需求（行程推荐）列表 total=N
```

**例 4：付费解锁**

> 以下为目标态；当前实际返回 `402 + blocked + PAY_NOT_READY`（SkillHub 入驻未完成导致 preorder 302，见步骤 4 说明）。

```
POST /huoli/needs  { channel_id: "act_pay_xxx" }  + X-API-Key
→ 402 + WeixinPay-Required(payment_code)   # 入驻完成后；当前为 PAY_NOT_READY（302）
→ 交 weixinpay_pay 代理支付
→ 再次 POST /huoli/needs + X-Out-Trade-No: <payment_code>
→ { errCode: 0, unlocked: true, list: [...] }
```

## Requirements

- **复用 act MCP 服务端**：`https://mcp.fore.vip/act/{search,detail,create,schedules}`（URL 化云对象，act 保持不变）。
- **huoli 专属 MCP 服务端**：`https://mcp.fore.vip/huoli/needs`（付费闸）+ `https://mcp.fore.vip/http/uni-skill-pay-notify`（支付回调）。
- **微信支付 V3 凭证**：`uni-config-center/uni-skill-pay/config.json` 的 `wxpayV3` 段（uni-config-center 官方 config.json 范式）。
- **SkillHub 开发者凭证**：同 `config.json` 的 `skillhub` 段（X402 预下单签名）。
- **依赖云对象**：`huoli`（needs / payChannel）、`uni-skill-pay-notify`（回调验签 + AES-256-GCM 解密置单）。
- **前端页面**：`pages/huoli/channel.vue`、`pages/huoli/needs.vue`（uni-app 主包）。

## Troubleshooting

| 现象 | 原因 | 处理 |
|------|------|------|
| `403 Invalid or missing X-API-Key` | 未带 / Key 无效 | 检查 `X-API-Key` 头，复用 ai-mcp 动态 Key |
| `402 + WeixinPay-Required` | 付费频道未解锁（X402 目标态；当前因端点故障改为返回 PAY_NOT_READY） | 按范式交 `weixinpay_pay` 代理支付，再带 `X-Unlocked` 重请求 |
| `402 + blocked: true + PAY_NOT_READY` | X402 预下单端点故障（`payapp.weixin.qq.com/.../preorder` 被微信网关 302 拦截；**非** V3 凭证问题，V3 Native 正常） | 属平台侧事项，需回 SkillHub 官方文档核实端点；C 端用户付费（`payChannel`）不受影响 |
| 创建的频道不在火力列表 | 未打 `huoli_channel=true` / `fee≠100` | 确认创建时 fee=100，后端自动标记 huoli_channel |
| `Channel not found` | `channel_id` 错 / 非 huoli 频道 | 确认 `activity._id` 且 `huoli_channel==true` |
| 解锁后仍返回 402 | `X-Out-Trade-No`/`payment_code` 订单校验失败 | 确认 `order.payment_code == X-Out-Trade-No` 且 `pay==true`（C 端 `X-Unlocked` 路径：确认 `oid==频道ID && type==5 && pay==true`） |

## References

| 项 | 路径 / 链接 |
|----|-------------|
| 工具契约总入口 | `references/mcp.json`（聚合以下分文件） |
| ├ act 搜索（内联副本） | `references/act-search.json` |
| ├ act 详情（内联副本） | `references/act-detail.json` |
| ├ act 创建频道（内联副本 + huoli 约束） | `references/act-create.json` |
| ├ act 行程列表（内联副本） | `references/act-schedules.json` |
| └ huoli 付费闸（专属） | `references/huoli-needs.json` |
| 外部 client 配置 | `mcp-standard.json`（根） |
| MCP 服务地址 | `https://mcp.fore.vip` |
| 频道列表页（前端） | `pages/huoli/channel.vue` |
| 需求页（前端） | `pages/huoli/needs.vue` |
| 部署与联调 | `doc/HUOLI_DEPLOY.md` |
| SkillHub Pay Skill 范式 | `https://skillhub.cn/tutorials#agent-pay-upgrade` |

## Changelog

### 1.2.5

- **付费闸返回真实 HTTP 402（集成响应模式）**：此前因不了解 uniCloud URL化自定义状态码机制，付费未解锁态以 `errCode:402` 普通 JSON 体（被框架包裹为 200）兜底。现改为 `mpserverlessComposedResponse: true` + `statusCode: 402` + 响应头 `WeixinPay-Required: <payment_code>`，严格对齐 SkillHub A2M 规范（Agent 识别 HTTP 402 + WeixinPay-Required 头即触发 `weixinpay_pay`）。`body` 同时含 `out_trade_no`/`amount`/`prompt` 便捷字段。
- 错误分支（`PAY_NOT_READY` / `V3_ERROR`）保持普通 JSON 返回（框架包裹为 200），不再误用 402，避免 Agent 误判为「可支付」态。
- 文档（`SKILL.md` / `references/huoli-needs.json`）同步：402 标注为真实 HTTP 状态码、`WeixinPay-Required` 为响应头（非 body 字段）。版本升 1.2.5。

### 1.2.4

- **对齐 SkillHub A2M 付费协议（修复「体验不全」真根因）**：此前 `needs()` 读取 `X-Unlocked` 头解锁，但 SkillHub 官方规范 Agent 支付后重试携带的是 **`X-Out-Trade-No`**（值=preorder 返回的 `payment_code`），导致 Agent 面付费闭环永远无法解锁。修正：
  - `checkUnlocked` 改读 `X-Out-Trade-No`（`payment_code` → `order` 回查已支付解锁），保留 `X-Unlocked` 作 C 端兼容。
  - `needs()` 付费流程 preorder 成功后把 `payment_code` 落库（`order.payment_code`），并在 402 响应体补齐 `out_trade_no`/`amount`（遵循 SkillHub 最佳实践体结构）。
  - `order` schema 新增 `payment_code` 字段。
  - `SKILL.md` 全部 `X-Unlocked` 协议描述改为 `X-Out-Trade-No`（值=payment_code），与官方逐字对齐。
- 剩余阻塞（非代码死结）：`skillId huoli` 未在 SkillHub 后台注册 + 绑定微信商户号前，preorder 返回 302（6a 验签失败），`needs(付费)` 暂返 `PAY_NOT_READY`；入驻后即闭环。C 端 `payChannel` 直付已真验可用。

### 1.2.3

- 品牌/标识归一：`huoli` 关键字统一改为「火力」（huoli）；支付能力抽离为通用底座 `uni-skill-pay`（含 `uni-skill-pay-notify` 通用回调），凭证统一单份 `uni-config-center/uni-skill-pay/config.json`，支撑多 SKILL 子模块共用支付。前端 `pages/huoli/*` → `pages/huoli/*`；`activity.huoli_channel` → `huoli_channel`（需数据迁移）。

### 1.2.2

- 隐私红线：huoli 云对象 `queryNeeds()` 以 `.field()` 投影**过滤联系方式类字段**（contact/phone/mobile/wechat/wxid），需求列表（免费 + 已解锁两路径）不再泄露发布者隐私。对应 `references/huoli-needs.json` 列表字段说明同步更新，并在正文新增「隐私红线」段落。

### 1.2.1

- 文档/声明层收敛（不动后端）：
  - 增补「付费范围说明」：明确 ¥1 付费仅对 C 端用户（needs.vue + payChannel）强制生效；Agent/MCP 侧经 `act/schedules` 读需求不触发计费（运营视角）。
  - X402 付费闸标注为「目标态」，当前因 SkillHub 预下单端点被微信网关 302 拦截返回 `PAY_NOT_READY`，Agent 代付闭环暂不可用。
  - 修正 Troubleshooting：`PAY_NOT_READY` 归因由「V3 凭证未配置」改为「X402 端点故障（非 V3 问题）」。
  - 补全 `X-Unlocked` 流程中 `orderId` 来源说明。
  - frontmatter：`tags` 移除过时 `act-submodule`、改 `act-compatible`；`negative_triggers` 收紧为「非火力/本地生活类」；版本升 1.2.1。

### 1.2.0

- 重构为**独立 skill**：移除对 `../act` 的引用，act 工具契约以内联副本拆分进 `references/act-*.json`（search/detail/create/schedules），huoli 自包含。
- `references/mcp.json` 改为聚合本地分文件（`$ref: ./act-*.json`），不再跨 skill 引用。
- act 文件/后端保持不变，两边为独立维护的副本关系。

### 1.1.0

- 重构为 **act 子级模块**：明确复用 act 后端（search/detail/create/schedules），huoli 仅叠加频道标记 + 付费闸。
- 业务流写入正文：频道检索/选择 → 无结果引导创建（复用 create_activity，type=ai + fee=100 + huoli_channel=true）→ 组织推送需求（行程推荐）→ 支付逻辑子级（X402）。
- act 文件与后端保持不变。

### 1.0.0

- 初版：huoli 云对象 `needs()`（付费闸 X402）+ `payChannel()`（前端直付）；uni-skill-pay-notify 回调验签解密。
- 前端频道列表 / 需求页（主包）+ 「我的」页入口。
- SKILL 声明三件套（SKILL.md / references/mcp.json / mcp-standard.json）对齐 act 分层。
- 按 SkillHub 官方规范补齐 frontmatter 与标准章节结构。
