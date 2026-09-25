#!/usr/bin/env python3
"""
Test Suite: Flathub Upstream AppStream Metainfo Specification & Packaging
(tests/test_flathub_upstream.py)
================================================================================
Validates Freedesktop AppStream 0.16+ XML metainfo specifications, licenses,
OARS content ratings, launchables, and Flatpak build recipe integration.
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestFlathubUpstream(unittest.TestCase):
    def setUp(self):
        self.metainfo_path = PROJECT_ROOT / "flatpak" / "org.arsarcanum.ArsArcanum.metainfo.xml"
        self.flatpak_manifest = PROJECT_ROOT / "org.arsarcanum.ArsArcanum.yaml"
        self.desktop_file = PROJECT_ROOT / "launchers" / "arcanum-control-center.desktop"

    def test_metainfo_file_exists(self):
        self.assertTrue(self.metainfo_path.exists(), f"Missing AppStream metainfo file: {self.metainfo_path}")

    def test_metainfo_xml_structure_and_tags(self):
        tree = ET.parse(self.metainfo_path)  # noqa: S314
        root = tree.getroot()
        self.assertIn(root.tag, ("component", "component type=\"desktop\"", "component type=\"desktop-application\""))

        # Required AppStream tags
        id_elem = root.find("id")
        self.assertIsNotNone(id_elem, "Missing <id> tag in metainfo")
        self.assertEqual(id_elem.text, "org.arsarcanum.ArsArcanum")

        metadata_lic = root.find("metadata_license")
        self.assertIsNotNone(metadata_lic, "Missing <metadata_license> tag")
        self.assertEqual(metadata_lic.text, "CC0-1.0")

        project_lic = root.find("project_license")
        self.assertIsNotNone(project_lic, "Missing <project_license> tag")
        self.assertIn("GPL", project_lic.text)

        name_elem = root.find("name")
        self.assertIsNotNone(name_elem, "Missing <name> tag")
        self.assertIn("Ars Arcanum", name_elem.text)

        summary_elem = root.find("summary")
        self.assertIsNotNone(summary_elem, "Missing <summary> tag")

        desc_elem = root.find("description")
        self.assertIsNotNone(desc_elem, "Missing <description> tag")

        # Launchable
        launch_elem = root.find("launchable")
        self.assertIsNotNone(launch_elem, "Missing <launchable> tag")
        self.assertEqual(launch_elem.get("type"), "desktop-id")
        self.assertEqual(launch_elem.text, "arcanum-control-center.desktop")

        # Screenshots
        screenshots_elem = root.find("screenshots")
        self.assertIsNotNone(screenshots_elem, "Missing <screenshots> tag")
        screenshots = screenshots_elem.findall("screenshot")
        self.assertGreaterEqual(len(screenshots), 1)

        # Content Rating (OARS 1.1)
        oars_elem = root.find("content_rating")
        self.assertIsNotNone(oars_elem, "Missing <content_rating> tag")
        self.assertEqual(oars_elem.get("type"), "oars-1.1")

        # Releases
        releases_elem = root.find("releases")
        self.assertIsNotNone(releases_elem, "Missing <releases> tag")
        releases = releases_elem.findall("release")
        self.assertGreaterEqual(len(releases), 1)
        v190 = [r for r in releases if r.get("version") == "1.9.0"]
        self.assertTrue(len(v190) > 0, "Missing 1.9.0 release in AppStream XML")

    def test_flatpak_manifest_installs_metainfo(self):
        self.assertTrue(self.flatpak_manifest.exists(), "Missing Flatpak manifest")
        manifest_content = self.flatpak_manifest.read_text(encoding="utf-8")
        self.assertIn(
            "cp flatpak/org.arsarcanum.ArsArcanum.metainfo.xml /app/share/metainfo/",
            manifest_content,
            "Flatpak manifest does not copy metainfo.xml into /app/share/metainfo/",
        )

    def test_desktop_file_matches_launchable(self):
        self.assertTrue(self.desktop_file.exists(), "Missing desktop entry file")
        desktop_text = self.desktop_file.read_text(encoding="utf-8")
        self.assertIn("Name=Ars Arcanum Control Center", desktop_text)
        self.assertIn("Categories=Office;WordProcessor;Publishing;", desktop_text)


if __name__ == "__main__":
    unittest.main()
