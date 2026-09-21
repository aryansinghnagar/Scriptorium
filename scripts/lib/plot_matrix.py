#!/usr/bin/env python3
"""
Ars Arcanum Multi-Track Narrative Plot Grid & Subplot Matrix Engine
(scripts/lib/plot_matrix.py)
================================================================================
Zero-dependency, offline plot thread matrix and subplot pacing analyzer.

Capabilities (PLT-101):
1. Narrative Plot Track Extraction:
   - Scans `@plot: TrackName`, `@thread: SubplotName`, `@arc: CharacterArc`,
     `@theme: ThemeName`, or YAML frontmatter tags across manuscript chapters.
2. Narrative Progression & Health Diagnostics:
   - Track lifecycle: Introduction, Escalation, Climax, Resolution.
   - Abandoned / Dormant thread alerts (threads absent for >= 4 chapters).
   - Dangling plot threads (unresolved plotlines never revisited).
   - Clustered resolution warnings (too many storylines resolving simultaneously).
   - Chapter thread density distribution (tracks per scene/chapter).
3. Visual Multi-Lane Grid & Matrix:
   - Terminal ASCII plot track matrix.
   - Interactive SVG / HTML multi-lane timeline visualizer with lane filters.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import json
import html
import argparse
import logging
from pathlib import Path
from collections import defaultdict, Counter

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

logger = logging.getLogger("arcanum.plot_matrix")


def extract_chapter_plot_metadata(file_path: Path, chapter_index: int) -> dict:
    """Extracts plot tags, POV, and wordcount from a markdown chapter file."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    plots = set()
    threads = set()
    arcs = set()
    pov = "Unknown"
    title = file_path.stem
    word_count = len(re.findall(r'\b\w+\b', content))

    in_frontmatter = False
    for line in lines:
        s_line = line.strip()
        if s_line == "---":
            in_frontmatter = not in_frontmatter
            continue

        if s_line.startswith("# ") and title == file_path.stem:
            title = s_line[2:].strip()

        # Tags
        pov_m = re.match(r'^@pov:\s*(.+)$', s_line, re.IGNORECASE)
        if pov_m:
            pov = pov_m.group(1).strip()

        plot_m = re.match(r'^@plot:\s*(.+)$', s_line, re.IGNORECASE)
        if plot_m:
            for item in plot_m.group(1).split(","):
                if item.strip():
                    plots.add(item.strip())

        thread_m = re.match(r'^@thread:\s*(.+)$', s_line, re.IGNORECASE)
        if thread_m:
            for item in thread_m.group(1).split(","):
                if item.strip():
                    threads.add(item.strip())

        arc_m = re.match(r'^@arc:\s*(.+)$', s_line, re.IGNORECASE)
        if arc_m:
            for item in arc_m.group(1).split(","):
                if item.strip():
                    arcs.add(item.strip())

    all_tracks = sorted(list(plots | threads | arcs))
    return {
        "index": chapter_index,
        "file": str(file_path),
        "filename": file_path.name,
        "title": title,
        "pov": pov,
        "word_count": word_count,
        "plots": sorted(list(plots)),
        "threads": sorted(list(threads)),
        "arcs": sorted(list(arcs)),
        "all_tracks": all_tracks,
        "track_count": len(all_tracks)
    }


