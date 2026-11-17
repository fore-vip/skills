#!/usr/bin/env python3
"""故事板 → 逐格生图 prompt 编译器（fore-vip-comic）。

用法:
    python build_prompts.py <storyboard.json> [output.json]

校验分两类：
1. 硬断言（结构性/确定性，不满足即报错）：style 已填、route 已填、四维标注齐全、
   scene 非空且为英文、固定层四格逐字一致。
2. 软提醒（创意性，只提示不阻断）：四格演进维度过于同质、scene 描述雷同。
   剧情是可无限扩展的路线，不用数值阈值卡死——提醒时给出参照模板，
   让调用者照着模板扩展（见 references/narrative-patterns.md）。

输入规范见 ../references/prompt-compiler.md。
"""

import json
import re
import sys

CJK = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff]")
DEFAULT_NEGATIVE = (
    "Absolutely NO text, NO letters, NO numbers, NO speech bubbles, "
    "NO captions, NO watermark anywhere in the image."
)
CHAR_FIELDS = ("role", "build", "hair", "eyes", "outfit", "colors", "signature")
EVOLVE_DIMS = ("shot", "state", "light")
STOP = set("a an the at of on in over under with and to for from as is are by into near beside".split())
REFERENCE_TEMPLATE = (
    "参照模板（可无限套用）：1 wide 交代起点 → 2 overhead/close 加压堆叠 → "
    "3 extreme_close 聚焦峰值 → 4 wide pull-back 收束。"
    "槽位与顺序可自由替换、增删；见 references/narrative-patterns.md「提示词参照模板」。"
)


def build_character(c):
    if isinstance(c, str):
        return c.strip()
    if not isinstance(c, dict):
        raise SystemExit("character 必须是字符串或对象")
    vals = [str(c[k]).strip() for k in CHAR_FIELDS if c.get(k)]
    if not vals:
        raise SystemExit("character 对象至少填写 role / hair / outfit / colors 中的一项")
    return ", ".join(vals)


def tokens(s):
    return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def evolution_notes(route, panels):
    """结构性必填仍硬校验；创意性同质只返回提醒，不阻断。"""
    if not route:
        raise SystemExit("缺少 route：必须先写一条主题路线（起点 → 转折 → 终点）")
    n = len(panels)
    for i, p in enumerate(panels, 1):
        for dim in EVOLVE_DIMS + ("emotion",):
            if not str(p.get(dim, "")).strip():
                raise SystemExit(f"panel{i}: 缺少演进标注 {dim}（shot/state/light/emotion 必填，照参照模板填写即可）")

    notes = []
    for dim in EVOLVE_DIMS + ("emotion",):
        distinct = len({str(p.get(dim)).strip().lower() for p in panels})
        if distinct < min(3, n):
            notes.append(f"{dim} 只有 {distinct} 种取值——可参照模板换一个视角，不必硬凑数量")
    scenes = [tokens(str(p.get("scene", ""))) for p in panels]
    for i in range(n):
        for j in range(i + 1, n):
            sim = jaccard(scenes[i], scenes[j])
            if sim > 0.55:
                notes.append(f"panel{i+1} 与 panel{j+1} scene 雷同度 {sim:.2f}——参照模板改写其中一格的景别或场景状态")
    return notes


def compile_storyboard(sb):
    style = str(sb.get("style", "")).strip()
    comp = str(sb.get("composition", "Composition leaves the upper third of the panel almost completely empty for a speech bubble.")).strip()
    frame = str(sb.get("character_frame", "Semi-realistic casual character design:")).strip()
    neg = str(sb.get("negative", DEFAULT_NEGATIVE)).strip()
    route = str(sb.get("route", "")).strip()
    if not style:
        raise SystemExit("缺少 style：必须从 references/styles.md 逐字复制画风前缀")
    char = build_character(sb.get("character"))
    fixed = [style, f"{frame} {char}.", comp]
    panels = sb.get("panels")
    if not isinstance(panels, list) or not panels:
        raise SystemExit("panels 必须是非空数组")

    notes = evolution_notes(route, panels)

    out = []
    for i, p in enumerate(panels, 1):
        scene = str(p.get("scene", "")).strip()
        emo = str(p.get("emotion", "")).strip()
        if not scene:
            raise SystemExit(f"panel{i}: 缺少 scene")
        segs = fixed + [scene, emo, neg]
        full = " ".join(s for s in segs if s)
        if CJK.search(full):
            raise SystemExit(f"panel{i}: prompt 含中日韩文字，模型可能据此绘制中文——把 scene/emotion 改成英文")
        out.append({
            "panel": i,
            "prompt": full,
            "layers": {"style": style, "character": char, "composition": comp,
                       "scene": scene, "emotion": emo, "negative": neg},
            "evolution": {d: str(p.get(d)).strip() for d in EVOLVE_DIMS + ("emotion",)},
        })

    for p in out[1:]:
        a, b = out[0]["layers"], p["layers"]
        for key in ("style", "character", "composition", "negative"):
            if a[key] != b[key]:
                raise SystemExit(f"panel{p['panel']}: 固定层 {key} 与 panel1 不一致")
    return {
        "route": route,
        "model_params": {"size": "1536x1024", "quality": "high",
                         "revise": False, "background": "opaque"},
        "reference_policy": {
            "anchor": "用角色定妆图作 image1；input_fidelity 先做小样确定取值",
            "serial": True, "distinct_output_dir": True,
        },
        "reference_template": REFERENCE_TEMPLATE,
        "warnings": notes,
        "panels": out,
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法: python build_prompts.py <storyboard.json> [output.json]")
    with open(sys.argv[1], encoding="utf-8") as fh:
        sb = json.load(fh)
    result = compile_storyboard(sb)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("saved", sys.argv[2])
    else:
        print(text)
    if result["warnings"]:
        for note in result["warnings"]:
            print("提醒:", note)
        print("参照:", result["reference_template"])
    print("check: 固定层逐字一致；路线与四维标注齐全；创意性同质只提醒、不阻断")


if __name__ == "__main__":
    main()
