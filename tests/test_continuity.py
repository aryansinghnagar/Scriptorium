#!/usr/bin/env python3
"""
Unit tests for Scriptorium Narrative Continuity Engine (scripts/lib/continuity.py).
Covers trait normalization, inline regex trait extraction, lore bible profiling,
lore trait contradiction detection (CNT-101), and inter-scene drift (CNT-102).
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.continuity import (  # noqa: E402
    normalize_trait,
    extract_traits_from_text,
    extract_lore_profiles,
    scan_manuscript_scenes,
    run_continuity_audit,
)


class TestContinuityEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)
        self.world_dir = self.root_path / "World"
        self.manuscript_dir = self.root_path / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.manuscript_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_normalize_trait(self):
        self.assertEqual(normalize_trait("eye_color", "sapphire"), "blue")
        self.assertEqual(normalize_trait("eye_color", "emerald"), "green")
        self.assertEqual(normalize_trait("eye_color", "dark"), "brown")
        self.assertEqual(normalize_trait("hair_color", "raven"), "black")
        self.assertEqual(normalize_trait("hair_color", "golden"), "blonde")
        self.assertEqual(normalize_trait("hair_color", "auburn"), "red")
        self.assertEqual(normalize_trait("status", "deceased"), "deceased")
        self.assertEqual(normalize_trait("status", "alive"), "alive")

    def test_extract_traits_from_text(self):
        text = "Her piercing blue eyes searched the room. His raven hair glistened in the rain."
        traits = extract_traits_from_text(text)
        self.assertIn("eye_color", traits)
        self.assertIn("blue", traits["eye_color"])
        self.assertIn("hair_color", traits)
        self.assertIn("black", traits["hair_color"])

    def test_extract_lore_profiles(self):
        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True)

        char_file = chars_dir / "Renée.md"
        char_file.write_text("""---
name: "Renée d'Anjou"
type: character
eyes: emerald
hair: raven
---
# Renée d'Anjou
The knight commander of the realm.
""", encoding="utf-8")

        profiles = extract_lore_profiles(self.world_dir)
        self.assertIn("Renée d'Anjou", profiles)
        self.assertIn("green", profiles["Renée d'Anjou"]["traits"].get("eye_color", []))
        self.assertIn("black", profiles["Renée d'Anjou"]["traits"].get("hair_color", []))

    def test_scan_manuscript_clean(self):
        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True)
        (chars_dir / "Kael.md").write_text("""---
name: "Kael"
type: character
---
Kael had piercing blue eyes and dark hair.
""", encoding="utf-8")

        scene_file = self.manuscript_dir / "01_Chapter_01.md"
        scene_file.write_text("""# Chapter 1
@pov: Kael

Kael entered the quiet hall. His blue eyes scanned the shadows.
""", encoding="utf-8")

        profiles = extract_lore_profiles(self.world_dir)
        findings = scan_manuscript_scenes(self.manuscript_dir, profiles)
        self.assertEqual(len(findings), 0)

    def test_scan_manuscript_lore_contradiction_cnt101(self):
        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True)
        (chars_dir / "Kael.md").write_text("""---
name: "Kael"
type: character
---
Kael had brilliant blue eyes.
""", encoding="utf-8")

        scene_file = self.manuscript_dir / "01_Chapter_01.md"
        scene_file.write_text("""# Chapter 1
@pov: Kael

Kael stood at the edge of the cliff. His emerald eyes gleamed under the sun.
""", encoding="utf-8")

        profiles = extract_lore_profiles(self.world_dir)
        findings = scan_manuscript_scenes(self.manuscript_dir, profiles)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["id"], "CNT-101")
        self.assertEqual(findings[0]["entity"], "Kael")
        self.assertEqual(findings[0]["trait"], "eye_color")
        self.assertEqual(findings[0]["expected"], "blue")
        self.assertEqual(findings[0]["found"], "green")

    def test_scan_manuscript_interscene_drift_cnt102(self):
        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True)
        (chars_dir / "Elena.md").write_text("""---
name: "Elena"
type: character
---
A mysterious wanderer.
""", encoding="utf-8")

        scene1 = self.manuscript_dir / "01_Chapter_01.md"
        scene1.write_text("""# Chapter 1
@pov: Elena

Elena stepped forward. Her golden hair blew in the wind.
""", encoding="utf-8")

        scene2 = self.manuscript_dir / "02_Chapter_02.md"
        scene2.write_text("""# Chapter 2
@pov: Elena

Elena hid behind the pillar. Her raven hair was covered by a dark hood.
""", encoding="utf-8")

        profiles = extract_lore_profiles(self.world_dir)
        findings = scan_manuscript_scenes(self.manuscript_dir, profiles)
        cnt102_findings = [f for f in findings if f["id"] == "CNT-102"]
        self.assertGreaterEqual(len(cnt102_findings), 1)
        self.assertEqual(cnt102_findings[0]["entity"], "Elena")
        self.assertEqual(cnt102_findings[0]["trait"], "hair_color")

    def test_scan_manuscript_multi_character_attribution(self):
        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True)
        (chars_dir / "Renée.md").write_text("""---
name: "Renée"
type: character
eyes: emerald
---
Renée of the realm.
""", encoding="utf-8")
        (chars_dir / "Julian.md").write_text("""---
name: "Julian"
type: character
eyes: blue
---
Julian the wanderer.
""", encoding="utf-8")

        scene = self.manuscript_dir / "01_Chapter_01.md"
        scene.write_text("""# Chapter 1
@chars: Renée, Julian

Julian turned around with bright blue eyes.
Renée smiled, her emerald eyes glowing softly.
""", encoding="utf-8")

        profiles = extract_lore_profiles(self.world_dir)
        findings = scan_manuscript_scenes(self.manuscript_dir, profiles)
        self.assertEqual(len(findings), 0)

    def test_run_continuity_audit(self):
        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True)
        (chars_dir / "Hero.md").write_text("""---
name: "Hero"
---
Hero had blue eyes.
""", encoding="utf-8")

        report = run_continuity_audit(str(self.world_dir), str(self.manuscript_dir))
        self.assertEqual(report["world"], "World")
        self.assertEqual(report["manuscript"], "Manuscript")
        self.assertEqual(report["entities_profiled"], 1)
        self.assertEqual(report["total_findings"], 0)


if __name__ == "__main__":
    unittest.main()

