# MCP Skills 文档索引

**项目**: 前凌智选 (fore.vip)  
**最后更新**: 2026-03-24  
**版本**: 0.0.6

---

## 🔐 认证 (Authentication)

### Open Key 获取方式

**中文**:
1. 在 [fore.vip](https://fore.vip) 平台注册/登录
2. 进入 **用户中心** → **API 设置**
3. 生成或复制你的 **Open Key**
4. 在请求头中包含 Open Key

**English**:
1. Register/Login on [fore.vip](https://fore.vip)
2. Go to **User Center** → **API Settings**
3. Generate/copy your **Open Key**
4. Include in request headers

### Header 格式

使用以下**任一**格式：

```http
Authorization: Bearer <your_open_key>
```

或

```http
X-Open-Key: <your_open_key>
```

### 认证要求

| 工具 | 认证 | 说明 |
|------|------|------|
| `create_activity` | 🔐 需要 | 创建活动需认证 |
| `create_kl` | 🔐 需要 | 发布产品需认证 |
| `query_kl` | ❌ 公开 | 查询产品无需认证 |

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
│  职责：纯业务逻辑，从 Header 获取 Open Key   │
└─────────────────────────────────────────┘
```

### 文件位置

```
/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/
├── tools/
│   └── index.obj.js          # MCP 协议层
└── mcp/
    └── index.obj.js          # 业务逻辑层（含 Open Key 验证）
```

---

## 🧩 可用工具

### create_activity (v0.0.6)

**MCP 工具**: `create_activity`  
**认证**: 🔐 需要 Open Key

#### 必需参数 (4 个)

| 参数 | 类型 | 说明 |
|------|------|------|
| `content` | string | 活动介绍 (≥2 字符) |
| `start_time` | number | 开始时间戳 (毫秒) |
| `address` | string | 活动地址 |
| `wx` | string | 联系方式 (微信) |

#### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `end_time` | number | - | 结束时间戳 |
| `location` | object | - | GeoJSON 坐标 |
| `range` | number | 0 | 门票金额 (分) |
| `pay` | boolean | false | 是否付费 |
| `url` | string | - | 外部链接 |

---

### product (v0.0.3)

**MCP 工具**: `query_kl`, `create_kl`

#### query_kl - 查询产品

**认证**: ❌ 公开（无需认证）

**可选参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tag` | string | - | 产品标签 |
| `limit` | number | 20 | 最大结果数 (1-100) |
| `skip` | number | 0 | 分页跳过数 |

#### create_kl - 发布产品

**认证**: 🔐 需要 Open Key

**必需参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称 (≥2 字符) |
| `content` | string | 产品描述 (≥10 字符) |

**可选参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pic` | string[] | [] | 图片 URL 数组 |
| `tag` | string | "推荐" | 产品标签 |
| `hot` | number | 0 | 热度 |
| `url` | string | "" | 外部链接 |

---

## 🔧 HTTP API 端点

### 基础 URL

```
https://api.fore.vip
```

### 端点列表

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/tools/list` | GET | ❌ | 获取工具列表 |
| `/mcp/create_activity` | POST | 🔐 | 创建活动 |
| `/mcp/create_kl` | POST | 🔐 | 发布产品 |
| `/mcp/query_kl` | POST | ❌ | 查询产品 |

---

## 📖 使用示例

### 创建活动（带认证）

```bash
curl -X POST https://api.fore.vip/mcp/create_activity \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "AI 技术分享会",
    "start_time": 1711094400000,
    "address": "北京三里屯",
    "wx": "forevip123"
  }'
```

### 查询产品（无需认证）

```bash
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{
    "tag": "推荐",
    "limit": 10
  }'
```

### 发布产品（带认证）

```bash
curl -X POST https://api.fore.vip/mcp/create_kl \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI 智能助手",
    "content": "强大的 AI 助手产品",
    "tag": "推荐"
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
  pic: ["图片 URL"],
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
  kid: "关联产品 ID",
  user: "创建者 ID",
  content: "活动介绍",
  start_time: 1711094400000,
  end_time: 1711108800000,
  address: "地址",
  location: { type: "Point", coordinates: [经度，纬度] },
  range: 0,
  pay: false,
  wx: "微信",
  hot: 0
}
```

---

## 📝 更新日志

### v0.0.6 (2026-03-24)

- ✅ 新增 Open Key 认证文档
- ✅ 说明 Header 格式（Authorization / X-Open-Key）
- ✅ 标注每个工具的认证要求
- ✅ 中英文文档同步更新

### v0.0.4 (2026-03-23)

- ✅ 新增 `create_kl` 工具
- ✅ 架构重构：分离 tools 和 mcp

---

**维护者**: wise · 严谨专业版  
**微信**: forevip123
