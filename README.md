# Fore-Vip Agent Skills Collection | AI Agents MCP Server

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.7-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-purple)](https://openclaw.ai/)
[![Hub](https://img.shields.io/badge/Hub-Integration-cyan)](https://hub.ai/)

🤖 **AI Agents Skills** collection for the **Fore-Vip (fore.vip)** platform.

**[中文版本](README_cn.md)** | **English**

---

## 📦 Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [activity-create](activity-create/) | Create offline events (requires Open Key) | v0.0.6 |
| [product](product/) | Query/create products, **auto-publish** with tag | v0.0.7 |

---

## 🔐 Authentication (Open Key)

### Get Open Key

1. Register/Login on [fore.vip](https://fore.vip)
2. Go to **User Center** → **API Settings**
3. Copy your **Open Key**

### Header Format

```http
Authorization: Bearer <your_open_key>
```

or

```http
X-Open-Key: <your_open_key>
```

### Auth Requirements

| Endpoint | Auth |
|----------|------|
| `create_activity` | 🔐 Required |
| `create_kl` | 🔐 Required |
| `query_kl` | ❌ Public |

---

## 🚀 New: Auto Publish (v0.0.7)

**One-tag publishing**: User provides only a tag, Agent handles the rest!

### How It Works

```
User: "发布一个 推荐 标签的产品"
   ↓
1. Agent queries hottest product with tag="推荐"
   ↓
2. Agent extracts best product as template
   ↓
3. Agent shows preview for confirmation
   ↓
4. User confirms
   ↓
5. Agent auto-fills all fields & publishes
   ↓
✅ Success!
```

### Example

**User**: 帮我发布一个"推荐"标签的产品

**Agent**:
```
🔍 查找"推荐"标签下最热门产品...

找到：AI 文案助手 (热度：21307866)
- 描述：请你扮演一个优质 AI 文案助手...
- 图片：2 张

是否以此模板发布？(确认/取消)
```

**User**: 确认

**Agent**:
```
✅ 发布成功！
链接：https://fore.vip/p?id=xxx
```

---

## 🌐 MCP Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/mcp/create_activity` | POST | 🔐 | Create activity |
| `/mcp/create_kl` | POST | 🔐 | Create product |
| `/mcp/query_kl` | POST | ❌ | Query products |
| `/tools/list` | GET | ❌ | List tools |

---

## 📚 Documentation

- **[MCP Spec](https://modelcontextprotocol.io/)**
- **[skills.sh](https://skills.sh/)**
- **[OpenClaw](https://openclaw.ai/)**
- **[Fore-Vip](https://fore.vip/)**

---

## 📝 Version History

### v0.0.7 (2026-03-24) - Auto Publish
- ✅ Added auto-publish workflow
- ✅ Agent can auto-fill from hottest product

### v0.0.6 (2026-03-24) - Open Key Auth
- ✅ Added Open Key authentication docs

---

**Version**: 0.0.7 | **Updated**: 2026-03-24
