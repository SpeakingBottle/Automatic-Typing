# 通用文字输入与界面重构 · 设计规格

- 日期：2026-11-11
- 状态：设计已确认，待规格评审
- 目标版本：2.0.0
- 关联需求：把“代码输入工具”扩展为“通用文字输入工具”，并重新设计交互与视觉

## 1. 背景

当前程序已经可以输入任意文本，但产品定位、默认参数和界面文案都偏向代码输入：

- 默认跳过行首缩进，适合 PTA 等自动缩进编辑器，不适合普通文章
- 编辑器使用通用字体，没有文章/代码场景区分
- 主界面由标题栏、文本框、滑块和按钮堆叠而成，信息层级弱
- 使用 Unicode 符号充当图标，视觉不统一
- 参数在打字过程中仍可调整，但引擎使用启动时的快照，容易造成理解偏差

本次改造保留现有引擎能力，重点重构 UI 层、默认行为和交互状态。

## 2. 目标与非目标

### 2.1 目标

- 默认面向通用文字输入，同时保留代码输入能力
- 提供“文章 / 作业”和“代码”两个场景预设
- 建立清晰的“输入 → 设置 → 开始 → 倒计时 → 输入中 → 完成”状态流
- 使用现代浅色界面，并支持深色模式
- 使用许可证清晰的开源图标
- 保持中文、Unicode、换行、缩进和控制操作的现有能力
- 让打包后的 exe 正确携带图标资源

### 2.2 非目标

本次不实现：

- 聊天 / 社交、表单 / 资料等更多预设
- 全局热键
- 系统托盘
- 输入历史
- 从文件导入
- 按字符自定义延迟规则
- 云端同步或多语言界面

这些能力保留为后续独立需求，避免把 2.0.0 做成大杂烩。

## 3. 产品行为

### 3.1 场景预设

| 预设 | 字体 | 默认节奏 | 倒计时 | 跳过行首缩进 | 自然节奏 |
|---|---|---|---|---|---|
| 文章 / 作业 | Microsoft YaHei UI，14px | 90 ms/字 | 3 秒 | 关闭 | 开启 |
| 代码 | Cascadia Code / Cascadia Mono / Consolas，13px | 150 ms/字 | 3 秒 | 开启 | 开启 |

规则：

- 默认选中“文章 / 作业”。
- 切换预设会应用该预设的字体、节奏、倒计时、缩进和自然节奏开关。
- 切换预设不清空已输入文本。
- 预设是一次性应用默认值；用户之后手动调整的参数以手动值为准，预设按钮保持当前选中状态。
- 倒计时、输入中、暂停状态下禁止切换预设和修改参数，避免引擎快照与界面显示不一致。

### 3.2 文本统计与预计用时

- 字数：文本字符数，排除 `\r`。
- 行数：空文本为 0，否则为 `\n` 数量 + 1。
- 速度换算：`约 60000 / speed_ms 字/分钟`，取整。
- 预计用时：`字数 × speed_ms / 1000 + 倒计时秒数`，忽略跳过缩进和换行额外延时。
- 展示格式：
  - 小于 60 秒：`约 45 秒`
  - 大于等于 60 秒：`约 1 分 20 秒`
- 字数、行数、预计用时在文本变化、速度变化、倒计时变化时更新。

### 3.3 状态机

应用状态：

- `IDLE`：就绪
- `COUNTDOWN`：倒计时
- `TYPING`：输入中
- `PAUSED`：已暂停
- `FINISHED`：完成

主按钮行为：

| 状态 | 主按钮文案 | 主按钮图标 | 主按钮行为 | 停止按钮 |
|---|---|---|---|---|
| IDLE | 开始打字 | play | 开始 | 隐藏 |
| COUNTDOWN | 取消 | x | 停止 | 隐藏 |
| TYPING | 暂停 | pause | 暂停 | 显示 |
| PAUSED | 继续 | play | 继续 | 显示 |
| FINISHED | 再次开始 | play | 重新开始 | 隐藏 |

状态栏：

| 状态 | 状态栏 |
|---|---|
| IDLE，空文本 | 请输入要输入的文字 |
| IDLE，有文本 | 就绪 · 预计用时 1 分 20 秒 |
| COUNTDOWN | 3 秒后开始，请切换到目标窗口 |
| TYPING | 正在输入 120/500 · 剩余约 45 秒 |
| PAUSED | 已暂停 · 120/500 |
| FINISHED | 完成 · 用时 1 分 18 秒 |

