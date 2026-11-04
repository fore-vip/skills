#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sim-life · 结局海报渲染

内容（叙事文字）由模型提供，排版由本脚本保证。二者不混。
用法:
  python3 render_poster.py --state <state.json>
  python3 render_poster.py --state <state.json> --beats beats.json \
      --epitaph "他一生没离开过那座城，但把三个孩子送了出去" --tags "小城,手艺人,长寿"
"""

import argparse
import html
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "poster-template.html")

ATTR_ORDER = [("health", "健康"), ("wealth", "财富"), ("bond", "关系"),
              ("spirit", "心境"), ("skill", "本事"), ("fame", "声量")]


def esc(s):
    return html.escape(str(s), quote=False)


def auto_beats(st, limit=14):
    """没有外部 beats 时，从 history 分层采样，保证每个年龄段都有节点"""
    hist = st.get("history", [])
    if len(hist) <= limit:
        return [{"age": h["age"], "year": h["year"], "title": h["title"],
                 "text": h.get("action") or "", "key": h.get("valence") != "neu"} for h in hist]

    buckets = {}
    for h in hist:
        buckets.setdefault(h["age"] // 10, []).append(h)
    picked = []
    keys = sorted(buckets)
    per = max(1, limit // len(keys))
    for k in keys:
        group = buckets[k]
        n = min(per, len(group))
        step = max(1, len(group) // n)
        picked.extend(group[::step][:n])
    picked = picked[:limit]
    return [{"age": h["age"], "year": h["year"], "title": h["title"],
             "text": h.get("action") or "", "key": h.get("valence") != "neu"} for h in picked]


def auto_tags(st):
    p, a, d = st["profile"], st["attrs"], st["death"] or {}
    out = [p["family"]["class"], p["birth"]["settlement"]]
    age = d.get("age", st["now"]["age"])
    if age >= 85:
        out.append("长寿")
    elif age < 50:
        out.append("早逝")
    if a["wealth"] >= 70:
        out.append("殷实")
    if a["fame"] >= 55:
        out.append("有名")
    if a["bond"] >= 70:
        out.append("身边不缺人")
    elif a["bond"] <= 25:
        out.append("独来独往")
    if a["spirit"] >= 62:
        out.append("心宽")
    elif a["spirit"] <= 28:
        out.append("一生寡欢")
    if a["skill"] >= 75:
        out.append("手上有真东西")
    return out[:5]


def auto_epitaph(st):
    p, a, d = st["profile"], st["attrs"], st["death"] or {}
    age = d.get("age", st["now"]["age"])
    place = p["birth"]["place"].split()[-1]
    if age >= 85:
        return f"{place}的一辈子，见过的比说过的多。"
    if age < 50:
        return f"故事停在{place}以外的地方，很多话还没来得及说。"
    if a["fame"] >= 60:
        return f"从{place}走出去，名字被一些人记住了。"
    if a["bond"] >= 68:
        return f"没做成什么大事，但{place}的人提起他，都还愿意多说两句。"
    return f"{place}的普通一生：来了，做了些事，然后走了。"


def render_cast(st, limit=6):
    """身边的人：出场次数最多的几个，带一句能认出他的细节"""
    cast = st.get("cast") or {}
    if not cast:
        return ""
    rows = sorted(cast.items(),
                  key=lambda kv: (kv[1].get("n", 1), kv[1].get("bond", 50)),
                  reverse=True)[:limit]
    out = []
    for cid, c in rows:
        first, last = c.get("first_age"), c.get("last_age")
        span = ""
        if first is not None and last is not None:
            span = f"在场 {max(1, last - first + 1)} 年"
        if c.get("dead_age") is not None and c.get("dead_year") is not None:
            span += "　已故"
            cls = "p gone"
        else:
            cls = "p"
        mark = c.get("mark") or c.get("note") or ""
        out.append(
            f'<div class="{cls}"><div><span class="nm">{esc(c["name"])}</span>'
            f'<span class="rl">{esc(c.get("role") or c.get("rel") or "")}</span>'
            f'<span class="sp">{esc(span)}</span></div>'
            + (f'<div class="mk">{esc(mark)}</div>' if mark else "")
            + "</div>"
        )
    return "\n      ".join(out)


def render_timeline(beats):
    out = []
    for b in beats:
        cls = "beat key" if b.get("key") else "beat"
        text = f'<div class="d">{esc(b["text"])}</div>' if b.get("text") else ""
        out.append(
            f'<div class="{cls}"><div class="when"><b>{b["age"]} 岁</b>{b["year"]}</div>'
            f'<div class="what"><div class="t">{esc(b["title"])}</div>{text}</div></div>'
        )
    return "\n      ".join(out)


def render_attrs(attrs):
    rows = []
    for k, zh in ATTR_ORDER:
        v = attrs.get(k, 0)
        rows.append(
            f'<div class="row"><div class="k">{zh}</div>'
            f'<div class="bar"><i style="width:{v}%"></i></div>'
            f'<div class="v">{v}</div></div>'
        )
    return "\n      ".join(rows)


def main():
    ap = argparse.ArgumentParser(description="sim-life 结局海报")
    ap.add_argument("--state", required=True)
    ap.add_argument("--beats", help="大事件 JSON：[{year,age,title,text,key}]")
    ap.add_argument("--epitaph", help="一句话概括")
    ap.add_argument("--tags", help="逗号分隔的标签")
    ap.add_argument("--out", help="输出 html 路径")
    a = ap.parse_args()

    st = json.load(open(a.state, encoding="utf-8"))
    p, attrs, d = st["profile"], st["attrs"], st.get("death") or {}

    beats = auto_beats(st)
    if a.beats:
        beats = json.load(open(a.beats, encoding="utf-8"))
        beats.sort(key=lambda x: x.get("year", 0))

    tags = [t.strip() for t in a.tags.split(",")] if a.tags else auto_tags(st)
    epitaph = a.epitaph or auto_epitaph(st)

    death_year = d.get("year", st["now"]["year"])
    birth_year = p["birth"]["year"]
    tpl = open(TEMPLATE, encoding="utf-8").read()

    rep = {
        "{{NAME}}": esc(p["name"]),
        "{{INDEX}}": esc(str(st["meta"]["seed"])[:6].upper()),
        "{{LIFE_SPAN}}": f'{birth_year} — {death_year}',
        "{{PLACE}}": esc(f'{p["birth"]["country_zh"]} · {p["birth"]["place"]}'),
        "{{SEX}}": esc(p["sex"]),
        "{{GIFT}}": esc(p["gift"]["name"]) if p.get("gift") else "",
        "{{EPITAPH}}": esc(epitaph),
        "{{TAGS}}": "".join(f'<span class="tag">{esc(t)}</span>' for t in tags),
        "{{TIMELINE}}": render_timeline(beats),
        "{{CAST}}": render_cast(st) if "{{#CAST}}" in tpl else "",
        "{{ATTRS}}": render_attrs(attrs),
        "{{SEED}}": esc(st["meta"]["seed"]),
        "{{YEARS}}": str(death_year - birth_year),
        "{{TURNS}}": str(st.get("turns", 0)),
        "{{EVENTS}}": str(len(beats)),
        "{{ERA}}": esc(f'{birth_year} 年生人'),
        "{{STAMP}}": datetime.now().strftime("%Y.%m.%d"),
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)

    # 无天赋时整段移除
    import re
    if p.get("gift"):
        tpl = tpl.replace("{{#GIFT}}", "").replace("{{/GIFT}}", "")
    else:
        tpl = re.sub(r"\{\{#GIFT\}\}.*?\{\{/GIFT\}\}", "", tpl, flags=re.S)

    # 没有人物册时整段移除
    if rep["{{CAST}}"]:
        tpl = tpl.replace("{{#CAST}}", "").replace("{{/CAST}}", "")
    else:
        tpl = re.sub(r"\{\{#CAST\}\}.*?\{\{/CAST\}\}", "", tpl, flags=re.S)

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.state)), "poster.html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(tpl)
    print(json.dumps({"poster": os.path.abspath(out), "beats": len(beats),
                      "tags": tags, "epitaph": epitaph}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
