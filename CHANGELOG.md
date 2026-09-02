# Changelog

## 2026-09-02

- 优化 SKILL: fore-vip-movie（v1.0.0→v1.1.0 · 来源: todo 电影优化）：① 补齐 frontmatter 规范字段（display_name/display_name_en/category:entertainment/version/author/agent_created）；② 步骤 3「调研与采集」改为硬规则「实时取数，禁止凭记忆编造」，明确 WebSearch(带 freshness)+WebFetch 取数 + 权威源清单，场景库只给逻辑不预填片目；③ 恢复并落地 CHANGELOG 记录过但丢失的「在线购票（推广）」资源位 `https://kurl08.cn/ts0VHB`（影划算电影票，已验证跳转，标注「推广/广告」、不代购不代付）；④ references/movie-guide.md 新增「二·5 实时数据获取清单」（端点+检索词模板）与场景库不预填片目说明；⑤ 新增「不可为（边界）」一节

## 2026-08-29

- 创建 SKILL: fore-vip-hot（热点雷达 · 来源: todo 热点；用户想看热点 → 先快扫近三天候选主题 → AskUserQuestion 弹出 4 个热门主题供点选或用户自输 → 选定主题后从微博/知乎/小红书/抖音/B站/公众号/权威媒体多平台深挖（WebSearch 必带 freshness=d3）→ 时效闸门硬过滤 >3 天 + 信源 S/A/B/C/D 分级交叉验证（✅已确认/⚠️多方报道/💬舆论/❓传闻）→ 去 AI 味可读性改写 → 输出「一句话结论/时间线/各方说法/事实核对表/跟你有什么关系/你可以现在做的几件事/信源清单」；涉政军事一票否决，投资医疗法律只做风险提示）

## 2026-08-28

- 创建 SKILL: fore-vip-gossip（八卦吃瓜 · 来源: todo 八卦；输入主题或明星人名 → 微博/知乎/豆瓣/小红书/权威媒体多平台检索 → 信源 S/A/B/C/D 分级交叉验证 → ✅已证实/⚠️待核实/❓纯传闻三级标注 → 沉浸式吃瓜输出：瓜况速览/时间线/各方回应/瓜点分级表/理性提示；不挖素人隐私、不造谣不传谣）
- 创建 SKILL: fore-vip-shopping-saver（购物超省 · 来源: fore.vip 电商比价；输入商品名/图片 → 从 ≥3 个用户配置的购物/导购/联盟接口聚合 链接/样图/SKU图/价格/领券地址 → 按 评分/价格/券后 排序 → 输出简洁大气高端 HTML 比价清单，图片缺失/跨域自动占位；无第三方依赖 Python 聚合脚本 + providers 配置规范 + 3 端可运行示例）

## 2026-08-27

- 创建 SKILL: fore-vip-oss（OSS 对象存储助手）— 概念科普 / 弹窗选供应商（6 家带 CLI）/ 安装 CLI / 引导 AK/SK / 域名绑定 / 场景建议

## [fore-ex v2.0.0] — 2026-08-07

### Changed
- 重构为活动发现器：对接 `mcp.fore.vip/act/search`（免鉴权），移除产品列表
- 活动卡片显示封面图（加载失败自动隐藏），点击跳 `fore.vip/pages/activity/detail`
- 菜单「发布活动」跳转 Open Key 管理页 `fore.vip/web/key`
- 移除「发布产品」菜单；删除废弃 activity.html
- manifest `host_permissions` 增加 `mcp.fore.vip` / `fore.vip`

### Removed
- 产品搜索能力（旧端点 `api.fore.vip/mcp/query_kl`）
- 插件内活动创建表单

## [2.1.1] — 2026-06-14

### Added
- 模式1：原子级交互创建（多轮收集 Key→封面→主题→地址→坐标→时间→确认→单次MCP）
- 模式2：自动化批量创建（搜索→封面→坐标→循环 create_activity→汇总）

## 2026-08-15 08:33

- 创建 SKILL: fore-vip-industrial-modeling-solution (来源: 前凌智创/3D/工业建模)
- 创建返回 url 链接字段

### Changed
- uploadImage 降级逻辑移除，封面转存失败→errCode=-3 活动不创建

---

## [2.1.0] — 2026-06-14

### Added
- `create_activity` MCP 工具：创建活动
- `POST /act/create` 端点（Header X-API-Key 静态鉴权）
- 封面自动转存（download → uploadFile → 云存储 URL）
- 创建参数校验：content/address/cover 必填 + 长度限制

### Changed
- `open` 系统填充为 1（不允许用户传入）
- `type` 系统填充为 "ai"（不允许用户传入）
- cover 从可选改为必填
- tools/list 新增 create_activity 工具声明

