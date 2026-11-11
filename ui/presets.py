"""文章 / 代码场景预设。"""

from __future__ import annotations

from dataclasses import dataclass

from ui.i18n import t


@dataclass(frozen=True)
class Preset:
    key: str
    font_candidates: tuple[str, ...]
    font_size: int
    speed_ms: int
    countdown_seconds: int
    skip_indent: bool
    randomize: bool

    @property
    def label(self) -> str:
        """按当前界面语言返回预设名称。"""
        return t(f"preset.{self.key}")


ARTICLE_PRESET = Preset(
    key="article",
    font_candidates=("Microsoft YaHei UI", "Microsoft YaHei"),
    font_size=14,
    speed_ms=90,
    countdown_seconds=3,
    skip_indent=False,
    randomize=True,
)

CODE_PRESET = Preset(
    key="code",
    font_candidates=("Cascadia Code", "Cascadia Mono", "Consolas"),
    font_size=13,
    speed_ms=150,
    countdown_seconds=3,
    skip_indent=True,
    randomize=True,
)

PRESETS = (ARTICLE_PRESET, CODE_PRESET)
PRESET_BY_KEY = {preset.key: preset for preset in PRESETS}
DEFAULT_PRESET = ARTICLE_PRESET
