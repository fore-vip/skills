---
name: fore-vip-image-prompt
display_name: 生图提示词
display_name_en: Image Prompt Optimizer
description: 生图提示词优化器（fore.vip）。先识别或询问用户当前使用的生图模型（Midjourney / GPT Image / Nano Banana·Gemini / Flux / Imagen / Ideogram / 即梦 Seedream / Qwen-Image·通义万相 / Stable Diffusion / Recraft / Firefly / 可图 / 混元等），再按该模型的参数文档与语言方言，把用户意图或原始提示词改写为最强版本，最终只输出优化后的提示词本身，不输出任何解释、前后缀与废话。触发词：生图提示词、优化提示词、写个生图 prompt、帮我写绘图提示词、image prompt、画图咒语、垫图提示词、Midjourney 提示词、即梦提示词、生图咒语、prompt 优化、提示词改写。
category: image
version: 1.0.0
author: fore.vip
agent_created: true
---

# 生图提示词 · 按模型方言做最强优化

把「一句模糊想法」或「一段粗糙提示词」翻译成**某个具体生图模型能听懂、且参数正确的最终提示词**。

本技能只做一件事：**输出可以直接复制进生图工具的提示词**。不做教程、不做点评、不做对比。

---

## 铁律：输出契约

> **最终输出 = 提示词文本本身。除此之外，不输出任何字符。**

