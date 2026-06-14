# act — 实现与架构

> 给开发者看的实现文档。

## 架构

```
AI Agent (SKILL.md / mcp.json)
      │ HTTP POST JSON (+ X-API-Key for create)
      ▼
mcp.fore.vip
      │ uniCloud JQL
      ▼
activity 集合 (MongoDB)
```

## 端点

| 端点 | 云对象方法 | 鉴权 |
|------|-----------|------|
| `/act/search` | `search()` | 无 |
| `/act/detail` | `detail()` | 无 |
| `/act/create` | `create()` | `X-API-Key` |

## 鉴权

`create()` 接口要求 HTTP Header `X-API-Key`。当前使用临时静态 Key（`act-dev-key-2026`），后续升级为数据库动态管理。

## 参数解析

```js
const httpInfo = this.getHttpInfo()
// POST body → JSON.parse(httpInfo.body)
// query string → 框架注入 arguments[0]
// Header → httpInfo.headers['x-api-key']
```

## 查询条件

- `dbCmd.and(a, b)` / `dbCmd.or(a, b)` — 逐参传递
- `new RegExp(pattern, 'i')` — 原生正则
- 关键词仅匹配 content + address

## 排序

- 有经纬度 → `aggregate().geoNear()` 距离 ASC
- 无经纬度 → `orderBy('view_count', 'desc')`

## 来源

代码仓库：`fore-vip/base` → `uni_modules/act/`

| 文件 | 说明 |
|------|------|
| `uniCloud/cloudfunctions/act/index.obj.js` | MCP 云对象 |
| `uniCloud/cloudfunctions/tools/index.obj.js` | Tools 清单 |
| `components/act-card.vue` | 活动卡片 |
| `docs/mcp.json` | 工具声明 |
| `docs/SKILL.md` | 模块内文档 |
