"""
主窗口应用。
组装所有 UI 面板，连接打字引擎与 UI 交互。
"""

import customtkinter as ctk

from engine.typer import TypingEngine
from ui.text_panel import TextPanel
from ui.control_panel import ControlPanel


# 浅蓝色主题配置
COLOR_THEME = {
    "bg": "#e8f4fd",           # 浅蓝背景
    "fg": "#1a1a2e",           # 深色文字
    "accent": "#4a90d9",       # 强调色（按钮等）
    "accent_hover": "#3a7bc8", # 悬停色
    "border": "#b8d4f0",       # 边框色
    "surface": "#f0f8ff",      # 卡片/面板底色
}


class App(ctk.CTk):
    """自动打字主窗口"""

    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title("自动打字 v1.0")
        self.geometry("700x560")
        self.minsize(500, 400)
        self.configure(fg_color=COLOR_THEME["bg"])

        # 设置 customtkinter 全局主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 图标（使用 Unicode 字符，Windows 窗口图标用空字符串兜底）
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # 打字引擎
        self._engine = TypingEngine()
        self._engine.on_countdown = self._on_countdown
        self._engine.on_progress = self._on_progress
        self._engine.on_finished = self._on_finished
        self._engine.on_status_change = self._on_status_change

        # ---- 构建界面 ----
        self._build_ui()

        # 窗口居中
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    # ==================== 构建界面 ====================

    def _build_ui(self) -> None:
        """构建所有 UI 组件。"""

        # ---- 标题栏 ----
        title_frame = ctk.CTkFrame(
            self, fg_color=COLOR_THEME["accent"], corner_radius=0
        )
        title_frame.pack(fill="x")

        title_label = ctk.CTkLabel(
            title_frame,
            text="⌨ 自动打字",
            font=("Microsoft YaHei", 20, "bold"),
            text_color="white",
        )
        title_label.pack(pady=12)

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="将代码逐字输入到任意文本框 · 专治禁止粘贴",
            font=("Microsoft YaHei", 12),
            text_color="#d0e4ff",
        )
        subtitle_label.pack(pady=(0, 12))

        # ---- 文本输入面板 ----
        self._text_panel = TextPanel(self, fg_color="transparent")
        self._text_panel.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # ---- 控制面板 ----
        self._control_panel = ControlPanel(self, fg_color="transparent")
        self._control_panel.pack(fill="x", padx=10, pady=(0, 10))

        # 连接按钮回调
        self._control_panel.on_start = self._handle_start
        self._control_panel.on_pause = self._handle_pause
        self._control_panel.on_stop = self._handle_stop

    # ==================== 按钮事件 ====================

    def _handle_start(self) -> None:
        """开始按钮回调。"""
        text = self._text_panel.get_text()
        if not text.strip():
            self._control_panel.set_status("请先输入要打字的文本！")
            return

        self._control_panel.set_running_state(running=True, paused=False)
        self._engine.start(
            text=text,
            base_delay_ms=self._control_panel.speed_ms,
            countdown_seconds=self._control_panel.countdown_seconds,
            skip_indent=self._control_panel.skip_indent,
        )

    def _handle_pause(self) -> None:
        """暂停/继续按钮回调。"""
        if self._engine.is_paused:
            self._engine.resume()
            self._control_panel.set_running_state(running=True, paused=False)
        else:
            self._engine.pause()
            self._control_panel.set_running_state(running=True, paused=True)

    def _handle_stop(self) -> None:
        """停止按钮回调。"""
        self._engine.stop()
        self._control_panel.set_running_state(running=False)

    # ==================== 引擎回调（子线程 -> UI 线程） ====================

    def _on_countdown(self, remaining: int) -> None:
        """倒计时回调。"""
        self.after(0, lambda: self._control_panel.set_status(
            f"倒计时 {remaining} 秒... 请切换到目标窗口！"
        ))

    def _on_progress(self, current: int, total: int) -> None:
        """进度回调。"""
        self.after(0, lambda: self._control_panel.set_status(
            f"正在打字... ({current}/{total})"
        ))

    def _on_finished(self) -> None:
        """完成回调。"""
        self.after(0, lambda: self._control_panel.set_running_state(running=False))
        self.after(0, lambda: self._control_panel.set_status("✅ 打字完成！"))

    def _on_status_change(self, status: str) -> None:
        """状态变更回调。"""
        self.after(0, lambda s=status: self._control_panel.set_status(s))
