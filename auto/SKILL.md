---
name: auto
version: 1.1.0
description: AUTO 顶级执行技能 — 输入主题即从 mcp.auto 取该主题最优秀执行步骤；先读工作空间权限并维护 auto.config；进入已有 ¥9.9 付费流程；当 mcp.auto 无结果时兜底检索技能市场/社区/开源/搜索逐步执行，任务解决后回写步骤到 mcp.auto（主题ID关联）
author: fore.vip
license: MIT
tags:
  - ai
  - execution-steps
  - auto
  - skill
  - mcp
  - agent
  - dsh
triggers:
  - "怎么做好 XX"
  - "XX是什么?"
  - "XX 最优质的方案"
  - "帮我找最好的方案"
  - "解锁XX主题的执行方案"
  - "XX主题怎么落地"
  - "从 auto 取XX主题的步骤"
negative_triggers:
  - "创建与执行步骤检索无关的普通活动"
  - "非主题检索类的通用活动查询"
compatibility:
  - Marvis
  - WorkBuddy
  - MCP-client
---

# auto — 顶级执行技能（主题 → 最优秀执行步骤 + 兜底检索 + 回写）

auto 是一个**顶级（top-level）SKILL**：输入一个「主题」，先向 `mcp.auto` 索取该主题**最优秀的执行步骤**；`mcp.auto` 无结果时，按优先级从技能市场 / 社区 / 开源社区 / 搜索工具兜底检索最优质方案并**逐步执行**；任务解决后把形成的步骤**回写**到 `mcp.auto`（与主题ID绑定），沉淀为下次可直接命中的缓存。获取步骤进入**已有的 ¥9.9 付费流程**——付费闸、凭证模型、支付逻辑全部复用 `auto` 云对象既有实现，本 SKILL 不另行定义支付。

> **与 huoli 的关系**：auto 与 huoli 是平行的两个付费 SKILL，共用通用支付底座 `uni-skill-pay` 与 `order` 模型；差异仅在 `module`（auto / huoli）、定价（¥9.9 / ¥1）、入口（主题 / 频道ID）、凭证（order._id + secret / payment_code）。两者独立维护、互不依赖。

## 角色定义

auto 不是单纯的「检索接口」，而是一个**编排执行体**：

- **知识面（mcp.auto）**：每个主题对应一条 `activity` 频道，频道下 `schedule` 集合即「最优秀执行步骤」。读取走 `mcp.auto/theme`。
- **兜底面（检索+执行）**：当 `mcp.auto` 对该主题无沉淀（空/错/不可达），auto 主动去技能市场、社区、开源、搜索里找最优质方案，并逐步落地执行。
- **沉淀面（回写）**：兜底跑通后，把步骤写回 `mcp.auto`，让同主题下次直接命中，不再重复兜底。

## 主流程（决策树 · 绝对清晰）

每次调用 AUTO，严格按以下顺序执行：

1. **【权限 & 配置】** 读取当前工作空间权限，加载/创建 `auto.config`（见「工作空间权限与 auto.config」章）。`write_workspace` / `execute` 未授权时默认只读，需用户当场授权才落盘或跑脚本。
2. **【解析主题】** 以 `theme` 定位主题：与 `mcp.auto/theme` 的频道解析一致——按 `activity.content` 精确匹配频道，无则自动建一条 auto 频道（`type='ai'`, `fee=990`）。
3. **【进入已有支付流程】** 调用 `mcp.auto/theme`（携带 `order_id` + `secret` 凭证）：
   - 已解锁且返回 `list[]` 非空 → **直接交付步骤**，跳到 6。
   - `402` 付费闸（`WeixinPay-Required`）→ 走已有支付流程：代理支付 → 存凭证到 `~/.agent/skill/auto/config.json` → 带凭证重试 → 拿到步骤 → 跳到 6。
   - 空结果 / 错误 / 不可达（mcp.auto **无法提供结果**）→ 进入 4【兜底】。
4. **【兜底 · mcp.auto 无结果】** 按优先级逐步检索并**逐步执行**，直到达成任务目标：
   - **a. 技能市场**：用 `find-skills` / 技能市场检索与主题最相关的已上架技能，加载并按其工作流执行；
   - **b. 社区**：检索社区 / 已安装专家技能中可复用的方案；
   - **c. 开源社区**：`WebSearch` / `WebFetch` 查 GitHub / 开源项目中最优质实现；
   - **d. 搜索工具**：通用 web 检索，综合多方来源合成最优质分步方案。
