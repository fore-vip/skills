---
name: h5-app-builder
slug: h5-app-builder
displayName: 主题落地页生成模板
display_name: 主题落地页生成模板
display_name_en: Theme-Driven Landing Page Builder
description: 输入任意主题，动态选版式并创建一个可运行、可交付的移动端宣传应用（或用户明确同意的页面草稿）。核心是「交付形态契约」：P0 先判定 draft/webapp/site，P3.5 必须发起应用创建（云服务、建表、写入读回、发布路径），P4 第五道交付判定闸门输出 DELIVERED / DRAFT / INCOMPLETE 三态，只有 DELIVERED 才允许汇报「已交付」。版式库按主题关键词路由（暖调生活服务 / 深色科技 / 明快营销 / 杂志编辑），零命中要确认或新增版式；内容结构与文案由 spec 决定，生成器不预设业务板块；业务事实必须有来源清单；所有控件共用 .ctl 基类并只引用版式 token，页内统一、跨主题不同。附带六角色验收清单，防止交出「只设计了首页」的半成品。
description_zh: 按主题动态选版式、写内容并创建可交付的移动端宣传应用；含交付形态契约、云服务接通、五道闸门与六角色验收，杜绝只给设计稿。
description_en: "Turn any topic into a deliverable mobile landing application: declare the delivery form up front, route the topic to a layout from an extensible registry, write topic-specific content, create the cloud-backed application, then pass five gates including a three-state delivery verdict and a six-role acceptance checklist."
category: engineering
version: 3.0.0
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
  - "只设计了首页"
  - "把这个过程做成技能"
---

# 主题落地页生成模板（应用创建）

> **是什么**：一套「输入主题 → 动态选版式 → 写出内容 → **创建应用** → 五道闸门 → 交付」的可复跑流程与可执行资产。
> **不是什么**：不是设计稿，不是「只出一个首页」的静态页，也不是换标签就复用的死模板。AUTO / auto.fore.vip 只是历史参考，本技能不依赖它。

## 0. 完成定义（最高优先级，先读这一段）

**用户要的是一个应用，不是一个首页设计。** 历史事故：专家独立运行时跑完 P0–P4，产出了 `index.html` + spec + 四张截图、闸门 16/16 全绿，然后停下汇报「已完成」；交付目录里没有应用实体、没有云服务、没有站点地址，主按钮「约一次到店护理」点了只会提示「不会保存」。用户看到的是半成品。根因不在专家偷懒，而在**当时 SKILL 的 P5 终点就是「本地预览 + 说明未上线」**，全链路没有「创建应用」这一步，也没有任何闸门能判定「这到底是不是应用」。

因此本版把完成定义写成硬约束：

1. **首动作契约**：接到主题后，第一个可执行动作是「建交付目录 + 写 spec 骨架」，不是先输出一段设计方案。禁止只交付文案、结构图、首页草图。
2. **交付形态契约**：`meta.deliverable` 必须显式声明 `draft | webapp | site`，并与用户诉求一致（见 P0）。未声明 = 未完成。
3. **应用创建不可跳过**：判定为 `webapp` 就必须走 P3.5（云服务激活 → 建表 → 写入读回 → 站点地址 → 发布路径）。确认框被取消时**停在 INCOMPLETE，不重试、不绕路、不静默降级**。
4. **三态判定**：`verify_delivery.py` 输出 `DELIVERED / DRAFT / INCOMPLETE`。只有 **DELIVERED** 允许汇报「已交付」；`DRAFT` 必须在标题写「页面草稿，不是应用」；`INCOMPLETE` 禁止汇报完成并列补齐步骤。
5. **闸门全绿不等于完成**：静态闸门、视口断言、截图目视都只证明页面质量，不证明应用存在。第五道闸门是最终裁判。
6. **如实汇报**：未上线就写未上线；示例数据就写示例数据；禁用按钮就写未开放。禁止把「已激活云服务 / 代码已提交 / 预演通过」混同为上线。

## 四条硬原则

