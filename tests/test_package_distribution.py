#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Multi-Platform Packager (scripts/package_distribution.py).
Validates:
- OPS-101: Reader edition, submission bundle, and ARC zip archive generation.
- SHA-256 manifest calculation.
"""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from package_distribution import (
    compute_file_sha256,
    package_arc_bundle,
    package_codex_bundle,
    package_reader_edition,
    package_submission_bundle,
)


class TestPackageDistribution(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Novel"
        self.ms_dir.mkdir(parents=True)
        (self.ms_dir / "Exports").mkdir()
        (self.ms_dir / "Exports" / "Novel.pdf").write_bytes(b"%PDF-1.4 test")
        (self.ms_dir / "Exports" / "Novel.epub").write_bytes(b"EPUB test")
        (self.ms_dir / "Submissions").mkdir()
        (self.ms_dir / "Submissions" / "Query.md").write_text("# Query", encoding="utf-8")
        (self.ms_dir / "Codex").mkdir()
        (self.ms_dir / "Codex" / "index.html").write_text("<html>Codex</html>", encoding="utf-8")
        (self.ms_dir / "Maps").mkdir()
        (self.ms_dir / "Maps" / "WorldMap.svg").write_text("<svg>Map</svg>", encoding="utf-8")
        self.out_dir = Path(self.temp_dir.name) / "Dist"
        self.out_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_package_reader_edition(self):
        pkg = package_reader_edition(self.ms_dir, self.out_dir)
        self.assertTrue(Path(pkg["archive_path"]).is_file())
        self.assertGreater(len(pkg["sha256"]), 20)

        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertIn("Ebooks/Novel.pdf", names)
            self.assertIn("Ebooks/Novel.epub", names)
            self.assertIn("README.txt", names)

    def test_package_submission_bundle(self):
        pkg = package_submission_bundle(self.ms_dir, self.out_dir)
        self.assertTrue(Path(pkg["archive_path"]).is_file())

        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertIn("Submission_Documents/Query.md", names)

    def test_package_arc_bundle(self):
        pkg = package_arc_bundle(self.ms_dir, self.out_dir, reviewer="Beta Reader")
        self.assertTrue(Path(pkg["archive_path"]).is_file())

        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertIn("ARC_LICENSE_NOTICE.txt", names)

    def test_package_codex_bundle(self):
        pkg = package_codex_bundle(self.ms_dir, self.out_dir)
        self.assertTrue(Path(pkg["archive_path"]).is_file())
        self.assertEqual(pkg["package_type"], "codex")

        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertIn("CODEX_INFO.txt", names)
            self.assertIn("Static_Codex/index.html", names)
            self.assertIn("Maps/WorldMap.svg", names)

    def test_cli_package_distribution(self):
        script_path = REPO_ROOT / "scripts" / "package_distribution.py"
        res = subprocess.run(
            [sys.executable, str(script_path), str(self.ms_dir), "-o", str(self.out_dir), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0)
        manifest = json.loads(res.stdout)
        self.assertEqual(manifest["manuscript"], "Novel")
        self.assertGreaterEqual(len(manifest["packages"]), 3)
        self.assertTrue((self.out_dir / "RELEASE_MANIFEST.json").is_file())

    def test_compute_file_sha256_accuracy(self):
        """Verifies compute_file_sha256 matches exact hashlib hash."""
        sample_file = self.out_dir / "sample.bin"
        sample_file.write_bytes(b"Sovereign Authoring Operating System")
        expected = hashlib.sha256(b"Sovereign Authoring Operating System").hexdigest()
        self.assertEqual(compute_file_sha256(sample_file), expected)

    def test_package_reader_edition_art_and_ebooks(self):
        """Verifies inclusion of cover art and HTML readers in Reader Edition."""
        art_dir = self.ms_dir / "03-Art"
        art_dir.mkdir(exist_ok=True)
        (art_dir / "Cover.png").write_bytes(b"\x89PNG test")
        (self.ms_dir / "Exports" / "Novel.html").write_text("<html>Reader</html>", encoding="utf-8")

        pkg = package_reader_edition(self.ms_dir, self.out_dir)
        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertIn("Art/Cover.png", names)
            self.assertIn("Ebooks/Novel.html", names)

    def test_package_arc_bundle_reviewer_watermark(self):
        """Verifies reviewer watermark is baked into ARC notice and archive filename."""
        reviewer_name = "Lady Mirella"
        pkg = package_arc_bundle(self.ms_dir, self.out_dir, reviewer=reviewer_name)
        self.assertIn("Lady_Mirella", pkg["filename"])
        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            notice = z.read("ARC_LICENSE_NOTICE.txt").decode("utf-8")
            self.assertIn("Lady Mirella", notice)
            self.assertIn("ADVANCE READING COPY", notice)

    def test_package_codex_bundle_with_nested_maps(self):
        """Verifies nested maps and css assets are properly structured in Codex bundle."""
        nested_map = self.ms_dir / "Maps" / "Regions" / "North.svg"
        nested_map.parent.mkdir(parents=True, exist_ok=True)
        nested_map.write_text("<svg>North</svg>", encoding="utf-8")

        pkg = package_codex_bundle(self.ms_dir, self.out_dir)
        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertTrue(any("North.svg" in n for n in names))

    def test_package_submission_bundle_with_docx(self):
        """Verifies .docx manuscripts in Exports are placed into Manuscripts/ folder."""
        (self.ms_dir / "Exports" / "Standard_Manuscript.docx").write_bytes(b"PK DOCX")
        pkg = package_submission_bundle(self.ms_dir, self.out_dir)
        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            names = z.namelist()
            self.assertIn("Manuscripts/Standard_Manuscript.docx", names)

    def test_empty_manuscript_packaging(self):
        """Verifies packaging an empty manuscript directory produces valid archives without errors."""
        empty_ms = Path(self.temp_dir.name) / "Empty_Project"
        empty_ms.mkdir()
        pkg = package_reader_edition(empty_ms, self.out_dir)
        self.assertTrue(Path(pkg["archive_path"]).is_file())
        with zipfile.ZipFile(pkg["archive_path"], "r") as z:
            self.assertIn("README.txt", z.namelist())

    def test_cli_specific_type_filter(self):
        """Verifies CLI execution with -t arc flag only creates the ARC package."""
        script_path = REPO_ROOT / "scripts" / "package_distribution.py"
        res = subprocess.run(
            [sys.executable, str(script_path), str(self.ms_dir), "-t", "arc", "--reviewer", "Grand Scribe", "-o", str(self.out_dir), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0)
        manifest = json.loads(res.stdout)
        self.assertEqual(len(manifest["packages"]), 1)
        self.assertEqual(manifest["packages"][0]["package_type"], "arc")
        self.assertEqual(manifest["packages"][0]["reviewer"], "Grand Scribe")


if __name__ == "__main__":
    unittest.main()
