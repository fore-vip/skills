# activity-create Skill

[![Version](https://img.shields.io/badge/version-v0.0.3-blue)](https://github.com/fore-vip/fore-ex)
[![Download](https://img.shields.io/badge/download-extension-blue)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![MCP](https://img.shields.io/badge/MCP-supported-green)](https://modelcontextprotocol.io/)

Agent skill for creating ForeSmart offline activities via MCP protocol.

---

## 📖 Introduction

`activity-create` is an MCP (Model Context Protocol) skill that enables AI assistants to help users create offline activities through natural language conversations.

**Core Features**:
- 🎯 Create activities via conversation
- 📍 Support for time, location, and ticket configuration
- 💬 Natural language interaction
- 🔗 Automatic redirect to activity detail page

---

## 🚀 Quick Start

### Installation

#### Method 1: Install via npx

```bash
npx skills add fore-vip/skills -s activity-create
```

#### Method 2: Use Chrome Extension (Recommended)

For regular users, we recommend using the Chrome browser extension:

- **Download**: [fore-ex-v1.1.zip](https://f.fore.vip/download/fore-ex-v1.1.zip)
- **Installation Guide**: [INSTALL_en.md](./INSTALL_en.md)
- **GitHub**: https://github.com/fore-vip/fore-ex

---

## 📋 Usage Examples

### Conversation Example

```
User: I want to create a weekend AI experience activity

Assistant: Great! I'll help you create this AI experience activity. Please provide:
   1. When does the activity start? (date and specific time)
   2. How long will it last? (end time)
   3. Where is the activity location? (optional)
   4. Is there a ticket fee? (optional)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | ✅ | Activity title/description |
| `start_time` | number | ✅ | Start time (milliseconds timestamp) |
| `end_time` | number | ⚪ | End time (milliseconds timestamp) |
| `address` | string | ✅ | Activity address |
| `range` | number | ⚪ | Ticket price (in cents, 0 means free) |
| `pay` | boolean | ⚪ | Whether payment is required |

---

## 📁 File Structure

```
activity-create/
├── SKILL.md              # Skill definition (English)
├── SKILL_cn.md           # Skill definition (Chinese)
├── README.md             # Project documentation (Chinese)
├── README_en.md          # Project documentation (English)
├── INSTALL.md            # Installation guide (Chinese)
├── INSTALL_en.md         # Installation guide (English)
├── test_local.sh         # Local test script
└── TEST_CONVERSATION.md  # Test conversation log
```

---

## 🧪 Testing

### Local Testing

Run the test script:

```bash
./test_local.sh
```

Test coverage:
- ✅ SKILL.md file check
- ✅ MCP endpoint connectivity
- ✅ Tool list retrieval
- ✅ Activity creation functionality

### Online Testing

Access MCP endpoints:

```bash
# Get tool list
curl https://api.fore.vip/mcp/tools/list

# Call tool
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": { ... }
  }'
```

---

## 🔄 Version History

### v0.0.3 (2026-03-20)

**Optimizations**
- ✅ Improved MCP protocol implementation
- ✅ Added error handling
- ✅ Optimized response format

### v0.0.2 (2026-03-19)

**New Features**
- ✅ Added Chinese skill definition
- ✅ Added local test script

### v0.0.1 (2026-03-18)

**Initial Release**
- ✅ Basic activity creation functionality
- ✅ MCP protocol integration

---

## 📞 Support

| Channel | Link |
|---------|------|
| **Website** | https://fore.vip |
| **GitHub** | https://github.com/fore-vip/fore-ex |
| **Issue Tracker** | https://github.com/fore-vip/fore-ex/issues |
| **MCP Specification** | https://modelcontextprotocol.io/ |

---

## 📄 License

MIT License

Copyright (c) 2026 ForeSmart

---

**Create activities effortlessly through natural language!** 🎉

Last Updated: 2026-03-21
