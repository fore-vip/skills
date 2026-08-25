# 驱动模板：直连 MQTT Broker

适用：设备/网关直接走 MQTT（米家 MQTT 桥、ESP 自制节点、Node-RED 主题、Tasmota/ESPHome 设备）。
通信方式：MQTT over TCP（中控用宿主环境的 MQTT 客户端发/收消息）。

## 连接信息（用户在 config.json 填）

```json
{
  "name": "local-mqtt",
  "type": "mqtt",
  "config": {
    "broker": "mqtt://192.168.1.50:1883",
    "username_env": "MQTT_USER",
    "password_env": "MQTT_PASS"
  }
}
```

## 主题约定（建议，用户可按设备实际改）

```
命令下发：  <base>/<device_id>/set      // payload: {"prop":"power","val":"on"}
状态上报：  <base>/<device_id>/state    // payload: {"prop":"power","val":"on","ts":...}
传感器读数：<base>/<device_id>/tele      // payload: {"prop":"moisture","val":42,"unit":"%"}
```
`<base>` 默认 `forebot`，如 `forebot/farm_soil_sensor/set`。

## 指令映射

| 中控指令 | MQTT 操作 |
|----------|-----------|
| `{act: discover}` | 订阅 `<base>/+/state` 一段时间，收集在线设备 |
| `{act: set, id, prop, val}` | `PUBLISH <base>/<id>/set` payload `{"prop","val"}` |
| `{act: read, id, prop}` | `SUBSCRIBE <base>/<id>/state` 或 `<base>/<id>/tele`，等回包 |
| `{act: batch, filter, prop, val}` | 对匹配设备逐个 `PUBLISH` |

## 状态回传

设备收到 `set` 后回 `state` 主题，中控解析为 `{val, unit, ts}`。
读操作等待 `tele`/`state` 回包，超时（默认 3s）报离线。

## 注意

- QoS 建议 ≥ 1，确保命令不丢。
- 传感器类设备通常只发 `tele` 不上报 `state`，读操作以最近一次 `tele` 为准。
- 凭证走环境变量，不在 SKILL 包内明文。
