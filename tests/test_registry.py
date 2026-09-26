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
    get_registry,
    get_engine,
    get_core_engines,
    get_craft_engines,
    is_engine_enabled,
    enable_engine,
    disable_engine,
    load_engine_module,
    get_engine_docs,
    get_all_engine_docs,
    format_engine_doc,
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

    def test_get_engine_lookups_and_aliases(self):
        # Hyphenated vs underscore
        self.assertIsNotNone(get_engine("magic-system"))
        self.assertIsNotNone(get_engine("scene-mechanics"))
        self.assertIsNotNone(get_engine("branching-graph"))
        self.assertIsNotNone(get_engine("series-continuity"))
        self.assertIsNotNone(get_engine("docx-sync"))
        self.assertIsNotNone(get_engine("world-doctor"))

        # Aliases and CLI commands
        self.assertIsNotNone(get_engine("calc astro"))
        self.assertIsNotNone(get_engine("polish typography"))
        self.assertIsNotNone(get_engine("astro"))
        self.assertIsNotNone(get_engine("diff"))

    def test_get_engine_docs(self):
        doc = get_engine_docs("astrophysics")
        self.assertIsNotNone(doc)
        assert doc is not None
        self.assertEqual(doc["name"], "astrophysics")
        self.assertEqual(doc["studio_tab"], "Worldbuilding")
        self.assertTrue(len(doc["logic_documentation"]) > 10)
        self.assertTrue(len(doc["worldbuilding_relevance"]) > 10)
        self.assertTrue(len(doc["storytelling_relevance"]) > 10)
        self.assertTrue(len(doc["writing_relevance"]) > 10)
        self.assertGreaterEqual(len(doc["advisory_guidance"]), 1)

        # Hyphenated lookup in get_engine_docs
        doc_hyphen = get_engine_docs("magic-system")
        self.assertIsNotNone(doc_hyphen)
        assert doc_hyphen is not None
        self.assertEqual(doc_hyphen["name"], "magic_system")

        # Non-existent
        self.assertIsNone(get_engine_docs("non_existent_fake"))

    def test_get_all_engine_docs(self):
        all_docs = get_all_engine_docs()
        self.assertGreaterEqual(len(all_docs), 50)
        for d in all_docs:
            self.assertIn("name", d)
            self.assertIn("title", d)
            self.assertIn("category", d)
            self.assertIn("studio_tab", d)
            self.assertIn("logic_documentation", d)
            self.assertIn("worldbuilding_relevance", d)
            self.assertIn("storytelling_relevance", d)
            self.assertIn("writing_relevance", d)
            self.assertIn("advisory_guidance", d)
            for adv in d["advisory_guidance"]:
                self.assertIn("pattern", adv)
                self.assertIn("option_a", adv)
                self.assertIn("option_b", adv)
                self.assertIn("option_c", adv)

    def test_format_engine_doc(self):
        formatted = format_engine_doc("magic_system")
        self.assertIn("MAGIC SYSTEM CONSTRAINTS", formatted)
        self.assertIn("Engine Logic & Scientific / Structural Foundations:", formatted)
        self.assertIn("Advisory Mechanics & Creative Freedom Resolution Pathways:", formatted)

        # Formatted via hyphenated string
        formatted_hyphen = format_engine_doc("magic-system")
        self.assertIn("MAGIC SYSTEM CONSTRAINTS", formatted_hyphen)

        # Unknown
        unknown_fmt = format_engine_doc("fake_xyz")
        self.assertIn("No documentation available", unknown_fmt)


if __name__ == "__main__":
    unittest.main()
