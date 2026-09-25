#!/usr/bin/env python3
"""
Test Suite: Path Traversal Defense & Volume Sanitization (tests/test_path_traversal_defense.py)
=============================================================================================
Validates:
1. Python validate_volume_name rejection of traversal sequences (../, ..\\, /, \\, empty, special chars).
2. Python sanitize_identifier behavior.
3. Integration with concordance and pacing analyzers.
4. Robustness against command injection payloads and dangerous path characters.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from scripts.lib._bootstrap import validate_volume_name, sanitize_identifier
from scripts.lib.pacing import scan_manuscript_pacing
from scripts.lib.concordance import generate_concordance


class TestPathTraversalDefense(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="arcanum_traversal_test_"))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_volume_names(self):
        valid_cases = [
            "Book-01",
            "Book_02",
            "Volume-3",
            "Prologue",
            "Act-1",
            "all",
            "ALL",
            "all-books",
            "omnibus",
        ]
        for name in valid_cases:
            with self.subTest(name=name):
                result = validate_volume_name(name)
                self.assertEqual(result, name)

    def test_path_traversal_rejections(self):
        invalid_cases = [
            "",
            "..",
            "../",
            "..\\",
            "../../etc/passwd",
            "..\\..\\Windows\\System32",
            "/absolute/path",
            "C:\\Windows\\System32",
            "Book-01/subfolder",
            "Book-01\\subfolder",
            "Book 01",  # whitespace
            "Book;rm -rf /",
            "Book$(whoami)",
            "Book`id`",
            "Book&calc.exe",
            "Book|dir",
        ]
        for name in invalid_cases:
            with self.subTest(name=name), self.assertRaises(ValueError, msg=f"Should reject: {name}"):
                validate_volume_name(name)

    def test_sanitize_identifier(self):
        self.assertEqual(sanitize_identifier("Book 01"), "Book01")
        self.assertEqual(sanitize_identifier("../../Dangerous! Name@#"), "DangerousName")
        self.assertEqual(sanitize_identifier("", fallback="default_vol"), "default_vol")
        self.assertEqual(sanitize_identifier("Valid-Name_123"), "Valid-Name_123")

    def test_pacing_rejects_traversal(self):
        ms_dir = self.temp_dir / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "01_Chapter.md").write_text("# Chapter 1\n\nSome exciting prose.", encoding="utf-8")

        with self.assertRaises(ValueError):
            scan_manuscript_pacing(ms_dir, target_book="../../etc")

    def test_concordance_rejects_traversal(self):
        bible_dir = self.temp_dir / "00-World-Bible"
        char_dir = bible_dir / "Characters"
        char_dir.mkdir(parents=True, exist_ok=True)
        (char_dir / "hero.md").write_text("---\nname: Hero\nrole: Protagonist\n---\nSummary", encoding="utf-8")

        ms_dir = self.temp_dir / "01-Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)

        with self.assertRaises(ValueError):
            generate_concordance(bible_dir=bible_dir, ms_dir=ms_dir, target_book="../evil_path")


if __name__ == "__main__":
    unittest.main()
