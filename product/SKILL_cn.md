---
name: product
description: 查询/创建 AI 产品。智能发布，支持从外部来源自动生成内容。
version: 0.1.0
license: MIT
keywords:
  - AI Agents
  - MCP Server
  - OpenClaw
  - 产品目录
  - 智能发布
  - AI 生成
  - fore.vip
---

# 产品技能（Product Skill）

在 **fore.vip** 平台上查询和创建 **AI 产品**。

**工具**:
- `query_kl`（公开） - 按标签或名称查询产品
- `create_kl`（🔐 需 Open Key） - 创建/发布产品
- `smart_publish_kl`（🔐 需 Open Key） - **AI 智能补全发布**

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

## 🚀 智能发布（v0.0.9）

**⚠️ 重要**：内容来自**外部来源**，而非已有产品（避免循环依赖）。

### 内容来源

| 来源 | 说明 | 示例 |
|------|------|------|
| **AI 生成** | 根据标签自动生成内容 | "推荐" → AI 创建产品 |
| **搜索引擎** | 搜索热门工具/产品 | 搜索 "AI tools 2026" |
| **对话上下文** | 用户之前提到的产品 | 聊天中描述的产品 |
| **GitHub** | 热门开源项目 | GitHub trending |
| **Product Hunt** | 每日热门产品 | ph.com trending |
| **其他技能** | 文案生成等 | 生成描述文案 |

### 工作流程

```
用户："发布一个"AI 工具"标签的产品"
   ↓
1. Agent 向用户询问详情，或
2. Agent 搜索外部来源：
   - 搜索引擎（Google/Bing）
   - GitHub trending
   - Product Hunt
   - AI 生成
   ↓
3. Agent 整理产品信息：
   - name, content, pic, tag, url
   ↓
4. 🔍 检查名称是否已存在（用 name 参数调用 query_kl）
   ↓
5. 如已存在 → 跳过创建，返回已有产品
   ↓
6. 如不存在 → 显示预览供确认
   ↓
7. 用户确认
   ↓
8. 调用 create_kl 提交数据
   ↓
✅ 发布成功！
```

### ⚠️ 重名检测逻辑

**创建产品前，必须检查名称是否已存在：**

```javascript
async function smartPublish(tag, openKey) {
  // 步骤 1：用 AI 生成产品内容
  const aiPrompt = `根据标签 "${tag}" 生成产品描述`;
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // 步骤 2：🔍 检查名称是否已存在
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    // 名称已存在，跳过创建
    return {
      skipped: true,
      reason: '产品名称已存在',
      existing: existing.data[0]
    };
  }
  
  // 步骤 3：显示预览 & 确认
  // 步骤 4：发布
  return await create_kl(product, openKey);
}
```

---

## 🌐 MCP 接口

### query_kl（公开）

**URL**: `https://api.fore.vip/mcp/query_kl`  
**Method**: `POST`  
**认证**: ❌ 公开

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tag` | string | - | 产品标签 |
| `name` | string | - | **产品名称（模糊匹配，不区分大小写）** |
| `limit` | number | 20 | 最大返回数量（1-100） |
| `skip` | number | 0 | 分页偏移 |

#### 示例

```bash
# 按标签查询
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"tag":"推荐","limit":10}'

# 按名称查询（模糊匹配）
curl -X POST https://api.fore.vip/mcp/query_kl \
  -H "Content-Type: application/json" \
  -d '{"name":"Cursor","limit":5}'
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

## 🤖 智能发布实现

### 方式一：AI 生成（推荐）

**适用场景**：用户提供标签，AI 自动生成内容

```javascript
async function smartPublish(tag, openKey) {
  // 步骤 1：用 AI 生成产品内容
  const aiPrompt = `
根据标签 "${tag}" 生成产品描述：
- 产品名称（创意、吸引人）
- 产品描述（50-100 字，有吸引力）
- 建议的图片关键词
- 外部链接（如有）
  `;
  
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // 步骤 2：🔍 检查名称是否已存在
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return {
      skipped: true,
      reason: '产品名称已存在',
      existing: existing.data[0]
    };
  }
  
  // 步骤 3：显示预览
  console.log(`
📦 产品预览:
- 名称：${product.name}
- 描述：${product.content}
- 标签：${tag}
- 图片来源：AI 生成建议

是否确认发布？(确认/取消)
  `);
  
  // 步骤 4：等待确认
  if (!await confirm()) return;
  
  // 步骤 5：发布
  return await create_kl(product, openKey);
}
```

### 方式二：搜索引擎

**适用场景**：从网络查找真实产品/工具

```javascript
async function publishFromSearch(topic, openKey) {
  // 步骤 1：搜索网络
  const searchQuery = `best ${topic} tools 2026`;
  const results = await searchEngine(searchQuery);
  
  // 步骤 2：提取首个结果
  const topResult = results[0];
  const product = {
    name: topResult.title,
    content: topResult.snippet,
    url: topResult.url,
    tag: topic
  };
  
  // 步骤 3：🔍 检查名称是否已存在
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 4：确认 & 发布
  // ...
}
```

