---
name: product
description: Query/create AI products on fore.vip. Supports auto-publish with tag-based smart fill.
version: 0.0.7
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - Product Catalog
  - Auto Publish
  - Smart Fill
  - 产品查询
  - 智能发布
  - fore.vip
---

# Product Skill

Query and create **AI products** on **fore.vip** platform.

**Tools**: 
- `query_kl` (public) - Query products by tag
- `create_kl` (🔐 requires Open Key) - Create/publish product
- `auto_publish_kl` (🔐 requires Open Key) - **Smart auto-fill & publish**

## 🔐 Authentication

### Get Open Key

1. Register/Login on [fore.vip](https://fore.vip)
2. Go to **User Center** → **API Settings**
3. Copy your **Open Key**

### Header Format

```http
Authorization: Bearer <your_open_key>
```

or

```http
X-Open-Key: <your_open_key>
```

---

## 🚀 New: Auto Publish (Smart Fill)

**v0.0.7 Feature**: User provides only a **tag**, Agent automatically:
1. Queries hottest products with that tag
2. Extracts best product as template
3. Auto-fills all fields
4. Submits for publishing (with user confirmation)

### Workflow

```
User: "发布一个 推荐 标签的产品"
   ↓
Agent calls query_kl(tag="推荐", limit=1)
   ↓
Get hottest product: {name, content, pic, tag, url}
   ↓
Agent shows preview to user
   ↓
User confirms
   ↓
Agent calls create_kl with auto-filled data
   ↓
Publish success!
```

### Example Conversation

**User**: 帮我发布一个"推荐"标签的产品

**Agent**: 
```
🔍 正在查找"推荐"标签下最热门的产品...

找到热门产品：
- 名称：AI 文案助手
- 热度：21307866
- 描述：请你扮演一个优质 AI 文案助手...

是否以此产品为模板进行发布？
- 名称：AI 文案助手 (复制)
- 内容：[原内容]
- 标签：推荐
- 图片：[原图片]
```

**User**: 确认发布

**Agent**: 
```
✅ 发布成功！
产品 ID: xxx
链接：https://fore.vip/p?id=xxx
```

---

## 🌐 MCP Endpoints

### query_kl (Public)

**URL**: `https://api.fore.vip/mcp/query_kl`  
**Method**: `POST`  
**Auth**: ❌ Public

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tag` | string | - | Product tag |
| `limit` | number | 20 | Max results (1-100) |
| `skip` | number | 0 | Pagination |

#### Example

```bash
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"tag":"推荐","limit":10}'
```

#### Response

```json
{
  "success": true,
  "total": 10,
  "data": [
    {
      "id": "xxx",
      "name": "AI 助手",
      "content": "描述内容...",
      "pic": ["url1", "url2"],
      "tag": "推荐",
      "hot": 21307866,
      "url": "https://..."
    }
  ]
}
```

---

### create_kl (Auth Required)

**URL**: `https://api.fore.vip/mcp/create_kl`  
**Method**: `POST`  
**Auth**: 🔐 Required

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Product name (≥2 chars) |
| `content` | string | Description (≥10 chars) |

#### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pic` | string[] | [] | Image URLs |
| `tag` | string | "推荐" | Product tag |
| `hot` | number | 0 | Hot score |
| `url` | string | "" | External link |

#### Example

```bash
curl -X POST https://api.fore.vip/mcp/create_kl \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Assistant",
    "content": "Powerful AI product",
    "tag": "推荐",
    "pic": ["https://..."]
  }'
```

---

## 🤖 Agent Implementation (Auto Publish)

### Pseudo Code

```javascript
async function autoPublishKl(tag, openKey) {
  // Step 1: Query hottest product with tag
  const queryRes = await fetch('https://api.fore.vip/mcp/query_kl', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag, limit: 1, skip: 0 })
  });
  const queryData = await queryRes.json();
  
  if (!queryData.success || queryData.total === 0) {
    throw new Error(`No products found with tag: ${tag}`);
  }
  
  // Step 2: Extract hottest product
  const template = queryData.data[0];
  
  // Step 3: Show preview to user
  console.log(`
📦 产品发布预览:
- 名称：${template.name}
- 热度：${template.hot}
- 标签：${template.tag}
- 描述：${template.content.substring(0, 50)}...
- 图片：${template.pic?.length || 0} 张

是否确认发布？(回复"确认"或"取消")
  `);
  
  // Step 4: Wait for user confirmation
  const confirmed = await waitForUserConfirmation();
  if (!confirmed) return;
  
  // Step 5: Publish with auto-filled data
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

### Agent Instructions

**When user says**: "发布一个 [标签] 的产品" or "create a [tag] product"

1. **Check Open Key** - If missing, ask user to provide
2. **Call query_kl** - Get hottest product with that tag (limit: 1)
3. **Show Preview** - Display product info and ask for confirmation
4. **On Confirmation** - Call create_kl with auto-filled data
5. **Show Result** - Display success message with product URL

---

## 📊 Auth Summary

| Tool | Auth | Description |
|------|------|-------------|
| `query_kl` | ❌ Public | Query products by tag |
| `create_kl` | 🔐 Required | Create/publish product |
| `auto_publish_kl` | 🔐 Required | Smart auto-fill & publish |

---

## 📝 Version History

### v0.0.7 (2026-03-24) - Auto Publish

- ✅ Added auto-publish workflow (tag → auto-fill → publish)
- ✅ Agent can query hottest product and use as template
- ✅ User confirmation before publishing
- ✅ Updated documentation with examples

### v0.0.6 (2026-03-24) - Open Key Auth

- ✅ Added Open Key authentication docs

---

**Version**: 0.0.7 | **Updated**: 2026-03-24
