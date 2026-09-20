#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Geopolitical Faction Matrix & Logistics (scripts/lib/factions.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.factions import (
    extract_faction_profiles,
    audit_faction_diplomacy,
    generate_faction_mermaid,
    generate_faction_html_report,
    calc_lanchester_battle,
    calc_campaign_logistics,
)


class TestFactionsEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "Factions").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_and_audit_clean_factions(self):
        (self.world_dir / "Factions" / "Solar_Empire.md").write_text("""---
name: "Solar Empire"
type: faction
faction_type: "Empire"
leader: "[[Emperor Sol]]"
allies:
  - "[[Lunar Kingdom]]"
rivals:
  - "[[Void Syndicate]]"
military_strength: 50000
---
# Solar Empire
""", encoding="utf-8")

        (self.world_dir / "Factions" / "Lunar_Kingdom.md").write_text("""---
name: "Lunar Kingdom"
type: faction
faction_type: "Kingdom"
leader: "[[Queen Luna]]"
allies:
  - "[[Solar Empire]]"
rivals:
  - "[[Void Syndicate]]"
military_strength: 30000
---
# Lunar Kingdom
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        self.assertIn("Solar Empire", factions)
        self.assertIn("Lunar Kingdom", factions)
        self.assertEqual(factions["Solar Empire"]["military_strength"], 50000.0)
        self.assertIn("Lunar Kingdom", factions["Solar Empire"]["allies"])

        findings = audit_faction_diplomacy(factions)
        self.assertEqual(len(findings), 0)

        mermaid = generate_faction_mermaid(factions)
        self.assertIn("flowchart LR", mermaid)
        self.assertIn("Solar Empire", mermaid)

    def test_diplomatic_paradoxes_fac101_fac102_fac103_fac104(self):
        # FAC-101: Asymmetric Rivalry / Alliance contradiction
        # FAC-102: Triad tension (A allies B, B allies C, A rivals C)
        # FAC-103: Vassal allied with overlord's rival
        # FAC-104: Self reference
        (self.world_dir / "Factions" / "House_A.md").write_text("""---
name: "House A"
allies:
  - "House B"
  - "House A"
rivals:
  - "House C"
vassals:
  - "House V"
---
""", encoding="utf-8")

        (self.world_dir / "Factions" / "House_B.md").write_text("""---
name: "House B"
allies:
  - "House A"
  - "House C"
---
""", encoding="utf-8")

        (self.world_dir / "Factions" / "House_C.md").write_text("""---
name: "House C"
allies:
  - "House B"
rivals:
  - "House A"
---
""", encoding="utf-8")

        (self.world_dir / "Factions" / "House_V.md").write_text("""---
name: "House V"
allies:
  - "House C"
overlord: "House A"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)

        finding_ids = [f["id"] for f in findings]
        self.assertIn("FAC-104", finding_ids) # House A lists House A
        self.assertIn("FAC-102", finding_ids) # Triad tension
        self.assertIn("FAC-103", finding_ids) # Vassal allied with rival

    def test_lanchester_battle_calculation(self):
        # Square Law test
        res_square = calc_lanchester_battle(attacker_force=10000, defender_force=5000, attacker_eff=1.0, defender_eff=1.0, law="square")
        self.assertEqual(res_square["victor"], "Attacker")
        self.assertGreater(res_square["final_attacker"], 0)
        self.assertLess(res_square["final_defender"], 2500)

        # Fortification bonus defending against superior attacker
        res_fort = calc_lanchester_battle(attacker_force=10000, defender_force=5000, fort_bonus=5.0, law="square")
        self.assertEqual(res_fort["victor"], "Defender")

        # Linear Law test
        res_linear = calc_lanchester_battle(attacker_force=5000, defender_force=5000, law="linear")
        self.assertIn("victor", res_linear)

    def test_campaign_logistics_calculation(self):
        log = calc_campaign_logistics(infantry=5000, cavalry=1000, support=500, distance_km=100.0, march_speed_km_day=20.0)
        self.assertGreater(log["daily_consumption"]["total_daily_supply_tons"], 0)
        self.assertGreater(log["logistics_requirements"]["wagons_required"], 0)
        self.assertTrue(log["logistics_requirements"]["is_within_wagon_radius"])

        # Test extreme distance exceeding wagon radius
        log_far = calc_campaign_logistics(infantry=5000, cavalry=1000, distance_km=5000.0, march_speed_km_day=15.0)
        self.assertFalse(log_far["logistics_requirements"]["is_within_wagon_radius"])
        self.assertIn("SUPPLY FAILURE", log_far["logistics_requirements"]["logistics_verdict"])

    def test_generate_faction_html_report(self):
        (self.world_dir / "Factions" / "Guild.md").write_text("""---
name: "Merchants Guild"
type: faction
---
""", encoding="utf-8")
        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        html_out = Path(self.temp_dir.name) / "factions.html"
        generate_faction_html_report({"world": "TestWorld", "factions": factions, "findings": findings}, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Merchants Guild", html_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
