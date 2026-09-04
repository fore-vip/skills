---
name: fore-vip-tts
display_name: 文字转语音
display_name_en: Text to Speech
description: 文字转语音（TTS）助手（fore.vip）。把用户输入的文字直接合成为语音文件，不总结、不分析、不加任何多余内容，拿到文字就转。引擎按「环境默认 → 免费方案（edge-tts / macOS say）→ 付费方案兜底（引导用户配置）」三级选择；多音色时弹窗让用户挑选；生成的语音文件优先存入资料库，无资料库时引导配置 IMA 或文档提供方后转存。触发词：转语音、文字转语音、语音合成、TTS、朗读、念一下、读出来、转成音频、配音、生成语音、把这段话变成语音。
description_zh: 文字转语音（TTS）助手。把输入的文字直接合成为语音文件，不总结、不分析、不加任何多余内容。引擎按「环境默认 → 免费方案（edge-tts / macOS say）→ 付费方案兜底」三级选择；多音色时弹窗让用户挑选；生成的语音文件优先存入资料库，无资料库时引导配置 IMA 或文档提供方后转存。
description_en: "Text-to-speech (TTS) assistant. Converts input text straight into an audio file with no summarization, analysis or filler. Engines are selected in three tiers: environment default, free options (edge-tts / macOS say), then paid fallback with setup guidance. When multiple voices are available the user picks via a prompt. Generated audio is stored in the library when available, otherwise the user is guided to configure IMA or another document provider first."
category: audio
version: 1.0.0
author: fore.vip
agent_created: true
---

# 文字转语音 · TTS

把用户给的文字**直接**合成为语音文件。本技能的全部价值在于「不废话、立刻出声音」。

## 核心铁律

1. **不做任何多余操作**：不总结文本、不分析内容、不纠错改写、不加「转换完成」「希望对你有帮助」等前后缀，用户给什么文字就转什么文字。
2. **只处理明确的 TTS 意图**：用户要求「转语音/朗读/念一下/配音」等才触发；闲聊中提到语音不算。
3. **正文文字即输入**：用户消息中的文字（或明确指定的文件内容）就是待合成文本，原样传入，一个字都不改。
4. **多音色必选**：可用音色多于 1 个且用户未指定时，必须弹窗（AskUserQuestion）让用户选，不要替用户决定音色。

## 工作流程

### 第一步：选引擎（三级递进）

按以下顺序确定引擎，命中即停：

1. **环境默认方案**：检查当前环境是否已提供 TTS 工具（如平台内置语音合成工具）。有 → 直接用。
2. **免费方案**（无默认工具时，用本技能脚本探测）：
   ```bash
   python3 <skill_dir>/scripts/tts.py --list-voices
   ```
   - 返回 `edge` 可用 → 用 edge-tts（免费网络引擎，音色自然，音色多）
   - 返回仅 `say` 可用（macOS）→ 用 say（免费本地引擎）
   - 两者皆无 → 跳到第三级
3. **付费方案兜底**（免费均不可用）：读 `references/paid-tts-providers.md`，向用户说明需要注册、配置密钥、可能产生费用，**经用户确认后**引导其完成配置（推荐腾讯云 TTS，有免费额度），再执行合成。密钥只存用户本地，严禁入库入仓。

### 第二步：定音色（弹窗选择）

```bash
python3 <skill_dir>/scripts/tts.py --list-voices --engine edge   # 或 say
```

- 可用音色 **> 1 个** 且用户未指定 → 用 AskUserQuestion 弹窗：常见中文音色列出 3-4 个选项（含性别/风格简述），用户也可通过 Other 输入自选音色名。
- 用户已指定音色（如「用婷婷的声音」「男声」）→ 匹配对应音色，匹配不上时弹窗展示可用音色让用户重选。
- 用户指定了引擎（如「用 edge-tts」「离线转」）→ 按指定引擎走，跳过探测。
- 同一会话中用户选过音色 → 后续沿用，不重复弹窗，除非用户要求换。

### 第三步：合成（脚本一行出结果）

```bash
# 短文本
python3 <skill_dir>/scripts/tts.py --text "待转换文字" --voice <音色> --out /tmp/tts-out.mp3
# 长文本（从文件读，避免命令行转义问题）
python3 <skill_dir>/scripts/tts.py --file input.txt --voice <音色> --out /tmp/tts-out.mp3
```

- 脚本输出 JSON：`{"ok": true, "engine": ..., "voice": ..., "file": ..., "bytes": ...}`，`ok:false` 时按 `error` 处理（音色不存在 → 退出码 2 回到第二步弹窗；无引擎 → 退出码 3 走付费兜底）。
- edge-tts 未安装时，先征得同意再执行 `pip3 install edge-tts`（免费，约 10 秒），装好重试。
- 输出统一 mp3（无 ffmpeg 的 macOS 会产出 m4a，JSON 中有 `note` 说明，属正常）。

### 第四步：存储（资料库优先）

语音文件生成后按优先级落位：

1. **优先存资料库**：环境有「资料库」skill 或网盘（tdrive / netdrive）工具时，把生成的音频文件上传到资料库，向用户回报资料库中的文件位置。
2. **兜底一（无资料库能力）**：引导用户配置 IMA 知识库或文档提供方（腾讯文档等）：
   - 明确告知当前无法直接转存，需要用户选择并配置存储提供方
   - 配置完成后重新确定存储位置，再把文件转存过去
3. **兜底二（用户拒绝配置）**：保留本地文件路径，明确告知文件所在位置及格式。

**转存前必须先向用户确认目标位置**；用户明确拒绝转存时不得强行上传。

## 脚本速查（scripts/tts.py）

| 命令 | 作用 |
|------|------|
| `--list-voices` | 列出全部可用引擎与中文音色（JSON） |
| `--list-voices --engine say/edge` | 只列指定引擎音色 |
| `--text "..."` / `--file x.txt` | 待合成文本（长文本用文件） |
| `--engine auto/edge/say` | 引擎选择，auto=edge 优先、say 兜底 |
| `--voice <名称>` | 音色；缺省 say=Tingting、edge=zh-CN-XiaoxiaoNeural |
| `--out <路径>` | 输出路径，默认 `tts-<时间戳>.mp3` |

退出码：`0` 成功 ｜ `2` 音色不存在 ｜ `3` 无可用免费引擎（走付费兜底）。

## 输出规范

- 对用户的最终回复保持极简：**音频文件位置（资料库链接或本地路径）+ 音色/引擎一句说明**，不超过 3 行。
- 不复述合成文本内容，不解释 TTS 原理，不推荐无关工具。
- 失败时只说失败原因和下一步（换音色 / 装依赖 / 走付费配置），不输出长篇排错日志。

## 注意事项

- edge-tts 为网络引擎，合成失败多为网络问题：重试 1 次，仍失败降级到 say（macOS）。
- 文本超过 5000 字建议先写入临时文件再用 `--file` 传入。
- 付费方案的密钥安全红线见 `references/paid-tts-providers.md` 末节，必须遵守。
- 本技能不做语音克隆、不做声音复刻——那是另一个能力域，超出单一职责。

## 参考资料

- `scripts/tts.py` — 统一合成脚本（引擎探测、音色列举、mp3 输出）
- `references/paid-tts-providers.md` — 付费方案配置指南（腾讯云/讯飞/MiniMax/Azure）