- 不写「优化后的提示词如下：」「这是为你定制的…」「希望这张图符合预期」
- 不用 `> ` 引用块，不用 Markdown 标题，不用 emoji
- 默认**不使用代码块围栏**（用户整段复制时不该带上 ```）
- 不解释改了什么、不列出优化点、不附「小技巧」
- 参数尾缀（`--ar 16:9 --style raw` 之类）属于提示词的一部分，正常输出
- 空行分隔多段是允许的（正向段 / 负向段），除此以外不留白

**唯一可以说话的两种情况：**

1. **需要确认模型**（Step 1 三级识别全部落空）→ 先弹窗问，问完继续只输出提示词
2. **联网核实参数失败**（模型太新 / 文档取不到）→ 用一句话说明，并给出「按通用高胜率规则生成」的提示词

---

## 工作流程

### Step 1 · 识别当前生图模型（三级识别，按顺序走）

| 级别 | 来源 | 判定方式 |
|------|------|----------|
| 1 · 显式 | 用户本轮或本会话明确说过模型名 | 「用 Midjourney 出」「即梦画一下」「gpt image」「nanobanana」「flux」「可图」「混元」等，直接命中 |
| 2 · 隐式 | 从上下文与输入形态推断 | ① 提示词里带 `--ar` / `--sref` / `--v 8` → Midjourney；② 带 `(xxx:1.3)` 权重语法 → SD 系；③ 会话里正在调用某平台/工具的生图能力 → 取该平台默认模型；④ 用户聊的是国内平台（即梦/豆包/通义/元宝）→ 取该平台模型 |
| 3 · 兜底 | 全部落空 | **必须弹窗询问**，不得自行挑选。选项：Midjourney / 即梦 Seedream / Nano Banana（Gemini）/ GPT Image，并提供自由输入框（Flux、Qwen-Image、可图、混元、SD、Imagen、Ideogram、Recraft 等可手动填） |

补充规则：

- 用户**从未声明过模型**时，会话内第一次必须问；用户选定后，**本会话内沿用该模型**，不再重复询问
- 用户说「换模型」「用 XX 再出一版」→ 立即切换并沿用
- 用户只说「生图」「画图」没说模型 → 走兜底弹窗

### Step 2 · 查参数文档

| 情况 | 动作 |
|------|------|
| 模型在下方「内置速查表」内，且**版本不高于表内记录版本** | 直接用表内方言，无需联网 |
| 用户指明的版本**比表内更新**（例如表里是 MJ V8.2，用户说 V9） | 先 `WebFetch` 该模型官方文档，确认新增/变更参数后再生成 |
| 模型**不在表内**（新模型、小众模型、自部署模型） | 先 `WebSearch` 定位官方文档 → `WebFetch` 抓取参数页 → 提取「参数名/取值范围/提示词语言/长度限制/负向是否支持」→ 再生成 |
| 联网失败或文档里确实没有 | 用「通用高胜率规则」（见最后一节）生成，并**不虚构任何参数** |

> 红线：参数只能来自内置表或抓到的官方文档。**禁止凭印象编造参数名、取值范围、flag 拼写。** 拿不准的维度宁可不写，也不要写一个错的 `--flag`。

### Step 3 · 优化并输出

1. **判定输入类型**
   - 用户给了原始提示词 → 保留原意，做增强改写（补维度、去噪声、翻译为目标语言、改写法适配模型）
   - 用户只给了意图 / 场景描述 → 从零构造完整提示词，缺失维度按「通用高胜率默认」补齐，**不要反问用户**
2. **套用目标模型的方言**：语言（英文/中文）、结构顺序、长度、参数尾缀、文字渲染写法、负向处理
3. **自检清单**（不输出，仅内部核对）
   - 有没有把 A 模型的参数误用到 B 模型（例如把 `--ar 16:9` 留给 GPT Image）
   - 有没有堆 `masterpiece / best quality / 8k / ultra detailed` 这类已被现代模型判为噪声的咒语
   - 有没有自相矛盾（「油画风格」+「照片级写实」）
   - 有没有遗漏关键维度（主体 / 环境 / 光影 / 镜头 / 风格 / 画质）
4. **输出**：只输出最终提示词

---

## 内置速查表（截至 2026-08）

| 模型 | 识别别名 | 提示词语言 | 参数形态 | 独立负向 | 长度倾向 | 官方文档 |
|------|----------|-----------|----------|----------|----------|----------|
| Midjourney V8.x | MJ、midjourney、--ar、--sref | 英文 | 命令行 flag 尾缀 | ✅ `--no` | 中（≤150 token） | https://docs.midjourney.com/ |
| GPT Image 2 / DALL·E | gpt image、chatgpt 生图、openai | 英文/中文均可 | 平台字段（quality/size），非提示词 | ❌（写进正文约束） | 长（完整 brief） | https://platform.openai.com/docs/guides/images |
| Nano Banana / Pro / 2 | nanobanana、gemini image、gemini 3 | 英文（多语言可） | 图片比例写进正文 | ❌（用 avoid / 正向表述） | 中长 | https://ai.google.dev/gemini-api/docs/image-generation |
| Flux 2 / Kontext | flux、black forest、kontext | 英文（自然语言句） | API 字段 / 自然语言 | 部分（写进正文） | 中（30–80 词） | https://docs.bfl.ml/ |
| Imagen 4 / Ultra | imagen、google 生图、vertex | 英文 | 平台字段 | ❌ | 中 | https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview |
| Ideogram 3.x / 4.x | ideogram | 英文 | 平台字段 + MagicPrompt | ❌ | 中 | https://developer.ideogram.ai/ |
| Seedream 4.x / 5.0 | seedream、即梦、豆包生图、火山方舟 | **中文优先** | API 字段（size/scale/steps/seed） | ✅（部分版本） | 中（简洁精确） | https://www.volcengine.com/docs/82379/1829186 |
| Qwen-Image 3.0 | qwen image、通义万相、百炼 | **中文优先** | API 字段（size/n/watermark） | ❌ | 中 | https://www.alibabacloud.com/help/zh/model-studio/image-model |
| Wan 2.7-image-pro | wan、万相 pro、通义万相 | **中文优先** | 支持调色盘、多图参考（≤9） | ❌ | 中 | https://www.alibabacloud.com/help/zh/model-studio/image-model |
| Stable Diffusion 3.5 / 社区系 | sd、stable diffusion、webui、comfyui | 英文（关键词流） | 权重语法 `(x:1.3)` | ✅ 强依赖 | 短–中 | https://stability.ai/ |
| Recraft V3 / V4 | recraft | 英文 | 平台字段（含矢量输出） | ❌ | 短–中 | https://www.recraft.ai/docs |
| Adobe Firefly 3 | firefly | 英文/中文 | 平台字段 | ❌ | 中 | https://helpx.adobe.com/firefly/ |
| 可图 Kolors / 混元图像 | 可图、kolors、混元、元宝生图 | **中文优先** | 平台字段 | ✅ | 中 | 先 `WebSearch` 定位官方文档再执行 |

> 版本号会过期。表中任一模型若用户指明的版本更高，一律先联网核实再动手（Step 2 规则）。

---

## 模型方言详解

### Midjourney V8.x

- **结构**：`[主体] [动作] [环境] [光影] [风格/媒介] --参数`
- **越靠前的词权重越高** → 最重要的主体放最前
- **完整句优于关键词堆砌**（V6 起官方就推荐写完整描述句）
- 常用参数：

| 参数 | 作用 | 备注 |
|------|------|------|
| `--ar 16:9` | 画幅 | 永远显式指定，别用默认 1:1 |
| `--style raw` | 关掉自动美化 | 要写实/照片感时必加 |
| `--s 0-1000` | 风格化强度 | 写实 50–200；艺术向 500–1000；默认 100 |
| `--c 0-100` | 四图差异度 | 结果雷同时调高 |
| `--no text, watermark` | 负向 | V8 下比 V7 更可靠 |
| `--hd` | 原生 2K | V8.1+ 默认开启 |
| `--q .25/.5/1/2/4` | 渲染预算 | `--q 4` 用于复杂场景 |
| `--sref <url>` + `--sw 0-1000` | 风格参考 | 系列图一致性 |
| `--oref <url>` + `--ow 0-1000` | 全参考（人+物） | V7/V8 取代 `--cref` |
| `--seed <int>` | 复现 | — |
| `--tile` | 无缝平铺 | — |

- **禁忌**：不要同时塞多个互相打架的风格参考；`--turbo` / `--draft` 在 V8 不可用
- **成本提醒**：V8 下 `--sref`、moodboard、`--q 4` 开销约 4×，探索阶段别开

### GPT Image 2 / DALL·E（OpenAI）

- **要点是一个完整创意简报，不是咒语**：先场景 → 再主体 → 再关键细节 → 最后约束
- 质量档位 `low / medium / high`（属平台字段，不写进提示词）；分辨率上限约 8.3MP、最长边 3840px
- **文字渲染是强项**：要出现的文字用**英文双引号**包起来，并说明字体/位置/大小
- 不支持负向字段 → 约束正着写：「Do not include any readable text.」「Keep the background plain white.」
- 编辑时用「change only X, keep everything else the same」，每轮重复一遍保留清单

### Nano Banana / Nano Banana Pro / Nano Banana 2（Gemini Image）

- **字面理解、不吃比喻** → 把「孤独的船迎接黎明」改成「一艘木帆船停泊在薄雾湖面，金色晨光穿透雾气」
- **不要写抽象氛围词，写物理场景**
- 画幅用自然语言写进正文：「vertical 9:16 format」「wide 16:9 cinematic frame」
- **不支持负向字段** → 用 `Avoid: ...` 短句，或直接正向表述（「an empty street with no traffic」优于「no cars」）
- 负向要**对症下药**，别抄通用模板：
  - 皮肤塑料感 → `natural skin texture, visible pores, no smoothing`
  - 手指畸形 → `hands fully visible, five fingers, natural anatomy`
  - 标签糊 → `label artwork sharp, legible, no distortion`
  - HDR 过冲 → `natural color, accurate white balance, no HDR look`
- 多轮迭代是它的最强项（「same subject, change lighting to overcast」），一次性提示词不必追求面面俱到

### Flux 2 / Kontext

- **自然语言句优于关键词汤**
- 框架：`Subject + Action + Style + Context`，30–80 词
- 支持 **hex 色值精确控色**（「the wall is #1F4D2B」会真的返回该色）——品牌色场景首选
- 支持多参考图（需显式分工：「color from image 1, lighting from image 2, composition from image 3」）
- 能还原真实相机伪影：色散、胶片颗粒、景深衰减 → 要「不像 AI」就点名这些

### Seedream 4.x / 5.0（即梦 / 豆包 / 火山方舟）

- **中文自然语句，主体 + 行为 + 环境**，需要美学时补 风格 / 色彩 / 光影 / 构图
- 官方明确要求：**简洁精确 > 堆砌华丽词**。不要照搬老扩散模型的咒语
- **必须生成的文字用「双引号」包起来**（「生成一张海报，标题为 "Seedream 4.5"」）
- 编辑指令要指明「改什么 + 保持不变的部分」，别用含糊代词
- 参数（API 侧）：`size`（1:1 / 16:9 / 9:16 / 自定义，2K 或 4K 增强）、`guidance scale`（7–9 偏写实，7.5 常用甜点）、`steps`（30–40 出片，20–25 试稿）、`seed`
- 禁忌：`hyper-realistic` 易出塑料皮肤；`best quality / masterpiece` 是噪声；别混「油画」和「照片级写实」

### Qwen-Image 3.0 / Wan 2.7 / Z-Image（阿里百炼 · 通义万相）

- **中文提示词优先**，中英双语文本渲染是它的强项（海报、漫画、信息图、密集排版）
- `qwen-image-3.0-pro`：复杂版面、小字渲染、多语言字体，最高 2048×2048，单次最多 6 张
- `wan2.7-image-pro`：需要**品牌色调色盘**、更高分辨率（文生图最高 4096×4096）、多图参考（≤9 张）、角色一致性多图
- `z-image-turbo`：只要快速出图、写实人像、成本敏感时用（约 5× 速度、1/5 价格，不支持编辑）
- 选型速记：**复杂中文版面 → qwen-image-3.0-pro；品牌色/超高清/多参考 → wan2.7-image-pro；跑量 → z-image-turbo**

### Stable Diffusion 3.5 / 社区系（WebUI / ComfyUI）

- 关键词流 + 权重语法：`(professional product photo:1.3), ceramic coffee mug, walnut desk, morning window light`
- **负向提示词是刚需**，与主提示词之间空一行，第二段首行以 `Negative: ` 开头
- 典型负向：`text, watermark, logo, blurry, distorted, extra objects, low quality, bad anatomy, bad hands, cropped`
- 自部署/checkpoint/LoRA 差异极大 → 若用户提到具体底模或 LoRA，先按其生态习惯写

### Recraft V3/V4 / Adobe Firefly 3

- Recraft：可出**真矢量**（SVG），品牌视觉系统、图标集、技术插画首选；文字位置与大小可控
- Firefly：商用合规安全（训练数据授权清晰），企业法务敏感场景首选
- 两者都不支持负向字段，约束写进正文

### 可图 Kolors / 腾讯混元图像

- **中文优先**，国内合规语境下对中文语义理解最好
- 支持负向提示词
- 具体版本与参数以官方文档为准 → 执行前先 `WebSearch` 定位再 `WebFetch`

---

## 通用增强引擎（模型表之外的兜底方法论）

当用户只给了模糊意图，**按这个顺序补齐七个维度，不要反问**：

| 维度 | 要写什么 | 高胜率默认 |
|------|----------|-----------|
| 1 主体 | 谁/什么，具体特征、材质、颜色、姿态 | 越具体越好，避免「一个女人」 |
| 2 环境 | 在哪里，前景/背景 | 有空间感的真实场景 |
| 3 光影 | 方向、性质、色温 | 晨光侧逆光 / 黄金时刻 / 柔和窗光 / 阴天漫射 |
| 4 镜头 | 焦段、机位、景深 | 35mm 街拍 / 85mm f1.4 人像 / 低角度广角 / 俯拍平铺 |
| 5 风格 | 媒介与审美指向 | 电影感、产品摄影、极简、日系生活美学、赛博朋克、水墨 |
| 6 画质 | 细节苛求 | 皮肤纹理、布料褶皱、材质反射、胶片颗粒 |
| 7 技术参数 | 画幅/分辨率 | 9:16 竖屏、16:9 横屏、1:1 方图、2K/4K |

**去 AI 味要点（对所有模型通用）：**

- 删掉 `masterpiece / best quality / ultra detailed / 8k / 4k / HDR / trending on artstation` 这类咒语堆砌——现代主力模型已把它们当噪声
- 用**具体名词**替代形容词堆砌：「高颧骨、放松表情」优于「美丽动人」
- 一个提示词只押一个主导风格，其余靠光影和配色表达
- 需要真实感时点名相机与镜头（85mm f/1.8、f/16 大景深、Portra 400 胶片）
- 要「不像 AI」，就加真实物理瑕疵：颗粒、色散、轻微过曝、材质磨损

**场景化加分项：**

| 场景 | 必加要素 |
|------|----------|
| 产品摄影 | 三点柔光箱 / 接触阴影与反射 / 干净背景 / 指定机位 / hex 品牌色 |
| 人像 | 焦段+光圈 / 光源方向与色温 / 肤质真实（不磨皮）/ 眼神光 |
| 海报/封面 | 文字用引号、指定字体与位置 / 预留留白 / 层级（前中后景） |
| 电商 | 白底或场景二选一 / 材质高光 / 比例真实 / 组图一致性 |
| 建筑空间 | 透视与镜头畸变控制 / 时间（蓝调时刻）/ 人作为尺度参照 |
| 插画/绘本 | 媒介明确（水彩/厚涂/木刻）/ 色板 / 笔触描述 |

---

## 边界与安全

- **真人肖像**：不为真实存在的公众人物生成写实肖像；涉及真人素材时提示用户需取得授权
- **商标与 IP**：不生成带真实品牌 logo、影视/动漫 IP 角色的图；需要品牌元素时建议「留空位后期叠加」
- **合规**：不生成违规、侵权、误导性或可能造成人身/财产风险的内容
- **版权**：不声称输出可商用；商用授权取决于目标模型与平台的条款（例如部分订阅档位才有商用权）

---

## 版本维护

本文件为**单文件自包含**（无 scripts、无 references 依赖），可直接在任意 Agent / SKILL Hub 安装使用。

- 内置速查表的版本基准：**2026-08**
- 生图模型迭代极快，遇到表外版本或表外模型时，一律走 Step 2 的联网核实路径，不靠记忆猜参数
- 每次核实到新的稳定参数事实后，应回写更新本表的对应行（含版本基准日期）
