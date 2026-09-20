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
        self.assertIn("PRP-101", ids) # Forgotten Fate is orphaned

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


if __name__ == "__main__":
    unittest.main()
