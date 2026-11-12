---
name: h5-app-builder
slug: h5-app-builder
displayName: 主题落地页生成模板
display_name: 主题落地页生成模板
display_name_en: Theme-Driven Landing Page Builder
description: 输入任意主题，判定交付形态（应用 / 站点 / 草稿），按主题关键词路由版式，写出主题专属内容，生成单文件移动端页面；判定为应用时接通云后端、建表并跑写入读回，最后过五道闸门并由 verify_delivery.py 给出 DELIVERED / DRAFT / INCOMPLETE 三态判定。版式库可扩展（暖调生活服务 / 深色科技 / 明快营销 / 杂志编辑），控件共用 .ctl 基类并只引用版式 token，页内统一、跨页随主题不同。
description_zh: 按主题动态选版式、写内容并生成可交付的移动端宣传页；含交付形态契约、云后端接通、五道闸门与三态判定。
description_en: "Turn any topic into a deliverable mobile landing page: declare the delivery form, route the topic to a layout from an extensible registry, write topic-specific content, generate a single-file page, attach a cloud backend when the delivery form is an app, then pass five gates ending in a three-state delivery verdict."
category: engineering
version: 3.1.0
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
  - "做成应用"
  - "创建一个应用"
  - "可发布应用"
  - "把这个过程做成技能"
---

# 主题落地页生成模板

输入主题 → 定交付形态 → 选版式 → 写内容 → 生成页面 → 按需创建应用 → 过五道闸门 → 交付。

适用：给任意主题做移动端落地宣传页；需要时连带创建带云后端的应用。

## 一、完成定义

交付形态必须在 `meta.deliverable` 显式声明，与用户诉求一致：

| 形态 | 判定信号 | 必做 |
|---|---|---|
| `webapp` | 应用 / 上线 / 发布 / 可访问 / 能收预约 / 留资 / 落库 / 后端 | P3.5 全套 + 真实站点地址 + 云端表单 |
| `site` | 部署到已有站点 / 官网 | 站点地址 + 部署记录 + 五道闸门 |
| `draft` | 先看看效果 / 做个草稿 / 只要设计 | 表单整体禁用 + 转应用步骤 |

**默认是 `webapp`。** 用户没说草稿时不得自行降级；信息不足就判 INCOMPLETE 并一次性索要缺失事实。

三条硬约束：

1. 第一个动作是「建交付目录 + 写 spec」，不是先输出设计方案。文案、结构图、首页草图都不算交付物。
2. 判定为 `webapp` 就必须走 P3.5。确认框被取消时停在 INCOMPLETE，不重试、不绕路、不静默降级成 localStorage 后谎称已接后端。
3. `verify_delivery.py` 是最终裁判。`DELIVERED` 才允许写「已交付」；`DRAFT` 标题必须写「页面草稿，不是应用」；`INCOMPLETE` 禁止汇报完成，只列缺项与补齐命令。①②③④ 闸门全绿只证明页面质量，不证明应用存在。

汇报口径：未上线写未上线，示例数据写示例数据，表单禁用写未开放。「已激活云服务 / 代码已提交 / 预演通过」都不等于上线。

## 二、四条原则

1. **形态先定**：先判 `deliverable` 再选版式。
2. **版式随主题变**：先跑主题路由再写内容；不同主题必须落到不同 token 集与不同叙事结构；零命中要确认或新增版式，不悄悄用兜底。
3. **内容随主题写、事实有来源**：文案按主题现场撰写；店名 / 地址 / 电话 / 营业时间 / 项目 / 时长 / 价格 / 经营承诺 / 顾客评价一律不得臆造，逐条登记 `meta.facts` 并标 `source`。正文不写制作过程、技术词、其他主题的词。
4. **页内统一、跨页不同**：同页所有可点控件走 `.ctl` 基类并只引用 `:root` token；不同版式形状不同是设计意图。

## P0 解析主题与定形态

从输入抽取四项，缺什么一次性问清，不分多轮：

| 项 | 说明 | 写入 |
|---|---|---|
| 主题原话 | 用于版式路由 | `meta.topic` |
| 受众与目标 | 给谁看、希望他做什么 | `meta.intent`（保留用户原话） |
| 交付形态 | 应用 / 站点 / 草稿 | `meta.deliverable` |
| 业务事实 | 店名、地址、价目、承诺、评价由谁提供 | `meta.facts` |

