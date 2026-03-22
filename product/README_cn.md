# 产品目录 MCP 技能

通过 MCP (Model Context Protocol) 查询和浏览前凌智选平台的产品目录。

## 版本

**v0.0.1** (2026-03-21)

## 描述

此技能使 Agent 能够查询前凌智选 (fore.vip) 平台 KL (知识/产品) 集合中的产品。支持按标签筛选、分页，并返回完整的产品元数据。

## MCP 工具

- **工具名称**: `query_kl`
- **服务器**: `fore-vip-mcp`
- **端点**: `https://api.fore.vip/mcp`

## 参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `tag` | string | 否 | - | 产品标签筛选 (如："推荐", "热门", "新品") |
| `limit` | number | 否 | 20 | 最大结果数 (1-100) |
| `skip` | number | 否 | 0 | 分页偏移量 |

## 快速开始

```bash
# 按标签查询产品
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "query_kl",
    "arguments": {
      "tag": "推荐",
      "limit": 20,
      "skip": 0
    }
  }'
```

## 测试

```bash
# 运行本地测试
./test_local.sh
```

## 文档

- [完整技能文档](SKILL.md)
- [中文文档](SKILL_cn.md)

## 相关链接

- **平台**: https://fore.vip
- **API**: https://api.fore.vip/mcp
- **MCP 规范**: https://modelcontextprotocol.io/

## 许可证

MIT
