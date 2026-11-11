import unittest

import customtkinter as ctk

from ui.countdown import CountdownOverlay
from ui.i18n import set_language


class CountdownOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        set_language("zh")
        self.overlay = CountdownOverlay(self.root)
        self.addCleanup(self.overlay.destroy)
        self.addCleanup(set_language, "zh")

    def test_countdown_mode_updates_ring_and_hint(self):
        self.overlay.show_countdown(3, 3)
        self.assertTrue(self.overlay.is_visible)
        self.assertEqual(
            self.overlay._ring.itemcget(self.overlay._ring_text, "text"),
            "3",
        )
        self.assertIn("3 秒后开始", self.overlay._countdown_hint.cget("text"))

    def test_control_mode_shows_progress_and_pause(self):
        self.overlay.show_control(5, 10, 8, paused=False)
        self.assertEqual(self.overlay._status_label.cget("text"), "正在输入")
        self.assertAlmostEqual(self.overlay._progress.get(), 0.5)
        self.overlay.set_paused(True)
        self.assertEqual(self.overlay._status_label.cget("text"), "已暂停")

    def test_language_refresh(self):
        self.overlay.show_control(5, 10, 8, paused=False)
        set_language("en")
        self.overlay.refresh_language()
        self.assertEqual(self.overlay._status_label.cget("text"), "Typing")
        self.assertIn("5/10", self.overlay._detail_label.cget("text"))


if __name__ == "__main__":
    unittest.main()
