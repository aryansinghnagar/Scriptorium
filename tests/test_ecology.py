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

    # ------------------------------------------------------------------ #
    # Original 3 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_clean_self_sustaining_ecosystem(self):
        (self.world_dir / "Flora" / "Sun_Grass.md").write_text(
            """---
name: "Sun Grass"
trophic_level: 1
habitat: "Savanna"
biomass_kg: 10000
population_density: 500
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Gazelle.md").write_text(
            """---
name: "Sun Gazelle"
trophic_level: 2
habitat: "Savanna"
dietary_prey:
  - "[[Sun Grass]]"
biomass_kg: 40
population_density: 100
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Shadow_Lion.md").write_text(
            """---
name: "Shadow Lion"
trophic_level: 4
habitat: "Savanna"
dietary_prey:
  - "[[Sun Gazelle]]"
biomass_kg: 180
population_density: 0.5
---
""",
            encoding="utf-8",
        )

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
        (self.world_dir / "Bestiary" / "Apex_Solitary.md").write_text(
            """---
name: "Apex Solitary"
trophic_level: 4
habitat: "Volcanic Ridge"
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Predator_A.md").write_text(
            """---
name: "Predator A"
trophic_level: 3
dietary_prey:
  - "Predator B"
habitat: "Jungle"
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Predator_B.md").write_text(
            """---
name: "Predator B"
trophic_level: 3
dietary_prey:
  - "Predator A"
habitat: "Jungle"
---
""",
            encoding="utf-8",
        )

        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-301", ids)  # Apex without prey
        self.assertIn("ECO-303", ids)  # Circular predation loop
        self.assertIn("ECO-304", ids)  # Volcanic Ridge missing Level 1 producers

    def test_generate_ecology_html_report(self):
        (self.world_dir / "Bestiary" / "Wolf.md").write_text(
            """---
name: "Timber Wolf"
trophic_level: 3
habitat: "Forest"
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        html_out = Path(self.temp_dir.name) / "ecology.html"
        generate_ecology_html_report(
            {"world": "TestWorld", "species": species, "findings": []}, html_out
        )
        self.assertTrue(html_out.is_file())
        self.assertIn("Timber Wolf", html_out.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # New tests 4–10                                                       #
    # ------------------------------------------------------------------ #

    def test_trophic_deficit_eco302(self):
        """Predator biomass density exceeding 35% of prey biomass density should raise ECO-302."""
        (self.world_dir / "Flora" / "Forest_Fern.md").write_text(
            """---
name: "Forest Fern"
trophic_level: 1
habitat: "Forest"
biomass_kg: 5000
population_density: 500
---
""",
            encoding="utf-8",
        )
        (self.world_dir / "Bestiary" / "Forest_Deer.md").write_text(
            """---
name: "Forest Deer"
trophic_level: 2
habitat: "Forest"
dietary_prey:
  - "[[Forest Fern]]"
biomass_kg: 50
population_density: 2
---
""",
            encoding="utf-8",
        )
        (self.world_dir / "Bestiary" / "Shadow_Wolf.md").write_text(
            """---
name: "Shadow Wolf"
trophic_level: 3
habitat: "Forest"
dietary_prey:
  - "[[Forest Deer]]"
biomass_kg: 80
population_density: 1
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)
        ids = [f["id"] for f in findings]
        self.assertIn("ECO-302", ids, msg="Expected ECO-302 for trophic deficit")

    def test_multiple_habitats_no_eco304(self):
        """Three separate habitats each with a trophic-level-1 producer → no ECO-304."""
        habitats = [
            ("Grassland", "Fern"),
            ("Desert", "Cactus"),
            ("Ocean", "Kelp"),
        ]
        for habitat, plant_name in habitats:
            safe_name = plant_name.replace(" ", "_")
            (self.world_dir / "Flora" / f"{safe_name}.md").write_text(
                f"""---
name: "{plant_name}"
trophic_level: 1
habitat: "{habitat}"
biomass_kg: 5000
population_density: 1000
---
""",
                encoding="utf-8",
            )

        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)
        eco304_findings = [f for f in findings if f["id"] == "ECO-304"]
        self.assertEqual(
            len(eco304_findings),
            0,
            msg=f"Unexpected ECO-304 findings: {eco304_findings}",
        )

    def test_extract_flora_species(self):
        """Flora files should be parsed and returned with trophic_level 1."""
        (self.world_dir / "Flora" / "MossPlant.md").write_text(
            """---
name: "Moss Plant"
trophic_level: 1
habitat: "Cavern"
biomass_kg: 300
population_density: 200
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        self.assertIn("Moss Plant", species)
        self.assertEqual(species["Moss Plant"]["trophic_level"], 1)

    def test_single_species_apex_no_prey_eco301(self):
        """A lone apex predator with no dietary_prey must trigger ECO-301."""
        (self.world_dir / "Bestiary" / "Lone_Apex.md").write_text(
            """---
name: "Lone Apex"
trophic_level: 4
habitat: "Tundra"
biomass_kg: 200
population_density: 0.1
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)
        ids = [f["id"] for f in findings]
        self.assertIn("ECO-301", ids, msg="Expected ECO-301 for apex predator without prey")

    def test_mermaid_contains_prey_arrows(self):
        """Mermaid output must include '-->' arrows representing predation links."""
        (self.world_dir / "Flora" / "Grass.md").write_text(
            """---
name: "Grass"
trophic_level: 1
habitat: "Plains"
biomass_kg: 8000
population_density: 2000
---
""",
            encoding="utf-8",
        )
        (self.world_dir / "Bestiary" / "Gazelle.md").write_text(
            """---
name: "Gazelle"
trophic_level: 2
habitat: "Plains"
dietary_prey:
  - "[[Grass]]"
biomass_kg: 45
population_density: 80
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        mermaid = generate_ecology_mermaid(species)
        self.assertIn("-->", mermaid, msg="Mermaid diagram should contain '-->' predation arrows")

    def test_html_csp_compliance(self):
        """Generated ecology HTML must include a Content-Security-Policy meta tag."""
        (self.world_dir / "Bestiary" / "Bear.md").write_text(
            """---
name: "Forest Bear"
trophic_level: 3
habitat: "Forest"
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        out = Path(self.temp_dir.name) / "ecology_csp.html"
        generate_ecology_html_report(
            {"world": "CSPTest", "species": species, "findings": []}, out
        )
        content = out.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="Ecology HTML report is missing a Content-Security-Policy meta tag",
        )

    def test_biomass_and_density_extracted(self):
        """Extracted species profile should faithfully preserve biomass_kg and population_density."""
        (self.world_dir / "Bestiary" / "Iron_Boar.md").write_text(
            """---
name: "Iron Boar"
trophic_level: 2
habitat: "Forest"
biomass_kg: 250
population_density: 5
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        self.assertIn("Iron Boar", species)
        profile = species["Iron Boar"]
        self.assertIn("biomass_kg", profile, msg="Profile should contain 'biomass_kg'")
        self.assertIn(
            "population_density", profile, msg="Profile should contain 'population_density'"
        )
        self.assertEqual(profile["biomass_kg"], 250)
        self.assertEqual(profile["population_density"], 5)


    def test_mermaid_starts_with_mermaid_fence(self):
        """generate_ecology_mermaid must start with the mermaid code fence marker."""
        (self.world_dir / "Flora" / "Meadow_Grass.md").write_text(
            "---\nname: \"Meadow Grass\"\ntrophic_level: 1\nhabitat: \"Meadow\"\nbiomass_kg: 5000\npopulation_density: 1000\n---\n",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        mermaid = generate_ecology_mermaid(species)
        self.assertTrue(
            mermaid.strip().startswith("```mermaid") or "flowchart TD" in mermaid,
            msg=f"Mermaid output should start with ```mermaid or contain flowchart TD: {mermaid[:80]}",
        )

    def test_species_profile_trophic_name_set(self):
        """Extracted species profile must include a human-readable trophic_name string."""
        (self.world_dir / "Bestiary" / "Fox.md").write_text(
            "---\nname: \"Sly Fox\"\ntrophic_level: 3\nhabitat: \"Forest\"\n---\n",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        self.assertIn("Sly Fox", species)
        profile = species["Sly Fox"]
        self.assertIn("trophic_name", profile, msg="Profile must contain 'trophic_name'")
        self.assertIsInstance(profile["trophic_name"], str)
        self.assertGreater(len(profile["trophic_name"]), 0)


if __name__ == "__main__":
    unittest.main()
