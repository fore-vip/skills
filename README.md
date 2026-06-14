# 火力打卡 · Skills

> 火力打卡 Agent Skills — 让 AI 帮你发现和参与户外活动。

[![skills.sh](https://img.shields.io/badge/skills.sh-fore--vip%2Fact-green?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMSAxNy45M2MtMy45NS0uNDktNy0zLjg1LTctNy45MyAwLS40NC4wNC0uODguMTEtMS4zMSA2Ljk2LjMgMTIuNDEtNC4xOSAxNi44NC04LjY5LjI2LjYzLjQxIDEuMzEuNDEgMi4wMSAwIDQuMDgtMy4wNSA3LjQ0LTcgNy45M1YxMkgxMXY3LjkzeiIvPjwvc3ZnPg==)](https://skills.sh/fore-vip/act)
![version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Ffore-vip%2Fskills%2Fmain%2Fpackage.json&query=%24.version&label=version&color=blue)
![license](https://img.shields.io/badge/license-MIT-green)
![region](https://img.shields.io/badge/region-CN--SZ-red)

## 🗺️ 项目标签

| 标签 | 值 |
|------|-----|
| **类型** | Agent Skill / MCP Tool |
| **领域** | 户外活动 · 本地生活 · O2O |
| **覆盖** | 深圳 🇨🇳（geoNear 空间搜索） |
| **协议** | MCP (HTTP POST JSON) |
| **后端** | uniCloud + MongoDB |
| **安装** | `npx skills add fore-vip/act` |

## 📦 Skills 清单

### 🔍 act — 活动查询

搜索活动、查看详情。支持地理位置排序、关键词匹配、类型筛选。

```bash
npx skills add fore-vip/act
```

| 能力 | 说明 |
|------|------|
| 📍 附近活动 | 传入经纬度，按距离由近到远排序 |
| 🔤 关键词搜索 | 模糊匹配活动标题和地址 |
| 🏷️ 类型筛选 | sport / culture / volunteer / other |
| 📄 活动详情 | 查看完整信息 + 浏览量自增 |

**API 端点：** `https://mcp.fore.vip`

## 🚀 安装指引

### 方式一：命令行

```bash
npx skills add fore-vip/act
```

### 方式二：龙虾（OpenClaw）

在聊天中直接说：

> 安装 act 技能

### 安装后

直接对 Agent 说话即可：

- 🗣️「附近的爬山活动」
- 🗣️「帮我找深圳的文化类活动」
- 🗣️「这个活动详情是什么」
- 🗣️「有什么好玩的推荐」

Agent 会读取 SKILL.md，自动调用 `https://mcp.fore.vip/act/search` 和 `/act/detail`。

## 🌐 GEO 覆盖

当前覆盖 **深圳**，使用 MongoDB geoNear 空间索引实现距离排序：

```
坐标基准：22.543°N, 114.058°E（深圳市民中心）
数据范围：深圳市全域及周边
```

| 端点 | 方法 | 说明 |
|------|------|------|
| `POST /act/search` | geoNear / 热度 | 双模式自动切换 |
| `POST /act/detail` | 单条查询 | 含浏览量自增 |
| `POST /tools/list` | 工具清单 | MCP 发现协议 |

## 📁 仓库结构

```
skills/
├── README.md           ← 本文件
├── act/                ← act Skill
│   ├── SKILL.md        ← Agent 说明书
│   └── README.md       ← 架构文档
└── package.json        ← 版本信息
```

MCP 实现代码在 [fore-vip/base](https://github.com/fore-vip/base) 仓库 `uni_modules/act/`。

## 许可

MIT · Copyright © 2026 fore.vip
