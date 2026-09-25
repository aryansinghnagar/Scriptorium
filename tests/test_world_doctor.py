#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum World Doctor (scripts/lib/world_doctor.py)
"""

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.world_doctor import (
    check_world,
    compare_timeline_dates,
    format_report_text,
    main as doctor_main,
    parse_frontmatter,
    parse_timeline_date,
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

    def test_parse_frontmatter_invalid_syntax(self):
        """Verifies unclosed frontmatter delimiters return ok=False."""
        unclosed = "---\nname: Unclosed Item\ntype: character\nNo closing delimiter"
        _fm, ok = parse_frontmatter(unclosed)
        self.assertFalse(ok)

    def test_missing_required_field_wld103(self):
        """Verifies character without name field triggers WLD-103."""
        no_name_file = self.bible / "Characters" / "Nameless.md"
        no_name_file.parent.mkdir(parents=True, exist_ok=True)
        no_name_file.write_text("""---
type: character
faction: "[[The Guild]]"
---
A nameless ghost.
""", encoding="utf-8")

        findings = check_world(str(self.bible))
        missing_fields = [m["field"] for m in findings["missing_required_fields"]]
        self.assertIn("name", missing_fields)

    def test_duplicate_identity_wld105(self):
        """Verifies identical names in different files trigger WLD-105."""
        char1 = self.bible / "Characters" / "Valerius_Prime.md"
        char1.parent.mkdir(parents=True, exist_ok=True)
        char1.write_text("""---
name: Valerius
type: character
---
Original Valerius.
""", encoding="utf-8")

        char2 = self.bible / "Characters" / "Valerius_Clone.md"
        char2.write_text("""---
name: Valerius
type: character
---
Clone Valerius.
""", encoding="utf-8")

        findings = check_world(str(self.bible))
        self.assertGreaterEqual(len(findings["duplicate_identities"]), 1)
        self.assertEqual(findings["duplicate_identities"][0]["code"], "WLD-105")

    def test_orphaned_lore_note_wld107(self):
        """Verifies unlinked note is detected as orphan WLD-107."""
        orphan = self.bible / "Locations" / "Forgotten_Isle.md"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("""---
name: Forgotten Isle
type: location
---
Isolated island with zero incoming or outgoing connections.
""", encoding="utf-8")

        findings = check_world(str(self.bible))
        orphan_files = [o["file"] for o in findings["orphans"]]
        self.assertTrue(any("Forgotten_Isle" in f for f in orphan_files))

    def test_manuscript_drift_wld108(self):
        """Verifies manuscript referencing nonexistent world entities triggers WLD-108."""
        # Clean character in world
        char = self.bible / "Characters" / "Theron.md"
        char.parent.mkdir(parents=True, exist_ok=True)
        char.write_text("""---
name: Archmage Theron
type: character
---
The high mage.
""", encoding="utf-8")

        # Manuscript mentioning nonexistent character
        ms_dir = self.base / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "01_Chap.md").write_text("""---
title: Chapter 1
---
@pov: UnknownGhost
@location: HighCitadel

Archmage [[Theron]] met with [[NonexistentHero]].
""", encoding="utf-8")

        findings = check_world(str(self.bible), manuscript_dir=str(ms_dir))
        drift_missing = [d["missing"] for d in findings["manuscript_name_drift"]]
        self.assertTrue(any("NonexistentHero" in m or "UnknownGhost" in m for m in drift_missing))

    def test_clean_world_zero_findings(self):
        """Verifies a fully cross-referenced World Bible produces 0 critical findings."""
        char = self.bible / "Characters" / "Aeloria.md"
        char.parent.mkdir(parents=True, exist_ok=True)
        char.write_text("""---
name: Aeloria
type: character
faction: "[[Silver Dawn]]"
current_location: "[[High Sanctuary]]"
---
Hero of the [[Silver Dawn]] at [[High Sanctuary]].
""", encoding="utf-8")

        fac = self.bible / "Factions" / "Silver_Dawn.md"
        fac.parent.mkdir(parents=True, exist_ok=True)
        fac.write_text("""---
name: Silver Dawn
type: faction
---
Order led by [[Aeloria]] in [[High Sanctuary]].
""", encoding="utf-8")

        loc = self.bible / "Locations" / "High_Sanctuary.md"
        loc.parent.mkdir(parents=True, exist_ok=True)
        loc.write_text("""---
name: High Sanctuary
type: location
---
Citadel guarded by [[Aeloria]] and [[Silver Dawn]].
""", encoding="utf-8")

        findings = check_world(str(self.bible))
        self.assertEqual(len(findings["broken_links"]), 0)
        self.assertEqual(len(findings["dangling_frontmatter_refs"]), 0)
        self.assertEqual(len(findings["timeline_errors"]), 0)

    def test_compare_timeline_dates_multi_era(self):
        """Verifies multi-era timeline comparisons across BCE/CE and numbered eras."""
        # 1st Era vs 2nd Era
        self.assertEqual(compare_timeline_dates("500 1E", "100 2E"), -1)
        self.assertEqual(compare_timeline_dates("300 2E", "100 1E"), 1)
        # Same Era ordering
        self.assertEqual(compare_timeline_dates("100 3E", "200 3E"), -1)
        self.assertEqual(compare_timeline_dates("200 3E", "200 3E"), 0)

    def test_cli_world_doctor_execution(self):
        """Verifies CLI execution with --json and directory path arguments."""
        char = self.bible / "Characters" / "Alden.md"
        char.parent.mkdir(parents=True, exist_ok=True)
        char.write_text("""---
name: Alden
type: character
---
A simple knight.
""", encoding="utf-8")

        stdout_buf = StringIO()
        with patch("sys.stdout", stdout_buf):
            code = doctor_main([str(self.bible), "--json"])
            self.assertIn(code, (0, 1))

        output = stdout_buf.getvalue()
        data = json.loads(output)
        self.assertIn("world", data)
        self.assertIn("notes", data)


if __name__ == "__main__":
    unittest.main()
