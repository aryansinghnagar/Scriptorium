#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Writing Sprint & Session Analytics Engine
===============================================================
scripts/lib/writing_sprint.py

Zero-dependency, offline writing sprint timer and productivity analytics system.

Capabilities:
1. Sprint Session Management:
   - start_sprint(target_words, duration_minutes, manuscript_dir, state_file): writes atomic .sprint_state.json
   - end_sprint(word_count, state_file, log_file): finalizes session, appends to .sprint_log.jsonl
   - get_sprint_status(state_file): reads current session state
2. Session Analytics:
   - load_sessions(log_file) -> list[SprintSession]: loads all past sessions
   - compute_velocity_stats(sessions) -> dict: avg_wpm, best_wpm, total_words, total_sessions, total_duration_min
   - compute_daily_streak(sessions) -> dict: current_streak_days, longest_streak_days, today_words
   - get_best_session(sessions) -> SprintSession | None
3. HTML Report:
   - generate_sprint_report_html(stats, streak, sessions, output_path): standalone offline CSP-compliant HTML dashboard
4. CLI: main(argv) dispatching 'start', 'stop', 'status', 'stats', 'report' subcommands
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]

logger = logging.getLogger("arcanum.writing_sprint")

# ---------------------------------------------------------------------------
# Sentinel defaults (avoids mutable defaults in function signatures)
# ---------------------------------------------------------------------------
_UNSET = object()

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SprintSession:
    """Represents a single completed writing sprint."""

    session_id: str          # ISO timestamp string used as unique key
    start_ts: str            # ISO datetime string (start of sprint)
    end_ts: str              # ISO datetime string (empty string if ongoing)
    target_words: int        # Word-count goal set at sprint start
    actual_words: int        # Words actually written
    duration_minutes: float  # Elapsed time in minutes
    wpm: float               # Words per minute
    manuscript_dir: str      # Absolute path of manuscript directory
    notes: str = field(default="")  # Optional freeform notes

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain dict suitable for JSON serialisation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> SprintSession:
        """Reconstruct a SprintSession from a plain dict."""
        return cls(
            session_id=data["session_id"],
            start_ts=data["start_ts"],
            end_ts=data.get("end_ts", ""),
            target_words=int(data["target_words"]),
            actual_words=int(data["actual_words"]),
            duration_minutes=float(data["duration_minutes"]),
            wpm=float(data["wpm"]),
            manuscript_dir=data.get("manuscript_dir", ""),
            notes=data.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _arcanum_dir(manuscript_dir: Path) -> Path:
    """Return the hidden .arcanum directory inside *manuscript_dir*."""
    return manuscript_dir / ".arcanum"


def _default_state_file(manuscript_dir: Path) -> Path:
    return _arcanum_dir(manuscript_dir) / ".sprint_state.json"


def _default_log_file(manuscript_dir: Path) -> Path:
    return _arcanum_dir(manuscript_dir) / ".sprint_log.jsonl"


def _ensure_arcanum_dir(manuscript_dir: Path) -> None:
    """Create .arcanum/ directory tree if absent."""
    _arcanum_dir(manuscript_dir).mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    """Return current UTC-local ISO timestamp (no timezone suffix for simplicity)."""
    return datetime.now().isoformat()


def _parse_iso(ts: str) -> datetime:
    """Parse an ISO timestamp string produced by _now_iso()."""
    # Handle fractional seconds gracefully
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        # Fallback: strip sub-second portion and retry
        return datetime.fromisoformat(ts[:19])


def _wpm(words: int, minutes: float) -> float:
    """Calculate words per minute, guarding against near-zero durations."""
    return round(words / max(minutes, 0.1), 2)


# ---------------------------------------------------------------------------
# Sprint Session Management
# ---------------------------------------------------------------------------

def start_sprint(
    target_words: int = 500,
    duration_minutes: float = 25.0,
    manuscript_dir: Path = Path("."),
    state_file: Path | None = None,
) -> dict:
    """
    Begin a new writing sprint and persist its state atomically.

    Parameters
    ----------
    target_words:     Word-count goal for this sprint.
    duration_minutes: Planned sprint length in minutes.
    manuscript_dir:   Root directory of the manuscript being worked on.
    state_file:       Override the default state-file location.

    Returns
    -------
    State dict written to disk.
    """
    manuscript_dir = manuscript_dir.resolve()
    state_file = state_file if state_file is not None else _default_state_file(manuscript_dir)
    _ensure_arcanum_dir(manuscript_dir)

    now = _now_iso()
    state: dict = {
        "session_id": now,
        "start_ts": now,
        "end_ts": "",
        "target_words": target_words,
        "duration_minutes": duration_minutes,
        "manuscript_dir": str(manuscript_dir),
    }
    atomic_write(state_file, json.dumps(state, indent=2))
    logger.info("Sprint started: %s (target=%d words, %g min)", now, target_words, duration_minutes)
    return state


def end_sprint(
    word_count: int,
    state_file: Path | None = None,
    log_file: Path | None = None,
) -> SprintSession:
    """
    Finalise an active sprint.

    Reads the persisted sprint state, computes elapsed time and WPM, constructs
    a :class:`SprintSession`, appends a JSON line to *log_file*, and removes the
    state file.

    Parameters
    ----------
    word_count: Actual words written during the sprint.
    state_file: Override the default state-file path.
    log_file:   Override the default JSONL log-file path.

    Returns
    -------
    The completed :class:`SprintSession`.

    Raises
    ------
    FileNotFoundError: If no active sprint state file can be found.
    """
    # ---- resolve state file ------------------------------------------------
    if state_file is None:
        # Try to find state in current directory
        state_file = _default_state_file(Path(".").resolve())

    if not state_file.exists():
        raise FileNotFoundError(f"No active sprint state found at {state_file}")

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError, KeyError) as exc:
        raise ValueError(f"Sprint state file is corrupt: {exc}") from exc

    manuscript_dir = Path(state.get("manuscript_dir", str(state_file.parent.parent)))

    # ---- resolve log file --------------------------------------------------
    if log_file is None:
        log_file = _default_log_file(manuscript_dir)

    _ensure_arcanum_dir(manuscript_dir)

    # ---- compute metrics ---------------------------------------------------
    end_ts = _now_iso()
    start_dt = _parse_iso(state["start_ts"])
    end_dt = _parse_iso(end_ts)
    elapsed_minutes = round((end_dt - start_dt).total_seconds() / 60.0, 4)

    session = SprintSession(
        session_id=state["session_id"],
        start_ts=state["start_ts"],
        end_ts=end_ts,
        target_words=int(state["target_words"]),
        actual_words=word_count,
        duration_minutes=elapsed_minutes,
        wpm=_wpm(word_count, elapsed_minutes),
        manuscript_dir=str(manuscript_dir),
    )

    # ---- append to JSONL log -----------------------------------------------
    existing_content = ""
    if log_file.exists():
        try:
            existing_content = log_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Could not read existing log file %s: %s", log_file, exc)

    new_line = json.dumps(session.to_dict()) + "\n"
    atomic_write(log_file, existing_content + new_line)

    # ---- remove state file -------------------------------------------------
    try:
        state_file.unlink()
    except OSError as exc:
        logger.warning("Could not remove state file %s: %s", state_file, exc)

    logger.info(
        "Sprint ended: %s — %d words in %.1f min (%.1f WPM)",
        session.session_id,
        session.actual_words,
        session.duration_minutes,
        session.wpm,
    )
    return session


