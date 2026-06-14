# act

活动搜索与查询服务。通过 HTTP 调用 `mcp.fore.vip` 获取活动数据。

## 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `https://mcp.fore.vip/tools/list` | POST | 工具清单 |
| `https://mcp.fore.vip/act/search` | POST | 搜索活动 |
| `https://mcp.fore.vip/act/detail` | POST | 活动详情 |

## 使用方式

Agent 直接 POST JSON 到对应端点即可，无需鉴权。

## 活动数据字段

返回的活动对象字段名与 DB 一致（未做映射）：
- `_id` / `content` / `address` / `cover` / `type`
- `start_time` / `end_time` (ms 时间戳)
- `location.coordinates` [lng, lat]
- `participant_count` / `view_count` / `tags` / `status`
- `creator_name` / `create_time`
