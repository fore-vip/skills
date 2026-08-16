# Changelog

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
