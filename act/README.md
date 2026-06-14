# act — 实现与架构

> 给开发者看的实现文档，Agent 看 SKILL.md。

## 架构

```
AI Agent (SKILL.md / mcp.json)
      │ HTTP POST JSON
      ▼
mcp.fore.vip
      │ uniCloud JQL
      ▼
activity 集合 (MongoDB)
```

## 端点

| 端点 | 云对象 | 方法 |
|------|--------|------|
| `/act/search` | `act/index.obj.js` | `search()` |
| `/act/detail` | `act/index.obj.js` | `detail()` |
| `/tools/list` | `tools/index.obj.js` | `list()` |

## 参数解析

```js
const httpInfo = this.getHttpInfo()
const body = httpInfo?.body ? JSON.parse(httpInfo.body) : {}
// query string 参数由框架注入到函数参数（均为字符串）
// POST body 手动解析后合并，POST 优先
```

## 查询条件

- `dbCmd.and(a, b)` / `dbCmd.or(a, b)` — 逐参传递，不可用数组形式
- `new RegExp(pattern, 'i')` — 原生正则，非 `db.RegExp`
- 关键词仅匹配 content + address（tags 为数组不支持 JQL 正则）

## 排序

- 有经纬度 → `aggregate().geoNear()` 距离 ASC
- 无经纬度 → `orderBy('view_count', 'desc')`
- 过滤条件叠加在两种模式

## 来源

代码仓库：`fore-vip/base` → `uni_modules/act/`

| 文件 | 说明 |
|------|------|
| `uniCloud/cloudfunctions/act/index.obj.js` | MCP 云对象 |
| `uniCloud/cloudfunctions/tools/index.obj.js` | Tools 清单 |
| `components/act-card.vue` | 活动卡片组件 |
| `docs/mcp.json` | 工具声明（静态副本） |
| `docs/SKILL.md` | 模块内文档 |
