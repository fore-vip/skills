---
name: fore-vip-enterprise-health
display_name: 企业工厂健康度体检
display_name_en: Enterprise & Factory Health Check
description: "企业与工厂全维度健康度体检（fore.vip）。用一套 26 维加权评分模型（企业侧 E1–E10：战略治理·财务·市场销售·产品研发·组织人才·流程运营·供应链·数字化·风险合规·客户服务；工厂侧 F1–F11：生产效能 OEE·质量 FPY/Cpk·设备 MTBF·成本精益·交付 OTIF·现场5S·EHS·人员技能·工艺工程·厂务能源·仓储物流；集团层 G1–G5：投资组合·总部管控·资金管控·多厂对标·干部梯队），按「企业型 / 制造型 / 集团多厂」三条子路线裁剪，问卷自评逐维打分并在有财报或生产报表时用实算指标校准，输出加权总分、红黄绿等级、红旗一票降级、雷达图与 ICE 排序整改清单，最终交付 Markdown 诊断报告加单文件 HTML 可视化报告。触发词：企业体检、工厂体检、企业健康度、工厂健康度、经营体检、经营诊断、企业诊断、工厂诊断、组织健康度、经营状况评估、工厂评估、企业自查、验厂自查、投前尽调自查、企业管理评估、工厂管理评估。"
description_zh: 企业与工厂全维度健康度体检。26 维加权评分模型覆盖企业侧 10 维与工厂侧 11 维，集团多厂另加 5 维管控层；按企业型、制造型、集团多厂三条路线裁剪，问卷自评加实算校准，输出总分等级、红旗降级、雷达图与 ICE 整改清单，交付 Markdown 与 HTML 双报告。
description_en: "A full-spectrum health check for enterprises and factories. A 26-dimension weighted scoring model covering 10 enterprise dimensions, 11 factory-floor dimensions and 5 group-level governance dimensions, routed across three modes (trading/service, manufacturing, multi-site group). Scores come from a structured self-assessment questionnaire calibrated by real financial and production metrics when available, producing a weighted total score, traffic-light grade, red-flag downgrades, a radar chart and an ICE-ranked remediation backlog, delivered as both a Markdown diagnostic report and a single-file HTML report."
category: management
version: 1.0.0
author: fore.vip
agent_created: true
---

# 企业 / 工厂健康度体检

把「这家公司（厂）到底健康不健康」从一句感觉，变成**一张可算分、可对标、可追责的表**。

**能干**：问卷自评打分、实算指标校准、加权总分与红黄绿等级、红旗一票降级、雷达图、ICE 排序整改清单、90 天路线图。
**不能干**：出具审计/法律/安全评价结论（EHS、环保、资质的合规判定必须由有资质第三方出具）；代客做投前尽调的法律意见。报告中须显式标注该边界。

---

## 一、路线路由（先定路线，再开问）

| 主体特征 | 模式 | 跑哪些卡 | 总分合成 |
|---|---|---|---|
| 无生产现场（贸易/服务/科技） | `enterprise` | E 卡 | E × 1.0 |
| 有生产现场（制造型） | `factory` | E 卡 + F 卡 | E × 0.4 + F × 0.6 |
| 2 个及以上厂区/子公司 | `group` | E 卡 + F 卡（**每厂各跑一遍**）+ G 卡 | E × 0.25 + F 各厂均值 × 0.45 + G × 0.30 |

**集团模式铁律**：F 卡按厂区各跑一遍，均值入总分，**最差厂区必须单独披露**——均值会掩盖问题，这是集团评估最常见的信息失真。

---

## 二、工作流程

### 第 1 步 · 锁主体（至多问 1 轮）

必须拿到：**主体名称 / 行业 / 人数规模 / 是否制造型 / 是否多厂区 / 这次体检的触发原因**（如老板自查、投前、接手新厂、客户验厂）。

缺失就一次问全，**禁止逐项轰炸**。用户只给了模糊描述时，先按最可能的路线启动，边采集边校正。

### 第 2 步 · 采集（问卷为主，实算校准）

- **分批提问**：维度多，一次不要问完。按 E 卡 → F 卡（分两批）→ G 卡分批，每批 3–5 个维度，用户答完再发下一批。
- **每个维度读对应评分卡的观察点**，把问题口语化后再问，不要直接甩维度名。
- **用户在某一维答不上来**：标「数据缺失」，列入缺失清单，**禁止用行业均值填充顶替**。
- **用户提供了财报/生产报表**：用 @references/formulas.md 实算，实算值与问卷分冲突时**以实算值为准**，并标注「实算校准」。
- **现场类维度（F6 现场 5S、F7 EHS）提醒用户**：看突击时的状态、夜班状态、角落与柜子内部，不要看通知后的现场。

### 第 3 步 · 打分

统一标尺：**5 优秀 / 4 良好 / 3 合格 / 2 薄弱 / 1 危险 / 0 不适用**。

- **分数必须有证据**。无证据时降一档并标注「待核实」，禁止给无依据高分。
- **0 分（不适用）**：不计入加权，其权重按剩余维度比例重分配。
- **红旗项**：见各评分卡「红旗」段。触发即整体降级，**每条降 1 级**（A→B→…→E 封顶），分数不变、等级变。

