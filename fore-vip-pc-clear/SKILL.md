---
name: fore-vip-pc-clear
display_name: PC清理优化
display_name_en: PC Clear & Optimize
description: 电脑系统清理与优化助手（fore.vip）。先读取当前系统信息（macOS/Windows/Linux 自动识别），再做三件事：①性能优化——检测硬件与软件状态，按优先级处理系统界面、启动项、后台进程，敏感/系统安全级操作必须先征询用户；②缓存与硬盘清理——按风险分级逐项清理，全程记录步骤并自动生成一键清理脚本放置到桌面；③环境优化——分析当前系统、工具列表与用户工作性质，推荐更优工具并引导配置到最佳状态。当用户说「清理电脑/电脑太卡了/清理缓存/磁盘清理/C盘满了/电脑提速/开机慢/后台太多/优化系统/系统垃圾」时启用。
description_zh: 电脑系统清理与优化助手。自动识别 macOS/Windows/Linux，完成系统体检、按风险分级（A安全/B中等/C敏感）清理缓存与硬盘、优化启动项与后台进程、推荐更优工具环境，并生成桌面一键清理脚本。敏感操作一律先征询用户。
description_en: A cross-platform (macOS/Windows/Linux) PC cleanup and performance optimization assistant. Runs a system health check, performs risk-graded (A safe / B moderate / C sensitive) cache and disk cleanup, tunes startup items and background processes, recommends better tooling, and generates a one-click cleanup script on the desktop. Sensitive operations always require explicit user consent.
category: system-tools
version: 1.1.0
author: fore.vip
agent_created: true
---

# PC清理优化 · 系统清理与性能优化

帮用户清理电脑垃圾、优化性能、改进工具环境。跨平台（macOS / Windows / Linux），一切动作以「先读系统信息」为前提，敏感操作必须征询用户，清理步骤必须沉淀为桌面一键脚本。

## 触发规则

| 用户意图 | 处理 |
|----------|------|
| 电脑卡 / 提速 / 开机慢 / 后台太多 / 优化系统 | 进入完整流程（从第 1 步开始） |
| 清理缓存 / 磁盘清理 / C盘满了 / 系统垃圾 | 直接进入第 3 步（仍先读系统信息） |
| 推荐 / 替换软件工具 | 直接进入第 4 步 |
| 只问本技能能干嘛 | 仅介绍，不执行任何操作 |

## 核心准则

- **系统信息先行**：任何操作前先完成第 1 步，禁止凭经验臆断用户环境。
- **风险分级**：所有清理/优化动作先对照风险分级表归类，C 级不征询不执行。
- **全程记录**：每执行一步就记录一步（命令 + 说明 + 级别），结束时必产桌面一键脚本。
- **逐步处理**：启动项与后台进程逐项列出、逐项确认，禁止批量盲操作。
- **最短路径**：能一条命令解决的检测不拆成多条；高危替代方案优先于直接删改。

## 风险分级表（执行任何动作前先归类）

| 级别 | 定义 | 处理方式 | 示例 |
|------|------|----------|------|
| **A 安全** | 用户级缓存/临时文件，删除可再生成 | 直接执行，事后汇报 | 浏览器缓存、npm/pip 缓存、系统临时目录、废纸篓 |
| **B 中等** | 删错会丢数据或影响体验，但可恢复 | 说明影响 + 回滚方式，征得同意后执行 | 下载目录旧文件、开发构建产物（DerivedData/node_modules）、系统日志 |
| **C 敏感/系统安全级** | 涉及系统内核、安全策略、开机自启、注册表、系统进程、sudo | **必须逐项征询用户**，说明风险与回滚，用户明确同意才执行，并优先给 GUI 替代路径 | 启动项增删、launchd/注册表/服务改动、内核扩展、关闭 SIP 相关项、结束系统进程 |

> 判断不确定时一律就高归类。各平台具体目标清单见 @references/cleanup-targets.md

## 工作流程

