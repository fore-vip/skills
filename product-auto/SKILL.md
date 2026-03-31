---
name: product-auto
description: Batch push AI products. Create multiple products from external sources (AI, search, GitHub, etc.) without duplicate check.
version: 2.0.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - Batch Push
  - Multiple Products
  - Auto Publish
  - fore.vip
---

# Product Batch Push Skill

**Batch push multiple AI products** to **fore.vip** platform. 

**⚠️ Important**: This skill is for **BATCH PUSH ONLY**. No duplicate check, no query. Use `product-create` skill for single product with duplicate detection.

**Tools**: 
- `create_kl` (🔐 requires Open Key) - Create/publish products in batch

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
1. Prepare product list from external sources:
   - AI generation (multiple products)
   - Search engine results
   - GitHub trending list
   - Product Hunt hot products
   ↓
2. For each product in batch:
   - Call create_kl directly
   - No duplicate check
   ↓
3. Return batch results
   ↓
✅ Batch push complete!
```

### ⚠️ Important Rules

1. **NO duplicate check** - This is batch push, duplicates handled externally
2. **NO query_kl** - This skill only creates, doesn't query
3. **Content MUST come from external sources** (AI, search, GitHub, etc.)
4. **Batch size recommended**: 5-20 products per batch

---

## 🌐 MCP Endpoints

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

## 🤖 Batch Push Implementation

### Example 1: Batch AI Generation

```javascript
async function batchPublish(tags, openKey) {
  const results = [];
  
  for (const tag of tags) {
    // Generate content using AI
    const aiPrompt = `Generate a product for tag "${tag}"`;
    const aiResponse = await callLLM(aiPrompt);
    const product = parseAIResponse(aiResponse);
    
    // Create directly (no duplicate check)
    const result = await create_kl(product, openKey);
    results.push(result);
  }
  
  return {
    total: results.length,
    success: results.filter(r => r.success).length,
    results: results
  };
}
```

### Example 2: Batch from GitHub Trending

```javascript
async function batchGitHubTrending(openKey) {
  // Fetch top 10 trending repos
  const repos = await fetch('https://api.github.com/trending');
  const top10 = repos.slice(0, 10);
  
  const results = [];
  
  for (const repo of top10) {
    const product = {
      name: repo.name,
      content: repo.description,
      url: repo.html_url,
      tag: '开源'
    };
    
    // Create directly (no duplicate check)
    const result = await create_kl(product, openKey);
    results.push(result);
  }
  
  return {
    total: results.length,
    success: results.filter(r => r.success).length,
    results: results
  };
}
```

### Example 3: Batch from Search Results

```javascript
async function batchFromSearch(topic, openKey) {
  // Search for multiple products
  const searchQuery = `top ${topic} tools 2026`;
  const results = await searchEngine(searchQuery);
  
  const products = results.slice(0, 10).map(r => ({
    name: r.title,
    content: r.snippet,
    url: r.url,
    tag: topic
  }));
  
  // Batch create
  const createResults = [];
  for (const product of products) {
    const result = await create_kl(product, openKey);
    createResults.push(result);
  }
  
  return {
    total: createResults.length,
    success: createResults.filter(r => r.success).length,
    results: createResults
  };
}
```

---

## 📝 Output Format

**Batch result summary:**

```
✅ 批量推送完成！
总计：10 个
成功：8 个
失败：2 个

成功列表:
- Product A: https://fore.vip/p?id=xxx
- Product B: https://fore.vip/p?id=yyy
...
```

**Minimal format:**

```
✅ 批量推送完成 (10/10)
```

---

## 📊 Auth Summary

| Tool | Auth | Description |
|------|------|-------------|
| `create_kl` | 🔐 Required | Batch create products |

**Note**: `query_kl` is NOT part of this skill. Use `product-create` skill if you need duplicate detection.

---

## 🔄 Skill Comparison

| Feature | `product-auto` (this) | `product-create` |
|---------|------------------|------------------|
| **Purpose** | Batch push | Single create |
| **Duplicate Check** | ❌ No | ✅ Yes |
| **Query Tool** | ❌ No | ✅ Yes |
| **Batch Size** | 5-20 products | 1 product |
| **Use Case** | Bulk import | Careful single publish |

---

## 📝 Version History

### v2.0.0 (2026-03-30) - Batch Push Only

- ✅ **Removed query_kl** - No longer part of this skill
- ✅ **Removed duplicate check** - Batch push doesn't check duplicates
- ✅ **Focused on batch creation** - Only create_kl tool
- ✅ Split single-product functionality to `product-create` skill

### v0.0.9 (2026-03-24) - Deprecated

- ⚠️ Old version with duplicate check (moved to `product-create`)

---

**Version**: 2.0.0 | **Updated**: 2026-03-30
