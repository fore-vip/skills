# act — 活动发现与创建

> 通用 Agent SKILL · v2.1.0 · MCP Tool
>
> 安装后 Agent 可搜索活动、查看详情、创建活动。
>
> **MCP 后端：** `https://mcp.fore.vip` · **区域：** 深圳 (CN-SZ)

---

## 功能矩阵

| 工具 | 端点 | 鉴权 | 说明 |
|------|------|------|------|
| `search_activities` | `POST /act/search` | 无 | 搜索活动：距离/热度双模式 |
| `get_activity_detail` | `POST /act/detail` | 无 | 查详情 + 浏览量自增 |
| `create_activity` | `POST /act/create` | `X-API-Key` | 创建新活动 |

## 安装

```bash
npx skills add fore-vip/act
```

---

## create_activity — 创建活动

> 系统自动填充：`open=1`（公开）、`type="ai"`（AI 创建）、`create_time`/`update_time`

```
POST https://mcp.fore.vip/act/create
Content-Type: application/json
X-API-Key: {key}

{
  "content": "周末爬山",           // 必填 ≤500字
  "address": "深圳梧桐山",          // 必填 ≤128字
  "cover": "https://example.com/pic.jpg",  // 必填，自动转存至云存储
  "tags": ["徒步", "周末"],         // 可选，最多10个
  "latitude": 22.543,              // 可选，与 longitude 生成位置
  "longitude": 114.058,
  "start_time": 1718000000000,     // 可选 ms时间戳
  "end_time": 1718100000000,       // 可选
  "max_participants": 20,          // 可选，默认0=不限
  "creator_name": "小明"            // 可选
}
```

创建成功返回完整活动对象（含 `_id`，`cover` 为云存储 URL）。

## search_activities — 搜索活动

```
POST https://mcp.fore.vip/act/search
{ keyword, type, latitude, longitude, page, pageSize }
```

排序：有经纬度→距离 ASC；无→热度 DESC。

## get_activity_detail — 活动详情

```
POST https://mcp.fore.vip/act/detail
{ id: "6a0a..." }
```

返回完整活动文档。

## 错误码

| 场景 | errCode | 说明 |
|------|---------|------|
| 创建缺 Key | 403 | Header 未带 X-API-Key |
| 字段缺失/超长 | -1 | content/address/cover 必填 |
| 封面转存失败 | -3 | 下载/上传失败，活动不创建 |
| DB 失败 | -2 | 数据库写入异常 |
| ID 缺失 | -1 | detail 缺少 id |
| 搜索无结果 | — | list=[], text 含提示 |

## 使用示例

| 用户说 | Agent 调用 |
|--------|-----------|
| "创建一个周末爬山的活动" | `create_activity({ content, address, cover, tags })` |
| "附近的爬山活动" | `search_activities({ keyword:"爬山", latitude, longitude })` |
| "这个活动详情" | `get_activity_detail({ id })` |