### 1. 读取系统信息

自动识别操作系统后按对应命令采集，输出一份「系统体检摘要」（机型/CPU/内存/磁盘占用 TOP/系统版本/运行时长）：

| 项目 | macOS | Windows | Linux |
|------|-------|---------|-------|
| 系统 | `sw_vers` | `systeminfo` 或 PowerShell `Get-ComputerInfo` | `cat /etc/os-release` |
| 硬件 | `sysctl -n machdep.cpu.brand_string; sysctl -n hw.memsize` | `Get-CimInstance Win32_Processor,Win32_PhysicalMemory` | `lscpu; free -h` |
| 磁盘占用 | `df -h /` | `Get-PSDrive` | `df -h /` |
| 大文件 TOP | `du -sh ~/Library/Caches/* 2>/dev/null \| sort -hr \| head` | WinDirStat 逻辑（PowerShell 按目录统计） | `du -sh ~/.cache/* \| sort -hr \| head` |
| 运行时长/负载 | `uptime` | `systeminfo`（系统启动时间） | `uptime` |

后续所有步骤以这份摘要为依据，摘要同时决定清理的优先目标。

### 2. 性能优化（按优先级处理）

1. **硬件/软件状态检测**：内存占用、磁盘剩余（<10% 告警）、CPU 占用 TOP 进程、运行时长过长提示重启。
2. **系统界面优化**（A/B 级）：关闭透明效果/动画、降低视觉效果——macOS 走「系统设置」路径提示，Windows 走「性能选项」，Linux 视 DE 而定。
3. **启动项处理**（C 级，逐项征询）：列出全部自启项（macOS `launchctl list` + 系统设置；Windows 任务管理器「启动」标签/`shell:startup`；Linux `systemctl list-unit-files` + crontab），逐项给出「保留/禁用/删除」建议，用户确认一项处理一项。
4. **后台进程**（视级别）：A 级（用户级卡死进程）可直接结束；C 级（系统进程/sudo）只建议不擅动。

### 3. 缓存与硬盘清理（必产一键脚本）

1. 按 @references/cleanup-targets.md 的平台清单逐项检测可回收空间。
2. A 级直接清理；B 级说明后清理；C 级征询。
3. **每执行一步立即记录**：`{描述, 命令, 风险级别, 回收空间}`。
4. 结束时调用 `scripts/gen_clean_script.py`，把本次全部步骤生成为一键清理脚本放到**桌面**：

```bash
python3 scripts/gen_clean_script.py --platform macos --title "PC清理" --steps steps.json
```

`steps.json` 由执行 Agent 按脚本内注释格式组装（或用 `--steps-json '<JSON>'` 直接传字符串）。生成规则：
- macOS → `~/Desktop/PC清理-一键.command`（自动 chmod +x）
- Windows → 桌面 `PC清理-一键.bat`
- Linux → `~/Desktop/PC清理-一键.sh`

脚本内容含：每步注释说明、风险级别标记、C 级步骤自动加交互确认。

> **⚠️ 脚本缺失兜底（必检）**：部分发布渠道（如 SKILLHUB 安装版）只分发 `SKILL.md`，`scripts/` 目录可能不存在。调用前先检测：
> ```bash
> test -f scripts/gen_clean_script.py && echo OK || echo MISSING
> ```
> 输出 `MISSING` 时**不中断、不尝试下载**，改按文末「附录 A · 脚本不可用时的等价生成规范」现场生成一次性脚本执行，产物与调用原脚本一致。

### 4. 环境优化

1. **盘点**：列用户已装工具（开发：`which`/包管理器列表；应用：/Applications、开始菜单、`dpkg`/`flatpak`），结合用户工作性质（从当前会话与用户画像判断，存疑直接问）。
2. **推荐**：对照 @references/tool-recommendations.md，只推荐「有明确优势」的替代（更快/更省/更安全），逐项给出「当前工具 → 推荐工具 + 理由 + 迁移成本」；无优势不推荐，不为了推荐而推荐。
3. **引导配置**：用户选定后，给出最佳状态配置步骤（设置项 + 命令），能自动执行的按风险分级执行，C 级（如改 shell 默认、系统代理）征询后执行。

