#!/usr/bin/env python3
"""
Ars Arcanum Custom Planetary Calendars & Multi-Moon Phase Engine (scripts/lib/calendar.py)
========================================================================================
Local-first planetary calendar arithmetic, multi-moon synodic phase tracker, and
celestial conjunction / eclipse predictor for speculative fantasy and sci-fi worlds.

Parses calendar and planetary metadata from `Cosmology/*.md` or `world.yaml`:

- `days_per_year`, `hours_per_day`, `months`, `weekdays`, `moons`, `eras`

Capabilities:
1. Custom Planetary Calendar Arithmetic:
   - Arbitrary days/year, hours/day, month definitions, and weekday cycles
   - Date advancing (+/- N days), day-of-year calculations, and era offsets
2. Multi-Moon Synodic Phase Tracker:
   - Computes real-time illumination percentage and phase states for multiple moons
   - Moon glyphs (🌑, 🌒, 🌓, 🌔, 🌕, 🌖, 🌗, 🌘)
3. Celestial Syzygy & Eclipse Conjunction Detection:
   - Identifies dates where multiple moons simultaneously enter Full Moon or New Moon
4. Calendar Visualizers:
   - Formatted ANSI terminal monthly grid with moon glyph annotations
   - Interactive standalone HTML calendar viewer
   - Structured JSON export (--json)

Zero external runtime dependencies; 100% offline privacy.
"""

import sys
import os
import re
import json
import math
import html
import argparse
import logging
from pathlib import Path

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.calendar")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)

DEFAULT_MONTHS = [
    {"name": "Primis", "days": 30},
    {"name": "Secundus", "days": 30},
    {"name": "Tertius", "days": 30},
    {"name": "Quartus", "days": 30},
    {"name": "Quintus", "days": 30},
    {"name": "Sextus", "days": 30},
    {"name": "Septimus", "days": 30},
    {"name": "Octavus", "days": 30},
    {"name": "Nonus", "days": 30},
    {"name": "Decimus", "days": 30},
    {"name": "Undecim", "days": 30},
    {"name": "Duodecim", "days": 35},
]

DEFAULT_WEEKDAYS = ["Moonday", "Towerday", "Waterday", "Earthday", "Fireday", "Starday", "Sunday"]

DEFAULT_MOONS = [
    {"name": "Lumina", "period": 28.0, "offset": 0.0, "color": "#f0f6fc"},
    {"name": "Umbra", "period": 19.5, "offset": 4.0, "color": "#bc8cff"},
]


def parse_yaml_frontmatter(content: str) -> dict:
    """Extracts frontmatter dictionary from markdown note."""
    fm_match = FRONTMATTER_REGEX.match(content)
    if not fm_match:
        return {}
    
    data = {}
    lines = fm_match.group(1).splitlines()
    current_key = None
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        
        if raw_line.startswith("  - ") or raw_line.startswith("    - ") or (raw_line.startswith("- ") and current_key):
            item_val = line.lstrip("- ").strip().strip("\"'")
            if current_key:
                if not isinstance(data.get(current_key), list):
                    data[current_key] = []
                data[current_key].append(item_val)
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            current_key = key
            
            if not val:
                data[key] = []
            elif val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
                data[key] = items
            else:
                try:
                    if "." in val:
                        data[key] = float(val)
                    else:
                        data[key] = int(val)
                except ValueError:
                    data[key] = val.strip("\"'")
    return data


