import unittest
from pathlib import Path

from utils.resources import resource_path


class ResourceTests(unittest.TestCase):
    def test_resource_path_resolves_project_root(self):
        self.assertEqual(resource_path("assets"), Path(__file__).resolve().parents[1] / "assets")


if __name__ == "__main__":
    unittest.main()
