# ⚡ Writing Sprint — Sovereign Craft Analytics

> **Ars Arcanum · Phase 13 · Scriptorium**  
> Offline, zero-dependency writing timer and productivity analytics engine.

---

## Overview

The Writing Sprint system lets you run focused, timed writing sessions (Pomodoro-style sprints) against any manuscript directory. Every session is recorded in a local JSONL log, and the engine can compute:

- Words-per-minute velocity (average, best, worst)
- Daily writing streaks
- Per-session history and goal tracking
- A standalone, offline HTML velocity dashboard

All state lives inside a hidden `.arcanum/` folder **inside your manuscript directory** — no cloud, no external dependencies.

---

## Sprint Workflow

### 1. Start a sprint

```bash
# Default: 500-word goal, 25-minute timer, current directory
arcanum-sprint start

# Custom goal and duration
arcanum-sprint start --target 750 --duration 30

# Point at a specific manuscript directory
arcanum-sprint start /path/to/my/novel --target 1000 --duration 45
```

The engine writes `.arcanum/.sprint_state.json` atomically. This file tracks your session ID, start time, target, and planned duration.

### 2. Write

Work in your manuscript files normally. The sprint timer is purely informational — the engine does not scan your files automatically. You supply the final word count when you stop.

### 3. Stop and record

```bash
# Record 430 words written (current directory)
arcanum-sprint stop --words 430

# With explicit manuscript directory
arcanum-sprint stop /path/to/my/novel --words 430
```

The engine:
1. Reads `.arcanum/.sprint_state.json`
2. Computes elapsed time and WPM
3. Appends one JSON line to `.arcanum/.sprint_log.jsonl`
4. Removes the state file

### 4. Check active sprint status

```bash
arcanum-sprint status
arcanum-sprint status /path/to/my/novel
```

Output shows session ID, target words, elapsed time, and remaining time.

---

## Analytics

### Summary statistics

```bash
arcanum-sprint stats
arcanum-sprint stats /path/to/my/novel
```

Prints:

| Field            | Description                              |
|------------------|------------------------------------------|
| Total sessions   | Number of completed sprints              |
| Total words      | Cumulative words across all sprints      |
| Total time       | Minutes spent writing                    |
| Avg WPM          | Mean words-per-minute across sessions    |
| Best WPM         | Personal record                          |
| Worst WPM        | Slowest session                          |
| Current streak   | Consecutive calendar days with ≥1 sprint |
| Longest streak   | All-time best consecutive day run        |
| Today's words    | Words written today                      |
| Best session     | Date and stats of top WPM session        |

### HTML Velocity Dashboard

```bash
# Write report.html to the manuscript directory
arcanum-sprint report

# Custom output path
arcanum-sprint report /path/to/my/novel --html ~/Desktop/sprint_report.html
```

Generates a self-contained, CSP-compliant HTML file with:
- Stat cards (total words, avg WPM, best WPM, streaks)
- A **pure-CSS bar chart** of daily word counts (last 30 days)
- A full session table with goal-met indicators

> [!NOTE]
> The HTML report is completely offline — no CDN, no external fonts, no JavaScript libraries. It works in any browser that supports inline CSS.

---

## File Locations

All sprint data is stored in `.arcanum/` inside your manuscript directory:

```
<manuscript_dir>/
└── .arcanum/
    ├── .sprint_state.json    ← active sprint state (deleted on stop)
    └── .sprint_log.jsonl     ← permanent session history (append-only)
```

| File                  | Format | Purpose                           |
|-----------------------|--------|-----------------------------------|
| `.sprint_state.json`  | JSON   | Single active sprint; deleted on `stop` |
| `.sprint_log.jsonl`   | JSONL  | One line per completed session    |

> [!IMPORTANT]
> **Never edit `.sprint_log.jsonl` manually** unless you understand the JSONL format. Each line must be a complete, valid JSON object matching the `SprintSession` schema.

