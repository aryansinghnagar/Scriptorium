#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Portfolio Dashboard (scripts/lib/portfolio.py).
Validates:
- OPS-103: Multi-manuscript scanning, wordcount aggregation, editorial stage tracking, and HTML generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.portfolio import (
    analyze_manuscript_project,
    scan_portfolio,
    generate_portfolio_html
)


class TestPortfolioDashboard(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        self.ms1 = self.root_dir / "Manuscript_A"
        self.ms1.mkdir()
        (self.ms1 / "manuscript.yaml").write_text('title: "Book Alpha"\nauthor: "Writer"\ntarget_words: 50000\n', encoding="utf-8")
        (self.ms1 / "01_Act_I").mkdir()
        (self.ms1 / "01_Act_I" / "01_Ch1.md").write_text("# Ch 1\n\nWord " * 500, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_analyze_manuscript_project(self):
        data = analyze_manuscript_project(self.ms1)
        self.assertEqual(data["title"], "Book Alpha")
        self.assertGreater(data["word_count"], 400)
        self.assertGreater(data["progress_pct"], 0.5)

    def test_scan_portfolio_and_html(self):
        report = scan_portfolio(self.root_dir)
        self.assertEqual(report["total_projects"], 1)
        self.assertGreater(report["total_words"], 400)

        out_html = self.root_dir / "portfolio.html"
        generate_portfolio_html(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Author Portfolio & Catalog Dashboard", out_html.read_text(encoding="utf-8"))

    def test_scan_portfolio_direct_manuscript_dir(self):
        # Passing self.ms1 directly should recognize it as 1 project
        report = scan_portfolio(self.ms1)
        self.assertEqual(report["total_projects"], 1)
        self.assertEqual(report["projects"][0]["title"], "Book Alpha")


if __name__ == "__main__":
    unittest.main()