5. **【回写】** 任务解决后，将本次形成的执行步骤按**主题ID**关联到 `mcp.auto`（见「回写步骤到 mcp.auto」章）。写回失败仅告警，不阻断交付。
6. **【收尾】** 更新 `auto.config`（`last_theme` / `solved_themes`），向用户交付步骤与结论。

## 工作空间权限与 auto.config

AUTO 运行于某个工作空间（WorkBuddy 项目 / 会话）。调用前先确认本环境能做什么、不能做什么，避免越权写文件或跑脚本。

- **配置文件路径**：`<workspace>/.workbuddy/auto.config.json`（`workspace` = 当前工作空间根；若该路径不可写，回退 `~/.agent/skill/auto/auto.config.json`）。
- **加载逻辑**：文件存在 → 读取 `permissions` 等字段；不存在 → 创建**默认配置**（如下）并保存。「默认权限提示：auto.config 需保存」即指此——每次调用结束（或权限 / 状态变更）后，须将最新状态写回该文件。
- **默认权限（只读优先，安全兜底）**：

  ```json
  {
    "permissions": { "read": true, "write_workspace": false, "execute": false, "web": true, "mcp_auto": true },
    "skillId": "auto",
    "last_theme": null,
    "solved_themes": [],
    "created_at": "<ISO>",
    "updated_at": "<ISO>"
  }
  ```

- **行为约束**：
  - `write_workspace=false` 时，不在工作空间落盘产物，除非用户当场授权；
  - `execute=false` 时，不跑 `Bash` / 脚本，除非用户当场授权；
  - `web=true` / `mcp_auto=true` 允许联网检索与调用 `mcp.auto`。

## 从 mcp.auto 获取执行步骤（进入已有支付流程）

`mcp.auto/theme` 是 AUTO 的知识面入口，工具契约见 `references/auto-theme.json`，总入口 `references/mcp.json`。

- 频道解析：按 `activity.content == theme` 精确匹配；无则自动建 auto 频道（`type='ai'`, `fee=990`）。
- 步骤即 `schedule` 集合：频道内行程 = `schedule` 表，`auto` 云对象按 `create_time desc` 返回（`schedule` 无 likes 字段，退化为时间序）。每条 `schedule` 即一条「执行步骤」（`content` 为步骤文本，可附 `price` / `images`）。
- 付费解锁（支付子级）：付费频道（¥9.9 / 990 分）解锁后可读全部步骤。付费经微信支付 Agent Pay X402 协议触发，返回 `WeixinPay-Required` 支付码，由调用方代理用户支付授权。

> **⚠️ 鉴权模型（无 API Key）**
> auto **不需要 X-API-Key**。调用方持有「订单凭证」即视为合法——凭证 = `order._id` + `order.secret`：
> - `order._id` 是订单主键；`order.secret` 在**生成订单时一次性写入** `order.secret`（36 位十六进制），与 `order._id` 配对回传解锁。
> - 请求带 `order_id`（参数或 `X-Order-Id` 头）+ `secret`（参数或 `X-Auto-Secret` 头）→ 云对象按 `order._id + order.secret` 回查 `module=='auto' && pay==true` 即解锁。
> - 无凭证或凭证无效/未付 → 走付费流程（返回 402）。

> **🔒 隐私红线（仅约束 Agent/MCP 面）**：步骤列表的 **Agent/MCP 面**（`get_auto_theme` / 云对象 `queryTopLiked()`）**不返回联系方式类字段**（`contact` / `phone` / `mobile` / `wechat` / `wxid`），仅展示 `content` / `price` / `images` / `create_time` 等非隐私信息；过滤以 `.field()` 投影实现。

## 回写步骤到 mcp.auto（主题ID关联 · 已实现）

任务经【兜底】解决后，把本次形成的执行步骤写回 `mcp.auto`，与主题ID绑定，使下次同主题直接走第 3 步命中缓存、无需再兜底。回写入口 `save_auto_steps`（`POST /auto/save`）**已实现**，且为**写操作、同样需已支付凭证**（与 `theme()` 对称）：