进度条：

- IDLE：0
- COUNTDOWN：0
- TYPING：`current / total`
- PAUSED：保持暂停时的进度
- FINISHED：1

### 3.4 编辑器

- 多行文本编辑器占据主区域，随窗口拉伸。
- 空文本且未聚焦时显示占位文字：`在这里输入或粘贴文字…`。
- 聚焦时隐藏占位文字；失焦且内容为空时恢复。
- 占位文字不能作为实际内容参与统计或启动。
- 编辑器字体随预设变化。
- 倒计时、输入中、暂停状态下编辑器设为只读，完成后恢复可编辑。
- 支持 Ctrl+V、Ctrl+A、Ctrl+C 等标准文本框操作。

### 3.5 工具栏

编辑器底部工具栏：

- 读取剪贴板：图标按钮 + 提示文字
- 清空：图标按钮 + 提示文字
- 右侧显示：`0 字 · 0 行`

行为：

- 读取剪贴板成功：替换编辑器内容，更新统计，聚焦编辑器。
- 剪贴板为空或读取失败：状态栏提示，不改变现有内容。
- 清空：清空编辑器并恢复占位文字，更新统计。

### 3.6 高级设置

可折叠抽屉，默认收起，包含：

- 跳过行首缩进：开关，附一句说明“依赖目标编辑器自动缩进”
- 自然节奏：开关，控制是否在基础间隔上叠加 ±30% 随机波动

高级设置与预设联动：

- 切换预设时同步开关状态。
- 用户手动切换后，以当前开关值为准。
- 运行期间禁用。

### 3.7 标题栏

- 左侧：应用图标、标题“自动打字”、副标题“把文字逐字输入任意窗口”
- 右侧：
  - 窗口置顶：pin / pin-off 图标，切换 `-topmost`
  - 主题：sun / moon 图标，切换浅色/深色

### 3.8 关闭窗口

- 窗口关闭时如果引擎仍在运行，先停止引擎，再销毁窗口。
- 不弹出额外确认框。

## 4. 界面布局

### 4.1 窗口

- 默认尺寸：760 × 640
- 最小尺寸：620 × 500
- 启动时居中
- 可拉伸
- 浅色/深色主题
- 默认浅色

### 4.2 布局结构

```text
┌──────────────────────────────────────────────────────────┐
│ ⌨ 自动打字        把文字逐字输入任意窗口       [置顶] [主题] │
├──────────────────────────────────────────────────────────┤
│ 场景   [ 文章 / 作业 ]   [ 代码 ]                         │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ 在这里输入或粘贴文字...                              │ │
│ │                                                      │ │
│ │                                                      │ │
│ └──────────────────────────────────────────────────────┘ │
│ [读取剪贴板] [清空]                      0 字 · 0 行      │
├──────────────────────────────────────────────────────────┤
│ 节奏   ─────────●────────  自然 · 90 ms/字 · 约 660 字/分 │
│ 倒计时 [3 秒 ▾]                    [▶ 开始打字]  [■]     │
│ █████████████░░░░░░░  正在输入 120/500 · 剩余约 45 秒     │
│ 高级设置 ▾                                               │
└──────────────────────────────────────────────────────────┘
```

### 4.3 布局尺寸

- 窗口外边距：16px
- 卡片间距：12px
- 卡片内边距：14–16px
- 标题栏高度：约 56px
- 场景栏高度：约 40px
- 编辑器最小高度：220px
- 控制区高度：约 150px，高级设置展开后增加
- 图标按钮：32 × 32
- 主按钮：高 38，圆角 10
- 卡片圆角：12
- 编辑器圆角：10

窗口使用 grid：

- 第 0 行：标题栏，固定
- 第 1 行：场景栏，固定
- 第 2 行：编辑器卡片，权重 1
- 第 3 行：控制卡片，固定

## 5. 视觉系统

### 5.1 颜色

浅色：

| Token | 色值 | 用途 |
|---|---|---|
| bg | `#F6F7F9` | 窗口背景 |
| surface | `#FFFFFF` | 卡片、编辑器 |
| surface_alt | `#F3F4F6` | 次级表面、滑块轨道 |
| text | `#111827` | 主文字 |
| text_muted | `#6B7280` | 次要文字、说明 |
| text_subtle | `#94A3B8` | 占位文字、禁用文字 |
| border | `#E5E7EB` | 卡片边框 |
| border_strong | `#D1D5DB` | 输入框边框、分隔线 |
| accent | `#4F46E5` | 主按钮、选中态 |
| accent_hover | `#4338CA` | 主按钮悬停 |
| accent_text | `#FFFFFF` | 主按钮文字 |
| danger | `#DC2626` | 停止、错误提示 |
| success | `#059669` | 完成状态 |

