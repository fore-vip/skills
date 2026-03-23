# fore-vip/skills - activity-create

**版本**: 0.0.2 (测试开发中)  
**许可证**: MIT

---

## 📦 安装

```bash
npx skills add fore-vip/skills -s activity-create
```

---

## 🚀 快速开始

### 1. 查看可用工具

```bash
curl https://api.fore.vip/mcp/tools/list
```

### 2. 创建活动

```bash
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "AI 周末聚会",
      "start_time": 1711094400000,
      "end_time": 1711108800000,
      "address": "北京三里屯",
      "range": 0,
      "pay": false
    }
  }'
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](activity-create/SKILL.md) | 英文技能文档 |
| [SKILL_cn.md](activity-create/SKILL_cn.md) | 中文技能文档 |
| [TEST_CONVERSATION.md](activity-create/TEST_CONVERSATION.md) | 模拟对话测试 |

---

## 🧪 测试状态

✅ **全部通过** (7/7)

| 类别 | 通过 | 总计 |
|------|------|------|
| 基础功能 | ✅ 3 | 3 |
| 错误处理 | ✅ 3 | 3 |
| 边界测试 | ✅ 1 | 1 |

---

## 🔧 MCP 端点

**Base URL**: `https://api.fore.vip/mcp`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/tools/list` | GET | 获取工具列表 |

---

## 📝 示例对话

### 用户
我想创建一个周末 AI 体验活动

### Agent
好的！我来帮你创建这个 AI 体验活动。请问：

1. **活动什么时候开始？** (日期和具体时间)
2. **预计持续多久？** (结束时间)
3. **活动地点在哪里？** (可选)
4. **是否收取门票？** (可选)

---

## 🎯 待办事项

### 测试环境 ✅
- [x] MCP 云函数实现
- [x] 基础功能测试
- [x] 错误处理测试
- [x] 文档编写

### 生产环境 🔲
- [ ] 用户认证 (token 验证)
- [ ] 移除硬编码数据
- [ ] 权限控制
- [ ] 日志记录
- [ ] 并发测试

---

## 📚 相关资源

- **MCP 规范**: https://modelcontextprotocol.io/
- **uniCloud 文档**: https://doc.dcloud.net.cn/uniCloud/
- **skills.sh**: https://skills.sh

---

**官网**: https://fore.vip  
**文档**: https://doc.fore.vip