### SprintSession schema

```json
{
  "session_id":       "2026-09-21T10:00:00.123456",
  "start_ts":         "2026-09-21T10:00:00.123456",
  "end_ts":           "2026-09-21T10:25:12.654321",
  "target_words":     500,
  "actual_words":     423,
  "duration_minutes": 25.2,
  "wpm":              16.79,
  "manuscript_dir":   "/home/author/my-novel",
  "notes":            ""
}
```

---

## CLI Reference

```
arcanum-sprint <COMMAND> [OPTIONS] [TARGET_DIR]
```

| Command  | Options                           | Description                          |
|----------|-----------------------------------|--------------------------------------|
| `start`  | `--target N` `--duration M`       | Begin a new sprint                   |
| `stop`   | `--words N` *(required)*          | End current sprint, record words     |
| `status` | —                                 | Show active sprint info              |
| `stats`  | —                                 | Print aggregate analytics            |
| `report` | `--html OUT`                      | Generate HTML velocity dashboard     |

All commands accept an optional positional `TARGET_DIR` argument. When omitted, the current working directory is used.

---

## Python API

You can embed the engine directly in your own scripts:

```python
from pathlib import Path
from lib.writing_sprint import (
    start_sprint, end_sprint, get_sprint_status,
    load_sessions, compute_velocity_stats, compute_daily_streak,
    get_best_session, generate_sprint_report_html,
)

ms = Path("/home/author/novel")

# Start a sprint
state = start_sprint(target_words=750, duration_minutes=30, manuscript_dir=ms)

# ... write ...

# End the sprint
session = end_sprint(word_count=680, state_file=ms / ".arcanum" / ".sprint_state.json")
print(f"WPM: {session.wpm}")

# Analytics
log = ms / ".arcanum" / ".sprint_log.jsonl"
sessions = load_sessions(log)
stats   = compute_velocity_stats(sessions)
streak  = compute_daily_streak(sessions)
best    = get_best_session(sessions)

# HTML report
generate_sprint_report_html(stats, streak, sessions, ms / "sprint_report.html")
```

---

## Integration with Studio Hub

The Writing Sprint engine is designed to integrate with the **Ars Arcanum Studio Hub** dashboard:

- The `.arcanum/.sprint_log.jsonl` path is discoverable from any manuscript directory registered in the Hub.
- The HTML report (`sprint_report.html`) can be embedded or linked from the Hub's project overview page.
- The `compute_velocity_stats()` and `compute_daily_streak()` functions can be called server-side to populate Hub widgets without re-parsing all sessions on each request — cache the result dict and invalidate when the JSONL mtime changes.

> [!TIP]
> For real-time sprint countdown in the Hub, poll `get_sprint_status(state_file)` every 30 seconds. The returned `remaining_minutes` field is ready to display directly.

---

## Streak Rules

- A **streak day** is any calendar date (UTC-local) on which at least one completed sprint has `actual_words > 0`.
- The **current streak** counts backward from today. If today has no session, yesterday's date starts the lookback — so you don't lose your streak the moment midnight passes.
- The **longest streak** is the maximum run of consecutive calendar dates ever recorded.

---

## WPM Calculation

```
WPM = actual_words / max(duration_minutes, 0.1)
```

The `max(..., 0.1)` guard prevents division-by-zero for near-instant stops, producing a finite (if extreme) WPM value rather than an error.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `No active sprint found` on `stop` | `start` was run in a different directory | Pass the same `TARGET_DIR` to `stop` |
| State file left behind after crash | `end_sprint` was never called | Run `stop` with an estimated word count |
| Log file has a blank line | Manual editing or interrupted write | The engine skips blank lines automatically |
| HTML report won't open | File written to a read-only path | Use `--html` to choose a writable path |

---

*Ars Arcanum · Sovereign Craft · Phase 13 — The Sovereign Craft Deepening*
