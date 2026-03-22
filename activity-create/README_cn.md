# activity-create 技能

[![Version](https://img.shields.io/badge/version-0.0.4-blue)](https://github.com/fore-vip/skills/tree/main/activity-create)
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

通过 MCP Server 为 fore.vip 平台创建线下活动。

---

## 📋 说明

此技能使 AI 智能体能够在 fore.vip 平台上创建线下活动。它处理活动安排、地点管理和联系信息收集。

---

## 🚀 安装

```bash
# 从 GitHub 安装
npx skills add fore-vip/skills --skill activity-create

# 从本地路径安装
npx skills add /path/to/skills --skill activity-create
```

---

## 🔧 MCP Server 配置

**端点**: `https://api.fore.vip/mcp/create_activity`  
**方法**: `POST`  
**Content-Type**: `application/json`

---

## 📝 参数

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `content` | string | 活动介绍（最少 2 字符） | `"AI 周末聚会"` |
| `start_time` | number | 开始时间戳（毫秒） | `1711094400000` |
| `address` | string | 活动地址 | `"北京三里屯"` |
| `wx` | string | 联系微信号 | `"forevip123"` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `end_time` | number | - | 结束时间戳（毫秒） |
| `location` | object | - | GeoJSON 坐标 |
| `range` | number | `0` | 门票金额（分） |
| `pay` | boolean | `false` | 是否付费活动 |
| `url` | string | - | 外部链接 URL |

---

## 💡 使用示例

### 基础活动创建

```javascript
const response = await fetch('https://api.fore.vip/mcp/create_activity', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'AI 周末聚会',
    start_time: Date.now() + 86400000,
    address: '北京三里屯',
    wx: 'forevip123'
  })
});

const result = await response.json();
console.log('活动创建成功:', result.url);
```

### 完整参数示例

```javascript
const event = {
  content: '高端 AI 大会',
  start_time: 1711872000000,
  end_time: 1711958400000,
  address: '上海静安寺',
  location: {
    type: 'Point',
    coordinates: [121.44, 31.23]
  },
  wx: 'forevip123',
  range: 9900,  // ¥99
  pay: true,
  url: 'https://example.com'
};
```

---

## 📊 响应格式

### 成功

```json
{
  "success": true,
  "id": "69bf8d848a5c785fa8c566cd",
  "url": "https://fore.vip/st?id=69bf8d848a5c785fa8c566cd"
}
```

### 错误

```json
{
  "success": false,
  "error": {
    "code": "FunctionBizError",
    "message": "Parameter content must be at least 2 characters"
  }
}
```

---

## ⚠️ 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Parameter content must be at least 2 characters` | 内容太短 | 提供更详细的描述 |
| `Missing required parameter: start_time` | 缺少开始时间 | 添加 start_time 字段 |
| `Missing required parameter: address` | 缺少地址 | 添加 address 字段 |
| `Missing required parameter: wx` | 缺少联系方式 | 添加 wx 字段 |

---

## 🧪 测试

```bash
# 运行本地测试
cd activity-create
./test_local.sh
```

**测试用例**:
- ✅ 创建活动（成功场景）
- ✅ 参数验证（内容太短）
- ✅ 参数验证（缺少必需字段）

---

## 📚 相关资源

- **[MCP 规范](https://modelcontextprotocol.io/)** - 协议文档
- **[skills.sh](https://skills.sh/)** - 技能目录
- **[Fore-Vip](https://fore.vip/)** - 平台官网
- **[API 文档](https://api.fore.vip/mcp)** - MCP API

---

## 📝 版本历史

### v0.0.4 (2026-03-22)
- ✅ 更新为 MCP Server 标准
- ✅ 简化 SKILL.md 格式
- ✅ 添加测试脚本
- ✅ 更新端点为 `/mcp/create_activity`

### v0.0.3 (2026-03-20)
- ✅ 初始版本

---

## 🤝 贡献

欢迎贡献！请：
1. Fork 仓库
2. 创建特性分支
3. 进行更改
4. 提交 PR

---

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件

---

**维护者**: wise  
**最后更新**: 2026-03-22
