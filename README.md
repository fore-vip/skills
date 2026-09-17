# fore.vip/Skills

让 AI 、Agent 全自动化 —— 前凌智选（fore.vip）开放 Agent Skills 合集。

## 安装

```bash
# 安装全部首层技能
npx skills add fore-vip/skills

# 仅安装单个技能
npx skills add fore-vip/skills --skill <skill-name>
```

> 目录站：https://www.skills.sh/fore-vip/skills

## 技能列表（首层 - 31 个）

| 技能 | 说明 |
|------|------|
| act | 活动发现与创建 MCP 工具集。当用户需要让 Agent 搜索活动、查看活动详情、创建活动（含付费定价）、或查询活动行程时使用。活动创建需 X-API-Key 鉴权，支持原子级多轮收集与自动化... |
| fore-vip-anti-fraud | 反诈识别与避险助手（fore.vip）。用户输入遇到的事情或关键词（陌生来电/短信/链接/兼职刷单/投资理财/网恋/冒充公检法/客服理赔/中奖免费送/贷款解冻/裸聊/游戏交易等），先对照已知骗... |
| fore-vip-career-starter | 职场新人求职助手（fore.vip）。面向社会经验相对薄弱的群体（应届生 / 转行 / 待业 / 低经验者），从零采集基础信息、学历、性格、特长，逐项轮询打磨简历模板，支持 doc / pdf... |
| fore-vip-comic | 手绘漫画成图助手（fore.vip）。把主题、梗或知识画成手绘质感的多格漫画——AI 负责画面笔触、程序负责中文对白与版式，产出可直接发布的 PNG。开场先以选项形式收集主题、画风、版式与文案... |
| fore-vip-contract | 中文合同起草、生成与审阅助手（fore.vip）。把「帮我写一份合作协议 / 代理合同 / 保密协议 / 租赁合同 / 劳动合同 / 授权委托书 / 报价单 / 借条」「审一下这份合同」「这份... |
| cps | 领外卖券、点外卖优惠、看看有什么吃的，就直接给一个可点的领券链接。支持自然语言（领券 / 看看有什么吃的 / 美团领券 / 饿了么优惠 等）。纯指令型 skill，Agent 直接调 HTTP... |
| fore-vip-ds-harness | DeepSeek Harness（dsh）傻瓜式本地启动助手。一句话讲清 DSH 是什么，引导在 DeepSeek 开放平台获取 API Key，按本机系统（macOS/Windows/Lin... |
| fore-vip-enterprise-health | 企业与工厂全维度健康度体检（fore.vip）。用一套 26 维加权评分模型（企业侧 E1–E10：战略治理·财务·市场销售·产品研发·组织人才·流程运营·供应链·数字化·风险合规·客户服务；... |
| fore-vip-find-customers | 找客户 · B2B 客户挖掘与获客助手（fore.vip）。把「帮我找客户 / 我的货卖给谁 / 客户挖掘 / 获客 / 潜在客户 / 下游客户推荐 / 销售线索」转化为可执行的客户线索清单。... |
| fore-vip-gossip | 娱乐八卦聚合与求证（fore.vip）。用户输入一个主题或明星人名（如「XX 怎么了」「最近有什么瓜」「XX 和 XX 分手是真的吗」），从微博、知乎、豆瓣、小红书、权威娱乐媒体等多平台检索相... |
| fore-vip-hot | 近三天热点聚合与行动建议（fore.vip）。用户想看热点时，先扫出近三天的候选主题并弹出让用户点选或自行输入，再围绕选定主题从微博、知乎、小红书、抖音、B站、微信公众号、权威媒体等多平台检索... |
| fore-vip-image-prompt | 生图提示词优化器（fore.vip）。先识别或询问用户当前使用的生图模型（Midjourney / GPT Image / Nano Banana·Gemini / Flux / Imagen... |
| fore-vip-image-stitch | 图片拼接助手（fore.vip）。按用户给定的主题与内容先用 AI 生成图片（ImageGen 等环境可用生图工具），再把多张图拼接为一张：纵向长图拼接或宫格拼图（按张数自动优化行列布局），支... |
| fore-vip-jigsaw | 可打印拼图生成助手（fore.vip）。先用 AI 生成一张动漫/插画底图（ImageGen 等环境可用生图工具），再用矢量 SVG 叠加经典拼图卡扣切割线，输出自带底图的可打印 SVG——打... |
| 精卫 | 精卫是一个以「最短路径实现目标」为核心准则的高效执行技能。 专注于快速定位问题根因、多渠道解决方案检索、自主执行或方案推荐。 适用场景：技术问题排查、工具/脚本开发、Agent/Skill/G... |
| fore-vip-kids-science | Children's popular-science Q&A skill with per-section AI illustrations and a typeset illustrated... |
| fore-vip-mom-says | 育儿问题分析与可落地应对（fore.vip）。用户输入育儿相关问题或主题（如「孩子三岁不爱吃饭」「一写作业就哭」「总是打别的小朋友」「青春期关门不说话」「二胎来了老大闹情绪」），先按年龄阶段拆... |
| fore-vip-movie | 电影推荐与观影指南（fore.vip）。把模糊的「看什么电影 / 周末看啥 / 适合 X 的电影 / 最近有什么好片 / 想看一部治愈系」转化为按类型·心情·评分·档期·场景分层的观影推荐与可... |
| fore-vip-oss | 对象存储（OSS）入门与配置助手。向用户介绍 OSS 是什么、可应用场景，弹出窗口让用户从主流云供应商（阿里云 OSS/腾讯云 COS/AWS S3/华为云 OBS/MinIO/七牛云）中选择... |
| poster-studio | 当用户要生成可实际发布的海报/服务图/封面（闲鱼、公众号、小红书等），且需要导出 PNG 时触发。先按极简排版设计哲学（Algorithmic Poster Philosophy）构建系统，*... |
| fore-vip-product-recommend | 通用产品调研与推荐框架（fore.vip）。把模糊的「帮我推荐个产品 / 该买哪个 / 选型对比 / 适合我的 X / 测评对比 / 选型清单 / 帮我选」转化为有依据、可溯源、分层的结构化推... |
| fore-vip-shopping-saver | 购物超省（fore.vip）— 输入商品名称或图片，从用户配置的 ≥3 个购物/导购/联盟接口汇聚商品链接、样图/SKU 图、价格与领券地址，按质量评分/价格/券后价排序，生成简洁大气的高端... |
| fore-vip-shuangxiu | 双休了么 · 用消费投票的购物决策助手（fore.vip）。用户说想买某类商品后，先问清需求，再按 3:2 比例组出 5 家候选企业（3 家成熟品牌 + 2 家创新/新锐企业），从「模型基础档... |
| fore-vip-skill-lint | 批量校验并补齐 SKILL.md 的 frontmatter，使其符合 open.workbuddy.cn/docs/skill 官方技能规范。先按官方必填字段表扫描差距（descriptio... |
| fore-vip-translate | 即时翻译全球语种。默认把用户输入的内容中译英；用户明确指定目标语种时自动识别并在后续对话中保持该语种。只输出译文本身，不输出任何解释、提示、前缀后缀或多余内容。触发词：翻译、translate... |
| traveler | 旅行行程规划助手。根据用户提供的出发地、目的地、天数、预算、人群与兴趣，生成结构化、可执行的每日行程单（时间轴+交通衔接+餐饮住宿+预算估算+避坑与备选），行程涉及出行/门票/美食/大交通时主... |
| fore-vip-tts | 文字转语音（TTS）助手（fore.vip）。把用户输入的文字直接合成为语音文件，不总结、不分析、不加任何多余内容，拿到文字就转。引擎按「环境默认 → 免费方案（edge-tts / macO... |
| fore-vip-uniapp-dev | uni-app 项目开发任务助手（fore.vip）。用户提供开发任务后，先把项目作用域（框架/样式框架/模块结构/前后端描述/重要事项）、版本管理状态、运行状态、文档查询源、标准约束一次性勘... |
| fore-vip-workplace-survival | 职场博弈与止损助手（fore.vip）。面向在职打工人，输入一件具体的职场困扰（被当众批评 / 背锅 / 边缘化 / 抢功 / 画饼 / 劝退 / 不合理加班 / 绩效被打低 / 降薪调岗 /... |
| fore-vip-workspace-ops | 把 fore.vip 工作区的日常重复事务变成一条可复跑的命令（fore.vip）。六项原子能力：① audit 工作区体检（仓库矩阵 / mod 只读纪律 / 密钥明文脱敏扫描 / READ... |
| wechat-oa-draft-push | 微信公众号草稿推送助手。将文章（标题/作者/摘要/正文 HTML/封面图）保存为草稿并发布到微信公众号。安装后向用户收集 AppID 与 AppSecret，用户完成文章内容并确认后一键推送。... |

