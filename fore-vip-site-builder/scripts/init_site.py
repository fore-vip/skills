#!/usr/bin/env python3
"""init_site.py — 官网脚手架生成器（fore-vip-site-builder）

把 templates/ 下的骨架组装成一个可直接发布的静态站点目录：
  页面（index / features）、主题 CSS、SEO 辅料（robots.txt / sitemap.xml）、
  发布脚本（deploy.sh）+ 两道发布闸门（sync_sitemap.py / check_assets.py）、.gitignore。

纯 Python 3 标准库，零第三方依赖。

用法：
  python3 init_site.py --name "前凌智选" --domain example.com \
      --style noir --host oss --bucket my-site --out ./site

  # 自定义品牌色（会自动校正到 WCAG AA 对比度）
  python3 init_site.py --name X --domain x.com --brand "#e53e3e" --out ./site

  # 已存在非空目录时必须显式确认
  python3 init_site.py --name X --domain x.com --out ./site --force

  # 一次性注入全部文案（推荐：先 init 看结构，再用 copy.json 重跑）
  python3 init_site.py --name X --domain x.com --out ./site --copy copy.json

可选：
  --style   noir | paper | brand            默认 paper
  --host    oss | vercel | none             默认 oss
  --bucket  OSS 桶名（--host oss 时用于 deploy.sh）
  --email   联系邮箱
  --icp     备案号（如 "京ICP备2026000000号-1"），填了才生成页脚备案链接
  --lang    zh-CN | en                      默认 zh-CN
  --tagline 一句话价值主张（不给则写入待填标记）
  --desc    meta description（不给则写入待填标记）
  --copy    文案 JSON：{ 占位符名: 文案 }，键名见 --dump-keys

退出码：0 = 生成成功（含自检通过）；1 = 参数错误或生成失败；2 = 生成成功但自检未过。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
TPL_DIR = SKILL_DIR / "templates"
AUDIT = HERE / "seo_audit.py"

STYLES = ("noir", "paper", "brand")
THEME_BG = {"noir": "#0b0d10", "paper": "#ffffff", "brand": "#ffffff"}
THEME_FG = {"noir": "#0b0d10", "paper": "#ffffff", "brand": "#ffffff"}
DEFAULT_BRAND = {"noir": "#ff6b6b", "paper": "#14171a", "brand": "#d92d20"}
MARK = "【待填：%s】"

# 页面引用的静态资源（由用户自行补齐，deploy 闸门会检查）
REQUIRED_ASSETS = [
    "favicon.ico", "apple-touch-icon.png", "logo-mark.png",
    "og-cover.png", "logo.png",
]

# ── 颜色工具 ────────────────────────────────────────────────────────────


def _lin(v: float) -> float:
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_hex(s: str) -> tuple[int, int, int]:
    s = s.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{3}", s):
        s = "".join(c * 2 for c in s)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s):
        raise ValueError(f"颜色格式不合法：{s}（用 #rgb 或 #rrggbb）")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def _toward(rgb: tuple[int, int, int], target: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(c + (target[c_i] - c) * t) for c_i, c in enumerate(rgb))  # type: ignore[return-value]


def fit_contrast(rgb: tuple[int, int, int], other: tuple[int, int, int], minimum: float = 4.5) -> tuple[int, int, int]:
    """把 rgb 朝黑或白方向推进，直到与 other 的对比度 >= minimum。保持色相尽量不变。"""
    if contrast(rgb, other) >= minimum:
        return rgb
    for target in ((0, 0, 0), (255, 255, 255)):
        t = 0.0
        while t <= 1.0001:
            cand = _toward(rgb, target, t)
            if contrast(cand, other) >= minimum:
                return cand
            t += 0.05
    return max(((0, 0, 0), (255, 255, 255)), key=lambda c: contrast(c, other))


# ── 文案默认值 ──────────────────────────────────────────────────────────


def build_values(a: argparse.Namespace) -> dict[str, str]:
    name = a.name
    domain = a.domain.strip().rstrip("/")
    origin = domain if domain.startswith(("http://", "https://")) else f"https://{domain}"
    home = origin + "/"
    today = dt.date.today().isoformat()
    year = today[:4]

    tagline = a.tagline or (MARK % "一句话价值主张，例如「让全自动化成为可能」")
    desc = a.desc or (MARK % "站点描述，70–150 字，说清提供什么、给谁、有何不同")
    title_suffix = a.tagline if a.tagline else "官网"

    icp_html = ""
    if a.icp:
        icp_html = (
            '<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">'
            f"{a.icp}</a>"
        )

    email = a.email or (MARK % "联系邮箱")

    v = {
        # 基础
        "LANG": a.lang,
        "OG_LOCALE": "zh_CN" if a.lang.startswith("zh") else a.lang.replace("-", "_"),
        "DOMAIN": domain,
        "HOME_URL": home,
        "CANONICAL": home,
        "OG_IMAGE": f"{origin}/og-cover.png",
        "SITE_NAME": name,
        "TITLE": f"{name} · {title_suffix}",
        "DESC": desc,
        "YEAR": year,
        "TODAY": today,
        "EMAIL": email,
        "ICP_HTML": icp_html,
        # 首页文案
        "TAGLINE": tagline,
        "LEAD": MARK % "2 行补充说明，讲清给谁解决什么问题",
        "EYEBROW": MARK % "定位标签，如「AI 环境自动化」",
        "CTA_TEXT": "联系我们",
        "HERO_NOTE": "",
        "VALUE_TITLE": MARK % "为什么选我们（区块标题）",
        "VALUE_LEAD": MARK % "这一段总起，1–2 句",
        "V1_TITLE": MARK % "卖点一标题",
        "V1_BODY": MARK % "卖点一句话解释，40 字内",
        "V2_TITLE": MARK % "卖点二标题",
        "V2_BODY": MARK % "卖点一句话解释，40 字内",
        "V3_TITLE": MARK % "卖点三标题",
        "V3_BODY": MARK % "卖点一句话解释，40 字内",
        "STEP1": MARK % "第一步用户需要做什么",
        "STEP2": MARK % "第二步能得到什么",
        "STEP3": MARK % "第三步如何持续",
        "PROOF_TITLE": MARK % "背书区块标题",
        "N1": MARK % "数字", "N1_LABEL": MARK % "指标名",
        "N2": MARK % "数字", "N2_LABEL": MARK % "指标名",
        "N3": MARK % "数字", "N3_LABEL": MARK % "指标名",
        "N4": MARK % "数字", "N4_LABEL": MARK % "指标名",
        "PROOF_NOTE": MARK % "数据口径与时间范围说明（没有数据就删掉整个区块）",
        "Q1": MARK % "问题一", "A1": MARK % "问题一答案",
        "Q2": MARK % "问题二", "A2": MARK % "问题二答案",
        "Q3": MARK % "问题三", "A3": MARK % "问题三答案",
        "Q4": MARK % "问题四", "A4": MARK % "问题四答案",
        "CTA_TITLE": MARK % "转化区标题，如「聊聊你的需求」",
        "CTA_LEAD": MARK % "转化区一句说明",
        "CTA_NOTE": MARK % "补充说明（可留空，留空则删掉该行）",
        "FOOTER_DESC": MARK % "页脚一句话简介",
        "CONTACT_EXTRA": MARK % "微信号 / 电话",
        # 功能页
        "F_NAME": f"{name}服务",
        "F_TITLE": f"{MARK % '功能页关键词'} · {name}",
        "F_DESC": MARK % "功能页描述，说清这项能力解决什么问题、给谁用，70–150 字",
        "F_CANONICAL": f"{origin}/features.html",
        "F_H1": MARK % "功能页主标题",
        "F_LEAD": MARK % "功能页一句话说明",
        "F_PROBLEM_TITLE": MARK % "问题区块标题",
        "P1": MARK % "现状痛点一", "P2": MARK % "现状痛点二", "P3": MARK % "现状痛点三",
        "G1": MARK % "改善后一", "G2": MARK % "改善后二", "G3": MARK % "改善后三",
        "S1_TITLE": MARK % "步骤一标题", "S1_BODY": MARK % "步骤一说明",
        "S2_TITLE": MARK % "步骤二标题", "S2_BODY": MARK % "步骤二说明",
        "S3_TITLE": MARK % "步骤三标题", "S3_BODY": MARK % "步骤三说明",
        "F_SPEC_TITLE": MARK % "能力明细区块标题",
        "SP1_TITLE": MARK % "能力一", "SP1_BODY": MARK % "能力一说明",
        "SP2_TITLE": MARK % "能力二", "SP2_BODY": MARK % "能力二说明",
        "SP3_TITLE": MARK % "能力三", "SP3_BODY": MARK % "能力三说明",
        "FQ1": MARK % "功能页问题一", "FA1": MARK % "问题一答案",
        "FQ2": MARK % "功能页问题二", "FA2": MARK % "问题二答案",
        "FQ3": MARK % "功能页问题三", "FA3": MARK % "问题三答案",
        "AREA_SERVED": "中国",
        "THEME_COLOR": "",
    }
    return v


# ── 生成 ────────────────────────────────────────────────────────────────


def render(text: str, values: dict[str, str]) -> str:
    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in values:
            raise KeyError(f"模板占位符 {{{{{key}}}}} 无对应值")
        return values[key]

    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", sub, text)


def set_var(css: str, var: str, value: str) -> str:
    return re.sub(rf"(--{var}\s*:\s*)[^;]+;", rf"\g<1>{value};", css, count=1)


ROBOTS = """User-agent: *
Allow: /

