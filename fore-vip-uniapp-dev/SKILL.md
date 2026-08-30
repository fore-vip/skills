---
name: fore-vip-uniapp-dev
display_name: uni-app 开发助手
display_name_en: uni-app Development Workflow
description: uni-app 项目开发任务助手（fore.vip）。用户提供开发任务后，先把项目作用域（框架/样式框架/模块结构/前后端描述/重要事项）、版本管理状态、运行状态、文档查询源、标准约束一次性勘查并同步组织到项目根目录 AGENTS.MD，再按 AGENTS.MD 约束执行开发任务，任务完成后回写变更。当用户交付 uni-app / uni-app x / uniCloud 开发任务、要求初始化或更新项目 AGENTS.MD、梳理项目上下文、检查仓库与运行状态、查询 uni-app 相关文档源时使用。
category: development
version: 1.0.0
author: fore.vip
agent_created: true
triggers:
  - "uni-app 开发"
  - "uniapp 开发任务"
  - "开发任务"
  - "AGENTS.MD"
  - "AGENTS.md"
  - "项目上下文"
  - "项目作用域"
  - "版本管理状态"
  - "运行状态检查"
  - "uniCloud 开发"
---

# uni-app 开发助手 · 任务驱动的上下文组织与执行

**输入**：一个 uni-app 项目的开发任务（新功能、改页面、修 bug、重构、迁移、接入第三方等）。
**产出**：项目根目录 `AGENTS.MD`（唯一事实源）+ 按约束落地的最小化代码变更 + 变更回写。

核心立场：**先建上下文，再动代码**。上下文缺失导致的返工，远大于勘查成本。

---

## 一、触发规则

| 用户意图 | 处理 |
|----------|------|
| 给一个 uni-app 项目的开发任务 | 走完整工作流（建/更新 AGENTS.MD → 执行 → 回写） |
| 只要求生成或更新 AGENTS.MD | 只执行 Step 1–7，不动业务代码 |
| 只问 uni-app 某个 API / 用法 | 直接查询官方文档源作答，不启动工作流 |
| 代码评审 / 只问不改 | 只读勘查 + 出报告，不写文件 |
| 非 uni-app 项目（纯 Web / 后端 / 其他框架） | 说明不适用，转通用开发流程 |

---

## 二、核心原则（不可协商）

1. **上下文先行** — 未确定项目作用域前，禁止写业务代码。
2. **AGENTS.MD 是唯一事实源** — 项目约定以 `AGENTS.MD` 为准；与模型先验冲突时，以 `AGENTS.MD` 为准。
3. **本地优先索引** — 新增/更新任务必须先检索本地已有实现（同栈项目、组件、范式、云对象），能复用就复用，禁止重复造轮子。
4. **官方文档优先** — 遇到不确定或新的 API/机制，先查官方文档源再动手；禁止凭训练数据臆造框架机制与 API。查不到就明确标注「需验证」。
5. **最小改动、不过度延伸** — 只改任务必需的部分；关联影响必须显性化提示，但不擅自扩大改动范围。
6. **可移植、无本地运行时依赖** — 本技能不依赖 python / shell / 固定安装路径。环境无 shell 时按「能力降级」章节执行。

---

## 三、工作流（8 步）

### Step 1 · 解析任务

从用户描述中提取并显式复述（不超过 5 行）：

- **目标**：一句话说清要交付什么
- **范围**：涉及模块 / 页面 / 云对象 / 数据表
- **约束**：用户显式提出的技术或产品约束
- **验收**：如何判断完成（页面表现 / 接口返回 / 编译通过）

任务描述含糊（缺目标或缺范围）时，先问清楚再继续。**一次问完，不挤牙膏式追问。**

### Step 2 · 项目作用域勘查

在项目根目录采集以下 5 类上下文，每类都要落到具体文件或结论，禁止泛泛而谈：

| 采集项 | 信息来源 | 输出要求 |
|--------|----------|----------|
| 框架与版本 | `package.json`（dependencies / devDependencies）、`manifest.json`（vueVersion）、`vite.config.*`、`vue.config.js` | Vue2 / Vue3、CLI 版或 HBuilderX 版、uni-app x 与否、构建工具 |
| 样式框架与令牌 | `uni.scss`、主题目录、`uni_modules/uni-scss`、UI 库（uni-ui / uView Plus / uv-ui / 自研） | 令牌源、CSS 变量策略、UI 库清单 |
| 模块结构 | 顶层目录、`pages.json`、`uni_modules/`、`components/`、`store/` | 目录职责表 + easycom 规则 |
| 前后端描述 | `uniCloud/`（`cloudfunctions` / `database`）、`common/`、`utils/`、`api/`、`services/` | 云函数 vs 云对象、数据访问层、鉴权方式 |
| 重要事项 | `README*`、`AGENTS.MD`、`CLAUDE.md`、`.workbuddy/memory/`、`manifest.json` 平台配置 | 已声明的规范、红线、待办、平台差异 |

