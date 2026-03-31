# 如何发布 Skill 到 skills.sh

## 📋 发布流程总览

```
1. 创建 GitHub 仓库
   ↓
2. 按标准格式编写 SKILL.md
   ↓
3. 提交到 GitHub
   ↓
4. (可选) 提交到 skills.sh 索引
```

---

## 1️⃣ 创建 GitHub 仓库

### 方式 A: 独立仓库 (推荐个人/团队)

```bash
# 仓库命名建议
<your-username>/skills          # 个人技能集合
<your-username>/<skill-name>    # 单个技能
```

**示例**:
```
forevip/skills          # AI 技能集合
forevip/product-create  # 单个产品创建技能
```

### 方式 B: 添加到现有仓库

如果你有现有项目，可以在仓库内创建 `skills/` 目录：

```
your-repo/
├── src/
├── package.json
└── skills/              # 新增
    ├── product-create/
    │   └── SKILL.md
    └── product/
        └── SKILL.md
```

---

## 2️⃣ 编写 SKILL.md

参考 [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md)

---

## 3️⃣ 提交到 GitHub

```bash
cd your-repo
git add skills/
git commit -m "feat: add skills"
git push
```

---

## 4️⃣ (可选) 提交到 skills.sh 索引

### 方法 A: 提交 Pull Request

1. Fork https://github.com/zacharysilton/skills
2. 编辑 `registry.json` 添加你的技能
3. 提交 PR

### 方法 B: 使用 CLI 工具

```bash
# 安装 CLI
npm install -g skills-cli

# 添加技能
npx skills add ./skills/product-create --list
```

---

## 📦 技能目录结构

```
skills/
├── product-create/
│   ├── SKILL.md           # 必需
│   ├── SKILL_cn.md        # 中文版本
│   ├── README.md          # 使用说明
│   └── test.sh            # 测试脚本
└── product/
    ├── SKILL.md
    └── SKILL_cn.md
```

---

## ✅ 发布检查清单

- [ ] SKILL.md 符合规范
- [ ] 工具定义完整 (name, description, inputSchema)
- [ ] 执行代码正确 (run 函数)
- [ ] 测试通过
- [ ] 文档完整 (README)
- [ ] 版本号正确

---

## 🔗 相关资源

- [skills.sh 官方文档](https://skills.sh/docs)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [SKILL 模板](SKILL_TEMPLATE.md)

---

**维护者**: wise  
**微信**: forevip123