Sitemap: {origin}/sitemap.xml
"""

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{origin}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{origin}/features.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
"""

GITIGNORE = """.DS_Store
*.log
.env
.vercel
node_modules/
__pycache__/
"""

DEPLOY_OSS = """#!/usr/bin/env bash
# deploy.sh — 增量发布到阿里云 OSS，并做两道 fail-closed 闸门
#
#   ./deploy.sh                 增量发布：只上传新增/变动的文件，不删除线上对象
#   ./deploy.sh -n              预演：只列出将要执行的动作
#   ./deploy.sh --rm <对象路径> 显式删除线上单个对象
#   ./deploy.sh --check         只跑闸门，不发布
#
# 为什么没有镜像删除：`sync --delete` 与 `--exclude` 组合会让删除集计算失真，
# 既不可靠又危险。删除一律显式指定对象。
set -euo pipefail

BASE="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
BUCKET="oss://{bucket}"
OSSUTIL="${{OSSUTIL:-$HOME/.local/bin/ossutil}}"
PY="${{PYTHON:-python3}}"
ORIGIN="{origin}"

if [ ! -x "$OSSUTIL" ]; then
  echo "找不到可执行的 ossutil：$OSSUTIL" >&2
  echo "安装见 skills/fore-vip-oss/references/providers.md" >&2
  exit 1
fi

ACTION=deploy; DRY=(); TARGET=""
while [ $# -gt 0 ]; do
  case "$1" in
    -n|--dry-run) DRY+=(--dry-run) ;;
    --check)      ACTION=check ;;
    --rm)         ACTION=rm; shift; TARGET="${{1:-}}" ;;
    -h|--help)    sed -n '2,10p' "$0" | sed 's/^# \\{{0,1\\}}//'; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 1 ;;
  esac
  shift
done

# ── 闸门 1：收录页面与 sitemap.xml 必须同步 ──────────────
if [ -f "$BASE/sync_sitemap.py" ]; then
  if ! "$PY" "$BASE/sync_sitemap.py" --check; then
    echo "" >&2
    echo "发布中止：sitemap.xml 未与页面同步。自动回写：python3 sync_sitemap.py" >&2
    exit 1
  fi
fi

# ── 闸门 2：页面引用的本地资源必须都存在（防线上破图） ──
if [ -f "$BASE/check_assets.py" ]; then
  if ! "$PY" "$BASE/check_assets.py" --quiet; then
    echo "" >&2
    echo "发布中止：存在断链引用。把缺失资源放进站点目录后重跑。" >&2
    exit 1
  fi
fi

[ "$ACTION" = check ] && {{ echo "闸门通过，未发布。"; exit 0; }}

if [ "$ACTION" = rm ]; then
  [ -z "$TARGET" ] && {{ echo "用法：./deploy.sh --rm <对象路径>" >&2; exit 1; }}
  TARGET="${{TARGET#/}}"
  echo "▶ 删除线上对象：$BUCKET/$TARGET"
  "$OSSUTIL" rm "$BUCKET/$TARGET" --force ${{DRY[@]+"${{DRY[@]}}"}}
  exit 0
fi

# 防误清空：站点根必须有 index.html
[ -f "$BASE/index.html" ] || {{ echo "预检失败：index.html 不存在，已中止。" >&2; exit 1; }}

NOTE=""; [ ${{#DRY[@]}} -gt 0 ] && NOTE="  [预演，不写入]"
echo "▶ 增量发布$NOTE：$BASE/  ->  $BUCKET/"
"$OSSUTIL" cp -r -u "$BASE/" "$BUCKET/" --force \\
  --exclude ".DS_Store" --exclude "**/.DS_Store" --exclude ".git/**" \\
  --exclude "deploy.sh" --exclude "sync_sitemap.py" --exclude "check_assets.py" \\
  --exclude "*.py" --exclude ".gitignore" ${{DRY[@]+"${{DRY[@]}}"}}

if [ ${{#DRY[@]}} -eq 0 ]; then
  echo
  printf '线上探针：%s  ->  HTTP %s\\n' "$ORIGIN/" \\
    "$(curl -s -o /dev/null -w '%{{http_code}}' -L --max-time 15 "$ORIGIN/")"
fi
"""

