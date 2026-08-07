> **工作空间身份**：fore.vip 五大单元之一 —— 前凌智选 Chrome 插件前端，调用 `mcp.fore.vip`（base 线上 MCP 后端）。全局设定见 [../README.md](../README.md)。

# 前凌智选 Chrome 插件（fore-ex）

[![版本](https://img.shields.io/badge/版本-v2.0-orange)](https://f.fore.vip/download/fore-ex-v2.0.zip)
[![下载](https://img.shields.io/badge/下载-静态网站-blue)](https://f.fore.vip/download/fore-ex-v2.0.zip)
[![官网](https://img.shields.io/badge/官网-fore.vip-green)](https://fore.vip)
[![GitHub](https://img.shields.io/badge/GitHub-fore--vip/fore--ex-black?logo=github)](https://github.com/fore-vip/fore-ex)

**前凌智选** Chrome 浏览器插件 —— 在浏览器里**浏览户外活动、发现优质内容**，一键跳转到活动详情页，并直达 Open Key 管理页获取 API 密钥。

---

## 📦 下载安装

### 国内用户（推荐）

从静态网站下载最新版本：

- **下载链接**: https://f.fore.vip/download/fore-ex-v2.0.zip
- **文件大小**: 约 90KB
- **更新时间**: 2026-08-07

[👉 点击下载 v2.0](https://f.fore.vip/download/fore-ex-v2.0.zip)

> 若下载链接暂未更新，可直接用「开发者模式」加载 `skills/fore-ex/` 源码目录（见下方安装教程），无需等待发布包。

### 国际用户

从 GitHub 仓库获取源码：

- **仓库地址**: https://github.com/fore-vip/fore-ex

---

## 📚 相关文档

### MCP 技能文档

- **act 技能（Agent 用）**: https://github.com/fore-vip/skills/tree/main/act
- **技能安装指引**: [INSTALL.md](https://github.com/fore-vip/skills/blob/main/act/INSTALL.md)

### 项目文档

- **前凌智选官网**: https://fore.vip
- **项目文档库**: https://doc.fore.vip

---

## 🚀 安装教程

### 方式一：开发者模式安装（推荐）

> ⏱️ 预计耗时：2 分钟

#### 第 1 步：下载并解压

1. 下载插件包：[fore-ex-v2.0.zip](https://f.fore.vip/download/fore-ex-v2.0.zip)
2. 解压到任意目录，例如：
   - macOS: `/Users/你的用户名/fore-ex`
   - Windows: `C:\Users\你的用户名\fore-ex`

#### 第 2 步：打开扩展管理页面

**方法 A: 地址栏访问**
```
chrome://extensions/
```

**方法 B: 菜单访问**
1. 点击 Chrome 右上角「⋮」菜单
2. 选择「更多工具」
3. 选择「扩展程序」

#### 第 3 步：开启开发者模式

在扩展管理页面右上角，找到「开发者模式」开关，将其打开（变为蓝色）。

#### 第 4 步：加载插件

1. 点击左上角「加载已解压的扩展程序」按钮
2. 在弹出的文件选择器中，找到并选择你解压后的 `fore-ex` 文件夹（含 `manifest.json`）
3. 点击「选择」或「打开」

#### 第 5 步：验证安装

- ✅ 插件出现在扩展列表中
- ✅ 插件图标出现在浏览器右上角工具栏
- ✅ 插件状态显示为「已启用」

#### 第 6 步：固定到工具栏（可选）

如果图标未显示：
1. 点击 Chrome 右上角「🧩」扩展图标
2. 找到「前凌智选」
3. 点击右侧的「📌」图钉图标，固定到工具栏

---

### 方式二：Git 克隆安装（开发者）

适合需要修改源码的开发者：

```bash
# 1. 克隆仓库
git clone git@github.com:fore-vip/fore-ex.git
cd fore-ex

# 2. 打开 Chrome 扩展管理页面
# chrome://extensions/

# 3. 开启开发者模式

# 4. 点击「加载已解压的扩展程序」
# 5. 选择 fore-ex 项目根目录
```

---

### 方式三：拖拽安装（.crx 文件）

> ⚠️ 注意：Chrome 新版可能限制此方式

如果有 `.crx` 文件：

1. 访问 `chrome://extensions/`
2. 开启「开发者模式」
3. 将 `.crx` 文件拖拽到页面任意位置
4. 在弹出的确认对话框中点击「添加扩展程序」

---

## 📖 功能特性

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🔍 活动搜索 | 搜索活动，支持关键词匹配 |
| 📋 活动列表 | 展示封面、内容、地址、标签、浏览/参与数 |
| 🖼️ 封面展示 | 卡片顶部显示活动封面（图片加载失败自动隐藏） |
| 📱 点击跳转 | 点击卡片直达活动详情页 `fore.vip/pages/activity/detail?id={_id}` |
| 📄 无限加载 | 滚动自动加载更多活动（分页 `page*pageSize < total`） |
| 🔑 Open Key | 菜单「发布活动」跳转到 Open Key 管理页，生成 / 复制 API 密钥 |

### 🎨 界面优化（v2.0）

- ✅ 活动卡片样式（简洁大气，圆角 16px，阴影 + hover）
- ✅ 封面图置顶显示（`object-fit:cover`，加载失败自动隐藏）
- ✅ 标签胶囊形 + 渐变
- ✅ 搜索框 + 发布菜单精致布局
- ✅ Logo 与标题同行，可点击跳转官网
- ✅ 响应式布局，适配不同屏幕

---

## 📋 使用指南

### 活动浏览流程

```
1. 点击浏览器右上角的前凌智选插件图标
        ↓
2. 在搜索框输入关键词（可选）
        ↓
3. 自动加载活动列表（封面 + 内容 + 地址 + 标签）
        ↓
4. 浏览活动信息：
   - 封面图（如有）
   - 活动内容
   - 活动地址
   - 标签分类
   - 浏览数 / 参与数
        ↓
5. 点击卡片 → 跳转到活动详情页
        ↓
6. 向下滚动 → 自动加载更多活动
```

### 功能说明

| 操作 | 说明 |
|------|------|
| 搜索框输入 | 输入关键词搜索特定活动 |
| 点击搜索按钮 | 执行搜索，刷新列表 |
| 按 Enter 键 | 快速执行搜索 |
| 点击活动卡片 | 打开活动详情页 `fore.vip/pages/activity/detail?id=` |
| 滚动到底部 | 自动加载更多活动 |
| 点击「⋯」菜单 | 打开下拉菜单 |
| 发布活动 | 跳转到 Open Key 管理页 `fore.vip/web/key` |
| 关于 | 查看插件信息 |

### 如何发布活动？

插件本身**不创建活动**（纯浏览器扩展无法走 uni-id 登录态生成 Key）。发布流程：

1. 点击插件菜单「发布活动」→ 打开 `https://fore.vip/web/key`
2. 在 web 端登录后**生成 / 复制 Open Key**（`ai-key._id`）
3. 用 Open Key（作为 `X-API-Key`）在 web 端或 `act` Agent Skill 调用 `POST /act/create` 创建活动

> 后续版本可扩展：插件内粘贴 Open Key + 内嵌创建表单，直接调 `act/create`。

### 📌 运营场景

| 你的角色 | 怎么用 fore-ex |
|----------|----------------|
| 运营 / 内容 | 日常巡检平台活动：看封面和地址找选题、截图做周报、点详情页复制链接发群里 |
| 达人 / 队长 | 发现优质活动 → 分享给粉丝参与；或自己发布活动拿 Open Key 做 CPS 分发 |
| 商务 / 渠道 | 快速查看活动规模（浏览 / 参与数）与城市分布，评估合作价值 |

**典型一天**
1. 打开插件 → 浏览今日活动列表
2. 搜关键词（如「徒步」「市集」）锁定目标活动
3. 点卡片进详情页 → 截图 / 复制链接，用于内容或汇报
4. 想自己发活动 → 菜单「发布活动」→ 去 Open Key 管理页生成密钥 → 创建活动

---

## 🔧 开发者参考（普通用户可跳过）

> 以下内容为技术实现细节，供开发维护人员阅读；运营 / 普通用户无需了解。

### 技术栈

| 技术 | 说明 |
|------|------|
| **Manifest V3** | Chrome 插件最新规范 |
| **HTML5 + CSS3** | 现代化界面 |
| **Vanilla JavaScript** | 轻量级，无框架依赖 |
| **MCP 协议** | 与 `mcp.fore.vip` 通信（HTTP POST JSON） |

### 项目结构

```
fore-ex/
├── manifest.json      # 插件配置（MV3）
├── popup.html         # 弹出页 HTML（活动列表）
├── popup.js           # 活动检索逻辑
├── styles.css         # 样式
├── icon.png           # 插件图标
├── README.md          # 项目说明
└── README_en.md       # 英文说明
# 历史调试页（已弃用）：index.html / test.html / check.html / popup.html.bak / icon2.png
```

### API 端点

| 端点 | 说明 |
|------|------|
| `https://mcp.fore.vip/act/search` | 活动列表（**免鉴权**，POST `keyword`/`page`/`pageSize`） |
| `https://fore.vip/pages/activity/detail?id={id}` | 活动详情页（点击卡片跳转） |
| `https://fore.vip/web/key` | Open Key 管理页（生成 / 复制 API 密钥） |

### 权限说明

| 权限 | 用途 |
|------|------|
| `storage` | 存储用户配置（可选功能） |
| `host_permissions: mcp.fore.vip` | 调用 `act/search` 读取活动列表 |
| `host_permissions: fore.vip` | 跳转活动详情页 / Open Key 管理页 |
| `host_permissions: api.fore.vip` | 兼容旧端点（保留） |

> **CORS 说明**：`mcp.fore.vip/act/search` 不返回 `access-control-allow-origin`，但 MV3 扩展页对已声明的 `host_permissions` 主机**豁免 CORS**，插件可直接 `fetch`，无需改造后端。

---

## 🔄 版本历史

### v2.0 (2026-08-07)

**重构：对接当前 MCP（mcp.fore.vip）**
- ✅ 移除产品列表，插件聚焦活动：popup 默认显示活动列表（`act/search` 免鉴权）
- ✅ 活动卡片显示封面图（有封面则显示，加载失败自动隐藏）
- ✅ 活动卡片点击跳活动详情页（`fore.vip/pages/activity/detail?id=`）
- ✅ 菜单「发布活动」跳转 Open Key 管理页（`fore.vip/web/key`），生成 / 复制 API 密钥
- ✅ 移除「发布产品」菜单
- ✅ 搜索框改为搜活动，移除旧端点 `api.fore.vip/mcp/query_kl`
- ✅ 删除废弃 `activity.html`（创建表单），清理 styles 死代码与 CSS 语法错误
- ✅ `manifest.json` 版本升 2.0，`host_permissions` 增加 `mcp.fore.vip` / `fore.vip`

### v1.4 (2026-03-27)

**功能调整**
- ✅ 发布活动功能调整为弹出提示引导
- ✅ 引导用户先发布产品再创建活动

**界面优化**
- ✅ 产品卡片样式全面升级（简洁大气）
- ✅ 卡片圆角 12px → 16px
- ✅ 卡片阴影优化，hover 效果增强
- ✅ 标签样式优化（胶囊形 + 渐变）
- ✅ 产品详情页跳转链接更新

**修复**
- ✅ 修复 JavaScript 语法错误（alert 换行问题）

### v1.1 (2026-03-21)

**优化**
- ✅ Logo 与标题同行显示
- ✅ 删除标题 emoji，界面更简洁
- ✅ Logo 和标题可点击跳转官网
- ✅ 移除外部链接字段，简化表单
- ✅ 优化表单布局，提升用户体验
- ✅ 完善 README 文档

**修复**
- ✅ 修复表单提交后 url 字段处理

### v1.0 (2025-12-25)

**首发版本**
- ✅ 基础活动创建功能
- ✅ MCP 协议集成
- ✅ 表单验证
- ✅ 自动跳转

---

## ❓ 常见问题

### Q: 插件无法加载？

**A**: 请确保：
1. ✅ 已解压 ZIP 文件，**不要直接从压缩包加载**
2. ✅ 选择的是包含 `manifest.json` 的文件夹
3. ✅ 已开启「开发者模式」开关
4. ✅ 文件夹路径不包含中文或特殊字符

### Q: 活动列表打不开 / 空白？

**A**: 检查以下几点：
1. ✅ 网络连接是否正常
2. ✅ 是否能访问 `https://mcp.fore.vip`（act/search 免鉴权）
3. ✅ 插件已重新加载（改过源码后需在 `chrome://extensions/` 点刷新）
4. ✅ `manifest.json` 的 `host_permissions` 含 `mcp.fore.vip`

### Q: 如何在插件里发布活动？

**A**: 插件当前不直接创建活动。点击菜单「发布活动」→ 打开 `https://fore.vip/web/key` → 登录后生成 / 复制 Open Key → 在 web 端或 `act` Agent Skill 用 Key 调用 `POST /act/create`。

### Q: 如何更新插件？

**A**:
1. 下载最新版本的 ZIP 包
2. 解压覆盖原目录
3. 在 `chrome://extensions/` 找到插件
4. 点击插件卡片上的「刷新」按钮 🔄

### Q: 数据是否安全？

**A**:
- ✅ 插件仅读取活动列表所需的最少信息
- ✅ 所有数据传输使用 HTTPS 加密
- ✅ 不存储任何用户隐私数据
- ✅ 不开启任何第三方统计或追踪

### Q: 卸载插件？

**A**:
1. 访问 `chrome://extensions/`
2. 找到「前凌智选」插件
3. 点击「移除」按钮
4. 在确认对话框中点击「移除」

---

## 📞 技术支持

| 渠道 | 链接 |
|------|------|
| **官网** | https://fore.vip |
| **MCP 服务** | https://mcp.fore.vip |
| **项目文档** | https://doc.fore.vip |
| **GitHub** | https://github.com/fore-vip/fore-ex |
| **问题反馈** | https://github.com/fore-vip/fore-ex/issues |

---

## 📄 许可证

MIT License

Copyright (c) 2026 前凌智选

---

**在浏览器里发现精彩活动！** 🎉

最后更新：2026-08-07
