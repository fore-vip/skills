#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sim-life · 人生引擎

负责一切「不该由模型拍脑袋决定」的部分：
  1. 掷骰判定（行动成败）
  2. 事件抽取（按年龄段 × 地区 × 阶层加权）
  3. 自然变化与寿命结算
  4. 状态落盘（一轮 = 一年，跨几十轮不失真）

用法:
  python3 life_engine.py new --seed 42 --out ./sim-lives
  python3 life_engine.py tick --state <state.json> --kind work --action "去城里找活" --bonus 5
  python3 life_engine.py show --state <state.json>
  python3 life_engine.py end  --state <state.json> --cause "一次没能挺过去的手术"
"""

import argparse
import json
import math
import os
import re
import random
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sample_life import build, CLASS_BASE, COUNTRIES, HOUSING  # noqa: E402

ATTRS = ["health", "wealth", "bond", "spirit", "skill", "fame"]
ATTR_ZH = {"health": "健康", "wealth": "财富", "bond": "关系",
           "spirit": "心境", "skill": "本事", "fame": "声量"}

REGION_OF = {
    "CN": "东亚", "JP": "东亚", "KR": "东亚", "KP": "东亚", "TW": "东亚",
    "IN": "南亚", "PK": "南亚", "BD": "南亚", "NP": "南亚", "LK": "南亚", "AF": "南亚",
    "ID": "东南亚", "VN": "东南亚", "TH": "东南亚", "PH": "东南亚",
    "MM": "东南亚", "MY": "东南亚", "KH": "东南亚",
    "NG": "非洲", "ET": "非洲", "CD": "非洲", "TZ": "非洲", "ZA": "非洲", "KE": "非洲",
    "UG": "非洲", "SD": "非洲", "AO": "非洲", "MZ": "非洲", "GH": "非洲", "ML": "非洲",
    "BF": "非洲", "MW": "非洲", "ZM": "非洲", "SN": "非洲", "ZW": "非洲",
    "RU": "欧洲", "DE": "欧洲", "GB": "欧洲", "FR": "欧洲", "IT": "欧洲", "ES": "欧洲",
    "PL": "欧洲", "UA": "欧洲", "NL": "欧洲", "BE": "欧洲", "SE": "欧洲", "PT": "欧洲",
    "HU": "欧洲", "RS": "欧洲", "RO": "欧洲",
    "US": "北美", "CA": "北美",
    "BR": "拉美", "MX": "拉美", "CO": "拉美", "AR": "拉美", "PE": "拉美",
    "VE": "拉美", "CL": "拉美", "EC": "拉美", "GT": "拉美",
    "EG": "中东", "IR": "中东", "TR": "中东", "DZ": "中东", "IQ": "中东", "MA": "中东",
    "SA": "中东", "YE": "中东", "SY": "中东", "TN": "中东", "AE": "中东", "IL": "中东",
    "AU": "大洋洲", "UZ": "中亚", "KZ": "中亚",
}

# 阶层的财富天花板：靠年复一年攒钱到不了顶，只能靠做成事突破
CLASS_CAP = {"贫困": 40, "温饱": 62, "工薪": 76, "中产": 88, "富裕": 100}

KIND_ATTR = {"learn": "skill", "work": "skill", "social": "bond",
             "love": "bond", "health": "health", "risk": "spirit", "money": "wealth"}

EVENTS_PATH = os.path.join(HERE, "..", "references", "events.json")
_EVENTS = None


def clamp(v, lo=0, hi=100):
    return int(max(lo, min(hi, v)))


def load_events():
    global _EVENTS
    if _EVENTS is None:
        with open(EVENTS_PATH, encoding="utf-8") as f:
            _EVENTS = json.load(f)["events"]
    return _EVENTS


def default_status(age):
    if age <= 6:
        return "还不懂事，世界只有院子那么大"
    if age <= 12:
        return "念书，放学后有自己的去处"
    if age <= 17:
        return "开始知道自己想要什么，也开始知道有些事不由自己"
    if age <= 24:
        return "站在岔口上，还没决定往哪走"
    if age <= 34:
        return "日子开始有重量"
    if age <= 49:
        return "在中间，往哪边都得使劲"
    if age <= 64:
        return "开始有人叫你老师傅"
    return "日子慢下来了，剩下的事不多"


def health_base(age_eff):
    """年龄对应的健康基线：身体会自我修复，但台阶随年龄下移"""
    for hi, v in [(9, 88), (19, 86), (29, 83), (39, 79), (49, 74),
                  (59, 67), (69, 58), (79, 46), (89, 32), (200, 20)]:
        if age_eff <= hi:
            return v
    return 20


def natural_drift(age, attrs, rng, le=None, active=True, earn=1.0, cap=100):
    """自然变化：向基线回归，而非单向衰减"""
    le = le or 78
    age_eff = age * 78.0 / le
    d = {k: 0 for k in ATTRS}

    gap = health_base(age_eff) - attrs["health"]
    if gap > 0:
        d["health"] += min(5, max(1, round(gap * 0.4)))     # 低于基线会回升
    else:
        d["health"] -= 2 if age_eff >= 60 else rng.randint(0, 1)

    # 本事：童年学得快，成年靠做事积累，老了会钝
    # 本事只由「做了什么」决定，不做事就不涨；老了会钝
    if age <= 18:
        d["skill"] += rng.randint(0, 1)
    elif age >= 70 and rng.random() < 0.4:
        d["skill"] -= 1

    # 财富只跟「这一年有没有做事」有关：不做事就吃老本
    if active and 22 <= age <= 58:
        gain = rng.randint(1, 3)
        if attrs["wealth"] > 70:
            gain = 1
        elif attrs["wealth"] > 85:
            gain = 0
        d["wealth"] += round(gain * earn)
    if attrs["wealth"] >= cap and rng.random() < 0.55:
        d["wealth"] -= 1        # 到了这个位置，钱留不住
    elif active and 59 <= age <= 67:
        d["wealth"] += rng.randint(0, 1)
    elif age >= 68:
        d["wealth"] -= rng.randint(0, 1)
    elif not active and age >= 30 and rng.random() < 0.5:
        d["wealth"] -= 1
    if attrs["wealth"] < 12 and 18 <= age <= 60:
        d["wealth"] += 1                                    # 求生本能

    # 关系：不主动维护会变淡，但不会一路归零
    if rng.random() < 0.22:
        d["bond"] -= 1
    if attrs["bond"] > 72 and rng.random() < 0.4:
        d["bond"] += 1                      # 关系有上限，不会无限累积
    if attrs["bond"] < 22 and rng.random() < 0.45:
        d["bond"] += 1                      # 太孤了，人自己会去找人

    # 声量：普通人的名声本就会褪色，只有持续经营才留得住
    if attrs["fame"] > 15 and rng.random() < 0.8:
        d["fame"] -= rng.randint(0, 1)

    # 心境：向 50 收敛，偏离越远回弹越快（人会自我消化，但不会瞬间痊愈）
    dev = attrs["spirit"] - 50
    if abs(dev) > 8:
        step = max(2, round(abs(dev) * 0.22))
        d["spirit"] += -step if dev > 0 else step
    else:
        d["spirit"] += 1 if rng.random() < 0.5 else 0
    return d


OPS = {
    "<":  lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
}


def cond_ok(cond, attrs):
    """属性门槛：{"wealth": ["<", 25], "skill": [">=", 60]}，多项须同时满足"""
    for k, spec in (cond or {}).items():
        op, val = spec
        fn = OPS.get(op)
        if fn is None or not fn(attrs.get(k, 0), val):
            return False
    return True


def flags_ok(e, flags):
    """requires 可写 "!married" 表示必须没有；forbids 表示必须没有"""
    for r in e.get("requires", []):
        want, key = (not r.startswith("!")), r.lstrip("!")
        if bool(flags.get(key)) != want:
            return False
    for r in e.get("forbids", []):
        if flags.get(r):
            return False
    return True


def chain_gate(e, event_age, age):
    """因果链：必须在前置事件之后 within 年内才可能出现，返回 (是否合格, 权重倍数)

    follows 可写单个 {id, within, boost}，也可写列表表示"任一前置成立即可"。
    """
    f = e.get("follows")
    if not f:
        return True, 1.0
    options = f if isinstance(f, list) else [f]
    best = 0.0
    for o in options:
        when = event_age.get(o.get("id"))
        if when is None:
            continue
        gap = age - when
        if 0 <= gap <= o.get("within", 999):
            best = max(best, o.get("boost", 1.0))
    return (best > 0), best


def chain_blocked(e, event_age, age):
    """互斥：某事件之后 N 年内，本事件不得出现（刚升职不会同年被裁）"""
    for b in e.get("not_follows", []):
        when = event_age.get(b.get("id"))
        if when is not None and age - when <= b.get("within", 2):
            return True
    return False


def cooldown_hit(e, tag_last, age):
    """同类事件刚发生过：权重压到很低，而非彻底禁止"""
    cd = e.get("cooldown")
    if not cd:
        return False
    return any(age - tag_last.get(t, -999) < cd for t in e.get("tags", []))


def _child_age(st, age):
    """孩子多大：用于拦住「孩子 17 岁就抱孙子」这类事件"""
    cb = st.get("flags", {}).get("child_born_age")
    return {"child_age": max(0, age - cb) if cb else 0}


def pick_event(events, age, region, cls, rng, used=(), flags=None, attrs=None,
               event_age=None, tag_last=None, last_rare=None, p_rare=0.07,
               pending=None, kind=None, mood=None):
    """抽取一个事件。

    逻辑（硬过滤）：年龄 / 地区 / 阶层 / flags / 属性门槛 / 互斥 / 因果链
    随机（软权重）：基础权重 × 属性倾向 × 因果加成 × 冷却衰减 × 重复衰减，
                   外加一条独立的稀有通道让意外有机会发生
    """
    attrs = attrs or {}
    flags = flags or {}
    event_age = event_age or {}
    tag_last = tag_last or {}
    used = set(used)

    # 待触发的「果」：因已经发生，窗口期内大幅提权（过期即作废）
    pend = {}
    for q in (pending or []):
        if q.get("id") and age <= q.get("until", age):
            pend[q["id"]] = max(pend.get(q["id"], 0), q.get("boost", 18))

    normal, rare = [], []
    for e in events:
        lo, hi = e["stage"]
        if not (lo <= age <= hi):
            continue
        if e.get("regions") and region not in e["regions"]:
            continue
        if e.get("classes") and cls not in e["classes"]:
            continue
        if e.get("kinds") and kind not in e["kinds"]:
            continue
        if not flags_ok(e, flags):
            continue
        if not cond_ok(e.get("when"), attrs):
            continue
        if chain_blocked(e, event_age, age):
            continue
        ok, boost = chain_gate(e, event_age, age)
        if not ok:
            continue

        base = e.get("w", 1.0)
        w = base * boost
        if e["id"] in pend:
            w = base * max(boost, pend[e["id"]])
        # 属性倾向：穷人多遇缺钱的事，能人更容易碰到机会
        for k, coef in (e.get("lean") or {}).items():
            w *= max(0.12, 1 + (attrs.get(k, 50) - 50) / 50.0 * coef)
        if mood and e.get("valence") in ("pos", "neg"):
            w *= 2.2 if e["valence"] == mood else 0.15
        if cooldown_hit(e, tag_last, age):
            w *= 0.1
        if e["id"] in used:
            if not e.get("repeatable"):
                continue
            w *= 0.25
        if w <= 0:
            continue
        (rare if e.get("rare") else normal).append((e, w))

    # 稀有通道：至少隔 8 年，且只在合格稀有池存在时开启
    use_rare = (rare and (last_rare is None or age - last_rare >= 8)
                and rng.random() < p_rare)
    pool = rare if use_rare else (normal or rare)
    if not pool:
        return None
    return rng.choices([x[0] for x in pool], weights=[x[1] for x in pool], k=1)[0]


# ------------------------------------------------------------------ 生成式事件
# 事件不查表：脚本掷出「这一年该发生什么」（类别/方向/量级/约束），
# 模型据此即兴写一件从没有过的事，脚本再逐条校验它在这个人身上是否成立。
# events.json 不再充当事件池，只留作兜底与风格样本。

CAT_PROFILE = {
    "job": {"stage": (15, 76),
            "affinity": {"work": 3.2, "money": 2.0, "risk": 1.6, "learn": 0.4, "none": 0.25},
            "w": 1.15},
    "money": {"stage": (15, 92),
              "affinity": {"money": 3.2, "work": 1.3, "risk": 2.2, "none": 0.3},
              "w": 0.95},
    "family": {"stage": (3, 110),
               "affinity": {"love": 2.6, "social": 1.7, "none": 0.8, "work": 0.6},
               "w": 1.0},
    "love": {"stage": (14, 78),
             "affinity": {"love": 3.2, "social": 1.6, "none": 0.4},
             "w": 0.8},
    "health": {"stage": (0, 110),
               "affinity": {"health": 2.2, "none": 1.3, "work": 0.6},
               "w": 0.9},
    "social": {"stage": (6, 110),
               "affinity": {"social": 2.8, "none": 1.0, "love": 0.8},
               "w": 0.7},
    "self": {"stage": (9, 100),
             "affinity": {"learn": 2.8, "none": 1.1, "health": 0.8},
             "w": 0.75},
    "era": {"stage": (0, 110), "affinity": {}, "w": 0.5},
    "accident": {"stage": (3, 106),
                 "affinity": {"risk": 2.4, "work": 1.1, "none": 0.7},
                 "w": 0.3},
}

CAT_ZH = {"job": "谋生", "money": "钱", "family": "家里", "love": "感情",
          "health": "身体", "social": "人情", "self": "自己", "era": "时代",
          "accident": "意外"}

_BUDGET = {1: 8, 2: 14, 3: 22}
_PER_ATTR = {1: 4, 2: 6, 3: 9}

VAL_BY_OUTCOME = {
    "大成功": {"pos": .72, "mix": .24, "neu": .04, "neg": .0},
    "成功":   {"pos": .46, "mix": .38, "neu": .14, "neg": .02},
    "小挫":   {"neg": .44, "mix": .38, "neu": .14, "pos": .04},
    "失败":   {"neg": .74, "mix": .24, "neu": .02, "pos": .0},
    None:     {"pos": .28, "neg": .30, "mix": .28, "neu": .14},
}

MEMORY_WORDS = ("想起", "记得", "梦见", "梦到", "梦里", "照片", "相片", "坟", "上坟",
                "祭", "扫墓", "忌日", "当年", "那年", "以前", "从前", "生前",
                "遗物", "遗像", "旧", "回忆", "留给他的", "再没见过")


def _bigrams(s):
    s = "".join(ch for ch in str(s) if ch.isalnum() or "\u4e00" <= ch <= "\u9fa5")
    if len(s) < 2:
        return {s} if s else set()
    return {s[i:i + 2] for i in range(len(s) - 1)}


def _similar(a, b):
    A, B = _bigrams(a), _bigrams(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def _ev_cat(e):
    """库事件归到某个生成类别，仅用于挑风格样本"""
    tags = set(e.get("tags") or [])
    if "health" in tags:
        return "health"
    if "danger" in tags:
        return "accident"
    if tags & {"family", "love", "loss"}:
        return "family" if "loss" in tags else "love"
    if "job" in tags:
        return "job"
    if "money" in tags:
        return "money"
    if tags & {"social", "fame"}:
        return "social"
    if "study" in tags:
        return "self"
    return "era"


def _pick_category(st, ctx, slot_needed, rng):
    age, kind = ctx["age"], ctx["kind"]
    before = ctx["before"]
    cand, w = [], []
    for cat, p in CAT_PROFILE.items():
        lo, hi = p["stage"]
        if not (lo <= age <= hi):
            continue
        ww = p["w"]
        aff = p["affinity"]
        ww *= aff.get(kind, 0.55) if aff else 1.0
        # 处境决定哪类事更容易找上门
        if cat == "health":
            ww *= 1 + max(0, 58 - before["health"]) / 34.0
        if cat == "money":
            ww *= 1 + max(0, 42 - before["wealth"]) / 26.0 * 0.9
        if cat == "social":
            ww *= 1 + before["fame"] / 110.0
        if cat == "love" and st["flags"].get("married"):
            ww *= 0.7
        if cat == "family" and not st["flags"].get("parents") and not st["flags"].get("children"):
            ww *= 0.5
        # 欠着人情、久未露面的人，会把「人情/家里」这类事拉回来
        if cat in ("social", "family"):
            cast = st.get("cast") or {}
            owed = sum(1 for c in cast.values()
                       if c.get("owed") and _cast_alive(c, ctx["year"]))
            gap = sum(1 for c in cast.values()
                      if _cast_alive(c, ctx["year"]) and age - c.get("last_age", age) >= 4)
            ww *= 1 + min(owed, 3) * 0.22 + min(gap, 4) * 0.08
        if ww <= 0:
            continue
        cand.append(cat)
        w.append(ww)
    if not cand:
        return "era"
    return rng.choices(cand, weights=w, k=1)[0]


def _pick_valence(ctx, cat, rng):
    roll = ctx["roll"]
    d = dict(VAL_BY_OUTCOME.get(roll["outcome"] if roll else None,
                                VAL_BY_OUTCOME[None]))
    if cat in ("health", "accident"):
        d["neg"] += 0.10
        d["pos"] = max(0.0, d["pos"] - 0.10)
    tot = sum(d.values()) or 1
    keys = list(d)
    return rng.choices(keys, weights=[d[k] / tot for k in keys], k=1)[0]


def _pick_intensity(ctx, rng):
    roll = ctx["roll"]
    age = ctx["age"]
    if roll is None:
        lo, hi = 1, 2
    elif roll["outcome"] in ("大成功", "失败"):
        lo, hi = 2, 3
    else:
        lo, hi = 1, 2
    if age <= 12 or age >= 78:
        hi = min(hi, 2)                      # 老小两头，事都不大
    return rng.randint(lo, hi)


def _exemplars(age, cat, valence, k=6, rng=None):
    """风格样本：同类、同年龄段、同方向，只给标题，禁止照抄"""
    pool = []
    for e in load_events():
        lo, hi = e["stage"]
        if not (lo - 6 <= age <= hi + 6):
            continue
        if _ev_cat(e) != cat:
            continue
        pool.append(e)
    if len(pool) < k:
        pool += [e for e in load_events()
                 if e["stage"][0] - 6 <= age <= e["stage"][1] + 6]
    same = [e for e in pool if e.get("valence") == valence]
    pool = same + [e for e in pool if e not in same]
    out, seen = [], set()
    for e in pool:
        if e["title"] in seen:
            continue
        seen.add(e["title"])
        out.append({"title": e["title"], "hook": (e.get("hook") or "")[:40]})
        if len(out) >= k:
            break
    return out


def _open_promises(st):
    return [{"pid": q.get("pid"), "text": q.get("text"),
             "until": q.get("until"), "from": q.get("from")}
            for q in st.get("pending", []) if q.get("text")]


# ------------------------------------------------------------------ 人物与回响
# 事件里的人不能是一次性道具。出场过的人进 cast：有名字、有固定细节、有亲疏、有旧账。
# 往年的旧事也不烂在 history 里：脚本每年挑一件该回响的写进 echo，模型必须接上。

REL_ZH = ("亲属", "师徒", "同事", "朋友", "邻里", "对手",
          "旧识", "恋人", "客户", "恩人")

REL_CAT = {
    "师徒": {"job", "self"}, "同事": {"job", "money"}, "客户": {"money", "job"},
    "朋友": {"social", "self"}, "邻里": {"social", "family"},
    "对手": {"job", "social"}, "旧识": {"social", "love"},
    "恋人": {"love"}, "恩人": {"social", "money"}, "亲属": {"family", "love"},
}

# 一个人一生里真正有名字的人不该太多，超过这个数就不再主动推新人
CAST_SOFT_CAP = 16


def _cast_all(st):
    return st.setdefault("cast", {})


def _cast_alive(c, year):
    """人还在不在：死了不出场；活着但已过百岁的，也当走了"""
    if c.get("dead_age") is not None:
        return False
    by = c.get("born_year")
    if by is not None and year - by > 99:
        return False
    return True


def _cast_age(c, age, year):
    by = c.get("born_year")
    return (year - by) if by is not None else None


def _cast_line(cid, c, age, year):
    """给模型看的一行人物卡：固定细节 + 上次见面 + 欠没欠账"""
    ca = _cast_age(c, age, year)
    gap = age - c.get("last_age", age)
    bits = [f'{cid}｜{c["name"]}（{c.get("role") or c.get("rel") or "认识的人"}）']
    if ca is not None:
        bits.append(f'今年约 {ca} 岁')
    bits.append(f'亲疏 {c.get("bond", 50)}')
    if c.get("mark"):
        bits.append(f'细节：{c["mark"]}')
    if gap >= 1:
        bits.append(f'已有 {gap} 年没在故事里露面')
    else:
        bits.append("就在身边")
    if c.get("last_act"):
        bits.append(f'上次是「{c["last_act"]}」')
    if c.get("owed"):
        bits.append(f'还欠着一笔：{c["owed"]}')
    if ca is not None and ca >= 80:
        bits.append("年事已高，可能是最后几次见面")
    return "；".join(bits)


def _cast_payload(cid, c, age, year):
    return {"id": cid, "name": c["name"], "role": c.get("role"),
            "rel": c.get("rel"), "mark": c.get("mark"),
            "bond": c.get("bond", 50), "age_now": _cast_age(c, age, year),
            "last_age": c.get("last_age"), "times": c.get("n", 1),
            "last_act": c.get("last_act"), "owed": c.get("owed")}


def _cast_due(st, age, year, cat, rng, k=3):
    """挑出「今年该回来的人」：久未露面、欠着账、亲疏高的优先"""
    cast = _cast_all(st)
    pool, w = [], []
    for cid, c in cast.items():
        if not _cast_alive(c, year):
            continue
        gap = age - c.get("last_age", age - 1)
        if gap < 1 and c.get("n", 1) > 3:
            continue                      # 去年刚见过、见了很多次，今年让位
        ww = 1.0
        if 2 <= gap <= 9:
            ww *= 1.0 + gap * 0.30        # 隔了几年，是该回来了
        elif gap > 9:
            ww *= 1.6                     # 很久不见 = 重逢本身就是事
        if c.get("owed"):
            ww *= 2.4                     # 账没结，人得回来
        ww *= 0.55 + c.get("bond", 50) / 100.0
        ww *= 1.7 if cat in REL_CAT.get(c.get("rel"), ()) else 0.85
        if c.get("dead_age") is not None:
            continue
        pool.append(cid)
        w.append(ww)
    if not pool:
        return []
    n = min(k, len(pool))
    picked = []
    ids = list(pool)
    ws = list(w)
    for _ in range(n):
        if not ids:
            break
        cid = rng.choices(ids, weights=ws, k=1)[0]
        i = ids.index(cid)
        ids.pop(i)
        ws.pop(i)
        picked.append(cid)
    return [{"id": cid, "card": _cast_line(cid, cast[cid], age, year),
             "data": _cast_payload(cid, cast[cid], age, year)} for cid in picked]


def _echo_pick(st, age, rng):
    """挑一件该在今年回响的旧事：隔了 5 年以上、当年没交代完的最优先"""
    held = [q for q in st.get("loose_ends", []) if q.get("text")]
    done = set(st.get("echoed") or [])
    if held:
        cand = [q for q in held if q.get("from") is not None
                and age - q["from"] >= 5 and q["from"] not in done]
        if cand and rng.random() < 0.78:
            q = rng.choice(cand)
            return {"age": q["from"], "kind": "loose_end", "text": q["text"],
                    "years_ago": age - q["from"],
                    "ask": "这笔账当年没结，现在有能力结了、或者彻底结不了了"}

    hist = [h for h in st.get("history", [])
            if h.get("hook") and 5 <= age - h["age"] <= 30 and h["age"] not in done]
    if not hist:
        return None
    if rng.random() > 0.52:
        return None
    # 没交代完后果的、偏负的、转折大的更值得回响
    w = []
    for h in hist:
        ww = 1.0
        if h.get("valence") == "neg":
            ww *= 2.2
        elif h.get("valence") == "mix":
            ww *= 1.7
        if not h.get("resolved"):
            ww *= 1.4
        w.append(ww)
    h = rng.choices(hist, weights=w, k=1)[0]
    return {"age": h["age"], "kind": "old_event", "title": h["title"],
            "hook": h.get("hook"), "years_ago": age - h["age"],
            "ask": "今年发生的事，要和这件事有可见的联系"}


def _constraints(st, ctx, slot):
    """把「不能写什么」写成白名单式的句子，模型照着写就不会错"""
    age, year = ctx["age"], ctx["year"]
    fl = st["flags"]
    prof = st["profile"]
    out = [f"年龄 {age}，年份 {year}，{prof['birth']['country_zh']}{prof['birth']['place']}，"
           f"家庭属{prof['family']['class']}阶层，住在{prof['family']['housing']}"]
    if age < 15:
        out.append("未满 15 岁：不得出现工作、婚恋、生育、驾驶、借贷、独自远行")
    elif age < 18:
        out.append("未满 18 岁：可打工或辍学，但不得结婚、生育、贷款、开车")
    if age < 50:
        out.append("未到 50 岁：不得出现退休、养老金、养老院")
    if age > 24:
        out.append("已过 24 岁：不得出现小学、中考、高考、上大学的场景")
    if age < 60:
        out.append("不得出现「同龄人大批离世」这类老年场景")
    if not fl.get("married"):
        out.append("未婚：不得出现配偶（老伴/妻子/丈夫/爱人），除非本事件就是成家并 sets.married")
    if not fl.get("children"):
        out.append("无子女：不得出现子女（儿子/女儿/孩子），除非本事件就是生育并 sets.children")
    elif not fl.get("child_born_age"):
        out.append("子女尚幼：不得出现孙辈")
    elif ctx["age"] - fl["child_born_age"] < 22:
        out.append(f"子女约 {ctx['age'] - fl['child_born_age']} 岁：不得出现孙辈，也谈不上「子女成家」")
    if not fl.get("parents"):
        out.append("父母已故：不得出现父母在世的情节（回忆、上坟、遗物可以）")
    if prof["family"]["class"] not in ("贫困", "温饱"):
        out.append("非贫困家庭：不得出现挑水、土坯房、煤油灯、交公粮这类只有赤贫农村才有的场景")
    if not prof["birth"].get("urban"):
        out.append("住在村庄或小镇：不宜出现地铁、写字楼、月供、网约车")
    else:
        out.append("住在城市：不宜出现挑水、放牛、走几里山路上学")
    if year < 1996:
        out.append(f"{year} 年：没有智能手机，没有微信，没有网约车")
    elif year < 2011:
        out.append(f"{year} 年：有手机但没有微信、扫码、网约车、短视频")
    if year < 1980:
        out.append(f"{year} 年：没有打工潮，没有包产到户，农村是集体劳动")

    # 人物线：死人不能复活，散了的账还挂着
    age_now, year_now = ctx["age"], ctx["year"]
    cast = st.get("cast") or {}
    dead = [c["name"] for c in cast.values() if c.get("dead_age") is not None]
    if dead:
        out.append("已故的人：" + "、".join(dead[:6])
                   + "（只能出现在回忆、遗物、上坟、梦里的场景）")
    owed = [f'{c["name"]}：{c["owed"]}' for c in cast.values()
            if c.get("owed") and _cast_alive(c, year_now)]
    if owed:
        out.append("还欠着的人：" + "；".join(owed[:4]))
    return out


def _roll(st, kind="none", bonus=0, difficulty=0, years=1, action="", rng=None):
    """只掷骰，不改状态。返回本轮上下文，供 brief 存档、commit 复用。"""
    rng = rng or random.Random(f'{st["meta"]["seed"]}:{st["turns"]}:{kind}:{years}')
    age = st["now"]["age"] + years
    year = st["now"]["year"] + years
    before = dict(st["attrs"])
    delta, roll = {}, None
    streak = st.get("fail_streak", 0)

    if kind and kind != "none":
        key = KIND_ATTR.get(kind, "skill")
        p = 50 + (before[key] - 50) * 0.45 + bonus - difficulty
        p += min(streak, 3) * 7
        p = max(5, min(95, p))
        dice = rng.randint(1, 100)
        if dice <= max(3, p * 0.15):
            outcome, scale = "大成功", 1.0
        elif dice <= p:
            outcome, scale = "成功", 0.62
        elif dice <= p + (100 - p) * 0.45:
            outcome, scale = "小挫", -0.45
        else:
            outcome, scale = "失败", -0.95
        mag = round((6 + rng.randint(0, 4)) * scale)
        if mag > 0 and key == "skill":
            mag = round(mag * max(0.0, 1 - before["skill"] / 95))
        if mag < 0 and key == "skill":
            mag = max(-2, round(mag * 0.35))
        delta[key] = mag
        if kind in ("work", "risk", "money") and mag > 0:
            delta["fame"] = max(1, round(mag * 0.2))
        if mag > 0:
            delta["spirit"] = round(mag * 0.45)
        else:
            delta["spirit"] = round(mag * 0.4)
            if outcome == "失败":
                delta["health"] = -1
        streak = streak + 1 if outcome in ("失败", "小挫") else 0
        roll = {"attr": ATTR_ZH[key], "p": round(p), "dice": dice, "outcome": outcome,
                "delta": {ATTR_ZH[k]: v for k, v in delta.items() if v}}

    if kind in ("work", "money"):
        earn = 1.0
    elif kind in (None, "none", ""):
        earn = 0.0
    else:
        earn = 0.35
    cap = CLASS_CAP.get(st["profile"]["family"]["class"], 85)
    drift = natural_drift(age, before, rng, st["profile"]["life_expectancy"],
                          active=(kind not in (None, "none", "")), earn=earn, cap=cap)

    return {"age": age, "year": year, "before": before, "roll": roll,
            "delta": delta, "drift": drift, "kind": kind, "years": years,
            "action": action, "fail_streak": streak}


def _should_event(st, ctx, rng):
    quiet = st.get("quiet_years", 0)
    dramatic = bool(ctx["roll"] and ctx["roll"]["outcome"] in ("大成功", "失败"))
    p_ev = 0.36 + (0.12 if dramatic else 0) + min(quiet, 3) * 0.16
    if ctx["years"] > 1:
        p_ev = 1.0
    return rng.random() < p_ev


def _kin_of(role):
    """认出父母，好在他们过世时同步人物册"""
    r = role or ""
    if re.search(r"父亲|爸|他爹|老爹|父$", r):
        return "father"
    if re.search(r"母亲|妈|他娘|老娘|母$", r):
        return "mother"
    return None


def _apply_people(st, ev, age, year, rng):
    """把这一年的出场人物写进 cast：续缘、入册、改亲疏、记账、送走。
    返回 (按出场顺序的 cid 列表, 本年被回想的旧年份列表)。"""
    cast = _cast_all(st)
    seq = st.get("cast_seq", 0)
    ties = ev.get("ties") or {}
    touched, order, recalls = [], [], []

    for p in ev.get("people") or []:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        if pid and pid in cast:
            c = cast[pid]
            c["last_age"] = age
            c["last_year"] = year
            c["n"] = c.get("n", 1) + 1
            if p.get("act"):
                c["last_act"] = str(p["act"])[:36]
            if p.get("recall_age") is not None:
                c["recent_recall"] = p["recall_age"]
                # 把旧事写进人物的账上，下次 brief 会把这句话带回来
                old = next((h for h in st.get("history", [])
                            if h["age"] == p["recall_age"]), None)
                if old:
                    c["note"] = f'{p["recall_age"]} 岁那年：{old["title"]}'
            if p.get("note"):
                c["note"] = str(p["note"])[:46]
            if p.get("owed"):
                c["owed"] = str(p["owed"])[:40]
            elif p.get("paid"):
                c.pop("owed", None)
            if p.get("dies"):
                c["dead_age"] = age
                c["dead_year"] = year
            touched.append(pid)
            order.append(pid)
            if isinstance(p.get("recall_age"), int):
                recalls.append(p["recall_age"])
        elif p.get("new"):
            nw = p["new"]
            name = str(nw.get("name") or "").strip()
            if not name:
                continue
            seq += 1
            cid = f"c{seq}"
            na = nw.get("age")
            if not isinstance(na, int):
                na = age + rng.choice([-6, -3, -1, 1, 2, 4, 7, 11])
            na = max(0, min(95, na))
            cast[cid] = {
                "name": name,
                "role": str(nw.get("role") or "")[:18],
                "rel": nw.get("rel") if nw.get("rel") in REL_ZH else "旧识",
                "sex": nw.get("sex") if nw.get("sex") in ("男", "女") else rng.choice(("男", "女")),
                "mark": str(nw.get("mark") or "")[:30],
                "kin": _kin_of(str(nw.get("role") or "")),
                "bond": int(nw.get("bond", 52)),
                "born_year": year - na,
                "first_age": age,
                "first_title": ev.get("title"),
                "last_age": age,
                "last_year": year,
                "n": 1,
                "last_act": str(p.get("act") or "")[:36],
                "note": f'{age} 岁那年认识的',
                "dead_age": None,
            }
            touched.append(cid)
            order.append(cid)

    for cid, d in ties.items():
        if cid in cast and isinstance(d, (int, float)):
            cast[cid]["bond"] = clamp(cast[cid].get("bond", 50) + int(d))

    # 上了年纪的人，不用等到写进事件才走
    for cid, c in cast.items():
        if c.get("dead_age") is not None or cid in touched:
            continue
        ca = _cast_age(c, age, year)
        if ca is None or ca < 82:
            continue
        if rng.random() < min(0.55, 0.04 + (ca - 82) * 0.032):
            c["dead_age"] = age
            c["dead_year"] = year
            c["quiet_death"] = True

    # 长期不见，关系自然淡一点；淡到底就是走散了
    for cid, c in cast.items():
        if cid in touched or c.get("dead_age") is not None:
            continue
        gap = age - c.get("last_age", age)
        if gap >= 4 and c.get("bond", 50) > 12:
            c["bond"] = clamp(c.get("bond", 50) - min(3, gap - 3))

    st["cast_seq"] = seq
    return order, recalls


def _apply(st, ctx, ev=None, status="", cause="", flags=None, action="", rng=None,
           seed_people=None):
    """把这一轮（判定 + 事件 + 漂移）落到状态上，并结算死亡。"""
    rng = rng or random.Random(f'{st["meta"]["seed"]}:{st["turns"]}:apply')
    age, year = ctx["age"], ctx["year"]
    before = ctx["before"]
    delta = dict(ctx["delta"])
    drift = ctx["drift"]
    for k, v in drift.items():
        delta[k] = delta.get(k, 0) + v
    if ev:
        for k, v in ev.get("effects", {}).items():
            delta[k] = delta.get(k, 0) + v

    st["attrs"] = {k: clamp(before[k] + delta.get(k, 0)) for k in ATTRS}
    st["now"]["age"] = age
    st["now"]["year"] = year
    st["turns"] += 1
    st["fail_streak"] = ctx.get("fail_streak", 0)
    if status:
        st["status"] = status
    if ev:
        for k, v in ev.get("sets", {}).items():
            st.setdefault("flags", {})[k] = v
    if flags:
        st.setdefault("flags", {}).update(flags)
    ch = st.setdefault("flags", {})
    if ch.get("children") and not ch.get("child_born_age"):
        ch["child_born_age"] = age
    if ch.get("married"):
        ch["ever_married"] = True

    # 父母不会永远在：过了四十八岁，这件事迟早要发生
    if ch.get("parents") and age >= 48 and rng.random() < 0.10:
        ch["parents"] = False
        st.setdefault("pending", []).append(
            {"id": "m03", "until": age + 2, "boost": 30})
        # 人物册里登记过的父母，同步走掉，别留在名单上
        for c in (st.get("cast") or {}).values():
            if c.get("kin") and c.get("dead_age") is None:
                c["dead_age"] = age
                c["dead_year"] = year

    # 死亡判定（Gompertz 曲线 + 健康修正）
    le = st["profile"]["life_expectancy"]
    age_eff = age * 78.0 / le
    p_death = 0.00006 * math.exp(0.088 * age_eff)
    p_death += max(0, 32 - st["attrs"]["health"]) * 0.004
    p_death = min(p_death, 0.92)
    if rng.random() < p_death or st["attrs"]["health"] <= 0 or age >= 105:
        if not cause:
            if st["attrs"]["health"] <= 25:
                cause = "久病"
            elif age < le - 12 and st["attrs"]["health"] > 45:
                cause = "一场没能救回来的急病"
            elif age >= le - 5:
                cause = "身体走到了尽头"
            else:
                cause = "身体撑不住了"
        st["ended"] = True
        st["death"] = {"age": age, "year": year, "cause": cause,
                       "attrs": dict(st["attrs"])}

    # 记录
    st["quiet_years"] = 0 if ev else st.get("quiet_years", 0) + 1
    if ev:
        for r in ev.get("resolves", []):
            st["pending"] = [q for q in st.get("pending", []) if q.get("pid") != r]
            st["loose_ends"] = [q for q in st.get("loose_ends", []) if q.get("pid") != r]
        for t in ev.get("then", []):
            if t.get("id"):
                st.setdefault("pending", []).append(
                    {"id": t["id"], "until": age + t.get("within", 3),
                     "boost": t.get("boost", 18)})
            else:
                st["promise_seq"] = st.get("promise_seq", 0) + 1
                st.setdefault("pending", []).append({
                    "pid": f"p{st['promise_seq']}", "text": t.get("text", ""),
                    "until": age + t.get("within", 3), "from": age,
                    "boost": t.get("boost", 0)})
        st.setdefault("used_events", []).append(ev.get("id") or ev["title"])
        if ev.get("id"):
            st.setdefault("event_age", {})[ev["id"]] = age
        for t in ev.get("tags", []):
            st.setdefault("tag_last", {})[t] = age
        if ev.get("rare"):
            st["last_rare"] = age
    # 到期没兑现的旧账不丢，转成 loose_ends —— 二十年后还会找上门
    keep, expired = [], []
    for q in st.get("pending", []):
        (keep if q.get("until", 0) >= age else expired).append(q)
    for q in expired:
        if q.get("text"):
            st.setdefault("loose_ends", []).append({**q, "forgot_at": age})
    st["pending"] = keep
    st["loose_ends"] = st.get("loose_ends", [])[-12:]

    # 人物落地：老人续缘、新人入册、亲疏变化
    ppl_ids, recall_ages = [], []
    ev_people = ((ev or {}).get("people") or seed_people or [])
    if ev_people:
        holder = dict(ev or {"title": f"{age} 岁那年身边的人"})
        holder["people"] = ev_people
        ppl_ids, recall_ages = _apply_people(st, holder, age, year, rng)

    if ev or action:
        lk_ages = [l.get("age") for l in (ev.get("links") or [])
                   if isinstance(l, dict)] if ev else []
        st["history"].append({
            "age": age, "year": year,
            "title": ev["title"] if ev else (action or f"{age} 岁"),
            "action": action or None,
            "valence": ev["valence"] if ev else "neu",
            "id": ev.get("id") if ev else None,
            "category": ev.get("category") if ev else None,
            "hook": ev.get("hook") if ev else None,
            "why": ev.get("why") if ev else None,
            "people": ppl_ids,
            "links": lk_ages,
            "recall": recall_ages,
            "resolved": bool(ev.get("resolves")) if ev else False,
            "flags": dict(st.get("flags", {})),
        })
        if ev and ev.get("links"):
            for l in ev["links"]:
                if isinstance(l, dict) and isinstance(l.get("age"), int):
                    st.setdefault("echoed", []).append(l["age"])
        if ev and isinstance(ev.get("_echo_age"), int):
            st.setdefault("echoed", []).append(ev["_echo_age"])

    st["echoed"] = list(dict.fromkeys(st.get("echoed") or []))[-40:]

    return {
        "age": age, "year": year, "place": st["now"]["place"],
        "action": action or None,
        "roll": ctx["roll"],
        "event": ({**{k: ev[k] for k in ("title", "hook", "valence")},
                   "id": ev.get("id"),
                   "category": ev.get("category"),
                   "tags": ev.get("tags", []),
                   "rare": bool(ev.get("rare")),
                   "why": ev.get("why"),
                   "effects": {ATTR_ZH[k]: v for k, v in ev.get("effects", {}).items()}}
                  if ev else None),
        "drift": {ATTR_ZH[k]: v for k, v in drift.items() if v},
        "delta_total": {ATTR_ZH[k]: st["attrs"][k] - before[k] for k in ATTRS
                        if st["attrs"][k] != before[k]},
        "attrs": {ATTR_ZH[k]: st["attrs"][k] for k in ATTRS},
        "flags": dict(st.get("flags", {})),
        "open": _open_promises(st),
        "quiet": ev is None,
        "alive": not st["ended"],
        "death": st["death"],
    }


def step(st, kind="none", bonus=0, difficulty=0, years=1, no_event=False,
         action="", status="", cause="", flags=None, rng=None):
    """库模式推进一步（兜底 / 压测用）。生成式流程走 brief + commit。"""
    rng = rng or random.Random(f'{st["meta"]["seed"]}:{st["turns"]}:{kind}:{years}')
    ctx = _roll(st, kind, bonus, difficulty, years, action, rng)
    ev = None
    if not no_event and _should_event(st, ctx, rng):
        ev = pick_event(load_events(), ctx["age"], st["now"]["region"],
                        st["profile"]["family"]["class"], rng,
                        used=set(st.get("used_events", [])),
                        flags=st.get("flags", {}),
                        attrs=dict(ctx["before"], **_child_age(st, ctx["age"])),
                        event_age=st.get("event_age", {}),
                        tag_last=st.get("tag_last", {}),
                        last_rare=st.get("last_rare"),
                        pending=st.get("pending", []),
                        kind=kind,
                        mood=("pos" if ctx["roll"] and ctx["roll"]["outcome"] == "大成功"
                              else "neg" if ctx["roll"] and ctx["roll"]["outcome"] == "失败"
                              else None))
        if ev:
            ev = dict(ev)
            ev["effects"] = dict(ev.get("effects", {}))
            vs = ev.get("variants")
            if vs:
                ev["hook"] = rng.choice([ev["hook"]] + list(vs))
    return _apply(st, ctx, ev, status, cause, flags, action, rng)


def make_brief(st, kind="none", bonus=0, difficulty=0, years=1, action="",
               rng=None, no_event=False):
    """掷出本年的槽位与上下文。不改属性，只把 ctx 存进 pending_turn。"""
    rng = rng or random.Random(f'{st["meta"]["seed"]}:{st["turns"]}:brief')
    ctx = _roll(st, kind, bonus, difficulty, years, action, rng)
    age, year = ctx["age"], ctx["year"]
    prof = st["profile"]

    slot = None
    if not no_event and _should_event(st, ctx, rng):
        cat = _pick_category(st, ctx, True, rng)
        val = _pick_valence(ctx, cat, rng)
        inten = _pick_intensity(ctx, rng)
        slot = {"category": cat, "category_zh": CAT_ZH[cat], "valence": val,
                "intensity": inten, "budget": _BUDGET[inten],
                "per_attr": _PER_ATTR[inten]}

    open_p = _open_promises(st)
    if slot and open_p:
        slot["must_resolve"] = [q for q in open_p
                                if q.get("until") is not None and q["until"] <= age]

    # 人物：本年该回来的人 + 该回响的旧事
    cast = _cast_all(st)
    due = _cast_due(st, age, year, slot["category"] if slot else "social", rng)
    echo = _echo_pick(st, age, rng) if slot else None
    if slot:
        slot["echo"] = echo
        slot["cast_due"] = [d["id"] for d in due]
    ctx["slot"] = slot

    recent = [h["title"] for h in st.get("history", [])[-10:]]
    return {
        "who": {"name": prof["name"], "sex": prof["sex"],
                "country": prof["birth"]["country_zh"],
                "place": prof["birth"]["place"],
                "settlement": prof["birth"].get("settlement"),
                "urban": prof["birth"].get("urban"),
                "class": prof["family"]["class"],
                "housing": prof["family"]["housing"],
                "traits": prof.get("traits", []),
                "life_expectancy": prof["life_expectancy"]},
        "when": {"age": age, "year": year, "decade": f"{year // 10 * 10}s"},
        "state": {"attrs": {ATTR_ZH[k]: ctx["before"][k] for k in ATTRS},
                  "status": st.get("status"),
                  "flags": st.get("flags", {}),
                  "recent": [{"age": h["age"], "title": h["title"]}
                             for h in st.get("history", [])[-4:]]},
        "this_year": {"kind": kind, "action": action or None,
                      "roll": ctx["roll"],
                      "drift": {ATTR_ZH[k]: v for k, v in ctx["drift"].items() if v}},
        "slot": slot,
        "people": {"due": due,
                   "roster": [{"id": cid, "name": c["name"],
                               "role": c.get("role"), "rel": c.get("rel"),
                               "bond": c.get("bond", 50),
                               "age_now": _cast_age(c, age, year),
                               "last_age": c.get("last_age"),
                               "times": c.get("n", 1),
                               "mark": c.get("mark"),
                               "owed": c.get("owed")}
                              for cid, c in cast.items() if _cast_alive(c, year)],
                   "recent_losses": [{"id": cid, "name": c["name"],
                                      "role": c.get("role"),
                                      "died_year": c.get("dead_year"),
                                      "age_then": c.get("dead_age")}
                                     for cid, c in cast.items()
                                     if c.get("dead_year") is not None
                                     and 0 <= year - c["dead_year"] <= 2],
                   "count": len(cast),
                   "note": ("人物已够多，今年优先让旧人回来，不要再添新面孔"
                            if len(cast) >= CAST_SOFT_CAP else
                            "身边的人还不多，这一年可以认识一个新的人")},
        "echo": echo,
        "open": open_p,
        "loose_ends": [q for q in st.get("loose_ends", []) if q.get("text")][-5:],
        "forbid_titles": recent,
        "constraints": _constraints(st, ctx, slot) if slot else [],
        "exemplars": _exemplars(age, slot["category"], slot["valence"], rng=rng) if slot else [],
        "schema": {"title": "3-16 字，具体，不用形容词",
                   "hook": "20-70 字，一个场景，两三个物件",
                   "why": "8-40 字，说清为什么此刻发生在它身上",
                   "valence": "/".join(["pos", "neg", "mix", "neu"]),
                   "category": slot["category"] if slot else None,
                   "intensity": slot["intensity"] if slot else None,
                   "effects": "键限 health/wealth/bond/spirit/skill/fame，整数",
                   "requires": "自陈前提：married/children_min/child_age_min/parents",
                   "sets": "本事件改变的状态：married/children/parents",
                   "people": "[{id, act, say?, recall_age?}] 用老人；"
                             "[{new: {name, role, rel, mark, age, sex}}] 添新人；最多 3 人",
                   "ties": "{id: 整数} 与某人的亲疏变化，-10..10",
                   "links": "[{age, how}] 挂到往年某件事上，age 必须是真实经历过的年份",
                   "echo_skip": "确实接不上本年 echo 时，写一句理由",
                   "then": "[{text, within<=5, with?}] 留下未了结的事，供以后兑现",
                   "resolves": "[pid] 本事件兑现了哪些 open",
                   "tags": "选填，如 job/money/health/family/loss"},
        "ctx": ctx,
    }


# ------------------------------------------------------------------ 生成校验
R_SPOUSE = r"老伴|妻子|丈夫|爱人|老婆|老公|太太|媳妇|内人"
R_EX = r"前妻|前夫|离了婚|离婚"
R_CHILD = r"儿子|女儿|孩子|闺女|独生子|长子|小儿子|大儿子|小女儿"
R_GRAND = r"孙子|孙女|外孙|孙辈|抱孙|当爷爷|当奶奶"
R_PARENT = r"父亲|母亲|爸爸|妈妈|他爹|他娘|老爹|老娘"
R_RETIRE = r"退休|退下来|养老金|领退休金|养老院"
R_PRIMARY = r"小学|初中|念书|上学|书包|同桌"
R_HIGH = r"高中|高考|中考|大学|考研|留学|专科|录取通知书"
R_WORK = r"上班|厂里|工地|公司|加班|工钱|师傅|工位|车间"
R_DRIVE = r"开车|货车|驾照|跑车|出租车|货车司机"
R_POOR = r"挑水|取水|水窖|旱灾|通电|土坯|煤油灯|赤脚|放牛|插秧|交公粮|生产队"
R_URBAN = r"地铁|高铁|写字楼|电梯|房贷|月供|外卖|网约车|写字间"

YEAR_RULES = [
    (r"高铁", 2008), (r"智能手机|微信|扫码|网约车|外卖|网购|短视频|直播", 2011),
    (r"手机", 1996), (r"互联网|上网|网吧|QQ", 1998),
    (r"彩电|冰箱|洗衣机|空调", 1986), (r"电视机|电视", 1978),
    (r"包产到户|化肥|杂交稻", 1979),
    (r"打工|南下|流水线", 1988), (r"下岗", 1994),
    (r"按揭|房贷", 1998), (r"新冠|核酸|封控", 2020),
]


def _is_memory(text):
    return any(w in text for w in MEMORY_WORDS)


def _text_issues(text, st, age, year, sets=None):
    """文本与处境的冲突检查：同一套规则，既用于生成时校验，也用于整条人生的事后审计。"""
    out = []
    fl = st.get("flags", {})
    prof = st["profile"]
    sets = sets or {}
    memory = _is_memory(text)
    if re.search(R_SPOUSE, text) and not fl.get("married") \
            and not sets.get("married") and not memory:
        out.append("写了配偶，但人物未婚（也没在事件里成家）")
    if re.search(R_EX, text) and not (fl.get("ever_married") or fl.get("married")) and not memory:
        out.append("写了前妻/前夫，但人物从未结婚")
    if re.search(R_CHILD, text) and not fl.get("children") and not sets.get("children"):
        out.append("写了子女，但人物没有孩子（也没在本事件里生育）")
    if re.search(R_GRAND, text):
        cb = fl.get("child_born_age")
        ca = (age - cb) if cb else 0
        if not fl.get("children") or ca < 22:
            out.append(f"写了孙辈，但子女仅 {ca} 岁（至少 22 岁才可能有下一代）")
    if re.search(R_PARENT, text) and not fl.get("parents") and not memory \
            and "parents" not in sets:
        out.append("写了父母在世，但父母已故（回忆/上坟可以，需写成回忆）")
    if re.search(R_RETIRE, text) and age < 50 and not sets.get("retired"):
        out.append(f"{age} 岁写了退休/养老金，不合常理")
    if re.search(R_PRIMARY, text) and age > 24:
        out.append(f"{age} 岁写了上学，不合常理")
    if re.search(R_HIGH, text) and not (14 <= age <= 32):
        out.append(f"{age} 岁写了高考/大学，不合常理")
    if re.search(R_WORK, text) and age < 14:
        out.append(f"{age} 岁写了做工，不合常理")
    if re.search(R_DRIVE, text) and age < 18:
        out.append(f"{age} 岁写了开车，不合常理")

    if re.search(R_POOR, text) and prof["family"]["class"] not in ("贫困", "温饱"):
        out.append(f"阶层是{prof['family']['class']}，不该出现赤贫农村的场景")
    if re.search(R_URBAN, text) and not prof["birth"].get("urban"):
        out.append("人物住在村庄/小镇，不该出现地铁、写字楼、月供这类城市场景")

    for pat, y0 in YEAR_RULES:
        if re.search(pat, text) and year < y0:
            out.append(f"{year} 年还没有「{re.search(pat, text).group(0)}」（{y0} 年才出现）")

    return out


def _people_issues(ev, st, age, year, text, slot):
    """出场人物与历史联动的校验：人不能凭空来，旧事不能凭空接。"""
    err = []
    cast = st.get("cast") or {}
    hist_age = {h["age"] for h in st.get("history", [])}
    hist_map = {h["age"]: h for h in st.get("history", [])}

    ppl = ev.get("people")
    if ppl is not None and not isinstance(ppl, list):
        err.append("people 必须是数组")
        ppl = []
    ppl = ppl or []
    if len(ppl) > 3:
        err.append(f"people 写了 {len(ppl)} 个人，一年最多 3 个（其余留到别的年份）")

    seen, new_names = set(), []
    for i, p in enumerate(ppl):
        if not isinstance(p, dict):
            err.append(f"people[{i}] 必须是对象")
            continue
        pid = p.get("id")
        if pid:
            if pid not in cast:
                err.append(f"people 引用了不存在的人物 {pid}："
                           f"旧人从 people.roster 里选，新人用 new 登记")
                continue
            c = cast[pid]
            if pid in seen:
                err.append(f"{pid}（{c['name']}）在 people 里重复了")
            seen.add(pid)
            if c.get("dead_age") is not None:
                if not _is_memory(text) and p.get("recall_age") is None:
                    err.append(f"{c['name']} 已在 {c['dead_age']} 岁那年去世，"
                               f"只能出现在回忆里：要么带上 recall_age 指回他活着的那年，"
                               f"要么把场景写成遗物、上坟、梦、旧照片")
            ra = p.get("recall_age")
            if ra is not None:
                if not isinstance(ra, int):
                    err.append(f"people[{i}].recall_age 必须是整数年份（年龄）")
                elif ra >= age:
                    err.append(f"{c['name']} 的 recall_age={ra}，不能是今年或以后")
                elif ra not in hist_age:
                    err.append(f"{c['name']} 的 recall_age={ra}：这个人那年没有出场记录，"
                               f"要挂旧事请用真实经历过的年份 {sorted(hist_age)[-6:]}")
        elif p.get("new"):
            nw = p["new"]
            if not isinstance(nw, dict):
                err.append(f"people[{i}].new 必须是对象")
                continue
            name = str(nw.get("name") or "").strip()
            role = str(nw.get("role") or "").strip()
            mark = str(nw.get("mark") or "").strip()
            if len(name) < 2:
                err.append(f"新人物 {i} 缺 name（至少 2 个字）")
            if not role:
                err.append(f"新人物「{name}」缺 role：一句话说清他是谁的什么人")
            if len(mark) < 4:
                err.append(f"新人物「{name}」缺 mark：一个能反复用的身体细节"
                           f"（手上的动作、口音、随身的东西），否则下次认不出他")
            if len(name) >= 2 and name in {c.get("name") for c in cast.values()}:
                err.append(f"「{name}」已经在册，直接用 id 引用，不要重复登记")
            rel = nw.get("rel")
            if rel and rel not in REL_ZH:
                err.append(f"新人物 rel 只能是 {list(REL_ZH)}")
            _fl = st.get("flags") or {}
            _sets = ev.get("sets") or {}
            if re.search(R_SPOUSE, role) and not _fl.get("married") \
                    and not _sets.get("married"):
                err.append(f"「{name}」写成{re.search(R_SPOUSE, role).group(0)}，"
                           f"但人物现在是未婚。先让本事件 sets.married 成家，再登记")
            if re.search(R_CHILD, role) and not _fl.get("children") \
                    and not _sets.get("children"):
                err.append(f"「{name}」写成{re.search(R_CHILD, role).group(0)}，"
                           f"但人物没有孩子。先让本事件 sets.children 生育，再登记")
            na = nw.get("age")
            if na is not None and not isinstance(na, int):
                err.append("新人物 age 必须是整数")
            elif isinstance(na, int):
                kin = _kin_of(role)
                if kin and na < age + 16:
                    err.append(f"「{name}」是他的{'父亲' if kin == 'father' else '母亲'}，"
                               f"生他时至少 16 岁，今年至少该 {age + 16} 岁"
                               f"（现在写的是 {na} 岁）")
                elif kin and na > age + 58:
                    err.append(f"「{name}」{na} 岁才生他，太晚了（上限 {age + 58}）")
                elif re.search(r"发小|同学|同桌|同岁|一起长大|同班", role):
                    if abs(na - age) > 6:
                        err.append(f"「{name}」写成 {na} 岁，但他 {age} 岁，"
                                   f"差 {abs(na - age)} 岁算不上{role}")
                elif na < 0 or na > 100:
                    err.append(f"「{name}」年龄 {na} 不合理")
            new_names.append(name)
        else:
            err.append(f"people[{i}] 既没有 id 也没有 new，不知道说的是谁")

    # 写了名字却没登记 —— 这个人下次就接不上，等于白出场
    missing = [cid for cid, c in cast.items()
               if c.get("name") and c["name"] in text and cid not in seen]
    if missing:
        err.append("文本里出现了 " + "、".join(f'{cast[m]["name"]}({m})' for m in missing)
                   + "，但 people 没登记。漏登记的人下次就接不上了，"
                     "请在 people 里写上 id 和今年的 act")

    # 旧事引用
    links = ev.get("links") or []
    if links and not isinstance(links, list):
        err.append("links 必须是数组")
        links = []
    for l in links:
        if not isinstance(l, dict):
            err.append("links 每项必须是对象 {age, how}")
            continue
        la = l.get("age")
        if la not in hist_map:
            if isinstance(la, int) and la < age and age - la < 2:
                err.append(f"links 指向 {la} 岁，太近了（至少隔 2 年才算「以前的事」）")
            else:
                err.append(f"links 引用了不存在的年份 {la}；"
                           f"可引用的年份：{sorted(hist_age)[-8:]}")
        elif age - la < 2:
            err.append(f"links 指向 {la} 岁，至少隔 2 年才算「以前的事」")
        if not str(l.get("how") or "").strip():
            err.append(f"links.age={la} 缺 how：说清这件事和那年怎么接上的")

    # 脚本点名要回响的旧事
    if slot and slot.get("echo"):
        e = slot["echo"]
        ea = e.get("age")
        hit = any(isinstance(p, dict) and p.get("recall_age") == ea for p in ppl) or \
              any(isinstance(l, dict) and l.get("age") == ea for l in links)
        if not hit and not str(ev.get("echo_skip") or "").strip():
            what = f"{ea} 岁那年的「{e.get('title') or e.get('text')}」"
            err.append(f"本年该回响 {what}，但 people/links 都没接上。"
                       f"要么接住，要么在 echo_skip 里写一句为什么接不上")

    # 谁在这一年里走了，要显式标出来，否则下次 brief 还会把他推出来
    for p in ppl:
        if not isinstance(p, dict):
            continue
        if p.get("dies") and not p.get("id"):
            err.append("people 里只有旧人（id）才能标 dies，新登记的人不会当年就死")

    return err


def validate_event(ev, st, ctx, slot=None):
    """生成事件的硬校验。返回错误列表，空列表表示通过。"""
    err = []
    if not isinstance(ev, dict):
        return ["事件必须是 JSON 对象"]

    title = str(ev.get("title", "")).strip()
    hook = str(ev.get("hook", "")).strip()
    why = str(ev.get("why", "")).strip()
    text = title + " " + hook + " " + why
    age, year = ctx["age"], ctx["year"]
    fl = st.get("flags", {})
    prof = st["profile"]

    if not (3 <= len(title) <= 20):
        err.append(f"title 长度 {len(title)}，应为 3-20 字")
    if not (12 <= len(hook) <= 110):
        err.append(f"hook 长度 {len(hook)}，应为 12-110 字")
    if len(why) < 8:
        err.append("why 缺失或过短：必须一句话说明这件事为什么发生在此时此地")

    slot = slot or ctx.get("slot")
    if slot:
        if ev.get("valence") not in ("pos", "neg", "mix", "neu"):
            err.append("valence 必须是 pos/neg/mix/neu")
        if ev.get("category") and ev["category"] != slot["category"]:
            err.append(f"category 应为 {slot['category']}（{slot['category_zh']}），"
                       f"实为 {ev['category']}")
        if slot["valence"] in ("pos", "neg") and ev.get("valence") != slot["valence"]:
            err.append(f"本年基调是 {slot['valence']}，事件方向不符")
        # 方向不能自相矛盾
        eff = ev.get("effects") or {}
        net = sum(v for v in eff.values() if isinstance(v, (int, float)))
        if ev.get("valence") == "pos" and net < 0:
            err.append("标了 pos，但各项影响合计为负（" + str(net) + "）")
        if ev.get("valence") == "neg" and net > 0:
            err.append("标了 neg，但各项影响合计为正（" + str(net) + "）")

    eff = ev.get("effects")
    if not isinstance(eff, dict) or not eff:
        err.append("effects 必须是非空对象")
        eff = {}
    else:
        bad = [k for k in eff if k not in ATTRS]
        if bad:
            err.append(f"effects 含非法键 {bad}，只允许 {ATTRS}")
        for k, v in eff.items():
            if k in ATTRS and not isinstance(v, int):
                err.append(f"effects.{k} 必须是整数")
        if slot:
            # 改变状态的事（成家、生育、送走长辈）本就更重，放宽额度
            major = bool(ev.get("sets"))
            budget = min(24, slot["budget"] + (8 if major else 0))
            per = min(9, slot["per_attr"] + (2 if major else 0))
            total = sum(abs(v) for k, v in eff.items()
                        if k in ATTRS and isinstance(v, (int, float)))
            if total > budget:
                err.append(f"影响过大：合计 {total}，本年上限 {budget}")
            for k, v in eff.items():
                if k in ATTRS and isinstance(v, int) and abs(v) > per:
                    err.append(f"effects.{k}={v} 超出单项上限 {per}")

    # 自陈前提
    req = ev.get("requires") or {}
    if req.get("married") and not fl.get("married"):
        err.append("requires.married 但人物未婚")
    if req.get("parents") and not fl.get("parents"):
        err.append("requires.parents 但父母已故")
    if req.get("children_min") and (fl.get("children") or 0) < req["children_min"]:
        err.append("requires.children_min 不满足")
    if req.get("child_age_min"):
        cb = fl.get("child_born_age")
        ca = (age - cb) if cb else 0
        if ca < req["child_age_min"]:
            err.append(f"requires.child_age_min={req['child_age_min']}，实际子女 {ca} 岁")

    sets = ev.get("sets") or {}
    if "children" in sets and not isinstance(sets["children"], int):
        err.append("sets.children 必须是整数")
    if sets.get("married") and age < 16:
        err.append(f"{age} 岁成家不合常理")

    err.extend(_text_issues(text, st, age, year, sets))
    err.extend(_people_issues(ev, st, age, year, text, slot))

    # 重复
    for h in st.get("history", [])[-24:]:
        old = h.get("title") or ""
        if not old:
            continue
        if _similar(title, old) >= 0.5:
            err.append(f"与 {h['age']} 岁的「{old}」太像（相似度 {_similar(title, old):.0%}），"
                       f"换一件事")
            break
    # 后续承诺
    for t in ev.get("then", []) or []:
        if not isinstance(t, dict) or not t.get("text"):
            err.append("then 每项需有 text")
            break
        if len(t["text"]) > 46:
            err.append("then.text 超过 46 字")
        if not (1 <= int(t.get("within", 3)) <= 5):
            err.append("then.within 必须在 1-5 年之间")

    # 必须兑现的旧账
    if slot and slot.get("must_resolve"):
        ids = set(ev.get("resolves") or [])
        miss = [q["pid"] for q in slot["must_resolve"] if q["pid"] not in ids]
        if miss:
            err.append(f"以下旧事已到期限，必须在 resolves 里交代：{miss}")

    return err
# ------------------------------------------------------------------ 子命令
def cmd_new(a):
    seed = a.seed or str(random.randrange(10 ** 12))
    prof = build(seed, a.country, a.birth_year, a.age_min, a.age_max)
    st = {
        "meta": {"id": prof["id"], "seed": seed,
                 "created": datetime.now().isoformat(timespec="seconds"),
                 "engine": "sim-life/1.0"},
        "profile": prof,
        "now": {"age": prof["birth"]["age_now"], "year": datetime.now().year,
                "place": prof["birth"]["place"],
                "region": REGION_OF.get(prof["birth"]["country"], "其他")},
        "attrs": dict(prof["attrs"]),
        "status": default_status(prof["birth"]["age_now"]),
        "assets": prof["family"]["housing"],
        "history": [],
        "ended": False,
        "death": None,
        "turns": 0,
        "fail_streak": 0,
        "used_events": [],
        "event_age": {},
        "tag_last": {},
        "quiet_years": 0,
        "pending": [],
        "cast": {},
        "cast_seq": 0,
        "loose_ends": [],
        "echoed": [],
        "flags": {"married": False, "children": 0, "parents": True,
                  "child_born_age": None},
    }
    out = a.out or "./sim-lives"
    path = os.path.join(out, prof["id"], "state.json")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    print(json.dumps({"state_path": os.path.abspath(path), "profile": prof,
                      "attrs": st["attrs"]}, ensure_ascii=False, indent=2))


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path, st):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def cmd_tick(a):
    st = _load(a.state)
    if st.get("ended"):
        print(json.dumps({"error": "这条命已经结束，请用 end/poster 收尾", "ended": True},
                         ensure_ascii=False))
        return
    flags = _parse_flags(a.flag)
    out = step(st, a.kind, a.bonus, a.difficulty, a.years, a.no_event,
               a.action, a.status, a.cause, flags=flags)
    _save(a.state, st)
    out["state_path"] = os.path.abspath(a.state)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_adjust(a):
    """阶段 1 的设定变更：只改这一个样本，不重抽"""
    st = _load(a.state)
    p = st["profile"]
    rng = random.Random(f'{st["meta"]["seed"]}:adjust')

    if a.country:
        row = next((c for c in COUNTRIES if c[0] == a.country.upper()), None)
        if not row:
            raise SystemExit(f"未知国家代码: {a.country}")
        p["birth"]["country"] = row[0]
        p["birth"]["country_zh"] = row[1]
        p["culture"] = row[6]
        p["birth"]["place"] = rng.choice(row[7])
        p["life_expectancy"] = round(row[3] + rng.uniform(-9, 9), 1)
        st["now"]["region"] = REGION_OF.get(row[0], "其他")
        st["now"]["place"] = p["birth"]["place"]
    if a.place:
        p["birth"]["place"] = a.place
        st["now"]["place"] = a.place
    if a.sex:
        p["sex"] = a.sex
    if a.traits:
        p["traits"] = [t.strip() for t in a.traits.split(",") if t.strip()][:2]
    if a.school_class:
        p["family"]["class"] = a.school_class
        p["family"]["housing"] = rng.choice(HOUSING[a.school_class])
        base = CLASS_BASE[a.school_class]
        st["attrs"] = {
            "health": clamp(base[0] + rng.randint(-8, 8)),
            "wealth": clamp(base[1] + rng.randint(-6, 8)),
            "bond":   clamp(base[2] + rng.randint(-10, 10)),
            "spirit": clamp(base[3] + rng.randint(-8, 8)),
            "skill":  clamp(base[4] + rng.randint(-8, 8)),
            "fame":   clamp(base[5] + rng.randint(0, 4)),
        }
    if a.age is not None:
        st["now"]["age"] = a.age
        st["now"]["year"] = p["birth"]["year"] + a.age
        st["status"] = default_status(a.age)
    _save(a.state, st)
    print(json.dumps({"adjusted": True, "profile": p, "attrs": st["attrs"],
                      "now": st["now"]}, ensure_ascii=False, indent=2))


def _parse_flags(items):
    out = {}
    for kv in items or []:
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        out[k.strip()] = v.strip() not in ("0", "false", "no", "")
    return out


def cmd_brief(a):
    """掷出本年的槽位与上下文，等模型生成事件。不改属性。"""
    st = _load(a.state)
    if st.get("ended"):
        print(json.dumps({"error": "这条命已经结束", "ended": True}, ensure_ascii=False))
        return
    if a.discard:
        st.pop("pending_turn", None)
        st.pop("pending_meta", None)
    if st.get("pending_turn"):
        print(json.dumps({"error": "上一轮 brief 还没 commit",
                          "hint": "先 commit 或丢弃后再 brief",
                          "slot": st["pending_turn"].get("slot")}, ensure_ascii=False))
        sys.exit(2)
    if a.action:
        st["status"] = a.status or st.get("status")
    seq = st.get("brief_seq", 0) + 1
    st["brief_seq"] = seq
    brief = make_brief(st, a.kind, a.bonus, a.difficulty, a.years,
                       a.action, no_event=a.no_event,
                       rng=random.Random(f'{st["meta"]["seed"]}:{st["turns"]}:brief:{seq}'))
    ctx = brief.pop("ctx")
    st["pending_turn"] = ctx
    st["pending_meta"] = {"action": a.action, "kind": a.kind}
    _save(a.state, st)
    if a.years > 1 and brief["when"]["age"] > 25:
        brief["warning"] = (f"一次跨了 {a.years} 年，结束时已 {brief['when']['age']} 岁。"
                            f"快进只用于童年蒙太奇或用户明确要求，否则会跳过整段人生")
    brief["state_path"] = os.path.abspath(a.state)
    print(json.dumps(brief, ensure_ascii=False, indent=2))


def cmd_commit(a):
    """接收模型生成的事件：校验 → 通过则落到状态上。"""
    st = _load(a.state)
    ctx = st.get("pending_turn")
    if not ctx:
        print(json.dumps({"ok": False, "errors": ["没有待提交的 brief，先跑 brief"]},
                         ensure_ascii=False))
        sys.exit(2)

    ev = None
    if a.event == "-":
        ev = json.load(sys.stdin)
    elif a.event:
        with open(a.event, encoding="utf-8") as f:
            ev = json.load(f)

    slot = ctx.get("slot")
    action = (st.get("pending_meta") or {}).get("action", "")

    seed_people = None
    if getattr(a, "people", None):
        with open(a.people, encoding="utf-8") as f:
            seed = json.load(f)
        seed_people = seed.get("people") if isinstance(seed, dict) else seed
        perrs = _people_issues({"people": seed_people or []}, st, ctx["age"],
                               ctx["year"], "", None)
        perrs = [e for e in perrs if "recall_age" not in e and "links" not in e
                 and "该回响" not in e]
        if perrs:
            print(json.dumps({"ok": False, "errors": perrs}, ensure_ascii=False, indent=2))
            sys.exit(2)

    if slot is None and ev:
        errs = ["本年没有事件槽位（slot 为 null），不应提交事件"]
    elif slot is not None and ev is None:
        errs = ["本年有事件槽位，必须提交事件（或用 --fallback）"]
    else:
        errs = validate_event(ev, st, ctx, slot) if ev else []

    if errs and a.fallback:
        ev = pick_event(load_events(), ctx["age"], st["now"]["region"],
                        st["profile"]["family"]["class"], random.Random(
                            f'{st["meta"]["seed"]}:{st["turns"]}:fb'),
                        used=set(st.get("used_events", [])),
                        flags=st.get("flags", {}),
                        attrs=dict(ctx["before"], **_child_age(st, ctx["age"])),
                        event_age=st.get("event_age", {}),
                        tag_last=st.get("tag_last", {}),
                        last_rare=st.get("last_rare"),
                        pending=st.get("pending", []),
                        kind=ctx["kind"],
                        mood=(slot["valence"] if slot and slot["valence"] in ("pos", "neg")
                              else None))
        errs = []

    if errs:
        print(json.dumps({"ok": False, "errors": errs,
                          "hint": "按 errors 逐条改，然后重跑 commit；改不动可用 --fallback"},
                         ensure_ascii=False, indent=2))
        sys.exit(2)

    if ev is not None and slot and slot.get("echo") and not str(ev.get("echo_skip") or "").strip():
        ev["_echo_age"] = slot["echo"].get("age")

    out = _apply(st, ctx, ev, a.status, a.cause, _parse_flags(a.flag),
                 action if ev or action else "", rng=random.Random(
                     f'{st["meta"]["seed"]}:{st["turns"]}:commit'),
                 seed_people=seed_people)
    st.pop("pending_turn", None)
    st.pop("pending_meta", None)
    _save(a.state, st)
    out["ok"] = True
    out["state_path"] = os.path.abspath(a.state)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_audit(a):
    """事后审计：把整条人生回放一遍，找自相矛盾的地方。"""
    st = _load(a.state)
    issues = []

    # 用当时的 flags 快照回查文本
    for h in st.get("history", []):
        if not h.get("hook"):
            continue
        snap = {"profile": st["profile"], "flags": h.get("flags") or st.get("flags", {})}
        for e in _text_issues(f"{h['title']} {h['hook']}", snap, h["age"], h["year"]):
            issues.append({"age": h["age"], "year": h["year"], "title": h["title"],
                           "kind": "前后矛盾", "detail": e})

    # 同一件事五年内重演
    seen = {}
    for h in st.get("history", []):
        if not h.get("hook"):
            continue                      # 只有行动、没有事件的年份不参与去重
        k = h["title"]
        if k in seen and h["age"] - seen[k] < 5:
            issues.append({"age": h["age"], "year": h["year"], "title": k,
                           "kind": "重复", "detail": f"{h['age'] - seen[k]} 年内重演"})
        seen[k] = h["age"]

    # 状态倒退：父母一旦走了不会再回来
    prev = None
    for h in st.get("history", []):
        fl = h.get("flags")
        if not fl:
            continue
        if prev is not None and prev.get("parents") is False and fl.get("parents") is True:
            issues.append({"age": h["age"], "year": h["year"], "title": h["title"],
                           "kind": "状态倒退", "detail": "父母已故又复活"})
        prev = fl

    if st.get("death"):
        for h in st.get("history", []):
            if h["age"] > st["death"]["age"]:
                issues.append({"age": h["age"], "title": h["title"],
                               "kind": "时序", "detail": "死亡之后还有事件"})

    # 人物：死了不能再出场（回忆、遗物、上坟不算出场）
    cast = st.get("cast") or {}
    for cid, c in cast.items():
        da = c.get("dead_age")
        if da is None:
            continue
        for h in st.get("history", []):
            if h["age"] <= da or cid not in (h.get("people") or []):
                continue
            txt = f'{h.get("title") or ""} {h.get("hook") or ""}'
            if _is_memory(txt) or h.get("recall"):
                continue
            issues.append({"age": h["age"], "year": h["year"], "title": c["name"],
                           "kind": "人物",
                           "detail": f'{c["name"]} 在 {da} 岁那年已去世，'
                                     f'{h["age"]} 岁又以在场的身份出场了'})
    # 登记了名字却从未出现在任何一年的事件里
    used = set()
    for h in st.get("history", []):
        for p in (h.get("people") or []):
            used.add(p)
    for cid, c in cast.items():
        if cid in used:
            continue
        issues.append({"age": c.get("first_age"), "title": c["name"], "kind": "人物",
                       "detail": f'{c["name"]} 登记在册但没有任何事件的 people 引用它'})

    n = len(st.get("history", []))
    print(json.dumps({"ok": not issues, "checked": n, "issues": issues},
                     ensure_ascii=False, indent=2))


def cmd_show(a):
    st = _load(a.state)
    p = st["profile"]
    print(f'{p["name"]}｜{p["sex"]}｜{p["birth"]["year"]} 年生于 {p["birth"]["country_zh"]} '
          f'{p["birth"]["place"]}（{p["birth"]["settlement"]}）')
    print(f'家庭：{p["family"]["structure"]}／{p["family"]["class"]}／'
          f'兄弟姐妹 {p["family"]["siblings"]}／{p["family"]["housing"]}')
    print(f'性格：{"、".join(p["traits"])}　天赋：{p["gift"]["name"] if p["gift"] else "无"}')
    print(f'当前：{st["now"]["age"]} 岁（{st["now"]["year"]} 年）　预期寿命约 {p["life_expectancy"]} 岁')
    print("属性：" + "　".join(f'{ATTR_ZH[k]} {st["attrs"][k]}' for k in ATTRS))
    print(f'处境：{st["status"]}')
    fl = st.get("flags", {})
    fam = []
    fam.append("已婚" if fl.get("married") else "未婚")
    fam.append(f'子女 {fl.get("children", 0)}')
    fam.append("父母在" if fl.get("parents") else "父母已故")
    print("家庭：" + "／".join(fam))
    print(f'已推演 {st["turns"]} 轮　事件 {len(st["history"])} 条　'
          f'{"已结束" if st["ended"] else "进行中"}')
    op = _open_promises(st)
    if op:
        print(f'未了结 {len(op)} 件：')
        for q in op:
            print(f'  [{q["pid"]}] {q["text"]}（{q["until"]} 岁前）')
    le = st.get("loose_ends") or []
    if le:
        print(f'烂在过去的账 {len(le)} 件：')
        for q in le[-4:]:
            print(f'  {q.get("from")} 岁欠下的：{q.get("text")}')
    cast = st.get("cast") or {}
    if cast:
        age = st["now"]["age"]
        year = st["now"]["year"]
        alive = [(cid, c) for cid, c in cast.items() if _cast_alive(c, year)]
        print(f'人物 {len(alive)} 人在册（共登记 {len(cast)}）：')
        for cid, c in sorted(alive, key=lambda x: -x[1].get("bond", 50))[:8]:
            ca = _cast_age(c, age, year)
            tag = f'约 {ca} 岁' if ca is not None else ''
            owe = f'　⚠ {c["owed"]}' if c.get("owed") else ''
            print(f'  {cid} {c["name"]}（{c.get("role") or c.get("rel")}）'
                  f'　亲疏 {c.get("bond", 50)}　出场 {c.get("n", 1)} 次'
                  f'　上次 {c.get("last_age")} 岁　{tag}{owe}')
    if st.get("pending_turn"):
        print("⚠️ 有一轮 brief 尚未 commit")
    if st["ended"]:
        d = st["death"]
        print(f'结局：{d["year"]} 年（{d["age"]} 岁）　{d["cause"]}')


def cmd_end(a):
    st = _load(a.state)
    if not st["ended"]:
        st["ended"] = True
        st["death"] = {"age": st["now"]["age"], "year": st["now"]["year"],
                       "cause": a.cause or "未记录", "attrs": dict(st["attrs"])}
    elif a.cause:
        st["death"]["cause"] = a.cause
    _save(a.state, st)
    print(json.dumps({"ended": True, "death": st["death"],
                      "state_path": os.path.abspath(a.state)}, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="sim-life 人生引擎")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new")
    n.add_argument("--seed")
    n.add_argument("--country")
    n.add_argument("--birth-year", type=int)
    n.add_argument("--age-min", type=int, default=0)
    n.add_argument("--age-max", type=int, default=40)
    n.add_argument("--out")

    t = sub.add_parser("tick")
    t.add_argument("--state", required=True)
    t.add_argument("--kind", default="none",
                   choices=["none", "learn", "work", "social", "love", "health", "risk", "money"])
    t.add_argument("--action", default="")
    t.add_argument("--bonus", type=int, default=0, help="情境加成 -10..20")
    t.add_argument("--difficulty", type=int, default=0)
    t.add_argument("--years", type=int, default=1, help="推进年数（快进用）")
    t.add_argument("--no-event", action="store_true")
    t.add_argument("--status", default="", help="一句话写回当前处境（供叙事与海报使用）")
    t.add_argument("--flag", action="append", default=[], metavar="K=V",
                   help="更新人物状态标记，如 --flag married=1 --flag children=2 --flag parents=0")
    t.add_argument("--cause", default="")

    b = sub.add_parser("brief", help="掷出本年事件槽位与约束，等模型生成")
    b.add_argument("--state", required=True)
    b.add_argument("--kind", default="none",
                   choices=["none", "learn", "work", "social", "love", "health", "risk", "money"])
    b.add_argument("--action", default="", help="这一年打算做什么，一句")
    b.add_argument("--bonus", type=int, default=0)
    b.add_argument("--difficulty", type=int, default=0)
    b.add_argument("--years", type=int, default=1)
    b.add_argument("--no-event", action="store_true")
    b.add_argument("--status", default="")
    b.add_argument("--discard", action="store_true", help="丢弃上一轮未提交的 brief")

    c = sub.add_parser("commit", help="提交模型生成的事件并校验")
    c.add_argument("--state", required=True)
    c.add_argument("--event", help="事件 JSON 文件路径，- 表示 stdin")
    c.add_argument("--people", help="单独登记人物的 JSON（平年/童年蒙太奇用）")
    c.add_argument("--status", default="")
    c.add_argument("--cause", default="")
    c.add_argument("--flag", action="append", default=[], metavar="K=V")
    c.add_argument("--fallback", action="store_true",
                   help="校验不过时回落到内置库（保底）")

    adj = sub.add_parser("adjust", help="阶段 1 的设定变更")
    adj.add_argument("--state", required=True)
    adj.add_argument("--country")
    adj.add_argument("--place")
    adj.add_argument("--sex", choices=["男", "女"])
    adj.add_argument("--school-class", dest="school_class",
                     choices=["贫困", "温饱", "工薪", "中产", "富裕"])
    adj.add_argument("--age", type=int)
    adj.add_argument("--traits", help="两个特质，逗号分隔")

    au = sub.add_parser("audit", help="回放整条人生，找自相矛盾处")
    au.add_argument("--state", required=True)

    s = sub.add_parser("show")
    s.add_argument("--state", required=True)

    e = sub.add_parser("end")
    e.add_argument("--state", required=True)
    e.add_argument("--cause", default="")

    a = ap.parse_args()
    {"new": cmd_new, "tick": cmd_tick, "brief": cmd_brief, "commit": cmd_commit,
     "show": cmd_show, "end": cmd_end, "adjust": cmd_adjust,
     "audit": cmd_audit}[a.cmd](a)


if __name__ == "__main__":
    main()
