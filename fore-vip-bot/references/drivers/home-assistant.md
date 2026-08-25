# 驱动模板：Home Assistant / MCP 网关

适用：已部署 Home Assistant 并开启 MCP 插件（或任意暴露 MCP 工具的智能家居网关）。
通信方式：MCP（中控作为 MCP 客户端调用网关工具）。

## 连接信息（用户在 config.json 填）

```json
{
  "name": "home-assistant",
  "type": "mcp",
  "config": {
    "mcp_url": "http://homeassistant.local:8123/mcp",
    "token_env": "HA_LONG_LIVED_TOKEN"
  }
}
```

`token_env` 指向宿主环境变量名，中控运行时读取，**不写明文**。

## 指令映射

| 中控指令 | MCP 工具调用 | 说明 |
|----------|-------------|------|
| `{act: discover}` | `list_entities` / `list_devices` | 返回所有实体 |
| `{act: set, id, prop: power, val: on}` | `call_service(domain=switch/light, service=turn_on, target=id)` | 开关 |
| `{act: set, id, prop: dim, val: 80}` | `call_service(light, service=set_brightness, brightness_pct=80)` | 调光 |
| `{act: set, id, prop: target_temp, val: 26}` | `call_service(climate, service=set_temperature, temperature=26)` | 设温 |
| `{act: set, id, prop: color, val: "#ff0000"}` | `call_service(light, service=turn_on, rgb_color=[255,0,0])` | 变色 |
| `{act: read, id, prop: moisture}` | `get_state(entity_id=id)` → 取属性 | 读状态 |
| `{act: action, id, prop: capture}` | `call_service(camera, service: snapshot)` | 摄像头抓拍 |

## 状态回传

MCP 工具返回实体 state + attributes，中控提取为 `{val, unit, ts}`。
例：`get_state(livingroom_light_01)` → `{power: on, brightness: 80, ts: "2026-08-24T02:00:00+08:00"}`。

## 注意

- HA 实体 id 即中控设备 `id`；首次 discover 后让用户把 `id` 映射成友好 `name`。
- 批量操作（`{act: batch}`）在中控层展开为多个单设备调用，逐个回报。
- 若网关不暴露 MCP 而只给 REST API，则改用 HTTP 驱动（结构同 MQTT 模板的 HTTP 段），把 `call_service` 换成 `POST /api/services/<domain>/<service>`。
