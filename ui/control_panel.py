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