事实来源顺序：用户当轮指令 → 待办详情 → 全库与工作区检索 → 项目资产库 → 历史对话。查不到就如实说明并一次性给出「待补事实清单」，不用示例值冒充真实信息。

`meta.facts` 每条形如 `{ "key": "价目", "value": "¥198 起", "source": "example" }`，`source` 取 `user` / `placeholder` / `example`。含 `example` 的页面必须 `factReview: true` 且 `disclaimer` 写明「示例 / 演示」，交付说明附待补清单；这类页面是演示应用，不得作为真实门店对外发布。

## P1 版式路由

```bash
python3 scripts/pick_layout.py --topic "社区美容门店 护肤 SPA 预约宣传页" --json
```

返回 `id / name / intent / tokens / sectionOrder / matched / score / hits / reason / alternatives`。规则在 `templates/layouts.json`：按关键词命中数选版式，长词加权，平局取注册顺序。`matched=false` 表示零命中已兜底 → 必须确认或新增版式。专家判断不合适时用 `--layout <id>` 或 `meta.layoutId` 覆盖并说明理由。

**新增版式只改 `layouts.json`，不动脚本**：复制一条记录，填 `id / name / keywords / intent / sectionOrder / heroAlign / tokens`。token 至少覆盖 `--bg --card --text --sub --muted --line --line-2 --brand --brand-soft --on-brand --surface --surface-2 --r-card --r-panel --r-pill --h-lg --px-lg --fs-lg --h-md --px-md --fs-md --h-sm --px-sm --fs-sm --focus --shadow --font-title --hero-pad --cols`。细节见 `references/layouts.md`。

## P2 写内容 spec

spec 是唯一内容源：

| 字段 | 作用 |
|---|---|
| `meta.topic / intent / brand / title / description` | 主题、诉求原话、品牌、标题 |
| `meta.deliverable / siteUrl / facts / factReview` | 交付形态、真实站点、业务事实来源、示例评审标记 |
| `meta.footerNote / disclaimer` | 页脚与口径声明；`disclaimer` 必须与 `cta.note` 逐字一致并原样出现在正文 |
| `meta.nav / ctaHref / ctaLabel / footerLinks` | 导航、右上按钮、页脚；无后端时 `ctaLabel` 不得含「预约 / 提交 / 立即 / 报名 / 下单」 |
| `meta.requiredTerms / forbiddenTerms` | 主题词审计：必备词全在、禁用词一个不在 |
| `meta.cloud` | `needed / table / columns / prefix`；`webapp` 必须 needed=true 且表名与字段齐备 |
| `hero / sections / assertions` | 首屏、区块数组（顺序即页面顺序）、业务交互断言 |

可用 section：`features / showcase / stats / steps / quote / faq / cta / notes`。叙事线性：**价值主张 → 具体项目或能力 → 可信证据 → 行动 → 常见疑问**。

写 spec 自检：每段文案换一个主题读起来应该别扭；品牌前后统一；数字与口径一致；`forbiddenTerms` 覆盖其他主题典型词、其他项目品牌、制作过程词与夸大词。

## P3 生成页面

```bash
# 页面草稿：不写站点地址，表单自动禁用
python3 scripts/build_page.py --spec x.json --out index.html

# 应用：显式站点地址 + 云端配置，表单可提交
python3 scripts/build_page.py --spec x.json --out index.html \
  --cloud-config /tmp/public-config.json --base-url https://<真实域名>
```

生成器流程：主题路由 → token 覆盖 → 按 `sections` 顺序渲染 → 写盘前自检，不过就不产出文件。自检覆盖占位符、标签平衡、域名与 head 三处 URL 一致、绝对外链、口径声明、区块文本重复、无障碍、JS 语法，并强制：

- `webapp` 必须有真实 `siteUrl`、云配置、`cloud.needed/table/columns`；
- 草稿态不写 `canonical / og:url / ld+json.url`，不出现占位域名；
- 无后端时表单整体禁用（input 与 button 都 disabled）；
- 有 favicon、分享卡类型与 `og:image` 自洽、`<noscript>` 降级提示、状态条 `role/aria-live`。

## P3.5 应用创建

判定为 `webapp` 时按序执行，任一步没成就停在 INCOMPLETE：

