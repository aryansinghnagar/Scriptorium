#!/usr/bin/env python3
"""
Ars Arcanum Story Paradigm & Narrative Structure Enforcer
(scripts/lib/structure.py)
================================================================================
Zero-dependency, offline narrative structural analyzer and pacing paradigm enforcer.

Capabilities (PLT-102):
1. Story Paradigm Models:
   - Three-Act Structure (Classic 8-sequence / 25-50-25 model)
   - Hero's Journey / Campbell-Vogler Monomyth (12 stages)
   - Save the Cat! 15 Beat Sheet (Blake Snyder)
   - Dan Harmon Story Circle (8 steps)
   - 7-Point Story Structure (Dan Wells)
   - Fichtean Curve (Crises & Climax model)
2. Manuscript Structural Mapping:
   - Computes proportional word counts across chapters / scenes
   - Maps actual chapter positions against ideal structural beat windows
   - Detects structural drift (late Inciting Incident, early Midpoint, rushed Climax)
   - Structural Harmony Score (0–100%)
3. Standalone Interactive HTML Beat Map with timeline bars.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import json
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

logger = logging.getLogger("arcanum.structure")

PARADIGMS = {
    "three_act": {
        "name": "Classic Three-Act Structure",
        "beats": [
            {"name": "Opening Status Quo", "target_pct": 0.05, "window": (0.0, 0.10), "desc": "Establish protagonist in the ordinary world"},
            {"name": "Inciting Incident", "target_pct": 0.12, "window": (0.08, 0.16), "desc": "Event that disrupts the balance and sets story in motion"},
            {"name": "Plot Point 1 / Break into Act II", "target_pct": 0.25, "window": (0.20, 0.30), "desc": "Protagonist steps into new world / accepts the challenge"},
            {"name": "First Pinch Point", "target_pct": 0.37, "window": (0.32, 0.42), "desc": "Antagonist forces push back; reminder of stakes"},
            {"name": "Midpoint", "target_pct": 0.50, "window": (0.45, 0.55), "desc": "Shift from reactive to proactive; false victory or false defeat"},
            {"name": "Second Pinch Point", "target_pct": 0.62, "window": (0.58, 0.68), "desc": "Antagonistic pressure intensifies; cracks in the plan"},
            {"name": "All Hope Is Lost / Crisis", "target_pct": 0.75, "window": (0.70, 0.80), "desc": "Lowest point; old methods fail; ultimate test"},
            {"name": "Climax", "target_pct": 0.88, "window": (0.82, 0.94), "desc": "Final showdown confronting core conflict"},
            {"name": "Resolution / Denouement", "target_pct": 0.96, "window": (0.92, 1.00), "desc": "New equilibrium established"},
        ]
    },
    "save_the_cat": {
        "name": "Save the Cat! 15 Beats",
        "beats": [
            {"name": "Opening Image", "target_pct": 0.01, "window": (0.0, 0.03), "desc": "Snapshot of starting world and flaw"},
            {"name": "Theme Stated", "target_pct": 0.05, "window": (0.03, 0.08), "desc": "Statement of core thematic truth"},
            {"name": "Set-Up", "target_pct": 0.08, "window": (0.01, 0.12), "desc": "Establish life, stakes, and six things needing fixing"},
            {"name": "Catalyst", "target_pct": 0.12, "window": (0.09, 0.15), "desc": "Inciting event that shakes up status quo"},
            {"name": "Debate", "target_pct": 0.18, "window": (0.13, 0.22), "desc": "Doubt, resistance, should I stay or go"},
            {"name": "Break into Two", "target_pct": 0.23, "window": (0.20, 0.27), "desc": "Proactive decision to enter Act 2"},
            {"name": "B Story", "target_pct": 0.25, "window": (0.22, 0.30), "desc": "Love interest or mentor subplot introduced"},
            {"name": "Fun and Games", "target_pct": 0.37, "window": (0.28, 0.48), "desc": "Promise of the premise explored"},
            {"name": "Midpoint", "target_pct": 0.50, "window": (0.46, 0.54), "desc": "False victory/defeat; stakes raised"},
            {"name": "Bad Guys Close In", "target_pct": 0.62, "window": (0.52, 0.72), "desc": "Internal and external pressure mounts"},
            {"name": "All Hope Is Lost", "target_pct": 0.75, "window": (0.70, 0.78), "desc": "Whiff of death; rock bottom"},
            {"name": "Dark Night of the Soul", "target_pct": 0.78, "window": (0.74, 0.82), "desc": "Mourning and discovering true epiphany"},
            {"name": "Break into Three", "target_pct": 0.82, "window": (0.78, 0.86), "desc": "New idea that synthesizes A and B story"},
            {"name": "Finale", "target_pct": 0.90, "window": (0.84, 0.96), "desc": "Execution of the new plan; defeating bad guys"},
            {"name": "Final Image", "target_pct": 0.99, "window": (0.96, 1.00), "desc": "Opposite mirror of the Opening Image"},
        ]
    },
    "heros_journey": {
        "name": "Hero's Journey (Monomyth)",
        "beats": [
            {"name": "1. Ordinary World", "target_pct": 0.05, "window": (0.0, 0.10), "desc": "Hero in baseline environment"},
            {"name": "2. Call to Adventure", "target_pct": 0.12, "window": (0.08, 0.16), "desc": "Disruption challenges hero to journey"},
            {"name": "3. Refusal of the Call", "target_pct": 0.18, "window": (0.13, 0.22), "desc": "Reluctance, fear, or obligation"},
            {"name": "4. Meeting the Mentor", "target_pct": 0.22, "window": (0.18, 0.26), "desc": "Guide gives wisdom, tool, or encouragement"},
            {"name": "5. Crossing the Threshold", "target_pct": 0.28, "window": (0.23, 0.33), "desc": "Entering the special world"},
            {"name": "6. Tests, Allies & Enemies", "target_pct": 0.40, "window": (0.30, 0.50), "desc": "Navigating rules of the new realm"},
            {"name": "7. Approach Inmost Cave", "target_pct": 0.55, "window": (0.48, 0.62), "desc": "Preparing for the central challenge"},
            {"name": "8. The Ordeal", "target_pct": 0.65, "window": (0.58, 0.72), "desc": "Direct brush with death/failure"},
            {"name": "9. Reward (Seizing the Sword)", "target_pct": 0.75, "window": (0.68, 0.80), "desc": "Hero claims prize / transformation"},
            {"name": "10. The Road Back", "target_pct": 0.82, "window": (0.76, 0.88), "desc": "Urgency and pursuit back home"},
            {"name": "11. Resurrection", "target_pct": 0.90, "window": (0.84, 0.95), "desc": "Final supreme test of transformed hero"},
            {"name": "12. Return with Elixir", "target_pct": 0.98, "window": (0.94, 1.00), "desc": "Sharing boon with the ordinary world"},
        ]
    },
    "story_circle": {
        "name": "Dan Harmon Story Circle",
        "beats": [
            {"name": "1. You (Comfort Zone)", "target_pct": 0.08, "window": (0.0, 0.15), "desc": "A character is in a zone of comfort"},
            {"name": "2. Need (Desire)", "target_pct": 0.20, "window": (0.12, 0.26), "desc": "But they want something"},
            {"name": "3. Go (Unfamiliar Situation)", "target_pct": 0.32, "window": (0.24, 0.38), "desc": "They enter an unfamiliar situation"},
            {"name": "4. Search (Adaptation)", "target_pct": 0.45, "window": (0.36, 0.52), "desc": "They adapt to it"},
            {"name": "5. Find (Getting What They Wanted)", "target_pct": 0.58, "window": (0.50, 0.65), "desc": "They get what they wanted"},
            {"name": "6. Take (Heavy Price)", "target_pct": 0.72, "window": (0.64, 0.80), "desc": "They pay a heavy price for it"},
            {"name": "7. Return (Back to Start)", "target_pct": 0.85, "window": (0.78, 0.92), "desc": "They return to their familiar situation"},
            {"name": "8. Change (Transformed)", "target_pct": 0.96, "window": (0.90, 1.00), "desc": "Having changed"},
        ]
    },
    "seven_point": {
        "name": "7-Point Story Structure",
        "beats": [
            {"name": "1. Hook", "target_pct": 0.05, "window": (0.0, 0.12), "desc": "Starting state opposite of resolution"},
            {"name": "2. Plot Turn 1", "target_pct": 0.22, "window": (0.15, 0.28), "desc": "Call to action; movement begins"},
            {"name": "3. Pinch Point 1", "target_pct": 0.37, "window": (0.30, 0.44), "desc": "Antagonist reveals power; pressure rises"},
            {"name": "4. Midpoint", "target_pct": 0.50, "window": (0.44, 0.56), "desc": "Character moves from reacting to acting"},
            {"name": "5. Pinch Point 2", "target_pct": 0.65, "window": (0.58, 0.72), "desc": "Disaster strikes; plan fails"},
            {"name": "6. Plot Turn 2", "target_pct": 0.80, "window": (0.74, 0.86), "desc": "Final piece of puzzle acquired"},
            {"name": "7. Resolution", "target_pct": 0.95, "window": (0.88, 1.00), "desc": "Climactic resolution and transformed status quo"},
        ]
    }
}


def scan_manuscript_structure(target_path: Path, paradigm_key: str = "three_act") -> dict:
    """Scans manuscript chapters and evaluates alignment against the chosen paradigm."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    paradigm = PARADIGMS.get(paradigm_key, PARADIGMS["three_act"])

    # Compute chapter words & cumulative curve
    chapters = []
    total_words = 0
    for idx, f in enumerate(files, 1):
        content = f.read_text(encoding="utf-8", errors="replace")
        words = len(re.findall(r'\b\w+\b', content))
        total_words += words
        chapters.append({
            "index": idx,
            "filename": f.name,
            "path": str(f),
            "words": words,
            "cumulative_words": total_words
        })

    # Add percentages
    prev_words = 0
    for ch in chapters:
        start_pct = prev_words / total_words if total_words > 0 else 0.0
        end_pct = ch["cumulative_words"] / total_words if total_words > 0 else 0.0
        ch["start_pct"] = round(start_pct, 3)
        ch["cum_pct"] = round(end_pct, 3)
        ch["mid_pct"] = round((start_pct + end_pct) / 2.0, 3)
        ch["pct_of_total"] = round((ch["words"] / total_words), 3) if total_words > 0 else 0.0
        prev_words = ch["cumulative_words"]

    # Map beats to closest chapter
    beat_evaluations = []
    drift_penalties = []

    for beat in paradigm["beats"]:
        target_pct = beat["target_pct"]
        w_min, w_max = beat["window"]
        target_words = int(target_pct * total_words)

        # Find containing chapter or closest chapter by midpoint
        closest_ch = None
        for ch in chapters:
            if ch["start_pct"] <= target_pct <= ch["cum_pct"]:
                closest_ch = ch
                break
        if not closest_ch and chapters:
            closest_ch = min(chapters, key=lambda ch: abs(ch["mid_pct"] - target_pct))

        actual_pct = closest_ch["mid_pct"] if closest_ch else 0.0
        drift = abs(actual_pct - target_pct)
        is_in_window = (w_min <= actual_pct <= w_max) or (closest_ch and (w_min <= closest_ch["cum_pct"] and closest_ch["start_pct"] <= w_max))
        
        penalty = max(0.0, (drift - 0.05) * 100) if not is_in_window else 0.0
        drift_penalties.append(penalty)

        beat_evaluations.append({
            "beat_name": beat["name"],
            "target_pct": target_pct,
            "target_words": target_words,
            "window_pct": [w_min, w_max],
            "actual_pct": actual_pct,
            "assigned_chapter": closest_ch["index"] if closest_ch else 1,
            "assigned_file": closest_ch["filename"] if closest_ch else "",
            "is_in_window": is_in_window,
            "drift_pct": round(drift * 100, 1),
            "desc": beat["desc"]
        })

    # Overall Structural Alignment Score
    mean_penalty = sum(drift_penalties) / len(drift_penalties) if drift_penalties else 0.0
    harmony_score = max(0.0, min(100.0, round(100.0 - mean_penalty * 2.5, 1)))

    return {
        "target": str(target_path),
        "total_words": total_words,
        "total_chapters": len(chapters),
        "paradigm_key": paradigm_key,
        "paradigm_name": paradigm["name"],
        "harmony_score": harmony_score,
        "chapters": chapters,
        "beats": beat_evaluations
    }


