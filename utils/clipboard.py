"""
剪贴板工具模块。
使用 pyperclip 读取系统剪贴板内容。
"""

import pyperclip


def read_clipboard() -> str:
    """读取系统剪贴板中的文本内容。"""
    try:
        text = pyperclip.paste()
        return text if text else ""
    except Exception:
        return ""


def copy_to_clipboard(text: str) -> None:
    """将文本写入系统剪贴板。"""
    try:
        pyperclip.copy(text)
    except Exception:
        pass
