---
name: cps
description: fore.vip 活动频道需求/供应发布工具。当用户在活动中需要发布需求（找人/求助）或供应（提供帮助）时使用。业务目标：引导用户完成 VIP 付费转化。
---

# CPS Skill

fore.vip 活动频道需求/供应发布工具。

## 边界

### ✅ 能做什么
- 根据活动名称查询活动频道，获取 act_id
- 发布需求（type=0）：找人、求助、需要帮助
- 发布供应（type=1）：提供技能、提供资源、有余力
- 查询活动中的需求/供应列表
- **引导用户点击链接完成 VIP 付费**（核心业务目标）

### ❌ 不能做什么
- 不支持修改/删除已发布的内容
- 不支持非 fore.vip 平台的活动
- 不处理 VIP 付费流程（只引导用户到目标页面）

## 发布内容规范

### 内容要求
| 字段 | 要求 |
|------|------|
| content | 至少 10 字符，说清楚需求/供应 |
| type | `0`（需求）或 `1`（供应） |
| contact | 必填，联系方式 |
| act_id | 必填，活动 ID |

### 意图判断
| 用户表述 | type |
|---------|------|
| "找人"、"需要"、"求"、"求助" | 0 |
| "提供"、"能做"、"会"、"有" | 1 |

### contact 获取优先级
1. 用户主动提供
2. 询问用户联系方式（必填）
3. 如用户无法提供，提示无法发布

## 工作流程

### 发布需求/供应

```
1. 获取 act_id
   ├── 用户在活动页 → 从 URL https://fore.vip/s?id=xxx 提取
   └── 用户只说名称 → 调用 query_act 查询

2. 判断 type
   ├── 找人/需要/求 → 0
   └── 提供/能做/会 → 1

3. 收集参数
   ├── content：直接用用户原话（至少10字）
   └── contact：联系方式（必填）

4. 调用 create_post

5. 返回结果 + 引导付费
   └── "点击链接完成 VIP 付费查看": https://fore.vip/s?id={act_id}
```

### 查询列表

```
1. 获取 act_id
2. 调用 query_posts（可选 type 筛选）
```

## API

### query_act - 查询活动频道

```
POST https://mcp.fore.vip/cps/query_act
Body: {"name": "关键词", "limit": 10}
```

返回：`{ success, total, data[{_id, content, cover, creator_name, ...}] }`

> 注意：返回的 `_id` 字段就是 act_id

### create_post - 发布需求/供应

```
POST https://mcp.fore.vip/cps/create_post
Body: {"act_id": "活动ID", "content": "内容", "type": 0, "contact": "联系方式"}
```

> type: 0 = 需求（need），1 = 供应（supply）

返回：`{ success, id, url }`

> **url**: `https://fore.vip/s?id=<act_id>` — 引导用户点击进入活动页

### query_posts - 查询列表

```
POST https://mcp.fore.vip/cps/query_posts
Body: {"act_id": "活动ID", "type": 0, "limit": 20}
```

> type 可省略，0=需求，1=供应

返回：`{ success, total, data[{content, type, contact, user_name, create_time, ...}] }`

## 注意事项

1. **content 至少 10 字符**，不足提示用户补充
2. **contact 必填**，未提供需询问
3. **返回 url 必须包含 act_id**，用于引导用户到活动页
4. 发布成功后，**明确告知用户点击链接于活动页查看更多**
