#!/usr/bin/env python3
"""故事板 → 逐格生图 prompt 编译器（fore-vip-comic）。

用法:
    python build_prompts.py <storyboard.json> [output.json]

输出含 model_params 与每格最终 prompt。内置两组断言：
1. 一致性：除 scene / emotion 外，所有格的固定层必须逐字相同。
2. 演进性：必须先定主题路线 route；四格的 shot/state/light/emotion
   必须多样，scene 描述不得两两雷同——拦截"四格同一构图"的失败模式。

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


def check_evolution(route, panels):
    if not route:
        raise SystemExit("缺少 route：必须先写一条主题路线（起点 → 转折 → 终点），不允许直接分镜")
    n = len(panels)
    for i, p in enumerate(panels, 1):
        for dim in EVOLVE_DIMS + ("emotion",):
            if not str(p.get(dim, "")).strip():
                raise SystemExit(f"panel{i}: 缺少演进标注 {dim}（shot/state/light/emotion 必填，见 narrative-patterns.md）")
    for dim in EVOLVE_DIMS + ("emotion",):
        distinct = len({str(p.get(dim)).strip().lower() for p in panels})
        if distinct < min(3, n):
            raise SystemExit(
                f"演进闸门：{dim} 只有 {distinct} 种取值（四格需 ≥3 种）。"
                f"四格不能同一景别/场景状态/光线/情绪——按主题路线重新设计每格，禁止只换道具。")
    scenes = [tokens(str(p.get("scene", ""))) for p in panels]
    for i in range(n):
        for j in range(i + 1, n):
            sim = jaccard(scenes[i], scenes[j])
            if sim > 0.55:
                raise SystemExit(
                    f"演进闸门：panel{i+1} 与 panel{j+1} 的 scene 雷同度 {sim:.2f} > 0.55，"
                    "判定为同一画面的复制。请改写景别（overhead/close-up/wide）、场景状态或光线。")


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

    check_evolution(route, panels)

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
    print("check: 固定层逐字一致；主题路线已定；shot/state/light/emotion 四格演进；scene 无雷同")


if __name__ == "__main__":
    main()
