#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Scene Mechanics MRU Analyzer (scripts/lib/scene_mechanics.py).
Validates:
- PLT-104: Motivation-Reaction Unit sentence classification.
- Proactive scene (Goal -> Conflict -> Disaster) vs Reactive sequel (Reaction -> Dilemma -> Decision).
- Inverted MRU sequence alerts.
- Goal, disaster, and scene type detection.
- HTML report generation with CSP compliance.
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
    generate_scene_mechanics_html,
)


class TestSceneMechanicsEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # Original 5 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_classify_mru_phases(self):
        """All five MRU phases must be correctly classified."""
        self.assertEqual(classify_sentence_mru('"Get down now!"'), "Action/Dialogue")
        self.assertEqual(classify_sentence_mru("Her heart hammered against her ribs as her breath caught."), "Visceral Reflex")
        self.assertEqual(classify_sentence_mru("A wave of pure terror washed over him."), "Emotional Response")
        self.assertEqual(classify_sentence_mru("He realized there was no escape through the northern gate."), "Cognitive Thought")
        self.assertEqual(classify_sentence_mru("The stone column crashed onto the marble floor."), "Action/Stimulus")

    def test_analyze_proactive_scene(self):
        """Scene heavy with external action and goal keywords must be typed as Proactive Scene."""
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
        """Cognitive thought directly followed by visceral reflex must flag an MRU inversion."""
        text = """
        He thought the archers had missed their mark.
        His breath seized as his heart jumped into his throat.
        """
        res = analyze_scene_text(text, "Inverted")
        self.assertGreater(len(res["mru_flaws"]), 0)

    def test_inverted_mru_dialogue_before_visceral(self):
        """Spoken dialogue directly followed by visceral reflex must flag an MRU inversion."""
        text = """
        "We are safe here," Elena said.
        Her heart slammed into her throat as a cold shiver ran down her spine.
        """
        res = analyze_scene_text(text, "DialogueBeforeVisceral")
        self.assertGreater(len(res["mru_flaws"]), 0)

    def test_scan_and_html_generation(self):
        """scan_manuscript_scenes and generate_scene_mechanics_html must work end-to-end."""
        (self.target_dir / "01_Scene1.md").write_text("He must find the book. He struck the foe.", encoding="utf-8")
        report = scan_manuscript_scenes(self.target_dir)
        self.assertEqual(report["total_scenes"], 1)

        out_html = self.target_dir / "scene_report.html"
        generate_scene_mechanics_html(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Scene Mechanics & Motivation-Reaction Units", out_html.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # New tests 6–12                                                       #
    # ------------------------------------------------------------------ #

    def test_classify_visceral_reflex_specific(self):
        """A sentence with 'pulse' must classify as Visceral Reflex."""
        result = classify_sentence_mru("His pulse raced as the shadow swept across the floor.")
        self.assertEqual(result, "Visceral Reflex")

    def test_classify_emotional_response_specific(self):
        """A sentence with 'terror' must classify as Emotional Response."""
        result = classify_sentence_mru("Terror gripped her as the door swung open.")
        self.assertEqual(result, "Emotional Response")

    def test_classify_cognitive_thought_specific(self):
        """A sentence with 'realized' must classify as Cognitive Thought."""
        result = classify_sentence_mru("She realized the key was still in her pocket.")
        self.assertEqual(result, "Cognitive Thought")

    def test_classify_action_stimulus_default(self):
        """A plain action sentence with no keyword triggers must classify as Action/Stimulus."""
        result = classify_sentence_mru("The iron gate slammed shut behind them.")
        self.assertEqual(result, "Action/Stimulus")

    def test_analyze_reactive_sequel(self):
        """Text heavy with emotional/visceral content must be typed as Reactive Sequel."""
        text = """
        Terror gripped him as dread pooled in his stomach.
        His breath came in ragged gasps, heart pounding.
        Fear of what lay ahead overwhelmed him utterly.
        Shame washed over him as panic surged through his veins.
        """
        res = analyze_scene_text(text, "ReactiveSequel")
        self.assertEqual(res["scene_type"], "Reactive Sequel")

    def test_scan_multiple_files_count(self):
        """scan_manuscript_scenes with 2 markdown files must return total_scenes == 2."""
        (self.target_dir / "01_Scene1.md").write_text("He had to find the relic.", encoding="utf-8")
        (self.target_dir / "02_Scene2.md").write_text("Terror washed over her as she gasped.", encoding="utf-8")
        report = scan_manuscript_scenes(self.target_dir)
        self.assertEqual(report["total_scenes"], 2)

    def test_html_csp_compliant(self):
        """generate_scene_mechanics_html output must contain Content-Security-Policy meta tag."""
        (self.target_dir / "01_ch.md").write_text("He must escape. Suddenly the gate crashed.", encoding="utf-8")
        report = scan_manuscript_scenes(self.target_dir)
        out_html = self.target_dir / "scene_csp.html"
        generate_scene_mechanics_html(report, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="Scene mechanics HTML is missing Content-Security-Policy meta tag",
        )


if __name__ == "__main__":
    unittest.main()
