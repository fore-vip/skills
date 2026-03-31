---
name: product-create
description: Create single AI product with duplicate check. Content from external sources (AI, search, GitHub, etc.).
version: 1.1.0
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
2. Get product info from external source:
   - AI generation
   - Search engine
   - GitHub trending
   - Product Hunt
   - User conversation context
   ↓
3. 🔍 Check if name exists (query_kl with name param)
   ↓
4. If exists → Skip, return existing product
   ↓
5. If not exists → Show preview for confirmation
   ↓
6. User confirms
   ↓
7. Call create_kl
   ↓
✅ Publish success!
```

### ⚠️ Important Rules

1. **Content MUST come from external sources** (AI, search, GitHub, etc.)
2. **NEVER use query_kl to get content** (circular dependency)
3. **ALWAYS check duplicate before creation**
4. **ALWAYS get user confirmation before publishing**
5. **URL is REQUIRED** - Must provide external link
6. **Content must be detailed** - Minimum 50 characters

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

## 🤖 Implementation Examples

### Example 1: AI Generation with Validation

```javascript
async function createProduct(tag, openKey) {
  // Step 0: Check Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key：\n1. 访问 https://fore.vip\n2. 注册/登录账号\n3. 进入 用户中心 → API 设置\n4. 复制你的 Open Key'
    };
  }
  
  // Step 1: Generate content using AI (ensure detailed content)
  const aiPrompt = `Generate a detailed product for tag "${tag}". Include:
    - Name (2+ chars)
    - Detailed description (50+ chars)
    - External URL (required)`;
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // Step 2: Validate required fields
  if (!product.url || !product.url.startsWith('http')) {
    return { error: 'URL 是必填项，请提供有效的产品链接' };
  }
  if (!product.content || product.content.length < 50) {
    return { error: '内容描述太短，请至少提供 50 字符的详细介绍' };
  }
  
  // Step 3: 🔍 Check duplicate
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return {
      skipped: true,
      reason: 'Product name already exists',
      existing: existing.data[0]
    };
  }
  
  // Step 4: Confirm & publish
  // Step 5: Call create_kl
  return await create_kl(product, openKey);
}
```

### Example 2: From Search with URL Validation

```javascript
async function createFromSearch(topic, openKey) {
  // Step 0: Check Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // Step 1: Search web
  const results = await searchEngine(`best ${topic} tools 2026`);
  const product = {
    name: results[0].title,
    content: results[0].snippet + ' ' + results[0].description, // Ensure 50+ chars
    url: results[0].url, // URL from search result
    tag: topic
  };
  
  // Step 2: Validate
  if (!product.url || !product.url.startsWith('http')) {
    return { error: 'URL 是必填项' };
  }
  if (product.content.length < 50) {
    // Enrich content
    product.content = await enrichContent(product.name, product.content);
  }
  
  // Step 3: 🔍 Check duplicate
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 4: Confirm & publish
  return await create_kl(product, openKey);
}
```

### Example 3: From GitHub Trending

```javascript
async function createGitHubTrending(openKey) {
  // Step 0: Check Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // Step 1: Fetch GitHub trending
  const repos = await fetch('https://api.github.com/trending');
  const topRepo = repos[0];
  
  const product = {
    name: topRepo.name,
    content: topRepo.description + ' - ' + topRepo.language + ' project with ' + topRepo.stars + ' stars', // Ensure 50+ chars
    url: topRepo.html_url, // GitHub URL
    tag: '开源'
  };
  
  // Step 2: Validate
  if (!product.url || !product.url.startsWith('http')) {
    return { error: 'URL 是必填项' };
  }
  
  // Step 3: 🔍 Check duplicate
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // Step 4: Confirm & publish
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
❌ 参数验证失败：
- URL 是必填项，请提供产品外部链接
- 内容描述太短，请至少提供 50 字符的详细介绍
```

---

## 📊 Auth Summary

| Tool | Auth | Description |
|------|------|-------------|
| `query_kl` | ❌ Public | Check duplicate (name only) |
| `create_kl` | 🔐 Required | Create product |

---

## 📝 Version History

### v1.1.0 (2026-03-31) - Enhanced Validation

- ✅ **Added Open Key prompt** - Clear instructions to get from https://fore.vip
- ✅ **URL is now REQUIRED** - Must provide valid external link
- ✅ **Content minimum 50 chars** - Ensure detailed descriptions
- ✅ **Better error messages** - Clear validation feedback

### v1.0.0 (2026-03-30) - Initial Release

- ✅ Split from `product` skill
- ✅ Focused on single product creation
- ✅ Mandatory duplicate check
- ✅ Content from external sources only

---

**Version**: 1.1.0 | **Updated**: 2026-03-31