1. **形态先定**：先判交付形态再选版式。用户话里出现「应用 / 上线 / 发布 / 可访问 / 能收预约 / 留资 / 落库」任一词，默认 `webapp`；只有用户明确说「先看看效果 / 做个草稿 / 只要设计」才允许 `draft`。
2. **版式随主题变**：先跑主题路由，再写内容。不同主题必须落到不同 token 集与不同叙事结构，不能用同一套骨架换词；零命中要确认或新增版式，不悄悄用兜底。
3. **内容随主题写、事实有来源**：文案由专家按主题现场撰写并写进 spec；**店名 / 地址 / 电话 / 营业时间 / 项目 / 价格 / 经营承诺 / 顾客评价一律不得臆造**，必须逐条登记在 `meta.facts` 并标 `source`。禁止把制作过程、技术词、其他主题的词写进正文。
4. **页内严格统一、跨页允许不同**：同页所有可点控件走 `.ctl` 基类并只引用 `:root` token；不同版式形状不同是设计意图。

---

## P0 解析主题 + 交付形态契约

从用户输入抽取四件事，缺什么**一次性**问清，不分多轮追问：

| 项 | 说明 | 写进 spec |
|---|---|---|
| `topic` | 主题原话，用于版式路由 | `meta.topic` |
| 受众与目标 | 给谁看、希望他做什么 | `meta.intent`（**保留用户原话**） |
| **交付形态** | 应用 / 页面草稿 / 站点 | `meta.deliverable` |
| **业务事实** | 店名、地址、价目、承诺、评价由谁提供 | `meta.facts` |

事实来源顺序：用户当轮指令 → 待办详情 → 全库与工作区检索 → 项目资产库 → 历史对话。**查不到就如实说查不到，并一次性列出「待补事实清单」**，不能用「示例内容」悄悄补齐后当作交付完成。

`meta.facts` 每条形如 `{ "key": "示例价目", "value": "¥198 等", "source": "example" }`，`source` 只能是 `user`（用户提供）、`placeholder`（占位待填）、`example`（示例，必须评审并标注）。含 `example` 事实的页面必须 `factReview: true` 且 `disclaimer` 含「示例 / 演示」；这类页面是**演示应用**，禁止作为真实门店对外发布。

## P1 版式路由（动态设定的核心）

```bash
python3 scripts/pick_layout.py --topic "社区美容门店 护肤 SPA 预约宣传页" --json
```

返回 `id / name / intent / tokens / sectionOrder / matched / score / hits / reason / alternatives`。规则在 `templates/layouts.json`：按关键词命中数选版式，命中词长度加权，平局取注册顺序；`matched=false` 表示零命中已兜底 → **必须确认或新增版式**；专家认为不合适时用 `--layout <id>` 或 `meta.layoutId` 覆盖并说明原因。内置 `warm / tech / fresh / editorial` 四套。

**新增版式只改 `layouts.json`，不改脚本**：复制一条记录，填 `id / name / keywords / intent / sectionOrder / heroAlign / tokens`。token 至少覆盖 `--bg --card --text --sub --muted --line --line-2 --brand --brand-soft --on-brand --surface --surface-2 --r-card --r-panel --r-pill --h-lg --px-lg --fs-lg --h-md --px-md --fs-md --h-sm --px-sm --fs-sm --focus --shadow --font-title --hero-pad --cols`。

## P2 按主题写内容 spec

spec 是唯一内容源，新增字段加粗：

| 字段 | 作用 |
|---|---|
| `meta.topic / intent / brand / title / description` | 主题、诉求原话、品牌、标题 |
| **`meta.deliverable / siteUrl / facts / factReview`** | 交付形态、真实站点地址、业务事实来源、示例评审标记 |
| `meta.footerNote / disclaimer` | 页脚与口径声明；**`disclaimer` 必须与 `cta.note` 逐字一致**并原样出现在正文 |
| `meta.nav / ctaHref / ctaLabel / footerLinks` | 导航、右上按钮、页脚；无后端时 `ctaLabel` 不得含「预约 / 提交 / 立即」 |
| `meta.requiredTerms / forbiddenTerms` | 主题词审计：必备词全在、禁用词一个不在 |
| `meta.cloud` | `needed / table / columns / prefix`；`webapp` 必须 needed=true 且表名与字段齐备 |
| `hero / sections / assertions` | 首屏、区块数组（顺序即页面顺序）、业务交互断言 |

可用 section：`features / showcase / stats / steps / quote / faq / cta / notes`。叙事必须线性：**价值主张 → 具体项目或能力 → 可信证据 → 行动 → 常见疑问**。

