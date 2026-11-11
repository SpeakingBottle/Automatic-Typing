"""文本统计、速度换算和时长格式化。"""

from __future__ import annotations

from dataclasses import dataclass


def normalize_text(text: str) -> str:
    """移除 Windows 回车符，保留换行符。"""
    return text.replace("\r", "")


def count_chars(text: str) -> int:
    """统计字符数，排除 \\r。"""
    return len(normalize_text(text))


def count_lines(text: str) -> int:
    """统计行数；空文本为 0。"""
    normalized = normalize_text(text)
    if not normalized:
        return 0
    return normalized.count("\n") + 1


def characters_per_minute(speed_ms: int) -> int:
    """把每字毫秒数换算成每分钟字符数。"""
    if speed_ms <= 0:
        raise ValueError("speed_ms must be positive")
    return round(60000 / speed_ms)


def estimate_seconds(text: str, speed_ms: int, countdown_seconds: int) -> int:
    """粗略估算总用时；不计换行额外停顿和跳过缩进。"""
    typing_seconds = count_chars(text) * speed_ms / 1000
    return round(typing_seconds) + max(0, countdown_seconds)


def format_duration(seconds: int) -> str:
    """把秒数格式化为中文时长。"""
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds} 秒"
    minutes, remainder = divmod(seconds, 60)
    if remainder == 0:
        return f"{minutes} 分"
    return f"{minutes} 分 {remainder} 秒"


def speed_band(speed_ms: int) -> str:
    """把速度映射为人类可读的节奏标签。"""
    if speed_ms < 80:
        return "快速"
    if speed_ms < 150:
        return "自然"
    if speed_ms < 250:
        return "稳健"
    return "慢速"


@dataclass(frozen=True)
class TextStats:
    """编辑器文本的展示统计。"""

    chars: int
    lines: int
    estimated_seconds: int

    @classmethod
    def from_text(cls, text: str, speed_ms: int, countdown_seconds: int) -> "TextStats":
        return cls(
            chars=count_chars(text),
            lines=count_lines(text),
            estimated_seconds=estimate_seconds(text, speed_ms, countdown_seconds),
        )
