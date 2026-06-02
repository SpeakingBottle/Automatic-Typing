"""
独立测试：验证 SendInput 能否在记事本中输入字符。
运行方式: python test_sendinput.py
运行后你有 3 秒时间切换到记事本窗口。
"""
import ctypes
from ctypes import wintypes
import struct
import time
import sys

# ===== 结构体定义 =====
_psize = struct.calcsize("P")
_ULONG_PTR = ctypes.c_uint64 if _psize == 8 else ctypes.c_uint32

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ULONG_PTR),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", _ULONG_PTR),
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

# ===== 常量 =====
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
VK_SHIFT = 0x10
MAPVK_VK_TO_VSC = 0

user32 = ctypes.windll.user32

_MapVirtualKeyW = user32.MapVirtualKeyW
_MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
_MapVirtualKeyW.restype = wintypes.UINT

_VkKeyScanExW = user32.VkKeyScanExW
_VkKeyScanExW.argtypes = [wintypes.WCHAR, wintypes.HKL]
_VkKeyScanExW.restype = wintypes.SHORT

# ===== 辅助函数 =====
def _make_input(vk, scan, flags):
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = scan
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = 0
    return inp

def _send_input(inp):
    result = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    return result

def send_char_scan(char):
    """扫描码方式发送字符"""
    vk_shift = _VkKeyScanExW(char, 0)
    if vk_shift == -1:
        print(f"  [SKIP] 字符 '{char}' 无法映射")
        return False

    vk = vk_shift & 0xFF
    shift_state = (vk_shift >> 8) & 0xFF
    need_shift = bool(shift_state & 1)
    scan = _MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)

    if need_shift:
        shift_scan = _MapVirtualKeyW(VK_SHIFT, MAPVK_VK_TO_VSC)
        inp = _make_input(VK_SHIFT, shift_scan, 0)
        ret = _send_input(inp)
        time.sleep(0.005)

    inp = _make_input(0, scan, KEYEVENTF_SCANCODE)
    ret = _send_input(inp)
    inp2 = _make_input(0, scan, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP)
    ret2 = _send_input(inp2)

    if need_shift:
        time.sleep(0.005)
        shift_scan = _MapVirtualKeyW(VK_SHIFT, MAPVK_VK_TO_VSC)
        inp = _make_input(VK_SHIFT, shift_scan, KEYEVENTF_KEYUP)
        _send_input(inp)

    return ret > 0 and ret2 > 0


def send_char_vk(char):
    """虚拟键码方式发送字符（备用测试）"""
    vk_shift = _VkKeyScanExW(char, 0)
    if vk_shift == -1:
        return False

    vk = vk_shift & 0xFF
    scan = _MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)

    inp = _make_input(vk, scan, 0)
    ret = _send_input(inp)
    inp2 = _make_input(vk, scan, KEYEVENTF_KEYUP)
    ret2 = _send_input(inp2)

    return ret > 0 and ret2 > 0


# ===== 主测试 =====
if __name__ == "__main__":
    print("=" * 50)
    print(f"INPUT 结构体大小: {ctypes.sizeof(INPUT)} bytes")
    print(f"KEYBDINPUT 大小: {ctypes.sizeof(KEYBDINPUT)} bytes")
    print(f"MOUSEINPUT 大小:  {ctypes.sizeof(MOUSEINPUT)} bytes")
    print(f"指针大小:        {_psize} bytes")
    print(f"Python:          {sys.version}")
    print("=" * 50)

    test_text = "Hello World!@#\nabc\t123"

    print(f"\n将在 3 秒后开始打字，请切换到记事本...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    print("\n开始测试 (扫描码模式)...")
    for ch in test_text:
        if ch == '\n':
            print(f"  [Enter]")
            # Enter key
            scan = _MapVirtualKeyW(0x0D, MAPVK_VK_TO_VSC)
            inp = _make_input(0x0D, scan, 0)
            _send_input(inp)
            inp2 = _make_input(0x0D, scan, KEYEVENTF_KEYUP)
            _send_input(inp2)
        elif ch == '\t':
            print(f"  [Tab]")
            scan = _MapVirtualKeyW(0x09, MAPVK_VK_TO_VSC)
            inp = _make_input(0x09, scan, 0)
            _send_input(inp)
            inp2 = _make_input(0x09, scan, KEYEVENTF_KEYUP)
            _send_input(inp2)
        else:
            ok = send_char_scan(ch)
            status = "OK" if ok else "FAIL"
            print(f"  '{ch}' -> {status}", flush=True)
        time.sleep(0.1)

    print("\n完成！")
