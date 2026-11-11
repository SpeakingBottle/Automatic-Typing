"""
核心打字引擎。
使用 Windows SendInput API（扫描码模式）模拟键盘输入。
支持暂停、继续、停止控制，以及随机打字延迟。
"""

import ctypes
import random
import time
import threading

from .key_mapping import (
    INPUT,
    INPUT_KEYBOARD,
    KEYEVENTF_KEYUP,
    KEYEVENTF_SCANCODE,
    KEYEVENTF_UNICODE,
    VK_SHIFT,
    VK_TAB,
    VK_RETURN,
    SPECIAL_KEYS,
    _get_vk_scan_shift,
    _VkKeyScanExW,
    _MapVirtualKeyW,
    MAPVK_VK_TO_VSC,
)


def _make_input(vk: int, scan: int, flags: int) -> INPUT:
    """构造一个 INPUT 结构体。"""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = scan
    inp.union.ki.dwFlags = flags
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = 0
    return inp


def _send_input(inp: INPUT) -> None:
    """发送一次 INPUT 事件。"""
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def _press_scancode(scan: int) -> None:
    """按下扫描码对应的键。"""
    inp = _make_input(0, scan, KEYEVENTF_SCANCODE)
    _send_input(inp)


def _release_scancode(scan: int) -> None:
    """释放扫描码对应的键。"""
    inp = _make_input(0, scan, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP)
    _send_input(inp)


def _press_vk(vk: int) -> None:
    """按下虚拟键码对应的键。"""
    scan = _MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)
    inp = _make_input(vk, scan, 0)
    _send_input(inp)


def _release_vk(vk: int) -> None:
    """释放虚拟键码对应的键。"""
    scan = _MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)
    inp = _make_input(vk, scan, KEYEVENTF_KEYUP)
    _send_input(inp)


def _send_unicode_char(char: str) -> None:
    """
    使用 KEYEVENTF_UNICODE 模式发送 Unicode 字符（中文、emoji 等）。
    扫描码方式无法处理这些字符，只能通过 Unicode 模式发送 WM_CHAR。
    """
    code_point = ord(char)

    # key down: 产生 WM_CHAR 消息
    inp = _make_input(0, code_point, KEYEVENTF_UNICODE)
    _send_input(inp)

    # key up: 产生 WM_KEYUP (VK_PACKET) 消息
    inp = _make_input(0, code_point, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP)
    _send_input(inp)


def send_char(char: str) -> None:
    """
    发送单个字符的键盘输入。
    - ASCII 字符：使用 VkKeyScanEx + MapVirtualKey 转为扫描码，
      通过 KEYEVENTF_SCANCODE 模式发送，兼容性最佳。
    - 非 ASCII 字符（中文等）：使用 KEYEVENTF_UNICODE 模式发送。
    """
    if not char:
        return

    # ---- 跳过 \r，避免 Windows \r\n 双回车 ----
    if char == '\r':
        return

    # ---- 特殊键：Enter、Tab ----
    if char in SPECIAL_KEYS:
        vk = SPECIAL_KEYS[char]
        _press_vk(vk)
        time.sleep(0.005)   # 确保目标应用能捕获按键事件
        _release_vk(vk)
        return

    # ---- 非 ASCII 字符：使用 Unicode 模式 ----
    if _VkKeyScanExW(char, 0) == -1:
        _send_unicode_char(char)
        return

    # ---- 普通 ASCII 字符：使用扫描码方式 ----
    vk, scan, need_shift = _get_vk_scan_shift(char)

    if need_shift:
        _press_vk(VK_SHIFT)
        time.sleep(0.002)

    _press_scancode(scan)
    _release_scancode(scan)

    if need_shift:
        time.sleep(0.002)
        _release_vk(VK_SHIFT)


