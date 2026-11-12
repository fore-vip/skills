---
name: h5-app-builder
slug: h5-app-builder
displayName: H5 应用创建模板
display_name: H5 应用创建模板
display_name_en: Mobile H5 App Builder Kit
description: 把一个只有标题的模糊需求，做成可点开的移动 H5 应用，并把创建全过程沉淀下来。适用于「做一个 XX H5」「把 XX 做成可运行原型」「加一个移动端页面」「H5 落地页 / 场景页 / 演示页」等任务。标准链路 P0 需求锚定（查待办详情 / 全库检索 / 资产库 / 历史对话，仍缺失才一次性结构化确认）→ P1 形态决策（纯前端原型 vs 需要云服务的真实应用，给出判据与激活步骤，确认框被取消时不重试不降级）→ P2 页面构建（spec JSON 驱动，单文件 HTML、零外链、移动优先，三段式 TAB：现场演示 / 使用方式 / 说明与边界）→ P3 接线登记（仅当目标是既有站点时适用：入口卡、分享卡、sitemap、一致性清单、发布闸门）→ P4 验证（结构自检 + 断链 + 真实 390 视口交互断言 + 截图目视）→ P5 交付沉淀（本地预览、发布预演、未上线状态说明、回写 SKILL / 专家 / 记忆）。内置可复跑的生成器、视口断言脚本、参考案例与红线清单，换一份 spec 就能换一个业务。
description_zh: 把模糊的「做一个 XX H5」变成可点开、可验证、可交付的移动应用：需求锚定 → 形态决策（是否需要云服务）→ spec 驱动生成单文件页面 → 接线登记 → 真实视口交互断言 → 发布预演与沉淀归档。含模板、脚本与红线清单，换个业务只改配置。
description_en: "Turn a vague build-me-an-H5 request into a clickable, verifiable, deliverable mobile app: anchor requirements, decide prototype vs cloud-backed app, generate a single-file page from a spec JSON, wire registrations, run real-viewport interaction assertions, rehearse publishing, and persist the playbook. Ships templates, scripts, case study and guardrails; swap the spec to swap the business."
category: engineering
version: 1.1.0
author: fore.vip
agent_created: true
triggers:
  - "做一个 H5"
  - "做个 H5 应用"
  - "可运行原型"
  - "交互原型"
  - "场景页"
  - "移动落地页"
  - "H5 演示页"
  - "把这个过程做成技能"
  - "应用创建流程"
---

# H5 应用创建模板

> **这是什么**：一套「从需求标题到可交付应用」的可复跑流程，加可直接用的模板与脚本。
> **这不是什么**：不是任何特定站点的附属脚本。**AUTO / auto.fore.vip 的模板、闸门与发布脚本只作为参考实现**列在 `references/case-store-h5.md` 与 `references/gates-and-pitfalls.md`，本技能不依赖它们、不假定它们的路径存在、不把它们当硬闸门。目标是任何独立的移动 H5 应用。

## 定位与边界

| 要做 | 不做 |
|---|---|
| 把模糊需求收敛成一份 `app.spec.json` | 替用户臆造需求细节并当成事实 |
| 生成单文件、零外链、可离线打开的 HTML | 引第三方 CDN / 字体 / 图表库当运行前提 |
| 明确区分「示例数据原型」与「真实能力」 | 做看起来能点、实际没有的安装 / 付费 / 提交按钮 |
| 用真实视口跑交互断言再交付 | 只截图一张就宣称「已验证」 |
| 如实标注上线状态 | 把「代码已提交」说成「已上线」 |
| 把本次做法回写成可复用资产 | 一次性交付完就结束 |

**口径铁律**：只要页面里有示例数据，首屏、演示区、说明区三处都要写明「示例数据 / 刷新复位 / 未开放安装（若确实未开放）」。不写就是误导。

---

## P0 需求锚定

拿到任务先按顺序查，不要一上来就问用户：

1. 待办详情（有 id 就读详情）；2. 工作区与项目根目录检索同名目录/文件；
3. 项目资产库 / 网盘检索；4. 历史对话检索相关讨论；5. 现有 README / AGENTS / CHANGELOG。

