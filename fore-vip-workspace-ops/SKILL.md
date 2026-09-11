---
name: fore-vip-workspace-ops
slug: workspace-ops
displayName: WorkspaceOps
display_name: 工作区自动化中枢
display_name_en: fore.vip Workspace Automation Hub
description: "把 fore.vip 工作区的日常重复事务变成一条可复跑的命令（fore.vip）。六项原子能力：① audit 工作区体检（仓库矩阵 / mod 只读纪律 / 密钥明文脱敏扫描 / README 路径漂移 / 残留与磁盘）；② skill 技能资产生命周期（list 合规矩阵 / check 发布前自检 / bump PATCH 递进 / owner 归属标注 / index 索引重建）；③ sync 多仓 git 同步（mod 硬拦截）；④ log 记忆回写（日日志 append-only / distill 提炼）；⑤ report 日报周报；⑥ selfcheck 环境自检。零第三方依赖，纯 Python 3 标准库，有 pyyaml 时自动切严格解析。内置项目红线：mod 只读、版本号只走 PATCH、凭证不入库、运行时数据不写安装目录。当用户说「工作区体检 / 巡检一下 / 技能发布前检查 / 版本号递进 / 批量补归属 / 同步提交 / 写工作日志 / 出个日报周报 / 工作区自动化」时使用。"
description_zh: "fore.vip 工作区自动化中枢。六项原子能力：工作区体检（仓库矩阵、只读纪律、密钥明文脱敏扫描、README 漂移、残留与磁盘）、技能资产生命周期（合规矩阵、发布前自检、PATCH 版本递进、归属标注、索引重建）、多仓 git 同步（只读仓硬拦截）、记忆回写（日志追加与提炼）、日报周报、环境自检。零第三方依赖，纯标准库实现。"
description_en: "Automation hub for the fore.vip workspace. Six atomic capabilities: workspace audit (repo matrix, read-only discipline, masked secret scanning, README drift, residue and disk), skill asset lifecycle (compliance matrix, pre-publish check, PATCH version bump, ownership tagging, index rebuild), multi-repo git sync with read-only enforcement, memory writeback (append-only logs and distillation), daily/weekly reports, and environment selfcheck. Pure Python 3 standard library with zero third-party dependencies."
category: development
version: 1.0.0
author: fore.vip
owner: team
agent_created: true
---

# 工作区自动化中枢 · WorkspaceOps

一次调用，跑完 fore.vip 工作区所有可自动化的重复事务。设计原则：**能用脚本跑的绝不手工做，脚本解决不了的才交给 Agent 判断。**

## 零 · 先自检（每次必做第一步）

```bash
PY=/Users/codes/.workbuddy/binaries/python/versions/3.13.12/bin/python3
SK=~/.workbuddy/skills/fore-vip-workspace-ops/scripts/ops.py   # 以实际安装路径为准
test -f "$SK" || echo "脚本缺失，走附录 A 现场生成"
$PY "$SK" selfcheck
```

- 工作区根**自动探测**（同时含 `skills/` 与 `.workbuddy/` 的目录），也可用 `--root` 显式指定或环境变量 `FOREVIP_ROOT`。
- 全部子命令支持 `--json`（`audit` / `skill list` / `skill check`），便于 Agent 结构化消费。
- `audit` 退出码：`0` 无 P0，`1` 存在 P0 —— 可直接用作流水线闸门。

## 一 · 能力矩阵

| 能力 | 命令 | 自动化的事 | Agent 该补的判断 |
|------|------|-----------|-----------------|
| 工作区体检 | `audit` | 仓库矩阵、只读纪律、密钥扫描、路径漂移、残留、磁盘 | 每个 P0 的处置方案与取舍 |
| 技能生命周期 | `skill list/check/bump/owner/index` | 合规矩阵、发布前自检、版本递进、归属标注、索引重建 | 改动说明、CHANGELOG 措辞 |
| 多仓同步 | `sync` | add/commit/push，只读仓硬拦截 | 提交信息、是否 push |
| 记忆回写 | `log append/distill/today` | 追加日志、列出待提炼清单 | 提炼与归并、MEMORY.md 措辞 |
| 日报周报 | `report daily/weekly` | 抽日志标题骨架 | 结论、优先级、下一步 |
| 环境自检 | `selfcheck` | 根目录、技能数、解析器可用性 | — |

## 二 · audit 工作区体检

```bash
$PY "$SK" audit            # 可读输出
$PY "$SK" audit --json     # 结构化
```

检查项与判级：

| 项 | P0 | P1 | P2 |
|----|----|----|----|
| 仓库 | 应有远端的仓无远端 | 有未提交改动 / 落后远端 | 含源码但未纳入 git |
| 只读纪律 | `mod/` 有未提交改动 | — | — |
| 密钥 | 明文密钥命中（**输出自动脱敏**） | — | — |
| 文档 | — | README 引用了不存在的顶层目录 | — |
| 残留 | — | — | `.DS_Store` 聚合计数、拼写错误目录 |
| 磁盘 | — | — | 单目录 > 100MB |