def get_sprint_status(state_file: Path) -> dict | None:
    """
    Return the current sprint state dict, or *None* if no sprint is active.

    Parameters
    ----------
    state_file: Path to the sprint state JSON file.
    """
    if not state_file.exists():
        return None
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        # Enrich with elapsed time for convenience
        start_dt = _parse_iso(state["start_ts"])
        elapsed = (datetime.now() - start_dt).total_seconds() / 60.0
        state["elapsed_minutes"] = round(elapsed, 2)
        state["remaining_minutes"] = round(
            max(float(state.get("duration_minutes", 25)) - elapsed, 0.0), 2
        )
        return state
    except (json.JSONDecodeError, OSError, ValueError, KeyError) as exc:
        logger.warning("Could not read sprint status from %s: %s", state_file, exc)
        return None


# ---------------------------------------------------------------------------
# Session Analytics
# ---------------------------------------------------------------------------

def load_sessions(log_file: Path) -> list:
    """
    Load all :class:`SprintSession` objects from a JSONL log file.

    Returns an empty list if the file does not exist or is empty.
    """
    if not log_file.exists():
        return []

    sessions: list[SprintSession] = []
    try:
        raw = log_file.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read log file %s: %s", log_file, exc)
        return []

    for lineno, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            sessions.append(SprintSession.from_dict(data))
        except (json.JSONDecodeError, OSError, ValueError, KeyError) as exc:
            logger.warning("Skipping malformed log entry at line %d: %s", lineno, exc)

    return sessions


