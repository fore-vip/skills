# 四级选路 · 工具路由

链路固定为 **T1 本地已有工具 ＞ T2 模型基本能力 ＞ T3 社区工具 ＞ T4 实时实现**。命中即停，跳级必须写明理由，每次降级都要让用户知道。

## 一、T1 本地已有工具

### 1.1 先探测，别假设

每条转换任务开始前跑一次本机能力探测，输出「有 / 无」清单，再决定路由：

```bash
for c in ffmpeg sips textutil cwebp cupsfilter pandoc libreoffice soffice magick convert pdftotext pdfinfo qpdf gs wkhtmltopdf calibre python3 node; do
  p=$(command -v "$c" 2>/dev/null); [ -n "$p" ] && echo "OK   $c -> $p" || echo "MISS $c"; done
```

本机当前实测（2026-11-15，macOS）：**有** `ffmpeg` / `sips` / `textutil` / `cwebp` / `cupsfilter` / `python3` / `node`；**无** `pandoc` / `libreoffice` / `magick` / `pdftotext` / `gs` / `qpdf` / `calibre`。此清单只作初判，**每次实测为准**，换了机器或环境就会变。

### 1.2 WorkBuddy 内置能力路由（按当前环境实际可用项判断）

| 需求 | 优先路由到的内置能力 | 说明 |
|---|---|---|
| 读 PDF、抽文字 / 表格 / 图片 | `workbuddy-pdf` / `pdf` / `pdfkit-py` | 只读，产出内容后再写目标格式 |
| 本地 Office 文件读写（doc/xls/ppt） | `workbuddy-local-office-edit` / `workbuddy-office-routing` | 能直接打开编辑，优先于重新生成 |
| Word 生成与排版 | `workbuddy-docx` / `tdoc-orchestrator` / `doc-formatter` | HTML → DOCX 走 `doc-converter` |
| PPT 生成与改写 | `workbuddy-pptx` | 演示类目标格式 |
| 表格读写、清洗、透视 | `workbuddy-sheetagent` | CSV / XLSX 方向优先 |
| 思维导图 | `tencent-xmind` | 已有 .xmind 的修改必须走它 |
| 图片处理与增强 | `buddy-image-processing` | 图片族转换与修复 |
| 在线文档导入导出 | `tencent-docs` / `tencent-saas-docs` | 云文档场景，注意写操作授权 |
| 云文件取还 | `tdrive.*` / 邮件附件下载 | 共享盘写回须先确认 |

内置能力清单会随环境变化，**先确认技能是否可用再引用**，不凭记忆下命令。

### 1.3 本机 CLI 快速映射

| 格式对 | 可用工具 | 要点 |
|---|---|---|
| 音视频互转、抽音轨、视频转 GIF | `ffmpeg` | 容器与编码分开看，先 `-i` 探测流 |
| 图片互转（常见格式） | `sips`（macOS） | 支持面窄，HEIC / 色彩配置要复验 |
| PNG/JPG → WebP | `cwebp` | 有损参数按 S6 取向设定 |
| txt / rtf / html / doc 文本抽取 | `textutil`（macOS） | 只保留文字与基础结构 |
| 结构化数据互转（csv/json/yaml/xml） | Python 标准库 | 归 T2，零依赖 |
| 压缩包解包 / 重打包 | Python `zipfile` / `tarfile` | 归 T2 |

## 二、T2 模型基本能力

判定条件：源与目标都是**纯文本或结构化数据**，转换不依赖二进制解析器。

覆盖范围：Markdown / 纯文本 / CSV / JSON / YAML / XML / HTML 片段的互转、编码与行尾符转换、字段映射与重命名规则、批量命名、简单表格重排、配置格式翻译。

做法：直接读取内容并写出目标格式；大文件分块处理，不整篇塞进上下文。零第三方依赖，不装包、不联网。

**边界**：涉及二进制容器（docx/xlsx/pptx/pdf/图片/音视频）时不算 T2，别用「看起来是文本」当理由硬做。

## 三、T3 社区工具

### 3.1 检索式模板（实时执行，不凭记忆推荐）

```
"<source fmt> to <target fmt> converter open source CLI 2026"
"<tool name> github releases last commit maintenance 2026"
"<tool name> <format> read write support official documentation"
```

### 3.2 候选工具（检索结果，2026-11-15 汇总；用前必须逐项验证）

