# 付费 TTS 方案配置指南（兜底）

> 仅当免费引擎（edge-tts / macOS say）均不可用时启用。启用前必须向用户说明：付费方案需要注册账号、开通服务、配置密钥，并会产生费用。用户确认后再按下文引导配置。

## 方案对比

| 方案 | 免费额度 | 音质 | 中文音色 | 适合 |
|------|---------|------|---------|------|
| 腾讯云 TTS | 每月 100 万字符（基础音色） | 高 | 多 | 国内首选，小程序生态友好 |
| 讯飞开放平台 | 每日 500 次（在线合成） | 高 | 多（含方言） | 音色丰富、情感音色 |
| MiniMax TTS | 少量体验额度 | 极高（语音大模型） | 多（拟真） | 对拟真度要求高 |
| Azure Speech | 每月 50 万字符（F0 层） | 高 | 多 | 有 Azure 账号时 |

## 腾讯云 TTS（推荐兜底）

1. 注册/登录腾讯云：https://console.cloud.tencent.com/
2. 开通「语音合成」：控制台搜索「语音合成」，开通基础语音合成（含免费额度）
3. 获取密钥：访问「访问管理 → API 密钥管理」，创建/查看 `SecretId` 与 `SecretKey`
4. 安装 SDK：`pip3 install tencentcloud-sdk-python-tts`
5. 配置密钥（二选一）：
   - 环境变量：`export TENCENT_SECRET_ID=xxx`、`export TENCENT_SECRET_KEY=xxx`
   - 或告知 Agent 密钥，由用户自行保管在本地 `~/.fore-vip/tts.json`
6. 音色列表参考：https://cloud.tencent.com/document/product/1073/92668
7. 调用示例（Agent 现场生成脚本或扩写 tts.py）：

```python
from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import tts_client, models
cred = credential.Credential(SECRET_ID, SECRET_KEY)
client = tts_client.TtsClient(cred, "ap-guangzhou")
req = models.TextToVoiceRequest()
req.Text = "待转换文本"
req.SessionId = "fore-vip-tts"
req.ModelType = 1          # 1=基础音型（走免费额度）
req.VoiceType = 101001     # 智瑜，情感女声
with open("out.mp3", "wb") as f:
    f.write(client.TextToVoice(req).Audio)  # 返回 base64，需解码
```

> 注意：`Audio` 字段为 base64 编码，需 `base64.b64decode()` 后落盘。

## 讯飞开放平台

1. 注册：https://www.xfyun.cn/ ，实名认证
2. 控制台创建应用 → 领取「在线语音合成」免费包
3. 记录 `APPID` / `APIKey` / `APISecret`
4. 安装：`pip3 install websocket-client`
5. 文档：https://www.xfyun.cn/doc/tts/online_tts/API.html （WebSocket 接口，Agent 按文档现场实现）

## MiniMax TTS

1. 注册：https://platform.minimaxi.com/ ，开通语音合成
2. 创建 API Key（平台 → 接口密钥）
3. 计费按字符，无稳定免费额度，启用前明确告知用户计费规则
4. 文档：https://platform.minimaxi.com/document/T2A%20V2

## Azure Speech

1. 注册 Azure 账号，创建 Speech 资源（F0 免费层）
2. 获取 `SPEECH_KEY` 与 `SPEECH_REGION`
3. 安装：`pip3 install azure-cognitiveservices-speech`
4. 免费层每月 50 万字符，注意不要误建 S0 付费层

## 密钥安全红线

- 密钥只允许存放在用户本地（环境变量或 `~/.fore-vip/` 下的本地配置文件），严禁写入 SKILL 仓库、代码注释、聊天记录或任何会上传的位置
- 付费调用前必须得到用户明确确认；每次调用失败重试不超过 2 次，避免重复计费
