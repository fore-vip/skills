---
name: product
description: Query and browse product catalog from fore.vip platform. Use when users want to discover products, search by tags, or view product details.
version: 0.0.1
license: MIT
---

## Description

Queries and browses the product catalog (KL collection) from the fore.vip (前凌智选) platform via MCP Server.

---

## MCP Tool

**Tool Name**: `query_kl`  
**Server**: `fore-vip-mcp`  
**Endpoint**: `https://api.fore.vip/mcp`

---

## Parameters

### Optional (可选参数)

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `tag` | string | - | Product tag to filter (e.g., "推荐", "热门", "新品") | `"推荐"` |
| `limit` | number | `20` | Maximum number of results (1-100) | `50` |
| `skip` | number | `0` | Number of results to skip for pagination | `20` |

> **Note**: All parameters are optional. If no tag is provided, returns all products ordered by popularity.

---

## HTTP API Endpoints

### List Tools

```bash
curl https://api.fore.vip/mcp/tools/list
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "tools": [
      {
        "name": "create_activity",
        "description": "Create offline event for fore.vip platform..."
      },
      {
        "name": "query_kl",
        "description": "Query products (KL collection) by tag. Returns list of products with name, description, images, and metadata.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "tag": {"type": "string", "description": "Product tag to filter (e.g., \"推荐\", \"热门\", \"新品\")"},
            "limit": {"type": "number", "description": "Maximum number of results to return (default: 20, max: 100)"},
            "skip": {"type": "number", "description": "Number of results to skip for pagination (default: 0)"}
          },
          "required": []
        }
      }
    ]
  }
}
```

### Call Tool

```bash
curl -X POST https://api.fore.vip/mcp/tools/call \
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

**Success Response**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\n  \"success\": true,\n  \"total\": 10,\n  \"limit\": 10,\n  \"skip\": 0,\n  \"hasMore\": true,\n  \"data\": [\n    {\n      \"id\": \"kl_xxx\",\n      \"name\": \"Product Name\",\n      \"content\": \"Product description...\",\n      \"pic\": [\"https://...\"],\n      \"tag\": \"推荐\",\n      \"hot\": 100,\n      \"url\": \"https://example.com\",\n      \"update_date\": 1234567890\n    }\n  ]\n}"
    }],
    "isError": false
  }
}
```

**Error Response**:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32000,
    "message": "Tool execution failed"
  }
}
```

---

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Query products by tag
const result = await fetch('https://api.fore.vip/mcp/tools/call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'query_kl',
    arguments: {
      tag: '推荐',
      limit: 20,
      skip: 0
    }
  })
})

const response = await result.json()

// Check for errors
if (response.error) {
  console.error('Error:', response.error.message)
} else {
  const data = JSON.parse(response.result.content[0].text)
  if (data.success) {
    console.log(`Found ${data.total} products`)
    data.data.forEach(product => {
      console.log(`- ${product.name} (${product.tag})`)
    })
  }
}
```

### Pagination Example

```javascript
// Get first page
const page1 = await queryProducts({ tag: '热门', limit: 20, skip: 0 })

// Get second page
if (page1.hasMore) {
  const page2 = await queryProducts({ tag: '热门', limit: 20, skip: 20 })
}
```

### uniCloud (Cloud Function)

```javascript
const mcp = uniCloud.importObject('mcp')

// Query products
const result = await mcp.tools_call({
  name: 'query_kl',
  arguments: {
    tag: '新品',
    limit: 50,
    skip: 0
  }
})

if (result.error) {
  console.error(result.error.message)
} else {
  const data = JSON.parse(result.result.content[0].text)
  console.log('Products:', data.data)
}
```

---

## Response Format

### Success Response Structure

