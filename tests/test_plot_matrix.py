#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Multi-Track Plot Grid & Subplot Matrix Engine
(scripts/lib/plot_matrix.py).
Validates:
- PLT-101: Plot and thread tag extraction (@plot:, @thread:, @arc:).
- Pacing gap & dormant thread alerts.
- Dangling subplot identification.
- SVG/HTML multi-lane matrix generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.plot_matrix import (
    extract_chapter_plot_metadata,
    scan_manuscript_plot_matrix,
    generate_plot_html_report
)


class TestPlotMatrixEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_chapter_plot_tags(self):
        ch = self.target_dir / "01_Ch1.md"
        ch.write_text("""# Chapter 1\n@pov: Vance\n@plot: The Heist\n@thread: Romance\n@arc: Vance Redemption\n\nVance climbed the wall.\n""", encoding="utf-8")
        meta = extract_chapter_plot_metadata(ch, 1)
        self.assertEqual(meta["pov"], "Vance")
        self.assertIn("The Heist", meta["plots"])
        self.assertIn("Romance", meta["threads"])
        self.assertIn("Vance Redemption", meta["arcs"])
        self.assertEqual(meta["track_count"], 3)

    def test_extract_comma_separated_tags(self):
        ch = self.target_dir / "02_Ch2.md"
        ch.write_text("""# Chapter 2\n@plot: The Heist, The Betrayal\n@thread: Subplot A, Subplot B\n\nText.\n""", encoding="utf-8")
        meta = extract_chapter_plot_metadata(ch, 2)
        self.assertIn("The Heist", meta["plots"])
        self.assertIn("The Betrayal", meta["plots"])
        self.assertIn("Subplot A", meta["threads"])
        self.assertIn("Subplot B", meta["threads"])
        self.assertEqual(meta["track_count"], 4)

    def test_dormant_and_dangling_thread_detection(self):
        # Create 6 chapters with a dangling thread in Ch 1 only, and a dormant gap in Ch 1 & 6
        (self.target_dir / "01_Ch1.md").write_text("@plot: Main Heist\n@plot: Forgotten Clue\n@plot: Gap Thread\nText.", encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "03_Ch3.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "04_Ch4.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "05_Ch5.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "06_Ch6.md").write_text("@plot: Main Heist\n@plot: Gap Thread\nText.", encoding="utf-8")

        report = scan_manuscript_plot_matrix(self.target_dir, max_gap_threshold=4)
        self.assertEqual(report["total_chapters"], 6)
        self.assertIn("Main Heist", report["tracks"])
        self.assertEqual(report["tracks"]["Main Heist"]["occurrences"], 6)

        # Gap thread has gap of 5 chapters (1 -> 6)
        self.assertGreater(len(report["abandoned_tracks"]), 0)
        abandoned_names = [a["track"] for a in report["abandoned_tracks"]]
        self.assertIn("Gap Thread", abandoned_names)

    def test_plot_matrix_html_generation(self):
        (self.target_dir / "01_Ch1.md").write_text("@plot: Odyssey\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        out_html = self.target_dir / "plot_report.html"
        generate_plot_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Multi-Track Plot Grid", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
