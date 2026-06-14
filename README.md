# skills

[![version](https://img.shields.io/badge/version-2.0.1-blue)](https://github.com/fore-vip/skills)
[![repo](https://img.shields.io/badge/github-fore--vip%2Fskills-black)](https://github.com/fore-vip/skills)

火力打卡 · 通用 Agent Skills。为 OpenClaw、Claude、微信 AI 等任意 Agent 提供活动搜索、详情查询的 MCP 接口定义。

---

## 产品概述

**火力打卡** 是一个基于 uni-app + uniCloud 的户外活动社交平台。用户可以：

- 发布/浏览活动（徒步、骑行、露营、运动等）
- 打卡签到、发表评论、上传图片
- 查看足迹、行程规划
- 获取贝壳积分、兑换权益

本仓库将火力打卡的**核心查询能力**封装为可被 Agent 调用的 Skill，使 AI 能够以自然语言帮助用户发现和参与活动。

---

## 已接入 Skill

### act — 活动查询

| 工具 | 端点 | 说明 |
|------|------|------|
| `search_activities` | `POST /act/search` | 搜索活动，含 GEO/关键词/类型三维召回 |
| `get_activity_detail` | `POST /act/detail` | 活动详情 + 自动热度计数 |

**服务地址**：`https://mcp.fore.vip`

详细文档见 `act/SKILL.md`，工具声明见 `act/mcp.json`。

---

## 召回策略

### GEO 三维召回

| 维度 | 条件 | 排序 | 说明 |
|------|------|------|------|
| 地理距离 | 提供 `latitude` + `longitude` | `geoNear` 由近到远 | MongoDB 2dsphere 地理空间索引 |
| 热度 | 未提供经纬度 | `view_count DESC` | 适用于浏览/发现场景 |
| 关键词 | 提供 `keyword` | 叠加前两者 | RegExp 匹配 `content` / `address` / `tags` |

**GEO 索引要求**：`activity.location` 字段为 `2dsphere` 索引（GeoJSON Point 格式）。

### 搜索边界

| 边界 | 值 | 说明 |
|------|-----|------|
| 最大返回 | 50 条/页 | `pageSize ≤ 50`，超限截断 |
| 默认返回 | 10 条/页 | 无参默认值 |
| 状态过滤 | `status=0` 且 `open≠0` | 仅返回生效中且公开的活动 |
| 无鉴权 | — | 所有查询公开，无用户态 |
| 超时 | uniCloud 默认 | 云函数 60s 上限 |

### 边界外（不在本 Skill 范围内）

| 场景 | 状态 | 替代方案 |
|------|------|----------|
| 创建/编辑活动 | 不在 Skill | 走原小程序页面 |
| 打卡签到 | 不在 Skill | 走原小程序页面 |
| 评论/上传图片 | 不在 Skill | 走原小程序页面 |
| 贝壳积分 | 不在 Skill | 后续 Skill 覆盖 |
| 用户登录/鉴权 | 不需要 | 查询公开数据，无需登录 |
| 写入操作 | 不支持 | Skill 仅提供查询 |

---

## SEO

### 数据 SEO

活动对象字段对搜索引擎/Agent 友好：

| 字段 | 类型 | 用途 |
|------|------|------|
| `content` | `string` | 活动标题，搜索关键词主匹配 |
| `address` | `string` | 可读地址，地理位置语义匹配 |
| `tags` | `string[]` | 标签数组，分类/场景匹配 |
| `type` | `enum` | 预定义类型，精确筛选 |
| `location.coordinates` | `[lng, lat]` | GeoJSON，空间查询 |

### API SEO

- 响应含 `text` 字段：为 Agent 提供可直接展示的自然语言摘要，减少 Agent 对结构化数据的二次加工
- `tools/list` 返回标准工具声明，Agent 开箱即用

---

## 目录结构

```
skills/
├── README.md           ← 本文件
├── act/
│   ├── SKILL.md        ← Skill 文档
│   └── mcp.json        ← 工具声明
```

---

## 接入指南

### OpenClaw

将本仓库安装为 Skill，Agent 自动读取 `mcp.json` 并注册工具。

### 其他 Agent

任何支持 MCP 协议的 Agent，读取 `act/mcp.json` 后按 `endpoint` + `method` 直接 HTTP 调用：

```bash
# 搜索活动
curl -s -X POST https://mcp.fore.vip/act/search \
  -H "Content-Type: application/json" \
  -d '{"keyword":"徒步","latitude":22.54,"longitude":113.93}'

# 活动详情
curl -s -X POST https://mcp.fore.vip/act/detail \
  -H "Content-Type: application/json" \
  -d '{"id":"6a0a872089bd27bae34e5502"}'

# 工具清单
curl -s -X POST https://mcp.fore.vip/tools/list \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 版本

`2.0.1` — 与火力打卡主项目版本同步。

---

## 许可

MIT