```json
{
  "success": true,
  "total": 20,
  "limit": 20,
  "skip": 0,
  "hasMore": true,
  "data": [
    {
      "id": "kl_xxx",
      "name": "Product Name",
      "content": "Product description text...",
      "pic": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
      "tag": "推荐",
      "hot": 150,
      "url": "https://example.com/product",
      "update_date": 1711094400000
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Query success status |
| `total` | number | Number of products returned in this response |
| `limit` | number | Requested limit value |
| `skip` | number | Requested skip value |
| `hasMore` | boolean | Whether more results are available |
| `data` | array | Array of product objects |

### Product Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Product ID (kl collection _id) |
| `name` | string | Product name |
| `content` | string | Product description |
| `pic` | array | Array of image URLs |
| `tag` | string | Product tag/category |
| `hot` | number | Popularity score |
| `url` | string | External link URL |
| `update_date` | number | Last update timestamp (milliseconds) |

---

## Error Codes

| Code | Error | Cause | Solution |
|------|-------|-------|----------|
| -32602 | `Missing required parameter: name` | name not provided in request | Include `name` field in request body |
| -32602 | `Unknown tool: xxx` | Invalid tool name | Use `query_kl` |
| -32000 | `Tool execution failed` | Database query error | Check server logs |

---

## Frontend Integration (Product Catalog Page)

### Vue 3 Component Example

```vue
<template>
  <view class="product-catalog">
    <!-- Tag Filter -->
    <o-tab-tag 
      :tags="['全部', '推荐', '热门', '新品']"
      :current="currentTag"
      @change="onTagChange"
    />
    
    <!-- Product List -->
    <scroll-view 
      scroll-y 
      class="product-list"
      @scrolltolower="loadMore"
    >
      <o-card 
        v-for="product in products" 
        :key="product.id"
        :title="product.name"
        :content="product.content"
        :bg="product.pic[0]"
        clickable
        @click="goToProduct(product.id)"
      />
      
      <!-- No More Indicator -->
      <o-nomore v-if="!hasMore && products.length > 0" />
      
      <!-- Empty State -->
      <view v-if="products.length === 0" class="empty">
        <text>暂无产品</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTag: '全部',
      products: [],
      skip: 0,
      limit: 20,
      hasMore: true,
      loading: false
    }
  },
  
  onLoad() {
    this.loadProducts()
  },
  
  methods: {
    async loadProducts() {
      if (this.loading) return
      
      this.loading = true
      
      try {
        const response = await fetch('https://api.fore.vip/mcp/tools/call', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'query_kl',
            arguments: {
              tag: this.currentTag === '全部' ? '' : this.currentTag,
              limit: this.limit,
              skip: this.skip
            }
          })
        })
        
        const result = await response.json()
        
        if (result.error) {
          uni.showToast({ title: result.error.message, icon: 'none' })
          return
        }
        
        const data = JSON.parse(result.result.content[0].text)
        
        if (data.success) {
          if (this.skip === 0) {
            this.products = data.data
          } else {
            this.products = [...this.products, ...data.data]
          }
          
          this.hasMore = data.hasMore
          this.skip += data.data.length
        }
      } catch (e) {
        console.error(e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    
    onTagChange(tag) {
      this.currentTag = tag
      this.skip = 0
      this.products = []
      this.hasMore = true
      this.loadProducts()
    },
    
    loadMore() {
      if (this.hasMore && !this.loading) {
        this.loadProducts()
      }
    },
    
    goToProduct(id) {
      uni.navigateTo({
        url: `/ai/s?id=${id}`
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.product-catalog {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.product-list {
  flex: 1;
  padding: 20rpx;
}

.empty {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
}
</style>
```

---

## Notes

1. **Tag Filtering**: If no tag is provided or tag is "全部", returns all products
2. **Pagination**: Use `skip` and `limit` for pagination. Check `hasMore` to determine if more results exist
3. **Ordering**: Results are ordered by `hot` (desc) then `update_date` (desc)
4. **Image URLs**: `pic` field is an array of image URLs, use `pic[0]` for thumbnail
5. **Product Detail**: Use product `id` to navigate to detail page: `/ai/s?id=${id}`

---

## Related Files

| File | Path |
|------|------|
| MCP Cloud Function | `/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/mcp/index.obj.js` |
| Skill Definition | `/Users/codes/git/ai/skills/product/SKILL.md` |
| Product Detail Page | `/Users/codes/git/ai/fore/ai/s.vue` |

---

**Version**: 0.0.1  
**Updated**: 2026-03-21  
**MCP Spec**: https://modelcontextprotocol.io/  
**API**: https://api.fore.vip/mcp  
**Platform**: https://fore.vip
