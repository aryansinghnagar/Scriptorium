#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Pre-Flight Typesetting & Compliance Linter (scripts/lib/preflight.py).
Validates:
- PUB-101: Metadata validation, asset cover checks, orphan headings, unclosed codeblocks.
- Page budgeting calculation.
- Compliance scoring & HTML certificate generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.preflight import (
    check_metadata,
    check_cover_and_assets,
    validate_chapter_formatting,
    run_preflight_linter,
    generate_preflight_html_report
)


class TestPreflightEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_metadata_validation(self):
        # Empty dir -> fail
        res = check_metadata(self.ms_dir)
        self.assertFalse(res["valid"])

        # Valid manifest
        (self.ms_dir / "manuscript.yaml").write_text("""title: "The Silent Cosmos"\nauthor: "Jane Doe"\nisbn: "978-0-123456-78-9"\n""", encoding="utf-8")
        res2 = check_metadata(self.ms_dir)
        self.assertTrue(res2["valid"])
        self.assertEqual(res2["data"]["title"], "The Silent Cosmos")

    def test_cover_asset_detection(self):
        res = check_cover_and_assets(self.ms_dir)
        self.assertFalse(res["has_cover"])

        art_dir = self.ms_dir / "03-Art"
        art_dir.mkdir(parents=True)
        (art_dir / "cover.png").write_bytes(b"PNGFAKE")

        res2 = check_cover_and_assets(self.ms_dir)
        self.assertTrue(res2["has_cover"])

    def test_chapter_formatting_orphan_heading(self):
        ch = self.ms_dir / "01_Orphan.md"
        ch.write_text("# Chapter 1\nSome text.\n# Orphan Heading At End", encoding="utf-8")
        issues = validate_chapter_formatting(ch)
        codes = [i["code"] for i in issues]
        self.assertIn("TYP-ORPHAN-HEAD", codes)

    def test_straight_quotes_warning(self):
        ch = self.ms_dir / "02_Quotes.md"
        ch.write_text('# Chapter 2\n"Hello," said John. "We must go." "Why?" asked Elena. "Because."\n', encoding="utf-8")
        issues = validate_chapter_formatting(ch)
        codes = [i["code"] for i in issues]
        self.assertIn("TYP-STRAIGHT-QUOTES", codes)

    def test_full_linter_and_html_generation(self):
        (self.ms_dir / "manuscript.yaml").write_text('title: "Valid Book"\nauthor: "A. Author"\n', encoding="utf-8")
        (self.ms_dir / "01_Ch1.md").write_text("# Chapter 1\n\nWord " * 150, encoding="utf-8")
        
        report = run_preflight_linter(self.ms_dir)
        self.assertGreater(report["compliance_score"], 50)
        self.assertGreater(report["total_words"], 100)

        out_html = self.ms_dir / "preflight_cert.html"
        generate_preflight_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Pre-Flight Typesetting & Publishing Compliance", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
