# Fore-Vip Agent Skills Collection

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.4-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)

A collection of Agent skills for the Fore-Vip (fore.vip) platform.

**[中文版本](README_cn.md)** | **English**

---

## 📦 Available Skills

| Skill | Description | Version | Install |
|-------|-------------|---------|---------|
| [activity-create](activity-create/) | Create offline events for fore.vip platform via MCP Server | v0.0.4 | `npx skills add fore-vip/skills -s activity-create` |

---

## 🚀 Quick Start

### Install Skill

```bash
# Install specific skill
npx skills add fore-vip/skills --skill activity-create

# Install all skills
npx skills add fore-vip/skills --all
```

### Usage

Once installed, AI agents can automatically use this skill when you ask to:
- Create an offline event
- Publish an activity on fore.vip
- Schedule a meetup

---

## 🔧 MCP Server

**Endpoint**: `https://api.fore.vip/mcp`

**Available Methods**:
- `POST /mcp/create_activity` - Create offline event
- `POST /mcp/query_kl` - Query products

**Example**:
```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI Weekend Meetup",
    "start_time": 1711094400000,
    "address": "Beijing Sanlitun",
    "wx": "forevip123"
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

---

## 📚 Documentation

- **[MCP Specification](https://modelcontextprotocol.io/)** - Model Context Protocol
- **[skills.sh](https://skills.sh/)** - Agent Skills Directory
- **[Fore-Vip](https://fore.vip/)** - Platform Website

---

## 🧪 Testing

```bash
# Run local tests
cd activity-create
./test_local.sh
```

---

## 📝 Version History

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

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Maintainer**: wise  
**Website**: https://fore.vip  
**API**: https://api.fore.vip/mcp
