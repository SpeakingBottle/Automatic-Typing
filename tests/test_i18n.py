import unittest

from ui.formatting import format_duration, speed_band
from ui.i18n import get_language, set_language, t, toggle_language
from ui.presets import ARTICLE_PRESET


class I18nTests(unittest.TestCase):
    def setUp(self):
        set_language("zh")

    def tearDown(self):
        set_language("zh")

    def test_default_is_chinese(self):
        self.assertEqual(get_language(), "zh")
        self.assertEqual(t("action.start"), "开始打字")

    def test_english_translation_and_format(self):
        set_language("en")
        self.assertEqual(get_language(), "en")
        self.assertEqual(t("action.start"), "Start typing")
        self.assertEqual(t("editor.stats", chars=3, lines=2), "3 chars · 2 lines")

    def test_toggle_language(self):
        self.assertEqual(toggle_language(), "en")
        self.assertEqual(toggle_language(), "zh")

    def test_missing_key_falls_back_to_key(self):
        self.assertEqual(t("does.not.exist"), "does.not.exist")

    def test_unsupported_language_raises(self):
        with self.assertRaises(ValueError):
            set_language("fr")

    def test_formatting_follows_language(self):
        set_language("en")
        self.assertEqual(format_duration(45), "45s")
        self.assertEqual(format_duration(80), "1m 20s")
        self.assertEqual(speed_band(90), "Natural")
        self.assertEqual(ARTICLE_PRESET.label, "Article / Homework")


if __name__ == "__main__":
    unittest.main()
