#!/usr/bin/env python3
"""第五道闸门：交付判定。回答「这到底是不是一个应用」，而不是「页面好不好看」。

三态结果：
  DELIVERED   应用实体、业务动作、站点地址、事实来源全部闭环，才允许汇报「已交付」
  DRAFT       用户明确同意的页面草稿：必须如实标注「不是应用」，并给出转应用步骤
  INCOMPLETE  用户诉求要应用、产物却是页面草稿：禁止汇报完成，必须列出补齐步骤

用法:
  python3 verify_delivery.py --spec app.spec.json --dir ./app
  python3 verify_delivery.py --spec app.spec.json --dir ./app --intent "给我做一个能收预约的应用"
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

BAD_HOSTS = ("example.com", "example.org", "example.net", "localhost", "127.0.0.1")
APP_WORDS = ("应用", "上线", "发布", "可访问", "链接", "能用", "真正", "收预约",
             "留资", "落库", "后端", "小程序", "部署")
APP_MARKS = (".genie", "applications.yaml", "deploy.manifest.json")
NEXT_STEPS = [
    "1. 向用户一次性索要真实业务事实（店名 / 地址 / 电话 / 营业时间 / 项目 / 价格 / 经营承诺 / 顾客评价），逐条写进 meta.facts 且 source=user",
    "2. 云服务：workbuddy_cloud_service action=inspect → action=activate（applicationMode=create）；确认框被取消就停在 INCOMPLETE，不重试不绕路",
    "3. 建业务表 + RLS + GRANT，管理侧跑一次「写入 → 读回 → 更新 → 再读回」",
    "4. spec 改 meta.deliverable=webapp、meta.siteUrl=真实域名、meta.cloud.needed=true 并填 table/columns",
    "5. 重新生成：python3 scripts/build_page.py --spec <spec> --out index.html --cloud-config <publicConfig.json> --base-url <站点地址>",
    "6. 跑完五道闸门后，用「发布为应用 / 部署站点」能力取得在线链接，再由用户确认对外发布",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--dir", default="", help="交付目录，默认取 spec 所在目录")
    ap.add_argument("--page", default="", help="默认 <dir>/index.html")
    ap.add_argument("--intent", default="", help="覆盖 spec.meta.intent（用户原话）")
    a = ap.parse_args()

    spec_path = Path(a.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    meta = spec["meta"]
    folder = Path(a.dir) if a.dir else spec_path.parent
    page_path = Path(a.page) if a.page else folder / "index.html"
    intent = a.intent or meta.get("intent", "")
    deliverable = meta.get("deliverable", "")
    cloud = meta.get("cloud", {})
    facts = meta.get("facts") or []
    wants_app = any(w in intent for w in APP_WORDS)
    checks = []
    blockers = []

    def ck(name, ok, detail="", fatal=True):
        checks.append((name, bool(ok), detail))
        if not ok and fatal:
            blockers.append(name + (" :: " + detail if detail else ""))

    page = page_path.read_text(encoding="utf-8") if page_path.exists() else ""
    ck("页面文件存在且非空", bool(page) and len(page) > 2000,
       str(page_path) + " / %d bytes" % len(page))
    ck("meta.deliverable 合法", deliverable in ("draft", "webapp", "site"), deliverable)
    ck("meta.intent 记录了用户原话", bool(intent.strip()), intent[:40])
    site = (meta.get("siteUrl") or "").strip().rstrip("/")
    host = urlparse(site).netloc
    bad_host_hits = [h for h in BAD_HOSTS if h in host or h in page]
    ck("没有占位 / 本地地址", not bad_host_hits,
       "、".join(bad_host_hits) or (host or "(草稿态无站点地址)"))

    # 诉求 ↔ 交付形态：这一条就是「只设计了首页」的判定
    if wants_app:
        ck("用户要应用，产物必须是应用形态", deliverable in ("webapp", "site"),
           "诉求原话=%s / 实际形态=%s" % (intent[:40], deliverable or "未声明"))

    has_form = "<form" in page
    if deliverable in ("webapp", "site"):
        marks = [m for m in APP_MARKS if (folder / m).exists()]
        marks += [p.name for p in folder.glob(".*.genie")]
        ck("交付目录存在应用实体标记", bool(marks),
           "、".join(marks[:3]) or "缺 .genie / applications.yaml / deploy.manifest.json")
        ck("有真实站点地址", bool(site) and not any(h in host for h in BAD_HOSTS), site or "(空)")
        ck("业务动作有后端落点", bool(cloud.get("needed")) and bool(cloud.get("table")),
           "cloud.needed=%s table=%s" % (cloud.get("needed"), cloud.get("table") or "(空)"))
        if has_form:
            ck("表单是可提交的", not re.findall(r"<(?:input|button)\b[^>]*disabled", page))
            ck("页面已接云 SDK", "createWorkBuddyCloud" in page)
        demos = [f for f in facts if f.get("source") == "example"]
        ck("业务事实清单齐备且示例已标注",
           bool(facts) and (not demos or (meta.get("factReview") is True
                and any(w in meta.get("disclaimer", "") for w in ("示例", "演示")))),
           "%d 条事实 / 示例 %d 条" % (len(facts), len(demos)))
    else:
        # 草稿：允许存在，但必须承认它不是应用
        ck("草稿不含可提交的业务表单",
           not has_form or bool(re.findall(r"<(?:input|button)\b[^>]*disabled", page)))
        examples = [f for f in facts if f.get("source") == "example"]
        ck("示例事实已列入待补清单", not examples or meta.get("factReview") is True,
           "%d 条示例事实" % len(examples))

    bad_assert = [x.get("name", "") for x in spec.get("assertions", [])
                  if any(w in str(x.get("expect", "")) for w in ("没有发送", "不会保存", "未开放"))]
    ck("没有把「业务不可用」写成验收项", not bad_assert, "、".join(bad_assert[:3]))
    shots = sorted(folder.rglob("*.png"))
    need_shots = len(spec["sections"]) + 1
    ck("截图覆盖全部区块（证明跑过逐段目视）", len(shots) >= need_shots,
       "%d 张 / 需要 ≥%d 张" % (len(shots), need_shots))

    for name, ok, detail in checks:
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))

    if blockers:
        state = "INCOMPLETE"
    elif deliverable in ("webapp", "site"):
        state = "DELIVERED"
    else:
        state = "DRAFT"

    print("\n交付形态 = %s | 用户诉求 = %s" % (deliverable or "未声明", "要应用" if wants_app else "未指定/页面"))
    print("RESULT " + state)
    if state == "DELIVERED":
        demos = [f.get("key", "?") for f in facts if f.get("source") == "example"]
        if demos:
            print("注意：含 %d 条示例事实（%s），属于演示应用，禁止作为真实门店对外发布。"
                  % (len(demos), "、".join(demos[:4])))
        print("允许汇报「已交付」；若未取得在线链接，仍需写明「未上线」。")
    elif state == "DRAFT":
        print("这是页面草稿，不是应用。交付标题必须写「页面草稿」，禁止写「应用已完成」。")
    else:
        print("禁止汇报「已完成」。缺项：")
        for b in blockers:
            print("  - " + b)

    if state != "DELIVERED":
        print("\n补齐为可发布应用的步骤：")
        for s in NEXT_STEPS:
            print("  " + s)
        pending = [f.get("key", "?") for f in facts if f.get("source") != "user"]
        if pending:
            print("  待补真实业务事实：" + "、".join(pending))
    return 2 if state == "INCOMPLETE" else 0


if __name__ == "__main__":
    sys.exit(main())
