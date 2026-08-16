# 公众号草稿推送 Skill

将文章（标题 / 作者 / 摘要 / 正文 HTML / 封面图）写入微信公众号**草稿箱**并**发布**。基于微信公众平台官方接口，无第三方中转。

## 安装

1. 将本目录整体放入：
   - 用户级：`~/.workbuddy/skills/wechat-oa-draft-push/`
   - 或项目级：`<项目>/.workbuddy/skills/wechat-oa-draft-push/`
2. 依赖：Python 3（标准库即可，无需 `pip install`）。
3. 对话中唤起本技能（说「推送公众号文章」「公众号草稿」等），按提示完成首次配置。

## 首次配置（收集 AppID / AppSecret）

在公众号后台「设置与开发 → 基本配置」获取 **AppID** 与 **AppSecret**，任选一种方式配置：

**方式 A：环境变量（推荐，更安全）**
```bash
export WX_APPID="wx你的appid"
export WX_APPSECRET="你的appsecret"
```

**方式 B：本地文件**
```bash
python3 scripts/oa_push.py config --appid "wx你的appid" --secret "你的appsecret"
```
凭据保存在 `<技能目录>/.credentials.json`，权限 0600，仅在本地使用，不会回显或外传。

> 注意：若公众号后台配置了「IP 白名单」，需把运行本技能机器的出口 IP 加入白名单，否则会报 `40164`。

## 使用

把文章正文写成 HTML 文件（如 `article.html`），然后：

```bash
# 草稿 + 发布（确认后执行，务必带 --yes）
python3 scripts/oa_push.py push \
  --title "标题" --author "作者" --digest "摘要" \
  --content article.html --cover cover.jpg --yes

# 仅写入草稿箱，暂不发布
python3 scripts/oa_push.py push \
  --title "标题" --content article.html --cover cover.jpg --draft-only --yes
```

查询发布状态：
```bash
python3 scripts/oa_push.py status --publish-id <PUBLISH_ID>
```

## 子命令

| 命令 | 说明 |
|------|------|
| `config --appid --secret` | 保存凭据并做连通校验 |
| `token [--force]` | 获取并打印 access_token（脱敏） |
| `push --title --content --cover [--author --digest --source-url --draft-only --yes]` | 写入草稿并可选发布 |
| `status --publish-id` | 查询发布状态 |

## 注意事项

- `封面图`为必填，--cover 传本地图片路径会自动上传为永久素材；传已有 `thumb_media_id` 则直接使用。
- `push` 不带 `--yes` 时只做参数预览、不真实调用，防止误发。
- 仅支持已开通「发布能力」的公众号（绝大多数认证号默认可用）。
