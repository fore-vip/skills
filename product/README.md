# Product MCP Skill

Query and browse product from fore.vip platform via MCP (Model Context Protocol).

## Version

**v0.0.1** (2026-03-21)

## Description

This skill enables agents to query products from the fore.vip (前凌智选) platform's KL (Knowledge/Product) collection. Supports filtering by tag, pagination, and returns comprehensive product metadata.

## MCP Tool

- **Tool Name**: `query_kl`
- **Server**: `fore-vip-mcp`
- **Endpoint**: `https://api.fore.vip/mcp`

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tag` | string | No | - | Product tag filter (e.g., "推荐", "热门", "新品") |
| `limit` | number | No | 20 | Max results (1-100) |
| `skip` | number | No | 0 | Pagination offset |

## Quick Start

```bash
# Query products by tag
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

## Testing

```bash
# Run local tests
./test_local.sh
```

## Documentation

- [Full Skill Documentation](SKILL.md)
- [中文文档](SKILL_cn.md)

## Related

- **Platform**: https://fore.vip
- **API**: https://api.fore.vip/mcp
- **MCP Spec**: https://modelcontextprotocol.io/

## License

MIT
