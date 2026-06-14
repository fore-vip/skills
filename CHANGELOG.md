# Changelog

## [2.1.1] — 2026-06-14

### Added
- 模式1：原子级交互创建（多轮收集 Key→封面→主题→地址→坐标→时间→确认→单次MCP）
- 模式2：自动化批量创建（搜索→封面→坐标→循环 create_activity→汇总）
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
