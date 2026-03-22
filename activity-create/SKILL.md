---
name: activity-create
description: AI Agents Skills - Create offline events and activities for fore.vip platform using MCP Server. Compatible with OpenClaw, Hub, and MCP protocols. Perfect for AI product launches, meetups, and community events.
version: 0.0.5
license: MIT
keywords:
  - AI Agents
  - Skills
  - MCP Server
  - OpenClaw
  - Activity Creation
  - Event Management
  - 活动创建
  - 线下活动
  - fore.vip
  - Hub
  - 智能体技能
---

# Activity Create Skill - AI Agents Skills for fore.vip

Create **offline events** and **activities** for the **fore.vip platform** via **MCP Server**. This **AI Agent Skill** is designed for **OpenClaw**, **Hub**, and other MCP-compatible platforms. Perfect for **AI product launches**, **tech meetups**, and **community events**.

## 🔥 Popular Keywords

**AI Agents** | **Skills** | **MCP Server** | **OpenClaw** | **Activity** | **活动创建** | **Event** | **Hub** | **AI 智能体** | **fore.vip** | **线下活动** | **Event Management**

## 📋 When to Use

Use this **AI Agent Skill** when you want to:

- 🎯 Create an **offline event** or **meetup** on fore.vip
- 📅 Publish an **activity** with time, location, and contact info
- 🚀 Launch **AI product** events and **tech meetups**
- 💬 Schedule **community events** with **WeChat contact**
- 🎫 Create **paid events** with ticket pricing
- 📍 Add **location coordinates** for **LBS-based** discovery
- 🔗 Integrate with **OpenClaw** and **Hub** platforms

## 🌐 MCP Server Configuration

**Endpoint**: `https://api.fore.vip/mcp/create_activity`  
**Method**: `POST`  
**Content-Type**: `application/json`  
**Protocol**: **MCP Server** (Compatible with **OpenClaw**, **Hub**, **AI Agents**)

### Architecture

The **fore.vip MCP Server** provides endpoints for **AI Agents** and **Skills**:

| Endpoint | Method | Usage | Recommended |
|----------|--------|-------|-------------|
| `/mcp/create_activity` | POST | Create **activities** (direct) | ⭐⭐⭐⭐⭐ |
| `/mcp/query_kl` | POST | Query **products** (direct) | ⭐⭐⭐⭐⭐ |
| `/tools/list` | GET | List tools (MCP standard) | ⭐⭐⭐ |
| `/tools/call` | POST | Call tool (MCP standard) | ⭐⭐⭐ |

## 📝 Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `content` | string | Event description (min 2 chars) | `"AI Weekend Meetup"` |
| `start_time` | number | Start timestamp (milliseconds) | `Date.now() + 86400000` |
| `address` | string | Event location address | `"Beijing Sanlitun"` |
| `wx` | string | Contact WeChat ID | `"forevip123"` |

## 📝 Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `end_time` | number | - | End timestamp (milliseconds) | `Date.now() + 90000000` |
| `location` | object | - | GeoJSON coordinates | `{type: "Point", coordinates: [lng, lat]}` |
| `range` | number | `0` | Ticket price in cents | `9900` (¥99) |
| `pay` | boolean | `false` | Payment required | `true` |
| `url` | string | - | External link URL | `"https://example.com"` |
| `kid` | string | - | Related product ID | `"670703627ae7081fd93d09f1"` |

## 🚀 Steps for AI Agents

1. **Collect event information from user**
   - Ask for **event name/description** (content)
   - Ask for **start time** (convert to milliseconds timestamp)
   - Ask for **event address** (location)
   - Ask for **WeChat contact** (wx)
   - Optional: end time, ticket price, coordinates

2. **Validate parameters** (OpenClaw & Hub Compatible)
   - Ensure content is at least 2 characters
   - Ensure start_time is a valid timestamp
   - Ensure address and wx are not empty
   - Validate range (if provided) is positive integer

3. **Call MCP Server**
   ```javascript
   const response = await fetch('https://api.fore.vip/mcp/create_activity', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       content: 'AI Weekend Meetup',
       start_time: Date.now() + 86400000,
       address: 'Beijing Sanlitun',
       wx: 'forevip123',
       range: 0,
       pay: false
     })
   });
   
   const result = await response.json();
   ```

4. **Handle response**
   - If `result.success === true`: Show success message with **event URL**
   - If `result.success === false`: Show error message from `result.error.message`

5. **Navigate to event page** (if successful)
   - Open `https://fore.vip/st?id=${result.id}` in new tab
   - Share **event link** with participants

## 📦 Example Request

```json
{
  "content": "AI Weekend Meetup - Explore AI Agents & MCP Skills",
  "start_time": 1711094400000,
  "address": "Beijing Sanlitun SOHO",
  "wx": "forevip123",
  "range": 0,
  "pay": false,
  "location": {
    "type": "Point",
    "coordinates": [116.4074, 39.9042]
  }
}
```

