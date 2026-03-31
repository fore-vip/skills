---
name: product-auto
description: Batch push AI products. Create multiple products from external sources (AI, search, GitHub, etc.) without duplicate check.
version: 2.1.0
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

**⚠️ Important**: You need an Open Key to publish products.

**How to get Open Key**:
1. Visit [https://fore.vip](https://fore.vip)
2. Register or Login
3. Go to **User Center** → **API Settings**
4. Copy your **Open Key**

**If Open Key is missing**, the agent should prompt:
```
⚠️ 需要 Open Key 才能发布产品

请前往 https://fore.vip 获取：
1. 访问 https://fore.vip
2. 注册/登录账号
3. 进入 用户中心 → API 设置
4. 复制你的 Open Key

获取后请提供 Open Key，我将继续发布产品。
```

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
1. Check if Open Key is provided
   - If missing → Prompt user to get from https://fore.vip
   ↓
2. Prepare product list from external sources:
   - AI generation (multiple products)
   - Search engine results
   - GitHub trending list
   - Product Hunt hot products
   ↓
3. Validate each product:
   - URL is required
   - Content ≥50 characters
   ↓
4. For each product in batch:
   - Call create_kl directly
   - No duplicate check
   ↓
5. Return batch results
   ↓
✅ Batch push complete!
```

### ⚠️ Important Rules

1. **NO duplicate check** - This is batch push, duplicates handled externally
2. **NO query_kl** - This skill only creates, doesn't query
3. **Content MUST come from external sources** (AI, search, GitHub, etc.)
4. **Batch size recommended**: 5-20 products per batch
5. **URL is REQUIRED** - Must provide external link for each product
6. **Content must be detailed** - Minimum 50 characters per product

---

## 🌐 MCP Endpoints

### create_kl (Auth Required)

**URL**: `https://api.fore.vip/mcp/create_kl`  
**Method**: `POST`  
**Auth**: 🔐 Required

#### Required Parameters

| Parameter | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `name` | string | Product name | ≥2 characters |
| `content` | string | **Detailed description** | **≥50 characters** |
| `url` | string | **External link** | **REQUIRED, valid URL** |

#### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pic` | string[] | [] | Image URLs |
| `tag` | string | "推荐" | Product tag |
| `hot` | number | 0 | Hot score |

#### Example

```bash
curl -X POST https://api.fore.vip/mcp/create_kl \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Assistant",
    "content": "This is a powerful AI product that helps you automate tasks, generate content, and boost productivity with advanced natural language processing capabilities.",
    "url": "https://example.com/product",
    "tag": "推荐"
  }'
```

#### ⚠️ Validation Rules

**Before calling create_kl, ensure**:
1. ✅ `url` is provided and is a valid URL (starts with http:// or https://)
2. ✅ `content` is at least 50 characters long
3. ✅ `name` is at least 2 characters long
4. ✅ Open Key is provided

**If validation fails**, return error:
```
❌ 参数验证失败：
- URL 是必填项，请提供产品外部链接
- 内容描述太短，请至少提供 50 字符的详细介绍
```

---

## 🤖 Batch Push Implementation

### Example 1: Batch AI Generation with Validation

```javascript
async function batchPublish(tags, openKey) {
  // Step 0: Check Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key：\n1. 访问 https://fore.vip\n2. 注册/登录账号\n3. 进入 用户中心 → API 设置\n4. 复制你的 Open Key'
    };
  }
  
  const results = [];
  
  for (const tag of tags) {
    // Generate content using AI (ensure detailed content + URL)
    const aiPrompt = `Generate a detailed product for tag "${tag}". Include:
      - Name (2+ chars)
      - Detailed description (50+ chars)
      - External URL (required)`;
    const aiResponse = await callLLM(aiPrompt);
    const product = parseAIResponse(aiResponse);
    
    // Validate
    if (!product.url || !product.url.startsWith('http')) {
      results.push({ success: false, error: 'URL 是必填项' });
      continue;
    }
    if (!product.content || product.content.length < 50) {
      results.push({ success: false, error: '内容描述太短' });
      continue;
    }
    
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
  // Step 0: Check Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // Fetch top 10 trending repos
  const repos = await fetch('https://api.github.com/trending');
  const top10 = repos.slice(0, 10);
  
  const results = [];
  
  for (const repo of top10) {
    const product = {
      name: repo.name,
      content: repo.description + ' - ' + repo.language + ' project with ' + repo.stars + ' stars on GitHub', // Ensure 50+ chars
      url: repo.html_url, // GitHub URL (required)
      tag: '开源'
    };
    
    // Validate URL
    if (!product.url || !product.url.startsWith('http')) {
      results.push({ success: false, error: 'URL 缺失' });
      continue;
    }
    
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
  // Step 0: Check Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // Search for multiple products
  const searchQuery = `top ${topic} tools 2026`;
  const results = await searchEngine(searchQuery);
  
  const products = results.slice(0, 10).map(r => ({
    name: r.title,
    content: r.snippet + ' ' + r.description, // Ensure 50+ chars
    url: r.url, // URL from search (required)
    tag: topic
  }));
  
  // Batch create with validation
  const createResults = [];
  for (const product of products) {
    if (!product.url || !product.url.startsWith('http')) {
      createResults.push({ success: false, error: 'URL 缺失' });
      continue;
    }
    if (product.content.length < 50) {
      createResults.push({ success: false, error: '内容太短' });
      continue;
    }
    
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

**If missing Open Key:**

```
⚠️ 需要 Open Key 才能发布产品

请前往 https://fore.vip 获取：
1. 访问 https://fore.vip
2. 注册/登录账号
3. 进入 用户中心 → API 设置
4. 复制你的 Open Key

获取后请提供 Open Key，我将继续发布产品。
```

**If validation fails:**

```
❌ 部分产品验证失败：
- Product A: URL 是必填项
- Product B: 内容描述太短（需要 50+ 字符）
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

### v2.1.0 (2026-03-31) - Enhanced Validation

- ✅ **Added Open Key prompt** - Clear instructions to get from https://fore.vip
- ✅ **URL is now REQUIRED** - Must provide valid external link
- ✅ **Content minimum 50 chars** - Ensure detailed descriptions
- ✅ **Better error messages** - Clear validation feedback

### v2.0.0 (2026-03-30) - Batch Push Only

- ✅ **Removed query_kl** - No longer part of this skill
- ✅ **Removed duplicate check** - Batch push doesn't check duplicates
- ✅ **Focused on batch creation** - Only create_kl tool
- ✅ Split single-product functionality to `product-create` skill

### v0.0.9 (2026-03-24) - Deprecated

- ⚠️ Old version with duplicate check (moved to `product-create`)

---

**Version**: 2.1.0 | **Updated**: 2026-03-31
