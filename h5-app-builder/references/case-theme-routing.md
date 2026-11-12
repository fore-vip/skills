# 案例：同一套技能，两个主题，两种版式

验证「模板选择根据主题动态变化」是否真的成立，必须至少用两个差异明显的主题跑通。

| 项 | 实例 A | 实例 B |
|---|---|---|
| 主题原话 | 社区美容门店 护肤 SPA 预约宣传页 | 门店自动化 AI SaaS 系统 巡店 数据平台 产品宣传 |
| 路由命中 | 美容、护肤、SPA、门店（score 4.5） | AI、SaaS、数据、自动化、平台（score 6.0） |
| 选中版式 | `warm` 暖调生活服务 | `tech` 深色科技产品 |
| 背景 / 主色 | 米白 `#faf6f2` / 赤陶 `#b4573c` | 深蓝黑 `#080d17` / 科技蓝 `#3b82f6` |
| 控件圆角 | 999px 胶囊 | 8px 直角 |
| 三档高度 | 48 / 40 / 34px | 46 / 38 / 32px |
| 首屏对齐 | 居中 | 左对齐 |
| 标题字体 | 衬线 | 无衬线 |
| 叙事顺序 | features → showcase → quote → steps → cta → faq | features → stats → steps → showcase → cta → faq |
| 必备词 | 护理 / 皮肤 / 预约 / 美容 | 门店 / 系统 / 自动化 / 接入 |
| 禁用词 | 营业额 / 订单数 / 客单价 / 品类动销 / 自动门店 | 美容 / 护理 / SPA / 皮肤 / 悦己研肤 |
| 云服务 | 预约表单接 `beauty_leads` 演示表 | 不接，表单明说未发送 |
| 静态闸门 | 21 项全 PASS | 16 项全 PASS |
| 视口闸门 | 19 项全 PASS | 18 项全 PASS |
| 横向溢出 | 390/390 | 390/390 |

两页的 `.ctl` 控件数量都是 11：页内圆角、三档高度、主色各自完全统一；跨页这些值全不同。这正是「页内统一 + 主题动态」的判定证据。

## 这一轮纠正过的三层偏差

1. **交付物搞错**：用户要的是「专家（含 SKILL）」，能力是按主题动态出页面；之前交的是一个具体页面。
2. **模板是死的**：固定 KPI 演示台（营收 / 人次 / 均价 / 待办 / 回话）换标签就复用，美容主题自然不搭调。
3. **内容与顺序串台**：品牌沿用别的项目、制作过程写进正文、说明放最后、口径前后矛盾。

修法是同一次改动：**版式库 + 主题路由 + 内容模型 + 双闸门**，而不是逐条改文案。

## 复跑命令

```bash
B=~/.workbuddy/skills/h5-app-builder
python3 "$B/scripts/pick_layout.py" --topic "社区美容门店 护肤 SPA 预约宣传页"
python3 "$B/scripts/build_page.py" --spec "$B/examples/beauty.spec.json" --out /tmp/beauty.html
python3 "$B/scripts/verify_static.py" --spec "$B/examples/beauty.spec.json" --page /tmp/beauty.html
node "$B/scripts/verify_viewport.mjs" --spec "$B/examples/beauty.spec.json" \
  --url http://127.0.0.1:PORT/index.html --shots /tmp/shot
```

云模式另加 `--cloud-config` 与 `verify_static.py --cloud`。样例 spec 在 `examples/`：改主题时必须整体重写文案与 sections，不要只替换几个词。
