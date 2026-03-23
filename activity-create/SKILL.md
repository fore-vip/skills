---
name: activity-create
description: Create offline events for fore.vip via MCP Server. Requires Open Key authentication.
version: 0.0.6
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - Activity Creation
  - Open Key
  - 活动创建
  - fore.vip
---

# Activity Create Skill

Create **offline events** for **fore.vip** platform via **MCP Server**.

**🔐 Requires Open Key Authentication**

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

## 🌐 MCP Endpoint

**URL**: `https://api.fore.vip/mcp/create_activity`  
**Method**: `POST`  
**Auth**: 🔐 Required

## 📝 Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | string | Event description (≥2 chars) |
| `start_time` | number | Start timestamp (ms) |
| `address` | string | Event address |
| `wx` | string | WeChat contact |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `end_time` | number | - | End timestamp |
| `location` | object | - | GeoJSON coords |
| `range` | number | 0 | Ticket price (cents) |
| `pay` | boolean | false | Payment required |
| `url` | string | - | External link |

## 🚀 Usage

```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI Meetup",
    "start_time": 1711094400000,
    "address": "Beijing",
    "wx": "forevip123"
  }'
```

## 📊 Response

```json
{
  "success": true,
  "id": "69bf8d848a5c785fa8c566cd",
  "url": "https://fore.vip/st?id=69bf8d848a5c785fa8c566cd"
}
```

## ⚠️ Errors

| Error | Solution |
|-------|----------|
| Missing Open Key | Add Authorization header |
| Invalid Open Key | Check your key |
| content too short | Use ≥2 characters |

---

**Version**: 0.0.6 | **Updated**: 2026-03-24
