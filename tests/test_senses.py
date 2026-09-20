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

        self.assertIn("SNS-101", ids) # White room syndrome flagged

    def test_generate_senses_html_report(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
The scarlet sun sank in silence. The icy wind howled.
""", encoding="utf-8")
        audit = audit_manuscript_senses(self.ms_dir)
        html_out = Path(self.temp_dir.name) / "senses.html"
        generate_senses_html_report(audit, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Sensory Palette", html_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
