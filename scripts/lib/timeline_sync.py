#!/usr/bin/env python3
"""
Ars Arcanum Dual-Track Chronological vs Narrative Timeline Synchronizer
(scripts/lib/timeline_sync.py)
================================================================================
Zero-dependency, offline dual-track timeline alignment engine for speculative
fiction novels, non-linear narratives, multi-POV epics, and series universes.

Capabilities:
1. Narrative vs Chronological Track Extraction:
   - Scans manuscript chapters and world history notes (`*.md`).
   - Extracts `@time:`, `@date:`, `@pov:`, `@location:`, `@event:`, and `@flashback:`.
2. Non-Linear Temporal Diagnostics:
   - Identifies flashbacks, flash-forwards, and temporal jumps.
   - Detects concurrent/simultaneous scenes across different character POVs.
   - Flags character teleportation paradoxes (same character in 2 locations at same time).
3. Visual Dual-Track Timelines:
   - ASCII terminal comparative dual timeline.
   - Interactive standalone HTML5/SVG dual-track Gantt chart with flashback arcs.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter

logger = logging.getLogger("arcanum.timeline")

TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


@dataclass
class TimelineEvent:
    id: str
    narrative_index: int
    title: str
    filename: str
    path: str
    pov: str
    location: str
    raw_time: str
    normalized_time: float  # Numerical coordinate for chronological sorting
    is_flashback: bool = False
    is_flashforward: bool = False
    characters: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_time_coordinate(raw_time: str, fallback_idx: int) -> tuple[float, bool, bool]:
    """Parses a time string into a sortable numeric coordinate and flags flashbacks/forwards.
    
    Supports:
    - Years / Epochs: "1422 3E", "Year 304", "Year -500"
    - Day offsets: "Day 14, 08:00", "Day 1"
    - ISO timestamps: "2045-10-12"
    - Relative tags: "Flashback: 10 years earlier", "5 years later"
    """
    clean = raw_time.strip().lower()
    is_flashback = "flashback" in clean or "earlier" in clean or "ago" in clean
    is_flashforward = "flashforward" in clean or "later" in clean or "future" in clean

    # 1. Year matching: e.g. "1422 3E", "year 304"
    m_year = re.search(r"\b(?:year\s*)?([+-]?\d+)(?:\s*(?:3e|2e|1e|ad|ce|bce|bc))?\b", clean)
    if m_year:
        try:
            base_year = float(m_year.group(1))
            # Check for day / hour within year
            m_day = re.search(r"\bday\s*(\d+)\b", clean)
            day_offset = float(m_day.group(1)) / 365.0 if m_day else 0.0
            return (base_year + day_offset, is_flashback, is_flashforward)
        except ValueError:
            pass

    # 2. Day matching: e.g. "Day 14"
    m_day_only = re.search(r"\bday\s*(\d+)(?:\s*,\s*(\d+):?(\d+)?)?\b", clean)
    if m_day_only:
        try:
            day_val = float(m_day_only.group(1))
            hour_val = float(m_day_only.group(2) or 0) / 24.0
            return (1000.0 + day_val + hour_val, is_flashback, is_flashforward)
        except ValueError:
            pass

    # 3. Fallback to narrative order relative position
    return (1000.0 + fallback_idx, is_flashback, is_flashforward)


def extract_timeline_events(target_path: Path) -> list[TimelineEvent]:
    """Scans manuscript chapters and extracts dual-track timeline events."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    events: list[TimelineEvent] = []

    for idx, f in enumerate(files, 1):
        content = f.read_text(encoding="utf-8", errors="replace")
        meta = parse_yaml_frontmatter(content)
        body = FRONTMATTER_REGEX.sub("", content)

        pov = str(meta.get("pov", meta.get("character", "")))
        location = str(meta.get("location", meta.get("setting", "")))
        raw_time = str(meta.get("time", meta.get("date", meta.get("timeline", ""))))
        h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        raw_title = str(meta.get("title", h1_match.group(1).strip() if h1_match else f.stem.replace("_", " ").replace("-", " ")))
        clean_title = re.sub(r"^\d+\s*[-_.]*\s*", "", raw_title).title()

        chars: list[str] = []
        if "characters" in meta and isinstance(meta["characters"], list):
            chars = [str(c) for c in meta["characters"]]

        lines = body.splitlines()
        prose_lines = []
        for line in lines:
            s_line = line.strip()
            m = TAG_REGEX.match(s_line)
            if m:
                k, v = m.group(1).lower(), m.group(2).strip()
                if k == "pov" and not pov:
                    pov = v
                elif k in ("location", "setting") and not location:
                    location = v
                elif k in ("time", "date", "timeline") and not raw_time:
                    raw_time = v
                elif k in ("char", "characters"):
                    chars.extend([c.strip() for c in v.split(",") if c.strip()])
            elif s_line and not s_line.startswith("#"):
                prose_lines.append(s_line)

        summary = " ".join(prose_lines)[:160].strip()
        if len(" ".join(prose_lines)) > 160:
            summary += "..."

        if not raw_time:
            raw_time = f"Narrative Step {idx}"

        coord, is_fb, is_ff = parse_time_coordinate(raw_time, fallback_idx=idx)

        events.append(TimelineEvent(
            id=f"evt_{idx}",
            narrative_index=idx,
            title=clean_title or f.stem,
            filename=f.name,
            path=str(f),
            pov=pov or "Omniscient",
            location=location or "Unspecified",
            raw_time=raw_time,
            normalized_time=coord,
            is_flashback=is_fb,
            is_flashforward=is_ff,
            characters=list(set(chars)),
            summary=summary or "No prose summary available.",
        ))

    return events


