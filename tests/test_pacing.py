#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Narrative Pacing, POV Balance & Tension Arc Analytics (scripts/lib/pacing.py).
Covers dialogue-to-exposition density ratios, sentence length variance, POV screen-time balance,
starvation warnings, and tension curve generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.pacing import (
    analyze_chapter_text,
    scan_manuscript_pacing,
    generate_pacing_html_report,
    print_sparkline,
)


class TestPacingEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.book_dir = self.ms_dir / "Book-01" / "01_Act_I"
        self.book_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_analyze_dialogue_heavy_text(self):
        text = """# Chapter 1
@pov: Alice

"Are you sure we should go?" Alice asked.
"We have no choice," Bob whispered. "The shadows are closing in."
"Then take the blade," she said.
"""
        metrics = analyze_chapter_text(text)
        self.assertGreater(metrics["word_count"], 15)
        self.assertGreater(metrics["dialogue_ratio"], 0.4)
        self.assertGreater(metrics["tension_score"], 30.0)

    def test_analyze_exposition_heavy_text(self):
        text = """# Chapter 2
@pov: Historian

The ancient Citadel of Sunspire had stood upon the western crags for seven centuries before the arrival of the High Archons. Its monolithic walls were constructed from calcified white marble that had been quarried from the subterranean depths of Mount Valen.
"""
        metrics = analyze_chapter_text(text)
        self.assertEqual(metrics["dialogue_ratio"], 0.0)
        self.assertGreater(metrics["exposition_ratio"], 0.5)
        self.assertGreater(metrics["mean_sentence_length"], 15.0)

    def test_pov_starvation_detection(self):
        # Create 5 chapters where Elena is POV in Ch1, then absent for Ch 2, 3, 4, 5
        (self.book_dir / "01_Ch1.md").write_text("""# Ch 1\n@pov: Elena\nElena took her seat at the high table and reviewed the ledger.""", encoding="utf-8")
        (self.book_dir / "02_Ch2.md").write_text("""# Ch 2\n@pov: Kaelen\nKaelen drew his blade in the dark alleyway.""", encoding="utf-8")
        (self.book_dir / "03_Ch3.md").write_text("""# Ch 3\n@pov: Kaelen\nKaelen marched through the pouring rain.""", encoding="utf-8")
        (self.book_dir / "04_Ch4.md").write_text("""# Ch 4\n@pov: Kaelen\nKaelen stormed the citadel gates.""", encoding="utf-8")
        (self.book_dir / "05_Ch5.md").write_text("""# Ch 5\n@pov: Kaelen\nKaelen faced the shadow commander.""", encoding="utf-8")

        report = scan_manuscript_pacing(self.ms_dir)
        self.assertEqual(report["total_chapters"], 5)
        self.assertIn("Elena", report["pov_distribution"])
        self.assertIn("Kaelen", report["pov_distribution"])
        self.assertTrue(report["pov_distribution"]["Elena"]["starvation_warning"])

    def test_tension_sparkline(self):
        values = [20.0, 35.0, 50.0, 75.0, 95.0]
        spark = print_sparkline(values)
        self.assertEqual(len(spark), 5)

    def test_html_report_generation(self):
        (self.book_dir / "01_Ch1.md").write_text("""# Ch 1\n@pov: Aric\nAric drew his sword and struck the monster.""", encoding="utf-8")
        report = scan_manuscript_pacing(self.ms_dir)
        out_html = self.ms_dir / "pacing_report.html"
        generate_pacing_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Narrative Pacing, POV Balance & Tension Arc", content)
        self.assertIn("<svg", content)


if __name__ == "__main__":
    unittest.main()
