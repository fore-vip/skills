---
name: product
description: Query/create AI products. Smart publish with AI-generated content from external sources.
version: 0.1.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - Product Catalog
  - Auto Publish
  - AI Generated
  - 产品查询
  - 智能发布
  - AI 生成
  - fore.vip
---

# Product Skill

Query and create **AI products** on **fore.vip** platform.

**Tools**: 
- `query_kl` (public) - Query products by tag or name
- `create_kl` (🔐 requires Open Key) - Create/publish product
- `smart_publish_kl` (🔐 requires Open Key) - **AI-powered auto-fill from external sources**

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

## 🚀 Smart Publish (v0.0.9)

**⚠️ Important**: Content is generated from **external sources**, NOT from existing products (avoids circular dependency).

### Content Sources

| Source | Description | Example |
|--------|-------------|---------|
| **AI Generation** | Generate content based on tag | "推荐" → AI creates product |
| **Search Engine** | Search for popular products/tools | Search "AI tools 2026" |
| **Session Context** | User's previous messages | Product described in chat |
| **GitHub** | Trending repositories | GitHub trending |
| **Product Hunt** | Daily hot products | ph.com trending |
| **Other Skills** | Copywriting, etc. | Generate descriptions |

### Workflow

```
User: "发布一个 AI 工具 标签的产品"
   ↓
1. Agent asks user for details OR
2. Agent searches external sources:
   - Search engine (Google/Bing)
   - GitHub trending
   - Product Hunt
   - AI generation
   ↓
3. Agent compiles product info:
   - name, content, pic, tag, url
   ↓
4. 🔍 Check if name exists (query_kl with name param)
   ↓
5. If exists → Skip creation, return existing product
   ↓
6. If not exists → Show preview for confirmation
   ↓
7. User confirms
   ↓
8. Call create_kl with collected data
   ↓
✅ Publish success!
```

### ⚠️ Duplicate Check Logic

**Before creating a product, ALWAYS check if the name already exists:**

```javascript
async function smartPublish(tag, openKey) {
  // Step 1: Generate product content using AI
  const aiPrompt = `Generate a product description for tag "${tag}"`;
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // Step 2: 🔍 Check if name exists
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    // Name exists, skip creation
    return {
      skipped: true,
      reason: 'Product name already exists',
      existing: existing.data[0]
    };
  }
  
  // Step 3: Show preview & confirm
  // Step 4: Publish
  return await create_kl(product, openKey);
}
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
| `name` | string | - | **Product name (fuzzy match, case-insensitive)** |
| `limit` | number | 20 | Max results (1-100) |
| `skip` | number | 0 | Pagination |

#### Example

```bash
# Query by tag
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"tag":"推荐","limit":10}'

# Query by name (fuzzy match)
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"name":"Cursor","limit":5}'
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
    "tag": "推荐"
  }'
