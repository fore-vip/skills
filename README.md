# MCP Skills for 前凌智选 (fore.vip)

**Version**: 0.0.9  
**Last Updated**: 2026-03-30

---

## 📦 Available Skills

| Skill | Version | Description | Tools |
|-------|---------|-------------|-------|
| **product-create** | v1.0.0 | Create single product with duplicate check | `query_kl`, `create_kl` |
| **product-auto** | v2.0.0 | Batch push multiple products (no duplicate check) | `create_kl` |

---

## 🚀 Quick Start

### 1. Get Open Key

1. Register/Login on [fore.vip](https://fore.vip)
2. Go to **User Center** → **API Settings**
3. Copy your **Open Key**

### 2. Choose Skill

**Single Product (with duplicate check)**:
```bash
Use skill: product-create
Tools: query_kl + create_kl
```

**Batch Push (no duplicate check)**:
```bash
Use skill: product-auto
Tools: create_kl only
```

---

## 📖 Documentation

- [Full Documentation](DOCUMENTATION.md)
- [Product Create Skill](product-create/SKILL.md)
- [Product Batch Push Skill](product-auto/SKILL.md)

---

## 🔧 MCP Endpoints

**Base URL**: `https://api.fore.vip`

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/tools/list` | GET | ❌ | List available tools |
| `/mcp/query_kl` | POST | ❌ | Query products |
| `/mcp/create_kl` | POST | 🔐 | Create product |

---

## 📝 Version History

### v0.0.9 (2026-03-30)

- ✅ Split `product` skill into (renamed to product-auto):
  - `product-create` (single + duplicate check)
  - `product-auto` (batch push only)
- ✅ Clear skill separation
- ✅ Updated documentation

### v0.0.8 (2026-03-24)

- ✅ Fixed circular dependency
- ✅ External content sources

---

**License**: MIT  
**Contact**: forevip123 (WeChat)
