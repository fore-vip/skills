---
name: fore-vip-comic
slug: comic
displayName: 手绘漫画
display_name: 手绘漫画
display_name_en: Handdrawn Comic
description: "手绘漫画成图助手（fore.vip）。把主题、梗或知识画成手绘质感的多格漫画——AI 负责画面笔触、程序负责中文对白与版式，产出可直接发布的 PNG。开场先以选项形式收集主题、画风、版式与文案调性，再逐格生图并用脚本合成；合成器内置文字溢出与气泡尾巴越界两道硬校验，不通过直接报错。当用户说「画漫画 / 四格漫画 / 六格漫画 / 手绘漫画 / 漫画版 XX / 把某个梗画成漫画 / 用漫画讲清楚 XX / 漫画配图」时启用。不产出单张海报或封面（走 poster-studio）、不改写生图提示词（走 fore-vip-image-prompt）、不做纯图片拼接（走 fore-vip-image-stitch）、不做儿童科普图文排版（走 fore-vip-kids-science）。"
description_zh: "把主题、梗或知识画成手绘质感的多格漫画。开场以选项收集主题、画风、版式与文案调性，再逐格 AI 生图、由脚本叠加中文对白气泡与版式，输出可直接发布的 PNG。内置文字溢出与气泡尾巴越界校验。不产出海报封面、不改写生图提示词、不做纯图片拼接。"
description_en: "Hand-drawn comic generator. Turns a theme, joke, or piece of knowledge into a multi-panel comic with a hand-drawn feel: AI supplies the artwork and brushwork, while a script handles the Chinese dialogue bubbles and layout, producing a publish-ready PNG. It first collects the theme, art style, panel count, and copy tone as interactive options, then generates and composites each panel, with built-in checks for text overflow and speech-bubble tail bounds so failures surface as errors rather than broken images. It does not produce posters or covers, rewrite image prompts, or stitch plain images."
category: image
version: 1.0.0
author: fore.vip
owner: team
agent_created: true
triggers:
  - "画漫画"
  - "四格漫画"
  - "六格漫画"
  - "手绘漫画"
  - "漫画版 XX"
  - "把某个梗画成漫画"
  - "用漫画讲清楚 XX"
  - "漫画配图"
  - "四格漫画生成"
negative_triggers:
  - "单张海报 / 封面 / 服务图（走 poster-studio）"
  - "只要生图提示词、不要成图（走 fore-vip-image-prompt）"
  - "纯图片拼接 / 宫格拼图（走 fore-vip-image-stitch）"
  - "儿童科普问答的图文排版（走 fore-vip-kids-science）"
  - "可打印拼图（走 fore-vip-jigsaw）"
---

# 手绘漫画成图

把主题、梗或知识变成**可直接发布的多格漫画**：AI 生图给出手绘质感，脚本负责中文对白、气泡与版式。

## 核心分工（不可动摇）

**AI 生图负责画面质感，程序负责文字与版式。**

AI 生图对中文几乎必然写错字，气泡位置也不可控；而漫画的对白是信息主体，必须零错字、位置精确。分工后两边都取最优：笔触由模型给，台词由字体给。

不要试图让 AI 一次画出带中文的完整四格——那是最容易翻车的路径。

## 第一步（强制）：以选项形式收集主题与风格

**在写分镜脚本之前，必须先调用 `AskUserQuestion` 收集四项参数。** 除非用户已在本轮对话中明确给出该项，此时跳过对应问题。

调用模板（照抄，按需删减已明确的项）：

```json
{
  "questions": [
    {
      "question": "这组漫画讲什么主题？",
      "header": "主题",
      "options": [
        {"label": "工作日常吐槽", "description": "办公协作、甲方需求、工具踩坑这类共鸣题材"},
        {"label": "生活观察", "description": "家庭、通勤、消费、社交中的小荒诞"},
        {"label": "知识科普", "description": "自然、健康、科技冷知识，一问一答式"},
        {"label": "品牌或产品说明", "description": "把卖点或使用场景画成小故事（文案需过合规审查）"}
      ]
    },
    {
      "question": "用哪种画风？",
      "header": "画风",
      "options": [
        {"label": "钢笔淡彩（推荐）", "description": "墨线加淡水彩，明快通用，四格风格最容易统一"},
        {"label": "日式黑白线稿", "description": "网点质感，情绪冲击强，适合吐槽与反差"},
        {"label": "水彩童书", "description": "柔和圆润，适合儿童与科普内容"},
        {"label": "彩铅手作", "description": "颗粒感强，温暖生活流"}
      ]
    },
    {
      "question": "版式要几格？",
      "header": "版式",
      "options": [
        {"label": "四格 2×2（推荐）", "description": "最通用的漫画版式，手机与信息流都合适"},
        {"label": "六格 2×3", "description": "信息量更大，适合完整叙事或产品说明"},
        {"label": "三格横排", "description": "轻量，适合单一梗或短对比"},
        {"label": "单格大图", "description": "只画一个场景，适合做封面或配图"}
      ]
    },
    {
      "question": "文案用什么调性？",
      "header": "文案调性",
      "options": [
        {"label": "口语吐槽", "description": "网感、短句、有情绪起伏"},
        {"label": "严谨科普", "description": "事实准确、不加戏，问题与答案分层"},
        {"label": "童书语气", "description": "温和、拟人、句子短，适合儿童"},
        {"label": "正式克制", "description": "品牌与官方场景，不加网络用语"}
      ]
    }
  ]
}
```

