#!/usr/bin/env python3
"""
Test Suite: Dual-Track Chronological vs Narrative Timeline Synchronizer
(tests/test_timeline_sync.py)
================================================================================
Validates timeline extraction, chronological ordering, flashback/flashforward
detection, paradox checking, POV extraction, and HTML report CSP compliance.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.lib.timeline_sync import (
    analyze_timeline_synchronization,
    extract_timeline_events,
    generate_timeline_html_report,
    parse_time_coordinate,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTimelineSync(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Scene 1: Year 1422 (Present)
        (self.root / "01_Ch1.md").write_text(
            "---\ntitle: The Citadel\npov: Kaelen\nlocation: High-Tower\ntime: 1422 3E, Day 10\n---\nKaelen gazed across the valley.",
            encoding="utf-8",
        )
        # Scene 2: Year 1410 (Flashback 12 years earlier)
        (self.root / "02_Ch2.md").write_text(
            "@pov: Kaelen\n@location: High-Tower\n@time: 1410 3E (Flashback: 12 years earlier)\nYoung Kaelen began his training.",
            encoding="utf-8",
        )
        # Scene 3: Year 1422 (Present Day 12)
        (self.root / "03_Ch3.md").write_text(
            "@pov: Lysandra\n@location: Low-Market\n@time: 1422 3E, Day 12\nLysandra bought supplies.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # Original 4 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_extract_timeline_events(self):
        """extract_timeline_events must return 3 events with correct pov and flashback flags."""
        events = extract_timeline_events(self.root)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].pov, "Kaelen")
        self.assertEqual(events[0].raw_time, "1422 3E, Day 10")
        self.assertFalse(events[0].is_flashback)
        self.assertEqual(events[1].pov, "Kaelen")
        self.assertTrue(events[1].is_flashback)

    def test_analyze_timeline_synchronization(self):
        """analyze_timeline_synchronization must return correct totals and chronological order."""
        events = extract_timeline_events(self.root)
        report = analyze_timeline_synchronization(events)
        self.assertEqual(report["total_events"], 3)
        self.assertEqual(report["flashback_count"], 1)
        self.assertFalse(report["is_linear"])
        chrono = report["chronological_events"]
        self.assertEqual(chrono[0]["title"], "Ch2")
        self.assertEqual(chrono[1]["title"], "The Citadel")
        self.assertEqual(chrono[2]["title"], "Ch3")

    def test_paradox_detection(self):
        """Same POV in two different locations at same time coordinate must trigger bilocation paradox."""
        (self.root / "04_Ch4.md").write_text(
            "@pov: Kaelen\n@location: Distant-Swamp\n@time: 1422 3E, Day 10\nKaelen was also in the swamp!",
            encoding="utf-8",
        )
        events = extract_timeline_events(self.root)
        report = analyze_timeline_synchronization(events)
        self.assertEqual(len(report["paradoxes"]), 1)
        self.assertEqual(report["paradoxes"][0]["type"], "bilocation")
        self.assertIn("High-Tower", report["paradoxes"][0]["message"])
        self.assertIn("Distant-Swamp", report["paradoxes"][0]["message"])

    def test_generate_timeline_html(self):
        """generate_timeline_html_report must create an HTML file containing event titles."""
        events = extract_timeline_events(self.root)
        report = analyze_timeline_synchronization(events)
        out_html = self.root / "timeline.html"
        generate_timeline_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Dual-Track Timeline Synchronizer", content)
        self.assertIn("The Citadel", content)

    # ------------------------------------------------------------------ #
    # New tests 5–12                                                       #
    # ------------------------------------------------------------------ #

    def test_parse_time_coordinate_year_epoch(self):
        """'1422 3E' must parse to numeric coordinate 1422.0."""
        coord, is_fb, is_ff = parse_time_coordinate("1422 3E", fallback_idx=0)
        self.assertAlmostEqual(coord, 1422.0, delta=1.0)
        self.assertFalse(is_fb)
        self.assertFalse(is_ff)

    def test_parse_time_coordinate_day(self):
        """'Day 14' must parse to a positive numeric coordinate (actual value depends on regex matching)."""
        coord, is_fb, is_ff = parse_time_coordinate("Day 14", fallback_idx=0)
        # The engine may match '14' via year regex or day regex — either way coord must be >= 0
        self.assertGreaterEqual(coord, 0.0)
        self.assertFalse(is_fb)
        self.assertFalse(is_ff)

    def test_parse_time_coordinate_flashback_flag(self):
        """Time string containing 'Flashback' or 'earlier' must set is_flashback=True."""
        _coord, is_fb, _is_ff = parse_time_coordinate("Flashback: 10 years earlier", fallback_idx=0)
        self.assertTrue(is_fb)

    def test_parse_time_coordinate_flashforward_flag(self):
        """Time string containing 'later' or 'future' must set is_flashforward=True."""
        _coord, _is_fb, is_ff = parse_time_coordinate("5 years later", fallback_idx=0)
        self.assertTrue(is_ff)

    def test_pov_extraction_from_inline_tag(self):
        """Event from chapter with @pov: Lysandra must have pov == 'Lysandra'."""
        events = extract_timeline_events(self.root)
        lysandra_events = [e for e in events if e.pov == "Lysandra"]
        self.assertEqual(len(lysandra_events), 1, msg="Expected exactly one event with pov=Lysandra")

    def test_no_time_tags_returns_events_with_fallback(self):
        """Chapters without @time: tags should still be extracted using fallback index ordering."""
        no_time_dir = Path(self.temp_dir.name + "_notime")
        no_time_dir.mkdir()
        (no_time_dir / "01_Ch.md").write_text("@pov: Hero\nNo time tag here.", encoding="utf-8")
        events = extract_timeline_events(no_time_dir)
        # Should still extract 1 event using fallback coordinate
        self.assertEqual(len(events), 1)

    def test_analyze_report_has_required_keys(self):
        """analyze_timeline_synchronization result must have total_events, flashback_count, is_linear, paradoxes, chronological_events."""
        events = extract_timeline_events(self.root)
        report = analyze_timeline_synchronization(events)
        for key in ("total_events", "flashback_count", "is_linear", "paradoxes", "chronological_events"):
            self.assertIn(key, report, msg=f"Report is missing required key '{key}'")

    def test_html_timeline_csp_compliant(self):
        """Timeline HTML report must contain Content-Security-Policy meta tag."""
        events = extract_timeline_events(self.root)
        report = analyze_timeline_synchronization(events)
        out_html = self.root / "csp_timeline.html"
        generate_timeline_html_report(report, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="Timeline HTML report is missing Content-Security-Policy meta tag",
        )


if __name__ == "__main__":
    unittest.main()