class TypingEngine:
    """打字引擎，在独立线程中运行。"""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._paused = False
        self._stopped = False
        self._running = False

        # 回调函数
        self.on_countdown: callable | None = None      # 倒计时回调(remaining_seconds)
        self.on_progress: callable | None = None        # 进度回调(current_index, total_chars)
        self.on_finished: callable | None = None        # 完成回调
        self.on_status_change: callable | None = None   # 状态变化回调(status: str)

    # ---- 属性 ----
    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    # ---- 控制方法 ----
    def start(self, text: str, base_delay_ms: int = 50, countdown_seconds: int = 3,
              skip_indent: bool = True) -> None:
        """
        开始打字。
        Args:
            text: 要输入的文本
            base_delay_ms: 基础字符间隔（毫秒）
            countdown_seconds: 开始前的倒计时秒数
            skip_indent: 是否跳过行首缩进（依赖编辑器自动缩进）
        """
        if self._running:
            return
        self._running = True
        self._paused = False
        self._stopped = False
        self._thread = threading.Thread(
            target=self._typing_loop,
            args=(text, base_delay_ms / 1000.0, countdown_seconds, skip_indent),
            daemon=True,
        )
        self._thread.start()

    def pause(self) -> None:
        """暂停打字。"""
        self._paused = True
        if self.on_status_change:
            self.on_status_change("已暂停")

    def resume(self) -> None:
        """继续打字。"""
        self._paused = False
        if self.on_status_change:
            self.on_status_change("正在打字...")

    def stop(self) -> None:
        """停止打字。"""
        self._stopped = True
        self._paused = False
        self._running = False
        if self.on_status_change:
            self.on_status_change("已停止")

    # ---- 内部逻辑 ----
    def _typing_loop(self, text: str, base_delay: float, countdown: int,
                     skip_indent: bool) -> None:
        """打字主循环（运行在子线程中）。"""
        # === 倒计时阶段 ===
        for i in range(countdown, 0, -1):
            if self._stopped:
                self._finish()
                return
            if self.on_countdown:
                self.on_countdown(i)
            if self.on_status_change:
                self.on_status_change(f"倒计时 {i} 秒...")
            time.sleep(1)

        if self._stopped:
            self._finish()
            return

        if self.on_status_change:
            self.on_status_change("正在打字...")

        # === 打字阶段 ===
        at_line_start = True  # 文本开头视为行首
        total = len(text)
        for idx, char in enumerate(text):
            if self._stopped:
                self._finish()
                return

            while self._paused and not self._stopped:
                time.sleep(0.1)

            if self._stopped:
                self._finish()
                return

            # ---- 跳过 \r：必须在循环层处理，避免额外延时和干扰 at_line_start ----
            if char == '\r':
                if self.on_progress:
                    self.on_progress(idx + 1, total)
                continue

            # ---- 行首跳过缩进：依赖编辑器自动缩进 ----
            if at_line_start and skip_indent and char in (' ', '\t'):
                # 不发送，但更新进度；加微小延迟让编辑器有时间完成自动缩进
                if self.on_progress:
                    self.on_progress(idx + 1, total)
                time.sleep(0.005)
                continue

            # 发送字符
            send_char(char)

            # 更新行首状态：换行后下一字符在行首，否则不在行首
            if char == '\n':
                at_line_start = True
                time.sleep(0.05)  # 给编辑器处理换行的时间，防止 PTA 自动补全吞掉 Enter
            else:
                at_line_start = False

            if self.on_progress:
                self.on_progress(idx + 1, total)

            # 随机延迟（±30% 波动，模拟真人）
            variation = base_delay * 0.3
            delay = base_delay + random.uniform(-variation, variation)
            delay = max(delay, 0.005)
            time.sleep(delay)

        self._finish()

    def _finish(self) -> None:
        """打字结束，重置状态。"""
        self._running = False
        self._paused = False
        if self.on_finished:
            self.on_finished()
        if self.on_status_change:
            self.on_status_change("等待开始...")
