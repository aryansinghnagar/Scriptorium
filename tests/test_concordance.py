#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Concordance & Back-Matter Engine (scripts/lib/concordance.py).
Validates:
- Frontmatter and body parsing, wikilink scrubbing.
- Template file exclusion (`is_template`).
- Dramatis Personae markdown synthesis with Protagonist, Antagonist, and Supporting sections.
- Glossary and Concordance markdown generation (Factions, Artifacts, Magic, Creatures, Languages).
- End-to-end `generate_concordance` across World Bible dossiers and Manuscript volumes.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.concordance import (
    build_dramatis_personae_markdown,
    build_glossary_markdown,
    clean_wikilinks,
    extract_summary_or_quote,
    generate_concordance,
    is_template,
    parse_frontmatter_and_body,
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

    # ------------------------------------------------------------------ #
    # 1. Wikilink Cleaning                                                #
    # ------------------------------------------------------------------ #
    def test_clean_wikilinks(self):
        """clean_wikilinks must strip brackets and handle pipe aliases properly."""
        self.assertEqual(clean_wikilinks("[[Alden Vance|Alden]]"), "Alden")
        self.assertEqual(clean_wikilinks("[[Obsidian Citadel]]"), "Obsidian Citadel")
        self.assertEqual(clean_wikilinks("Plain Text"), "Plain Text")
        self.assertEqual(clean_wikilinks(None), "")

    # ------------------------------------------------------------------ #
    # 2. Template Detection                                              #
    # ------------------------------------------------------------------ #
    def test_is_template_detection(self):
        """is_template must flag files with Template in name or <% in frontmatter."""
        self.assertTrue(is_template(Path("Templates/Char_Template.md"), {}))
        self.assertTrue(is_template(Path("Characters/Template_Hero.md"), {}))
        self.assertTrue(is_template(Path("Characters/Hero.md"), {"name": "<% tp.file.title %>"}))
        self.assertFalse(is_template(Path("Characters/Hero.md"), {"name": "Kaelen"}))

    # ------------------------------------------------------------------ #
    # 3. Frontmatter and Body Parsing                                    #
    # ------------------------------------------------------------------ #
    def test_parse_frontmatter_and_body(self):
        """parse_frontmatter_and_body must extract YAML dict and body markdown."""
        f = self.base / "test_doc.md"
        f.write_text("""---
name: "Kaelen"
role: "Protagonist"
aliases:
  - "Shadow"
  - "Blade"
---
# Heading
This is the body content.
""", encoding="utf-8")
        fm, body = parse_frontmatter_and_body(f)
        self.assertEqual(fm.get("name"), "Kaelen")
        self.assertEqual(fm.get("role"), "Protagonist")
        self.assertEqual(fm.get("aliases"), ["Shadow", "Blade"])
        self.assertIn("This is the body content.", body)

    # ------------------------------------------------------------------ #
    # 4. Summary and Quote Extraction                                    #
    # ------------------------------------------------------------------ #
    def test_extract_summary_or_quote(self):
        """extract_summary_or_quote must find ## Summary section or fallback quote."""
        body = """
> "The night belongs to the brave."

## Summary
The master scribe of the Sun Citadel.
"""
        summary = extract_summary_or_quote(body)
        self.assertIn("The master scribe of the Sun Citadel.", summary)

    # ------------------------------------------------------------------ #
    # 5. Dramatis Personae Section Grouping                              #
    # ------------------------------------------------------------------ #
    def test_build_dramatis_personae_markdown_groups(self):
        """Dramatis Personae must group characters into Protagonists, Antagonists, and Supporting."""
        chars = [
            {"name": "Hero Vance", "role": "Protagonist", "species": "Human", "summary": "The main champion."},
            {"name": "Darth Malakar", "role": "Antagonist / Villain", "species": "Eldritch", "summary": "The nemesis."},
            {"name": "Sage Elion", "role": "Supporting / Mentor", "species": "Elf", "summary": "The guide."},
        ]
        dp_text = build_dramatis_personae_markdown(chars)
        self.assertIn("## Protagonists & Major Figures", dp_text)
        self.assertIn("## Antagonists & Rivals", dp_text)
        self.assertIn("## Supporting Personae & Affiliations", dp_text)
        self.assertIn("Hero Vance", dp_text)
        self.assertIn("Darth Malakar", dp_text)
        self.assertIn("Sage Elion", dp_text)

    # ------------------------------------------------------------------ #
    # 6. Dramatis Personae Empty Roster                                  #
    # ------------------------------------------------------------------ #
    def test_build_dramatis_personae_empty(self):
        """Dramatis Personae with empty list must include notice."""
        dp_text = build_dramatis_personae_markdown([])
        self.assertIn("No character dossiers registered", dp_text)

    # ------------------------------------------------------------------ #
    # 7. Glossary Markdown Categories                                    #
    # ------------------------------------------------------------------ #
    def test_build_glossary_markdown_categories(self):
        """build_glossary_markdown must render factions, relics, magic, and creatures."""
        factions = [{"name": "Iron Guild", "type": "Syndicate", "motto": "Iron Binds All", "summary": "Blacksmith cartel."}]
        artifacts = [{"name": "Sunstone Ring", "rarity": "Legendary", "bearer": "Hero", "summary": "Glows in darkness."}]
        magic = [{"name": "Aether-Weaving", "classification": "Hard Magic", "source": "Starlight", "summary": "Light manipulation."}]
        creatures = [{"name": "Shadow Drake", "threat": "Extreme", "habitat": "Volcanic Spires", "summary": "Winged horror."}]
        languages = [{"name": "High Valyrian", "speakers": "Nobility", "summary": "Ancient tongue."}]

        gc_text = build_glossary_markdown(factions, artifacts, magic, creatures, languages)
        self.assertIn("## Factions & Sovereign Powers", gc_text)
        self.assertIn("Iron Guild", gc_text)
        self.assertIn("## Legendary Artifacts & Relics", gc_text)
        self.assertIn("Sunstone Ring", gc_text)
        self.assertIn("## Magic & Arcane Disciplines", gc_text)
        self.assertIn("Aether-Weaving", gc_text)
        self.assertIn("## Bestiary & Ecological Hazards", gc_text)
        self.assertIn("Shadow Drake", gc_text)

    # ------------------------------------------------------------------ #
    # 8. End-to-End Concordance Generation                               #
    # ------------------------------------------------------------------ #
    def test_build_dramatis_personae_and_glossary(self):
        """End-to-end generate_concordance must write files to 04_Back_Matter."""
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

    # ------------------------------------------------------------------ #
    # 9. Artifact and Bestiary In-Vault Discovery                         #
    # ------------------------------------------------------------------ #
    def test_artifact_and_bestiary_discovery(self):
        """generate_concordance must scan Artifacts/ and Bestiary/ folders."""
        art_dir = self.bible / "Artifacts"
        art_dir.mkdir(parents=True)
        (art_dir / "Crown.md").write_text("""---
name: Crown of Sol
type: Regalia
rarity: Unique
---
## Description
The golden circlet of ancient monarchs.
""", encoding="utf-8")

        best_dir = self.bible / "Bestiary"
        best_dir.mkdir(parents=True)
        (best_dir / "Wyrm.md").write_text("""---
name: Frost Wyrm
threat: Lethal
habitat: Glacial Caverns
---
## Overview
A colossal subterranean serpent of living ice.
""", encoding="utf-8")

        res = generate_concordance(bible_dir=self.bible, ms_dir=self.ms, target_book="Book-01")
        self.assertEqual(res["artifacts_count"], 1)
        self.assertEqual(res["creatures_count"], 1)

        gc_file = self.ms / "Book-01" / "04_Back_Matter" / "02_Glossary_and_Concordance.md"
        gc_text = gc_file.read_text(encoding="utf-8")
        self.assertIn("Crown of Sol", gc_text)
        self.assertIn("Frost Wyrm", gc_text)

    # ------------------------------------------------------------------ #
    # 10. Magic System and Conlang Discovery                             #
    # ------------------------------------------------------------------ #
    def test_magic_and_language_discovery(self):
        """generate_concordance must scan Magic-Technology/ and Languages/ dossiers."""
        mag_dir = self.bible / "Magic-Technology"
        mag_dir.mkdir(parents=True)
        (mag_dir / "Pyromancy.md").write_text("""---
name: Solar Pyromancy
classification: Elemental
source: Sun Core
---
## Summary
The disciplined manipulation of raw solar heat.
""", encoding="utf-8")

        lang_dir = self.bible / "Languages"
        lang_dir.mkdir(parents=True)
        (lang_dir / "Elder.md").write_text("""---
name: Elder Tongue
speakers: Archons
---
## Overview
The liturgical language of the ancient scribes.
""", encoding="utf-8")

        res = generate_concordance(bible_dir=self.bible, ms_dir=self.ms, target_book="Book-01")
        self.assertEqual(res["magic_systems_count"], 1)
        self.assertEqual(res["languages_count"], 1)

        gc_file = self.ms / "Book-01" / "04_Back_Matter" / "02_Glossary_and_Concordance.md"
        gc_text = gc_file.read_text(encoding="utf-8")
        self.assertIn("Solar Pyromancy", gc_text)
        self.assertIn("Elder Tongue", gc_text)

    # ------------------------------------------------------------------ #
    # 11. Multi-Volume Target Update                                     #
    # ------------------------------------------------------------------ #
    def test_generate_concordance_all_volumes(self):
        """generate_concordance target_book='all' must update multiple volume folders."""
        (self.ms / "Book-01" / "01_Act_I").mkdir(parents=True)
        (self.ms / "Book-02" / "01_Act_I").mkdir(parents=True)

        res = generate_concordance(bible_dir=self.bible, ms_dir=self.ms, target_book="all")
        self.assertEqual(res["volumes_updated"], 2)

        self.assertTrue((self.ms / "Book-01" / "04_Back_Matter" / "01_Dramatis_Personae.md").exists())
        self.assertTrue((self.ms / "Book-02" / "04_Back_Matter" / "01_Dramatis_Personae.md").exists())

    # ------------------------------------------------------------------ #
    # 12. Empty Bible Graceful Handling                                  #
    # ------------------------------------------------------------------ #
    def test_empty_bible_graceful_handling(self):
        """generate_concordance with empty bible must succeed and report 0 entities."""
        res = generate_concordance(bible_dir=self.bible, ms_dir=self.ms, target_book="Book-01")
        self.assertEqual(res["characters_count"], 0)
        self.assertEqual(res["factions_count"], 0)
        self.assertEqual(res["volumes_updated"], 1)
        dp_file = self.ms / "Book-01" / "04_Back_Matter" / "01_Dramatis_Personae.md"
        self.assertTrue(dp_file.exists())


if __name__ == "__main__":
    unittest.main()