- **关联键**：主题 → `activity` 频道（`content==theme`），频道 `_id` 即主题ID；步骤写入该频道的 `schedule` 集合（与 `mcp.auto/theme` 读取同源）。
- **已带有效已付凭证（`order_id` + `secret`）** → 直接把 `steps[]` 批量写入该频道 `schedule`，并返回 `saved` 条数 + **回传支付配置（`order_id` / `secret`）**，确认凭证有效。
- **无凭证 / 凭证无效未付** → 回传 **HTTP 402 支付表单**（`WeixinPay-Required` 头 + body `order_id` + `secret`）并**直接拒绝，不写**；调用方代理支付后携凭证重试 `save` 即写入。
- **步骤格式**：每条 `step = { content(必填), type?, order?, price?, images? }`，`content` 为可执行结论 / 命令 / 要点的文本；可附 `price` / `images` 等既有 `schedule` 字段。
- 完整契约见 `references/auto-writeback.json`（status: implemented）。云端 `auto.save()` 已实现，需 URL化 `/auto/save` + SkillHub 注册 `skillId:'auto'` 后线上生效。

## 📌 凭证管理（SKILL 提示词 · 调用方必须遵循）

auto 的付费凭证 = **`order_id` + `secret`**（订单密钥，生成订单时一次性写入 `order.secret`）。**凭证的持久化位置固定为 `~/.agent/skill/auto/config.json`**，这段以 SKILL 提示词形式存在，不塞进接口返回体（接口 `prompt` 仅回状态）。

**1. 收到 402（付费闸）时**，响应体同时回显 `order_id` 与 `secret`。**代理支付成功后**，必须把二者写入固定位置：

```json
// ~/.agent/skill/auto/config.json
{
  "order_id": "<402 响应体的 order_id>",
  "secret": "<402 响应体的 secret>"
}
```

> 若该文件已存在，覆盖更新（同一客户端只保留最新一笔 auto 解锁凭证）。

**2. 下次同主题调用时**，先读取 `~/.agent/skill/auto/config.json`；若已存在，直接带上凭证重试主题检索：

- `order_id` → 请求体参数 `order_id` **或** 请求头 `X-Order-Id`
- `secret` → 请求体参数 `secret` **或** 请求头 `X-Auto-Secret`

云对象按 `order._id + order.secret` 回查 `pay==true` 即直返已付步骤，**无需重复付费**。

**3. `secret` 所有权密钥**：务必与 `order_id` 配对保存、配对回传；仅持 `order_id` 无 `secret` 也可解锁（兼容旧流程），但配对更严谨、防冒用。

**4. X402 重试头 `X-Out-Trade-No`** 仍用 `payment_code`（= `WeixinPay-Required` 的值），供 SkillHub 平台验签（与 huoli 一致），与上面的 `order_id/secret` 凭证是两回事。

---

## Usage

### 步骤 1 — 主题检索（付费闸）

```
POST /auto/theme  { theme: "火锅探店", page?, pageSize? }
```

- 免费频道（理论上不会，auto 频道固定 fee=990）→ 直接返回步骤。
- 付费频道且未带有效凭证 → 返回 HTTP 402（集成响应）+ `WeixinPay-Required` 头 + body 含 `order_id` + `secret` 凭证。

```json
{
  "mpserverlessComposedResponse": true,
  "statusCode": 402,
  "headers": {
    "content-type": "application/json",
    "WeixinPay-Required": "<payment_code>"
  },
  "body": "{\"errCode\":402,\"pay_required\":true,\"unlocked\":false,\"order_id\":\"<order._id>\",\"secret\":\"<order.secret>\",\"out_trade_no\":\"<payment_code>\",\"amount\":990,\"currency\":\"CNY\",\"prompt\":\"pay_required\"}"
}
```

> `prompt` 仅回状态（`pay_required` / `unlocked`），**不含任何凭证存储指引**——指引见上方「凭证管理（SKILL 提示词）」。

### 步骤 2 — 代理支付 + 存凭证 + 重试解锁

调用方将 `WeixinPay-Required` 的值作为 `paymentCode` 交给微信支付 Agent（`weixinpay_pay`），由 Agent 向用户申请支付授权。**支付成功后：**

