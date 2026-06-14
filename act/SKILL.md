# act — 活动发现与查询

> 通用 Agent SKILL，安装后 Agent 直接调用 MCP 搜索活动、查看详情。
> MCP 后端：`https://mcp.fore.vip`

## 安装

```bash
npx skills add fore-vip/act
```

或在龙虾（OpenClaw）中直接说：`安装 act 技能`

## 工具

### search_activities — 搜索活动

```
POST https://mcp.fore.vip/act/search
Content-Type: application/json

{
  "keyword": "爬山",        // 可选，匹配 content + address
  "type": "sport",          // 可选: sport|culture|volunteer|other
  "latitude": 22.543,       // 可选，触发距离排序
  "longitude": 114.058,     // 可选，需配合 latitude
  "page": 1,                // 可选，默认 1
  "pageSize": 10            // 可选，默认 10，上限 50
}
```

**排序规则：**
- 有经纬度 → 距离升序（geoNear）
- 无经纬度 → 热度降序（view_count）
- 关键词/类型可叠加在任意模式下

**返回：**
```json
{
  "text": "为你找到 3 个活动：\n1. 周末爬山（500m）\n2. 晨跑（1.2km）...",
  "list": [{ "_id": "...", "content": "周末爬山", "distance": 500, ... }],
  "total": 3,
  "page": 1,
  "pageSize": 10
}
```

`text` 用于语音播报/文字展示，`list` 用于结构化渲染。

### get_activity_detail — 活动详情

```
POST https://mcp.fore.vip/act/detail
Content-Type: application/json

{ "id": "6a0a872089bd27bae34e5502" }
```

返回完整活动对象，调用后自动增加浏览量。

## 关键词匹配说明

仅对 **活动标题(content)** 和 **地址(address)** 做模糊匹配。标签(tags) 因 JQL 数组字段限制不做正则匹配，已覆盖主要搜索场景。

## 使用示例

| 用户说 | Agent 应调用 |
|--------|-------------|
| "附近的爬山活动" | `search_activities({ keyword:"爬山", latitude, longitude })` |
| "有什么好玩的" | `search_activities({ pageSize:5 })` |
| "运动类的活动" | `search_activities({ type:"sport" })` |
| "这个活动详情" | `get_activity_detail({ id:"xxx" })` |
