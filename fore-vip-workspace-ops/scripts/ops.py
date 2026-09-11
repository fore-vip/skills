#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fore.vip 工作区自动化中枢 (WorkspaceOps) —— 零第三方依赖，仅用 Python 3 标准库。

子命令:
  audit     工作区体检（仓库矩阵 / 只读纪律 / 密钥明文 / 残留 / 磁盘 / README 漂移）
  skill     技能资产生命周期（list / check / bump / owner / index）
  sync      多仓 git 同步（mod 默认只读拦截）
  log       记忆回写（append-only 日志 / distill 提炼）
  report    从日志生成日报 / 周报
  selfcheck 脚本自检

通用:
  --root <dir>   工作区根（默认自动探测）
  --json         机器可读输出（audit / skill list / check 支持）
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

# ---------------------------------------------------------------- 常量与设定

SKILL_DIR_NAME = "skills"
MEMORY_REL = ".workbuddy/memory"

# 需要纳入体检的子仓（只读纪律 / 远端要求）
REPOS = {
    "base":   {"readonly": False, "need_remote": True},
    "mod":    {"readonly": True,  "need_remote": False},
    "doc":    {"readonly": False, "need_remote": True},
    "skills": {"readonly": False, "need_remote": True},
}

# 明文密钥风险模式（扫描文本类文件，命中即 P0）
SECRET_PATTERNS = [
    (r"[?&]key=[A-Z0-9]{20,}", "地图/API key 明文"),
    (r"AKID[0-9A-Za-z]{16,}", "腾讯云 SecretId"),
    (r"LTAI[0-9A-Za-z]{12,}", "阿里云 AccessKeyId"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI/LLM sk 密钥"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub Personal Token"),
]
SECRET_SKIP_DIRS = {".git", "node_modules", "uni_modules", ".workbuddy", "__pycache__"}
SECRET_TEXT_EXT = {".json", ".js", ".vue", ".md", ".py", ".yml", ".yaml", ".html", ".env", ".txt", ".sh"}

# 官方必填 frontmatter（open.workbuddy.cn/docs/skill）
REQUIRED_FIELDS = ["description", "description_zh", "description_en", "version", "author"]
# skillhub 发布必填
PUBLISH_FIELDS = ["slug", "displayName", "version"]

LEVEL_ORDER = {"P0": 0, "P1": 1, "P2": 2, "INFO": 3}


# ---------------------------------------------------------------- 基础工具

def find_root(explicit=None):
    """自动探测工作区根：同时存在 skills/ 与 .workbuddy/ 的目录。"""
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get("FOREVIP_ROOT")
    if env and os.path.isdir(env):
        return os.path.abspath(env)
    here = os.path.abspath(os.path.dirname(__file__))
    cur = here
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, SKILL_DIR_NAME)) and os.path.isdir(os.path.join(cur, ".workbuddy")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(os.path.join(here, "..", "..", ".."))


def run(cmd, cwd=None):
    """执行命令，返回 (code, stdout, stderr)。异常永不抛出。"""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:  # noqa: BLE001
        return 127, "", str(e)


def du_bytes(path):
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SECRET_SKIP_DIRS]
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.1f%s" % (n, unit)
        n /= 1024.0
    return "%.1fGB" % n


def git_info(path):
    if not os.path.isdir(os.path.join(path, ".git")):
        return {"git": False}
    branch = run(["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"])[1]
    dirty = run(["git", "-C", path, "status", "--porcelain"])[1]
    dirty_list = [l for l in dirty.splitlines() if l.strip()]
    remote = run(["git", "-C", path, "remote", "get-url", "origin"])[1]
    behind = run(["git", "-C", path, "rev-list", "--count", "HEAD..@{u}"])[1] if remote else ""
    return {
        "git": True, "branch": branch or "?", "dirty": len(dirty_list),
        "dirty_list": dirty_list[:20], "remote": remote or None,
        "behind": int(behind) if behind.isdigit() else 0,
    }


# ---------------------------------------------------------------- frontmatter

