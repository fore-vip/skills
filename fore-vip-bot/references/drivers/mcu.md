# 驱动模板：树莓派 / Arduino / ESP32（串口 / BLE）

适用：创客硬件——继电器、舵机、步进、摄像头模块、传感器板，挂在本机串口或 BLE。
通信方式：串口（USB/UART）或 BLE GATT；中控经宿主环境工具（如 `pyserial` / `bleak`）收发。

## 连接信息（用户在 config.json 填）

```json
{
  "name": "esp32-serial",
  "type": "serial",
  "config": {
    "port": "/dev/cu.usbserial-0001",
    "baud": 115200
  }
}
```

BLE 设备把 `type` 改为 `ble`，`config` 填 `mac` 或 `name`。

## 帧格式约定（建议，MCU 固件需配合）

```
中控→MCU:  <CMD>,<PROP>,<VAL>\n    例: SET,POWER,1\n   /  READ,MOISTURE\n
MCU→中控:  <PROP>,<VAL>,<TS>\n       例: MOISTURE,42,2026-08-24T02:00:00\n
```
MCU 收到 `SET` 执行动作，收到 `READ` 回当前值。

## 指令映射

| 中控指令 | 串口/BLE 写出 |
|----------|---------------|
| `{act: discover}` | 发 `LIST\n`，MCU 回设备清单（或中控读已注册表） |
| `{act: set, id, prop, val}` | `SET,<prop>,<val>\n` |
| `{act: read, id, prop}` | `READ,<prop>\n` → 等回包 |
| `{act: action, id, prop: capture}` | `ACTION,CAPTURE\n`（摄像头类，MCU 触发拍照存卡/回传） |

## 状态回传

按帧格式解析 `PROP,VAL,TS`，转 `{val, unit, ts}`。读超时（默认 2s）报无响应。

## 注意

- 多 MCU 挂同一串口时，用 `id` 前缀区分（固件侧做路由）。
- BLE 需先配对/连接，中控在 discover 阶段建连并缓存。
- 舵机/继电器类无"状态回读"的，set 后回报"指令已发"，不保证物理到位（建议加回执固件）。
