#!/usr/bin/env python3
"""gen_clean_script.py — 桌面一键清理脚本生成器（fore-vip-pc-clear）

把本次清理会话记录的步骤生成为可重复执行的一键脚本，放到用户桌面：
- macOS  → ~/Desktop/PC清理-一键.command（自动 chmod +x）
- Windows → 桌面/PC清理-一键.bat
- Linux  → ~/Desktop/PC清理-一键.sh（自动 chmod +x）

用法：
    python3 gen_clean_script.py --platform macos --title "PC清理" --steps steps.json
    python3 gen_clean_script.py --platform windows --steps-json '<JSON>'

steps.json 格式：
{
  "platform": "macos",            # macos | windows | linux（与 --platform 一致或省略）
  "title": "PC清理-20260822",     # 可选，默认含日期
  "steps": [
    {
      "desc": "清理 Homebrew 缓存",       # 必填：步骤说明（写入脚本注释）
      "cmd": "brew cleanup --prune=all -s",  # 必填：命令
      "level": "A"                        # 必填：A | B | C
    }
  ]
}

规则：
- 只有可安全重复执行的步骤才应写入（一次性危险操作不要传进来）
- C 级步骤在生成的脚本中自动加交互确认（不确认则跳过）
- Windows 生成 .bat；如需 PowerShell 版可自行扩展

独立运行，无第三方依赖。
"""

import argparse
import datetime
import json
import os
import sys

VALID_PLATFORMS = ("macos", "windows", "linux")


def desktop_path() -> str:
    """定位桌面目录（跨平台，含中文系统 User Shell Folders 兜底）。"""
    # 1) 显式配置
    desktop = os.environ.get("PC_CLEAR_DESKTOP")
    if desktop and os.path.isdir(desktop):
        return desktop
    # 2) 常规 ~/Desktop
    home = os.path.expanduser("~")
    candidate = os.path.join(home, "Desktop")
    if os.path.isdir(candidate):
        return candidate
    # 3) Windows 中文系统注册表兜底
    if sys.platform.startswith("win"):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            )
            val, _ = winreg.QueryValueEx(key, "Desktop")
            resolved = os.path.expandvars(val)
            if os.path.isdir(resolved):
                return resolved
        except OSError:
            pass
    # 4) XDG 兜底（Linux）
    xdg = os.environ.get("XDG_DESKTOP_DIR")
    if xdg and os.path.isdir(xdg):
        return xdg
    return home  # 最后兜底放用户根目录


