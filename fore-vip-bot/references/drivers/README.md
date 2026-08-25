# 驱动机制总览 · Driver Framework

`fore-vip-bot` 中控本身不含任何设备通信代码。它定义**设备抽象层 + 指令范式**，真正"怎么发指令"由**驱动（driver）**决定。

## 驱动是什么

驱动 = 把中控的**统一指令**翻译为**某类设备通信协议具体消息**的规则说明。一份驱动模板描述：

- 适用设备类型（light/switch/sensor/mcu...）
- 通信方式（MCP / HTTP / MQTT / BLE / 串口 / 系统 API）
- 连接信息（端点/凭证，由用户填）
- 指令映射表（中控指令 → 协议消息）
- 状态回传格式

## 驱动来源优先级

1. **已连 MCP 服务**（Home Assistant MCP、用户自建网关 MCP）→ 直接用 MCP 工具，无需手写驱动。
2. **用户本地服务/API**（HTTP/WebSocket/MQTT）→ 用户在 config 里填地址+凭证。
3. **`references/drivers/` 模板** → 用户照模板填连接信息启用。
4. **系统 API/CLI** → 本机外设（音量/屏幕/电源）走宿主系统能力。

## 驱动文件约定

| 文件 | 作用 |
|------|------|
| `config.example.json` | 用户驱动配置样例，复制为 `config.json` 填真实值 |
| `home-assistant.md` | HA / MCP 网关驱动模板 |
| `mqtt.md` | 直连 MQTT broker 驱动模板 |
| `mcu.md` | 树莓派/Arduino/ESP32 串口/BLE 驱动模板 |
| `system.md` | 本机外设系统 API 驱动模板 |

## 编写新驱动的步骤

1. 确定设备通信方式（上面 4 类选最近的一个作基础）。
2. 复制对应模板，改名为 `my-driver.md`。
3. 填连接信息占位符（`<HA_URL>` / `<MQTT_BROKER>` 等）。
4. 补全指令映射表（中控指令 → 实际消息）。
5. 在中控设备注册表里把设备的 `driver` 指向你的驱动。
6. 测试一条 read + 一条 set 指令，确认状态回传正常。

> 驱动不含密钥明文。凭证一律走用户 `config.json`（不入库、不进 SKILL 分发包），或走宿主环境的环境变量 / 密钥管理。
