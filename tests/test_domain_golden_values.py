#!/usr/bin/env python3
"""
Golden Reference Value & Domain Accuracy Tests (tests/test_domain_golden_values.py)
==================================================================================
Validates physical, astronomical, mathematical, and stylistic calculations against
published scientific reference benchmarks (F-18).
"""

import unittest
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.astrophysics import (
    calc_brachistochrone,
    calc_time_dilation,
    calc_orbital_transfer,
    LIGHT_YEAR,
    AU,
    G0,
    C,
)
from lib.climate import calc_planetary_insolation
from lib.factions import calc_lanchester_battle
from lib.tactical_sim import simulate_single_battle, run_monte_carlo
from lib.calendar import get_moon_phase, date_to_absolute_day, absolute_day_to_date
from lib.stylistics import analyze_readability_rhythm
from lib.voice import compute_voice_profile


class TestDomainGoldenValues(unittest.TestCase):

    # -------------------------------------------------------------------------
    # 1. Astrophysics & Relativistic Flight Reference Benchmarks
    # -------------------------------------------------------------------------
    def test_relativistic_brachistochrone_alpha_centauri(self):
        """
        Benchmark: 1g continuous acceleration with turnover to Alpha Centauri (4.37 ly).
        Published reference values:
        - Ship proper time: ~3.56 years (tau = 2*(c/g)*acosh(1 + g*(d/2)/c^2))
        - Coordinate observer time: ~6.00 years (t = 2*(c/g)*sinh(g*(tau/2)/c))
        - Peak velocity: ~0.95c
        """
        dist_m = 4.37 * LIGHT_YEAR
        res = calc_brachistochrone(distance_m=dist_m, acc_mps2=G0)

        # Ship proper time in years
        tau_years = res["proper_time_sec"] / (365.25 * 86400.0)
        # Coordinate observer time in years
        t_years = res["coordinate_time_sec"] / (365.25 * 86400.0)

        self.assertAlmostEqual(tau_years, 3.56, delta=0.1)
        self.assertAlmostEqual(t_years, 6.00, delta=0.1)
        self.assertGreater(res["peak_velocity_c_fraction"], 0.94)
        self.assertLess(res["peak_velocity_c_fraction"], 0.96)

    def test_lorentz_time_dilation_factor(self):
        """
        Benchmark: Lorentz gamma factor gamma = 1 / sqrt(1 - beta^2)
        - At v = 0.8c: gamma = 1 / sqrt(1 - 0.64) = 1 / 0.6 = 1.6667
        - At v = 0.99c: gamma = 1 / sqrt(1 - 0.9801) = 1 / 0.141067 = 7.0888
        """
        res_08 = calc_time_dilation(beta=0.8)
        self.assertAlmostEqual(res_08["kinematic"]["gamma"], 1.6667, delta=0.001)

        res_099 = calc_time_dilation(beta=0.99)
        self.assertAlmostEqual(res_099["kinematic"]["gamma"], 7.0888, delta=0.001)

    def test_hohmann_transfer_earth_to_mars(self):
        """
        Benchmark: Hohmann transfer from Earth (1.0 AU) to Mars (1.524 AU).
        Published orbital mechanics reference:
        - Total delta-v from LEO insertion / heliocentric burn: ~5.59 km/s total delta-v
        - One-way transfer transit duration: ~259 days (~0.71 years)
        """
        res = calc_orbital_transfer(primary_body="sun", r1_m=1.0 * AU, r2_m=1.5237 * AU)
        self.assertAlmostEqual(res["delta_v_total_kms"], 5.59, delta=0.2)
        days = res["transfer_duration_sec"] / 86400.0
        self.assertAlmostEqual(days, 259.0, delta=5.0)

    # -------------------------------------------------------------------------
    # 2. Planetary Climate & Insolation Reference Benchmarks
    # -------------------------------------------------------------------------
    def test_earth_solar_insolation_and_temperature(self):
        """
        Benchmark: Solar constant at 1 AU with 1.0 Solar Luminosity.
        - Solar Flux: 1361 W/m^2
        - Blackbody Equilibrium Temp (A=0.30): ~254.8 K (-18.3°C)
        - Earth Surface Temp with greenhouse (+33K): ~287.8 K (~14.6°C)
        """
        res = calc_planetary_insolation(
            stellar_luminosity=1.0,
            semi_major_axis_au=1.0,
            bond_albedo=0.30,
            greenhouse_warming_k=33.0,
        )

        self.assertAlmostEqual(res["stellar_flux_w_m2"], 1361.0, delta=1.0)
        self.assertAlmostEqual(res["equilibrium_temp_k"], 254.8, delta=0.5)
        self.assertAlmostEqual(res["surface_temp_c"], 14.6, delta=0.5)
        self.assertTrue(res["liquid_water_habitable"])

    # -------------------------------------------------------------------------
    # 3. Tactical Combat Lanchester Square Law Mechanics
    # -------------------------------------------------------------------------
    def test_lanchester_square_law_combat(self):
        """
        Benchmark: Lanchester's Square Law for modern ranged combat:
        N0^2 * beta vs M0^2 * alpha.
        Force A: 1000 troops, effectiveness 1.0
        Force B: 500 troops, effectiveness 1.0
        Force A should win with ~866 survivors (sqrt(1000^2 - 500^2) = sqrt(750000) = 866.02).
        """
        sim = calc_lanchester_battle(
            attacker_force=1000,
            defender_force=500,
            attacker_eff=1.0,
            defender_eff=1.0,
            law="square",
            rounds=100,
            morale_threshold=1.0,
        )

        self.assertEqual(sim["victor"], "Attacker")
        # Analytical result is ~866 troops
        self.assertAlmostEqual(sim["final_attacker"], 866, delta=25)
        self.assertEqual(sim["final_defender"], 0)

    def test_tactical_sim_monte_carlo(self):
        """
        Benchmark: Tactical skirmish simulation and Monte Carlo win rate.
        """
        side1 = [{"name": "Knight", "hp": 50, "armor": 5, "attack": 10, "damage": 15, "type": "melee", "agility": 5, "morale": 90}]
        side2 = [{"name": "Goblin", "hp": 10, "armor": 1, "attack": 2, "damage": 3, "type": "melee", "agility": 2, "morale": 20}]
        battle = simulate_single_battle(side1, side2, terrain="open_field")
        self.assertIn(battle["winner"], [0, 1, 2])
        self.assertEqual(battle["winner"], 1)

        mc = run_monte_carlo(side1, side2, terrain="open_field", runs=10)
        self.assertEqual(mc["runs"], 10)
        self.assertEqual(mc["side1_win_rate"], 100.0)

    # -------------------------------------------------------------------------
    # 4. Planetary Calendar & Moon Phase Math
    # -------------------------------------------------------------------------
    def test_moon_phase_geometry_and_illumination(self):
        """
        Benchmark: Moon phase illumination cosine wave.
        - Day 0: New Moon (0% illumination)
        - Mid-cycle (day 14 of 28): Full Moon (100% illumination)
        - Quarter-cycle (day 7 of 28): First Quarter (50% illumination)
        """
        moon = {"name": "Luna", "period": 28.0, "offset": 0.0}

        new_moon = get_moon_phase(0, moon)
        self.assertEqual(new_moon["phase_name"], "New Moon")
        self.assertAlmostEqual(new_moon["illumination_percent"], 0.0, delta=1.0)

        full_moon = get_moon_phase(14, moon)
        self.assertEqual(full_moon["phase_name"], "Full Moon")
        self.assertAlmostEqual(full_moon["illumination_percent"], 100.0, delta=1.0)

        quarter_moon = get_moon_phase(7, moon)
        self.assertAlmostEqual(quarter_moon["illumination_percent"], 50.0, delta=2.0)

    def test_calendar_day_indexing_roundtrip(self):
        cal_spec = {
            "days_per_year": 360,
            "months": [{"name": f"Month_{i}", "days": 30} for i in range(1, 13)],
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        }

        # Year 3, Month 5, Day 12
        abs_day = date_to_absolute_day(year=3, month_idx=4, day=12, cal_spec=cal_spec)
        # Convert back
        yr, m_idx, dy, dow = absolute_day_to_date(abs_day, cal_spec)
        self.assertEqual(yr, 3)
        self.assertEqual(m_idx, 4)
        self.assertEqual(dy, 12)

    # -------------------------------------------------------------------------
    # 5. Stylistics & Readability Metrics Benchmark
    # -------------------------------------------------------------------------
    def test_stylistics_readability_metrics(self):
        """
        Benchmark standard passage readability.
        """
        sample_prose = """
        The ancient castle stood tall on the cliff overlooking the stormy sea.
        Lightning illuminated the dark spires as thunder echoed across the valley.
        The guards remained watchful at their posts, gripping their spears with nervous tension.
        Inside the grand hall, the king reviewed the war maps by flickering candlelight.
        Generals debated the strategic maneuvers needed to repel the incoming invasion.
        Every soldier knew that dawn would bring the decisive battle of their lifetime.
        The scouts had reported enemy ships gathering near the northern harbor.
        Archers inspected their bowstrings and sharpened arrows in quiet determination.
        In the temple, priests chanted prayers for victory and protection.
        No one slept that night as the kingdom prepared for its ultimate defense.
        """
        metrics = analyze_readability_rhythm(sample_prose)
        self.assertGreater(metrics["word_count"], 100)
        self.assertIsNone(metrics["sample_size_warning"])
        self.assertGreater(metrics["flesch_reading_ease"], 40.0)
        self.assertLess(metrics["flesch_reading_ease"], 85.0)

    def test_sample_size_warning_on_short_text(self):
        short_prose = "He ran fast. She followed closely behind."
        metrics = analyze_readability_rhythm(short_prose)
        self.assertLess(metrics["word_count"], 100)
        self.assertIsNotNone(metrics["sample_size_warning"])
        self.assertIn("fewer than 100 words", metrics["sample_size_warning"])

        voice_res = compute_voice_profile(["Hello.", "Wait here."], char_name="Alden")
        self.assertLess(voice_res["total_words"], 100)
        self.assertIsNotNone(voice_res["sample_size_warning"])


if __name__ == "__main__":
    unittest.main()
