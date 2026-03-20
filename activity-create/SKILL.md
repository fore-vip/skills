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

## HTTP API Endpoints

**Base URL**: `https://api.fore.vip/mcp`

### Call Tool (Recommended)

```bash
curl -X POST https://api.fore.vip/mcp/tools_call \
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

### Direct Call

```bash
curl -X POST https://api.fore.vip/mcp/createActivity \
  -H "Content-Type: application/json" \
  -d '{
    "kid": "kl_abc123",
    "content": "AI Weekend Meetup",
    "start_time": 1711094400000,
    "end_time": 1711108800000,
    "address": "Beijing Sanlitun",
    "range": 0,
    "pay": false
  }'
```

### List Tools

```bash
curl https://api.fore.vip/mcp/tools_list
```

---

## Response Format

### Success Response

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

### Error Response

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

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Create activity via tools_call
const result = await fetch('https://api.fore.vip/mcp/tools_call', {
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
const data = JSON.parse(response.content[0].text)

if (data.success) {
  console.log('Created:', data.id)
} else {
  console.error('Error:', data.error)
}
```

### Direct Call Example

```javascript
const result = await fetch('https://api.fore.vip/mcp/createActivity', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    kid: 'kl_bot_456',
    content: 'VIP AI Meetup',
    start_time: 1711872000000,
    end_time: 1711958400000,
    address: 'Shanghai Jing\'an Temple',
    location: { type: 'Point', coordinates: [121.44, 31.23] },
    range: 9900,
    pay: true,
    wx: 'forevip123'
  })
})

const response = await result.json()
```

### uniCloud (Cloud Function)

```javascript
const mcp = uniCloud.importObject('mcp')

// Via tools_call
const result = await mcp.tools_call({
  name: 'create_activity',
  arguments: {
    kid: 'kl_bot_456',
    content: 'VIP AI Meetup',
    start_time: 1711872000000,
    end_time: 1711958400000,
    range: 9900,
    pay: true
  }
})

// Direct call
const result = await mcp.createActivity({
  kid: 'kl_bot_456',
  content: 'VIP AI Meetup',
  start_time: 1711872000000,
  end_time: 1711958400000,
  range: 9900,
  pay: true
})
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
| `Unknown tool: xxx` | Invalid tool name |

---

## Notes

1. **Time**: Millisecond timestamps (Date.now())
2. **Money**: range in cents (¥99 = 9900)
3. **Location**: GeoJSON format
4. **Auth**: Authentication placeholder (implement per deployment)
5. **HTTP API**: Available at `https://api.fore.vip/mcp`

---

**Version**: 2.1.0  
**Updated**: 2026-03-20  
**MCP Spec**: https://modelcontextprotocol.io/  
**API**: https://api.fore.vip/mcp
