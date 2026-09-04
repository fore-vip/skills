---
name: fore-vip-skill-lint
display_name: 技能规范校验
display_name_en: Skill Spec Lint
description: 批量校验并补齐 SKILL.md 的 frontmatter，使其符合 open.workbuddy.cn/docs/skill 官方技能规范。先按官方必填字段表扫描差距（description / description_zh / description_en / version / author），用 yaml.safe_load 严格解析实测（不靠正则），再幂等批量补齐，最后全量复验。内置半角冒号炸 YAML、块标量插入点、BOM 与行尾符等已踩过的坑。当用户说「检查技能规范 / 补齐 frontmatter / SKILL.md 合规 / 技能批量体检 / 发布前检查 / skill lint / 技能字段缺失」时使用。
description_zh: 批量校验并补齐 SKILL.md 的 frontmatter，使其符合官方技能规范。按必填字段表扫描差距，用 yaml.safe_load 严格解析实测，幂等批量补齐后全量复验。覆盖长文本引号、块标量、BOM、行尾符等常见坑。
description_en: "Batch-validate and backfill SKILL.md frontmatter against the official skill spec at open.workbuddy.cn/docs/skill. Scans for gaps across the required field table, verifies with real yaml.safe_load parsing (never regex), applies idempotent batch fixes, then re-validates everything. Covers known pitfalls: bare long scalars containing a colon-space, block scalar insertion points, BOM and line endings."
category: development
version: 1.0.0
author: fore.vip
agent_created: true
---

# 技能规范校验 · frontmatter 批量体检与补齐

把「这批 SKILL 合规吗」变成一次可复跑的体检。规范依据：https://open.workbuddy.cn/docs/skill

## 官方字段表（判断依据）

| 字段 | 必填 | 说明 |
|------|------|------|
| `description` | **是** | 写清用途**和触发词** |
| `description_zh` | **是** | 简短中文介绍 |
| `description_en` | **是** | A Brief English Introduction |
| `version` | **是** | 语义化版本号，如 `1.0.0` |
| `author` | **是** | 合作方名称 |
| `name` | 否 | 技能标识 |
| `allowed-tools` | 否 | 工具白名单（逗号分隔） |
| `disable-model-invocation` | 否 | true 则仅手动调用 |
| `user-invocable` | 否 | false 则隐藏菜单 |

仓库惯例叠加（非规范必填，但保持一致）：`display_name` / `display_name_en` / `category` / `agent_created: true`。

## 工作流程

### 第 1 步 · 扫描差距

读每个 `<skill>/SKILL.md`，正则取出 frontmatter，按字段表比对，输出差距表（缺失项 / 当前 version / 有无 category）。

### 第 2 步 · 严格解析实测（不可跳过）

**必须用 `yaml.safe_load` 解析 frontmatter**，不能用正则或「字段存在性」判断通过。

原因：字段在文本里存在 ≠ YAML 能解析。曾出现「正则扫描 29/29 全 OK，实测 10 个解析失败」的情况。

```python
# 隔离 venv（勿污染用户环境）
# python3 -m venv ~/.workbuddy/binaries/python/envs/default
# ~/.workbuddy/binaries/python/envs/default/bin/pip install pyyaml
import yaml
yaml.safe_load(frontmatter_text)   # 抛异常即不合格
```

### 第 3 步 · 幂等批量补齐

**写脚本做，不要逐个 Edit。** 理由：① 量大；② 可 dry-run 预检；③ 规避并行 Edit 静默覆盖（同一文件并行多次 Edit，工具回报 success 但只有最后一次落盘）。

脚本要点：
- **幂等**：已存在的字段绝不覆盖；重复执行无副作用。
- **行插入**：在 `description` 字段结束行之后插入 `description_zh` / `description_en` / [`category`] / [`version`] / [`author`]。
- **dry-run 先行**：加 `--apply` 才落盘，先打印插入位置与内容预览。
- 写完**必须复跑第 2 步**校验。

### 第 4 步 · 全量复验 + 变更记录

复跑扫描，确认「必填字段全齐 / YAML 解析通过 / 分类覆盖」三项达标；`git diff --stat` 确认是小增量（正常 2–8 行/文件），出现整文件重写说明行尾符被改动，需修复。

## 已踩过的坑（照做可避）

### 坑 1 · 半角「冒号+空格」炸掉 YAML（最高频）

长文本字段裸写时，值内一旦出现半角 `: `（如 `Pipeline: clarify`、`protocol: drivers`、`list: requirement`），YAML 直接报 `mapping values are not allowed here`。

**规则：长文本字段值一律双引号包裹**，内部 `"` 与 `\` 转义：

```python
'"%s"' % val.replace("\\", "\\\\").replace('"', '\\"')
```

中文全角冒号「：」安全，无需处理。

### 坑 2 · 块标量插入点

`description: |` 或 `description: >` 是多行块，插入点**必须退到 frontmatter 末尾**，不能插在块中间，否则破坏结构。

```python
if re.match(r"^description:\s*[|>]\s*$", line):
    anchor = len(front_lines)     # 退到末尾
else:
    anchor = desc_end_index + 1
```

### 坑 3 · BOM 与行尾符

- frontmatter 可能带 `\ufeff` BOM，正则需允许并原样回填。
- 行尾符要先探测再原样写回，否则整文件 diff 变重写：

```python
eol = "\r\n" if "\r\n" in front_text else "\n"
```

### 坑 4 · description_zh 不是 description 的复制

`description` 是「用途 + 触发词」的完整说明，`description_zh` 要求是**简短**介绍、`description_en` 是其英文对应。撰写时按正文与 H1 提炼，不照抄长描述。

## 补齐脚本骨架

以下为可直接在临时目录运行的一次性脚本骨架（用完即弃，不落盘技能目录）：

```python
import os, re
ROOT = "<skills 根目录>"
TARGET = ("description", "description_zh", "description_en")

def read_front(p):
    t = open(p, encoding="utf-8", newline="").read()
    m = re.match(r"^(\ufeff)?---(\r?\n)(.*?)\r?\n---\r?\n", t, re.S)
    return t, m

def parse_fields(front_lines):
    """{field: [start, end_exclusive]}，支持多行值"""
    idx, keys = {}, []
    for i, line in enumerate(front_lines):
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            idx[m.group(1)] = [i, i + 1]; keys.append(m.group(1))
        elif keys and line.strip():
            idx[keys[-1]][1] = i + 1
    return idx

def write_back(p, t, m, bom, eol, front_lines):
    out = "%s---%s%s%s---%s%s" % (bom, eol, eol.join(front_lines), eol, eol, t[m.end():])
    open(p, "w", encoding="utf-8", newline="").write(out)
```

## 注意事项

- **不擅自改已有值**：`author` 若非 `fore.vip`（如 `WISE`）属历史设定，保留不动。
- **不臆造分类**：`category` 仅对定位明确的技能补，拿不准就留空。
- **只补该补的**：规范未要求的字段（`triggers` / `compatibility` / `tags` 等）属既有扩展，不删不改。

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
