---
name: wechat-oa-draft-push
display_name: 公众号草稿推送
display_name_en: WeChat OA Draft Pusher
description: 微信公众号草稿推送助手。将文章（标题/作者/摘要/正文 HTML/封面图）保存为草稿并发布到微信公众号。安装后向用户收集 AppID 与 AppSecret，用户完成文章内容并确认后一键推送。触发词：公众号草稿、草稿推送、推送公众号、发布公众号文章、公众号发文、草稿箱、freepublish。
description_zh: 将文章保存为公众号草稿并发布，安装后收集 AppID/AppSecret，确认即推送。
description_en: Save articles as WeChat Official Account drafts and publish them. Collects AppID/AppSecret after install; pushes on user confirmation.
category: social
version: 1.0.0
author: WISE
---

# 公众号草稿推送

## 概述

将用户提供的文章（标题、作者、摘要、正文 HTML、封面图）写入微信公众号**草稿箱**，并按需**发布**。全程贴合微信公众平台官方接口（`cgi-bin/draft/add` + `cgi-bin/freepublish/submit`），不做任何第三方中转。

适用于：把已写好的推文快速发到公众号、把 AI 生成/整理好的长文一键群发、把本地 HTML 内容转为正式推文。

## 触发规则

| 场景 | 处理 |
|------|------|
| 用户要发/推/发布公众号文章、写入草稿箱 | 执行推送流程 |
| 用户问本技能能干嘛、怎么用 | 仅介绍技能 |
| 用户只给零散想法、未形成文章 | 先协助成稿，再进入推送流程 |

## 能力边界（事实）

- 本技能只做「草稿写入 + 发布」，不负责**写文章**（写文请用写作类技能，成稿后回到本技能推送）。
- 仅支持**已认证的服务号/订阅号**且开通了「发布能力」；草稿箱与发布接口对绝大多数公众号开放。
- 封面图 `thumb_media_id` 为**必填**，发布前必须提供封面（本地图片会自动上传为永久素材）。
- `access_token` 有效期 7200 秒，脚本自动缓存并在过期前复用。

## 基础设定（SKILL 配置）

凭据来源（二选一，环境变量优先于本地文件）：

1. **环境变量**（推荐，更安全）：`WX_APPID`、`WX_APPSECRET`
2. **本地文件**：`~/.workbuddy/skills/wechat-oa-draft-push/.credentials.json`，权限 0600，结构 `{"appid":"...","appsecret":"..."}`

> 安全约定：AppSecret 属敏感凭据，仅落本地 0600 文件或环境变量，绝不写进 SKILL 文档、日志、产物或对外回复。脚本输出会脱敏。

## 安装指引

1. 将本技能目录放入 `~/.workbuddy/skills/wechat-oa-draft-push/`（用户级）或项目级 `.workbuddy/skills/`。
2. 依赖：Python 3（标准库即可，无需 `pip install`）。
3. 首次对话本技能会自动引导你配置 AppID / AppSecret（见下）。
4. 完整说明见 `README.md`。

## 首次使用：收集 AppID 与 AppSecret

> 对应需求：「安装技能后向用户收集 APPID、密钥」

1. 检查是否已有凭据（环境变量或 `.credentials.json`）。
2. 若无，向用户**明确说明用途**（调用微信接口所需，仅保存在本地），请用户提供：
   - **AppID**（公众号后台「设置与开发 → 基本配置 → 开发者ID」）
   - **AppSecret**（同一页面「开发者密码」，点击「重置」可见，仅显示一次）
3. 写入凭据：
   ```bash
   python3 <技能目录>/scripts/oa_push.py config --appid <APPID> --secret <APPSECRET>
   ```
4. 立即做一次连通性校验（获取 token），失败则提示用户核对 AppID/AppSecret 与 IP 白名单。
   ```bash
   python3 <技能目录>/scripts/oa_push.py token
   ```

## 推送流程：用户成稿 → 确认 → 发布

> 对应需求：「用户完成文章的内容发送推送、确认时完成文章的推送」

**⚠️ 关键：必须先向用户完整复述待推送信息（标题、作者、摘要、封面、是否立即发布），等用户明确确认后，才执行实际发布。不要在确认前调用发布接口。**

1. 收集文章要素：
   - `标题`（必填）
   - `作者`（可选）
   - `摘要`（可选，留空微信自动取正文前若干字）
   - `正文`（必填，HTML 片段，写入文件后传路径）
   - `封面图`（必填，本地图片路径；或已存在的 `thumb_media_id`）
   - `原文链接 content_source_url`（可选）
2. 将正文 HTML 保存为临时文件（如 `article.html`），便于脚本读取。
3. **向用户展示并确认**：标题 / 作者 / 摘要 / 封面文件名 / 是否立即发布。
4. 用户确认后执行：
   ```bash
   # 立即发布（草稿+发布）
   python3 <技能目录>/scripts/oa_push.py push \
     --title "标题" --author "作者" --digest "摘要" \
     --content article.html --cover cover.jpg --yes

   # 仅写入草稿箱、暂不发布
   python3 <技能目录>/scripts/oa_push.py push \
     --title "标题" --content article.html --cover cover.jpg --draft-only --yes
   ```
5. 脚本返回 `media_id`（草稿）、`publish_id`（发布）与发布状态。将结果反馈给用户，并给出公众号后台链接供核对。
6. 如需查询发布状态：
   ```bash
   python3 <技能目录>/scripts/oa_push.py status --publish-id <PUBLISH_ID>
   ```

## 错误处理（事实 → 建议）

| 现象 | 含义 | 处理建议 |
|------|------|----------|
| `40013 invalid appid` | AppID 错误 | 核对 AppID |
| `40125 invalid appsecret` | AppSecret 错误 | 重置并重新 `config` |
| `40164` / `50001` | IP 不在白名单 | 公众号后台「IP白名单」加入当前出口 IP |
| `40007 invalid media_id` | 封面 media_id 失效 | 重新上传封面 |
| `45009` 接口调用超限 | 触发频率限制 | 稍后重试 |

## 输出约定

- 公开发回给用户的内容只包含：标题、media_id、publish_id、发布状态、后台核对链接。
- 绝不回显 AppSecret、access_token、完整请求体。
