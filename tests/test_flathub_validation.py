#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Flathub Upstream Submission Validator (flatpak/flathub_submission_validate.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "flatpak"))

from flathub_submission_validate import (
    validate_appstream_metainfo,
    validate_flatpak_manifest,
    validate_flathub_submission,
)


class TestFlathubValidation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_canonical_repo_metainfo_is_valid(self):
        """Repository canonical AppStream metainfo XML passes without fatal errors."""
        canonical_meta = REPO_ROOT / "flatpak" / "org.arsarcanum.ArsArcanum.metainfo.xml"
        findings = validate_appstream_metainfo(canonical_meta)
        errors = [f for f in findings if f.severity == "ERROR"]
        self.assertEqual(len(errors), 0, f"Unexpected errors in canonical metainfo: {errors}")

    def test_canonical_repo_manifest_is_valid(self):
        """Repository canonical Flatpak YAML manifest passes without fatal errors."""
        canonical_manifest = REPO_ROOT / "org.arsarcanum.ArsArcanum.yaml"
        findings = validate_flatpak_manifest(canonical_manifest)
        errors = [f for f in findings if f.severity == "ERROR"]
        self.assertEqual(len(errors), 0, f"Unexpected errors in canonical manifest: {errors}")

    def test_missing_metainfo_file(self):
        """Missing metainfo file produces FLT-101 error."""
        findings = validate_appstream_metainfo(self.root / "missing.xml")
        ids = [f.id for f in findings]
        self.assertIn("FLT-101", ids)

    def test_invalid_xml_syntax(self):
        """Corrupted XML syntax produces FLT-102 error."""
        meta_file = self.root / "bad.xml"
        meta_file.write_text("<component><unclosed>", encoding="utf-8")
        findings = validate_appstream_metainfo(meta_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-102", ids)

    def test_missing_id_tag(self):
        """Metainfo without <id> tag produces FLT-104."""
        meta_file = self.root / "meta.xml"
        meta_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <name>Test</name>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-3.0</project_license>
  <summary>Summary text</summary>
  <description><p>Desc</p></description>
  <screenshots><screenshot><image>https://example.com/shot.png</image></screenshot></screenshots>
  <content_rating type="oars-1.1"/>
  <releases><release version="1.0.0" date="2026-01-01"/></releases>
  <url type="homepage">https://example.com</url>
</component>""", encoding="utf-8")
        findings = validate_appstream_metainfo(meta_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-104", ids)

    def test_missing_metadata_license(self):
        """Metainfo without <metadata_license> tag produces FLT-105."""
        meta_file = self.root / "meta.xml"
        meta_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>org.arsarcanum.ArsArcanum</id>
  <name>Test</name>
  <project_license>GPL-3.0</project_license>
  <summary>Summary text</summary>
  <description><p>Desc</p></description>
  <screenshots><screenshot><image>https://example.com/shot.png</image></screenshot></screenshots>
  <content_rating type="oars-1.1"/>
  <releases><release version="1.0.0" date="2026-01-01"/></releases>
  <url type="homepage">https://example.com</url>
</component>""", encoding="utf-8")
        findings = validate_appstream_metainfo(meta_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-105", ids)

    def test_insecure_http_screenshot_url(self):
        """Screenshot with HTTP rather than HTTPS URL produces FLT-111 error."""
        meta_file = self.root / "meta.xml"
        meta_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>org.arsarcanum.ArsArcanum</id>
  <name>Test</name>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-3.0</project_license>
  <summary>Summary text</summary>
  <description><p>Desc</p></description>
  <screenshots><screenshot><image>http://insecure.example.com/shot.png</image></screenshot></screenshots>
  <content_rating type="oars-1.1"/>
  <releases><release version="1.0.0" date="2026-01-01"/></releases>
  <url type="homepage">https://example.com</url>
</component>""", encoding="utf-8")
        findings = validate_appstream_metainfo(meta_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-111", ids)

    def test_missing_manifest_file(self):
        """Missing manifest file produces FLT-201 error."""
        findings = validate_flatpak_manifest(self.root / "missing.yaml")
        ids = [f.id for f in findings]
        self.assertIn("FLT-201", ids)

    def test_missing_filesystem_home_grant(self):
        """Manifest without --filesystem=home produces FLT-205 error."""
        man_file = self.root / "app.yaml"
        man_file.write_text("""app-id: org.arsarcanum.ArsArcanum
runtime: org.gnome.Platform
sdk: org.gnome.Sdk
finish-args:
  - --socket=wayland
""", encoding="utf-8")
        findings = validate_flatpak_manifest(man_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-205", ids)

    def test_deprecated_tilde_in_manifest(self):
        """Deprecated tilde filesystem grant produces FLT-206 error."""
        man_file = self.root / "app.yaml"
        man_file.write_text("""app-id: org.arsarcanum.ArsArcanum
runtime: org.gnome.Platform
finish-args:
  - --filesystem=home
  - --filesystem=~/Universes
""", encoding="utf-8")
        findings = validate_flatpak_manifest(man_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-206", ids)

    def test_full_flathub_submission_report(self):
        """validate_flathub_submission returns complete ValidationReport object."""
        report = validate_flathub_submission(REPO_ROOT)
        self.assertTrue(report.is_compliant)
        self.assertEqual(report.error_count, 0)
        report_dict = report.to_dict()
        self.assertIn("is_compliant", report_dict)
        self.assertIn("findings", report_dict)

    def test_missing_content_rating(self):
        """Metainfo without content_rating tag produces FLT-112 error."""
        meta_file = self.root / "meta.xml"
        meta_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>org.arsarcanum.ArsArcanum</id>
  <name>Test</name>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-3.0</project_license>
  <summary>Summary text</summary>
  <description><p>Desc</p></description>
  <screenshots><screenshot><image>https://example.com/shot.png</image></screenshot></screenshots>
  <releases><release version="1.0.0" date="2026-01-01"/></releases>
  <url type="homepage">https://example.com</url>
</component>""", encoding="utf-8")
        findings = validate_appstream_metainfo(meta_file)
        ids = [f.id for f in findings]
        self.assertIn("FLT-112", ids)


if __name__ == "__main__":
    unittest.main()
