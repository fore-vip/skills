# 各平台清理目标与风险分级明细

按平台列出可检测/清理的目标。执行前先 `du -sh` / 目录统计确认体积，再按分级处理。**列表未穷尽，遇到新目标按定义归类，拿不准就高。**

## macOS

### A 级（直接执行）

| 目标 | 路径 / 命令 | 说明 |
|------|------------|------|
| 用户缓存 | `~/Library/Caches/` | 应用缓存，删后自动重建 |
| 系统临时目录 | `/tmp`（用户可写部分）、`$TMPDIR` | 重启即清，安全 |
| 废纸篓 | `~/.Trash/` | 先提醒用户确认 |
| DNS 缓存 | `sudo dscacheutil -flushcache`（sudo 但无风险） | 网络解析缓存 |
| Homebrew 缓存 | `brew cleanup --prune=all -s` | 官方命令 |
| npm 缓存 | `npm cache clean --force` | |
| pip 缓存 | `pip cache purge` | |
| Xcode 模拟器缓存 | `~/Library/Developer/CoreSimulator/Caches/` | 非设备数据 |

### B 级（说明后执行）

| 目标 | 路径 | 说明 / 回滚 |
|------|------|------------|
| Xcode 构建产物 | `~/Library/Developer/Xcode/DerivedData/` | 下次构建重新生成，首次变慢 |
| iOS 设备备份 | `~/Library/Application Support/MobileSync/Backup/` | **删除即丢备份**，列出体积让用户决定 |
| 下载目录旧文件 | `~/Downloads/` | 只列出 >100MB 且 >90 天的文件供用户勾选 |
| 日志文件 | `~/Library/Logs/` | 排查问题会缺失历史日志 |
| Docker 悬空镜像 | `docker system prune -f`（有容器则 B 级） | 不可恢复，仅清未引用资源 |
| node_modules / venv | 各项目目录 | 需重新 `npm install`，先列总占用 |

### C 级（必须逐项征询）

| 目标 | 说明 |
|------|------|
| 启动项：`launchctl list` + `~/Library/LaunchAgents/`、`/Library/LaunchAgents/`、`/Library/LaunchDaemons/` | 删错可能导致服务失效；建议改用 `launchctl disable` 而非删文件 |
| 系统文件 / `/System`、`/Library` 下任何内容 | SIP 保护，禁止引导关闭 SIP |
| 内核扩展 | `kextstat` 查看，一律只建议不动 |
| 系统进程（`kill` PID < 100 或 root 进程） | 只建议，不执行 |
| FileVault / 防火墙 / Gatekeeper 设置 | 安全策略，只给 GUI 路径让用户自己改 |

## Windows

### A 级

| 目标 | 命令 / 路径 |
|------|------------|
| 磁盘清理 | `cleanmgr /sagerun:1` 或「存储感知」 |
| 系统临时文件 | `%TEMP%`（用户级）、`C:\Windows\Temp`（需管理员） |
| DNS 缓存 | `ipconfig /flushdns` |
| 浏览器缓存 | 各浏览器设置内清除 |
| npm/pip 缓存 | 同 macOS命令 |
| 回收站 | `Clear-RecycleBin -Force`（先确认） |
| 传递优化文件 | 设置 → 系统 → 存储 → 临时文件 |

### B 级

| 目标 | 说明 |
|------|------|
| Windows 更新缓存 `C:\Windows\SoftwareDistribution\Download` | 清后需重新下载更新，建议先停 wuauserv 服务 |
| 休眠文件 `hiberfil.sys`（`powercfg /h off`） | 关闭休眠功能，占用约内存大小 |
| `WinSxS` 组件清理（`Dism /Online /Cleanup-Image /StartComponentCleanup`） | 耗时长，不可回滚旧更新 |
| 下载目录旧文件 | 同 macOS 逻辑 |
| Docker/WSL 虚拟磁盘 | `wsl --shutdown` 后 compact，操作前提示关闭会话 |

### C 级

| 目标 | 说明 |
|------|------|
| 启动项：任务管理器「启动」标签、`shell:startup`、注册表 `HKCU\...\Run` | 注册表改动必须先导出备份 `.reg` |
| 系统服务 `services.msc` / `sc config` | 禁用关键服务会导致系统异常，逐项说明 |
| 系统进程（任务管理器中标「系统关键」） | 只建议 |
| UAC / Defender / 防火墙设置 | 安全策略，只给路径 |
| `sfc /scannow` 等修复操作 | 变更系统文件，征询后执行 |

## Linux

### A 级

| 目标 | 命令 |
|------|------|
| 用户缓存 | `~/.cache/` |
| 包管理器缓存 | Debian: `sudo apt clean`；Fedora: `sudo dnf clean all`；Arch: `sudo pacman -Sc` |
| 临时文件 | `/tmp`（注意正在使用的会话文件） |
| journal 日志 | `sudo journalctl --vacuum-time=7d` |

### B 级

| 目标 | 说明 |
|------|------|
| 旧内核 | `apt autoremove --purge`，保留当前内核 |
| Docker 清理 | `docker system prune -f`（有运行容器则 B 级） |
| snap 旧版本 | `snap list --all` 中 disabled 的版本 |
| ~/.cache 下大型工具链缓存（rustup、go、pip） | 重下耗时 |

### C 级

| 目标 | 说明 |
|------|------|
| systemd 服务 `systemctl enable/disable` | 逐项征询，说明依赖关系 |
| crontab / 用户级 systemd timer | 同上 |
| 内核参数 sysctl | 修改前备份原值 |
| 系统进程 / root 进程 | 只建议 |

## 通用规则

1. 清理前先「测量」：每项先统计体积写入记录，清理后对比，得出回收空间。
2. 浏览器缓存优先走浏览器自带「清除浏览数据」，避免直接删 Profile 目录（会丢登录态/扩展，属 B 级）。
3. 云盘同步目录（iCloud/OneDrive/坚果云）、聊天工具数据目录（微信/QQ 接收文件）**只列出不删**，由用户手动处理。
4. 任何 `rm`/删除类命令写入一键脚本前，确认路径为「可重建的缓存/临时」类目标。
