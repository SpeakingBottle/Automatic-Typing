# 自动打字 · AGENTS.md

> 智能体工作指引：项目理解 + 文档体系 + 交互协议 + 开发工作流。
> `CLAUDE.md` 仅作为本文件的入口；需求与设计细节以 `docs/analysis/` 为准。

## ① 项目理解

**自动打字 (Automatic Typing)** 是一款 Windows 桌面工具：通过模拟真实键盘输入，把代码或文本逐字送入目标窗口，适用于禁止粘贴、只能手动输入的文本框。

- 技术栈：Python 3.10+（开发与验证环境为 3.13）+ customtkinter + Windows `SendInput` API
- 运行平台：Windows 10 / 11，无需管理员权限
- 入口：`main.py`；UI 在 `ui/`，打字引擎在 `engine/`，工具函数在 `utils/`
- 打包：PyInstaller + `build.spec`，输出 `dist/自动打字.exe`

核心输入策略：

- ASCII 字符走 `KEYEVENTF_SCANCODE` 扫描码模式；非 ASCII 字符回退到 `KEYEVENTF_UNICODE`
- `VkKeyScanExW(char, 0)` 判断字符能否映射到当前键盘布局，注意传字符本身而不是 `ord(char)`
- `\r` 必须跳过；每个 `\n` 后额外等待 `0.05s`；Enter/Tab 与跳过的缩进空白也有独立延时
- `skip_indent=True` 时跳过行首空白，依赖目标编辑器的自动缩进
- `dwExtraInfo` 使用 `ULONG_PTR`（`c_uint64` / `c_uint32`），不能用 `POINTER(c_ulong)`

详细机制见 [技术设计](docs/analysis/technical-design.md)，问题定位见 [故障排查](docs/agent-reference/troubleshooting.md)。

## ② 文档体系

| 位置 | 用途 |
|---|---|
| `docs/README.md` | 文档索引、权威来源与维护规则 |
| `docs/analysis/` | 需求、技术设计、UI 设计；业务与技术语义以这里为准 |
| `docs/agent-reference/` | 开发、测试、发布、排障等按需参考文档 |
| `docs/history-version/` | 已发布版本的实现指南与测试报告，归档后不再修改 |
| `docs/templates/` | Agent 定义模板等项目模板 |
| `AGENTS.md` / `CLAUDE.md` | 智能体工作指引 / 入口指针 |
| `CHANGELOG.md` | 版本变更记录 |

文档规则：

- 代码或行为变更时，在同一个提交中更新受影响的文档。
- `docs/analysis/` 是语义权威；其他文档与它冲突时，以 `docs/analysis/` 为准。
- 活文档只写当前口径，不叠加“本版新增 / 修改”等演进注释。
- 版本开发中的文档命名为 `docs/vX.Y.Z-implementation-guide.md` 和 `docs/vX.Y.Z-test-report.md`；发布后移入 `docs/history-version/`。
- 相对链接必须可点击；修改文件名或目录后，全仓搜索旧路径。

## ③ 交互协议

- 默认使用中文交流和汇报。
- 开始开发前先阅读对应文档；涉及代码结构、交互或发布流程的改动，先说明方案再执行。
- 纯文档修正、错别字和失效链接可以直接处理。
- 批量读取文件时先用 Grep 定位，再按需读取行段，避免整读大文档。
- 测试结论必须来自实际执行；未运行的测试要明确标注“未验证”。
- 删除文件、重写 Git 历史、强制推送等不可逆操作，先说明范围并取得确认。

## ④ 开发工作流

1. **需求与设计**：需求变化更新 `docs/analysis/requirements.md`；技术方案更新 `technical-design.md`；界面变化更新 `ui-design.md`。
2. **实现**：UI 改动只涉及 `ui/`，打字逻辑只涉及 `engine/`，工具函数放在 `utils/`；遵守现有分层和命名规范。
3. **验证**：至少执行导入检查和受影响的手动测试；键盘底层问题先用 `test_sendinput.py` 隔离。完整矩阵见 [测试指南](docs/agent-reference/testing.md)。
4. **文档同步**：更新相关文档、`docs/README.md` 索引和 `CHANGELOG.md`；确认没有旧路径残留。
5. **发布**：按 [发布指南](docs/agent-reference/release.md) 打包、检查、记录版本并归档版本文档。

## ⑤ 常用命令

```bash
# 开发模式（在项目根目录执行）
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe main.py

# 或双击 start.bat

# 导入检查
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -c "import main"

# SendInput 隔离测试
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe test_sendinput.py

# 打包
pyinstaller build.spec

# 提交前检查
git diff --check
```

## ⑥ 环境信息

- Python 路径：`C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe`
- 注意：MSYS2 的 Python 3.12 可能在 PATH 前面，必须显式使用 Python 3.13 路径
- 依赖已安装在 Python 3.13 全局环境：`customtkinter==5.2.2`、`pyperclip==1.11.0`
- 项目根目录：`D:\Automatic-Typing`
