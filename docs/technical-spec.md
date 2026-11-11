# 技术规范

## 技术栈

| 层面 | 技术选择 | 版本要求 | 协议 |
|------|---------|---------|------|
| 语言 | Python | 3.10+ | PSF |
| GUI 框架 | customtkinter | >=5.2.0 | MIT |
| 键盘模拟 | ctypes + Win32 `SendInput` API | Windows 内置 | - |
| 剪贴板 | pyperclip | >=1.8.2 | MIT |
| 打包 | PyInstaller | >=6.0.0 | GPL |

## 项目结构

```
Automatic-Typing/
├── main.py              # 程序入口
├── ui/                  # UI 层
│   ├── app.py           #   主窗口（组装各面板，连接引擎）
│   ├── text_panel.py    #   文本输入面板
│   └── control_panel.py #   控制面板
├── engine/              # 业务逻辑层
│   ├── typer.py         #   核心打字引擎（多线程）
│   └── key_mapping.py   #   字符到虚拟键码映射 + SendInput 结构体
├── utils/               # 工具层
│   └── clipboard.py     #   剪贴板工具
├── docs/                # 开发文档
│   ├── requirements.md
│   ├── technical-spec.md
│   ├── design-spec.md
│   ├── execution-standards.md
│   └── agent-template.md
├── assets/              # 设计资源
├── README.md            # 项目说明
├── LICENSE              # MIT 许可证
├── .gitignore           # Git 忽略规则
├── requirements.txt     # Python 依赖
├── build.spec           # PyInstaller 打包配置
└── 启动自动打字.bat      # 启动脚本
```

## 架构分层

```
┌─────────────────────────┐
│        main.py          │  ← 入口，初始化 App
├─────────────────────────┤
│       ui/app.py         │  ← 组装 UI、连接引擎回调
│  ┌─────────┬──────────┐ │
│  │ text    │ control  │ │  ← Panel 组件（纯 UI）
│  │ panel   │ panel    │ │
│  └─────────┴──────────┘ │
├─────────────────────────┤
│    engine/typer.py      │  ← 打字引擎（线程管理 + 状态机）
│    engine/key_mapping.py│  ← SendInput 底层封装
├─────────────────────────┤
│    utils/clipboard.py   │  ← 剪贴板工具
└─────────────────────────┘
```

## 核心 API

### TypingEngine

```
TypingEngine()
    .start(text, base_delay_ms, countdown_seconds, skip_indent)  # 开始打字
    .pause()                                                      # 暂停
    .resume()                                                     # 继续
    .stop()                                                       # 停止
    .is_running / .is_paused                                      # 状态属性
    .on_countdown(remaining)                                      # 倒计时回调
    .on_progress(current, total)                                  # 进度回调
    .on_finished()                                                # 完成回调
    .on_status_change(status)                                     # 状态变更回调
```

参数说明：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | `str` | - | 要输入的文本 |
| `base_delay_ms` | `int` | 150 | 基础字符间隔（毫秒），范围 30-500 |
| `countdown_seconds` | `int` | 3 | 开始前倒计时（秒），范围 1-10 |
| `skip_indent` | `bool` | `True` | 是否跳过行首缩进（依赖编辑器自动缩进） |

## 键盘输入原理

使用 Windows `SendInput` API，采用**双模式混合**策略——ASCII 字符走扫描码模式，非 ASCII 字符走 Unicode 模式：

### 字符发送流程

引擎在 `send_char()` 中按以下优先级处理每个字符：

1. **特殊键**（Enter `\n`、Tab `\t`）：使用虚拟键码模式发送，press→release 之间有 `0.005s` 延迟确保目标应用捕获事件
2. **非 ASCII 字符**（中文、emoji 等）：若 `VkKeyScanExW(char, 0) == -1`（无法映射到键盘布局），使用 `KEYEVENTF_UNICODE` 模式直接发送 WM_CHAR 消息
3. **ASCII 字符**（英文、数字、符号）：使用 `KEYEVENTF_SCANCODE` 扫描码模式，这是兼容性最好的键盘模拟方式

### ASCII 字符：扫描码模式