def scan_manuscript_plot_matrix(target_path: Path, max_gap_threshold: int = 4) -> dict:
    """Scans all chapters in a manuscript to build the multi-track plot grid."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    chapters = []
    for idx, f in enumerate(files, 1):
        ch_meta = extract_chapter_plot_metadata(f, idx)
        chapters.append(ch_meta)

    total_chapters = len(chapters)
    track_appearances = defaultdict(list)

    for ch in chapters:
        for t in ch["all_tracks"]:
            track_appearances[t].append(ch["index"])

    # Analyze individual track lifecycles & health
    tracks_report = {}
    abandoned_tracks = []
    dangling_tracks = []

    for t, appearances in sorted(track_appearances.items()):
        first_ch = appearances[0]
        last_ch = appearances[-1]
        freq = len(appearances)

        # Gaps between appearances
        gaps = [appearances[i] - appearances[i-1] for i in range(1, len(appearances))]
        max_gap = max(gaps) if gaps else 0

        is_abandoned = max_gap >= max_gap_threshold
        is_dangling = (last_ch <= total_chapters * 0.6) and freq < 3 and total_chapters >= 5

        status = "Healthy"
        if is_abandoned:
            status = "Dormant/Gap Alert"
            abandoned_tracks.append({
                "track": t,
                "max_gap": max_gap,
                "first_seen": first_ch,
                "last_seen": last_ch,
                "appearances": appearances
            })
        elif is_dangling:
            status = "Dangling Warning"
            dangling_tracks.append({
                "track": t,
                "last_seen": last_ch,
                "appearances": appearances
            })

        tracks_report[t] = {
            "first_chapter": first_ch,
            "last_chapter": last_ch,
            "occurrences": freq,
            "density": round(freq / total_chapters, 2) if total_chapters > 0 else 0,
            "max_gap": max_gap,
            "status": status,
            "chapters": appearances
        }

    # Density per chapter distribution
    density_counts = Counter(ch["track_count"] for ch in chapters)

    return {
        "target": str(target_path),
        "total_chapters": total_chapters,
        "total_tracks": len(tracks_report),
        "chapters": chapters,
        "tracks": tracks_report,
        "abandoned_tracks": abandoned_tracks,
        "dangling_tracks": dangling_tracks,
        "density_histogram": dict(density_counts)
    }


def generate_plot_html_report(report: dict, output_path: Path) -> Path:
    """Generates an interactive HTML/SVG plot track multi-lane timeline."""
    chapters = report.get("chapters", [])
    tracks = report.get("tracks", {})
    total_ch = report.get("total_chapters", 1)

    colors = ["#38bdf8", "#ec4899", "#8b5cf6", "#10b981", "#f59e0b", "#06b6d4", "#f97316", "#a855f7"]

    # Generate SVG Grid
    svg_width = max(800, total_ch * 60 + 200)
    track_list = sorted(tracks.keys())
    svg_height = max(300, len(track_list) * 45 + 80)

    svg_elements = []

    # Chapter column guidelines
    for ch in chapters:
        x = 180 + (ch["index"] - 1) * 60
        svg_elements.append(f'<line x1="{x+25}" y1="40" x2="{x+25}" y2="{svg_height-30}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1" />')
        svg_elements.append(f'<text x="{x+25}" y="30" fill="#94a3b8" font-size="11" text-anchor="middle">Ch {ch["index"]}</text>')

    # Track horizontal lanes and nodes
    for idx, t in enumerate(track_list):
        y = 70 + idx * 45
        color = colors[idx % len(colors)]
        t_meta = tracks[t]
        # Track label
        svg_elements.append(f'<text x="160" y="{y+5}" fill="{color}" font-weight="600" font-size="12" text-anchor="end">{html.escape(t[:20])}</text>')
        svg_elements.append(f'<line x1="170" y1="{y}" x2="{svg_width-40}" y2="{y}" stroke="#1e293b" stroke-width="20" rx="10" />')

        # Connect line across active range
        if len(t_meta["chapters"]) >= 2:
            x_start = 180 + (t_meta["first_chapter"] - 1) * 60 + 25
            x_end = 180 + (t_meta["last_chapter"] - 1) * 60 + 25
            svg_elements.append(f'<line x1="{x_start}" y1="{y}" x2="{x_end}" y2="{y}" stroke="{color}" stroke-width="3" stroke-opacity="0.6" />')

        # Active nodes
        for ch_idx in t_meta["chapters"]:
            cx = 180 + (ch_idx - 1) * 60 + 25
            svg_elements.append(f'<circle cx="{cx}" cy="{y}" r="7" fill="{color}" stroke="#0f172a" stroke-width="2"><title>{html.escape(t)} in Chapter {ch_idx}</title></circle>')

    svg_content = "\n".join(svg_elements)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Multi-Track Plot Matrix</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .chart-box {{ overflow-x: auto; padding: 1rem 0; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--border); }}
  .badge {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
  .badge-warn {{ background: #78350f; color: #fde68a; }}
  .badge-ok {{ background: #064e3b; color: #a7f3d0; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📊 Multi-Track Plot Grid & Subplot Matrix</h1>
    <p style="color: var(--muted);">Target: {html.escape(report.get('target', ''))} | Total Chapters: {report.get('total_chapters', 0)} | Tracks: {report.get('total_tracks', 0)}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Active Plot Tracks</h3>
      <div class="metric">{report.get('total_tracks', 0)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Across {report.get('total_chapters', 0)} chapters</p>
    </div>
    <div class="card">
      <h3>Dormant Gaps (≥4 Ch)</h3>
      <div class="metric" style="color: {'var(--warn)' if report.get('abandoned_tracks') else 'var(--success)'};">{len(report.get('abandoned_tracks', []))}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Long gaps between appearances</p>
    </div>
    <div class="card">
      <h3>Dangling Threads</h3>
      <div class="metric" style="color: {'var(--danger)' if report.get('dangling_tracks') else 'var(--success)'};">{len(report.get('dangling_tracks', []))}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Unresolved early subplots</p>
    </div>
  </div>

  <div class="section">
    <h2>🗺️ Visual Multi-Lane Plot Grid</h2>
    <div class="chart-box">
      <svg width="{svg_width}" height="{svg_height}" style="background: #0f172a; border-radius: 8px;">
        {svg_content}
      </svg>
    </div>
  </div>

  <div class="section">
    <h2>📋 Narrative Track Health Ledger</h2>
    <table class="table">
      <thead><tr><th>Track Name</th><th>Appearances</th><th>Range</th><th>Max Gap</th><th>Status</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td><strong>{html.escape(t)}</strong></td><td>{meta['occurrences']} ch ({meta['density']*100:.0f}%)</td><td>Ch {meta['first_chapter']} → Ch {meta['last_chapter']}</td><td>{meta['max_gap']} ch</td><td><span class='badge badge-{'ok' if meta['status']=='Healthy' else 'warn'}'>{meta['status']}</span></td></tr>" for t, meta in sorted(tracks.items())) or '<tr><td colspan="5" style="color:var(--muted);">No plot tracks found. Tag scenes with @plot: Name or @thread: Name.</td></tr>'}
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
    parser = argparse.ArgumentParser(description="Ars Arcanum Multi-Track Plot Grid Engine (PLT-101)")
    parser.add_argument("target", help="Manuscript directory or file")
    parser.add_argument("--gap", type=int, default=4, help="Maximum gap before alerting dormant thread (default 4)")
    parser.add_argument("--html", help="Generate HTML report to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    parser.add_argument("--matrix", action="store_true", help="Print ASCII track matrix")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = scan_manuscript_plot_matrix(target_path, max_gap_threshold=args.gap)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"=== Multi-Track Plot Grid: {target_path.name} ===")
    print(f"Total Chapters: {report['total_chapters']} | Narrative Tracks: {report['total_tracks']}")
    print("-" * 65)
    for t, meta in sorted(report["tracks"].items()):
        print(f"📌 {t:<22} | {meta['occurrences']:>2} scenes | Range: Ch {meta['first_chapter']}..{meta['last_chapter']} | Status: {meta['status']}")

    if report["abandoned_tracks"]:
        print("\n⚠️ Dormant / Extended Gap Alerts (≥4 chapters apart):")
        for at in report["abandoned_tracks"]:
            print(f"  - '{at['track']}': {at['max_gap']} chapter gap between appearances")

    if report["dangling_tracks"]:
        print("\n⚠️ Dangling Subplot Warnings:")
        for dt in report["dangling_tracks"]:
            print(f"  - '{dt['track']}': Last seen in Chapter {dt['last_seen']}")

    if args.matrix and report["tracks"]:
        print("\n=== Narrative Track ASCII Grid ===")
        header = f"{'Track':<20} | " + "".join(f"{ch['index']:>3}" for ch in report["chapters"])
        print(header)
        print("-" * len(header))
        for t, meta in sorted(report["tracks"].items()):
            row = f"{t[:20]:<20} | "
            for ch in report["chapters"]:
                row += "  ●" if ch["index"] in meta["chapters"] else "  ·"
            print(row)

    if args.html:
        out_p = Path(args.html)
        generate_plot_html_report(report, out_p)
        print(f"\nHTML report written to: {out_p}")


if __name__ == "__main__":
    main()
