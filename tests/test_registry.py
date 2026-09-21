#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Engine & Plugin Registry (scripts/lib/registry.py)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.registry import (
    EngineCategory,
    EngineSpec,
    get_registry,
    get_engine,
    list_engines,
    get_core_engines,
    get_craft_engines,
    is_engine_enabled,
    enable_engine,
    disable_engine,
    load_engine_module,
)


class TestRegistry(unittest.TestCase):

    def test_registry_contains_core_and_craft_engines(self):
        reg = get_registry()
        self.assertGreater(len(reg), 25)
        
        # Check core engines present
        core = get_core_engines()
        core_names = {e.name for e in core}
        self.assertIn("config", core_names)
        self.assertIn("cache", core_names)
        self.assertIn("fs_utils", core_names)
        self.assertIn("migrate", core_names)
        self.assertIn("docx_sync", core_names)
        self.assertIn("world_doctor", core_names)
        self.assertIn("concordance", core_names)
        self.assertIn("diagnostics", core_names)

        # Check craft engines present
        craft = get_craft_engines()
        craft_names = {e.name for e in craft}
        self.assertIn("astrophysics", craft_names)
        self.assertIn("climate", craft_names)
        self.assertIn("cartography", craft_names)
        self.assertIn("causality", craft_names)
        self.assertIn("factions", craft_names)
        self.assertIn("magic_system", craft_names)
        self.assertIn("voice", craft_names)

    def test_get_engine_by_name_and_alias(self):
        # By primary name
        eng = get_engine("docx_sync")
        self.assertIsNotNone(eng)
        self.assertEqual(eng.category, EngineCategory.CORE)
        self.assertEqual(eng.cli_command, "docx")

        # By alias
        eng_alias = get_engine("diff")
        self.assertIsNotNone(eng_alias)
        self.assertEqual(eng_alias.name, "manuscript_diff")

        # Unknown
        self.assertIsNone(get_engine("non_existent_engine_xyz"))

    def test_enable_disable_engine(self):
        self.assertTrue(is_engine_enabled("astrophysics"))
        disable_engine("astrophysics")
        self.assertFalse(is_engine_enabled("astrophysics"))
        
        # list_engines with enabled_only=True should exclude it
        enabled_craft = get_craft_engines(enabled_only=True)
        self.assertNotIn("astrophysics", {e.name for e in enabled_craft})

        # Re-enable
        enable_engine("astrophysics")
        self.assertTrue(is_engine_enabled("astrophysics"))
        enabled_craft_after = get_craft_engines(enabled_only=True)
        self.assertIn("astrophysics", {e.name for e in enabled_craft_after})

    def test_load_engine_module(self):
        mod = load_engine_module("fs_utils")
        self.assertTrue(hasattr(mod, "atomic_write"))


if __name__ == "__main__":
    unittest.main()