def read_frontmatter(path):
    """返回 (fields_dict, raw_front_text, error)。无 pyyaml 时用内置解析。"""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return {}, "", str(e)
    m = re.match(r"^(\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return {}, "", "no frontmatter"
    front = m.group(2)
    try:
        import yaml  # 有 pyyaml 则用严格解析
        data = yaml.safe_load(front)
        return (data if isinstance(data, dict) else {}), front, None
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        return {}, front, "yaml parse error: %s" % e
    return _mini_yaml(front), front, None


def _mini_yaml(front):
    """极简 YAML 解析：key: value，支持引号包裹与缩进续行。够用于 frontmatter。"""
    data, key = {}, None
    for line in front.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val in ("|", ">", "| -", ">"):
                data[key] = ""
                continue
            if val.startswith(("[", "{")):
                data[key] = val
            else:
                data[key] = val.strip('"').strip("'")
        elif key is not None:
            data[key] = (data.get(key, "") + " " + line.strip()).strip()
    return data


def write_frontmatter_field(path, key, value):
    """幂等写入 frontmatter 字段：已存在则跳过，返回 (changed, msg)。"""
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    eol = "\r\n" if "\r\n" in text else "\n"
    m = re.match(r"^(\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return False, "no frontmatter"
    front = m.group(2)
    if re.search(r"^%s\s*:" % re.escape(key), front, re.M):
        return False, "exists"
    lines = front.split(eol if eol in front else "\n")
    sep = eol if eol in front else "\n"
    lines.append("%s: %s" % (key, _quote(value)))
    new = "%s---%s%s%s---%s%s" % (m.group(1) or "", sep, sep.join(lines), sep, sep, text[m.end():])
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    return True, "added"


def _quote(v):
    v = str(v)
    if (": " in v) or v[:1] in "\"'*&!%@`{" or v.strip() == "":
        return '"%s"' % v.replace("\\", "\\\\").replace('"', '\\"')
    return v


def bump_patch(version):
    parts = re.findall(r"\d+", str(version or ""))
    if not parts:
        return "1.0.0"
    parts = [int(x) for x in parts][:3]
    while len(parts) < 3:
        parts.append(0)
    parts[2] += 1
    return ".".join(str(x) for x in parts)


# ---------------------------------------------------------------- audit

def cmd_audit(args):
    root = find_root(args.root)
    issues = []

    for name, cfg in REPOS.items():
        p = os.path.join(root, name)
        if not os.path.isdir(p):
            issues.append(("P1", "repo", "%s/ 不存在" % name))
            continue
        info = git_info(p)
        if not info["git"]:
            issues.append(("P1", "repo", "%s/ 未纳入 git 版本管理" % name))
            continue
        if cfg["need_remote"] and not info["remote"]:
            issues.append(("P0", "repo", "%s/ 无远端（本地唯一副本，数据丢失不可逆）" % name))
        if cfg["readonly"] and info["dirty"] > 0:
            issues.append(("P0", "readonly", "%s/ 违反只读纪律：%d 项未提交改动" % (name, info["dirty"])))
        elif info["dirty"] > 0:
            issues.append(("P1", "repo", "%s/ 有 %d 项未提交改动" % (name, info["dirty"])))
        if info["behind"] > 0:
            issues.append(("P1", "repo", "%s/ 落后远端 %d 个提交" % (name, info["behind"])))

    # 未纳入 git 的源码目录
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if not os.path.isdir(p) or d.startswith(".") or d in REPOS:
            continue
        if not os.path.isdir(os.path.join(p, ".git")):
            if any(os.path.isdir(os.path.join(p, s)) or
                   len([f for f in os.listdir(p) if f.endswith((".js", ".py", ".vue", ".json", ".html"))]) > 0
                   for s in ("src", "pages", "components")) or \
               len([f for f in os.listdir(p) if f.endswith((".js", ".py", ".vue", ".html"))]) > 0:
                issues.append(("P2", "repo", "%s/ 含源码但未纳入 git" % d))

    # 密钥明文扫描
    for sub in REPOS:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for r, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SECRET_SKIP_DIRS]
            for f in files:
                if os.path.splitext(f)[1].lower() not in SECRET_TEXT_EXT:
                    continue
                fp = os.path.join(r, f)
                try:
                    if os.path.getsize(fp) > 2 * 1024 * 1024:
                        continue
                    with open(fp, encoding="utf-8", errors="replace") as fh:
                        content = fh.read()
                except OSError:
                    continue
                for pat, label in SECRET_PATTERNS:
                    hit = re.search(pat, content)
                    if not hit:
                        continue
                    val = hit.group(0)
                    if re.search(r"xxx|your|example|placeholder|demo|test|\$\{|<", val, re.I):
                        continue  # 占位符，非真密钥
                    masked = val[:6] + "*" * max(4, len(val) - 10) + val[-4:]
                    issues.append(("P0", "secret", "%s 命中 %s（%s，已脱敏）"
                                   % (os.path.relpath(fp, root), label, masked)))
                    break

    # 残留文件（.DS_Store 聚合计数，避免刷屏）
    ds_count, ds_dirs = 0, []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SECRET_SKIP_DIRS]
        for f in files:
            if f == ".DS_Store":
                ds_count += 1
                ds_dirs.append(os.path.relpath(r, root))
        for d in list(dirs):
            if re.search(r"\.workbbuddy$", d):
                issues.append(("P2", "residue", "%s（拼写错误目录）" % os.path.relpath(os.path.join(r, d), root)))
    if ds_count:
        sample = "，例：" + "、".join(ds_dirs[:3]) if ds_dirs else ""
        issues.append(("P2", "residue", ".DS_Store 共 %d 个%s（可 `find . -name .DS_Store -delete` 清理）"
                       % (ds_count, sample)))

    # 磁盘
    big = []
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p) and not d.startswith(".git"):
            size = du_bytes(p)
            if size > 100 * 1024 * 1024:
                big.append((d, size))
                issues.append(("P2", "disk", "%s/ 占用 %s（建议清理策略）" % (d, human(size))))

    # README 漂移：README 中出现但工作区不存在的顶层路径
    readme = os.path.join(root, "README.md")
    if os.path.isfile(readme):
        with open(readme, encoding="utf-8", errors="replace") as f:
            content = f.read()
        # 仅匹配「顶层相对路径引用」：前缀不能是 / 或字母数字，避免 doc/web/ 里的 web/ 被误判
        for token in set(re.findall(r"(?:^|[^\w/.\-`])([a-zA-Z][\w-]{2,20})/(?:\s|$|`)", content)):
            if token in SECRET_SKIP_DIRS:
                continue
            if not os.path.isdir(os.path.join(root, token)):
                issues.append(("P1", "doc", "README 引用了不存在的目录 %s/" % token))

    issues.sort(key=lambda x: (LEVEL_ORDER.get(x[0], 9), x[1]))
    result = {"root": root, "issues": [{"level": a, "cat": b, "msg": c} for a, b, c in issues],
              "counts": {lv: sum(1 for i in issues if i[0] == lv) for lv in ("P0", "P1", "P2")}}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("工作区体检 · %s" % root)
        print("时间: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("-" * 68)
        if not issues:
            print("无异常项。")
        for lv, cat, msg in issues:
            print("[%s] %-8s %s" % (lv, cat, msg))
        print("-" * 68)
        print("合计 P0=%d P1=%d P2=%d" % (result["counts"]["P0"], result["counts"]["P1"], result["counts"]["P2"]))
    return 1 if result["counts"]["P0"] else 0


# ---------------------------------------------------------------- skill

def iter_skills(root):
    sroot = os.path.join(root, SKILL_DIR_NAME)
    if not os.path.isdir(sroot):
        return []
    out = []
    for d in sorted(os.listdir(sroot)):
        p = os.path.join(sroot, d)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
            out.append((d, os.path.join(p, "SKILL.md")))
    return out


def cmd_skill(args):
    root = find_root(args.root)
    if args.action == "list":
        rows = []
        for name, path in iter_skills(root):
            fields, _, err = read_frontmatter(path)
            miss = [f for f in REQUIRED_FIELDS if not fields.get(f)]
            miss_pub = [f for f in PUBLISH_FIELDS if not fields.get(f)]
            rows.append({
                "name": name, "version": fields.get("version", "-"),
                "owner": fields.get("owner", "未归类"),
                "author": fields.get("author", "-"),
                "missing": miss, "missing_publish": miss_pub, "error": err,
            })
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print("%-32s %-8s %-8s %s" % ("技能", "版本", "归属", "缺失"))
            print("-" * 68)
            for r in rows:
                flag = "OK" if not r["missing"] and not r["error"] else "!!"
                miss = ",".join(r["missing"] + r["missing_publish"]) or "-"
                if r["error"]:
                    miss = r["error"]
                print("%-32s %-8s %-8s %s %s" % (r["name"], r["version"], r["owner"], flag, miss))
        return 0

    if args.action == "check":
        target = args.target
        path = os.path.join(root, SKILL_DIR_NAME, target, "SKILL.md")
        if not os.path.isfile(path):
            print("未找到 SKILL.md: %s" % path)
            return 2
        fields, _, err = read_frontmatter(path)
        problems = []
        if err:
            problems.append(("P0", "frontmatter 解析失败: %s" % err))
        for f in REQUIRED_FIELDS:
            if not fields.get(f):
                problems.append(("P0", "缺必填字段 %s" % f))
        for f in PUBLISH_FIELDS:
            if not fields.get(f):
                problems.append(("P1", "缺 skillhub 发布字段 %s（slug 需小写连字符，displayName 需驼峰）" % f))
        if not fields.get("owner"):
            problems.append(("P1", "未标注归属 owner: personal|team"))
        # 单层子目录检查
        sdir = os.path.dirname(path)
        for r, dirs, _ in os.walk(sdir):
            depth = os.path.relpath(r, sdir)
            if depth.count(os.sep) >= 1:
                problems.append(("P0", "存在二级子目录 %s（开放平台不允许）" % depth))
            break
        # 尾部反馈声明
        with open(path, encoding="utf-8", errors="replace") as f:
            body = f.read()
        if "## 反馈" not in body:
            problems.append(("P2", "缺少尾部「## 反馈」声明"))
        # 运行时数据落点（须剥离代码块：fence 内是命令行路径，按仓库惯例不动）
        prose = re.sub(r"```.*?```", "", body, flags=re.S)
        if re.search(r"SKILL_DIR|skills/%s/" % re.escape(target), prose):
            problems.append(("P2", "疑似把运行时数据写入安装目录（应落用户目录）"))
        if args.json:
            print(json.dumps({"skill": target, "problems": [{"level": a, "msg": b} for a, b in problems]},
                             ensure_ascii=False, indent=2))
        else:
            print("发布前自检 · %s" % target)
            print("-" * 68)
            if not problems:
                print("全部通过。可发布。")
            for lv, msg in sorted(problems, key=lambda x: LEVEL_ORDER.get(x[0], 9)):
                print("[%s] %s" % (lv, msg))
        return 1 if any(p[0] == "P0" for p in problems) else 0

    if args.action == "bump":
        path = os.path.join(root, SKILL_DIR_NAME, args.target, "SKILL.md")
        if not os.path.isfile(path):
            print("未找到 SKILL.md: %s" % path)
            return 2
        fields, _, _ = read_frontmatter(path)
        old = fields.get("version", "1.0.0")
        new = bump_patch(old)
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        text2, n = re.subn(r"(^version:\s*)[\d.]+", r"\g<1>%s" % new, text, count=1, flags=re.M)
        if n == 0:
            print("未匹配到 version 行，未改动")
            return 2
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text2)
        print("version: %s -> %s (PATCH)" % (old, new))
        return 0

    if args.action == "owner":
        path = os.path.join(root, SKILL_DIR_NAME, args.target, "SKILL.md")
        changed, msg = write_frontmatter_field(path, "owner", args.value)
        print("%s owner=%s -> %s" % (args.target, args.value, msg))
        return 0

    if args.action == "index":
        rows = []
        for name, path in iter_skills(root):
            fields, _, _ = read_frontmatter(path)
            desc = str(fields.get("description_zh") or fields.get("description") or "").replace("\n", " ")
            desc = desc[:60] + ("…" if len(desc) > 60 else "")
            rows.append((name, desc))
        print("| 技能 | 说明 |")
        print("|------|------|")
        for n, d in rows:
            print("| %s | %s |" % (n, d))
        print("\n共 %d 个技能。" % len(rows))
        return 0

    return 2


