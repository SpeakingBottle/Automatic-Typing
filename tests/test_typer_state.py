import inspect
import unittest

from engine.typer import TypingEngine


class TypingEngineStateTests(unittest.TestCase):
    def test_start_exposes_randomize(self):
        signature = inspect.signature(TypingEngine.start)
        self.assertIn("randomize", signature.parameters)
        self.assertTrue(signature.parameters["randomize"].default)

    def test_completed_finish_calls_finished_only(self):
        engine = TypingEngine()
        events = []
        engine.on_finished = lambda: events.append("finished")
        engine.on_stopped = lambda: events.append("stopped")

        engine._finish(completed=True)

        self.assertEqual(events, ["finished"])
        self.assertFalse(engine.is_running)

    def test_stopped_finish_calls_stopped_only(self):
        engine = TypingEngine()
        events = []
        engine.on_finished = lambda: events.append("finished")
        engine.on_stopped = lambda: events.append("stopped")

        engine._finish(completed=False)

        self.assertEqual(events, ["stopped"])
        self.assertFalse(engine.is_running)

    def test_finish_is_idempotent(self):
        engine = TypingEngine()
        events = []
        engine.on_finished = lambda: events.append("finished")
        engine.on_stopped = lambda: events.append("stopped")

        engine._finish(completed=False)
        engine._finish(completed=True)

        self.assertEqual(events, ["stopped"])


if __name__ == "__main__":
    unittest.main()
