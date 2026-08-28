# 购物超省 · 平台来源与配置规范

本文件说明「购物超省」需要接入的购物 / 导购 / 联盟接口来源，如何配置密钥并保持持久化，以及
`providers.json` 的完整结构。脚本 `scripts/shopping_saver.py` 只认这个配置，不理解任何具体平台。

> 任务硬要求：**至少配置 3 个来源（3 端接口）**，且用户在可获取的接口端配置密钥与访问方式并持久化。

---

## 1. 配置方式（持久化）

配置文件的查找顺序（命中第一个即止）：

1. `--config <路径>` 显式指定
2. 环境变量 `SHOPPING_SAVER_CONFIG`
3. `~/.workbuddy/fore-vip-shopping-saver/providers.json`（推荐：用户级，自动持久化）
4. `<skill>/config/providers.json`（随仓库，需自行 gitignore）

**密钥安全：** 不要把密钥写进会提交到 Git 的 `providers.json`。两种方式二选一：

- **环境变量（推荐）：** 在配置里写 `"apikey": "${JUTUIKE_APIKEY}"`，实际值来自 `export JUTUIKE_APIKEY=xxx`。
- **本地 secrets 段：** 把真实值写在用户级 `~/.workbuddy/.../providers.json` 的 `secrets` 段（该目录已被仓库 .gitignore 忽略）。

`references/providers.example.json` 是可复制的模板（3 端来源已全部启用且为 key-based，开箱即用）。

---

## 2. providers.json 结构

```jsonc
{
  "secrets": { "ANY_KEY": "明文（建议留空，改走环境变量）" },
  "providers": [
    {
      "id": "jutuike",                 // 唯一标识
      "name": "聚推客",                // 展示用来源名（会显示在卡片角标）
      "enabled": true,                 // false 则跳过
      "adapter": "generic",            // generic | custom:<相对路径>.py
      "request": {                     // generic 适配器使用
        "method": "GET",               // GET | POST
        "url": "https://...",
        "query":  { "apikey": "${ENV}", "keyword": "{keyword}", "page": 1 },
        "headers": { "Authorization": "Bearer ${TOKEN}" },
        "body":   { }                  // 仅 POST 使用
      },
      "response": {
        "items_path": "data",          // 响应中商品数组的 JSON 路径（点/方括号）
        "fields": {                    // 输出字段 → 商品对象内的路径
          "title": "title",
          "image": "img",
          "sku_images": "sku_imgs",
          "price": "price",
          "coupon_amount": "coupon_price",
          "coupon_url": "coupon_url",
          "score": "score",
          "product_url": "item_url"
        }
      }
    }
  ]
}
```

**模板变量（request 段内）：**

- `{keyword}`：运行时替换为用户输入的商品名。
- `${ENV}`：替换为 `secrets` 段或同名环境变量的值。

**`fields` 固定输出键（脚本据此渲染，务必映射到这些键）：**

| 输出键 | 含义 | 缺省 |
|--------|------|------|
| `title` | 商品标题 | — |
| `image` | 封面图 URL | 缺失→占位 |
| `sku_images` | SKU 图数组 | `[]` |
| `price` | 原价（数字） | `None` |
| `coupon_amount` | 优惠券面额（数字） | `None` |
| `coupon_url` | 领券地址 | `None` |
| `score` | 质量评分（数字，用于排序） | `0` |
| `product_url` | 商品购买/落地链接 | `None` |

---

## 3. 推荐的可达来源（任选 ≥3）

### A. 即插即用（key-based，无需签名）—— 首选

| 来源 | 注册/开放平台 | 覆盖范围 | 鉴权 |
|------|---------------|----------|------|
| **聚推客 Jutuike** | https://www.jutuike.com/ | 京东 / 淘宝 / 拼多多 / 唯品会 / 饿了么 | `apikey` 参数 |
| **折淘客 Zhetaoke** | https://www.zhetaoke.com/ | 淘宝 / 天猫（免费淘客 API） | `sid` + `appkey` + 淘宝联盟 `pid` |
| **大淘客 / 选单网 / 好单库**（任选其一作第三端） | 各官网开放平台 | 淘宝 / 天猫 | 多数 key-based，个别需 sign |

> 这三家足以满足「≥3 端」且无需实现签名。模板已默认启用 聚推客 + 折淘客 + 一个导购API示例占位。

### B. 签名类开放平台（需 custom 适配器）

| 来源 | 注册/开放平台 | 签名方式 |
|------|---------------|----------|
| **京东联盟** | https://union.jd.com/ （开放平台 api.jd.com） | MD5(appSecret + 排序参数字符串 + appSecret) 转大写 |
| **淘宝联盟 / 阿里妈妈** | https://pub.alimama.com/ （淘宝开放平台） | MD5(appSecret + 排序参数字符串 + appSecret) 转大写 |
| **拼多多多多进宝** | https://jinbao.pinduoduo.com/ （拼多多开放平台） | MD5(排序 key=value 拼接 + client_secret) 转大写 |
| **唯品会联盟** | https://union.vip.com/ | MD5 + appKey/appSecret |

接入方式：写一个 `adapters/<name>.py`，导出 `request(keyword, provider, ctx) -> dict`（返回解析后的响应 JSON，内部自行处理签名与"响应里再包一层 JSON 字符串"的情况），在 provider 里设 `"adapter": "custom:adapters/<name>.py"`。响应解析（items_path / fields）仍走通用逻辑。

**通用 MD5 签名片段（适配京东/淘宝系）：**

```python
import hashlib, time, json, urllib.parse, urllib.request

def md5_sign(params: dict, secret: str) -> str:
    s = secret + "".join(f"{k}{params[k]}" for k in sorted(params)) + secret
    return hashlib.md5(s.encode()).hexdigest().upper()

def request(keyword, provider, ctx):
    secret = ctx["secrets"].get("JD_SECRET") or os.environ["JD_SECRET"]
    params = {
        "method": "jd.union.open.goods.query",
        "app_key": ctx["secrets"].get("JD_APPKEY"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json", "v": "1.0", "sign_method": "md5",
        "param_json": json.dumps({"goodsReqDTO": {"keyword": keyword, "pageIndex": 1, "pageSize": 20}}),
    }
    params["sign"] = md5_sign(params, secret)
    url = "https://api.jd.com/routerjson?" + urllib.parse.urlencode(params)
    # ...urllib 请求并把"结果再包一层 JSON 字符串"的字段解析成 dict 后返回
```

> 注意：各联盟的 **方法名 / 参数名 / 返回字段路径** 会随版本变动，以上为通用范式，落地时以对应平台最新文档为准。

---

## 4. 排序规则

脚本按以下模式排序（`--sort`）：

- `score`（默认）：质量评分降序 → 券后价升序
- `price`：原价升序
- `coupon`：券后价升序

券后价 = `price - coupon_amount`（任一项缺失则回退原价）。

---

## 5. 图片与占位

- `image` 缺失或为空 → 直接使用内置占位图（data-URI SVG，无外链）。
- 存在但可能跨域防盗链 → `<img>` 加 `referrerpolicy="no-referrer"` 与 `onerror` 兜底占位，
  避免裂图。SKU 图当前仅作为数据保留，卡片默认展示封面图。
