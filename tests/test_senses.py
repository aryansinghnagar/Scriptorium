#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum 6D Sensory Palette & White Room Engine (scripts/lib/senses.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.senses import (
    analyze_text_senses,
    audit_manuscript_senses,
    generate_senses_html_report,
)


class TestSensesEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.ms_dir.mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    # --- Original 3 tests ---

    def test_analyze_text_senses(self):
        sample = """
        The crimson banner fluttered in the darkness. A deafening roar echoed through the stone hall.
        The pungent aroma of sulfur and burning smoke filled his nostrils, while the bitter taste of ash
        lingered on his tongue. Freezing rain struck his rough skin as vertigo made him stumble with dizziness.
        """
        res = analyze_text_senses(sample)
        self.assertGreater(res["counts"]["visual"], 0)
        self.assertGreater(res["counts"]["auditory"], 0)
        self.assertGreater(res["counts"]["olfactory"], 0)
        self.assertGreater(res["counts"]["gustatory"], 0)
        self.assertGreater(res["counts"]["tactile_thermal"], 0)
        self.assertGreater(res["counts"]["kinesthetic_vestibular"], 0)

    def test_white_room_and_monotony_detection(self):
        # White room: 200 words of pure visual or abstract discourse without auditory/tactile/olfactory
        white_room_text = "The room was large and rectangular with white walls and a grey ceiling. " * 20
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_WhiteRoom.md").write_text(white_room_text, encoding="utf-8")

        audit = audit_manuscript_senses(self.ms_dir)
        findings = audit["findings"]
        ids = [f["id"] for f in findings]

        self.assertIn("SNS-101", ids)  # White room syndrome flagged

    def test_generate_senses_html_report(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
The scarlet sun sank in silence. The icy wind howled.
""", encoding="utf-8")
        audit = audit_manuscript_senses(self.ms_dir)
        html_out = Path(self.temp_dir.name) / "senses.html"
        generate_senses_html_report(audit, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Sensory Palette", html_out.read_text(encoding="utf-8"))

    # --- New tests (4–12) ---

    def test_pure_visual_text_dominance(self):
        """Text containing only visual words should have dominant == 'visual'."""
        visual_text = (
            "The crimson shadow gleamed with golden radiance across the azure gloom. "
            "Scarlet silhouettes shimmered in the amber darkness, vivid and luminous. "
            "An ivory pallor settled over the ebony emerald wall, opaque and translucent. "
        )
        res = analyze_text_senses(visual_text)
        # Find the dimension with the highest count
        dominant = max(res["counts"], key=lambda d: res["counts"][d])
        self.assertEqual(dominant, "visual")

    def test_empty_text_returns_zero_counts(self):
        """Empty string should return all-zero sensory counts."""
        res = analyze_text_senses("")
        for dim in ("visual", "auditory", "olfactory", "gustatory", "tactile_thermal", "kinesthetic_vestibular"):
            self.assertEqual(res["counts"][dim], 0)
        self.assertEqual(res["total_sensory_anchors"], 0)

    def test_sensory_monotony_sns102(self):
        """Scene >300 words with >=5 sensory anchors all visual, >=90% visual → SNS-102."""
        # Build >300-word scene using repeated visual phrases (no other senses)
        visual_phrase = (
            "The crimson shadow gleamed across the azure gloom. "
            "Scarlet silhouettes shimmered in the amber darkness. "
            "An ivory pallor bathed the ebony emerald edifice. "
            "The vivid golden radiance flickered in translucent murk. "
            "Cobalt and indigo gleam sparkled in the brilliant glare. "
        )
        long_visual_scene = visual_phrase * 12  # well over 300 words, purely visual
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Monotony.md").write_text(
            long_visual_scene, encoding="utf-8"
        )
        audit = audit_manuscript_senses(self.ms_dir)
        ids = [f["id"] for f in audit["findings"]]
        self.assertIn("SNS-102", ids)

    def test_rich_prose_no_findings(self):
        """Scene that covers all 6 senses should generate zero diagnostic findings."""
        rich_scene = (
            "The crimson banner cast a scarlet gleam across the golden hall. "
            "A low roar echoed from beyond the iron gate, followed by the whisper of wind. "
            "The pungent aroma of sulfur and musty incense drifted through the corridor. "
            "Ash and bitter copper coated his tongue with a metallic tang. "
            "Freezing rain drummed against his rough skin and coarse cloak. "
            "Vertigo seized him as he lurched sideways, momentum carrying him off-balance. "
        ) * 6  # repeat to ensure >150 words
        (self.ms_dir / "Book-01" / "01_Act_I" / "03_Rich.md").write_text(
            rich_scene, encoding="utf-8"
        )
        audit = audit_manuscript_senses(self.ms_dir)
        self.assertEqual(len(audit["findings"]), 0)

    def test_audit_multiple_chapters(self):
        """Audit over 2 chapters (one white room, one rich) should return >=2 scenes and findings."""
        # Chapter 1: white room
        white_text = "The hallway was long and rectangular with pale walls and a grey ceiling. " * 20
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_WhiteRoom.md").write_text(
            white_text, encoding="utf-8"
        )
        # Chapter 2: rich prose
        rich_text = (
            "The crimson beacon blazed in the amber gloom. A shriek and rumble echoed from the abyss. "
            "The stench and musk of sulfur filled his lungs. Bitter ash coated his tongue. "
            "Icy stone was rough under his freezing palm. Vertigo made him stagger as momentum faded. "
        ) * 6
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Rich.md").write_text(
            rich_text, encoding="utf-8"
        )
        audit = audit_manuscript_senses(self.ms_dir)
        self.assertGreaterEqual(len(audit["scenes"]), 2)
        self.assertGreater(len(audit["findings"]), 0)

    def test_analyze_returns_total_count(self):
        """Sample text with known lexicon words should yield total_sensory_anchors > 0."""
        sample = "The shadow glimmered. A whisper echoed. The scent of pine drifted past."
        res = analyze_text_senses(sample)
        self.assertGreater(res["total_sensory_anchors"], 0)

    def test_html_csp_compliance(self):
        """Generated HTML report must contain the mandatory CSP meta tag."""
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text(
            "The scarlet sun sank. The icy wind howled. Pungent smoke drifted past. "
            "A bitter taste lingered. Rough stone abraded his palm. Vertigo struck him. ",
            encoding="utf-8",
        )
        audit = audit_manuscript_senses(self.ms_dir)
        html_out = Path(self.temp_dir.name) / "csp_test.html"
        generate_senses_html_report(audit, html_out)
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("default-src", content)

    def test_html_contains_all_dimensions(self):
        """HTML report must surface all 6 sensory dimension labels."""
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text(
            "The crimson dawn broke silently. A roar echoed. Pungent smoke filled the air. "
            "Bitter ash coated his tongue. The rough icy stone scraped his skin. "
            "Vertigo made him stagger with momentum. ",
            encoding="utf-8",
        )
        audit = audit_manuscript_senses(self.ms_dir)
        html_out = Path(self.temp_dir.name) / "dim_test.html"
        generate_senses_html_report(audit, html_out)
        content = html_out.read_text(encoding="utf-8")
        for label in ("Visual", "Auditory", "Olfactory", "Gustatory", "Tactile", "Kinesthetic"):
            self.assertIn(label, content)

    def test_json_output_structure(self):
        """analyze_text_senses result must contain all 6 dimension keys inside 'counts'."""
        res = analyze_text_senses("The scarlet banner gleamed. A whisper echoed through the darkness.")
        expected_dims = {
            "visual",
            "auditory",
            "olfactory",
            "gustatory",
            "tactile_thermal",
            "kinesthetic_vestibular",
        }
        self.assertEqual(set(res["counts"].keys()), expected_dims)


if __name__ == "__main__":
    unittest.main()
