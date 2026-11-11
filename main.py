"""
自动打字软件入口。
启动 Windows GUI 应用。
"""

import ctypes
import os
import sys

# 确保项目根目录在 sys.path 中（打包后也能正确导入）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App

APP_USER_MODEL_ID = "SpeakingBottle.AutomaticTyping"


def _set_app_user_model_id() -> None:
    """让任务栏使用应用自己的图标，而不是 Python 解释器图标。"""
    if sys.platform != "win32":
        return
    try:
        shell32 = ctypes.windll.shell32
        shell32.SetCurrentProcessExplicitAppUserModelID.argtypes = [ctypes.c_wchar_p]
        shell32.SetCurrentProcessExplicitAppUserModelID.restype = ctypes.c_long
        shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        pass


def main():
    _set_app_user_model_id()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
