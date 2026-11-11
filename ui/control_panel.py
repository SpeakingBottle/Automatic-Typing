"""场景切换、节奏参数、传输控制和进度。"""

from __future__ import annotations

import customtkinter as ctk

from ui.formatting import characters_per_minute, speed_band
from ui.i18n import t
from ui.icons import get_icon
from ui.presets import DEFAULT_PRESET, PRESET_BY_KEY, PRESETS, Preset
from ui.theme import COLORS, UI_FONT_CANDIDATES, get_font
from ui.tooltip import Tooltip

COUNTDOWN_SECONDS = (1, 3, 5, 10)


def countdown_label(seconds: int) -> str:
    """返回当前语言下的倒计时选项文字。"""
    return t("countdown.option", n=seconds)


class PresetBar(ctk.CTkFrame):
    def __init__(self, master, on_change: callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._selected_key = DEFAULT_PRESET.key
        self._labels: dict[str, str] = {}
        self._enabled = True
        self._rebuild_labels()

        self.scene_label = ctk.CTkLabel(
            self,
            text=t("control.scene"),
            font=get_font(UI_FONT_CANDIDATES, 13),
            text_color=COLORS["text_muted"],
        )
        self.scene_label.pack(side="left", padx=(2, 10))

        self.segmented = ctk.CTkSegmentedButton(
            self,
            values=self._values(),
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

    def _values(self) -> list[str]:
        return [preset.label for preset in PRESETS]

    def _rebuild_labels(self) -> None:
        self._labels = {preset.label: preset.key for preset in PRESETS}

    def _changed(self, label: str) -> None:
        key = self._labels.get(label)
        if key:
            self._on_change(key)

    def set_selected(self, key: str) -> None:
        if key not in PRESET_BY_KEY:
            return
        self._selected_key = key
        self.segmented.set(PRESET_BY_KEY[key].label)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.segmented.configure(state="normal" if enabled else "disabled")

    def refresh_language(self) -> None:
        """切换语言后重建分段按钮文字并保持当前选择。"""
        self.scene_label.configure(text=t("control.scene"))
        values = self._values()
        self._rebuild_labels()
        self.segmented.configure(values=values)
        self.segmented.set(PRESET_BY_KEY[self._selected_key].label)
        self.set_enabled(self._enabled)


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
        self._can_start = False
        self._primary_icon = "play"
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        speed_row = ctk.CTkFrame(self, fg_color="transparent")
        speed_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))
        speed_row.grid_columnconfigure(1, weight=1)

        self.speed_label = ctk.CTkLabel(
            speed_row,
            text=t("control.speed"),
            font=get_font(UI_FONT_CANDIDATES, 13),
            text_color=COLORS["text_muted"],
        )
        self.speed_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

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

        self.countdown_title = ctk.CTkLabel(
            action_row,
            text=t("control.countdown"),
            font=get_font(UI_FONT_CANDIDATES, 13),
            text_color=COLORS["text_muted"],
        )
        self.countdown_title.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.countdown_menu = ctk.CTkOptionMenu(
            action_row,
            values=[countdown_label(seconds) for seconds in COUNTDOWN_SECONDS],
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
        self._set_countdown(3)
        self.countdown_menu.grid(row=0, column=1, sticky="w")

        self.btn_primary = ctk.CTkButton(
            action_row,
            text=t("action.start"),
            image=get_icon("play", "on_accent"),
            compound="left",
            width=132,
            height=38,
            corner_radius=10,
            font=get_font(UI_FONT_CANDIDATES, 14, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"],
            text_color_disabled=COLORS["text_muted"],
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
        self._tooltip_stop = Tooltip(self.btn_stop, t("control.stop"))

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
            text=t("control.advanced"),
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
            text=t("control.skip_indent"),
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
            text=t("control.randomize"),
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
            self.btn_advanced.configure(
                text=t("control.advanced_collapse"),
                image=get_icon("chevron-up", "theme"),
            )
        else:
            self.advanced_frame.grid_remove()
            self.btn_advanced.configure(
                text=t("control.advanced"),
                image=get_icon("chevron-down", "theme"),
            )

    def _on_speed_change(self, value: float) -> None:
        self.refresh_speed_label()
        self._notify_settings()

    def refresh_speed_label(self) -> None:
        speed = self.speed_ms
        cpm = characters_per_minute(speed)
        self.speed_value.configure(
            text=t(
                "control.speed_value",
                band=speed_band(speed),
                speed=speed,
                cpm=cpm,
            )
        )

    def _set_countdown(self, seconds: int) -> None:
        if seconds not in COUNTDOWN_SECONDS:
            seconds = 3
        self.countdown_menu.set(countdown_label(seconds))

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
        try:
            return int(self.countdown_menu.get().split()[0])
        except (IndexError, ValueError):
            return 3

    @property
    def skip_indent(self) -> bool:
        return bool(self.skip_var.get())

    @property
    def randomize(self) -> bool:
        return bool(self.random_var.get())

    def apply_preset(self, preset: Preset) -> None:
        self.speed_slider.set(preset.speed_ms)
        self._set_countdown(preset.countdown_seconds)
        self.skip_var.set(preset.skip_indent)
        self.random_var.set(preset.randomize)
        self.refresh_speed_label()
        self._notify_settings()

    def _apply_primary_enabled(self, enabled: bool) -> None:
        icon_variant = "on_accent" if enabled else "theme"
        if enabled:
            self.btn_primary.configure(
                state="normal",
                image=get_icon(self._primary_icon, icon_variant),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["accent_text"],
            )
        else:
            self.btn_primary.configure(
                state="disabled",
                image=get_icon(self._primary_icon, icon_variant),
                fg_color=COLORS["surface_alt"],
                hover_color=COLORS["surface_alt"],
                text_color=COLORS["text_muted"],
            )

    def set_can_start(self, value: bool) -> None:
        """空文本时禁用主按钮；运行中不受此状态影响。"""
        value = bool(value)
        if value == self._can_start:
            return
        self._can_start = value
        if self._state in {"idle", "finished"}:
            self._apply_primary_enabled(value)

    def set_state(self, state: str) -> None:
        self._state = state
        running = state in {"countdown", "typing", "paused"}

        if state == "idle":
            text, icon = t("action.start"), "play"
        elif state == "countdown":
            text, icon = t("action.cancel"), "x"
        elif state == "typing":
            text, icon = t("action.pause"), "pause"
        elif state == "paused":
            text, icon = t("action.resume"), "play"
        else:
            text, icon = t("action.start"), "play"

        self._primary_icon = icon
        self.btn_primary.configure(text=text)
        self._apply_primary_enabled(
            not (state in {"idle", "finished"} and not self._can_start)
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
        token = {
            "muted": "text_muted",
            "error": "danger",
            "success": "success",
        }.get(tone, "text_muted")
        self.status_label.configure(text=text, text_color=COLORS[token])

    def set_progress(self, current: int, total: int) -> None:
        value = 0.0 if total <= 0 else max(0.0, min(1.0, current / total))
        self.progress.set(value)

    def refresh_language(self) -> None:
        """切换语言后刷新所有静态文案。"""
        current_countdown = self.countdown_seconds
        self.speed_label.configure(text=t("control.speed"))
        self.countdown_title.configure(text=t("control.countdown"))
        self.countdown_menu.configure(
            values=[countdown_label(seconds) for seconds in COUNTDOWN_SECONDS]
        )
        self._set_countdown(current_countdown)
        self.refresh_speed_label()
        self.btn_advanced.configure(
            text=t(
                "control.advanced_collapse"
                if self._advanced_visible
                else "control.advanced"
            )
        )
        self.skip_switch.configure(text=t("control.skip_indent"))
        self.random_switch.configure(text=t("control.randomize"))
        self._tooltip_stop.set_text(t("control.stop"))
        self.set_state(self._state)

    def refresh_icons(self) -> None:
        self.set_state(self._state)
        self.btn_advanced.configure(
            image=get_icon(
                "chevron-up" if self._advanced_visible else "chevron-down",
                "theme",
            )
        )