---

## [2.0.1] — 2026-06-14

### Added
- act SKILL: search_activities + get_activity_detail MCP tools
- GEO 空间搜索（MongoDB geoNear）

### Fixed
- POST body 解析（this.getHttpInfo().body）
- keyword 匹配条件（dbCmd.or 逐参传递）

---

- [2026-08-14 17:52] 创建 SKILL: fore-vip-light-entertainment (来源: 前凌智创/轻娱)
- [2026-08-14 18:49] 创建 SKILL: fore-vip-manufacturing (来源: 前凌智创/制造业)
- [2026-08-14 19:18] 重构 SKILL: fore-vip-manufacturing + fore-vip-light-entertainment，从"市场调研模板"改为"行业从业者落地工具"；同步更新自动化任务 prompt
- [2026-08-14 19:48] 创建 SKILL: fore-vip-ebike-community-service (来源: 前凌智创/两轮电动车)
- [2026-08-14 20:47] 创建 SKILL: fore-vip-sharing-economy (来源: 前凌智创/共享)
- [2026-08-14 21:45] 创建 SKILL: fore-vip-parent-child-business (来源: 前凌智创/母婴·儿童)
- [2026-08-14 22:49] 创建 SKILL: fore-vip-agriculture-business (来源: 前凌智创/农业)
- [2026-08-14 23:49] 创建 SKILL: fore-vip-insurance-broker-assistant (来源: 前凌智创/保险)
- [2026-08-15 01:43] 创建 SKILL: fore-vip-social-community-business (来源: 前凌智创/社交·社区)
- [2026-08-15 02:40] 创建 SKILL: fore-vip-emerging-sports-operator (来源: 前凌智创/体育)
- [2026-08-15 03:39] 创建 SKILL: fore-vip-printing-paper-service (来源: 前凌智创/印刷·造纸)
- [2026-08-15 04:37] 创建 SKILL: fore-vip-erp-consultant (来源: 前凌智创/软件/ERP)
- [2026-08-15 07:27] 创建 SKILL: fore-vip-low-altitude-operator (来源: 前凌智创/低空经济)
- [2026-08-19 04:03] 创建 SKILL: fore-vip-movie（电影推荐 · 观影指南；C 端观影决策，纯提示词 + references/movie-guide.md 场景库/评分标尺/分级参考）
- [2026-08-19 04:53] 更新 fore-vip-movie：新增「在线购票（推广）」资源位，固定电影票 CPS 链接 https://kurl08.cn/ts0VHB，结尾引导自行购票；边界改为「不代购票/不代下单、仅提供入口」，并标注「推广/广告」
- [2026-08-19 06:09] 创建 SKILL: fore-vip-anti-fraud（来源: fore.vip 反诈 · 用户遇事先对照骗局特征库识别，无法识别则检索同类案例，疑似新型则推演利益点/伪装身份/损害途径，输出风险清单+即时应对+官方求助渠道 96110/110/国家反诈中心/12377/12315/银行止付）
- [2026-08-19 08:59] 创建 SKILL: fore-vip-career-starter（来源: fore.vip 求职 · 职场新人求职助手；C 端低经验用户从零写简历/定岗/补能力/找渠道/备选路径，纯提示词 + references 简历模板/平台/成长路线/备选路径）
- [2026-08-26 03:15] 更新 SKILL: auto（v1.0.1→v1.1.0 角色重定义：顶级执行技能，主题→mcp.auto 取最优秀执行步骤；新增工作空间权限读取+auto.config 维护；进入已有¥9.9付费流程；mcp.auto 无结果时兜底检索技能市场/社区/开源/搜索逐步执行+解决后回写步骤到 mcp.auto(主题ID关联)；回写云端方法 auto.save() 已实现）
- [2026-08-26 03:25] 实现 SKILL auto 回写云端方法 auto.save()（base/uni_modules/ai-mcp/uniCloud/cloudfunctions/auto/index.obj.js）：写操作同样需已支付凭证(order._id+secret)，与 theme() 对称——已付→批量写 steps 到主题频道 schedule 并回传支付配置(order_id,secret)；无凭证/凭证无效未付→回传 HTTP 402 支付表单直接拒绝不写。抽 module 级 buildPaywallResponse(theme,orderId,secret) 复用付费闸（与 theme() 内联块同源）。references/auto-writeback.json 改 status=implemented+支付门控+输出 order_id/secret；mcp.json 加 save_auto_steps 到 tools+version→1.1.0+writeback.status=implemented。聚焦单测 13/13 PASS（无凭证→402不写/无效→402/已付→写2条+回传/secret不符→402/新主题自动建频道写入）。部署待用户侧：URL化 /auto/save + SkillHub 注册 skillId auto。
