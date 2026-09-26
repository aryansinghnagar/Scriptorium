#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Astrophysics & Relativistic Flight Engine (scripts/lib/astrophysics.py).
Covers Brachistochrone trajectories, Lorentz factors, time dilation, Hohmann transfers, comms latencies,
and planetary habitability / surface gravity calculations.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.astrophysics import (
    G0, AU, LIGHT_YEAR, EARTH_MASS, EARTH_RADIUS,
    parse_distance, parse_acceleration, format_duration, format_distance,
    calc_brachistochrone, calc_time_dilation, calc_orbital_transfer,
    calc_comms_delay, calc_habitability_gravity, generate_astrophysics_html_report, calc_planetary_dossier
)


class TestAstrophysicsEngine(unittest.TestCase):

    def test_parse_distance(self):
        self.assertAlmostEqual(parse_distance("1.0 AU"), AU, places=1)
        self.assertAlmostEqual(parse_distance("4.2 ly"), 4.2 * LIGHT_YEAR, places=1)
        self.assertAlmostEqual(parse_distance("1000 km"), 1000000.0)
        self.assertAlmostEqual(parse_distance("earth-moon"), 384400000.0)
        self.assertAlmostEqual(parse_distance("alpha-centauri"), 4.37 * LIGHT_YEAR, places=1)
        # Edge cases with multi-letter suffixes
        self.assertAlmostEqual(parse_distance("54 mkm"), 54e9)
        self.assertAlmostEqual(parse_distance("54 million-km"), 54e9)
        self.assertAlmostEqual(parse_distance("2.5 billion-km"), 2.5e12)
        self.assertAlmostEqual(parse_distance("10 kpc"), 10.0 * 1e3 * 30856775814913700.0)
        self.assertAlmostEqual(parse_distance("500 meters"), 500.0)

    def test_parse_acceleration(self):
        self.assertAlmostEqual(parse_acceleration("1g"), G0, places=3)
        self.assertAlmostEqual(parse_acceleration("2g"), 2.0 * G0, places=3)
        self.assertAlmostEqual(parse_acceleration("9.81 m/s^2"), 9.81, places=2)

    def test_format_duration(self):
        self.assertIn("seconds", format_duration(45.0))
        self.assertIn("minutes", format_duration(300.0))
        self.assertIn("hours", format_duration(7200.0))
        self.assertIn("days", format_duration(86400.0 * 5))
        self.assertIn("years", format_duration(86400.0 * 365.25 * 3.5))

    def test_format_distance(self):
        self.assertIn("AU", format_distance(AU * 1.5))
        self.assertIn("ly", format_distance(LIGHT_YEAR * 4.2))
        self.assertIn("km", format_distance(50000000.0))

    def test_brachistochrone_relativistic_sublight(self):
        # Earth to Mars average distance ~ 225 million km
        d = 225e9
        res = calc_brachistochrone(d, acc_mps2=G0)
        self.assertGreater(res["proper_time_sec"], 0)
        self.assertGreater(res["coordinate_time_sec"], 0)
        # At interplanetary distances, relativistic gamma is very close to 1
        self.assertAlmostEqual(res["peak_gamma"], 1.0, places=3)
        self.assertAlmostEqual(res["proper_time_sec"], res["coordinate_time_sec"], delta=10.0)

    def test_brachistochrone_interstellar_relativistic(self):
        # Alpha Centauri ~ 4.37 light years
        d = 4.37 * LIGHT_YEAR
        res = calc_brachistochrone(d, acc_mps2=G0, exhaust_vel_mps=3e7)
        # Crew proper time should be significantly dilated compared to observer time
        # ~3.58 proper years vs ~6.0 coordinate observer years
        proper_years = res["proper_time_sec"] / (86400.0 * 365.25)
        coord_years = res["coordinate_time_sec"] / (86400.0 * 365.25)
        self.assertGreater(coord_years, proper_years)
        self.assertGreater(res["peak_velocity_c_fraction"], 0.90)
        self.assertGreater(res["peak_gamma"], 2.0)
        self.assertIsNotNone(res["propellant_mass_ratio"])

    def test_time_dilation_kinematic(self):
        # At v = 0.866c, gamma is approximately 2.0
        res = calc_time_dilation(beta=0.866)
        kin = res["kinematic"]
        self.assertAlmostEqual(kin["gamma"], 2.0, places=1)
        self.assertAlmostEqual(kin["crew_time_ratio"], 0.5, places=1)
        self.assertAlmostEqual(kin["proper_seconds_per_observer_day"], 43200.0, delta=100.0)

    def test_time_dilation_gravitational(self):
        # Test near Earth surface
        res = calc_time_dilation(beta=0.0, grav_mass_kg=EARTH_MASS, grav_radius_m=EARTH_RADIUS)
        self.assertIn("gravitational", res)
        g_info = res["gravitational"]
        self.assertAlmostEqual(g_info["gravitational_dilation_factor"], 1.0, places=5)
        self.assertGreater(g_info["schwarzschild_radius_m"], 0.0)

    def test_hohmann_orbital_transfer(self):
        # Earth orbit (1 AU) to Mars orbit (1.524 AU) around Sun
        r1 = 1.0 * AU
        r2 = 1.524 * AU
        res = calc_orbital_transfer(primary_body="sun", r1_m=r1, r2_m=r2)
        # Earth orbital velocity ~ 29.8 km/s
        self.assertAlmostEqual(res["v1_kms"], 29.78, delta=0.5)
        # Mars transfer duration ~ 259 days (~ 2.2e7 seconds)
        transfer_days = res["transfer_duration_sec"] / 86400.0
        self.assertAlmostEqual(transfer_days, 258.8, delta=10.0)
        # Delta-v total ~ 5.6 km/s
        self.assertAlmostEqual(res["delta_v_total_kms"], 5.59, delta=0.5)

    def test_comms_delay(self):
        # Earth to Moon ~ 1.28 light-seconds one way
        res = calc_comms_delay(384400000.0)
        self.assertAlmostEqual(res["one_way_seconds"], 1.282, places=2)
        self.assertAlmostEqual(res["round_trip_seconds"], 2.564, places=2)

    def test_habitability_gravity(self):
        # Earth parameters
        res = calc_habitability_gravity(EARTH_MASS, EARTH_RADIUS)
        self.assertAlmostEqual(res["surface_gravity_g"], 1.0, places=2)
        self.assertAlmostEqual(res["escape_velocity_kms"], 11.18, delta=0.1)
        hz = res["habitable_zone_conservative"]
        self.assertAlmostEqual(hz["inner_au"], 0.95, delta=0.05)
        self.assertAlmostEqual(hz["outer_au"], 1.37, delta=0.05)

    def test_html_report_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "astro_report.html"
            sample_data = {"Mission Metrics": calc_brachistochrone(AU * 2.0)}
            generate_astrophysics_html_report("Test Flight", sample_data, out_file)
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("Test Flight", content)
            self.assertIn("Ars Arcanum Relativistic & Astrophysics Engine", content)



    def test_planetary_dossier(self):
        dossier = calc_planetary_dossier(
            mass_kg=EARTH_MASS, radius_m=EARTH_RADIUS,
            star_luminosity_watts=3.828e26, semi_major_axis_au=1.0,
            planet_type="tidally-locked"
        )
        self.assertEqual(dossier["planet_type"], "tidally-locked")
        self.assertIn("habitability_metrics", dossier)
        self.assertIn("climate_insolation", dossier)
        self.assertIn("climate_circulation", dossier)
        self.assertTrue(any("Tidally locked" in w for w in dossier["scientific_plausibility_warnings"]))


if __name__ == "__main__":
    unittest.main()