## 📊 Example Response

```json
{
  "success": true,
  "id": "69bf86f6f08210bff892e966",
  "url": "https://fore.vip/st?id=69bf86f6f08210bff892e966"
}
```

## 🔗 Activity URL Pattern

Each **activity/event** can be accessed via:

```
https://fore.vip/st?id={activity_id}
```

**Example**:
- Activity ID: `69bf86f6f08210bff892e966`
- Activity URL: `https://fore.vip/st?id=69bf86f6f08210bff892e966`

### Display Format (SEO-Optimized for AI Agents & OpenClaw)

```markdown
🎉 **活动创建成功!**

- 📝 名称：AI Weekend Meetup
- 📅 时间：2026-03-22 14:00
- 📍 地点：Beijing Sanlitun
- 💬 联系：forevip123
- 🎫 门票：免费
- 🔗 链接：https://fore.vip/st?id=69bf86f6f08210bff892e966
- 🌐 平台：fore.vip | OpenClaw | Hub | MCP
```

## ⚠️ Error Handling

Common errors for **AI Agents** and **Skills**:

| Error | Cause | Solution |
|-------|-------|----------|
| `Parameter content must be at least 2 characters` | Content too short | Provide longer description |
| `Missing required parameter: start_time` | No start time | Add start_time timestamp |
| `Missing required parameter: address` | No address | Provide event location |
| `Missing required parameter: wx` | No contact | Add WeChat ID |
| Network timeout | MCP Server error | Retry with exponential backoff |

## 💻 Implementation Details

**Cloud Object URL Trigger**:
- After URL triggering, POST request body is a **string**
- Must use `this.getHttpInfo().body` to get the body
- Must manually `JSON.parse()` to convert string to object

```javascript
// Cloud Object Code (mcp/index.obj.js)
async create_activity() {
  const httpInfo = this.getHttpInfo();
  const pm = JSON.parse(httpInfo.body);  // String → Object
  const { content, start_time, address, wx, range = 0, pay = false } = pm;
  // ... business logic
}
```

**Timestamp Conversion**:
```javascript
// JavaScript Date to milliseconds
const startTime = new Date('2026-03-22 14:00:00').getTime();
// Output: 1711094400000

// Current time
const now = Date.now();
```

**GeoJSON Location**:
```javascript
// Beijing coordinates
const location = {
  type: "Point",
  coordinates: [116.4074, 39.9042]  // [longitude, latitude]
};
```

## 📌 Notes

- ⏰ All timestamps should be in **milliseconds** (e.g., `Date.now()`)
- 💰 Ticket price (`range`) is in **cents** (¥99 = 9900 cents)
- 📍 Location uses **GeoJSON format**: `{type: "Point", coordinates: [lng, lat]}`
- 🔗 The skill uses **MCP Server protocol** for **AI Agents** communication
- ✅ Compatible with **OpenClaw**, **Hub**, and other **MCP platforms**
- 🏷️ **SEO Keywords**: AI Agents, Skills, MCP, Activity, 活动创建，OpenClaw, Hub, fore.vip

## 🏷️ SEO Metadata

**Primary Keywords**:
- AI Agents Skills
- Activity Creation
- Event Management
- MCP Server
- OpenClaw Skills
- 活动创建
- 线下活动
- fore.vip Events

**Secondary Keywords**:
- Hub Integration
- Meetup Creation
- AI Product Launch
- MCP Protocol
- Agent Skills Marketplace
- 智能体技能
- OpenClaw 插件
- Event Publishing

**Long-tail Keywords**:
- How to create events with AI Agents
- fore.vip MCP Server activity API
- OpenClaw event creation skill
- Create meetups with MCP protocol
- AI Agents skills for event management
- 如何使用 AI 智能体创建活动
- fore.vip 平台线下活动 API
- AI product launch event creation

## 🎯 Use Cases

### 1. AI Product Launch Event

```json
{
  "content": "AI Agents & MCP Skills Product Launch",
  "start_time": 1711094400000,
  "address": "Beijing Zhongguancun",
  "wx": "forevip123",
  "range": 9900,
  "pay": true
}
```

### 2. Tech Meetup

```json
{
  "content": "OpenClaw & Hub Developer Meetup",
  "start_time": 1711180800000,
  "address": "Shanghai Zhangjiang",
  "wx": "devmeetup",
  "range": 0,
  "pay": false
}
```

### 3. Community Event

```json
{
  "content": "AI 智能体技术分享会",
  "start_time": 1711267200000,
  "address": "Shenzhen Nanshan",
  "wx": "aishare",
  "range": 0,
  "pay": false
}
```

---

**Version**: 0.0.5 (SEO Optimized)  
**Last Updated**: 2026-03-22  
**Compatible With**: OpenClaw, Hub, MCP Server, AI Agents  
**Platform**: fore.vip  
**Category**: Activity/Event Management
