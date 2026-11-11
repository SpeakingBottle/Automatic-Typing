"""屏幕顶部居中的倒计时浮层。"""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from ui.i18n import t
from ui.theme import COLORS, UI_FONT_CANDIDATES, get_font


class CountdownOverlay:
    """不抢焦点的置顶倒计时卡片，仅在倒计时阶段显示。"""

    def __init__(self, master: tk.Misc):
        self._master = master
        self._window: ctk.CTkToplevel | None = None
        self._title_label: ctk.CTkLabel | None = None
        self._number_label: ctk.CTkLabel | None = None
        self._hint_label: ctk.CTkLabel | None = None
        self._remaining = 0
        self._visible = False

    @property
    def is_visible(self) -> bool:
        return self._visible

    def show(self, remaining: int) -> None:
        """显示或更新倒计时；remaining 为剩余秒数。"""
        self._remaining = max(0, int(remaining))
        if self._window is None or not self._window.winfo_exists():
            self._build()
        self._retranslate()
        self._number_label.configure(text=str(self._remaining))
        self._window.deiconify()
        self._window.update_idletasks()
        self._place()
        self._window.lift()
        self._window.attributes("-topmost", True)
        self._visible = True

    def hide(self) -> None:
        """隐藏浮层，不销毁窗口。"""
        self._visible = False
        if self._window is not None and self._window.winfo_exists():
            self._window.withdraw()

    def refresh_language(self) -> None:
        """语言切换后更新浮层文案。"""
        if self._window is None or not self._window.winfo_exists():
            return
        self._retranslate()
        self._window.update_idletasks()
        self._place()

    def destroy(self) -> None:
        """销毁浮层窗口。"""
        if self._window is not None:
            try:
                self._window.destroy()
            except tk.TclError:
                pass
            self._window = None
        self._visible = False

    def _build(self) -> None:
        window = ctk.CTkToplevel(self._master)
        window.withdraw()
        window.overrideredirect(True)
        window.configure(fg_color=COLORS["surface"])
        window.attributes("-topmost", True)
        for attribute in ("-noactivate", "-toolwindow"):
            try:
                window.attributes(attribute, True)
            except tk.TclError:
                pass

        card = ctk.CTkFrame(
            window,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["accent"],
            corner_radius=18,
        )
        card.pack(padx=2, pady=2)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=26, pady=12)

        self._title_label = ctk.CTkLabel(
            inner,
            text=t("overlay.title"),
            font=get_font(UI_FONT_CANDIDATES, 11),
            text_color=COLORS["text_muted"],
        )
        self._title_label.pack()

        self._number_label = ctk.CTkLabel(
            inner,
            text="3",
            font=get_font(UI_FONT_CANDIDATES, 46, "bold"),
            text_color=COLORS["accent"],
            width=72,
        )
        self._number_label.pack()

        self._hint_label = ctk.CTkLabel(
            inner,
            text=t("overlay.hint"),
            font=get_font(UI_FONT_CANDIDATES, 11),
            text_color=COLORS["text_muted"],
        )
        self._hint_label.pack()

        self._window = window

    def _retranslate(self) -> None:
        if self._title_label is not None:
            self._title_label.configure(text=t("overlay.title"))
        if self._hint_label is not None:
            self._hint_label.configure(text=t("overlay.hint"))

    def _place(self) -> None:
        """把浮层放在屏幕顶部水平居中。"""
        if self._window is None:
            return
        width = max(180, self._window.winfo_reqwidth())
        height = max(96, self._window.winfo_reqheight())
        screen_width = self._window.winfo_screenwidth()
        x = max(0, (screen_width - width) // 2)
        y = 24
        self._window.geometry(f"{width}x{height}+{x}+{y}")