### 方式三：对话上下文

**适用场景**：用户在对话中已提到某产品

```javascript
async function publishFromContext(sessionHistory, openKey) {
  // 步骤 1：分析对话内容
  const productInfo = extractProductFromChat(sessionHistory);
  
  // 步骤 2：用 AI 补全缺失字段
  const completeProduct = await aiFill(productInfo);
  
  // 步骤 3：🔍 检查名称是否已存在
  const existing = await query_kl({ name: completeProduct.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 4：确认 & 发布
  // ...
}
```

### 方式四：GitHub Trending

**适用场景**：分享热门开源项目

```javascript
async function publishGitHubTrending(language, openKey) {
  // 步骤 1：获取 GitHub trending
  const repos = await fetch('https://api.github.com/trending');
  const topRepo = repos[0];
  
  // 步骤 2：格式化为产品
  const product = {
    name: topRepo.name,
    content: topRepo.description,
    url: topRepo.html_url,
    tag: language || '开源'
  };
  
  // 步骤 3：🔍 检查名称是否已存在
  const existing = await query_kl({ name: product.name, limit: 1 });
  
  if (existing.data && existing.data.length > 0) {
    return { skipped: true, existing: existing.data[0] };
  }
  
  // 步骤 4：确认 & 发布
  // ...
}
```

---

## 📝 用户对话示例

### 示例一：AI 生成

```
用户：帮我发布一个"AI 工具"标签的产品

Agent: 
🤖 正在为您生成"AI 工具"相关产品内容...

📦 产品预览:
- 名称：智能写作助手 Pro
- 描述：基于最新 AI 技术的写作助手，支持多语言、风格调整、语法检查，让您的写作更高效。
- 标签：AI 工具
- 图片来源：建议使用 AI 生成工具图标

是否确认发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
产品 ID: xxx
链接：https://fore.vip/p?id=xxx
```

### 示例二：从搜索

```
用户：发布一个关于"Notion 替代品"的产品

Agent:
🔍 正在搜索"Notion 替代品 2026"...

找到热门产品：Anytype
- 描述：Local-first, E2E encrypted note-taking app
- 链接：https://anytype.io
- 来源：Product Hunt #1 today

是否发布此产品？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
```

### 示例三：从对话上下文

```
用户：我想分享一个很棒的 AI 工具，叫 Cursor，是一个 AI 代码编辑器

[... 对话继续 ...]

用户：把刚才说的 Cursor 发布到平台上

Agent:
📦 根据对话内容整理:
- 名称：Cursor
- 描述：AI 代码编辑器，支持智能补全、代码生成
- 标签：AI 工具
- 链接：https://cursor.sh

是否发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
```

### 示例四：重名检测

```
用户：发布一个名为"智能写作助手"的产品

Agent:
🔍 检查产品名称...
⚠️ 发现同名产品已存在：
- 名称：智能写作助手
- 描述：AI 驱动的写作工具
- 链接：https://fore.vip/p?id=xxx

跳过创建，使用现有产品。
```

---

## ⚠️ 重要注意事项

1. **禁止循环依赖**：内容来自外部来源，不能用 query_kl 查询结果作为内容
2. **用户确认**：发布前必须让用户确认
3. **数据准确性**：核实外部来源的信息
4. **版权尊重**：尊重原始内容归属
5. **🔍 重名检测**：创建前必须检查产品名称是否已存在

---

## 📊 认证权限总览

| 工具 | 认证 | 说明 |
|------|------|------|
| `query_kl` | ❌ 公开 | 按标签或名称查询产品 |
| `create_kl` | 🔐 必填 | 创建产品 |
| `smart_publish_kl` | 🔐 必填 | AI 智能发布 |

---

## 📢 输出规范

**保持输出简洁聚焦：**

- ✅ 只显示最终结果（成功/失败）
- ✅ 无错误时跳过中间步骤
- ✅ 成功消息格式简洁
- ✅ 只包含必要信息（ID、链接）

**示例：**

```
✅ 发布成功！
ID: xxx
链接：https://fore.vip/p?id=xxx
```

---

## 📝 版本历史

### v0.0.9 (2026-03-24) - 重名检测 + 精简输出

- ✅ 新增 `name` 参数到 `query_kl`（模糊匹配）
- ✅ **创建前强制重名检测**
- ✅ 更新智能发布流程，加入名称校验
- ✅ 新增输出规范（精简、聚焦）
- ✅ 更新文档示例

### v0.0.8 (2026-03-24) - 智能发布（外部来源）

- ✅ 修复循环依赖问题
- ✅ 内容来自外部来源（AI、搜索、上下文、GitHub）
- ✅ 新增多种发布方式
- ✅ 更新文档

### v0.0.7 (2026-03-24) - 自动发布

- ⚠️ 已废弃：使用 query_kl 获取内容（循环依赖）

### v0.0.6 (2026-03-24) - Open Key 认证

- ✅ 新增 Open Key 认证

---

**版本**: 0.0.9 | **更新**: 2026-03-24