```

---

## 🤖 Smart Publish Implementation

### Method 1: AI Generation (Recommended)

**Use Case**: User provides tag, AI generates content

```javascript
async function smartPublish(tag, openKey) {
  // Step 1: Generate product content using AI
  const aiPrompt = `
Generate a product description for tag "${tag}":
- Product name (creative, catchy)
- Description (50-100 chars, engaging)
- Suggested image keywords
- External URL (if applicable)
  `;
  
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // Step 2: 🔍 Check if name exists
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return {
      skipped: true,
      reason: 'Product name already exists',
      existing: existing.data[0]
    };
  }
  
  // Step 3: Show preview
  console.log(`
📦 产品预览:
- 名称：${product.name}
- 描述：${product.content}
- 标签：${tag}
- 图片来源：AI 生成建议

是否确认发布？(确认/取消)
  `);
  
  // Step 4: Wait for confirmation
  if (!await confirm()) return;
  
  // Step 5: Publish
  return await create_kl(product, openKey);
}
```

### Method 2: Search Engine

**Use Case**: Find real products/tools online

```javascript
async function publishFromSearch(topic, openKey) {
  // Step 1: Search web
  const searchQuery = `best ${topic} tools 2026`;
  const results = await searchEngine(searchQuery);
  
  // Step 2: Extract top result
  const topResult = results[0];
  const product = {
    name: topResult.title,
    content: topResult.snippet,
    url: topResult.url,
    tag: topic
  };
  
  // Step 3: 🔍 Check if name exists
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 4: Confirm & publish
  // ...
}
```

### Method 3: Session Context

**Use Case**: User described product in conversation

```javascript
async function publishFromContext(sessionHistory, openKey) {
  // Step 1: Analyze conversation
  const productInfo = extractProductFromChat(sessionHistory);
  
  // Step 2: Fill missing fields with AI
  const completeProduct = await aiFill(productInfo);
  
  // Step 3: 🔍 Check if name exists
  const existing = await query_kl({ name: completeProduct.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 4: Confirm & publish
  // ...
}
```

### Method 4: GitHub Trending

**Use Case**: Share popular open-source projects

```javascript
async function publishGitHubTrending(language, openKey) {
  // Step 1: Fetch GitHub trending
  const repos = await fetch('https://api.github.com/trending');
  const topRepo = repos[0];
  
  // Step 2: Format as product
  const product = {
    name: topRepo.name,
    content: topRepo.description,
    url: topRepo.html_url,
    tag: language || '开源'
  };
  
  // Step 3: 🔍 Check if name exists
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 4: Confirm & publish
  // ...
}
```

---

## 📝 User Conversation Examples

### Example 1: AI Generation

```
User: 帮我发布一个"AI 工具"标签的产品

Agent: 
🤖 正在为您生成"AI 工具"相关产品内容...

📦 产品预览:
- 名称：智能写作助手 Pro
- 描述：基于最新 AI 技术的写作助手，支持多语言、风格调整、语法检查，让您的写作更高效。
- 标签：AI 工具
- 图片来源：建议使用 AI 生成工具图标

是否确认发布？(确认/取消)

User: 确认

Agent:
✅ 发布成功！
产品 ID: xxx
链接：https://fore.vip/p?id=xxx
```

### Example 2: From Search

```
User: 发布一个关于"Notion 替代品"的产品

Agent:
🔍 正在搜索"Notion 替代品 2026"...

找到热门产品：Anytype
- 描述：Local-first, E2E encrypted note-taking app
- 链接：https://anytype.io
- 来源：Product Hunt #1 today

是否发布此产品？(确认/取消)

User: 确认

Agent:
✅ 发布成功！
```

### Example 3: From Context

```
User: 我想分享一个很棒的 AI 工具，叫 Cursor，是一个 AI 代码编辑器

[... conversation continues ...]

User: 把刚才说的 Cursor 发布到平台上

Agent:
📦 根据对话内容整理:
- 名称：Cursor
- 描述：AI 代码编辑器，支持智能补全、代码生成
- 标签：AI 工具
- 链接：https://cursor.sh

是否发布？(确认/取消)

User: 确认

Agent:
✅ 发布成功！
```

### Example 4: Duplicate Detection

```
User: 发布一个名为"智能写作助手"的产品

Agent:
🔍 检查产品名称...
⚠️ 发现同名产品已存在：
- 名称：智能写作助手
- 描述：AI 驱动的写作工具
- 链接：https://fore.vip/p?id=xxx

跳过创建，使用现有产品。
```

---

## ⚠️ Important Notes

1. **NO Circular Dependency**: Content comes from external sources, NOT from query_kl
2. **User Confirmation**: Always confirm before publishing
3. **Data Accuracy**: Verify information from external sources
4. **Copyright**: Respect original content ownership
5. **🔍 Duplicate Check**: Always check if product name exists before creating

---

## 📊 Auth Summary

| Tool | Auth | Description |
|------|------|-------------|
| `query_kl` | ❌ Public | Query products by tag or name |
| `create_kl` | 🔐 Required | Create product |
| `smart_publish_kl` | 🔐 Required | AI-powered publish |

---

## 📢 Output Guidelines

**Keep output minimal and focused:**

- ✅ Only show final results (success/failure)
- ✅ Skip intermediate steps unless errors occur
- ✅ Use concise format for success messages
- ✅ Include essential info only (ID, URL)

**Example:**

```
✅ 发布成功！
ID: xxx
链接：https://fore.vip/p?id=xxx
```

---

## 📝 Version History

### v0.0.9 (2026-03-24) - Duplicate Check + Minimal Output

- ✅ Added `name` parameter to `query_kl` (fuzzy match)
- ✅ **Mandatory duplicate check before creation**
- ✅ Updated smart publish workflow with name validation
- ✅ Added output guidelines (minimal, focused results)
- ✅ Updated documentation with examples

### v0.0.8 (2026-03-24) - Smart Publish (External Sources)

- ✅ Fixed circular dependency issue
- ✅ Content from external sources (AI, search, context, GitHub)
- ✅ Added multiple publish methods
- ✅ Updated documentation

### v0.0.7 (2026-03-24) - Auto Publish

- ⚠️ Deprecated: Used query_kl for content (circular dependency)

### v0.0.6 (2026-03-24) - Open Key Auth

- ✅ Added Open Key authentication

---

**Version**: 0.0.9 | **Updated**: 2026-03-24
