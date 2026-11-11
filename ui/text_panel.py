"""
文本输入面板组件。
包含多行文本框和操作按钮（读取剪贴板、清空）。
"""

import customtkinter as ctk

from utils.clipboard import read_clipboard


class TextPanel(ctk.CTkFrame):
    """文本输入面板：文本框 + 按钮行"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # 多行文本框
        self.textbox = ctk.CTkTextbox(
            self,
            font=("Microsoft YaHei", 13),
            border_width=1,
            corner_radius=8,
            wrap="word",
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # 按钮行
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_clipboard = ctk.CTkButton(
            btn_frame,
            text="📋 读取剪贴板",
            width=140,
            corner_radius=6,
            command=self._on_read_clipboard,
        )
        self.btn_clipboard.pack(side="left", padx=(0, 8))

        self.btn_clear = ctk.CTkButton(
            btn_frame,
            text="🗑 清空",
            width=100,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            text_color="#2c3e50",
            text_color_disabled="#95a5a6",
            command=self._on_clear,
        )
        self.btn_clear.pack(side="left")

    def get_text(self) -> str:
        """获取文本框中的内容。"""
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text: str) -> None:
        """设置文本框内容（替换）。"""
        self.textbox.delete("1.0", "end")
        if text:
            self.textbox.insert("1.0", text)

    def _on_read_clipboard(self) -> None:
        """读取剪贴板按钮回调。"""
        text = read_clipboard()
        if text:
            self.set_text(text)

    def _on_clear(self) -> None:
        """清空按钮回调。"""
        self.textbox.delete("1.0", "end")
