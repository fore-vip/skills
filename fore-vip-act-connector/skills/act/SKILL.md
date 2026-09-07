---
name: 火力打卡活动服务
description: 通过自然语言搜索附近活动、查看活动详情、创建或管理用户发起的本地生活活动（运动 / 文化 / 志愿等）。
---

# 火力打卡 · 活动服务（fore-vip-act）

本 Skill 指导 AI 正确使用 `fore-vip-act` MCP 连接器的 6 个工具。连接器后端为 `https://mcp.fore.vip/act/mcp`（火力打卡服务），已内置 OAuth 2.1 + PKCE 鉴权，WorkBuddy 内置 OAuth 管理器会自动完成授权，无需手动填 token。

## 何时使用

- 用户想「找 / 搜 / 发现」本地活动（运动、文化、志愿服务等），尤其是带位置或"附近"语义时。
- 用户想「看某个活动详情」。
- 用户想「创建一个活动」「发起一个局」「组个活动」。
- 用户想「改 / 更新 / 删」自己之前创建的活动。
- 用户想看「某个活动下的行程安排」。

## 工具清单

### 1. search_activities — 搜索活动
- 参数：`keyword`（可选）、`type`（`sport`/`culture`/`volunteer`/`other`）、`latitude`+`longitude`（触发距离排序）、`page`、`pageSize`
- 技巧：给了经纬度按"由近到远"排；不给则按热度（浏览数）排。关键词只匹配标题和地址。

### 2. get_activity_detail — 活动详情
- 参数：`id`（活动 _id，必填）
- 返回封面、地址、时间、参与人数、费用（`fee` 单位：分，100=1元，`pay_required` 为 true 时前端展示「¥X 加入」拉起支付）。

### 3. create_activity — 创建活动
- 必填：`content`（≤500 字）、`address`（≤128 字）、`cover`（封面图 URL，自动转存云存储）
- 可选：`tags`、`latitude`+`longitude`、`start_time`/`end_time`（ms 时间戳）、`max_participants`、`creator_name`、`fee`（分；>0 自动标记付费）
- 注意：调用需写权限（连接器 OAuth scope 含 `fore-vip.mcp`）；系统自动填充 `open=1`、`type=ai`。

### 4. list_activity_schedules — 活动行程列表
- 参数：`activity_id`（必填）、`page`、`pageSize`
- 按开始时间升序，返回该活动下的行程。

### 5. update_activity — 更新活动
- 必填：`id`；可选白名单字段：`content`/`address`/`cover`/`tags`/`start_time`/`end_time`/`latitude`+`longitude`
- 不可改：`creator`/`type`/`status`/`open`/`view_count`。至少提供一个待更新字段。

### 6. delete_activity — 删除活动
- 参数：`id`（必填）；仅允许删除本服务创建的 `type=ai` 活动，删除不可恢复。

## 错误与恢复

- `403 Invalid or missing X-API-Key` / 鉴权失败 → 引导用户在 WorkBuddy 内重新绑定连接器授权（重新走 OAuth）。
- `Activity not found` → id 有误或活动已删除，向用户确认。
- 创建时封面转存失败 → 换个可访问的封面图 URL 重试。

## 安全 / 权限

- 创建、更新、删除属于写操作，必须基于已授权的用户会话（连接器 OAuth 令牌）。
- 不要替用户编造活动 id；更新/删除前先 `get_activity_detail` 或 `list_activity_schedules` 确认目标。
