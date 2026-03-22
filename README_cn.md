# Fore-Vip Agent Skills 集合

[![Skills](https://img.shields.io/badge/skills-fore--vip%2Fskills-blue)](https://skills.sh/github/fore-vip/skills)
[![Version](https://img.shields.io/badge/version-0.0.4-blue)](https://github.com/fore-vip/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Server-orange)](https://modelcontextprotocol.io/)

为 Fore-Vip (fore.vip) 平台创建的 AI 智能体技能集合。

**English** | **[中文版本](README_cn.md)**

---

## 📦 可用技能

| 技能 | 说明 | 版本 | 安装命令 |
|------|------|------|----------|
| [activity-create](activity-create/) | 通过 MCP Server 为 fore.vip 平台创建线下活动 | v0.0.4 | `npx skills add fore-vip/skills -s activity-create` |

---

## 🚀 快速开始

### 安装技能

```bash
# 安装特定技能
npx skills add fore-vip/skills --skill activity-create

# 安装所有技能
npx skills add fore-vip/skills --all
```

### 使用方式

安装后，AI 智能体在以下场景会自动使用此技能：
- 创建线下活动
- 在 fore.vip 发布活动
- 安排聚会

---

## 🔧 MCP Server

**端点**: `https://api.fore.vip/mcp`

**可用方法**:
- `POST /mcp/create_activity` - 创建线下活动
- `POST /mcp/query_kl` - 查询产品

**示例**:
```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI 周末聚会",
    "start_time": 1711094400000,
    "address": "北京三里屯",
    "wx": "forevip123"
  }'
```

**响应**:
```json
{
  "success": true,
  "id": "69bf8d848a5c785fa8c566cd",
  "url": "https://fore.vip/st?id=69bf8d848a5c785fa8c566cd"
}
```

---

## 📚 文档

- **[MCP 规范](https://modelcontextprotocol.io/)** - Model Context Protocol
- **[skills.sh](https://skills.sh/)** - Agent 技能目录
- **[Fore-Vip](https://fore.vip/)** - 平台官网

---

## 🧪 测试

```bash
# 运行本地测试
cd activity-create
./test_local.sh
```

---

## 📝 版本历史

### v0.0.4 (2026-03-22)
- ✅ 更新为 MCP Server 标准
- ✅ 简化 SKILL.md 格式，符合 skills.sh 规范
- ✅ 添加 test_local.sh 测试脚本
- ✅ 更新端点为 `/mcp/create_activity`

### v0.0.3 (2026-03-20)
- ✅ 初始版本
- ✅ 基础活动创建功能

---

## 🤝 贡献

1. Fork 仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**维护者**: wise  
**官网**: https://fore.vip  
**API**: https://api.fore.vip/mcp
