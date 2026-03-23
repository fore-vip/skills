---
name: product
description: 查询和发布前凌智选平台的产品。支持查询产品目录和发布新产品。
version: 0.0.2
license: MIT
---

## 描述

通过 MCP Server 查询和发布前凌智选 (fore.vip) 平台的产品目录 (KL 集合)。

---

## MCP 工具

**工具名称**: `query_kl`, `create_kl`  
**服务器**: `fore-vip-mcp`  

---

## 工具列表

### query_kl - 查询产品

#### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tag` | string | - | 产品标签过滤 |
| `limit` | number | 20 | 最大返回结果数 (1-100) |
| `skip` | number | 0 | 分页跳过的结果数 |

### create_kl - 发布产品

#### 必需参数 (3 个)

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 产品名称 (≥2 字符) |
| `content` | string | 产品描述 (≥10 字符) |
| `user` | string | 创建者用户 ID |

#### 可选参数 (4 个)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pic` | string[] | [] | 图片 URL 数组 |
| `tag` | string | "推荐" | 产品标签 |
| `hot` | number | 0 | 热度分数 |
| `url` | string | "" | 外部链接 |

---

## HTTP API 端点

### 获取工具列表

```bash
curl https://api.fore.vip/tools/list
```

### 调用工具

```bash
# 查询产品
  -H "Content-Type: application/json" \
  -d '{
    "name": "query_kl",
    "arguments": {
      "tag": "推荐",
      "limit": 10,
      "skip": 0
    }
  }'

# 发布产品
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_kl",
    "arguments": {
      "name": "AI 智能助手",
      "content": "这是一款强大的 AI 智能助手产品，可以帮助您高效完成各种任务。",
      "user": "6437c73e09e2988160cb54f6",
      "pic": ["https://example.com/image.jpg"],
      "tag": "推荐",
      "hot": 0,
      "url": "https://example.com"
    }
  }'
```

---

## 响应格式

### query_kl 响应

```json
{
  "success": true,
  "total": 20,
  "limit": 20,
  "skip": 0,
  "hasMore": true,
  "data": [...]
}
```

### create_kl 响应

```json
{
  "success": true,
  "id": "kl_xxx",
  "url": "https://fore.vip/s?id=kl_xxx"
}
```

---

## 错误码

| 代码 | 错误 | 解决方案 |
|------|------|----------|
| -32602 | `Missing name` | 请求体中包含 `name` 字段 |
| -32602 | `Unknown tool: xxx` | 使用 `query_kl` 或 `create_kl` |
| -32602 | `Parameter name must be at least 2 characters` | 提供至少 2 字符的产品名称 |
| -32602 | `Parameter content must be at least 10 characters` | 提供至少 10 字符的产品描述 |
| -32602 | `Missing required parameter: user` | 在请求体中包含 `user` 字段 |
| -32000 | 业务错误 | 检查错误消息 |

---

## 注意事项

1. **架构**: tools (协议层) → mcp (业务层)
2. **标签筛选**: 查询时不提供标签将返回所有产品
3. **分页**: 使用 `skip` 和 `limit` 进行分页
4. **排序**: 查询结果按 `hot` 和 `update_date` 降序排序
5. **用户 ID**: 发布产品时必须提供有效的用户 ID

---

## 相关文件

| 文件 | 路径 |
|------|------|
| 协议层云函数 | `/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/tools/index.obj.js` |
| 业务层云函数 | `/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/mcp/index.obj.js` |
| 技能定义 | `/Users/codes/git/ai/skills/product/SKILL_cn.md` |

---

**版本**: 0.0.2  
**更新**: 2026-03-23  
**API**: https://api.fore.vip/tools  
**平台**: https://fore.vip
