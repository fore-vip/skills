# 画风字典

每种画风给一段**风格前缀**（英文），逐字粘贴到每格的 prompt 开头，只替换 `Scene:` 段。
四格之间除 Scene 外必须逐字相同，否则风格会飘。

所有画风都遵守两条铁律：**留白给气泡**（`upper third empty`）、**禁止任何文字**。

---

## 1. 钢笔淡彩（默认推荐，已实测）

适用：绝大多数题材。明快、有手作感，颜色不刺眼，社交平台友好。

```
Hand-drawn pen-and-ink comic panel with light watercolor wash. Loose expressive black ink
linework with varied line weight, subtle paper grain texture, warm off-white paper background.
Muted watercolor palette with one single vivid red accent.
Composition leaves the upper third of the panel almost completely empty for a speech bubble.
Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO captions, NO watermark
anywhere in the image. Scene: <本格画面>
```

红色点缀换成小而具体的物件（红杯子、红瓢虫、红胸羽、红蝴蝶），并在 Scene 里点名。

---

## 2. 日式黑白线稿

适用：情绪冲击强的吐槽、喜剧、反差梗。黑白本身就有"漫画"的正式感。

```
Hand-drawn black-and-white manga panel, crisp pen linework with varied line weight,
screentone dot shading for shadows, clean white background, high contrast ink drawing.
Composition leaves the upper third of the panel completely empty for a speech bubble.
Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO captions, NO watermark
anywhere in the image. Scene: <本格画面>
```

黑白稿里唯一的彩色元素留给情绪高潮格（如红色怒符），其余保持纯黑白。

---

## 3. 彩铅手作

适用：生活流、亲子、温暖日常。颗粒感最强，最"手工"。

```
Hand-drawn colored pencil illustration, visible pencil grain and paper tooth texture,
soft layered strokes, warm cream paper background, gentle muted palette with one vivid red accent.
Composition leaves the upper third of the panel empty for a speech bubble.
Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO captions, NO watermark
anywhere in the image. Scene: <本格画面>
```

铅笔颗粒在缩图后会变糊，单格尺寸不要小于 1024 宽。

---

## 4. 水彩童书

适用：儿童科普、绘本、教育内容。与"十万个为什么"这类题材天然契合。

```
Hand-drawn storybook watercolor illustration for children, soft rounded shapes, gentle linework,
light pastel watercolor washes, textured paper background, friendly and warm mood.
Composition leaves the upper third of the panel empty for a speech bubble.
Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO captions, NO watermark
anywhere in the image. Scene: <本格画面>
```

主体轮廓要简单圆润，避免细节堆叠；拟人化角色此处最自然。

---

## 5. 国风水墨

适用：文化、节气、传统、哲思类题材。写意留白，气质文气。

```
Traditional Chinese ink wash painting, xuan paper texture, expressive brush strokes,
ink density variation from deep black to pale grey, generous negative space,
one small vermilion red seal-like accent.
Composition leaves the upper third of the panel empty for a speech bubble.
Absolutely NO text, NO letters, NO numbers, NO calligraphy, NO seals with characters,
NO watermark anywhere in the image. Scene: <本格画面>
```

注意：水墨本身留白多，容易让气泡无处安放，Scene 里要主动要求主体集中在一侧。
模型爱画"印章 + 书法"，必须在负面约束里点名 `NO calligraphy, NO seals with characters`。

---

## 画风选择速查

| 题材 | 首选画风 |
|---|---|
| 职场吐槽、协作梗 | 日式黑白线稿 |
| 自然科普、儿童内容 | 水彩童书 / 钢笔淡彩 |
| 生活日常、家庭 | 彩铅手作 |
| 文化、节气、哲思 | 国风水墨 |
| 品牌、产品、通用 | 钢笔淡彩 |

不确定时用钢笔淡彩：容错最高，四格风格最容易统一。
