# act — 活动 MCP Skill

> 通用 Agent SKILL，不绑定具体平台。遵循 skills.sh 规范。

## 架构

```
AI Agent（读取 SKILL.md）
      │
      │ HTTP POST JSON
      ▼
┌─────────────────────────┐
│  MCP 服务 (mcp.fore.vip) │
│  · /act/search          │
│  · /act/detail          │
│  · /tools/list          │
└───────────┬─────────────┘
            │ uniCloud JQL
            ▼
┌─────────────────────────┐
│  activity 集合 (MongoDB) │
└─────────────────────────┘
```

## MCP 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `https://mcp.fore.vip/act/search` | POST | 搜索活动 |
| `https://mcp.fore.vip/act/detail` | POST | 活动详情 |
| `https://mcp.fore.vip/tools/list` | POST | 工具清单 |

## 实现要点

### 参数解析
uniCloud URL化云对象通过 `this.getHttpInfo().body` 获取 POST body，同时兼容 query string 参数注入。参照 `ai/mod/mcp` 实现。

### 查询条件构建
- `dbCmd.and(a, b)` / `dbCmd.or(a, b)` — **必须逐参传递**，不可用 `dbCmd.and([arr])` 数组单参形式，否则嵌套 OR 条件会被静默丢弃
- `new RegExp(pattern, 'i')` — 使用原生正则，非 `db.RegExp`
- 关键词仅匹配 content + address，tags 为数组字段不支持 JQL 正则

### 双模式排序
- 有经纬度 → `aggregate().geoNear()`，距离升序
- 无经纬度 → `orderBy('view_count', 'desc')`，热度降序
- 关键词 / 类型筛选可叠加

## 核心文件

| 文件 | 说明 |
|------|------|
| `uni_modules/act/uniCloud/cloudfunctions/act/index.obj.js` | MCP 云对象 |
| `uni_modules/act/uniCloud/cloudfunctions/tools/index.obj.js` | Tools 清单 |
| `uni_modules/act/components/act-card.vue` | 活动卡片组件 |
| `uni_modules/act/docs/mcp.json` | MCP 工具声明 |
| `uni_modules/act/docs/SKILL.md` | 模块内文档 |
