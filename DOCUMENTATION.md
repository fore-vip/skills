# MCP Skills 文档索引

**项目**: 前凌智选 (fore.vip)  
**最后更新**: 2026-03-24  
**版本**: 0.0.8

---

## 🔐 认证 (Authentication)

### Open Key 获取方式

1. 在 [fore.vip](https://fore.vip) 平台注册/登录
2. 进入 **用户中心** → **API 设置**
3. 生成或复制你的 **Open Key**

### Header 格式

```http
Authorization: Bearer <your_open_key>
```

或

```http
X-Open-Key: <your_open_key>
```

### 认证要求

| 工具 | 认证 | 说明 |
|------|------|------|
| `create_activity` | 🔐 需要 | 创建活动 |
| `create_kl` | 🔐 需要 | 发布产品 |
| `query_kl` | ❌ 公开 | 查询产品 |

---

## 🚀 智能发布 (Smart Publish) - v0.0.8

### ⚠️ 重要说明

**内容来源**: 外部来源（**不是**现有产品数据库）

**原因**: 避免循环依赖（不能先查询产品再发布同样的产品）

### 内容来源

| 来源 | 说明 | 适用场景 |
|------|------|----------|
| **AI 生成** | AI 根据标签创作内容 | 通用产品发布 |
| **搜索引擎** | Google/Bing 搜索结果 | 分享真实产品 |
| **会话上下文** | 用户对话中提到的内容 | 用户描述的产品 |
| **GitHub** | 热门开源项目 | 技术类分享 |
| **Product Hunt** | 每日热门产品 | 新产品发现 |
| **其他技能** | copywriting 等技能 | 专业内容生成 |

### 工作流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 用户请求发布产品                                      │
│     用户："发布一个 AI 工具 标签的产品"                    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  2. Agent 选择内容来源                                    │
│     - AI 生成（默认）                                     │
│     - 搜索引擎                                          │
│     - 会话上下文                                        │
│     - GitHub/Product Hunt                               │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  3. 获取/生成产品信息                                    │
│     {name, content, pic, tag, url}                      │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  4. Agent 显示预览                                        │
│     "📦 产品预览：名称、描述、标签...                    │
│      是否确认发布？(确认/取消)"                          │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  5. 用户确认                                              │
│     用户："确认"                                          │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  6. Agent 调用 create_kl 发布                              │
│     POST /mcp/create_kl                                 │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  7. 发布成功                                              │
│     ✅ 产品 ID: xxx                                       │
│     🔗 https://fore.vip/p?id=xxx                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent 实现方案

### 方案 1: AI 生成（推荐）

```javascript
async function smartPublish(tag, openKey) {
  // Step 1: AI 生成内容
  const aiPrompt = `
为标签"${tag}"生成一个产品介绍：
- 产品名称（有吸引力）
- 产品描述（50-100 字）
- 建议的图片关键词
- 外部链接（如有）
  `;
  
  const aiResponse = await callLLM(aiPrompt);
  const product = parseAIResponse(aiResponse);
  
  // Step 2: 显示预览
  console.log(`
📦 产品预览:
- 名称：${product.name}
- 描述：${product.content}
- 标签：${tag}

是否确认发布？(确认/取消)
  `);
  
  // Step 3: 等待确认
  if (!await confirm()) return;
  
  // Step 4: 发布
  return await create_kl(product, openKey);
}
```

### 方案 2: 搜索引擎

```javascript
async function publishFromSearch(topic, openKey) {
  // Step 1: 搜索
  const results = await search(`best ${topic} tools 2026`);
  
  // Step 2: 提取信息
  const product = {
    name: results[0].title,
    content: results[0].snippet,
    url: results[0].url,
    tag: topic
  };
  
  // Step 3: 确认并发布
  // ...
}
```

### 方案 3: 会话上下文

```javascript
async function publishFromContext(history, openKey) {
  // Step 1: 分析对话
  const info = extractProductFromChat(history);
  
  // Step 2: AI 补全
  const product = await aiFill(info);
  
  // Step 3: 确认并发布
  // ...
}
```

### 方案 4: GitHub Trending

```javascript
async function publishGitHubTrending(lang, openKey) {
  // Step 1: 获取热门
  const repos = await fetch('https://api.github.com/trending');
  
  // Step 2: 格式化
  const product = {
    name: repos[0].name,
    content: repos[0].description,
    url: repos[0].html_url,
    tag: lang || '开源'
  };
  
  // Step 3: 确认并发布
  // ...
}
```

---

## 📖 用户对话示例

### 示例 1: AI 生成

```
用户：帮我发布一个"AI 工具"标签的产品

Agent: 
🤖 正在为您生成"AI 工具"相关产品内容...

📦 产品预览:
- 名称：智能写作助手 Pro
- 描述：基于最新 AI 技术的写作助手，支持多语言、风格调整、语法检查。
- 标签：AI 工具

是否确认发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
产品 ID: xxx
链接：https://fore.vip/p?id=xxx
```

### 示例 2: 搜索引擎

```
用户：发布一个"Notion 替代品"的产品

Agent:
🔍 正在搜索"Notion 替代品 2026"...

找到：Anytype
- 描述：Local-first, E2E encrypted note-taking app
- 链接：https://anytype.io

是否发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
```

### 示例 3: 会话上下文

```
用户：我想分享 Cursor，是个 AI 代码编辑器，很好用！

[... 对话继续 ...]

用户：把刚才说的 Cursor 发布到平台

Agent:
📦 根据对话内容整理:
- 名称：Cursor
- 描述：AI 代码编辑器，支持智能补全
- 标签：AI 工具
- 链接：https://cursor.sh

是否发布？(确认/取消)

用户：确认

Agent:
✅ 发布成功！
```

---

## 🧩 可用工具

### query_kl (v0.0.3)

**认证**: ❌ 公开

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `tag` | string | - | 产品标签 |
| `limit` | number | 20 | 最大结果数 |
| `skip` | number | 0 | 分页 |

### create_kl (v0.0.3)

**认证**: 🔐 需要 Open Key

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称 (≥2 字符) |
| `content` | string | 产品描述 (≥10 字符) |
| `pic` | string[] | 图片 URL |
| `tag` | string | 产品标签 |
| `hot` | number | 热度 |
| `url` | string | 外部链接 |

---

## 🔧 HTTP API 端点

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/tools/list` | GET | ❌ | 工具列表 |
| `/mcp/query_kl` | POST | ❌ | 查询产品 |
| `/mcp/create_kl` | POST | 🔐 | 发布产品 |
| `/mcp/create_activity` | POST | 🔐 | 创建活动 |

---

## 📝 更新日志

### v0.0.8 (2026-03-24)

- ✅ 修复循环依赖问题
- ✅ 内容来自外部来源（AI、搜索、GitHub 等）
- ✅ 多种发布方案
- ✅ 完善文档

### v0.0.7 (2026-03-24)

- ⚠️ 已弃用（循环依赖）

### v0.0.6 (2026-03-24)

- ✅ Open Key 认证

---

**维护者**: wise · 严谨专业版  
**微信**: forevip123
