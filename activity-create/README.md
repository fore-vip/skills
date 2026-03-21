# activity-create 技能

[![版本](https://img.shields.io/badge/版本-v0.0.3-blue)](https://github.com/fore-vip/fore-ex)
[![下载](https://img.shields.io/badge/下载-插件-blue)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![MCP](https://img.shields.io/badge/MCP-支持-green)](https://modelcontextprotocol.io/)

通过 MCP 协议创建前凌智选线下活动的 Agent 技能。

---

## 📖 简介

`activity-create` 是一个 MCP（Model Context Protocol）技能，允许 AI 助手通过自然语言对话帮助用户创建线下活动。

**核心功能**:
- 🎯 通过对话创建活动
- 📍 支持时间、地点、门票配置
- 💬 自然语言交互
- 🔗 自动跳转到活动详情页

---

## 🚀 快速开始

### 安装方式

#### 方式 1: 使用 npx 安装

```bash
npx skills add fore-vip/skills -s activity-create
```

#### 方式 2: 使用 Chrome 插件（推荐）

对于普通用户，建议使用 Chrome 浏览器插件：

- **下载**: [fore-ex-v1.1.zip](https://f.fore.vip/download/fore-ex-v1.1.zip)
- **安装指引**: [INSTALL.md](./INSTALL.md)
- **GitHub**: https://github.com/fore-vip/fore-ex

---

## 📋 使用示例

### 对话示例

```
用户：我想创建一个周末 AI 体验活动

助手：好的！我来帮你创建这个 AI 体验活动。请问：
   1. 活动什么时候开始？(日期和具体时间)
   2. 预计持续多久？(结束时间)
   3. 活动地点在哪里？(可选)
   4. 是否收取门票？(可选)
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | ✅ | 活动标题/描述 |
| `start_time` | number | ✅ | 开始时间（毫秒时间戳） |
| `end_time` | number | ⚪ | 结束时间（毫秒时间戳） |
| `address` | string | ✅ | 活动地址 |
| `range` | number | ⚪ | 门票价格（分，0 表示免费） |
| `pay` | boolean | ⚪ | 是否支付可见 |

---

## 📁 文件结构

```
activity-create/
├── SKILL.md              # 技能定义（英文）
├── SKILL_cn.md           # 技能定义（中文）
├── README.md             # 项目说明（本文件）
├── INSTALL.md            # 安装指引（中文）
├── INSTALL_en.md         # 安装指引（英文）
├── test_local.sh         # 本地测试脚本
└── TEST_CONVERSATION.md  # 测试对话记录
```

---

## 🧪 测试

### 本地测试

运行测试脚本：

```bash
./test_local.sh
```

测试内容：
- ✅ SKILL.md 文件检查
- ✅ MCP 端点连通性
- ✅ 工具列表获取
- ✅ 创建活动功能

### 在线测试

访问 MCP 端点：

```bash
# 获取工具列表
curl https://api.fore.vip/mcp/tools/list

# 调用工具
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": { ... }
  }'
```

---

## 🔄 版本历史

### v0.0.3 (2026-03-20)

**优化**
- ✅ 完善 MCP 协议实现
- ✅ 添加错误处理
- ✅ 优化响应格式

### v0.0.2 (2026-03-19)

**新增**
- ✅ 添加中文技能定义
- ✅ 添加本地测试脚本

### v0.0.1 (2026-03-18)

**首发版本**
- ✅ 基础活动创建功能
- ✅ MCP 协议集成

---

## 📞 技术支持

| 渠道 | 链接 |
|------|------|
| **官网** | https://fore.vip |
| **GitHub** | https://github.com/fore-vip/fore-ex |
| **问题反馈** | https://github.com/fore-vip/fore-ex/issues |
| **MCP 规范** | https://modelcontextprotocol.io/ |

---

## 📄 许可证

MIT License

Copyright (c) 2026 前凌智选

---

**通过自然语言，轻松创建活动！** 🎉

最后更新：2026-03-21
