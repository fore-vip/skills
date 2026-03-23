# Fore-Vip Agent Skills Collection | AI Agents MCP Server

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.6-blue)](https://github.com/fore-vip/skills)
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
| [🎯 activity-create](activity-create/) | Create **offline events** & **activities** for fore.vip via **MCP Server**. Requires **Open Key** authentication. | v0.0.6 | `npx skills add fore-vip/skills -s activity-create` |
| [📦 product](product/) | Query **AI product catalog**. `query_kl` is public, `create_kl` requires **Open Key**. | v0.0.3 | `npx skills add fore-vip/skills -s product` |

---

## 🔐 Authentication (Open Key)

Some MCP endpoints require **Open Key authentication** via HTTP headers.

### How to Get Open Key

1. **Register/Login** on [fore.vip](https://fore.vip) platform
2. Go to **User Center** → **API Settings**
3. **Generate** or **copy** your **Open Key**
4. Include it in request headers

### Header Format

Use **either** format:

```http
Authorization: Bearer <your_open_key>
```

or

```http
X-Open-Key: <your_open_key>
```

### Authentication Requirements

| Endpoint | Auth |
|----------|------|
| `create_activity` | 🔐 Required |
| `create_kl` | 🔐 Required |
| `query_kl` | ❌ Public |
| `/tools/list` | ❌ Public |

---

## 🌐 MCP Server Configuration

**Base Endpoint**: `https://api.fore.vip/mcp`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/mcp/create_activity` | POST | 🔐 | Create activity |
| `/mcp/create_kl` | POST | 🔐 | Create product |
| `/mcp/query_kl` | POST | ❌ | Query products |
| `/tools/list` | GET | ❌ | List tools |

### Example (with Auth)

```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content":"AI Meetup","start_time":1711094400000,"address":"Beijing","wx":"forevip123"}'
```

---

## 📚 Documentation

- **[MCP Spec](https://modelcontextprotocol.io/)**
- **[skills.sh](https://skills.sh/)**
- **[OpenClaw](https://openclaw.ai/)**
- **[Fore-Vip](https://fore.vip/)**

---

## 📝 Version History

### v0.0.6 (2026-03-24) - Open Key Auth
- ✅ Added Open Key authentication docs
- ✅ Updated all skills with auth requirements

### v0.0.5 (2026-03-22) - SEO
- ✅ SEO optimization

---

**Version**: 0.0.6 | **Updated**: 2026-03-24
