"""
控制面板组件。
包含打字速度滑块、倒计时设置、开始/暂停/停止按钮。
"""

import customtkinter as ctk


class ControlPanel(ctk.CTkFrame):
    """控制面板：参数调节 + 打字控制按钮"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ---- 打字速度 ----
        speed_label = ctk.CTkLabel(
            self, text="打字速度:", font=("Microsoft YaHei", 13)
        )
        speed_label.grid(row=0, column=0, sticky="w", padx=10, pady=(12, 0))

        self.speed_value_label = ctk.CTkLabel(
            self, text="150 ms", font=("Microsoft YaHei", 13, "bold"), width=60
        )
        self.speed_value_label.grid(row=0, column=2, sticky="e", padx=(0, 10), pady=(12, 0))

        self.speed_slider = ctk.CTkSlider(
            self,
            from_=30,
            to=500,
            number_of_steps=94,
            command=self._on_speed_change,
        )
        self.speed_slider.set(150)
        self.speed_slider.grid(row=0, column=1, sticky="ew", padx=10, pady=(12, 0))

        # ---- 倒计时 ----
        countdown_label = ctk.CTkLabel(
            self, text="倒计时:", font=("Microsoft YaHei", 13)
        )
        countdown_label.grid(row=1, column=0, sticky="w", padx=10, pady=(8, 0))

        self.countdown_value_label = ctk.CTkLabel(
            self, text="3 秒", font=("Microsoft YaHei", 13, "bold"), width=60
        )
        self.countdown_value_label.grid(row=1, column=2, sticky="e", padx=(0, 10), pady=(8, 0))

        self.countdown_slider = ctk.CTkSlider(
            self,
            from_=1,
            to=10,
            number_of_steps=9,
            command=self._on_countdown_change,
        )
        self.countdown_slider.set(3)
        self.countdown_slider.grid(row=1, column=1, sticky="ew", padx=10, pady=(8, 0))

        # 列权重：让中间滑块列可以拉伸
        self.grid_columnconfigure(1, weight=1)

        # ---- 行首缩进跳过 ----
        self.skip_indent_var = ctk.BooleanVar(value=True)
        self.skip_indent_check = ctk.CTkCheckBox(
            self,
            text="跳过行首缩进（依赖编辑器自动缩进，避免重复缩进）",
            variable=self.skip_indent_var,
            font=("Microsoft YaHei", 12),
            checkbox_width=18,
            checkbox_height=18,
            border_width=1,
        )
        self.skip_indent_check.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 0))

        # ---- 控制按钮 ----
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(10, 12))

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text="▶ 开始打字",
            width=120,
            height=36,
            corner_radius=8,
            font=("Microsoft YaHei", 14, "bold"),
            command=self._on_start,
        )
        self.btn_start.pack(side="left", padx=4)

        self.btn_pause = ctk.CTkButton(
            btn_frame,
            text="⏸ 暂停",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            text_color="#2c3e50",
            text_color_disabled="#95a5a6",
            state="disabled",
            command=self._on_pause,
        )
        self.btn_pause.pack(side="left", padx=4)

        self.btn_stop = ctk.CTkButton(
            btn_frame,
            text="⏹ 停止",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            text_color="#2c3e50",
            text_color_disabled="#95a5a6",
            state="disabled",
            command=self._on_stop,
        )
        self.btn_stop.pack(side="left", padx=4)

        # ---- 状态栏 ----
        self.status_label = ctk.CTkLabel(
            self,
            text="等待开始...",
            font=("Microsoft YaHei", 12),
            text_color="gray",
        )
        self.status_label.grid(row=4, column=0, columnspan=3, pady=(0, 10))

        # 回调引用（由 App 设置）
        self.on_start: callable | None = None
        self.on_pause: callable | None = None
        self.on_stop: callable | None = None

    # ---- 属性 ----
    @property
    def speed_ms(self) -> int:
        return int(self.speed_slider.get())

    @property
    def countdown_seconds(self) -> int:
        return int(self.countdown_slider.get())

    @property
    def skip_indent(self) -> bool:
        return self.skip_indent_var.get()

    # ---- UI 更新 ----
    def set_status(self, text: str) -> None:
        """更新状态栏文本。"""
        self.status_label.configure(text=text)

    def set_running_state(self, running: bool, paused: bool = False) -> None:
        """
        设置按钮的启用/禁用状态。
        running=False: 开始可用，暂停/停止禁用
        running=True, paused=False: 开始禁用，暂停/停止可用
        running=True, paused=True: 开始禁用，暂停显示"继续"，停止可用
        """
        if not running:
            self.btn_start.configure(state="normal")
            self.btn_pause.configure(state="disabled", text="⏸ 暂停")
            self.btn_stop.configure(state="disabled")
        elif paused:
            self.btn_start.configure(state="disabled")
            self.btn_pause.configure(state="normal", text="▶ 继续")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_start.configure(state="disabled")
            self.btn_pause.configure(state="normal", text="⏸ 暂停")
            self.btn_stop.configure(state="normal")

    # ---- 内部回调 ----
    def _on_speed_change(self, value: float) -> None:
        self.speed_value_label.configure(text=f"{int(value)} ms")

    def _on_countdown_change(self, value: float) -> None:
        self.countdown_value_label.configure(text=f"{int(value)} 秒")

    def _on_start(self) -> None:
        if self.on_start:
            self.on_start()

    def _on_pause(self) -> None:
        if self.on_pause:
            self.on_pause()

    def _on_stop(self) -> None:
        if self.on_stop:
            self.on_stop()
