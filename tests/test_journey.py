#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Overland & Naval Journey Modeler (scripts/lib/journey.py).
Covers terrain friction modifiers, travel pace calculations, party supply burn,
itinerary generation, and HTML report export.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.journey import (
    parse_distance_km,
    calculate_journey,
    generate_journey_html_report,
)


class TestJourneyEngine(unittest.TestCase):

    def test_parse_distance_km(self):
        self.assertEqual(parse_distance_km("150 km"), 150.0)
        self.assertAlmostEqual(parse_distance_km("100 miles"), 160.934, places=2)
        self.assertAlmostEqual(parse_distance_km("10 leagues"), 48.28, places=1)
        self.assertEqual(parse_distance_km("5000 m"), 5.0)

    def test_calculate_journey_road_foot(self):
        # 48 km on paved road (1.0x) at normal foot pace (24 km/day) -> 2.0 days
        res = calculate_journey(distance_km=48.0, terrain="road", mode="foot-normal", party_size=4)
        self.assertEqual(res["effective_speed_km_day"], 24.0)
        self.assertEqual(res["total_days"], 2.0)
        self.assertEqual(res["supplies_required"]["rations_food_kg"], 8.0) # 4 people * 1 kg/day * 2 days
        self.assertEqual(res["supplies_required"]["water_liters"], 24.0)   # 4 people * 3 L/day * 2 days
        self.assertEqual(len(res["itinerary"]), 2)

    def test_calculate_journey_mountain_friction(self):
        # 84 km through mountains (0.35x) at normal foot pace (24 km/day -> 8.4 km/day) -> 10 days
        res = calculate_journey(distance_km=84.0, terrain="mountains", mode="foot-normal", party_size=2)
        self.assertAlmostEqual(res["effective_speed_km_day"], 8.4, places=2)
        self.assertEqual(res["total_days"], 10.0)
        self.assertEqual(res["supplies_required"]["rations_food_kg"], 20.0)
        self.assertEqual(len(res["itinerary"]), 10)

    def test_calculate_journey_cavalry_and_mounts(self):
        # 96 km on plains (0.75x) on horse trot (48 km/day -> 36 km/day) with 2 mounts
        res = calculate_journey(distance_km=72.0, terrain="plains", mode="horse-trot", party_size=2, mounts=2)
        self.assertEqual(res["effective_speed_km_day"], 36.0)
        self.assertEqual(res["total_days"], 2.0)
        self.assertEqual(res["supplies_required"]["mount_feed_kg"], 32.0) # 2 mounts * 8 kg * 2 days
        self.assertEqual(res["supplies_required"]["mount_water_liters"], 100.0) # 2 mounts * 25 L * 2 days

    def test_calculate_journey_desert_water_burn(self):
        # In desert, water burn increases to 4.5 L/person/day
        res = calculate_journey(distance_km=40.0, terrain="desert", mode="foot-fast", party_size=2)
        self.assertAlmostEqual(res["supplies_required"]["water_liters"], 2 * 4.5 * res["total_days"], places=1)

    def test_html_report_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "journey_report.html"
            journey = calculate_journey(distance_km=100.0, terrain="forest", mode="foot-normal")
            generate_journey_html_report(journey, out_file)
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("Expedition Route & Journey Plan", content)


if __name__ == "__main__":
    unittest.main()