**产物**：写入 AGENTS.MD 的「项目上下文」章节。

### Step 3 · 版本管理状态检查

按序执行（有 git 与 shell 能力时）：

```bash
git rev-parse --is-inside-work-tree   # 是否为 git 仓库
git branch --show-current             # 当前分支
git status --short                    # 工作区是否干净
git log -3 --oneline                  # 最近提交
git remote -v                         # 远端与推送目标
git stash list                        # 是否存在未应用的暂存
```

判定与处置：

| 状态 | 处置 |
|------|------|
| 工作区不干净 | 提示用户；涉及同名文件的改动必须先确认，禁止 `git checkout --` / `git reset --hard` 类破坏性操作 |
| 处于 main / master 等保护分支 | 提醒新建特性分支，不擅自切分支 |
| 无 git 仓库 | 记录为「无版本管理」，提示风险，不擅自 `git init` |
| 有 stash | 列出并提示，不擅自 pop |

**产物**：写入 AGENTS.MD 的「版本管理状态」章节，含检查时间与结论。

### Step 4 · 运行状态检查

| 检查项 | 方法 | 说明 |
|--------|------|------|
| 依赖是否就绪 | `package.json` 的 scripts + `node_modules` 是否存在 | 缺依赖时给出安装命令，不擅自安装 |
| 启动 / 构建命令 | 读取 `scripts` 字段（如 `dev:mp-weixin` / `build:mp-weixin`） | 记录到 AGENTS.MD，作为标准入口 |
| 编译产物 | `unpackage/dist/dev/mp-weixin`（开发）、`unpackage/dist/build/mp-weixin`（发行） | 自动化测试与真机预览用 `dev` 目录 |
| 目标平台配置 | `manifest.json` 的 `mp-weixin.appid` 等 | AppID 缺失或错配会导致运行失败 |
| 开发者工具进程 | 在 `.workbuddy/memory/` 或进程列表中确认 | 仅提示，不代为启动 GUI |

**产物**：写入 AGENTS.MD 的「运行状态」章节。

### Step 5 · 文档源登记

按项目**实际使用的技术栈**从下表挑选，逐条登记到 AGENTS.MD 的「文档查询源」。未使用的技术不登记，避免噪音。
如果项目文档源因为官方安全拦截不可达,尝试通过其它技能或者路径获取,如果获取失败要告知用户，拒绝胡乱定义！

| 类别 | 官方文档源 | 适用条件 |
|------|-----------|----------|
| uni-app 框架 | https://uniapp.dcloud.net.cn/ （旧址 https://uniapp.dcloud.io/ 会自动跳转） | 必选 |
| uni-app x | https://doc.dcloud.net.cn/uni-app-x/ | 使用 uts / uni-app x 时 |
| uniCloud | https://doc.dcloud.net.cn/uniCloud/ | 使用云开发时 |
| uni-id / uni-id-common | https://doc.dcloud.net.cn/uni-id/ | 使用官方用户体系时 |
| uni-id-pages | https://doc.dcloud.net.cn/uni-id-pages/ | 引入 uni-id-pages 时 |
| uni_modules 规范 | https://uniapp.dcloud.net.cn/uni_modules | 必选（涉及复用与发布） |
| easycom 组件规范 | https://uniapp.dcloud.net.cn/collocation/pages?id=easycom | 必选 |
| uni-ui / uni-scss | https://uniapp.dcloud.net.cn/component/uniui/ | 引入官方组件库时 |
| Vue 3 | https://cn.vuejs.org/ | Vue3 项目 |
| Pinia | https://pinia.vuejs.org/zh/ | 使用 Pinia 时 |
| 微信小程序 | https://developers.weixin.qq.com/miniprogram/dev/framework/ | 发行到微信小程序 |
| QQ 小程序 | https://q.qq.com/wiki/ | 发行到 QQ 小程序 |
| 支付宝 / 抖音小程序 | 各平台开放文档 | 对应平台发行时 |
| 腾讯位置服务 | https://lbs.qq.com/ | 使用定位 / 地图能力 |