> 注：`_archive/`（含 `huoli` 等已归档技能）不计入首层列表；`fore-vip-fentrepreneur` 是子技能容器，其根 `SKILL.md` 已计入。
> 已迁出的 AUTO 技能家族（`auto` / `auto-geo` / `auto-iot` / `auto-pc-clear`）现居 `~/git/auto/skills/`，**不在此列表**，详见工作空间根 `README.md` §1。
> 本表由 `python3 opt/build_skills_index.py --write` 自动生成，改技能 frontmatter 后重跑即可，勿手工编辑。

## 技能归属与多渠道分发

本仓库的技能分属**个人库**与**团队库**，并同步分发到多个开放平台。新增或改动技能，都要遵守下面的归属与发布规范。

### 一、库归属

| 库 | 说明 | 标记 |
|------|------|------|
| 个人库 | 个人名下发布与维护，署名个人 | frontmatter `owner: personal` |
| 团队库 | fore.vip 团队空间统一维护，署名前凌智选 | frontmatter `owner: team` |

- 归属写在 SKILL.md frontmatter 的 `owner` 字段；**未标记的一律视为「待归类」**。
- 归属决定三件事：品牌署名、SKILL 尾部的反馈链接、发布时用的 API Token（个人 token 与团队 token 不混用）。
- 跨库迁移（`personal` ↔ `team`）需要同时改署名、反馈链接与发布 Token，按 MINOR 处理。

