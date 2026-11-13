# references 现状盘点与合并建议

> 来源：`_common/mapping.md @ 1.0.0` · 盘点日：2026-11-13
> 统计口径：三处技能包内的 `references/` 目录（含 `_archive` 历史基线），**不含本通用库自身**；副本判定按文件字节的 MD5 一致。

<!-- STATS total=116 fore.vip/skills=55 auto/skills=37 auto/experts=24 dup_groups=21 dup_files=43 cross_root_groups=21 -->

## 一、事实：分布

| 仓库 | 份数 | 说明 |
|---|---|---|
| `fore.vip/skills` | 55 | 前凌智选技能家族，含 `_archive/huoli` 历史件 |
| `auto/skills` | 37 | AUTO 技能家族 |
| `auto/experts` | 24 | 专家包内嵌的技能副本 |
| **合计** | **116** | |

字节完全一致的副本 **21 组、43 个文件**，且 21 组全部跨仓库（同一份文档在 `auto/skills` 与 `auto/experts`，或 `fore.vip/skills` 与 `auto/experts` 各存一份）。重名出现 3 次以上的文件：

| 文件名 | 次数 | 是否同一内容 |
|---|---|---|
| `sources.md` | 4 | 否，各技能信源不同，方法层同构 |
| `report-template.md` | 4 | 部分是副本 |
| `dimensions.md` | 4 | 部分是副本，评分维度属技能专属 |
| `mcp.json` | 3 | 否，配置各异 |
| `providers.md` | 3 | 否，厂商清单各异 |
| `crm-api.md` | 3 | 否，两个服务口径不同 |

## 二、事实：三类归档

| 类别 | 代表文件 | 判定 |
|---|---|---|
| A 方法层可抽取 | `sources.md`（4）、`report-template.md`（4）、`writing-guide.md`（2）、`style-guide.md`（2）、`compliance.md`、`compliance-checklist.md`、`delivery.md`（2） | 方法、结构、红线可通用；细节仍属技能专属 → 已抽象进本库 6 份文档 |
| B 项目耦合 | `crm-api.md`（3）、`crm-system.md`（2）、`providers.md`（3）、`mcp.json`（3）、`hosting.md`（2）、`cloud-schema.md`（2）、`app-spec.md`（2）、`events.json`、各类 `*.json` 配置与样例 | 含网关、内部表、端点、单技能契约或运行时数据 → **禁止通用化** |
| C 技能专属 | `dimensions-*.md`、`pet-*.md`、`playbook.md`、`rights-cn.md`、`narrative-*.md`、`fraud-typology.md` 等 | 业务口径，留在原技能 |

同名不等于同内容：`sources.md` 四份内容不同，只是方法同构；`dimensions.md` 四份中部分是同一技能的副本，部分是不同评分卡。**按文件名批量合并会串味**。

## 三、分析：重复的根因

1. 专家包内嵌技能副本（`auto/experts/*/skills/*/references/`）与 `auto/skills` 同源，但没有同步机制，版本靠人工对齐。
2. 跨仓库没有共同的方法层事实源，合规、目录、信源、报告口径散在 AGENTS.md、README、CHANGELOG 与各技能文档里，新建技能时只能各写一遍。
3. 平台只认技能包内单层 `references/`，无法做运行时共享；因此「共享」只能落在**单一事实源 + 复制基线**，不能靠引用路径解决。

## 四、建议（本次不执行）

| 优先级 | 动作 | 触发条件 | 风险 |
|---|---|---|---|
| 1 | 新建或改造技能时，从本库复制所需通用件，按 `README.md` 约定标注来源与版本 | 下一次技能改动 | 低，单技能范围 |
| 2 | 给 21 组完全一致副本补「权威源 + 版本」标注，避免继续漂移 | 相关技能下一次发布前 | 中，涉及两仓与专家包内嵌 |
| 3 | 评估批量去重（副本改为生成时复制，不入库） | 队长明确指令后 | 高：跨 2 个 git 仓库 + 专家包内嵌，影响面不确定，属必须先确认的类型 |

本次交付范围止于建库与对照表，**未改任何技能正文、未删除任何副本、未动另外两个仓库**。

## 五、复核方式

```bash
python3 scripts/check_common_refs.py
```

脚本会现算上面的 STATS 各项并与本文件声明值比对；数字不一致即判 FAIL。盘点结论为**事实**，根因与优先级为**分析**，未执行的三项为**建议**。
