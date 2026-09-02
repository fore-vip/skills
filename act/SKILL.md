---
name: act
description: 活动发现与创建 MCP 工具集。当用户需要让 Agent 搜索活动、查看活动详情、创建活动（含付费定价）、或查询活动行程时使用。活动创建需 X-API-Key 鉴权，支持原子级多轮收集与自动化批量两种模式；付费活动经 create_activity 传 fee（分）自动标记并接入 H5 支付。
agent_created: true
---

# act — 活动发现与创建（MCP Tool）

通用 Agent 技能，通过 MCP 后端 `https://mcp.fore.vip` 提供活动搜索、详情、创建、行程查询能力。后端实现（URL 化云对象风格，非 JSON-RPC）。

## 何时使用

- 用户要"创建 / 发布活动"（含付费活动定价）
- 用户要"搜附近 / 深圳的活动"、"看某活动详情"、"某活动有哪些行程"

## 工具清单

精确字段定义（inputSchema / outputSchema / 错误码）一律读 `references/mcp.json`，需要精确字段时再读取，不要凭记忆。

| 工具 | 端点 | 鉴权 | 说明 |
|------|------|------|------|
| `search_activities` | `POST /act/search` | 无 | 距离 / 热度双模式搜索 |
| `get_activity_detail` | `POST /act/detail` | 无 | 详情 + view_count 自增 |
| `create_activity` | `POST /act/create` | `X-API-Key` | 创建活动（支持 fee 付费） |
| `list_activity_schedules` | `POST /act/schedules` | 无 | 按 activity_id 查行程列表 |

## 模式 1：原子级创建（多轮收集 → 单次调用）

触发："帮我创建一个活动"。逐轮收集所有必填信息，确认后才调用 MCP。流程不可跳步：

1. **API Key** — 第一件事就问。不存不记，每轮创建都重问；返回 403 则中止。
2. **封面图片** — 必填。用户发图用图链、发链接直接用；无图必须拒绝，不能跳过。
3. **活动主题** — ≤500 字；同时确认标签（最多 10 个）。
4. **地址** — ≤128 字。
5. **经纬坐标** — 自动 `web_search` 解析地址经纬度，展示请用户确认。GeoJSON 标准 `[lng, lat]`（经度在前）。
6. **开始 / 结束时间** — 自然语言转 Unix ms 时间戳；不确定结束设 `null`。

收集完总结确认，**用户确认后只调一次** `create_activity`：

```js
create_activity({
  content: "周末梧桐山徒步",
  address: "深圳梧桐山国家森林公园",
  cover: "https://...",           // 必填，后端自动转存云存储
  tags: ["徒步", "周末", "户外"],
  latitude: 22.581, longitude: 114.196,
  start_time: 1750352400000,
  max_participants: 0,
  fee: 990                        // 可选，单位：分（9.9 元），默认 0=免费
})
```

- 成功：展示主题 + 返回链接 `url` + 封面 + 地图 + 时间范围。
- 失败：403→"Key 无效"；-1→告知哪个字段问题；-3→"封面下载失败，换一张"。

## 模式 2：批量创建（搜索 → 生成 → 循环）

触发："批量搜深圳活动并发布"。流程不可跳步：

1. 确认 API Key（403 中止）。
2. `web_search` 分 3 维度搜未来活动（只创建真实存在、信息明确的，禁止编造），至少 3 个候选。
3. 为每个活动搜封面图（提取可公网访问 URL，无则跳过并提示）。
4. 解析各活动地址经纬度。
5. **逐条、顺序**调用 `create_activity`（等上一条返回再调下一条），每创建完一条汇报进度，全部完成后输出成功 / 失败汇总。

## 关键约束（易错点）

- **时间戳**：`start_time` / `end_time` 均为 **Unix 毫秒（13 位）**，非秒。
- **坐标**：GeoJSON `[lng, lat]`（经度在前），与多数地图 SDK `[lat, lng]` 相反。
- **`create_activity` 鉴权**：每次 Header 带 `X-API-Key`，不缓存、不存储，每轮重问。
- **`get_activity_detail` 副作用**：调用即自增 `view_count`，勿为同一活动重复调用。
- **付费活动**：`create_activity` 可选 `fee`（单位：分，100=1 元）。`fee>0` → 后端自动标 `pay_required=true`，H5 详情页展示「¥X 加入」拉起支付，链路与小程序创建一致。省略 / 0 = 免费。**校验规则**：默认 0（免费）；仅当传入非 0 值时做非负校验，负值或非法值忽略并回退为 0。
- **行程不联表 guest**：`list_activity_schedules` 返 `guest_id`（uni-id-users._id 字符串）但不返昵称 / 头像，需展示自行查 user 表。
- **分页**：`pageSize` 上限 50，默认 10；超过截断到 50。
- **空行程**：新活动 `list=[]`、`total:0` 属正常，提示"该活动暂无行程"。

## 安装

```bash
npx skills add fore-vip/skills --skill act
```

外部 MCP client（Claude Desktop / Cursor 等）可直接用仓库根 `mcp-standard.json`（声明 `https://mcp.fore.vip/act/mcp`）接入，无需经 skills 机制。

## 引用

| 项 | 路径 / 链接 |
|----|-------------|
| 工具契约（字段级） | `references/mcp.json` |
| 外部 client 配置 | `mcp-standard.json`（根） |
| MCP 服务地址 | `https://mcp.fore.vip` |
| 活动详情页（H5） | `https://fore.vip/pages/activity/detail?id={_id}` |
