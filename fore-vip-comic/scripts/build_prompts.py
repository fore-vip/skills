#!/usr/bin/env python3
"""故事板 → 逐格生图 prompt 编译器（fore-vip-comic）。

用法:
    python build_prompts.py <storyboard.json> [output.json]

输出含 model_params 与每格最终 prompt。内置一致性断言：
除 scene / emotion 两层外，所有格的固定层必须逐字相同。
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


def build_character(c):
    if isinstance(c, str):
        return c.strip()
    if not isinstance(c, dict):
        raise SystemExit("character 必须是字符串或对象")
    vals = [str(c[k]).strip() for k in CHAR_FIELDS if c.get(k)]
    if not vals:
        raise SystemExit("character 对象至少填写 role / hair / outfit / colors 中的一项")
    return ", ".join(vals)


def compile_storyboard(sb):
    style = str(sb.get("style", "")).strip()
    comp = str(sb.get("composition", "Composition leaves the upper third of the panel almost completely empty for a speech bubble.")).strip()
    frame = str(sb.get("character_frame", "Semi-realistic casual character design:")).strip()
    neg = str(sb.get("negative", DEFAULT_NEGATIVE)).strip()
    if not style:
        raise SystemExit("缺少 style：必须从 references/styles.md 逐字复制画风前缀")
    char = build_character(sb.get("character"))
    fixed = [style, f"{frame} {char}.", comp]
    panels = sb.get("panels")
    if not isinstance(panels, list) or not panels:
        raise SystemExit("panels 必须是非空数组")

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
        })

    for p in out[1:]:
        a, b = out[0]["layers"], p["layers"]
        for key in ("style", "character", "composition", "negative"):
            if a[key] != b[key]:
                raise SystemExit(f"panel{p['panel']}: 固定层 {key} 与 panel1 不一致")
    return {
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
    print("check: 固定层逐字一致；可变层 = scene / emotion")


if __name__ == "__main__":
    main()
