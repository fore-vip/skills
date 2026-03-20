# Fore-Vip Agent Skills 集合

[![Version](https://img.shields.io/badge/version-0.0.2-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0-orange)](https://modelcontextprotocol.io/)

为 前凌智选 (fore.vip) 平台创建的 Agent 技能集合。

**中文** | **[English Version](README.md)**

---

## 📦 可用技能

| 技能 | 说明 | 版本 | 安装命令 |
|------|------|------|----------|
| [activity-create](skills/activity-create/SKILL.md) | 创建 前凌智选线下活动 | v0.0.2 | `npx skills add fore-vip/skills -s activity-create` |

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

---

## 🧪 测试

### 测试 MCP 端点

```bash
# 获取工具列表
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
      "address": "北京",
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
| 边界测试 | ✅ 1 | 1 |

---

## 📁 目录结构

```
skills/
├── README.md                 # 英文版
├── README_cn.md              # 中文版 (本文件)
├── README_ACTIVITY.md        # activity-create 使用指南
├── LICENSE
├── SKILL_TEMPLATE.md         # SKILL.md 标准模板
├── PUBLISH_GUIDE.md          # 发布指南
└── skills/
    ├── activity-create/
    │   ├── SKILL.md          # 英文技能文档
    │   ├── SKILL_cn.md       # 中文技能文档
    │   ├── TEST_CONVERSATION.md  # 对话测试
    │   └── test_local.sh     # 本地测试脚本
    └── ...                   # 更多技能
```

---

## 🛠️ 开发新技能

### 1. 创建技能结构

```bash
mkdir -p skills/你的技能名称
cd skills/你的技能名称
```

### 2. 编写 SKILL.md

参考 [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) 格式：

```markdown
---
name: 你的技能名称
description: 技能功能描述
version: 0.0.1
license: MIT
---

## 说明
...

## 参数
...

## 使用示例
...
```

### 3. 本地测试

```bash
bash skills/activity-create/test_local.sh
```

### 4. 提交 PR

1. 提交你的修改
2. 创建 Pull Request
3. 等待审核

---

## 📚 相关项目

| 项目 | 说明 |
|------|------|
| [前凌智选](https://fore.vip) | 主平台 |
| [MCP 服务器](https://api.fore.vip/mcp) | MCP API 端点 |
| [文档](https://doc.fore.vip) | 平台文档 |

---

## 🔗 资源链接

- **MCP 规范**: https://modelcontextprotocol.io/
- **skills.sh**: https://skills.sh
- **uniCloud 文档**: https://doc.dcloud.net.cn/uniCloud/

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**官网**: https://fore.vip  
**文档**: https://doc.fore.vip  
**API**: https://api.fore.vip/mcp

---

*最后更新：2026-03-20*