登记时必须同时写入以下强制声明（原文照抄）：

> **遇新问题必须查询官方文档**：任何不确定的 API、配置项、平台差异、框架机制，必须先查询上表对应文档源再实施。禁止凭记忆或训练数据臆造 API 与机制；官方文档未覆盖时，明确标注「需验证」并给出验证方式，不得伪装成既定事实。

### Step 6 · 标准约束声明

向 AGENTS.MD 写入「标准约束」章节，包含四类声明：

1. **敏捷设计规范**
   - 任务拆到可独立验证的粒度，单任务单提交
   - 先跑通主链路，再补边界与异常
   - 每轮结束必须给出可验证结果（编译通过 / 页面可达 / 接口返回符合预期）
2. **文档规范**
   - 代码注释只解释「为什么」，不解释「是什么」
   - 涉及接口、数据结构、配置项的改动，同步更新对应文档或 AGENTS.MD
   - 变更记录写入 AGENTS.MD 的「变更日志」
3. **设计规范**
   - 间距 / 圆角 / 颜色 / 字号一律使用项目既有的设计令牌或 CSS 变量，禁止魔法数字
   - 新增全局样式类前，先确认 2 个以上使用场景，否则就地实现
   - 跨页面视觉元素（渐变、间距、主色）保持一致
4. **开发规范**
   - **本地优先**：新增 / 更新任务先索引本地已实现的项目、组件、范式，能复用不重写
   - **简化路径**：优先最简实现，能用配置解决的不写代码，能用一个组件解决的不新增组件
   - **边界关联**：改动前检查依赖与被依赖方（配置、路由、数据表、接口契约、缓存），在回复中显性列出影响面
   - **不过度延伸**：不做任务之外的重构、优化、格式化；发现额外问题只报告不擅自动手

### Step 7 · 写入 / 更新 AGENTS.MD

**位置**：项目根目录，文件名 `AGENTS.MD`（已存在 `AGENTS.MD` / `AGENTS.md` / `CLAUDE.md` 时复用已有文件，做增量合并，**禁止覆盖用户已写内容**）。

首次生成使用以下骨架，按实填，无内容的小节写「暂缺」而不是删除：

```markdown
# AGENTS.MD

> 由 fore-vip-uniapp-dev 生成 · 最后更新：<YYYY-MM-DD>

## 1. 项目上下文

### 1.1 框架与版本
- 框架：uni-app（Vue3 / CLI 版）
- 构建：<vite / webpack>
- 关键依赖：<名称@版本>

### 1.2 样式框架与令牌
- 令牌源：<uni.scss / theme.scss / CSS 变量>
- UI 库：<uni-ui / uView Plus / 自研>
- 约束：<间距|圆角|颜色|字号 一律走令牌，禁止魔法数字>

### 1.3 模块结构
| 目录 | 职责 |
|------|------|
| pages/ | 页面 |
| components/ | 项目内组件 |
| uni_modules/ | 跨项目复用模块（含各自 components/，自动 easycom） |
| uniCloud/cloudfunctions/ | 云对象与云函数 |
| store/ | 状态管理 |

### 1.4 前后端描述
- 后端形态：<云对象 / 云函数 / 自建 API>
- 鉴权：<uni-id-common checkToken / 自建 token>：`<范式说明>`
- 数据访问：<数据库集合 / ORM / 直连>

### 1.5 重要事项
- <已声明红线、平台差异、待办>

## 2. 版本管理状态
- 仓库：<是 / 否>　分支：<name>　工作区：<干净 / N 个改动>
- 最近提交：<hash 摘要>
- 风险提示：<无 / 具体风险>

## 3. 运行状态
- 依赖：<已安装 / 缺失>
- 启动命令：`npm run dev:mp-weixin`
- 构建命令：`npm run build:mp-weixin`
- 编译产物：unpackage/dist/dev/mp-weixin
- 平台配置：mp-weixin appid <AppID>

## 4. 文档查询源

| 类别 | 文档源 |
|------|--------|
| uni-app | https://uniapp.dcloud.net.cn/ |
| ... | ... |

> **遇新问题必须查询官方文档**：任何不确定的 API、配置项、平台差异、框架机制，必须先查询上表对应文档源再实施。禁止凭记忆或训练数据臆造 API 与机制；官方文档未覆盖时，明确标注「需验证」并给出验证方式，不得伪装成既定事实。

## 5. 标准约束

### 5.1 敏捷设计规范
### 5.2 文档规范
### 5.3 设计规范
### 5.4 开发规范

## 6. 本地可复用索引

| 能力 | 本地实现位置 | 复用方式 |
|------|------------|---------|

## 7. 变更日志

### YYYY-MM-DD
- <任务>：<改动摘要 + 影响面 + 验证方式>
```