def compute_velocity_stats(sessions: list) -> dict:
    """
    Compute aggregate velocity statistics across all sessions.

    Parameters
    ----------
    sessions: List of :class:`SprintSession` objects.

    Returns
    -------
    dict with keys:
        total_sessions, total_words, total_duration_min,
        avg_wpm, best_wpm, worst_wpm
    """
    if not sessions:
        return {
            "total_sessions": 0,
            "total_words": 0,
            "total_duration_min": 0.0,
            "avg_wpm": 0.0,
            "best_wpm": 0.0,
            "worst_wpm": 0.0,
        }

    total_words = sum(s.actual_words for s in sessions)
    total_duration = sum(s.duration_minutes for s in sessions)
    wpms = [s.wpm for s in sessions]

    return {
        "total_sessions": len(sessions),
        "total_words": total_words,
        "total_duration_min": round(total_duration, 2),
        "avg_wpm": round(sum(wpms) / len(wpms), 2),
        "best_wpm": round(max(wpms), 2),
        "worst_wpm": round(min(wpms), 2),
    }


def compute_daily_streak(sessions: list) -> dict:
    """
    Compute writing streak information from session history.

    A *streak day* is any calendar date (YYYY-MM-DD) that has at least one
    completed session with ``actual_words > 0``.

    Parameters
    ----------
    sessions: List of :class:`SprintSession` objects.

    Returns
    -------
    dict with keys:
        current_streak_days, longest_streak_days, today_words, dates_written
    """
    # Collect unique writing dates (only sessions with actual words)
    date_words: dict[str, int] = {}
    for s in sessions:
        if s.actual_words <= 0:
            continue
        day_key = s.start_ts[:10]  # YYYY-MM-DD
        date_words[day_key] = date_words.get(day_key, 0) + s.actual_words

    if not date_words:
        return {
            "current_streak_days": 0,
            "longest_streak_days": 0,
            "today_words": 0,
            "dates_written": [],
        }

    today_str = date.today().isoformat()
    today_words = date_words.get(today_str, 0)

    # Sort unique dates
    sorted_dates = sorted(date_words.keys())

    # Build streak by walking sorted dates
    longest = 1
    current_run = 1
    for i in range(1, len(sorted_dates)):
        prev_date = date.fromisoformat(sorted_dates[i - 1])
        curr_date = date.fromisoformat(sorted_dates[i])
        if (curr_date - prev_date) == timedelta(days=1):
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # Current streak: count backward from today or yesterday
    current_streak = 0
    check = date.today()
    while check.isoformat() in date_words:
        current_streak += 1
        check -= timedelta(days=1)

    # If we have no writing today, also check if streak ended yesterday
    if current_streak == 0:
        check = date.today() - timedelta(days=1)
        while check.isoformat() in date_words:
            current_streak += 1
            check -= timedelta(days=1)

    return {
        "current_streak_days": current_streak,
        "longest_streak_days": longest,
        "today_words": today_words,
        "dates_written": sorted_dates,
    }


