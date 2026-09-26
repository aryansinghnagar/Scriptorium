#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Dynastic Genealogies & Succession Lineages (scripts/lib/genealogy.py).
Covers family tree graph construction, biological/chronological paradox detection,
succession ranking, Mermaid.js code generation, HTML reporting, and terminal tree rendering.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.genealogy import (
    generate_genealogy_html_report,
    generate_mermaid_flowchart,
    get_house_lineage,
    load_characters_and_houses,
    matches_house_or_character,
    normalize_house_token,
    parse_year,
    print_terminal_tree,
    validate_genealogy,
)


class TestGenealogyEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.chars_dir = self.world_dir / "Characters"
        self.chars_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_parse_year(self) -> None:
        """parse_year correctly converts BCE, BC, negative, and positive year strings to floats."""
        self.assertEqual(parse_year("450 BCE"), -450.0)
        self.assertEqual(parse_year("-300 IE"), -300.0)
        self.assertEqual(parse_year("1200 AC"), 1200.0)
        self.assertEqual(parse_year(500), 500.0)
        self.assertIsNone(parse_year(None))
        self.assertIsNone(parse_year(""))

    def test_load_characters_relationships(self) -> None:
        """load_characters_and_houses establishes bidirectional parent, child, and spouse links."""
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

    def test_chronological_paradox_child_before_parent_gen101(self) -> None:
        """GEN-101 flags when a child is recorded as born before their parent."""
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
        self.assertTrue(any(f["id"] == "GEN-101" and "before or same year" in f["message"] for f in findings))

    def test_chronological_paradox_child_after_parent_deceased_gen101(self) -> None:
        """GEN-101 flags when a child is born more than 1 year after parent's death."""
        (self.chars_dir / "DeceasedFather.md").write_text("""---
name: "DeceasedFather"
born: "100 AC"
died: "140 AC"
---
""", encoding="utf-8")

        (self.chars_dir / "LateChild.md").write_text("""---
name: "LateChild"
parents: ["[[DeceasedFather]]"]
born: "145 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "deceased" in f["message"] for f in findings))

    def test_fuzzy_generational_builder_skips_chron_checks(self) -> None:
        """Fuzzy generation connections bypass GEN-101 chron checks."""
        (self.chars_dir / "AncientAncestor.md").write_text("""---
name: "AncientAncestor"
born: "100 AC"
died: "150 AC"
---
""", encoding="utf-8")

        (self.chars_dir / "LateDescendant.md").write_text("""---
name: "LateDescendant"
parents: ["direct descendant via ~4 unrecorded generations from [[AncientAncestor]]"]
born: "300 AC"
---
""", encoding="utf-8")
        
        chars = load_characters_and_houses(self.world_dir)
        self.assertIn("AncientAncestor", chars["LateDescendant"]["parents"])
        self.assertIn("AncientAncestor", chars["LateDescendant"]["fuzzy_parents"])
        
        findings = validate_genealogy(chars)
        # Should not flag GEN-101 for LateDescendant
        self.assertFalse(any(f["id"] == "GEN-101" and f["character"] == "LateDescendant" for f in findings))

    def test_lifespan_sanity_died_before_born_gen101(self) -> None:
        """GEN-101 flags when a character's death year precedes their birth year."""
        (self.chars_dir / "TimeTraveler.md").write_text("""---
name: "TimeTraveler"
born: "200 AC"
died: "180 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "died" in f["message"] for f in findings))

    def test_circular_ancestry_paradox_gen101(self) -> None:
        """GEN-101 detects circular ancestry loops (A -> B -> A)."""
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

    def test_succession_order_conflict_gen102(self) -> None:
        """GEN-102 detects multiple claimants to the same succession rank in a house."""
        (self.chars_dir / "Claimant1.md").write_text("""---
name: "Claimant1"
house: "House Corrino"
succession_order: 1
---
""", encoding="utf-8")

        (self.chars_dir / "Claimant2.md").write_text("""---
name: "Claimant2"
house: "House Corrino"
succession_order: 1
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-102" and "#1" in f["message"] for f in findings))

    def test_mermaid_generation(self) -> None:
        """Mermaid generator produces flowchart with styling classes and succession emojis."""
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

    def test_lineage_roster_sorting(self) -> None:
        """Lineage roster sorts claimants primarily by succession order, then birth year."""
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

    def test_house_name_normalization_matching(self) -> None:
        """House name matcher normalizes prefixes like 'House', 'Clan', and 'Dynasty'."""
        (self.chars_dir / "Eddard.md").write_text("""---
name: "Eddard"
house: "Stark"
succession_order: 1
---
""", encoding="utf-8")

        self.assertEqual(normalize_house_token("The House of Stark"), "stark")
        self.assertEqual(normalize_house_token("Clan Dragon"), "dragon")

        chars = load_characters_and_houses(self.world_dir)
        lineage = get_house_lineage(chars, "House Stark")
        self.assertEqual(len(lineage), 1)
        self.assertEqual(lineage[0]["name"], "Eddard")

        self.assertTrue(matches_house_or_character(chars["Eddard"], "Stark"))

    def test_html_report_generation(self) -> None:
        """HTML report generates with strict offline Content-Security-Policy and table markup."""
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
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Dynastic Genealogy", content)
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    def test_terminal_tree_output(self) -> None:
        """print_terminal_tree renders unicode tree representation to stdout."""
        (self.chars_dir / "King.md").write_text("""---
name: "High King"
title: "Sovereign"
succession_order: 1
children: ["[[Prince]]"]
---
""", encoding="utf-8")
        (self.chars_dir / "Prince.md").write_text("""---
name: "Prince"
title: "Heir"
succession_order: 2
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_terminal_tree(chars, "High King")
            output = mock_stdout.getvalue()
            self.assertIn("High King", output)
            self.assertIn("Prince", output)


if __name__ == "__main__":
    unittest.main()
