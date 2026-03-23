# MCP Skills 文档索引

**项目**: 前凌智选 (fore.vip)  
**最后更新**: 2026-03-23  
**版本**: 0.0.4

---

## 🏗️ 架构说明

### 职责分离

```
┌─────────────────────────────────────────┐
│  tools (协议层)                          │
│  URL: /tools                            │
│  - list() → 返回 MCP 工具列表             │
│  - call(params) → 调用工具               │
│  职责：处理 JSON-RPC 2.0 协议格式          │
└──────────────┬──────────────────────────┘
               │ 调用
               ▼
┌─────────────────────────────────────────┐
│  mcp (业务层)                            │
│  URL: 云对象内部调用                      │
│  - create_activity(params)              │
│  - query_kl(params)                     │
│  - create_kl(params)                    │
│  职责：纯业务逻辑，不管协议格式            │
└─────────────────────────────────────────┘
```

### 文件位置

```
/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/
├── tools/
│   └── index.obj.js          # MCP 协议层（tools_list, tools_call）
└── mcp/
    └── index.obj.js          # 业务逻辑层（create_activity, query_kl, create_kl）
```

---

## 🧩 可用工具

### create_activity (v0.0.3)

**MCP 工具**: `create_activity`  
**端点**: `https://api.fore.vip/tools/call`

#### 必需参数 (4 个)

| 参数 | 类型 | 说明 |
|------|------|------|
| `content` | string | 活动介绍 (≥2 字符) |
| `start_time` | number | 开始时间戳 (毫秒) |
| `address` | string | 活动地址 |
| `wx` | string | 联系方式 (微信) |

#### 可选参数 (6 个)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `end_time` | number | - | 结束时间戳 |
| `location` | object | - | GeoJSON 坐标 |
| `range` | number | 0 | 门票金额 (分) |
| `pay` | boolean | false | 是否付费 |
| `url` | string | - | 外部链接 |

---

### product (v0.0.2)

**MCP 工具**: `query_kl`, `create_kl`  
**端点**: `https://api.fore.vip/tools/call`

#### query_kl - 查询产品

**可选参数** (3 个):

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tag` | string | - | 产品标签过滤 |
| `limit` | number | 20 | 最大返回结果数 (1-100) |
| `skip` | number | 0 | 分页跳过的结果数 |

#### create_kl - 发布产品

**必需参数** (3 个):

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称 (≥2 字符) |
| `content` | string | 产品描述 (≥10 字符) |
| `user` | string | 创建者用户 ID |

**可选参数** (4 个):

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pic` | string[] | [] | 图片 URL 数组 |
| `tag` | string | "推荐" | 产品标签 |
| `hot` | number | 0 | 热度分数 |
| `url` | string | "" | 外部链接 |

---

## 🔧 HTTP API 端点

### 基础 URL

```
https://api.fore.vip
```

### 端点列表

| 端点 | 方法 | 说明 | 云对象 |
|------|------|------|--------|
| `/tools/list` | GET | 获取 MCP 工具列表 | tools |
| `/tools/call` | POST | 调用 MCP 工具 | tools |

### 协议

- **规范**: Model Context Protocol (MCP)
- **格式**: JSON-RPC 2.0

---

## 📖 使用示例

### 获取工具列表

```bash
curl https://api.fore.vip/tools/list
```

### 调用工具

```bash
# 发布产品
curl -X POST https://api.fore.vip/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_kl",
    "arguments": {
      "name": "AI 智能助手",
      "content": "这是一款强大的 AI 智能助手产品，可以帮助您高效完成各种任务。",
      "user": "6437c73e09e2988160cb54f6",
      "pic": ["https://example.com/image.jpg"],
      "tag": "推荐",
      "hot": 0,
      "url": "https://example.com"
    }
  }'

# 查询产品
curl -X POST https://api.fore.vip/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "query_kl",
    "arguments": {
      "tag": "推荐",
      "limit": 10,
      "skip": 0
    }
  }'
```

---

## 🗄️ 数据库结构

### kl 集合 (产品)

```javascript
{
  _id: "产品 ID",
  name: "产品名称",
  content: "产品描述",
  pic: ["图片 URL 数组"],
  tag: "标签",
  hot: 0,
  url: "外部链接",
  user: "创建者 ID",
  update_date: 1711094400000
}
```

### act 集合 (活动)

```javascript
{
  _id: "活动 ID",
  kid: "关联机器人 ID",
  user: "创建者 ID",
  content: "活动介绍",
  start_time: 1711094400000,
  end_time: 1711108800000,
  address: "地址文本",
  location: { type: "Point", coordinates: [经度，纬度] },
  range: 0,
  pay: false,
  url: "",
  wx: "",
  type: 0,
  hot: 0,
  create_date: 1711000000000
}
```

---

## 📝 更新日志

### v0.0.4 (2026-03-23)

- ✅ 新增 `create_kl` 工具 - 发布产品功能
- ✅ **架构重构**: 分离 tools (协议层) 和 mcp (业务层)
- ✅ tools 云对象：处理 JSON-RPC 2.0 协议
- ✅ mcp 云对象：纯业务逻辑

### v0.0.3 (2026-03-20)

- ✅ 修正必需参数：`content`, `start_time`, `address`, `wx`
- ✅ 更新错误代码表

---

**维护者**: wise · 严谨专业版  
**联系方式**: forevip123 (微信)