## 输出模板

```
## 系统体检摘要
[系统/硬件/磁盘/负载 一览，异常项标红]

## 性能优化
| 项目 | 发现 | 处理 | 级别 | 状态 |
（敏感项标注「已征询」）

## 清理结果
| 清理项 | 级别 | 回收空间 |
合计回收：XX GB
一键脚本：~/Desktop/PC清理-一键.command（含 N 步，C 级 X 步已加确认）

## 环境优化建议
| 当前工具 | 推荐替代 | 理由 | 迁移成本 |
已引导配置：…
```

## 注意事项

- **禁止**：未经征询执行任何 C 级操作；删除 `~/Documents`、用户相册、聊天记录等用户数据目录；`rm -rf` 任何未先 `du`/`ls` 核实的路径。
- 生成的一键脚本是「可重复执行」的清理脚本，不是一次性记录——只沉淀安全可重复的步骤，一次性危险操作不写入。
- Windows 下优先 PowerShell（管理员权限单独提示），macOS/Linux 下 sudo 命令在脚本中保留但标注需密码。
- 工具推荐遵守中立原则：不给返利导向的「推荐」，不推荐破解/来路不明的软件。

## 附录 A · 脚本不可用时的等价生成规范

当 `scripts/gen_clean_script.py` 缺失（渠道只分发 `SKILL.md`）时，Agent **现场写一个一次性 Python 脚本**到临时目录（`$TMPDIR` / `%TEMP%` / `/tmp`）执行，用完即弃，**不落盘到技能目录**（仓库零脚本原则）。生成的一键脚本必须满足以下全部约束：

**1. 输入**
- 步骤数组，每项三字段：`desc`（说明）、`cmd`（命令）、`level`（`A` / `B` / `C`）。
- 缺任一字段直接校验失败退出；`level` 非 A/B/C 亦失败。

**2. 桌面目录定位（依次回退）**
`$PC_CLEAR_DESKTOP` → `~/Desktop` → Windows 注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders` 的 `Desktop` 值 → `$XDG_DESKTOP_DIR` → 用户根目录 `~`。

**3. 输出文件**
| 平台 | 文件名 | 权限 |
|------|--------|------|
| macOS | `PC清理-一键.command` | `chmod 755` |
| Windows | `PC清理-一键.bat` | — |
| Linux | `PC清理-一键.sh` | `chmod 755` |

标题默认 `PC清理-YYYYMMDD`，可由用户指定。

**4. 脚本正文**
- 头部：`#!` 声明（Unix）/ `@echo off` + `chcp 65001 >nul`（Windows），写生成日期与级别说明（A=安全可重复 / B=中等 / C=敏感需确认）。
- 每步前加注释块：`第 N 步 [X级] <desc>`；B 级额外注释「可能影响首次速度/丢失历史数据」。
- **A/B 级**：按序执行，单步失败仅打印告警并继续，累计成功/跳过数。
- **C 级**：必须包裹交互确认，Unix 用 `read -r -p "确认执行？(y/N)"`、Windows 用 `set /p REPLY=`，仅输入 `y/Y` 才执行，否则跳过计数。
- Windows 版末尾 `pause`；两个版本结尾均打印「完成：执行 N 步，跳过 M 步」。

**5. 硬约束**
- 只写入「可安全重复执行」的步骤，一次性危险操作不得进入脚本。
- 生成的脚本不得包含 `rm -rf` 未经核实的路径。

## 参考资料

- @references/cleanup-targets.md — 各平台清理目标与风险分级明细
- @references/tool-recommendations.md — 按工作性质的工具替代推荐库
- @scripts/gen_clean_script.py — 桌面一键清理脚本生成器（可能随渠道缺失，见附录 A）

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
