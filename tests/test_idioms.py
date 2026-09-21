#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Earth Idiom & Immersion Engine (scripts/lib/idioms.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.idioms import (
    audit_manuscript_idioms,
    generate_idioms_html_report,
)


class TestIdiomsEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.ms_dir.mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_detect_eponyms_and_cliches(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Chapter 1
He knew this was a pyrrhic victory and their achilles' heel was exposed.
Playing devil's advocate, she warned him not to ignore the canary in a coal mine.
""", encoding="utf-8")

        findings = audit_manuscript_idioms(self.ms_dir)
        phrases = [f["phrase"] for f in findings]
        ids = [f["id"] for f in findings]

        self.assertIn("pyrrhic", phrases)
        self.assertIn("achilles' heel", phrases)
        self.assertIn("devil's advocate", phrases)
        self.assertIn("canary in a coal mine", phrases)

        self.assertIn("IDM-101", ids) # Eponym
        self.assertIn("IDM-102", ids) # Mythological/Scriptural
        self.assertIn("IDM-103", ids) # Flora/Fauna cliche

    def test_custom_whitelist(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Scene.md").write_text("""# Chapter 2
He ordered a sandwich before starting his diesel engine.
""", encoding="utf-8")

        findings_all = audit_manuscript_idioms(self.ms_dir)
        self.assertGreater(len(findings_all), 0)

        # Whitelist sandwich and diesel
        findings_whitelisted = audit_manuscript_idioms(self.ms_dir, custom_whitelist=["sandwich", "diesel"])
        self.assertEqual(len(findings_whitelisted), 0)

    def test_generate_idioms_html_report(self):
        html_out = Path(self.temp_dir.name) / "idioms.html"
        generate_idioms_html_report({
            "manuscript": "TestMS",
            "findings": [{"id": "IDM-101", "phrase": "draconian", "category": "Eponym", "snippet": "draconian law", "origin": "Draco", "suggestion": "harsh", "file": "01_Scene.md", "line": 1}]
        }, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("draconian", html_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