1. 调用 `VkKeyScanExW(char, 0)` 获取字符的虚拟键码（VK）和 Shift 状态
2. 调用 `MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)` 将 VK 转为硬件扫描码
3. 构造 `INPUT` 结构体，`dwFlags=KEYEVENTF_SCANCODE`，`wScan=扫描码`
4. 调用 `SendInput` 发送按下事件，再发送释放事件（`KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP`）
5. 若需 Shift，在按键前后分别按下/释放 Shift（间隔 `0.002s`）

### 非 ASCII 字符：Unicode 模式

当 `VkKeyScanExW` 返回 `-1` 时（字符无法映射到任何键盘布局），自动回退到 Unicode 模式：

1. 构造 `INPUT` 结构体，`dwFlags=KEYEVENTF_UNICODE`，`wScan=Unicode码点`
2. 发送 key down → 系统合成 `WM_CHAR` 消息传递给目标窗口
3. 发送 key up（`KEYEVENTF_UNICODE | KEYEVENTF_KEYUP`）

该模式适用于中文、emoji 等任何 Unicode 字符。对 ASCII 字符不推荐使用（部分应用不处理 VK_PACKET），仅作为无法映射字符的回退方案。

### 特殊字符处理

- **Enter**: 虚拟键码模式发送 `VK_RETURN`，press→release 间隔 `0.005s`；每次 Enter 后额外 `sleep(0.05s)`，给编辑器时间处理换行并完成自动缩进，防止被自动补全截获
- **Tab**: 虚拟键码模式发送 `VK_TAB`，press→release 间隔 `0.005s`
- **`\r` 跳过**: Windows 换行为 `\r\n`。`\r` 在 `_typing_loop` 循环层和 `send_char` 函数层双保险跳过，避免产生额外延时或状态干扰

### 行首缩进跳过（skip_indent）

当 `skip_indent=True` 时，引擎维护一个 `at_line_start` 标志：
1. 文本开头视为行首（初始 `True`）
2. 遇到 `\n`（Enter）后置 `True`
3. 遇到任何非空白字符后置 `False`
4. 当 `at_line_start=True` 且当前字符为空格或 Tab 时，跳过不发送，但每个跳过的空白字符消耗 `0.005s`，让编辑器有时间完成自动缩进

这样让目标编辑器的自动缩进接管缩进，避免 PTA 等平台的缩进叠加问题。

### 时序设计（防止字符粘连）

| 场景 | 延迟 | 说明 |
|------|------|------|
| Enter press→release | `0.005s` | 确保目标应用捕获 Enter 事件 |
| Enter 后等待 | `0.05s` | 给编辑器换行 + 自动缩进的处理时间 |
| 跳过缩进空白 | `0.005s/字符` | 模拟跳过空白的时间消耗，防止下一字符过早到达 |
| Tab press→release | `0.005s` | 确保目标应用捕获 Tab 事件 |
| Shift 组合键 | `0.002s` press/release 前后 | 确保 Shift 修饰生效 |
| 字符间随机延迟 | `base_delay ± 30%`，最低 `0.005s` | 模拟真人打字节奏 |

这些时序叠加后，从 Enter 到下一行首个非空白字符的延迟至少为 `0.005 + 0.05 + N×0.005 + random_delay`（N 为跳过的空白字符数），有效防止 `@Override` 与下一行 `public` 粘连的竞态问题。

## 线程模型

- **主线程**: GUI 事件循环（customtkinter）
- **打字线程**: daemon 线程，负责逐字发送键盘事件
- **跨线程通信**: 引擎回调通过 `CTk.after(0, callback)` 回到主线程更新 UI

## 结构体定义

`INPUT` / `KEYBDINPUT` 等结构体使用 ctypes 精确映射 Windows SDK 定义：
- `dwExtraInfo` 类型为 `ULONG_PTR`（64 位下 8 字节，32 位下 4 字节）
- `INPUT_UNION` 包含 `KEYBDINPUT`、`MOUSEINPUT`、`HARDWAREINPUT`，确保 union 大小正确
- 总 `INPUT` 结构体大小：40 bytes（64 位）

## 调试工具

`test_sendinput.py` — 独立于 GUI 的 SendInput 测试脚本，可用于隔离排查键盘输入问题。

- 使用 PyInstaller 打包为单文件 .exe
- `console=False`（无控制台窗口）
- 隐藏导入: `customtkinter`, `pyperclip`
