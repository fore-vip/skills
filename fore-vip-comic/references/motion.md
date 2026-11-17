# 动态化：从静态四格到动起来

## 两条路径

| 路径 | 产物 | 成本 | 运动质量 | 适用 |
|---|---|---|---|---|
| A · 镜头动效 | GIF | 0 credits | 平移+缩放+交叉淡化 | 信息流配图、社交平台、成本敏感 |
| B · 真动画 | MP4 | 50–100 credits/5 秒 | 角色动作、表情变化、运镜 | 品牌内容、需要"活起来"的场景 |

默认走 A。用户明确要"动画 / 动起来 / 视频"时才走 B，且必须先告知 credits 成本。

## 路径 A · 镜头动效（零成本）

成品 PNG 定稿后运行：

```bash
python scripts/make_motion.py <spec.json> <out.gif>
```

脚本按 spec 的网格几何裁出每一格，做：封面微推（0.8s）→ 逐格 Ken Burns 推近（1.3s/格）→ 格间交叉淡化（0.2s），循环播放。只依赖 Pillow，不调用任何生图/生视频模型。

- 传 spec.json：按 `margin/gap/title_h/cols` 精确裁格，推荐。
- 传成品 PNG：按 2×2 均分裁，仅适用于无标题区的图。
- GIF 是 256 色，输出后目视检查渐变是否断层；断层就减小画幅或降低 `MAX_W`。

## 路径 B · 真动画（VideoGen）

### 前置告知（不可省）

开跑前告诉用户：每段约 5 秒、消耗 50–100 credits，四格做几段就乘以几。用户确认后再调用。

### 三种玩法

| 玩法 | 输入 | 效果 | 段数 |
|---|---|---|---|
| 单格微动 | `image` = 某格 PNG | 该格人物眨眼、轻微动作 | 1/格 |
| 四格连播 | `image` = 第 1 格，`last_image` = 第 4 格，`reference_images` = [第 2, 3 格] | 一镜贯穿四格剧情 | 1 |
| 逐格转场 | 每格分别 `image` → 短视频 | 格与格硬切或淡入淡出 | 1/格，后拼接 |

四格连播最省成本、风格最连贯，优先选它。

### prompt 模板

```
Keep the exact hand-drawn style and character design from the reference images.
Camera slowly pushes in across four comic panels.
Panel 1: <第一格画面简述>. Panel 2: <第二格>. Panel 3: <第三格>. Panel 4: <第四格>.
Smooth cross-fade between panels. Subtle motion only: blinking, slight head turn, paper grain.
No new text, no captions, no watermark.
```

scene 用编译后的英文 scene 层，不要另写中文——模型对中文台词会画字。

### 参数纪律

| 参数 | 用法 |
|---|---|
| `image` | 首格绝对路径 |
| `last_image` | 尾格绝对路径；模型可能要求先有 `image`，按模型能力来 |
| `reference_images` | 中间格路径数组，用来锁角色与画风 |
| `seconds` | 用户没明确要求就省略，让模型决定 |
| `enable_audio` | 默认省略，不主动加音效 |
| `output_dir` | 每段指定独立目录，避免撞名覆盖 |

### 与合成器的顺序

**先合成静态 PNG，再动画化。** 合成器负责气泡、台词、版式，是信息主体；动画只做运动。不要在生图阶段试图让模型直接输出带对白的动画——中文必错字。

## 交付

- GIF/MP4 与静态 PNG 母版一起用 `present_files` 展示。
- 保留 spec.json 与 prompts.json：用户改台词时只需重跑合成 + 动效，不必重新生图或重新生成视频。
