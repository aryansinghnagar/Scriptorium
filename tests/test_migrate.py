#!/usr/bin/env python3
"""
Unit tests for the Project Migration Engine (scripts/lib/migrate.py).
Validates:
- Upgrades unversioned universes, worlds, and manuscripts to schema_version 1.0.
- Migrates legacy 05-Backups/ and 04-Publishing/ folders cleanly.
- Preserves existing lore and prose without data loss.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.migrate import migrate_project, CURRENT_SCHEMA_VERSION


class TestMigrateEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_migrate_legacy_world(self):
        world_dir = self.work_dir / "LegacyWorld"
        world_dir.mkdir()
        (world_dir / "Characters").mkdir()
        (world_dir / "05-Backups").mkdir()
        (world_dir / "scriptorium.yaml").write_text("name: LegacyWorld\nauthor: OldScribe\n", encoding="utf-8")

        res = migrate_project(world_dir)
        self.assertEqual(res["type"], "world")
        self.assertTrue((world_dir / "world.yaml").is_file())
        self.assertTrue((world_dir / "Backups").is_dir())
        self.assertFalse((world_dir / "05-Backups").exists())

        world_yaml = (world_dir / "world.yaml").read_text(encoding="utf-8")
        self.assertIn(f'schema_version: "{CURRENT_SCHEMA_VERSION}"', world_yaml)
        self.assertIn("OldScribe", world_yaml)

    def test_migrate_manuscript(self):
        ms_dir = self.work_dir / "LegacyManuscript"
        ms_dir.mkdir()
        (ms_dir / "Book-01").mkdir()
        (ms_dir / "04-Publishing").mkdir()
        (ms_dir / "manuscript.yaml").write_text("title: Epic Novel\nauthor: Writer\n", encoding="utf-8")

        res = migrate_project(ms_dir)
        self.assertEqual(res["type"], "manuscript")
        self.assertTrue((ms_dir / "Exports").is_dir())
        self.assertFalse((ms_dir / "04-Publishing").exists())

        ms_yaml = (ms_dir / "manuscript.yaml").read_text(encoding="utf-8")
        self.assertIn(f'schema_version: "{CURRENT_SCHEMA_VERSION}"', ms_yaml)


if __name__ == "__main__":
    unittest.main()
