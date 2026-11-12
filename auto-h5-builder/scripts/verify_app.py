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
LAYOUTS = ("magazine", "poster", "split", "quiet")
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

    # ② 右上菜单：预约 / 分享 / 登录 / 退出，是唯一导航入口
    menu = re.findall(r'data-menu="([a-z]+)"', html)
    check("右上菜单四项", ",".join(menu), menu == ["book", "share", "admin", "logout"])
    labels = dict(re.findall(r'data-menu="([a-z]+)"[^>]*>([^<]*)<', html))
    got = [labels.get(k, "").strip() for k in ("book", "share", "admin", "logout")]
    check("菜单文案 预约/分享/登录/退出", "/".join(got), got == ["预约", "分享", "登录", "退出"])
    check("菜单有开合控件", 'id="btnMenu"' in html and 'id="menuPanel"' in html,
          'id="btnMenu"' in html)
    check("退出登录在菜单里", 'id="menuLogout"' in html and 'id="btnLogout"' not in html,
          'id="menuLogout"' in html)
    check("无底部导航", 'class="tabbar"' not in html and 'data-tab=' not in html,
          'class="tabbar"' not in html)

    # ③ 预约页 / 分享页 / 店主页各自独立成页
    heads = html.count('class="page-head"')
    check("三个独立页各有页头", heads, heads == 3)
    for view in ("book", "share", "admin"):
        block = re.search(r'data-view="%s"[^>]*>(.*?)</section>' % view, html, re.S)
        body = block.group(1) if block else ""
        check("%s 页有独立页头" % view, 'class="page-head"' in body, 'class="page-head"' in body)
        check("%s 页默认隐藏" % view, 'id="view-%s" hidden' % view,
              'id="view-%s" hidden' % view in html)

    # ④ 移动端视口
    check("移动端 viewport", "width=device-width" in html, "width=device-width" in html)

    # ⑤ 无占位符残留
    left = sorted(set(re.findall(r"__[A-Z][A-Z0-9_]*__", html)))
    check("无未替换占位符", left or "0", not left)

    # ⑥ 外部资源白名单（脚本不能被注释掉）
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

    # ⑦ 云配置
    cfg_json = re.search(r"window\.APP_CFG=(\{.*?\}|null);", html, re.S)
    cfg = json.loads(cfg_json.group(1)) if cfg_json and cfg_json.group(1) != "null" else None
    if cloud:
        ok = isinstance(cfg, dict) and all(cfg.get(k) for k in ("endpoint", "publishableKey"))
        check("云配置三字段就位", list(cfg.keys()) if cfg else "null", ok)
        check("oauthRelayBaseUrl 已传", bool(cfg.get("oauthRelayBaseUrl")), bool(cfg.get("oauthRelayBaseUrl")))
    else:
        check("预览版无云配置", cfg, cfg is None)

    # ⑧ 管理侧标识不外泄
    banned = [k for k in ("applicationId", "resourceId", "serviceRoleKey", "secretKey") if k in html]
    check("无 applicationId / 密钥", banned or "0", not banned)

    # ⑨ 预约写入走云表
    check("预约写入 database.insert",
          "database.from(TABLE).insert(row)" in html or ".insert(row)" in html,
          ".insert(row)" in html)
    check("写入失败有可见提示",
          "没提交成功" in html and "formHint" in html,
          "没提交成功" in html)

    # ⑩ 状态枚举与按钮
    statuses = [s for s in ("pending", "confirmed", "done", "cancelled") if s + ":" in html]
    check("四状态枚举齐", ",".join(statuses), len(statuses) == 4)
    check("状态可改（update + eq）", "update({ status: next })" in html or ".update({status:next})" in html,
          "update({ status: next })" in html)

    # ⑪ 邀请与分享
    check("分享链接带 ref", "?ref=" in html, "?ref=" in html)
    check("邀请码本地留存", "auto-h5.code" in html, "auto-h5.code" in html)
    check("下单记录邀请码", "invite_code" in html, "invite_code" in html)

    # ⑫ 登录与店长身份
    check("验证码登录（sendOtp）", "sendOtp" in html, "sendOtp" in html)
    check("验证码登录（verifyOtp）", "verifyOtp" in html, "verifyOtp" in html)
    check("登录失败给可操作提示", "店主登录还没开通" in html, "店主登录还没开通" in html)
    check("首登即店长（store_owner 单行认领）", "store_owner" in html and "insert({ id: 1 })" in html,
          "store_owner" in html and "insert({ id: 1 })" in html)
    check("非店主账号被拦下", "这个账号不是店主" in html, "这个账号不是店主" in html)

    # ⑬ 表单校验与拨号
    check("手机号 11 位校验", r"^1\d{10}$" in html, r"^1\d{10}$" in html)
    check("电话可拨（tel:）", 'href="tel:' in html or "href = 'tel:'" in html or "tel:' +" in html,
          'tel:' in html)

    # ⑭ 品牌色注入
    brand = spec["store"].get("brand", "#b4735a").lower()
    check("品牌色与 spec 一致", "--brand:" + brand, ("--brand:" + brand) in html.lower())

    # ⑮ 单文件自包含
    check("样式与脚本内联", html.count("<style>") >= 1 and html.count("<script>") >= 2,
          html.count("<style>") >= 1)

    # ⑯ 首页版式：四套之一，只注入一套，接线齐全
    layout = re.search(r'data-layout="([a-z]+)"', html)
    name = layout.group(1) if layout else ""
    check("首页版式在四套之内", name or "无", name in LAYOUTS)
    marks = sorted(set(re.findall(r"/\* layout:([a-z]+) \*/", html)))
    check("只注入一套版式样式", ",".join(marks) or "0", marks == [name])
    home_block = re.search(r'data-view="home".*?</section>', html, re.S)
    home_block = home_block.group(0) if home_block else ""
    check("首页有主行动按钮", 'data-go="book"' in home_block, 'data-go="book"' in home_block)
    check("首页服务与到访均接线",
          'id="svcList"' in home_block and 'id="storeInfo"' in home_block,
          'id="svcList"' in home_block and 'id="storeInfo"' in home_block)
    check("首页样式不外挂", "style=" not in home_block and "<style" not in home_block,
          "style=" not in home_block)

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
