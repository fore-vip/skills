---
name: h5-app-builder
slug: h5-app-builder
displayName: 主题落地页生成模板
display_name: 主题落地页生成模板
display_name_en: Theme-Driven Landing Page Builder
description: 输入任意主题，动态选择视觉版式并生成一份内容贴合该主题的移动端落地宣传页。适用于「做一个 XX 宣传页 / 落地页」「按主题出页面」「给美容店做个页面」「产品发布页」「换个主题重做一版」等任务。核心能力是主题路由：从 templates/layouts.json 按关键词选版式（暖调生活服务 / 深色科技 / 明快营销 / 杂志编辑），零命中可显式指定或新增版式；内容结构由 spec.sections 顺序决定，生成器不预设任何业务板块。链路 P0 解析主题 → P1 版式路由 → P2 按主题写内容 spec → P3 生成页面与可选云接线 → P4 四道闸门（生成器自检、主题口径与样式一致性静态断言、CDP 真实 390 视口计算样式与交互断言、三档截图目视）→ P5 交付与沉淀。所有控件共用 .ctl 基类并只引用版式 token，保证同一页内圆角/高度/字号/状态严格统一，而不同主题之间风格明显不同。
description_zh: 按用户给的主题自动挑版式、写内容、生成移动端落地宣传页；版式库可扩展，内容不套死模板，页内控件风格统一，附带主题口径与视觉一致性自动闸门。
description_en: "Generate a mobile landing page from any topic: route the topic to a visual layout from an extensible registry, write topic-specific content into a spec, render a single-file page, and pass four automated gates covering content relevance, control-style consistency, real-viewport interaction and visual review."
category: engineering
version: 2.0.0
author: fore.vip
agent_created: true
triggers:
  - "做一个落地页"
  - "做个宣传页"
  - "按主题生成页面"
  - "换个主题重做"
  - "landing page"
  - "产品发布页"
  - "门店宣传页"
  - "美容宣传页"
  - "动态版式"
  - "H5 落地页"
  - "把这个过程做成技能"
---

# 主题落地页生成模板

> **这是什么**：一套「输入主题 → 动态选版式 → 生成贴合主题的移动落地宣传页」的可复跑流程与可执行资产。
> **这不是什么**：不是一套换标签就复用的死模板。**版式、配色、控件形状、叙事顺序、每一句文案都由主题决定**；AUTO / auto.fore.vip 的实现只作为历史参考，本技能不依赖它、不假定它的路径存在。

## 三条硬原则

1. **版式随主题变**：先跑主题路由，再写内容。不同主题必须落到不同 token 集与不同叙事结构，不能用同一套骨架换词。
2. **内容随主题写**：文案由专家按主题现场撰写，写进 `spec`。**禁止把制作过程、生成器、技能、云配置、其他主题的词写进页面正文**。每个 spec 必须自带 `requiredTerms` / `forbiddenTerms` 并过静态闸门。
3. **页内严格统一、跨页允许不同**：同一页里所有可点控件必须走 `.ctl` 基类并只引用 `:root` token，圆角 / 三档高度 / 字号 / 主色 / 状态必须一致；不同版式形状不同是设计意图，不是不一致。

---

## P0 解析主题

从用户输入抽取三件事，缺什么一次性问清，不要分多轮追问：

| 项 | 说明 | 例 |
|---|---|---|
| `topic` | 主题原话，用于版式路由 | 「社区美容店预约宣传页」 |
| 受众与目标 | 给谁看、希望他做什么 | 附近居民 → 预约体验；企业采购 → 预约产品演示 |
| 口径 | 真实上线 / 演示页 / 是否接后端 | 演示页，表单写入演示表 |

事实来源顺序：用户当轮指令 → 待办详情 → 全库与工作区检索 → 项目资产库 → 历史对话。**查不到就如实说查不到**，不臆造需求细节当成事实。

## P1 版式路由（动态设定的核心）

```bash
python3 scripts/pick_layout.py --topic "社区美容门店 护肤 SPA 预约宣传页" --json
```

返回 `id / name / intent / tokens / sectionOrder / matched / score / hits / reason / alternatives`。规则在 `templates/layouts.json`：

- 按关键词命中数选版式，命中词长度加权；平局取注册顺序
- `matched=false` 表示零命中，已用 `default` 兜底并给出理由 → **专家必须确认或新增一套版式**，不能悄悄用兜底交付
- 专家认为路由不合适时，用 `--layout <id>` 或 spec 的 `meta.layoutId` 显式覆盖，并在交付说明里写清理由
- 内置四套：`warm`（美容 / 餐饮 / 生活服务）、`tech`（AI / SaaS / 工具）、`fresh`（活动 / 促销 / 招生）、`editorial`（文化 / 教育 / 咨询）

**新增一套版式只改 `layouts.json`，不改任何脚本**：复制一条 `layouts` 记录，填 `id / name / keywords / intent / sectionOrder / heroAlign / tokens`。token 至少要覆盖 `--bg --card --text --sub --muted --line --line-2 --brand --brand-soft --on-brand --surface --surface-2 --r-card --r-panel --r-pill --h-lg --px-lg --fs-lg --h-md --px-md --fs-md --h-sm --px-sm --fs-sm --focus --shadow --font-title --hero-pad --cols`。这就是「模板选择根据用户主题动态变化」的扩展点。

## P2 按主题写内容 spec

`spec` 是唯一内容源，字段速查：

