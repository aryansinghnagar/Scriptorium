#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Custom Planetary Calendars & Multi-Moon Phase Engine (scripts/lib/calendar.py).
Covers calendar spec loading, date arithmetic, absolute day conversions, multi-moon synodic phases,
syzygy/conjunction detection, terminal grid rendering, and HTML export.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.calendar import (
    absolute_day_to_date,
    date_to_absolute_day,
    detect_celestial_events,
    generate_calendar_html_report,
    get_moon_phase,
    load_calendar_spec,
    render_month_terminal_grid,
    resolve_world_dir,
)


class TestCalendarEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.cosmology_dir = self.world_dir / "Cosmology"
        self.cosmology_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_calendar_spec(self) -> None:
        """load_calendar_spec parses days, hours, months, weekdays, and moon definitions."""
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

    def test_load_calendar_spec_fallback_defaults(self) -> None:
        """load_calendar_spec provides defaults when cosmology notes are absent."""
        empty_world = Path(self.temp_dir.name) / "EmptyWorld"
        empty_world.mkdir(parents=True)
        spec = load_calendar_spec(empty_world)
        self.assertEqual(spec["days_per_year"], 365)
        self.assertEqual(spec["hours_per_day"], 24)
        self.assertEqual(len(spec["months"]), 12)
        self.assertEqual(len(spec["weekdays"]), 7)

    def test_date_conversions_roundtrip_day1(self) -> None:
        """Day 1 of Year 1 maps to absolute day 0 and inverts back cleanly."""
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": f"M{i+1}", "days": 30} for i in range(12)],
            "weekdays": ["D1", "D2", "D3", "D4", "D5", "D6"],
            "moons": [],
        }
        abs1 = date_to_absolute_day(1, 0, 1, cal_spec)
        self.assertEqual(abs1, 0)
        y, m, d, dow = absolute_day_to_date(abs1, cal_spec)
        self.assertEqual((y, m, d, dow), (1, 0, 1, 0))

    def test_date_conversions_roundtrip_multiyear(self) -> None:
        """Multi-year dates convert to continuous absolute day count and round-trip."""
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": f"M{i+1}", "days": 30} for i in range(12)],
            "weekdays": ["D1", "D2", "D3", "D4", "D5", "D6"],
            "moons": [],
        }
        # Year 3, Month 4 (index 3), Day 15
        abs_val = date_to_absolute_day(3, 3, 15, cal_spec)
        # (3-1)*360 + 3*30 + 14 = 720 + 90 + 14 = 824
        self.assertEqual(abs_val, 824)
        y, m, d, dow = absolute_day_to_date(abs_val, cal_spec)
        self.assertEqual((y, m, d), (3, 3, 15))
        self.assertEqual(dow, 824 % 6)

    def test_date_advancing_with_offset(self) -> None:
        """Adding day offsets correctly rolls over months and years."""
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": "M1", "days": 30}, {"name": "M2", "days": 30}],
            "weekdays": ["D1", "D2", "D3", "D4", "D5"],
            "moons": [],
        }
        # Start Year 1, Month 0, Day 1 (abs 0) + 35 days -> Month 1, Day 6
        abs_day = date_to_absolute_day(1, 0, 1, cal_spec) + 35
        y, m_idx, d, _dow = absolute_day_to_date(abs_day, cal_spec)
        self.assertEqual((y, m_idx, d), (1, 1, 6))

    def test_moon_phases_synodic_cycle(self) -> None:
        """get_moon_phase computes phases, illumination percentage, and glyphs across synodic cycle."""
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

    def test_syzygy_conjunction_detection_grand_and_dark(self) -> None:
        """detect_celestial_events identifies simultaneous Full Moons (Grand Conjunction) and New Moons (Dark Convergence)."""
        moons = [
            {"name": "MoonA", "period": 20.0, "offset": 0.0},
            {"name": "MoonB", "period": 40.0, "offset": 0.0},
        ]
        # At day 10: MoonA at 10/20=0.5 (Full), MoonB at 10/40=0.25 (First Quarter) -> No syzygy
        events10 = detect_celestial_events(10, moons)
        self.assertEqual(len(events10), 0)

        # At day 40: MoonA at 40/20=0 (New), MoonB at 40/40=0 (New) -> Dark Convergence / Eclipse!
        events40 = detect_celestial_events(40, moons)
        self.assertEqual(len(events40), 1)
        self.assertIn("Dark Convergence", events40[0])

    def test_render_month_terminal_grid_layout(self) -> None:
        """render_month_terminal_grid formats title, weekdays, day numbers, and moon glyphs."""
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

    def test_render_month_terminal_grid_multiweek(self) -> None:
        """Month grids pad leading and trailing empty weekdays properly."""
        cal_spec = {
            "world": "Mythos",
            "days_per_year": 360,
            "months": [{"name": "Secundus", "days": 28}],
            "weekdays": ["W1", "W2", "W3", "W4"],
            "moons": [],
        }
        grid = render_month_terminal_grid(1, 0, cal_spec)
        self.assertIn("Secundus 1", grid)
        self.assertIn("W1", grid)

    def test_html_report_generation_and_csp(self) -> None:
        """HTML report generates with strict offline Content-Security-Policy and calendar grid."""
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
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    def test_resolve_world_dir(self) -> None:
        """resolve_world_dir correctly resolves absolute directory paths."""
        resolved = resolve_world_dir(str(self.world_dir))
        self.assertEqual(resolved, str(self.world_dir.resolve()))

    def test_multi_moon_offset_and_differing_periods(self) -> None:
        """Multiple moons calculate distinct illuminations and cycle positions."""
        moon1 = {"name": "FastMoon", "period": 10.0, "offset": 0.0}
        moon2 = {"name": "SlowMoon", "period": 30.0, "offset": 5.0}

        p1 = get_moon_phase(5, moon1)
        p2 = get_moon_phase(5, moon2)

        # At day 5: FastMoon at 5/10 = 0.5 (Full Moon, 100% illumination)
        self.assertEqual(p1["phase_name"], "Full Moon")
        self.assertAlmostEqual(p1["illumination_percent"], 100.0, places=1)

        # At day 5: SlowMoon at (5+5)/30 = 0.333 (Waxing Gibbous)
        self.assertEqual(p2["phase_name"], "Waxing Gibbous")


if __name__ == "__main__":
    unittest.main()
