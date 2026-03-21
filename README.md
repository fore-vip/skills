# Fore-Vip Agent Skills Collection

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.3-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0-orange)](https://modelcontextprotocol.io/)

A collection of Agent skills created for the Fore-Vip (fore.vip) platform.

**[中文版本](README_cn.md)** | **English**

---

## 📦 Available Skills

| Skill | Description | Version | Install Command |
|-------|-------------|---------|-----------------|
| [activity-create](activity-create/SKILL.md) | Create offline events for fore.vip platform | v0.0.3 | `npx skills add fore-vip/skills -s activity-create` |

---

## 🚀 Quick Start

### Prerequisites

- Node.js >= 16
- npm or npx installed

### Install All Skills

```bash
npx skills add fore-vip/skills
```

### Install Single Skill

```bash
npx skills add fore-vip/skills -s activity-create
```

### List Available Skills

```bash
npx skills add fore-vip/skills --list
```

### Install to Specific Agents

```bash
# Install to Claude Code
npx skills add fore-vip/skills -a claude-code

# Install to multiple agents
npx skills add fore-vip/skills -a claude-code -a cursor -a opencode

# Global install (available across all projects)
npx skills add fore-vip/skills -g
```

---

## 🧪 Testing

### Test MCP Endpoints

```bash
# List available tools
curl https://api.fore.vip/mcp/tools/list

# Create activity
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "Test Event",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "Beijing",
      "range": 0,
      "pay": false
    }
  }'
```

### Test Status

✅ **All tests passed** (7/7)

| Category | Passed | Total |
|----------|--------|-------|
| Basic Functionality | ✅ 3 | 3 |
| Error Handling | ✅ 3 | 3 |
| Edge Cases | ✅ 1 | 1 |

---

## 📁 Directory Structure

```
skills/
├── README.md                 # This file (English)
├── README_cn.md              # Chinese version
├── README_ACTIVITY.md        # activity-create usage guide
├── LICENSE
├── SKILL_TEMPLATE.md         # SKILL.md Standard Template
├── PUBLISH_GUIDE.md          # Publishing Guide
├── DOCUMENTATION.md          # MCP Documentation
└── activity-create/
    ├── SKILL.md              # English skill doc
    ├── SKILL_cn.md           # Chinese skill doc
    ├── INSTALL.md            # Installation guide (CN)
    ├── INSTALL_en.md         # Installation guide (EN)
    ├── README.md             # Skill README (CN)
    ├── README_en.md          # Skill README (EN)
    ├── TEST_CONVERSATION.md  # Conversation tests
    └── test_local.sh         # Local test script
```

---

## 🛠️ Developing New Skills

### 1. Create Skill Structure

```bash
mkdir -p activity-create
cd activity-create
```

### 2. Write SKILL.md

Follow the [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) format:

```markdown
---
name: your-skill-name
description: What your skill does
version: 0.0.1
license: MIT
---

## Description
...

## Parameters
...

## Usage Examples
...
```

### 3. Test Locally

```bash
bash activity-create/test_local.sh
```

### 4. Submit PR

1. Commit your changes
2. Create a pull request
3. Wait for review

---

## 📚 Related Projects

| Project | Description |
|---------|-------------|
| [Fore-Vip](https://fore.vip) | Main Platform |
| [MCP Server](https://api.fore.vip/mcp) | MCP API Endpoints |
| [Documentation](https://doc.fore.vip) | Platform Docs |
| [Legal Docs](https://doc.fore.vip/legal/) | Terms & Privacy |

---

## 🔗 Resources

- **MCP Specification**: https://modelcontextprotocol.io/
- **skills.sh Directory**: https://skills.sh/github/fore-vip/skills
- **Agent Skills Spec**: https://agentskills.io
- **uniCloud Docs**: https://doc.dcloud.net.cn/uniCloud/

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Website**: https://fore.vip  
**Documentation**: https://doc.fore.vip  
**API**: https://api.fore.vip/mcp  
**Skills**: https://skills.sh/github/fore-vip/skills

---

*Last updated: 2026-03-21*
