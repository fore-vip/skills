# 版式设计与扩展

## 为什么需要多套版式

一个固定骨架换词，会让主题和页面互相打架：美容门店出现「成交额 / 到店人次 / 单次均价」、制作过程写进正文，读者当然看不懂。**版式与叙事结构必须一起随主题变**。

## 内置四套

| id | 适用主题 | 视觉 | 建议叙事顺序 |
|---|---|---|---|
| `warm` | 美容、SPA、餐饮、花艺、亲子、宠物、民宿 | 米白底、赤陶色、衬线标题、大圆角卡片、胶囊控件 | features → showcase → quote → steps → cta → faq |
| `tech` | AI、SaaS、工具、数据平台、开发者产品 | 深蓝黑、科技蓝、直角微圆角、左对齐首屏 | features → stats → steps → showcase → cta → faq |
| `fresh` | 活动、促销、电商、招生、开业、新品 | 白底高饱和橙、粗标题、强阴影、居中首屏 | stats → features → showcase → cta → faq |
| `editorial` | 文化、出版、艺术、教育、咨询、研究 | 米白墨黑、朱红点缀、细线分隔、大留白、方形控件 | quote → features → showcase → steps → faq → cta |

## token 分两类

- **形状 / 尺寸**：`--r-card --r-panel --r-pill --h-lg --h-md --h-sm --px-* --fs-* --icon --ctl-gap`。同一页内所有控件共享，保证统一。
- **色彩 / 质感**：`--bg --card --text --sub --muted --line --line-2 --brand --brand-soft --on-brand --surface --surface-2 --ok* --warn* --focus --shadow --font-title --hero-pad --cols`。决定跨主题差异。

`base.css` 的 `:root` 是兜底值（等同 `fresh`）；生成时把选中版式的 token 作为第二个 `:root` 覆盖块插在其后。**控件规则本身不含任何硬编码 px 或色值**，静态闸门会逐块扫描 `.ctl*` 规则，出现硬编码直接 FAIL。

## 「统一」的正确判定

| 判定 | 范围 | 由谁保证 |
|---|---|---|
| 同一页内圆角 / 三档高度 / 字号 / 主色 / 焦点态一致 | **页内** | `.ctl` 基类 + 单一 token 源 + `verify_static.py` + `verify_viewport.mjs` 计算样式断言 |
| 不同主题形状不同 | **跨页** | `layouts.json` 的 token 覆盖，是设计意图 |

例：美容页所有控件 999px / 48-40-34px / 赤陶；门店产品页所有控件 8px / 46-38-32px / 科技蓝。两页各自内部完全统一，彼此明显不同。

## 新增版式（扩展点）

只改 `templates/layouts.json`，不动脚本：

1. 在 `layouts` 数组追加一条，填 `id`（小写英文）、`name`、`keywords`（主题词，中文直接子串匹配，英文按词边界）、`intent`、`sectionOrder`、`heroAlign`
2. 补齐 `tokens`；至少要有上文「形状 / 尺寸」全部键，缺的会回落到 `base.css` 默认值（可能和其它版式撞脸）
3. 跑 `python3 scripts/pick_layout.py --topic "<新主题原话>"` 确认命中
4. 写一份新 spec，`python3 scripts/build_page.py` 生成后过四道闸门
5. 把样例 spec 放进 `examples/`

调路由：命中不够就往对应版式的 `keywords` 加词；误命中就删词或加更长的专有词（长词权重 1.5，短词 1.0）。零命中时返回 `matched=false` 并给 `alternatives`，**此时不要直接用兜底交付**，先问用户或补版式。

## 首屏对齐

`heroAlign=left` 的两套（`tech` / `editorial`）在 `base.css` 里有专门规则：首屏文字与按钮左对齐、标题不居中。这是版式级差异，不要靠内联样式临时改。
