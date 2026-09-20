#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Planetary Climate & Orographic Simulator (scripts/lib/climate.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.climate import (
    calc_planetary_insolation,
    calc_atmospheric_circulation,
    calc_orographic_rain_shadow,
    classify_koppen_biome,
    generate_climate_html_report,
)


class TestClimateEngine(unittest.TestCase):

    def test_earth_like_insolation(self):
        ins = calc_planetary_insolation(
            stellar_luminosity=1.0,
            semi_major_axis_au=1.0,
            bond_albedo=0.30,
            greenhouse_warming_k=33.0
        )
        self.assertAlmostEqual(ins["stellar_flux_w_m2"], 1361.0, places=0)
        # Earth equilibrium temp ~ 255K, surface temp ~ 288K (15°C)
        self.assertAlmostEqual(ins["equilibrium_temp_k"], 254.9, delta=2.0)
        self.assertAlmostEqual(ins["surface_temp_c"], 14.8, delta=2.0)
        self.assertTrue(ins["liquid_water_habitable"])

    def test_atmospheric_circulation_cells(self):
        # Earth 24h rotation -> 3 cells
        circ_earth = calc_atmospheric_circulation(rotation_period_hours=24.0)
        self.assertEqual(circ_earth["circulation_cells_per_hemisphere"], 3)
        self.assertEqual(len(circ_earth["wind_bands"]), 3)

        # Slow rotator (e.g. Venus 243d) -> 1 cell
        circ_slow = calc_atmospheric_circulation(rotation_period_hours=500.0)
        self.assertEqual(circ_slow["circulation_cells_per_hemisphere"], 1)

        # Fast rotator (e.g. Jupiter 10h) -> 5 cells
        circ_fast = calc_atmospheric_circulation(rotation_period_hours=10.0)
        self.assertEqual(circ_fast["circulation_cells_per_hemisphere"], 5)

    def test_koppen_biome_classification(self):
        self.assertEqual(classify_koppen_biome(-15.0, 100.0), "Polar Ice Cap")
        self.assertEqual(classify_koppen_biome(25.0, 100.0), "Hyper-Arid Subtropical Desert")
        self.assertEqual(classify_koppen_biome(25.0, 2500.0), "Tropical Rainforest (Equatorial)")
        self.assertEqual(classify_koppen_biome(15.0, 1500.0), "Temperate Rainforest")

    def test_orographic_rain_shadow(self):
        # 3500m mountain ridge
        oro = calc_orographic_rain_shadow(mountain_elevation_m=3500.0, base_precip_mm=1000.0, base_temp_c=22.0)
        self.assertGreater(oro["windward"]["precipitation_mm"], 1000.0)
        self.assertLess(oro["leeward"]["precipitation_mm"], 400.0)
        self.assertTrue(oro["is_severe_rain_shadow"])

    def test_generate_climate_html_report(self):
        ins = calc_planetary_insolation()
        circ = calc_atmospheric_circulation()
        oro = calc_orographic_rain_shadow()
        tmp_html = Path(tempfile.gettempdir()) / "test_climate.html"
        generate_climate_html_report({"insolation": ins, "circulation": circ, "orography": oro}, tmp_html)
        self.assertTrue(tmp_html.is_file())
        self.assertIn("Planetary Climate", tmp_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
