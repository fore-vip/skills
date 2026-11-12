# 版式库与扩展

## 为什么需要多套版式

一套固定骨架只换标签，会让主题和页面互相打架：讲服务的主题被迫用营收指标、讲产品的主题被迫用生活化语气。版式与叙事结构必须一起随主题变。

## 内置四套

| id | 适用主题 | 视觉 | 建议叙事顺序 |
|---|---|---|---|
| `warm` | 美容、SPA、餐饮、花艺、亲子、宠物、民宿 | 米白底、赤陶色、衬线标题、大圆角卡片、胶囊控件、首屏居中 | features → showcase → quote → steps → cta → faq |
| `tech` | AI、SaaS、工具、数据平台、开发者产品 | 深蓝黑、科技蓝、直角微圆角、首屏左对齐 | features → stats → steps → showcase → cta → faq |
| `fresh` | 活动、促销、电商、招生、开业、新品 | 白底高饱和橙、粗标题、强阴影、首屏居中 | stats → features → showcase → cta → faq |
| `editorial` | 文化、出版、艺术、教育、咨询、研究 | 米白墨黑、朱红点缀、细线分隔、大留白、方形控件 | quote → features → showcase → steps → faq → cta |

以上顺序只是默认值，`spec.sections` 的实际数组顺序即页面顺序；按主题需要可在 `sectionOrder` 上调整。

## token 分两类

- **形状 / 尺寸**：`--r-card --r-panel --r-pill --h-lg --h-md --h-sm --px-* --fs-* --icon --ctl-gap`。同一页内所有控件共享，保证同形。
- **色彩 / 质感**：`--bg --card --text --sub --muted --line --line-2 --brand --brand-soft --on-brand --surface --surface-2 --ok* --warn* --focus --shadow --font-title --hero-pad --cols`。决定跨主题差异。

`base.css` 的 `:root` 是兜底值（等同 `fresh`）；生成时把选中版式的 token 作为第二个 `:root` 覆盖块插在其后。控件规则本身不含任何硬编码 px 或色值，静态闸门会逐块扫描 `.ctl*` 规则，出现硬编码即 FAIL。

## 「统一」的判定

| 判定 | 范围 | 由谁保证 |
|---|---|---|
| 同页圆角 / 三档高度 / 字号 / 主色 / 焦点态一致 | 页内 | `.ctl` 基类 + 单一 token 源 + `verify_static.py` + `verify_viewport.mjs` 计算样式断言 |
| 不同主题形状不同 | 跨页 | `layouts.json` 的 token 覆盖，属设计意图 |

判据：同页所有可点控件读数必须落在同一组值上；两个主题之间这些值应明显不同。

## 新增版式

只改 `templates/layouts.json`，不动脚本：

1. 在 `layouts` 数组追加一条：`id`（小写英文）、`name`、`keywords`（中文按子串匹配，英文按词边界）、`intent`、`sectionOrder`、`heroAlign`
2. 补齐 `tokens`，至少覆盖上文「形状 / 尺寸」全部键；缺项会回落到 `base.css` 默认值，容易与其他版式撞脸
3. `python3 scripts/pick_layout.py --topic "<新主题原话>"` 确认命中
4. 写新 spec 生成页面，过五道闸门
5. 样例 spec 放进 `examples/`

调路由：命中不足就补 `keywords`；误命中就删词或加更长的专有词（长词权重 1.5，短词 1.0）。零命中时返回 `matched=false` 并给 `alternatives`，此时先确认或补版式，不要拿兜底结果直接交付。

## 首屏对齐

`heroAlign=left` 的版式（`tech` / `editorial`）在 `base.css` 有专门规则：首屏文字与按钮左对齐、标题不居中。这是版式级差异，不要用内联样式临时改。

## 版式不牺牲可达性

版式差异只改变视觉语言，不改变信息架构与可操作性。以下对所有版式一致，由静态闸门与双视口断言守住：

- 窄屏导航入口不得用 `display:none` 删除；改为第二行横向滚动，保证各区块有直达路径。
- sticky header 变高后 `.sect` 必须有 `scroll-margin-top`，锚点跳转与逐段截图不被盖住。
- 焦点态用实线描边（宽度抽成 `--focus-w` token），不用 `outline:none` 配半透明阴影。
- 所有 `<input>` 有可读名称，状态容器有 `role="status"` 与 `aria-live`，装饰 svg 有 `aria-hidden`。
- 有 `<form>` 就有 `<noscript>` 降级说明；无后端时表单控件整体禁用。

## 主题对照示例

两个差异明显的主题应得到明确不同的结果，这是「动态选版式」的可验收信号：

| 维度 | 生活服务类主题 | 技术产品类主题 |
|---|---|---|
| 命中版式 | `warm` | `tech` |
| 背景 / 主色 | 米白 / 赤陶 | 深蓝黑 / 科技蓝 |
| 控件圆角 | 胶囊 | 直角微圆角 |
| 三档高度 | 48 / 40 / 34px | 46 / 38 / 32px |
| 首屏对齐 / 标题字体 | 居中 / 衬线 | 左对齐 / 无衬线 |
| 叙事顺序 | features → showcase → quote → steps → cta → faq | features → stats → steps → showcase → cta → faq |
| 后端 | 预约表单接演示表 | 不接，表单说明未发送 |

复跑：

```bash
B=~/.workbuddy/skills/h5-app-builder
python3 "$B/scripts/pick_layout.py" --topic "社区美容门店 护肤 SPA 预约宣传页"
python3 "$B/scripts/build_page.py" --spec "$B/examples/beauty.spec.json" --out /tmp/beauty.html
python3 "$B/scripts/verify_static.py" --spec "$B/examples/beauty.spec.json" --page /tmp/beauty.html
node "$B/scripts/verify_viewport.mjs" --spec "$B/examples/beauty.spec.json" \
  --url http://127.0.0.1:PORT/index.html --shots /tmp/shot
```

云模式另加 `--cloud-config` 与 `verify_static.py --cloud`。换主题时必须整体重写文案与 sections，不要只替换几个词。
