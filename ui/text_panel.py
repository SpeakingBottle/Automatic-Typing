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
            toolbar,
            "clipboard",
            "读取剪贴板",
            lambda: self.on_read_clipboard and self.on_read_clipboard(),
        )
        self.btn_clipboard.pack(side="left")

        self.btn_clear = self._icon_button(
            toolbar,
            "trash-2",
            "清空",
            lambda: self.on_clear and self.on_clear(),
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
