# Fore-Vip Agent Skills Collection | AI Agents MCP Server

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.5-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-purple)](https://openclaw.ai/)
[![Hub](https://img.shields.io/badge/Hub-Integration-cyan)](https://hub.ai/)

🤖 **AI Agents Skills** collection for the **Fore-Vip (fore.vip)** platform. Compatible with **OpenClaw**, **Hub**, and **MCP Server** protocols. Build **AI products**, create **activities**, and manage **events** with powerful **agent skills**.

**[中文版本](README_cn.md)** | **English**

---

## 🔥 Popular Keywords

**AI Agents** | **Skills** | **MCP Server** | **OpenClaw** | **Hub** | **Product** | **活动 (Activities)** | **Event Management** | **fore.vip** | **AI 智能体** | **产品目录** | **线下活动**

---

## 📦 Available Skills

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [🎯 activity-create](activity-create/) | Create **offline events** & **activities** for fore.vip via **MCP Server**. Perfect for **AI product launches**, **meetups**, **community events**. | v0.0.5 | `npx skills add fore-vip/skills -s activity-create` |
| [📦 product](product/) | Query **AI product catalog** from fore.vip platform. Browse **products**, **AI agents**, **activities** by tag. **SEO-optimized** for **OpenClaw** & **Hub**. | v0.0.3 | `npx skills add fore-vip/skills -s product` |

### Coming Soon

- 🔐 **auth** - User authentication & authorization for **AI Agents**
- 📊 **analytics** - **Product** & **activity** analytics dashboard
- 💬 **chat** - **AI chat** integration with **fore.vip** platform
- 🎫 **ticket** - **Event ticket** management & booking

---

## 🚀 Quick Start

### Install Skills

```bash
# Install specific skill (AI Agents & OpenClaw Compatible)
npx skills add fore-vip/skills --skill activity-create

# Install product query skill
npx skills add fore-vip/skills --skill product

# Install all skills (Hub Integration Ready)
npx skills add fore-vip/skills --all
```

### Usage with AI Agents

Once installed, **AI agents** can automatically use these skills when you ask to:

- 🎯 Create an **offline event** or **meetup**
- 📅 Publish an **activity** on fore.vip platform
- 📦 Query **AI products** by tag (推荐，热门，游戏，etc.)
- 🚀 Launch **AI product** events
- 💬 Schedule **community events** with **WeChat contact**
- 🎫 Create **paid events** with ticket pricing

### OpenClaw Integration

```bash
# OpenClaw compatible skills
# Skills are automatically loaded from ~/.agents/skills/
```

### Hub Integration

```bash
# Hub platform integration
# MCP Server endpoint: https://api.fore.vip/mcp
```

---

## 🌐 MCP Server Configuration

**Base Endpoint**: `https://api.fore.vip/mcp`

**Available Methods**:

| Endpoint | Method | Skill | Description |
|----------|--------|-------|-------------|
| `/mcp/create_activity` | POST | activity-create | Create **offline event** / **activity** |
| `/mcp/query_kl` | POST | product | Query **AI products** catalog |
| `/tools/list` | GET | All | List available **MCP tools** |

### Example: Create Activity

```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI Agents & MCP Skills Meetup",
    "start_time": 1711094400000,
    "address": "Beijing Sanlitun SOHO",
    "wx": "forevip123",
    "range": 0,
    "pay": false
  }'
```

**Response**:
```json
{
  "success": true,
  "id": "69bf8d848a5c785fa8c566cd",
  "url": "https://fore.vip/st?id=69bf8d848a5c785fa8c566cd"
}
```

### Example: Query Products

```bash
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{
    "tag": "推荐",
    "limit": 10,
    "skip": 0
  }'
```

**Response**:
```json
{
  "success": true,
  "total": 10,
  "data": [
    {
      "id": "670703627ae7081fd93d09f1",
      "name": "AI 文案助手",
      "tag": "推荐",
      "url": "https://fore.vip/p?id=670703627ae7081fd93d09f1"
    }
  ]
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AI Agents Layer                        │
│  ┌─────────────┬─────────────┬─────────────────────┐   │
│  │ OpenClaw    │ Hub         │ Other MCP Clients   │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Server Layer                       │
│              api.fore.vip/mcp/*                          │
│  ┌─────────────────────┬─────────────────────────────┐ │
│  │ activity-create     │ product (query_kl)          │ │
│  │ - Create events     │ - Query products            │ │
│  │ - Manage activities │ - Browse catalog            │ │
│  └─────────────────────┴─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                             │
│              UniCloud Database                           │
│  ┌─────────────┬─────────────┬─────────────────────┐   │
│  │ act         │ kl          │ Other Collections   │   │
│  │ (Activities)│ (Products)  │                     │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Documentation

### Core Documentation

- **[MCP Specification](https://modelcontextprotocol.io/)** - Model Context Protocol
- **[skills.sh](https://skills.sh/)** - Agent Skills Directory
- **[OpenClaw](https://openclaw.ai/)** - OpenClaw Platform
- **[Fore-Vip](https://fore.vip/)** - Platform Website
- **[API Docs](https://api.fore.vip/mcp)** - MCP API Reference

### Skill Documentation

| Skill | Docs |
|-------|------|
| activity-create | [activity-create/SKILL.md](activity-create/SKILL.md) |
| product | [product/SKILL.md](product/SKILL.md) |

---

## 🧪 Testing

```bash
# Run local tests for activity-create
cd activity-create
./test_local.sh

# Run local tests for product
cd product
./test_local.sh

# Test MCP Server endpoints
curl https://api.fore.vip/mcp/tools/list
```

---

## 🔧 Development

### Prerequisites

- **Node.js** v18+
- **MCP Server** access
- **fore.vip** account (optional)

### Local Development

```bash
# Clone repository
git clone https://github.com/fore-vip/skills.git
cd skills

# Install dependencies (if any)
npm install

# Run tests
npm test
```

### Skill Template

Use [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) to create new **AI Agent Skills**.

---

## 📝 Version History

### v0.0.5 (2026-03-22) - SEO Optimized

- ✅ **SEO Optimization** for all skill documentation
- ✅ Added **product** skill (v0.0.3) - Query AI product catalog
- ✅ Updated **activity-create** to v0.0.5 with SEO keywords
- ✅ Added **OpenClaw** & **Hub** integration notes
- ✅ Enhanced **MCP Server** documentation
- ✅ Added architecture diagram
- ✅ Updated **keywords**: AI Agents, Skills, MCP, Product, 活动，OpenClaw, Hub

### v0.0.4 (2026-03-22)

- ✅ Update to MCP Server standard
- ✅ Simplify SKILL.md format to follow skills.sh
- ✅ Add test_local.sh script
- ✅ Update endpoint to `/mcp/create_activity`

### v0.0.3 (2026-03-20)

- ✅ Initial release
- ✅ Basic activity creation

---

## 🤝 Contributing

Contributions welcome! Help us build better **AI Agent Skills** for **fore.vip** platform.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-skill`)
3. Commit your changes (`git commit -m 'Add amazing AI skill'`)
4. Push to the branch (`git push origin feature/amazing-skill`)
5. Create a new Pull Request

### Contribution Guidelines

- Follow **MCP Server** protocol standards
- Include **SEO-optimized** documentation
- Add **test_local.sh** for testing
- Support **OpenClaw** & **Hub** integration
- Use **SKILL_TEMPLATE.md** as reference

---

## 🏷️ SEO Keywords

**Primary**: AI Agents Skills, MCP Server, OpenClaw, Hub, fore.vip, Product Catalog, Activity Creation, Event Management, AI 智能体，产品查询，活动创建

**Secondary**: Agent Skills Marketplace, MCP Protocol, AI Product Discovery, Meetup Creation, Tech Events, Community Events, 智能体技能，线下活动

**Long-tail**: How to create events with AI Agents, fore.vip MCP Server integration, OpenClaw product search skill, AI Agents skills for event management

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Website**: https://fore.vip
- **API**: https://api.fore.vip/mcp
- **GitHub**: https://github.com/fore-vip/skills
- **NPM**: https://www.npmjs.com/org/fore-vip
- **Documentation**: https://doc.fore.vip

---

**Maintainer**: wise (AI Agent)  
**Version**: 0.0.5 (SEO Optimized)  
**Last Updated**: 2026-03-22  
**Compatible With**: OpenClaw, Hub, MCP Server, AI Agents  
**Platform**: fore.vip
