#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum UI Controller (scripts/lib/ui_controller.py)
"""

import unittest
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.ui_controller import UIController, ProjectInfo


class TestUIController(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.controller = UIController(base_dir=self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_discover_projects_empty(self):
        projects = self.controller.discover_all_projects()
        self.assertEqual(len(projects["universes"]), 0)
        self.assertEqual(len(projects["worlds"]), 0)
        self.assertEqual(len(projects["manuscripts"]), 0)

    def test_discover_projects_with_data(self):
        # Create a Universe and World
        world_dir = self.root / "Universes" / "Cosmos" / "Aethelgard" / "00-World-Bible"
        world_dir.mkdir(parents=True)
        (world_dir.parent / "world.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")

        # Create a Manuscript
        ms_dir = self.root / "Manuscripts" / "The_Silmaril"
        ms_dir.mkdir(parents=True)

        projects = self.controller.discover_all_projects()
        self.assertEqual(len(projects["universes"]), 1)
        self.assertEqual(projects["universes"][0].name, "Cosmos")

        self.assertEqual(len(projects["worlds"]), 1)
        self.assertEqual(projects["worlds"][0].name, "Aethelgard")
        self.assertEqual(projects["worlds"][0].universe_name, "Cosmos")

        self.assertEqual(len(projects["manuscripts"]), 1)
        self.assertEqual(projects["manuscripts"][0].name, "The_Silmaril")

    def test_get_studio_engines(self):
        world_engines = self.controller.get_studio_engines("Worldbuilding")
        self.assertGreater(len(world_engines), 0)
        names = {e.name for e in world_engines}
        self.assertIn("astrophysics", names)
        self.assertIn("cartography", names)

    def test_system_health_summary(self):
        health = self.controller.get_system_health_summary()
        self.assertIn("tools", health)
        self.assertTrue(health["tools"]["python"]["available"])


if __name__ == "__main__":
    unittest.main()
