#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Hard Magic Systems & Arcane Constraint Matrix (scripts/lib/magic_system.py).
Covers magic profile extraction, character tier limits, catalyst validation, fatigue tracking,
hard limitation enforcement, and HTML report generation.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.magic_system import (
    extract_character_magic_profiles,
    extract_magic_profiles,
    generate_magic_html_report,
    resolve_manuscript_dir,
    resolve_world_dir,
    run_magic_audit,
)


class TestMagicSystemEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)

        (self.world_dir / "Magic-Technology").mkdir(parents=True)
        (self.world_dir / "Characters").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extract_magic_profiles(self) -> None:
        """Parses magic system frontmatter and markdown sections for rules and limits."""
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

    def test_extract_character_magic_profiles(self) -> None:
        """Parses character affinity, registered tier, and catalyst attunement."""
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
        self.assertEqual(chars["Valen Vance"]["max_fatigue"], 80)



    def test_detect_missing_catalyst_mag102(self) -> None:
        """MAG-102 is raised when required spell catalyst is absent from scene and inventory."""
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

    def test_detect_hard_limitation_breach_resurrection_mag103(self) -> None:
        """MAG-103 detects resurrection descriptions violating explicit system bounds."""
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

    def test_detect_hard_limitation_breach_matter_creation_mag103(self) -> None:
        """MAG-103 detects matter creation violating physical conservation bounds."""
        (self.world_dir / "Magic-Technology" / "Elementalism.md").write_text("""---
name: "Elementalism"
type: magic_tech_system
hard_limitations:
  - "Cannot create matter from nothing"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "04_Scene.md"
        scene.write_text("""# Scene 4
@pov: Valen

With a wave of his hand, he created water from nothing to quench their thirst.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-103" for f in audit["findings"]))



    def test_clean_scene_compliant_cast_no_findings(self) -> None:
        """Compliant casting within tier, with catalyst, under fatigue limit gives 0 findings."""
        (self.world_dir / "Magic-Technology" / "Aether.md").write_text("""---
name: "Aether"
type: magic_tech_system
---
""", encoding="utf-8")

        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen"
magic_tier: 3
catalyst: "Opal Focus"
max_fatigue: 100
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "06_Scene.md"
        scene.write_text("""# Scene 6
@pov: Valen
@reagent: Opal Focus
@cast: Valen, Spark, tier=1, catalyst=Opal Focus, cost=10

A single bright spark flickered to life.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertEqual(audit["total_findings"], 0)

    def test_character_inventory_catalyst_satisfies_requirement(self) -> None:
        """Catalyst registered in character profile frontmatter satisfies catalyst check."""
        (self.world_dir / "Characters" / "Elena.md").write_text("""---
name: "Elena"
magic_tier: 3
attuned_catalysts:
  - "Star Shard"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "07_Scene.md"
        scene.write_text("""# Scene 7
@pov: Elena
@cast: Elena, Radiant Ward, tier=2, catalyst=Star Shard

The protective barrier hummed with power.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertEqual(audit["total_findings"], 0)

    def test_html_report_generation_and_csp(self) -> None:
        """HTML report generates with strict offline Content-Security-Policy."""
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
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Arcane Constraint Matrix", content)
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    def test_html_report_clean_world_pass(self) -> None:
        """HTML report displays green success badge when zero findings are detected."""
        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        out_html = self.ms_dir / "clean_report.html"
        generate_magic_html_report(audit, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("100% consistent", content)

    def test_resolve_world_and_manuscript_dir(self) -> None:
        """Directory path resolution helpers resolve absolute and relative paths."""
        resolved_w = resolve_world_dir(str(self.world_dir))
        self.assertEqual(resolved_w, str(self.world_dir.resolve()))
        resolved_m = resolve_manuscript_dir(str(self.ms_dir))
        self.assertEqual(resolved_m, str(self.ms_dir.resolve()))


if __name__ == "__main__":
    unittest.main()
