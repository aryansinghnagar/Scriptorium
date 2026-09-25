#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Speculative Plugin Marketplace
(tests/test_plugin_market.py)
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.plugin_market import (
    get_marketplace_plugin,
    install_marketplace_plugin,
    list_marketplace_plugins,
    load_marketplace_catalog,
    main as market_main,
    uninstall_marketplace_plugin,
    verify_catalog_integrity,
)
from scripts.lib.plugins import PluginManager


class TestPluginMarketplace(unittest.TestCase):
    """Validates catalog discovery, schema verification, installation, and lifecycle."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create custom test catalog
        self.catalog_file = self.root / "test_catalog.json"
        self.catalog_data = {
            "version": "1.0.0",
            "catalog_name": "Test Speculative Marketplace",
            "plugins": [
                {
                    "id": "pantheon_audit",
                    "name": "Pantheon Audit Plugin",
                    "version": "1.2.0",
                    "author": "Lore Guild",
                    "category": "lore",
                    "description": "Audits pantheon domains and divine portfolios.",
                    "min_arcanum_version": "1.6.0",
                    "hooks": ["validate_entity"],
                    "tags": ["deities", "pantheon"],
                    "files": {
                        "plugin.json": json.dumps({
                            "id": "pantheon_audit",
                            "name": "Pantheon Audit Plugin",
                            "version": "1.2.0",
                            "author": "Lore Guild",
                            "description": "Audits pantheon domains.",
                            "category": "lore",
                            "entry_point": "plugin.py",
                            "hooks": ["validate_entity"],
                            "min_arcanum_version": "1.6.0"
                        }),
                        "plugin.py": (
                            "def hook_validate_entity(entity_data, context):\n"
                            "    return [{'severity': 'info', 'message': 'Pantheon check pass', 'target': 'God'}]\n"
                        )
                    }
                },
                {
                    "id": "trope_subverter",
                    "name": "Trope Subverter",
                    "version": "1.0.0",
                    "author": "Craft Council",
                    "category": "craft",
                    "description": "Scans for cliché fantasy tropes.",
                    "min_arcanum_version": "1.6.0",
                    "hooks": ["custom_metric"],
                    "tags": ["craft", "tropes"],
                    "files": {
                        "plugin.json": json.dumps({
                            "id": "trope_subverter",
                            "name": "Trope Subverter",
                            "version": "1.0.0",
                            "author": "Craft Council",
                            "description": "Scans for clichés.",
                            "category": "craft",
                            "entry_point": "plugin.py",
                            "hooks": ["custom_metric"],
                            "min_arcanum_version": "1.6.0"
                        }),
                        "plugin.py": (
                            "def hook_custom_metric(text, context):\n"
                            "    return {'cliche_score': 42}\n"
                        )
                    }
                }
            ]
        }
        self.catalog_file.write_text(json.dumps(self.catalog_data), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_official_workspace_catalog(self) -> None:
        """Verifies loading the main repository plugin catalog."""
        catalog = load_marketplace_catalog()
        self.assertIn("plugins", catalog)
        self.assertGreaterEqual(len(catalog["plugins"]), 3)

        # Check official catalog integrity
        is_valid, issues = verify_catalog_integrity()
        self.assertTrue(is_valid, f"Catalog integrity issues: {issues}")
        self.assertEqual(len(issues), 0)

    def test_list_and_filter_plugins(self) -> None:
        """Verifies filtering plugins by category and search queries."""
        # All plugins
        all_p = list_marketplace_plugins(catalog_path=self.catalog_file)
        self.assertEqual(len(all_p), 2)

        # Category filter
        lore_p = list_marketplace_plugins(category="lore", catalog_path=self.catalog_file)
        self.assertEqual(len(lore_p), 1)
        self.assertEqual(lore_p[0]["id"], "pantheon_audit")

        # Query filter on tags
        craft_p = list_marketplace_plugins(query="tropes", catalog_path=self.catalog_file)
        self.assertEqual(len(craft_p), 1)
        self.assertEqual(craft_p[0]["id"], "trope_subverter")

    def test_get_plugin_info(self) -> None:
        """Verifies retrieval of single plugin metadata."""
        p = get_marketplace_plugin("pantheon_audit", catalog_path=self.catalog_file)
        self.assertIsNotNone(p)
        self.assertEqual(p["name"], "Pantheon Audit Plugin")
        self.assertEqual(p["author"], "Lore Guild")

        missing = get_marketplace_plugin("nonexistent_plugin", catalog_path=self.catalog_file)
        self.assertIsNone(missing)

    def test_install_and_uninstall_lifecycle(self) -> None:
        """Verifies full installation, PluginManager discovery, and uninstallation."""
        target_dir = self.root / "installed_plugins" / "pantheon_audit"

        # 1. Install
        success, msg = install_marketplace_plugin(
            "pantheon_audit",
            target_dir=target_dir,
            catalog_path=self.catalog_file,
        )
        self.assertTrue(success, msg)
        self.assertTrue(target_dir.is_dir())
        self.assertTrue((target_dir / "plugin.json").is_file())
        self.assertTrue((target_dir / "plugin.py").is_file())

        # 2. Discover with PluginManager
        mgr = PluginManager(search_paths=[target_dir.parent])
        mgr.discover_plugins()
        installed_plugin = mgr.get_plugin("pantheon_audit")
        self.assertIsNotNone(installed_plugin)
        self.assertEqual(installed_plugin.name, "Pantheon Audit Plugin")

        # 3. Prevent overwrite without --force
        success_dup, msg_dup = install_marketplace_plugin(
            "pantheon_audit",
            target_dir=target_dir,
            catalog_path=self.catalog_file,
            force=False,
        )
        self.assertFalse(success_dup)
        self.assertIn("already exists", msg_dup)

        # 4. Overwrite with --force
        success_force, _ = install_marketplace_plugin(
            "pantheon_audit",
            target_dir=target_dir,
            catalog_path=self.catalog_file,
            force=True,
        )
        self.assertTrue(success_force)

        # 5. Uninstall
        uninst_success, uninst_msg = uninstall_marketplace_plugin("pantheon_audit", target_dir=target_dir)
        self.assertTrue(uninst_success, uninst_msg)
        self.assertFalse(target_dir.exists())

    def test_cli_interface(self) -> None:
        """Verifies CLI dispatching of marketplace subcommands."""
        # list
        code_list = market_main(["list", "--catalog", str(self.catalog_file)])
        self.assertEqual(code_list, 0)

        # info
        code_info = market_main(["info", "pantheon_audit", "--catalog", str(self.catalog_file)])
        self.assertEqual(code_info, 0)

        # verify
        code_verify = market_main(["verify", "--catalog", str(self.catalog_file)])
        self.assertEqual(code_verify, 0)


if __name__ == "__main__":
    unittest.main()
