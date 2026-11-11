import unittest

from ui.presets import ARTICLE_PRESET, CODE_PRESET, DEFAULT_PRESET, PRESET_BY_KEY, PRESETS


class PresetTests(unittest.TestCase):
    def test_default_is_article(self):
        self.assertIs(DEFAULT_PRESET, ARTICLE_PRESET)

    def test_article_defaults(self):
        self.assertEqual(ARTICLE_PRESET.speed_ms, 90)
        self.assertEqual(ARTICLE_PRESET.font_size, 14)
        self.assertFalse(ARTICLE_PRESET.skip_indent)

    def test_code_defaults(self):
        self.assertEqual(CODE_PRESET.speed_ms, 150)
        self.assertEqual(CODE_PRESET.font_size, 13)
        self.assertTrue(CODE_PRESET.skip_indent)

    def test_lookup(self):
        self.assertEqual(PRESET_BY_KEY["article"], ARTICLE_PRESET)
        self.assertEqual(PRESET_BY_KEY["code"], CODE_PRESET)
        self.assertEqual([p.key for p in PRESETS], ["article", "code"])


if __name__ == "__main__":
    unittest.main()
