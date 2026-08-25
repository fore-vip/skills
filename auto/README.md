# AUTO — 付费解锁后获取主题最佳执行步骤

输入一个「主题」，AUTO 返回该主题**最优质的执行步骤提示**。步骤来自 `mcp.auto` 已沉淀内容；无沉淀时兜底检索技能市场 / 社区 / 开源 / 搜索并逐步执行，解决后回写沉淀。

## 付费

- 定价：**¥9.9 / 主题**（按主题独立计费，CNY）。
- 未付费返回 HTTP 402，由调用方经 `weixinpay_pay` 代理支付后携凭证重试解锁。
- 调用前请确认 Agent 已安装微信支付能力（`weixinpay`）。

## 入口

- 主题获取：`POST /auto/theme`
- 步骤回写：`POST /auto/save`（写操作，需已付凭证）
- 原路退款：`POST /auto/refund`（付费后未交付有效步骤时，Agent 自动触发）

## 文档

- 使用说明：`SKILL.md`
- 接口契约：`references/mcp.json`、`references/auto-theme.json`、`references/auto-writeback.json`、`references/auto-pay.json`