**判据**：四处都无定义，才做**一次**结构化确认，一次问清「落在哪 / 交付到什么深度」，不要挤牙膏式追问。确认结果写进 spec 的 `meta.decision`，后续所有措辞以它为准。

**常见坑**：详情接口未挂载时只能拿到标题；此时不要把「没读到」说成「没有需求」，要如实记录读不到，并把确认结果作为事实源。

---

## P1 形态决策（含云服务）

先判「这个应用要不要后端」，判据只有四条，命中任意一条即需要云服务：

- 数据要跨刷新保留（清单、记录、设置、订单）；
- 要有用户体系（注册登录、按人隔离）；
- 要传文件并拿到可访问链接；
- 要免密钥调用大模型。

**纯静态页、纯前端交互、无持久化 → 不激活后端**。这是规范，不是偷懒；但必须把结论**主动告诉用户**，不能默默略过。

需要后端时按平台规范走：`inspect` → 选定应用（reuse/create）→ `activate`（**由平台确认框收集授权，禁止自己用问答替代**）→ 拿到 `publicConfig` 后才写云代码。单文件 HTML 用 CDN 形式初始化一次 client，`endpoint` / `publishableKey` 必须来自 `publicConfig`，web 登录还要带 `oauthRelayBaseUrl`；建表与 RLS 走管理侧工具，业务代码只做 CRUD。

**确认框被取消 / 能力不可用**：这是正常结果，**不重试、不换工具绕路、不静默降级成 localStorage 还宣称已接后端**。如实记录为「本轮未接入云端，保持纯前端」，并把接入步骤留在 spec 与报告里。

**确认框通过**：拿到 `billingStatus=normal` / `provisionStatus=assigned` 与 `publicConfig` 后才写云代码。建表与 RLS 走管理侧工具；单文件页面用生成器的 `--cloud-config` 接上 CDN SDK 与 CRUD 适配层。模板内置了该分支，实例见 `references/case-beauty-h5.md`，步骤与坑见 `references/cloud-service.md`。

---

## P2 页面构建（spec 驱动）

复制 `templates/app.spec.json` 改成新业务，然后：

```bash
python3 scripts/build_app.py --spec templates/app.spec.json --out index.html
```

生成器做四件事：读 spec → 拼装 `templates/shell.html` 的四个占位块 → **写盘前自检**（占位符清零、标签平衡、外链受控、JS 语法、声明口径存在）→ 输出单文件 `index.html`。自检不过直接非零退出，不产出半截文件。

**云适配层**：给 `--cloud-config <publicConfig.json>` 就启用，表名取 `--cloud-table` 或 `spec.meta.cloud.table`。生成器只把 `endpoint` / `oauthRelayBaseUrl` / `publishableKey` 三个端上可用值写进页面，注入唯一的 SDK CDN 脚本、初始化一次 client、把演示区的待办动作接到 `upsert`，并在页面上显示云端连通状态与所有失败原因。纯前端模式仍严格零外链；云模式只允许这一条 SDK 白名单。

```bash
python3 scripts/build_app.py --spec app.spec.json --out index.html --cloud-config publicConfig.json
```

**换业务只改 spec**：三段 TAB 文案、演示维度、数字、待办、话术规则、柱图提示（`demo.lowLabel`）、视口断言全部在 spec 里；`meta.cloud` 记录本轮云结论。已验证的两个实例：自动门店（纯前端）与美容台账（接通云端）。

三段式 TAB 是默认骨架，不是强制：**现场演示**（可点的数据）/ **使用方式**（怎么唤起、分几步、轻重分级）/ **说明与边界**（现在到哪一步、数据从哪来、会不会动真账、能不能装）。第二、三段是将来接真实能力时的落点，别省。

演示数据一律放 spec 的 `demo` 节点，不要散在 HTML 里；切维度、改状态、说一句话给回话，都由生成器注入的脚本按数据渲染。换业务只改 spec，不改生成器。

---

## P3 接线登记（**可选适配层**）

只有「目标是已有站点」才做，独立应用直接跳过。需要做时按清单逐项勾，别漏：

- [ ] 首页 / 导航入口卡
- [ ] 分享卡（OG 图）与 meta 信息
- [ ] sitemap 或路由登记
- [ ] 结构一致性清单（若该站点有 parity 检查）
- [ ] 站内兄弟页互链
- [ ] 发布闸门的预演

