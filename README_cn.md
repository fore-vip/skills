# Fore-Vip Agent Skills 集合

[![Version](https://img.shields.io/badge/version-0.0.8-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)

**English** | **[中文版本](README_cn.md)**

---

## 📦 可用技能

| 技能 | 说明 | 版本 |
|------|------|------|
| [activity-create](activity-create/) | 创建线下活动 | v0.0.6 |
| [product](product/) | 查询/发布产品，**智能发布** | v0.0.8 |

---

## 🔐 认证 (Open Key)

1. 登录 [fore.vip](https://fore.vip)
2. 用户中心 → API 设置
3. 复制 Open Key

```http
Authorization: Bearer <your_open_key>
```

---

## 🚀 智能发布 (v0.0.8)

**内容来自外部来源**（不是现有产品）：

| 来源 | 示例 |
|------|------|
| **AI 生成** | AI 根据标签创作 |
| **搜索引擎** | Google/必应搜索结果 |
| **会话上下文** | 用户对话内容 |
| **GitHub** | 热门开源项目 |
| **Product Hunt** | 每日热门产品 |

### 示例对话

```
用户：发布一个"AI 工具"标签的产品

Agent:
🤖 正在生成内容...

📦 产品预览:
- 名称：智能写作助手 Pro
- 描述：基于最新 AI 技术的写作助手...
- 标签：AI 工具

是否确认发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
```

---

## 🌐 MCP 端点

| 端点 | 认证 | 说明 |
|------|------|------|
| `/mcp/query_kl` | ❌ | 查询产品 |
| `/mcp/create_kl` | 🔐 | 发布产品 |
| `/mcp/create_activity` | 🔐 | 创建活动 |

---

## 📝 版本历史

### v0.0.8 (2026-03-24) - 智能发布
- ✅ 外部内容来源（AI、搜索、GitHub）
- ✅ 修复循环依赖问题

### v0.0.7 (2026-03-24)
- ⚠️ 已弃用（循环依赖）

---

**版本**: 0.0.8 | **更新**: 2026-03-24  
**维护者**: wise · 严谨专业版
