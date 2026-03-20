---
name: activity-create
description: 创建 前凌智选线下活动。使用此技能当用户需要创建活动时，包括活动信息设置、时间地点配置、门票价格等。
version: 1.0.0
---

## 技能说明

此技能帮助创建 前凌智选 (fore.vip) 平台的线下活动。通过 MCP 云函数实现服务端数据持久化。

---

## 使用场景

- 用户要创建新的线下活动
- 需要设置活动时间、地点、门票等信息
- 关联已有的 AI 机器人 (kl 集合)

---

## 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `kid` | string | 关联的机器人 ID (kl._id) | `"kl_abc123"` |
| `content` | string | 活动介绍内容 (至少 2 字符) | `"周末 AI 体验活动"` |
| `start_time` | number | 开始时间戳 (毫秒) | `1711008000000` |
| `end_time` | number | 结束时间戳 (毫秒) | `1711094400000` |

## 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `address` | string | - | 活动地址文本 |
| `location` | object | - | 经纬坐标 `{type:"Point",coordinates:[lng,lat]}` |
| `range` | number | `0` | 门票金额 (分，如 9900=99 元) |
| `pay` | boolean | `false` | 是否支付可见 |
| `url` | string | - | 外部链接 |
| `wx` | string | - | 联系方式 (微信) |
| `pic` | array | - | 图片数组 `[{url:"..."}]` |

---

## 处理流程

### 1. 收集信息

向用户询问以下信息（如未提供）：

```
1. 关联哪个 AI 机器人？(需要 kid 或机器人名称)
2. 活动介绍内容是什么？
3. 活动开始和结束时间？
4. 活动地点在哪里？(可选)
5. 是否需要门票？(可选)
```

### 2. 验证参数

```javascript
// 验证规则
- kid: 必需，字符串
- content: 必需，长度 >= 2
- start_time: 必需，数字，必须是未来时间
- end_time: 必需，数字，必须晚于 start_time
- range: 可选，数字，>= 0
```

### 3. 调用云函数

```javascript
const mcp = uniCloud.importObject('mcp')

const res = await mcp.createAct({
  token: uni.getStorageSync('token'),
  kid: "kl_xxx",
  content: "活动介绍",
  start_time: 1711008000000,
  end_time: 1711094400000,
  address: "北京市朝阳区 xxx",
  location: { type: "Point", coordinates: [116.4, 39.9] },
  range: 9900,
  pay: true
})

// 返回结果
// { id: "act_xxx", created: true, kid, content }
```

### 4. 处理结果

**成功**:
```javascript
uni.showToast({ title: '创建成功', icon: 'success' })
uni.navigateTo({ url: '/ai/st?id=' + res.id })
```

**失败**:
```javascript
uni.showToast({ title: e.message, icon: 'none' })
// 根据错误提示用户重新输入
```

---

## 错误处理

| 错误信息 | 处理建议 |
|----------|----------|
| `用户未登录` | 引导用户先登录 |
| `请指定关联的机器人` | 询问 kid 或帮用户查找机器人 |
| `活动介绍至少 2 个字符` | 请用户完善活动描述 |
| `开始时间必须早于结束时间` | 请用户检查时间设置 |
| `机器人不存在` | 确认 kid 是否正确 |
| `只能为自己的机器人创建活动` | 提示权限问题 |

---

## 示例对话

### 示例 1: 完整流程

**用户**: 我想创建一个周末 AI 体验活动

**AI**: 好的！我来帮你创建活动。请问：
1. 这个活动关联哪个 AI 机器人？(提供机器人 ID 或名称)
2. 活动的具体介绍内容是什么？
3. 活动什么时候开始和结束？
4. 活动地点在哪里？
5. 是否需要设置门票？

**用户**: 关联我的聊天机器人，内容是"与 AI 面对面交流"，周六下午 2 点到 6 点，在北京三里屯，免费

**AI**: 好的，我来为你创建活动...

```javascript
// 调用云函数
const res = await mcp.createAct({
  token,
  kid: "kl_user_bot_123",  // 先查询用户的机器人
  content: "与 AI 面对面交流",
  start_time: 1711094400000,  // 周六 14:00
  end_time: 1711108800000,    // 周六 18:00
  address: "北京三里屯",
  range: 0,
  pay: false
})
```

**AI**: ✅ 活动创建成功！[点击查看活动详情](/ai/st?id=act_xxx)

---

### 示例 2: 带门票的活动

**用户**: 帮我为机器人创建个付费活动，门票 99 元

**AI**: 好的，请问：
1. 是哪个机器人？
2. 活动内容和时间？
3. 活动地点？

**用户**: 客服机器人，"VIP 用户见面会"，下周日全天，上海静安寺

**AI**: 
```javascript
const res = await mcp.createAct({
  token,
  kid: "kl_cs_bot_456",
  content: "VIP 用户见面会",
  start_time: 1711872000000,  // 下周日 00:00
  end_time: 1711958400000,    // 下周日 23:59
  address: "上海静安寺",
  range: 9900,  // 99 元 = 9900 分
  pay: true
})
```

---

## 相关云函数

MCP 云函数提供以下活动相关方法：

| 方法 | 说明 | 参数 |
|------|------|------|
| `createAct` | 创建新活动 | `kid, content, start_time, end_time, ...` |
| `updateAct` | 更新活动 | `id, data` |
| `deleteAct` | 删除活动 | `id` |
| `listActs` | 获取活动列表 | `kid, limit` |
| `getAct` | 获取活动详情 | `id` |

---

## 注意事项

1. **时间格式**: 必须使用毫秒时间戳 (Date.now())
2. **金额单位**: range 使用分为单位 (99 元 = 9900)
3. **坐标格式**: location 使用 GeoJSON 格式 `{type:"Point",coordinates:[经度，纬度]}`
4. **权限控制**: 只能操作自己创建的活动
5. **图片上传**: pic 数组需先通过 uni-file-picker 上传获取 URL

---

## 代码片段

### 查询用户的机器人

```javascript
const db = uniCloud.database()
const bots = await db.collection('kl')
  .where({ user: auth.uid })
  .field('_id,name')
  .get()
```

### 时间选择器转换

```javascript
// uni-datetime-picker 返回的时间字符串转时间戳
const startTime = new Date(dateTimeString).getTime()
```

### 位置选择

```javascript
uni.chooseLocation({
  success: (res) => {
    location = {
      type: "Point",
      coordinates: [res.longitude, res.latitude]
    }
    address = res.address
  }
})
```

---

**版本**: 1.0.0  
**最后更新**: 2026-03-20  
**服务端**: MCP 云函数 (`uniCloud-aliyun/cloudfunctions/mcp/index.obj.js`)
