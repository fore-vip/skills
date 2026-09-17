#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双休了么 · 企业评分引擎（fore-vip-shuangxiu）

把 5 家候选企业的 8 个子项得分，按固定权重算成百分制总分、等级与排名，
并输出 Markdown 报告骨架与可选的 HTML 可视化评分卡。

用法:
    python3 score.py --template-demo                    # 打印输入 JSON 样例
    python3 score.py -i scores.json -o report.md        # 生成 Markdown 报告
    python3 score.py -i scores.json -o report.md --html report.html
    python3 score.py -i scores.json --json result.json  # 只导出计算结果 JSON
    python3 score.py -i scores.json -o report.md --rank-only   # 终端只打印排名表

输入 schema 见 --template-demo 输出。仅依赖 Python 标准库（3.8+）。

设计说明:
  - 子项得分取 0-5 整数; 无法取证的子项填 null, 按行业中位 3 分代入并标记。
  - 总分 = Σ(子项得分 / 5 × 子项权重), 满分 100。
  - 数据完整度 = 有实证的子项数 / 8; <50% 的企业不进确定排名。
"""

import argparse
import html as html_mod
import json
import os
import sys

# ---------------------------------------------------------------- 维度定义

DIMS = [
    ("P1", "用工友好与工时", [
        ("P1.1", "双休制落实", 18),
        ("P1.2", "实际加班强度", 15),
        ("P1.3", "加班补偿落实", 12),
    ]),
    ("P2", "劳动合规与雇主口碑", [
        ("P2.1", "劳动纠纷与仲裁记录", 12),
        ("P2.2", "社保与用工合规", 8),
        ("P2.3", "员工社区口碑", 10),
    ]),
    ("P3", "产品质量与供应链", [
        ("P3.1", "产品质量风评", 15),
        ("P3.2", "供应链用工与稳定性", 10),
    ]),
]

SUB_WEIGHTS = {code: w for _, _, subs in DIMS for code, _, w in subs}
SUB_NAMES = {code: name for _, _, subs in DIMS for code, name, _ in subs}
DIM_OF = {code: dcode for dcode, _, subs in DIMS for code, _, _ in subs}

TOTAL_WEIGHT = sum(SUB_WEIGHTS.values())   # 100
MIN_ENTRIES = 3                            # 候选企业下限(3 成熟品牌 + 2 创新企业)
IMPUTE = 3                                 # 信息不足时的中位代入分
MIN_COMPLETENESS = 0.5                     # 低于此完整度不进确定排名

# 等级: (下限分数, 代号, 名称, 色值)
LEVELS = [
    (85, "S", "良心雇主", "#16a34a"),
    (70, "A", "值得买", "#84cc16"),
    (55, "B", "谨慎考虑", "#eab308"),
    (40, "C", "有争议", "#f97316"),
    (0, "D", "建议避雷", "#dc2626"),
]

DISCLAIMER = (
    "本报告的评分仅基于公开可检索信息在本次候选范围内的横向比较，"
    "不构成对企业用工合法性的认定，也不代表任何官方评级。"
    "标注「未证实」的内容为企业外部人员单方主张，未经司法或行政确认。"
    "企业经营状况与用工政策会随时间变化，请以企业最新公开信息为准。"
)

# ---------------------------------------------------------------- 工具


def level_of(score):
    for low, code, name, color in LEVELS:
        if score >= low:
            return code, name, color
    return "D", "建议避雷", "#dc2626"


def die(msg):
    sys.stderr.write("错误: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------- 计算


def evaluate(company):
    """对单家企业算分, 返回结果字典。"""
    name = (company.get("name") or "").strip()
    if not name:
        die("companies[] 中存在缺少 name 的条目")

    raw = company.get("scores") or {}
    if not isinstance(raw, dict):
        die("%s: scores 必须是对象" % name)

    unknown = [k for k in raw if k not in SUB_WEIGHTS]
    if unknown:
        die("%s: 未知子项 %s（可用: %s）"
            % (name, ", ".join(sorted(unknown)), ", ".join(sorted(SUB_WEIGHTS))))

    subs, imputed, evidenced = {}, [], 0
    for code, weight in SUB_WEIGHTS.items():
        v = raw.get(code, None)
        if v is None:
            subs[code] = {"score": IMPUTE, "weight": weight,
                          "contribution": round(IMPUTE / 5.0 * weight, 4),
                          "imputed": True, "raw": None}
            imputed.append(code)
        else:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                die("%s: 子项 %s 得分必须是数字或 null，收到 %r" % (name, code, v))
            if v < 0 or v > 5:
                die("%s: 子项 %s 得分 %s 超出 0-5 范围" % (name, code, v))
            if abs(v - round(v)) > 1e-9:
                die("%s: 子项 %s 得分 %s 必须是整数" % (name, code, v))
            s = int(round(v))
            subs[code] = {"score": s, "weight": weight,
                          "contribution": round(s / 5.0 * weight, 4),
                          "imputed": False, "raw": s}
            evidenced += 1

    dim_scores = {}
    for dcode, _, dsubs in DIMS:
        dim_scores[dcode] = round(sum(subs[c]["contribution"] for c, _, _ in dsubs), 2)

    total = round(sum(d["contribution"] for d in subs.values()), 1)
    completeness = round(evidenced / float(len(SUB_WEIGHTS)), 3)
    code, lname, color = level_of(total)

    return {
        "name": name,
        "tier": company.get("tier") or "brand",
        "positioning": company.get("positioning") or "",
        "total": total,
        "level": code,
        "level_name": lname,
        "color": color,
        "dims": dim_scores,
        "subs": subs,
        "completeness": completeness,
        "evidenced": evidenced,
        "imputed": imputed,
        "flags": list(company.get("flags") or []),
        "notes": company.get("notes") or "",
        "evidences": company.get("evidences") or {},
        "stores": list(company.get("stores") or []),
    }


def rank(results):
    """分组排序: 证据充分的可排名, 证据不足的单列。"""
    solid = [r for r in results if r["completeness"] >= MIN_COMPLETENESS]
    weak = [r for r in results if r["completeness"] < MIN_COMPLETENESS]
    solid.sort(key=lambda r: (-r["total"], r["name"]))
    weak.sort(key=lambda r: (-r["completeness"], r["name"]))
    return solid, weak


# ---------------------------------------------------------------- Markdown


def md_report(payload, solid, weak):
    product = payload.get("product") or "（未指定品类）"
    out = []
    out.append("# 双休了么 · %s 选购报告\n" % product)
    meta = []
    for label, key in (("你要买", "purpose"), ("预算", "budget"), ("偏好", "preference")):
        if payload.get(key):
            meta.append("**%s**：%s" % (label, payload[key]))
    if meta:
        out.append("> " + " ｜ ".join(meta) + "\n")

    # 候选一览
    out.append("## 候选企业\n")
    out.append("| # | 企业 | 属性 | 一句话定位 | 数据完整度 |")
    out.append("|---|------|------|-----------|-----------|")
    order = solid + weak
    for i, r in enumerate(order, 1):
        tier = "成熟品牌" if r["tier"] == "brand" else "创新企业"
        out.append("| %d | %s | %s | %s | %d/8 |"
                   % (i, r["name"], tier, r["positioning"] or "—", r["evidenced"]))
    out.append("")

    # 评分表
    out.append("## 评分结果\n")
    out.append("权重：用工友好 45 · 劳动合规 30 · 产品质量 25\n")
    head = "| 排名 | 企业 |"
    for code in SUB_WEIGHTS:
        head += " %s<br>%d |" % (SUB_NAMES[code], SUB_WEIGHTS[code])
    head += " **总分** | 等级 |"
    out.append(head)
    out.append("|------|------|" + ":---:|" * len(SUB_WEIGHTS) + ":---:|:---:|")
    for i, r in enumerate(solid, 1):
        row = "| %d | %s |" % (i, r["name"])
        for code in SUB_WEIGHTS:
            cell = r["subs"][code]
            if cell["imputed"]:
                row += " ?(%d) |" % cell["score"]
            else:
                row += " %d |" % cell["score"]
        row += " **%s** | %s |" % (r["total"], r["level"])
        out.append(row)
    out.append("")
    out.append("> 等级：S ≥85 良心雇主｜A 70–85 值得买｜B 55–70 谨慎考虑｜C 40–55 有争议｜D <40 建议避雷")
    out.append("> 括号分值表示该项信息不足，已按行业中位 3 分代入，请勿当作实证结论。\n")

    # 结论
    out.append("## 推荐结论\n")
    for i, r in enumerate(solid[:3], 1):
        out.append("### 第 %d 名 · %s（%s 分 · %s %s）\n"
                   % (i, r["name"], r["total"], r["level"], r["level_name"]))
        if r["evidences"]:
            out.append("- **评分依据**：")
            for code, text in r["evidences"].items():
                if code in SUB_WEIGHTS and text:
                    out.append("  - %s：%s" % (SUB_NAMES[code], text))
            out.append("")
        if r["flags"]:
            out.append("- **已知短板**：")
            for f in r["flags"]:
                out.append("  - %s" % f)
            out.append("")
        else:
            out.append("- **已知短板**：本次检索未发现明显短板。\n")
    if not solid:
        out.append("本次无企业达到可排名的证据完整度门槛。\n")

    # 证据不足单列
    if weak:
        out.append("## 无法可靠评估的企业\n")
        out.append("| 企业 | 数据完整度 | 缺失子项 |")
        out.append("|------|-----------|----------|")
        for r in weak:
            missing = "、".join(SUB_NAMES[c] for c in r["imputed"])
            out.append("| %s | %d/8 | %s |" % (r["name"], r["evidenced"], missing or "—"))
        out.append("")
        out.append("> 上列企业公开证据不足，本次不作排名，避免给出不可靠的确定结论。\n")

    # 旗舰店
    top = solid[:3]
    if top:
        out.append("## 前 3 名官方旗舰店\n")
        out.append("| 企业 | 平台 | 店铺全名 | 检索路径 |")
        out.append("|------|------|----------|----------|")
        for r in top:
            if not r["stores"]:
                out.append("| %s | — | — | 暂未核实到官方旗舰店，建议从品牌官网入口进入 |" % r["name"])
                continue
            for s in r["stores"]:
                out.append("| %s | %s | %s | %s |"
                           % (r["name"], s.get("platform", "—"),
                              s.get("name", "—"), s.get("path", "—")))
        out.append("")
        out.append("> 认准平台官方认证标识（天猫品牌旗舰店 / 京东自营·官方旗舰店 / 抖音蓝V官方店），"
                   "避开「XX 专卖店」「XX 海外专营店」等易混淆店铺。店铺与平台状态会变动，下单前请再确认一次。\n")

    # 信源
    rows = []
    for r in order:
        for code, text in (r["evidences"] or {}).items():
            if code in SUB_WEIGHTS and text:
                rows.append((r["name"], SUB_NAMES[code], text))
    if rows:
        out.append("## 信源清单\n")
        out.append("| 企业 | 维度 | 证据摘要 |")
        out.append("|------|------|----------|")
        for a, b, c in rows:
            out.append("| %s | %s | %s |" % (a, b, c))
        out.append("")

    out.append("## 免责声明\n")
    out.append(DISCLAIMER + "\n")
    return "\n".join(out)


# ---------------------------------------------------------------- HTML


def esc(s):
    return html_mod.escape(str(s if s is not None else ""), quote=True)


def html_report(payload, solid, weak):
    product = payload.get("product") or "选购报告"
    parts = []
    head_doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>双休了么 · __TITLE__</title>
<style>
:root{--bg:#f7f8fa;--card:#fff;--line:#e5e6eb;--ink:#1d2129;--ink2:#4e5969;--ink3:#86909c;--brand:#e53e3e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;padding:28px 16px}
.wrap{max-width:880px;margin:0 auto}
h1{font-size:24px;margin:0 0 6px}
.meta{color:var(--ink2);font-size:13px;margin-bottom:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:14px}
.rank{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.badge{width:30px;height:30px;border-radius:8px;background:var(--brand);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex:0 0 auto}
.cname{font-size:17px;font-weight:600;flex:1}
.lvl{padding:3px 10px;border-radius:999px;color:#fff;font-size:12px;font-weight:600}
.total{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}
.bars{margin-top:6px}
.bar{display:flex;align-items:center;gap:10px;margin:8px 0;font-size:13px;color:var(--ink2)}
.bar .lab{width:130px;flex:0 0 auto}
.track{flex:1;height:8px;background:#eef0f3;border-radius:999px;overflow:hidden}
.fill{height:100%;border-radius:999px}
.bar .val{width:52px;text-align:right;font-variant-numeric:tabular-nums;color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:center}
th{background:#fafbfc;color:var(--ink2);font-weight:600}
td.name{text-align:left;font-weight:600}
.imputed{color:var(--ink3)}
.foot{color:var(--ink3);font-size:12px;line-height:1.8;margin-top:18px}
h2{font-size:16px;margin:26px 0 10px}
</style>
</head>
<body><div class="wrap">
"""
    parts.append(head_doc.replace("__TITLE__", esc(product)))

    parts.append("<h1>双休了么 · %s</h1>" % esc(product))
    meta = []
    for label, key in (("用途", "purpose"), ("预算", "budget"), ("偏好", "preference")):
        if payload.get(key):
            meta.append("%s：%s" % (label, esc(payload[key])))
    if meta:
        parts.append('<div class="meta">%s</div>' % " ｜ ".join(meta))

    # 排名卡
    for i, r in enumerate(solid, 1):
        parts.append('<div class="card">')
        parts.append('<div class="rank"><div class="badge">%d</div>'
                     '<div class="cname">%s</div>'
                     '<div class="total">%s</div>'
                     '<div class="lvl" style="background:%s">%s %s</div></div>'
                     % (i, esc(r["name"]), r["total"], r["color"], r["level"], esc(r["level_name"])))
        if r["positioning"]:
            parts.append('<div class="meta" style="margin-bottom:0">%s</div>' % esc(r["positioning"]))
        parts.append('<div class="bars">')
        for dcode, dname, dsubs in DIMS:
            full = sum(w for _, _, w in dsubs)
            got = r["dims"][dcode]
            pct = max(0.0, min(100.0, got / float(full) * 100))
            parts.append('<div class="bar"><div class="lab">%s</div>'
                         '<div class="track"><div class="fill" style="width:%.1f%%;background:%s"></div></div>'
                         '<div class="val">%.1f/%d</div></div>'
                         % (esc(dname), pct, r["color"], got, full))
        parts.append("</div></div>")

    # 明细表
    all_rows = solid + weak
    if all_rows:
        parts.append("<h2>评分明细</h2>")
        parts.append("<table><tr><th>企业</th>")
        for code in SUB_WEIGHTS:
            parts.append("<th>%s<br><span style='color:#86909c'>%d</span></th>" % (esc(SUB_NAMES[code]), SUB_WEIGHTS[code]))
        parts.append("<th>总分</th><th>等级</th></tr>")
        for r in all_rows:
            thin = r["completeness"] < MIN_COMPLETENESS
            parts.append("<tr%s><td class='name'>%s</td>"
                         % (" style='color:#86909c'" if thin else "", esc(r["name"])))
            for code in SUB_WEIGHTS:
                c = r["subs"][code]
                if c["imputed"]:
                    parts.append("<td class='imputed'>%d<sup>?</sup></td>" % c["score"])
                else:
                    parts.append("<td>%d</td>" % c["score"])
            if thin:
                parts.append("<td><b>%s</b></td><td style='color:#86909c'>不排名</td></tr>" % r["total"])
            else:
                parts.append("<td><b>%s</b></td><td style='color:%s;font-weight:600'>%s</td></tr>"
                             % (r["total"], r["color"], r["level"]))
        parts.append("</table>")
        parts.append("<div class='foot'><sup>?</sup> 该项信息不足，按行业中位 3 分代入，非实证结论。</div>")

    if weak:
        parts.append("<h2>无法可靠评估</h2>")
        parts.append("<table><tr><th>企业</th><th>数据完整度</th><th>缺失子项</th></tr>")
        for r in weak:
            missing = "、".join(SUB_NAMES[c] for c in r["imputed"])
            parts.append("<tr><td class='name'>%s</td><td>%d/8</td><td>%s</td></tr>"
                         % (esc(r["name"]), r["evidenced"], esc(missing or "—")))
        parts.append("</table>")

    top = solid[:3]
    if top:
        parts.append("<h2>前 3 名官方旗舰店</h2>")
        parts.append("<table><tr><th>企业</th><th>平台</th><th>店铺全名</th><th>检索路径</th></tr>")
        for r in top:
            if not r["stores"]:
                parts.append("<tr><td class='name'>%s</td><td colspan='3'>暂未核实到官方旗舰店，建议从品牌官网入口进入</td></tr>" % esc(r["name"]))
                continue
            for s in r["stores"]:
                parts.append("<tr><td class='name'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                             % (esc(r["name"]), esc(s.get("platform", "—")),
                                esc(s.get("name", "—")), esc(s.get("path", "—"))))
        parts.append("</table>")
        parts.append("<div class='foot'>认准平台官方认证标识（天猫品牌旗舰店 / 京东自营·官方旗舰店 / 抖音蓝V官方店），"
                     "避开「XX 专卖店」「XX 海外专营店」等易混淆店铺。店铺状态会变动，下单前请再确认一次。</div>")

    parts.append("<div class='foot' style='margin-top:26px;border-top:1px solid #e5e6eb;padding-top:14px'>%s</div>" % esc(DISCLAIMER))
    parts.append("</div></body></html>")
    return "".join(parts)


