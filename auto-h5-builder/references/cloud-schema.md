# 云端建表、权限与接线

一个应用 = 一家店。两张表：`bookings` 存订单，`store_owner` 存店长归属（只有一行）。

## 一、建表与授权（13 条，按顺序逐条执行，`mode=migrate`）

```sql
-- ① 订单表
CREATE TABLE bookings (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,                -- 单号，前端生成，顾客与店主用它对单
  customer_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  service TEXT NOT NULL,
  slot_date DATE NOT NULL,
  slot_time TEXT NOT NULL,
  note TEXT,
  invite_code TEXT,                          -- 推荐人码，为空表示自然到店
  status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ② 开 RLS
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- ③ 授权（漏了会得到形似策略失效的 42501）
GRANT INSERT, SELECT ON TABLE public.bookings TO anon, authenticated;
GRANT UPDATE ON TABLE public.bookings TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.bookings_id_seq TO anon, authenticated;

-- ④ 订单策略
CREATE POLICY bookings_insert_public ON bookings FOR INSERT TO anon, authenticated
  WITH CHECK (status = 'pending');
CREATE POLICY bookings_select_owner ON bookings FOR SELECT TO authenticated
  USING (EXISTS (SELECT 1 FROM store_owner WHERE owner_uid = auth.uid()));
CREATE POLICY bookings_update_owner ON bookings FOR UPDATE TO authenticated
  USING (EXISTS (SELECT 1 FROM store_owner WHERE owner_uid = auth.uid()))
  WITH CHECK (status IN ('pending','confirmed','done','cancelled'));

-- ⑤ 店长归属表：主键固定为 1，所以全库只可能有一行
CREATE TABLE store_owner (
  id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  owner_uid TEXT NOT NULL DEFAULT auth.uid(),   -- 服务端填，前端不传
  claimed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE store_owner ENABLE ROW LEVEL SECURITY;
GRANT SELECT, INSERT ON TABLE public.store_owner TO authenticated;
CREATE POLICY store_owner_read ON store_owner FOR SELECT TO authenticated
  USING (owner_uid = auth.uid());
CREATE POLICY store_owner_claim ON store_owner FOR INSERT TO authenticated
  WITH CHECK (owner_uid = auth.uid());
```

`exec_sql` 一次只能执行一条语句，上面要分 13 次跑。页面没有 DELETE 权限：订单只能标 `cancelled`，店长归属只能由 `exec_sql` 改。

## 二、首登即店长

`store_owner` 只有一行，谁先登录谁写进去，之后别人写不进来：

| 登录的账号 | 读 `store_owner` | 写 `store_owner` | 结果 |
|---|---|---|---|
| 第一个账号 | 0 行 | 成功（`DEFAULT auth.uid()`） | 成为店长，页面直接进管理台 |
| 之后的账号 | 0 行（策略只看自己的行） | 失败 `23505` 主键冲突 | 页面提示「这个账号不是店主」，立即退出登录 |

所以「店长」不是配置出来的角色，是首登行为：上线后先自己登录一次占住，再把链接发出去。换店长只能在 `exec_sql` 里改这一行：

```sql
UPDATE store_owner SET owner_uid = '<新账号 uid>', claimed_at = now() WHERE id = 1;
```

## 三、策略对应关系

| 策略 | 谁 | 能做什么 |
|---|---|---|
| `bookings_insert_public` | 匿名 + 登录 | 只能写 `pending` 新单，不能挑状态 |
| `bookings_select_owner` | 登录且是店长 | 读全部订单；匿名读不到任何行，手机号不外泄 |
| `bookings_update_owner` | 登录且是店长 | 改状态，且只能改成四个合法值 |
| `store_owner_read` | 登录 | 只读得到自己那一行 |
| `store_owner_claim` | 登录 | 只在表为空时写入成功 |

## 四、前端接线

页面只拿三个值，全部来自 `publicConfig`：

```js
var cloud = WorkBuddyCloud.createWorkBuddyCloud({
  endpoint: CFG.endpoint,
  oauthRelayBaseUrl: CFG.oauthRelayBaseUrl,
  publishableKey: CFG.publishableKey
});
```

- 顾客下单：`cloud.database.from('bookings').insert(row)`，**不要链 `.select()`**，因为匿名没有读权限。
- 店长登录：`sendOtp({email|phone})` → 保存 `verificationId / isExistingUser` → `verifyOtp({...})`。
- 认领店长：登录后 `select('*').from('store_owner')`；0 行则 `insert({ id: 1 })`（不传 `owner_uid`）。
- 店长读单：`select('*').order('created_at',{ascending:false}).limit(200)`。
- 店长改状态：`update({status}).eq('id', id)`。
- 退出：`signOut()`，并清空页面上已加载的订单。
- `applicationId / resourceId` 不进前端，生成器会丢弃。

## 五、邀请统计口径

```sql
SELECT invite_code, count(*) AS orders
FROM bookings
WHERE invite_code IS NOT NULL
GROUP BY invite_code
ORDER BY orders DESC;
```

页面上的「邀请单」= `invite_code` 非空的订单数；单条订单卡片直接显示邀请码，便于店主对账。顾客自己的邀请码存在浏览器本地（`auto-h5.code`），清缓存会重置，属预期行为。

## 六、失败路径

| 情况 | 页面表现 | 交付说明 |
|---|---|---|
| SDK 未加载 | 提交失败提示「云端组件没加载出来」，可拨门店电话 | 写明是网络或 CDN 问题 |
| 4xx / RLS 拒绝 | 显示服务端原文，不吞错 | 附错误原文与触发的 SQL |
| 第二个账号登录 | 「这个账号不是店主：本店已由首次登录的账号管理」 | 属预期，说明店长账号是哪个 |
| 邮箱含 `+` 等特殊字符 | 「这个邮箱收不到验证码，换一个常用邮箱」 | 平台不收这类地址 |
| 邮件/短信登录未开启 | 「店主登录还没开通：到云服务控制台打开…」 | 让店主去控制台开开关 |
| 发送过于频繁 | 「请求太频繁：同一邮箱每分钟只能发一次」 | 等一分钟重试 |
| 提交成功 | 显示单号，清空表单 | 附 SQL 读回证据 |

任何情况下都不把本地写入说成已存云端。
