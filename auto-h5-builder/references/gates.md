# 五道闸门与实现要点

## 闸门

| # | 命令 | 挡住什么 |
|---|---|---|
| ① | `build_page.py` 内建自检 | 占位符、标签不平衡、假域名、head 三处 URL 不一致、绝对外链、口径声明缺失、区块文本重复、无后端却留可提交表单、无障碍缺失、JS 语法；不过就不写盘 |
| ② | `verify_static.py --spec x.json --page index.html [--cloud]` | 交付形态与诉求、站点地址、分享卡自洽、主题词与串台、业务事实来源、叙事顺序、CTA 与能力一致、控件一致性、无障碍、云白名单 |
| ③ | `verify_viewport.mjs --spec ... --url ... --shots <交付目录>/shots/run` | CDP 真实 390 + 1280 双视口：页内圆角 / 高度 / 字号 / 主色统一、输入框同形、零内联样式、窄屏导航可见、桌面不溢出、spec 业务断言、逐 section 截图 |
| ④ | 逐段截图目视 | 自动断言覆盖不到的观感：主题可辨、品牌统一、无重复文案、无截断溢出错位、控件同形 |
| ⑤ | `verify_delivery.py --spec x.json --dir <交付目录>` | 最终裁判：应用实体、诉求与形态一致、业务动作闭环、真实站点、事实来源、截图覆盖度；输出 `DELIVERED / DRAFT / INCOMPLETE` |

云模式 ② 加 `--cloud`。脚本返回非零退出码即失败，不要只看最后一行输出。①–④ 全绿不等于完成，只有 ⑤ 能宣布交付。

## 实现要点

- **按字段声明而非按类型打补丁**：renderer 用 `owns` 声明自己渲染了哪些字段，新增 section 类型必须同步声明，不要在 `render_sections` 里按类型加特例。
- **head 不整段跳过**：`visible_text` 剔除 `<head>` 是为了查正文口径，但 canonical / og:url / og:image / favicon 必须单独进校验清单。
- **窄屏不删入口**：导航用第二行横向滚动，不用 `display:none`；sticky header 变高后给 `.sect` 加 `scroll-margin-top`。
- **焦点态可见**：`outline:none` 配半透明阴影在浅色背景上几乎不可见，用实线描边并把宽度抽成 token。
- **表单禁用彻底**：无后端时 input 与 button 都 disabled，加 `<noscript>`；只 `preventDefault` 会让 JS 关闭时以为提交成功。
- **截图覆盖全页**：首屏 + 每个 section + 页尾，落进交付目录；手工补几张无法复现，不算验收证据。

## 运行注意

- 无头 Chrome 的 `--window-size` 会被夹到最小 500px，390 必须用 CDP `Emulation.setDeviceMetricsOverride`。
- 云 SDK 的 CDN 在本机时通时不通（`curl` 可能返回 000）；页面必须给可见失败提示，且不把本地操作说成已存云端。
- 新增 token 时若 `.ctl` 规则出现硬编码 px 或色值，静态闸门直接 FAIL，一律抽成变量。
- 脚本运行会写 `__pycache__` 污染技能包，生成器与闸门脚本均设置 `sys.dont_write_bytecode = True`。
- 长稿交付前跑一次禁用词与英文噪声词差集。
- 归档时若工作树里有他人改动，只暂存自己新增的路径。
