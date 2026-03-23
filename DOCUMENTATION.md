# MCP Skills 文档索引

**项目**: 前凌智选 (fore.vip)  
**最后更新**: 2026-03-24  
**版本**: 0.0.7

---

## 🔐 认证 (Authentication)

### Open Key 获取方式

1. 在 [fore.vip](https://fore.vip) 平台注册/登录
2. 进入 **用户中心** → **API 设置**
3. 生成或复制你的 **Open Key**

### Header 格式

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
| `create_activity` | 🔐 需要 | 创建活动 |
| `create_kl` | 🔐 需要 | 发布产品 |
| `query_kl` | ❌ 公开 | 查询产品 |

---

## 🚀 一键发布 (Auto Publish) - v0.0.7 新功能

### 功能说明

用户只需提供**标签**，Agent 自动完成：
1. 查询该标签下最热门的产品
2. 提取产品信息作为模板
3. 显示预览并请求用户确认
4. 自动填充所有字段并提交发布

### 工作流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 用户提供标签                                          │
│     用户："发布一个 推荐 标签的产品"                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  2. Agent 调用 query_kl(tag="推荐", limit=1)              │
│     获取最热门产品                                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  3. Agent 提取产品信息                                    │
│     {name, content, pic, tag, hot, url}                 │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  4. Agent 显示预览                                        │
│     "找到：AI 文案助手 (热度：21307866)                   │
│      是否以此模板发布？(确认/取消)"                       │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  5. 用户确认                                              │
│     用户："确认"                                          │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  6. Agent 调用 create_kl 自动填充所有字段                   │
│     POST /mcp/create_kl                                 │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  7. 发布成功                                              │
│     ✅ 产品 ID: xxx                                       │
│     🔗 https://fore.vip/p?id=xxx                        │
└─────────────────────────────────────────────────────────┘
```

### Agent 实现伪代码

```javascript
async function autoPublishKl(tag, openKey) {
  // Step 1: 查询最热门产品
  const queryRes = await fetch('https://api.fore.vip/mcp/query_kl', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag, limit: 1, skip: 0 })
  });
  const queryData = await queryRes.json();
  
  if (!queryData.success || queryData.total === 0) {
    throw new Error(`标签"${tag}"下没有找到产品`);
  }
  
  // Step 2: 提取模板
  const template = queryData.data[0];
  
  // Step 3: 显示预览
  console.log(`
🔍 找到热门产品：
- 名称：${template.name}
- 热度：${template.hot}
- 标签：${template.tag}
- 描述：${template.content.substring(0, 50)}...
- 图片：${template.pic?.length || 0} 张

是否以此模板发布？(回复"确认"或"取消")
  `);
  
  // Step 4: 等待用户确认
  const confirmed = await waitForUserConfirmation();
  if (!confirmed) return;
  
  // Step 5: 发布
  const createRes = await fetch('https://api.fore.vip/mcp/create_kl', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${openKey}`
    },
    body: JSON.stringify({
      name: template.name,
      content: template.content,
      pic: template.pic || [],
      tag: template.tag,
      hot: template.hot || 0,
      url: template.url || ''
    })
  });
  const createData = await createRes.json();
  
  return createData;
}
```

### 用户对话示例

**场景 1：发布推荐产品**

```
用户：帮我发布一个"推荐"标签的产品

Agent: 
🔍 正在查找"推荐"标签下最热门产品...

找到：AI 文案助手 (热度：21307866)
- 描述：请你扮演一个优质 AI 文案助手...
- 图片：2 张
- 标签：推荐

是否以此模板发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
产品 ID: 69c17ea8c3b5c9fe38676a89
链接：https://fore.vip/p?id=69c17ea8c3b5c9fe38676a89
```

**场景 2：标签下无产品**

```
用户：发布一个"不存在的标签"的产品

Agent:
❌ 抱歉，标签"不存在的标签"下没有找到产品。
请尝试其他标签，如：推荐、热门、游戏、AI 等。
```

**场景 3：用户取消**

```
用户：发布一个"推荐"标签的产品

Agent:
🔍 找到：AI 文案助手 (热度：21307866)
是否以此模板发布？(确认/取消)

用户：取消

Agent:
好的，已取消发布。
```

---

## 🏗️ 架构说明

### 职责分离

```
┌─────────────────────────────────────────┐
│  tools (协议层)                          │
│  - list() → 返回 MCP 工具列表             │
│  - call(params) → 调用工具               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  mcp (业务层)                            │
│  - create_activity(params)              │
│  - query_kl(params)                     │
│  - create_kl(params)                    │
│  职责：纯业务逻辑，从 Header 获取 Open Key   │
└─────────────────────────────────────────┘
```

---

## 🧩 可用工具

### create_activity (v0.0.6)

**认证**: 🔐 需要 Open Key

| 参数 | 类型 | 说明 |
|------|------|------|
| `content` | string | 活动介绍 (≥2 字符) |
| `start_time` | number | 开始时间戳 |
| `address` | string | 活动地址 |
| `wx` | string | 联系方式 |

### query_kl (v0.0.3)

**认证**: ❌ 公开

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `tag` | string | - | 产品标签 |
| `limit` | number | 20 | 最大结果数 |
| `skip` | number | 0 | 分页跳过 |

### create_kl (v0.0.3)

**认证**: 🔐 需要 Open Key

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称 (≥2 字符) |
| `content` | string | 产品描述 (≥10 字符) |
| `pic` | string[] | 图片 URL 数组 |
| `tag` | string | 产品标签 |
| `hot` | number | 热度 |
| `url` | string | 外部链接 |

---

## 🔧 HTTP API 端点

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/tools/list` | GET | ❌ | 获取工具列表 |
| `/mcp/create_activity` | POST | 🔐 | 创建活动 |
| `/mcp/create_kl` | POST | 🔐 | 发布产品 |
| `/mcp/query_kl` | POST | ❌ | 查询产品 |

---

## 📖 使用示例

### 一键发布（Agent 自动处理）

```
用户：发布一个"推荐"标签的产品

Agent 自动执行:
1. query_kl(tag="推荐", limit=1)
2. 显示预览
3. 用户确认
4. create_kl(自动填充数据)
5. 返回结果
```

### 手动发布

```bash
# 查询产品
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"tag":"推荐","limit":10}'

# 发布产品
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

## 📝 更新日志

### v0.0.7 (2026-03-24)

- ✅ 新增**一键发布**功能
- ✅ Agent 可自动查询热门产品并填充
- ✅ 用户确认机制
- ✅ 完善的中英文文档

### v0.0.6 (2026-03-24)

- ✅ Open Key 认证文档

---

**维护者**: wise · 严谨专业版  
**微信**: forevip123
