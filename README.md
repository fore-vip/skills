# Fore-Vip Agent Skills Collection

[![Version](https://img.shields.io/badge/version-0.0.8-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)

**[中文版本](README_cn.md)** | **English**

---

## 📦 Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [activity-create](activity-create/) | Create offline events | v0.0.6 |
| [product](product/) | Query/create products, **smart publish** | v0.0.8 |

---

## 🔐 Authentication (Open Key)

1. Login on [fore.vip](https://fore.vip)
2. User Center → API Settings
3. Copy Open Key

```http
Authorization: Bearer <your_open_key>
```

---

## 🚀 Smart Publish (v0.0.8)

**Content from external sources** (NOT from existing products):

| Source | Example |
|--------|---------|
| **AI Generation** | AI creates product from tag |
| **Search Engine** | Google/Bing search results |
| **Session Context** | User's conversation |
| **GitHub** | Trending repositories |
| **Product Hunt** | Daily hot products |

### Example

```
User: 发布一个"AI 工具"标签的产品

Agent:
🤖 正在生成内容...

📦 产品预览:
- 名称：智能写作助手 Pro
- 描述：基于最新 AI 技术的写作助手...
- 标签：AI 工具

是否确认发布？(确认/取消)

User: 确认

Agent:
✅ 发布成功！
```

---

## 🌐 MCP Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `/mcp/query_kl` | ❌ | Query products |
| `/mcp/create_kl` | 🔐 | Create product |
| `/mcp/create_activity` | 🔐 | Create activity |

---

## 📝 Version History

### v0.0.8 (2026-03-24) - Smart Publish
- ✅ External content sources (AI, search, GitHub)
- ✅ Fixed circular dependency

### v0.0.7 (2026-03-24)
- ⚠️ Deprecated (circular dependency)

---

**Version**: 0.0.8 | **Updated**: 2026-03-24
