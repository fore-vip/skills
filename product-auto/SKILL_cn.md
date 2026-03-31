---
name: product-auto
description: 批量推送 AI 产品。从外部来源创建多个产品，不查重。
version: 2.1.0
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
- `create_kl`（🔐 需 Open Key）- 批量创建/发布产品

## 🔐 认证方式

### 获取 Open Key

**⚠️ 重要**: 发布产品需要 Open Key。

**获取方式**:
1. 访问 [https://fore.vip](https://fore.vip)
2. 注册或登录账号
3. 进入 **用户中心** → **API 设置**
4. 复制你的 **Open Key**

**如果缺少 Open Key**，Agent 应提示：
```
⚠️ 需要 Open Key 才能发布产品

请前往 https://fore.vip 获取：
1. 访问 https://fore.vip
2. 注册/登录账号
3. 进入 用户中心 → API 设置
4. 复制你的 Open Key

获取后请提供 Open Key，我将继续发布产品。
```

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
1. 检查是否提供 Open Key
   - 如缺失 → 提示用户从 https://fore.vip 获取
   ↓
2. 从外部来源准备产品列表:
   - AI 生成（多个产品）
   - 搜索引擎结果
   - GitHub trending 列表
   - Product Hunt 热门产品
   ↓
3. 验证每个产品:
   - URL 是必填项
   - 内容 ≥50 字符
   ↓
4. 批量调用 create_kl:
   - 直接创建
   - 不查重
   ↓
5. 返回批量结果
   ↓
✅ 批量推送完成！
```

### ⚠️ 重要规则

1. **不查重** - 批量推送，外部处理重复
2. **不使用 query_kl** - 此技能仅创建，不查询
3. **内容必须来自外部来源**（AI、搜索、GitHub 等）
4. **推荐批量大小**: 5-20 个产品
5. **URL 是必填项** - 每个产品必须提供外部链接
6. **内容必须详细** - 每个产品最少 50 字符

---

## 🌐 MCP 接口

### create_kl (需要认证)

**URL**: `https://api.fore.vip/mcp/create_kl`  
**方法**: `POST`  
**认证**: 🔐 需要

#### 必填参数

| 参数 | 类型 | 说明 | 约束 |
|------|------|------|------|
| `name` | string | 产品名称 | ≥2 字符 |
| `content` | string | **详细描述** | **≥50 字符** |
| `url` | string | **外部链接** | **必填，有效 URL** |

#### 可选参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `pic` | string[] | [] | 图片 URL |
| `tag` | string | "推荐" | 产品标签 |
| `hot` | number | 0 | 热度 |

#### 示例

```bash
curl -X POST https://api.fore.vip/mcp/create_kl \
  -H "Authorization: Bearer YOUR_OPEN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI 助手",
    "content": "这是一款强大的 AI 产品，帮助你自动化任务、生成内容、提高生产力，具有先进的自然语言处理能力。",
    "url": "https://example.com/product",
    "tag": "推荐"
  }'
```

#### ⚠️ 验证规则

**调用 create_kl 前确保**:
1. ✅ `url` 已提供且是有效 URL（以 http:// 或 https:// 开头）
2. ✅ `content` 至少 50 字符
3. ✅ `name` 至少 2 字符
4. ✅ Open Key 已提供

**如验证失败**，返回错误：
```
❌ 参数验证失败：
- URL 是必填项，请提供产品外部链接
- 内容描述太短，请至少提供 50 字符的详细介绍
```

---

## 🤖 批量推送实现

### 示例 1: 批量 AI 生成 + 验证

```javascript
async function batchPublish(tags, openKey) {
  // 步骤 0: 检查 Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key：\n1. 访问 https://fore.vip\n2. 注册/登录账号\n3. 进入 用户中心 → API 设置\n4. 复制你的 Open Key'
    };
  }
  
  const results = [];
  
  for (const tag of tags) {
    // AI 生成内容（确保详细内容 + URL）
    const aiPrompt = `为标签"${tag}"生成详细产品信息。包括：
      - 名称（2+ 字符）
      - 详细描述（50+ 字符）
      - 外部 URL（必填）`;
    const aiResponse = await callLLM(aiPrompt);
    const product = parseAIResponse(aiResponse);
    
    // 验证
    if (!product.url || !product.url.startsWith('http')) {
      results.push({ success: false, error: 'URL 是必填项' });
      continue;
    }
    if (!product.content || product.content.length < 50) {
      results.push({ success: false, error: '内容描述太短' });
      continue;
    }
    
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

### 示例 2: GitHub Trending 批量

```javascript
async function batchGitHubTrending(openKey) {
  // 步骤 0: 检查 Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // 获取前 10 个 trending 仓库
  const repos = await fetch('https://api.github.com/trending');
  const top10 = repos.slice(0, 10);
  
  const results = [];
  
  for (const repo of top10) {
    const product = {
      name: repo.name,
      content: repo.description + ' - ' + repo.language + ' 项目，GitHub 获得 ' + repo.stars + ' stars', // 确保 50+ 字符
      url: repo.html_url, // GitHub URL（必填）
      tag: '开源'
    };
    
    // 验证 URL
    if (!product.url || !product.url.startsWith('http')) {
      results.push({ success: false, error: 'URL 缺失' });
      continue;
    }
    
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

### 示例 3: 搜索结果批量

```javascript
async function batchFromSearch(topic, openKey) {
  // 步骤 0: 检查 Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // 搜索多个产品
  const searchQuery = `top ${topic} tools 2026`;
  const results = await searchEngine(searchQuery);
  
  const products = results.slice(0, 10).map(r => ({
    name: r.title,
    content: r.snippet + ' ' + r.description, // 确保 50+ 字符
    url: r.url, // 搜索结果中的 URL（必填）
    tag: topic
  }));
  
  // 批量创建 + 验证
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

## 📝 输出格式

**批量结果汇总:**

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

**简洁格式:**

```
✅ 批量推送完成 (10/10)
```

**如缺少 Open Key:**

```
⚠️ 需要 Open Key 才能发布产品

请前往 https://fore.vip 获取：
1. 访问 https://fore.vip
2. 注册/登录账号
3. 进入 用户中心 → API 设置
4. 复制你的 Open Key

获取后请提供 Open Key，我将继续发布产品。
```

**如验证失败:**

```
❌ 部分产品验证失败：
- Product A: URL 是必填项
- Product B: 内容描述太短（需要 50+ 字符）
```

---

## 📊 认证摘要

| 工具 | 认证 | 说明 |
|------|------|------|
| `create_kl` | 🔐 需要 | 批量创建产品 |

**注意**: `query_kl` 不是此技能的一部分。如需查重请使用 `product-create` 技能。

---

## 🔄 技能对比

| 功能 | `product-auto` (此技能) | `product-create` |
|------|------------------|------------------|
| **用途** | 批量推送 | 单个创建 |
| **查重** | ❌ 无 | ✅ 有 |
| **查询工具** | ❌ 无 | ✅ 有 |
| **批量大小** | 5-20 个产品 | 1 个产品 |
| **使用场景** | 批量导入 | 精确单个发布 |

---

## 📝 版本历史

### v2.1.0 (2026-03-31) - 增强验证

- ✅ **新增 Open Key 提示** - 清晰的 https://fore.vip 获取指引
- ✅ **URL 现在是必填项** - 必须提供有效外部链接
- ✅ **内容最少 50 字符** - 确保详细描述
- ✅ **更好的错误信息** - 清晰的验证反馈

### v2.0.0 (2026-03-30) - 仅批量推送

- ✅ **移除 query_kl** - 不再属于此技能
- ✅ **移除查重** - 批量推送不查重
- ✅ **专注批量创建** - 仅 create_kl 工具
- ✅ 拆分单个产品功能到 `product-create` 技能

### v0.0.9 (2026-03-24) - 已弃用

- ⚠️ 旧版本带查重（已移至 `product-create`）

---

**版本**: 2.1.0 | **更新**: 2026-03-31