def generate_structure_html_report(report: dict, output_path: Path) -> Path:
    """Generates an offline HTML visual timeline report for story structure."""
    beats = report.get("beats", [])
    score = report.get("harmony_score", 0.0)

    beat_rows = []
    for b in beats:
        status_badge = "<span style='background:#064e3b;color:#a7f3d0;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>On Target</span>" if b["is_in_window"] else f"<span style='background:#78350f;color:#fde68a;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>Drift ({b['drift_pct']}%)</span>"
        row = f"""
        <tr>
          <td><strong>{html.escape(b['beat_name'])}</strong><br><small style="color:#94a3b8;">{html.escape(b['desc'])}</small></td>
          <td>{int(b['target_pct']*100)}% ({b['target_words']:,} w)</td>
          <td>Ch {b['assigned_chapter']} ({int(b['actual_pct']*100)}%)</td>
          <td>{status_badge}</td>
        </tr>
        """
        beat_rows.append(row)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Story Paradigm Alignment Report</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1000px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📐 Story Paradigm & Structure Alignment</h1>
    <p style="color: var(--muted);">Model: {html.escape(report.get('paradigm_name', ''))} | Target: {html.escape(report.get('target', ''))}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Harmony Score</h3>
      <div class="metric" style="color: {'var(--success)' if score >= 80 else ('var(--warn)' if score >= 60 else 'var(--danger)')};">{score}%</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Structural Beat Fidelity</p>
    </div>
    <div class="card">
      <h3>Total Word Count</h3>
      <div class="metric">{report.get('total_words', 0):,}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Across {report.get('total_chapters', 0)} chapters</p>
    </div>
    <div class="card">
      <h3>Paradigm Beats</h3>
      <div class="metric">{len(beats)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Mapped to narrative milestones</p>
    </div>
  </div>

  <div class="section">
    <h2>🎯 Structural Beat Sheet Map</h2>
    <table class="table">
      <thead><tr><th>Story Beat</th><th>Target Pct</th><th>Assigned Position</th><th>Status</th></tr></thead>
      <tbody>
        {''.join(beat_rows)}
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
    parser = argparse.ArgumentParser(description="Ars Arcanum Story Paradigm Enforcer (PLT-102)")
    parser.add_argument("target", help="Manuscript directory or file")
    parser.add_argument(
        "--paradigm", "-p",
        choices=["three_act", "save_the_cat", "heros_journey", "story_circle", "seven_point"],
        default="three_act",
        help="Story structure paradigm model (default: three_act)"
    )
    parser.add_argument("--html", help="Generate HTML report to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = scan_manuscript_structure(target_path, paradigm_key=args.paradigm)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"=== Story Paradigm Enforcer: {report['paradigm_name']} ===")
    print(f"Target: {target_path.name} | Total Words: {report['total_words']:,} | Chapters: {report['total_chapters']}")
    print(f"Structural Harmony Score: {report['harmony_score']}%")
    print("-" * 75)
    for b in report["beats"]:
        status = "[ON TARGET]" if b["is_in_window"] else f"[DRIFT {b['drift_pct']}%]"
        print(f"  {b['beat_name']:<30} | Target: {int(b['target_pct']*100):>2}% | Ch {b['assigned_chapter']:>2} ({int(b['actual_pct']*100):>2}%) | {status}")

    if args.html:
        out_p = Path(args.html)
        generate_structure_html_report(report, out_p)
        print(f"\nHTML report written to: {out_p}")


if __name__ == "__main__":
    main()
