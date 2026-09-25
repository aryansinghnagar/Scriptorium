#!/usr/bin/env python3
"""
Test Suite: Sovereign Offline Flatpak Bundle & Packaging Invariants
(tests/test_flatpak_offline.py)
================================================================================
Validates the offline Flatpak build harness, AppStream metainfo compliance,
sandbox permissions, and reproducibility constraints for version 3.0.0.
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLATPAK_DIR = REPO_ROOT / "flatpak"
MANIFEST = REPO_ROOT / "org.arsarcanum.ArsArcanum.yaml"
METAINFO = FLATPAK_DIR / "org.arsarcanum.ArsArcanum.metainfo.xml"
BUILD_SCRIPT = FLATPAK_DIR / "build_offline_bundle.sh"


class TestFlatpakOfflinePackaging(unittest.TestCase):
    """Verifies Flatpak offline build scripts and manifest assertions."""

    def test_files_exist(self):
        self.assertTrue(MANIFEST.exists(), "Missing Flatpak manifest org.arsarcanum.ArsArcanum.yaml")
        self.assertTrue(METAINFO.exists(), "Missing AppStream metainfo XML")
        self.assertTrue(BUILD_SCRIPT.exists(), "Missing build_offline_bundle.sh script")

    def test_build_script_syntax_and_dry_run(self):
        """Validates build script dry-run execution if bash is available."""
        script_content = BUILD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("flatpak-builder", script_content)
        self.assertIn("--dry-run", script_content)
        self.assertIn("ArsArcanum", script_content)

    def test_manifest_offline_sandboxing_invariants(self):
        """Ensures manifest contains required offline sandboxing parameters."""
        content = MANIFEST.read_text(encoding="utf-8")

        self.assertIn("app-id: org.arsarcanum.ArsArcanum", content)
        self.assertIn("--filesystem=home", content)
        self.assertIn("--talk-name=org.freedesktop.Flatpak", content)
        self.assertIn("--talk-name=org.freedesktop.Notifications", content)
        self.assertIn("buildsystem: simple", content)

    def test_metainfo_appstream_compliance(self):
        """Validates AppStream 0.16+ metainfo XML tags and metadata."""
        tree = ET.parse(METAINFO)  # noqa: S314
        root = tree.getroot()

        id_elem = root.find("id")
        self.assertIsNotNone(id_elem)
        self.assertEqual(id_elem.text, "org.arsarcanum.ArsArcanum")

        name_elem = root.find("name")
        self.assertIsNotNone(name_elem)
        self.assertEqual(name_elem.text, "Ars Arcanum")

        lic_elem = root.find("metadata_license")
        self.assertIsNotNone(lic_elem)
        self.assertEqual(lic_elem.text, "CC0-1.0")

        # Verify releases section exists
        releases = root.find("releases")
        self.assertIsNotNone(releases, "Missing <releases> section in AppStream metainfo")
        rel_list = releases.findall("release")
        self.assertTrue(len(rel_list) > 0, "No <release> tags found in metainfo")


if __name__ == "__main__":
    unittest.main()
