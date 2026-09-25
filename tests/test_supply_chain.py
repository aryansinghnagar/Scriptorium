#!/usr/bin/env python3
"""
Unit and integration tests for Ars Arcanum Supply Chain Integrity (tests/test_supply_chain.py).
Validates vendor locks, sha256 checksums, and dependency digests.
"""

import hashlib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOCK_FILE = REPO_ROOT / "dependencies.lock"
PLUGINS_DIR = REPO_ROOT / "templates" / "world-bible" / ".obsidian" / "plugins"


class TestSupplyChainIntegrity(unittest.TestCase):
    """Verifies that all third-party and vendored assets match their pinned cryptographic hashes."""

    def test_dependencies_lock_exists(self):
        """Ensure dependencies.lock exists in repository root."""
        self.assertTrue(LOCK_FILE.is_file(), "dependencies.lock must exist at repository root")

    def test_obsidian_plugins_sha256_match_lockfile(self):
        """Verify that all vendored Obsidian plugin main.js files match dependencies.lock digests."""
        self.assertTrue(LOCK_FILE.is_file())
        lines = LOCK_FILE.read_text(encoding="utf-8").splitlines()

        lock_hashes: dict[str, str] = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ".main_js_sha256" in line and "=" in line:
                k, v = line.split("=", 1)
                plugin_name = k.strip().replace(".main_js_sha256", "")
                lock_hashes[plugin_name] = v.strip()

        self.assertGreaterEqual(len(lock_hashes), 10, "Expected at least 10 plugin lock hashes in dependencies.lock")

        for plugin_name, expected_sha in lock_hashes.items():
            main_js_path = PLUGINS_DIR / plugin_name / "main.js"
            self.assertTrue(
                main_js_path.is_file(),
                f"Vendored main.js missing for plugin '{plugin_name}' at {main_js_path}"
            )
            data = main_js_path.read_bytes()
            actual_sha = hashlib.sha256(data).hexdigest()
            self.assertEqual(
                actual_sha,
                expected_sha,
                f"SHA-256 mismatch for Obsidian plugin '{plugin_name}': expected {expected_sha}, got {actual_sha}"
            )


if __name__ == "__main__":
    unittest.main()
