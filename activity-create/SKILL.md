---
name: activity-create
description: Create offline events for Qianling Zhixuan (fore.vip) platform. Use this skill when users need to create activities, including event info, time/location setup, ticket pricing, etc.
version: 1.0.0
license: MIT
---

## Skill Description

This skill helps create offline events for the Qianling Zhixuan (fore.vip) platform. Data is persisted via MCP cloud functions.

---

## Use Cases

- User wants to create a new offline event
- Need to set event time, location, ticket price, etc.
- Link to existing AI bots (kl collection)

---

## Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `kid` | string | Associated bot ID (kl._id) | `"kl_abc123"` |
| `content` | string | Event description (min 2 chars) | `"Weekend AI Experience"` |
| `start_time` | number | Start timestamp (milliseconds) | `1711008000000` |
| `end_time` | number | End timestamp (milliseconds) | `1711094400000` |

## Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `address` | string | - | Event address text |
| `location` | object | - | Geo coordinates `{type:"Point",coordinates:[lng,lat]}` |
| `range` | number | `0` | Ticket price in cents (e.g., 9900 = ¥99) |
| `pay` | boolean | `false` | Whether payment is required |
| `url` | string | - | External link |
| `wx` | string | - | Contact (WeChat) |
| `pic` | array | - | Image array `[{url:"..."}]` |

---

## Processing Flow

### 1. Information Collection

Ask user for missing required parameters:

```
Please confirm the following:
1. Which AI bot to associate? (need kid or bot name)
2. What is the event description?
3. When does the event start and end?
4. Where is the event location? (optional)
5. Is there a ticket fee? (optional)
```

### 2. Parameter Validation

```javascript
// Validation rules
- kid: required, string
- content: required, length >= 2
- start_time: required, number, must be future time
- end_time: required, number, must be after start_time
- range: optional, number, >= 0
```

### 3. Call Cloud Function

```javascript
const mcp = uniCloud.importObject('mcp')

const res = await mcp.createAct({
  token: uni.getStorageSync('token'),
  kid: "kl_xxx",
  content: "Event description",
  start_time: 1711008000000,
  end_time: 1711094400000,
  address: "Beijing Chaoyang District xxx",
  location: { type: "Point", coordinates: [116.4, 39.9] },
  range: 9900,
  pay: true
})

// Returns
// { id: "act_xxx", created: true, kid, content }
```

### 4. Handle Results

**Success**:
```javascript
uni.showToast({ title: 'Created successfully', icon: 'success' })
uni.navigateTo({ url: '/ai/st?id=' + res.id })
```

**Failure**:
```javascript
uni.showToast({ title: e.message, icon: 'none' })
// Guide user to fix based on error
```

---

## Error Handling

| Error Message | Cause | Suggested Action |
|---------------|-------|------------------|
| `User not logged in` | Token expired/missing | Guide user to login |
| `Please specify bot (kid)` | kid not provided | Ask for kid or help find bot |
| `Description min 2 chars` | content too short | Ask user to elaborate |
| `Start time must be before end time` | Invalid time range | Ask user to check times |
| `Bot not found` | Invalid kid | Verify kid is correct |
| `Can only create for own bots` | Permission denied | Explain permission issue |

---

## Example Conversations

### Example 1: Standard Flow

**User**: I want to create a weekend AI experience event

**AI**: Great! I'll help you create the event. Please provide:
1. Which AI bot to associate? (provide bot ID or name)
2. What's the event description?
3. When does it start and end?
4. Where is the location?
5. Is there a ticket fee?

**User**: Associate my chatbot, description "Face-to-face AI interaction", Saturday 2pm-6pm, at Sanlitun Beijing, free

**AI**: Creating your event...

```javascript
// Call cloud function
const res = await mcp.createAct({
  token,
  kid: "kl_user_bot_123",  // Query user's bots first
  content: "Face-to-face AI interaction",
  start_time: 1711094400000,  // Saturday 14:00
  end_time: 1711108800000,    // Saturday 18:00
  address: "Beijing Sanlitun",
  range: 0,
  pay: false
})
```

**AI**: ✅ Event created successfully! [View details](/ai/st?id=act_xxx)

---

### Example 2: Paid Event

**User**: Help me create a paid event for my bot, ticket price ¥99

**AI**: Sure, please provide:
1. Which bot?
2. Event description and time?
3. Location?

**User**: Customer service bot, "VIP User Meetup", next Sunday all day, Jing'an Temple Shanghai

**AI**: 
```javascript
const res = await mcp.createAct({
  token,
  kid: "kl_cs_bot_456",
  content: "VIP User Meetup",
  start_time: 1711872000000,  // Next Sunday 00:00
  end_time: 1711958400000,    // Next Sunday 23:59
  address: "Shanghai Jing'an Temple",
  range: 9900,  // ¥99 = 9900 cents
  pay: true
})
```

---

## Related Cloud Functions

MCP cloud functions provide these event-related methods:

| Method | Description | Parameters |
|--------|-------------|------------|
| `createAct` | Create new event | `kid, content, start_time, end_time, ...` |
| `updateAct` | Update event | `id, data` |
| `deleteAct` | Delete event | `id` |
| `listActs` | List events | `kid, limit` |
| `getAct` | Get event details | `id` |

---

## Notes

1. **Time Format**: Must use millisecond timestamps (Date.now())
2. **Currency Unit**: range is in cents (¥99 = 9900)
3. **Coordinate Format**: location uses GeoJSON `{type:"Point",coordinates:[longitude,latitude]}`
4. **Permission**: Can only operate on own events
5. **Image Upload**: pic array must be uploaded via uni-file-picker first to get URLs

---

## Code Snippets

### Query User's Bots

```javascript
const db = uniCloud.database()
const bots = await db.collection('kl')
  .where({ user: auth.uid })
  .field('_id,name')
  .get()
```

### Time Picker Conversion

```javascript
// Convert uni-datetime-picker string to timestamp
const startTime = new Date(dateTimeString).getTime()
```

### Location Selection

```javascript
uni.chooseLocation({
  success: (res) => {
    location = {
      type: "Point",
      coordinates: [res.longitude, res.latitude]
    }
    address = res.address
  }
})
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-20  
**Backend**: MCP Cloud Function (`uniCloud-aliyun/cloudfunctions/mcp/index.obj.js`)  
**Platform**: Qianling Zhixuan (fore.vip)
