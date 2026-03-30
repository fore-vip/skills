---
name: product
description: 批量推送 AI 产品。从外部来源创建多个产品，不查重。
version: 2.0.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - 批量推送
  - 多个产品
  - 自动发布
  - fore.vip
---

# 产品批量推送技能

**批量推送多个 AI 产品**到 **fore.vip** 平台。

**⚠️ 重要**：此技能仅用于**批量推送**。无查重、无查询。单个产品创建请使用 `product-create` 技能。

**工具**:
- `create_kl`（🔐 需 Open Key） - 批量创建/发布产品

## 🔐 认证方式

### 获取 Open Key

1. 在 [fore.vip](https://fore.vip) 注册/登录
2. 进入 **用户中心** → **API 设置**
3. 复制你的 **Open Key**

### 请求头格式

```http
Authorization: Bearer <your_open_key>
```

或

```http
X-Open-Key: <your_open_key>
```

---

## 🚀 使用说明

### 工作流程

```
1. 从外部来源准备产品列表：
   - AI 生成（多个产品）
   - 搜索引擎结果
   - GitHub trending 列表
   - Product Hunt 热门产品
   ↓
2. 对每个产品：
   - 直接调用 create_kl
   - 不查重
   ↓
3. 返回批量结果
   ↓
✅ 批量推送完成！
```

### ⚠️ 重要规则

1. **不查重** - 批量推送，外部处理重复
2. **不使用 query_kl** - 此技能仅创建，不查询
3. **内容必须来自外部来源**（AI、搜索、GitHub 等）
4. **推荐批量大小**：每次 5-20 个产品

---

## 🌐 MCP 接口

### create_kl（需认证）

**URL**: `https://api.fore.vip/mcp/create_kl`  
**Method**: `POST`  
**认证**: 🔐 必填

#### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称（≥2 个字符） |
| `content` | string | 产品描述（≥10 个字符） |

#### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pic` | string[] | [] | 图片 URL 列表 |
| `tag` | string | "推荐" | 产品标签 |
| `hot` | number | 0 | 热度分 |
| `url` | string | "" | 外部链接 |

#### 示例

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

## 🤖 批量推送实现

### 示例一：批量 AI 生成

```javascript
async function batchPublish(tags, openKey) {
  const results = [];
  
  for (const tag of tags) {
    // 用 AI 生成内容
    const aiPrompt = `根据标签 "${tag}" 生成产品`;
    const aiResponse = await callLLM(aiPrompt);
    const product = parseAIResponse(aiResponse);
    
    // 直接创建（不查重）
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

### 示例二：批量从 GitHub Trending

```javascript
async function batchGitHubTrending(openKey) {
  // 获取前 10 个 trending 仓库
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
    
    // 直接创建（不查重）
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

### 示例三：批量从搜索结果

```javascript
async function batchFromSearch(topic, openKey) {
  // 搜索多个产品
  const searchQuery = `top ${topic} tools 2026`;
  const results = await searchEngine(searchQuery);
  
  const products = results.slice(0, 10).map(r => ({
    name: r.title,
    content: r.snippet,
    url: r.url,
    tag: topic
  }));
  
  // 批量创建
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

## 📝 输出格式

**批量结果汇总：**

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

**精简格式：**

```
✅ 批量推送完成 (10/10)
```

---

## 📊 认证权限总览

| 工具 | 认证 | 说明 |
|------|------|------|
| `create_kl` | 🔐 必填 | 批量创建产品 |

**注意**: `query_kl` 不属于此技能。如需查重请使用 `product-create` 技能。

---

## 🔄 技能对比

| 功能 | `product` (本技能) | `product-create` |
|------|-------------------|------------------|
| **用途** | 批量推送 | 单个创建 |
| **查重** | ❌ 无 | ✅ 有 |
| **查询工具** | ❌ 无 | ✅ 有 |
| **批量大小** | 5-20 个产品 | 1 个产品 |
| **使用场景** | 批量导入 | 精确单个发布 |

---

## 📝 版本历史

### v2.0.0 (2026-03-30) - 仅批量推送

- ✅ **移除 query_kl** - 不再属于此技能
- ✅ **移除查重逻辑** - 批量推送不查重
- ✅ **专注于批量创建** - 仅使用 create_kl 工具
- ✅ 拆分单个产品功能到 `product-create` 技能

### v0.0.9 (2026-03-24) - 已废弃

- ⚠️ 旧版本含查重（已移至 `product-create`）

---

**版本**: 2.0.0 | **更新**: 2026-03-30
