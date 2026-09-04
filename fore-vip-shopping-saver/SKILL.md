---
name: fore-vip-shopping-saver
display_name: 购物超省
display_name_en: Shopping Super-Save
description: 购物超省（fore.vip）— 输入商品名称或图片，从用户配置的 ≥3 个购物/导购/联盟接口汇聚商品链接、样图/SKU 图、价格与领券地址，按质量评分/价格/券后价排序，生成简洁大气的高端 HTML 比价清单；图片缺失或跨域时自动占位。当用户说"购物超省""帮我找 XX 的优惠/优惠券""XX 哪里买最便宜""全网比价""搜 XX 优惠券""识别这张图找同款优惠"时使用。
description_zh: 全网比价优惠聚合。输入商品名称或图片，从用户配置的 ≥3 个购物 / 导购 / 联盟接口汇聚商品链接、样图与 SKU 图、价格与领券地址，按质量评分 / 价格 / 券后价排序，生成简洁大气的高端 HTML 比价清单；图片缺失或跨域时自动占位。
description_en: Cross-store price comparison and deal aggregator. Given a product name or image, it pulls product links, sample and SKU images, prices and coupon URLs from three or more user-configured shopping, deal and affiliate sources, sorts by quality score, price and post-coupon price, and generates a clean, premium HTML comparison page. Missing or cross-origin images fall back to placeholders.
category: ecommerce
version: 1.0.0
author: fore.vip
agent_created: true
triggers:
  - "购物超省"
  - "帮我找"
  - "优惠券"
  - "哪里买便宜"
  - "全网比价"
  - "比价"
  - "搜一下"
  - "优惠券"
  - "找券"
  - "购物省钱"
  - "识别这个商品"
  - "找同款"
negative_triggers:
  - "外卖领券 / 美团红包 / 饿了么优惠（由 cps 技能处理，不重复做）"
  - "仅查询物流 / 订单状态，无购买比价意图"
  - "仅问商品参数/评测无购买与优惠意图"
  - "股票 / 基金 / 行情报价"
compatibility:
  - WorkBuddy
  - Marvis
  - MCP-client
---

# 购物超省 · 全网比价优惠聚合

用户输入**商品名称**或**商品图片**，你从用户已配置的 ≥3 个购物 / 导购 / 联盟接口汇聚同款商品，
提炼出**商品链接、样图 / SKU 图、价格、领券地址**，按**质量评分 / 价格 / 券后价**排序，输出一份
**简洁大气、高端**的 HTML 比价清单。图片缺失或存在跨域防盗链时自动使用占位图。

> 与 `cps`（外卖领券）分工：本技能做**实物商品全网比价**；外卖红包走 `cps`，不要重复处理。

## 用户会怎么说

- 「购物超省：iPhone 15」「帮我找 AirPods Pro 的优惠」
- 「XX 哪里买最便宜」「全网比价一下这个键盘」
- 「搜一下 茅台 的优惠券」「找券」
- 发来一张商品图：「识别这个，找同款优惠」

## 工作流程

### 1. 取得商品名（输入归一化）

- 文本输入 → 直接作为 `keyword`。
- **图片输入** → 用你的视觉能力识别图中商品（品牌 / 型号 / 品类），与用户确认或直接使用识别结果作为 `keyword`。
  说明：真正的以图搜货需对应平台识图 API（淘宝联盟 / 京东联盟支持，属进阶 custom 适配器），
  默认走「识别商品名 → 关键词搜索」即可满足需求。

### 2. 确认来源已配置（关键，≥3 端）

读取 `references/providers.md` 了解来源与配置规范。运行前确认 `providers.json` 已就绪：

- 查找顺序：`--config` → `$SHOPPING_SAVER_CONFIG` → `~/.workbuddy/fore-vip-shopping-saver/providers.json` → `<skill>/config/providers.json`。
- **必须 ≥3 个 `enabled` 来源**（任务硬要求）。模板 `references/providers.example.json` 已含 3 端 key-based 来源（聚推客 / 折淘客 / 导购API示例），可直接复制使用。
- 若用户尚未配置：引导其任选 ≥3 个可达来源（优先 key-based：聚推客、折淘客、大淘客/选单网/好单库 等），
  在对应开放平台注册拿到密钥，按模板填 `request` 与 `response.fields`，密钥用 `${ENV}` 走环境变量（不入 Git）。

### 3. 运行聚合脚本

```bash
python3 <skill>/scripts/shopping_saver.py \
  --keyword "<商品名>" \
  [--config <providers.json 路径>] \
  [--sort score|price|coupon] \
  [--limit 30] \
  [--output 结果.html]
```

- 默认排序 `score`（质量评分降序 → 券后价升序）；`price` 按原价升序；`coupon` 按券后价升序。
- 脚本逐来源请求、规范化、排序、生成**自包含** HTML，并打印 JSON 摘要（各来源命中数 / 总数 / 输出路径）。
- 单来源失败不影响整体，会在 stderr 提示并跳过。
- 若环境无 Python，按 `references/providers.md` 的数据模型与字段，手动整理为同样结构的 HTML 清单（仅兜底）。

### 4. 呈现结果

把生成的 HTML 路径交给用户（建议直接打开预览）。口头简述：**共 N 条、来自哪些来源、推荐的前 1–3 个最优选项**
（券后价最低 / 评分最高）。不要只丢链接，给一句结论。

## 数据模型（每条商品）

| 字段 | 说明 |
|------|------|
| `title` | 商品标题 |
| `image` | 封面图（缺失→占位） |
| `sku_images` | SKU 图数组 |
| `price` | 原价 |
| `coupon_amount` | 优惠券面额 |
| `coupon_url` | 领券地址 |
| `score` | 质量评分（参与排序） |
| `product_url` | 商品购买 / 落地链接 |

券后价 = `price − coupon_amount`（任一项缺失则回退原价）。

## 输出规范（HTML 清单）

- **形态**：响应式卡片网格，每条含封面图、标题、来源角标、价格（券后价突出、原价划线）、领券标签、去购买按钮。
- **风格**：简洁大气高端——浅灰底、白卡、圆角 16px、克制的红色 `#e53e3e` 作价格/优惠强调色、悬停微浮起。
- **占位**：无封面图或跨域防盗链图片自动用内置 SVG 占位（`referrerpolicy="no-referrer"` + `onerror` 兜底），不出现裂图。
- **自包含**：HTML 内联 CSS 与占位图（data-URI），单文件可直接打开，无外部依赖。

## 边界与合规

- **凭证零外泄**：密钥只进 `providers.json`（用户级 / 环境变量），不在对话、日志、产物中回显明文。
- **不代下单不代付**：只提供链接与比价结论，下单 / 领券动作由用户在对应平台完成。
- **广告法红线**：不得对商品做绝对化 / 极限词承诺；优惠券信息如实展示，不夸大「全网最低」。
- **数据时效**：价格与券以平台实时为准，输出中注明「以平台实时为准」。

## 关联技能 / 工具

- 外卖红包 / 美团饿了么领券 → `cps`
- 来源配置规范与签名类平台接法 → `references/providers.md`
- 配置模板（3 端可运行示例） → `references/providers.example.json`
- 聚合 / 排序 / 渲染 → `scripts/shopping_saver.py`

## 参考资料

- `references/providers.md` — 来源清单、providers.json 结构、密钥安全、custom 适配器（签名平台）写法
- `references/providers.example.json` — 3 端 key-based 来源配置模板
- `scripts/shopping_saver.py` — 无第三方依赖的聚合脚本（urllib / json / argparse）
