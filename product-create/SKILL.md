---
name: product-create
description: Create single AI product with duplicate check. Content from external sources (AI, search, GitHub, etc.).
version: 1.0.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - Product Create
  - Single Product
  - Duplicate Check
  - fore.vip
---

# Product Create Skill

Create **single AI product** on **fore.vip** platform with automatic duplicate detection.

**Tools**: 
- `query_kl` (public) - Check if product name exists
- `create_kl` (🔐 requires Open Key) - Create/publish product

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

## 🚀 Usage

### Workflow

```
1. Get product info from external source:
   - AI generation
   - Search engine
   - GitHub trending
   - Product Hunt
   - User conversation context
   ↓
2. 🔍 Check if name exists (query_kl with name param)
   ↓
3. If exists → Skip, return existing product
   ↓
4. If not exists → Show preview for confirmation
   ↓
5. User confirms
   ↓
6. Call create_kl
   ↓
✅ Publish success!
```

### ⚠️ Important Rules

1. **Content MUST come from external sources** (AI, search, GitHub, etc.)
2. **NEVER use query_kl to get content** (circular dependency)
3. **ALWAYS check duplicate before creation**
4. **ALWAYS get user confirmation before publishing**

---

## 🌐 MCP Endpoints

### query_kl (Public)

**URL**: `https://api.fore.vip/mcp/query_kl`  
**Method**: `POST`  
**Auth**: ❌ Public

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | - | **Product name (fuzzy match, case-insensitive)** |
| `limit` | number | 1 | Max results (use 1 for duplicate check) |

#### Example

```bash
# Check if product name exists
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"name":"Cursor","limit":1}'
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

## 🤖 Implementation Examples

### Example 1: AI Generation

```javascript
async function createProduct(tag, openKey) {
  // Step 1: Generate content using AI
  const aiPrompt = `Generate a product for tag "${tag}"`;
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // Step 2: 🔍 Check duplicate
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return {
      skipped: true,
      reason: 'Product name already exists',
      existing: existing.data[0]
    };
  }
  
  // Step 3: Confirm & publish
  // Step 4: Call create_kl
  return await create_kl(product, openKey);
}
```

### Example 2: From Search

```javascript
async function createFromSearch(topic, openKey) {
  // Step 1: Search web
  const results = await searchEngine(`best ${topic} tools 2026`);
  const product = {
    name: results[0].title,
    content: results[0].snippet,
    url: results[0].url,
    tag: topic
  };
  
  // Step 2: 🔍 Check duplicate
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 3: Confirm & publish
  return await create_kl(product, openKey);
}
```

### Example 3: From GitHub Trending

```javascript
async function createGitHubTrending(openKey) {
  // Step 1: Fetch GitHub trending
  const repos = await fetch('https://api.github.com/trending');
  const topRepo = repos[0];
  
  const product = {
    name: topRepo.name,
    content: topRepo.description,
    url: topRepo.html_url,
    tag: '开源'
  };
  
  // Step 2: 🔍 Check duplicate
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 3: Confirm & publish
  return await create_kl(product, openKey);
}
```

---

## 📝 Output Format

**Keep output minimal:**

```
✅ 发布成功！
ID: xxx
链接：https://fore.vip/p?id=xxx
```

**If duplicate:**

```
⚠️ 产品名称已存在，跳过创建
现有产品：xxx
链接：https://fore.vip/p?id=xxx
```

---

## 📊 Auth Summary

| Tool | Auth | Description |
|------|------|-------------|
| `query_kl` | ❌ Public | Check duplicate (name only) |
| `create_kl` | 🔐 Required | Create product |

---

## 📝 Version History

### v1.0.0 (2026-03-30) - Initial Release

- ✅ Split from `product` skill
- ✅ Focused on single product creation
- ✅ Mandatory duplicate check
- ✅ Content from external sources only

---

**Version**: 1.0.0 | **Updated**: 2026-03-30
