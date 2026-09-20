#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Custom Planetary Calendars & Multi-Moon Phase Engine (scripts/lib/calendar.py).
Covers calendar spec loading, date arithmetic, absolute day conversions, multi-moon synodic phases,
syzygy/conjunction detection, and HTML export.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.calendar import (
    load_calendar_spec,
    date_to_absolute_day,
    absolute_day_to_date,
    get_moon_phase,
    detect_celestial_events,
    render_month_terminal_grid,
    generate_calendar_html_report,
)


class TestCalendarEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.cosmology_dir = self.world_dir / "Cosmology"
        self.cosmology_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_calendar_spec(self):
        (self.cosmology_dir / "Pantheon.md").write_text("""---
name: "Solar Pantheon"
type: cosmology
days_per_year: 400
hours_per_day: 28
months:
  - "Dawn"
  - "Sunhigh"
  - "Dusk"
  - "Nightfall"
weekdays:
  - "Moonday"
  - "Fireday"
  - "Waterday"
  - "Earthday"
  - "Starday"
moons:
  - name: "Selene"
    period: 25.0
    offset: 0.0
---
""", encoding="utf-8")

        spec = load_calendar_spec(self.world_dir)
        self.assertEqual(spec["days_per_year"], 400)
        self.assertEqual(spec["hours_per_day"], 28)
        self.assertEqual(len(spec["months"]), 4)
        self.assertEqual(len(spec["weekdays"]), 5)
        self.assertEqual(spec["moons"][0]["name"], "Selene")

    def test_date_conversions_roundtrip(self):
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": f"M{i+1}", "days": 30} for i in range(12)],
            "weekdays": ["D1", "D2", "D3", "D4", "D5", "D6"],
            "moons": [],
        }

        # Day 1 of Year 1
        abs1 = date_to_absolute_day(1, 0, 1, cal_spec)
        self.assertEqual(abs1, 0)
        y, m, d, dow = absolute_day_to_date(abs1, cal_spec)
        self.assertEqual((y, m, d, dow), (1, 0, 1, 0))

        # Year 3, Month 4 (idx 3), Day 15
        abs_val = date_to_absolute_day(3, 3, 15, cal_spec)
        # (3-1)*360 + 3*30 + 14 = 720 + 90 + 14 = 824
        self.assertEqual(abs_val, 824)
        y, m, d, dow = absolute_day_to_date(abs_val, cal_spec)
        self.assertEqual((y, m, d), (3, 3, 15))
        self.assertEqual(dow, 824 % 6)

    def test_moon_phases_synodic(self):
        moon = {"name": "Lumina", "period": 28.0, "offset": 0.0}

        # Day 0: New Moon (0% progress)
        p0 = get_moon_phase(0, moon)
        self.assertEqual(p0["phase_name"], "New Moon")
        self.assertEqual(p0["glyph"], "🌑")

        # Day 7: First Quarter (25% progress)
        p7 = get_moon_phase(7, moon)
        self.assertEqual(p7["phase_name"], "First Quarter")
        self.assertEqual(p7["glyph"], "🌓")

        # Day 14: Full Moon (50% progress)
        p14 = get_moon_phase(14, moon)
        self.assertEqual(p14["phase_name"], "Full Moon")
        self.assertEqual(p14["glyph"], "🌕")

        # Day 21: Third Quarter (75% progress)
        p21 = get_moon_phase(21, moon)
        self.assertEqual(p21["phase_name"], "Third Quarter")
        self.assertEqual(p21["glyph"], "🌗")

    def test_syzygy_conjunction_detection(self):
        moons = [
            {"name": "MoonA", "period": 20.0, "offset": 0.0},
            {"name": "MoonB", "period": 40.0, "offset": 0.0},
        ]
        # At day 10: MoonA at 10/20=0.5 (Full), MoonB at 10/40=0.25 (First Quarter) -> No syzygy
        events10 = detect_celestial_events(10, moons)
        self.assertEqual(len(events10), 0)

        # At day 20: MoonA at 20/20=0 (New), MoonB at 20/40=0.5 (Full) -> No multi-full syzygy
        # At day 40: MoonA at 40/20=0 (New), MoonB at 40/40=0 (New) -> Dark Convergence / Eclipse!
        events40 = detect_celestial_events(40, moons)
        self.assertEqual(len(events40), 1)
        self.assertIn("Dark Convergence", events40[0])

    def test_render_month_terminal_grid(self):
        cal_spec = {
            "world": "Eldoria",
            "days_per_year": 365,
            "months": [{"name": "Primis", "days": 30}],
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "moons": [{"name": "Lumina", "period": 28.0, "offset": 0.0}],
        }
        grid = render_month_terminal_grid(1, 0, cal_spec)
        self.assertIn("Primis 1", grid)
        self.assertIn("Mon", grid)
        self.assertIn("30", grid)

    def test_html_report_generation(self):
        cal_spec = {
            "world": "Eldoria",
            "days_per_year": 365,
            "hours_per_day": 24,
            "months": [{"name": "Solaris", "days": 30}],
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "moons": [{"name": "Lumina", "period": 28.0, "offset": 0.0}],
        }
        out_html = self.world_dir / "calendar.html"
        generate_calendar_html_report(1, 0, cal_spec, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Planetary Calendar", content)
        self.assertIn("Solaris 1", content)

    def test_resolve_world_dir(self):
        from lib.calendar import resolve_world_dir
        resolved = resolve_world_dir(str(self.world_dir))
        self.assertEqual(resolved, str(self.world_dir.resolve()))


if __name__ == "__main__":
    unittest.main()
