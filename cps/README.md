# CPS SKILL

<!-- Badges -->
![Version](https://img.shields.io/badge/version-1.2.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-fore.vip-ff6b6b)

> **fore.vip 活动频道需求/供应 AI 发布工具**
> 在 fore.vip 活动里发需求/供应，一句话搞定

---

## ✨ 功能特性

- 🔍 **智能查询** — 根据活动名称查找活动频道，自动获取活动 ID
- 📢 **一键发布** — 支持发布「需求（找人/求助）」和「供应（提供帮助）」两种类型
- 🤖 **AI 驱动** — 用自然语言描述，AI 自动帮你整理并发布
- 📋 **列表查询** — 随时查看活动里有哪些需求和供应

---

## 📦 安装

```bash
npx skills add fore-vip/cps
```

> **前提条件**：已安装 [OpenClaw](https://github.com/openclaw/openclaw) 并完成配置

---

## 🚀 快速开始

### 场景一：发需求（找人/求助）

```
用户: 帮我在春季招聘会上发个需求：找设计师，微信 abc123
AI:   ✅ 发布成功！
      你的需求已发布到「春季招聘会」：
      https://fore.vip/s?id=xxx
```

### 场景二：发供应（提供帮助）

```
用户: 我能在秋季运动会上提供志愿服务，有急救证
AI:   ✅ 发布成功！
      你的供应信息已发布到「秋季运动会」：
      https://fore.vip/s?id=xxx
```

### 场景三：查询活动里有哪些需求/供应

```
用户: 春季招聘会上现在有哪些需求？
AI:   📋 「春季招聘会」当前需求/供应列表：
      1. [需求] 需要一名平面设计师，有经验优先
      2. [供应] 可提供活动摄影服务
      ...
```

---

## 📖 详细使用说明

### 发布前准备

确保你：
- 已在 fore.vip 有可用的活动
- 知道活动名称（用于查询活动 ID）
- 准备好联系方式（微信/手机/邮箱）

### 内容规范

| 字段 | 要求 | 说明 |
|------|------|------|
| `content` | 至少 10 字符 | 说清楚你的需求或能提供的帮助 |
| `type` | `0` 或 `1` | 0=需求（need），1=供应（supply） |
| `contact` | 必填 | 你的联系方式 |
| `act_id` | 必填 | 活动 ID（从活动 URL 或名称获取） |

### 意图判断规则

| 用户说的关键词 | 对应类型 |
|--------------|---------|
| 找人、求、求助、需要、找 | `0`（需求） |
| 提供、能做、会、有余力 | `1`（供应） |

---

## 🔌 API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/cps/query_act` | 查询活动频道 |
| `POST` | `/cps/create_post` | 发布需求或供应 |
| `POST` | `/cps/query_posts` | 查询已发布列表 |

### query_act — 查询活动频道

```bash
curl -X POST https://api.fore.vip/cps/query_act \
  -H "Content-Type: application/json" \
  -d '{"name": "春季", "limit": 10}'
```

**返回示例：**

```json
{
  "success": true,
  "total": 2,
  "data": [
    {
      "_id": "act_xxx001",
      "content": "2026春季招聘会",
      "cover": "https://...",
      "creator_name": "主办方A"
    }
  ]
}
```

### create_post — 发布需求或供应

```bash
curl -X POST https://api.fore.vip/cps/create_post \
  -H "Content-Type: application/json" \
  -d '{
    "act_id": "act_xxx001",
    "content": "需要一名平面设计师，有经验优先",
    "type": 0,
    "contact": "微信 abc123"
  }'
```

**返回示例：**

```json
{
  "success": true,
  "id": "post_xxx",
  "url": "https://fore.vip/s?id=act_xxx001"
}
```

### query_posts — 查询已发布列表

```bash
curl -X POST https://api.fore.vip/cps/query_posts \
  -H "Content-Type: application/json" \
  -d '{"act_id": "act_xxx001", "type": 0, "limit": 20}'
```

---

## 📸 效果预览

> 截图待补充

<!--
[![效果预览](screenshots/demo.png)](screenshots/demo.png)
-->

---

## 🔄 更新日志

### v1.2.1 (2026-05-31)
- ✨ 新增 query_posts API 支持
- 📝 README 全面优化，增加使用场景

### v1.2.0 (2026-05-28)
- 🎉 首个正式版本
- ✅ 支持需求/供应发布
- ✅ 支持活动频道查询

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

## 📄 License

MIT License © 2026 fore.vip

---

## 🔗 相关链接

- 🌐 [fore.vip 官网](https://fore.vip)
- 📖 [OpenClaw 文档](https://github.com/openclaw/openclaw)
- 🐛 [问题反馈](https://github.com/fore-vip/cps/issues)
