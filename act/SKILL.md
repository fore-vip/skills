# act — 活动发现与查询

> 通用 Agent SKILL · v2.0.1 · MCP Tool
>
> 安装后 Agent 直接调用 MCP 搜索活动、查看详情。
>
> **MCP 后端：** `https://mcp.fore.vip` · **区域：** 深圳 (CN-SZ)

---

## 功能矩阵

| 工具 | 端点 | 说明 |
|------|------|------|
| `search_activities` | `POST /act/search` | 搜索活动：距离/热度双模式、关键词、类型筛选 |
| `get_activity_detail` | `POST /act/detail` | 查详情：完整文档 + 浏览量自增 |

## 安装

```bash
npx skills add fore-vip/act
```

或在 OpenClaw 聊天中说：`安装 act 技能`

---

## 工具详细

### search_activities

```http
POST https://mcp.fore.vip/act/search
Content-Type: application/json

{
  "keyword": "爬山",        // optional — 匹配 content + address
  "type": "sport",          // optional — sport|culture|volunteer|other
  "latitude": 22.543,       // optional — 触发 geoNear
  "longitude": 114.058,     // optional — 需配合 latitude
  "page": 1,                // optional — 默认 1
  "pageSize": 10            // optional — 默认 10，上限 50
}
```

**排序逻辑：**

| 条件 | 排序 | 方法 |
|------|------|------|
| 有经纬度 ± 过滤 | 距离 ASC | `aggregate().geoNear()` |
| 无经纬度 ± 过滤 | 热度 DESC | `orderBy('view_count', 'desc')` |

**返回：**

成功时返回 `{ text, list, total, page, pageSize }`：

- `text` — 自然语言摘要，可直接语音播报
- `list` — 结构化数据，含 `_id/content/address/distance/tags/type/cover/view_count/participant_count/creator_name`
- `total` — 匹配总条数，非当前页条数

结果为空时 `text` 输出提示语，`list` 为空数组 `[]`。

### get_activity_detail

```http
POST https://mcp.fore.vip/act/detail
Content-Type: application/json

{ "id": "6a0a872089bd27bae34e5502" }
```

返回完整 activity 文档对象。调用后异步自增 `view_count`（fire-and-forget）。

## 错误处理

| 状态 | 表现 | 处理 |
|------|------|------|
| 搜索无结果 | `text` 含"没有找到"提示，`list: []` | 正常返回，建议扩大范围 |
| 无经纬度时传经纬度 | 静默自动切到热度模式 | 无需干预 |
| 非法参数类型 | 静默降级忽略 | 不影响正常查询 |
| 缺少 `id` 参数 | 返回 -1 | 提示用户提供活动ID |
| `_id` 不存在 | 返回 -1 | 提示用户活动可能已删除 |

## 搜索行为说明

- **关键词匹配：** 仅对 `content` 和 `address` 做模糊正则匹配，`tags` 数组因 JQL 限制不做匹配
- **类型筛选：** 枚举值 `sport/culture/volunteer/other`，仅当数据库有该类型数据时有结果
- **经纬度：** 缺一则不做 geoNear，不会降级用单坐标

## 使用示例

| 用户说 | Agent 调用 |
|--------|-----------|
| "附近的爬山活动" | `search_activities({ keyword:"爬山", latitude, longitude })` |
| "有什么好玩的" | `search_activities({ pageSize:5 })` |
| "文化类的活动" | `search_activities({ type:"culture" })` |
| "这个活动详情" | `get_activity_detail({ id:"6a0a..." })` |
| "帮我搜深圳的骑行" | `search_activities({ keyword:"骑行", latitude:22.543, longitude:114.058 })` |
