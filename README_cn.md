# MCP 技能 - 前凌智选 (fore.vip)

**版本**: 0.0.9  
**最后更新**: 2026-03-30

---

## 📦 可用技能

| 技能 | 版本 | 说明 | 工具 |
|------|------|------|------|
| **product-create** | v1.0.0 | 创建单个产品，带重名检测 | `query_kl`, `create_kl` |
| **product** | v2.0.0 | 批量推送多个产品（不查重） | `create_kl` |
| **activity-create** | v0.0.5 | 创建线下活动 | `create_activity` |

---

## 🚀 快速开始

### 1. 获取 Open Key

1. 在 [fore.vip](https://fore.vip) 注册/登录
2. 进入 **用户中心** → **API 设置**
3. 复制你的 **Open Key**

### 2. 选择技能

**单个产品（带查重）**：
```bash
使用技能：product-create
工具：query_kl + create_kl
```

**批量推送（不查重）**：
```bash
使用技能：product
工具：仅 create_kl
```

**创建活动**：
```bash
使用技能：activity-create
工具：create_activity
```

---

## 📖 文档

- [完整文档](DOCUMENTATION.md)
- [产品创建技能](product-create/SKILL_cn.md)
- [产品批量推送技能](product/SKILL_cn.md)
- [活动创建技能](activity-create/SKILL_cn.md)

---

## 🔧 MCP 接口

**基础 URL**: `https://api.fore.vip`

| 接口 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/tools/list` | GET | ❌ | 工具列表 |
| `/mcp/query_kl` | POST | ❌ | 查询产品 |
| `/mcp/create_kl` | POST | 🔐 | 创建产品 |
| `/mcp/create_activity` | POST | 🔐 | 创建活动 |

---

## 📝 版本历史

### v0.0.9 (2026-03-30)

- ✅ 拆分 `product` 技能为：
  - `product-create`（单个 + 查重）
  - `product`（仅批量推送）
- ✅ 明确技能分工
- ✅ 更新文档

### v0.0.8 (2026-03-24)

- ✅ 修复循环依赖
- ✅ 外部内容来源

---

**License**: MIT  
**联系**: forevip123 (微信)
