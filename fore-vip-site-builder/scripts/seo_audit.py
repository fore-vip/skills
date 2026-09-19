#!/usr/bin/env python3
"""seo_audit.py — 官网 SEO 辅料自检（发布闸门）

用法：
  python3 seo_audit.py <站点目录或 index.html ...> [--base-url https://example.com]
  python3 seo_audit.py . --base-url https://example.com --strict
  python3 seo_audit.py . --require-icp          # 内地节点站点：页脚必须有备案号

检查项（编号为逻辑分组，运行时按实际启用项顺序输出）：
  1  title 存在 / 非空 / <= 60 字符（含【待填】时降级为 WARN）
  2  description 存在 / 30-300 字符（同上）
  3  <html lang> 已声明
  4  viewport 含 width=device-width
  5  canonical 存在且为绝对 URL
  6  og:title / og:description / og:image / og:url 齐全
  7  twitter:card 存在
  8  JSON-LD 存在且可解析
  9  恰好 1 个 h1
 10  标题层级不跳号
 11  所有 img 都有 alt（alt="" 视为合规）
 12  无 {{占位符}} / TODO / FIXME 残留
 13  【待填：…】草稿标记 —— 默认 WARN，--strict 时 FAIL
 14  --require-icp 时页脚含 ICP 备案号
 15  robots.txt 存在且含 Sitemap:
 16  sitemap.xml 存在、loc 全为绝对 URL、与实际页面双向一致
 17  跨页 title 唯一

退出码：0 = 全过；1 = 有 FAIL。
纯 Python 3 标准库，零依赖。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

MARK = "【待填"
PLACEHOLDER = [r"\{\{[A-Z0-9_]+\}\}", r"\bTODO\b", r"\bFIXME\b"]
SM_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
ICP_RE = r"(ICP备|京ICP|沪ICP|粤ICP|浙ICP|苏ICP|川ICP|渝ICP|鲁ICP|闽ICP|湘ICP|鄂ICP|备案号)"


class Doc(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title = ""
        self.metas: list[tuple[str, str]] = []
        self.links: list[tuple[str, str]] = []
        self.headings: list[tuple[str, str]] = []
        self.imgs: list[dict[str, str]] = []
        self.jsonld: list[str] = []
        self._open_h: str | None = None
        self._buf: list[str] = []
        self._in_title = False
        self._in_jsonld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._in_title, self._buf = True, []
        elif tag == "meta":
            key = a.get("name", "") or a.get("property", "")
            if key:
                self.metas.append((key.lower(), a.get("content", "")))
        elif tag == "link":
            self.links.append((a.get("rel", "").lower(), a.get("href", "")))
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "script":
            if a.get("type", "").lower() == "application/ld+json":
                self._in_jsonld, self._buf = True, []
        elif re.fullmatch(r"h[1-6]", tag):
            self._open_h, self._buf = tag, []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._in_title:
            self.title = "".join(self._buf).strip()
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._buf).strip())
            self._in_jsonld = False
        elif tag == self._open_h:
            self.headings.append((tag, "".join(self._buf).strip()))
            self._open_h = None

    def handle_data(self, data: str) -> None:
        if self._in_title or self._in_jsonld or self._open_h:
            self._buf.append(data)

    def meta(self, key: str) -> str:
        for k, v in self.metas:
            if k == key:
                return v
        return ""


def strip_text(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    return re.sub(r"<[^>]+>", " ", html)


def audit_page(path: Path, strict: bool, require_icp: bool) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    d = Doc()
    d.feed(raw)
    body = strip_text(raw)
    fails: list[str] = []
    no = 0

    def chk(name: str, ok: bool, detail: str = "", warn_only: bool = False) -> None:
        nonlocal no
        no += 1
        status = "PASS" if ok else ("WARN" if warn_only else "FAIL")
        print(f"  {no:>2}. {name:<26} {status} {detail}".rstrip())
        if not ok and not warn_only:
            fails.append(f"{path.name}: {name} —— {detail or '不通过'}")

    title = d.title
    chk("title", bool(title) and len(title) <= 60,
        f"{len(title)} 字符" if title else "缺失", warn_only=MARK in title)
    desc = d.meta("description")
    chk("description", bool(desc) and 30 <= len(desc) <= 300,
        f"{len(desc)} 字符" if desc else "缺失", warn_only=MARK in desc)
    chk("html lang", bool(d.lang), d.lang or "缺失")
    chk("viewport", "width=device-width" in d.meta("viewport"),
        d.meta("viewport") or "缺失")
    canon = next((h for r, h in d.links if "canonical" in r), "")
    chk("canonical", canon.startswith(("http://", "https://")), canon or "缺失")
    missing_og = [k for k in ("og:title", "og:description", "og:image", "og:url") if not d.meta(k)]
    chk("og:*", not missing_og, "缺 " + "/".join(missing_og) if missing_og else "")
    chk("twitter:card", bool(d.meta("twitter:card")), d.meta("twitter:card") or "缺失")

    bad_jsonld = []
    for i, blob in enumerate(d.jsonld):
        try:
            json.loads(blob)
        except Exception as e:  # noqa: BLE001
            bad_jsonld.append(f"#{i + 1}: {e}")
    chk("JSON-LD", bool(d.jsonld) and not bad_jsonld,
        f"{len(d.jsonld)} 块" if d.jsonld and not bad_jsonld
        else ("; ".join(bad_jsonld) if bad_jsonld else "缺失"))

    h1 = [t for tag, t in d.headings if tag == "h1"]
    chk("h1 唯一", len(h1) == 1, f"发现 {len(h1)} 个")

    levels = [int(tag[1]) for tag, _ in d.headings]
    skips = [(levels[i - 1], levels[i]) for i in range(1, len(levels))
             if levels[i] - levels[i - 1] > 1]
    chk("标题层级", not skips, f"跳号 {skips}" if skips else "")

    no_alt = [i + 1 for i, a in enumerate(d.imgs) if "alt" not in a]
    chk("img alt", not no_alt, f"第 {no_alt} 张无 alt" if no_alt else "")

    left = sorted({p for pat in PLACEHOLDER for p in re.findall(pat, body)})
    chk("占位符残留", not left, str(left) if left else "")

    # 草稿标记扫全文（含 meta 属性里的 description）；占位符只扫正文，避免误伤内联 JS
    marks = len(re.findall(MARK, raw))
    chk("草稿标记【待填】", marks == 0, f"{marks} 处" if marks else "",
        warn_only=not strict)

    if require_icp:
        ok = bool(re.search(ICP_RE, body))
        chk("ICP 备案号", ok, "" if ok else "页脚未发现备案号")

    return fails


def check_site_files(site: Path) -> list[str]:
    fails: list[str] = []

    robots = site / "robots.txt"
    if not robots.exists():
        fails.append("robots.txt 缺失")
    elif "sitemap:" not in robots.read_text(encoding="utf-8", errors="ignore").lower():
        fails.append("robots.txt 未声明 Sitemap:")

    pages = set()
    for p in site.rglob("*.html"):
        r = p.relative_to(site)
        if any(part.startswith((".", "_")) for part in r.parts):
            continue
        pages.add(r.as_posix())

    sm = site / "sitemap.xml"
    if not sm.exists():
        fails.append("sitemap.xml 缺失")
        return fails
    try:
        root = ET.fromstring(sm.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError as e:
        fails.append(f"sitemap.xml 无法解析（{e}）")
        return fails

    locs = [(el.text or "").strip() for el in root.iter(f"{SM_NS}loc")]
    if not locs:
        fails.append("sitemap.xml 无 <loc>")
        return fails

    listed: set[str] = set()
    for loc in locs:
        if not loc.startswith(("http://", "https://")):
            fails.append(f"sitemap <loc> 非绝对 URL：{loc}")
            continue
        rel = re.sub(r"^https?://[^/]+/", "", loc).split("?")[0] or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        listed.add(rel)

    for r in sorted(listed - pages):
        fails.append(f"sitemap 指向不存在的页面：{r}")
    for p in sorted(pages - listed):
        fails.append(f"页面未收录进 sitemap：{p}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("paths", nargs="+", help="站点目录或 .html 文件")
    ap.add_argument("--base-url", default="", help="规范域（仅展示，用于人工核对）")
    ap.add_argument("--strict", action="store_true", help="【待填】草稿标记也判为失败")
    ap.add_argument("--require-icp", action="store_true", help="页脚必须有 ICP 备案号")
    a = ap.parse_args()

    site: Path | None = None
    htmls: list[Path] = []
    for raw in a.paths:
        p = Path(raw).expanduser().resolve()
        if p.is_dir():
            site = p
            htmls += [x for x in sorted(p.rglob("*.html"))
                      if not any(part.startswith((".", "_")) for part in x.relative_to(p).parts)]
        elif p.suffix.lower() in (".html", ".htm"):
            htmls.append(p)
            site = site or p.parent
        else:
            print(f"跳过（非目录、非 html）：{p}", file=sys.stderr)

    if not htmls:
        print("没有找到要检查的 HTML 文件。", file=sys.stderr)
        return 1

    print(f"站点：{site}")
    if a.base_url:
        print(f"规范域：{a.base_url.rstrip('/')}")
    print("=" * 60)

    all_fails: list[str] = []
    for h in htmls:
        print(f"\n=== {h.name} ===")
        all_fails += audit_page(h, a.strict, a.require_icp)

    site_fails: list[str] = []
    if site:
        print("\n=== 全站文件（robots.txt / sitemap.xml）===")
        site_fails = check_site_files(site)
        if site_fails:
            for x in site_fails:
                print(f"  FAIL {x}")
        else:
            print("  PASS robots.txt 与 sitemap.xml 一致")
        all_fails += site_fails

    if len(htmls) > 1:
        print("\n=== 跨页唯一性 ===")
        seen: dict[str, list[str]] = {}
        for h in htmls:
            d = Doc()
            d.feed(h.read_text(encoding="utf-8", errors="ignore"))
            seen.setdefault(d.title.strip(), []).append(h.name)
        dup = {t: who for t, who in seen.items() if len(who) > 1}
        if dup:
            for t, who in dup.items():
                msg = f"title 重复（{'、'.join(who)}）：{t or '(空)'}"
                print(f"  FAIL {msg}")
                all_fails.append(msg)
        else:
            print("  PASS 各页 title 互不相同")

    print("\n" + "=" * 60)
    uniq = sorted(set(all_fails))
    if uniq:
        for x in uniq:
            print(f"  x {x}")
        print(f"\n结果：FAIL（{len(uniq)} 项）—— 不建议发布")
        return 1
    print("结果：PASS —— 可以发布")
    return 0


if __name__ == "__main__":
    sys.exit(main())
