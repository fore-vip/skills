---
name: activity-create
description: Create offline events for fore.vip platform. Use when users need to create activities with time, location, and ticket information.
version: 0.0.2
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

## HTTP API Endpoints

**Base URL**: `https://api.fore.vip/mcp`

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
    "tools": [
      {
        "name": "create_activity",
        "description": "Create offline event...",
        "inputSchema": { ... }
      }
    ]
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
      "kid": "kl_abc123",
      "content": "AI Weekend Meetup",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "Beijing Sanlitun",
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
    "content": [
      {
        "type": "text",
        "text": "{\n  \"success\": true,\n  \"id\": \"act_xxx\",\n  \"message\": \"Activity created successfully\"\n}"
      }
    ],
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
    "message": "Unknown tool: invalid_name"
  }
}
```

---

## Usage Examples

### JavaScript (Fetch API)

```javascript
// List tools
const toolsRes = await fetch('https://api.fore.vip/mcp/tools/list')
const tools = await toolsRes.json()
console.log(tools.result.tools)

// Create activity
const result = await fetch('https://api.fore.vip/mcp/tools/call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
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
})

const response = await result.json()

// Check for errors
if (response.error) {
  console.error('Error:', response.error.message)
} else {
  const data = JSON.parse(response.result.content[0].text)
  if (data.success) {
    console.log('Created:', data.id)
  }
}
```

### uniCloud (Cloud Function)

```javascript
const mcp = uniCloud.importObject('mcp')

// List tools
const tools = await mcp.tools_list()
console.log(tools.result.tools)

// Create activity
const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    kid: 'kl_bot_456',
    content: 'VIP AI Meetup',
    start_time: 1711872000000,
    end_time: 1711958400000,
    address: 'Shanghai Jing\'an Temple',
    location: { type: 'Point', coordinates: [121.44, 31.23] },
    range: 9900,
    pay: true,
    wx: 'forevip123'
  }
})

if (result.error) {
  console.error(result.error.message)
} else {
  const data = JSON.parse(result.result.content[0].text)
  console.log('Created:', data.id)
}
```

---

## Error Codes

| Code | Error | Cause |
|------|-------|-------|
| -32602 | `Missing required parameter: name` | name not provided |
| -32602 | `Unknown tool: xxx` | Invalid tool name |
| -32000 | `Missing required parameter: kid` | kid not provided |
| -32000 | `Parameter content must be at least 2 characters` | content too short |
| -32000 | `Bot not found: xxx` | Invalid bot ID |

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

## Notes

1. **Time**: Millisecond timestamps (Date.now())
2. **Money**: range in cents (¥99 = 9900)
3. **Location**: GeoJSON format
4. **Auth**: Not implemented (placeholder)
5. **MCP Spec**: JSON-RPC 2.0 format

---

**Version**: 3.0.0  
**Updated**: 2026-03-20  
**MCP Spec**: https://modelcontextprotocol.io/  
**API**: https://api.fore.vip/mcp
