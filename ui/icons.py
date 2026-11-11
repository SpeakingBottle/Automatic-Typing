"""Lucide PNG 图标加载与缓存。"""

from __future__ import annotations

from functools import lru_cache

from PIL import Image
import customtkinter as ctk

from utils.resources import resource_path


@lru_cache(maxsize=256)
def _load(path: str) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGBA").copy()


def get_icon(
    name: str,
    variant: str = "theme",
    size: tuple[int, int] = (18, 18),
) -> ctk.CTkImage | None:
    """加载图标；缺失或损坏时返回 None，调用方退化为文字。"""
    try:
        if variant == "theme":
            light = _load(str(resource_path(f"assets/icons/light/{name}.png")))
            dark = _load(str(resource_path(f"assets/icons/dark/{name}.png")))
            return ctk.CTkImage(light_image=light, dark_image=dark, size=size)

        folder = variant if variant in {"light", "dark", "on_accent"} else "light"
        image = _load(str(resource_path(f"assets/icons/{folder}/{name}.png")))
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    except Exception:
        return None
