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


def get_screen_size() -> tuple[int, int]:
    """返回主屏幕物理像素尺寸；非 Windows 返回 (0, 0)。"""
    if sys.platform != "win32":
        return (0, 0)
    try:
        user32 = _user32()
        user32.GetSystemMetrics.argtypes = [ctypes.c_int]
        user32.GetSystemMetrics.restype = ctypes.c_int
        return (int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1)))
    except Exception:
        return (0, 0)


def set_rounded_window_region(widget: tk.Misc, radius: int) -> None:
    """把原生窗口裁剪为圆角矩形，去掉无边框窗口外层的直角。"""
    if sys.platform != "win32":
        return
    try:
        widget.update_idletasks()
        width = widget.winfo_width()
        height = widget.winfo_height()
        if width <= 1 or height <= 1:
            return
        hwnd = get_window_handle(widget)
        if not hwnd:
            return
        gdi32 = ctypes.windll.gdi32
        gdi32.CreateRoundRectRgn.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        gdi32.CreateRoundRectRgn.restype = ctypes.c_void_p
        user32 = _user32()
        user32.SetWindowRgn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
        user32.SetWindowRgn.restype = ctypes.c_int
        region = gdi32.CreateRoundRectRgn(
            0,
            0,
            width + 1,
            height + 1,
            max(2, int(radius)) * 2,
            max(2, int(radius)) * 2,
        )
        if region:
            user32.SetWindowRgn(hwnd, region, True)
    except Exception:
        pass
