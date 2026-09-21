#!/usr/bin/env python3
"""
Ars Arcanum Portfolio Dashboard & Author Velocity Analytics
(scripts/lib/portfolio.py)
================================================================================
Zero-dependency, offline author portfolio dashboard and catalog analytics engine.

Capabilities (OPS-103):
1. Multi-Manuscript Portfolio Aggregation:
   - Scans ~/Manuscripts/ and ~/Universes/ for novel projects, volumes, and drafts.
   - Calculates total catalog word counts, chapter counts, and volume counts.
2. Lifecycle & Editorial Stage Tracking:
   - Identifies status: Scaffolding, First Draft, Revisions, Pre-Flight, Published.
   - Computes target completion percentages and wordcount milestones.
3. Standalone HTML Portfolio Hub:
   - Interactive dashboard with progress bars, velocity metrics, and project cards.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import json
import html
import datetime
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

logger = logging.getLogger("arcanum.portfolio")


def analyze_manuscript_project(ms_dir: Path) -> dict:
    """Analyzes a single manuscript directory for stats, stage, and word counts."""
    manifest_path = ms_dir / "manuscript.yaml"
    meta = {}
    if manifest_path.is_file():
        for line in manifest_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip().strip('"\'')

    title = meta.get("title", ms_dir.name.replace("_", " "))
    author = meta.get("author", "Author")
    target_words = int(meta.get("target_words", 80000))

    # Chapters and volumes
    volumes = sorted([d.name for d in ms_dir.glob("Book-*") if d.is_dir()])
    if not volumes:
        volumes = ["Book-01"]

    chapter_files = [f for f in ms_dir.rglob("*.md") if not f.name.startswith((".", "_")) and "Backups" not in f.parts and "04_Back_Matter" not in f.parts]

    total_words = 0
    for cf in chapter_files:
        try:
            txt = cf.read_text(encoding="utf-8", errors="replace")
            total_words += len(re.findall(r'\b\w+\b', txt))
        except Exception:
            pass

    # Determine stage
    progress_pct = round((total_words / target_words * 100), 1) if target_words > 0 else 0.0
    stage = "Scaffolding"
    if total_words >= target_words:
        stage = "Revisions / Pre-Flight"
    elif total_words >= target_words * 0.5:
        stage = "Drafting (Act II/III)"
    elif total_words > 1000:
        stage = "Drafting (Act I)"

    exports_dir = ms_dir / "Exports"
    has_exports = exports_dir.is_dir() and any(exports_dir.glob("*.pdf"))
    if has_exports and progress_pct >= 90:
        stage = "Publication-Ready"

    return {
        "id": ms_dir.name,
        "title": title,
        "author": author,
        "path": str(ms_dir),
        "volumes": volumes,
        "volume_count": len(volumes),
        "chapter_count": len(chapter_files),
        "word_count": total_words,
        "target_words": target_words,
        "progress_pct": min(100.0, progress_pct),
        "stage": stage,
        "has_exports": has_exports
    }


def scan_portfolio(root_dir: Path | None = None) -> dict:
    """Scans all manuscripts in the environment."""
    candidates = []
    if root_dir and root_dir.is_dir():
        candidates.append(root_dir)
    else:
        home = Path.home()
        candidates.extend([
            home / "Manuscripts",
            home / "Coding Projects" / "7-Scriptorium" / "fixtures",
            home / "Coding Projects" / "7-Scriptorium" / "templates"
        ])

    manuscript_dirs = []
    for c in candidates:
        if c.is_dir():
            # Check if c itself is directly a manuscript project
            if (c / "manuscript.yaml").is_file() or (c / "Book-01").is_dir() or any(c.glob("*.nwx")):
                manuscript_dirs.append(c)
            else:
                # Look for subdirectories with manuscript.yaml or Book-*
                for sub in sorted(c.iterdir()):
                    if sub.is_dir() and not sub.name.startswith((".", "_")) and ((sub / "manuscript.yaml").is_file() or (sub / "Book-01").is_dir() or any(sub.glob("*.nwx"))):
                        manuscript_dirs.append(sub)

    projects = [analyze_manuscript_project(d) for d in manuscript_dirs]
    total_words = sum(p["word_count"] for p in projects)
    total_chapters = sum(p["chapter_count"] for p in projects)
    total_volumes = sum(p["volume_count"] for p in projects)

    return {
        "scan_time": datetime.datetime.now().isoformat(),
        "total_projects": len(projects),
        "total_words": total_words,
        "total_chapters": total_chapters,
        "total_volumes": total_volumes,
        "projects": projects
    }


def generate_portfolio_html(report: dict, output_path: Path) -> Path:
    """Generates a standalone HTML portfolio hub."""
    projects = report.get("projects", [])
    total_words = report.get("total_words", 0)

    proj_cards = []
    for p in projects:
        card = f"""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:1.5rem;margin-bottom:1rem;">
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <h3 style="margin:0;color:#38bdf8;font-size:1.25rem;">{html.escape(p['title'])}</h3>
            <span style="background:#334155;color:#94a3b8;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:700;">{html.escape(p['stage'])}</span>
          </div>
          <p style="color:#94a3b8;font-size:0.875rem;margin:0.5rem 0;">{p['volume_count']} Volumes | {p['chapter_count']} Chapters | {p['word_count']:,} / {p['target_words']:,} words ({p['progress_pct']}%)</p>
          <div style="background:#0f172a;border-radius:6px;height:10px;overflow:hidden;margin-top:0.75rem;">
            <div style="background:#38bdf8;height:100%;width:{p['progress_pct']}%;"></div>
          </div>
        </div>
        """
        proj_cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Author Portfolio Hub</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 950px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📚 Author Portfolio & Catalog Dashboard</h1>
    <p style="color: var(--muted);">Unified Authorial Progress & Editorial Pipeline</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Active Manuscripts</h3>
      <div class="metric">{report.get('total_projects', 0)}</div>
    </div>
    <div class="card">
      <h3>Total Catalog Words</h3>
      <div class="metric">{total_words:,}</div>
    </div>
    <div class="card">
      <h3>Total Chapters</h3>
      <div class="metric">{report.get('total_chapters', 0)}</div>
    </div>
    <div class="card">
      <h3>Total Volumes</h3>
      <div class="metric">{report.get('total_volumes', 0)}</div>
    </div>
  </div>

  <h2>📖 Manuscript Projects</h2>
  {''.join(proj_cards) or '<p style="color:var(--muted);">No active manuscripts discovered.</p>'}
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Portfolio Dashboard (OPS-103)")
    parser.add_argument("path", nargs="?", help="Optional root path to scan for manuscripts")
    parser.add_argument("--html", help="Generate HTML portfolio hub to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    root_p = Path(args.path) if args.path else None
    report = scan_portfolio(root_p)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=== Ars Arcanum Author Portfolio Dashboard ===")
    print(f"Projects: {report['total_projects']} | Catalog Words: {report['total_words']:,} | Chapters: {report['total_chapters']}")
    print("-" * 75)
    for p in report["projects"]:
        print(f"  📖 {p['title']:<24} | {p['stage']:<20} | {p['word_count']:>6,} / {p['target_words']:>6,} w ({p['progress_pct']:>5.1f}%)")

    if args.html:
        out_p = Path(args.html)
        generate_portfolio_html(report, out_p)
        print(f"\nHTML Portfolio Hub written to: {out_p}")


if __name__ == "__main__":
    main()
