---
name: fore-vip-comic
slug: comic
displayName: 手绘漫画
display_name: 手绘漫画
display_name_en: Handdrawn Comic
description: "手绘漫画与动画成图助手（fore.vip）。把主题、梗或知识画成手绘质感的多格漫画——提示词由六层编译器生成、角色风格用参考图跨格锁定、成品可一键转镜头动效或真动画，产出可直接发布的 PNG/GIF/MP4。开场先以选项形式收集主题、画风、版式与文案调性，再编译分镜为逐格 prompt、带锚点串行生图、脚本合成中文对白与版式；合成器内置文字溢出与气泡尾巴越界两道硬校验，不通过直接报错。当用户说「画漫画 / 四格漫画 / 六格漫画 / 手绘漫画 / 四格动画 / 让漫画动起来 / 漫画版 XX / 把某个梗画成漫画 / 用漫画讲清楚 XX / 漫画配图」时启用。不产出单张海报或封面（走 poster-studio）、不改写生图提示词（走 fore-vip-image-prompt）、不做纯图片拼接（走 fore-vip-image-stitch）、不做儿童科普图文排版（走 fore-vip-kids-science）。"
description_zh: "把主题、梗或知识画成手绘质感的多格漫画并可动化。六层提示词编译 + 参考图锁定角色风格 + 合成器硬校验，开场选项收集参数，输出 PNG/GIF/MP4。不产出海报封面、不改写生图提示词、不做纯图片拼接。"
description_en: "Hand-drawn comic and animation generator. Turns a theme, joke, or knowledge into a multi-panel comic with a hand-drawn feel: a six-layer prompt compiler, reference-image style locking across panels, and a compositor that renders Chinese dialogue and layout with built-in overflow and bubble-tail checks, outputting publish-ready PNG/GIF/MP4. It collects parameters as options, compiles the storyboard into per-panel prompts, generates serially with an anchor image, then offers zero-cost motion or AI animation. It does not produce posters, rewrite image prompts, or stitch plain images."
category: image
version: 1.1.1
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
  - "四格动画"
  - "让漫画动起来"
negative_triggers:
  - "单张海报 / 封面 / 服务图（走 poster-studio）"
  - "只要生图提示词、不要成图（走 fore-vip-image-prompt）"
  - "纯图片拼接 / 宫格拼图（走 fore-vip-image-stitch）"
  - "儿童科普问答的图文排版（走 fore-vip-kids-science）"
  - "可打印拼图（走 fore-vip-jigsaw）"
---

# 手绘漫画与动画成图

把主题、梗或知识变成**可直接发布的多格漫画，并可让它动起来**。三处能力是本 SKILL 的核心，不可降级为手写：

| 能力 | 做法 | 不可动摇的规则 |
|---|---|---|
| **提示词生成** | 六层编译器 `scripts/build_prompts.py` | 固定层（风格/角色/构图/负面）四格逐字相同，脚本强制断言；手写层只有 scene 与 emotion |
| **风格一致性** | 参考图锚定 `references/consistency.md` | 第一格确认后作锚点，第 2–4 格图生图带 `image1` + `input_fidelity`，一组只用一个锚点 |
| **动态生成** | 零成本 GIF / 真动画 MP4 `references/motion.md` | 先合成静态 PNG 再动画化；真动画必须先告知 credits 成本 |

## 核心分工（不可动摇）

**AI 生图负责画面质感，程序负责文字与版式。**

AI 生图对中文几乎必然写错字，气泡位置也不可控；而漫画的对白是信息主体，必须零错字、位置精确。分工后两边都取最优：笔触由模型给，台词由字体给。

不要试图让 AI 一次画出带中文的完整四格——那是最容易翻车的路径。
动画化同理：运动由动态模块给，不要让模型直接生成带对白的动画。

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
        {"label": "彩铅手作", "description": "颗粒感强，温暖生活流"},
        {"label": "国风水墨", "description": "写意留白，适合文化、节气、哲思题材"}
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

## 第二步：写分镜 + 编译提示词

选定题材后，**先定主题路线，再落分镜**，最后编译提示词。

- **主题路线（强制）**：一句话写清"起点 → 转折 → 终点"，四格沿这条线推进。只定四幕职责、不定路线，必然产出四格同构图的失败品。五类题材的路线模板见 `references/narrative-patterns.md`。
- **画面演进（强制）**：四格在景别 `shot`、场景状态 `state`、光线 `light`、情绪 `emotion` 四维上各需 ≥3 种取值；`scene` 里显式写 `_shot_`（`overhead` / `extreme close-up` / `wide pull-back`）。编译器会拦截雷同分镜。
- 四幕节奏、各题材的叙事模板、文案字数预算见 `references/narrative-patterns.md`。
- 第 3 格安排视觉峰值，第 4 格放最妙的一句。
- 台词字数必须控制在预算内（答案 ≤16 字、问题 ≤13 字），超了就改文案，不要缩字号硬塞。