# ---------------------------------------------------------------- sync

def cmd_sync(args):
    root = find_root(args.root)
    results = []
    targets = [args.repo] if args.repo else list(REPOS.keys())
    for name in targets:
        p = os.path.join(root, name)
        cfg = REPOS.get(name, {"readonly": False})
        if not os.path.isdir(os.path.join(p, ".git")):
            results.append((name, "SKIP", "非 git 仓库"))
            continue
        if cfg.get("readonly") and not args.force:
            results.append((name, "BLOCK", "只读仓库，需 --force 才同步"))
            continue
        if cfg.get("readonly") and args.force:
            results.append((name, "BLOCK", "只读仓库，拒绝同步（纪律）"))
            continue
        code, out, err = run(["git", "-C", p, "status", "--porcelain"])
        if not out.strip():
            results.append((name, "SKIP", "无改动"))
            continue
        run(["git", "-C", p, "add", "-A"])
        msg = args.message or "chore: 自动化同步 %s" % datetime.now().strftime("%Y-%m-%d %H:%M")
        c, _, e = run(["git", "-C", p, "commit", "-m", msg])
        if c != 0:
            results.append((name, "FAIL", "commit 失败: %s" % (e or "无改动")))
            continue
        if args.no_push:
            results.append((name, "OK", "已提交（未 push）"))
            continue
        c, _, e = run(["git", "-C", p, "push"])
        results.append((name, "OK" if c == 0 else "FAIL", "已 push" if c == 0 else "push 失败: %s" % e))
    for n, s, m in results:
        print("%-8s %-6s %s" % (n, s, m))
    return 0