1. 把 402 响应体的 `order_id` + `secret` 写入 `~/.agent/skill/auto/config.json`（见上方提示词）。
2. 携 `order_id` + `secret` 重试，云对象按 `order._id + order.secret` 回查 `pay==true` 即返回已付步骤。

```js
const res = await fetch('https://mcp.fore.vip/auto/theme', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Order-Id': '<order_id>',     // auto 凭证①（也可放 body.order_id 参数）
    'X-Auto-Secret': '<secret>'     // auto 凭证②（也可放 body.secret 参数）
  },
  body: JSON.stringify({ theme: '火锅探店' })
})
// → { errCode:0, unlocked:true, list:[...], total:N }
```

> 注意：若频道已有未支付单，`auto` 会复用该单（避免刷出孤儿单）；若传入 `order_id` 无效/已付/密钥不符，忽略并重建。

### 前端直付（小程序 / H5，预留）

前端页面可走 `payChannel()` 直接拿微信 Native `code_url` 扫码付，**不经 X402**（X402 仅对 MCP / Agent 调用方生效）：

```js
// 云对象方法：auto.payChannel({ theme }) → { errCode: 0, unlocked: false, orderId, secret, codeUrl, amount: 990 }
const r = await uniCloud.importObject('auto').payChannel({ theme: '火锅探店' })
// r.codeUrl → vk-uni-qrcode 展示扫码付 → 轮询 order.pay 自动解锁（前端可把 r.orderId + r.secret 持久化）
```

## Configuration

| 项 | 说明 |
|----|------|
| `auto.config` 路径 | `<workspace>/.workbuddy/auto.config.json`（不可写则回退 `~/.agent/skill/auto/auto.config.json`）；记录 `permissions` / `skillId` / `last_theme` / `solved_themes`，每次调用结束须保存。 |
| 默认权限 | `read:true, write_workspace:false, execute:false, web:true, mcp_auto:true`（只读优先，写/执行需用户当场授权）。 |
| 鉴权 | **无 X-API-Key**。凭证 = `order._id` + `order.secret`（生成订单时写入 order.secret）。 |
| `order_id` / `X-Order-Id` | auto 凭证①：支付成功重试带回；云对象按 `order._id` 回查 `module=='auto' && pay==true` 解锁。 |
| `secret` / `X-Auto-Secret` | auto 凭证②：订单密钥，与 `order._id` 配对回传解锁（生成订单时写入 order.secret）。 |
| 凭证持久化路径 | **固定** `~/.agent/skill/auto/config.json`，内容为 `{ "order_id", "secret" }`（见「凭证管理」提示词）。 |
| `X-Out-Trade-No` | SkillHub A2M 标准重试头，值=preorder 返回的 `payment_code`；供平台验签（与 huoli 一致）。 |
| `activity.type` | auto 频道来源分类复用此字段（写 `'ai'`），**不另加 `auto_channel` 之类布尔标记**（冗余）。fee=990 触发 pay_required。 |
| `order.type=6` | auto 解锁订单固定值；`oid`=频道 ID，`price`=990（分），`module`='auto'，`secret`=订单密钥。 |
| `createNativePay` amount | ¥9.9 = 990 分，与 order.price 一致。 |
| 回写端点 | `POST /auto/save`（契约 `references/auto-writeback.json`）**已实现**；写操作需已付凭证，无/无效→402 拒绝不写。 |

精确字段定义一律读 `references/mcp.json`、`references/auto-theme.json`、`references/auto-writeback.json`，不要凭记忆。

## Examples

**例 1：主题已有沉淀（直接命中）**

```
POST /auto/theme  { theme: "周末露营" }
→ 频道存在且已付费凭证有效 → { errCode:0, unlocked:true, list:[...执行步骤], total:N }
```

**例 2：主题无沉淀 → 付费闸 → 代理支付 → 重试**

```
POST /auto/theme  { theme: "周末露营" }
→ 无 "周末露营" 频道 → 自动建 activity 频道(type='ai', fee=990)
→ 返回 HTTP 402 + WeixinPay-Required(payment_code) + body.order_id + body.secret
→ 交 weixinpay_pay 代理支付（paymentCode = WeixinPay-Required）
→ 写 ~/.agent/skill/auto/config.json = { "order_id": "...", "secret": "..." }
→ 再次 POST /auto/theme { theme:"周末露营" } + X-Order-Id:<order_id> + X-Auto-Secret:<secret>
→ { errCode:0, unlocked:true, list:[...执行步骤], total:N }
```

