#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Dynastic Genealogies & Succession Lineages (scripts/lib/genealogy.py).
Covers family tree graph construction, biological/chronological paradox detection,
succession ranking, Mermaid.js code generation, and HTML reporting.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.genealogy import (
    load_characters_and_houses,
    validate_genealogy,
    get_house_lineage,
    generate_mermaid_flowchart,
    generate_genealogy_html_report,
    parse_year,
)


class TestGenealogyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.chars_dir = self.world_dir / "Characters"
        self.chars_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_year(self):
        self.assertEqual(parse_year("450 BCE"), -450.0)
        self.assertEqual(parse_year("-300 IE"), -300.0)
        self.assertEqual(parse_year("1200 AC"), 1200.0)
        self.assertEqual(parse_year(500), 500.0)

    def test_load_characters_relationships(self):
        # Father: King Eldor
        (self.chars_dir / "King_Eldor.md").write_text("""---
name: "King Eldor I"
type: character
house: "House Vance"
title: "High King"
born: "100 AC"
died: "165 AC"
succession_order: 1
---
""", encoding="utf-8")

        # Son: Prince Valen
        (self.chars_dir / "Prince_Valen.md").write_text("""---
name: "Prince Valen"
type: character
house: "House Vance"
title: "Crown Prince"
parents: ["[[King Eldor I]]"]
born: "125 AC"
died: "180 AC"
succession_order: 2
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        self.assertIn("King Eldor I", chars)
        self.assertIn("Prince Valen", chars)

        # Check bidirectional relationship
        self.assertIn("Prince Valen", chars["King Eldor I"]["children"])
        self.assertIn("King Eldor I", chars["Prince Valen"]["parents"])

    def test_chronological_paradox_child_before_parent(self):
        # Parent born 150 AC, Child born 120 AC (Paradox!)
        (self.chars_dir / "Parent.md").write_text("""---
name: "Parent"
born: "150 AC"
---
""", encoding="utf-8")

        (self.chars_dir / "Child.md").write_text("""---
name: "Child"
parents: ["[[Parent]]"]
born: "120 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "born" in f["message"] for f in findings))

    def test_circular_ancestry_paradox(self):
        # A parent of B, B parent of A
        (self.chars_dir / "Alpha.md").write_text("""---
name: "Alpha"
parents: ["[[Beta]]"]
---
""", encoding="utf-8")

        (self.chars_dir / "Beta.md").write_text("""---
name: "Beta"
parents: ["[[Alpha]]"]
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "Circular ancestry" in f["message"] for f in findings))

    def test_mermaid_generation(self):
        (self.chars_dir / "Lord_Stark.md").write_text("""---
name: "Lord Stark"
house: "House Stark"
title: "Warden of the North"
born: "250 AC"
succession_order: 1
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        mermaid = generate_mermaid_flowchart(chars, "House Stark")
        self.assertIn("```mermaid", mermaid)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("Lord Stark", mermaid)
        self.assertIn("👑 <b>#1</b>", mermaid)

    def test_lineage_roster_sorting(self):
        (self.chars_dir / "Prince_B.md").write_text("""---
name: "Prince B"
house: "House Tudor"
succession_order: 2
born: "1500"
---
""", encoding="utf-8")

        (self.chars_dir / "King_A.md").write_text("""---
name: "King A"
house: "House Tudor"
succession_order: 1
born: "1480"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        lineage = get_house_lineage(chars, "House Tudor")
        self.assertEqual(len(lineage), 2)
        self.assertEqual(lineage[0]["name"], "King A")
        self.assertEqual(lineage[1]["name"], "Prince B")

    def test_house_name_normalization_matching(self):
        # Character has house: "Stark" (without 'House' prefix in note)
        (self.chars_dir / "Eddard.md").write_text("""---
name: "Eddard"
house: "Stark"
succession_order: 1
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        # Querying with 'House Stark' should successfully match house: 'Stark'
        lineage = get_house_lineage(chars, "House Stark")
        self.assertEqual(len(lineage), 1)
        self.assertEqual(lineage[0]["name"], "Eddard")

        # Querying with 'Stark' should also match
        lineage2 = get_house_lineage(chars, "Stark")
        self.assertEqual(len(lineage2), 1)

    def test_html_report_generation(self):
        (self.chars_dir / "Noble.md").write_text("""---
name: "Noble"
house: "House Vance"
---
""", encoding="utf-8")
        chars = load_characters_and_houses(self.world_dir)
        mermaid = generate_mermaid_flowchart(chars, "House Vance")
        lineage = get_house_lineage(chars, "House Vance")
        out_html = self.world_dir / "genealogy.html"
        generate_genealogy_html_report("House Vance", mermaid, lineage, [], out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Dynastic Genealogy", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
