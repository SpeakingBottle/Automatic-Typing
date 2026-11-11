# 故障排查

> 本文记录键盘输入、中文/Unicode、换行、缩进、环境和打包问题的排查路径。
> 底层机制见 [技术设计](../analysis/technical-design.md)。

## 快速判断

| 现象 | 优先检查 |
|---|---|
| 英文字符丢失或错字 | 扫描码模式、`VkKeyScanExW`、Shift 状态 |
| 中文 / emoji 变成空格或乱码 | Unicode 回退通道、目标应用是否处理 `WM_CHAR` |
| 多出空行 | `\r` 是否被跳过、Enter 后延时是否足够 |
| 注解和下一行粘连 | Enter 后 `0.05s` 延时、编辑器自动补全 |
| 缩进重复 | `skip_indent` 是否开启、目标编辑器是否自动缩进 |
| 暂停后重复或丢字 | 线程状态机、暂停位置索引、UI 回调线程 |
| 程序无法启动 | Python 版本、依赖、工作目录、`start.bat` |
| 打包后无法运行 | `hiddenimports`、控制台配置、目标机环境 |

## 1. 英文和 ASCII 字符异常

检查顺序：

1. 确认使用的是 `KEYEVENTF_SCANCODE` 模式，而不是 `KEYEVENTF_UNICODE`。
2. 确认 `VkKeyScanExW(char, 0)` 传入的是字符本身，不是 `ord(char)`。
3. 确认 `MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)` 返回了有效扫描码。
4. 检查 Shift 状态：需要 Shift 的字符是否在按下/释放前后正确包裹。
5. 用 `test_sendinput.py` 在记事本中隔离测试，排除 GUI 和目标应用因素。

## 2. 中文、emoji 和特殊 Unicode

- `VkKeyScanExW(char, 0) == -1` 表示字符无法映射到当前键盘布局，应走 `KEYEVENTF_UNICODE`。
- Unicode 模式发送 key down → 系统合成 `WM_CHAR` → key up。
- 某些应用不处理 `VK_PACKET`，因此 ASCII 字符不要走 Unicode 通道。
- 若中文正常但 emoji 异常，优先检查目标应用对代理对和 `WM_CHAR` 的支持。
- 若所有非 ASCII 都异常，检查 `INPUT` / `KEYBDINPUT` 结构体大小和字段类型。

## 3. 换行、空行和粘连

- Windows 换行是 `\r\n`；`\r` 必须在 `_typing_loop` 或 `send_char` 层跳过。
- 每个 `\n`（Enter）后额外 `sleep(0.05s)`，给编辑器处理换行和自动缩进。
- Enter/Tab 的 press → release 之间保留 `0.005s`，确保目标应用捕获事件。
- 若出现 `@Overridepublic` 粘连，优先增加 Enter 后延时，或在目标编辑器关闭自动补全。
- 若出现双空行，检查是否把 `\r` 当成独立 Enter 发送。

## 4. 缩进问题

### 开启 skip_indent 后缩进丢失

- 目标编辑器可能没有自动缩进。记事本等编辑器应关闭 `skip_indent`。
- 确认 `at_line_start` 状态在遇到非空白字符后正确置为 `False`。
- 确认跳过的每个空白字符都消耗了 `0.005s`，给编辑器处理时间。

### 关闭 skip_indent 后缩进重复

- 目标编辑器可能已经自动缩进，此时应开启 `skip_indent`。
- 在 PTA、VS Code 等编辑器中分别验证空格和 Tab 两种缩进。

## 5. 暂停、继续和停止

- 打字线程是 daemon 线程；UI 更新必须通过 `CTk.after(0, callback)` 回到主线程。
- 暂停时记录当前字符索引，继续时从该索引恢复，避免重复或跳字。
- 停止后要清理线程状态，确保可以重新开始。
- 若按钮状态和实际行为不一致，检查引擎状态回调和按钮 `state` 更新是否同步。

## 6. 环境与启动

- 本项目要求 Python 3.13；MSYS2 的 Python 3.12 可能在 PATH 前面。
- 显式使用：
  `C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe`
- 依赖：`pip install -r requirements.txt`
- 确认在项目根目录执行命令；`start.bat` 会自动 `cd /d "%~dp0"`。
- `start.bat` 使用 `pythonw.exe`，不会保留命令行窗口；若双击后无窗口，先改用 `python main.py` 查看异常输出。
- 若 `start.bat` 找不到 Python，检查脚本中的解释器路径是否存在；脚本会回退到 PATH 中的 `pythonw`。

