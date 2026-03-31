---
name: product-create
description: 创建单个 AI 产品，自动查重。内容来自外部来源（AI、搜索、GitHub 等）。
version: 1.1.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - 产品创建
  - 单个产品
  - 自动查重
  - fore.vip
---

# 产品创建技能

在 **fore.vip** 平台创建**单个 AI 产品**，带自动重名检测。

**工具**: 
- `query_kl`（公开）- 检查产品名称是否存在
- `create_kl`（🔐 需 Open Key）- 创建/发布产品

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
2. 从外部来源获取产品信息:
   - AI 生成
   - 搜索引擎
   - GitHub trending
   - Product Hunt
   - 用户对话上下文
   ↓
3. 🔍 检查名称是否存在 (query_kl with name param)
   ↓
4. 如已存在 → 跳过，返回现有产品
   ↓
5. 如不存在 → 显示预览供确认
   ↓
6. 用户确认
   ↓
7. 调用 create_kl
   ↓
✅ 发布成功！
```

### ⚠️ 重要规则

1. **内容必须来自外部来源**（AI、搜索、GitHub 等）
2. **绝不使用 query_kl 获取内容**（循环依赖）
3. **创建前必须查重**
4. **发布前必须获得用户确认**
5. **URL 是必填项** - 必须提供外部链接
6. **内容必须详细** - 最少 50 字符

---

## 🌐 MCP 接口

### query_kl (公开)

**URL**: `https://api.fore.vip/mcp/query_kl`  
**方法**: `POST`  
**认证**: ❌ 公开

#### 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | string | - | **产品名称（模糊匹配，不区分大小写）** |
| `limit` | number | 1 | 最大结果数（查重用 1） |

#### 示例

```bash
# 检查产品名称是否存在
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"name":"Cursor","limit":1}'
```

---

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

## 🤖 实现示例

### 示例 1: AI 生成 + 验证

```javascript
async function createProduct(tag, openKey) {
  // 步骤 0: 检查 Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key：\n1. 访问 https://fore.vip\n2. 注册/登录账号\n3. 进入 用户中心 → API 设置\n4. 复制你的 Open Key'
    };
  }
  
  // 步骤 1: AI 生成内容（确保详细内容）
  const aiPrompt = `为标签"${tag}"生成详细产品信息。包括：
    - 名称（2+ 字符）
    - 详细描述（50+ 字符）
    - 外部 URL（必填）`;
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // 步骤 2: 验证必填字段
  if (!product.url || !product.url.startsWith('http')) {
    return { error: 'URL 是必填项，请提供有效的产品链接' };
  }
  if (!product.content || product.content.length < 50) {
    return { error: '内容描述太短，请至少提供 50 字符的详细介绍' };
  }
  
  // 步骤 3: 🔍 查重
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return {
      skipped: true,
      reason: '产品名称已存在',
      existing: existing.data[0]
    };
  }
  
  // 步骤 4: 确认并发布
  // 步骤 5: 调用 create_kl
  return await create_kl(product, openKey);
}
```

### 示例 2: 搜索 + URL 验证

```javascript
async function createFromSearch(topic, openKey) {
  // 步骤 0: 检查 Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // 步骤 1: 搜索网络
  const results = await searchEngine(`best ${topic} tools 2026`);
  const product = {
    name: results[0].title,
    content: results[0].snippet + ' ' + results[0].description, // 确保 50+ 字符
    url: results[0].url, // 搜索结果中的 URL
    tag: topic
  };
  
  // 步骤 2: 验证
  if (!product.url || !product.url.startsWith('http')) {
    return { error: 'URL 是必填项' };
  }
  if (product.content.length < 50) {
    // 丰富内容
    product.content = await enrichContent(product.name, product.content);
  }
  
  // 步骤 3: 🔍 查重
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 4: 确认并发布
  return await create_kl(product, openKey);
}
```

### 示例 3: GitHub Trending

```javascript
async function createGitHubTrending(openKey) {
  // 步骤 0: 检查 Open Key
  if (!openKey) {
    return {
      error: '需要 Open Key',
      message: '请前往 https://fore.vip 获取 Open Key'
    };
  }
  
  // 步骤 1: 获取 GitHub trending
  const repos = await fetch('https://api.github.com/trending');
  const topRepo = repos[0];
  
  const product = {
    name: topRepo.name,
    content: topRepo.description + ' - ' + topRepo.language + ' 项目，获得 ' + topRepo.stars + ' stars', // 确保 50+ 字符
    url: topRepo.html_url, // GitHub URL
    tag: '开源'
  };
  
  // 步骤 2: 验证
  if (!product.url || !product.url.startsWith('http')) {
    return { error: 'URL 是必填项' };
  }
  
  // 步骤 3: 🔍 查重
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 4: 确认并发布
  return await create_kl(product, openKey);
}
```

---

## 📝 输出格式

**保持输出简洁:**

```
✅ 发布成功！
ID: xxx
链接：https://fore.vip/p?id=xxx
```

**如重复:**

```
⚠️ 产品名称已存在，跳过创建
现有产品：xxx
链接：https://fore.vip/p?id=xxx
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
❌ 参数验证失败：
- URL 是必填项，请提供产品外部链接
- 内容描述太短，请至少提供 50 字符的详细介绍
```

---

## 📊 认证摘要

| 工具 | 认证 | 说明 |
|------|------|------|
| `query_kl` | ❌ 公开 | 查重（仅名称） |
| `create_kl` | 🔐 需要 | 创建产品 |

---

## 📝 版本历史

### v1.1.0 (2026-03-31) - 增强验证

- ✅ **新增 Open Key 提示** - 清晰的 https://fore.vip 获取指引
- ✅ **URL 现在是必填项** - 必须提供有效外部链接
- ✅ **内容最少 50 字符** - 确保详细描述
- ✅ **更好的错误信息** - 清晰的验证反馈

### v1.0.0 (2026-03-30) - 初始版本

- ✅ 从 `product` 技能拆分
- ✅ 专注单个产品创建
- ✅ 强制查重
- ✅ 内容仅来自外部来源

---

**版本**: 1.1.0 | **更新**: 2026-03-31
