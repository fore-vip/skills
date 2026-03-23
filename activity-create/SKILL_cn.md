---
name: activity-create
description: 创建 前凌智选线下活动。用于创建包含时间、地点、门票信息的活动。
version: 0.0.3
license: MIT
---

## 说明

通过 MCP Server 为 前凌智选 (fore.vip) 平台创建线下活动。

---

## MCP 工具

**工具名称**: `create_activity`  
**服务器**: `fore-vip`  
**端点**: `https://api.fore.vip/tools`

---

## 参数

### 必需参数

| 参数 | 类型 | 说明 | 验证规则 | 示例 |
|------|------|------|----------|------|
| `content` | string | 活动介绍 | 最少 2 字符 | `"AI 周末聚会"` |
| `start_time` | number | 开始时间戳 (毫秒) | 有效时间戳 | `1711094400000` |
| `address` | string | 活动地址文本 | 非空 | `"北京三里屯"` |
| `wx` | string | 联系方式 (微信) | 非空 | `"forevip123"` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 | 示例 |
|------|------|--------|------|------|
| `kid` | string | 硬编码 | 关联机器人 ID (kl 集合 _id) | `"69bcdb49189f8658d9ad6dbf"` |
| `end_time` | number | - | 结束时间戳 (毫秒) | `1711108800000` |
| `location` | object | - | GeoJSON 坐标 | `{type:"Point",coordinates:[116.4,39.9]}` |
| `range` | number | `0` | 门票金额 (分，¥99 = 9900) | `9900` |
| `pay` | boolean | `false` | 是否付费活动 | `true` |
| `url` | string | - | 外部链接 URL | `"https://example.com"` |

> **注意**: 当前 `kid` 和 `user` 为硬编码测试数据，后续版本会更新。

---

## HTTP API 端点

### 获取工具列表

```bash
curl https://api.fore.vip/tools/list
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "tools": [{
      "name": "create_activity",
      "description": "Create offline event for fore.vip platform. Requires bot ID, event description, start/end time. Optional: location, ticket price, contact info.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "kid": {"type": "string", "description": "Associated bot ID (kl collection _id) - optional for test"},
          "content": {"type": "string", "description": "Event description (minimum 2 characters)"},
          "start_time": {"type": "number", "description": "Start timestamp in milliseconds (e.g., Date.now())"},
          "end_time": {"type": "number", "description": "End timestamp in milliseconds (must be after start_time)"},
          "address": {"type": "string", "description": "Event address text"},
          "location": {"type": "object", "description": "GeoJSON coordinates", "properties": {"type": {"type": "string", "enum": ["Point"]}, "coordinates": {"type": "array", "items": {"type": "number"}, "description": "[longitude, latitude]"}}},
          "range": {"type": "number", "description": "Ticket price in cents (e.g., 9900 = ¥99), default 0"},
          "url": {"type": "string", "description": "External link URL"},
          "wx": {"type": "string", "description": "Contact information (WeChat)"}
        },
        "required": ["content", "start_time", "address", "wx"]
      }
    }]
  }
}
```

### 调用工具

```bash
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "AI 周末聚会",
      "start_time": 1711094400000,
      "address": "北京三里屯",
      "wx": "forevip123",
      "end_time": 1711108800000,
      "range": 0,
      "pay": false
    }
  }'
```

**成功响应**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"success\": true,\n  \"id\": \"act_xxx\",\n  \"message\": \"Activity created successfully URL: https://fore.vip/st?id=act_xxx\"\n}"
    }],
    "isError": false
  }
}
```

**错误响应**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32602,
    "message": "Missing required parameter: name"
  }
}
```

---

## 使用示例

### JavaScript (Fetch API)