# ---------------------------------------------------------------- log

def cmd_log(args):
    root = find_root(args.root)
    mdir = os.path.join(root, MEMORY_REL)
    os.makedirs(mdir, exist_ok=True)
    if args.action == "append":
        day = args.date or datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(mdir, "%s.md" % day)
        content = args.text
        if not content:
            content = sys.stdin.read()
        if not content.strip():
            print("无内容，未写入")
            return 2
        header = "" if os.path.exists(path) else "# %s 工作日志\n\n" % day
        with open(path, "a", encoding="utf-8") as f:
            if header:
                f.write(header)
            f.write("\n## %s · %s\n\n%s\n" % (args.title or "记录",
                                              datetime.now().strftime("%H:%M"), content.strip()))
        print("已追加 -> %s" % os.path.relpath(path, root))
        return 0
    if args.action == "distill":
        cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        olds = sorted(f for f in os.listdir(mdir) if re.match(r"^\d{4}-\d{2}-\d{2}\.md$", f) and f[:10] < cutoff)
        print("待提炼日志（早于 %s）：%d 份" % (cutoff, len(olds)))
        for f in olds:
            print("  - %s" % f)
        print("\n提炼动作交由 Agent 执行：读取上述文件 → 按主题归并 → 追加到 MEMORY.md → 确认后删除原文件。")
        print("本脚本不自动删除任何日志。")
        return 0
    if args.action == "today":
        day = args.date or datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(mdir, "%s.md" % day)
        if not os.path.exists(path):
            print("今日日志不存在: %s" % path)
            return 1
        with open(path, encoding="utf-8") as f:
            print(f.read())
        return 0
    return 2


