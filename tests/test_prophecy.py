#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Prophecy Resolution Matrix (scripts/lib/prophecy.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.prophecy import (
    extract_prophecies,
    audit_prophecy_resolution,
    generate_prophecy_mermaid,
    generate_prophecy_html_report,
)


class TestProphecyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)
        (self.world_dir / "Cosmology" / "Prophecies").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    # --- Original 4 tests ---

    def test_extract_and_audit_prophecy(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "The_Bleeding_Star.md").write_text("""---
name: "The Bleeding Star"
type: prophecy
oracle: "[[Pythia of Delphi]]"
target_entity: "[[Chosen King]]"
status: unfulfilled
clauses:
  - "When the red star bleeds across the dawn"
  - "The shattered crown shall be remade"
---
# The Bleeding Star
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Chapter 1
The priest recalled The Bleeding Star prophecy as the red meteor streaked overhead.
@prophecy: The Bleeding Star
""", encoding="utf-8")

        prophecies = extract_prophecies(self.world_dir)
        self.assertIn("The Bleeding Star", prophecies)
        self.assertEqual(prophecies["The Bleeding Star"]["oracle"], "Pythia of Delphi")
        self.assertEqual(len(prophecies["The Bleeding Star"]["clauses"]), 2)

        findings = audit_prophecy_resolution(prophecies, self.ms_dir)
        self.assertEqual(len(findings), 0)

        mermaid = generate_prophecy_mermaid(prophecies)
        self.assertIn("stateDiagram-v2", mermaid)

    def test_orphan_prophecy_prp101(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Forgotten_Fate.md").write_text("""---
name: "Forgotten Fate"
type: prophecy
status: unfulfilled
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Chapter 1
A quiet day at the bakery with fresh warm bread.
""", encoding="utf-8")

        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir)

        ids = [f["id"] for f in findings]
        self.assertIn("PRP-101", ids)  # Forgotten Fate is orphaned

    def test_dead_chosen_one_prp102(self):
        (self.world_dir / "Characters").mkdir(parents=True, exist_ok=True)
        (self.world_dir / "Characters" / "Chosen_One.md").write_text("""---
name: "Chosen One"
type: character
status: deceased
death_year: "450 AC"
---
""", encoding="utf-8")
        (self.world_dir / "Cosmology" / "Prophecies" / "Fate.md").write_text("""---
name: "Ancient Fate"
type: prophecy
target_entity: "[[Chosen One]]"
status: unfulfilled
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, world_dir=self.world_dir)
        ids = [f["id"] for f in findings]
        self.assertIn("PRP-102", ids)

    def test_generate_prophecy_html_report(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Test_Prophecy.md").write_text("""---
name: "Solar Prophecy"
type: prophecy
status: fulfilled
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        html_out = Path(self.temp_dir.name) / "prophecy.html"
        generate_prophecy_html_report({"world": "TestWorld", "prophecies": prophecies, "findings": []}, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Solar Prophecy", html_out.read_text(encoding="utf-8"))

    # --- New tests (5–12) ---

    def test_multiple_prophecies_extracted(self):
        """Three distinct prophecy files → three entries in the extracted dict."""
        for slug, name in [
            ("Alpha.md", "Alpha Prophecy"),
            ("Beta.md", "Beta Prophecy"),
            ("Gamma.md", "Gamma Prophecy"),
        ]:
            (self.world_dir / "Cosmology" / "Prophecies" / slug).write_text(
                f'---\nname: "{name}"\ntype: prophecy\nstatus: unfulfilled\n---\n',
                encoding="utf-8",
            )
        prophecies = extract_prophecies(self.world_dir)
        self.assertEqual(len(prophecies), 3)

    def test_fulfilled_prophecy_with_manuscript_evidence(self):
        """status=fulfilled + manuscript mentions it by name → no PRP-103 finding."""
        (self.world_dir / "Cosmology" / "Prophecies" / "Sunfire.md").write_text("""---
name: "Sunfire Oath"
type: prophecy
status: fulfilled
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text(
            "The Sunfire Oath was finally fulfilled when the twin suns aligned.\n"
            "@prophecy: Sunfire Oath\n",
            encoding="utf-8",
        )
        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir)
        ids = [f["id"] for f in findings]
        self.assertNotIn("PRP-103", ids)

    def test_resolution_discrepancy_prp103(self):
        """status=fulfilled in lore with NO manuscript mention → PRP-103 raised."""
        (self.world_dir / "Cosmology" / "Prophecies" / "Silent_Covenant.md").write_text("""---
name: "Silent Covenant"
type: prophecy
status: fulfilled
---
""", encoding="utf-8")
        # Manuscript deliberately contains no mention of the prophecy or 'fulfilled'
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text(
            "A merchant sold apples in the square on a warm afternoon.\n",
            encoding="utf-8",
        )
        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir)
        ids = [f["id"] for f in findings]
        self.assertIn("PRP-103", ids)

    def test_clauses_extracted_correctly(self):
        """Prophecy with 3 clauses in frontmatter → len(clauses) == 3."""
        (self.world_dir / "Cosmology" / "Prophecies" / "Tripartite.md").write_text("""---
name: "Tripartite Vision"
type: prophecy
status: unfulfilled
clauses:
  - "When iron weeps upon the dawn"
  - "The silver throne shall crack asunder"
  - "And the last heir shall rise from ash"
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        self.assertIn("Tripartite Vision", prophecies)
        self.assertEqual(len(prophecies["Tripartite Vision"]["clauses"]), 3)

    def test_empty_prophecy_dir(self):
        """No prophecy files → empty dict and zero findings from audit."""
        # The Prophecies dir exists but is empty (created in setUp)
        prophecies = extract_prophecies(self.world_dir)
        self.assertEqual(len(prophecies), 0)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir)
        self.assertEqual(len(findings), 0)

    def test_mermaid_contains_states(self):
        """generate_prophecy_mermaid should include status keywords from the prophecy."""
        (self.world_dir / "Cosmology" / "Prophecies" / "Dawn.md").write_text("""---
name: "Dawn Pact"
type: prophecy
status: unfulfilled
---
""", encoding="utf-8")
        (self.world_dir / "Cosmology" / "Prophecies" / "Dusk.md").write_text("""---
name: "Dusk Accord"
type: prophecy
status: fulfilled
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        mermaid = generate_prophecy_mermaid(prophecies)
        # Either 'unfulfilled' or 'fulfilled' should appear as a lifecycle state label
        has_state = "unfulfilled" in mermaid.lower() or "fulfilled" in mermaid.lower()
        self.assertTrue(has_state)

    def test_html_csp_compliance(self):
        """Generated prophecy HTML report must include the mandatory CSP meta tag."""
        (self.world_dir / "Cosmology" / "Prophecies" / "Starfall.md").write_text("""---
name: "Starfall Omen"
type: prophecy
status: unfulfilled
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        html_out = Path(self.temp_dir.name) / "prp_csp.html"
        generate_prophecy_html_report(
            {"world": "TestWorld", "prophecies": prophecies, "findings": []}, html_out
        )
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("default-src", content)

    def test_partially_fulfilled_status(self):
        """Prophecy with status=partially_fulfilled is extracted with the correct status value."""
        (self.world_dir / "Cosmology" / "Prophecies" / "Partial.md").write_text("""---
name: "Ember Prophecy"
type: prophecy
status: partially_fulfilled
oracle: "[[The Blind Seer]]"
target_entity: "[[The Half-King]]"
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        self.assertIn("Ember Prophecy", prophecies)
        self.assertEqual(prophecies["Ember Prophecy"]["status"], "partially_fulfilled")


if __name__ == "__main__":
    unittest.main()
