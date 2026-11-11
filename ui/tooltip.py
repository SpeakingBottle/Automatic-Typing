"""轻量图标按钮提示。"""

from __future__ import annotations

import tkinter as tk

from ui.theme import UI_FONT_CANDIDATES, color, get_font


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id: str | None = None
        self._tip: tk.Toplevel | None = None
        self._label: tk.Label | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def set_text(self, text: str) -> None:
        """更新提示文字，用于切换语言。"""
        self.text = text
        if self._label is not None:
            self._label.configure(text=text)

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
        self._label = tk.Label(
            self._tip,
            text=self.text,
            background=color("surface_alt"),
            foreground=color("text"),
            padx=8,
            pady=4,
            font=get_font(UI_FONT_CANDIDATES, 10),
        )
        self._label.pack()

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None
            self._label = None
