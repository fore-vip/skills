---
name: activity-create
description: Create offline events for fore.vip platform using MCP Server
version: 0.0.4
license: MIT
---

# Activity Create Skill

Create offline events for the fore.vip platform via MCP Server.

## When to Use

Use this skill when the user wants to:
- Create an offline event or meetup
- Publish an activity on fore.vip platform
- Schedule an event with time, location, and contact information

## MCP Server Configuration

**Endpoint**: `https://api.fore.vip/mcp/create_activity`  
**Method**: `POST`  
**Content-Type**: `application/json`

## Required Parameters

- `content` (string): Event description (minimum 2 characters)
- `start_time` (number): Start timestamp in milliseconds (e.g., `Date.now()`)
- `address` (string): Event location address
- `wx` (string): Contact WeChat ID

## Optional Parameters

- `end_time` (number): End timestamp in milliseconds
- `location` (object): GeoJSON coordinates `{type: "Point", coordinates: [longitude, latitude]}`
- `range` (number): Ticket price in cents (default: 0)
- `pay` (boolean): Whether the event requires payment (default: false)
- `url` (string): External link URL

## Steps

1. **Collect event information from user**
   - Ask for event name/description
   - Ask for start time (convert to milliseconds timestamp)
   - Ask for event address
   - Ask for WeChat contact

2. **Validate parameters**
   - Ensure content is at least 2 characters
   - Ensure start_time is a valid timestamp
   - Ensure address and wx are not empty

3. **Call MCP Server**
   ```javascript
   const response = await fetch('https://api.fore.vip/mcp/create_activity', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       content: 'Event description',
       start_time: Date.now() + 86400000,
       address: 'Event location',
       wx: 'wechat_id'
     })
   });
   
   const result = await response.json();
   ```

4. **Handle response**
   - If `result.success === true`: Show success message with event URL
   - If `result.success === false`: Show error message from `result.error.message`

5. **Navigate to event page** (if successful)
   - Open `https://fore.vip/st?id=${result.id}` in new tab

## Example Request

```json
{
  "content": "AI Weekend Meetup",
  "start_time": 1711094400000,
  "address": "Beijing Sanlitun",
  "wx": "forevip123",
  "range": 0,
  "pay": false
}
```

## Example Response

```json
{
  "success": true,
  "id": "69bf86f6f08210bff892e966",
  "url": "https://fore.vip/st?id=69bf86f6f08210bff892e966"
}
```

## Error Handling

Common errors:
- `Parameter content must be at least 2 characters` - Content too short
- `Missing required parameter: start_time` - No start time provided
- `Missing required parameter: address` - No address provided
- `Missing required parameter: wx` - No contact info provided

## Notes

- All timestamps should be in milliseconds (e.g., `Date.now()`)
- Ticket price (`range`) is in cents (¥99 = 9900 cents)
- Location uses GeoJSON format: `{type: "Point", coordinates: [lng, lat]}`
- The skill uses MCP Server protocol for communication
