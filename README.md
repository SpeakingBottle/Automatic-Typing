# 自动打字 (Automatic Typing)

一款 Windows 桌面工具：通过模拟真实键盘输入，将代码或文本逐字输入到目标窗口，适用于禁止粘贴、只能手动输入的文本框。

> 本项目由 Claude Code + DeepSeek V4-pro 辅助生成。

## 功能特性

- 逐字模拟键盘输入，支持英文字母、数字和代码常用符号
- 中文字符、中文标点和 emoji 自动切换 Unicode 输入通道
- 可调节打字速度（30ms ~ 500ms），并带有 ±30% 随机波动
- 开始前可配置 1 ~ 10 秒倒计时，方便切换到目标窗口
- 可跳过行首缩进，避免与编辑器的自动缩进叠加
- 支持暂停、继续和停止
- 一键读取系统剪贴板
- 提供 PyInstaller 打包配置，可生成独立 `.exe`

## 运行环境

- Windows 10 / 11
- Python 3.10+（开发环境使用 Python 3.13）
- 无需管理员权限

## 快速开始

### 从源码运行

```bash
git clone https://github.com/SpeakingBottle/Automatic-Typing.git
cd Automatic-Typing
pip install -r requirements.txt
python main.py
```

也可以双击 `启动自动打字.bat` 启动。

### 打包为 exe

```bash
pip install -r requirements.txt
pyinstaller build.spec
```

输出文件位于 `dist/自动打字.exe`。

## 使用步骤

1. 启动程序，将代码或文本粘贴到输入区，或点击 **读取剪贴板**。
2. 根据需要调整打字速度、倒计时和 **跳过行首缩进** 选项。
3. 点击 **开始打字**。
4. 在倒计时结束前，将光标切换到目标输入框并保持目标窗口在前台。
5. 打字过程中可以暂停、继续或停止。

## 注意事项

- 倒计时结束前务必切换到目标窗口，否则文字会输入到本程序自己的文本框中。
- 目标窗口需要保持前台激活，打字过程中不要切换窗口。
- 如果目标编辑器没有自动缩进（例如记事本），请取消勾选 **跳过行首缩进**。
- 某些编辑器的自动补全可能产生多余的闭合括号，建议在目标编辑器中关闭自动补全。
- 打字速度过快可能触发平台风控，建议保持在 100ms ~ 300ms。

## 项目结构

```text
Automatic-Typing/
├── main.py              # 程序入口
├── ui/                  # UI 层（customtkinter）
├── engine/              # 打字引擎与 SendInput 封装
├── utils/               # 剪贴板等工具
├── docs/                # 需求、技术、设计与执行规范
├── test_sendinput.py    # SendInput 独立测试脚本
├── build.spec           # PyInstaller 打包配置
└── 启动自动打字.bat      # Windows 启动脚本
```

## 开发文档

- [需求文档](docs/requirements.md)
- [技术规范](docs/technical-spec.md)
- [设计规范](docs/design-spec.md)
- [执行规范](docs/execution-standards.md)

## 参与贡献

欢迎提交 Issue 或 Pull Request。提交代码前请先阅读 [执行规范](docs/execution-standards.md)，并确保手动测试覆盖基本输入、中文、Unicode、换行、缩进和控制操作。

## 免责声明

本项目仅供技术学习和研究使用。请遵守目标平台的使用规则，因其他用途使用本项目造成的后果由使用者自行承担。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