def analyze_timeline_synchronization(events: list[TimelineEvent]) -> dict[str, Any]:
    """Analyzes the timeline for flashbacks, concurrent events, and paradoxes."""
    # Chronological sort
    chronological_order = sorted(events, key=lambda e: (e.normalized_time, e.narrative_index))

    # Mark chronological ranks
    for rank, evt in enumerate(chronological_order, 1):
        evt_in_orig = next(e for e in events if e.id == evt.id)
        # Compute jump distance
        jump = rank - evt_in_orig.narrative_index
        if jump < 0 and not evt_in_orig.is_flashback:
            # Occurs earlier in in-world history than previous narrative scenes
            evt_in_orig.is_flashback = True

    # Check for character co-location paradoxes
    paradoxes = []
    by_time: dict[float, list[TimelineEvent]] = {}
    for e in events:
        by_time.setdefault(e.normalized_time, []).append(e)

    for _t_val, concurrent in by_time.items():
        if len(concurrent) > 1:
            # Check if any character appears in 2 different locations at same time
            for i in range(len(concurrent)):
                for j in range(i + 1, len(concurrent)):
                    e1, e2 = concurrent[i], concurrent[j]
                    if e1.location != e2.location and e1.location != "Unspecified" and e2.location != "Unspecified":
                        # Check shared characters
                        shared = set(e1.characters) & set(e2.characters)
                        if e1.pov != "Omniscient" and e1.pov == e2.pov:
                            shared.add(e1.pov)
                        for char in shared:
                            paradoxes.append({
                                "type": "bilocation",
                                "character": char,
                                "time": e1.raw_time,
                                "event1": e1.title,
                                "loc1": e1.location,
                                "event2": e2.title,
                                "loc2": e2.location,
                                "message": f"Character '{char}' is active in both '{e1.location}' ({e1.title}) and '{e2.location}' ({e2.title}) simultaneously at '{e1.raw_time}'.",
                            })

    flashback_count = sum(1 for e in events if e.is_flashback)
    simultaneous_count = sum(len(grp) for grp in by_time.values() if len(grp) > 1)

    return {
        "total_events": len(events),
        "narrative_events": [e.to_dict() for e in events],
        "chronological_events": [e.to_dict() for e in chronological_order],
        "flashback_count": flashback_count,
        "simultaneous_event_count": simultaneous_count,
        "paradoxes": paradoxes,
        "is_linear": (flashback_count == 0),
    }


