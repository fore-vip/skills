# Changelog v0.0.9 (2026-03-30)

## 🎯 技能重构

### 主要变更

将原有的 `product` 技能（批量推送）拆分为两个独立技能，明确职责分工：

#### 1. ✅ 新增 `product-create` 技能 (v1.0.0)

**用途**: 单个产品创建，带自动重名检测

**特点**:
- ✅ 专注于单个产品发布
- ✅ 自动调用 `query_kl` 检查产品名称是否存在
- ✅ 避免重复创建
- ✅ 适合精确发布场景

**工具**:
- `query_kl` - 重名检测
- `create_kl` - 创建产品

**工作流程**:
```
外部来源 → 查重 (query_kl) → 确认 → 发布 (create_kl)
```

**使用场景**:
- 发布单个产品
- 需要保证不重复
- 用户明确指定的产品

---

#### 2. ✅ 升级 `product-auto` 技能 (v2.0.0)

**用途**: 批量推送多个产品，不查重

**特点**:
- ✅ 专注于批量创建
- ✅ 移除了 `query_kl` 工具
- ✅ 移除了重名检测逻辑
- ✅ 更高的批量处理效率

**工具**:
- `create_kl` - 批量创建产品（仅此工具）

**工作流程**:
```
外部来源 → 批量发布 (create_kl) → 汇总结果
```

**使用场景**:
- 批量导入产品（5-20 个）
- 已在外部处理过查重
- 快速推送产品列表

---

## 📊 技能对比

| 功能 | `product-create` (新) | `product` (升级) |
|------|----------------------|------------------|
| **用途** | 单个创建 | 批量推送 |
| **重名检测** | ✅ 自动检测 | ❌ 不检测 |
| **query_kl 工具** | ✅ 使用 | ❌ 移除 |
| **批量大小** | 1 个产品 | 5-20 个产品 |
| **发布效率** | 精确、谨慎 | 快速、批量 |
| **适用场景** | 精确发布 | 批量导入 |

---

## 📝 文件变更清单

### 新增文件

```
product-create/
├── SKILL.md          (新) - 英文版技能文档
└── SKILL_cn.md       (新) - 中文版技能文档
```

### 修改文件

```
product-auto/
├── SKILL.md          (升级) - 改为批量推送技能
└── SKILL_cn.md       (升级) - 改为批量推送技能

DOCUMENTATION.md      (更新) - 添加新技能说明
README.md             (更新) - 更新技能列表
README_cn.md          (更新) - 更新技能列表
CHANGELOG_v0.0.9.md   (新增) - 版本变更记录
```

---

## 🔧 迁移指南

### 原 `product-auto` 技能用户

**如果你之前使用 `product-auto` 技能发布单个产品**:
- ✅ 迁移到 `product-create` 技能
- ✅ 自动享受重名检测功能

**如果你需要批量发布产品**:
- ✅ 继续使用 `product-auto` 技能（已升级为批量推送）
- ✅ 注意：不再自动查重，需在外部处理

---

## ⚠️ 重要说明

### 重名检测逻辑

**`product-create` 技能**:
```javascript
// 自动查重
const existing = await query_kl({ name: productName, limit: 1 });
if (existing.data.length > 0) {
  return { skipped: true, existing: existing.data[0] };
}
// 继续创建
```

**`product-auto` 技能**:
```javascript
// 直接创建，不查重
const result = await create_kl(product, openKey);
```

### 内容来源规则

**两个技能都遵守**:
- ✅ 内容必须来自外部来源（AI、搜索、GitHub 等）
- ❌ 禁止从 `query_kl` 获取内容（避免循环依赖）

---

## 📖 文档链接

- [product-create 技能文档](product-create/SKILL.md)
- [product 技能文档](product-auto/SKILL.md)
- [完整文档索引](DOCUMENTATION.md)

---

## 🚀 使用示例

### product-create (单个 + 查重)

```bash
# 使用场景：发布单个产品
用户："帮我发布一个 Cursor AI 编辑器"

Agent:
1. 🔍 检查名称 "Cursor" 是否已存在
2. 如不存在 → 显示预览
3. 用户确认 → 发布
4. ✅ 发布成功
```

### product-auto (批量推送)

```bash
# 使用场景：批量发布 GitHub Trending Top 10
用户："批量发布 GitHub 热门项目"

Agent:
1. 获取 GitHub trending Top 10
2. 批量调用 create_kl (10 次)
3. ✅ 批量推送完成 (10/10)
```

---

**版本**: v0.0.9  
**日期**: 2026-03-30  
**维护者**: wise · 严谨专业版
