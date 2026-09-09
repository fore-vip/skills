#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业/工厂健康度评分引擎（fore-vip-enterprise-health）

用法:
    python3 score.py -i scores.json -o report.md
    python3 score.py -i scores.json -o report.md --html report.html --radar radar.svg
    python3 score.py --template-demo                # 输出一份输入 JSON 样例

输入 JSON schema 见 --template-demo 输出。
仅依赖 Python 标准库（3.8+）。
"""

import argparse
import json
import math
import os
import sys

# ---------- 维度定义 ----------
DIM_NAMES = {
    "E1": "战略与治理", "E2": "财务健康", "E3": "市场与销售", "E4": "产品与研发",
    "E5": "组织与人才", "E6": "流程与运营", "E7": "供应链", "E8": "数字化与数据",
    "E9": "风险与合规", "E10": "客户与服务",
    "F1": "生产效能", "F2": "质量", "F3": "设备", "F4": "成本与精益",
    "F5": "交付与计划", "F6": "现场5S/6S", "F7": "EHS安全环保", "F8": "人员与技能",
    "F9": "工艺与工程", "F10": "厂务与能源", "F11": "仓储与物流",
    "G1": "战略与投资组合", "G2": "总部管控与共享", "G3": "资金与财务管控",
    "G4": "多厂对标与复制", "G5": "干部梯队与文化",
}

DEFAULT_WEIGHTS = {
    "E1": 9, "E2": 17, "E3": 13, "E4": 11, "E5": 11,
    "E6": 8, "E7": 8, "E8": 8, "E9": 10, "E10": 5,
    "F1": 14, "F2": 14, "F3": 10, "F4": 12, "F5": 12, "F6": 6,
    "F7": 12, "F8": 7, "F9": 7, "F10": 3, "F11": 3,
    "G1": 25, "G2": 20, "G3": 20, "G4": 20, "G5": 15,
}

# 模式 -> 各卡在总分中的占比
MODE_MIX = {
    "enterprise": {"E": 1.0},
    "factory":    {"E": 0.4, "F": 0.6},
    "group":      {"E": 0.25, "F": 0.45, "G": 0.30},
}

LEVELS = [
    (4.2, "A", "健康", "#16a34a"),
    (3.6, "B", "亚健康", "#84cc16"),
    (2.8, "C", "预警", "#eab308"),
    (2.0, "D", "病态", "#f97316"),
    (0.0, "E", "危重", "#dc2626"),
]

LEVEL_ORDER = ["A", "B", "C", "D", "E"]


# ---------- 计算 ----------
def norm_dim(v):
    """维度值既可为数字，也可为 {score, note, findings}"""
    if isinstance(v, (int, float)):
        return float(v), "", []
    if isinstance(v, dict):
        return float(v.get("score", 0)), v.get("note", ""), v.get("findings", []) or []
    raise ValueError("维度值格式错误: %r" % (v,))


def calc_card(dims, prefix, weights, label):
    """计算单张卡（E/F/G）的加权分；0 分视为不适用并剔除后重分配"""
    rows, total_w, acc = [], 0.0, 0.0
    skipped = []
    for k in sorted([d for d in dims if d.startswith(prefix)],
                    key=lambda x: int(x[1:])):
        score, note, findings = norm_dim(dims[k])
        w = float(weights.get(k, DEFAULT_WEIGHTS.get(k, 0)))
        if score <= 0 or w <= 0:
            skipped.append(k)
            continue
        total_w += w
        acc += score * w
        rows.append({
            "key": k, "name": DIM_NAMES.get(k, k), "score": score,
            "raw_w": w, "note": note, "findings": findings,
        })
    if total_w <= 0:
        return {"label": label, "score": 0.0, "rows": [], "skipped": skipped,
                "empty": True}
    for r in rows:
        r["eff_w"] = round(r["raw_w"] / total_w * 100, 1)
        r["weighted"] = round(r["score"] * r["raw_w"] / total_w, 3)
    return {"label": label, "score": round(acc / total_w, 2), "rows": rows,
            "skipped": skipped, "empty": False}


def level_of(score):
    for thr, code, name, color in LEVELS:
        if score >= thr:
            return code, name, color
    return "E", "危重", "#dc2626"


def downgrade(code, n):
    i = LEVEL_ORDER.index(code)
    return LEVEL_ORDER[min(i + n, len(LEVEL_ORDER) - 1)]


def code_meta(code):
    for c, n, col in [("A", "健康", "#16a34a"), ("B", "亚健康", "#84cc16"),
                      ("C", "预警", "#eab308"), ("D", "病态", "#f97316"),
                      ("E", "危重", "#dc2626")]:
        if c == code:
            return c, n, col
    return "E", "危重", "#dc2626"


def site_scores(data, weights):
    out = []
    for s in data.get("sites", []) or []:
        card = calc_card(s.get("dims", {}), "F", weights, s.get("name", "厂区"))
        out.append(card)
    return out


def evaluate(data):
    weights = dict(DEFAULT_WEIGHTS)
    weights.update(data.get("weights", {}) or {})
    mode = data.get("mode", "enterprise")
    if mode not in MODE_MIX:
        raise ValueError("mode 必须是 enterprise / factory / group，收到: %s" % mode)
    dims = data.get("dims", {}) or {}

    cards = {}
    if "E" in MODE_MIX[mode]:
        cards["E"] = calc_card(dims, "E", weights, "企业侧")
    if "F" in MODE_MIX[mode]:
        cards["F"] = calc_card(dims, "F", weights, "工厂侧")
    if "G" in MODE_MIX[mode]:
        cards["G"] = calc_card(dims, "G", weights, "集团层")

    sites = site_scores(data, weights) if mode == "group" else []

    # 集团模式：工厂侧取各厂区均值
    if mode == "group" and sites:
        valid = [s for s in sites if not s["empty"]]
        if valid:
            f_mean = round(sum(s["score"] for s in valid) / len(valid), 2)
            cards["F"] = {"label": "工厂侧(各厂区均值)", "score": f_mean,
                          "rows": [], "skipped": [], "empty": False,
                          "sites": sites}

    mix = MODE_MIX[mode]
    total = 0.0
    for k, share in mix.items():
        c = cards.get(k)
        if c and not c["empty"]:
            total += c["score"] * share

    # 红旗降级：每条降一级
    flags = data.get("red_flags", []) or []
    code, name, color = level_of(total)
    if flags:
        code = downgrade(code, len(flags))
        code, name, color = code_meta(code)

    return {
        "org": data.get("org", "未命名主体"),
        "mode": mode,
        "date": data.get("date", ""),
        "auditor": data.get("auditor", ""),
        "cards": cards,
        "sites": sites,
        "mix": mix,
        "total": round(total, 2),
        "code": code, "level_name": name, "color": color,
        "red_flags": flags,
        "actions": sorted_actions(data.get("actions", []) or []),
        "data_gaps": data.get("data_gaps", []) or [],
    }


def sorted_actions(actions):
    out = []
    for a in actions:
        i = float(a.get("impact", 5))
        c = float(a.get("confidence", 5))
        e = float(a.get("ease", 5))
        out.append(dict(a, ice=round(i * c * e / 100.0, 2)))
    out.sort(key=lambda x: -x["ice"])
    for n, a in enumerate(out, 1):
        a["rank"] = n
    return out


# ---------- 渲染 ----------
def radar_svg(rows, total, color, width=560, height=460):
    if not rows:
        return ""
    n = len(rows)
    cx, cy, r = width / 2, height / 2 + 6, min(width, height) / 2 - 78
    rings = [1, 2, 3, 4, 5]

    def pt(idx, val):
        ang = -math.pi / 2 + 2 * math.pi * idx / n
        rr = r * (val / 5.0)
        return cx + rr * math.cos(ang), cy + rr * math.sin(ang)

    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height)]
    p.append('<rect width="100%%" height="100%%" fill="#ffffff"/>')
    p.append('<g fill="none" stroke="#e5e7eb" stroke-width="1">')
    for ring in rings:
        pts = " ".join("%.1f,%.1f" % pt(i, ring) for i in range(n))
        p.append('<polygon points="%s"/>' % pts)
    p.append('</g>')
    p.append('<g stroke="#e5e7eb" stroke-width="1">')
    for i in range(n):
        x, y = pt(i, 5)
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cx, cy, x, y))
    p.append('</g>')
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.22" stroke="%s" stroke-width="2"/>'
             % (" ".join("%.1f,%.1f" % pt(i, rows[i]["score"]) for i in range(n)), color, color))
    for i in range(n):
        x, y = pt(i, rows[i]["score"])
        p.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>' % (x, y, color))
    for i in range(n):
        x, y = pt(i, 5.9)
        anchor = "middle" if abs(x - cx) < 12 else ("start" if x > cx else "end")
        p.append('<text x="%.1f" y="%.1f" font-size="12" fill="#374151" text-anchor="%s">%s %s</text>'
                 % (x, y + 4, anchor, rows[i]["key"], rows[i]["name"]))
        p.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s" text-anchor="%s">%.1f</text>'
                 % (x, y + 18, color, anchor, rows[i]["score"]))
    p.append('<text x="%.1f" y="26" font-size="15" font-weight="bold" fill="#111827" text-anchor="middle">健康度综合 %.2f / 5.00</text>' % (cx, total))
    p.append('</svg>')
    return "".join(p)


def bar(score, color):
    filled = int(round(score))
    return "%s%s %.1f" % ("■" * filled, "□" * (5 - filled), score)


def render_md(r):
    L = []
    L.append("# %s · 健康度检查报告" % r["org"])
    L.append("")
    meta = ["- **检查模式**：%s" % {"enterprise": "企业型（E 卡）", "factory": "制造型（E 卡 + F 卡）",
                                    "group": "集团多厂（E 卡 + F 卡各厂 + G 卡）"}[r["mode"]]]
    if r["date"]:
        meta.append("- **检查日期**：%s" % r["date"])
    if r["auditor"]:
        meta.append("- **检查人**：%s" % r["auditor"])
    meta.append("- **综合评分**：**%.2f / 5.00** — **%s 级 · %s**" % (r["total"], r["code"], r["level_name"]))
    L.extend(meta)
    L.append("")

    # 分卡汇总
    L.append("## 一、分卡得分")
    L.append("")
    L.append("| 评分卡 | 得分 | 在总分中占比 | 加权贡献 |")
    L.append("|---|---:|---:|---:|")
    for k in ["E", "F", "G"]:
        c = r["cards"].get(k)
        if not c or c.get("empty"):
            continue
        share = r["mix"].get(k, 0)
        L.append("| %s | **%.2f** | %d%% | %.2f |" % (c["label"], c["score"], round(share * 100), c["score"] * share))
    L.append("| **综合** | **%.2f** | 100%% | **%.2f** |" % (r["total"], r["total"]))
    L.append("")

    if r["red_flags"]:
        L.append("> ## ⛔ 红旗项（已触发整体降级 %d 级）" % len(r["red_flags"]))
        L.append(">")
        for f in r["red_flags"]:
            L.append("> - %s" % f)
        L.append("")

    # 各卡明细
    sec = 2
    for k in ["E", "F", "G"]:
        c = r["cards"].get(k)
        if not c or c.get("empty") or not c.get("rows"):
            continue
        L.append("## %s、%s 明细（本卡得分 %.2f）"
                 % (["二", "三", "四", "五"][sec - 2], c["label"], c["score"]))
        L.append("")
        L.append("| 维度 | 名称 | 得分 | 有效权重% | 加权 | 等级 | 关键发现 |")
        L.append("|---|---|---:|---:|---:|:--:|---|")
        for row in c["rows"]:
            lv = level_of(row["score"])[0]
            note = "; ".join(row["findings"]) if row["findings"] else row["note"]
            L.append("| %s | %s | %s | %.1f | %.2f | **%s** | %s |"
                     % (row["key"], row["name"], bar(row["score"], "#374151"),
                        row["eff_w"], row["weighted"], lv, note.replace("|", "/") or "—"))
        L.append("")
        if c.get("skipped"):
            L.append("> 不适用/未评维度（权重已重分配）：%s" % "、".join(c["skipped"]))
            L.append("")
        sec += 1

    # 厂区对比（集团）
    if r["sites"]:
        L.append("## 厂区横向对比")
        L.append("")
        L.append("| 厂区 | 工厂侧得分 | 等级 | 最强维度 | 最弱维度 |")
        L.append("|---|---:|:--:|---|---|")
        for s in r["sites"]:
            if s["empty"]:
                continue
            rows = sorted([x for x in s["rows"]], key=lambda x: -x["score"])
            best = "%s %s(%.1f)" % (rows[0]["key"], rows[0]["name"], rows[0]["score"]) if rows else "—"
            worst = "%s %s(%.1f)" % (rows[-1]["key"], rows[-1]["name"], rows[-1]["score"]) if rows else "—"
            L.append("| %s | **%.2f** | %s | %s | %s |" % (s["label"], s["score"], level_of(s["score"])[0], best, worst))
        worst_site = min([s for s in r["sites"] if not s["empty"]], key=lambda x: x["score"], default=None)
        if worst_site:
            L.append("")
            L.append("> **最差厂区单独披露**：%s 得分 %.2f（%s 级），不得被均值掩盖。"
                     % (worst_site["label"], worst_site["score"], level_of(worst_site["score"])[0]))
        L.append("")

    # 整改清单
    if r["actions"]:
        L.append("## 整改清单（按 ICE 优先级排序）")
        L.append("")
        L.append("| # | 整改项 | 关联维度 | 预期效果 KPI | 负责人 | 完成时间 | I | C | E | **ICE** |")
        L.append("|---:|---|---|---|:--:|:--:|:--:|:--:|:--:|---:|")
        for a in r["actions"]:
            L.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | **%.2f** |"
                     % (a["rank"], a.get("title", ""), a.get("dim", "—"),
                        a.get("kpi", "—"), a.get("owner", "—"), a.get("due", "—"),
                        a.get("impact", 5), a.get("confidence", 5), a.get("ease", 5), a["ice"]))
        L.append("")
        L.append("> ICE = Impact(1-10) × Confidence(1-10) × Ease(1-10) ÷ 100，越高越优先。")
        L.append("")

    if r["data_gaps"]:
        L.append("## 数据缺失清单（需补充采集）")
        L.append("")
        for g in r["data_gaps"]:
            L.append("- %s" % g)
        L.append("")

    L.append("---")
    L.append("")
    L.append("> 本报告由 fore-vip-enterprise-health 生成。评分基于问卷自评与可选实算校准，"
             "属管理诊断建议，不构成审计/法律/安全评价结论；涉及EHS、环保、资质的合规判定须由具备资质的第三方出具。")
    L.append("")
    return "\n".join(L)


def render_html(r, svg):
    rows_html = []
    for k in ["E", "F", "G"]:
        c = r["cards"].get(k)
        if not c or c.get("empty") or not c.get("rows"):
            continue
        for row in c["rows"]:
            lv, _, col = level_of(row["score"])
            pct = row["score"] / 5.0 * 100
            rows_html.append(
                '<tr><td class="k">%s</td><td>%s</td>'
                '<td class="num"><b>%.1f</b></td>'
                '<td><div class="bar"><i style="width:%.0f%%;background:%s"></i></div></td>'
                '<td class="ctr"><span class="lv" style="background:%s">%s</span></td>'
                '<td class="note">%s</td></tr>'
                % (row["key"], row["name"], row["score"], pct, col, col, lv,
                   ("; ".join(row["findings"]) if row["findings"] else row["note"]) or "—"))

    acts_html = []
    for a in r["actions"][:12]:
        acts_html.append(
            '<tr><td class="ctr">%d</td><td>%s</td><td class="ctr">%s</td><td>%s</td>'
            '<td class="ctr">%s</td><td class="ctr">%s</td><td class="ctr"><b>%.2f</b></td></tr>'
            % (a["rank"], a.get("title", ""), a.get("dim", "—"), a.get("kpi", "—"),
               a.get("owner", "—"), a.get("due", "—"), a["ice"]))

    flags_html = ""
    if r["red_flags"]:
        flags_html = ('<div class="flags"><h3>⛔ 红旗项（整体降级 %d 级）</h3><ul>%s</ul></div>'
                      % (len(r["red_flags"]), "".join("<li>%s</li>" % f for f in r["red_flags"])))

    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(org)s · 健康度检查报告</title>
<style>
:root{--brand:#e53e3e;--ink:#1f2937;--sub:#6b7280;--line:#e5e7eb}
*{box-sizing:border-box}
body{margin:0;background:#f5f6f8;color:var(--ink);
 font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6}
.wrap{max-width:960px;margin:0 auto;padding:32px 20px 64px}
.hero{background:linear-gradient(135deg,#1f2937,#374151);color:#fff;border-radius:16px;padding:28px 32px}
.hero h1{margin:0 0 6px;font-size:24px}
.hero .meta{opacity:.75;font-size:13px}
.score{display:flex;align-items:baseline;gap:14px;margin-top:18px}
.score .num{font-size:52px;font-weight:800;line-height:1}
.score .lv{display:inline-block;padding:4px 14px;border-radius:999px;font-weight:700;color:#fff;font-size:15px}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:24px;margin-top:20px}
h2{margin:0 0 14px;font-size:18px;border-left:4px solid var(--brand);padding-left:10px}
table{width:100%%;border-collapse:collapse;font-size:14px}
th,td{padding:9px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
th{background:#fafafa;color:var(--sub);font-weight:600;font-size:13px}
td.k{color:var(--sub);font-weight:700;width:44px}
td.num{width:52px;text-align:right}
td.ctr{text-align:center}
td.note{color:#4b5563;font-size:13px}
.bar{background:#f0f1f3;border-radius:999px;height:8px;overflow:hidden;width:120px}
.bar i{display:block;height:100%%;border-radius:999px}
.lv{display:inline-block;min-width:24px;padding:2px 8px;border-radius:6px;color:#fff;font-size:12px;font-weight:700}
.flags{background:#fef2f2;border:1px solid #fecaca;border-radius:14px;padding:20px 24px;margin-top:20px}
.flags h3{margin:0 0 8px;color:#b91c1c;font-size:16px}
.flags ul{margin:0;padding-left:20px;color:#7f1d1d;font-size:14px}
.radar{text-align:center}
.foot{margin-top:24px;color:var(--sub);font-size:12px;text-align:center}
@media(max-width:640px){.wrap{padding:16px 12px 40px}table{font-size:12px}.bar{width:70px}}
</style></head><body><div class="wrap">
<div class="hero">
  <h1>%(org)s · 企业/工厂健康度检查报告</h1>
  <div class="meta">%(modename)s · %(date)s %(auditor)s</div>
  <div class="score"><span class="num">%(total).2f</span>
    <span class="lv" style="background:%(color)s">%(code)s 级 · %(levelname)s</span>
    <span style="opacity:.7">/ 5.00</span></div>
</div>
%(flags)s
<div class="card radar">%(svg)s</div>
<div class="card"><h2>维度评分总表</h2><table>
<thead><tr><th>维度</th><th>名称</th><th class="ctr">得分</th><th>分布</th><th class="ctr">等级</th><th>关键发现</th></tr></thead>
<tbody>%(rows)s</tbody></table></div>
%(acts)s
<div class="foot">由 fore-vip-enterprise-health 生成 · 属管理诊断建议，不构成审计/法律/安全评价结论</div>
</div></body></html>""" % {
        "org": r["org"],
        "modename": {"enterprise": "企业型", "factory": "制造型", "group": "集团多厂"}[r["mode"]],
        "date": r["date"] or "", "auditor": ("· " + r["auditor"]) if r["auditor"] else "",
        "total": r["total"], "color": r["color"], "code": r["code"], "levelname": r["level_name"],
        "flags": flags_html, "svg": svg,
        "rows": "".join(rows_html),
        "acts": ('<div class="card"><h2>整改优先级（ICE）</h2><table><thead><tr>'
                 '<th>#</th><th>整改项</th><th>维度</th><th>预期 KPI</th><th>负责人</th><th>完成时间</th><th>ICE</th>'
                 '</tr></thead><tbody>%s</tbody></table></div>' % "".join(acts_html)) if acts_html else "",
    }


