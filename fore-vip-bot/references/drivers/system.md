# 驱动模板：本机外设（系统 API / CLI）

适用：控制用户**电脑本身**的外设与系统状态——音量、屏幕亮度/开关、电源（休眠/关机）、麦克风/摄像头占用、风扇转速等。
通信方式：宿主系统 API 或 CLI（macOS/Windows/Linux 差异由中控做平台判断）。

## 连接信息

无需外部连接，`type: system`，`config: {}`。中控运行时按 `process.platform` 选实现。

## 平台指令映射

| 中控指令 | macOS | Windows | Linux |
|----------|-------|---------|-------|
| `{act: set, id: sys_volume, prop: level, val: 50}` | `osascript -e "set volume 5"` (0–100→0–7) | `nircmd setsysvolume 32768` | `amixer set Master 50%` |
| `{act: set, id: sys_display, prop: power, val: off}` | `pmset displaysleepnow` | `nircmd monitor off` | `xset dpms force off` |
| `{act: set, id: sys_power, prop: state, val: sleep}` | `pmset sleepnow` | `rundll32 powrprof.dll,SetSuspendState` | `systemctl suspend` |
| `{act: read, id: sys_volume, prop: level}` | `osascript -e "output volume of (get volume settings)"` | `nircmd` 读 | `amixer get Master` |
| `{act: action, id: sys_cam, prop: capture}` | 调 `imagesnap` / 宿主相机 API | 宿主相机 API | `fswebcam` |

## 安全确认

- `sys_power` 的 `shutdown` / `restart` 属**不可逆高危**，强制二次确认。
- `sys_display off` / `sys_power sleep` 若用户正在用本机，可能中断会话，提示风险。
- 不默认常开摄像头/麦克风，捕获前明确告知。

## 注意

- 命令需宿主环境的 CLI 工具（nircmd/amixer/imagesnap 等）存在；缺失则报错并给安装提示。
- 权限：macOS 调系统事件需辅助功能/麦克风相机权限；首次会弹系统授权，中控提示用户允许。
- 这些指令是**本地执行**，不走网络，凭证无关。
