---
name: activity-create
description: Create offline events for fore.vip platform. Use when users need to create activities with time, location, and ticket information.
version: 2.1.0
license: MIT
---

## Description

Creates offline events for the fore.vip (前凌智选) platform via MCP Server.

---

## MCP Tool

**Tool Name**: `create_activity`  
**Server**: `fore-vip-mcp`

---

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `kid` | string | Bot ID to associate (kl collection _id) |
| `content` | string | Event description (min 2 chars) |
| `start_time` | number | Start timestamp (milliseconds) |
| `end_time` | number | End timestamp (milliseconds) |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `address` | string | - | Event address |
| `location` | object | - | GeoJSON `{type:"Point",coordinates:[lng,lat]}` |
| `range` | number | 0 | Ticket price in cents (¥99 = 9900) |
| `pay` | boolean | false | Payment required |
| `url` | string | - | External link |
| `wx` | string | - | Contact (WeChat) |
| `pic` | array | - | Images `[{url:"..."}]` |

---

## MCP Request/Response

### Request Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_activity",
    "arguments": {
      "kid": "kl_abc123",
      "content": "AI Weekend Meetup",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "Beijing Sanlitun",
      "range": 0,
      "pay": false
    }
  }
}
```

### Success Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"success\": true,\n  \"id\": \"act_xxx\",\n  \"kid\": \"kl_abc123\",\n  \"message\": \"Activity created successfully\"\n}"
      }
    ],
    "isError": false
  }
}
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"success\": false,\n  \"error\": \"Bot not found: kl_invalid\"\n}"
      }
    ],
    "isError": true
  }
}
```

---

## Usage Examples

### uniCloud Call (Cloud Function)

```javascript
// Import MCP cloud function
const mcp = uniCloud.importObject('mcp')

// List available tools
const tools = await mcp.tools_list()

// Create activity
const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    kid: 'kl_user_bot_123',
    content: 'AI Experience Day',
    start_time: Date.now() + 86400000,
    end_time: Date.now() + 90000000,
    address: 'Beijing Sanlitun',
    range: 0,
    pay: false
  }
})

// Parse result
const response = JSON.parse(result.content[0].text)
if (response.success) {
  console.log('Created:', response.id)
} else {
  console.error('Error:', response.error)
}
```

### Client Call (uni-app)

```javascript
// In uni-app client
const mcp = uniCloud.importObject('mcp')

const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    kid: 'kl_bot_456',
    content: 'VIP AI Meetup',
    start_time: 1711872000000,
    end_time: 1711958400000,
    address: 'Shanghai Jing\'an Temple',
    location: {
      type: 'Point',
      coordinates: [121.44, 31.23]
    },
    range: 9900,
    pay: true,
    wx: 'forevip123'
  }
})

const response = JSON.parse(result.content[0].text)
```

---

## Error Codes

| Error | Cause |
|-------|-------|
| `Missing required parameter: kid` | kid not provided |
| `Parameter content must be at least 2 characters` | content too short |
| `Missing required parameters: start_time and end_time` | Time not provided |
| `start_time must be before end_time` | Invalid time range |
| `range cannot be negative` | Invalid ticket price |
| `Bot not found: xxx` | Invalid bot ID |

---

## Notes

1. **Time**: Millisecond timestamps (Date.now())
2. **Money**: range in cents (¥99 = 9900)
3. **Location**: GeoJSON format
4. **Auth**: Authentication placeholder (implement per deployment)
5. **uniCloud**: Methods use underscore naming (tools_list, tools_call)

---

**Version**: 2.1.0  
**Updated**: 2026-03-20  
**MCP Spec**: https://modelcontextprotocol.io/
