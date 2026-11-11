import unittest

import customtkinter as ctk

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


if __name__ == "__main__":
    unittest.main()
