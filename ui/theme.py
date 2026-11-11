"""颜色 token、字体选择和外观模式。"""

from __future__ import annotations

import tkinter.font as tkfont

import customtkinter as ctk

COLORS: dict[str, tuple[str, str]] = {
    "bg": ("#F6F7F9", "#0F172A"),
    "surface": ("#FFFFFF", "#111827"),
    "surface_alt": ("#F3F4F6", "#1F2937"),
    "text": ("#111827", "#E5E7EB"),
    "text_muted": ("#6B7280", "#94A3B8"),
    "text_subtle": ("#94A3B8", "#64748B"),
    "border": ("#E5E7EB", "#263244"),
    "border_strong": ("#D1D5DB", "#334155"),
    "accent": ("#4F46E5", "#6366F1"),
    "accent_hover": ("#4338CA", "#4F46E5"),
    "accent_text": ("#FFFFFF", "#FFFFFF"),
    "danger": ("#DC2626", "#F87171"),
    "success": ("#059669", "#34D399"),
}

UI_FONT_CANDIDATES = ("Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI")
ARTICLE_FONT_CANDIDATES = ("Microsoft YaHei UI", "Microsoft YaHei")
CODE_FONT_CANDIDATES = ("Cascadia Code", "Cascadia Mono", "Consolas")


def _families() -> set[str]:
    try:
        return set(tkfont.families())
    except Exception:
        return set()


def get_font(candidates: tuple[str, ...], size: int, weight: str = "normal") -> tuple:
    """返回系统中第一个可用字体；全部不可用时退回 Segoe UI。"""
    families = _families()
    for family in candidates:
        if family in families:
            return (family, size, weight)
    return ("Segoe UI", size, weight)


def color(name: str, mode: str | None = None) -> str:
    """返回某个 token 在当前或指定外观模式下的单色值。"""
    light, dark = COLORS[name]
    current = (mode or ctk.get_appearance_mode()).lower()
    return dark if current == "dark" else light


def apply_appearance(mode: str) -> None:
    ctk.set_appearance_mode(mode)
