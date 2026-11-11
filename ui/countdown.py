"""屏幕顶部居中的倒计时与输入控制浮层。"""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from ui.formatting import format_duration
from ui.i18n import t
from ui.icons import get_icon
from ui.theme import COLORS, UI_FONT_CANDIDATES, color, get_font
from ui.tooltip import Tooltip
from utils.windows import get_screen_size, get_window_handle, set_rounded_window_region


class CountdownOverlay:
    """倒计时卡片；倒计时结束后切换为紧凑的输入控制条。"""

    def __init__(
        self,
        master: tk.Misc,
        on_cancel: callable | None = None,
        on_toggle_pause: callable | None = None,
        on_stop: callable | None = None,
        on_pointer_enter: callable | None = None,
    ):
        self._master = master
        self._on_cancel = on_cancel
        self._on_toggle_pause = on_toggle_pause
        self._on_stop = on_stop
        self._on_pointer_enter = on_pointer_enter

        self._window: ctk.CTkToplevel | None = None
        self._mode = "countdown"
        self._remaining = 0
        self._countdown_total = 3
        self._current = 0
        self._total = 0
        self._remaining_seconds = 0.0
        self._paused = False
        self._visible = False

        self._ring: tk.Canvas | None = None
        self._ring_bg: int | None = None
        self._ring_arc: int | None = None
        self._ring_text: int | None = None
        self._dot: tk.Canvas | None = None
        self._dot_item: int | None = None

    @property
    def is_visible(self) -> bool:
        return self._visible

    @property
    def hwnd(self) -> int:
        """返回浮层原生窗口句柄，用于识别前台窗口。"""
        if self._window is None or not self._window.winfo_exists():
            return 0
        return get_window_handle(self._window)

    def prewarm(self) -> None:
        """提前创建隐藏窗口，避免首次倒计时出现明显卡顿。"""
        self._ensure_window()
        if self._window is not None:
            self._window.update_idletasks()

    def show_countdown(self, remaining: int, total: int | None = None) -> None:
        """显示或更新倒计时；remaining 为剩余秒数。"""
        self._mode = "countdown"
        self._remaining = max(0, int(remaining))
        self._countdown_total = max(int(total or remaining or 1), 1)
        self._ensure_window()
        self._countdown_frame.grid()
        self._control_frame.grid_remove()
        self._render_countdown()
        self._show_window()

    def show_control(
        self,
        current: int,
        total: int,
        remaining_seconds: float = 0.0,
        paused: bool = False,
    ) -> None:
        """切换为输入控制条，显示进度、暂停/继续和停止。"""
        self._mode = "control"
        self._current = max(0, int(current))
        self._total = max(0, int(total))
        self._remaining_seconds = max(0.0, float(remaining_seconds))
        self._paused = bool(paused)
        self._ensure_window()
        self._control_frame.grid()
        self._countdown_frame.grid_remove()
        self._render_control()
        self._show_window()

    def set_paused(self, paused: bool) -> None:
        """更新暂停/继续状态和按钮图标。"""
        self._paused = bool(paused)
        if self._mode == "control" and self._window is not None:
            self._render_control()
            self._place()

    def hide(self) -> None:
        """隐藏浮层，不销毁窗口。"""
        self._visible = False
        if self._window is not None and self._window.winfo_exists():
            self._window.withdraw()

    def refresh_language(self) -> None:
        """语言切换后更新浮层文案。"""
        if self._window is None or not self._window.winfo_exists():
            return
        if self._mode == "countdown":
            self._render_countdown()
        else:
            self._render_control()
        self._window.update_idletasks()
        self._place()

    def refresh_theme(self) -> None:
        """刷新 Canvas 颜色，使圆环和状态点在主题切换后保持可读。"""
        if self._window is None or not self._window.winfo_exists():
            return
        if self._ring is not None:
            self._ring.configure(bg=color("surface"))
            self._ring.itemconfigure(self._ring_bg, outline=color("border"))
            self._ring.itemconfigure(self._ring_arc, outline=color("accent"))
            self._ring.itemconfigure(self._ring_text, fill=color("accent"))
        if self._dot is not None:
            self._dot.configure(bg=color("surface"))
            self._dot.itemconfigure(
                self._dot_item,
                fill=color("text_muted" if self._paused else "accent"),
            )

    def destroy(self) -> None:
        """销毁浮层窗口。"""
        if self._window is not None:
            try:
                self._window.destroy()
            except tk.TclError:
                pass
            self._window = None
        self._visible = False

    def _ensure_window(self) -> None:
        if self._window is None or not self._window.winfo_exists():
            self._build()

    def _build(self) -> None:
        window = ctk.CTkToplevel(self._master)
        window.withdraw()
        window.overrideredirect(True)
        window.configure(fg_color=COLORS["surface"])
        window.attributes("-topmost", True)
        try:
            window.attributes("-toolwindow", True)
        except tk.TclError:
            pass
        window.bind("<Enter>", self._handle_pointer_enter, add="+")

        card = ctk.CTkFrame(
            window,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=20,
        )
        card.pack(fill="both", expand=True)
        card.bind("<Enter>", self._handle_pointer_enter, add="+")

        # ---- 倒计时模式 ----
        countdown = ctk.CTkFrame(card, fg_color="transparent")
        countdown.grid(row=0, column=0, sticky="nsew", padx=16, pady=12)
        countdown.grid_columnconfigure(1, weight=1)
        self._countdown_frame = countdown

        self._ring = tk.Canvas(
            countdown,
            width=80,
            height=80,
            highlightthickness=0,
            bg=color("surface"),
        )
        self._ring.grid(row=0, column=0, rowspan=2, sticky="w", padx=(2, 14))
        self._ring_bg = self._ring.create_oval(
            7, 7, 73, 73, outline=color("border"), width=6
        )
        self._ring_arc = self._ring.create_arc(
            7,
            7,
            73,
            73,
            start=90,
            extent=-360,
            style="arc",
            outline=color("accent"),
            width=6,
        )
        self._ring_text = self._ring.create_text(
            40,
            40,
            text="3",
            fill=color("accent"),
            font=get_font(UI_FONT_CANDIDATES, 24, "bold"),
        )

        self._countdown_title = ctk.CTkLabel(
            countdown,
            text=t("overlay.title"),
            font=get_font(UI_FONT_CANDIDATES, 15, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        self._countdown_title.grid(row=0, column=1, sticky="sw")
        self._countdown_hint = ctk.CTkLabel(
            countdown,
            text="",
            font=get_font(UI_FONT_CANDIDATES, 11),
            text_color=COLORS["text_muted"],
            anchor="w",
            justify="left",
            wraplength=236,
        )
        self._countdown_hint.grid(row=1, column=1, sticky="nw", pady=(3, 0))

        self._btn_cancel = ctk.CTkButton(
            countdown,
            text="",
            image=get_icon("x", "theme"),
            width=28,
            height=28,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            command=self._cancel,
        )
        self._btn_cancel.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(12, 0))
        self._tooltip_cancel = Tooltip(self._btn_cancel, t("overlay.cancel"))

        # ---- 输入控制模式 ----
        control = ctk.CTkFrame(card, fg_color="transparent")
        control.grid(row=0, column=0, sticky="nsew", padx=16, pady=12)
        control.grid_columnconfigure(1, weight=1)
        self._control_frame = control

        self._dot = tk.Canvas(
            control,
            width=10,
            height=10,
            highlightthickness=0,
            bg=color("surface"),
        )
        self._dot.grid(row=0, column=0, rowspan=2, sticky="w", padx=(2, 10))
        self._dot_item = self._dot.create_oval(
            1, 1, 9, 9, fill=color("accent"), outline=""
        )

        self._status_label = ctk.CTkLabel(
            control,
            text=t("overlay.typing"),
            font=get_font(UI_FONT_CANDIDATES, 13, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        self._status_label.grid(row=0, column=1, sticky="w")
        self._detail_label = ctk.CTkLabel(
            control,
            text="",
            font=get_font(UI_FONT_CANDIDATES, 11),
            text_color=COLORS["text_muted"],
            anchor="w",
            width=248,
        )
        self._detail_label.grid(row=1, column=1, sticky="w", pady=(2, 0))

        self._btn_pause = ctk.CTkButton(
            control,
            text="",
            image=get_icon("pause", "on_accent"),
            width=34,
            height=34,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._toggle_pause,
        )
        self._btn_pause.grid(row=0, column=2, rowspan=2, padx=(12, 0))
        self._tooltip_pause = Tooltip(self._btn_pause, t("overlay.pause"))

        self._btn_stop = ctk.CTkButton(
            control,
            text="",
            image=get_icon("square", "theme"),
            width=34,
            height=34,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
            command=self._stop,
        )
        self._btn_stop.grid(row=0, column=3, rowspan=2, padx=(8, 0))
        self._tooltip_stop = Tooltip(self._btn_stop, t("overlay.stop"))

        self._progress = ctk.CTkProgressBar(
            control,
            height=6,
            corner_radius=3,
            fg_color=COLORS["surface_alt"],
            progress_color=COLORS["accent"],
        )
        self._progress.grid(
            row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0)
        )
        self._progress.set(0)

        self._countdown_frame.grid()
        self._control_frame.grid_remove()
        self._window = window

    def _render_countdown(self) -> None:
        fraction = 0.0
        if self._countdown_total > 0:
            fraction = max(0.0, min(1.0, self._remaining / self._countdown_total))
        if self._ring is not None:
            self._ring.itemconfigure(self._ring_arc, extent=-360 * fraction)
            self._ring.itemconfigure(self._ring_text, text=str(self._remaining))
        self._countdown_title.configure(text=t("overlay.title"))
        self._countdown_hint.configure(
            text=t("overlay.countdown_hint", n=self._remaining)
        )
        self._tooltip_cancel.set_text(t("overlay.cancel"))

    def _render_control(self) -> None:
        percent = 0 if self._total <= 0 else round(self._current * 100 / self._total)
        self._status_label.configure(
            text=t("overlay.paused" if self._paused else "overlay.typing"),
            text_color=COLORS["text"],
        )
        self._detail_label.configure(
            text=t(
                "overlay.detail",
                current=self._current,
                total=self._total,
                percent=percent,
                remaining=format_duration(round(self._remaining_seconds)),
            )
        )
        if self._dot is not None:
            self._dot.itemconfigure(
                self._dot_item,
                fill=color("text_muted" if self._paused else "accent"),
            )
        self._btn_pause.configure(
            image=get_icon("play" if self._paused else "pause", "on_accent")
        )
        self._tooltip_pause.set_text(
            t("overlay.resume" if self._paused else "overlay.pause")
        )
        self._tooltip_stop.set_text(t("overlay.stop"))
        self._progress.set(0.0 if self._total <= 0 else self._current / self._total)

    def _show_window(self) -> None:
        if self._window is None:
            return
        self._window.deiconify()
        self._window.update_idletasks()
        self._place()
        self._window.lift()
        self._window.attributes("-topmost", True)
        self._visible = True

    def _place(self) -> None:
        """把浮层放在屏幕顶部水平居中，并按模式设置最小尺寸。"""
        if self._window is None:
            return
        self._window.update_idletasks()
        if self._mode == "countdown":
            min_width, min_height = 360, 112
        else:
            min_width, min_height = 430, 96
        width = max(min_width, self._window.winfo_reqwidth())
        height = max(min_height, self._window.winfo_reqheight())
        self._window.geometry(f"{width}x{height}")
        self._window.update_idletasks()

        # Tk 的 geometry 位置是物理像素，宽度是逻辑像素；居中要用缩放后的实际宽度。
        physical_width = self._window.winfo_width()
        screen_width, _ = get_screen_size()
        if screen_width <= 0:
            screen_width = self._window.winfo_screenwidth()
        x = max(0, (screen_width - physical_width) // 2)
        y = 22
        self._window.geometry(f"+{x}+{y}")
        self._window.update_idletasks()

        try:
            scaling = ctk.ScalingTracker.get_window_scaling(self._window)
        except Exception:
            scaling = 1.0
        set_rounded_window_region(self._window, max(12, round(20 * scaling)))

    def _handle_pointer_enter(self, _event=None) -> None:
        if self._on_pointer_enter:
            self._on_pointer_enter()

    def _cancel(self) -> None:
        if self._on_cancel:
            self._on_cancel()

    def _toggle_pause(self) -> None:
        if self._on_toggle_pause:
            self._on_toggle_pause()

    def _stop(self) -> None:
        if self._on_stop:
            self._on_stop()
