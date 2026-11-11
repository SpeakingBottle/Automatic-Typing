"""界面文案与中英文切换。"""

from __future__ import annotations

LANGUAGE_ZH = "zh"
LANGUAGE_EN = "en"
LANGUAGES = (LANGUAGE_ZH, LANGUAGE_EN)

_current_language = LANGUAGE_ZH

_TRANSLATIONS: dict[str, dict[str, str]] = {
    LANGUAGE_ZH: {
        "app.title": "自动打字",
        "app.subtitle": "把文字逐字输入任意窗口",
        "app.tooltip.pin": "窗口置顶",
        "app.tooltip.theme": "切换主题",
        "app.tooltip.language": "切换语言 / Switch language",
        "preset.article": "文章 / 作业",
        "preset.code": "代码",
        "editor.placeholder": "在这里输入或粘贴文字…",
        "editor.stats": "{chars} 字 · {lines} 行",
        "editor.tooltip.clipboard": "读取剪贴板",
        "editor.tooltip.clear": "清空",
        "control.scene": "场景",
        "control.speed": "节奏",
        "control.countdown": "倒计时",
        "control.speed_value": "{band} · {speed} ms/字 · 约 {cpm} 字/分",
        "control.advanced": "高级设置",
        "control.advanced_collapse": "收起高级设置",
        "control.skip_indent": "跳过行首缩进（依赖目标编辑器自动缩进）",
        "control.randomize": "自然节奏（±30% 随机延迟）",
        "control.stop": "停止",
        "countdown.option": "{n} 秒",
        "action.start": "开始打字",
        "action.cancel": "取消",
        "action.pause": "暂停",
        "action.resume": "继续",
        "action.restart": "再次开始",
        "duration.seconds": "{n} 秒",
        "duration.minutes": "{n} 分",
        "duration.minutes_seconds": "{m} 分 {s} 秒",
        "speed.fast": "快速",
        "speed.natural": "自然",
        "speed.steady": "稳健",
        "speed.slow": "慢速",
        "status.preset": "已切换为「{label}」预设",
        "status.ready": "就绪 · 预计用时 {duration}",
        "status.enter_text": "请输入要输入的文字",
        "status.need_text": "请先输入要输入的文字",
        "status.preparing": "准备中…",
        "status.paused": "已暂停",
        "status.typing": "正在输入…",
        "status.countdown": "{n} 秒后开始，请切换到目标窗口",
        "status.progress": "正在输入 {current}/{total} · 剩余约 {remaining}",
        "status.finished": "完成 · 用时 {duration}",
        "status.stopped": "已停止",
        "status.clipboard_failed": "读取剪贴板失败",
        "status.clipboard_empty": "剪贴板中没有文本",
        "status.clipboard_read": "已读取剪贴板",
        "status.cleared": "已清空",
        "overlay.title": "准备开始",
        "overlay.hint": "秒后开始 · 请切换到目标窗口",
    },
    LANGUAGE_EN: {
        "app.title": "Automatic Typing",
        "app.subtitle": "Type text character by character into any window",
        "app.tooltip.pin": "Keep window on top",
        "app.tooltip.theme": "Toggle theme",
        "app.tooltip.language": "Switch language / 切换语言",
        "preset.article": "Article / Homework",
        "preset.code": "Code",
        "editor.placeholder": "Type or paste text here…",
        "editor.stats": "{chars} chars · {lines} lines",
        "editor.tooltip.clipboard": "Read clipboard",
        "editor.tooltip.clear": "Clear",
        "control.scene": "Scene",
        "control.speed": "Speed",
        "control.countdown": "Countdown",
        "control.speed_value": "{band} · {speed} ms/char · ~{cpm} chars/min",
        "control.advanced": "Advanced settings",
        "control.advanced_collapse": "Hide advanced settings",
        "control.skip_indent": "Skip leading indentation (relies on editor auto-indent)",
        "control.randomize": "Natural rhythm (±30% random delay)",
        "control.stop": "Stop",
        "countdown.option": "{n} s",
        "action.start": "Start typing",
        "action.cancel": "Cancel",
        "action.pause": "Pause",
        "action.resume": "Resume",
        "action.restart": "Start again",
        "duration.seconds": "{n}s",
        "duration.minutes": "{n}m",
        "duration.minutes_seconds": "{m}m {s}s",
        "speed.fast": "Fast",
        "speed.natural": "Natural",
        "speed.steady": "Steady",
        "speed.slow": "Slow",
        "status.preset": "Switched to the “{label}” preset",
        "status.ready": "Ready · estimated {duration}",
        "status.enter_text": "Enter the text you want to type",
        "status.need_text": "Please enter some text first",
        "status.preparing": "Preparing…",
        "status.paused": "Paused",
        "status.typing": "Typing…",
        "status.countdown": "Starting in {n}s — switch to the target window",
        "status.progress": "Typing {current}/{total} · ~{remaining} left",
        "status.finished": "Done · took {duration}",
        "status.stopped": "Stopped",
        "status.clipboard_failed": "Could not read the clipboard",
        "status.clipboard_empty": "The clipboard contains no text",
        "status.clipboard_read": "Clipboard loaded",
        "status.cleared": "Cleared",
        "overlay.title": "Get ready",
        "overlay.hint": "seconds · switch to the target window",
    },
}


def get_language() -> str:
    """返回当前界面语言代码。"""
    return _current_language


def set_language(language: str) -> None:
    """切换界面语言；不支持的语言代码抛出 ValueError。"""
    global _current_language
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    _current_language = language


def toggle_language() -> str:
    """在中英文之间切换，并返回切换后的语言代码。"""
    set_language(LANGUAGE_EN if _current_language == LANGUAGE_ZH else LANGUAGE_ZH)
    return _current_language


def t(key: str, **kwargs) -> str:
    """读取当前语言的文案；缺失时回退中文，再回退 key。"""
    table = _TRANSLATIONS.get(_current_language, {})
    text = table.get(key)
    if text is None:
        text = _TRANSLATIONS[LANGUAGE_ZH].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
