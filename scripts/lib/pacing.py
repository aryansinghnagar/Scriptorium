#!/usr/bin/env python3
"""
Ars Arcanum Narrative Pacing, POV Balance & Tension Arc Analytics (scripts/lib/pacing.py)
=======================================================================================
Offline narrative analytics suite for novelists and authors. Evaluates prose rhythm,
dialogue-to-exposition density ratios, sentence length variance, POV screen-time balance,
subplot thread momentum, and chapter tension curves.

Capabilities:
1. Pacing & Prose Rhythm Analytics:
   - Dialogue vs Action vs Exposition density ratios
   - Sentence length mean, variance, and standard deviation (staccato vs flowing cadence)
   - Paragraph length distribution
2. POV Distribution & Screen-Time Balance:
   - Word count allocation per POV character
   - Consecutive absence / POV starvation warnings (>3 chapters without active scene)
3. Subplot Thread Momentum Matrix:
   - Tracks `@thread:` and `@plot:` progression across acts and chapters
   - Identifies stalled or abandoned plot threads
4. Narrative Tension Arc Curve Modeling:
   - Composite tension index (0-100) per chapter based on syntactic cadence,
     conflict sentiment density, dialogue pacing, and `@tension:` / `@climax` directives
5. Interactive Standalone HTML Report with SVG Visualization Charts

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
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.pacing")

SENTENCE_REGEX = re.compile(r"(?<=[.!?])\s+")
DIALOGUE_REGEX = re.compile(r'["“][^"“”]*["”]|(?<=\s)[\'‘][^\'‘’]*[\'’]')
TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")

# Conflict & Tension Keywords (case-insensitive)
CONFLICT_KEYWORDS = {
    "blood", "blade", "sword", "gun", "strike", "wound", "fire", "flame", "shadow", "dark",
    "scream", "shout", "whisper", "gasp", "death", "die", "kill", "danger", "trap", "run",
    "flee", "clash", "crash", "fear", "terror", "dread", "panic", "sudden", "breath", "pulse",
    "heart", "fall", "shatter", "break", "burst", "rage", "fury", "cold", "pain", "bleed",
    "stealth", "silence", "freeze", "edge", "iron", "steel", "abyss", "threat", "enemy", "war"
}


def analyze_chapter_text(text: str) -> dict:
    """Analyzes prose metrics for a single chapter or scene."""
    lines = text.splitlines()
    prose_lines = []
    tags = defaultdict(list)

    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("@"):
            m = TAG_REGEX.match(clean)
            if m:
                t_name = m.group(1).lower()
                t_val = m.group(2).strip()
                tags[t_name].append(t_val)
        elif not clean.startswith("#"):
            prose_lines.append(clean)

    full_prose = "\n\n".join(prose_lines)
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", full_prose)
    word_count = len(words)

    if word_count == 0:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "mean_sentence_length": 0.0,
            "sentence_variance": 0.0,
            "dialogue_ratio": 0.0,
            "exposition_ratio": 0.0,
            "action_ratio": 0.0,
            "tension_score": 0.0,
            "tags": dict(tags)
        }

    # Dialogue extraction
    dialogue_matches = DIALOGUE_REGEX.findall(full_prose)
    dialogue_words = sum(len(re.findall(r"\b[A-Za-z0-9'-]+\b", m)) for m in dialogue_matches)
    dialogue_ratio = dialogue_words / word_count if word_count > 0 else 0.0

    # Sentence length metrics
    sentences = [s.strip() for s in SENTENCE_REGEX.split(full_prose) if s.strip()]
    sentence_count = len(sentences)
    sent_lengths = [len(re.findall(r"\b[A-Za-z0-9'-]+\b", s)) for s in sentences if s]

    if sent_lengths:
        mean_len = sum(sent_lengths) / len(sent_lengths)
        variance = sum((l - mean_len) ** 2 for l in sent_lengths) / len(sent_lengths)
        std_dev = math.sqrt(variance)
    else:
        mean_len = 0.0
        variance = 0.0
        std_dev = 0.0

    # Tension & conflict keyword density
    conflict_word_count = sum(1 for w in words if w.lower() in CONFLICT_KEYWORDS)
    conflict_density = conflict_word_count / word_count if word_count > 0 else 0.0

    # Short sentence factor (sentences < 8 words indicate fast action/tempo)
    short_sent_ratio = (sum(1 for l in sent_lengths if l <= 8) / sentence_count) if sentence_count > 0 else 0.0

    # Long sentence factor (> 24 words indicates exposition/reflection)
    long_sent_ratio = (sum(1 for l in sent_lengths if l >= 24) / sentence_count) if sentence_count > 0 else 0.0

    exposition_ratio = max(0.0, min(1.0, (1.0 - dialogue_ratio) * 0.6 + long_sent_ratio * 0.4))
    action_ratio = max(0.0, min(1.0, (1.0 - exposition_ratio - dialogue_ratio) * 0.5 + short_sent_ratio * 0.5))

    # Composite tension index (0 to 100)
    # Check manual tension override in @tension: tag
    manual_tension = None
    if "tension" in tags:
        try:
            manual_tension = float(tags["tension"][0]) * 10.0 if float(tags["tension"][0]) <= 10 else float(tags["tension"][0])
        except ValueError:
            pass

    if manual_tension is not None:
        tension_score = max(0.0, min(100.0, manual_tension))
    else:
        base_tension = 30.0
        base_tension += conflict_density * 400.0        # Up to +40 for high conflict words
        base_tension += short_sent_ratio * 35.0        # Up to +35 for staccato action sentences
        base_tension += (dialogue_ratio * 20.0)        # Up to +20 for dialogue tension
        base_tension -= (long_sent_ratio * 25.0)       # Down for heavy exposition
        if "climax" in tags or any("climax" in t for t in tags.get("plot", [])):
            base_tension += 25.0
        tension_score = max(10.0, min(98.0, base_tension))

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "mean_sentence_length": round(mean_len, 2),
        "sentence_std_dev": round(std_dev, 2),
        "sentence_variance": round(variance, 2),
        "dialogue_ratio": round(dialogue_ratio, 3),
        "exposition_ratio": round(exposition_ratio, 3),
        "action_ratio": round(action_ratio, 3),
        "conflict_density": round(conflict_density, 4),
        "tension_score": round(tension_score, 1),
        "tags": dict(tags),
    }


def scan_manuscript_pacing(manuscript_dir: Path, target_book: str = None) -> dict:
    """Scans all chapters in manuscript and computes overall pacing, POV balance, and tension arc."""
    chapters = []
    pov_totals = defaultdict(int)
    pov_chapters = defaultdict(list)
    thread_chapters = defaultdict(list)

    # Collect markdown files (exclude World Bible folders and non-manuscript artifacts)
    excluded_folders = {
        "Outlines", "Exports", "Backups", "04_Back_Matter",
        "00-World-Bible", "World-Bible", "Characters", "Locations",
        "Cosmology", "Languages", "Magic-Technology", "Templates", ".obsidian", ".git"
    }

    md_files = []
    for f in sorted(manuscript_dir.rglob("*.md")):
        if any(part.startswith(".") or part in excluded_folders for part in f.parts):
            continue
        if target_book and target_book.lower() not in [p.lower() for p in f.parts]:
            continue
        md_files.append(f)

    for idx, f in enumerate(md_files, 1):
        content = f.read_text(encoding="utf-8", errors="replace")
        rel_path = str(f.relative_to(manuscript_dir)).replace("\\", "/")
        
        # Determine chapter title
        title = f.stem.replace("_", " ")
        for l in content.splitlines()[:5]:
            if l.startswith("# "):
                title = l[2:].strip()
                break

        metrics = analyze_chapter_text(content)
        metrics["index"] = idx
        metrics["file"] = rel_path
        metrics["title"] = title

        # POV attribution
        pov_list = metrics["tags"].get("pov", [])
        primary_pov = pov_list[0].strip("[]\"'") if pov_list else "Omniscient"
        metrics["primary_pov"] = primary_pov

        pov_totals[primary_pov] += metrics["word_count"]
        pov_chapters[primary_pov].append(idx)

        # Thread attribution
        for t in metrics["tags"].get("thread", []) + metrics["tags"].get("plot", []):
            clean_t = t.strip("[]\"'")
            if clean_t:
                thread_chapters[clean_t].append(idx)

        chapters.append(metrics)

    total_words = sum(c["word_count"] for c in chapters)

    # Calculate POV balance & starvation
    pov_stats = {}
    for pov, words in pov_totals.items():
        ch_list = pov_chapters[pov]
        # Calculate max gap between chapters
        max_gap = 0
        if len(ch_list) > 1:
            gaps = [ch_list[i] - ch_list[i-1] for i in range(1, len(ch_list))]
            max_gap = max(gaps)
        elif len(chapters) > 1:
            max_gap = len(chapters) - 1

        share = (words / total_words * 100.0) if total_words > 0 else 0.0
        starved = max_gap > 3 and share > 10.0

        pov_stats[pov] = {
            "word_count": words,
            "share_percent": round(share, 1),
            "chapter_count": len(ch_list),
            "chapters": ch_list,
            "max_chapter_gap": max_gap,
            "starvation_warning": starved,
        }

    # Thread continuity
    threads_stats = {}
    for t_name, ch_list in thread_chapters.items():
        threads_stats[t_name] = {
            "chapter_count": len(ch_list),
            "chapters": ch_list,
            "active_span": f"Ch {min(ch_list)} – Ch {max(ch_list)}",
            "is_recent": (len(chapters) - max(ch_list)) <= 2,
        }

    return {
        "manuscript": manuscript_dir.name,
        "total_chapters": len(chapters),
        "total_words": total_words,
        "chapters": chapters,
        "pov_distribution": pov_stats,
        "thread_momentum": threads_stats,
    }


# ==============================================================================
# HTML & Visual SVG Chart Generator
# ==============================================================================

def generate_pacing_html_report(report: dict, output_file: Path):
    """Generates an interactive HTML pacing & tension curve report with pure SVG charts."""
    chaps = report["chapters"]
    
    # Generate SVG Tension Curve
    svg_width = 800
    svg_height = 240
    padding = 40
    plot_w = svg_width - 2 * padding
    plot_h = svg_height - 2 * padding

    points = []
    if chaps:
        x_step = plot_w / max(1, len(chaps) - 1) if len(chaps) > 1 else plot_w / 2
        for i, c in enumerate(chaps):
            x = padding + (i * x_step if len(chaps) > 1 else plot_w / 2)
            y = padding + plot_h - (c["tension_score"] / 100.0 * plot_h)
            points.append((x, y, c))

    path_d = ""
    circles = ""
    if points:
        path_d = f"M {points[0][0]},{points[0][1]}"
        for x, y, _ in points[1:]:
            path_d += f" L {x},{y}"

        for x, y, c in points:
            col = "#f85149" if c["tension_score"] >= 75 else "#58a6ff" if c["tension_score"] >= 45 else "#3fb950"
            circles += f"""<circle cx="{x}" cy="{y}" r="5" fill="{col}" stroke="#fff" stroke-width="1.5">
              <title>Ch {c['index']}: {html.escape(c['title'])} (Tension: {c['tension_score']})</title>
            </circle>\n"""

    svg_curve = f"""
    <svg viewBox="0 0 {svg_width} {svg_height}" class="chart-svg">
      <defs>
        <linearGradient id="curveGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#f85149" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#58a6ff" stop-opacity="0.0"/>
        </linearGradient>
      </defs>
      <!-- Grid Lines -->
      <line x1="{padding}" y1="{padding}" x2="{svg_width - padding}" y2="{padding}" stroke="#30363d" stroke-dasharray="4"/>
      <line x1="{padding}" y1="{padding + plot_h/2}" x2="{svg_width - padding}" y2="{padding + plot_h/2}" stroke="#30363d" stroke-dasharray="4"/>
      <line x1="{padding}" y1="{padding + plot_h}" x2="{svg_width - padding}" y2="{padding + plot_h}" stroke="#30363d"/>
      <!-- Labels -->
      <text x="{padding - 10}" y="{padding + 5}" fill="#8b949e" font-size="10" text-anchor="end">100</text>
      <text x="{padding - 10}" y="{padding + plot_h/2 + 4}" fill="#8b949e" font-size="10" text-anchor="end">50</text>
      <text x="{padding - 10}" y="{padding + plot_h + 4}" fill="#8b949e" font-size="10" text-anchor="end">0</text>
      <!-- Tension Path -->
      <path d="{path_d}" fill="none" stroke="#58a6ff" stroke-width="3" stroke-linecap="round"/>
      {circles}
    </svg>
    """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Narrative Pacing & Tension Analytics — {html.escape(report['manuscript'])}</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #58a6ff;
    --success: #3fb950;
    --warning: #d29922;
    --danger: #f85149;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  body {{ background-color: var(--bg); color: var(--text); font-family: var(--font); line-height: 1.6; margin: 0; padding: 24px; }}
  .container {{ max-width: 1040px; margin: 0 auto; }}
  header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ color: var(--accent); margin: 0 0 8px 0; }}
  .badge {{ background: #1f6feb22; color: var(--accent); border: 1px solid var(--accent); padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }}
  th {{ color: #8b949e; font-weight: 600; }}
  td {{ color: #f0f6fc; }}
  .chart-svg {{ width: 100%; height: auto; background: #0b0f14; border-radius: 6px; border: 1px solid var(--border); }}
  .starvation-tag {{ background: #f8514922; color: var(--danger); border: 1px solid var(--danger); padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
  footer {{ text-align: center; font-size: 12px; color: #8b949e; margin-top: 40px; border-top: 1px solid var(--border); padding-top: 16px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>📈 Narrative Pacing, POV Balance & Tension Arc</h1>
    <span class="badge">Manuscript: {html.escape(report['manuscript'])}</span>
    <span class="badge">Total Words: {report['total_words']:,}</span>
    <span class="badge">Chapters: {report['total_chapters']}</span>
  </header>

  <div class="card">
    <h2>Chapter Tension Arc Curve (0 – 100)</h2>
    {svg_curve}
  </div>

  <div class="card">
    <h2>POV Screen-Time Allocation</h2>
    <table>
      <tr><th>POV Character</th><th>Total Words</th><th>Share (%)</th><th>Chapters</th><th>Max Gap</th><th>Status</th></tr>
"""
    for pov, p_data in report["pov_distribution"].items():
        status = '<span class="starvation-tag">⚠️ POV Starvation</span>' if p_data["starvation_warning"] else '<span style="color: var(--success);">✓ Balanced</span>'
        html_content += f"""      <tr>
        <td><strong>{html.escape(pov)}</strong></td>
        <td>{p_data['word_count']:,}</td>
        <td>{p_data['share_percent']}%</td>
        <td>{p_data['chapter_count']}</td>
        <td>{p_data['max_chapter_gap']} chapters</td>
        <td>{status}</td>
      </tr>\n"""

    html_content += f"""    </table>
  </div>

  <div class="card">
    <h2>Chapter-by-Chapter Pacing Breakdown</h2>
    <table>
      <tr><th>#</th><th>Chapter</th><th>POV</th><th>Words</th><th>Mean Sent</th><th>Dialogue</th><th>Action</th><th>Exposition</th><th>Tension</th></tr>
"""
    for c in chaps:
        t_col = "color: var(--danger);" if c["tension_score"] >= 75 else "color: var(--accent);" if c["tension_score"] >= 45 else "color: var(--success);"
        html_content += f"""      <tr>
        <td>{c['index']}</td>
        <td><strong>{html.escape(c['title'])}</strong></td>
        <td>{html.escape(c['primary_pov'])}</td>
        <td>{c['word_count']:,}</td>
        <td>{c['mean_sentence_length']} wps</td>
        <td>{c['dialogue_ratio']*100:.1f}%</td>
        <td>{c['action_ratio']*100:.1f}%</td>
        <td>{c['exposition_ratio']*100:.1f}%</td>
        <td style="{t_col} font-weight: bold;">{c['tension_score']}</td>
      </tr>\n"""

    html_content += """    </table>
  </div>
  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    output_file.write_text(html_content, encoding="utf-8")


# ==============================================================================
# CLI Entrypoint & Formatting
# ==============================================================================

def print_sparkline(values: list) -> str:
    """Renders a Unicode text sparkline ( ▂▃▄▅▆▇█) for terminal visualization."""
    if not values:
        return ""
    bars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    min_v = min(values)
    max_v = max(values)
    if max_v == min_v:
        return "".join([bars[3] for _ in values])
    
    line = ""
    for v in values:
        idx = int((v - min_v) / (max_v - min_v) * (len(bars) - 1))
        line += bars[idx]
    return line


def resolve_manuscript_dir(target_str: str = None) -> str:
    """Resolves manuscript input string (path or name) to absolute directory path."""
    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for m_dir in sorted((home / "Manuscripts").glob("*")):
            if m_dir.is_dir() and m_dir.name.lower() == target_str.lower():
                return str(m_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)

    home = Path.home()
    mss = sorted((home / "Manuscripts").glob("*"), key=lambda p: str(p))
    mss = [p for p in mss if p.is_dir()]
    if len(mss) == 1:
        return str(mss[0])
    elif len(mss) > 1:
        print("Error: Multiple manuscripts discovered — specify one explicitly with -m/--manuscript.", file=sys.stderr)
        sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Narrative Pacing & Tension Analytics")
    subparsers = parser.add_subparsers(dest="subcommand", help="Pacing subcommands")

    # 1. pace
    p_pace = subparsers.add_parser("pace", help="Analyze narrative pacing, dialogue/action density, and rhythm")
    p_pace.add_argument("manuscript", nargs="?", help="Manuscript project directory")
    p_pace.add_argument("-m", "--manuscript", "--ms", dest="ms_flag", help="Manuscript project directory")
    p_pace.add_argument("-b", "--book", help="Filter by volume (e.g. 'Book-01')")
    p_pace.add_argument("--pov", action="store_true", help="Focus on POV distribution breakdown")
    p_pace.add_argument("--html", help="Path to export interactive HTML report")
    p_pace.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 2. tension
    p_ten = subparsers.add_parser("tension", help="Model chapter tension curves and climax arcs")
    p_ten.add_argument("manuscript", nargs="?", help="Manuscript project directory")
    p_ten.add_argument("-m", "--manuscript", "--ms", dest="ms_flag", help="Manuscript project directory")
    p_ten.add_argument("-b", "--book", help="Filter by volume (e.g. 'Book-01')")
    p_ten.add_argument("--html", help="Path to export interactive HTML report")
    p_ten.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. pov
    p_pov = subparsers.add_parser("pov", help="Analyze POV screen-time balance and starvation warnings")
    p_pov.add_argument("manuscript", nargs="?", help="Manuscript project directory")
    p_pov.add_argument("-m", "--manuscript", "--ms", dest="ms_flag", help="Manuscript project directory")
    p_pov.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    # Discover manuscript
    raw_ms = getattr(args, "ms_flag", None) or getattr(args, "manuscript", None)
    ms_dir = resolve_manuscript_dir(raw_ms)

    if not ms_dir or not Path(ms_dir).is_dir():
        print("Error: No valid Manuscript directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    report = scan_manuscript_pacing(Path(ms_dir), getattr(args, "book", None))

    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
        sys.exit(0)

    subcmd = args.subcommand or "pace"

    if subcmd in ("pace", "tension") and not getattr(args, "pov", False):
        print(f"\n\033[1;36m=== Ars Arcanum Narrative Pacing & Tension Report ===\033[0m")
        print(f"Manuscript: \033[1m{report['manuscript']}\033[0m | Total Words: \033[32m{report['total_words']:,}\033[0m | Chapters: \033[33m{report['total_chapters']}\033[0m\n")

        # Tension Sparkline
        tensions = [c["tension_score"] for c in report["chapters"]]
        if tensions:
            print(f"Tension Arc Sparkline: \033[1;35m{print_sparkline(tensions)}\033[0m (Avg: {sum(tensions)/len(tensions):.1f}/100)\n")

        print(f"{'#':<3} {'Chapter Title':<30} {'POV':<14} {'Words':<8} {'Dialogue':<10} {'Action':<8} {'Expo':<8} {'Tension':<8}")
        print("-" * 92)
        for c in report["chapters"]:
            t_col = "\033[31m" if c["tension_score"] >= 75 else "\033[36m" if c["tension_score"] >= 45 else "\033[32m"
            print(f"{c['index']:<3} {c['title'][:28]:<30} {c['primary_pov'][:12]:<14} {c['word_count']:<8} {c['dialogue_ratio']*100:>5.1f}%    {c['action_ratio']*100:>5.1f}%   {c['exposition_ratio']*100:>5.1f}%   {t_col}{c['tension_score']:>5.1f}\033[0m")
        print()

    if getattr(args, "pov", False) or subcmd == "pov":
        print(f"\n\033[1;33m=== POV Character Screen-Time Distribution ===\033[0m\n")
        print(f"{'POV Character':<20} {'Word Count':<12} {'Share (%)':<10} {'Chapters':<10} {'Status':<16}")
        print("-" * 70)
        for pov, p_data in report["pov_distribution"].items():
            status = "\033[31m⚠️ Starvation\033[0m" if p_data["starvation_warning"] else "\033[32m✓ Balanced\033[0m"
            print(f"{pov:<20} {p_data['word_count']:<12,} {p_data['share_percent']:>5.1f}%     {p_data['chapter_count']:<10} {status}")
        print()

    if getattr(args, "html", None):
        out_p = Path(args.html)
        generate_pacing_html_report(report, out_p)
        print(f"\nInteractive HTML report written to: {out_p}")


if __name__ == "__main__":
    main()