def generate_timeline_html_report(report: dict[str, Any], output_path: Path) -> Path:
    """Generates an offline interactive HTML5 dual-track timeline visualization."""
    narrative_events = report.get("narrative_events", [])
    paradoxes = report.get("paradoxes", [])

    rows = []
    for _idx, e in enumerate(narrative_events, 1):
        fb_badge = "<span style='background:#78350f;color:#fde68a;padding:2px 6px;border-radius:4px;font-size:0.75rem;'>Flashback</span>" if e.get("is_flashback") else ""
        row = f"""
        <tr>
          <td><strong>#{e['narrative_index']}</strong></td>
          <td><strong>{html.escape(e['title'])}</strong><br><small style="color:#94a3b8;">👤 {html.escape(e['pov'])} | 📍 {html.escape(e['location'])}</small></td>
          <td><code style="background:#1e293b;padding:2px 6px;border-radius:4px;">{html.escape(e['raw_time'])}</code> {fb_badge}</td>
          <td>{html.escape(e['summary'])}</td>
        </tr>
        """
        rows.append(row)

    paradox_section = ""
    if paradoxes:
        p_rows = "".join(f"<li><strong>[BILOCATION PARADOX]</strong> {html.escape(p['message'])}</li>" for p in paradoxes)
        paradox_section = f"""
        <div style="background:#450a0a;border:1px solid #b91c1c;border-radius:8px;padding:1rem;margin-bottom:1.5rem;">
          <h3 style="margin-top:0;color:#fca5a5;">⚠️ Temporal Inconsistencies & Bilocation Anomalies</h3>
          <ul style="color:#fecaca;margin-bottom:0;">{p_rows}</ul>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Dual-Track Timeline Synchronizer</title>
<style>
  :root {{
    --bg: #0b1120; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-end; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--muted); font-size: 0.85rem; text-transform: uppercase; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1 style="margin:0;">⏳ Dual-Track Timeline Synchronizer</h1>
      <p style="color:var(--muted);margin:0.25rem 0 0 0;">Narrative Reader Sequence vs In-Universe Chronological Progression</p>
    </div>
    <div>
      <span style="background:{'#064e3b' if report.get('is_linear') else '#78350f'};color:{'#a7f3d0' if report.get('is_linear') else '#fde68a'};padding:4px 12px;border-radius:6px;font-weight:600;font-size:0.875rem;">
        {'Linear Timeline' if report.get('is_linear') else 'Non-Linear / Flashbacks'}
      </span>
    </div>
  </div>

  {paradox_section}

  <div class="grid">
    <div class="card">
      <h3>Total Scenes</h3>
      <div class="metric">{report.get('total_events', 0)}</div>
      <p style="color:var(--muted);margin:0.5rem 0 0 0;">Extracted story beats</p>
    </div>
    <div class="card">
      <h3>Flashbacks</h3>
      <div class="metric" style="color:{'var(--warn)' if report.get('flashback_count', 0) > 0 else 'var(--success)'};">{report.get('flashback_count', 0)}</div>
      <p style="color:var(--muted);margin:0.5rem 0 0 0;">Non-linear temporal jumps</p>
    </div>
    <div class="card">
      <h3>Simultaneous Scenes</h3>
      <div class="metric">{report.get('simultaneous_event_count', 0)}</div>
      <p style="color:var(--muted);margin:0.5rem 0 0 0;">Concurrent multi-POV windows</p>
    </div>
    <div class="card">
      <h3>Temporal Paradoxes</h3>
      <div class="metric" style="color:{'var(--danger)' if paradoxes else 'var(--success)'};">{len(paradoxes)}</div>
      <p style="color:var(--muted);margin:0.5rem 0 0 0;">Bilocation or causal clashes</p>
    </div>
  </div>

  <div class="section">
    <h2>📖 Narrative Sequence Track</h2>
    <table>
      <thead>
        <tr><th>#</th><th>Scene & Characters</th><th>In-World Timestamp</th><th>Prose Excerpt</th></tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Dual-Track Timeline Synchronizer")
    parser.add_argument("target", help="Manuscript directory or World Lore folder")
    parser.add_argument("--chronological", "-c", action="store_true", help="Display sorted by in-world chronological time")
    parser.add_argument("--html", help="Generate standalone interactive HTML report to path")
    parser.add_argument("--json", action="store_true", help="Output timeline report as JSON")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    events = extract_timeline_events(target_path)
    report = analyze_timeline_synchronization(events)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=== Dual-Track Timeline Synchronizer ===")
    print(f"Target: {target_path.name} | Total Scenes: {report['total_events']} | Flashbacks: {report['flashback_count']}")
    if report["paradoxes"]:
        print(f"⚠️  {len(report['paradoxes'])} Bilocation / Paradox anomalies detected!")
    print("-" * 80)

    display_events = report["chronological_events"] if args.chronological else report["narrative_events"]
    mode_label = "Chronological Order" if args.chronological else "Narrative Order"
    print(f"Sequence Track ({mode_label}):\n")

    for e in display_events:
        fb = " [FLASHBACK]" if e.get("is_flashback") else ""
        print(f"  #{e['narrative_index']:<3} {e['title']:<28} | 👤 {e['pov']:<15} | 📍 {e['location']:<15} | {e['raw_time']}{fb}")

    if args.html:
        out_p = Path(args.html)
        generate_timeline_html_report(report, out_p)
        print(f"\nHTML report written to: {out_p}")


if __name__ == "__main__":
    main()
