# 文档体系

> 本目录是自动打字项目的文档中心。`docs/analysis/` 是需求与技术语义的唯一权威来源；其他文档只负责操作指引、问题排查和版本记录。

## 文档导航

| 文档 | 职责 | 什么时候看 |
|---|---|---|
| [analysis/requirements.md](analysis/requirements.md) | 功能需求、交互流程、验收口径 | 新增功能、确认行为边界 |
| [analysis/technical-design.md](analysis/technical-design.md) | 架构、模块、API、键盘输入机制 | 修改引擎、UI 或打包方式 |
| [analysis/ui-design.md](analysis/ui-design.md) | 配色、字体、图标、布局、控件规格 | 修改界面或视觉样式 |
| [agent-reference/development.md](agent-reference/development.md) | 开发环境、编码规范、Git 工作流 | 开始开发、提交代码 |
| [agent-reference/testing.md](agent-reference/testing.md) | 测试分层、手动矩阵、回归清单 | 每次变更后、发布前 |
| [agent-reference/release.md](agent-reference/release.md) | 依赖、打包、发布与归档流程 | 发布版本、制作 exe |
| [agent-reference/troubleshooting.md](agent-reference/troubleshooting.md) | 键盘、中文、换行、环境问题的排查 | 出现异常时 |
| [history-version/README.md](history-version/README.md) | 已发布版本文档的归档规则 | 版本收尾 |
| [history-version/templates/](history-version/templates/) | 版本实现指南与测试报告模板 | 开始版本开发时 |
| [superpowers/specs/](superpowers/specs/) | 大型改造的设计规格 | 开始重大功能前 |
| [superpowers/plans/](superpowers/plans/) | 设计规格对应的实现计划 | 执行大型改造时 |
| [templates/agent-template.md](templates/agent-template.md) | Agent 定义模板 | 新建 Agent 时 |
| [../CHANGELOG.md](../CHANGELOG.md) | 版本变更记录 | 了解版本差异 |
| [../README.en.md](../README.en.md) | 英文项目说明 | 面向英文读者 |
| [../AGENTS.md](../AGENTS.md) | 智能体工作指引 | AI 协作、项目总览 |

## 三层结构

```text
docs/
├── analysis/          # 需求与设计：语义权威
├── agent-reference/   # 开发、测试、发布、排障：操作参考
├── history-version/   # 已发布版本：只读归档
└── templates/         # 可复用模板
```

### analysis

- 需求变化先改 `requirements.md`。
- 架构、API、键盘输入机制变化改 `technical-design.md`。
- 界面视觉和布局变化改 `ui-design.md`。
- 三份文档只写当前口径，不记录历史演进。

### agent-reference

- 面向开发者和 AI 的操作说明。
- 可以包含命令、检查清单和排障步骤。
- 与 `analysis/` 冲突时，以 `analysis/` 为准。

### history-version

- 版本发布后，把实现指南和测试报告移入这里。
- 归档文件不再修改；发现错误时在新版本文档中修正。
- 模板位于 `history-version/templates/`。

## 维护规则

1. **同提交更新**：代码变更和受影响的文档放在同一个提交中。
2. **单一事实来源**：需求语义只看 `analysis/requirements.md`；技术机制只看 `analysis/technical-design.md`；UI 规格只看 `analysis/ui-design.md`。
3. **不写演进注释**：活文档只描述当前状态，不写“本版新增”“本次修改”。
4. **链接可点击**：使用相对路径；重命名文件后全仓搜索旧路径。
5. **版本可追溯**：每个公开版本更新 `CHANGELOG.md`，并按 `history-version/README.md` 归档。
6. **不提交产物**：`build/`、`dist/`、`__pycache__/` 和日志不进入仓库。

## 文档检查

提交前至少执行：

```bash
git diff --check
```

并确认：

- [ ] 新增或修改的链接可以打开
- [ ] 文档中的命令与当前目录结构一致
- [ ] `AGENTS.md` 和 `README.md` 的文档入口已同步
- [ ] 版本变更已写入 `CHANGELOG.md`
- [ ] 已发布的版本文档位于 `history-version/`，开发中的文档不在归档目录
