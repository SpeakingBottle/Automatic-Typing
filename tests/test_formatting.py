import unittest

from ui.formatting import (
    TextStats,
    characters_per_minute,
    count_chars,
    count_lines,
    estimate_seconds,
    format_duration,
    speed_band,
)


class FormattingTests(unittest.TestCase):
    def test_count_chars_ignores_carriage_return(self):
        self.assertEqual(count_chars("a\r\nb"), 3)

    def test_count_lines(self):
        self.assertEqual(count_lines(""), 0)
        self.assertEqual(count_lines("abc"), 1)
        self.assertEqual(count_lines("a\nb\nc"), 3)

    def test_characters_per_minute(self):
        self.assertEqual(characters_per_minute(150), 400)
        self.assertEqual(characters_per_minute(90), 667)

    def test_estimate_seconds_includes_countdown(self):
        self.assertEqual(estimate_seconds("a" * 100, 100, 3), 13)

    def test_format_duration(self):
        self.assertEqual(format_duration(0), "0 秒")
        self.assertEqual(format_duration(45), "45 秒")
        self.assertEqual(format_duration(60), "1 分")
        self.assertEqual(format_duration(80), "1 分 20 秒")

    def test_speed_band_boundaries(self):
        self.assertEqual(speed_band(30), "快速")
        self.assertEqual(speed_band(79), "快速")
        self.assertEqual(speed_band(80), "自然")
        self.assertEqual(speed_band(149), "自然")
        self.assertEqual(speed_band(150), "稳健")
        self.assertEqual(speed_band(249), "稳健")
        self.assertEqual(speed_band(250), "慢速")

    def test_text_stats(self):
        stats = TextStats.from_text("abc\ndef", 100, 3)
        self.assertEqual(stats.chars, 7)
        self.assertEqual(stats.lines, 2)
        self.assertEqual(stats.estimated_seconds, 4)


if __name__ == "__main__":
    unittest.main()