# ---------------------------------------------------------------- report

def cmd_report(args):
    root = find_root(args.root)
    mdir = os.path.join(root, MEMORY_REL)
    if not os.path.isdir(mdir):
        print("无记忆目录")
        return 1
    days = 1 if args.range == "daily" else 7
    files = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        p = os.path.join(mdir, "%s.md" % d)
        if os.path.exists(p):
            files.append(p)
    if not files:
        print("近 %d 天无日志" % days)
        return 1
    print("# 工作%s报 · %s\n" % ("日" if days == 1 else "周", datetime.now().strftime("%Y-%m-%d")))
    for p in files:
        with open(p, encoding="utf-8") as f:
            lines = [l.rstrip() for l in f if l.startswith(("# ", "## ", "### "))]
        if not lines:
            continue
        print("## %s" % os.path.basename(p)[:-3])
        for l in lines[1:]:
            print("  %s" % l)
        print()
    return 0


# ---------------------------------------------------------------- selfcheck

def cmd_selfcheck(args):
    root = find_root(args.root)
    ok = True
    print("工作区根: %s" % root)
    for d in REPOS:
        p = os.path.join(root, d)
        print("  %-8s %s" % (d, "OK" if os.path.isdir(p) else "缺失"))
        if not os.path.isdir(p):
            ok = False
    n = len(iter_skills(root))
    print("  技能数: %d" % n)
    try:
        import yaml  # noqa: F401
        print("  pyyaml: 可用（严格解析模式）")
    except ImportError:
        print("  pyyaml: 不可用（内置简易解析，够用；装 pyyaml 可切严格模式）")
    print("  python: %s" % sys.version.split()[0])
    return 0 if ok else 1


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="fore.vip 工作区自动化中枢")
    ap.add_argument("--root", help="工作区根路径")
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("audit", help="工作区体检")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_audit)

    s = sub.add_parser("skill", help="技能资产生命周期")
    s.add_argument("action", choices=["list", "check", "bump", "owner", "index"])
    s.add_argument("target", nargs="?")
    s.add_argument("value", nargs="?")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_skill)

    y = sub.add_parser("sync", help="多仓 git 同步")
    y.add_argument("--repo", help="仅同步指定仓库")
    y.add_argument("--message", "-m")
    y.add_argument("--no-push", action="store_true")
    y.add_argument("--force", action="store_true", help="尝试同步只读仓库（仍会被拒绝）")
    y.set_defaults(func=cmd_sync)

    l = sub.add_parser("log", help="记忆回写")
    l.add_argument("action", choices=["append", "distill", "today"])
    l.add_argument("--title", default="记录")
    l.add_argument("--text", help="内容；不传则从 stdin 读取")
    l.add_argument("--date")
    l.add_argument("--days", type=int, default=30)
    l.set_defaults(func=cmd_log)

    r = sub.add_parser("report", help="日报/周报")
    r.add_argument("range", choices=["daily", "weekly"])
    r.set_defaults(func=cmd_report)

    c = sub.add_parser("selfcheck", help="脚本自检")
    c.set_defaults(func=cmd_selfcheck)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        ap.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
