#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Hard Magic Systems & Arcane Constraint Matrix (scripts/lib/magic_system.py).
Covers magic profile extraction, character tier limits, catalyst validation, fatigue tracking,
hard limitation enforcement, and HTML report generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.magic_system import (
    extract_magic_profiles,
    extract_character_magic_profiles,
    scan_scene_magic_constraints,
    run_magic_audit,
    generate_magic_html_report,
)


class TestMagicSystemEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)

        (self.world_dir / "Magic-Technology").mkdir(parents=True)
        (self.world_dir / "Characters").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_magic_profiles(self):
        magic_file = self.world_dir / "Magic-Technology" / "Aether_Weaving.md"
        magic_file.write_text("""---
name: "Aether Weaving"
type: magic_tech_system
classification: "Hard Magic"
source_of_power: "Atmospheric Aether"
danger_cost: "High"
max_tier: 5
disciplines:
  - "Pyromancy"
  - "Chronomancy"
catalysts:
  - "Ruby Focus"
  - "Silver Thread"
hard_limitations:
  - "Cannot resurrect the dead"
  - "Cannot create matter from nothing"
---
# Aether Weaving
## 1. Core Concept & The Fundamental Rule
Energy must be conserved.
""", encoding="utf-8")

        profiles = extract_magic_profiles(self.world_dir)
        self.assertIn("Aether Weaving", profiles)
        data = profiles["Aether Weaving"]
        self.assertEqual(data["classification"], "Hard Magic")
        self.assertEqual(data["max_tier"], 5)
        self.assertIn("Pyromancy", data["disciplines"])
        self.assertIn("ruby focus", data["catalysts"])
        self.assertTrue(any("resurrect" in lim for lim in data["hard_limitations"]))

    def test_extract_character_magic_profiles(self):
        char_file = self.world_dir / "Characters" / "Valen.md"
        char_file.write_text("""---
name: "Valen Vance"
type: character
role: Protagonist
magic_tier: 2
magic_ability: "Pyromancy"
catalyst: "Ruby Focus"
max_fatigue: 80
---
# Valen Vance
A promising initiate.
""", encoding="utf-8")

        chars = extract_character_magic_profiles(self.world_dir)
        self.assertIn("Valen Vance", chars)
        self.assertEqual(chars["Valen Vance"]["magic_tier"], 2)
        self.assertIn("pyromancy", chars["Valen Vance"]["affinity"])
        self.assertIn("ruby focus", chars["Valen Vance"]["catalysts"])

    def test_detect_tier_violation_mag101(self):
        # Valen is Tier 2, scene has @cast: Valen Vance, Hellfire, tier=4
        (self.world_dir / "Magic-Technology" / "Aether.md").write_text("""---
name: "Aether"
type: magic_tech_system
---
""", encoding="utf-8")

        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen Vance"
magic_tier: 2
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md"
        scene.write_text("""# Scene 1
@pov: Valen Vance
@cast: Valen Vance, Hellfire, tier=4

Valen reached deep into the aether.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertEqual(audit["total_findings"], 1)
        finding = audit["findings"][0]
        self.assertEqual(finding["id"], "MAG-101")
        self.assertEqual(finding["character"], "Valen Vance")
        self.assertIn("Tier 2", finding["message"])

    def test_detect_missing_catalyst_mag102(self):
        # Spell requires catalyst Diamond, but character and scene lack it
        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen Vance"
magic_tier: 3
catalyst: "Ruby Focus"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "02_Scene.md"
        scene.write_text("""# Scene 2
@pov: Valen Vance
@cast: Valen Vance, Diamond Shield, tier=2, catalyst=Diamond

The light shone through the prism.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-102" for f in audit["findings"]))

    def test_detect_hard_limitation_breach_mag103(self):
        (self.world_dir / "Magic-Technology" / "Necromancy.md").write_text("""---
name: "Necromancy"
type: magic_tech_system
hard_limitations:
  - "Cannot resurrect the dead"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "03_Scene.md"
        scene.write_text("""# Scene 3
@pov: Elena

With a gasp, the fallen king was resurrected before their eyes.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-103" for f in audit["findings"]))

    def test_html_report_generation(self):
        (self.world_dir / "Magic-Technology" / "Alchemy.md").write_text("""---
name: "Alchemy"
type: magic_tech_system
classification: "Potioncraft"
---
""", encoding="utf-8")
        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        out_html = self.ms_dir / "magic_report.html"
        generate_magic_html_report(audit, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Arcane Constraint Matrix", out_html.read_text(encoding="utf-8"))

    def test_resolve_world_dir(self):
        from lib.magic_system import resolve_world_dir
        resolved = resolve_world_dir(str(self.world_dir))
        self.assertEqual(resolved, str(self.world_dir.resolve()))


if __name__ == "__main__":
    unittest.main()
