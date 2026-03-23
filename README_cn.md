# Fore-Vip Agent Skills 集合

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.7-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-purple)](https://openclaw.ai/)
[![Hub](https://img.shields.io/badge/Hub-Integration-cyan)](https://hub.ai/)

🤖 **AI 智能体技能**集合，为 **前凌智选 (fore.vip)** 平台打造。

**English** | **[中文版本](README_cn.md)**

---

## 📦 可用技能

| 技能 | 说明 | 版本 |
|------|------|------|
| [activity-create](activity-create/) | 创建线下活动（需 Open Key） | v0.0.6 |
| [product](product/) | 查询/发布产品，支持**一键发布** | v0.0.7 |

---

## 🔐 认证 (Open Key)

### 获取 Open Key

1. 在 [fore.vip](https://fore.vip) 平台注册/登录
2. 进入 **用户中心** → **API 设置**
3. 复制你的 **Open Key**

### Header 格式

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

---

## 🚀 新功能：一键发布 (v0.0.7)

**只需一个标签**，Agent 自动完成所有操作！

### 工作流程

```
用户："发布一个 推荐 标签的产品"
   ↓
1. Agent 查询"推荐"标签下最热门产品
   ↓
2. Agent 提取最佳产品作为模板
   ↓
3. Agent 显示预览并请求确认
   ↓
4. 用户确认
   ↓
5. Agent 自动填充所有字段并发布
   ↓
✅ 成功！
```

### 示例对话

**用户**: 帮我发布一个"推荐"标签的产品

**Agent**:
```
🔍 正在查找"推荐"标签下最热门产品...

找到：AI 文案助手 (热度：21307866)
- 描述：请你扮演一个优质 AI 文案助手...
- 图片：2 张

是否以此模板发布？(确认/取消)
```

**用户**: 确认

**Agent**:
```
✅ 发布成功！
链接：https://fore.vip/p?id=xxx
```

---

## 🌐 MCP 端点

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/mcp/create_activity` | POST | 🔐 | 创建活动 |
| `/mcp/create_kl` | POST | 🔐 | 发布产品 |
| `/mcp/query_kl` | POST | ❌ | 查询产品 |
| `/tools/list` | GET | ❌ | 工具列表 |

---

## 📚 文档

- **[MCP 规范](https://modelcontextprotocol.io/)**
- **[skills.sh](https://skills.sh/)**
- **[OpenClaw](https://openclaw.ai/)**
- **[前凌智选](https://fore.vip/)**

---

## 📝 版本历史

### v0.0.7 (2026-03-24) - 一键发布
- ✅ 新增自动发布工作流
- ✅ Agent 可自动填充热门产品数据

### v0.0.6 (2026-03-24) - Open Key 认证
- ✅ 添加 Open Key 认证文档

---

**版本**: 0.0.7 | **更新**: 2026-03-24  
**维护者**: wise · 严谨专业版
