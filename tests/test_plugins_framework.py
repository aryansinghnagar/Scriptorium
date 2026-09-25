#!/usr/bin/env python3
"""
Test Suite: Speculative Fiction Plugin Architecture & Extensibility
(tests/test_plugins_framework.py)
================================================================================
Validates plugin discovery, manifest parsing, sandboxed execution, and built-in plugins.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.plugins import PluginManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPluginsFramework(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.plugins_dir = self.root / "plugins"
        self.plugins_dir.mkdir()
        self.state_file = self.root / ".test_plugins_state.json"
        self.mgr = PluginManager(search_paths=[self.plugins_dir, PROJECT_ROOT / "configs" / "plugins"], state_file=self.state_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_built_in_plugins_discovered(self):
        plugins = self.mgr.list_plugins()
        plugin_ids = {p.id for p in plugins}
        self.assertIn("speculative_naming", plugin_ids)
        self.assertIn("magic_system_audit", plugin_ids)
        self.assertIn("pacing_heat_map", plugin_ids)

    def test_plugin_manifest_properties(self):
        p = self.mgr.get_plugin("magic_system_audit")
        self.assertIsNotNone(p)
        self.assertEqual(p.category, "speculative")
        self.assertIn("validate_entity", p.hooks)
        self.assertTrue(p.enabled)

    def test_scaffold_new_plugin(self):
        new_plugin_dir = self.mgr.create_plugin_scaffold(
            target_dir=self.plugins_dir,
            plugin_id="custom_creature_audit",
            name="Custom Creature Auditor",
            author="Lore Master",
            description="Audits bestiary entries for ecological consistency.",
            category="speculative",
        )
        self.assertTrue(new_plugin_dir.is_dir())
        manifest_file = new_plugin_dir / "plugin.json"
        self.assertTrue(manifest_file.is_file())
        self.assertTrue((new_plugin_dir / "plugin.py").is_file())
        self.assertTrue((new_plugin_dir / "README.md").is_file())

        # Rediscover
        self.mgr.discover_plugins()
        custom = self.mgr.get_plugin("custom_creature_audit")
        self.assertIsNotNone(custom)
        self.assertEqual(custom.name, "Custom Creature Auditor")

    def test_plugin_enable_disable_state(self):
        self.assertTrue(self.mgr.disable_plugin("magic_system_audit"))
        p = self.mgr.get_plugin("magic_system_audit")
        self.assertFalse(p.enabled)
        self.assertTrue(self.state_file.is_file())

        # Re-enable
        self.assertTrue(self.mgr.enable_plugin("magic_system_audit"))
        p = self.mgr.get_plugin("magic_system_audit")
        self.assertTrue(p.enabled)

    def test_error_isolation_on_crashing_plugin(self):
        # Create a buggy plugin that throws an exception
        bad_dir = self.plugins_dir / "buggy_plugin"
        bad_dir.mkdir()
        manifest = {
            "id": "buggy_plugin",
            "name": "Buggy Plugin",
            "version": "1.0.0",
            "entry_point": "plugin.py",
            "hooks": ["validate_entity"],
        }
        (bad_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
        (bad_dir / "plugin.py").write_text("def hook_validate_entity(e, c):\n    raise RuntimeError('Catastrophic failure in plugin!')\n", encoding="utf-8")

        self.mgr.discover_plugins()
        results = self.mgr.execute_hook("validate_entity", {"name": "Test"}, {})
        self.assertIn("buggy_plugin", results)
        self.assertTrue(results["buggy_plugin"].get("crashed"))

    def test_speculative_naming_plugin(self):
        p_naming = self.mgr.get_plugin("speculative_naming")
        self.assertIsNotNone(p_naming)

        # 1. Phoneme collision check
        context = {"known_names": ["Aeloria", "Kaelen", "Theron"]}
        diag = self.mgr.run_entity_validation({"name": "Aelora"}, context=context, plugin_id="speculative_naming")
        self.assertTrue(any("Aeloria" in d.message for d in diag))

        # 2. Consonant cluster check
        diag_cluster = self.mgr.run_entity_validation({"name": "Xzklthvr"}, context={}, plugin_id="speculative_naming")
        self.assertTrue(any("consonant cluster" in d.message for d in diag_cluster))

    def test_magic_system_audit_plugin(self):
        # Entity with magic description but no cost
        unbalanced_spell = {
            "name": "Oblivion-Flare",
            "path": "Magic/Spells/Oblivion-Flare.md",
            "content": "A supreme incantation that instantly destroys any castle across the cosmos with pure aether fire.",
        }
        diag = self.mgr.run_entity_validation(unbalanced_spell, context={}, plugin_id="magic_system_audit")
        self.assertTrue(any("Cost, Limitation, or Drawback" in d.message for d in diag))

        # Balanced spell with cost
        balanced_spell = {
            "name": "Flame-Touch",
            "path": "Magic/Spells/Flame-Touch.md",
            "content": "Ignites a candle. Cost: Drains 1 unit of body heat, causing temporary numbness. Source: Ambient spark.",
        }
        diag_bal = self.mgr.run_entity_validation(balanced_spell, context={}, plugin_id="magic_system_audit")
        self.assertEqual(len(diag_bal), 0)

    def test_pacing_heat_map_plugin(self):
        talking_heads = {
            "title": "DialogueHeavy",
            "content": '"Hello there my dear friend, how are you doing on this wonderful morning?" ' * 10,
        }
        ms_data = {"title": "MS", "chapters": [talking_heads]}
        diag = self.mgr.run_manuscript_validation(ms_data, context={}, plugin_id="pacing_heat_map")
        self.assertTrue(any("talking heads" in d.message.lower() for d in diag))


if __name__ == "__main__":
    unittest.main()
