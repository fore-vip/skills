#!/usr/bin/env python3
"""主题 -> 版式。规则数据在 templates/layouts.json，新增版式只改那份 JSON。

用法:
  python3 pick_layout.py --topic "社区美容店的预约宣传页" --json
  python3 pick_layout.py --topic "AI 客服工具" --layout tech --json
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "templates" / "layouts.json"


def load_registry(path=None):
    return json.loads(Path(path or DEFAULT_REGISTRY).read_text(encoding="utf-8"))


def hit_count(topic, keywords):
    t = topic.lower()
    hits = []
    for kw in keywords:
        k = kw.lower()
        if re.fullmatch(r"[a-z0-9 +._-]+", k):
            found = re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t) is not None
        else:
            found = k in t
        if found:
            hits.append(kw)
    score = sum(1.5 if len(h) > 2 else 1.0 for h in hits)
    return score, hits


def choose(topic, registry=None, override=None):
    reg = registry or load_registry()
    layouts = reg["layouts"]
    if override:
        hit = next((x for x in layouts if x["id"] == override), None)
        if not hit:
            raise ValueError("未知版式 id: " + override + "（可用: "
                             + ", ".join(x["id"] for x in layouts) + "）")
        return dict(id=hit["id"], name=hit["name"], intent=hit["intent"],
                    tokens=hit["tokens"], sectionOrder=hit.get("sectionOrder", []),
                    heroAlign=hit.get("heroAlign", "center"), matched=True,
                    score=None, hits=[], reason="专家显式指定版式 " + override,
                    alternatives=[])
    scored = []
    for x in layouts:
        s, hits = hit_count(topic, x.get("keywords", []))
        scored.append((s, hits, x))
    scored.sort(key=lambda r: -r[0])
    best_s, best_hits, best = scored[0]
    if best_s <= 0:
        best = next(x for x in layouts if x["id"] == reg["default"])
        return dict(id=best["id"], name=best["name"], intent=best["intent"],
                    tokens=best["tokens"], sectionOrder=best.get("sectionOrder", []),
                    heroAlign=best.get("heroAlign", "center"), matched=False,
                    score=0, hits=[], reason="主题未命中任何关键词，已用兜底版式 "
                    + best["id"] + "；专家应确认或新增一套版式",
                    alternatives=[r[2]["id"] for r in scored if r[2]["id"] != best["id"]])
    return dict(id=best["id"], name=best["name"], intent=best["intent"],
                tokens=best["tokens"], sectionOrder=best.get("sectionOrder", []),
                heroAlign=best.get("heroAlign", "center"), matched=True,
                score=best_s, hits=best_hits,
                reason="主题「" + topic + "」命中关键词 " + "、".join(best_hits)
                + "，选用「" + best["name"] + "」版式",
                alternatives=[r[2]["id"] for r in scored[1:] if r[0] > 0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--layout", default="", help="显式指定版式 id，跳过自动路由")
    ap.add_argument("--registry", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = choose(a.topic, load_registry(a.registry) if a.registry else None, a.layout or None)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print("版式: %s（%s） matched=%s score=%s" % (r["id"], r["name"], r["matched"], r["score"]))
        print("理由: " + r["reason"])
        print("建议叙事顺序: " + " -> ".join(r["sectionOrder"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