## 7. 打包问题

- 确认 `build.spec` 的 `hiddenimports` 包含 `customtkinter` 和 `pyperclip`。
- 若 exe 启动即退出，临时把 `console=True` 查看 traceback，定位后再改回。
- 若打包后缺少资源，检查 `datas` 和 `pathex` 配置。
- 在无 Python 环境的 Windows 机器上验证最终 exe。

### 图标不显示

1. 确认 `assets/icons/light`、`dark`、`on_accent` 三套 PNG 存在。
2. 确认文件名与 `ui/icons.py` 中的名称一致，例如 `trash-2.png`。
3. 开发环境检查 `resource_path("assets")` 是否指向项目根目录。
4. 打包环境检查 `build.spec` 的 `datas=[('assets', 'assets')]` 是否生效。
5. 图标缺失时按钮应退化为纯文字；如果程序崩溃，检查 `get_icon` 的异常回退是否被绕过。

### 任务栏仍是 Python 默认图标或图标发糊

- `main.py` 必须在创建 `App` 前调用 `SetCurrentProcessExplicitAppUserModelID`。
- `App._apply_window_icon()` 同时设置 `app.ico` 和 `app.png`；确认两个资源都在 `assets/` 下。
- customtkinter 会在 200ms 后设置自己的图标；项目通过提前调用 `iconbitmap` 阻止覆盖。
- `assets/app.ico` 由 `node tools/render_icons.mjs` 生成，包含 16~256px 九个尺寸；不要用单张 PNG 直接缩放生成 ico。
- 任务栏可能缓存旧图标，必要时重启资源管理器或重新登录 Windows。

### 从浮层点击继续后字符输入到浮层

- `utils/windows.py` 记录最近一个非本程序的前台窗口。
- 继续输入前必须先调用 `set_foreground_window(target_hwnd)`，再延迟约 60ms 恢复引擎。
- 若目标窗口已关闭，`SetForegroundWindow` 会失败；此时应回到主窗口并重新选择目标。
- 浮层按钮会激活浮层本身，不能假设目标窗口一直保持前台。

### 主窗口没有自动最小化

- `App._start_typing()` 在显示浮层后通过 `after(60, ...)` 调用 `iconify()`。
- 检查浮层是否已成功创建；首次创建较慢时可依赖 `CountdownOverlay.prewarm()` 提前构建。
- 若用户使用 `python main.py` 且窗口未激活，`iconify()` 仍然有效；如果被其他窗口管理器拦截，检查 Windows 窗口状态。

### 切换语言后文案没有更新

- 新控件必须实现 `refresh_language()`，并由 `App._retranslate_ui()` 调用。
- 状态栏使用 `_set_status(key, ...)` 保存 key；直接拼接字符串会导致切换语言后无法恢复。
- 检查 `ui/i18n.py` 是否同时存在 `zh` 和 `en` 条目。

### 主题切换后图标颜色不更新

- `ui/app.py` 的主题切换会重新应用标题栏、编辑器工具栏和控制栏图标。
- 若新增图标按钮，必须同时在主题切换时重新调用 `get_icon(..., "theme")`。
- 检查 `CTkImage` 是否同时提供 `light_image` 和 `dark_image`。

### 停止后显示“完成”

- `TypingEngine.on_finished` 只应在自然输入完成时触发。
- 用户停止或取消倒计时应触发 `on_stopped`。
- 若停止后出现完成提示，检查 `_finish(completed=...)` 的调用位置，以及 UI 是否在 `on_stopped` 后覆盖状态。
- 运行 `python -m unittest tests.test_typer_state -v` 验证回调契约。

### 打包后提示缺少 Pillow

- 确认 `requirements.txt` 包含 `Pillow>=10.0.0`。
- 重新执行 `pip install -r requirements.txt` 后再打包。
- PyInstaller 会通过 `ui/icons.py` 的 PIL 导入自动收集 Pillow；若仍缺失，在 `hiddenimports` 中加入 `PIL`。

## 8. 隔离调试

```bash
# 在项目根目录执行
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe test_sendinput.py
```

运行后 3 秒内切换到记事本。若隔离脚本正常而 GUI 异常，问题更可能在 GUI 状态管理、焦点切换或目标窗口；若隔离脚本也异常，优先检查 `engine/key_mapping.py` 和 SendInput 结构体。
