> **工作空间身份**：fore.vip 五大单元之一 —— 与 base 对接的 MCP 接口实现库（act/cps）。声明在此仓库，实现在 `base/uni_modules/`。全局设定见 [../README.md](../README.md)。

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

### 🧩 fore-ex — 活动发现浏览器插件（运营 / 达人工具）

> 给**运营、达人、团队成员**用的 Chrome 插件：在电脑浏览器里直接逛平台活动、找优质内容做素材、一键进活动详情，并引导发布活动获取 Open Key（用于活动创建与 CPS 分发）。

**它能帮你做什么**
- 📋 在浏览器侧边随时看平台**活动列表**（带封面、地址、标签、热度）
- 🔍 按关键词快速找目标活动
- 📱 点卡片直达**活动详情页**，方便截图、分享、做内容
- 🔑 菜单「发布活动」直达 **Open Key 管理页**，登录后即可生成 / 复制密钥，用来创建自己的活动

**适合谁用**
- 运营同学：日常巡检活动、找选题、做活动复盘
- 达人 / 队长：发现优质活动，引导粉丝参与或自行发布
- 商务 / 渠道：快速查看活动规模与分布

**怎么拿到**
- 开发者模式加载 `skills/fore-ex/` 源码目录（详见 [fore-ex/README.md](fore-ex/README.md)）
- 或等团队发布安装包后一键安装

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
├── act/
│   ├── SKILL.md       ← Agent 说明书（AI 读取）
│   ├── README.md       ← 开发文档（人读）
│   └── mcp.json        ← MCP 工具声明
└── fore-ex/
    ├── manifest.json   ← 插件配置（MV3）
    ├── popup.html       ← 弹出页（活动列表）
    ├── popup.js         ← 活动检索逻辑
    ├── styles.css       ← 样式
    └── README.md        ← 插件文档（人读）
```

- MCP 实现代码在 base 仓库 `uni_modules/act/`
- fore-ex 浏览器插件为独立前端，直连 `mcp.fore.vip`，无后端代码

## 许可

MIT · Copyright © 2026 fore.vip
