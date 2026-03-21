# activity-create Skill

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-v0.0.3-blue)](https://github.com/fore-vip/skills)
[![Download](https://img.shields.io/badge/download-extension-blue)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![MCP](https://img.shields.io/badge/MCP-supported-green)](https://modelcontextprotocol.io/)

Agent skill for creating offline events on fore.vip platform via MCP protocol.

---

## Overview

`activity-create` is an MCP (Model Context Protocol) skill that enables AI assistants to help users create offline events through natural language conversations.

**Core Features**:
- Create events via conversation
- Support for time, location, and ticket configuration
- Natural language interaction
- Auto-redirect to event detail page

---

## Quick Start

### Installation

#### Option 1: Install via npx

```bash
npx skills add fore-vip/skills -s activity-create
```

#### Option 2: Global Installation

```bash
npx skills add fore-vip/skills -s activity-create -g
```

#### Option 3: Install to Specific Agent

```bash
# Claude Code
npx skills add fore-vip/skills -s activity-create -a claude-code

# Cursor
npx skills add fore-vip/skills -s activity-create -a cursor

# OpenCode
npx skills add fore-vip/skills -s activity-create -a opencode
```

---

## Usage Examples

### Basic Usage

```
User: I want to create an AI tech sharing event
Assistant: Sure, please provide the event name, time, location...
```

### Complete Conversation Example

```
User: Create a weekend book club event

Assistant: I'll help you create the event. Please provide:
- Event Name: Weekend Book Club
- Start Time: 2026-03-28 14:00
- End Time: 2026-03-28 17:00
- Location: Sanlitun, Chaoyang District, Beijing
- Ticket Price: Free

Event created successfully! View details: https://fore.vip/st?id=xxx
```

---

## Parameters

### MCP Tool: `create_activity`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | Event name/description |
| `start_time` | number | Yes | Start timestamp (milliseconds) |
| `end_time` | number | No | End timestamp (milliseconds) |
| `address` | string | Yes | Event address |
| `range` | number | No | Ticket price in cents (default: 0) |
| `pay` | boolean | No | Payment required visibility (default: false) |

---

## Architecture

```
┌─────────────┐
│   AI Agent  │
│  (Claude/   │
│   Cursor)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ SKILL.md    │
│ (Event Logic)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ MCP Server  │
│ api.fore.vip│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ UniCloud DB │
│ (act collect)│
└─────────────┘
```

---

## Testing

### Local Test

```bash
bash test_local.sh
```

### Online Test

```bash
# Test MCP endpoint
curl https://api.fore.vip/mcp/tools/list

# Test create activity
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "Test Event",
      "start_time": 1711094400000,
      "address": "Beijing"
    }
  }'
```

---

## Files

```
activity-create/
├── SKILL.md           # Main skill doc (English)
├── SKILL_cn.md        # Main skill doc (Chinese)
├── README.md          # Chinese documentation
├── README_en.md       # This file (English docs)
├── INSTALL.md         # Installation guide (CN)
├── INSTALL_en.md      # Installation guide (EN)
├── test_local.sh      # Local test script
└── TEST_CONVERSATION.md  # Conversation test cases
```

---

## Links

| Resource | URL |
|----------|-----|
| Fore.Vip Official | https://fore.vip |
| MCP Server | https://api.fore.vip/mcp |
| Documentation | https://doc.fore.vip |
| Legal Docs | https://doc.fore.vip/legal/ |
| Chrome Extension | https://f.fore.vip/download/fore-ex-v1.1.zip |

---

## License

MIT License

---

**Version**: v0.0.3  
**Last Updated**: 2026-03-21  
**Maintainer**: Fore-Zhixiang (Shenzhen) Technology Co., Ltd.
