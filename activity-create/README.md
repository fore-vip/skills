# activity-create 技能

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![版本](https://img.shields.io/badge/版本-v0.0.3-blue)](https://github.com/fore-vip/skills)
[![下载](https://img.shields.io/badge/下载-插件-blue)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![MCP](https://img.shields.io/badge/MCP-支持-green)](https://modelcontextprotocol.io/)

通过 MCP 协议创建前凌智选线下活动的 Agent 技能。

---

## 📖 简介

`activity-create` 是一个 MCP（Model Context Protocol）技能，允许 AI 助手通过自然语言对话帮助用户创建线下活动。

**核心功能**:
- 通过对话创建活动
- 支持时间、地点、门票配置
- 自然语言交互
- 自动跳转到活动详情页

---

## 🚀 快速开始

### 安装方式

#### 方式 1: 使用 npx 安装

```bash
npx skills add fore-vip/skills -s activity-create
```

#### 方式 2: 全局安装

```bash
npx skills add fore-vip/skills -s activity-create -g
```

#### 方式 3: 安装到指定 Agent

```bash
# Claude Code
npx skills add fore-vip/skills -s activity-create -a claude-code

# Cursor
npx skills add fore-vip/skills -s activity-create -a cursor

# OpenCode
npx skills add fore-vip/skills -s activity-create -a opencode
```

---

## 💡 使用示例

### 基础用法

```
用户：我想创建一个 AI 技术分享活动
助手：好的，请告诉我活动的具体名称、时间、地点等信息...
```

### 完整对话示例

```
用户：创建一个周末读书会活动

助手：好的，我来帮你创建活动。请提供以下信息：
- 活动名称：周末读书会
- 开始时间：2026-03-28 14:00
- 结束时间：2026-03-28 17:00
- 活动地点：北京市朝阳区三里屯
- 门票价格：免费

活动创建成功！查看详情：https://fore.vip/st?id=xxx
```

---

## 📋 参数说明

### MCP 工具：`create_activity`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 活动名称/描述 |
| `start_time` | number | 是 | 开始时间（毫秒时间戳） |
| `end_time` | number | 否 | 结束时间（毫秒时间戳） |
| `address` | string | 是 | 活动地点 |
| `range` | number | 否 | 门票金额（分，默认 0） |
| `pay` | boolean | 否 | 是否支付可见（默认 false） |

---

## 🔧 技术架构

```
┌─────────────┐
│   AI Agent  │
│  (Claude/   │
│   Cursor)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ SKILL.md    │
│ (活动创建逻辑)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ MCP Server  │
│ api.fore.vip│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ UniCloud DB │
│ (act 集合)   │
└─────────────┘
```

---

## 🧪 测试

### 本地测试

```bash
bash test_local.sh
```

### 在线测试

```bash
# 测试 MCP 端点
curl https://api.fore.vip/mcp/tools/list

# 测试创建活动
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "测试活动",
      "start_time": 1711094400000,
      "address": "北京市朝阳区"
    }
  }'
```

---

## 📁 文件结构

```
activity-create/
├── SKILL.md           # 技能主文档（英文）
├── SKILL_cn.md        # 技能主文档（中文）
├── README.md          # 本文件（中文说明）
├── README_en.md       # 英文说明
├── INSTALL.md         # 安装指南（中文）
├── INSTALL_en.md      # 安装指南（英文）
├── test_local.sh      # 本地测试脚本
└── TEST_CONVERSATION.md  # 对话测试用例
```

---

## 🔗 相关链接

| 资源 | 链接 |
|------|------|
| 前凌智选官网 | https://fore.vip |
| MCP Server | https://api.fore.vip/mcp |
| 项目文档 | https://doc.fore.vip |
| 法律文档 | https://doc.fore.vip/legal/ |
| Chrome 插件 | https://f.fore.vip/download/fore-ex-v1.1.zip |

---

## 📄 许可证

MIT License

---

**版本**: v0.0.3  
**最后更新**: 2026-03-21  
**维护者**: 前凌智像（深圳）科技有限公司
