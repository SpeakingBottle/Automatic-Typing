import unittest

import customtkinter as ctk

from ui.countdown import CountdownOverlay
from ui.i18n import set_language
from utils.windows import get_screen_size


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

    def test_window_is_horizontally_centered(self):
        screen_width, _ = get_screen_size()
        if screen_width <= 0:
            self.skipTest("screen size unavailable")
        self.overlay.show_countdown(3, 3)
        self.overlay._window.update_idletasks()
        center = self.overlay._window.winfo_rootx() + self.overlay._window.winfo_width() / 2
        self.assertAlmostEqual(center, screen_width / 2, delta=2)

    def test_content_fills_window_width(self):
        for mode, show in (
            ("countdown", lambda: self.overlay.show_countdown(3, 3)),
            ("control", lambda: self.overlay.show_control(5, 10, 8)),
        ):
            with self.subTest(mode=mode):
                show()
                self.overlay._window.update()
                frame = (
                    self.overlay._countdown_frame
                    if mode == "countdown"
                    else self.overlay._control_frame
                )
                right_gap = self.overlay._window.winfo_width() - (
                    frame.winfo_x() + frame.winfo_width()
                )
                self.assertLessEqual(right_gap, 40)


if __name__ == "__main__":
    unittest.main()