1. `workbuddy_cloud_service action=inspect` 看本会话已有应用；可复用就复用，没有才 `action=activate`（`applicationMode=create`，`appName` 用主题名，`domainPrefix` 用主题拼音或英文，`appType=web`）。确认框由平台弹出，取消则记录 cancelled。
2. 拿到 `publicConfig`，只把 `endpoint / oauthRelayBaseUrl / publishableKey` 写进前端；`applicationId / resourceId` 不落前端。
3. 管理侧建业务表：DDL → `ENABLE ROW LEVEL SECURITY` → GRANT → 读/写 POLICY，顺序不能反；跑一次「插入 → 读回 → 冲突更新 → 再读回」留证。
4. `--cloud-config` 重新生成页面；前端只做 `select / insert`，初始化一次 client；SDK 加载失败要给可见提示。
5. `meta.siteUrl` 填激活返回的真实域名。发布为应用 / 站点上线需用户明确指令，交付说明必须给出可执行命令清单。
6. 发布复用同一个 applicationId，换 ID 会让域名变化并导致 Origin 精确匹配失败。

没有登录时数据表是应用级共享演示数据：页面说明须写明任何人都能改、别填真实个人信息。

## P4 五道闸门

```bash
# ① 生成器自检（build_page.py 内建，失败不写盘）
# ② 形态 / 主题口径 / 事实来源 / 叙事 / 控件一致性 / 无障碍 / 资源边界
python3 scripts/verify_static.py --spec x.json --page index.html [--cloud]
# ③ CDP 真实双视口：计算样式 + 业务断言 + 逐区块截图
node scripts/verify_viewport.mjs --spec x.json --url http://127.0.0.1:PORT/index.html --shots <交付目录>/shots/run
# ④ 逐段截图目视：主题可辨、无重复文案、无截断溢出、控件同形
# ⑤ 交付判定（最终裁判）
python3 scripts/verify_delivery.py --spec x.json --dir <交付目录>
```

③ 默认跑 390 与 1280 两档，断言窄屏导航入口未被隐藏、桌面不横向溢出；截图按「首屏 + 每个 section + 页尾」逐段落进交付目录，缺段即不合格。⑤ 输出三态并列出补齐步骤。

自动断言全绿不等于观感合格，必须看图；看图不等于应用存在，必须过 ⑤。脚本返回非零退出码即失败，不要只看最后一行输出。

## P5 交付与验收

汇报前逐角色确认，任一不成立就回对应阶段修：

| 角色 | 必须成立 |
|---|---|
| 产品经理 | `meta.intent` 与 `meta.deliverable` 一致；主 CTA 点下去有结果；有发布或访问地址 |
| UI 设计师 | 主题一眼可辨；页内控件同形同尺寸；窄屏导航入口可用；同一句不重复渲染；截图覆盖全页 |
| 应用开发 | 站点地址真实、head 三处 URL 一致；表单有落点或整体禁用；有 `<noscript>`；正文无技术词 |
| 测试 | 五道闸门逐道有结果；双视口；逐 section 截图；失败路径有可见提示 |
| 业务方 | 店名 / 地址 / 电话 / 价目 / 承诺 / 评价都有 `source`；无 `user` 来源不得对外发布 |
| 终端用户 | 主按钮有明确结果；禁用态有说明；看得懂下一步 |

汇报按「产出文件 / 版式与理由 / 交付形态与三态 / 五道闸门结果 / 六角色自检 / 未做事项 / 下一步命令」写，关键结论带证据（断言项数、视口尺寸、闸门状态）。

## 目录

```
SKILL.md                     本文件：流程与判定
references/layouts.md        版式库、token 分类、扩展步骤
references/content-rules.md  叙事顺序、文案框架、主题词审计、事实来源
references/cloud-and-delivery.md  形态判据、云接线六步、三态定义、交付模板
references/gates.md          五道闸门明细、实现要点、运行注意
templates/layouts.json       版式注册表（扩展点）
templates/base.css           共享 .ctl 控件层，只引用 token
templates/page.html          页面骨架
scripts/pick_layout.py       主题 → 版式
scripts/build_page.py        spec + 版式 → 单文件页面（写盘前自检）
scripts/verify_static.py     ② 静态闸门
scripts/verify_viewport.mjs  ③ 双视口断言与逐段截图
scripts/verify_delivery.py   ⑤ 交付三态判定
examples/*.spec.json         可跑样例（webapp 与 draft 两种形态）
```
