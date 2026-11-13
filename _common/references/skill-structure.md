# SKILL 目录、元数据与引用规范

> 来源：`_common/references/skill-structure.md @ 1.0.0`
> 用于新建技能、补齐 frontmatter、发布前结构自检。

## 一、目录基线

```
<技能>/
├── SKILL.md          主文件：定位、流程、完成标准、参考资料区
├── references/       文档（单层，不放二级目录）
├── templates/        模板与骨架
├── scripts/          可执行脚本
├── examples/         可跑样例
└── _icon.png         技能头像
```

| 约束 | 说明 |
|---|---|
| 单层子目录 | 开放平台不识别 `references/xxx/` 这类二级层；文档摊平放 `references/`，模板放 `templates/` |
| 安装目录只读 | 配置、注册表、用户自定义资产落用户目录，平台升级会覆盖安装目录 |
| 运行时数据不入库 | 配置与产物不进技能包；打包产物（zip）本地生成、不提交 |
| 凭证不入库 | 平台 Token 只在命令行传入 |

## 二、frontmatter 字段

| 字段 | 要求 | 备注 |
|---|---|---|
| `name` | 与目录名对齐 | 已发布标识改名会错配，改前确认 |
| `description` | 触发条件 + 能力 + 边界 | 长文本含半角「冒号+空格」必须双引号包裹 |
| `description_zh` / `description_en` | 开放平台必填 | `_zh` 是简短介绍，不是 `description` 的复制；英文同理 |
| `version` | `x.y.z` | 递进走第三位 PATCH，不擅自升 MINOR / MAJOR |
| `author` | 必填 | 组织级统一取值 |
| `slug` + `displayName` | 上架平台必填 | `displayName` 用驼峰；发布前跑 `skillhub publish <dir> --dry-run --json` |

可选增强：`display_name` / `display_name_en`、`category`、`owner`、`agent_created`、`triggers`（十条左右触发词）。

## 三、YAML 四个已踩坑

1. 长文本裸写遇半角「冒号+空格」会炸解析 → 用双引号包裹整个值。
2. `description: |` 块标量的插入点要退到 frontmatter 末尾，别插在中间。
3. BOM 与行尾符原样回填；改完立刻 `git diff --numstat` 核对，数量级接近总行数即被整篇改写。
4. 批量补齐后必须 `yaml.safe_load` 严格复验，不做「看起来对」的字符串判断。

## 四、资源引用语法

| 场景 | 写法 |
|---|---|
| 正文引用文档 | `@references/xxx.md` |
| 正文引用脚本 | `@scripts/xxx.py` |
| 命令行调用 | `python3 scripts/xxx.py`（代码块内保持相对路径，不加 `@`） |
| 参考资料区 | SKILL.md 末尾汇总本次用到的全部文档，避免孤儿引用 |

一份文档若在正文散落引用却没进「参考资料」区，等同没有登记。新增技能时同步核对三个位置：目录、`package.json` 的 `skills` 数组、`files` 白名单。

## 五、版本与发布

- 版本递进 `1.0.1 → 1.0.2`；迁入技能按仓库现状口径统一，不另起血统号。
- 发布顺序：本地跑校验 → dry-run 预检 → 明确指令后正式发布。
- 中英 README 结构保持一致（标题、代码块、表格行、分隔线计数），改一份立即同步另一份再提交。
- 只分发 `SKILL.md` 的渠道，要在正文写「脚本不可用时的等价生成规范」，保证双渠道产物一致。

## 六、自检清单

1. `references/` 是否单层、文件是否都在「参考资料」区登记？
2. 五必填字段齐全，`yaml.safe_load` 通过？
3. 版本号是否与本轮改动匹配，是否只动了 PATCH？
4. 有没有凭证、内部路径、绝对路径混进公开文件？
5. `skillhub publish --dry-run --json` 是否通过？
