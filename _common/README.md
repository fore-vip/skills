# 通用 references · 单一事实源

> 版本 `1.0.0` · 权威源：`~/git/fore.vip/skills/_common/`
> 适用：`fore.vip/skills`、`auto/skills`、`auto/experts` 三个技能家族新建与改造 SKILL 时取用。

## 一、定位：先说清不是什么

本目录是**跨技能通用的参考文档基线**，不是技能、不发布，也不进 `package.json` 的 `skills` 数组。

SKILL 平台只识别技能包内的**单层** `references/`，没有跨技能引用机制。所以本库的用法是「复制基线」，不是运行时依赖：

```
_common/references/xxx.md
  → 复制到 <技能>/references/xxx.md 并按该技能裁剪
  → SKILL.md 正文用 @references/xxx.md 引用
```

技能发布时必须自带所需文档；只在本库引用、不打进技能包，安装版会缺文件。

## 二、文件清单

| 文件 | 主题 | 什么时候读 | 主要事实源 |
|---|---|---|---|
| `compliance.md` | 合规与文案红线 | 出稿、对外文案、上架前 | `auto-hot-script/references/compliance.md`、`contract/compliance-checklist.md`、仓库 AGENTS.md §七 |
| `skill-structure.md` | 目录、frontmatter、引用语法 | 新建技能、补齐元数据 | `auto/skills/AGENTS.md` §六、`fore.vip/skills/README.md` §三、CHANGELOG 2026-09-04 |
| `source-grading.md` | 信源分级与取证纪律 | 调研、检索、评分 | `shuangxiu/references/sources.md`、`gossip/sources.md`、`auto-prompt/sources.md` |
| `report-template.md` | 报告结构与措辞 | 交付报告、结论评审 | `shuangxiu/references/report-template.md`、`enterprise-health/report-template.md` |
| `delivery-gates.md` | 交付、发布、提交闸门 | 改完自测与提交前 | `~/git/AGENTS.md` §三 §五、`auto-h5-builder/references/delivery.md` |
| `visual-style.md` | 视觉、移动端、图表口径 | 做页面、封面、图表 | `USER.md`、`~/git/AGENTS.md` §七、`auto-site-builder/references/style-guide.md` |

`mapping.md` 是现状盘点与合并建议（元数据，不供复制）。`scripts/check_common_refs.py` 是本库自检闸门。

## 三、引用约定

1. 正文资源引用统一写 `@references/xxx.md`、`@scripts/xxx.py`；**代码块内的命令行路径不动**（`python3 scripts/xxx.py` 保持原样）。
2. SKILL.md 结尾设「参考资料」区，把用到的文档汇总列一次；散落在正文里的引用容易变成孤儿。
3. 复制进技能时，在文档首行下方注明 `来源：_common/references/xxx.md @ 1.0.0`，便于回溯与差异比对。
4. 通用件与技能专属件同名时，以技能专属为准；通用件只补不改，不覆盖业务口径。
5. 通用件内不写运行时数据、凭证、内部端点、本机绝对路径。

## 四、版本口径

| 情形 | 动作 |
|---|---|
| 改通用文档内容 | 升库版本第三位（`1.0.0 → 1.0.1`），在本文件「变更记录」写一行 |
| 技能副本自行裁剪 | 副本升自己的 PATCH，不反向改本库 |
| 两仓技能副本不一致 | 以本库为准重新复制，不做双向同步 |
| 新增通用主题 | 加文件 + 补本表 + 补自检脚本期望清单，仍走 PATCH |

不擅自升 MINOR / MAJOR；迁入技能的版本血统按仓库现状口径，不另起一套。

## 五、自检

```bash
python3 scripts/check_common_refs.py
```

退出码 `0` = PASS，`1` = FAIL。脚本会现算三处仓库的 references 数量、副本组数与 `mapping.md` 声明值比对，并检查单层结构、索引一致性与私有信息残留。跨仓统计依赖同机存在另外两个仓库；缺失时给 WARN，可用 `--root` 指定。

## 六、边界

- 不含项目私有信息：网关地址、AppID、内部路径、密钥、部署配置。
- 不替代技能专属 references：评分维度、事件库、云表结构、驱动清单、平台渠道库等仍留在各自技能内。
- 本次只建库与对照表，**不改任何技能正文**；合并路径见 `mapping.md`，执行前单独确认。

## 变更记录

- `1.0.0`（2026-11-13）：建立 6 份通用文档、现状对照表与自检脚本。盘点口径：三处仓库 116 份 references，21 组完全一致副本共 43 个文件。