def load_calendar_spec(world_dir: Path) -> dict:
    """Scans Cosmology/ notes or world.yaml for calendar and planetary specifications."""
    spec = {
        "world": world_dir.name,
        "hours_per_day": 24,
        "days_per_year": 365,
        "months": DEFAULT_MONTHS,
        "weekdays": DEFAULT_WEEKDAYS,
        "moons": DEFAULT_MOONS,
        "eras": [{"name": "Imperial Era", "short": "IE", "offset": 0}],
    }

    # 1. Check world.yaml
    w_yaml = world_dir / "world.yaml"
    if w_yaml.is_file():
        try:
            fm = parse_yaml_frontmatter(w_yaml.read_text(encoding="utf-8", errors="replace"))
            if "hours_per_day" in fm:
                spec["hours_per_day"] = int(fm["hours_per_day"])
            if "days_per_year" in fm:
                spec["days_per_year"] = int(fm["days_per_year"])
        except Exception as e:
            logger.debug("Error parsing world.yaml: %s", e)

    # 2. Check Cosmology/ notes
    dirs_to_check = [
        world_dir / "Cosmology",
        world_dir / "00-World-Bible" / "Cosmology",
    ]
    for cdir in dirs_to_check:
        if not cdir.is_dir():
            continue
        for md_file in sorted(cdir.rglob("*.md")):
            if "Template" in md_file.name:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                fm = parse_yaml_frontmatter(content)
                if "days_per_year" in fm or "orbital_period_days" in fm:
                    spec["days_per_year"] = int(fm.get("days_per_year", fm.get("orbital_period_days", 365)))
                if "hours_per_day" in fm or "day_length_hours" in fm:
                    spec["hours_per_day"] = int(fm.get("hours_per_day", fm.get("day_length_hours", 24)))
                if "weekdays" in fm and isinstance(fm["weekdays"], list):
                    spec["weekdays"] = fm["weekdays"]
                if "months" in fm and isinstance(fm["months"], list):
                    # Convert list of names to month dicts
                    month_list = []
                    default_days = spec["days_per_year"] // len(fm["months"])
                    rem = spec["days_per_year"] % len(fm["months"])
                    for i, m_name in enumerate(fm["months"]):
                        m_days = default_days + (rem if i == len(fm["months"]) - 1 else 0)
                        month_list.append({"name": str(m_name), "days": m_days})
                    spec["months"] = month_list
                if "moons:" in content:
                    m_sec = content.split("moons:", 1)[1]
                    if "---" in m_sec:
                        m_sec = m_sec.split("---", 1)[0]
                    parsed_moons = []
                    cur_m = None
                    for line in m_sec.splitlines():
                        ls = line.strip()
                        if ls.startswith("- name:") or (ls.startswith("- ") and ":" in ls):
                            if cur_m and "name" in cur_m:
                                parsed_moons.append(cur_m)
                            cur_m = {}
                            k, v = ls.lstrip("- ").split(":", 1)
                            cur_m[k.strip().lower()] = v.strip().strip("\"'")
                        elif ":" in ls and cur_m is not None:
                            k, v = ls.split(":", 1)
                            k = k.strip().lower()
                            v = v.strip().strip("\"'")
                            try:
                                cur_m[k] = float(v) if "." in v else int(v)
                            except ValueError:
                                cur_m[k] = v
                        elif ls.startswith("- ") and cur_m is None:
                            m_val = ls.lstrip("- ").strip().strip("\"'")
                            if m_val:
                                parsed_moons.append({"name": m_val, "period": 28.0, "offset": 0.0})
                    if cur_m and "name" in cur_m:
                        parsed_moons.append(cur_m)
                    if parsed_moons:
                        spec["moons"] = parsed_moons
            except Exception as e:
                logger.debug("Error parsing cosmology note %s: %s", md_file, e)

    # Ensure total days in months matches days_per_year
    total_m_days = sum(m["days"] for m in spec["months"])
    if total_m_days > 0:
        spec["days_per_year"] = total_m_days

    return spec


# ==============================================================================
# Date & Moon Phase Calculations
# ==============================================================================

def date_to_absolute_day(year: int, month_idx: int, day: int, cal_spec: dict) -> int:
    """Calculates continuous absolute day index from Year 1, Month 1, Day 1."""
    days = (year - 1) * cal_spec["days_per_year"]
    for m in cal_spec["months"][:month_idx]:
        days += m["days"]
    days += (day - 1)
    return days


