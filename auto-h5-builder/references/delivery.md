# 交付清单与验收记录

## 一、七步交付

| 步 | 动作 | 判据 |
|---|---|---|
| 1 | 写 `spec.json`，补全门店必填项 | `build_app.py` 校验通过 |
| 2 | `workbuddy_cloud_service action=inspect`，选定 applicationId | 复用已有应用，不新建同义应用 |
| 3 | `activate`（reuse 或 create，`appType=web`） | 拿到 `publicConfig`；用户取消就停 |
| 4 | `exec_sql` 建表 + 授权 + 策略（见 cloud-schema.md 13 条） | 每条返回空数组即成功 |
| 5 | `build_app.py --cloud-config --base-url` 生成正式页 | 静态闸门 37–38 项全过 |
| 6 | `verify_flow.mjs --cloud` 真机流程 | 37–38 项全过，且 SQL 能查到刚提交的单 |
| 7 | 店长用真实账号登录一次 | 菜单出现「店长」标记、管理台直接可见并可改状态；同时完成首登认领 |

第 7 步必须在分享链接之前做完：先占住店长归属，再把页面发出去。之后还要提醒店主打开验证码登录开关。

## 二、验收记录模板

```
产出：index.html（单文件，四页）+ spec.json + bookings / store_owner 两张表
导航：右上菜单（预约 / 分享 / 登录 / 退出）；登录即店长登录，登录后直达管理台
云端：applicationId / 表名 / 单号
证据：提交单号 <code> → SQL 读回 status=pending → 管理台改 confirmed → SQL 读回 confirmed
店长：store_owner.owner_uid = <uid>（认领时间 <ts>）；第二个账号登录被拒绝
邀请：分享链接 <url?ref=CH-XXXX>；带该参数下单后 invite_code=CH-XXXX
闸门：静态 37/37，流程 38/38
登录开关：邮箱验证码 已开 / 未开（未开则管理台不可用，必须写清）
未做：未发布上线；示例数据仅演示
```

## 三、常见阻塞

| 现象 | 原因 | 处理 |
|---|---|---|
| 提交报「云端组件没加载出来」 | 页面加载不到 CDN SDK | 换网络重试；本机可用 npm 包内 `lib/index.global.js` 自托管做本地验收，线上仍用官方 CDN |
| 提交报 `42501` | 漏 GRANT 或漏策略 | 按 cloud-schema.md 逐条补齐，`migrate` 模式执行 |
| 管理台登录报「未开启」 | 云服务控制台没开邮箱/短信登录 | 让店主开一次开关，属于一次性配置 |
| 登录后列表为空 | 还没人下过单，或策略只给了 authenticated | 先用顾客端下一单，再刷新管理台 |
| 发布后登录失效 | 换了 applicationId，域名变了，Origin 对不上 | 必须复用同一个 applicationId |
| 邮件每分钟只能发一次 | 平台限流 | 等 60 秒再点，不要连点 |
| 登录报「这个账号不是店主」 | `store_owner` 已被首登账号占住 | 属预期；用店主账号登录，或 `exec_sql` 改这一行 |
| 邮箱报「收不到验证码」 | 邮箱含 `+` 等平台不收的字符 | 换一个常用邮箱 |

## 四、汇报口径

- 没发布就写「本地预览，未上线」。
- 用了示例门店信息就写「示例数据」，并附待补清单。
- 登录开关没开就写「管理台登录未验证」，不写「管理台可用」。
- 改动过策略或表结构，把执行的 SQL 原文贴进交付说明。
