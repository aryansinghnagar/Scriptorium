#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Multi-Platform Packager (scripts/package_distribution.py).
Validates:
- OPS-101: Reader edition, submission bundle, and ARC zip archive generation.
- SHA-256 manifest calculation.
"""

import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from package_distribution import (
    package_reader_edition,
    package_submission_bundle,
    package_arc_bundle
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


if __name__ == "__main__":
    unittest.main()