# ---------- 输入样例 ----------
DEMO = {
    "org": "示例精密制造有限公司",
    "mode": "factory",
    "date": "2026-09-07",
    "auditor": "检查人",
    "dims": {
        "E1": {"score": 3, "findings": ["三年战略有文档但无年度分解"]},
        "E2": {"score": 2, "findings": ["现金 runway 2.4 个月", "DSO 92 天"]},
        "E3": {"score": 4},
        "E4": 3, "E5": 3, "E6": 3, "E7": 3, "E8": 2, "E9": 3, "E10": 4,
        "F1": {"score": 2, "findings": ["OEE 51%"]},
        "F2": {"score": 2, "findings": ["FPY 84%", "无 Cpk 数据"]},
        "F3": 3, "F4": 2, "F5": 3, "F6": 3,
        "F7": {"score": 1, "findings": ["特种作业无证上岗 2 人"]},
        "F8": 3, "F9": 3, "F10": 3, "F11": 3,
    },
    "red_flags": ["现金 runway < 3 个月", "特种作业无证上岗"],
    "actions": [
        {"title": "特种作业人员取证并冻结无证上岗", "dim": "F7", "impact": 10,
         "confidence": 9, "ease": 8, "owner": "安全部", "due": "2026-10-15",
         "kpi": "持证率 100%"},
        {"title": "建立应收专项清收机制", "dim": "E2", "impact": 9, "confidence": 8,
         "ease": 5, "owner": "财务总监", "due": "2026-11-30", "kpi": "DSO 92→70 天"},
    ],
    "data_gaps": ["近 12 个月质量成本 COPQ 未统计"],
}


