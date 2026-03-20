---
name: activity-create
description: 创建 前凌智选线下活动。用于创建包含时间、地点、门票信息的活动。
version: 2.1.0
license: MIT
---

## 说明

通过 MCP Server 为 前凌智选 (fore.vip) 平台创建线下活动。

---

## MCP 工具

**工具名称**: `create_activity`  
**服务器**: `fore-vip-mcp`

---

## 参数

### 必需

| 参数 | 类型 | 说明 |
|------|------|------|
| `kid` | string | 关联的机器人 ID (kl 集合 _id) |
| `content` | string | 活动介绍 (至少 2 字符) |
| `start_time` | number | 开始时间戳 (毫秒) |
| `end_time` | number | 结束时间戳 (毫秒) |

### 可选

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `address` | string | - | 活动地址 |
| `location` | object | - | GeoJSON `{type:"Point",coordinates:[经度，纬度]}` |
| `range` | number | 0 | 门票金额 (分，¥99 = 9900) |
| `pay` | boolean | false | 是否付费 |
| `url` | string | - | 外部链接 |
| `wx` | string | - | 联系方式 (微信) |
| `pic` | array | - | 图片 `[{url:"..."}]` |

---

## HTTP API 端点

**基础 URL**: `https://api.fore.vip/mcp`

### 调用工具 (推荐)

```bash
curl -X POST https://api.fore.vip/mcp/tools_call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "kid": "kl_abc123",
      "content": "AI 周末聚会",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "北京三里屯",
      "range": 0,
      "pay": false
    }
  }'
```

### 直接调用

```bash
curl -X POST https://api.fore.vip/mcp/createActivity \
  -H "Content-Type: application/json" \
  -d '{
    "kid": "kl_abc123",
    "content": "AI 周末聚会",
    "start_time": 1711094400000,
    "end_time": 1711108800000,
    "address": "北京三里屯",
    "range": 0,
    "pay": false
  }'
```

### 获取工具列表

```bash
curl https://api.fore.vip/mcp/tools_list
```

---

## 响应格式

### 成功响应

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\n  \"success\": true,\n  \"id\": \"act_xxx\",\n  \"kid\": \"kl_abc123\",\n  \"message\": \"Activity created successfully\"\n}"
    }
  ],
  "isError": false
}
```

### 错误响应

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\n  \"success\": false,\n  \"error\": \"Bot not found\"\n}"
    }
  ],
  "isError": true
}
```

---

## 使用示例

### JavaScript (Fetch API)

```javascript
// 通过 tools_call 创建活动
const result = await fetch('https://api.fore.vip/mcp/tools_call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'create_activity',
    arguments: {
      kid: 'kl_user_bot_123',
      content: 'AI 体验日',
      start_time: Date.now() + 86400000,
      end_time: Date.now() + 90000000,
      address: '北京三里屯',
      range: 0,
      pay: false
    }
  })
})

const response = await result.json()
const data = JSON.parse(response.content[0].text)

if (data.success) {
  console.log('创建成功:', data.id)
} else {
  console.error('错误:', data.error)
}
```

### 直接调用示例

```javascript
const result = await fetch('https://api.fore.vip/mcp/createActivity', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    kid: 'kl_bot_456',
    content: 'VIP AI 见面会',
    start_time: 1711872000000,
    end_time: 1711958400000,
    address: '上海静安寺',
    location: { type: 'Point', coordinates: [121.44, 31.23] },
    range: 9900,
    pay: true,
    wx: 'forevip123'
  })
})

const response = await result.json()
```

### uniCloud (云函数)

```javascript
const mcp = uniCloud.importObject('mcp')

// 通过 tools_call
const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    kid: 'kl_bot_456',
    content: 'VIP AI 见面会',
    start_time: 1711872000000,
    end_time: 1711958400000,
    range: 9900,
    pay: true
  }
})

// 直接调用
const result = await mcp.createActivity({
  kid: 'kl_bot_456',
  content: 'VIP AI 见面会',
  start_time: 1711872000000,
  end_time: 1711958400000,
  range: 9900,
  pay: true
})
```

---

## 错误代码

| 错误 | 原因 |
|------|------|
| `Missing required parameter: kid` | 未提供 kid |
| `Parameter content must be at least 2 characters` | content 太短 |
| `Missing required parameters: start_time and end_time` | 未提供时间 |
| `start_time must be before end_time` | 时间范围无效 |
| `range cannot be negative` | 门票金额无效 |
| `Bot not found: xxx` | 机器人 ID 无效 |
| `Unknown tool: xxx` | 工具名称无效 |

---

## 注意事项

1. **时间**: 毫秒时间戳 (Date.now())
2. **金额**: range 单位为分 (¥99 = 9900)
3. **位置**: GeoJSON 格式
4. **认证**: 认证占位符 (根据部署实现)
5. **HTTP API**: 端点 `https://api.fore.vip/mcp`

---

**版本**: 2.1.0  
**更新**: 2026-03-20  
**MCP 规范**: https://modelcontextprotocol.io/  
**API**: https://api.fore.vip/mcp