**例 3：mcp.auto 无结果 → 兜底检索 + 回写（已付用户直接写）**

```
用户：「火锅探店主题怎么落地」（已持有该主题已付凭证 order_id+secret）
→ mcp.auto/theme 返回空 / 不可达（无沉淀）
→ 兜底：技能市场检索「本地生活探店」相关技能 → 无；社区/开源检索最优质探店执行清单 → 逐步执行
→ 解决后 POST /auto/save { theme:"火锅探店", steps:[...], order_id, secret }
→ 已付凭证有效 → { errCode:0, saved:N, order_id, secret(回传支付配置) }（写入该频道 schedule）
→ 交付步骤 + 告知下次同主题直接命中缓存

（若无支付配置 → /auto/save 回传 402 表单直接拒绝，不写；代理支付后携凭证重试即写入）
```

## Requirements

- **auto 专属 MCP 服务端**：`https://mcp.fore.vip/auto/theme`（付费闸）+ `https://mcp.fore.vip/auto/save`（**回写，已实现**）+ `https://mcp.fore.vip/http/uni-skill-pay-notify`（支付回调，与 huoli 共用）。
- **微信支付 V3 凭证**：`uni-config-center/uni-skill-pay/config.json` 的 `wxpayV3` 段。
- **SkillHub 开发者凭证**：同 `config.json` 的 `skillhub` 段（`x402Preorder` 调用时显式传 `skillId:'auto'`）。
- **依赖云对象**：`auto`（theme / payChannel / **save 已实现**）、`uni-skill-pay-notify`（回调验签 + AES-256-GCM 解密置单）；通用底座 `uni-skill-pay`（common 共享模块）。
- **前端页面**：暂未建（auto 定位 Agent/MCP）；`payChannel()` 方法已预留。
- **回写部署（用户侧，使 /auto/save 线上生效）**：`auto.save()` 云端方法已实现，需补 ① HBuilderX 将 `auto/save` URL化 为 `https://mcp.fore.vip/auto/save`；② SkillHub 注册 `skillId:'auto'`（否则 X402/写权限受限，同 huoli 入驻事项）。

## Troubleshooting

| 现象 | 原因 | 处理 |
|------|------|------|
| `402 + WeixinPay-Required` | 付费频道未解锁（X402 目标态；当前因 skillId auto 未入驻返回 PAY_NOT_READY） | 按「凭证管理」提示词交 `weixinpay_pay` 代理支付，存 `~/.agent/skill/auto/config.json`，再带 `X-Order-Id`+`X-Auto-Secret` 重请求 |
| `402 + blocked: true + PAY_NOT_READY` | X402 预下单端点故障（`payapp.weixin.qq.com/.../preorder` 被微信网关 302 拦截；**非** V3 凭证问题） | auto 的 skillId 未在 SkillHub 后台注册+绑商户（302 根因）；属平台侧事项，入驻后即闭环；C 端直付（payChannel）不受影响 |
| `Missing theme` | 未传主题 | 必填 `theme` |
| 解锁后仍返回 402 | `order_id`/`secret` 订单校验失败 | 确认 `order._id == X-Order-Id && order.secret == X-Auto-Secret && module=='auto' && pay==true`；密钥不符会被拒绝 |
| mcp.auto 返回空 / 不可达 | 该主题无沉淀或云端异常 | 进入【兜底】检索+执行；解决后尝试回写（降级展示） |
| `POST /auto/save` 返回 402 + WeixinPay-Required | 回写为写操作，需已支付凭证；无凭证/凭证无效未付被拒 | 代理支付（同 theme 流程）后携 `order_id`+`secret` 重试 `save` 即写入；已付用户直接写并回传支付配置 |
| `POST /auto/save` 返回 402 + blocked: true + PAY_NOT_READY | X402 预下单端点故障（同 theme 的 PAY_NOT_READY 根因） | 需 SkillHub 后台注册 `skillId auto` 并绑定商户；C 端直付不受影响 |

