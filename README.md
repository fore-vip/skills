# 火力打卡 · Skills

> 火力打卡 Agent Skills — 让 AI 帮你发现和参与户外活动。

[![skills.sh](https://skills.sh/b/fore-vip/act)](https://skills.sh/fore-vip/act)
![version](https://img.shields.io/badge/version-2.0.1-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![region](https://img.shields.io/badge/region-CN_SZ-red)
![status](https://img.shields.io/badge/status-verified-brightgreen)

## 🗺️ 项目信息

| 标签 | 值 |
|------|-----|
| **类型** | Agent Skill / MCP Tool |
| **领域** | 户外活动 · 本地生活 · O2O |
| **区域** | 深圳 🇨🇳（geoNear 空间搜索） |
| **协议** | MCP (HTTP POST JSON) |
| **后端** | uniCloud + MongoDB |

## 📦 Skills

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

**MCP 端点：** `https://mcp.fore.vip`

## 🚀 安装

### 命令行

```bash
npx skills add fore-vip/act
```

### OpenClaw（龙虾）

在聊天中说：

> 安装 act 技能

### 安装后使用

- 🗣️「附近的爬山活动」
- 🗣️「深圳有什么文化类的活动」
- 🗣️「这个活动详情是什么」

Agent 自动调用 `https://mcp.fore.vip/act/search` 和 `/act/detail`。

## 🌐 GEO 覆盖

| 属性 | 值 |
|------|-----|
| 区域 | 深圳 |
| 坐标基准 | 114.058°E, 22.543°N（深圳市民中心） |
| 覆盖范围 | 深圳市全域及周边（~80km） |
| 空间索引 | MongoDB 2dsphere + geoNear |

## 📁 仓库结构

```
skills/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
├── package.json
└── act/
    ├── SKILL.md       ← Agent 说明书（AI 读取）
    ├── README.md       ← 开发文档（人读）
    └── mcp.json        ← MCP 工具声明
```

MCP 实现代码在 base 仓库 `uni_modules/act/`。

## 许可

MIT · Copyright © 2026 fore.vip
