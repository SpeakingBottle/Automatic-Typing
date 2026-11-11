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
        self.geometry("760x700")
        self.minsize(620, 600)
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
        width = 760
        height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.minsize(620, 600)
        self.geometry(f"{width}x{height}+{x}+{y}")

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
            self._control_panel.set_status("已暂停")
        elif self._state == STATE_PAUSED:
            self._engine.resume()
            self._set_state(STATE_TYPING)
            self._control_panel.set_status("正在输入…")

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
        def update() -> None:
            if self._state != STATE_COUNTDOWN:
                return
            self._control_panel.set_status(f"{remaining} 秒后开始，请切换到目标窗口")

        self.after(0, update)

    def _on_progress(self, current: int, total: int) -> None:
        def update() -> None:
            if self._state not in ACTIVE_STATES:
                return
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
            if self._state not in ACTIVE_STATES:
                return
            elapsed = max(0, round(time.monotonic() - self._started_at))
            self._set_state(STATE_FINISHED)
            self._control_panel.set_progress(1, 1)
            self._control_panel.set_status(
                f"完成 · 用时 {format_duration(elapsed)}", "success"
            )

        self.after(0, update)

    def _on_stopped(self) -> None:
        def update() -> None:
            if self._state not in ACTIVE_STATES:
                return
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
        self._text_panel.refresh_icons()
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
