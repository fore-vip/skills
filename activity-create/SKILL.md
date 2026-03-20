---
name: activity-create
description: Create offline events for fore.vip platform. Use when users need to create activities with time, location, and ticket information.
version: 0.0.3
license: MIT
---

## Description

Creates offline events for the fore.vip (前凌智选) platform via MCP Server.

---

## MCP Tool

**Tool Name**: `create_activity`  
**Server**: `fore-vip-mcp`  
**Endpoint**: `https://api.fore.vip/mcp`

---

## Parameters

### Required (必需参数)

| Parameter | Type | Description | Validation | Example |
|-----------|------|-------------|------------|---------|
| `content` | string | Event description | Min 2 characters | `"AI Weekend Meetup"` |
| `start_time` | number | Start timestamp (milliseconds) | Must be valid timestamp | `1711094400000` |
| `address` | string | Event address text | Non-empty | `"Beijing Sanlitun"` |
| `wx` | string | Contact information (WeChat) | Non-empty | `"forevip123"` |

### Optional (可选参数)

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `kid` | string | Hardcoded | Bot ID (kl collection _id) | `"69bcdb49189f8658d9ad6dbf"` |
| `end_time` | number | - | End timestamp (milliseconds) | `1711108800000` |
| `location` | object | - | GeoJSON coordinates | `{type:"Point",coordinates:[116.4,39.9]}` |
| `range` | number | `0` | Ticket price in cents (¥99 = 9900) | `9900` |
| `pay` | boolean | `false` | Payment required | `true` |
| `url` | string | - | External link URL | `"https://example.com"` |

> **Note**: Currently `kid` and `user` are hardcoded for testing. This will be updated in future versions.

---

## HTTP API Endpoints

### List Tools

```bash
curl https://api.fore.vip/mcp/tools/list
```

**Response**:
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

### Call Tool

```bash
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "AI Weekend Meetup",
      "start_time": 1711094400000,
      "address": "Beijing Sanlitun",
      "wx": "forevip123",
      "end_time": 1711108800000,
      "range": 0,
      "pay": false
    }
  }'
```

**Success Response**:
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

**Error Response**:
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

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Create activity
const result = await fetch('https://api.fore.vip/mcp/tools/call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'create_activity',
    arguments: {
      content: 'AI Experience Day',
      start_time: Date.now() + 86400000,
      address: 'Beijing Sanlitun',
      wx: 'forevip123',
      end_time: Date.now() + 90000000,
      range: 0,
      pay: false
    }
  })
})

const response = await result.json()

// Check for errors
if (response.error) {
  console.error('Error:', response.error.message)
} else {
  const data = JSON.parse(response.result.content[0].text)
  if (data.success) {
    console.log('Created:', data.id)
    console.log('Activity URL:', 'https://fore.vip/st?id=' + data.id)
  }
}
```

### uniCloud (Cloud Function)

```javascript
const mcp = uniCloud.importObject('mcp')

// Create activity
const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    content: 'VIP AI Meetup',
    start_time: 1711872000000,
    end_time: 1711958400000,
    address: 'Shanghai Jing\'an Temple',
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
  console.log('Created:', data.id)
  console.log('URL:', 'https://fore.vip/st?id=' + data.id)
}
```

---

## Error Codes

| Code | Error | Cause | Solution |
|------|-------|-------|----------|
| -32602 | `Missing required parameter: name` | name not provided in request | Include `name` field in request body |
| -32602 | `Unknown tool: xxx` | Invalid tool name | Use `create_activity` |
| -32000 | `Parameter content must be at least 2 characters` | content too short | Provide longer description |
| -32000 | `Missing required parameters: start_time` | start_time not provided | Include valid timestamp |
| -32000 | `range cannot be negative` | Negative ticket price | Use positive value or 0 |

---

## MCP Response Format

### Success

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

### Error

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32602,
    "message": "Error message"
  }
}
```

---

## Implementation Details

### Database Schema (act collection)

```javascript
const actData = {
  kid: '69bcdb49189f8658d9ad6dbf',    // Hardcoded for testing
  user: '6437c73e09e2988160cb54f6',     // Hardcoded for testing
  content: 'Activity description',
  start_time: 1711094400000,
  end_time: 1711108800000,
  address: 'Beijing Sanlitun',
  location: { type: 'Point', coordinates: [116.4, 39.9] },
  range: 0,           // Ticket price in cents
  pay: false,         // Payment required
  url: '',            // External link
  wx: 'forevip123',   // Contact info
  type: 0,            // Activity type
  hot: 0,             // Popularity
  create_date: Date.now()
}
```

### Validation Logic

```javascript
// Parameter validation
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

## Notes

1. **Time Format**: Millisecond timestamps (`Date.now()`)
2. **Money**: `range` in cents (¥99 = 9900)
3. **Location**: GeoJSON format `{type:"Point",coordinates:[longitude,latitude]}`
4. **Authentication**: Not implemented yet (placeholder)
5. **Test Data**: `kid` and `user` are currently hardcoded
6. **MCP Spec**: JSON-RPC 2.0 format

---

## Related Files

| File | Path |
|------|------|
| MCP Cloud Function | `/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/mcp/index.obj.js` |
| Skill Definition | `/Users/codes/git/ai/skills/activity-create/SKILL.md` |
| Skill (Chinese) | `/Users/codes/git/ai/skills/activity-create/SKILL_cn.md` |

---

**Version**: 0.0.3  
**Updated**: 2026-03-20  
**MCP Spec**: https://modelcontextprotocol.io/  
**API**: https://api.fore.vip/mcp  
**Platform**: https://fore.vip
