#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Story Paradigm & Structure Enforcer (scripts/lib/structure.py).
Validates:
- PLT-102: Multi-paradigm structural alignment (Three-Act, Save the Cat, Hero's Journey, Story Circle).
- Chapter wordcount accumulation and percentage milestone mapping.
- Structural harmony score and drift penalties.
- HTML report generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.structure import (
    scan_manuscript_structure,
    generate_structure_html_report,
    PARADIGMS
)


class TestStructureEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_paradigms_available(self):
        self.assertIn("three_act", PARADIGMS)
        self.assertIn("save_the_cat", PARADIGMS)
        self.assertIn("heros_journey", PARADIGMS)
        self.assertIn("story_circle", PARADIGMS)
        self.assertIn("seven_point", PARADIGMS)

    def test_structure_scan_and_beat_mapping(self):
        # Create 8 balanced chapters (each ~250 words)
        words_chunk = "Word " * 250
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Chapter_{i}.md").write_text(f"# Chapter {i}\n\n{words_chunk}\n", encoding="utf-8")

        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        self.assertEqual(report["total_chapters"], 8)
        self.assertGreater(report["total_words"], 1900)
        self.assertGreater(report["harmony_score"], 60.0)

        # Check beat mappings
        beat_names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Inciting Incident", beat_names)
        self.assertIn("Midpoint", beat_names)
        self.assertIn("Climax", beat_names)

    def test_structure_html_generation(self):
        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\nWord " * 100, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="save_the_cat")
        out_html = self.target_dir / "structure_report.html"
        generate_structure_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Story Paradigm & Structure Alignment", out_html.read_text(encoding="utf-8"))

    def test_containing_chapter_assignment(self):
        # Chapter 1 is 100 words, Chapter 2 is 900 words
        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("# Ch 2\n\n" + "word " * 900, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        # Opening Status Quo (5%) should be mapped to Chapter 1
        opening_beat = next(b for b in report["beats"] if b["beat_name"] == "Opening Status Quo")
        self.assertEqual(opening_beat["assigned_chapter"], 1)
        self.assertTrue(opening_beat["is_in_window"])


if __name__ == "__main__":
    unittest.main()
