# 可填写 HTML 书签规范（Fillable HTML Spec）

生成模式第 5 步产出的 HTML 必须遵循本规范，才能被 `html-to-docx`（及任意 html→docx 工具）高保真转换为可打印、可填写的 Word 合同。

> 本规范与 WorkBuddy 内置 `generate-fillable-contract-html` 书签约定一致；本技能自带副本以便在所有 SKILL HUB 独立运行。若运行环境已加载该内置技能，可直接委托其生成。

---

## 字段规则（硬性要求）

- 表格内**不要**用横线当书签，用**空格**（`&nbsp;`）当书签范围。
- 书签必须换成**中文名**，且**无空格**。
- 每个字段保留稳定的英文 `data-docx-field`，并用 `data-docx-bookmark` 指定**唯一**中文书签名。
- 重复业务字段在中文名后加 `_01`、`_02` 区分。
- 正文书签范围使用**连续下划线**；表格书签范围只使用 `&nbsp;`。
- 不得出现：正文普通空格填空、只有冒号的空值、`请输入`/`待填写` 提示文案、英文书签名、表格下划线书签。

---

## 示例

**正文填空（连续下划线）**
```html
<p>甲方名称：<span data-docx-field="party_a_name" data-docx-bookmark="甲方名称">________________</span></p>
```

**表格填空（&nbsp; 提供可见空白书签范围）**
```html
<tr>
  <th>软件名称</th>
  <td><span data-docx-field="software_name" data-docx-bookmark="软件名称">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></td>
</tr>
```

**重复字段**
```html
<p>联系地址_01：<span data-docx-field="address_01" data-docx-bookmark="联系地址_01">________________</span></p>
<p>联系地址_02：<span data-docx-field="address_02" data-docx-bookmark="联系地址_02">________________</span></p>
```

---

## 输出要求

- 输出完整 HTML5 文档，含 `html` / `head` / `style` / `body`。
- `style` 内用 CSS 控制中文合同排版（宋体/仿宋、A4 边距、标题居中、条款编号）。
- 书签范围长度适中（下划线约 16 字符宽，表格 `&nbsp;` 约 8 个），既可见又不过长。
- 合同末尾含「甲方（签章）」「乙方（签章）」「签订日期」签署栏，均为书签。

---

## 自检清单（生成后必过）

- [ ] 每个字段同时含英文 `data-docx-field` 与唯一中文 `data-docx-bookmark`。
- [ ] 正文书签用连续下划线；表格书签只用 `&nbsp;`。
- [ ] 中文书签名无空格；重复字段用 `_01`、`_02` 区分。
- [ ] 不含提示性占位文案、正文普通空格填空或表格下划线书签。
- [ ] 无广告法极限词（见 `compliance-checklist.md`）。
- [ ] 所有待填项已汇总进「待填写清单」。

---

## 转换方式

- **环境具备内置技能**：调用 `generate-fillable-contract-html` 校验/生成书签 HTML，再用 `html-to-docx` 转 `.docx` 交付。
- **环境不具备**：直接交付本 HTML，提示用户用任意「HTML 转 Word」工具打开即得可填写文档；或说明可安装 `html-to-docx` 技能后转换。
