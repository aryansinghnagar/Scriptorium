#!/usr/bin/env python3
"""
Test Suite: Flatpak Packaging Manifest & AppStream Compliance
(tests/test_flatpak_manifest.py)
================================================================================
Validates Flatpak manifest syntax, sandbox permissions, and launcher mappings.
"""

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestFlatpakManifest(unittest.TestCase):
    def setUp(self):
        self.manifest_path = PROJECT_ROOT / "org.arsarcanum.ArsArcanum.yaml"

    def test_manifest_exists(self):
        self.assertTrue(self.manifest_path.is_file(), "Flatpak manifest org.arsarcanum.ArsArcanum.yaml must exist.")

    def test_manifest_structure_and_app_id(self):
        content = self.manifest_path.read_text(encoding="utf-8")
        self.assertIn("app-id: org.arsarcanum.ArsArcanum", content)
        self.assertIn("runtime: org.gnome.Platform", content)
        self.assertIn("sdk: org.gnome.Sdk", content)
        self.assertIn("command: arcanum", content)

    def test_finish_args_sandbox_permissions(self):
        content = self.manifest_path.read_text(encoding="utf-8")
        # Sockets
        self.assertIn("--socket=wayland", content)
        self.assertIn("--socket=fallback-x11", content)
        self.assertIn("--share=ipc", content)
        # Filesystems
        self.assertIn("--filesystem=home", content)
        # DBus permissions
        self.assertIn("--talk-name=org.freedesktop.Notifications", content)
        self.assertIn("--talk-name=org.freedesktop.Flatpak", content)
        # Verify no actual finish-args entries use deprecated tilde grants
        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("- --filesystem="):
                self.assertNotIn("~/", line_str, "Deprecated tilde path grant in finish-args")

    def test_build_commands_and_reproducibility(self):
        content = self.manifest_path.read_text(encoding="utf-8")
        # Strips pycache bytecode
        self.assertIn("__pycache__", content)
        # Executable permissions
        self.assertIn("chmod +x", content)
        # Project root substitution assertion
        self.assertIn("__PROJECT_ROOT__", content)
        self.assertIn("/app/bin/arcanum", content)


if __name__ == "__main__":
    unittest.main()
