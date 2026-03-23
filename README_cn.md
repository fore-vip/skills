# Fore-Vip Agent Skills 集合

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.6-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-purple)](https://openclaw.ai/)
[![Hub](https://img.shields.io/badge/Hub-Integration-cyan)](https://hub.ai/)

🤖 **AI 智能体技能**集合，为 **前凌智选 (fore.vip)** 平台打造。兼容 **OpenClaw**、**Hub** 和 **MCP Server** 协议。

**English** | **[中文版本](README_cn.md)**

---

## 🔥 热门关键词

**AI 智能体** | **技能** | **MCP Server** | **OpenClaw** | **Hub** | **产品** | **活动** | **fore.vip** | **产品目录** | **线下活动**

---

## 📦 可用技能

| 技能 | 说明 | 版本 | 安装 |
|------|------|------|------|
| [🎯 activity-create](activity-create/) | 创建线下活动，需要 **Open Key** 认证 | v0.0.6 | `npx skills add fore-vip/skills -s activity-create` |
| [📦 product](product/) | 查询产品目录，`query_kl` 公开，`create_kl` 需 **Open Key** | v0.0.3 | `npx skills add fore-vip/skills -s product` |

---

## 🔐 认证 (Open Key)

部分 MCP 端点需要 **Open Key 认证**。

### 如何获取 Open Key

1. 在 [fore.vip](https://fore.vip) 平台 **注册/登录**
2. 进入 **用户中心** → **API 设置**
3. **生成**或**复制**你的 **Open Key**
4. 在请求头中包含 Open Key

### Header 格式

使用以下**任一**格式：

```http
Authorization: Bearer <your_open_key>
```

或

```http
X-Open-Key: <your_open_key>
```

### 认证要求

| 端点 | 认证 |
|------|------|
| `create_activity` | 🔐 需要 |
| `create_kl` | 🔐 需要 |
| `query_kl` | ❌ 公开 |
| `/tools/list` | ❌ 公开 |

---

## 🌐 MCP Server 配置

**基础端点**: `https://api.fore.vip/mcp`

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/mcp/create_activity` | POST | 🔐 | 创建活动 |
| `/mcp/create_kl` | POST | 🔐 | 发布产品 |
| `/mcp/query_kl` | POST | ❌ | 查询产品 |
| `/tools/list` | GET | ❌ | 工具列表 |

### 示例（带认证）

```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content":"AI 技术分享会","start_time":1711094400000,"address":"北京","wx":"forevip123"}'
```

---

## 📚 文档

- **[MCP 规范](https://modelcontextprotocol.io/)**
- **[skills.sh](https://skills.sh/)**
- **[OpenClaw](https://openclaw.ai/)**
- **[前凌智选](https://fore.vip/)**

---

## 📝 版本历史

### v0.0.6 (2026-03-24) - Open Key 认证
- ✅ 添加 Open Key 认证文档
- ✅ 更新所有技能的认证要求

### v0.0.5 (2026-03-22) - SEO 优化
- ✅ SEO 优化所有文档

---

**版本**: 0.0.6 | **更新**: 2026-03-24  
**维护者**: wise · 严谨专业版