# ---------------------------------------------------------------- 模板样例


def template_demo():
    demo = {
        "product": "无线吸尘器",
        "purpose": "家里养猫，主要吸毛发，需要轻一点",
        "budget": "1500-2500",
        "preference": "不优先考虑有劳务外包争议的企业",
        "companies": [
            {
                "name": "示例家电",
                "tier": "brand",
                "positioning": "国产头部，性价比与渠道覆盖强",
                "scores": {"P1.1": 5, "P1.2": 4, "P1.3": 4,
                           "P2.1": 5, "P2.2": 5, "P2.3": 4,
                           "P3.1": 4, "P3.2": 3},
                "evidences": {
                    "P1.1": "招聘页明确写明双休；脉脉 2025-08 多条在职反馈印证",
                    "P2.1": "裁判文书网近 3 年无劳动争议案件",
                },
                "flags": ["供应链以代工为主且无用工合规披露（信息不足）"],
                "stores": [
                    {"platform": "天猫", "name": "示例家电官方旗舰店",
                     "path": "天猫搜「示例家电」，认准品牌旗舰店标识"},
                    {"platform": "京东", "name": "示例家电京东自营旗舰店",
                     "path": "京东搜「示例家电」，筛选「自营」"}
                ]
            },
            {
                "name": "示例创科",
                "tier": "innovator",
                "positioning": "新锐 DTC 品牌，设计驱动",
                "scores": {"P1.1": 5, "P1.2": 5, "P1.3": None,
                           "P2.1": 5, "P2.2": 4, "P2.3": 5,
                           "P3.1": 3, "P3.2": None},
                "evidences": {"P1.2": "知乎、小红书多条反馈「到点走、不打卡」（2025-06）"},
                "flags": [],
                "stores": []
            }
        ]
    }
    print(json.dumps(demo, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- 主流程


def main():
    ap = argparse.ArgumentParser(
        description="双休了么 · 企业评分引擎（8 子项加权百分制）")
    ap.add_argument("-i", "--input", help="输入 JSON 路径")
    ap.add_argument("-o", "--output", help="输出 Markdown 报告路径")
    ap.add_argument("--html", help="输出 HTML 评分卡路径")
    ap.add_argument("--json", dest="json_out", help="导出计算结果 JSON")
    ap.add_argument("--rank-only", action="store_true", help="终端只打印排名表")
    ap.add_argument("--template-demo", action="store_true", help="打印输入 JSON 样例后退出")
    args = ap.parse_args()

    if args.template_demo:
        template_demo()
        return

    if not args.input:
        ap.print_help()
        sys.stderr.write("\n提示: 先用 --template-demo 看输入格式，或用 -i 指定输入文件。\n")
        sys.exit(2)

    if not os.path.isfile(args.input):
        die("找不到输入文件 %s" % args.input)

    with open(args.input, encoding="utf-8") as fh:
        try:
            payload = json.load(fh)
        except ValueError as exc:
            die("输入 JSON 解析失败: %s" % exc)

    companies = payload.get("companies") or []
    if not isinstance(companies, list) or not companies:
        die("companies 必须是非空数组")
    if len(companies) < MIN_ENTRIES:
        sys.stderr.write("提示: 候选企业少于 %d 家（应为 3 家成熟品牌 + 2 家创新企业），"
                         "结论的横向比较意义有限。\n" % MIN_ENTRIES)

    results = [evaluate(c) for c in companies]
    solid, weak = rank(results)

    if args.rank_only or not (args.output or args.html or args.json_out):
        print("候选 %d 家 | 权重合计 %d 分 | 可排名 %d 家 | 证据不足 %d 家\n"
              % (len(results), TOTAL_WEIGHT, len(solid), len(weak)))
        print("%-4s %-16s %8s %6s %6s %5s" % ("名次", "企业", "总分", "等级", "完整度", "短板"))
        for i, r in enumerate(solid, 1):
            print("%-4d %-16s %8.1f %6s %5.0f%% %5d"
                  % (i, r["name"], r["total"], r["level"],
                     r["completeness"] * 100, len(r["flags"])))
        for r in weak:
            print("%-4s %-16s %8.1f %6s %5.0f%% %5s"
                  % ("—", r["name"], r["total"], r["level"],
                     r["completeness"] * 100, "不排名"))
        print("\n" + DISCLAIMER)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(md_report(payload, solid, weak))
        sys.stderr.write("已写入 Markdown: %s\n" % args.output)

    if args.html:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(html_report(payload, solid, weak))
        sys.stderr.write("已写入 HTML: %s\n" % args.html)

    if args.json_out:
        export = {
            "product": payload.get("product"),
            "weights": SUB_WEIGHTS,
            "ranked": [r["name"] for r in solid],
            "not_ranked": [r["name"] for r in weak],
            "results": [
                {"name": r["name"], "total": r["total"], "level": r["level"],
                 "dims": r["dims"], "scores": {k: v["score"] for k, v in r["subs"].items()},
                 "imputed": r["imputed"], "completeness": r["completeness"]}
                for r in solid + weak
            ],
            "disclaimer": DISCLAIMER,
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(export, fh, ensure_ascii=False, indent=2)
        sys.stderr.write("已写入结果 JSON: %s\n" % args.json_out)


if __name__ == "__main__":
    main()
