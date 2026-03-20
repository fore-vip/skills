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
forevip/skills          # AI 飞花令技能集合
forevip/activity-create # 单独的活动创建技能
```

### 方式 B: 添加到现有仓库

如果你有现有项目，可以在仓库内创建 `skills/` 目录：

```
your-repo/
├── src/
├── package.json
└── skills/              # 新增
    ├── activity-create/
    │   └── SKILL.md
    └── bot-publish/
        └── SKILL.md
```

---

## 2️⃣ 编写 SKILL.md

### 标准目录结构

```
your-repo/
└── skills/
    └── activity-create/
        ├── SKILL.md          # 必需
        ├── LICENSE.txt       # 推荐
        └── preview.png       # 可选 (预览图)
```

### SKILL.md 最小格式

```markdown
---
name: activity-create
description: 创建 AI 飞花令线下活动
license: MIT
---

## 技能说明

此技能帮助创建 AI 飞花令平台的线下活动...

## 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `kid` | string | 关联的机器人 ID |
| `content` | string | 活动介绍 |
| `start_time` | number | 开始时间戳 |
| `end_time` | number | 结束时间戳 |

## 处理流程

1. 收集信息
2. 验证参数
3. 调用云函数
4. 返回结果

## 示例

[具体示例代码]
```

---

## 3️⃣ 提交到 GitHub

### 使用 Git 命令行

```bash
# 克隆或创建仓库
git clone https://github.com/your-username/skills.git
cd skills

# 创建技能目录
mkdir -p skills/activity-create

# 添加 SKILL.md
cp /Users/codes/.jvs/.openclaw/workspace/skills/activity-create/SKILL.md \
   skills/activity-create/

# 提交
git add .
git commit -m "feat: add activity-create skill"
git push origin main
```

### 使用 GitHub 网页

1. 访问 https://github.com/new
2. 创建新仓库 (公开)
3. 点击 "Add file" → "Create new file"
4. 输入路径 `skills/activity-create/SKILL.md`
5. 粘贴 SKILL.md 内容
6. Commit changes

---

## 4️⃣ 验证技能格式

### 使用 skills CLI 测试

```bash
# 安装 CLI
npm install -g npx

# 本地测试
npx skills add ./skills/activity-create --list

# 验证 SKILL.md 格式
npx skills init test-skill
# 对比生成的模板
```

### 在线验证

访问 https://skills.sh 搜索你的仓库：
```
https://skills.sh/<your-username>/<repo-name>
```

---

## 5️⃣ (可选) 提交到 skills.sh 索引

skills.sh 会自动索引 GitHub 上的技能仓库，但你可以主动提交：

### 方式 A: 提交到官方仓库列表

1. Fork https://github.com/vercel-labs/skills
2. 在 `README.md` 的 agent-list 部分添加你的仓库
3. 提交 Pull Request

### 方式 B: 等待自动抓取

skills.sh 会定期抓取 GitHub 上符合格式的仓库，通常 24-48 小时内会显示。

**加快收录的技巧**:
- 使用 `skills` 关键词在仓库描述中
- 在 README 中添加 `agent skills` 标签
- 提交到 https://skills.sh 的反馈渠道

---

## 📦 完整示例

### 示例仓库结构

```
forevip/skills/
├── README.md
├── LICENSE
└── skills/
    ├── activity-create/
    │   ├── SKILL.md
    │   └── preview.png
    ├── bot-publish/
    │   └── SKILL.md
    └── nearby-search/
        └── SKILL.md
```

### README.md 模板

```markdown
# AI 飞花令技能集合

为 AI 飞花令 (fore.vip) 平台创建的 Agent 技能集合。

## 可用技能

| 技能 | 说明 | 安装 |
|------|------|------|
| activity-create | 创建线下活动 | `npx skills add forevip/skills -s activity-create` |
| bot-publish | 发布 AI 机器人 | `npx skills add forevip/skills -s bot-publish` |
| nearby-search | 附近活动搜索 | `npx skills add forevip/skills -s nearby-search` |

## 安装

```bash
# 安装所有技能
npx skills add forevip/skills

# 安装单个技能
npx skills add forevip/skills -s activity-create
```

## 开发

参考 [SKILL.md 标准范式](./skills/SKILL_TEMPLATE.md)
```

---

## 🔍 发布后验证

### 1. 检查 skills.sh 是否收录

访问：
```
https://skills.sh/forevip/skills
```

### 2. 测试安装命令

```bash
# 测试安装 (不实际安装，只列出)
npx skills add forevip/skills --list

# 应该看到:
# ✓ activity-create
# ✓ bot-publish
# ✓ nearby-search
```

### 3. 实际安装测试

```bash
# 创建测试项目
mkdir test-skills && cd test-skills

# 安装技能
npx skills add forevip/skills -s activity-create

# 验证安装
npx skills list
```

---

## ⚠️ 常见问题

### Q: 技能没有立即显示在 skills.sh 上？

**A**: skills.sh 不是实时同步的，需要等待抓取周期 (24-48 小时)。你可以：
- 在 Twitter 上 @VercelLabs 提醒
- 在 GitHub 仓库添加 `skills-sh` 标签
- 提交到 https://github.com/vercel-labs/skills/issues

### Q: 如何更新已发布的技能？

**A**: 直接修改 SKILL.md 并 push 到 GitHub：
```bash
git add skills/activity-create/SKILL.md
git commit -m "docs: update activity-create skill"
git push
```

用户执行 `npx skills update` 即可更新。

### Q: 可以发布私有仓库吗？

**A**: 不支持。skills.sh 只索引公开仓库。

### Q: 需要审核吗？

**A**: 不需要。skills.sh 是开放生态，但建议：
- 遵守 SKILL.md 格式规范
- 添加清晰的 license
- 不包含恶意代码

---

## 🚀 快速发布清单

```bash
# 1. 创建 GitHub 仓库
# 2. 复制 SKILL.md 到 skills/<skill-name>/
# 3. 提交并 push
# 4. 等待 24-48 小时自动收录
# 5. 验证：https://skills.sh/<your-username>/<repo>
```

---

## 📚 相关资源

| 资源 | 链接 |
|------|------|
| skills.sh 官网 | https://skills.sh |
| Vercel Labs 示例 | https://github.com/vercel-labs/agent-skills |
| Anthropic 官方技能 | https://github.com/anthropics/skills |
| CLI 文档 | https://github.com/vercel-labs/skills |

---

**最后更新**: 2026-03-20  
**适用**: skills.sh 平台技能发布
