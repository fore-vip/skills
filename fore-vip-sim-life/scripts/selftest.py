#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sim-life 自检：人物、回响、校验规则。

直接调用引擎函数，不经过 CLI，所以不受掷骰影响，每次结果都一样。
用法:  python3 scripts/selftest.py
退出码 0 = 全过。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import life_engine as E  # noqa: E402
from sample_life import build  # noqa: E402

AGE = 30
YEAR = 2056
PASS, FAIL = [], []


def make_state():
    prof = build("selftest", "CN", 2026, 30, 30)
    return {
        "meta": {"id": "t", "seed": "selftest", "engine": "sim-life/selftest"},
        "profile": prof,
        "now": {"age": AGE, "year": YEAR, "place": prof["birth"]["place"],
                "region": E.REGION_OF.get(prof["birth"]["country"], "其他")},
        "attrs": dict(prof["attrs"]),
        "status": "在城里做工",
        "history": [
            {"age": AGE - 12, "year": YEAR - 12, "title": "进厂头一天",
             "hook": "师傅把一把扳手放在他手里，握的位置正好。",
             "valence": "pos", "people": ["c1"], "links": [], "flags": {}},
            {"age": AGE - 6, "year": YEAR - 6, "title": "楼下搬来一家人",
             "hook": "一床棉被搭在绳子上，被角补着两种颜色的布。",
             "valence": "neu", "people": ["c2"], "links": [], "flags": {}},
        ],
        "cast": {
            "c1": {"name": "赵德发", "role": "带他的师傅", "rel": "师徒",
                   "sex": "男", "mark": "右手中指缺半截，说话前先清嗓子",
                   "bond": 62, "born_year": YEAR - 54, "first_age": AGE - 12,
                   "last_age": AGE - 4, "last_year": YEAR - 4, "n": 5,
                   "last_act": "替他把罚款认了", "owed": "这份人情还没还",
                   "dead_age": None},
            "c2": {"name": "周凤兰", "role": "住在楼下的邻居", "rel": "邻里",
                   "sex": "女", "mark": "数钱时要用手指蘸一下嘴",
                   "bond": 48, "born_year": YEAR - 72, "first_age": AGE - 6,
                   "last_age": AGE - 6, "last_year": YEAR - 6, "n": 1,
                   "dead_age": AGE - 3, "dead_year": YEAR - 3},
        },
        "cast_seq": 2, "loose_ends": [], "echoed": [], "pending": [],
        "flags": {"married": False, "children": 0, "parents": True,
                  "child_born_age": None},
        "turns": 1, "quiet_years": 0, "used_events": [], "event_age": {},
        "tag_last": {}, "ended": False, "death": None,
    }


def ctx(echo=None):
    st = make_state()
    slot = {"category": "social", "category_zh": "人情", "valence": "neu",
            "intensity": 2, "budget": 14, "per_attr": 6}
    if echo:
        slot["echo"] = echo
    return st, {
        "age": AGE, "year": YEAR, "before": dict(st["attrs"]),
        "roll": None, "delta": {}, "drift": {}, "kind": "social", "years": 1,
        "action": "走动", "fail_streak": 0, "slot": slot,
    }


BASE = {"title": "他站在门口没进来",
        "hook": "门开着，他在门槛外面站了一会儿，手里捏着一张折过两次的纸。",
        "why": "这几天厂里在传名单，谁都怕自己的名字在上面。",
        "valence": "neu", "category": "social", "effects": {"spirit": -3}}


def event(**kw):
    e = dict(BASE)
    e.update(kw)
    return e


def check(name, expect, ev, echo=None):
    """expect: 'pass' 应当通过；'fail' 应当被拒"""
    st, c = ctx(echo)
    errs = E.validate_event(ev, st, c, c["slot"])
    ok = not errs
    good = ok == (expect == "pass")
    tag = "✓" if good else "✗"
    msg = "通过" if ok else errs[0]
    print(f"  {tag} {name}: {'通过' if ok else '拒绝'} → {msg[:78]}")
    (PASS if good else FAIL).append(name)


