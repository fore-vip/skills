# 提示词编译：六层结构与故事板

## 为什么不再"逐字复制前缀"

旧做法把一整段前缀粘到每格 prompt 开头，靠人肉保证四格一致。问题：前缀藏在自然语言的 `# 第三步` 里，改一次画风要改四处；角色描述每格手写一遍，措辞迟早漂移；中文台词混进 prompt 时模型会照着画字。

新做法：**把 prompt 拆成六层，固定层由脚本注入，手写层只有 scene 和 emotion**。`scripts/build_prompts.py` 编译后强制校验——除 scene/emotion 外，任意两格必须逐字相同，不一致直接报错。

## 六层结构

| 层 | 字段 | 固定/可变 | 来源 | 作用 |
|---|---|---|---|---|
| 1 风格层 | `style` | 固定 | `styles.md` 逐字复制 | 画风、笔触、纸感、负面约束 |
| 2 角色层 | `character` | 固定 | 定妆块（见下） | 锁人物长相与穿着 |
| 3 构图层 | `composition` | 固定 | 通常 `upper third empty` | 给气泡留位 |
| 4 场景层 | `scene` | **可变** | 分镜脚本 | 本格画面，纯物理描述 |
| 5 情绪层 | `emotion` | **可变** | 分镜脚本 | 表情与肢体，弱于场景 |
| 6 负面层 | `negative` | 固定 | 默认或覆盖 | 禁文字、禁气泡、禁水印 |

编译结果 = `1 + 2 + 3 + 4 + 5 + 6`，四格之间只有第 4、5 层不同。

## 角色定妆块（第二次起复用）

`character` 用对象写，字段固定顺序，脚本拼成一句英文。四格必须传同一个对象。

| 字段 | 含义 | 示例 |
|---|---|---|
| `role` | 身份 | `a junior designer` |
| `build` | 体型 | `slim, slightly hunched` |
| `hair` | 发型发色 | `short messy black hair` |
| `eyes` | 眼部特征 | `round glasses` |
| `outfit` | 穿着 | `oversized hoodie, rolled-up sleeves` |
| `colors` | 主色 | `beige and muted blue palette` |
| `signature` | 记忆点道具 | `a red mug in hand` |

写够 5–7 个字段，模型才能锁住；少于 3 个字段时四格飘的概率显著上升。字段值一律英文短句，不写中文。

## storyboard.json 格式

```json
{
  "style": "<从 styles.md 复制的整段风格前缀>",
  "route": "正常需求 → 层层加码 → 当场爆发 → 一问打回",
  "composition": "Composition leaves the upper third of the panel almost completely empty for a speech bubble.",
  "character": {
    "role": "a junior designer", "build": "slim, slightly hunched",
    "hair": "short messy black hair", "eyes": "round glasses",
    "outfit": "oversized hoodie", "colors": "beige and muted blue",
    "signature": "a red mug in hand"
  },
  "panels": [
    {"scene": "A wide shot of a designer at a tidy desk facing a single email, morning light.", "emotion": "calm, expectant", "shot": "wide", "state": "tidy", "light": "soft"},
    {"scene": "A closer view as seven chat pop-ups stack up across the screen, the desk now crowded with printouts.", "emotion": "increasingly tense", "shot": "close", "state": "crowded", "light": "warm"},
    {"scene": "An extreme close-up of the designer throwing both hands up, the red mug tilted, sharp shadows.", "emotion": "bursting, eyes wide", "shot": "extreme_close", "state": "chaotic", "light": "highlight"},
    {"scene": "A wide shot pull-back: one calm question bubble on the screen, the designer frozen, still air.", "emotion": "deadpan silence", "shot": "wide", "state": "settled", "light": "clear"}
  ]
}
```

### 顶层 `route`（必填）

主题路线，一句话写清"起点 → 转折 → 终点"，中文即可。四格必须沿这条线推进。**缺失时编译器直接拒绝**——不允许没有路线就分镜。路线模板见 `narrative-patterns.md`「主题路线」节。

### 每格演进标注（必填，不进 prompt）

| 字段 | 含义 | 取值示例 |
|---|---|---|
| `shot` | 景别 | `wide` / `mid` / `close` / `extreme_close` / `overhead` |
| `state` | 场景状态 | `tidy` / `crowded` / `chaotic` / `focused` / `settled` |
| `light` | 光线色调 | `soft` / `warm` / `dark` / `highlight` / `clear` |
| `emotion` | 人物情绪（同时进 prompt） | 英文短句，四格各异 |

四格在 `shot / state / light / emotion` 四个维度上**每个都至少需要 3 种不同取值**，且相邻格的 scene 描述雷同度不得 > 0.55。这些标注只用于闸门校验，不拼进 prompt（避免中文或标签词进入生图）。

**来自剧情提案时**：确认过的路线直接填 `route`，四维标注与英文 `scene` / `emotion` 直接取自提案，台词草案另存供合成器使用；提案里的假设清单不必写进 storyboard（已确认即事实），如需追溯可放可选的 `assumptions` 字段，编译器会忽略它。

## scene 写法铁律

1. **只写可拍摄的物理事实**：谁、在哪、做什么、手里拿什么、光线如何。
2. **不写台词、不写文字内容**——对白留给合成器，写进去模型会画错字。
3. **不写抽象概念**（"压力""崩溃"），改写成可见动作（"双手举起""杯子倾斜"）。情绪交给 `emotion` 层。
4. 英文，单句 15–30 词。中文会被编译器拒绝。

## 编译与校验

```bash
python scripts/build_prompts.py storyboard.json prompts.json
```

脚本做五件事：拼六层、拒绝含中文的 prompt、断言固定层四格逐字相同、断言主题路线 `route` 已填、**拦截同构图四连**（演进维度取值不足或 scene 两两雷同度 >0.55 时报错，并提示改写景别/场景状态）。输出 `prompts.json` 含每格最终 prompt、`route`、`model_params` 与每格 `evolution` 标注。

`model_params` 里两个关键值不要改：

| 参数 | 值 | 原因 |
|---|---|---|
| `revise` | `false` | 关闭模型自动改写 prompt，否则会偷偷改掉固定层 |
| `background` | `opaque` | 手绘纸感需要实底，透明底会让纸纹丢失 |

生图时逐格取 `panels[i].prompt`，参数用 `1536x1024` + `quality=high`。