深色：

| Token | 色值 | 用途 |
|---|---|---|
| bg | `#0F172A` | 窗口背景 |
| surface | `#111827` | 卡片、编辑器 |
| surface_alt | `#1F2937` | 次级表面、滑块轨道 |
| text | `#E5E7EB` | 主文字 |
| text_muted | `#94A3B8` | 次要文字、说明 |
| text_subtle | `#64748B` | 占位文字、禁用文字 |
| border | `#263244` | 卡片边框 |
| border_strong | `#334155` | 输入框边框、分隔线 |
| accent | `#6366F1` | 主按钮、选中态 |
| accent_hover | `#4F46E5` | 主按钮悬停 |
| accent_text | `#FFFFFF` | 主按钮文字 |
| danger | `#F87171` | 停止、错误提示 |
| success | `#34D399` | 完成状态 |

图标颜色：

- 浅色主题：`#475569`
- 深色主题：`#CBD5E1`
- 主按钮反白：`#FFFFFF`
- 禁用态：使用浅色/深色主题的 `text_subtle`

### 5.2 字体

| 场景 | 字体 | 字号 | 字重 |
|---|---|---|---|
| 标题 | Microsoft YaHei UI | 16 | Bold |
| 副标题 / 说明 | Microsoft YaHei UI | 12 | Normal |
| 正文 / 标签 | Microsoft YaHei UI | 13 | Normal |
| 主按钮 | Microsoft YaHei UI | 14 | Bold |
| 字数统计 | Microsoft YaHei UI | 12 | Normal |
| 文章编辑器 | Microsoft YaHei UI | 14 | Normal |
| 代码编辑器 | Cascadia Code / Cascadia Mono / Consolas | 13 | Normal |

字体选择使用候选列表，取系统中第一个可用字体。

### 5.3 控件风格

- 卡片：surface 背景、1px border、12px 圆角
- 编辑器：surface 背景、1px border、10px 圆角
- 主按钮：accent 背景、白色文字、10px 圆角、悬停 accent_hover
- 次级按钮：透明背景、1px border、10px 圆角
- 图标按钮：32 × 32、透明背景、8px 圆角、悬停 surface_alt
- 滑块：surface_alt 轨道、accent 进度、圆形滑块
- 开关：accent 选中色
- 不使用大面积渐变、阴影和多重强调色

## 6. 图标与资源

### 6.1 图标库

使用 **Lucide** 图标：

- 许可证：ISC License；部分来自 Feather 的图标为 MIT
- 来源：`https://lucide.dev/`
- 使用方式：下载 SVG，离线生成 PNG，随程序打包
- 不依赖运行时网络

### 6.2 图标清单

| 名称 | 用途 |
|---|---|
| `keyboard` | 应用图标、标题 |
| `clipboard` | 读取剪贴板 |
| `trash-2` | 清空 |
| `play` | 开始 / 继续 |
| `pause` | 暂停 |
| `square` | 停止 |
| `x` | 取消倒计时 |
| `pin` | 窗口置顶开启 |
| `pin-off` | 窗口置顶关闭 |
| `sun` | 浅色主题 |
| `moon` | 深色主题 |
| `chevron-down` | 高级设置展开 |
| `chevron-up` | 高级设置收起 |

预设按钮使用文字，不使用图标。

### 6.3 资源目录

```text
assets/
├── app.ico
└── icons/
    ├── LICENSE
    ├── README.md
    ├── light/
    │   ├── keyboard.png
    │   ├── clipboard.png
    │   └── ...
    ├── dark/
    │   └── ...
    └── on_accent/
        └── ...
```

- 源 PNG 尺寸：40 × 40，显示时缩放到 18–20px
- `light/` 使用浅色主题图标色
- `dark/` 使用深色主题图标色
- `on_accent/` 使用白色，供主按钮使用
- `assets/icons/LICENSE` 保存 Lucide 的 ISC 许可证文本
- `assets/icons/README.md` 记录来源、版本、图标清单和再生成方法
- `assets/app.ico` 由 Lucide `keyboard` 图标加 accent 圆角底生成，256px 源图导出
- 图标使用 Lucide SVG 源文件，通过开发期 Node `sharp` 渲染为 PNG；`sharp` 不进入运行时依赖

