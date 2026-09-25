"""
tests/test_writing_sprint.py
============================
Test suite for the Ars Arcanum Writing Sprint & Session Analytics engine.

15 tests covering:
  - Sprint lifecycle (start, end, status)
  - Session loading and serialisation
  - Velocity statistics
  - Daily streak computation
  - Best-session lookup
  - HTML report generation
"""

import json
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow running from repo root or directly
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.writing_sprint import (
    SprintSession,
    compute_daily_streak,
    compute_velocity_stats,
    end_sprint,
    generate_sprint_report_html,
    get_best_session,
    get_sprint_status,
    load_sessions,
    start_sprint,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session(
    start_ts: str,
    words: int = 300,
    duration: float = 3.0,
    target: int = 500,
    manuscript_dir: str = "fixtures/ms",
) -> SprintSession:
    """Create a SprintSession with pre-calculated WPM for test fixtures."""
    wpm = round(words / max(duration, 0.1), 2)
    return SprintSession(
        session_id=start_ts,
        start_ts=start_ts,
        end_ts=(datetime.fromisoformat(start_ts) + timedelta(minutes=duration)).isoformat(),
        target_words=target,
        actual_words=words,
        duration_minutes=duration,
        wpm=wpm,
        manuscript_dir=manuscript_dir,
    )


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestWritingSprintEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name)
        self.arcanum_dir = self.ms_dir / ".arcanum"
        self.arcanum_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.arcanum_dir / ".sprint_state.json"
        self.log_file = self.arcanum_dir / ".sprint_log.jsonl"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------
    # 1. start_sprint creates state file
    # ------------------------------------------------------------------
    def test_start_sprint_creates_state_file(self) -> None:
        """start_sprint() must write a JSON state file containing session_id."""
        start_sprint(
            target_words=300,
            duration_minutes=10.0,
            manuscript_dir=self.ms_dir,
            state_file=self.state_file,
        )
        self.assertTrue(self.state_file.exists(), "State file was not created")
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.assertIn("session_id", state)
        self.assertIsInstance(state["session_id"], str)
        self.assertGreater(len(state["session_id"]), 0)

    # ------------------------------------------------------------------
    # 2. start_sprint default target words
    # ------------------------------------------------------------------
    def test_start_sprint_default_target(self) -> None:
        """start_sprint() with no target_words argument defaults to 500."""
        start_sprint(manuscript_dir=self.ms_dir, state_file=self.state_file)
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.assertEqual(state["target_words"], 500)

    # ------------------------------------------------------------------
    # 3. end_sprint creates log entry readable by load_sessions
    # ------------------------------------------------------------------
    def test_end_sprint_creates_log_entry(self) -> None:
        """start + end_sprint(300) → log file exists and load_sessions returns 1 session."""
        start_sprint(manuscript_dir=self.ms_dir, state_file=self.state_file)
        # Small sleep so elapsed time > 0
        time.sleep(0.05)
        end_sprint(word_count=300, state_file=self.state_file, log_file=self.log_file)

        self.assertTrue(self.log_file.exists(), "Log file was not created after end_sprint")
        sessions = load_sessions(self.log_file)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].actual_words, 300)

    # ------------------------------------------------------------------
    # 4. end_sprint computes wpm > 0
    # ------------------------------------------------------------------
    def test_end_sprint_computes_wpm(self) -> None:
        """end_sprint with 300 words and some elapsed time → wpm > 0."""
        start_sprint(manuscript_dir=self.ms_dir, state_file=self.state_file)
        time.sleep(0.05)
        session = end_sprint(word_count=300, state_file=self.state_file, log_file=self.log_file)
        self.assertGreater(session.wpm, 0.0)
        self.assertEqual(session.actual_words, 300)

    # ------------------------------------------------------------------
    # 5. get_sprint_status returns dict for active sprint
    # ------------------------------------------------------------------
    def test_get_sprint_status_active(self) -> None:
        """get_sprint_status() returns dict with session_id when sprint is active."""
        start_sprint(manuscript_dir=self.ms_dir, state_file=self.state_file)
        status = get_sprint_status(self.state_file)
        self.assertIsNotNone(status)
        self.assertIn("session_id", status)
        self.assertIn("elapsed_minutes", status)
        self.assertIn("remaining_minutes", status)

    # ------------------------------------------------------------------
    # 6. get_sprint_status returns None when no state file
    # ------------------------------------------------------------------
    def test_get_sprint_status_no_active(self) -> None:
        """get_sprint_status() returns None when no state file exists."""
        result = get_sprint_status(self.state_file)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # 7. load_sessions returns empty list when no log file
    # ------------------------------------------------------------------
    def test_load_sessions_empty(self) -> None:
        """load_sessions() returns [] when log file does not exist."""
        nonexistent = self.ms_dir / "no_such.jsonl"
        result = load_sessions(nonexistent)
        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # 8. load_sessions returns all sessions for multiple sprints
    # ------------------------------------------------------------------
    def test_load_sessions_multiple(self) -> None:
        """Running 3 sprints → load_sessions returns exactly 3 sessions."""
        for i in range(3):
            start_sprint(manuscript_dir=self.ms_dir, state_file=self.state_file)
            time.sleep(0.02)
            end_sprint(
                word_count=100 + i * 50,
                state_file=self.state_file,
                log_file=self.log_file,
            )

        sessions = load_sessions(self.log_file)
        self.assertEqual(len(sessions), 3)

    # ------------------------------------------------------------------
    # 9. compute_velocity_stats basic
    # ------------------------------------------------------------------
    def test_compute_velocity_stats_basic(self) -> None:
        """2 sessions each with 100 WPM → avg_wpm == 100.0."""
        now = datetime.now()
        sessions = [
            _make_session(
                (now - timedelta(minutes=10)).isoformat(),
                words=300,
                duration=3.0,  # 100 wpm
            ),
            _make_session(
                now.isoformat(),
                words=300,
                duration=3.0,  # 100 wpm
            ),
        ]
        stats = compute_velocity_stats(sessions)
        self.assertEqual(stats["total_sessions"], 2)
        self.assertAlmostEqual(stats["avg_wpm"], 100.0, places=1)
        self.assertEqual(stats["total_words"], 600)

    # ------------------------------------------------------------------
    # 10. compute_velocity_stats with empty list
    # ------------------------------------------------------------------
    def test_compute_velocity_stats_empty(self) -> None:
        """compute_velocity_stats([]) → total_sessions == 0 and avg_wpm == 0.0."""
        stats = compute_velocity_stats([])
        self.assertEqual(stats["total_sessions"], 0)
        self.assertEqual(stats["avg_wpm"], 0.0)
        self.assertEqual(stats["total_words"], 0)

    # ------------------------------------------------------------------
    # 11. compute_daily_streak single day
    # ------------------------------------------------------------------
    def test_compute_daily_streak_single_day(self) -> None:
        """One session written today → current_streak_days == 1."""
        today_ts = datetime.now().isoformat()
        sessions = [_make_session(today_ts, words=200)]
        streak = compute_daily_streak(sessions)
        self.assertEqual(streak["current_streak_days"], 1)
        self.assertGreaterEqual(streak["longest_streak_days"], 1)
        self.assertEqual(streak["today_words"], 200)

    # ------------------------------------------------------------------
    # 12. get_best_session returns highest WPM session
    # ------------------------------------------------------------------
    def test_get_best_session(self) -> None:
        """3 sessions with different WPM → get_best_session returns the highest."""
        now = datetime.now()
        sessions = [
            _make_session((now - timedelta(hours=2)).isoformat(), words=100, duration=2.0),   # 50 wpm
            _make_session((now - timedelta(hours=1)).isoformat(), words=300, duration=2.0),   # 150 wpm
            _make_session(now.isoformat(), words=200, duration=4.0),                          # 50 wpm
        ]
        best = get_best_session(sessions)
        self.assertIsNotNone(best)
        self.assertAlmostEqual(best.wpm, 150.0, places=0)
        self.assertEqual(best.actual_words, 300)

    # ------------------------------------------------------------------
    # 13. generate_sprint_report_html creates file with CSP header
    # ------------------------------------------------------------------
    def test_generate_sprint_report_html(self) -> None:
        """generate_sprint_report_html() → file exists and contains CSP meta tag."""
        out = self.ms_dir / "report.html"
        stats = compute_velocity_stats([])
        streak = compute_daily_streak([])
        generate_sprint_report_html(stats, streak, [], out)
        self.assertTrue(out.exists(), "HTML report was not created")
        content = out.read_text(encoding="utf-8")
        self.assertIn("default-src", content)
        self.assertIn("Content-Security-Policy", content)

    # ------------------------------------------------------------------
    # 14. HTML report contains WPM data
    # ------------------------------------------------------------------
    def test_html_contains_wpm_data(self) -> None:
        """generate_sprint_report_html with real stats → HTML contains 'WPM'."""
        now = datetime.now()
        sessions = [_make_session(now.isoformat(), words=300, duration=3.0)]
        stats = compute_velocity_stats(sessions)
        streak = compute_daily_streak(sessions)
        out = self.ms_dir / "wpm_report.html"
        generate_sprint_report_html(stats, streak, sessions, out)
        content = out.read_text(encoding="utf-8")
        self.assertTrue(
            "WPM" in content or "wpm" in content,
            "HTML report does not contain WPM label",
        )

    # ------------------------------------------------------------------
    # 15. SprintSession serialisation round-trip
    # ------------------------------------------------------------------
    def test_sprint_session_serialization(self) -> None:
        """SprintSession → dict → JSON → dict → SprintSession preserves all fields."""
        original = SprintSession(
            session_id="2026-09-21T10:00:00",
            start_ts="2026-09-21T10:00:00",
            end_ts="2026-09-21T10:25:00",
            target_words=500,
            actual_words=420,
            duration_minutes=25.0,
            wpm=16.8,
            manuscript_dir="/home/author/novel",
            notes="Great flow today!",
        )
        serialised = json.dumps(original.to_dict())
        restored = SprintSession.from_dict(json.loads(serialised))

        self.assertEqual(restored.session_id, original.session_id)
        self.assertEqual(restored.start_ts, original.start_ts)
        self.assertEqual(restored.end_ts, original.end_ts)
        self.assertEqual(restored.target_words, original.target_words)
        self.assertEqual(restored.actual_words, original.actual_words)
        self.assertAlmostEqual(restored.duration_minutes, original.duration_minutes, places=5)
        self.assertAlmostEqual(restored.wpm, original.wpm, places=5)
        self.assertEqual(restored.manuscript_dir, original.manuscript_dir)
        self.assertEqual(restored.notes, original.notes)


if __name__ == "__main__":
    unittest.main()