def absolute_day_to_date(abs_day: int, cal_spec: dict) -> tuple:
    """Converts absolute day count into (year, month_index, day_of_month, day_of_week_idx)."""
    days_in_yr = cal_spec["days_per_year"]
    year = (abs_day // days_in_yr) + 1
    rem_days = abs_day % days_in_yr

    month_idx = 0
    day = 1
    for i, m in enumerate(cal_spec["months"]):
        if rem_days < m["days"]:
            month_idx = i
            day = rem_days + 1
            break
        rem_days -= m["days"]

    dow_idx = abs_day % len(cal_spec["weekdays"])
    return (year, month_idx, day, dow_idx)


def get_moon_phase(abs_day: int, moon: dict) -> dict:
    """Calculates moon phase, illumination percentage, and Unicode glyph for a given day."""
    period = float(moon.get("period", 28.0))
    offset = float(moon.get("offset", 0.0))
    
    cycle_pos = ((abs_day + offset) % period) / period  # 0.0 to 1.0

    # Illumination fraction (0% at 0.0/1.0, 100% at 0.5)
    illumination = 0.5 * (1.0 - math.cos(cycle_pos * 2.0 * math.pi))

    # Determine Phase Name & Glyph
    if cycle_pos < 0.06 or cycle_pos >= 0.94:
        phase_name = "New Moon"
        glyph = "🌑"
    elif cycle_pos < 0.19:
        phase_name = "Waxing Crescent"
        glyph = "🌒"
    elif cycle_pos < 0.31:
        phase_name = "First Quarter"
        glyph = "🌓"
    elif cycle_pos < 0.44:
        phase_name = "Waxing Gibbous"
        glyph = "🌔"
    elif cycle_pos < 0.56:
        phase_name = "Full Moon"
        glyph = "🌕"
    elif cycle_pos < 0.69:
        phase_name = "Waning Gibbous"
        glyph = "🌖"
    elif cycle_pos < 0.81:
        phase_name = "Third Quarter"
        glyph = "🌗"
    else:
        phase_name = "Waning Crescent"
        glyph = "🌘"

    return {
        "name": moon["name"],
        "period_days": period,
        "cycle_position": round(cycle_pos, 4),
        "illumination_percent": round(illumination * 100.0, 1),
        "phase_name": phase_name,
        "glyph": glyph,
        "is_full": phase_name == "Full Moon",
        "is_new": phase_name == "New Moon",
    }


def detect_celestial_events(abs_day: int, moons: list) -> list:
    """Detects multi-moon conjunctions, blood convergences, or solar eclipses."""
    events = []
    moon_phases = [get_moon_phase(abs_day, m) for m in moons]

    full_moons = [mp["name"] for mp in moon_phases if mp["is_full"]]
    new_moons = [mp["name"] for mp in moon_phases if mp["is_new"]]

    if len(full_moons) >= 2:
        events.append(f"🌕 Grand Conjunction / Syzygy: Multiple Moons in Full Phase ({', '.join(full_moons)})")
    if len(new_moons) >= 2:
        events.append(f"🌑 Dark Convergence: Multiple Moons in New Phase ({', '.join(new_moons)}) — Eclipse Window")

    return events


# ==============================================================================
# Rendering & Export
# ==============================================================================

def render_month_terminal_grid(year: int, month_idx: int, cal_spec: dict) -> str:
    """Renders a clean ANSI monthly calendar grid."""
    months = cal_spec["months"]
    weekdays = cal_spec["weekdays"]
    m_info = months[month_idx]
    
    first_day_abs = date_to_absolute_day(year, month_idx, 1, cal_spec)
    start_dow = first_day_abs % len(weekdays)

    lines = []
    title = f"{m_info['name']} {year} ({cal_spec['world']})"
    lines.append(f"\033[1;36m=== {title} ===\033[0m")
    
    # Weekday headers
    hdr = "  ".join(f"\033[1m{w[:3]:<4}\033[0m" for w in weekdays)
    lines.append(hdr)
    lines.append("-" * len(hdr))

    cur_row = ["    "] * start_dow
    for d in range(1, m_info["days"] + 1):
        cur_abs = first_day_abs + (d - 1)
        m_phases = [get_moon_phase(cur_abs, m) for m in cal_spec["moons"]]
        glyph = m_phases[0]["glyph"] if m_phases else ""
        
        day_str = f"{d:>2}{glyph}"
        cur_row.append(f"{day_str:<4}")

        if len(cur_row) == len(weekdays):
            lines.append("  ".join(cur_row))
            cur_row = []

    if cur_row:
        while len(cur_row) < len(weekdays):
            cur_row.append("    ")
        lines.append("  ".join(cur_row))

    return "\n".join(lines)


def generate_calendar_html_report(year: int, month_idx: int, cal_spec: dict, output_file: Path):
    """Generates an interactive HTML calendar with moon phase diagrams and upcoming conjunctions."""
    m_info = cal_spec["months"][month_idx]
    first_day_abs = date_to_absolute_day(year, month_idx, 1, cal_spec)
    start_dow = first_day_abs % len(cal_spec["weekdays"])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(cal_spec['world'])} Calendar — {m_info['name']} {year}</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #58a6ff;
    --gold: #d29922;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  body {{ background-color: var(--bg); color: var(--text); font-family: var(--font); line-height: 1.6; margin: 0; padding: 24px; }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ color: var(--accent); margin: 0 0 8px 0; }}
  .badge {{ background: #1f6feb22; color: var(--accent); border: 1px solid var(--accent); padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  .cal-grid {{ display: grid; grid-template-columns: repeat({len(cal_spec['weekdays'])}, 1fr); gap: 6px; margin-top: 16px; }}
  .cal-hdr {{ font-weight: bold; color: #8b949e; text-align: center; padding: 8px 0; }}
  .cal-cell {{ background: #0b0f14; border: 1px solid var(--border); border-radius: 6px; min-height: 70px; padding: 8px; font-size: 12px; }}
  .cal-empty {{ background: transparent; border: none; }}
  .day-num {{ font-size: 14px; font-weight: bold; color: #f0f6fc; }}
  .moon-row {{ margin-top: 4px; display: flex; gap: 4px; font-size: 14px; }}
  footer {{ text-align: center; font-size: 12px; color: #8b949e; margin-top: 40px; border-top: 1px solid var(--border); padding-top: 16px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>📅 {html.escape(cal_spec['world'])} Planetary Calendar</h1>
    <span class="badge">Year {year} • {m_info['name']}</span>
    <span class="badge">{cal_spec['days_per_year']} Days/Year • {cal_spec['hours_per_day']}h/Day</span>
  </header>

  <div class="card">
    <h2>{m_info['name']} {year}</h2>
    <div class="cal-grid">
"""
    for w in cal_spec["weekdays"]:
        html_content += f"""      <div class="cal-hdr">{html.escape(w[:4])}</div>\n"""

    for _ in range(start_dow):
        html_content += """      <div class="cal-cell cal-empty"></div>\n"""

    for d in range(1, m_info["days"] + 1):
        cur_abs = first_day_abs + (d - 1)
        m_phases = [get_moon_phase(cur_abs, m) for m in cal_spec["moons"]]
        glyphs = "".join(f"<span title='{mp['name']}: {mp['phase_name']} ({mp['illumination_percent']}%)'>{mp['glyph']}</span>" for mp in m_phases)
        html_content += f"""      <div class="cal-cell">
        <div class="day-num">{d}</div>
        <div class="moon-row">{glyphs}</div>
      </div>\n"""

    html_content += """    </div>
  </div>
  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    atomic_write(output_file, html_content)


def resolve_world_dir(target_str: str = None) -> str:
    """Resolves world input string (path or name) to absolute directory path."""
    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for u_dir in sorted((home / "Universes").glob("*/*")):
            if u_dir.is_dir() and u_dir.name.lower() == target_str.lower():
                return str(u_dir)
        for w_dir in sorted((home / "Worlds").glob("*")):
            if w_dir.is_dir() and w_dir.name.lower() == target_str.lower():
                return str(w_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)

    home = Path.home()
    universes = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
    universes = [p for p in universes if p.is_dir() and p.name not in ("Worlds", ".git")]
    if len(universes) == 1:
        return str(universes[0])
    elif len(universes) > 1:
        print("Error: Multiple worlds discovered — specify one with -w/--world.", file=sys.stderr)
        sys.exit(2)
    else:
        worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
        worlds = [p for p in worlds if p.is_dir()]
        if len(worlds) == 1:
            return str(worlds[0])
        elif len(worlds) > 1:
            print("Error: Multiple legacy worlds discovered — specify one with -w/--world.", file=sys.stderr)
            sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Planetary Calendar & Moon Phase Engine")
    parser.add_argument("world", nargs="?", help="World Bible lore directory")
    parser.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory alternative")
    parser.add_argument("-y", "--year", type=int, default=1, help="Calendar year (default: 1)")
    parser.add_argument("-m", "--month", type=int, default=1, help="Month index (1 to N, default: 1)")
    parser.add_argument("-d", "--day", type=int, default=1, help="Day of month (default: 1)")
    parser.add_argument("--advance", type=int, default=0, help="Advance date by +N days")
    parser.add_argument("--phases", action="store_true", help="Print detailed multi-moon phase breakdown")
    parser.add_argument("--html", help="Export standalone interactive HTML calendar report")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    # Discover world
    raw_w = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir = resolve_world_dir(raw_w)

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    cal_spec = load_calendar_spec(Path(world_dir))

    # Compute target date
    m_idx = max(0, min(len(cal_spec["months"]) - 1, args.month - 1))
    abs_day = date_to_absolute_day(args.year, m_idx, args.day, cal_spec) + args.advance
    calc_yr, calc_m_idx, calc_day, calc_dow_idx = absolute_day_to_date(abs_day, cal_spec)
    
    current_m_name = cal_spec["months"][calc_m_idx]["name"]
    current_dow = cal_spec["weekdays"][calc_dow_idx]

    moon_states = [get_moon_phase(abs_day, m) for m in cal_spec["moons"]]
    events = detect_celestial_events(abs_day, cal_spec["moons"])

    if args.json:
        out_data = {
            "world": cal_spec["world"],
            "year": calc_yr,
            "month_index": calc_m_idx + 1,
            "month_name": current_m_name,
            "day": calc_day,
            "weekday": current_dow,
            "absolute_day": abs_day,
            "calendar_spec": {
                "days_per_year": cal_spec["days_per_year"],
                "hours_per_day": cal_spec["hours_per_day"],
                "months_count": len(cal_spec["months"]),
                "weekdays_count": len(cal_spec["weekdays"]),
            },
            "moons": moon_states,
            "celestial_events": events,
        }
        print(json.dumps(out_data, indent=2))
        sys.exit(0)

    # Terminal output
    print(f"\n\033[1;36m=== Ars Arcanum Planetary Calendar: {cal_spec['world']} ===\033[0m")
    print(f"Current Date: \033[1m{current_dow}, {current_m_name} {calc_day}, Year {calc_yr}\033[0m (Day {abs_day:,} of Era)")
    print(f"Planetary Cycle: \033[32m{cal_spec['days_per_year']} days/year\033[0m | \033[33m{cal_spec['hours_per_day']} hours/day\033[0m\n")

    print("\033[1mMoon Phases & Illuminations:\033[0m")
    for mp in moon_states:
        print(f"  {mp['glyph']} \033[1;36m{mp['name']}\033[0m: {mp['phase_name']} ({mp['illumination_percent']}% illuminated, Period: {mp['period_days']}d)")
    print()

    if events:
        print("\033[1;33mUpcoming Celestial Conjunctions:\033[0m")
        for ev in events:
            print(f"  ✨ \033[1m{ev}\033[0m")
        print()

    # Render Month Grid
    print(render_month_terminal_grid(calc_yr, calc_m_idx, cal_spec))
    print()

    if args.html:
        out_p = Path(args.html)
        generate_calendar_html_report(calc_yr, calc_m_idx, cal_spec, out_p)
        print(f"Interactive HTML calendar written to: {out_p}")


if __name__ == "__main__":
    main()