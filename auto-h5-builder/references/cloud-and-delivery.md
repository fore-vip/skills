# 交付形态与云接线

## 一、形态判据

| 形态 | 判定信号 | 云接线 | 表单 |
|---|---|---|---|
| `webapp` | 应用 / 上线 / 发布 / 可访问 / 能收预约 / 留资 / 落库 / 后端 | 必须走本文第三节六步 | 可提交，写入真实表 |
| `site` | 部署到已有站点 / 官网 | 按站点需要决定 | 有表单就必须有落点 |
| `draft` | 先看看效果 / 做个草稿 / 只要设计 | 不接 | 整体禁用（input 与 button 都 disabled）+ `<noscript>` + 明确说明 |

命中以下任一条也必须接后端：提交要跨刷新或跨设备保留、需要登录或用户隔离、要存文件或调大模型、需要真实业务回写。

不为「显得完整」而接后端；也不为省事把用户要的应用降级成草稿。

`meta.intent` 原样记录用户当轮指令，`meta.deliverable` 是判定结果，两者一起留证，交付判定会用它比对诉求。

## 二、三态定义

`verify_delivery.py` 是唯一裁判，输出三态：

| 状态 | 含义 | 汇报方式 |
|---|---|---|
| `DELIVERED` | 应用实体、业务动作、站点地址、事实来源全部闭环 | 可写「已交付」；未取得在线链接仍须写「未上线」；含示例事实须写「演示应用，禁止作为真实门店对外发布」 |
| `DRAFT` | 用户明确同意的页面草稿 | 标题写「页面草稿，不是应用」，附转应用步骤，不写「应用已完成」 |
| `INCOMPLETE` | 诉求与产物不匹配，或关键闭环缺失 | 禁止汇报完成，逐条列缺项与补齐命令 |

判定顺序：页面与形态合法性 → `meta.intent` 与 `meta.deliverable` 是否一致 → 按形态查应用实体 / 站点 / 后端 / 事实 → 断言是否把业务不可用写成验收项 → 截图覆盖度。任一硬项失败即 INCOMPLETE。

## 三、应用创建六步

1. **inspect**：`workbuddy_cloud_service action=inspect` 看本会话已有应用；能复用就复用同一个 applicationId，换 ID 会让域名变化并导致 Origin 精确匹配失败。没有合适的才 `action=activate`（`applicationMode=create`、`appName` 用主题名、`domainPrefix` 用主题拼音或英文、`appType=web`）。
2. **确认框**：由平台弹出，不代替用户决定。`cancelled: true` → 记录 cancelled，停在 INCOMPLETE，不重试、不绕路、不静默降级成 localStorage 后谎称已接后端。
3. **配置边界**：只把 `endpoint / oauthRelayBaseUrl / publishableKey` 写进前端；`applicationId / resourceId` 等管理侧标识不落页面。
4. **建表**：DDL → `ENABLE ROW LEVEL SECURITY` → GRANT → 读/写 POLICY，顺序不能反（漏 GRANT 会得到形似策略失效的 42501）。管理侧跑一次「插入 → 读回 → 冲突更新 → 再读回」，结果写进交付说明。
5. **重新生成**：`meta.deliverable=webapp`、`meta.siteUrl=真实域名`、`meta.cloud.needed=true` 且填 `table/columns`，用 `--cloud-config` 与 `--base-url` 重新生成；前端只做 `select / insert`。
6. **发布路径**：发布为应用或站点上线需用户明确指令，但交付说明必须给出可执行命令清单。

没有登录时数据表是应用级共享表：任何人都能写，页面须说明「演示表、别填真实个人信息」。要做用户隔离就加 `owner_id` + 基于 `auth.uid()` 的 RLS 策略并接登录。

## 四、表结构与字段约定

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

`meta.cloud` 填 `{"needed":true,"table":"beauty_leads","columns":["name","contact","service"],"prefix":"预约 · "}`。`columns` 必须与表列名一致，生成器按 `f_<列名>` 取输入框。

## 五、前端接线与白名单

云模式只允许加载一个外部脚本：

```
https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js
```

静态闸门断言：脚本 src 精确等于该地址、初始化三字段都从 `CFG` 取、页面无 `applicationId / resourceId`。前端初始化一次 client，只做 CRUD。

## 六、失败路径必须可见

| 情况 | 页面表现 | 交付说明 |
|---|---|---|
| SDK 未加载 | 状态条提示「本次提交不会保存」 | 写明环境限制，不写「已接通」 |
| 字段未填完 | 提示先补全信息 | — |
| 初始化 / 写入异常或 RLS 拒绝 | 显示可读原因，不吞错 | 附错误信息 |
| 成功 | 明确写「已收到」并清空表单 | 附管理侧读回证据 |

任何时候都不把本地操作说成已存云端。管理侧验证通过但前端未跑通时，只写「管理侧已验证 / 前端未验证」并说明原因。

## 七、交付说明模板

```
产出文件：<index.html / spec / 应用标记 / shots 数量>
版式与理由：<id> 命中 <关键词>，与其他主题的差异是 <...>
交付形态：<webapp|site|draft> | 判定：<DELIVERED|DRAFT|INCOMPLETE>
五道闸门：① 自检 PASS ② 静态 N 项 ③ 双视口 N 项 ④ 逐段截图 N 张 ⑤ <状态>
六角色自检：产品 / UI / 开发 / 测试 / 业务方 / 用户 逐条结论
云服务：接了什么、没接什么、取消原因、写入读回证据
未做事项：未上线 / 未发布 / 待补事实清单
下一步命令：激活、生成、发布各一条可执行命令
```
