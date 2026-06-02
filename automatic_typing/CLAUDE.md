# CLAUDE.md

## 项目概述

**自动打字 (Automatic Typing)** — Windows 桌面软件，通过模拟键盘输入将代码/文本逐字输入到目标窗口，绕过 PTA 等平台的禁止粘贴限制。

- 技术栈: Python 3.13 + customtkinter + Windows SendInput API
- 运行平台: Windows 10/11
- GUI 框架: customtkinter (MIT)

---

## 标准文档路径

所有项目规范和标准文档位于 [docs/](docs/) 目录：

| 文档 | 路径 | 说明 |
|------|------|------|
| 需求文档 | [docs/requirements.md](docs/requirements.md) | 项目需求、核心功能定义 |
| 技术规范 | [docs/technical-spec.md](docs/technical-spec.md) | 技术栈、架构、API、线程模型、打包 |
| 设计规范 | [docs/design-spec.md](docs/design-spec.md) | 配色、字体、图标、布局、组件规格 |
| 执行规范 | [docs/execution-standards.md](docs/execution-standards.md) | 开发环境、编码规范、测试要求、发布检查清单 |

> **重要**: 任何开发工作开始前，必须先阅读对应的标准文档。修改代码时必须同步更新受影响的文档。

---

## 项目结构

```
automatic_typing/
├── main.py              # 入口
├── ui/                  # UI 层（customtkinter 组件）
│   ├── app.py           #   主窗口 App 类
│   ├── text_panel.py    #   文本输入面板
│   └── control_panel.py #   控制面板
├── engine/              # 引擎层（键盘模拟）
│   ├── typer.py         #   打字引擎（线程 + 状态机）
│   └── key_mapping.py   #   虚拟键码 + SendInput 结构体
├── utils/               # 工具层
│   └── clipboard.py     #   剪贴板读写
├── docs/                # 开发文档（见上方表格）
├── assets/              # 设计资源
├── requirements.txt     # Python 依赖
├── build.spec           # PyInstaller 打包配置
├── test_sendinput.py    # SendInput 独立测试脚本
└── 启动自动打字.bat      # 启动脚本
```

---

## 工作说明

### 启动应用

```bash
# 开发模式
cd automatic_typing
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe main.py

# 或双击 启动自动打字.bat
```

### 修改代码时

1. **阅读文档**: 先查看 [docs/](docs/) 中对应规范
2. **分层修改**: UI 改动只涉及 `ui/`，逻辑改动只涉及 `engine/`，工具函数在 `utils/`
3. **命名遵守**: 类名 PascalCase，函数/变量 snake_case，私有成员 `_` 前缀
4. **注释**: 每个文件用 docstring 说明模块用途，公共方法写 docstring
5. **同步文档**: 修改功能后更新对应的规范文档

### 添加新功能时

1. 先在 [docs/requirements.md](docs/requirements.md) 中记录新需求
2. 在 [docs/technical-spec.md](docs/technical-spec.md) 中补充技术方案
3. 如需 UI 变更，更新 [docs/design-spec.md](docs/design-spec.md)
4. 代码实现放在对应层级目录
5. 在 `build.spec` 中补充 `hiddenimports`（如有新依赖）

### 键盘输入关键点

- ASCII 字符：使用 `KEYEVENTF_SCANCODE` 模式（扫描码），非 `KEYEVENTF_UNICODE`（后者对 ASCII 不可靠）
- 非 ASCII 字符（中文、emoji 等）：自动回退到 `KEYEVENTF_UNICODE` 模式发送 WM_CHAR
- 判断方式：`VkKeyScanExW(char, 0) == -1` → 字符无法映射到键盘布局 → 走 Unicode 通道
- `VkKeyScanExW(char, 0)` — 注意传字符本身，不是 `ord(char)`
- `MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)` — VK 码转硬件扫描码
- `\r` 必须跳过（在 `_typing_loop` 循环层处理），否则会多空行且干扰 `at_line_start` 状态
- 每个 `\n`（Enter）后额外 `sleep(0.05s)`，给编辑器时间处理换行，避免被自动补全吞掉
- Enter/Tab 的 press→release 之间有 `sleep(0.005s)`，确保目标应用能捕获按键事件
- skip_indent 跳过的每个空格也有 `sleep(0.005s)`，让编辑器有时间完成自动缩进
- `dwExtraInfo` 类型为 ULONG_PTR（`c_uint64`/`c_uint32`），不能用 `POINTER(c_ulong)`

### 测试

每次代码变更后，手动启动应用并在记事本中验证：
- 基本文字输入 ✔
- 特殊符号 `{}[]();:""<>!@#$%^&*` ✔
- 中文字符（纯中文、中英混排、中文标点）✔
- Unicode 字符（emoji 等）✔
- 换行（确认不出现双空行）+ Tab 缩进 ✔
- 换行衔接：`@Override` 等注解后换行不会与下一行粘连 ✔
- skip_indent 复选框：在记事本中取消勾选验证保留原文缩进，在 PTA 中勾选验证不重复缩进 ✔
- 暂停/继续/停止 ✔

键盘问题隔离调试：
```bash
C:\...\Python313\python.exe test_sendinput.py  # 独立测试 SendInput
```

### 打包

```bash
cd automatic_typing
pyinstaller build.spec
# 输出 exe: dist/自动打字.exe
```

---

## 环境信息

- Python 路径: `C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe`
- 注意: MSYS2 的 Python 3.12 在 PATH 前面，必须显式使用 Python 3.13 路径
- 依赖已安装在 Python 3.13 全局环境: `customtkinter==5.2.2`, `pyperclip==1.11.0`
