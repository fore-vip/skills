# Changelog

## [2.1.0] — 2026-06-14

### Added
- `create_activity` MCP 工具：创建活动
- `POST /act/create` 端点（Header X-API-Key 静态鉴权）
- 创建参数校验：content/address 必填 + 长度限制

### Changed
- tools/list 新增 create_activity 工具声明
- mcp.json 新增 auth 区块 + create tool schema
- SKILL.md 新增 create_activity 文档

---

## [2.0.1] — 2026-06-14

### Added
- act SKILL: search_activities + get_activity_detail MCP tools
- GEO 空间搜索（MongoDB geoNear）
- 双模式排序（距离/热度自动切换）
- 关键词模糊搜索（content + address）
- 类型筛选（sport/culture/volunteer/other）
- 浏览量异步自增
- act/mcp.json 工具声明
- LICENSE (MIT)
- .gitignore

### Fixed
- POST body 解析（this.getHttpInfo().body）
- keyword 匹配条件（dbCmd.or 逐参传递）
- 参数类型归一化（parseInt/parseFloat/String.trim）

---

## [2.0.0] — 2026-06-01

### Added
- Skills 仓库初始化
- act 云对象骨架
- tools/list 端点
- act-card.vue 组件
