import unittest

import customtkinter as ctk

from ui.control_panel import ControlPanel, PresetBar
from ui.i18n import set_language
from ui.presets import ARTICLE_PRESET, CODE_PRESET


class ControlPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_preset_application(self):
        panel = ControlPanel(self.root, on_primary=lambda: None, on_stop=lambda: None)
        panel.apply_preset(CODE_PRESET)
        self.assertEqual(panel.speed_ms, 150)
        self.assertTrue(panel.skip_indent)
        panel.apply_preset(ARTICLE_PRESET)
        self.assertEqual(panel.speed_ms, 90)
        self.assertFalse(panel.skip_indent)
        panel.destroy()

    def test_state_changes_primary_text(self):
        panel = ControlPanel(self.root, on_primary=lambda: None, on_stop=lambda: None)
        panel.set_state("typing")
        self.assertEqual(panel.btn_primary.cget("text"), "暂停")
        panel.set_state("idle")
        self.assertEqual(panel.btn_primary.cget("text"), "开始打字")
        panel.set_state("finished")
        self.assertEqual(panel.btn_primary.cget("text"), "开始打字")
        panel.destroy()

    def test_preset_bar_returns_key(self):
        selected = []
        bar = PresetBar(self.root, on_change=selected.append)
        bar.set_selected("code")
        self.assertEqual(bar.segmented.get(), "代码")
        bar.destroy()

    def test_primary_disabled_without_text(self):
        panel = ControlPanel(self.root, on_primary=lambda: None, on_stop=lambda: None)
        panel.set_can_start(False)
        panel.set_state("idle")
        self.assertEqual(str(panel.btn_primary.cget("state")), "disabled")
        panel.set_can_start(True)
        self.assertEqual(str(panel.btn_primary.cget("state")), "normal")
        panel.set_state("typing")
        panel.set_can_start(False)
        self.assertEqual(str(panel.btn_primary.cget("state")), "normal")
        panel.destroy()

    def test_language_refresh(self):
        self.addCleanup(set_language, "zh")
        panel = ControlPanel(self.root, on_primary=lambda: None, on_stop=lambda: None)
        bar = PresetBar(self.root, on_change=lambda _key: None)
        bar.set_selected("code")

        set_language("en")
        panel.refresh_language()
        bar.refresh_language()

        self.assertEqual(panel.btn_primary.cget("text"), "Start typing")
        self.assertEqual(panel.speed_label.cget("text"), "Speed")
        self.assertEqual(bar.segmented.get(), "Code")
        panel.destroy()
        bar.destroy()


if __name__ == "__main__":
    unittest.main()
