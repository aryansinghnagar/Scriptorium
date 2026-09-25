#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Geopolitical Faction Matrix & Logistics (scripts/lib/factions.py).
Covers faction profiling, diplomatic paradoxes (FAC-101 to FAC-104), Mermaid generation,
Lanchester combat mathematics, campaign logistics, and HTML reporting.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.factions import (
    audit_faction_diplomacy,
    calc_campaign_logistics,
    calc_lanchester_battle,
    extract_faction_profiles,
    generate_faction_html_report,
    generate_faction_mermaid,
)


class TestFactionsEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "Factions").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extract_and_audit_clean_factions(self) -> None:
        """extract_faction_profiles correctly parses allies, rivals, and military strength."""
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

    def test_diplomatic_asymmetric_alliance_fac101(self) -> None:
        """FAC-101 WARNING is raised when an alliance is unreciprocated in frontmatter."""
        (self.world_dir / "Factions" / "Faction_A.md").write_text("""---
name: "Faction A"
allies:
  - "Faction B"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_B.md").write_text("""---
name: "Faction B"
allies: []
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-101" and f["severity"] == "WARNING" and "Asymmetric Alliance" in f["message"] for f in findings))

    def test_diplomatic_contradiction_fac101(self) -> None:
        """FAC-101 ERROR is raised when A claims alliance with B, but B lists A as a rival."""
        (self.world_dir / "Factions" / "Faction_A.md").write_text("""---
name: "Faction A"
allies:
  - "Faction B"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_B.md").write_text("""---
name: "Faction B"
rivals:
  - "Faction A"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-101" and f["severity"] == "ERROR" and "Contradiction" in f["message"] for f in findings))

    def test_diplomatic_triad_tension_fac102(self) -> None:
        """FAC-102 WARNING is raised when A allies B, B allies C, but A and C are declared rivals."""
        (self.world_dir / "Factions" / "Faction_A.md").write_text("""---
name: "Faction A"
allies:
  - "Faction B"
rivals:
  - "Faction C"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_B.md").write_text("""---
name: "Faction B"
allies:
  - "Faction A"
  - "Faction C"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_C.md").write_text("""---
name: "Faction C"
allies:
  - "Faction B"
rivals:
  - "Faction A"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-102" for f in findings))

    def test_diplomatic_vassal_allegiance_conflict_fac103(self) -> None:
        """FAC-103 ERROR is raised when a vassal is allied with its overlord's rival."""
        (self.world_dir / "Factions" / "Overlord.md").write_text("""---
name: "Overlord"
rivals:
  - "Enemy"
vassals:
  - "Vassal"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Enemy.md").write_text("""---
name: "Enemy"
rivals:
  - "Overlord"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Vassal.md").write_text("""---
name: "Vassal"
overlord: "Overlord"
allies:
  - "Enemy"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-103" and f["severity"] == "ERROR" for f in findings))

    def test_diplomatic_self_reference_fac104(self) -> None:
        """FAC-104 flags when a faction lists itself in allies or rivals."""
        (self.world_dir / "Factions" / "House_Solo.md").write_text("""---
name: "House Solo"
allies:
  - "House Solo"
rivals:
  - "House Solo"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-104" for f in findings))

    def test_lanchester_square_law_combat(self) -> None:
        """Square Law calculates aimed ranged combat where numerical superiority scales quadratically."""
        res = calc_lanchester_battle(attacker_force=10000, defender_force=5000, law="square")
        self.assertEqual(res["victor"], "Attacker")
        self.assertGreater(res["final_attacker"], 7000)
        self.assertEqual(res["law"], "square")

    def test_lanchester_fortification_bonus_turnaround(self) -> None:
        """Fortification multiplier allows a smaller garrison to hold against a larger force."""
        res_no_fort = calc_lanchester_battle(attacker_force=10000, defender_force=6000, fort_bonus=1.0)
        self.assertEqual(res_no_fort["victor"], "Attacker")

        res_fort = calc_lanchester_battle(attacker_force=10000, defender_force=6000, fort_bonus=5.0)
        self.assertEqual(res_fort["victor"], "Defender")

    def test_lanchester_linear_melee_combat(self) -> None:
        """Linear Law simulates bounded melee engagement contact width."""
        res_linear = calc_lanchester_battle(attacker_force=5000, defender_force=5000, law="linear")
        self.assertIn("victor", res_linear)
        self.assertEqual(res_linear["law"], "linear")

    def test_campaign_logistics_within_wagon_radius(self) -> None:
        """Feasible march distance within wagon radius calculates positive requirements and success verdict."""
        log = calc_campaign_logistics(infantry=5000, cavalry=1000, support=500, distance_km=100.0, march_speed_km_day=20.0)
        self.assertGreater(log["daily_consumption"]["total_daily_supply_tons"], 0)
        self.assertGreater(log["logistics_requirements"]["wagons_required"], 0)
        self.assertTrue(log["logistics_requirements"]["is_within_wagon_radius"])
        self.assertIn("Feasible", log["logistics_requirements"]["logistics_verdict"])

    def test_campaign_logistics_exceeds_wagon_radius_failure(self) -> None:
        """Excessive march distance triggers SUPPLY FAILURE when draught animals consume cargo."""
        log_far = calc_campaign_logistics(infantry=5000, cavalry=1000, distance_km=5000.0, march_speed_km_day=15.0)
        self.assertFalse(log_far["logistics_requirements"]["is_within_wagon_radius"])
        self.assertIn("SUPPLY FAILURE", log_far["logistics_requirements"]["logistics_verdict"])

    def test_generate_faction_html_report_and_csp(self) -> None:
        """HTML report generates with strict offline Content-Security-Policy and table markup."""
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
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Merchants Guild", content)
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)


if __name__ == "__main__":
    unittest.main()
