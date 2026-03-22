# activity-create Skill

[![Version](https://img.shields.io/badge/version-0.0.4-blue)](https://github.com/fore-vip/skills/tree/main/activity-create)
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

Create offline events for the fore.vip platform via MCP Server.

---

## 📋 Description

This skill enables AI agents to create offline events on the fore.vip platform. It handles event scheduling, location management, and contact information collection.

---

## 🚀 Installation

```bash
# Install from GitHub
npx skills add fore-vip/skills --skill activity-create

# Install from local path
npx skills add /path/to/skills --skill activity-create
```

---

## 🔧 MCP Server Configuration

**Endpoint**: `https://api.fore.vip/mcp/create_activity`  
**Method**: `POST`  
**Content-Type**: `application/json`

---

## 📝 Parameters

### Required

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `content` | string | Event description (min 2 chars) | `"AI Weekend Meetup"` |
| `start_time` | number | Start timestamp (ms) | `1711094400000` |
| `address` | string | Event location address | `"Beijing Sanlitun"` |
| `wx` | string | Contact WeChat ID | `"forevip123"` |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `end_time` | number | - | End timestamp (ms) |
| `location` | object | - | GeoJSON coordinates |
| `range` | number | `0` | Ticket price in cents |
| `pay` | boolean | `false` | Is paid event |
| `url` | string | - | External link URL |

---

## 💡 Usage Examples

### Basic Event Creation

```javascript
const response = await fetch('https://api.fore.vip/mcp/create_activity', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'AI Weekend Meetup',
    start_time: Date.now() + 86400000,
    address: 'Beijing Sanlitun',
    wx: 'forevip123'
  })
});

const result = await response.json();
console.log('Event created:', result.url);
```

### With All Parameters

```javascript
const event = {
  content: 'Premium AI Conference',
  start_time: 1711872000000,
  end_time: 1711958400000,
  address: 'Shanghai Jing\\'an Temple',
  location: {
    type: 'Point',
    coordinates: [121.44, 31.23]
  },
  wx: 'forevip123',
  range: 9900,  // ¥99
  pay: true,
  url: 'https://example.com'
};
```

---

## 📊 Response Format

### Success

```json
{
  "success": true,
  "id": "69bf8d848a5c785fa8c566cd",
  "url": "https://fore.vip/st?id=69bf8d848a5c785fa8c566cd"
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "FunctionBizError",
    "message": "Parameter content must be at least 2 characters"
  }
}
```

---

## ⚠️ Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Parameter content must be at least 2 characters` | Content too short | Provide longer description |
| `Missing required parameter: start_time` | No start time | Add start_time field |
| `Missing required parameter: address` | No address | Add address field |
| `Missing required parameter: wx` | No contact | Add wx field |

---

## 🧪 Testing

```bash
# Run local tests
cd activity-create
./test_local.sh
```

**Test Cases**:
- ✅ Create event (success scenario)
- ✅ Parameter validation (short content)
- ✅ Parameter validation (missing required fields)

---

## 📚 Related Resources

- **[MCP Specification](https://modelcontextprotocol.io/)** - Protocol docs
- **[skills.sh](https://skills.sh/)** - Skills directory
- **[Fore-Vip](https://fore.vip/)** - Platform website
- **[API Docs](https://api.fore.vip/mcp)** - MCP API

---

## 📝 Version History

### v0.0.4 (2026-03-22)
- ✅ Update to MCP Server standard
- ✅ Simplify SKILL.md format
- ✅ Add test script
- ✅ Update endpoint to `/mcp/create_activity`

### v0.0.3 (2026-03-20)
- ✅ Initial release

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a PR

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file.

---

**Maintainer**: wise  
**Last Updated**: 2026-03-22