## References

| 项 | 路径 / 链接 |
|----|-------------|
| 工具契约总入口 | `references/mcp.json` |
| └ auto 主题获取（专属） | `references/auto-theme.json` |
| └ auto 步骤回写（已实现） | `references/auto-writeback.json` |
| 外部 client 配置 | `mcp-standard.json`（根） |
| MCP 服务地址 | `https://mcp.fore.vip` |
| 部署与联调 | `doc/HUOLI_DEPLOY.md`（auto 复用同套支付部署） |
| SkillHub Pay Skill 范式 | `https://skillhub.cn/tutorials#agent-pay-upgrade` |

## Changelog

### 1.1.0

- **角色重定义为顶级执行技能**：AUTO 从「主题精选行程检索」升级为「主题 → 最优秀执行步骤」的编排执行体——先向 `mcp.auto` 取步骤，无结果则兜底检索技能市场/社区/开源/搜索逐步执行，解决后回写 `mcp.auto`（主题ID关联）。
- **新增工作空间权限与 auto.config**：调用前读取工作空间权限，维护 `<workspace>/.workbuddy/auto.config.json`（不可写回退 `~/.agent/skill/auto/auto.config.json`），默认 `read:true, write_workspace:false, execute:false, web:true, mcp_auto:true`，写/执行需用户当场授权；每次调用结束须保存。
- **明确进入已有支付流程**：获取步骤仍走 `mcp.auto/theme` 的 ¥9.9 付费闸 + 凭证（`order._id`+`secret`）模型，不另行定义支付。
- **新增回写契约（已实现）**：`references/auto-writeback.json` 定义 `save_auto_steps`（`POST /auto/save`，body `{theme, steps[]}` → 落到对应频道 `schedule`）；云端方法 `auto.save()` 已实现，写操作需已付凭证，无/无效→402 拒绝不写。
- 触发词对齐新角色（「XX主题的执行步骤 / 最优质方案 / 怎么落地」等），保留负触发（非主题检索类活动查询）。

### 1.0.1

- **去 API Key 鉴权**：auto 不需要 X-API-Key，凭证即订单 = `order._id` + `order.secret`（生成订单时一次性写入 `order.secret`）；移除 `verifyApiKey`/`STATIC_API_KEY` 及 403 网关。
- **加订单密钥 `secret`**：`order` schema 新增 `secret` 字段；生成 auto 订单时 `genSecret()` 写入；重试经 `secret`/`X-Auto-Secret` 配对校验解锁，`order._id` 单凭证仍兼容。
- **prompt 只回状态**：402 响应体 `prompt` 改为 `'pay_required'`（状态串），凭证存储/重试指引从响应体抽出，改为「凭证管理（SKILL 提示词）」章节，**固定持久化路径 `~/.agent/skill/auto/config.json`**（`{order_id, secret}`）。
- **复用 type 字段、去冗余标记**：`activity.add` 不再写 `auto_channel:true`，来源分类复用既有 `type:'ai'`，避免 `*_channel` 冗余布尔字段。

### 1.0.0

- 初版：auto 云对象 `theme()`（主题→频道解析/自动建频道 + 精选行程 + ¥9.9 付费闸）+ `payChannel()`（前端直付预留）。
- 复用通用支付底座 `uni-skill-pay`（`createNativePay` / `x402Preorder` / `verifyWechatSignature` / `decryptResource`）与 `uni-skill-pay-notify` 回调；订单 `type=6, module='auto', price=990`。
- 凭证模型 = `order._id`：402 响应体回显 `order_id`，提示词要求 Agent 存到固定位置、携其重试解锁；X402 重试头 `X-Out-Trade-No` 仍用 `payment_code`。
- 主题无频道时 `auto` 云对象直接 `activity.add` 最小频道（content=主题, fee=990）。
- 列表按 `create_time desc` 排序（schedule 无 likes 字段，退化为时间序）。
- 隐私红线：列表 `.field()` 过滤 contact/phone/mobile/wechat/wxid（Agent/MCP 面）。
- 402 以集成响应模式（`mpserverlessComposedResponse:true` + `statusCode:402` + `WeixinPay-Required` 头）返回，对齐 SkillHub A2M。
