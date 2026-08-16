#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号草稿推送 —— 命令行入口
子命令：config / token / push / status

依赖：Python 3 标准库（无需 pip install）
凭据：环境变量 WX_APPID / WX_APPSECRET 优先；否则读本地 .credentials.json（0600）
"""

import argparse
import json
import os
import sys
import time
import mimetypes
import uuid
import urllib.request
import urllib.parse
import urllib.error

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED_FILE = os.path.join(SKILL_DIR, ".credentials.json")
TOKEN_CACHE = os.path.join(SKILL_DIR, ".token_cache.json")

WX_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
WX_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
WX_DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"
WX_PUBLISH_SUBMIT_URL = "https://api.weixin.qq.com/cgi-bin/freepublish/submit"
WX_PUBLISH_GET_URL = "https://api.weixin.qq.com/cgi-bin/freepublish/get"

PUBLISH_STATUS_TEXT = {
    0: "发布中",
    1: "发布成功",
    2: "发布失败",
    3: "原创审核失败",
    4: "系统错误",
}


# ---------- 凭据 ----------
def load_credentials():
    appid = os.environ.get("WX_APPID")
    secret = os.environ.get("WX_APPSECRET")
    if appid and secret:
        return appid, secret
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("appid"), data.get("appsecret")
        except Exception:
            return None, None
    return None, None


def save_credentials(appid, secret):
    data = {"appid": appid, "appsecret": secret}
    # 先写临时文件再改名，保证 0600 权限
    tmp = CRED_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, CRED_FILE)
    os.chmod(CRED_FILE, 0o600)
    print("已保存凭据到 %s（权限 0600）" % CRED_FILE)


# ---------- HTTP ----------
def http_get_json(url):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        raise RuntimeError("HTTP %s: %s" % (e.code, body))
    except urllib.error.URLError as e:
        raise RuntimeError("网络错误: %s" % e.reason)


def http_post_json(url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        raise RuntimeError("HTTP %s: %s" % (e.code, body))
    except urllib.error.URLError as e:
        raise RuntimeError("网络错误: %s" % e.reason)


def http_upload_image(url, file_path):
    boundary = uuid.uuid4().hex
    filename = os.path.basename(file_path)
    mime = mimetypes.guess_type(file_path)[0] or "image/jpeg"
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    parts = []
    parts.append(("--%s" % boundary).encode())
    parts.append(
        ('Content-Disposition: form-data; name="media"; filename="%s"' % filename).encode("utf-8")
    )
    parts.append(("Content-Type: %s" % mime).encode())
    parts.append(b"")
    parts.append(file_bytes)
    parts.append(("--%s--" % boundary).encode())
    parts.append(b"")
    body = b"\r\n".join(parts)
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("上传封面 HTTP %s: %s" % (e.code, e.read().decode("utf-8", "ignore")))
    except urllib.error.URLError as e:
        raise RuntimeError("上传封面网络错误: %s" % e.reason)


# ---------- token ----------
def get_access_token(force=False):
    appid, secret = load_credentials()
    if not appid or not secret:
        raise RuntimeError("未配置凭据：请先设置环境变量 WX_APPID/WX_APPSECRET，或执行 config 子命令。")

    # 复用缓存
    if not force and os.path.exists(TOKEN_CACHE):
        try:
            with open(TOKEN_CACHE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            if cache.get("appid") == appid and time.time() < cache.get("expires_at", 0) - 60:
                return cache["access_token"]
        except Exception:
            pass

    url = "%s?%s" % (
        WX_TOKEN_URL,
        urllib.parse.urlencode(
            {"grant_type": "client_credential", "appid": appid, "secret": secret}
        ),
    )
    resp = http_get_json(url)
    if "access_token" not in resp:
        raise RuntimeError("获取 access_token 失败: %s" % resp.get("errmsg", resp))
    expires_in = int(resp.get("expires_in", 7200))
    cache = {
        "appid": appid,
        "access_token": resp["access_token"],
        "expires_at": int(time.time()) + expires_in,
    }
    try:
        with open(TOKEN_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        os.chmod(TOKEN_CACHE, 0o600)
    except Exception:
        pass
    return resp["access_token"]


# ---------- 封面 ----------
def resolve_thumb_media_id(token, cover):
    """cover 为本地图片路径则上传，否则当作已有 media_id 直用。"""
    if cover and os.path.isfile(cover):
        resp = http_upload_image(
            "%s?%s" % (WX_MATERIAL_URL, urllib.parse.urlencode({"access_token": token, "type": "image"})),
            cover,
        )
        if "media_id" not in resp:
            raise RuntimeError("上传封面失败: %s" % resp.get("errmsg", resp))
        return resp["media_id"]
    if cover:
        return cover  # 已是 media_id
    raise RuntimeError("缺少封面：请提供本地图片路径或已有的 thumb_media_id。")


# ---------- 草稿 / 发布 ----------
def add_draft(token, article):
    url = "%s?access_token=%s" % (WX_DRAFT_ADD_URL, token)
    resp = http_post_json(url, {"articles": [article]})
    if resp.get("errcode", 0) != 0 or "media_id" not in resp:
        raise RuntimeError("新建草稿失败: %s" % resp.get("errmsg", resp))
    return resp


def submit_publish(token, media_id):
    url = "%s?access_token=%s" % (WX_PUBLISH_SUBMIT_URL, token)
    resp = http_post_json(url, {"media_id": media_id})
    if resp.get("errcode", 0) != 0:
        raise RuntimeError("发布失败: %s" % resp.get("errmsg", resp))
    return resp


def get_publish_status(token, publish_id):
    url = "%s?access_token=%s" % (WX_PUBLISH_GET_URL, token)
    resp = http_post_json(url, {"publish_id": publish_id})
    if resp.get("errcode", 0) != 0:
        raise RuntimeError("查询发布状态失败: %s" % resp.get("errmsg", resp))
    status = resp.get("publish_status")
    resp["publish_status_text"] = PUBLISH_STATUS_TEXT.get(status, "未知(%s)" % status)
    return resp


# ---------- 子命令 ----------
def cmd_config(args):
    save_credentials(args.appid, args.secret)
    # 立即做一次连通校验
    try:
        tk = get_access_token(force=True)
        print("凭据有效，access_token 获取成功（已脱敏，长度 %d）。" % len(tk))
    except Exception as e:
        print("凭据已保存，但连通校验失败：%s" % e)


def cmd_token(args):
    tk = get_access_token(force=args.force)
    mask = tk[:6] + "****" + tk[-4:] if len(tk) > 12 else "****"
    print("access_token: %s（已脱敏）" % mask)


def cmd_push(args):
    if not args.yes:
        print("【安全确认】未加 --yes，仅做参数校验，不会真正写入草稿或发布。")
        print("标题: %s" % args.title)
        print("作者: %s" % (args.author or "(空)"))
        print("摘要: %s" % (args.digest or "(空，微信自动取正文前字)"))
        print("正文: %s" % args.content)
        print("封面: %s" % args.cover)
        print("原文链接: %s" % (args.source_url or "(空)"))
        print("模式: %s" % ("仅草稿" if args.draft_only else "草稿+发布"))
        return

    if not os.path.isfile(args.content):
        raise RuntimeError("正文文件不存在: %s" % args.content)
    with open(args.content, "r", encoding="utf-8") as f:
        content_html = f.read()

    token = get_access_token()
    thumb_media_id = resolve_thumb_media_id(token, args.cover)

    article = {
        "title": args.title,
        "author": args.author or "",
        "digest": args.digest or "",
        "content": content_html,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    if args.source_url:
        article["content_source_url"] = args.source_url

    draft = add_draft(token, article)
    media_id = draft["media_id"]
    print("草稿已创建 media_id=%s" % media_id)

    if args.draft_only:
        print("（仅写入草稿箱，未发布）可在公众号后台草稿箱查看。")
        return

    pub = submit_publish(token, media_id)
    publish_id = pub.get("publish_id")
    print("已提交发布 publish_id=%s" % publish_id)
    try:
        st = get_publish_status(token, publish_id)
        print("发布状态: %s" % st.get("publish_status_text"))
    except Exception as e:
        print("已提交，状态查询稍后可用：%s" % e)


def cmd_status(args):
    token = get_access_token()
    st = get_publish_status(token, args.publish_id)
    print("publish_id=%s 状态=%s" % (args.publish_id, st.get("publish_status_text")))
    if st.get("article_detail"):
        d = st["article_detail"]
        print("标题: %s" % d.get("title", ""))


def build_parser():
    p = argparse.ArgumentParser(description="公众号草稿推送")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("config", help="保存 AppID/AppSecret")
    c.add_argument("--appid", required=True)
    c.add_argument("--secret", required=True)
    c.set_defaults(func=cmd_config)

    t = sub.add_parser("token", help="获取并打印 access_token")
    t.add_argument("--force", action="store_true", help="忽略缓存强制刷新")
    t.set_defaults(func=cmd_token)

    pu = sub.add_parser("push", help="写入草稿并（可选）发布")
    pu.add_argument("--title", required=True)
    pu.add_argument("--author", default="")
    pu.add_argument("--digest", default="")
    pu.add_argument("--content", required=True, help="正文 HTML 文件路径")
    pu.add_argument("--cover", required=True, help="封面图本地路径 或 已有 thumb_media_id")
    pu.add_argument("--source-url", default="", help="原文链接 content_source_url")
    pu.add_argument("--draft-only", action="store_true", help="仅写入草稿箱，不发布")
    pu.add_argument("--yes", action="store_true", help="确认执行真实写入/发布")
    pu.set_defaults(func=cmd_push)

    s = sub.add_parser("status", help="查询发布状态")
    s.add_argument("--publish-id", required=True)
    s.set_defaults(func=cmd_status)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