DEPLOY_VERCEL = """#!/usr/bin/env bash
# deploy.sh — 发布到 Vercel，并做两道 fail-closed 闸门
#
#   ./deploy.sh        闸门通过后执行 vercel --prod
#   ./deploy.sh --check 只跑闸门，不发布
set -euo pipefail

BASE="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PY="${{PYTHON:-python3}}"
ORIGIN="{origin}"

if [ -f "$BASE/sync_sitemap.py" ]; then
  "$PY" "$BASE/sync_sitemap.py" --check || {{ echo "发布中止：sitemap 未同步。" >&2; exit 1; }}
fi
if [ -f "$BASE/check_assets.py" ]; then
  "$PY" "$BASE/check_assets.py" --quiet || {{ echo "发布中止：存在断链引用。" >&2; exit 1; }}
fi
[ "${{1:-}}" = "--check" ] && {{ echo "闸门通过，未发布。"; exit 0; }}

command -v vercel >/dev/null || {{ echo "未安装 vercel CLI：npm i -g vercel" >&2; exit 1; }}
vercel --prod

echo
printf '线上探针：%s  ->  HTTP %s\\n' "$ORIGIN/" \\
  "$(curl -s -o /dev/null -w '%{{http_code}}' -L --max-time 20 "$ORIGIN/")"
"""

