# 云端建表、权限与接线

一个应用 = 一家店。表只有一张 `bookings`，四视图都围绕它。

## 一、建表与授权（按顺序逐条执行）

```sql
-- 1 建表
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

-- 2 开 RLS
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- 3 授权（漏了会得到形似策略失效的 42501）
GRANT INSERT, SELECT ON TABLE public.bookings TO anon, authenticated;
GRANT UPDATE ON TABLE public.bookings TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.bookings_id_seq TO anon, authenticated;

-- 4 策略
CREATE POLICY bookings_insert_public ON bookings FOR INSERT TO anon, authenticated
  WITH CHECK (status = 'pending');
CREATE POLICY bookings_select_auth ON bookings FOR SELECT TO authenticated USING (true);
CREATE POLICY bookings_update_auth ON bookings FOR UPDATE TO authenticated
  USING (true) WITH CHECK (status IN ('pending','confirmed','done','cancelled'));
```

四条策略对应四件事：

| 策略 | 谁 | 能做什么 |
|---|---|---|
| insert | 匿名 + 登录 | 只能写 `pending` 新单，不能挑状态 |
| select | 仅登录 | 店主读全部订单；匿名读不到任何行，手机号不外泄 |
| update | 仅登录 | 改状态，且只能改成四个合法值 |
| 无 delete | — | 订单不删，只标 `cancelled` |

`exec_sql` 一次只能执行一条语句，上面 8 条要分 8 次跑，`mode` 用 `migrate`。

## 二、单店模型的边界

这个范式只服务一家门店，所以订单表不带 `store_id`：应用本身就属于这家店。

- 顾客端不提供任何登录入口，因此能登录的只有店主。
- 不要把管理台链接公开分享；它靠登录拦，不靠隐藏拦。
- 需要多店（一个应用管多家分店）时，加 `stores` 表 + `bookings.store_id` + 基于 `owner_id = auth.uid()` 的 RLS，那是另一个模型，别在这个范式里混着改。

## 三、前端接线

页面只拿三个值，全部来自 `publicConfig`：

```js
var cloud = WorkBuddyCloud.createWorkBuddyCloud({
  endpoint: CFG.endpoint,
  oauthRelayBaseUrl: CFG.oauthRelayBaseUrl,
  publishableKey: CFG.publishableKey
});
```

- 顾客下单：`cloud.database.from('bookings').insert(row)`，**不要链 `.select()`**，因为匿名没有读权限。
- 店主登录：`sendOtp({email|phone})` → 保存 `verificationId / isExistingUser` → `verifyOtp({...})`。
- 店主读单：`select('*').order('created_at',{ascending:false}).limit(200)`。
- 店主改状态：`update({status}).eq('id', id)`。
- `applicationId / resourceId` 不进前端，生成器会丢弃。

## 四、邀请统计口径

```sql
SELECT invite_code, count(*) AS orders
FROM bookings
WHERE invite_code IS NOT NULL
GROUP BY invite_code
ORDER BY orders DESC;
```

页面上的「邀请单」= `invite_code` 非空的订单数；单条订单卡片直接显示邀请码，便于店主对账。顾客自己的邀请码存在浏览器本地（`auto-h5.code`），清缓存会重置，属预期行为。

## 五、失败路径

| 情况 | 页面表现 | 交付说明 |
|---|---|---|
| SDK 未加载 | 提交失败提示「云端组件没加载出来」，可拨门店电话 | 写明是网络或 CDN 问题 |
| 4xx / RLS 拒绝 | 显示服务端原文，不吞错 | 附错误原文与触发的 SQL |
| 邮件/短信登录未开启 | 「店主登录还没开通：到云服务控制台打开…」 | 让店主去控制台开开关 |
| 发送过于频繁 | 「请求太频繁：同一邮箱每分钟只能发一次」 | 等一分钟重试 |
| 提交成功 | 显示单号，清空表单 | 附 SQL 读回证据 |

任何情况下都不把本地写入说成已存云端。
