#!/usr/bin/env python3
"""通用 references 库自检闸门。

用法：
    python3 scripts/check_common_refs.py
    python3 scripts/check_common_refs.py --root fore.vip/skills=/path/to/skills

退出码：0 = PASS，1 = FAIL。跨仓统计依赖同机存在另外两个仓库，
缺失时给 WARN 并跳过 STATS 比对，不影响本库自身检查。
"""

import argparse
import hashlib
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

COMMON = Path(__file__).resolve().parents[1]
REFS = COMMON / "references"
README = COMMON / "README.md"
MAPPING = COMMON / "mapping.md"

EXPECTED_DOCS = [
    "compliance.md",
    "skill-structure.md",
    "source-grading.md",
    "report-template.md",
    "delivery-gates.md",
    "visual-style.md",
]

DEFAULT_ROOTS = [
    ("fore.vip/skills", Path.home() / "git" / "fore.vip" / "skills"),
    ("auto/skills", Path.home() / "git" / "auto" / "skills"),
    ("auto/experts", Path.home() / "git" / "auto" / "experts"),
]

PRIVATE_PATTERNS = [
    (r"wxc[0-9A-Za-z]{10,}", "AppID"),
    (r"sk-[A-Za-z0-9]{16,}", "密钥"),
    (r"/Users/|/home/", "本机绝对路径"),
    (r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", "私钥"),
    (r"mcp\.fore\.vip|uniCloud|ossutil", "内部端点或部署实现"),
    (r"password\s*[:=]\s*\S+", "明文口令"),
]


class Report:
    def __init__(self):
        self.items = []

    def add(self, ok, label, detail=""):
        self.items.append((ok, label, detail))

    def warn(self, label, detail=""):
        self.items.append((None, label, detail))

    def render(self):
        fails = 0
        warns = 0
        for ok, label, detail in self.items:
            tag = "PASS" if ok is True else ("WARN" if ok is None else "FAIL")
            if ok is False:
                fails += 1
            if ok is None:
                warns += 1
            line = "[{}] {}".format(tag, label)
            if detail:
                line += " -- " + detail
            print(line)
        passed = sum(1 for ok, _, _ in self.items if ok is True)
        verdict = "FAIL" if fails else "PASS"
        print("RESULT {} ({} pass, {} fail, {} warn)".format(
            verdict, passed, fails, warns))
        return 1 if fails else 0


def check_library(rep):
    if not REFS.is_dir():
        rep.add(False, "references/ 存在", str(REFS))
        return
    subdirs = [p.name for p in REFS.iterdir() if p.is_dir()]
    rep.add(not subdirs, "references/ 单层", "发现子目录: {}".format(subdirs) if subdirs else "")

    files = sorted(p for p in REFS.iterdir() if p.is_file())
    names = sorted(p.name for p in files)
    rep.add(names == sorted(EXPECTED_DOCS), "文档集合与期望清单一致",
            "actual={} expected={}".format(names, sorted(EXPECTED_DOCS)))
    non_md = [p.name for p in files if p.suffix != ".md"]
    rep.add(not non_md, "references/ 仅含 Markdown", str(non_md))

    readme = README.read_text(encoding="utf-8") if README.exists() else ""
    missing_in_readme = [n for n in EXPECTED_DOCS if n not in readme]
    rep.add(bool(readme) and not missing_in_readme, "README 文件清单覆盖全部文档",
            str(missing_in_readme))

    for name in EXPECTED_DOCS:
        p = REFS / name
        if not p.exists():
            rep.add(False, "{} 存在".format(name))
            continue
        raw = p.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        issues = []
        if raw.startswith(b"\xef\xbb\xbf"):
            issues.append("BOM")
        if b"\r\n" in raw:
            issues.append("CRLF")
        if not text.startswith("# "):
            issues.append("缺一级标题")
        if "来源：`_common/references/" not in text:
            issues.append("缺来源标注")
        for pattern, label in PRIVATE_PATTERNS:
            if re.search(pattern, text):
                issues.append("私有信息: " + label)
        rep.add(not issues, "{} 格式与内容洁净".format(name), "; ".join(issues))


def parse_stats(text):
    m = re.search(r"<!--\s*STATS\s+([^>]+?)\s*-->", text)
    if not m:
        return None
    result = {}
    for token in m.group(1).split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        try:
            result[key] = int(value)
        except ValueError:
            continue
    return result


def collect(roots):
    files = []
    missing = []
    for label, root in roots:
        if not root.is_dir():
            missing.append(label)
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            parts = set(p.relative_to(root).parts)
            if "references" not in parts:
                continue
            if parts & {"_common", ".git", "__pycache__", "node_modules"}:
                continue
            files.append((label, p))
    return files, missing


def check_stats(rep, roots):
    if not MAPPING.exists():
        rep.add(False, "mapping.md 存在")
        return
    declared = parse_stats(MAPPING.read_text(encoding="utf-8"))
    if declared is None:
        rep.add(False, "mapping.md 含 STATS 标记")
        return
    rep.add(True, "mapping.md 含 STATS 标记")

    files, missing = collect(roots)
    if missing:
        rep.warn("跨仓盘点跳过", "缺少根目录: {}；可用 --root 指定".format(", ".join(missing)))
        return

    per_root = Counter(label for label, _ in files)
    by_hash = defaultdict(list)
    for label, p in files:
        digest = hashlib.md5(p.read_bytes()).hexdigest()
        by_hash[digest].append(label)
    dup = {h: labels for h, labels in by_hash.items() if len(labels) > 1}

    actual = {
        "total": len(files),
        "dup_groups": len(dup),
        "dup_files": sum(len(v) for v in dup.values()),
        "cross_root_groups": sum(1 for v in dup.values() if len(set(v)) > 1),
    }
    for label, _ in roots:
        actual[label] = per_root.get(label, 0)

    for key, value in sorted(actual.items()):
        got = declared.get(key)
        rep.add(got == value, "STATS {} 与实测一致".format(key),
                "declared={} actual={}".format(got, value))
    extra = sorted(set(declared) - set(actual))
    rep.add(not extra, "STATS 无多余键", str(extra))


def main():
    parser = argparse.ArgumentParser(description="通用 references 库自检")
    parser.add_argument("--root", action="append", default=[],
                        help="覆盖盘点根目录，格式 LABEL=PATH，可重复")
    args = parser.parse_args()

    roots = []
    if args.root:
        for spec in args.root:
            if "=" not in spec:
                print("[FAIL] --root 格式应为 LABEL=PATH: {}".format(spec))
                return 1
            label, path = spec.split("=", 1)
            roots.append((label, Path(path).expanduser().resolve()))
    else:
        roots = DEFAULT_ROOTS

    rep = Report()
    check_library(rep)
    check_stats(rep, roots)
    return rep.render()


if __name__ == "__main__":
    sys.exit(main())