```javascript
// 创建活动
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'create_activity',
    arguments: {
      content: 'AI 体验日',
      start_time: Date.now() + 86400000,
      address: '北京三里屯',
      wx: 'forevip123',
      end_time: Date.now() + 90000000,
      range: 0,
      pay: false
    }
  })
})

const response = await result.json()

// 检查错误
if (response.error) {
  console.error('错误:', response.error.message)
} else {
  const data = JSON.parse(response.result.content[0].text)
  if (data.success) {
    console.log('创建成功:', data.id)
    console.log('活动 URL:', 'https://fore.vip/st?id=' + data.id)
  }
}
```

### uniCloud (云函数)

```javascript
const mcp = uniCloud.importObject('mcp')

// 创建活动
const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    content: 'VIP AI 见面会',
    start_time: 1711872000000,
    end_time: 1711958400000,
    address: '上海静安寺',
    location: { type: 'Point', coordinates: [121.44, 31.23] },
    wx: 'forevip123',
    range: 9900,
    pay: true
  }
})

if (result.error) {
  console.error(result.error.message)
} else {
  const data = JSON.parse(result.result.content[0].text)
  console.log('创建成功:', data.id)
  console.log('URL:', 'https://fore.vip/st?id=' + data.id)
}
```

---

## 错误代码

| 代码 | 错误 | 原因 | 解决方案 |
|------|------|------|----------|
| -32602 | `Missing required parameter: name` | 请求未提供 name | 在请求体中包含 `name` 字段 |
| -32602 | `Unknown tool: xxx` | 工具名称无效 | 使用 `create_activity` |
| -32000 | `Parameter content must be at least 2 characters` | content 太短 | 提供更详细的活动介绍 |
| -32000 | `Missing required parameters: start_time` | 未提供 start_time | 提供有效时间戳 |
| -32000 | `range cannot be negative` | 门票金额为负 | 使用正值或 0 |

---

## MCP 响应格式

### 成功

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "content": [{ "type": "text", "text": "..." }],
    "isError": false
  }
}
```

### 错误

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32602,
    "message": "错误信息"
  }
}
```

---

## 实现细节

### 数据库结构 (act 集合)

```javascript
const actData = {
  kid: '69bcdb49189f8658d9ad6dbf',    // 测试硬编码
  user: '6437c73e09e2988160cb54f6',     // 测试硬编码
  content: '活动介绍',
  start_time: 1711094400000,
  end_time: 1711108800000,
  address: '北京三里屯',
  location: { type: 'Point', coordinates: [116.4, 39.9] },
  range: 0,           // 门票金额 (分)
  pay: false,         // 是否付费
  url: '',            // 外部链接
  wx: 'forevip123',   // 联系方式
  type: 0,            // 活动类型
  hot: 0,             // 热度
  create_date: Date.now()
}
```

### 验证逻辑

```javascript
// 参数验证
if (!content || content.length < 2) {
  throw new Error('Parameter content must be at least 2 characters')
}
if (!start_time) {
  throw new Error('Missing required parameters: start_time and end_time')
}
if (range < 0) {
  throw new Error('range cannot be negative')
}
```

---

## 注意事项

1. **时间格式**: 毫秒时间戳 (`Date.now()`)
2. **金额单位**: `range` 使用分为单位 (¥99 = 9900)
3. **位置格式**: GeoJSON 标准 `{type:"Point",coordinates:[经度，纬度]}`
4. **认证机制**: 当前未实现 (占位符)
5. **测试数据**: `kid` 和 `user` 当前为硬编码
6. **MCP 规范**: JSON-RPC 2.0 格式

---

## 相关文件

| 文件 | 路径 |
|------|------|
| MCP 云函数 | `/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/mcp/index.obj.js` |
| 技能定义 (英文) | `/Users/codes/git/ai/skills/activity-create/SKILL.md` |
| 技能定义 (中文) | `/Users/codes/git/ai/skills/activity-create/SKILL_cn.md` |

---

**版本**: 0.0.3  
**更新**: 2026-03-20  
**MCP 规范**: https://modelcontextprotocol.io/  
**API**: https://api.fore.vip/tools  
**平台**: https://fore.vip