def main():
    ap = argparse.ArgumentParser(description="企业/工厂健康度评分引擎")
    ap.add_argument("-i", "--input", help="输入 JSON 路径")
    ap.add_argument("-o", "--out", help="输出 Markdown 路径")
    ap.add_argument("--html", help="输出 HTML 报告路径")
    ap.add_argument("--radar", help="输出雷达图 SVG 路径")
    ap.add_argument("--json", help="输出计算结果 JSON 路径")
    ap.add_argument("--template-demo", action="store_true", help="打印输入 JSON 样例")
    args = ap.parse_args()

    if args.template_demo:
        print(json.dumps(DEMO, ensure_ascii=False, indent=2))
        return 0

    if not args.input:
        ap.error("需要 -i/--input，或用 --template-demo 查看样例")

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    r = evaluate(data)

    all_rows = []
    for k in ["E", "F", "G"]:
        c = r["cards"].get(k)
        if c and c.get("rows"):
            all_rows.extend(c["rows"])
    svg = radar_svg(all_rows, r["total"], r["color"])

    md = render_md(r)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        print(md)

    if args.radar and svg:
        with open(args.radar, "w", encoding="utf-8") as f:
            f.write(svg)
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(render_html(r, svg))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)

    sys.stderr.write("[OK] %s 综合 %.2f / %s 级 %s\n"
                     % (r["org"], r["total"], r["code"], r["level_name"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
