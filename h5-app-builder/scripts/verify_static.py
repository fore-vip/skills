#!/usr/bin/env python3
"""静态闸门：主题口径 + 叙事顺序 + 控件样式一致性 + 资源边界。

用法: python3 verify_static.py --spec examples/beauty.spec.json --page index.html [--cloud]
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

SDK_CDN = "https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js"
# 制作过程词：宣传页正文里出现任何一个都算串台
PROCESS_WORDS = ["生成器", "spec.json", "SKILL", "模板生成", "激活云服务", "publicConfig",
                 "applicationId", "H5App", "前凌智选", "AUTO 工作室", "示例数据原型",
                 "KPI", "待办清单", "现场演示"]
OLD_CONTROL_CLASSES = ["btn-p", "btn-g", "hd-cta", "d-switch", "d-acts", "stChips", "class=\"tab\""]


def visible_text(page):
    t = re.sub(r"<head[\s\S]*?</head>", "", page)
    t = re.sub(r"<script[\s\S]*?</script>", "", t)
    t = re.sub(r"<style[\s\S]*?</style>", "", t)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--page", required=True)
    ap.add_argument("--cloud", action="store_true")
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    page = Path(a.page).read_text(encoding="utf-8")
    meta = spec["meta"]
    text = visible_text(page)
    css = "\n".join(re.findall(r"<style>([\s\S]*?)</style>", page))
    checks = []

    def ck(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # 1) 主题口径
    required = meta.get("requiredTerms", [])
    missing = [w for w in required if w not in text]
    ck("主题必备词全部出现（%d 个）" % len(required), not missing,
       "缺少: " + "、".join(missing) if missing else "")
    forbidden = meta.get("forbiddenTerms", []) + PROCESS_WORDS
    leaked = [w for w in forbidden if w in text]
    ck("主题禁用词与制作过程词均未出现（%d 个）" % len(forbidden), not leaked,
       "残留: " + "、".join(leaked[:6]) if leaked else "")
    dis = meta.get("disclaimer", "")
    ck("口径声明出现在正文", bool(dis) and dis in text, dis[:24])

    # 2) 叙事顺序
    ids = re.findall(r'<section class="sect" id="([^"]+)"', page)
    want = [s.get("id", s["type"]) for s in spec["sections"]]
    ck("区块渲染顺序与 spec 完全一致", ids == want,
       "渲染=" + "/".join(ids) + " 期望=" + "/".join(want))
    ck("首屏 hero 在全部区块之前", page.find('class="hero"') < page.find('class="sect"'))
    ck("行动区 cta 存在且不在第一个区块", "cta" in want and want.index("cta") > 0,
       "cta 位置=" + str(want.index("cta") if "cta" in want else -1))

    # 3) 控件样式一致性（静态）
    ck("存在唯一 .ctl 基类与 .ctl.is-on 选中态",
       ".ctl{" in css and ".ctl.is-on{" in css and ".ctl.on{" not in css)
    ck("无旧版控件类残留", not [c for c in OLD_CONTROL_CLASSES if c in page],
       "、".join([c for c in OLD_CONTROL_CLASSES if c in page]))
    ck("无内联样式与 JS 内联写样式",
       'style="' not in page and "style.cssText" not in page and ".style." not in page)
    buttons = re.findall(r"<(?:button|summary)\b[^>]*>", page)
    bad_btn = [b for b in buttons if "ctl" not in b]
    ck("所有可点控件统一带 ctl 类（%d 个）" % len(buttons), not bad_btn,
       "例外 " + str(len(bad_btn)) + ": " + str(bad_btn[:2]))
    inputs = re.findall(r"<input\b[^>]*>", page)
    bad_in = [i for i in inputs if "field" not in i]
    ck("所有输入框统一为 .field（%d 个）" % len(inputs), not bad_in, str(bad_in[:2]))
    ctl_blocks = re.findall(r"\.ctl[^{]*\{([^}]*)\}", css)
    hardcoded = []
    for b in ctl_blocks:
        # 1px 是描边宽度与按压位移的结构常量，不属于设计 token
        hardcoded += [x for x in re.findall(r"\b\d+(?:\.\d+)?px\b", b) if x != "1px"]
        hardcoded += re.findall(r"#[0-9a-fA-F]{3,8}\b", b)
        hardcoded += re.findall(r"\brgba?\(", b)
    ck(".ctl 系列规则不含硬编码尺寸/色值", not hardcoded, "、".join(hardcoded[:6]))
    token_block = re.findall(r":root\{(__TOKENS__|[^}]*--[^}]*)\}", css)
    ck("版式 token 以 :root 变量集中覆盖", len(token_block) >= 2,
       "检测到 %d 个变量块" % len(token_block))
    body_layout = re.search(r'<body data-layout="([^"]+)"', page)
    actual_layout = body_layout.group(1) if body_layout else ""
    sys.dont_write_bytecode = True  # 运行不污染技能包
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pick_layout import choose
    expected = choose(meta.get("topic", meta["title"]), override=meta.get("layoutId") or None)
    ck("页面版式与主题路由结果一致", bool(actual_layout) and actual_layout == expected["id"],
       "页面=" + actual_layout + " 路由=" + expected["id"] + "（" + expected["name"] + "）")

    # 4) 资源边界
    srcs = [s.strip().strip('"').strip("'")
            for s in re.findall(r"<script[^>]*\ssrc=([^\s>]+)", page)]
    if a.cloud:
        ck("云模式仅加载白名单 SDK", srcs == [SDK_CDN], str(srcs))
        for needle in ("createWorkBuddyCloud", "endpoint: CFG.endpoint",
                       "publishableKey: CFG.publishableKey",
                       "oauthRelayBaseUrl: CFG.oauthRelayBaseUrl"):
            ck("云接线 " + needle, needle in page)
        ck("前端未泄漏管理侧标识", "applicationId" not in page and "resourceId" not in page)
    else:
        ck("纯前端零外部脚本", not srcs, str(srcs))
    ck("无外部样式与远程图片",
       not re.search(r'<link[^>]+rel=.stylesheet|<img[^>]+src=.https?://', page))

    for name, ok, detail in checks:
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))
    bad = [c for c in checks if not c[1]]
    print("RESULT " + ("ALL PASS (%d)" % len(checks) if not bad else "FAIL (%d/%d)" % (len(bad), len(checks))))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
