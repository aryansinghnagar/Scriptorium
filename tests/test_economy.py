#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Economy, Commodity PPP & Anachronism Matrix (scripts/lib/economy.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.economy import (
    extract_economy_profiles,
    calculate_ppp_rates,
    audit_manuscript_prices,
    audit_technological_anachronisms,
    calc_trade_margin,
    generate_economy_html_report,
)


class TestEconomyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)
        (self.world_dir / "Economies").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_economy_profiles_and_ppp(self):
        (self.world_dir / "Economies" / "Solar_Standard.md").write_text("""---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
tech_era: "medieval"
currencies:
  - "Solar Crown: 1.0"
  - "Silver Sovereign: 0.1"
  - "Copper Bit: 0.01"
commodity_basket:
  - "loaf_of_bread: 2"
  - "pint_of_ale: 1"
  - "riding_horse: 500"
---
# Solar Standard Economy
""", encoding="utf-8")

        (self.world_dir / "Economies" / "Lunar_Dinar.md").write_text("""---
name: "Lunar Economy"
base_currency: "Lunar Dinar"
tech_era: "medieval"
currencies:
  - "Lunar Dinar: 1.0"
  - "Silver Dirham: 0.2"
commodity_basket:
  - "loaf_of_bread: 4"
  - "pint_of_ale: 2"
  - "riding_horse: 1000"
---
# Lunar Economy
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        self.assertIn("Solar Standard Economy", econs)
        self.assertIn("Lunar Economy", econs)

        ppp = calculate_ppp_rates(econs)
        # Solar loaf is 2, Lunar loaf is 4 -> Solar/Lunar ratio = 0.5
        self.assertAlmostEqual(ppp["Solar Standard Economy"]["Lunar Economy"], 0.5, places=2)
        self.assertAlmostEqual(ppp["Lunar Economy"]["Solar Standard Economy"], 2.0, places=2)

    def test_extract_currency_denominations(self):
        (self.world_dir / "Economies" / "Merchant_Guild.md").write_text("""---
name: "Merchant Guild Economy"
base_currency: "Gold Ducat"
currencies:
  - "Gold Ducat: 1.0"
  - "Silver Florin: 0.1"
  - "Copper Groat: 0.01"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        self.assertIn("Merchant Guild Economy", econs)
        mg = econs["Merchant Guild Economy"]
        self.assertEqual(mg["currencies"]["Gold Ducat"], 1.0)
        self.assertEqual(mg["currencies"]["Silver Florin"], 0.1)
        self.assertEqual(mg["currencies"]["Copper Groat"], 0.01)

    def test_calculate_ppp_disjoint_baskets(self):
        (self.world_dir / "Economies" / "Econ_A.md").write_text("""---
name: "Economy A"
commodity_basket:
  - "silk: 50"
---
""", encoding="utf-8")
        (self.world_dir / "Economies" / "Econ_B.md").write_text("""---
name: "Economy B"
commodity_basket:
  - "ore: 100"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        ppp = calculate_ppp_rates(econs)
        self.assertIsNone(ppp["Economy A"]["Economy B"])

    def test_audit_manuscript_prices_anomalies_eco101(self):
        (self.world_dir / "Economies" / "Imperial.md").write_text("""---
name: "Imperial Economy"
base_currency: "Gold Crown"
commodity_basket:
  - "loaf_of_bread: 1"
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("""# Chapter 1
The traveler entered the tavern.
@price: 100 Gold Crown for loaf_of_bread
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-101", ids)

    def test_audit_unregistered_currency_eco102(self):
        (self.world_dir / "Economies" / "Imperial.md").write_text("""---
name: "Imperial Economy"
base_currency: "Gold Crown"
currencies:
  - "Gold Crown: 1.0"
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("""# Chapter 1
He also paid with 50 Galactico credits for wine.
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-102", ids)

    def test_audit_prose_price_detection(self):
        (self.world_dir / "Economies" / "Imperial.md").write_text("""---
name: "Imperial Economy"
base_currency: "Gold Crown"
currencies:
  - "Gold Crowns: 1.0"
commodity_basket:
  - "iron sword: 10"
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Chapter.md").write_text("""# Chapter 2
The blacksmith demanded 600 Gold Crowns for iron sword.
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)
        ids = [f["id"] for f in findings]
        self.assertIn("ECO-101", ids)

    def test_audit_technological_anachronisms_eco201(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
The knight polished his plate armor and checked the radar screen before wrapping his food in plastic.
""", encoding="utf-8")

        findings = audit_technological_anachronisms(self.ms_dir, baseline_era="medieval")
        terms = [f["term"] for f in findings]
        self.assertIn("radar", terms)
        self.assertIn("plastic", terms)
        self.assertNotIn("plate armor", terms)

    def test_anachronism_interstellar_era_clean(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_SciFi.md").write_text("""# Starship Bridge
The commander checked the radar screen and initialized the fusion drive.
""", encoding="utf-8")

        findings = audit_technological_anachronisms(self.ms_dir, baseline_era="interstellar")
        self.assertEqual(len(findings), 0)

    def test_calc_trade_margin_profitable(self):
        res = calc_trade_margin(
            buy_price_per_ton=100.0,
            sell_price_per_ton=300.0,
            cargo_tons=50.0,
            distance_km_or_ly=100.0,
            transit_cost_per_ton_unit=0.5,
            tariff_pct=0.05
        )
        self.assertTrue(res["is_profitable"])
        self.assertGreater(res["net_profit"], 0)
        self.assertGreater(res["roi_pct"], 0)

    def test_calc_trade_margin_unprofitable(self):
        res = calc_trade_margin(
            buy_price_per_ton=200.0,
            sell_price_per_ton=210.0,
            cargo_tons=10.0,
            distance_km_or_ly=500.0,
            transit_cost_per_ton_unit=1.0,
            tariff_pct=0.15
        )
        self.assertFalse(res["is_profitable"])
        self.assertLess(res["net_profit"], 0)

    def test_generate_economy_html_report_csp(self):
        (self.world_dir / "Economies" / "Econ.md").write_text("""---
name: "Barter Economy"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        html_out = Path(self.temp_dir.name) / "economy.html"
        generate_economy_html_report({"world": "TestWorld", "economies": econs, "findings": []}, html_out)
        self.assertTrue(html_out.is_file())
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("Barter Economy", content)

    def test_empty_world_economy_profiles(self):
        empty_dir = Path(self.temp_dir.name) / "EmptyWorld"
        empty_dir.mkdir()
        econs = extract_economy_profiles(empty_dir)
        self.assertEqual(len(econs), 0)


if __name__ == "__main__":
    unittest.main()