DEPLOY_NONE = """#!/usr/bin/env bash
# deploy.sh — 仅做发布前闸门（托管方式未确定时使用）
set -euo pipefail
BASE="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
PY="${PYTHON:-python3}"
"$PY" "$BASE/sync_sitemap.py" --check
"$PY" "$BASE/check_assets.py" --quiet
echo "闸门通过。请在确定托管方式后替换本脚本（见 references/hosting.md）。"
echo "目标站点：{origin}/"
"""

SYNC_SITEMAP = '''#!/usr/bin/env python3
"""sync_sitemap.py — 让 sitemap.xml 与站点实际收录页面保持一致（发布闸门）

  python3 sync_sitemap.py          按站点目录回写 sitemap.xml
  python3 sync_sitemap.py --check  只校验不改文件（不一致则退出码 1）

收录范围：站点根目录下的 *.html（递归），排除以 `_` 开头的文件与目录。
判定：新增页面缺 <url> → 差异；<loc> 无对应文件 → 差异；
      有对应文件但 <lastmod> 早于文件 mtime → 差异。
纯标准库，零依赖。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SITEMAP = BASE / "sitemap.xml"
ORIGIN = "{origin}"


def pages() -> list[Path]:
    out = []
    for p in sorted(BASE.rglob("*.html")):
        rel = p.relative_to(BASE)
        if any(part.startswith("_") or part.startswith(".") for part in rel.parts):
            continue
        out.append(p)
    return out


def loc_of(p: Path) -> str:
    rel = p.relative_to(BASE).as_posix()
    return ORIGIN + "/" if rel == "index.html" else f"{{ORIGIN}}/{{rel}}"


def parse() -> dict[str, str]:
    if not SITEMAP.exists():
        return {{}}
    text = SITEMAP.read_text(encoding="utf-8")
    found = {{}}
    for loc, lastmod in re.findall(
        r"<loc>(.*?)</loc>\\s*(?:<lastmod>(.*?)</lastmod>)?", text, re.S
    ):
        found[loc.strip()] = (lastmod or "").strip()
    return found


def write(entries: list[tuple[str, str]]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in entries:
        pri = "1.0" if loc.rstrip("/") == ORIGIN else "0.8"
        freq = "weekly" if pri == "1.0" else "monthly"
        lines += [
            "  <url>",
            f"    <loc>{{loc}}</loc>",
            f"    <lastmod>{{lastmod}}</lastmod>",
            f"    <changefreq>{{freq}}</changefreq>",
            f"    <priority>{{pri}}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    SITEMAP.write_text("\\n".join(lines) + "\\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验，不改文件")
    a = ap.parse_args()

    existing = parse()
    want: list[tuple[str, str]] = []
    problems: list[str] = []
    for p in pages():
        loc = loc_of(p)
        mtime = dt.date.fromtimestamp(p.stat().st_mtime).isoformat()
        want.append((loc, mtime))
        old = existing.get(loc)
        if old is None:
            problems.append(f"缺少 <url>：{{loc}}")
        elif old and old < mtime:
            problems.append(f"<lastmod> 过期：{{loc}}  声明 {{old}} < 文件 {{mtime}}")

    known = {{loc for loc, _ in want}}
    for loc in existing:
        if loc not in known:
            problems.append(f"多余 <url>（无对应文件）：{{loc}}")

    if problems:
        for x in problems:
            print("  ✗ " + x)
        if not a.check:
            write(want)
            print(f"\\n已回写 {{SITEMAP.name}}：{{len(want)}} 条")
            return 0
        print("\\nsitemap.xml 与页面不一致（--check）")
        return 1

    print(f"sitemap.xml 与页面一致：{{len(want)}} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

CHECK_ASSETS = '''#!/usr/bin/env python3
"""check_assets.py — 检查页面引用的本地资源是否都存在（发布闸门，防线上破图）

  python3 check_assets.py            报告断链，退出码 1
  python3 check_assets.py --quiet    只输出断链清单
  python3 check_assets.py --strict   把「常见装饰资源缺失」也算失败（默认只告警）

检查对象：站点根下 *.html（递归）里 src / href / poster / data-src / content 的本地引用。
跳过：外链（http/https/protocol-relative）、锚点、mailto/tel、data:、{{占位符}}。
纯标准库，零依赖。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

BASE = Path(__file__).resolve().parent

# 这两个文件是「可后补」的装饰性资源：内容图缺失算硬伤，它们只告警
SOFT = {"favicon.ico", "apple-touch-icon.png", "logo-mark.png", "logo.png", "og-cover.png"}

ATTR = re.compile(
    r"""(?:src|href|poster|data-src|content)\\s*=\\s*["']([^"']+)["']""",
    re.I,
)
EXT = r"\\.(?:html|htm|css|js|mjs|png|jpg|jpeg|webp|svg|ico|gif|avif|woff2?|ttf|otf|xml|txt|json|pdf|mp4|webm)$"


def site_origin() -> str:
    """从 sitemap.xml 取站点 origin，用于把站内绝对 URL（og:image、JSON-LD logo）也纳入检查。"""
    sm = BASE / "sitemap.xml"
    if not sm.exists():
        return ""
    m = re.search(r"<loc>\\s*(https?://[^/<\\s]+)", sm.read_text(encoding="utf-8", errors="ignore"))
    return m.group(1) if m else ""


def refs(html: str, origin: str) -> set[str]:
    out: set[str] = set()
    for m in ATTR.finditer(html):
        raw = m.group(1).strip()
        if not raw or raw.startswith(("#", "mailto:", "tel:", "data:")):
            continue
        if raw.startswith("//"):
            continue
        if raw.startswith(("http://", "https://")):
            if not origin or not raw.startswith(origin + "/"):
                continue
            raw = raw[len(origin):]
        path = raw.split("?")[0].split("#")[0]
        if not re.search(EXT, path, re.I):
            continue
        out.add(unquote(path))
    # JSON-LD 里的绝对 URL（如 logo）也要检查，它们是正文节点而非 HTML 属性
    if origin:
        for blob in re.findall(r"<script[^>]*application/ld\\+json[^>]*>([\\s\\S]*?)</script>", html, re.I):
            for url in re.findall(r"""https?://[^\\s"'<>]+""", blob):
                if not url.startswith(origin + "/"):
                    continue
                path = url[len(origin):].split("?")[0]
                if re.search(EXT, path, re.I):
                    out.add(unquote(path))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    origin = site_origin()
    hard: list[str] = []
    soft: list[str] = []
    for page in sorted(BASE.rglob("*.html")):
        rel = page.relative_to(BASE)
        if any(p.startswith((".", "_")) for p in rel.parts):
            continue
        for ref in sorted(refs(page.read_text(encoding="utf-8", errors="ignore"), origin)):
            if (BASE / ref.lstrip("/")).exists():
                continue
            name = Path(ref).name
            line = f"{rel} -> {ref}"
            if name in SOFT or name.startswith("og-"):
                soft.append(line)
            else:
                hard.append(line)

    if hard or soft:
        if not a.quiet:
            for x in hard:
                print("  x 断链：" + x)
            for x in soft:
                print("  ! 缺装饰资源（可后补）：" + x)
    else:
        print("未发现断链引用。")

    if hard:
        return 1
    if soft and a.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--name", help="品牌 / 公司 / 产品名")
    ap.add_argument("--domain", help="域名，如 example.com")
    ap.add_argument("--out", help="输出目录")
    ap.add_argument("--style", default="paper", choices=STYLES)
    ap.add_argument("--brand", default="", help="品牌强调色 #rrggbb（自动校正对比度）")
    ap.add_argument("--host", default="oss", choices=("oss", "vercel", "none"))
    ap.add_argument("--bucket", default="", help="OSS 桶名（--host oss 必填）")
    ap.add_argument("--email", default="")
    ap.add_argument("--icp", default="")
    ap.add_argument("--lang", default="zh-CN")
    ap.add_argument("--tagline", default="")
    ap.add_argument("--desc", default="")
    ap.add_argument("--copy", default="",
                    help="文案 JSON 文件：{占位符名: 文案}，一次性注入全部【待填】项")
    ap.add_argument("--dump-keys", action="store_true",
                    help="打印全部可注入的文案占位符键名后退出（用于编写 copy.json）")
    ap.add_argument("--force", action="store_true", help="目标目录非空时覆盖")
    a = ap.parse_args()

    if a.dump_keys:
        ns = argparse.Namespace(name="X", domain="example.com", tagline="",
                                desc="", email="", icp="", lang=a.lang)
        for k in sorted(build_values(ns)):
            print(k)
        return 0

    for req in ("name", "domain", "out"):
        if not getattr(a, req):
            print(f"--{req} 为必填（--dump-keys 可查看文案键名）", file=sys.stderr)
            return 1
    if not TPL_DIR.is_dir():
        print(f"模板目录不存在：{TPL_DIR}", file=sys.stderr)
        print("渠道只分发 SKILL.md 时，请按 SKILL.md 附录 A 现场生成等价物。", file=sys.stderr)
        return 1
    if a.host == "oss" and not a.bucket:
        print("--host oss 时必须给 --bucket（OSS 桶名）", file=sys.stderr)
        return 1

    out = Path(a.out).expanduser().resolve()
    if out.exists() and any(out.iterdir()) and not a.force:
        print(f"目标目录非空：{out}\n如确认覆盖请加 --force", file=sys.stderr)
        return 1

    values = build_values(a)

    if a.copy:
        cp = Path(a.copy).expanduser()
        if not cp.exists():
            print(f"文案文件不存在：{cp}", file=sys.stderr)
            return 1
        try:
            data = json.loads(cp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"文案文件读取失败：{e}", file=sys.stderr)
            return 1
        if not isinstance(data, dict):
            print("文案文件必须是 {占位符名: 文案} 的 JSON 对象", file=sys.stderr)
            return 1
        unknown = [k for k in data if k not in values]
        for k, v in data.items():
            if k not in values:
                continue
            values[k] = str(v)
        if unknown:
            print("⚠ 文案文件中以下键无对应占位符，已忽略：", file=sys.stderr)
            print("  " + ", ".join(sorted(unknown)), file=sys.stderr)
        # 派生值跟随注入的文案：TAGLINE 变了，title 也要跟着变
        tg = values["TAGLINE"]
        if not tg.startswith(MARK):
            values["TITLE"] = f"{a.name} · {tg}"

    # 主题色：先定强调色（对 --bg 可读），再定实心按钮底色（对 --accent-fg 可读）
    bg = parse_hex(THEME_BG[a.style])
    fg = parse_hex(THEME_FG[a.style])
    brand = parse_hex(a.brand) if a.brand else parse_hex(DEFAULT_BRAND[a.style])
    accent = fit_contrast(brand, bg)
    accent_solid = fit_contrast(brand, fg)
    values["THEME_COLOR"] = to_hex(bg)

    theme_css = (TPL_DIR / "assets" / f"theme-{a.style}.css").read_text(encoding="utf-8")
    theme_css = set_var(theme_css, "accent-solid", to_hex(accent_solid))
    theme_css = set_var(theme_css, "accent-fg", to_hex(fg))
    theme_css = set_var(theme_css, "accent", to_hex(accent))

    # ── 写文件 ──────────────────────────────────────────────────────
    (out / "assets" / "css").mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    for tpl_name, dest in (("index.html", "index.html"), ("features.html", "features.html")):
        html = render((TPL_DIR / tpl_name).read_text(encoding="utf-8"), values)
        (out / dest).write_text(html, encoding="utf-8", newline="\n")
        written.append(dest)

    base_css = render((TPL_DIR / "assets" / "base.css").read_text(encoding="utf-8"), values)
    (out / "assets" / "css" / "base.css").write_text(base_css, encoding="utf-8", newline="\n")
    (out / "assets" / "css" / "theme.css").write_text(render(theme_css, values), encoding="utf-8", newline="\n")
    written += ["assets/css/base.css", "assets/css/theme.css"]

    origin = values["HOME_URL"].rstrip("/")
    (out / "robots.txt").write_text(ROBOTS.format(origin=origin), encoding="utf-8", newline="\n")
    (out / "sitemap.xml").write_text(
        SITEMAP.format(origin=origin, today=values["TODAY"]), encoding="utf-8", newline="\n"
    )
    (out / ".gitignore").write_text(GITIGNORE, encoding="utf-8", newline="\n")
    written += ["robots.txt", "sitemap.xml", ".gitignore"]

    (out / "sync_sitemap.py").write_text(
        SYNC_SITEMAP.format(origin=origin), encoding="utf-8", newline="\n"
    )
    (out / "check_assets.py").write_text(CHECK_ASSETS, encoding="utf-8", newline="\n")
    written += ["sync_sitemap.py", "check_assets.py"]

    if a.host == "oss":
        deploy = DEPLOY_OSS.format(bucket=a.bucket, origin=origin)
    elif a.host == "vercel":
        deploy = DEPLOY_VERCEL.format(origin=origin)
    else:
        deploy = DEPLOY_NONE.format(origin=origin)
    dp = out / "deploy.sh"
    dp.write_text(deploy, encoding="utf-8", newline="\n")
    dp.chmod(0o755)
    written.append("deploy.sh")

    # ── 输出 ────────────────────────────────────────────────────────
    print(f"已生成站点：{out}")
    print(f"  风格 {a.style}  强调色 {to_hex(accent)}（实心按钮 {to_hex(accent_solid)}）  托管 {a.host}")
    for w in sorted(written):
        print(f"  + {w}")

    missing = [x for x in REQUIRED_ASSETS if not (out / x).exists()]
    if missing:
        print("\n⚠ 还需补齐的静态资源（补齐前 deploy.sh 的断链闸门会拦截）：")
        for m in missing:
            print(f"  - {m}")
        print("  说明：logo-mark.png 用于顶栏 28×28；og-cover.png 建议 1200×630；")
        print("       favicon.ico 32×32；apple-touch-icon.png 180×180。")

    todo = [k for k, val in values.items() if val.startswith("【待填")]
    if todo:
        print(f"\n⚠ 文中还有 {len(todo)} 处【待填：…】标记，需按你的产品替换后才会通过 --strict 自检。")

    rc = 0
    if AUDIT.exists():
        print("\n── 自检（seo_audit.py）─────────────────────────")
        py = sys.executable or "python3"
        r = subprocess.run([py, str(AUDIT), str(out), "--base-url", origin],
                           capture_output=True, text=True)
        print(r.stdout.rstrip())
        if r.returncode != 0:
            rc = 2

    print("\n下一步：")
    print("  1. 补齐静态资源与【待填】文案（按 references/style-guide.md 的区块范式）")
    print("  2. python3 seo_audit.py . --base-url %s --strict" % origin)
    print("  3. ./deploy.sh --check  然后  ./deploy.sh")
    print("  4. 按 references/seo-submit.md 到各站长平台认证并提交 sitemap")
    return rc


if __name__ == "__main__":
    sys.exit(main())
