#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Multi-Volume Dramatis Personae & Universe Cast Matrix
(scripts/lib/dramatis_personae.py).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.dramatis_personae import (
    AppearanceRecord,
    CharacterProfile,
    cross_reference_manuscripts,
    generate_dramatis_personae_html,
    generate_dramatis_personae_markdown,
    main,
    normalize_name,
    scan_character_profiles,
)


class TestDramatisPersonae(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.world_dir = self.root / "World"
        self.chars_dir = self.world_dir / "Characters"
        self.ms_dir = self.root / "Manuscripts"

        self.chars_dir.mkdir(parents=True, exist_ok=True)
        self.ms_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_scan_empty_world_no_crash(self) -> None:
        """Scanning a non-existent or empty world directory returns an empty dict without crashing."""
        chars = scan_character_profiles(self.root / "NonExistent")
        self.assertEqual(chars, {})
        empty_chars = scan_character_profiles(self.world_dir)
        self.assertEqual(empty_chars, {})

    def test_scan_character_profile_fields(self) -> None:
        """Parsing character dossiers correctly extracts metadata fields."""
        char_file = self.chars_dir / "Kaelen_Vane.md"
        char_file.write_text(
            """---
name: Kaelen Vane
aliases:
  - The Ghostblade
  - Shade of Oakhaven
role: Major Protagonist
status: Active
faction: Silver Concordat
origin: High Vale
---
# Kaelen Vane
Master swordsman of the northern reaches.
""",
            encoding="utf-8",
        )

        chars = scan_character_profiles(self.world_dir)
        norm_key = normalize_name("Kaelen Vane")
        self.assertIn(norm_key, chars)
        prof = chars[norm_key]

        self.assertEqual(prof.name, "Kaelen Vane")
        self.assertIn("The Ghostblade", prof.aliases)
        self.assertIn("Shade of Oakhaven", prof.aliases)
        self.assertEqual(prof.category, "Major")
        self.assertEqual(prof.role, "Major Protagonist")
        self.assertEqual(prof.status, "Active")
        self.assertEqual(prof.faction, "Silver Concordat")
        self.assertEqual(prof.origin, "High Vale")
        self.assertTrue(prof.lore_file.endswith("Kaelen_Vane.md"))

    def test_alias_resolution_in_manuscript(self) -> None:
        """Mentions using an alias resolve to the canonical character profile."""
        char_file = self.chars_dir / "Kaelen.md"
        char_file.write_text(
            """---
name: Kaelen
aliases: [The Ghostblade]
---
""",
            encoding="utf-8",
        )
        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        scene = vol1 / "Chapter-01.md"
        scene.write_text(
            """---
title: The Arrival
---
@char: The Ghostblade
The cloaked warrior stood in silence.
""",
            encoding="utf-8",
        )

        chars = scan_character_profiles(self.world_dir)
        updated_chars, _ = cross_reference_manuscripts(chars, self.ms_dir)

        norm_key = normalize_name("Kaelen")
        prof = updated_chars[norm_key]
        self.assertEqual(prof.total_appearances, 1)
        self.assertEqual(prof.appearances[0].chapter, "Chapter-01.md")
        self.assertEqual(prof.appearances[0].volume, "Book-01")

    def test_pov_count_incremented(self) -> None:
        """Scenes with @pov: tags increment character pov_count and appearance count."""
        char_file = self.chars_dir / "Elena.md"
        char_file.write_text("---\nname: Elena\nrole: Protagonist\n---\n", encoding="utf-8")

        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        ch1 = vol1 / "Chapter-01.md"
        ch1.write_text("@pov: Elena\nElena surveyed the citadel.\n", encoding="utf-8")
        ch2 = vol1 / "Chapter-02.md"
        ch2.write_text("---\npov: Elena\n---\nElena drew her sword.\n", encoding="utf-8")

        chars = scan_character_profiles(self.world_dir)
        updated_chars, _ = cross_reference_manuscripts(chars, self.ms_dir)

        prof = updated_chars[normalize_name("Elena")]
        self.assertEqual(prof.pov_count, 2)
        self.assertEqual(prof.total_appearances, 2)

    def test_first_and_last_appearance_tracked(self) -> None:
        """First and last appearances are correctly recorded across sequential chapters."""
        char_file = self.chars_dir / "Marcus.md"
        char_file.write_text("---\nname: Marcus\n---\n", encoding="utf-8")

        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        (vol1 / "Chapter-01.md").write_text("@char: Marcus\nIntroduction.", encoding="utf-8")
        (vol1 / "Chapter-02.md").write_text("@char: Marcus\nMiddle.", encoding="utf-8")
        (vol1 / "Chapter-03.md").write_text("@char: Marcus\nConclusion.", encoding="utf-8")

        chars = scan_character_profiles(self.world_dir)
        updated_chars, _ = cross_reference_manuscripts(chars, self.ms_dir)

        prof = updated_chars[normalize_name("Marcus")]
        self.assertEqual(prof.first_appearance, "Book-01 / Chapter-01.md")
        self.assertEqual(prof.last_appearance, "Book-01 / Chapter-03.md")
        self.assertEqual(prof.total_appearances, 3)

    def test_ghost_character_cas101(self) -> None:
        """Untracked character mentioned in manuscript triggers CAS-101 warning."""
        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        (vol1 / "Chapter-01.md").write_text("@char: Lord Vane\nA mysterious figure.", encoding="utf-8")

        chars = scan_character_profiles(self.world_dir)
        _, findings = cross_reference_manuscripts(chars, self.ms_dir)

        cas101 = [f for f in findings if f["id"] == "CAS-101"]
        self.assertTrue(len(cas101) >= 1)
        self.assertEqual(cas101[0]["character"], "Lord Vane")
        self.assertEqual(cas101[0]["severity"], "WARNING")

    def test_orphan_character_cas103(self) -> None:
        """Character with lore profile but 0 manuscript mentions triggers CAS-103 info."""
        (self.chars_dir / "Forgotten_Hero.md").write_text("---\nname: Forgotten Hero\n---\n", encoding="utf-8")

        chars = scan_character_profiles(self.world_dir)
        _, findings = cross_reference_manuscripts(chars, self.ms_dir)

        cas103 = [f for f in findings if f["id"] == "CAS-103"]
        self.assertEqual(len(cas103), 1)
        self.assertEqual(cas103[0]["character"], "Forgotten Hero")
        self.assertEqual(cas103[0]["severity"], "INFO")

    def test_post_mortem_action_cas102(self) -> None:
        """Character acting after their death event triggers CAS-102 error."""
        (self.chars_dir / "Boromir.md").write_text("---\nname: Boromir\n---\n", encoding="utf-8")

        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        (vol1 / "Chapter-01.md").write_text("@char: Boromir\nBoromir fights valiantly.", encoding="utf-8")
        (vol1 / "Chapter-02.md").write_text("@death: Boromir\nBoromir falls in battle.", encoding="utf-8")
        (vol1 / "Chapter-03.md").write_text("@char: Boromir\nBoromir orders another round at the tavern.", encoding="utf-8")

        chars = scan_character_profiles(self.world_dir)
        updated_chars, findings = cross_reference_manuscripts(chars, self.ms_dir)

        prof = updated_chars[normalize_name("Boromir")]
        self.assertEqual(prof.status, "Deceased")
        self.assertEqual(prof.death_chapter, "Book-01 / Chapter-02.md")

        cas102 = [f for f in findings if f["id"] == "CAS-102"]
        self.assertEqual(len(cas102), 1)
        self.assertEqual(cas102[0]["character"], "Boromir")
        self.assertEqual(cas102[0]["severity"], "ERROR")

    def test_generate_markdown_appendix(self) -> None:
        """Markdown Dramatis Personae contains proper headers, tables, and faction groupings."""
        prof1 = CharacterProfile(
            id="kaelen",
            name="Kaelen Vane",
            role="Captain",
            status="Active",
            faction="Silver Concordat",
            origin="High Vale",
            first_appearance="Book-01 / Chapter-01.md",
            pov_count=3,
        )
        prof2 = CharacterProfile(
            id="morrigan",
            name="Morrigan",
            role="Sorceress",
            status="Deceased",
            faction="Eclipse Coven",
            origin="Abyssal Gate",
            first_appearance="Book-01 / Chapter-05.md",
            pov_count=0,
        )

        md = generate_dramatis_personae_markdown([prof1, prof2], title="Cast of Characters")
        self.assertIn("# Cast of Characters", md)
        self.assertIn("## Silver Concordat", md)
        self.assertIn("## Eclipse Coven", md)
        self.assertIn("| **Kaelen Vane** | Captain | 🟢 Active | High Vale | Book-01 / Chapter-01.md | ✓ |", md)
        self.assertIn("| **Morrigan** | Sorceress | 🔴 Deceased | Abyssal Gate | Book-01 / Chapter-05.md | — |", md)

    def test_generate_html_gallery_exists(self) -> None:
        """HTML gallery file is generated and contains character names and metadata."""
        prof = CharacterProfile(
            id="kaelen",
            name="Kaelen Vane",
            aliases=["The Ghostblade"],
            role="Captain",
            status="Active",
            faction="Silver Concordat",
            origin="High Vale",
            first_appearance="Book-01 / Chapter-01.md",
            last_appearance="Book-01 / Chapter-10.md",
            total_appearances=5,
            pov_count=2,
        )
        out_html = self.root / "gallery.html"
        generate_dramatis_personae_html(
            {"universe": "Aethelgard", "characters": [prof], "findings": []},
            out_html,
        )

        self.assertTrue(out_html.exists())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Kaelen Vane", content)
        self.assertIn("The Ghostblade", content)
        self.assertIn("Silver Concordat", content)
        self.assertIn("Aethelgard", content)

    def test_html_csp_compliance(self) -> None:
        """HTML gallery enforces strict offline Content-Security-Policy."""
        out_html = self.root / "csp_test.html"
        generate_dramatis_personae_html(
            {"universe": "Test", "characters": [], "findings": []},
            out_html,
        )
        content = out_html.read_text(encoding="utf-8")
        self.assertIn(
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; img-src data:; media-src data: blob:;">',
            content,
        )

    def test_multi_volume_series_support(self) -> None:
        """Appearances across multiple book subdirectories are cleanly partitioned and aggregated."""
        (self.chars_dir / "Aria.md").write_text("---\nname: Aria\n---\n", encoding="utf-8")

        b1 = self.ms_dir / "Book-01-Dawn"
        b2 = self.ms_dir / "Book-02-Dusk"
        b1.mkdir(parents=True, exist_ok=True)
        b2.mkdir(parents=True, exist_ok=True)

        (b1 / "Chapter-01.md").write_text("@char: Aria\nBook 1 start.", encoding="utf-8")
        (b2 / "Chapter-12.md").write_text("@char: Aria\nBook 2 climax.", encoding="utf-8")

        chars = scan_character_profiles(self.world_dir)
        updated_chars, _ = cross_reference_manuscripts(chars, self.ms_dir)

        prof = updated_chars[normalize_name("Aria")]
        self.assertEqual(prof.total_appearances, 2)
        vols = {app.volume for app in prof.appearances}
        self.assertEqual(vols, {"Book-01-Dawn", "Book-02-Dusk"})
        self.assertEqual(prof.first_appearance, "Book-01-Dawn / Chapter-01.md")
        self.assertEqual(prof.last_appearance, "Book-02-Dusk / Chapter-12.md")

    def test_frontmatter_cast_list_parsed(self) -> None:
        """Frontmatter characters/chars/cast list fields are parsed alongside inline tags."""
        (self.chars_dir / "Garrick.md").write_text("---\nname: Garrick\n---\n", encoding="utf-8")
        (self.chars_dir / "Lyra.md").write_text("---\nname: Lyra\n---\n", encoding="utf-8")

        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        (vol1 / "Chapter-01.md").write_text(
            """---
title: Council of War
characters:
  - Garrick
  - Lyra
---
The council convened.
""",
            encoding="utf-8",
        )

        chars = scan_character_profiles(self.world_dir)
        updated_chars, _ = cross_reference_manuscripts(chars, self.ms_dir)

        self.assertEqual(updated_chars[normalize_name("Garrick")].total_appearances, 1)
        self.assertEqual(updated_chars[normalize_name("Lyra")].total_appearances, 1)

    def test_character_profile_serialization(self) -> None:
        """CharacterProfile objects serialize cleanly to dict and JSON round-trip."""
        app = AppearanceRecord(volume="Book-01", chapter="Ch01.md", is_pov=True, is_death_event=False)
        prof = CharacterProfile(
            id="test-char",
            name="Test Character",
            aliases=["Tester"],
            category="Major",
            role="Protagonist",
            status="Active",
            faction="Guild",
            origin="Capital",
            appearances=[app],
        )

        d = prof.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["name"], "Test Character")
        self.assertEqual(len(d["appearances"]), 1)
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["id"], "test-char")

    def test_cli_main_dramatis_personae(self) -> None:
        """CLI main function executes and writes markdown/HTML artifacts and outputs JSON."""
        (self.chars_dir / "Kaelen.md").write_text("---\nname: Kaelen\nrole: Major Protagonist\n---\n", encoding="utf-8")
        vol1 = self.ms_dir / "Book-01"
        vol1.mkdir(parents=True, exist_ok=True)
        (vol1 / "Chapter-01.md").write_text("@char: Kaelen\nScene 1", encoding="utf-8")

        out_md = self.root / "cast.md"
        out_html = self.root / "cast.html"

        exit_code = main([
            str(self.root),
            "--markdown",
            str(out_md),
            "--html",
            str(out_html),
            "--json",
        ])
        self.assertEqual(exit_code, 0)
        self.assertTrue(out_md.exists())
        self.assertTrue(out_html.exists())
        self.assertIn("Kaelen", out_md.read_text(encoding="utf-8"))
        self.assertIn("Kaelen", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
