import unittest

import customtkinter as ctk

from ui.i18n import set_language
from ui.text_panel import TextPanel


class TextPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_placeholder_is_not_content(self):
        panel = TextPanel(self.root)
        self.assertEqual(panel.get_text(), "")
        panel.destroy()

    def test_set_and_clear_text(self):
        panel = TextPanel(self.root)
        panel.set_text("hello")
        self.assertEqual(panel.get_text(), "hello")
        panel.clear()
        self.assertEqual(panel.get_text(), "")
        panel.destroy()

    def test_placeholder_follows_language(self):
        self.addCleanup(set_language, "zh")
        panel = TextPanel(self.root)
        set_language("en")
        panel.refresh_language()
        self.assertEqual(panel.textbox.get("1.0", "end-1c"), "Type or paste text here…")
        panel.destroy()


if __name__ == "__main__":
    unittest.main()
