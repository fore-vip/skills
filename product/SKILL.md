---
name: product
description: Query/create AI products on fore.vip. query_kl is public, create_kl requires Open Key.
version: 0.0.3
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - Product Catalog
  - Open Key
  - 产品查询
  - fore.vip
---

# Product Skill

Query and create **AI products** on **fore.vip** platform.

**Tools**: `query_kl` (public), `create_kl` (🔐 requires Open Key)

## 🔐 Authentication

### Get Open Key

1. Register/Login on [fore.vip](https://fore.vip)
2. Go to **User Center** → **API Settings**
3. Copy your **Open Key**

### Header Format

```http
Authorization: Bearer <your_open_key>
```

or

```http
X-Open-Key: <your_open_key>
```

## 🌐 MCP Endpoints

### query_kl (Public)

**URL**: `https://api.fore.vip/mcp/query_kl`  
**Method**: `POST`  
**Auth**: ❌ Public

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tag` | string | - | Product tag |
| `limit` | number | 20 | Max results (1-100) |
| `skip` | number | 0 | Pagination |

#### Example

```bash
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"tag":"推荐","limit":10}'
```

#### Response

```json
{
  "success": true,
  "total": 10,
  "data": [{"id":"xxx","name":"AI 助手","tag":"推荐"}]
}
```

---

### create_kl (Auth Required)

**URL**: `https://api.fore.vip/mcp/create_kl`  
**Method**: `POST`  
**Auth**: 🔐 Required

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Product name (≥2 chars) |
| `content` | string | Description (≥10 chars) |

#### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pic` | string[] | [] | Image URLs |
| `tag` | string | "推荐" | Product tag |
| `hot` | number | 0 | Hot score |
| `url` | string | "" | External link |

#### Example

```bash
curl -X POST https://api.fore.vip/mcp/create_kl \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Assistant",
    "content": "Powerful AI product",
    "tag": "推荐"
  }'
```

#### Response

```json
{
  "success": true,
  "id": "xxx",
  "url": "https://fore.vip/p?id=xxx"
}
```

---

## 📊 Auth Summary

| Tool | Auth |
|------|------|
| `query_kl` | ❌ Public |
| `create_kl` | 🔐 Required |

---

**Version**: 0.0.3 | **Updated**: 2026-03-24
