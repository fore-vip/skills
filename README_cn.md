# Fore-Vip Agent Skills 集合

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.3-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0-orange)](https://modelcontextprotocol.io/)

为前凌智选 (fore.vip) 平台创建的 Agent 技能集合。

**中文** | **[English Version](README.md)**

---

## 📦 可用技能

| 技能 | 说明 | 版本 | 安装命令 |
|------|------|------|----------|
| [activity-create](activity-create/SKILL.md) | 创建前凌智选线下活动 | v0.0.3 | `npx skills add fore-vip/skills -s activity-create` |

---

## 🚀 快速开始

### 前置要求

- Node.js >= 16
- 已安装 npm 或 npx

### 安装所有技能

```bash
npx skills add fore-vip/skills
```

### 安装单个技能

```bash
npx skills add fore-vip/skills -s activity-create
```

### 列出可用技能

```bash
npx skills add fore-vip/skills --list
```

### 安装到指定 Agent

```bash
# 安装到 Claude Code
npx skills add fore-vip/skills -a claude-code

# 安装到多个 Agent
npx skills add fore-vip/skills -a claude-code -a cursor -a opencode

# 全局安装（所有项目可用）
npx skills add fore-vip/skills -g
```

---

## 🧪 测试

### 测试 MCP 端点

```bash
# 列出可用工具
curl https://api.fore.vip/mcp/tools/list

# 创建活动
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "测试活动",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "北京市朝阳区",
      "range": 0,
      "pay": false
    }
  }'
```

### 测试状态

✅ **全部测试通过** (7/7)

| 类别 | 通过 | 总计 |
|------|------|------|
| 基础功能 | ✅ 3 | 3 |
| 错误处理 | ✅ 3 | 3 |
| 边界情况 | ✅ 1 | 1 |

---

## 📁 目录结构

```
skills/
├── README.md                 # 英文说明
├── README_cn.md              # 中文说明（本文件）
├── README_ACTIVITY.md        # activity-create 使用指南
├── LICENSE
├── SKILL_TEMPLATE.md         # SKILL.md 标准模板
├── PUBLISH_GUIDE.md          # 发布指南
├── DOCUMENTATION.md          # MCP 文档
└── activity-create/
    ├── SKILL.md              # 英文技能文档
    ├── SKILL_cn.md           # 中文技能文档
    ├── INSTALL.md            # 安装指南（中文）
    ├── INSTALL_en.md         # 安装指南（英文）
    ├── README.md             # 技能说明（中文）
    ├── README_en.md          # 技能说明（英文）
    ├── TEST_CONVERSATION.md  # 对话测试
    └── test_local.sh         # 本地测试脚本
```

---

## 🛠️ 开发新技能

### 1. 创建技能结构

```bash
mkdir -p your-skill-name
cd your-skill-name
```

### 2. 编写 SKILL.md

参考 [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) 格式：

```markdown
---
name: your-skill-name
description: 技能功能描述
version: 0.0.1
license: MIT
---

## 描述
...

## 参数
...

## 使用示例
...
```

### 3. 本地测试

```bash
bash your-skill-name/test_local.sh
```

### 4. 提交 PR

1. 提交更改
2. 创建 Pull Request
3. 等待审核

---

## 📚 相关项目

| 项目 | 说明 |
|------|------|
| [前凌智选](https://fore.vip) | 主平台 |
| [MCP Server](https://api.fore.vip/mcp) | MCP API 端点 |
| [项目文档](https://doc.fore.vip) | 平台文档 |
| [法律文档](https://doc.fore.vip/legal/) | 服务条款与隐私政策 |

---

## 🔗 资源链接

- **MCP 规范**: https://modelcontextprotocol.io/
- **skills.sh 目录**: https://skills.sh/github/fore-vip/skills
- **Agent Skills 规范**: https://agentskills.io
- **uniCloud 文档**: https://doc.dcloud.net.cn/uniCloud/

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**官网**: https://fore.vip  
**文档**: https://doc.fore.vip  
**API**: https://api.fore.vip/mcp  
**Skills**: https://skills.sh/github/fore-vip/skills

---

*最后更新：2026-03-21*