### 6.4 加载与回退

- `ui/icons.py` 负责根据名称和主题变体加载 PNG，返回 `CTkImage`。
- 图标加载失败时返回 `None`，按钮退化为纯文字，不得抛异常。
- 主题切换时，如果 customtkinter 未自动刷新已有控件图标，则显式重新应用图标。

## 7. 工程结构

```text
ui/
├── app.py              # 主窗口、状态协调、引擎回调
├── theme.py            # 颜色 token、字体、间距、主题切换
├── presets.py          # 文章/代码预设定义
├── icons.py            # 图标加载与缓存
├── tooltip.py          # 图标按钮提示
├── text_panel.py       # 编辑器卡片、工具栏、统计
└── control_panel.py    # 场景、节奏、倒计时、传输控制、进度、高级设置

engine/
└── typer.py            # 增加 randomize 参数，默认 True

assets/
├── app.ico
└── icons/...

utils/
└── resources.py        # 开发/打包环境的资源路径解析
```

### 7.1 `ui/theme.py`

提供：

- `COLORS`：浅色/深色 token 映射
- `UI_FONT`：UI 字体候选
- `ARTICLE_FONT`、`CODE_FONT`
- `get_font(candidates, size, weight)`：返回系统中可用的第一个字体
- `apply_appearance(mode)`：设置 customtkinter 外观模式

所有颜色使用 `(light, dark)` 元组传给 customtkinter，避免在业务代码中散落颜色常量。

### 7.2 `ui/presets.py`

使用 dataclass 定义：

```python
@dataclass(frozen=True)
class Preset:
    key: str
    label: str
    font_candidates: tuple[str, ...]
    font_size: int
    speed_ms: int
    countdown_seconds: int
    skip_indent: bool
    randomize: bool
```

预设：

- `article`：label `文章 / 作业`，字体候选 `("Microsoft YaHei UI", "Microsoft YaHei")`，字号 14，90ms，3 秒，`skip_indent=False`，`randomize=True`
- `code`：label `代码`，字体候选 `("Cascadia Code", "Cascadia Mono", "Consolas")`，字号 13，150ms，3 秒，`skip_indent=True`，`randomize=True`

### 7.3 `ui/icons.py`

- `IconRegistry` 单例或模块级缓存
- `get_icon(name: str, variant: str = "theme", size: tuple[int, int] = (18, 18)) -> CTkImage | None`
- `variant` 支持 `light`、`dark`、`on_accent`、`theme`
- `theme` 变体同时传入 `light_image` 和 `dark_image`
- 加载失败返回 `None`

### 7.4 `ui/tooltip.py`

- 轻量 `Tooltip` 类，基于 `tkinter.Toplevel`
- 鼠标进入后延迟约 400ms 显示
- 离开、点击或销毁时隐藏
- 用于所有图标-only 按钮

### 7.5 `ui/text_panel.py`

- `EditorCard(ctk.CTkFrame)`
- 内部包含 `CTkTextbox`、工具栏、统计标签
- 提供：
  - `get_text() -> str`
  - `set_text(text: str)`
  - `clear()`
  - `set_read_only(bool)`
  - `set_editor_font(font)`
  - `focus_editor()`
  - `on_text_changed` 回调
- 占位文字逻辑在组件内部处理
- 统计标签由父组件传入统计结果，或组件内部计算后通过回调通知

### 7.6 `ui/control_panel.py`

- `PresetBar`：场景切换
- `ControlCard`：
  - 节奏滑块与说明
  - 倒计时下拉
  - 主按钮
  - 停止按钮
  - 进度条
  - 状态栏
  - 高级设置抽屉
- 暴露属性：
  - `speed_ms`
  - `countdown_seconds`
  - `skip_indent`
  - `randomize`
- 暴露回调：
  - `on_primary`
  - `on_stop`
  - `on_preset_change`
  - `on_settings_change`
- 提供：
  - `set_state(state)`
  - `set_status(text)`
  - `set_progress(current, total)`
  - `apply_preset(preset)`
  - `set_controls_enabled(bool)`

### 7.7 `ui/app.py`

- 初始化主题、引擎、组件
- 协调状态机
- 处理剪贴板、统计、预计用时
- 处理窗口置顶、主题切换、关闭窗口
- 注册 `on_countdown`、`on_progress`、`on_finished`、`on_stopped`、`on_status_change`
- 将引擎回调通过 `after(0, ...)` 回到 UI 线程

