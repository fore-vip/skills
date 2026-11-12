# 云接线与应用创建（webapp 必接）

## 判据：v3 起由交付形态决定

**`meta.deliverable=webapp` 时必须接后端**，这不是可选项。历史事故：专家把「演示页」当成默认口径，做出一个「能填手机号、点了却不会保存」的预约页，用户看到的是半成品。

| 形态 | 云接线 | 表单 |
|---|---|---|
| `webapp` | 必须 `inspect → activate → 建表 → 写入读回 → --cloud-config` | 可提交，写入真实表 |
| `site` | 按站点需要决定，但要有部署记录与真实站点地址 | 有表单就必须有落点 |
| `draft` | 不接 | **整体禁用**（input 与 button 都 disabled），加 `<noscript>` 与明确说明 |

另外命中任一条也必须接：提交要跨刷新 / 跨设备保留、需要登录或用户隔离、要存文件或调大模型、需要真实业务回写。**不要为了显得完整而接后端**，接了就要跑通写入读回；也不要为了省事把用户要的应用悄悄降级成草稿。

## 流程

1. `workbuddy_cloud_service` 的 `inspect` 看本会话已有应用；能复用就复用同一个 applicationId，**换 ID 会让保留域名与 Origin 精确匹配失效**
2. `activate`（`applicationMode=create`、`appName`、`domainPrefix`、`appType=web`）→ 平台确认框由用户决定
3. **确认框被取消（`cancelled=true`）→ 不重试、不绕路、不静默降级成 localStorage 后谎称已接后端**，如实记为「未接入」
4. 激活成功后拿 `publicConfig`，只把 `endpoint / oauthRelayBaseUrl / publishableKey` 三个值写进前端；`applicationId / resourceId` 不落前端
5. 管理侧建表（DDL → ENABLE RLS → GRANT → POLICY，顺序不能反；漏 GRANT 会得到形似策略失效的 42501）
6. `build_page.py --cloud-config /tmp/public-config.json` 生成带云表单提交的页面

## 表结构示例

```sql
CREATE TABLE beauty_leads (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL, contact TEXT NOT NULL, service TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE beauty_leads ENABLE ROW LEVEL SECURITY;
GRANT SELECT, INSERT ON TABLE public.beauty_leads TO authenticated, anon;
CREATE POLICY beauty_leads_read ON beauty_leads FOR SELECT TO authenticated, anon USING (true);
CREATE POLICY beauty_leads_insert ON beauty_leads FOR INSERT TO authenticated, anon WITH CHECK (true);
```

`meta.cloud` 填 `{"needed":true,"table":"beauty_leads","columns":["name","contact","service"],"prefix":"预约 · "}`。`columns` 必须与表列名一致，生成器会按 `f_<列名>` 取输入框。

**没有登录时这是应用级共享表**：任何人都能写，页面要如实说明「演示表、别填真实个人信息」。要做用户隔离就加 `owner_id` + 基于 `auth.uid()` 的 RLS 策略，并接登录。

## 前端接法与白名单

云模式只允许加载一个外部脚本：

```
https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js
```

`verify_static.py` 会断言脚本 src 精确等于它、初始化三字段都从 `CFG` 取、页面无 `applicationId / resourceId`。前端只做 `insert` 一类 CRUD，初始化一次 client。

## 失败路径（必须可见）

- SDK 没加载出来 → 状态条提示「本次提交不会保存」
- 字段没填完 → 提示「请先把信息填完整」
- 初始化 / 写入异常或 RLS 拒绝 → 显示可读原因，不吞错
- 成功 → 明确写「已收到」并清空表单

**绝不把本地操作说成已存云端。** 本机沙箱对 CDN 时通时不通（`curl` 可能返回 000），这是环境限制，不是功能缺失；如实在交付说明里写清。

## 本轮验证记录

- 应用 `wbapp_ZwQZBhDOo16VOG4OVnIe2r` 已在上一轮激活成功（`billingStatus=normal / provisionStatus=assigned`）
- 新建 `beauty_leads`：`pg_class` 回读 `rls=true`、2 条策略；管理侧 insert / read / delete 全通过
- 前端端到端：本机 CDN 本次未加载出 SDK（`typeof WorkBuddyCloud === "undefined"`），页面显示「云端组件没加载出来，本次提交不会保存」，提交后显示「当前未连到云端，这条没有保存」，**失败路径符合预期、没有假装成功**
- 上一轮在 `beauty_tasks` 上曾完成过一次真实端到端写入读回（前端点击 → SQL 回读状态变化 → 刷新保留），证明接线本身可用

## v3 强制项

- P3.5 的六步顺序见 `references/delivery-contract.md`；**确认框被取消 → 停在 INCOMPLETE，不重试、不绕路、不谎称已接后端**。
- `meta.cloud` 的 `needed / table / columns` 与 `--cloud-config` 必须同时具备，生成器自检会拦住「声称是应用却没接后端」。
- 没有后端时 `ctaLabel` / `hero.primary` / `cta.submit` 不得含「预约 / 提交 / 立即 / 报名 / 下单」，避免承诺做不到的事。
- 页面必须给可见失败提示；CDN 不通时如实写「本次提交不会保存」，绝不把本地操作说成已存云端。
- 交付判定 `verify_delivery.py` 会核对应用实体标记、真实站点地址、后端落点与业务事实来源，任一缺失即 INCOMPLETE。
