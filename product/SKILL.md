---
name: product
description: Query product catalog from fore.vip platform via MCP Server
version: 0.0.2
license: MIT
---

# Product Query Skill

Query and browse the product catalog (KL collection) from the fore.vip platform via MCP Server.

## When to Use

Use this skill when the user wants to:
- Browse products on fore.vip platform
- Search products by tag (e.g., "推荐", "热门", "新品")
- View product details (name, description, images)
- Get paginated product lists

## MCP Server Configuration

### Architecture

The fore.vip MCP Server has two endpoints:

1. **Direct MCP Endpoint** (Recommended) - `https://api.fore.vip/mcp/*`
2. **Tools Protocol Endpoint** (MCP Standard) - `https://api.fore.vip/tools/*`

### Endpoints

| Endpoint | Method | Usage | Recommended |
|----------|--------|-------|-------------|
| `/mcp/query_kl` | POST | Query products (direct) | ⭐⭐⭐⭐⭐ |
| `/mcp/create_activity` | POST | Create activity (direct) | ⭐⭐⭐⭐⭐ |
| `/tools/list` | GET | List tools (MCP standard) | ⭐⭐⭐ |
| `/tools/call` | POST | Call tool (MCP standard) | ⭐⭐⭐ |

### Direct Call (Recommended)

```bash
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{
    "tag": "推荐",
    "limit": 10
  }'
```

**Response**:
```json
{
  "success": true,
  "total": 10,
  "limit": 10,
  "skip": 0,
  "hasMore": false,
  "data": [
    {
      "id": "670703627ae7081fd93d09f1",
      "name": "文案助手",
      "content": "请你扮演一个优质文案助手...",
      "pic": [],
      "tag": "推荐",
      "hot": 21307866,
      "update_date": 1234567890
    }
  ]
}
```

### Via Tools Protocol (MCP Standard)

```bash
curl -X POST https://api.fore.vip/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "query_kl",
    "arguments": {
      "tag": "推荐",
      "limit": 10
    }
  }'
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"success\":true,\"total\":10,...}"
    }],
    "isError": false
  }
}
```

## Parameters

### Optional

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `tag` | string | - | Product tag to filter | `"推荐"` |
| `limit` | number | `20` | Max results (1-100) | `50` |
| `skip` | number | `0` | Skip for pagination | `20` |

## Steps

1. **Collect search parameters from user**
   - Ask for product tag/category (optional)
   - Ask for number of results (default: 20, max: 100)
   - Ask for page number (for pagination)

2. **Validate parameters**
   - Ensure limit is between 1-100
   - Ensure skip is non-negative

3. **Call MCP Server**
   ```javascript
   const response = await fetch('https://api.fore.vip/mcp/query_kl', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       tag: '推荐',
       limit: 10,
       skip: 0
     })
   });
   
   const result = await response.json();
   ```

4. **Handle response**
   - If `result.success === true`: Display product list
   - Show total count and pagination info
   - If `result.success === false`: Show error message

5. **Display products**
   - Show product name, description, images
   - Provide navigation for next/previous page

## Example Request

```json
{
  "tag": "推荐",
  "limit": 10,
  "skip": 0
}
```

## Example Response

```json
{
  "success": true,
  "total": 10,
  "limit": 10,
  "skip": 0,
  "hasMore": false,
  "data": [
    {
      "id": "670703627ae7081fd93d09f1",
      "name": "文案助手",
      "content": "请你扮演一个优质文案助手...",
      "pic": [],
      "tag": "推荐",
      "hot": 21307866,
      "update_date": 1234567890
    }
  ]
}
```

## Error Handling

Common errors:
- Invalid limit value (must be 1-100)
- Invalid skip value (must be >= 0)
- Network errors

## Implementation Details

**Cloud Object URL Trigger**:
- After URL triggering, POST request body is a **string**
- Must use `this.getHttpInfo().body` to get the body
- Must manually `JSON.parse()` to convert string to object

```javascript
// Cloud Object Code (mcp/index.obj.js)
async query_kl() {
  const httpInfo = this.getHttpInfo();
  const pm = JSON.parse(httpInfo.body);  // String → Object
  const { tag, limit = 20, skip = 0 } = pm;
  // ... business logic
}
```

## Notes

- Default limit is 20, maximum is 100
- Use `skip` for pagination (skip = (page-1) * limit)
- Products are sorted by hot (desc) and update_date (desc)
- Images are returned as arrays of image objects
- The skill uses MCP Server protocol for communication