写 spec 时自检：每段文案换个主题读起来会别扭才算写对；品牌前后统一；所有数字、称呼、流程口径一致；`forbiddenTerms` 至少覆盖其他主题典型词、其他项目品牌、制作过程词与夸大词；**禁止把「没有发送 / 不会保存 / 未开放」写成 PASS 断言的 expect**（这会变成「业务不可用也算验收通过」）。

## P3 生成页面

```bash
# 页面草稿：不写站点地址，表单自动禁用
python3 scripts/build_page.py --spec x.json --out index.html

# 应用：显式站点地址 + 云端配置，表单可提交
python3 scripts/build_page.py --spec x.json --out index.html \
  --cloud-config /tmp/public-config.json --base-url https://<真实域名>
```

生成器：主题路由 → token 覆盖 → 按 `sections` 顺序渲染 → 写盘前自检。**不过就不产出文件**。自检覆盖占位符、标签平衡、域名与三处 head URL 一致、绝对外链、口径声明、区块文本重复、无障碍、JS 语法，并强制：

- `webapp` 必须有真实 `siteUrl`、云配置、`cloud.needed/table/columns`；
- 草稿态不写 `canonical / og:url / ld+json.url`，不出现 `example.com` 之类占位域名；
- **没有后端时表单整体禁用**（input 与 button 都 disabled），避免「填完手机号却白填」；
- 有 favicon、分享卡类型与 `og:image` 自洽、`<noscript>` 降级提示、状态条 `role/aria-live`。

## P3.5 应用创建（不可跳过）

判定为 `webapp` 时按顺序执行，任一步没成就停在 INCOMPLETE：

1. `workbuddy_cloud_service action=inspect` 看本会话已有应用；有合适的复用，没有才 `action=activate`（`applicationMode=create`，`appName` / `domainPrefix` / `appType=web`）。**确认框被取消 → 记录 cancelled，不重试、不绕路、不假装已接后端。**
2. 拿到 `publicConfig`，只把 `endpoint / oauthRelayBaseUrl / publishableKey` 写进前端；`applicationId` 等管理侧标识不进页面。
3. 管理侧建业务表 + `ENABLE ROW LEVEL SECURITY` + GRANT + 读/写策略；跑一次「插入 → 读回 → 冲突更新 → 再读回」留证。
4. `--cloud-config` 重新生成页面；前端只做 `select / insert`，CDN 加载失败要给可见提示，绝不把本地操作说成已存云端。
5. `meta.siteUrl` 写激活返回的真实域名；发布为应用 / 站点上线**需用户明确指令**，但交付说明必须给出可执行命令清单，不能只报「未上线」。
6. 发布必须复用同一个 applicationId，否则域名变化会让 Origin 精确匹配失败。

详细步骤与失败处置见 `references/delivery-contract.md` 与 `references/cloud-service.md`。

## P4 五道闸门（缺一不可）

```bash
# ① 生成器自检（build_page.py 内，失败不写盘）
# ② 交付形态 / 主题口径 / 事实来源 / 叙事 / 控件一致性 / 无障碍 / 资源边界
python3 scripts/verify_static.py --spec x.json --page index.html [--cloud]
# ③ CDP 真实双视口：计算样式 + 业务断言 + 逐区块截图
node scripts/verify_viewport.mjs --spec x.json --url http://127.0.0.1:PORT/index.html --shots <交付目录>/shots/run
# ④ 逐段截图目视：主题一眼可辨、无重复文案、无截断溢出、控件像一家人
# ⑤ 交付判定（最终裁判）
python3 scripts/verify_delivery.py --spec x.json --dir <交付目录>
```

③ 默认跑 **390 + 1280 两档**，断言窄屏导航入口没有被 `display:none` 抹掉、桌面不横向溢出；截图按「首屏 + 每个 section + 页尾」逐段输出并落进交付目录，缺段即判不合格。⑤ 输出三态并列出补齐步骤，是唯一能宣布「完成」的闸门。

**自动断言全绿不等于观感合格，必须看图**；看图也不等于应用存在，必须过 ⑤。

## P5 交付与沉淀：六角色验收清单

