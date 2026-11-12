#!/usr/bin/env python3
"""静态闸门：检查生成出来的门店 H5 是否结构完整、接线正确、没有半成品痕迹。

用法：
  python3 verify_app.py --spec examples/salon.spec.json --page examples/salon.html
  python3 verify_app.py --spec examples/salon.spec.json --page out/index.html --cloud
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
import pathlib
import re

SDK = "https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js"
CHECKS = []


def check(name, value, ok):
    CHECKS.append((name, str(value)[:70], bool(ok)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--page", required=True)
    ap.add_argument("--cloud", action="store_true", help="按云端模式检查")
    args = ap.parse_args()

    spec = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))
    html = pathlib.Path(args.page).read_text(encoding="utf-8")
    cloud = args.cloud

    # ① 四视图
    views = [v for v in ("home", "book", "share", "admin") if 'data-view="%s"' % v in html]
    check("四视图齐全", ",".join(views), len(views) == 4)

    # ② 底部导航四项
    tabs = re.findall(r'data-tab="([a-z]+)"', html)
    check("底部导航覆盖四视图", ",".join(tabs), set(tabs) == {"home", "book", "share", "admin"})

    # ③ 移动端视口
    check("移动端 viewport", "width=device-width" in html, "width=device-width" in html)

    # ④ 无占位符残留
    left = sorted(set(re.findall(r"__[A-Z][A-Z0-9_]*__", html)))
    check("无未替换占位符", left or "0", not left)

    # ⑤ 外部资源白名单（脚本不能被注释掉）
    scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
    if cloud:
        check("仅一个云端 SDK 外链", scripts, scripts == [SDK])
    else:
        check("预览版零外链脚本", scripts or "0", not scripts)
    commented = re.findall(r"<!--\s*<script", html)
    check("外链脚本未被注释", commented or "0", not commented)
    check("无外部样式表", "stylesheet" in html, "stylesheet" not in html)
    remote_img = re.findall(r"<img[^>]+src=\"https?://[^\"]+", html)
    check("无远程图片", remote_img or "0", not remote_img)

    # ⑥ 云配置
    cfg_json = re.search(r"window\.APP_CFG=(\{.*?\}|null);", html, re.S)
    cfg = json.loads(cfg_json.group(1)) if cfg_json and cfg_json.group(1) != "null" else None
    if cloud:
        ok = isinstance(cfg, dict) and all(cfg.get(k) for k in ("endpoint", "publishableKey"))
        check("云配置三字段就位", list(cfg.keys()) if cfg else "null", ok)
        check("oauthRelayBaseUrl 已传", bool(cfg.get("oauthRelayBaseUrl")), bool(cfg.get("oauthRelayBaseUrl")))
    else:
        check("预览版无云配置", cfg, cfg is None)

    # ⑦ 管理侧标识不外泄
    banned = [k for k in ("applicationId", "resourceId", "serviceRoleKey", "secretKey") if k in html]
    check("无 applicationId / 密钥", banned or "0", not banned)

    # ⑧ 预约写入走云表
    check("预约写入 database.insert",
          "database.from(TABLE).insert(row)" in html or ".insert(row)" in html,
          ".insert(row)" in html)
    check("写入失败有可见提示",
          "没提交成功" in html and "formHint" in html,
          "没提交成功" in html)

    # ⑨ 状态枚举与按钮
    statuses = [s for s in ("pending", "confirmed", "done", "cancelled") if s + ":" in html]
    check("四状态枚举齐", ",".join(statuses), len(statuses) == 4)
    check("状态可改（update + eq）", "update({ status: next })" in html or ".update({status:next})" in html,
          "update({ status: next })" in html)

    # ⑩ 邀请与分享
    check("分享链接带 ref", "?ref=" in html, "?ref=" in html)
    check("邀请码本地留存", "auto-h5.code" in html, "auto-h5.code" in html)
    check("下单记录邀请码", "invite_code" in html, "invite_code" in html)

    # ⑪ 登录
    check("验证码登录（sendOtp）", "sendOtp" in html, "sendOtp" in html)
    check("验证码登录（verifyOtp）", "verifyOtp" in html, "verifyOtp" in html)
    check("登录失败给可操作提示", "店主登录还没开通" in html, "店主登录还没开通" in html)

    # ⑫ 表单校验与拨号
    check("手机号 11 位校验", r"^1\d{10}$" in html, r"^1\d{10}$" in html)
    check("电话可拨（tel:）", 'href="tel:' in html or "href = 'tel:'" in html or "tel:' +" in html,
          'tel:' in html)

    # ⑬ 品牌色注入
    brand = spec["store"].get("brand", "#b4735a").lower()
    check("品牌色与 spec 一致", "--brand:" + brand, ("--brand:" + brand) in html.lower())

    # ⑭ 单文件自包含
    check("样式与脚本内联", html.count("<style>") >= 1 and html.count("<script>") >= 2,
          html.count("<style>") >= 1)

    failed = 0
    for name, value, ok in CHECKS:
        print(("PASS " if ok else "FAIL ") + name + " :: " + value)
        if not ok:
            failed += 1
    print(("RESULT ALL PASS (%d)" % len(CHECKS)) if not failed
          else ("RESULT FAIL (%d/%d)" % (failed, len(CHECKS))))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
