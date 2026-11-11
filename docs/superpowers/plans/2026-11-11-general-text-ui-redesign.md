# 自动打字 2.0.0 通用文字与界面重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把自动打字从代码输入工具扩展为通用文字输入工具，并完成现代浅色/深色界面、场景预设、开源图标和状态流重构。

**Architecture:** 保留现有 `TypingEngine` 的逐字输入能力，只增加 `randomize` 和完成/停止回调区分。UI 拆成主题、预设、图标、提示、编辑器、控制栏和主窗口七个职责清晰的部分，所有颜色和字体集中在 `ui/theme.py`。

**Tech Stack:** Python 3.10+（开发环境 3.13）、customtkinter 5.2.2、Pillow、Windows SendInput、unittest、Lucide 图标（ISC）、PyInstaller。

**Spec:** `docs/superpowers/specs/2026-11-11-general-text-ui-redesign-design.md`

## Global Constraints

- 运行平台：Windows 10 / 11。
- 开发与验证 Python：`C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe`。
- 新增运行时依赖只允许 `Pillow>=10.0.0`；不要把 Node、sharp 或图标生成工具加入运行时。
- 图标使用 Lucide 1.72.0，许可证为 ISC；必须随仓库保存 `assets/icons/LICENSE`。
- 默认预设为“文章 / 作业”：字体 Microsoft YaHei UI 14，90 ms/字，倒计时 3 秒，`skip_indent=False`。
- 代码预设：字体 Cascadia Code / Cascadia Mono / Consolas 13，150 ms/字，倒计时 3 秒，`skip_indent=True`。
- 所有颜色使用 `ui.theme.COLORS` 中的 `(light, dark)` 元组，不在 UI 组件中散落十六进制颜色。
- 不实现全局热键、托盘、输入历史、文件导入、聊天/表单预设。
- 未经用户明确要求，不执行 `git commit` 或 `git push`；每个任务用测试和 diff 检查作为检查点。
- 每完成一个任务，运行该任务列出的测试；失败时先修复，不进入下一任务。

---

### Task 1: 格式化函数与场景预设

**Files:**
- Create: `ui/formatting.py`
- Create: `ui/presets.py`
- Create: `tests/__init__.py`
- Create: `tests/test_formatting.py`
- Create: `tests/test_presets.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `TextStats.from_text(text: str, speed_ms: int, countdown_seconds: int) -> TextStats`
  - `count_chars(text: str) -> int`
  - `count_lines(text: str) -> int`
  - `characters_per_minute(speed_ms: int) -> int`
  - `estimate_seconds(text: str, speed_ms: int, countdown_seconds: int) -> int`
  - `format_duration(seconds: int) -> str`
  - `speed_band(speed_ms: int) -> str`
  - `Preset` dataclass、`ARTICLE_PRESET`、`CODE_PRESET`、`PRESETS`、`PRESET_BY_KEY`、`DEFAULT_PRESET`

- [ ] **Step 1: Write the failing tests**

`tests/test_formatting.py`:

```python
import unittest

from ui.formatting import (
    TextStats,
    characters_per_minute,
    count_chars,
    count_lines,
    estimate_seconds,
    format_duration,
    speed_band,
)


class FormattingTests(unittest.TestCase):
    def test_count_chars_ignores_carriage_return(self):
        self.assertEqual(count_chars("a\r\nb"), 3)

    def test_count_lines(self):
        self.assertEqual(count_lines(""), 0)
        self.assertEqual(count_lines("abc"), 1)
        self.assertEqual(count_lines("a\nb\nc"), 3)

    def test_characters_per_minute(self):
        self.assertEqual(characters_per_minute(150), 400)
        self.assertEqual(characters_per_minute(90), 667)

    def test_estimate_seconds_includes_countdown(self):
        self.assertEqual(estimate_seconds("a" * 100, 100, 3), 13)

    def test_format_duration(self):
        self.assertEqual(format_duration(0), "0 秒")
        self.assertEqual(format_duration(45), "45 秒")
        self.assertEqual(format_duration(60), "1 分")
        self.assertEqual(format_duration(80), "1 分 20 秒")

    def test_speed_band_boundaries(self):
        self.assertEqual(speed_band(30), "快速")
        self.assertEqual(speed_band(79), "快速")
        self.assertEqual(speed_band(80), "自然")
        self.assertEqual(speed_band(149), "自然")
        self.assertEqual(speed_band(150), "稳健")
        self.assertEqual(speed_band(249), "稳健")
        self.assertEqual(speed_band(250), "慢速")

    def test_text_stats(self):
        stats = TextStats.from_text("abc\ndef", 100, 3)
        self.assertEqual(stats.chars, 7)
        self.assertEqual(stats.lines, 2)
        self.assertEqual(stats.estimated_seconds, 4)


if __name__ == "__main__":
    unittest.main()
```

`tests/test_presets.py`:

```python
import unittest

from ui.presets import ARTICLE_PRESET, CODE_PRESET, DEFAULT_PRESET, PRESET_BY_KEY, PRESETS


