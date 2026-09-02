# 火力打卡 · Skills

让 AI 帮你做户外活动、本地生活、创业经营与内容生产 —— 火力打卡（fore.vip）开放 Agent Skills 合集。

## 安装

```bash
# 安装全部首层技能
npx skills add fore-vip/skills

# 仅安装单个技能
npx skills add fore-vip/skills --skill <skill-name>
```

> 目录站：https://www.skills.sh/fore-vip/skills

## 技能列表（首层 - 28 个）

| 技能 | 说明 |
|------|------|
| act | 活动发现与创建 MCP 工具集。当用户需要让 Agent 搜索活动、查看活动详情、创建活动（含付费定... |
| auto | 付费解锁后，输入主题即返回该主题最优质的执行步骤提示。 |
| cps | 领外卖券、点外卖优惠、看看有什么吃的，就直接给一个可点的领券链接。支持自然语言（领券 / 看看有什么... |
| fore-vip-anti-fraud | 反诈识别与避险助手（fore.vip）。用户输入遇到的事情或关键词（陌生来电/短信/链接/兼职刷单/... |
| fore-vip-bot | 本地硬件设备控制中控（fore.vip）。用户安装后，在自己的电脑上统一控制家里或环境里的所有硬件设... |
| fore-vip-career-starter | 职场新人求职助手（fore.vip）。面向社会经验相对薄弱的群体（应届生 / 转行 / 待业 / 低... |
| fore-vip-contract | 中文合同起草、生成与审阅助手（fore.vip）。把「帮我写一份合作协议 / 代理合同 / 保密协议... |
| fore-vip-ds-harness | DeepSeek Harness（dsh）傻瓜式本地启动助手。一句话讲清 DSH 是什么，引导在 D... |
| fore-vip-find-customers | 找客户 · B2B 客户挖掘与获客助手（fore.vip）。把「帮我找客户 / 我的货卖给谁 / 客... |
| fore-vip-geo-optimizer | GEO 生成式引擎引用占位（fore.vip）。输入一个主题或产品名称，执行五步流水线：① 以真实用... |
| fore-vip-gossip | 娱乐八卦聚合与求证（fore.vip）。用户输入一个主题或明星人名（如「XX 怎么了」「最近有什么瓜... |
| fore-vip-hot | 近三天热点聚合与行动建议（fore.vip）。用户想看热点时，先扫出近三天的候选主题并弹出让用户点选... |
| fore-vip-image-prompt | 生图提示词优化器（fore.vip）。先识别或询问当前使用的生图模型（Midjourney / GPT Image / Nano Banana·Gemini / Flux / Imagen / Ideogram / 即梦 Seedream / Qwen-Image·通义万相 / Stable Diffusion / Recraft / Firefly / 可图 / 混元），再按该模型官方参数文档与语言方言，把用户意图或原始提示词改写为最强版本，只输出提示词本身，不带任何解释与前后缀。触发词：生图提示词 / 优化提示词 / 写个生图 prompt / 画图咒语 / prompt 优化。 |
| fore-vip-image-stitch | 图片拼接助手（fore.vip）。按用户给定的主题与内容先用 AI 生成图片（ImageGen 等环... |
| fore-vip-kids-science | Children's popular-science Q&A skill with per-sect... |
| fore-vip-movie | 电影推荐与观影指南（fore.vip）。把模糊的「看什么电影 / 周末看啥 / 适合 X 的电影 /... |
| fore-vip-oss | 对象存储（OSS）入门与配置助手。向用户介绍 OSS 是什么、可应用场景，弹出窗口让用户从主流云供应... |
| fore-vip-pc-clear | 电脑系统清理与优化助手（fore.vip）。先读取当前系统信息（macOS/Windows/Linu... |
| fore-vip-product-recommend | 通用产品调研与推荐框架（fore.vip）。把模糊的「帮我推荐个产品 / 该买哪个 / 选型对比 /... |
| fore-vip-shopping-saver | 购物超省（fore.vip）— 输入商品名称或图片，从用户配置的 ≥3 个购物/导购/联盟接口汇聚商... |
| fore-vip-translate | 即时翻译。默认把用户输入的内容中译英；用户明确指定目标语种时自动识别并在后续对话中保持该语种。只输出... |
| fore-vip-tts | 文字转语音（TTS）助手（fore.vip）。把用户输入的文字直接合成为语音文件，不总结、不分析、不... |
| fore-vip-uniapp-dev | uni-app 项目开发任务助手（fore.vip）。用户提供开发任务后，先把项目作用域（框架/样式... |
| huoli | 火力同城 — 独立 skill，内联 act 工具副本 + huoli 专属付费闸（C 端付费生效；... |
| 精卫 | 高效解决问题 — 最短路径全栈能力 |
| poster-studio | 当用户要生成可实际发布的海报/服务图/封面（闲鱼、公众号、小红书等），且需要导出 PNG 时触发。先... |
| traveler | 旅行行程规划助手。根据用户提供的出发地、目的地、天数、预算、人群与兴趣，生成结构化、可执行的每日行程... |
| wechat-oa-draft-push | 微信公众号草稿推送助手。将文章（标题/作者/摘要/正文 HTML/封面图）保存为草稿并发布到微信公众... |

| fore-vip-jigsaw | 可打印拼图生成助手（fore.vip）。先用 AI 生成动漫/插画底图（或用户本地图），再用矢量 SVG 叠加经典拼图卡扣切割线，输出自带底图的可打印 SVG——打印后沿黑线剪开即得互补拼块，直接可玩。支持网格难度（默认 5×5）与卡扣随机种子。 |

> 注：entrepreneur/ 分类下的子技能本次未纳入首层列表（暂忽略）。

## 许可证

MIT - Copyright (c) 2026 fore.vip