设计要点（踩过的坑，勿回退）：
- **密钥必须脱敏输出**，只打印前 6 位与后 4 位；占位符（`xxx` / `your` / `example` / `${...}`）自动跳过，避免文档示例误报。
- **路径漂移只看顶层引用**：正则前缀排除 `/`，否则 `doc/web/` 里的 `web/` 会被误判成顶层目录缺失。
- **`.DS_Store` 聚合**：不逐条刷屏，只报数量 + 3 个样例目录。

## 三 · skill 技能资产生命周期

```bash
$PY "$SK" skill list                      # 合规矩阵：版本 / 归属 / 缺失字段
$PY "$SK" skill check  <dir>              # 发布前自检
$PY "$SK" skill bump   <dir>              # 版本号 PATCH 递进
$PY "$SK" skill owner  <dir> personal|team
$PY "$SK" skill index                     # 重建 README 技能列表表格
```

`check` 的自检项：

| 级别 | 检查 |
|------|------|
| P0 | frontmatter 可解析；官方必填五字段齐（`description` / `description_zh` / `description_en` / `version` / `author`）；无二级子目录 |
| P1 | skillhub 发布字段齐（`slug` 小写连字符 / `displayName` 驼峰 / `version`）；已标注 `owner` |
| P2 | 有尾部「## 反馈」声明；运行时数据未写入安装目录 |

**版本号只走第三位 PATCH**（`1.0.1 → 1.0.2`），`bump` 自动完成，**禁止手改 MINOR / MAJOR**，除非队长明确要求。

## 四 · sync 多仓同步

```bash
$PY "$SK" sync                     # 全量：base / doc / skills
$PY "$SK" sync --repo skills -m "chore: 同步"
$PY "$SK" sync --no-push           # 只提交不推送
```

- `mod/` 是**只读参照仓**，`sync` 硬拦截，即使 `--force` 也拒绝 —— 不允许绕过。
- 提交信息默认 `chore: 自动化同步 <时间戳>`，可用 `-m` 覆盖。

## 五 · log 记忆回写

```bash
$PY "$SK" log append --title "技能发布" --text "..."
cat note.md | $PY "$SK" log append --title "..."
$PY "$SK" log distill --days 30      # 列出待提炼日志（不自动删除）
$PY "$SK" log today
```

- 写入目标是 `.workbuddy/memory/YYYY-MM-DD.md`，**严格 append-only**，自动补文件头。
- `distill` 只列清单，提炼与删除必须经队长确认后由 Agent 执行 —— 脚本绝不自动删日志。

## 六 · 周期性自动化编排

需要长期巡检时，用 `automation_update` 注册定时任务（不要在 SKILL 里写死时间）。推荐组合：

| 任务 | 频率 | prompt 要点 |
|------|------|------------|
| 工作区体检 | 每日 09:00 | 跑 `audit --json`，有 P0 才推送，无异常静默 |
| 技能合规巡检 | 每周一 10:00 | 跑 `skill list`，列出缺 `owner` 与缺发布字段的技能 |
| 周报 | 每周五 18:00 | 跑 `report weekly`，由 Agent 补结论与下一步 |

注册 prompt 必须自带工作区根路径与脚本路径（未来运行看不到当前对话）。改完自动任务 prompt **必须回读校验转义** —— 反斜杠会被多转义一层。

## 七 · 项目红线（脚本已内置部分，Agent 必须遵守）

1. **`mod/` 只读**：只能抄范式，禁止在 mod 做现状诊断或改动。诊断一律以 `base/` 为准。
2. **凭证不入库**：API Token 只在命令行传入，禁止写进任何仓库文件；`audit` 发现的明文密钥要提示队长轮换，不代为处置。
3. **Vercel 部署**：提交邮箱必须匹配 GitHub 账号（`onsoul <onsoul@qq.com>`），否则静默拦截部署。
4. **行尾符**：多数 `.vue` 是 CRLF，改完务必 `git diff --stat` 复核，出现整文件重写说明行尾符被改坏。
5. **运行时数据不进 SKILL 安装目录**：配置与产物一律落用户目录，平台升级会覆盖安装目录。
6. **事实 / 分析 / 建议分开讲**：体检输出的是事实，处置建议要标明是判断。

## 参考资料

- 技能规范：https://open.workbuddy.cn/docs/skill
- 配套技能：`fore-vip-skill-lint`（frontmatter 批量补齐，本技能 `check` 的判定依据同源）

## 附录 A · 脚本不可用时的等价生成规范

渠道只分发 SKILL.md 时（如 SKILLHUB 安装版无 `scripts/`），Agent 需现场生成一次性脚本，满足：

1. **纯 Python 3 标准库**，零第三方依赖；`pyyaml` 可选，缺失时降级为内置简易 frontmatter 解析。
2. 文件头含 `find_root()`（向上探测同时含 `skills/` 与 `.workbuddy/` 的目录）、`run()`（subprocess 且不抛异常）、`human()`（字节格式化）。
3. `audit` 必须覆盖六类检查与 P0/P1/P2 判级，密钥输出**必须脱敏**，`.DS_Store` **必须聚合**。
4. `skill bump` 只改 PATCH 位；`sync` 必须拦截 `mod/`。
5. 用完即弃，不落盘技能安装目录；临时脚本放系统临时目录。

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