def load_steps(args) -> dict:
    if args.steps_json:
        data = json.loads(args.steps_json)
    elif args.steps:
        with open(args.steps, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise SystemExit("必须提供 --steps <file> 或 --steps-json '<JSON>'")

    if not isinstance(data, dict) or not data.get("steps"):
        raise SystemExit("steps.json 格式错误：缺少非空 steps 数组")

    for i, s in enumerate(data["steps"], 1):
        for field in ("desc", "cmd", "level"):
            if not s.get(field):
                raise SystemExit(f"第 {i} 步缺少必填字段 {field}")
        if s["level"] not in ("A", "B", "C"):
            raise SystemExit(f"第 {i} 步 level 必须为 A/B/C")
    return data


def render_unix(data: dict, title: str) -> str:
    """生成 macOS .command / Linux .sh 脚本。"""
    lines = [
        "#!/bin/bash",
        f"# {title} — 一键清理脚本（fore-vip-pc-clear 生成）",
        f"# 生成时间：{datetime.date.today().isoformat()}",
        "# 级别说明：A=安全可重复 | B=中等（注释已标影响） | C=敏感（执行前交互确认）",
        "set -u  # 未定义变量报错，但单步失败不中断（每步独立判断）",
        "",
        'echo "========================================"',
        f'echo " {title}"',
        'echo "========================================"',
        'TOTAL_OK=0; TOTAL_SKIP=0',
        "",
    ]
    for i, s in enumerate(data["steps"], 1):
        level, desc, cmd = s["level"], s["desc"], s["cmd"]
        lines.append(f"# ---------- 第 {i} 步 [{level}级] {desc} ----------")
        if level == "C":
            lines += [
                'read -r -p "  ↑ 敏感操作，确认执行？(y/N) " REPLY',
                'if [[ "$REPLY" == "y" || "$REPLY" == "Y" ]]; then',
                f"  {cmd}",
                "  TOTAL_OK=$((TOTAL_OK+1))",
                "else",
                '  echo "  已跳过"',
                "  TOTAL_SKIP=$((TOTAL_SKIP+1))",
                "fi",
            ]
        else:
            if level == "B":
                lines.append("# B级提示：可能影响首次使用速度/丢失历史数据")
            lines += [
                f"echo \"[{i}/{len(data['steps'])}] {desc}\"",
                f"if {cmd}; then",
                "  TOTAL_OK=$((TOTAL_OK+1))",
                "else",
                '  echo "  ⚠ 本步失败，已跳过"',
                "fi",
            ]
        lines.append("")
    lines += [
        'echo "========================================"',
        'echo " 完成：执行 $TOTAL_OK 步，跳过 $TOTAL_SKIP 步"',
        'echo "========================================"',
    ]
    return "\n".join(lines) + "\n"


def render_windows(data: dict, title: str) -> str:
    """生成 Windows .bat 脚本（GBK 兼容性优先，中文注释用 chcp 65001）。"""
    n = len(data["steps"])
    lines = [
        "@echo off",
        "chcp 65001 >nul",
        f"rem {title} — 一键清理脚本（fore-vip-pc-clear 生成）",
        f"rem 生成时间：{datetime.date.today().isoformat()}",
        f"setlocal EnableDelayedExpansion",
        "set /a TOTAL_OK=0",
        "set /a TOTAL_SKIP=0",
        'echo ========================================',
        f'echo  {title}',
        'echo ========================================',
    ]
    for i, s in enumerate(data["steps"], 1):
        level, desc, cmd = s["level"], s["desc"], s["cmd"]
        lines.append(f"rem ---------- 第 {i} 步 [{level}级] {desc} ----------")
        if level == "C":
            lines += [
                "set /p REPLY=  ↑ 敏感操作，确认执行？(y/N): ",
                'if /I "!REPLY!"=="y" (',
                f"  {cmd}",
                "  set /a TOTAL_OK+=1",
                ") else (",
                '  echo   已跳过',
                "  set /a TOTAL_SKIP+=1",
                ")",
            ]
        else:
            lines += [
                f'echo [{i}/{n}] {desc}',
                f"{cmd}",
                'if !errorlevel! equ 0 (set /a TOTAL_OK+=1) else (echo   ⚠ 本步失败，已跳过)',
            ]
    lines += [
        'echo ========================================',
        'echo  完成：执行 %TOTAL_OK% 步，跳过 %TOTAL_SKIP% 步',
        'echo ========================================',
        "pause",
    ]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="生成桌面一键清理脚本")
    ap.add_argument("--platform", required=True, choices=VALID_PLATFORMS)
    ap.add_argument("--steps", help="steps.json 文件路径")
    ap.add_argument("--steps-json", help="steps JSON 字符串（与 --steps 二选一）")
    ap.add_argument("--title", default="", help="脚本标题（默认：PC清理-<日期>）")
    args = ap.parse_args()

    data = load_steps(args)
    platform = data.get("platform", args.platform)
    if platform not in VALID_PLATFORMS:
        platform = args.platform
    title = args.title or data.get("title") or f"PC清理-{datetime.date.today():%Y%m%d}"

    desktop = desktop_path()
    if platform == "windows":
        path = os.path.join(desktop, f"{title}-一键.bat")
        content = render_windows(data, title)
    else:
        ext = "command" if platform == "macos" else "sh"
        path = os.path.join(desktop, f"{title}-一键.{ext}")
        content = render_unix(data, title)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    if platform != "windows":
        os.chmod(path, 0o755)

    n = len(data["steps"])
    c_count = sum(1 for s in data["steps"] if s["level"] == "C")
    print(f"✅ 已生成一键清理脚本：{path}")
    print(f"   共 {n} 步（C级敏感步骤 {c_count} 步，执行时将逐项确认）")


if __name__ == "__main__":
    main()