> AUTO 站点的 `scene.html` / `gen_og.py` / `sync_sitemap.py` / `deploy.sh -n` 是**一个已验证的参考实现**，步骤与坑见 `references/case-store-h5.md`。换站点就换成该站点自己的对应物。

---

## P4 验证（四道，都要有证据）

| # | 检查 | 命令 / 方式 | 通过标准 |
|---|---|---|---|
| 1 | 生成自检 | `python3 scripts/build_app.py …` | 非零退出即阻断 |
| 2 | 静态引用 | 自建断链检查或 `check_assets.py` 同思路 | 本地引用零 404；运行依赖只允许云 SDK 白名单，导航/元信息外链只登记 |
| 3 | 真实视口交互断言 | `node scripts/verify_viewport.mjs --spec <spec> --url <本地URL> --wait 6000` | 全部 PASS，含「无横向溢出」；云页面要留足 SDK 加载时间 |
| 4 | 截图目视 | 断言脚本自动出图，PC / 390 各看一遍 | 无截断、无重叠、无错位 |

**视口坑**：无头浏览器 `--window-size=390` 常被夹到最小 500 逻辑宽度，截图看着像内容被裁其实是假象。必须用 CDP 的 `Emulation.setDeviceMetricsOverride` 强制真实 390×844，再回读 `innerWidth` 确认。脚本模板在 `scripts/verify_viewport.mjs`，断言从 JSON 读，换业务只改断言。

交付话术里要写清断言项数、视口尺寸、有无溢出，不能只说「测过了」。

---

## P5 交付与沉淀

1. 起本地静态服务（需常驻后台），给出可点开的预览地址；
2. 跑发布**预演**（不写入），列出待传对象并核对有没有无谓重传；
3. 明确写「**未上线**」，并给出一条可执行的上线命令；发布是对外动作，**必须有明确指令才执行**；
4. 回写：本次做法 → 本 SKILL（若发现新坑）/ 专家包 / 项目记忆；按既有链路归档项目目录 → 入 git → 需要时发布 SkillHub。

---

## 资源清单

| 路径 | 用途 |
|---|---|
| `templates/app.spec.json` | 配置模板：元信息、首屏、三段 TAB 文案、演示数据、话术规则、断言 |
| `templates/shell.html` | 单文件页面骨架（自带 CSS，四个占位块，零外链） |
| `scripts/build_app.py` | spec → HTML 生成器，含写盘前自检与可选云适配层 |
| `scripts/verify_viewport.mjs` | CDP 真实视口 + 参数化交互断言 + 截图 |
| `references/cloud-service.md` | 云服务判据、激活流程、取消后的正确处置 |
| `references/gates-and-pitfalls.md` | 验证闸门、口径红线、本机工具链已知坑 |
| `references/case-store-h5.md` | 参考案例：自动门店 H5 的完整复盘（AUTO 仅作参考） |
| `references/case-beauty-h5.md` | 参考案例：美容台账（云服务接通版）完整复盘 |
| `examples/beauty.spec.json` | 第二个实例配置：只换数据就换业务，含云字段与可配柱图提示 |
| `examples/` | 用本模板生成并经四道验证跑通的实例页面 |

## 验收清单（交付前逐条打勾）

- [ ] spec 里的 `meta.decision` 与用户确认的方向一致
- [ ] 示例数据 / 未开放能力，三处口径都写明
- [ ] 生成自检、断链、交互断言、截图目视四项都有输出
- [ ] `innerWidth` 回读确认为目标宽度，且 `scrollWidth <= 视口宽`
- [ ] 云模式：每个初始化点都从 `publicConfig` 取值，且写库后读回、失败提示可见
- [ ] CDN 不通时不把本地交互说成已接云端，且页面给出可见原因
- [ ] 云服务结论（接了 / 没接 / 取消）已明确告知用户，写入读回有证据，无静默降级
- [ ] 上线状态如实，未发布不写成已发布
- [ ] 沉淀物（SKILL / 专家 / 记忆）已归档

## 反馈

前凌智选 · SKILLHUB.cn