**关键动作**：Step 2 勘查出的本地可复用实现（同栈项目、组件、云对象、范式）必须登记到「本地可复用索引」，作为后续任务的优先检索入口。

### Step 8 · 执行任务与回写

1. 按 AGENTS.MD 约束实施改动，遵守「本地优先」与「不过度延伸」
2. 不确定处查文档源；仍不确定则标注「需验证」并暂停等待确认
3. 自测：编译 / 运行 / 接口返回，给出可验证结论
4. **回写 AGENTS.MD**：更新「变更日志」与受影响章节（新增组件、新依赖、新约定）
5. 按「输出规范」汇报

---

## 四、能力探测与降级

不同运行环境能力不同，按可用能力降级，禁止因缺少某能力而中断任务：

| 能力 | 有 | 无（降级方案） |
|------|----|---------------|
| shell | 执行 git / 依赖 / 进程检查 | 跳过 Step 3 命令，改读目录与配置文件推断，缺失项在 AGENTS.MD 标注「未检查（无 shell 能力）」 |
| git | 完整版本状态 | 记录「版本管理状态未知」，提示用户手动确认 |
| 联网检索 | 查官方文档源 | 明确告知某项未查证，标注「需验证」，不臆造 |
| 文件写入 | 生成 AGENTS.MD | 输出完整 AGENTS.MD 内容由用户自行保存 |

---

## 五、执行红线

- **禁止破坏性 git 操作**：`reset --hard`、`checkout --`、`clean -fd`、`push --force` 一律不主动执行，必须先取得用户明确确认。
- **删除文件走回收站**：macOS 用 `trash`，禁止 `rm -rf`。清理目录前必须排除当前工作目录。
- **不擅自安装依赖、不擅自初始化仓库、不擅自切换分支**。
- **不修改 `uni_modules` 内第三方模块源码**（会被插件市场更新覆盖）；需要定制时在业务层包装。
- **不凭记忆写框架机制**：uni-app / uniCloud / 小程序 API 一律以官方文档源为准。
- **改动范围超出任务**时停下报告，不自行扩大。

---

## 六、输出规范

每次任务结束按三段式汇报：

```
## 结论
一句话：完成什么 / 结论是什么

## 执行步骤
1. ...
2. ...

## 引用来源
- 官方文档：<链接>
- 本地复用：<项目/文件路径>
- 变更文件：<路径清单>
```

**未查证项必须单独列出**，标注「需验证」。

---

## 七、技术基线（uni-app v3 常见项目，按项目实际上下文校正）

以下为高频基线，**仅在 Step 2 勘查确认项目确实使用该技术后写入 AGENTS.MD**，不适用则忽略：

| 主题 | 基线 | 反例 |
|------|------|------|
| 登录态 | uni-id-pages 项目用 `import { store } from '@/uni_modules/uni-id-pages/common/store.js'`，读 `store.userInfo` / `store.hasLogin` | `uni.getStorageSync('uni-id-pages-userInfo')`（非响应式、耦合内部 key） |
| 后端鉴权 | 云对象内 `uni-id-common` 的 `createInstance` + 方法体 `await checkToken(this.getUniIdToken())` | v2 时代的 `uniID.action(...)` / `callFunction` 调 uni-id |
| 网络请求 | `await uni.request({...})` 或项目既有封装，Promise 风格 | `let [err, res] = await uni.request()`（axios 风格，非 uni-app 标准） |
| 样式令牌 | 单一权威令牌源（如 `uni.scss`）→ CSS 变量由令牌派生 | CSS 变量里手写独立数值，与 SASS 令牌脱钩 |
| 组件复用 | 跨项目复用放 `uni_modules/<module>/components/`，项目内复用放 `components/` | 把 `uni_modules` 组件复制到项目 `components/` |
| 页面实现 | 页面只做组合，复杂逻辑抽组件 / composable | 单体大页堆砌 |

---

**版本**：v1.0.0（2026-08-30）
**标签**：uni-app, uniCloud, 微信小程序, 开发工作流, AGENTS.MD
