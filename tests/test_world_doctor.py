#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum World Doctor (scripts/lib/world_doctor.py)
"""

import unittest
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.world_doctor import (
    parse_frontmatter,
    parse_timeline_date,
    compare_timeline_dates,
    check_world,
    format_report_text,
)


class TestWorldDoctor(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.bible = self.base / "00-World-Bible"
        self.bible.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_frontmatter(self):
        text = """---
name: Alden Vance
type: character
aliases: [The Shadowblade, Alden]
faction: "[[The Obsidian Vanguard]]"
---
# Alden Vance
A sworn warrior.
"""
        fm, ok = parse_frontmatter(text)
        self.assertTrue(ok)
        self.assertEqual(fm["name"], "Alden Vance")
        self.assertEqual(fm["type"], "character")
        self.assertEqual(fm["aliases"], ["The Shadowblade", "Alden"])
        self.assertEqual(fm["faction"], "[[The Obsidian Vanguard]]")

    def test_parse_timeline_dates(self):
        # BCE / CE
        self.assertEqual(parse_timeline_date("500 BCE")[1], -500.0)
        self.assertEqual(parse_timeline_date("1422 CE")[1], 1422.0)
        
        # Ordinal Eras (1E, 2E, 3E)
        p1 = parse_timeline_date("1422 3E")
        self.assertEqual(p1[0], "3e")
        self.assertEqual(p1[1], 1422.0)

        # Date comparisons
        self.assertEqual(compare_timeline_dates("500 BCE", "100 CE"), -1)
        self.assertEqual(compare_timeline_dates("100 2E", "50 3E"), -1)
        self.assertEqual(compare_timeline_dates("1422 3E", "1000 3E"), 1)

    def test_check_world_consistency_and_broken_links(self):
        # Create character note with link to missing faction and missing location
        char_file = self.bible / "Characters" / "Alden.md"
        char_file.parent.mkdir(parents=True, exist_ok=True)
        char_file.write_text("""---
name: Alden
type: character
faction: "[[The Night Guild]]"
---
Alden went to [[The Lost Citadel]] to find [[Kaelen]].
""", encoding="utf-8")

        # Create Kaelen note
        kaelen_file = self.bible / "Characters" / "Kaelen.md"
        kaelen_file.write_text("""---
name: Kaelen
type: character
---
Kaelen waits for [[Alden]].
""", encoding="utf-8")

        findings = check_world(str(self.bible))
        self.assertEqual(findings["notes"], 2)
        
        # Lost Citadel is broken link
        broken_missing = [b["missing"] for b in findings["broken_links"]]
        self.assertIn("The Lost Citadel", broken_missing)
        self.assertNotIn("Kaelen", broken_missing)

        # Night Guild is dangling frontmatter ref
        dangling_missing = [d["missing"] for d in findings["dangling_frontmatter_refs"]]
        self.assertIn("The Night Guild", dangling_missing)

        # Test report text formatter
        text_rep = format_report_text(findings)
        self.assertIn("Broken wiki-links [WLD-101]", text_rep)
        self.assertIn("The Lost Citadel", text_rep)

    def test_timeline_error_detection(self):
        char_file = self.bible / "Characters" / "Lord_Vane.md"
        char_file.parent.mkdir(parents=True, exist_ok=True)
        char_file.write_text("""---
name: Lord Vane
type: character
birth_year: 1450 CE
death_year: 1410 CE
---
An immortal lord whose death preceded his birth.
""", encoding="utf-8")

        findings = check_world(str(self.bible))
        self.assertEqual(len(findings["timeline_errors"]), 1)
        self.assertIn("Death year", findings["timeline_errors"][0]["issue"])


if __name__ == "__main__":
    unittest.main()