class PresetTests(unittest.TestCase):
    def test_default_is_article(self):
        self.assertIs(DEFAULT_PRESET, ARTICLE_PRESET)

    def test_article_defaults(self):
        self.assertEqual(ARTICLE_PRESET.speed_ms, 90)
        self.assertEqual(ARTICLE_PRESET.font_size, 14)
        self.assertFalse(ARTICLE_PRESET.skip_indent)

    def test_code_defaults(self):
        self.assertEqual(CODE_PRESET.speed_ms, 150)
        self.assertEqual(CODE_PRESET.font_size, 13)
        self.assertTrue(CODE_PRESET.skip_indent)

    def test_lookup(self):
        self.assertEqual(PRESET_BY_KEY["article"], ARTICLE_PRESET)
        self.assertEqual(PRESET_BY_KEY["code"], CODE_PRESET)
        self.assertEqual([p.key for p in PRESETS], ["article", "code"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_formatting tests.test_presets -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'ui.formatting'`.

- [ ] **Step 3: Implement `ui/formatting.py`**

```python
"""文本统计、速度换算和时长格式化。"""

from __future__ import annotations

from dataclasses import dataclass


def normalize_text(text: str) -> str:
    """移除 Windows 回车符，保留换行符。"""
    return text.replace("\r", "")


def count_chars(text: str) -> int:
    """统计字符数，排除 \\r。"""
    return len(normalize_text(text))


def count_lines(text: str) -> int:
    """统计行数；空文本为 0。"""
    normalized = normalize_text(text)
    if not normalized:
        return 0
    return normalized.count("\n") + 1


def characters_per_minute(speed_ms: int) -> int:
    """把每字毫秒数换算成每分钟字符数。"""
    if speed_ms <= 0:
        raise ValueError("speed_ms must be positive")
    return round(60000 / speed_ms)


def estimate_seconds(text: str, speed_ms: int, countdown_seconds: int) -> int:
    """粗略估算总用时；不计换行额外停顿和跳过缩进。"""
    typing_seconds = count_chars(text) * speed_ms / 1000
    return round(typing_seconds) + max(0, countdown_seconds)


def format_duration(seconds: int) -> str:
    """把秒数格式化为中文时长。"""
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds} 秒"
    minutes, remainder = divmod(seconds, 60)
    if remainder == 0:
        return f"{minutes} 分"
    return f"{minutes} 分 {remainder} 秒"


def speed_band(speed_ms: int) -> str:
    """把速度映射为人类可读的节奏标签。"""
    if speed_ms < 80:
        return "快速"
    if speed_ms < 150:
        return "自然"
    if speed_ms < 250:
        return "稳健"
    return "慢速"


@dataclass(frozen=True)
class TextStats:
    """编辑器文本的展示统计。"""

    chars: int
    lines: int
    estimated_seconds: int

    @classmethod
    def from_text(cls, text: str, speed_ms: int, countdown_seconds: int) -> "TextStats":
        return cls(
            chars=count_chars(text),
            lines=count_lines(text),
            estimated_seconds=estimate_seconds(text, speed_ms, countdown_seconds),
        )
```

- [ ] **Step 4: Implement `ui/presets.py`**

```python
"""文章 / 代码场景预设。"""

from __future__ import annotations

from dataclasses import dataclass


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


ARTICLE_PRESET = Preset(
    key="article",
    label="文章 / 作业",
    font_candidates=("Microsoft YaHei UI", "Microsoft YaHei"),
    font_size=14,
    speed_ms=90,
    countdown_seconds=3,
    skip_indent=False,
    randomize=True,
)

CODE_PRESET = Preset(
    key="code",
    label="代码",
    font_candidates=("Cascadia Code", "Cascadia Mono", "Consolas"),
    font_size=13,
    speed_ms=150,
    countdown_seconds=3,
    skip_indent=True,
    randomize=True,
)

PRESETS = (ARTICLE_PRESET, CODE_PRESET)
PRESET_BY_KEY = {preset.key: preset for preset in PRESETS}
DEFAULT_PRESET = ARTICLE_PRESET
```

- [ ] **Step 5: Run tests to verify they pass**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_formatting tests.test_presets -v
```

Expected: 11 tests PASS.

- [ ] **Step 6: Checkpoint**

Run `git diff --check`. Do not commit unless the user asks.

---

### Task 2: 引擎生命周期与自然节奏开关

**Files:**
- Modify: `engine/typer.py`
- Create: `tests/test_typer_state.py`

**Interfaces:**
- Consumes: `TypingEngine`
- Produces:
  - `TypingEngine.on_stopped: Callable[[], None] | None`
  - `TypingEngine.start(..., randomize: bool = True)`
  - `TypingEngine._finish(completed: bool)`
  - 自然完成只触发 `on_finished`；用户停止只触发 `on_stopped`

- [ ] **Step 1: Write the failing tests**

`tests/test_typer_state.py`:

```python
import inspect
import unittest

from engine.typer import TypingEngine


class TypingEngineStateTests(unittest.TestCase):
    def test_start_exposes_randomize(self):
        signature = inspect.signature(TypingEngine.start)
        self.assertIn("randomize", signature.parameters)
        self.assertTrue(signature.parameters["randomize"].default)

    def test_completed_finish_calls_finished_only(self):
        engine = TypingEngine()
        events = []
        engine.on_finished = lambda: events.append("finished")
        engine.on_stopped = lambda: events.append("stopped")

        engine._finish(completed=True)

        self.assertEqual(events, ["finished"])
        self.assertFalse(engine.is_running)

    def test_stopped_finish_calls_stopped_only(self):
        engine = TypingEngine()
        events = []
        engine.on_finished = lambda: events.append("finished")
        engine.on_stopped = lambda: events.append("stopped")

        engine._finish(completed=False)

        self.assertEqual(events, ["stopped"])
        self.assertFalse(engine.is_running)

    def test_finish_is_idempotent(self):
        engine = TypingEngine()
        events = []
        engine.on_finished = lambda: events.append("finished")
        engine.on_stopped = lambda: events.append("stopped")

        engine._finish(completed=False)
        engine._finish(completed=True)

        self.assertEqual(events, ["stopped"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_typer_state -v
```

Expected: FAIL because `randomize` and `_finish` do not exist.

- [ ] **Step 3: Modify `engine/typer.py`**

Apply these changes:

```python
# __init__ 中新增
self._finished = False
self.on_stopped: callable | None = None

# start 签名新增 randomize
def start(self, text: str, base_delay_ms: int = 50, countdown_seconds: int = 3,
          skip_indent: bool = True, randomize: bool = True) -> None:
    if self._running:
        return
    self._running = True
    self._paused = False
    self._stopped = False
    self._finished = False
    self._thread = threading.Thread(
        target=self._typing_loop,
        args=(text, base_delay_ms / 1000.0, countdown_seconds, skip_indent, randomize),
        daemon=True,
    )
    self._thread.start()

# stop 不再直接修改状态后静默返回；调用 _finish 统一收口
def stop(self) -> None:
    if not self._running:
        return
    self._stopped = True
    self._paused = False
    self._finish(completed=False)

# _typing_loop 签名新增 randomize
def _typing_loop(self, text: str, base_delay: float, countdown: int,
                 skip_indent: bool, randomize: bool) -> None:
    ...

# 所有因 stopped 提前返回的 self._finish() 改为 self._finish(completed=False)
# 文件末尾自然完成改为 self._finish(completed=True)

# 延迟计算
if randomize:
    variation = base_delay * 0.3
    delay = base_delay + random.uniform(-variation, variation)
else:
    delay = base_delay
delay = max(delay, 0.005)

# 替换原 _finish
def _finish(self, completed: bool) -> None:
    """结束输入；completed=False 表示用户停止或取消。"""
    if self._finished:
        return
    self._finished = True
    self._running = False
    self._paused = False
    if completed:
        if self.on_finished:
            self.on_finished()
    else:
        if self.on_stopped:
            self.on_stopped()
```

同时删除 `stop()` 和 `_finish()` 中原有的 `on_status_change("已停止")` / `on_status_change("等待开始...")`，终态文案统一由 UI 设置。

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_typer_state -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Run existing import check**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -c "import main; print('import main: OK')"
```

Expected: `import main: OK`.

- [ ] **Step 6: Checkpoint**

Run `git diff --check`. Do not commit unless the user asks.

---

### Task 3: 主题、资源路径、图标与提示

**Files:**
- Create: `utils/resources.py`
- Create: `ui/theme.py`
- Create: `ui/icons.py`
- Create: `ui/tooltip.py`
- Create: `tools/package.json`
- Create: `tools/render_icons.mjs`
- Modify: `.gitignore`（忽略 `tools/node_modules/`）
- Create: `assets/icons/README.md`
- Create: `assets/icons/LICENSE`
- Create: `assets/icons/light/*.png`
- Create: `assets/icons/dark/*.png`
- Create: `assets/icons/on_accent/*.png`
- Create: `assets/app.ico`
- Test: `tests/test_resources.py`

**Interfaces:**
- Consumes: `Pillow`、`customtkinter`
- Produces:
  - `resource_path(relative: str) -> Path`
  - `COLORS: dict[str, tuple[str, str]]`
  - `color(name: str, mode: str | None = None) -> str`
  - `get_font(candidates: tuple[str, ...], size: int, weight: str = "normal") -> tuple`
  - `apply_appearance(mode: str) -> None`
  - `get_icon(name: str, variant: str = "theme", size: tuple[int, int] = (18, 18)) -> ctk.CTkImage | None`
  - `Tooltip(widget, text: str, delay: int = 400)`

- [ ] **Step 1: Write the failing resource test**

`tests/test_resources.py`:

```python
import unittest
from pathlib import Path

from utils.resources import resource_path


class ResourceTests(unittest.TestCase):
    def test_resource_path_resolves_project_root(self):
        self.assertEqual(resource_path("assets"), Path(__file__).resolve().parents[1] / "assets")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_resources -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'utils.resources'`.

- [ ] **Step 3: Implement `utils/resources.py`**

```python
"""开发环境与 PyInstaller 打包环境的资源路径解析。"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """返回资源绝对路径；打包后从 sys._MEIPASS 读取。"""
    if getattr(sys, "frozen", False):
        root = Path(sys._MEIPASS)
    else:
        root = Path(__file__).resolve().parents[1]
    return root / relative
```

- [ ] **Step 4: Create the icon generation tool**

`tools/package.json`:

```json
{
  "name": "automatic-typing-icons",
  "private": true,
  "type": "module",
  "dependencies": {
    "sharp": "0.35.5"
  }
}
```

`tools/render_icons.mjs`:

```javascript
import { mkdir } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const VERSION = "1.72.0";
const BASE = `https://unpkg.com/lucide-static@${VERSION}/icons`;
const OUT = "assets/icons";
const ICONS = [
  "keyboard",
  "clipboard",
  "trash-2",
  "play",
  "pause",
  "square",
  "x",
  "pin",
  "pin-off",
  "sun",
  "moon",
  "chevron-down",
  "chevron-up",
];
const VARIANTS = {
  light: "#475569",
  dark: "#CBD5E1",
  on_accent: "#FFFFFF",
};

async function fetchSvg(name) {
  const response = await fetch(`${BASE}/${name}.svg`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${name}: ${response.status}`);
  }
  return response.text();
}

for (const variant of Object.keys(VARIANTS)) {
  await mkdir(path.join(OUT, variant), { recursive: true });
}

for (const name of ICONS) {
  const svg = await fetchSvg(name);
  for (const [variant, color] of Object.entries(VARIANTS)) {
    const colored = svg.replaceAll("currentColor", color);
    const output = path.join(OUT, variant, `${name}.png`);
    await sharp(Buffer.from(colored), { density: 384 })
      .resize(40, 40)
      .png()
      .toFile(output);
  }
}

const keyboardSvg = (await fetchSvg("keyboard")).replaceAll("currentColor", "#FFFFFF");
const keyboardPng = await sharp(Buffer.from(keyboardSvg), { density: 384 })
  .resize(128, 128)
  .png()
  .toBuffer();

const background = Buffer.from(`
  <svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
    <rect width="256" height="256" rx="56" fill="#4F46E5"/>
  </svg>
`);

await sharp(background)
  .composite([{ input: keyboardPng, gravity: "center" }])
  .png()
  .toFile("assets/app.png");

console.log(`Rendered ${ICONS.length} icons in 3 variants.`);
```

- [ ] **Step 5: Ignore icon tool dependencies**

在 `.gitignore` 中追加：

```text
# 图标生成工具依赖
tools/node_modules/
```

- [ ] **Step 6: Generate icon assets**

Run:

```powershell
npm install --prefix tools
node tools/render_icons.mjs
```

Then create the ICO with Pillow:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -c "from PIL import Image; img=Image.open('assets/app.png'); img.save('assets/app.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
```

Expected:

- `assets/icons/light/`, `dark/`, `on_accent/` each contain 13 PNGs
- `assets/app.ico` exists
- `assets/app.png` exists（可以保留作为源图）

- [ ] **Step 7: Add Lucide license and attribution**

Run:

```powershell
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/lucide-icons/lucide/main/LICENSE' -OutFile 'assets/icons/LICENSE'
```

Create `assets/icons/README.md`:

````markdown
# Lucide Icons

- Source: https://lucide.dev/
- Package: `lucide-static@1.72.0`
- License: ISC License (see `LICENSE`); some Feather-derived icons are MIT
- Variants:
  - `light/`: `#475569`
  - `dark/`: `#CBD5E1`
  - `on_accent/`: `#FFFFFF`
- Regenerate:

```bash
npm install --prefix tools
node tools/render_icons.mjs
```
````

- [ ] **Step 8: Implement `ui/theme.py`**

```python
"""颜色 token、字体选择和外观模式。"""

from __future__ import annotations

import tkinter.font as tkfont

import customtkinter as ctk

COLORS: dict[str, tuple[str, str]] = {
    "bg": ("#F6F7F9", "#0F172A"),
    "surface": ("#FFFFFF", "#111827"),
    "surface_alt": ("#F3F4F6", "#1F2937"),
    "text": ("#111827", "#E5E7EB"),
    "text_muted": ("#6B7280", "#94A3B8"),
    "text_subtle": ("#94A3B8", "#64748B"),
    "border": ("#E5E7EB", "#263244"),
    "border_strong": ("#D1D5DB", "#334155"),
    "accent": ("#4F46E5", "#6366F1"),
    "accent_hover": ("#4338CA", "#4F46E5"),
    "accent_text": ("#FFFFFF", "#FFFFFF"),
    "danger": ("#DC2626", "#F87171"),
    "success": ("#059669", "#34D399"),
}

UI_FONT_CANDIDATES = ("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI")
ARTICLE_FONT_CANDIDATES = ("Microsoft YaHei UI", "Microsoft YaHei")
CODE_FONT_CANDIDATES = ("Cascadia Code", "Cascadia Mono", "Consolas")


def _families() -> set[str]:
    try:
        return set(tkfont.families())
    except Exception:
        return set()


def get_font(candidates: tuple[str, ...], size: int, weight: str = "normal") -> tuple:
    """返回系统中第一个可用字体；全部不可用时退回 Segoe UI。"""
    families = _families()
    for family in candidates:
        if family in families:
            return (family, size, weight)
    return ("Segoe UI", size, weight)


def color(name: str, mode: str | None = None) -> str:
    """返回某个 token 在当前或指定外观模式下的单色值。"""
    light, dark = COLORS[name]
    current = (mode or ctk.get_appearance_mode()).lower()
    return dark if current == "dark" else light


def apply_appearance(mode: str) -> None:
    ctk.set_appearance_mode(mode)
```

- [ ] **Step 9: Implement `ui/icons.py`**

```python
"""Lucide PNG 图标加载与缓存。"""

from __future__ import annotations

from functools import lru_cache

from PIL import Image
import customtkinter as ctk

from utils.resources import resource_path


@lru_cache(maxsize=256)
def _load(path: str) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGBA").copy()


def get_icon(
    name: str,
    variant: str = "theme",
    size: tuple[int, int] = (18, 18),
) -> ctk.CTkImage | None:
    """加载图标；缺失或损坏时返回 None，调用方退化为文字。"""
    try:
        if variant == "theme":
            light = _load(str(resource_path(f"assets/icons/light/{name}.png")))
            dark = _load(str(resource_path(f"assets/icons/dark/{name}.png")))
            return ctk.CTkImage(light_image=light, dark_image=dark, size=size)

        folder = variant if variant in {"light", "dark", "on_accent"} else "light"
        image = _load(str(resource_path(f"assets/icons/{folder}/{name}.png")))
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    except Exception:
        return None
```

- [ ] **Step 10: Implement `ui/tooltip.py`**

```python
"""轻量图标按钮提示。"""

from __future__ import annotations

import tkinter as tk

from ui.theme import color


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id: str | None = None
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None) -> None:
        self._cancel()
        self._after_id = self.widget.after(self.delay, self._show)

    def _cancel(self) -> None:
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self) -> None:
        if self._tip is not None:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self._tip,
            text=self.text,
            background=color("surface_alt"),
            foreground=color("text"),
            padx=8,
            pady=4,
            font=("Microsoft YaHei UI", 10),
        )
        label.pack()

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None
```

- [ ] **Step 11: Run tests and imports**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_resources -v
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -c "from ui.theme import COLORS; from ui.icons import get_icon; from ui.tooltip import Tooltip; print('ui imports: OK')"
```

Expected: test PASS and `ui imports: OK`.

- [ ] **Step 12: Checkpoint**

Run `git diff --check`. Do not commit unless the user asks.

---

### Task 4: 编辑器卡片

**Files:**
- Modify: `ui/text_panel.py`
- Create: `tests/test_text_panel.py`

**Interfaces:**
- Consumes: `ui.theme`, `ui.icons`, `ui.tooltip`
- Produces:
  - `TextPanel(master, on_text_changed: callable | None = None, **kwargs)`
  - `TextPanel.get_text() -> str`
  - `TextPanel.set_text(text: str) -> None`
  - `TextPanel.clear() -> None`
  - `TextPanel.set_read_only(value: bool) -> None`
  - `TextPanel.set_editor_font(font: tuple) -> None`
  - `TextPanel.focus_editor() -> None`
  - `TextPanel.set_stats(chars: int, lines: int) -> None`
  - `TextPanel.on_read_clipboard: callable | None`
  - `TextPanel.on_clear: callable | None`

- [ ] **Step 1: Write the failing smoke test**

`tests/test_text_panel.py`:

```python
import unittest

import customtkinter as ctk

from ui.text_panel import TextPanel


class TextPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_placeholder_is_not_content(self):
        panel = TextPanel(self.root)
        self.assertEqual(panel.get_text(), "")
        panel.destroy()

    def test_set_and_clear_text(self):
        panel = TextPanel(self.root)
        panel.set_text("hello")
        self.assertEqual(panel.get_text(), "hello")
        panel.clear()
        self.assertEqual(panel.get_text(), "")
        panel.destroy()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_text_panel -v
```

Expected: FAIL because `TextPanel` has no placeholder-aware `get_text`.

- [ ] **Step 3: Replace `ui/text_panel.py`**

```python
"""文本编辑器卡片：输入区、剪贴板/清空工具栏和统计。"""

from __future__ import annotations

import customtkinter as ctk

from ui.icons import get_icon
from ui.theme import ARTICLE_FONT_CANDIDATES, COLORS, get_font
from ui.tooltip import Tooltip


class TextPanel(ctk.CTkFrame):
    """编辑器卡片。"""

    PLACEHOLDER = "在这里输入或粘贴文字…"

    def __init__(self, master, on_text_changed: callable | None = None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=12,
            **kwargs,
        )
        self._on_text_changed = on_text_changed
        self._placeholder_active = False
        self.on_read_clipboard: callable | None = None
        self.on_clear: callable | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(
            self,
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
            wrap="word",
            font=get_font(ARTICLE_FONT_CANDIDATES, 14),
            text_color=COLORS["text"],
        )
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 4))

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.btn_clipboard = self._icon_button(
            toolbar, "clipboard", "读取剪贴板", lambda: self.on_read_clipboard and self.on_read_clipboard()
        )
        self.btn_clipboard.pack(side="left")

        self.btn_clear = self._icon_button(
            toolbar, "trash-2", "清空", lambda: self.on_clear and self.on_clear()
        )
        self.btn_clear.pack(side="left", padx=(4, 0))

        self.stats_label = ctk.CTkLabel(
            toolbar,
            text="0 字 · 0 行",
            font=("Microsoft YaHei UI", 12),
            text_color=COLORS["text_muted"],
        )
        self.stats_label.pack(side="right", padx=(0, 4))

        self.textbox.bind("<FocusIn>", self._on_focus_in, add="+")
        self.textbox.bind("<FocusOut>", self._on_focus_out, add="+")
        self.textbox.bind("<<Modified>>", self._on_modified, add="+")
        self._show_placeholder()

    def _icon_button(self, master, icon: str, tooltip: str, command) -> ctk.CTkButton:
        button = ctk.CTkButton(
            master,
            text="",
            image=get_icon(icon, "theme"),
            width=32,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            command=command,
        )
        Tooltip(button, tooltip)
        return button

    def _show_placeholder(self) -> None:
        if self.get_text():
            return
        self._placeholder_active = True
        self.textbox.configure(text_color=COLORS["text_subtle"])
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", self.PLACEHOLDER)

    def _hide_placeholder(self) -> None:
        if not self._placeholder_active:
            return
        self._placeholder_active = False
        self.textbox.delete("1.0", "end")
        self.textbox.configure(text_color=COLORS["text"])

    def _on_focus_in(self, _event=None) -> None:
        self._hide_placeholder()

    def _on_focus_out(self, _event=None) -> None:
        if not self.textbox.get("1.0", "end-1c"):
            self._show_placeholder()

    def _on_modified(self, _event=None) -> None:
        try:
            self.textbox._textbox.edit_modified(False)
        except Exception:
            pass
        if not self._placeholder_active:
            self._notify_changed()

    def _notify_changed(self) -> None:
        if self._on_text_changed:
            self._on_text_changed()

    def get_text(self) -> str:
        if self._placeholder_active:
            return ""
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text: str) -> None:
        self._placeholder_active = False
        self.textbox.configure(text_color=COLORS["text"])
        self.textbox.delete("1.0", "end")
        if text:
            self.textbox.insert("1.0", text)
        else:
            self._show_placeholder()
        self._notify_changed()

    def clear(self) -> None:
        self.set_text("")

    def set_read_only(self, value: bool) -> None:
        self.textbox.configure(state="disabled" if value else "normal")

    def set_editor_font(self, font: tuple) -> None:
        self.textbox.configure(font=font)

    def focus_editor(self) -> None:
        self.textbox.focus_set()

    def set_stats(self, chars: int, lines: int) -> None:
        self.stats_label.configure(text=f"{chars} 字 · {lines} 行")
```

- [ ] **Step 4: Run smoke tests**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_text_panel -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Checkpoint**

Run `git diff --check`. Do not commit unless the user asks.

---

### Task 5: 场景栏与控制卡片

**Files:**
- Modify: `ui/control_panel.py`
- Create: `tests/test_control_panel.py`

**Interfaces:**
- Consumes: `ui.presets`, `ui.icons`, `ui.theme`, `ui.tooltip`
- Produces:
  - `PresetBar(master, on_change: callable, **kwargs)`
  - `PresetBar.set_selected(key: str) -> None`
  - `PresetBar.set_enabled(enabled: bool) -> None`
  - `ControlPanel(master, on_primary: callable, on_stop: callable, on_settings_change: callable | None = None, **kwargs)`
  - `ControlPanel.speed_ms: int`
  - `ControlPanel.countdown_seconds: int`
  - `ControlPanel.skip_indent: bool`
  - `ControlPanel.randomize: bool`
  - `ControlPanel.apply_preset(preset) -> None`
  - `ControlPanel.set_state(state: str) -> None`
  - `ControlPanel.set_status(text: str, tone: str = "muted") -> None`
  - `ControlPanel.set_progress(current: int, total: int) -> None`
  - `ControlPanel.refresh_icons() -> None`

- [ ] **Step 1: Write the failing smoke test**

`tests/test_control_panel.py`:

```python
import unittest

import customtkinter as ctk

from ui.control_panel import ControlPanel, PresetBar
from ui.presets import ARTICLE_PRESET, CODE_PRESET


class ControlPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_preset_application(self):
        panel = ControlPanel(self.root, on_primary=lambda: None, on_stop=lambda: None)
        panel.apply_preset(CODE_PRESET)
        self.assertEqual(panel.speed_ms, 150)
        self.assertTrue(panel.skip_indent)
        panel.apply_preset(ARTICLE_PRESET)
        self.assertEqual(panel.speed_ms, 90)
        self.assertFalse(panel.skip_indent)
        panel.destroy()

    def test_state_changes_primary_text(self):
        panel = ControlPanel(self.root, on_primary=lambda: None, on_stop=lambda: None)
        panel.set_state("typing")
        self.assertEqual(panel.btn_primary.cget("text"), "暂停")
        panel.set_state("idle")
        self.assertEqual(panel.btn_primary.cget("text"), "开始打字")
        panel.destroy()

    def test_preset_bar_returns_key(self):
        selected = []
        bar = PresetBar(self.root, on_change=selected.append)
        bar.set_selected("code")
        self.assertEqual(bar.segmented.get(), "代码")
        bar.destroy()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_control_panel -v
```

Expected: FAIL because `ControlPanel` does not expose the new API.

- [ ] **Step 3: Replace `ui/control_panel.py`**

```python
"""场景切换、节奏参数、传输控制和进度。"""

from __future__ import annotations

import customtkinter as ctk

from ui.formatting import characters_per_minute, speed_band
from ui.icons import get_icon
from ui.presets import PRESETS, Preset
from ui.theme import COLORS, UI_FONT_CANDIDATES, get_font
from ui.tooltip import Tooltip

COUNTDOWN_OPTIONS = ("1 秒", "3 秒", "5 秒", "10 秒")


class PresetBar(ctk.CTkFrame):
    def __init__(self, master, on_change: callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._labels = {preset.label: preset.key for preset in PRESETS}

        ctk.CTkLabel(
            self,
            text="场景",
            font=get_font(UI_FONT_CANDIDATES, 13),
            text_color=COLORS["text_muted"],
        ).pack(side="left", padx=(2, 10))

        self.segmented = ctk.CTkSegmentedButton(
            self,
            values=[preset.label for preset in PRESETS],
            command=self._changed,
            font=get_font(UI_FONT_CANDIDATES, 13),
            height=32,
            corner_radius=8,
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"],
            text_color=COLORS["text"],
        )
        self.segmented.pack(side="left")

    def _changed(self, label: str) -> None:
        key = self._labels.get(label)
        if key:
            self._on_change(key)

    def set_selected(self, key: str) -> None:
        for preset in PRESETS:
            if preset.key == key:
                self.segmented.set(preset.label)
                return

    def set_enabled(self, enabled: bool) -> None:
        self.segmented.configure(state="normal" if enabled else "disabled")


class ControlPanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_primary: callable,
        on_stop: callable,
        on_settings_change: callable | None = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=12,
            **kwargs,
        )
        self._on_primary = on_primary
        self._on_stop = on_stop
        self._on_settings_change = on_settings_change
        self._state = "idle"
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        speed_row = ctk.CTkFrame(self, fg_color="transparent")
        speed_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))
        speed_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            speed_row,
            text="节奏",
            font=get_font(UI_FONT_CANDIDATES, 13),
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.speed_slider = ctk.CTkSlider(
            speed_row,
            from_=30,
            to=500,
            number_of_steps=94,
            command=self._on_speed_change,
            fg_color=COLORS["surface_alt"],
            progress_color=COLORS["accent"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.speed_slider.set(90)
        self.speed_slider.grid(row=0, column=1, sticky="ew")

        self.speed_value = ctk.CTkLabel(
            speed_row,
            text="",
            font=get_font(UI_FONT_CANDIDATES, 12),
            text_color=COLORS["text"],
            width=190,
            anchor="e",
        )
        self.speed_value.grid(row=0, column=2, sticky="e", padx=(10, 0))

        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.grid(row=1, column=0, sticky="ew", padx=14, pady=(10, 0))
        action_row.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            action_row,
            text="倒计时",
            font=get_font(UI_FONT_CANDIDATES, 13),
            text_color=COLORS["text_muted"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.countdown_menu = ctk.CTkOptionMenu(
            action_row,
            values=list(COUNTDOWN_OPTIONS),
            width=88,
            height=32,
            corner_radius=8,
            font=get_font(UI_FONT_CANDIDATES, 12),
            fg_color=COLORS["surface_alt"],
            button_color=COLORS["surface_alt"],
            button_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self._on_countdown_change,
        )
        self.countdown_menu.set("3 秒")
        self.countdown_menu.grid(row=0, column=1, sticky="w")

        self.btn_primary = ctk.CTkButton(
            action_row,
            text="开始打字",
            image=get_icon("play", "on_accent"),
            compound="left",
            width=132,
            height=38,
            corner_radius=10,
            font=get_font(UI_FONT_CANDIDATES, 14, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"],
            command=lambda: self._on_primary(),
        )
        self.btn_primary.grid(row=0, column=3, sticky="e", padx=(10, 0))

        self.btn_stop = ctk.CTkButton(
            action_row,
            text="",
            image=get_icon("square", "theme"),
            width=38,
            height=38,
            corner_radius=10,
            font=get_font(UI_FONT_CANDIDATES, 13),
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            command=lambda: self._on_stop(),
        )
        self.btn_stop.grid(row=0, column=4, sticky="e", padx=(8, 0))
        Tooltip(self.btn_stop, "停止")

        self.progress = ctk.CTkProgressBar(
            self,
            height=8,
            corner_radius=4,
            fg_color=COLORS["surface_alt"],
            progress_color=COLORS["accent"],
        )
        self.progress.grid(row=2, column=0, sticky="ew", padx=14, pady=(12, 0))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=get_font(UI_FONT_CANDIDATES, 12),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self.status_label.grid(row=3, column=0, sticky="ew", padx=14, pady=(6, 0))

        self.btn_advanced = ctk.CTkButton(
            self,
            text="高级设置",
            image=get_icon("chevron-down", "theme"),
            compound="left",
            anchor="w",
            width=100,
            height=28,
            corner_radius=6,
            font=get_font(UI_FONT_CANDIDATES, 12),
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["text_muted"],
            command=self._toggle_advanced,
        )
        self.btn_advanced.grid(row=4, column=0, sticky="w", padx=12, pady=(4, 10))

        self.advanced_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.advanced_frame.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 12))
        self.advanced_frame.grid_columnconfigure(0, weight=1)

        self.skip_var = ctk.BooleanVar(value=False)
        self.skip_switch = ctk.CTkSwitch(
            self.advanced_frame,
            text="跳过行首缩进（依赖目标编辑器自动缩进）",
            variable=self.skip_var,
            font=get_font(UI_FONT_CANDIDATES, 12),
            text_color=COLORS["text_muted"],
            progress_color=COLORS["accent"],
            command=self._notify_settings,
        )
        self.skip_switch.grid(row=0, column=0, sticky="w", pady=2)

        self.random_var = ctk.BooleanVar(value=True)
        self.random_switch = ctk.CTkSwitch(
            self.advanced_frame,
            text="自然节奏（±30% 随机延迟）",
            variable=self.random_var,
            font=get_font(UI_FONT_CANDIDATES, 12),
            text_color=COLORS["text_muted"],
            progress_color=COLORS["accent"],
            command=self._notify_settings,
        )
        self.random_switch.grid(row=1, column=0, sticky="w", pady=2)

        self.advanced_frame.grid_remove()
        self._advanced_visible = False
        self.refresh_speed_label()
        self.set_state("idle")

    def _toggle_advanced(self) -> None:
        self._advanced_visible = not self._advanced_visible
        if self._advanced_visible:
            self.advanced_frame.grid()
            self.btn_advanced.configure(text="收起高级设置", image=get_icon("chevron-up", "theme"))
        else:
            self.advanced_frame.grid_remove()
            self.btn_advanced.configure(text="高级设置", image=get_icon("chevron-down", "theme"))

    def _on_speed_change(self, value: float) -> None:
        self.refresh_speed_label()
        self._notify_settings()

    def refresh_speed_label(self) -> None:
        speed = self.speed_ms
        cpm = characters_per_minute(speed)
        self.speed_value.configure(text=f"{speed_band(speed)} · {speed} ms/字 · 约 {cpm} 字/分")

    def _on_countdown_change(self, _value: str) -> None:
        self._notify_settings()

    def _notify_settings(self) -> None:
        if self._on_settings_change:
            self._on_settings_change()

    @property
    def speed_ms(self) -> int:
        return int(self.speed_slider.get())

    @property
    def countdown_seconds(self) -> int:
        text = self.countdown_menu.get()
        return int(text.split(" ")[0])

    @property
    def skip_indent(self) -> bool:
        return bool(self.skip_var.get())

    @property
    def randomize(self) -> bool:
        return bool(self.random_var.get())

    def apply_preset(self, preset: Preset) -> None:
        self.speed_slider.set(preset.speed_ms)
        self.countdown_menu.set(f"{preset.countdown_seconds} 秒")
        self.skip_var.set(preset.skip_indent)
        self.random_var.set(preset.randomize)
        self.refresh_speed_label()
        self._notify_settings()

    def set_state(self, state: str) -> None:
        self._state = state
        running = state in {"countdown", "typing", "paused"}

        if state == "idle":
            text, icon = "开始打字", "play"
        elif state == "countdown":
            text, icon = "取消", "x"
        elif state == "typing":
            text, icon = "暂停", "pause"
        elif state == "paused":
            text, icon = "继续", "play"
        else:
            text, icon = "再次开始", "play"

        self.btn_primary.configure(
            text=text,
            image=get_icon(icon, "on_accent"),
            state="normal",
        )
        if state in {"typing", "paused"}:
            self.btn_stop.grid()
        else:
            self.btn_stop.grid_remove()

        enabled = not running
        self.speed_slider.configure(state="normal" if enabled else "disabled")
        self.countdown_menu.configure(state="normal" if enabled else "disabled")
        self.skip_switch.configure(state="normal" if enabled else "disabled")
        self.random_switch.configure(state="normal" if enabled else "disabled")
        self.btn_advanced.configure(state="normal" if enabled else "disabled")

    def set_status(self, text: str, tone: str = "muted") -> None:
        token = {"muted": "text_muted", "error": "danger", "success": "success"}.get(tone, "text_muted")
        self.status_label.configure(text=text, text_color=COLORS[token])

    def set_progress(self, current: int, total: int) -> None:
        value = 0.0 if total <= 0 else max(0.0, min(1.0, current / total))
        self.progress.set(value)

    def refresh_icons(self) -> None:
        self.set_state(self._state)
        self.btn_advanced.configure(
            image=get_icon("chevron-up" if self._advanced_visible else "chevron-down", "theme")
        )
```

- [ ] **Step 4: Run smoke tests**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest tests.test_control_panel -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Checkpoint**

Run `git diff --check`. Do not commit unless the user asks.

---

### Task 6: 主窗口状态机与打包资源

**Files:**
- Modify: `ui/app.py`
- Modify: `requirements.txt`
- Modify: `build.spec`

**Interfaces:**
- Consumes: `TextPanel`、`PresetBar`、`ControlPanel`、`TypingEngine`、`TextStats`、`get_icon`、`resource_path`
- Produces: 可运行的 `App`

- [ ] **Step 1: Add dependencies and packaging resources**

`requirements.txt`:

```text
customtkinter>=5.2.0
pyperclip>=1.8.2
pyinstaller>=6.0.0
Pillow>=10.0.0
```

`build.spec` 修改：

```python
datas=[('assets', 'assets')],
```

并在 `EXE(...)` 中加入：

```python
icon=str(ROOT / 'assets' / 'app.ico'),
```

- [ ] **Step 2: Replace `ui/app.py`**

```python
"""主窗口：布局、状态机、主题、置顶和引擎回调。"""

from __future__ import annotations

import time

import customtkinter as ctk

from engine.typer import TypingEngine
from ui.control_panel import ControlPanel, PresetBar
from ui.formatting import TextStats, format_duration
from ui.icons import get_icon
from ui.presets import DEFAULT_PRESET, PRESET_BY_KEY
from ui.text_panel import TextPanel
from ui.theme import COLORS, UI_FONT_CANDIDATES, apply_appearance, get_font
from ui.tooltip import Tooltip
from utils.clipboard import read_clipboard
from utils.resources import resource_path

STATE_IDLE = "idle"
STATE_COUNTDOWN = "countdown"
STATE_TYPING = "typing"
STATE_PAUSED = "paused"
STATE_FINISHED = "finished"
ACTIVE_STATES = {STATE_COUNTDOWN, STATE_TYPING, STATE_PAUSED}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        apply_appearance("light")
        ctk.set_default_color_theme("blue")

        self.title("自动打字")
        self.geometry("760x640")
        self.minsize(620, 500)
        self.configure(fg_color=COLORS["bg"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        try:
            self.iconbitmap(str(resource_path("assets/app.ico")))
        except Exception:
            pass

        self._state = STATE_IDLE
        self._started_at = 0.0
        self._preset_key = DEFAULT_PRESET.key

        self._engine = TypingEngine()
        self._engine.on_countdown = self._on_countdown
        self._engine.on_progress = self._on_progress
        self._engine.on_finished = self._on_finished
        self._engine.on_stopped = self._on_stopped
        self._engine.on_status_change = None

        self._build_ui()
        self._apply_preset(DEFAULT_PRESET.key, announce=False)
        self._set_state(STATE_IDLE)
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        header.grid_columnconfigure(1, weight=1)

        app_icon = get_icon("keyboard", "theme", size=(24, 24))
        ctk.CTkLabel(
            header,
            text="" if app_icon else "⌨",
            image=app_icon,
            width=28,
        ).grid(row=0, column=0, rowspan=2, sticky="w", padx=(2, 10))

        ctk.CTkLabel(
            header,
            text="自动打字",
            font=get_font(UI_FONT_CANDIDATES, 16, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(
            header,
            text="把文字逐字输入任意窗口",
            font=get_font(UI_FONT_CANDIDATES, 12),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).grid(row=1, column=1, sticky="nw")

        self.btn_pin = self._header_button(header, "pin-off", "窗口置顶", self._toggle_pin)
        self.btn_pin.grid(row=0, column=2, rowspan=2, padx=(4, 0))
        self.btn_theme = self._header_button(header, "moon", "切换主题", self._toggle_theme)
        self.btn_theme.grid(row=0, column=3, rowspan=2, padx=(4, 0))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        self._preset_bar = PresetBar(main, on_change=self._on_preset_change)
        self._preset_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._text_panel = TextPanel(main, on_text_changed=self._refresh_stats)
        self._text_panel.grid(row=1, column=0, sticky="nsew")
        self._text_panel.on_read_clipboard = self._read_clipboard
        self._text_panel.on_clear = self._clear_text

        self._control_panel = ControlPanel(
            main,
            on_primary=self._handle_primary,
            on_stop=self._handle_stop,
            on_settings_change=self._refresh_stats,
        )
        self._control_panel.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def _header_button(self, master, icon: str, tooltip: str, command) -> ctk.CTkButton:
        button = ctk.CTkButton(
            master,
            text="",
            image=get_icon(icon, "theme"),
            width=32,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            command=command,
        )
        Tooltip(button, tooltip)
        return button

    def _center_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"+{x}+{y}")

    def _set_state(self, state: str) -> None:
        self._state = state
        self._control_panel.set_state(state)
        self._preset_bar.set_enabled(state not in ACTIVE_STATES)
        self._text_panel.set_read_only(state in ACTIVE_STATES)

    def _on_preset_change(self, key: str) -> None:
        if self._state in ACTIVE_STATES:
            return
        self._apply_preset(key)

    def _apply_preset(self, key: str, announce: bool = True) -> None:
        preset = PRESET_BY_KEY[key]
        self._preset_key = key
        self._preset_bar.set_selected(key)
        self._text_panel.set_editor_font(get_font(preset.font_candidates, preset.font_size))
        self._control_panel.apply_preset(preset)
        self._refresh_stats()
        if announce and self._state in {STATE_IDLE, STATE_FINISHED}:
            self._control_panel.set_status(f"已切换为「{preset.label}」预设")

    def _refresh_stats(self) -> None:
        text = self._text_panel.get_text()
        stats = TextStats.from_text(
            text,
            self._control_panel.speed_ms,
            self._control_panel.countdown_seconds,
        )
        self._text_panel.set_stats(stats.chars, stats.lines)
        if self._state == STATE_IDLE:
            if text.strip():
                self._control_panel.set_status(
                    f"就绪 · 预计用时 {format_duration(stats.estimated_seconds)}"
                )
            else:
                self._control_panel.set_status("请输入要输入的文字")

    def _handle_primary(self) -> None:
        if self._state in {STATE_IDLE, STATE_FINISHED}:
            self._start_typing()
        elif self._state == STATE_COUNTDOWN:
            self._handle_stop()
        elif self._state == STATE_TYPING:
            self._engine.pause()
            self._set_state(STATE_PAUSED)
        elif self._state == STATE_PAUSED:
            self._engine.resume()
            self._set_state(STATE_TYPING)

    def _start_typing(self) -> None:
        text = self._text_panel.get_text()
        if not text.strip():
            self._control_panel.set_status("请先输入要输入的文字", "error")
            self._text_panel.focus_editor()
            return

        self._started_at = time.monotonic()
        self._set_state(STATE_COUNTDOWN)
        self._control_panel.set_progress(0, len(text))
        self._control_panel.set_status("准备中…", "muted")
        self._engine.start(
            text=text,
            base_delay_ms=self._control_panel.speed_ms,
            countdown_seconds=self._control_panel.countdown_seconds,
            skip_indent=self._control_panel.skip_indent,
            randomize=self._control_panel.randomize,
        )

    def _handle_stop(self) -> None:
        self._engine.stop()

    def _on_countdown(self, remaining: int) -> None:
        self.after(0, lambda: self._control_panel.set_status(
            f"{remaining} 秒后开始，请切换到目标窗口"
        ))

    def _on_progress(self, current: int, total: int) -> None:
        def update() -> None:
            if self._state == STATE_COUNTDOWN:
                self._set_state(STATE_TYPING)
            self._control_panel.set_progress(current, total)
            remaining = max(0, total - current) * self._control_panel.speed_ms / 1000
            self._control_panel.set_status(
                f"正在输入 {current}/{total} · 剩余约 {format_duration(round(remaining))}"
            )

        self.after(0, update)

    def _on_finished(self) -> None:
        def update() -> None:
            elapsed = max(0, round(time.monotonic() - self._started_at))
            self._set_state(STATE_FINISHED)
            self._control_panel.set_progress(1, 1)
            self._control_panel.set_status(
                f"完成 · 用时 {format_duration(elapsed)}", "success"
            )

        self.after(0, update)

    def _on_stopped(self) -> None:
        def update() -> None:
            self._set_state(STATE_IDLE)
            self._control_panel.set_progress(0, 1)
            self._refresh_stats()
            self._control_panel.set_status("已停止")

        self.after(0, update)

    def _read_clipboard(self) -> None:
        try:
            text = read_clipboard()
        except Exception:
            self._control_panel.set_status("读取剪贴板失败", "error")
            return
        if not text.strip():
            self._control_panel.set_status("剪贴板中没有文本", "error")
            return
        self._text_panel.set_text(text)
        self._text_panel.focus_editor()
        self._control_panel.set_status("已读取剪贴板")

    def _clear_text(self) -> None:
        self._text_panel.clear()
        self._control_panel.set_status("已清空")

    def _toggle_theme(self) -> None:
        current = ctk.get_appearance_mode().lower()
        new_mode = "dark" if current == "light" else "light"
        apply_appearance(new_mode)
        self.btn_theme.configure(image=get_icon("moon" if new_mode == "light" else "sun", "theme"))
        self._control_panel.refresh_icons()

    def _toggle_pin(self) -> None:
        topmost = bool(self.attributes("-topmost"))
        new_value = not topmost
        self.attributes("-topmost", new_value)
        self.btn_pin.configure(image=get_icon("pin" if new_value else "pin-off", "theme"))

    def _on_close(self) -> None:
        if self._engine.is_running:
            self._engine.stop()
        self.destroy()
```

- [ ] **Step 3: Run import and unit tests**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -c "import main; print('import main: OK')"
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests -v
```

Expected: import OK and all tests PASS.

- [ ] **Step 4: Launch the app for a smoke test**

Run:

```powershell
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe main.py
```

Expected:

- 窗口打开，默认文章预设
- 占位文字显示
- 浅色主题正常
- 关闭窗口不报错

- [ ] **Step 5: Checkpoint**

Run `git diff --check`. Do not commit unless the user asks.

---

### Task 7: 文档、打包与完整验收

**Files:**
- Modify: `docs/analysis/requirements.md`
- Modify: `docs/analysis/technical-design.md`
- Modify: `docs/analysis/ui-design.md`
- Modify: `docs/agent-reference/testing.md`
- Modify: `docs/agent-reference/troubleshooting.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `AGENTS.md`（如结构变化需要）
- Modify: `docs/README.md`（如新增文档需要）

- [ ] **Step 1: Update requirements**

在 `docs/analysis/requirements.md` 中补充：

- 产品定位改为通用文字输入
- 两个场景预设及其默认值
- 状态机（就绪/倒计时/输入中/暂停/完成）
- 字数、行数、预计用时、速度换算
- 浅色/深色、窗口置顶
- 明确不包含全局热键、托盘、历史、文件导入

- [ ] **Step 2: Update technical design**

在 `docs/analysis/technical-design.md` 中补充：

- 新 UI 模块结构
- `randomize` 参数与 `on_stopped` 回调
- `resource_path` 和 PyInstaller `datas`
- `Pillow` 依赖
- 图标生成工具不进入运行时

- [ ] **Step 3: Update UI design**

用新设计替换 `docs/analysis/ui-design.md` 中的旧配色和布局：

- 浅色/深色 token
- 字体表和场景字体
- 新布局图
- 控件尺寸、圆角、间距
- Lucide 图标规范和许可证说明

- [ ] **Step 4: Update testing and troubleshooting**

在 `docs/agent-reference/testing.md` 中加入 U01–U20 手动矩阵和打包检查。

在 `docs/agent-reference/troubleshooting.md` 中加入：

- 图标缺失 / 路径错误
- 主题切换图标不刷新
- 打包后 assets 缺失
- `Pillow` 未安装
- 停止后误报完成

- [ ] **Step 5: Update README and CHANGELOG**

`README.md`：

- 功能特性加入场景预设、浅色/深色、字数统计、预计用时
- 运行环境加入 `Pillow`
- 项目结构加入 `assets/icons/`、`ui/theme.py` 等
- 使用步骤更新为新交互

`CHANGELOG.md`：

```markdown
## [2.0.0] - 2026-11-11

### Added

- 通用文字输入定位，新增文章 / 作业与代码场景预设
- 字数、行数、预计用时和速度换算
- 浅色 / 深色主题、窗口置顶
- Lucide 开源图标与应用图标
- 高级设置中的自然节奏开关

### Changed

- 主界面重构为编辑器 + 底部控制栏
- 默认场景改为文章 / 作业，默认不跳过行首缩进
- 停止与自然完成使用不同状态，不再误报完成
- 打包配置收集 assets 资源

### Fixed

- 停止输入后可能显示“打字完成”的问题
- 运行中修改参数与引擎快照不一致的问题（运行期间禁用参数）
```

- [ ] **Step 6: Run full verification**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests -v
C:\Users\Deki\AppData\Local\Programs\Python\Python313\python.exe -c "import main; print('import main: OK')"
git diff --check
```

Then run the manual matrix U01–U20 from the spec.

- [ ] **Step 7: Build the exe**

Run:

```powershell
pyinstaller build.spec
```

Expected:

- `dist/自动打字.exe` 生成
- 在无 Python 环境或临时目录运行 exe
- 窗口图标、主题、场景预设、输入功能正常

- [ ] **Step 8: Final checkpoint**

确认：

- [ ] 所有测试通过
- [ ] 手动矩阵记录完成
- [ ] 文档链接有效
- [ ] `git status` 只包含预期改动
- [ ] 未经用户要求，未提交或推送
