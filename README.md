# 自动打字 (Automatic Typing)

简体中文 | [English](README.en.md)

一款 Windows 桌面工具：通过模拟真实键盘输入，将代码或文本逐字输入到目标窗口，适用于禁止粘贴、只能手动输入的文本框。

![自动打字主界面](docs/images/app-zh.png)

## 下载

- [GitHub Releases](https://github.com/SpeakingBottle/Automatic-Typing/releases/latest) 下载 `自动打字.exe`
- 单文件绿色版，无需安装 Python，双击即可运行
- 首次运行若出现 SmartScreen 提示，点击“更多信息 → 仍要运行”

## 功能特性

- 通用文字输入：默认文章 / 作业场景，保留代码场景
- 文章 / 代码预设自动切换字体、节奏和缩进策略
- 逐字模拟键盘输入，支持英文、数字、符号、中文、中文标点和 emoji
- 可调节打字速度（30ms ~ 500ms），支持自然节奏 ±30% 随机波动
- 1 / 3 / 5 / 10 秒倒计时，屏幕顶部居中显示圆环倒计时浮层
- 倒计时结束后浮层变为控制条，显示进度、百分比、剩余时间、暂停/继续和停止
- 点击开始后主窗口自动最小化，完成或停止后恢复
- 字数、行数和预计用时实时统计
- 空文本时自动禁用“开始打字”按钮
- 支持暂停、继续、停止和读取剪贴板
- 浅色 / 深色主题、窗口置顶
- 中文 / English 界面切换
- Lucide 开源图标，窗口和任务栏使用清晰的多尺寸应用图标
- `start.bat` 使用 `pythonw` 启动，不保留命令行窗口
- 提供独立 `.exe` 打包配置

## 运行环境

- Windows 10 / 11
- Python 3.10+（开发与验证环境为 Python 3.13）
- 依赖：`customtkinter`、`pyperclip`、`Pillow`、`pyinstaller`
- 无需管理员权限

## 快速开始

### 从源码运行

```bash
git clone https://github.com/SpeakingBottle/Automatic-Typing.git
cd Automatic-Typing
pip install -r requirements.txt
python main.py
```

也可以双击 `start.bat` 启动。脚本使用 `pythonw.exe`，启动后不会保留命令行窗口；需要查看控制台输出调试时，请直接运行 `python main.py`。

### 打包为 exe

```bash
pip install -r requirements.txt
pyinstaller build.spec
```

输出文件位于 `dist/自动打字.exe`。

## 使用步骤

1. 启动程序，默认进入 **文章 / 作业** 场景。
2. 粘贴或输入文字，或点击 **读取剪贴板**。
3. 根据需要切换 **代码** 场景，调整节奏和倒计时。
4. 点击 **开始打字**，主窗口自动最小化，屏幕顶部中央出现圆环倒计时浮层。
5. 在倒计时结束前，将光标切换到目标输入框并保持目标窗口在前台。
6. 倒计时结束后浮层变为控制条，可以直接查看进度、暂停/继续或停止。
7. 完成后主窗口自动恢复，按钮仍显示 **开始打字**。
8. 点击右上角的语言按钮（文A），可以在中文和 English 之间切换。

## 注意事项

- 倒计时结束前务必切换到目标窗口，否则文字会输入到本程序自己的文本框中。
- 目标窗口需要保持前台激活，打字过程中不要切换窗口。
- 如果目标编辑器没有自动缩进（例如记事本），请在高级设置中关闭 **跳过行首缩进**。
- 某些编辑器的自动补全可能产生多余的闭合括号，建议在目标编辑器中关闭自动补全。
- 打字速度过快可能触发平台风控，建议保持在 100ms ~ 300ms。

## 项目结构

```text
Automatic-Typing/
├── main.py              # 程序入口
├── ui/                  # UI 层（主题、预设、中英文、图标、面板）
│   ├── i18n.py          #   中文 / English 文案
│   ├── countdown.py     #   倒计时与输入控制浮层
│   └── ...
├── engine/              # 打字引擎与 SendInput 封装
├── utils/               # 剪贴板、资源路径与前台窗口
├── assets/              # 应用图标与 Lucide PNG
│   └── icons/
├── tools/               # 图标生成工具（开发期）
├── tests/               # unittest 测试
├── docs/                # 文档中心
│   ├── README.md        #   文档索引与维护规则
│   ├── images/          #   README 截图
│   ├── analysis/        #   需求、技术设计、UI 设计
│   ├── agent-reference/ #   开发、测试、发布、排障
│   ├── history-version/ #   已发布版本的实现指南与测试报告
│   └── templates/       #   可复用模板
├── AGENTS.md            # 智能体工作指引
├── CLAUDE.md            # 指向 AGENTS.md
├── CHANGELOG.md         # 版本变更记录
├── README.md            # 中文项目说明
├── README.en.md         # 英文项目说明
├── LICENSE              # MIT 许可证
├── requirements.txt     # Python 依赖
├── build.spec           # PyInstaller 打包配置
├── test_sendinput.py    # SendInput 独立测试脚本
└── start.bat            # Windows 启动脚本
```

## 开发文档

- [English README](README.en.md)
- [文档体系索引](docs/README.md)
- [项目需求](docs/analysis/requirements.md)
- [技术设计](docs/analysis/technical-design.md)
- [UI 设计规范](docs/analysis/ui-design.md)
- [开发指南](docs/agent-reference/development.md)
- [测试指南](docs/agent-reference/testing.md)
- [发布指南](docs/agent-reference/release.md)
- [故障排查](docs/agent-reference/troubleshooting.md)
- [版本变更记录](CHANGELOG.md)
- [智能体工作指引](AGENTS.md)

## 参与贡献

欢迎提交 Issue 或 Pull Request。提交代码前请先阅读 [开发指南](docs/agent-reference/development.md) 和 [测试指南](docs/agent-reference/testing.md)，并确保手动测试覆盖基本输入、中文、Unicode、换行、缩进和控制操作。

## 免责声明

本项目仅供技术学习和研究使用。请遵守目标平台的使用规则，因其他用途使用本项目造成的后果由使用者自行承担。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