### 7.8 `engine/typer.py`

- `start()` 增加 `randomize: bool = True`
- `_typing_loop()` 增加 `randomize` 参数
- `randomize=True`：保持当前 ±30% 随机延迟
- `randomize=False`：使用固定 `base_delay`，仍保证最低 0.005s
- 默认值必须保持 `True`，避免改变现有调用行为
- `skip_indent` 的引擎默认值保持 `True`，但 UI 始终显式传入预设值，产品默认由 UI 决定
- 区分自然完成与用户停止：
  - `on_finished` 只在文本自然输入完成时触发
  - 新增 `on_stopped` 回调，用于用户点击停止或取消倒计时
  - `_finish(completed: bool)` 根据 `completed` 触发对应回调
  - 停止后不得再触发“完成”状态或“打字完成”提示
- `TypingEngine` 增加 `on_stopped` 回调属性
- 更新 docstring

### 7.9 `utils/resources.py`

- `resource_path(relative_path: str) -> Path`
- 打包后使用 `sys._MEIPASS`，开发环境使用项目根目录
- 供图标、app.ico 使用

## 8. 数据流

### 8.1 启动流程

1. 用户点击主按钮。
2. 读取编辑器文本；如果为空，状态栏提示并聚焦编辑器。
3. 记录当前节奏、倒计时、缩进、自然节奏、文本快照。
4. 设置状态 `COUNTDOWN`，禁用编辑器和参数控件。
5. 调用 `engine.start(...)`。
6. 倒计时回调更新状态栏和主按钮文案。
7. 倒计时结束，状态转为 `TYPING`。
8. 进度回调更新进度条、状态栏和剩余时间。
9. 自然完成时触发 `on_finished`，状态转为 `FINISHED`。
10. 用户停止或取消倒计时时触发 `on_stopped`，状态回到 `IDLE`。
11. 完成或停止后恢复编辑器和参数控件。

### 8.2 暂停/继续

- `TYPING` 点击主按钮 → `engine.pause()` → `PAUSED`，主按钮变为“继续”。
- `PAUSED` 点击主按钮 → `engine.resume()` → `TYPING`，主按钮变为“暂停”。

### 8.3 停止

- 任意运行状态点击停止或倒计时点击“取消” → `engine.stop()` → `IDLE`。
- 停止后保留文本，恢复编辑器和参数控件。

### 8.4 预设切换

1. 读取预设。
2. 应用字体、节奏、倒计时、缩进、自然节奏。
3. 更新统计和预计用时。
4. 不清空文本。
5. 状态栏提示 `已切换为「文章 / 作业」预设`。

### 8.5 主题切换

1. 切换 customtkinter 外观模式。
2. 更新标题栏主题图标。
3. 如需要，刷新图标控件的 `CTkImage`。
4. 保持窗口位置和文本内容。

### 8.6 置顶切换

1. 读取当前 `-topmost` 状态。
2. 取反并设置 `self.attributes("-topmost", value)`。
3. 更新 pin / pin-off 图标和 tooltip。

## 9. 错误处理

| 场景 | 处理 |
|---|---|
| 文本为空点击开始 | 状态栏提示“请先输入要输入的文字”，聚焦编辑器 |
| 剪贴板为空 | 状态栏提示“剪贴板中没有文本”，不改变内容 |
| 剪贴板读取异常 | 状态栏提示“读取剪贴板失败” |
| 图标文件缺失 | 返回 `None`，按钮退化为纯文字，不崩溃 |
| 资源目录缺失 | 图标回退，文字界面仍可用 |
| 打包后资源路径错误 | 使用 `resource_path` 统一解析；发布前验证 exe |
| 窗口关闭时仍在运行 | 先 `engine.stop()`，再销毁窗口 |
| 重复点击开始 | 引擎已在运行时忽略 |
| 运行中切换预设 | 控件禁用，不允许操作 |

## 10. 打包与依赖

- `requirements.txt` 增加 `Pillow>=10.0.0`
- `build.spec` 的 `datas` 增加 `('assets', 'assets')`
- 确保 `assets/icons` 和 `assets/app.ico` 被 PyInstaller 收集
- `iconbitmap` 使用 `resource_path("assets/app.ico")`
- 在无 Python 环境的 Windows 机器上验证 exe
- 图标生成使用开发期工具 `sharp`，不进入运行时依赖

