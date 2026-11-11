"""开发环境与 PyInstaller 打包环境的资源路径解析。"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """返回资源绝对路径；打包后从 sys._MEIPASS 读取。"""
    if getattr(sys, "frozen", False):
        root = Path(sys._MEIPASS)
    else:
        root = Path(__file__).resolve().parents[1]
    return root / relative
