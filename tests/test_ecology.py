#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Trophic Food Web & Ecology Simulator (scripts/lib/ecology.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.ecology import (
    extract_species_profiles,
    audit_ecosystem,
    generate_ecology_mermaid,
    generate_ecology_html_report,
)


class TestEcologyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "Bestiary").mkdir(parents=True)
        (self.world_dir / "Flora").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_self_sustaining_ecosystem(self):
        (self.world_dir / "Flora" / "Sun_Grass.md").write_text("""---
name: "Sun Grass"
trophic_level: 1
habitat: "Savanna"
biomass_kg: 10000
population_density: 500
---
""", encoding="utf-8")

        (self.world_dir / "Bestiary" / "Gazelle.md").write_text("""---
name: "Sun Gazelle"
trophic_level: 2
habitat: "Savanna"
dietary_prey:
  - "[[Sun Grass]]"
biomass_kg: 40
population_density: 100
---
""", encoding="utf-8")

        (self.world_dir / "Bestiary" / "Shadow_Lion.md").write_text("""---
name: "Shadow Lion"
trophic_level: 4
habitat: "Savanna"
dietary_prey:
  - "[[Sun Gazelle]]"
biomass_kg: 180
population_density: 0.5
---
""", encoding="utf-8")

        species = extract_species_profiles(self.world_dir)
        self.assertIn("Sun Grass", species)
        self.assertIn("Sun Gazelle", species)
        self.assertIn("Shadow Lion", species)

        findings = audit_ecosystem(species)
        self.assertEqual(len(findings), 0)

        mermaid = generate_ecology_mermaid(species)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("Shadow Lion", mermaid)

    def test_trophic_anomalies_eco301_eco303_eco304(self):
        # ECO-301: Apex without prey
        # ECO-303: Circular predation loop
        # ECO-304: Missing primary producers in habitat
        (self.world_dir / "Bestiary" / "Apex_Solitary.md").write_text("""---
name: "Apex Solitary"
trophic_level: 4
habitat: "Volcanic Ridge"
---
""", encoding="utf-8")

        (self.world_dir / "Bestiary" / "Predator_A.md").write_text("""---
name: "Predator A"
trophic_level: 3
dietary_prey:
  - "Predator B"
habitat: "Jungle"
---
""", encoding="utf-8")

        (self.world_dir / "Bestiary" / "Predator_B.md").write_text("""---
name: "Predator B"
trophic_level: 3
dietary_prey:
  - "Predator A"
habitat: "Jungle"
---
""", encoding="utf-8")

        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-301", ids) # Apex without prey
        self.assertIn("ECO-303", ids) # Circular predation loop
        self.assertIn("ECO-304", ids) # Volcanic Ridge missing Level 1 producers

    def test_generate_ecology_html_report(self):
        (self.world_dir / "Bestiary" / "Wolf.md").write_text("""---
name: "Timber Wolf"
trophic_level: 3
habitat: "Forest"
---
""", encoding="utf-8")
        species = extract_species_profiles(self.world_dir)
        html_out = Path(self.temp_dir.name) / "ecology.html"
        generate_ecology_html_report({"world": "TestWorld", "species": species, "findings": []}, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Timber Wolf", html_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
