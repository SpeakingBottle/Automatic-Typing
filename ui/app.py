"""主窗口：布局、状态机、主题、置顶和引擎回调。"""

from __future__ import annotations

import time
import tkinter as tk

import customtkinter as ctk

from engine.typer import TypingEngine
from ui.control_panel import ControlPanel, PresetBar
from ui.countdown import CountdownOverlay
from ui.formatting import TextStats, format_duration
from ui.i18n import t, toggle_language
from ui.icons import get_icon
from ui.presets import DEFAULT_PRESET, PRESET_BY_KEY
from ui.text_panel import TextPanel
from ui.theme import COLORS, UI_FONT_CANDIDATES, apply_appearance, get_font
from ui.tooltip import Tooltip
from utils.clipboard import read_clipboard
from utils.resources import resource_path
from utils.windows import (
    get_foreground_window,
    get_window_handle,
    set_foreground_window,
)

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

        self.title(t("app.title"))
        self.geometry("760x700")
        self.minsize(620, 600)
        self.configure(fg_color=COLORS["bg"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._icon_photo = None
        self._apply_window_icon()

        self._state = STATE_IDLE
        self._started_at = 0.0
        self._preset_key = DEFAULT_PRESET.key
        self._status_key = "status.enter_text"
        self._status_kwargs: dict = {}
        self._status_tone = "muted"
        self._self_hwnd = 0
        self._target_hwnd = 0
        self._progress_current = 0
        self._progress_total = 0
        self._progress_remaining = 0.0

        self._engine = TypingEngine()
        self._engine.on_countdown = self._on_countdown
        self._engine.on_progress = self._on_progress
        self._engine.on_finished = self._on_finished
        self._engine.on_stopped = self._on_stopped
        self._engine.on_status_change = None

        self._countdown_overlay = CountdownOverlay(
            self,
            on_cancel=self._handle_stop,
            on_toggle_pause=self._toggle_pause,
            on_stop=self._handle_stop,
            on_pointer_enter=self._remember_target_window,
        )

        self._build_ui()
        self._apply_preset(DEFAULT_PRESET.key, announce=False)
        self._set_state(STATE_IDLE)
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(250, self._track_target_window)
        self.after(200, self._countdown_overlay.prewarm)

    def _apply_window_icon(self) -> None:
        """同时设置窗口图标和任务栏图标。"""
        try:
            self.iconbitmap(str(resource_path("assets/app.ico")))
        except Exception:
            pass
        try:
            self._icon_photo = tk.PhotoImage(
                master=self,
                file=str(resource_path("assets/app.png")),
            )
            self.iconphoto(True, self._icon_photo)
        except Exception:
            self._icon_photo = None

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

        self._title_label = ctk.CTkLabel(
            header,
            text=t("app.title"),
            font=get_font(UI_FONT_CANDIDATES, 16, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        self._title_label.grid(row=0, column=1, sticky="sw")
        self._subtitle_label = ctk.CTkLabel(
            header,
            text=t("app.subtitle"),
            font=get_font(UI_FONT_CANDIDATES, 12),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._subtitle_label.grid(row=1, column=1, sticky="nw")

        self.btn_language = self._header_button(
            header, "languages", t("app.tooltip.language"), self._toggle_language
        )
        self.btn_language.grid(row=0, column=2, rowspan=2, padx=(4, 0))
        self.btn_pin = self._header_button(
            header, "pin-off", t("app.tooltip.pin"), self._toggle_pin
        )
        self.btn_pin.grid(row=0, column=3, rowspan=2, padx=(4, 0))
        self.btn_theme = self._header_button(
            header, "moon", t("app.tooltip.theme"), self._toggle_theme
        )
        self.btn_theme.grid(row=0, column=4, rowspan=2, padx=(4, 0))

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

    def _header_button(self, master, icon: str, tooltip_text: str, command) -> ctk.CTkButton:
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
        button.tooltip = Tooltip(button, tooltip_text)
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

    def _own_hwnd(self) -> int:
        if not self._self_hwnd:
            self._self_hwnd = get_window_handle(self)
        return self._self_hwnd

    def _remember_target_window(self) -> None:
        """记录最近一个非本程序的前台窗口，供继续输入时恢复焦点。"""
        if self._state not in ACTIVE_STATES:
            return
        hwnd = get_foreground_window()
        if not hwnd:
            return
        if hwnd in {self._own_hwnd(), self._countdown_overlay.hwnd}:
            return
        self._target_hwnd = hwnd

    def _track_target_window(self) -> None:
        self._remember_target_window()
        self.after(250, self._track_target_window)

    def _restore_target_focus(self) -> None:
        if self._target_hwnd:
            set_foreground_window(self._target_hwnd)

    def _restore_main_window(self) -> None:
        try:
            self.deiconify()
            self.lift()
        except tk.TclError:
            pass

    def _minimize_for_typing(self) -> None:
        if self._state in {STATE_COUNTDOWN, STATE_TYPING, STATE_PAUSED}:
            try:
                self.iconify()
            except tk.TclError:
                pass

    def _toggle_pause(self) -> None:
        if self._state == STATE_TYPING:
            self._engine.pause()
            self._set_state(STATE_PAUSED)
            self._set_status("status.paused")
            self._countdown_overlay.show_control(
                self._progress_current,
                self._progress_total,
                self._progress_remaining,
                paused=True,
            )
        elif self._state == STATE_PAUSED:
            self._restore_target_focus()
            self.after(60, self._resume_typing)

    def _resume_typing(self) -> None:
        if self._state != STATE_PAUSED:
            return
        self._engine.resume()
        self._set_state(STATE_TYPING)
        self._set_status("status.typing")
        self._countdown_overlay.show_control(
            self._progress_current,
            self._progress_total,
            self._progress_remaining,
            paused=False,
        )

    def _set_state(self, state: str) -> None:
        self._state = state
        self._control_panel.set_state(state)
        self._preset_bar.set_enabled(state not in ACTIVE_STATES)
        self._text_panel.set_read_only(state in ACTIVE_STATES)
        if state not in {STATE_COUNTDOWN, STATE_TYPING, STATE_PAUSED}:
            self._countdown_overlay.hide()

    def _status_text(self) -> str:
        """按当前语言渲染状态栏，时长等参数在渲染时格式化。"""
        key = self._status_key
        kwargs = dict(self._status_kwargs)
        if key in {"status.ready", "status.finished"} and "seconds" in kwargs:
            kwargs["duration"] = format_duration(int(kwargs.pop("seconds")))
        if key == "status.progress" and "remaining_seconds" in kwargs:
            kwargs["remaining"] = format_duration(round(kwargs.pop("remaining_seconds")))
        if key == "status.preset" and "preset_key" in kwargs:
            preset = PRESET_BY_KEY.get(kwargs.pop("preset_key"))
            kwargs["label"] = preset.label if preset else ""
        return t(key, **kwargs)

    def _set_status(self, key: str, tone: str = "muted", **kwargs) -> None:
        self._status_key = key
        self._status_kwargs = kwargs
        self._status_tone = tone
        self._control_panel.set_status(self._status_text(), tone)

    def _refresh_status(self) -> None:
        self._control_panel.set_status(self._status_text(), self._status_tone)

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
            self._set_status("status.preset", preset_key=key)

    def _refresh_stats(self) -> None:
        text = self._text_panel.get_text()
        stats = TextStats.from_text(
            text,
            self._control_panel.speed_ms,
            self._control_panel.countdown_seconds,
        )
        self._text_panel.set_stats(stats.chars, stats.lines)
        has_text = bool(text.strip())
        self._control_panel.set_can_start(has_text)
        if self._state == STATE_IDLE:
            if has_text:
                self._set_status("status.ready", seconds=stats.estimated_seconds)
            else:
                self._set_status("status.enter_text")
        elif self._state == STATE_FINISHED:
            if not has_text:
                self._set_status("status.enter_text")
            elif self._status_key == "status.enter_text":
                self._set_status("status.ready", seconds=stats.estimated_seconds)

    def _handle_primary(self) -> None:
        if self._state in {STATE_IDLE, STATE_FINISHED}:
            self._start_typing()
        elif self._state == STATE_COUNTDOWN:
            self._handle_stop()
        elif self._state in {STATE_TYPING, STATE_PAUSED}:
            self._toggle_pause()

    def _start_typing(self) -> None:
        text = self._text_panel.get_text()
        if not text.strip():
            self._set_status("status.need_text", "error")
            self._text_panel.focus_editor()
            return

        self._started_at = time.monotonic()
        self._target_hwnd = 0
        self._progress_current = 0
        self._progress_total = len(text)
        self._progress_remaining = (
            len(text) * self._control_panel.speed_ms / 1000
        )
        countdown = self._control_panel.countdown_seconds
        self._set_state(STATE_COUNTDOWN)
        self._control_panel.set_progress(0, len(text))
        self._set_status("status.preparing")
        self._countdown_overlay.show_countdown(countdown, countdown)
        self._engine.start(
            text=text,
            base_delay_ms=self._control_panel.speed_ms,
            countdown_seconds=countdown,
            skip_indent=self._control_panel.skip_indent,
            randomize=self._control_panel.randomize,
        )
        self.after(60, self._minimize_for_typing)

    def _handle_stop(self) -> None:
        self._engine.stop()

    def _on_countdown(self, remaining: int) -> None:
        def update() -> None:
            if self._state != STATE_COUNTDOWN:
                return
            self._set_status("status.countdown", n=remaining)
            self._countdown_overlay.show_countdown(
                remaining,
                self._control_panel.countdown_seconds,
            )

        self.after(0, update)

    def _on_progress(self, current: int, total: int) -> None:
        def update() -> None:
            if self._state not in ACTIVE_STATES:
                return
            self._remember_target_window()
            if self._state == STATE_COUNTDOWN:
                self._set_state(STATE_TYPING)
            self._progress_current = current
            self._progress_total = total
            remaining = max(0, total - current) * self._control_panel.speed_ms / 1000
            self._progress_remaining = remaining
            self._control_panel.set_progress(current, total)
            self._set_status(
                "status.progress",
                current=current,
                total=total,
                remaining_seconds=remaining,
            )
            self._countdown_overlay.show_control(
                current,
                total,
                remaining,
                paused=self._state == STATE_PAUSED,
            )

        self.after(0, update)

    def _on_finished(self) -> None:
        def update() -> None:
            if self._state not in ACTIVE_STATES:
                return
            elapsed = max(0, round(time.monotonic() - self._started_at))
            self._set_state(STATE_FINISHED)
            self._control_panel.set_progress(1, 1)
            self._set_status("status.finished", "success", seconds=elapsed)
            self._restore_main_window()

        self.after(0, update)

    def _on_stopped(self) -> None:
        def update() -> None:
            if self._state not in ACTIVE_STATES:
                return
            self._set_state(STATE_IDLE)
            self._control_panel.set_progress(0, 1)
            self._refresh_stats()
            self._set_status("status.stopped")
            self._restore_main_window()

        self.after(0, update)

    def _read_clipboard(self) -> None:
        try:
            text = read_clipboard()
        except Exception:
            self._set_status("status.clipboard_failed", "error")
            return
        if not text.strip():
            self._set_status("status.clipboard_empty", "error")
            return
        self._text_panel.set_text(text)
        self._text_panel.focus_editor()
        self._set_status("status.clipboard_read")

    def _clear_text(self) -> None:
        self._text_panel.clear()
        self._set_status("status.cleared")

    def _toggle_theme(self) -> None:
        current = ctk.get_appearance_mode().lower()
        new_mode = "dark" if current == "light" else "light"
        apply_appearance(new_mode)
        self.btn_theme.configure(image=get_icon("moon" if new_mode == "light" else "sun", "theme"))
        self._text_panel.refresh_icons()
        self._control_panel.refresh_icons()
        self._countdown_overlay.refresh_theme()

    def _toggle_language(self) -> None:
        toggle_language()
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """语言切换后刷新全局文案、占位文字和状态栏。"""
        self.title(t("app.title"))
        self._title_label.configure(text=t("app.title"))
        self._subtitle_label.configure(text=t("app.subtitle"))
        self.btn_language.tooltip.set_text(t("app.tooltip.language"))
        self.btn_pin.tooltip.set_text(t("app.tooltip.pin"))
        self.btn_theme.tooltip.set_text(t("app.tooltip.theme"))
        self._preset_bar.refresh_language()
        self._text_panel.refresh_language()
        self._control_panel.refresh_language()
        self._countdown_overlay.refresh_language()
        self._refresh_stats()
        self._refresh_status()

    def _toggle_pin(self) -> None:
        topmost = bool(self.attributes("-topmost"))
        new_value = not topmost
        self.attributes("-topmost", new_value)
        self.btn_pin.configure(image=get_icon("pin" if new_value else "pin-off", "theme"))

    def _on_close(self) -> None:
        if self._engine.is_running:
            self._engine.stop()
        self._countdown_overlay.destroy()
        self.destroy()
