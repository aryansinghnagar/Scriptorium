#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Concordance Engine (scripts/lib/concordance.py)
"""

import unittest
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.concordance import (
    clean_wikilinks,
    parse_frontmatter_and_body,
    extract_summary_or_quote,
    build_dramatis_personae_markdown,
    build_glossary_markdown,
    generate_concordance,
)


class TestConcordance(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.bible = self.base / "00-World-Bible"
        self.bible.mkdir(parents=True)
        self.ms = self.base / "01-Manuscript"
        self.ms.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_wikilinks(self):
        self.assertEqual(clean_wikilinks("[[Alden Vance|Alden]]"), "Alden")
        self.assertEqual(clean_wikilinks("[[Obsidian Citadel]]"), "Obsidian Citadel")
        self.assertEqual(clean_wikilinks("Plain Text"), "Plain Text")

    def test_build_dramatis_personae_and_glossary(self):
        # Setup Character
        char_dir = self.bible / "Characters"
        char_dir.mkdir(parents=True)
        (char_dir / "Alden.md").write_text("""---
name: Alden Vance
role: Protagonist
aliases: [The Shadowblade]
faction: "[[The Obsidian Order]]"
---
## Summary
A retired vanguard commander drawn back into conflict.
""", encoding="utf-8")

        # Setup Faction
        fac_dir = self.bible / "Factions"
        fac_dir.mkdir(parents=True)
        (fac_dir / "Obsidian_Order.md").write_text("""---
name: The Obsidian Order
faction_type: Sovereign Military
leader: "[[High Justiciar Vane]]"
motto: "In Silence We Endure"
---
## Overview
The elite guardians of the high spires.
""", encoding="utf-8")

        res = generate_concordance(
            bible_dir=self.bible,
            ms_dir=self.ms,
            target_book="Book-01",
        )

        self.assertEqual(res["characters_count"], 1)
        self.assertEqual(res["factions_count"], 1)
        self.assertEqual(res["volumes_updated"], 1)

        dp_file = self.ms / "Book-01" / "04_Back_Matter" / "01_Dramatis_Personae.md"
        gc_file = self.ms / "Book-01" / "04_Back_Matter" / "02_Glossary_and_Concordance.md"

        self.assertTrue(dp_file.exists())
        self.assertTrue(gc_file.exists())

        dp_text = dp_file.read_text(encoding="utf-8")
        self.assertIn("Alden Vance", dp_text)
        self.assertIn("The Shadowblade", dp_text)
        self.assertIn("A retired vanguard commander", dp_text)

        gc_text = gc_file.read_text(encoding="utf-8")
        self.assertIn("The Obsidian Order", gc_text)
        self.assertIn("In Silence We Endure", gc_text)


if __name__ == "__main__":
    unittest.main()
