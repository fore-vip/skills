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

## 第三次运行：专家独立会话（反面案例）

用户单独调用专家、只给「社区美容门店」主题。专家按 v2 SKILL 跑完 P0–P4：路由命中 `warm`，写出 `community-beauty.spec.json` 与 `index.html`（20749 字节），产出四张 390px 截图，静态闸门 16/16、视口断言 29/29 全 PASS，然后汇报完成。

用 v3 的 `verify_delivery.py` 回判（把用户诉求原话传进去）得到 `RESULT INCOMPLETE`，缺项逐条为：

- `meta.deliverable` 未声明，用户要的是应用；
- 页面 `canonical / og:url / ld+json.url` 是 `https://example.com/index.html`；
- 草稿里留着可提交的表单，主 CTA 承诺「约一次到店护理」却不会保存；
- 断言把「没有发送」「不会保存」「未开放真实预约」写成 PASS 验收项；
- 四张截图没有覆盖全部六个区块。

这不是专家执行失败，而是**流程里根本没有创建应用这一步**。v3 的交付形态契约、P3.5、第五道闸门与六角色清单就是针对这次复盘加的。修好后同一份 spec 重新生成，静态闸门 37 项、双视口 34 项全 PASS，交付判定为 `DRAFT`（如实标注「页面草稿，不是应用」）。

另有两个正面样本：美容应用 `webapp` 形态（有 `.genie`、真实站点地址、云端表与可提交表单）判定 `DELIVERED`；门店自动化产品 `draft` 形态判定 `DRAFT`。三态都被实跑验证过，不是纸面规则。
