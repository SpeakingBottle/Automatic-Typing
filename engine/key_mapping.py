"""
字符到 Windows 虚拟键码 / 扫描码的映射表。
使用 ctypes 定义 SendInput 所需的常量和结构体。
"""

import ctypes
from ctypes import wintypes

# ULONG_PTR 在某些 Python 版本的 wintypes 中不存在，使用 POINTER 大小推断
import struct
_pointer_size = struct.calcsize("P")
_ulong_ptr = ctypes.c_uint64 if _pointer_size == 8 else ctypes.c_uint32

# ==================== Windows API 常量 ====================

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# 虚拟键码 (Virtual-Key Codes)
VK_SHIFT = 0x10
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SPACE = 0x20
VK_BACK = 0x08

# MapVirtualKey 常量
MAPVK_VK_TO_VSC = 0

# ==================== SendInput 结构体 ====================

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ulong_ptr),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ulong_ptr),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


# ==================== Windows API 函数绑定 ====================

user32 = ctypes.windll.user32

# UINT MapVirtualKeyW(UINT uCode, UINT uMapType)
_MapVirtualKeyW = user32.MapVirtualKeyW
_MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
_MapVirtualKeyW.restype = wintypes.UINT

# SHORT VkKeyScanExW(WCHAR ch, HKL dwhkl)
_VkKeyScanExW = user32.VkKeyScanExW
_VkKeyScanExW.argtypes = [wintypes.WCHAR, wintypes.HKL]
_VkKeyScanExW.restype = wintypes.SHORT


def _get_vk_scan_shift(char: str) -> tuple[int, int, bool]:
    """
    使用 VkKeyScanEx 获取字符的虚拟键码、扫描码、是否需要 Shift。
    返回: (vk_code, scan_code, need_shift)
    """
    vk_shift_state = _VkKeyScanExW(char, 0)

    if vk_shift_state == -1:
        # 无法映射的字符，用空格代替
        return (VK_SPACE, _MapVirtualKeyW(VK_SPACE, MAPVK_VK_TO_VSC), False)

    vk = vk_shift_state & 0xFF
    shift_state = (vk_shift_state >> 8) & 0xFF
    need_shift = bool(shift_state & 1)

    scan = _MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)

    return (vk, scan, need_shift)


# ==================== 特殊键处理 ====================

SPECIAL_KEYS: dict[str, int] = {
    '\n': VK_RETURN,  # 换行 → Enter
    '\t': VK_TAB,     # 制表符 → Tab
    # '\r' 不处理：Windows 换行为 \r\n，只让 \n 触发 Enter，避免双回车
}
