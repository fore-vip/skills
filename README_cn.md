# AI 飞花令 Agent Skills 集合

为 AI 飞花令 (fore.vip) 平台创建的 Agent 技能集合。

## 📦 可用技能

| 技能 | 说明 | 安装命令 |
|------|------|----------|
| [activity-create](activity-create/SKILL.md) | 创建线下活动 | `npx skills add forevip/skills -s activity-create` |

## 🚀 快速开始

### 安装所有技能

```bash
npx skills add forevip/skills
```

### 安装单个技能

```bash
npx skills add forevip/skills -s activity-create
```

### 列出可用技能

```bash
npx skills add forevip/skills --list
```

## 📁 目录结构

```
skills/
├── README.md                 # 本文件 (英文)
├── README_cn.md              # 本文件 (中文)
├── LICENSE                   # MIT License
├── SKILL_TEMPLATE.md         # SKILL.md 标准模板
├── PUBLISH_GUIDE.md          # 发布指南
└── activity-create/
    ├── SKILL.md              # 英文版技能文档
    ├── SKILL_cn.md           # 中文版技能文档
    ├── TEST_CONVERSATION.md  # 测试对话示例
    └── test_local.sh         # 本地测试脚本
```

## 🛠️ 开发新技能

1. 参考 [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) 了解标准格式
2. 在 `skills/` 目录下创建新的技能文件夹
3. 编写 `SKILL.md` 文件
4. 提交 PR

## 📚 相关项目

| 项目 | 说明 |
|------|------|
| [AI 飞花令](https://fore.vip) | 主平台 |
| [MCP 云函数](../fore/uniCloud-aliyun/cloudfunctions/mcp/) | 服务端技能实现 |

## 🔗 相关链接

- **官网**: https://fore.vip
- **文档**: https://doc.fore.vip
- **MCP 规范**: https://modelcontextprotocol.io/
- **skills.sh**: https://skills.sh

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**维护者**: wise · 严谨专业版  
**最后更新**: 2026-03-20
