# MCP Skills 文档索引

**项目**: AI 飞花令 (fore.vip)  
**最后更新**: 2026-03-20  
**版本**: 0.0.3

---

## 📋 文档清单

| 文档 | 路径 | 说明 |
|------|------|------|
| **README.md** | `./README.md` | 英文项目说明 |
| **README_cn.md** | `./README_cn.md` | 中文项目说明 |
| **SKILL.md** | `./activity-create/SKILL.md` | activity-create 技能文档 (英文) |
| **SKILL_cn.md** | `./activity-create/SKILL_cn.md` | activity-create 技能文档 (中文) |
| **SKILL_TEMPLATE.md** | `./SKILL_TEMPLATE.md` | SKILL.md 标准模板 |
| **PUBLISH_GUIDE.md** | `./PUBLISH_GUIDE.md` | 技能发布指南 |
| **DOCUMENTATION.md** | `./DOCUMENTATION.md` | 本文档索引 |

---

## 🏗️ 项目结构

```
/Users/codes/git/ai/skills/
├── README.md                    # 英文项目说明
├── README_cn.md                 # 中文项目说明
├── DOCUMENTATION.md             # 文档索引 (本文件)
├── LICENSE                      # MIT License
├── SKILL_TEMPLATE.md            # SKILL.md 标准模板
├── PUBLISH_GUIDE.md             # 发布指南
└── activity-create/             # activity-create 技能
    ├── SKILL.md                 # 英文版技能文档
    ├── SKILL_cn.md              # 中文版技能文档
    ├── TEST_CONVERSATION.md     # 测试对话示例
    └── test_local.sh            # 本地测试脚本

/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/mcp/
├── index.obj.js                 # MCP Server 实现
└── package.json                 # 依赖配置
```

---

## 🧩 可用技能

### activity-create (v0.0.3)

**MCP 工具**: `create_activity`  
**端点**: `https://api.fore.vip/mcp/tools/call`

#### 必需参数 (4 个)

| 参数 | 类型 | 说明 |
|------|------|------|
| `content` | string | 活动介绍 (≥2 字符) |
| `start_time` | number | 开始时间戳 (毫秒) |
| `address` | string | 活动地址 |
| `wx` | string | 联系方式 (微信) |

#### 可选参数 (6 个)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `kid` | string | 硬编码 | 关联机器人 ID |
| `end_time` | number | - | 结束时间戳 |
| `location` | object | - | GeoJSON 坐标 |
| `range` | number | 0 | 门票金额 (分) |
| `pay` | boolean | false | 是否付费 |
| `url` | string | - | 外部链接 |

#### 快速测试

```bash
curl -X POST https://api.fore.vip/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_activity",
    "arguments": {
      "content": "AI 周末聚会",
      "start_time": 1711094400000,
      "address": "北京三里屯",
      "wx": "forevip123",
      "range": 0,
      "pay": false
    }
  }'
```

---

## 🔧 MCP 云对象

### 位置

```
/Users/codes/git/ai/fore/uniCloud-aliyun/cloudfunctions/mcp/
```

### 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/mcp/tools/list` | GET | 获取工具列表 |
| `/mcp/tools/call` | POST | 调用工具 |

### 协议

- **规范**: Model Context Protocol (MCP)
- **格式**: JSON-RPC 2.0
- **基础 URL**: `https://api.fore.vip/mcp`

---

## 📖 使用指南

### 1. 安装技能

```bash
npx skills add forevip/skills -s activity-create
```

### 2. 列出可用技能

```bash
npx skills add forevip/skills --list
```

### 3. 使用技能

通过支持 MCP 的 AI 客户端调用：

```
用户：帮我创建一个 AI 周末聚会活动
AI：好的，我需要以下信息：
    1. 活动介绍 (content)
    2. 开始时间 (start_time)
    3. 活动地址 (address)
    4. 联系方式 (wx)
```

### 4. 本地测试

```bash
cd /Users/codes/git/ai/skills/activity-create
./test_local.sh
```

---

## 🗄️ 数据库结构

### act 集合

```javascript
{
  _id: "活动 ID",
  kid: "关联机器人 ID",
  user: "创建者 ID",
  content: "活动介绍",
  start_time: 1711094400000,
  end_time: 1711108800000,
  address: "地址文本",
  location: { type: "Point", coordinates: [经度，纬度] },
  range: 0,           // 门票金额 (分)
  pay: false,         // 是否付费
  url: "",            // 外部链接
  wx: "",             // 联系方式
  type: 0,            // 活动类型
  hot: 0,             // 热度
  create_date: 1711000000000
}
```

---

## 🔗 相关链接

| 资源 | 链接 |
|------|------|
| **MCP 规范** | https://modelcontextprotocol.io/ |
| **skills.sh** | https://skills.sh |
| **AI 飞花令官网** | https://fore.vip |
| **项目文档** | https://doc.fore.vip |
| **Vercel Labs 示例** | https://github.com/vercel-labs/agent-skills |

---

## 📝 更新日志

### v0.0.3 (2026-03-20)

- ✅ 修正必需参数：`content`, `start_time`, `address`, `wx`
- ✅ 将 `kid` 标记为可选 (当前硬编码)
- ✅ 更新错误代码表
- ✅ 添加实现细节说明
- ✅ 完善 MCP 响应格式文档

### v0.0.2 (2026-03-19)

- ✅ 添加中英文技能文档
- ✅ 添加 HTTP API 示例
- ✅ 添加错误处理说明

### v0.0.1 (2026-03-18)

- ✅ 初始版本
- ✅ 实现 MCP Server 基础功能
- ✅ 创建 activity-create 技能

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**维护者**: wise · 严谨专业版  
**联系方式**: forevip123 (微信)
