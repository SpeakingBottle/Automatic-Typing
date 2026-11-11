# 开发指南

> 本文说明本地开发环境、启动方式、编码规范和 Git 工作流。
> 需求与设计见 [analysis](../analysis/)，测试见 [测试指南](testing.md)，打包发布见 [发布指南](release.md)。

## 开发环境

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows 10 / 11 |
| Python | 3.10+（当前开发与验证环境：3.13，路径 `C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe`） |
| 包管理 | pip |
| 虚拟环境 | 可选，当前使用全局环境 |
| 依赖 | `customtkinter>=5.2.0`、`pyperclip>=1.8.2`、`pyinstaller>=6.0.0` |

> MSYS2 的 Python 3.12 可能在 PATH 前面。为避免依赖或解释器不一致，命令中显式使用 Python 3.13 路径。

## 启动方式

### 源码运行

```bash
# 在项目根目录执行
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe main.py
```

也可以双击 `start.bat`。脚本会切换到自身所在目录后启动 `main.py`。

### SendInput 隔离测试

```bash
# 在项目根目录执行
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe test_sendinput.py
# 3 秒内切换到记事本，观察字符是否正常输入
```

## 编码规范

### Python 代码风格

- 遵循 PEP 8
- 缩进：4 个空格
- 引号：优先使用双引号 `"`
- 编码声明：需要中文时在文件头使用 `# -*- coding: utf-8 -*-`
- 类型注解：推荐使用 Python 3.10+ 语法

### 命名规范

| 类型 | 风格 | 示例 |
|---|---|---|
| 模块 / 文件 | snake_case | `text_panel.py` |
| 类 | PascalCase | `TypingEngine` |
| 函数 / 方法 | snake_case | `send_char()` |
| 变量 | snake_case | `base_delay` |
| 私有成员 | `_` 前缀 | `_thread`、`_paused` |
| 常量 | UPPER_SNAKE_CASE | `VK_SHIFT` |
| 回调方法 | `_on_` 前缀 | `_on_start()`、`_on_finished()` |

### 注释规范

- 每个 `.py` 文件开头使用 `"""..."""` 说明模块用途
- 公共方法写 docstring
- 复杂逻辑使用行内注释解释
- 注释语言：中文（面向中文开发者）

### 导入顺序

1. 标准库
2. 第三方库
3. 项目内部模块

各组之间空一行。

## Git 工作流

- 主分支：`main`
- 功能分支：`feature/<功能名>`
- 修复分支：`fix/<问题描述>`
- 提交信息使用中文，格式：`<类型>: <描述>`，例如 `feat: 添加全局热键支持`
- 提交前执行：
  - `git diff --check`
  - `python -c "import main"`（使用项目约定的 Python 3.13 路径）
  - 与改动相关的手动测试
- 不提交 `__pycache__/`、`build/`、`dist/`、虚拟环境或日志文件；这些已由 `.gitignore` 排除。

## 文档同步

修改代码时按以下对应关系更新文档：

| 变更类型 | 需要更新的文档 |
|---|---|
| 需求、功能范围 | `docs/analysis/requirements.md` |
| 架构、API、键盘输入机制 | `docs/analysis/technical-design.md` |
| 配色、布局、控件规格 | `docs/analysis/ui-design.md` |
| 开发环境、编码规范 | 本文 |
| 测试范围、回归清单 | `docs/agent-reference/testing.md` |
| 打包、依赖、发布流程 | `docs/agent-reference/release.md` |
| 新问题与排查方法 | `docs/agent-reference/troubleshooting.md` |
| 文档结构或权威来源 | `docs/README.md` |
| 版本变更 | `CHANGELOG.md` 与版本归档 |

## 相关文档

- [文档体系索引](../README.md)
- [项目需求](../analysis/requirements.md)
- [技术设计](../analysis/technical-design.md)
- [UI 设计规范](../analysis/ui-design.md)
- [测试指南](testing.md)
- [发布指南](release.md)
- [故障排查](troubleshooting.md)
