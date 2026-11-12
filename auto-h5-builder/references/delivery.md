# 交付清单与验收记录

## 一、六步交付

| 步 | 动作 | 判据 |
|---|---|---|
| 1 | 写 `spec.json`，补全门店必填项 | `build_app.py` 校验通过 |
| 2 | `workbuddy_cloud_service action=inspect`，选定 applicationId | 复用已有应用，不新建同义应用 |
| 3 | `activate`（reuse 或 create，`appType=web`） | 拿到 `publicConfig`；用户取消就停 |
| 4 | `exec_sql` 建表 + 授权 + 策略（见 cloud-schema.md 8 条） | 每条返回空数组即成功 |
| 5 | `build_app.py --cloud-config --base-url` 生成正式页 | 静态闸门 24 项全过 |
| 6 | `verify_flow.mjs --cloud` 真机流程 | 21 项全过，且 SQL 能查到刚提交的单 |

第 6 步之后还要手动跑一次「管理台登录 → 改状态」，并提醒店主打开验证码登录开关。

## 二、验收记录模板

```
产出：index.html（单文件，四视图）+ spec.json + bookings 表
云端：applicationId / 表名 / 单号
证据：提交单号 <code> → SQL 读回 status=pending → 管理台改 confirmed → SQL 读回 confirmed
邀请：分享链接 <url?ref=CH-XXXX>；带该参数下单后 invite_code=CH-XXXX
闸门：静态 24/24，流程 21/21
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

## 四、汇报口径

- 没发布就写「本地预览，未上线」。
- 用了示例门店信息就写「示例数据」，并附待补清单。
- 登录开关没开就写「管理台登录未验证」，不写「管理台可用」。
- 改动过策略或表结构，把执行的 SQL 原文贴进交付说明。
