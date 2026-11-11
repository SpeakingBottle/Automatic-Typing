# 执行规范

## 开发环境

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 / 11 |
| Python | 3.13（当前开发环境路径: `C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe`） |
| 包管理 | pip |
| 虚拟环境 | 可选，当前使用全局环境 |

## 启动方式

### 开发模式

```bash
# 方式一：使用完整 Python 3.13 路径（避免 MSYS2 冲突，在项目根目录执行）
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe main.py

# 方式二：使用批处理脚本（推荐）
启动自动打字.bat
```

### SendInput 测试（排查键盘输入问题）

```bash
# 在项目根目录执行
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe test_sendinput.py
# 3 秒内切换到记事本，观察字符是否正常输入
```

### 打包

```bash
pip install pyinstaller
# 在项目根目录执行
pyinstaller build.spec
# 输出: dist/自动打字.exe
```

## 编码规范

### Python 代码风格
- 遵循 PEP 8
- 缩进: 4 个空格
- 引号: 优先使用双引号 `"`
- 编码声明: 文件头使用 `# -*- coding: utf-8 -*-`（如需中文）
- 类型注解: 推荐使用（Python 3.10+ 语法）

### 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块/文件 | snake_case | `text_panel.py` |
| 类 | PascalCase | `TypingEngine` |
| 函数/方法 | snake_case | `send_char()` |
| 变量 | snake_case | `base_delay` |
| 私有成员 | _ 前缀 | `_thread`, `_paused` |
| 常量 | UPPER_SNAKE_CASE | `VK_SHIFT` |
| 回调方法 | _on_ 前缀 | `_on_start()`, `_on_finished()` |

### 注释规范

- 每个 `.py` 文件开头使用 `"""..."""` 说明模块用途
- 公共方法使用 docstring
- 复杂逻辑使用行内注释解释
- 注释语言: 中文（面向中文开发者）

### 导入顺序

1. 标准库
2. 第三方库
3. 项目内部模块

各组之间空一行。

## 分支与变更

- 项目使用 Git 管理，主分支: `main`
- 功能分支: `feature/<功能名>`
- 修复分支: `fix/<问题描述>`
- 提交信息: 使用中文，格式: `<类型>: <描述>`（如 `feat: 添加全局热键支持`）

## 测试要求

| 测试类型 | 范围 | 方法 |
|------|------|------|
| 手动测试 | 每次变更后 | 启动应用，在记事本中验证打字功能 |
| 字符测试 | 特殊字符 | 测试包含特殊符号、换行、Tab 的文本 |
| 中文测试 | 中文字符 | 测试纯中文、中英混排、中文标点，确认不被替换为空格 |
| Unicode 测试 | emoji/全角 | 测试 emoji（如 `😀`）、全角符号，确认 Unicode 回退通道正常 |
| 换行测试 | `\r\n` 双回车 | 粘贴多行文本，确认不会多出空行 |
| 换行衔接测试 | `@Override` 等注解后换行 | 确认注解后的换行正确，不会与下一行合并为 `@Overridepublic` |
| 缩进跳过测试 | skip_indent 复选框 | 在 PTA 中验证缩进不重复；在记事本中验证取消勾选后保留原文缩进 |
| 行间空白测试 | 两个方法之间的空行 | 确认空行正常保留，`\r` 被正确跳过 |
| 速度测试 | 默认 150ms | 确认打字速度像真人，不触发平台检测 |
| 状态测试 | 控制操作 | 测试开始、暂停、继续、停止操作 |
| SendInput 测试 | 隔离调试 | 运行 `test_sendinput.py` 排查底层问题 |
| 打包验证 | 发布前 | 在无 Python 环境的机器上运行 .exe |

## 依赖管理

### 添加依赖
1. 在 `requirements.txt` 中添加（含版本范围）
2. 运行 `pip install -r requirements.txt`
3. 如需打包，确保 `build.spec` 的 `hiddenimports` 中包含新模块

### 依赖审查
- 优先选择 MIT / Apache 2.0 / BSD 协议
- 避免 GPL 协议依赖（PyInstaller 仅在构建期使用，不包含在分发包中）
- 关注依赖体积，避免引入大型框架

## 发布检查清单

- [ ] 所有功能在 Windows 10/11 上测试通过
- [ ] `pyinstaller build.spec` 打包成功
- [ ] 生成的 .exe 在无 Python 环境下可运行
- [ ] 特殊字符（`{}[]();:""''<>/\!@#$%^&*`）输入正常
- [ ] 换行、Tab 缩进正常（不出现多余空行）
- [ ] skip_indent 复选框布局正确，与按钮分行
- [ ] 中文字符（含标点）正常，中英混排正常
- [ ] Unicode 字符（emoji 等）正常，不出现替换为空格的情况
- [ ] 暂停/继续/停止 操作正常
- [ ] UI 颜色与设计规范一致
- [ ] 目标编辑器自动补全行为已确认（必要时提醒用户关闭自动补全）
