# 前凌智选技能集合

为 前凌智选 (fore.vip) 平台创建的 Agent 技能集合。

## 📦 可用技能

| 技能 | 说明 | 安装命令 |
|------|------|----------|
| [activity-create](skills/activity-create/SKILL.md) | 创建 前凌智选线下活动 | `npx skills add fore-vip/skills -s activity-create` |

## 🚀 快速开始

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

## 📁 目录结构

```
skills/
├── README.md
├── LICENSE
├── SKILL_TEMPLATE.md       # SKILL.md 标准范式
├── PUBLISH_GUIDE.md        # 发布指南
└── skills/
    ├── activity-create/
    │   └── SKILL.md        # 活动创建技能
    └── ...                 # 更多技能
```

## 🛠️ 开发新技能

1. 参考 [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) 了解标准格式
2. 在 `skills/` 目录下创建新技能文件夹
3. 编写 `SKILL.md` 文件
4. 提交 PR

## 📚 相关项目

| 项目 | 说明 |
|------|------|
| [前凌智选](https://fore.vip) | 主平台 |
| [MCP 云函数](https://github.com/fore-vip/skills) | 服务端技能实现 |

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

**官网**: https://fore.vip  
**文档**: https://doc.fore.vip