**跳过规则**：用户已给出该项时不要重复问——已经说了主题就跳过主题题，说了"你定"就全部使用默认值（钢笔淡彩 + 四格 2×2 + 口语吐槽）。
**用户若只给了方向、没给具体主题**（例如选了"知识科普"或答"你定"）：先产出 **3 个具体主题候选**，每个用一句话讲清四格分别画什么，让用户挑选后再进入分镜。不要在主题模糊时直接开画。

## 第二步：写分镜脚本

选定题材后，先落定每格的**画面内容 + 台词 + 说话人**，再动手生图。

- 四幕节奏、各题材的叙事模板、文案字数预算见 `references/narrative-patterns.md`。
- 第 3 格安排视觉峰值，第 4 格放最妙的一句。
- 台词字数必须控制在预算内（答案 ≤16 字、问题 ≤13 字），超了就改文案，不要缩字号硬塞。

## 第三步：逐格生图

从 `references/styles.md` 取所选画风的**风格前缀**，逐字粘贴到每格 prompt 开头，只替换 `Scene:` 段。四格之间除 Scene 外必须完全一致，否则风格会飘。

```
<画风前缀，逐字复用>
Semi-realistic casual character design: <角色描述，四格逐字相同>.
Composition leaves the upper third of the panel almost completely empty for a speech bubble.
Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO captions, NO watermark
anywhere in the image. Scene: <本格画面>
```

参数：`size=1536x1024`、`quality=high`。

**硬性纪律**：逐张**串行**调用，且**每张指定互不相同的 `output_dir`**；开跑前告知用户成本（每张约 5-10 credits）。原因与实测损耗见 `references/pitfalls.md`。

## 第四步：合成

把每格的 `image`、气泡坐标、台词写进一个 JSON，交给脚本：

```bash
python scripts/compose_comic.py <spec.json>
```

字段含义与完整示例见 `references/spec-format.md`。脚本完成裁底去水印、网格拼版、手绘外框、气泡与尾巴、中文字排版、缩放输出，并内置两道硬校验：

1. 文字块装不装得进气泡（按形状算可用高度）
2. 尾巴基点是否落在气泡主体内部

校验不通过会直接报错并给出修正建议，不会产出废图。坐标微调后重跑即可——**改台词只需重跑合成，不需要重新生图**，这是本方案相对"让 AI 再画一次"的最大优势。

## 交付与迭代

成品 PNG 用 `present_files` 展示，并保留 spec JSON 与合成脚本，便于用户改文案或换字体后重跑。

若某格画面不达标：**两次不达标就换主体或换表达角度**，不要第三次硬拗（见 `references/pitfalls.md` 的能力边界表）。

## 资源索引

| 文件 | 何时读 | 内容 |
|---|---|---|
| `scripts/compose_comic.py` | 第 4 步合成时调用 | 通用合成器，JSON 驱动，自带两道校验 |
| `references/spec-format.md` | 写 spec JSON 时读 | 字段说明、坐标定法、完整示例 |
| `references/styles.md` | 第 3 步生图前读 | 5 种画风的 prompt 前缀与适用场景（即画风选项的来源） |
| `references/narrative-patterns.md` | 第 2 步写分镜时读 | 5 种四幕节奏模板、文案字数预算、气泡形状语用表 |
| `references/pitfalls.md` | 生图与修补时读 | 生图纪律、能力边界、瑕疵修补、环境事实 |

## 环境依赖

- Python 3 + `Pillow`（脚本仅依赖这两项），无需其他第三方库。
- 中文字体：macOS 走 `Hiragino Sans GB.ttc`；其他系统需在 spec 的 `font` 字段指定本机可用中文字体。
- 生图依赖环境可用的生图工具（优先 `ImageGen`），不可用时如实告知，不静默降级。

## 服务

- 服务由前凌智选提供 https://fore.vip

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
