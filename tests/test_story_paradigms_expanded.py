#!/usr/bin/env python3
"""
Test Suite: Universal Multi-Paradigm Story Structure Engine
(tests/test_story_paradigms_expanded.py)
================================================================================
Validates all 9 narrative paradigms, beat sheet windows, and HTML generation.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.lib.structure import PARADIGMS, generate_structure_html_report, scan_manuscript_structure

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestStoryParadigmsExpanded(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        # Create a mock 4-chapter manuscript
        self.ch1 = self.root / "01_Ch1.md"
        self.ch2 = self.root / "02_Ch2.md"
        self.ch3 = self.root / "03_Ch3.md"
        self.ch4 = self.root / "04_Ch4.md"

        self.ch1.write_text("Word " * 500, encoding="utf-8")
        self.ch2.write_text("Word " * 500, encoding="utf-8")
        self.ch3.write_text("Word " * 500, encoding="utf-8")
        self.ch4.write_text("Word " * 500, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_all_nine_paradigms_registered(self):
        expected_keys = {
            "three_act",
            "save_the_cat",
            "heros_journey",
            "story_circle",
            "seven_point",
            "eight_sequence",
            "fichtean_curve",
            "kishotenketsu",
            "freytags_pyramid",
        }
        self.assertTrue(expected_keys.issubset(set(PARADIGMS.keys())))

    def test_paradigm_beat_specifications(self):
        for key, paradigm in PARADIGMS.items():
            self.assertIn("name", paradigm, f"Paradigm '{key}' missing 'name'")
            self.assertIn("beats", paradigm, f"Paradigm '{key}' missing 'beats'")
            self.assertGreaterEqual(len(paradigm["beats"]), 4, f"Paradigm '{key}' must have at least 4 beats")

            last_pct = 0.0
            for beat in paradigm["beats"]:
                self.assertIn("name", beat)
                self.assertIn("target_pct", beat)
                self.assertIn("window", beat)
                self.assertIn("desc", beat)

                target_pct = beat["target_pct"]
                w_min, w_max = beat["window"]

                self.assertGreaterEqual(target_pct, 0.0)
                self.assertLessEqual(target_pct, 1.0)
                self.assertLessEqual(w_min, w_max)
                self.assertGreaterEqual(w_min, 0.0)
                self.assertLessEqual(w_max, 1.0)
                self.assertGreaterEqual(target_pct, last_pct, f"Beat target_pct out of order in '{key}': {beat['name']}")
                last_pct = target_pct

    def test_scan_all_paradigms_on_manuscript(self):
        for p_key in PARADIGMS:
            report = scan_manuscript_structure(self.root, paradigm_key=p_key)
            self.assertEqual(report["total_words"], 2000)
            self.assertEqual(report["total_chapters"], 4)
            self.assertEqual(report["paradigm_key"], p_key)
            self.assertGreaterEqual(report["harmony_score"], 0.0)
            self.assertLessEqual(report["harmony_score"], 100.0)
            self.assertEqual(len(report["beats"]), len(PARADIGMS[p_key]["beats"]))

    def test_html_report_generation(self):
        import html
        out_html = self.root / "report.html"
        for p_key in ["eight_sequence", "kishotenketsu", "fichtean_curve", "freytags_pyramid"]:
            report = scan_manuscript_structure(self.root, paradigm_key=p_key)
            res_path = generate_structure_html_report(report, out_html)
            self.assertTrue(res_path.is_file())
            content = out_html.read_text(encoding="utf-8")
            self.assertIn(html.escape(report["paradigm_name"]), content)
            self.assertIn("Structural Beat Sheet Map", content)


if __name__ == "__main__":
    unittest.main()