### 第 4 步 · 计算

优先跑脚本；脚本不在则按下方等价规范手工算。

```bash
# 检测脚本是否存在（SKILLHUB 单文件渠道可能不随包分发 scripts/）
test -f scripts/score.py && echo "脚本可用" || echo "走手工等价算法"

# 生成输入样例
python3 scripts/score.py --template-demo > /tmp/scores.json
# 填完分数后计算并输出双报告
python3 scripts/score.py -i /tmp/scores.json -o report.md --html report.html --radar radar.svg
```

输入 JSON 关键字段：`org` / `mode`(enterprise|factory|group) / `date` / `auditor` / `dims`（键为 `E1`–`G5`，值为分数或 `{score, note, findings}`）/ `weights`（可选覆盖默认权重）/ `sites`（集团模式各厂 F 卡）/ `red_flags` / `actions`（含 impact·confidence·ease·owner·due·kpi）/ `data_gaps`。

**脚本不可用时的等价算法**：见 @references/report-template.md 第二节，口径与脚本完全一致（剔除 0 分后权重重分配 → 卡内加权 → 按路线合成 → 等级映射 → 红旗降级 → ICE 排序）。

### 第 5 步 · 补定性（脚本不管的部分）

脚本只出量化结果，**以下三节必须手写补上**，规范见 @references/report-template.md：

1. **一句话结论**：最致命短板 + 90 天只做一件事做什么 + 什么都不做最先爆哪里。
2. **根因链**：每个 ≤2 分维度连问 3 个为什么。**禁止停在「员工执行力差」「意识不足」这类伪根因**。
3. **90 天路线图**：0–30 天止血 / 31–60 天建机制 / 61–90 天提指标，每项配**可验证判据**（写「FPY ≥90%」，不写「提升质量意识」）。

### 第 6 步 · 交付

产出 **Markdown 诊断报告 + 单文件 HTML 可视化报告**，用 present_files 呈现，先 HTML 后 Markdown。
HTML 渲染规范（配色、结构、免责声明）见 @references/report-template.md 第三节。交付前按该文件第四节清单自检。

---

## 三、评分模型速查

**等级**：≥4.2 A 健康（绿 `#16a34a`）｜≥3.6 B 亚健康（黄绿 `#84cc16`）｜≥2.8 C 预警（黄 `#eab308`）｜≥2.0 D 病态（橙 `#f97316`）｜<2.0 E 危重（红 `#dc2626`）。

**默认权重**（合计 100，可按行业微调但须在报告中说明理由）：

| E1 战略治理 | E2 财务 | E3 市场销售 | E4 产品研发 | E5 组织人才 | E6 流程 | E7 供应链 | E8 数字化 | E9 风险合规 | E10 客户服务 |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 9 | **17** | 13 | 11 | 11 | 8 | 8 | 8 | 10 | 5 |

| F1 生产效能 | F2 质量 | F3 设备 | F4 成本精益 | F5 交付计划 | F6 现场5S | F7 EHS | F8 人员技能 | F9 工艺工程 | F10 厂务能源 | F11 仓储物流 |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 14 | 14 | 10 | 12 | 12 | 6 | **12** | 7 | 7 | 3 | 3 |

| G1 投资组合 | G2 总部管控 | G3 资金管控 | G4 多厂对标 | G5 干部梯队 |
|:--:|:--:|:--:|:--:|:--:|
| 25 | 20 | 20 | 20 | 15 |

**行业微调**：重资产上调 E2/E7/F3；流程行业（化工/食品）上调 F7/F10；电子组装上调 F2/F9；科技型上调 E4/E5；贸易型上调 E3/E7。

---

## 四、注意事项

- **不越界下结论**：发现疑似偷排、两套账、重大安全隐患时，写「**建议立即委托有资质第三方核查**」，不下「违法」定论。
- **不凑数**：数据缺失就是缺失，缺失本身是风险信号（尤其能耗、质量成本无计量）。
- **不平均主义打分**：全打 3 分等于没做。每份报告至少识别出 2 个 ≤2 分的真短板，否则说明采集不到位。
- **不夸大**：本技能输出的是管理诊断建议，不是认证、不是审计报告。
- **整改项不要超过 12 条进报告**，多的放附录；人一次能推动的事有限。

---

## 五、参考资料

- @references/dimensions-enterprise.md — 企业侧 E1–E10 评分卡：每维评分项、实算指标、红旗项
- @references/dimensions-factory.md — 工厂侧 F1–F11 评分卡：每维评分项、实算指标、红旗项
- @references/dimensions-group.md — 集团层 G1–G5 评分卡：投资组合、总部管控、资金、多厂对标、干部梯队
- @references/formulas.md — 财务与生产指标公式库、行业基准区间、实算值到评分的锚定规则
- @references/report-template.md — 报告定性结构、脚本缺失时的等价算法、HTML 渲染规范、交付自检清单
- scripts/score.py — 加权评分引擎：总分/等级/红旗降级/雷达图 SVG/ICE 排序，Python 标准库即可运行

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