交付汇报前，逐角色回答下表；任一「不合格判据」命中就回到对应阶段修，不许带着它汇报完成。

| 角色 | 必答问题 | 不合格判据 |
|---|---|---|
| 产品经理 | 用户要应用还是草稿？核心业务动作有没有闭环？发布 URL 是什么？ | 诉求要应用却只有 `index.html`；主 CTA 点了不产生结果；完成判定靠「闸门全绿」 |
| UI 设计师 | 主题一眼可辨吗？页内控件像一家人吗？窄屏导航入口还在吗？有没有重复文案？ | 导航被隐藏；同一句渲染两遍；焦点态几乎不可见；截图没覆盖全页 |
| 应用开发 | 站点地址真实吗？head 三处 URL 自洽吗？表单有落点吗？JS 关闭会怎样？ | `example.com` / canonical 不一致 / 无后端 / 无 `<noscript>` / 技术词漏进正文 |
| 测试 | 五道闸门逐道结果？双视口？逐段截图？失败路径？ | 只跑 390 一档；把「不会保存」写成 PASS 断言；CDN 不通时无可见提示 |
| 店长 | 店名、价目、地址、电话、承诺、评价哪些是真实提供的？ | 任何业务事实没有 `source=user` 却准备对外发布；替店长承诺「不办卡 / 不收费」 |
| 终端用户 | 点主按钮后得到什么？会不会白填手机号？看不看得懂下一步？ | 禁用态没说明；提交后无结果；满屏「示例」却伪装成真店 |

汇报按「产出文件 / 版式与理由 / 交付形态与三态 / 五道闸门结果 / 六角色自检 / 未做事项 / 下一步命令」写，关键结论带证据（断言项数、视口尺寸、闸门状态）。

沉淀：新主题 spec 放 `examples/`，选版理由与坑写进 `references/`；本地预览用后台常驻 `python3 -m http.server`；归档链路为主副本 `~/.workbuddy/skills/h5-app-builder/` → 项目仓库 → 专家内嵌副本 → git（只暂存自己的路径）；SkillHub 发布与站点上线都需明确指令，先 `--dry-run`。

---

## 目录

```
templates/layouts.json    版式注册表（扩展点：加主题只改这里）
templates/base.css        共享 .ctl 控件层，只引用 token
templates/page.html       页面骨架
scripts/pick_layout.py     主题 → 版式
scripts/build_page.py     spec + 版式 → 单文件页面（写盘前自检）
scripts/verify_static.py  ② 形态 / 口径 / 事实 / 叙事 / 样式 / 无障碍 / 资源
scripts/verify_viewport.mjs ③ 双视口计算样式 + 业务断言 + 逐段截图
scripts/verify_delivery.py ⑤ 交付三态判定与补齐步骤
references/*.md           交付契约、六角色清单、版式、内容红线、云接线、坑、案例
examples/*.spec.json      跑通的主题样例（含 webapp 与 draft 两种形态）
```

## 已知坑

- 无头 Chrome 的 `--window-size` 会被夹到最小 500px，390 必须用 CDP `Emulation.setDeviceMetricsOverride`
- 云 SDK 的 CDN 在本机时通时不通；页面必须给可见失败提示，且不能把本地操作说成已存云端
- `verify_static.py` 会把 `<head>` 排除后再查主题词，但 head 内 URL 单独走校验清单
- 新增 token 时若 `.ctl` 规则出现硬编码 px / 色值，静态闸门直接 FAIL
- 区块文本重复：renderer 用 `owns` 声明自己渲染了哪些字段，新增 section 类型必须同步声明，不要在 `render_sections` 里按类型打补丁
- 长稿预检：禁用词 + 英文噪声词差集，跑完再交付
- 工作树里有别人的活时，只暂存自己新增的路径

## 版本

- **3.0.0**：六角色体验复盘后重做。新增交付形态契约、P3.5 应用创建、第五道交付判定三态、六角色验收清单；修复假域名、引语重复、窄屏导航消失、表单假提交、焦点态、无障碍与双视口覆盖；`verify_static.py` 从 16 项扩到 37–41 项。
- 2.0.0：改为主题驱动，移除固定 KPI 演示台，新增版式库与双闸门。
- 1.x：历史版本见 git 记录，旧架构已归档，不再作为模板使用。