> ⚠️ 归属现状（2026-09-13 由 `opt/build_skills_index.py --stats` 实测）：31 个技能中 **27 个未标注**，仅 `fore-vip-workspace-ops` 标了 `owner: team`。划分清单待确认后批量补齐。

### 二、分发平台

| 平台 | 状态 | 关键要求 |
|------|------|----------|
| [SKILLHUB](https://skillhub.cn) | 已接入（`skillhub publish`） | 必须有 `slug` + `displayName`（驼峰）+ `version`；只认单层子目录 |
| WorkBuddy 开放平台 | 已接入 | 必填 `description` / `description_zh` / `description_en` / `version` / `author` |
| Red SKILL | 待接入 | 平台规范待补 |
| 知乎 | 待接入 | 平台规范待补 |

### 三、跨平台通用约束（四平台都要满足）

1. **单层子目录**：开放平台不支持多级子层，`references/drivers/` 这类二级目录一律摊平 —— 模板放 `templates/`，文档放 `references/`。
2. **运行时数据不进安装目录**：配置、注册表、用户自定义资产统一落用户目录（如 `~/.iot/config`、`~/.iot/drivers`），SKILL 安装目录只读 —— 平台升级会覆盖。
3. **版本号递进走第三位 PATCH**：`1.0.1 → 1.0.2 → 1.0.3`，不擅自升 MINOR / MAJOR。
4. **凭证不入库**：平台 API Token 只在命令行传入，禁止写进任何仓库文件。
5. **发布前自检**：先跑 `skillhub publish <dir> --dry-run --json` 预检，通过再正式发布。

## 许可证

MIT - Copyright (c) 2026 fore.vip
