#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Scene Mechanics MRU Analyzer (scripts/lib/scene_mechanics.py).
Validates:
- PLT-104: Motivation-Reaction Unit sentence classification.
- Proactive scene (Goal -> Conflict -> Disaster) vs Reactive sequel (Reaction -> Dilemma -> Decision).
- Inverted MRU sequence alerts.
- HTML report generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.scene_mechanics import (
    classify_sentence_mru,
    analyze_scene_text,
    scan_manuscript_scenes,
    generate_scene_mechanics_html
)


class TestSceneMechanicsEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_classify_mru_phases(self):
        self.assertEqual(classify_sentence_mru('"Get down now!"'), "Action/Dialogue")
        self.assertEqual(classify_sentence_mru("Her heart hammered against her ribs as her breath caught."), "Visceral Reflex")
        self.assertEqual(classify_sentence_mru("A wave of pure terror washed over him."), "Emotional Response")
        self.assertEqual(classify_sentence_mru("He realized there was no escape through the northern gate."), "Cognitive Thought")
        self.assertEqual(classify_sentence_mru("The stone column crashed onto the marble floor."), "Action/Stimulus")

    def test_analyze_proactive_scene(self):
        text = """# Infiltration
        We must breach the lower vaults before midnight.
        The guards attacked with iron halberds, clashing against our shields.
        Suddenly, the ceiling collapsed in a shower of stone, trapping our retreat.
        """
        res = analyze_scene_text(text, "Infiltration")
        self.assertEqual(res["scene_type"], "Proactive Scene")
        self.assertTrue(res["has_goal"])
        self.assertTrue(res["has_disaster"])

    def test_inverted_mru_detection(self):
        # Cognitive Thought followed by Visceral Reflex
        text = """
        He thought the archers had missed their mark.
        His breath seized as his heart jumped into his throat.
        """
        res = analyze_scene_text(text, "Inverted")
        self.assertGreater(len(res["mru_flaws"]), 0)

    def test_inverted_mru_dialogue_before_visceral(self):
        # Spoken Dialogue followed by Visceral Reflex
        text = """
        "We are safe here," Elena said.
        Her heart slammed into her throat as a cold shiver ran down her spine.
        """
        res = analyze_scene_text(text, "DialogueBeforeVisceral")
        self.assertGreater(len(res["mru_flaws"]), 0)

    def test_scan_and_html_generation(self):
        (self.target_dir / "01_Scene1.md").write_text("He must find the book. He struck the foe.", encoding="utf-8")
        report = scan_manuscript_scenes(self.target_dir)
        self.assertEqual(report["total_scenes"], 1)

        out_html = self.target_dir / "scene_report.html"
        generate_scene_mechanics_html(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Scene Mechanics & Motivation-Reaction Units", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