| 工具 | 适用方向 | 已验证的注意点 |
|---|---|---|
| Pandoc | 标记文本互转、标记文本 → Office、Office → 标记文本 | 中间表示不保留源格式全部特性；写 PDF 需额外 PDF 引擎；旧版二进制 Office 读不了 |
| LibreOffice headless | Office → PDF、Office ↔ Office、旧版 `.doc/.ppt/.xls` | 保版式优于 Pandoc；单实例并发会静默失败；输出文件名由它自己定 |
| ImageMagick | 图片互转、图片 → PDF | 读 PDF 需 Ghostscript；读 / 写支持方向不一致；策略文件可能拦格式 |
| FFmpeg | 音视频互转、mp4 → GIF | 编码器支持取决于构建；有损源转码不会恢复已丢弃信息 |
| MarkItDown / Docling | PDF / Office / 图片 → Markdown（喂模型场景） | 图片、备注、链接保留策略各异，需实测 |
| Calibre | 电子书格式互转 | 文本输出默认丢链接，需显式开启保留选项 |
| Sharp / 语言库 | 图片批处理、HTML → Markdown | 属库而非 CLI，通常落到 T4 脚本 |

### 3.3 验证四项（缺一不采用）

1. **维护活跃**：近期有 release / commit，不是多年未动的归档项目。
2. **许可明确**：可本地运行，无隐性收费或强制账号。
3. **读写方向确实支持**：能打开某格式 ≠ 能写出该格式；查官方文档的 format 表，必要时跑最小样例。
4. **可离线本地运行**：不把文件内容上传到第三方服务。

### 3.4 安装前告知（用户同意才装）

说明工具名、用途、来源、完整安装命令、是否联网、是否改动系统环境、是否收费、预计影响范围。含敏感内容的文件不走在线服务；用户不同意安装时降到 T4 或改选目标格式，不擅自执行。

## 四、T4 实时实现

判定：前三级都不覆盖、格式私有、需要定制字段映射或多步中转。

- 脚本落系统临时目录或用户指定的输出目录，**不写进技能安装目录**（平台升级会覆盖）。
- 语言优先级：Python / Node 标准库 ＞ 已装依赖 ＞ 新装依赖（需同意）。
- 一次只解决当前格式对，不造通用框架；脚本内写清输入输出、失败退出码、复验方式。
- 多步中转示例：Markdown → PDF 的 PDF 引擎不可用时，走 `md → docx → pdf`，并在回执里标明中转链路。
- 实时实现也跑不出结果时，如实说明不可行，给替代目标格式或人工路径，不硬凑一个「看起来像」的产物。

## 五、降级规则

| 情况 | 下一级 | 必须告知用户 |
|---|---|---|
| T1 工具未安装或不支持该方向 | T2（纯文本）/ T3 | 缺哪个工具、卡在哪个方向 |
| T1 转换后复验不达标 | T3 或改目标格式 | 具体哪项校验没过 |
| T2 遇到二进制容器 | T3 | 为什么模型基本能力不适用 |
| T3 需装依赖但用户不同意 | T4 / 改目标格式 | 不安装会带来什么限制 |
| T4 也做不到 | 停止 | 不可行原因 + 可替代方案 |

**禁止静默降级**：换工具、换目标格式、换方案都要在对话里说明原因。

## 六、已踩过的坑

1. **扩展名 ≠ 真实格式**：`.csv` 可能是 XLSX 容器，`.html` 可能是纯文本。批量前用 `file` 全量过一遍。
2. **CRLF 被改写**：部分编辑工具会把 CRLF 整篇转 LF，造成几百行假 diff；处理文本产物前后各探一次行尾符。
3. **BOM**：写出的 CSV 可能带 UTF-8 BOM（`ef bb bf`），交付前查首 3 字节。
4. **LibreOffice 输出名不听话**：`--outdir` 下按输入 stem 命名，需再重命名对齐 S3 约定。
5. **单实例冲突**：`libreoffice --headless` 并发会有一个静默什么都不做，批量一律串行。
6. **Pandoc 的 PDF 引擎**：需 `pdflatex` / `xelatex` / `typst` / `weasyprint` 之一；生僻 Unicode 优先 `xelatex`；引擎报错可改走 `docx` 中转。
7. **容器 ≠ 编码**：同为 `.mp4` 内部流可能完全不同，选编码器前先探测。
8. **有损源不回血**：JPG / MP3 / 有损 MP4 转成无损容器只是换壳，回执里不得写「无损」。
9. **macOS shell 差异**：BSD `grep` 不支持 `\|`，用 `grep -E`；`sed -i ''` 会失败，用 `perl -ni -e`。
10. **大批量前先测代表文件**：带表格、图片、特殊字符的那份最能暴露问题。
