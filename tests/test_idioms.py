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

    # Convenience: write a scene file and return its path
    def _write_scene(self, filename: str, text: str) -> Path:
        path = self.ms_dir / "Book-01" / "01_Act_I" / filename
        path.write_text(text, encoding="utf-8")
        return path

    # ------------------------------------------------------------------ #
    # Original 3 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_detect_eponyms_and_cliches(self):
        self._write_scene(
            "01_Scene.md",
            """# Chapter 1
He knew this was a pyrrhic victory and their achilles' heel was exposed.
Playing devil's advocate, she warned him not to ignore the canary in a coal mine.
""",
        )

        findings = audit_manuscript_idioms(self.ms_dir)
        phrases = [f["phrase"] for f in findings]
        ids = [f["id"] for f in findings]

        self.assertIn("pyrrhic", phrases)
        self.assertIn("achilles' heel", phrases)
        self.assertIn("devil's advocate", phrases)
        self.assertIn("canary in a coal mine", phrases)

        self.assertIn("IDM-101", ids)  # Eponym
        self.assertIn("IDM-102", ids)  # Mythological/Scriptural
        self.assertIn("IDM-103", ids)  # Flora/Fauna cliché

    def test_custom_whitelist(self):
        self._write_scene(
            "02_Scene.md",
            """# Chapter 2
He ordered a sandwich before starting his diesel engine.
""",
        )

        findings_all = audit_manuscript_idioms(self.ms_dir)
        self.assertGreater(len(findings_all), 0)

        # Whitelist sandwich and diesel
        findings_whitelisted = audit_manuscript_idioms(
            self.ms_dir, custom_whitelist=["sandwich", "diesel"]
        )
        self.assertEqual(len(findings_whitelisted), 0)

    def test_generate_idioms_html_report(self):
        html_out = Path(self.temp_dir.name) / "idioms.html"
        generate_idioms_html_report(
            {
                "manuscript": "TestMS",
                "findings": [
                    {
                        "id": "IDM-101",
                        "phrase": "draconian",
                        "category": "Eponym",
                        "snippet": "draconian law",
                        "origin": "Draco",
                        "suggestion": "harsh",
                        "file": "01_Scene.md",
                        "line": 1,
                    }
                ],
            },
            html_out,
        )
        self.assertTrue(html_out.is_file())
        self.assertIn("draconian", html_out.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # New tests 4–10                                                       #
    # ------------------------------------------------------------------ #

    def test_machiavellian_detected(self):
        """'machiavellian' is an IDM-101 eponym and must be flagged."""
        self._write_scene(
            "03_Scene.md",
            """# Chapter 3
His machiavellian scheme unfolded with cold precision.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        phrases = [f["phrase"] for f in findings]
        ids = [f["id"] for f in findings]
        self.assertIn(
            "machiavellian", phrases, msg="Expected 'machiavellian' to be flagged as IDM-101"
        )
        self.assertIn("IDM-101", ids)

    def test_pandoras_box_detected(self):
        """'pandora's box' is an IDM-102 mythological reference and must be flagged."""
        self._write_scene(
            "04_Scene.md",
            """# Chapter 4
Opening that vault was like lifting pandora's box.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        phrases = [f["phrase"] for f in findings]
        ids = [f["id"] for f in findings]
        self.assertIn(
            "pandora's box", phrases, msg="Expected 'pandora's box' to be flagged as IDM-102"
        )
        self.assertIn("IDM-102", ids)

    def test_empty_chapter_no_findings(self):
        """A file with no prose (only a heading) should produce zero findings."""
        self._write_scene(
            "05_Scene.md",
            """# Empty Chapter

""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        self.assertEqual(
            len(findings), 0, msg=f"Expected 0 findings for empty chapter but got: {findings}"
        )

    def test_multiple_idioms_in_one_chapter(self):
        """A chapter containing pyrrhic + achilles' heel + canary should yield ≥ 3 findings."""
        self._write_scene(
            "06_Scene.md",
            """# Chapter 6
It was a pyrrhic victory at best.
The kingdom's achilles' heel had been its pride.
Nobody had noticed the canary in a coal mine.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        self.assertGreaterEqual(
            len(findings),
            3,
            msg=f"Expected at least 3 findings but got {len(findings)}: {findings}",
        )

    def test_whitelist_partial(self):
        """Whitelisting 'pyrrhic' only suppresses that idiom; others remain detected."""
        self._write_scene(
            "07_Scene.md",
            """# Chapter 7
A pyrrhic outcome left him hollow.
It was his achilles' heel all along.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir, custom_whitelist=["pyrrhic"])
        phrases = [f["phrase"] for f in findings]
        self.assertNotIn(
            "pyrrhic", phrases, msg="'pyrrhic' should be suppressed by whitelist"
        )
        self.assertIn(
            "achilles' heel", phrases, msg="'achilles' heel' should still be detected"
        )

    def test_html_csp_compliance(self):
        """Generated idioms HTML report must include a Content-Security-Policy meta tag."""
        html_out = Path(self.temp_dir.name) / "idioms_csp.html"
        generate_idioms_html_report(
            {
                "manuscript": "CSPTest",
                "findings": [
                    {
                        "id": "IDM-103",
                        "phrase": "canary in a coal mine",
                        "category": "Flora/Fauna Cliché",
                        "snippet": "the canary in a coal mine sang",
                        "origin": "Mining industry",
                        "suggestion": "a silent warning",
                        "file": "08_Scene.md",
                        "line": 2,
                    }
                ],
            },
            html_out,
        )
        content = html_out.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="Idioms HTML report is missing a Content-Security-Policy meta tag",
        )

    def test_finding_has_required_fields(self):
        """Every returned finding dict must contain id, phrase, file, and line fields."""
        self._write_scene(
            "09_Scene.md",
            """# Chapter 9
The herculean effort required a sisyphean commitment.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        self.assertGreater(len(findings), 0, msg="Expected at least one finding")
        required_fields = {"id", "phrase", "file", "line"}
        for finding in findings:
            missing = required_fields - finding.keys()
            self.assertEqual(
                missing,
                set(),
                msg=f"Finding is missing required fields {missing}: {finding}",
            )


    def test_finding_has_message_field(self):
        """Every returned finding dict must contain a 'message' field with non-empty string."""
        self._write_scene(
            "10_Scene.md",
            """# Chapter 10
The draconian regulations made his sisyphean task even harder.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        self.assertGreater(len(findings), 0, msg="Expected at least one finding")
        for finding in findings:
            self.assertIn("message", finding, msg=f"Finding missing 'message' field: {finding}")
            self.assertIsInstance(finding["message"], str)
            self.assertGreater(len(finding["message"]), 0)

    def test_trojan_horse_detected(self):
        """'trojan horse' is an IDM-101 eponym and must be flagged."""
        self._write_scene(
            "11_Scene.md",
            """# Chapter 11
The gift was a trojan horse designed to lull them into safety.
""",
        )
        findings = audit_manuscript_idioms(self.ms_dir)
        phrases = [f["phrase"] for f in findings]
        self.assertIn(
            "trojan horse", phrases, msg="Expected 'trojan horse' to be flagged as IDM-101"
        )


if __name__ == "__main__":
    unittest.main()