## 11. 测试与验收

### 11.1 自动/脚本检查

- `python -c "import main"` 通过
- `git diff --check` 无输出
- 所有本地 Markdown 链接可解析
- `pyinstaller build.spec` 打包成功

### 11.2 手动测试

| 编号 | 用例 | 预期 |
|---|---|---|
| U01 | 默认启动 | 显示文章预设、浅色主题、空编辑器占位文字 |
| U02 | 输入文本 | 字数、行数、预计用时实时更新 |
| U03 | 切换代码预设 | 字体变等宽，速度 150ms，跳过缩进开启 |
| U04 | 切换文章预设 | 字体恢复，速度 90ms，跳过缩进关闭 |
| U05 | 读取剪贴板 | 内容替换，统计更新 |
| U06 | 空剪贴板 | 状态提示，内容不变 |
| U07 | 清空 | 编辑器清空，占位文字恢复，统计归零 |
| U08 | 空文本开始 | 状态提示，不进入倒计时 |
| U09 | 开始 → 倒计时 | 主按钮变“取消”，状态提示切换窗口 |
| U10 | 倒计时取消 | 回到就绪，控件恢复 |
| U11 | 输入中暂停 | 主按钮变“继续”，进度保持 |
| U12 | 继续 | 从暂停位置继续，不重复不丢字 |
| U13 | 输入中停止 | 回到就绪，保留文本 |
| U14 | 完成 | 进度 100%，状态显示完成和用时 |
| U15 | 浅色/深色切换 | 文字、边框、图标、按钮对比度正常 |
| U16 | 窗口置顶 | 切换后窗口保持在其他窗口之上 |
| U17 | 长文本 | 编辑器滚动正常，统计正确 |
| U18 | 中文/Unicode/换行/缩进 | 原有输入行为不回归 |
| U19 | 150% DPI | 布局不重叠，文字和图标清晰 |
| U20 | 打包 exe | 图标、主题、输入功能正常 |

### 11.3 验收标准

- 默认场景为文章，普通用户不需要理解“缩进”和“扫描码”即可使用
- 代码场景仍能完成原有 PTA 输入任务
- 所有主要操作都能在单窗口内完成
- 浅色和深色主题下没有不可读文字或丢失图标
- 打包 exe 包含图标资源
- 文档与代码一致

## 12. 文档同步

实现完成后更新：

- `docs/analysis/requirements.md`：产品定位、场景预设、交互状态
- `docs/analysis/technical-design.md`：UI 架构、资源路径、randomize 参数
- `docs/analysis/ui-design.md`：新颜色、字体、布局、图标规范
- `docs/agent-reference/testing.md`：新增 U01–U20 测试矩阵
- `docs/agent-reference/troubleshooting.md`：图标缺失、主题、打包资源问题
- `README.md`：功能特性、界面说明、依赖
- `CHANGELOG.md`：2.0.0 变更
- `AGENTS.md`：如项目结构或命令发生变化则同步
- `docs/README.md`：如新增设计规格目录则补充索引

## 13. 风险与应对

| 风险 | 影响 | 应对 |
|---|---|---|
| customtkinter 主题切换不刷新已有图标 | 图标颜色错误 | 主题切换后显式重设图标 |
| CTkTextbox 占位文字与真实内容混淆 | 统计或启动错误 | 使用独立占位状态，`get_text()` 过滤占位 |
| DPI 缩放导致布局重叠 | 界面错位 | 用 grid + 相对权重，测试 100%/125%/150% |
| PyInstaller 未收集 assets | exe 图标缺失 | `datas` 添加 assets，发布前验证 exe |
| Lucide 许可证遗漏 | 合规问题 | 打包 `assets/icons/LICENSE` 与来源 README |
| engine `randomize` 改动引入回归 | 打字节奏异常 | 默认 True，保留原逻辑，手动回归 |
| 图标 PNG 体积过大 | 包体增大 | 只用必要图标，40–64px 源图，PNG 压缩 |

## 14. 已确认决策

- 产品定位：通用文字 + 场景预设
- 交互骨架：编辑器 + 底部控制栏
- 视觉方向：清爽浅色 + 深色模式
- 预设：文章 / 作业、代码
- 图标：Lucide（ISC）
- 本次不增加全局热键、托盘、历史、文件导入
- 文章预设默认不跳过缩进；代码预设默认跳过缩进
