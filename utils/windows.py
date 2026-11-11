"""Windows 前台窗口与原生窗口句柄工具。"""

from __future__ import annotations

import ctypes
import sys
import tkinter as tk

_GA_ROOT = 2


def _user32():
    return ctypes.windll.user32


def get_window_handle(widget: tk.Misc) -> int:
    """返回 tkinter 控件的顶层原生窗口句柄。"""
    if sys.platform != "win32":
        return 0
    try:
        user32 = _user32()
        user32.GetAncestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        user32.GetAncestor.restype = ctypes.c_void_p
        hwnd = int(widget.winfo_id())
        root = user32.GetAncestor(hwnd, _GA_ROOT)
        return int(root or hwnd)
    except Exception:
        return 0


def get_foreground_window() -> int:
    """返回当前前台窗口句柄。"""
    if sys.platform != "win32":
        return 0
    try:
        user32 = _user32()
        user32.GetForegroundWindow.restype = ctypes.c_void_p
        return int(user32.GetForegroundWindow() or 0)
    except Exception:
        return 0


def set_foreground_window(hwnd: int) -> bool:
    """把指定窗口切换到前台；成功返回 True。"""
    if sys.platform != "win32" or not hwnd:
        return False
    try:
        user32 = _user32()
        user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
        user32.SetForegroundWindow.restype = ctypes.c_bool
        return bool(user32.SetForegroundWindow(hwnd))
    except Exception:
        return False