def main():
    echo = {"age": AGE - 12, "kind": "old_event", "title": "进厂头一天",
            "hook": "师傅把扳手放在他手里。", "years_ago": 12, "ask": "要接上"}

    print("人物：")
    check("引用不存在的 id", "fail",
          event(people=[{"id": "c99", "act": "走过来"}]))
    check("旧人正常出场", "pass",
          event(people=[{"id": "c1", "act": "把烟递过来"}], ties={"c1": 3}))
    check("新人物缺 mark", "fail",
          event(people=[{"new": {"name": "王大江", "role": "同组的伙计",
                                 "rel": "同事", "age": 33}}]))
    check("新人物缺 role", "fail",
          event(people=[{"new": {"name": "王大江", "mark": "手上有机油味",
                                 "rel": "同事", "age": 33}}]))
    check("新人物齐全", "pass",
          event(people=[{"new": {"name": "王大江", "role": "同组的伙计",
                                 "rel": "同事", "mark": "手上有机油味",
                                 "age": 33}}]))
    check("一年四个人", "fail",
          event(people=[{"new": {"name": f"路人{i}", "role": "伙计", "rel": "同事",
                                 "mark": "手里捏着打火机", "age": 30}}
                        for i in range(4)]))
    check("写了名字没登记", "fail",
          event(hook="赵德发在门口站着，右手中指那半截在灯下看得很清楚。"))
    check("死人以在场身份出场", "fail",
          event(people=[{"id": "c2", "act": "端着一碗腌菜上楼"}]))
    check("死人写在回忆里", "pass",
          event(hook="他翻出一只空碗，碗底留着一点褐色的印子，是那年楼下送的。",
                people=[{"id": "c2", "act": "想起那碗腌菜",
                         "recall_age": AGE - 6}]))
    check("未婚登记妻子", "fail",
          event(people=[{"new": {"name": "何秀英", "role": "妻子", "rel": "恋人",
                                 "mark": "生气时只把碗摆得很响", "age": 28}}]))
    check("父母年龄不够", "fail",
          event(people=[{"new": {"name": "李秀兰", "role": "母亲", "rel": "亲属",
                                 "mark": "洗碗前把袖子绕两圈", "age": 27}}]))

    print("回响：")
    check("recall_age 不是真实年份", "fail",
          event(people=[{"id": "c1", "act": "提起以前", "recall_age": AGE - 9}]))
    check("links 指向未来", "fail",
          event(links=[{"age": AGE + 3, "how": "以后的事"}]))
    check("links 太近", "fail",
          event(links=[{"age": AGE - 1, "how": "去年的事"}]))
    check("links 缺 how", "fail",
          event(links=[{"age": AGE - 12}]))
    check("links 正常", "pass",
          event(links=[{"age": AGE - 12, "how": "同一把扳手，换他递给别人"}]))
    check("echo 未接住", "fail", event(), echo=echo)
    check("echo 用 recall_age 接住", "pass",
          event(people=[{"id": "c1", "act": "提起那天", "recall_age": AGE - 12}]),
          echo=echo)
    check("echo_skip 放行", "pass",
          event(echo_skip="这一年他人在外地，够不着这件事"), echo=echo)

    print("落地：")
    st, c = ctx()
    ev = event(title="他站在门口没进来",
               people=[{"id": "c1", "act": "把纸接过去看了两眼"},
                       {"new": {"name": "王大江", "role": "同组的伙计",
                                "rel": "同事", "mark": "手上有机油味", "age": 33}}],
               ties={"c1": 5})
    errs = E.validate_event(ev, st, c, c["slot"])
    if errs:
        print(f"  ✗ 落地前校验失败：{errs[0]}")
        FAIL.append("落地")
    else:
        E._apply(st, c, ev, "事情过去了一些", None, None, "走动",
                 rng=__import__("random").Random("x"))
        cast = st["cast"]
        new_id = next((k for k, v in cast.items() if v["name"] == "王大江"), None)
        checks = [
            ("新人物拿到 id", new_id == "c3"),
            ("老人出场次数 +1", cast["c1"]["n"] == 6),
            ("老人亲疏变化", cast["c1"]["bond"] == 67),
            ("老人最后出场年份", cast["c1"]["last_age"] == AGE),
            ("history 记下 cid", st["history"][-1]["people"][:2] == ["c1", "c3"]),
        ]
        for name, ok in checks:
            print(f'  {"✓" if ok else "✗"} {name}')
            (PASS if ok else FAIL).append(name)

    print(f"\n通过 {len(PASS)}　失败 {len(FAIL)}")
    if FAIL:
        print("失败项：" + "、".join(FAIL))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
