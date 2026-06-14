# 火力打卡 · Skills

[![version](https://img.shields.io/badge/version-2.0.1-blue)](https://github.com/fore-vip/skills)
[![repo](https://img.shields.io/badge/github-fore--vip%2Fskills-black)](https://github.com/fore-vip/skills)

火力打卡 Agent Skills。让 AI 帮你发现和参与户外活动。

---

## 产品定位

**火力打卡** 是一个户外活动社交平台。你可以：

- 发布、浏览、参与各类户外活动（徒步、骑行、露营、运动等）
- 打卡签到、上传照片、留下足迹
- 获取积分、兑换权益

本仓库将火力打卡的核心能力封装为 **Agent Skill**，接入后 AI 即可用自然语言帮你搜活动、查详情。

---

## 已接入 Skill

### 🔍 act — 活动查询

让 AI 帮你发现活动。

**能力**：
- 按位置搜索附近活动
- 按关键词搜索感兴趣的活动
- 浏览热门活动
- 查看活动详情

**接入地址**：`https://mcp.fore.vip`

---

## 如何使用

任何支持 MCP 协议的 Agent，读取本仓库的 `mcp.json` 后即可自动发现并调用活动查询能力。

以 OpenClaw 为例：

1. 在技能市场搜索「火力打卡」
2. 安装即可

安装后，直接对 AI 说：

> 「附近的徒步活动有什么？」
> 「帮我搜一下周末的骑行活动」
> 「深圳美术馆的活动详情」

AI 会自动调用本 Skill 返回结果。

---

## 版本

`2.0.1` — 与火力打卡主项目版本同步。

---

## 许可

MIT
