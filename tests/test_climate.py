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

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # Original 5 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_earth_like_insolation(self):
        ins = calc_planetary_insolation(
            stellar_luminosity=1.0,
            semi_major_axis_au=1.0,
            bond_albedo=0.30,
            greenhouse_warming_k=33.0,
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
        oro = calc_orographic_rain_shadow(
            mountain_elevation_m=3500.0, base_precip_mm=1000.0, base_temp_c=22.0
        )
        self.assertGreater(oro["windward"]["precipitation_mm"], 1000.0)
        self.assertLess(oro["leeward"]["precipitation_mm"], 400.0)
        self.assertTrue(oro["is_severe_rain_shadow"])

    def test_generate_climate_html_report(self):
        ins = calc_planetary_insolation()
        circ = calc_atmospheric_circulation()
        oro = calc_orographic_rain_shadow()
        tmp_html = Path(self.temp_dir.name) / "test_climate.html"
        generate_climate_html_report(
            {"insolation": ins, "circulation": circ, "orography": oro}, tmp_html
        )
        self.assertTrue(tmp_html.is_file())
        self.assertIn("Planetary Climate", tmp_html.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # New tests 6–10                                                       #
    # ------------------------------------------------------------------ #

    def test_hot_dry_world_not_habitable(self):
        """A bright, close-in world with no albedo or greenhouse → scorching surface."""
        ins = calc_planetary_insolation(
            stellar_luminosity=5.0,
            semi_major_axis_au=0.5,
            bond_albedo=0.0,
            greenhouse_warming_k=0.0,
        )
        # Either surface temperature exceeds 100°C or the habitable flag is False
        self.assertTrue(
            ins["surface_temp_c"] > 100 or not ins["liquid_water_habitable"],
            msg=f"Expected uninhabitable world but got surface_temp_c={ins['surface_temp_c']}, "
                f"liquid_water_habitable={ins['liquid_water_habitable']}",
        )

    def test_wind_bands_cover_hemisphere(self):
        """Every wind band for a 24-hour rotator must stay within 0–90° latitude."""
        circ = calc_atmospheric_circulation(rotation_period_hours=24.0)
        bands = circ["wind_bands"]
        self.assertGreater(len(bands), 0, "Expected at least one wind band")
        for band in bands:
            self.assertGreaterEqual(
                band["lat_min"],
                0,
                msg=f"Band '{band.get('name')}' has lat_min={band['lat_min']} < 0",
            )
            self.assertLessEqual(
                band["lat_max"],
                90,
                msg=f"Band '{band.get('name')}' has lat_max={band['lat_max']} > 90",
            )

    def test_moderate_mountain_shadow(self):
        """A 1500 m ridge should still produce a measurable leeward precipitation deficit."""
        oro = calc_orographic_rain_shadow(
            mountain_elevation_m=1500.0,
            base_precip_mm=800.0,
            base_temp_c=20.0,
        )
        self.assertLess(
            oro["leeward"]["precipitation_mm"],
            oro["windward"]["precipitation_mm"],
            msg="Leeward side should receive less precipitation than windward side",
        )

    def test_koppen_tundra_classification(self):
        """Cold, low-precipitation conditions should yield a polar/tundra/subarctic label."""
        result = classify_koppen_biome(-5.0, 300.0)
        keywords = ("tundra", "subarctic", "polar")
        self.assertTrue(
            any(kw in result.lower() for kw in keywords),
            msg=f"Expected a tundra/subarctic/polar biome but got: '{result}'",
        )

    def test_html_csp_compliance(self):
        """Generated HTML report must declare a Content-Security-Policy meta tag."""
        ins = calc_planetary_insolation()
        circ = calc_atmospheric_circulation()
        oro = calc_orographic_rain_shadow()
        out = Path(self.temp_dir.name) / "climate_csp.html"
        generate_climate_html_report(
            {"insolation": ins, "circulation": circ, "orography": oro}, out
        )
        content = out.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="HTML report is missing a Content-Security-Policy meta tag",
        )


    def test_insolation_return_keys(self):
        """calc_planetary_insolation must return all documented keys including surface_temp_f."""
        ins = calc_planetary_insolation()
        for key in ("stellar_flux_w_m2", "equilibrium_temp_k", "surface_temp_k",
                    "surface_temp_c", "surface_temp_f", "liquid_water_habitable"):
            self.assertIn(key, ins, msg=f"Insolation result is missing key '{key}'")

    def test_orographic_leeward_has_biome(self):
        """calc_orographic_rain_shadow leeward sub-dict must include a biome classification string."""
        oro = calc_orographic_rain_shadow(mountain_elevation_m=3000.0, base_precip_mm=1000.0)
        self.assertIn("biome", oro["leeward"], msg="Leeward dict is missing 'biome' key")
        self.assertIsInstance(oro["leeward"]["biome"], str)
        self.assertGreater(len(oro["leeward"]["biome"]), 0)


if __name__ == "__main__":
    unittest.main()
