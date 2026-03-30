---
name: product-create
description: 创建单个 AI 产品，自动查重。内容来自外部来源（AI、搜索、GitHub 等）。
version: 1.0.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - 产品创建
  - 单个产品
  - 重名检测
  - fore.vip
---

# 产品创建技能

在 **fore.vip** 平台创建**单个 AI 产品**，自动检测重名。

**工具**:
- `query_kl`（公开） - 检查产品名称是否存在
- `create_kl`（🔐 需 Open Key） - 创建/发布产品

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
1. 从外部来源获取产品信息：
   - AI 生成
   - 搜索引擎
   - GitHub trending
   - Product Hunt
   - 用户对话上下文
   ↓
2. 🔍 检查名称是否已存在（用 name 参数调用 query_kl）
   ↓
3. 如已存在 → 跳过，返回已有产品
   ↓
4. 如不存在 → 显示预览供确认
   ↓
5. 用户确认
   ↓
6. 调用 create_kl
   ↓
✅ 发布成功！
```

### ⚠️ 重要规则

1. **内容必须来自外部来源**（AI、搜索、GitHub 等）
2. **禁止用 query_kl 获取内容**（循环依赖）
3. **创建前必须查重**
4. **发布前必须获得用户确认**

---

## 🌐 MCP 接口

### query_kl（公开）

**URL**: `https://api.fore.vip/mcp/query_kl`  
**Method**: `POST`  
**认证**: ❌ 公开

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | string | - | **产品名称（模糊匹配，不区分大小写）** |
| `limit` | number | 1 | 最大返回数量（查重用 1） |

#### 示例

```bash
# 检查产品名称是否存在
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"name":"Cursor","limit":1}'
```

---

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

## 🤖 实现示例

### 示例一：AI 生成

```javascript
async function createProduct(tag, openKey) {
  // 步骤 1：用 AI 生成内容
  const aiPrompt = `根据标签 "${tag}" 生成产品`;
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // 步骤 2：🔍 查重
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return {
      skipped: true,
      reason: '产品名称已存在',
      existing: existing.data[0]
    };
  }
  
  // 步骤 3：确认 & 发布
  // 步骤 4：调用 create_kl
  return await create_kl(product, openKey);
}
```

### 示例二：从搜索

```javascript
async function createFromSearch(topic, openKey) {
  // 步骤 1：搜索网络
  const results = await searchEngine(`best ${topic} tools 2026`);
  const product = {
    name: results[0].title,
    content: results[0].snippet,
    url: results[0].url,
    tag: topic
  };
  
  // 步骤 2：🔍 查重
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 3：确认 & 发布
  return await create_kl(product, openKey);
}
```

### 示例三：从 GitHub Trending

```javascript
async function createGitHubTrending(openKey) {
  // 步骤 1：获取 GitHub trending
  const repos = await fetch('https://api.github.com/trending');
  const topRepo = repos[0];
  
  const product = {
    name: topRepo.name,
    content: topRepo.description,
    url: topRepo.html_url,
    tag: '开源'
  };
  
  // 步骤 2：🔍 查重
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 3：确认 & 发布
  return await create_kl(product, openKey);
}
```

---

## 📝 输出格式

**保持输出简洁：**

```
✅ 发布成功！
ID: xxx
链接：https://fore.vip/p?id=xxx
```

**如果重名：**

```
⚠️ 产品名称已存在，跳过创建
现有产品：xxx
链接：https://fore.vip/p?id=xxx
```

---

## 📊 认证权限总览

| 工具 | 认证 | 说明 |
|------|------|------|
| `query_kl` | ❌ 公开 | 检查重名（仅 name） |
| `create_kl` | 🔐 必填 | 创建产品 |

---

## 📝 版本历史

### v1.0.0 (2026-03-30) - 初始版本

- ✅ 从 `product` 技能拆分
- ✅ 专注于单个产品创建
- ✅ 强制重名检测
- ✅ 内容仅来自外部来源

---

**版本**: 1.0.0 | **更新**: 2026-03-30