def get_best_session(sessions: list) -> SprintSession | None:
    """
    Return the session with the highest WPM, or *None* if the list is empty.

    Parameters
    ----------
    sessions: List of :class:`SprintSession` objects.
    """
    if not sessions:
        return None
    return max(sessions, key=lambda s: s.wpm)


# ---------------------------------------------------------------------------
# HTML Report Generation
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ars Arcanum · Writing Sprint Dashboard</title>
  <style>
    :root {{
      --bg: #0d0f14;
      --surface: #161922;
      --card: #1e2330;
      --border: #2a3148;
      --accent: #7c6af7;
      --accent2: #e2a84b;
      --text: #d4d8e8;
      --muted: #6b7499;
      --good: #4caf80;
      --warn: #e2a84b;
      --danger: #e05a5a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Georgia', serif;
      padding: 2rem;
      min-height: 100vh;
    }}
    h1 {{
      font-size: 1.9rem;
      color: var(--accent);
      letter-spacing: .04em;
      margin-bottom: .25rem;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: .9rem;
      margin-bottom: 2rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem 1rem;
      text-align: center;
    }}
    .card .label {{
      font-size: .75rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .08em;
      margin-bottom: .4rem;
    }}
    .card .value {{
      font-size: 1.9rem;
      font-weight: bold;
      color: var(--accent);
    }}
    .card .unit {{
      font-size: .75rem;
      color: var(--muted);
      margin-top: .15rem;
    }}
    .section-title {{
      font-size: 1.1rem;
      color: var(--accent2);
      border-bottom: 1px solid var(--border);
      padding-bottom: .5rem;
      margin: 2rem 0 1rem;
    }}
    /* Bar chart */
    .chart-wrap {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem 1rem 1rem;
      overflow-x: auto;
    }}
    .bars {{
      display: flex;
      align-items: flex-end;
      gap: 6px;
      height: 160px;
    }}
    .bar-col {{
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;
      min-width: 32px;
    }}
    .bar {{
      width: 100%;
      background: linear-gradient(180deg, var(--accent) 0%, #4a3cc7 100%);
      border-radius: 4px 4px 0 0;
      transition: opacity .2s;
    }}
    .bar:hover {{ opacity: .8; }}
    .bar-label {{
      font-size: .6rem;
      color: var(--muted);
      margin-top: .4rem;
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      white-space: nowrap;
    }}
    .bar-val {{
      font-size: .65rem;
      color: var(--text);
      margin-bottom: 2px;
    }}
    /* Session table */
    .tbl-wrap {{ overflow-x: auto; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .85rem;
    }}
    thead tr {{
      background: var(--surface);
    }}
    th, td {{
      padding: .6rem .8rem;
      border: 1px solid var(--border);
      text-align: left;
    }}
    th {{
      color: var(--muted);
      font-weight: normal;
      text-transform: uppercase;
      font-size: .72rem;
      letter-spacing: .06em;
    }}
    tr:nth-child(even) {{ background: var(--surface); }}
    .pill {{
      display: inline-block;
      padding: .1rem .55rem;
      border-radius: 999px;
      font-size: .7rem;
      font-weight: bold;
    }}
    .pill-good {{ background: #1e3d2f; color: var(--good); }}
    .pill-warn {{ background: #3d2e1a; color: var(--warn); }}
    .pill-neutral {{ background: #2a2d42; color: var(--text); }}
    footer {{
      margin-top: 3rem;
      text-align: center;
      font-size: .75rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <h1>⚡ Writing Sprint Dashboard</h1>
  <p class="subtitle">Ars Arcanum · Sovereign Craft Analytics · Generated {generated_at}</p>

  <!-- Stat Cards -->
  <div class="grid">
    <div class="card">
      <div class="label">Total Words</div>
      <div class="value">{total_words}</div>
      <div class="unit">across all sprints</div>
    </div>
    <div class="card">
      <div class="label">Avg WPM</div>
      <div class="value">{avg_wpm}</div>
      <div class="unit">words per minute</div>
    </div>
    <div class="card">
      <div class="label">Best WPM</div>
      <div class="value">{best_wpm}</div>
      <div class="unit">personal record</div>
    </div>
    <div class="card">
      <div class="label">Sessions</div>
      <div class="value">{total_sessions}</div>
      <div class="unit">completed sprints</div>
    </div>
    <div class="card">
      <div class="label">Current Streak</div>
      <div class="value">{current_streak}</div>
      <div class="unit">consecutive days</div>
    </div>
    <div class="card">
      <div class="label">Longest Streak</div>
      <div class="value">{longest_streak}</div>
      <div class="unit">days</div>
    </div>
    <div class="card">
      <div class="label">Today</div>
      <div class="value">{today_words}</div>
      <div class="unit">words written</div>
    </div>
  </div>

  <!-- Daily Bar Chart -->
  <div class="section-title">Daily Word Count (Last {chart_days} Days)</div>
  <div class="chart-wrap">
    <div class="bars">
{bar_rows}
    </div>
  </div>

  <!-- Session Table -->
  <div class="section-title">Session History</div>
  <div class="tbl-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Date</th>
          <th>Start</th>
          <th>Duration (min)</th>
          <th>Words</th>
          <th>WPM</th>
          <th>Target</th>
          <th>Goal</th>
        </tr>
      </thead>
      <tbody>
{table_rows}
      </tbody>
    </table>
  </div>

  <footer>Ars Arcanum Scriptorium · Offline Sprint Analytics Engine</footer>
</body>
</html>
"""


def _build_bar_rows(sessions: list, max_days: int = 30) -> str:
    """Build pure-CSS bar-chart HTML rows for the last *max_days* calendar days."""
    # Aggregate words per day
    date_words: dict[str, int] = {}
    for s in sessions:
        day = s.start_ts[:10]
        date_words[day] = date_words.get(day, 0) + s.actual_words

    # Last N days
    today = date.today()
    days: list[str] = [(today - timedelta(days=i)).isoformat() for i in range(max_days - 1, -1, -1)]

    if not date_words:
        return "      <div class='bar-col'><span style='color:var(--muted);font-size:.8rem'>No data yet</span></div>"

    max_words = max((date_words.get(d, 0) for d in days), default=1) or 1
    lines: list[str] = []
    for d in days:
        words = date_words.get(d, 0)
        height_pct = round((words / max_words) * 100)
        short_label = d[5:]  # MM-DD
        lines.append(
            f"      <div class='bar-col'>"
            f"<div class='bar-val'>{words if words else ''}</div>"
            f"<div class='bar' style='height:{height_pct}%' title='{d}: {words} words'></div>"
            f"<div class='bar-label'>{short_label}</div>"
            f"</div>"
        )
    return "\n".join(lines)


def _build_table_rows(sessions: list) -> str:
    """Build HTML table rows for all sessions, newest first."""
    if not sessions:
        return "        <tr><td colspan='8' style='text-align:center;color:var(--muted)'>No sessions recorded yet.</td></tr>"

    sorted_sessions = sorted(sessions, key=lambda s: s.start_ts, reverse=True)
    rows: list[str] = []
    for idx, s in enumerate(sorted_sessions, start=1):
        met_goal = s.actual_words >= s.target_words
        pill_class = "pill-good" if met_goal else "pill-warn"
        pill_text = "✓ Met" if met_goal else "✗ Missed"
        date_part = s.start_ts[:10]
        time_part = s.start_ts[11:19] if len(s.start_ts) > 10 else ""
        rows.append(
            f"        <tr>"
            f"<td>{idx}</td>"
            f"<td>{date_part}</td>"
            f"<td>{time_part}</td>"
            f"<td>{s.duration_minutes:.1f}</td>"
            f"<td>{s.actual_words}</td>"
            f"<td>{s.wpm:.1f}</td>"
            f"<td>{s.target_words}</td>"
            f"<td><span class='pill {pill_class}'>{pill_text}</span></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def generate_sprint_report_html(
    stats: dict,
    streak: dict,
    sessions: list,
    output_path: Path,
) -> None:
    """
    Generate a standalone, CSP-compliant offline HTML velocity dashboard.

    Parameters
    ----------
    stats:       Output of :func:`compute_velocity_stats`.
    streak:      Output of :func:`compute_daily_streak`.
    sessions:    Full list of :class:`SprintSession` objects.
    output_path: Destination path for the HTML file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    bar_rows = _build_bar_rows(sessions, max_days=30)
    table_rows = _build_table_rows(sessions)

    html = _HTML_TEMPLATE.format(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total_words=f"{stats.get('total_words', 0):,}",
        avg_wpm=f"{stats.get('avg_wpm', 0.0):.1f}",
        best_wpm=f"{stats.get('best_wpm', 0.0):.1f}",
        total_sessions=stats.get("total_sessions", 0),
        current_streak=streak.get("current_streak_days", 0),
        longest_streak=streak.get("longest_streak_days", 0),
        today_words=f"{streak.get('today_words', 0):,}",
        chart_days=30,
        bar_rows=bar_rows,
        table_rows=table_rows,
    )

    atomic_write(output_path, html)
    logger.info("Sprint report written to %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_manuscript_dir(args_dir: str | None) -> Path:
    """Return an absolute Path for the manuscript directory from CLI args."""
    return Path(args_dir).resolve() if args_dir else Path(".").resolve()


def _cmd_start(args: argparse.Namespace) -> int:
    manuscript_dir = _resolve_manuscript_dir(getattr(args, "dir", None))
    state = start_sprint(
        target_words=args.target,
        duration_minutes=args.duration,
        manuscript_dir=manuscript_dir,
    )
    print(
        f"⚡ Sprint started!\n"
        f"   Session  : {state['session_id']}\n"
        f"   Target   : {state['target_words']} words\n"
        f"   Duration : {state['duration_minutes']} minutes\n"
        f"   Dir      : {state['manuscript_dir']}"
    )
    return 0


def _cmd_stop(args: argparse.Namespace) -> int:
    manuscript_dir = _resolve_manuscript_dir(getattr(args, "dir", None))
    state_file = _default_state_file(manuscript_dir)
    if not state_file.exists():
        print("✗ No active sprint found. Start one with: arcanum sprint start")
        return 1
    try:
        session = end_sprint(word_count=args.words, state_file=state_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"✗ Error ending sprint: {exc}")
        return 1
    goal_str = "✓ Goal met!" if session.actual_words >= session.target_words else "✗ Goal not met."
    print(
        f"✓ Sprint complete!\n"
        f"   Words    : {session.actual_words} / {session.target_words}  {goal_str}\n"
        f"   Duration : {session.duration_minutes:.1f} min\n"
        f"   WPM      : {session.wpm:.1f}"
    )
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    manuscript_dir = _resolve_manuscript_dir(getattr(args, "dir", None))
    state_file = _default_state_file(manuscript_dir)
    status = get_sprint_status(state_file)
    if status is None:
        print("No active sprint. Use 'arcanum sprint start' to begin.")
        return 0
    print(
        f"⏱  Active Sprint\n"
        f"   Session   : {status['session_id']}\n"
        f"   Target    : {status['target_words']} words\n"
        f"   Elapsed   : {status['elapsed_minutes']:.1f} min\n"
        f"   Remaining : {status['remaining_minutes']:.1f} min"
    )
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    manuscript_dir = _resolve_manuscript_dir(getattr(args, "dir", None))
    log_file = _default_log_file(manuscript_dir)
    sessions = load_sessions(log_file)
    if not sessions:
        print("No sprint sessions recorded yet.")
        return 0
    stats = compute_velocity_stats(sessions)
    streak = compute_daily_streak(sessions)
    best = get_best_session(sessions)
    print(
        f"📊 Sprint Analytics\n"
        f"   Total sessions : {stats['total_sessions']}\n"
        f"   Total words    : {stats['total_words']:,}\n"
        f"   Total time     : {stats['total_duration_min']:.1f} min\n"
        f"   Avg WPM        : {stats['avg_wpm']:.1f}\n"
        f"   Best WPM       : {stats['best_wpm']:.1f}\n"
        f"   Worst WPM      : {stats['worst_wpm']:.1f}\n"
        f"   Current streak : {streak['current_streak_days']} day(s)\n"
        f"   Longest streak : {streak['longest_streak_days']} day(s)\n"
        f"   Today's words  : {streak['today_words']:,}"
    )
    if best is not None:
        print(f"   Best session   : {best.start_ts[:10]} — {best.wpm:.1f} WPM ({best.actual_words} words)")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    manuscript_dir = _resolve_manuscript_dir(getattr(args, "dir", None))
    log_file = _default_log_file(manuscript_dir)
    sessions = load_sessions(log_file)
    stats = compute_velocity_stats(sessions)
    streak = compute_daily_streak(sessions)
    out_path = Path(args.html).resolve() if args.html else manuscript_dir / "sprint_report.html"
    generate_sprint_report_html(stats, streak, sessions, out_path)
    print(f"✓ Report written to: {out_path}")
    return 0


def main(argv: list | None = None) -> None:
    """CLI dispatcher for Ars Arcanum sprint subcommands."""
    parser = argparse.ArgumentParser(
        prog="arcanum-sprint",
        description="Ars Arcanum Writing Sprint Manager",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ---- start ----
    p_start = sub.add_parser("start", help="Begin a new writing sprint")
    p_start.add_argument("dir", nargs="?", default=None, metavar="TARGET_DIR")
    p_start.add_argument("--target", type=int, default=500, metavar="N",
                         help="Word-count target (default: 500)")
    p_start.add_argument("--duration", type=float, default=25.0, metavar="M",
                         help="Sprint length in minutes (default: 25)")

    # ---- stop ----
    p_stop = sub.add_parser("stop", help="End the current sprint")
    p_stop.add_argument("dir", nargs="?", default=None, metavar="TARGET_DIR")
    p_stop.add_argument("--words", type=int, required=True, metavar="N",
                        help="Actual word count written")

    # ---- status ----
    p_status = sub.add_parser("status", help="Show active sprint status")
    p_status.add_argument("dir", nargs="?", default=None, metavar="TARGET_DIR")

    # ---- stats ----
    p_stats = sub.add_parser("stats", help="Show aggregate session analytics")
    p_stats.add_argument("dir", nargs="?", default=None, metavar="TARGET_DIR")

    # ---- report ----
    p_report = sub.add_parser("report", help="Generate HTML velocity dashboard")
    p_report.add_argument("dir", nargs="?", default=None, metavar="TARGET_DIR")
    p_report.add_argument("--html", default=None, metavar="OUT",
                          help="Output HTML file path")

    parsed = parser.parse_args(argv)

    dispatch = {
        "start": _cmd_start,
        "stop": _cmd_stop,
        "status": _cmd_status,
        "stats": _cmd_stats,
        "report": _cmd_report,
    }

    handler = dispatch.get(parsed.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(parsed))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
