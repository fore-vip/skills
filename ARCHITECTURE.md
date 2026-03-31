# MCP Server Architecture

**Version**: v0.0.4  
**Last Updated**: 2026-03-22

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Apps                         │
│  (skills.sh / fore-ex / uni-app / AI Agents)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Method 1: Direct mcp call (Recommended)
                     │ https://api.fore.vip/mcp/*
                     ▼
┌─────────────────────────────────────────────────────────┐
│              mcp Cloud Object (/mcp)                     │
│  Role: Business Logic Layer                              │
│  Methods:                                                │
│  • query_kl() - Query products                           │
│  • create_kl() - Create products                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Method 2: Via tools protocol (MCP Standard)
                     │ https://api.fore.vip/tools/*
                     ▼
┌─────────────────────────────────────────────────────────┐
│              tools Cloud Object (/tools)                 │
│  Role: MCP Protocol Adapter Layer                        │
│  Methods:                                                │
│  • list()     → Return tools list definition             │
│  • call()     → Call mcp methods                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Call Methods Comparison

### Method 1: Direct mcp Call (Recommended) ✅

**Advantages**: Simple, direct, better performance  
**Use Cases**: Frontend, Chrome extension, uni-app

### Method 2: Via tools Protocol (MCP Standard)

**Advantages**: MCP standard compliant, supports tools/list  
**Use Cases**: skills.sh, AI Agent auto-discovery

---

## 📊 Endpoints

| Endpoint | Method | Usage | Recommended |
|----------|--------|-------|-------------|
| `/mcp/query_kl` | POST | Query products | ⭐⭐⭐⭐⭐ |
| `/mcp/create_kl` | POST | Create products | ⭐⭐⭐⭐⭐ |
| `/tools/list` | GET | List tools | ⭐⭐⭐ |

---

## ⚠️ Key Technical Point

**Cloud Object URL Trigger**: POST body is a **string**, must `JSON.parse()`:

```javascript
async query_kl() {
  const httpInfo = this.getHttpInfo();
  const pm = JSON.parse(httpInfo.body);  // String → Object
}
```

---

**Maintainer**: wise  
**Version**: v0.0.4
