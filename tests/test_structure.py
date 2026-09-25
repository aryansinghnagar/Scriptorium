#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Story Paradigm & Structure Enforcer (scripts/lib/structure.py).
Validates:
- PLT-102: Multi-paradigm structural alignment across all 9 canonical models.
- Chapter wordcount accumulation and percentage milestone mapping.
- Structural harmony score and drift penalties.
- HTML report generation with Content Security Policy.
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
    PARADIGMS,
)


class TestStructureEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_paradigms_available(self):
        expected = [
            "three_act", "save_the_cat", "heros_journey", "story_circle",
            "seven_point", "eight_sequence", "fichtean_curve", "kishotenketsu",
            "freytags_pyramid"
        ]
        for p in expected:
            self.assertIn(p, PARADIGMS)
            self.assertGreater(len(PARADIGMS[p]["beats"]), 3)

    def test_structure_scan_and_beat_mapping_three_act(self):
        # Create 8 balanced chapters (each ~250 words)
        words_chunk = "Word " * 250
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Chapter_{i}.md").write_text(f"# Chapter {i}\n\n{words_chunk}\n", encoding="utf-8")

        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        self.assertEqual(report["total_chapters"], 8)
        self.assertGreater(report["total_words"], 1900)
        self.assertGreater(report["harmony_score"], 60.0)

        beat_names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Inciting Incident", beat_names)
        self.assertIn("Midpoint", beat_names)
        self.assertIn("Climax", beat_names)

    def test_structure_scan_save_the_cat_15_beats(self):
        for i in range(1, 16):
            (self.target_dir / f"0{i:02d}_Ch.md").write_text(f"# Chapter {i}\n\n" + "word " * 100, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="save_the_cat")
        self.assertEqual(len(report["beats"]), 15)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Opening Image", names)
        self.assertIn("All Hope Is Lost", names)
        self.assertIn("Final Image", names)

    def test_structure_scan_heros_journey_12_stages(self):
        for i in range(1, 13):
            (self.target_dir / f"0{i:02d}_Ch.md").write_text(f"# Chapter {i}\n\n" + "hero " * 150, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="heros_journey")
        self.assertEqual(len(report["beats"]), 12)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. Ordinary World", names)
        self.assertIn("8. The Ordeal", names)
        self.assertIn("12. Return with Elixir", names)

    def test_structure_scan_story_circle_8_steps(self):
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "step " * 200, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="story_circle")
        self.assertEqual(len(report["beats"]), 8)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. You (Comfort Zone)", names)
        self.assertIn("5. Find (Getting What They Wanted)", names)

    def test_structure_scan_seven_point(self):
        for i in range(1, 8):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "plot " * 150, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="seven_point")
        self.assertEqual(len(report["beats"]), 7)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. Hook", names)
        self.assertIn("4. Midpoint", names)
        self.assertIn("7. Resolution", names)

    def test_structure_scan_eight_sequence(self):
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "seq " * 200, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="eight_sequence")
        self.assertEqual(len(report["beats"]), 8)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Sequence A: Status Quo & Inciting Incident", names)
        self.assertIn("Sequence D: Midpoint Crisis & Shift of Intent", names)

    def test_structure_scan_fichtean_curve(self):
        for i in range(1, 8):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "crisis " * 180, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="fichtean_curve")
        self.assertEqual(len(report["beats"]), 7)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("2. Crisis 1 (First Complication)", names)
        self.assertIn("6. Climax (Supreme Confrontation)", names)

    def test_structure_scan_kishotenketsu(self):
        for i in range(1, 5):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "story " * 250, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="kishotenketsu")
        self.assertEqual(len(report["beats"]), 4)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. 起 Ki (Introduction)", names)
        self.assertIn("3. 転 Ten (The Twist / Turn)", names)

    def test_structure_scan_freytags_pyramid(self):
        for i in range(1, 8):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "dramatic " * 150, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="freytags_pyramid")
        self.assertEqual(len(report["beats"]), 7)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. Exposition", names)
        self.assertIn("4. Climax / Turning Point", names)

    def test_containing_chapter_assignment(self):
        # Chapter 1 is 100 words, Chapter 2 is 900 words
        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("# Ch 2\n\n" + "word " * 900, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        opening_beat = next(b for b in report["beats"] if b["beat_name"] == "Opening Status Quo")
        self.assertEqual(opening_beat["assigned_chapter"], 1)
        self.assertTrue(opening_beat["is_in_window"])

    def test_structure_html_generation_csp(self):
        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="save_the_cat")
        out_html = self.target_dir / "structure_report.html"
        generate_structure_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Story Paradigm & Structure Alignment", content)
        self.assertIn("Content-Security-Policy", content)


if __name__ == "__main__":
    unittest.main()