把分镜写成 `storyboard.json`（格式、route 与演进字段见 `references/prompt-compiler.md`），然后编译：

```bash
python scripts/build_prompts.py storyboard.json prompts.json
```

编译器做三件事：把 **6 层**（风格/角色/构图/场景/情绪/负面）拼成逐格 prompt；拒绝含中文的 prompt；断言四格的固定层逐字相同。**不要手写 prompt 绕过编译器**——那是风格漂移的头号来源。台词与说话人另存，供第四步合成使用，不进 prompt。

## 第三步：带锚点逐格生图

取 `prompts.json` 里每格的 `prompt` 与 `model_params`（`revise=false`、`background=opaque` 不要改）。

**图像锁（风格一致性的关键，按顺序执行）**：

1. 先用第 1 格 prompt 生图，用户确认可用后**存为锚点**（固定路径，如 `anchor.png`）。
2. 第 2–4 格用图生图：传 `image1=<锚点>`、`input_fidelity` 按画风取值（详见 `references/consistency.md`），prompt 用各自编译结果。参考图只锁角色与笔触，scene 由 prompt 主导。
3. 一组四格自始至终用同一锚点；锚点崩了整组重做，不中途换图。

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

## 第五步（可选）：动态化

静态 PNG 定稿后，按用户需求决定动不动、怎么动，细则见 `references/motion.md`。

- **默认给零成本镜头动效**：`python scripts/make_motion.py <spec.json> <out.gif>`，Pillow 实现平移/缩放/淡化，不消耗 credits。
- **用户明确要"动画 / 视频 / 让角色动起来"才走真动画**：先告知每段 5 秒约 50–100 credits，确认后用 VideoGen；优先"首格 + 尾格 + 中间格参考图"一镜贯穿，最省成本也最连贯。
- 无论如何都**先合成静态 PNG 再动画化**，不让模型直接生成带对白的动画。

## 交付与迭代

成品 PNG（及 GIF/MP4）用 `present_files` 展示，并保留 spec JSON、prompts.json 与合成脚本，便于用户改文案、换字体或换动效后重跑，不必重新生图。

若某格画面不达标：**两次不达标就换主体或换表达角度**，不要第三次硬拗（见 `references/pitfalls.md` 的能力边界表）。

## 资源索引

| 文件 | 何时读 | 内容 |
|---|---|---|
| `scripts/build_prompts.py` | 第 2 步编译 prompt 时调用 | 六层提示词编译器，含固定层逐字一致断言 |
| `scripts/compose_comic.py` | 第 4 步合成时调用 | 通用合成器，JSON 驱动，自带两道校验 |
| `scripts/make_motion.py` | 第 5 步零成本动效时调用 | 按 spec 网格裁格，Ken Burns + 淡化输出 GIF |
| `references/prompt-compiler.md` | 第 2 步写 storyboard.json 时读 | 六层结构、角色定妆块、scene 铁律 |
| `references/consistency.md` | 第 3 步生图时读 | 文字锁 + 图像锁、锚点策略、fidelity 取值、验收清单 |
| `references/motion.md` | 第 5 步动态化时读 | GIF / MP4 两条路径、成本告知、VideoGen 玩法与参数 |
| `references/spec-format.md` | 写 spec JSON 时读 | 字段说明、坐标定法、完整示例 |
| `references/styles.md` | 第 2 步写 storyboard 时读 | 5 种画风的 prompt 前缀与适用场景（即画风选项的来源） |
| `references/narrative-patterns.md` | 第 2 步写分镜时读 | 5 种四幕节奏模板、文案字数预算、气泡形状语用表 |
| `references/pitfalls.md` | 生图与修补时读 | 生图纪律、能力边界、瑕疵修补、环境事实 |

## 环境依赖

- Python 3 + `Pillow`（三个脚本仅依赖这两项），无需其他第三方库。
- 中文字体：macOS 走 `Hiragino Sans GB.ttc`；其他系统需在 spec 的 `font` 字段指定本机可用中文字体。
- 生图依赖环境可用的生图工具（优先 `ImageGen`，图生图走 `image1`/`input_fidelity`），不可用时如实告知，不静默降级。
- 真动画依赖 `VideoGen`，按 credits 计费，用前必须告知用户成本。

## 服务

- 服务由前凌智选提供 https://fore.vip

## 反馈
- SKILL 由 [前凌智选](https://fore.vip) 创建, 并发布于 SKILLHUB.cn
- 可于SKILLHUB反馈使用问题、优化意见