| 字段 | 作用 |
|---|---|
| `meta.topic` | 版式路由输入 |
| `meta.brand / title / description / footerNote / disclaimer` | 品牌、标题、页脚与口径声明（`disclaimer` 必须出现在正文） |
| `meta.nav / ctaHref / ctaLabel / footerLinks` | 导航、右上行动按钮、页脚 |
| `meta.requiredTerms / forbiddenTerms` | 主题词审计：必备词必须全在、禁用词一个都不能在 |
| `meta.cloud` | 可选：`needed / table / columns / prefix` |
| `hero` | `eyebrow / h1 / em / p / primary / secondary / primaryHref / secondaryHref` |
| `sections` | **数组顺序即页面顺序**；每项 `type / id / title / text / items` |

可用 section：`features`（能力或服务卡）、`showcase`（场景 / 案例）、`stats`（数字）、`steps`（流程）、`quote`（引语）、`faq`（可展开问答）、`cta`（预约 / 留资表单）、`notes`（说明卡）。版式的 `sectionOrder` 是建议顺序，**按主题取舍**，不照抄。

叙事必须线性：**价值主张 → 具体项目 / 能力 → 可信证据 → 行动 → 常见疑问**。不要把「这是什么」放到最后，不要先砸一堆数字再解释，不要把制作过程写进正文。

写 spec 时的自检：
- 每个 section 的文案都读得出主题，换个主题读起来会别扭才算写对
- 品牌统一，页眉 / 页脚 / 正文不出现另一个项目或另一个门店的名字
- 页面里所有数字、称呼、流程都自称「示例」或明确真实，前后不矛盾
- `forbiddenTerms` 至少覆盖：其他主题的典型词、其他项目品牌、制作过程词

## P3 生成页面与可选云接线

```bash
# 纯前端
python3 scripts/build_page.py --spec examples/beauty.spec.json --out index.html

# 显式指定版式（路由不合适时）
python3 scripts/build_page.py --spec x.json --out index.html --layout editorial

# 预约表单写入云端（可选）
python3 scripts/build_page.py --spec x.json --out index.html --cloud-config /tmp/public-config.json
```

生成器做四件事：调用 `pick_layout.choose()` → 把选中 token 覆盖进 `:root` → 按 `sections` 顺序渲染 → 写盘前自检（占位符、标签平衡、零外链、口径声明、JS 语法），**不过就不产出文件**。

云接线判据与步骤见 `references/cloud-service.md`。不接后端时表单会明确提示「没有发送、也不会保存」，绝不假装成功；CDN 加载不出来同样给可见提示。

## P4 四道闸门（缺一不可）

```bash
# ① 生成器自检（已在 build_page.py 内，失败不写盘）
# ② 主题口径 + 叙事顺序 + 控件样式一致性
python3 scripts/verify_static.py --spec x.json --page index.html [--cloud]
# ③ CDP 真实 390 视口：计算样式一致性 + spec.assertions 交互
node scripts/verify_viewport.mjs --spec x.json --url http://127.0.0.1:PORT/index.html --shots /tmp/shot
# ④ 三张截图目视：hero / mid / bottom
```

`verify_viewport.mjs` 会回读所有 `.ctl` 的计算样式，断言页内圆角统一、三档高度各自统一、字号不超过三档、主色按钮底色一致、输入框与控件同高同圆角、零内联样式，再跑 spec 里的业务断言。**换主题只改 spec.assertions**，脚本不动。

目视重点：主题是否一眼可辨、品牌是否统一、叙事顺序是否顺、有无截断 / 溢出 / 错位、控件看起来是否像一家人。自动断言全绿不等于观感合格，必须看图。

## P5 交付与沉淀

- 本地预览用 `python3 -m http.server`，**必须以后台任务方式常驻**；交付时说明「未上线」
- 归档链路：主副本 `~/.workbuddy/skills/h5-app-builder/` → 项目仓库 `fore.vip/skills/` → 专家包内嵌副本 → git 提交（只暂存自己的路径，别裹带他人改动）
- 每次跑出新主题，把 spec 放进 `examples/`，把选版理由与坑写进 `references/`，让下一次更准
- SkillHub 正式发布与站点上线都需用户明确指令，先 `--dry-run` 预演

---

## 目录

```
templates/layouts.json   版式注册表（扩展点：加主题就改这里）
templates/base.css       共享 .ctl 控件层，只引用 token
templates/page.html      页面骨架
scripts/pick_layout.py    主题 → 版式
scripts/build_page.py    spec + 版式 → 单文件 HTML
scripts/verify_static.py 主题口径 / 叙事顺序 / 样式一致性 / 资源边界
scripts/verify_viewport.mjs 真实视口计算样式与交互断言
references/*.md          版式设计、内容红线、云接线、坑、案例
examples/*.spec.json     跑通的主题样例
```

## 已知坑

- 无头 Chrome 用 `--window-size` 会被夹到最小 500px，390 必须用 CDP `Emulation.setDeviceMetricsOverride`
- 云 SDK 的 CDN 在本机时通时不通；页面必须给可见失败提示，且不能把本地操作说成已存云端
- `verify_static.py` 会把 `<script>` / `<style>` 排除后再查主题词，别把技术字符串当正文
- 新增 token 时若 `.ctl` 规则里出现硬编码 px / 色值，静态闸门会直接 FAIL —— 一律抽成变量
- 长稿预检：禁用词 + 英文噪声词差集，跑完再交付

## 版本

- **2.0.0**：改为主题驱动。移除固定 KPI 演示台；新增版式库、主题路由、内容模型、口径与样式双闸门；两个差异主题实例验证通过。
- 1.1.0 / 1.0.0：历史版本，见 git 记录；旧架构已归档，不再作为模板使用。
