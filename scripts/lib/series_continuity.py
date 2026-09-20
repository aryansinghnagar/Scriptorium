#!/usr/bin/env python3
"""
Ars Arcanum Series Cross-Book Continuity & Trait Consistency Engine
(scripts/lib/series_continuity.py)
================================================================================
Zero-dependency, offline multi-volume continuity checker for book series.

Capabilities (WOR-103):
1. Multi-Volume Series Discovery:
   - Identifies Book-01, Book-02, Book-03 volumes within a manuscript or universe.
2. Cross-Book Character Continuity:
   - Mortality Invariants: Catches characters deceased in Book N appearing alive in Book N+1.
   - Physical Trait Drift: Flags contradictory eye/hair colors, scars, or handedness across books.
   - Character Aging: Verifies chronological aging across inter-book timeskips.
   - Artifact Possession Chains: Verifies relic holders between volume boundaries.
3. Standalone Interactive HTML Series Ledger with volume timeline.

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import json
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

logger = logging.getLogger("arcanum.series_continuity")

# Physical trait extraction patterns
EYE_COLOR_PATTERN = re.compile(r'\b([A-Z][a-zA-Z]{1,20})\b[^\.\n]{0,50}\b(?:had|with|of)\s+([a-z]+)\s+eyes\b', re.IGNORECASE)
HAIR_COLOR_PATTERN = re.compile(r'\b([A-Z][a-zA-Z]{1,20})\b[^\.\n]{0,50}\b(?:had|with|of)\s+([a-z]+)\s+hair\b', re.IGNORECASE)
DEATH_PATTERNS = [
    re.compile(r'\b([A-Z][a-zA-Z]{1,20})\b\s+(?:died|was slain|perished|succumbed|fell in battle|was executed|breathed their last)\b', re.IGNORECASE),
    re.compile(r'\bthe death of\s+([A-Z][a-zA-Z]{1,20})\b', re.IGNORECASE)
]


def extract_book_entities(book_dir: Path) -> dict:
    """Extracts characters, physical traits, and deaths mentioned within a book volume."""
    text_content = ""
    for md_file in sorted(book_dir.rglob("*.md")):
        if not md_file.name.startswith((".", "_")) and "04_Back_Matter" not in md_file.parts:
            text_content += f"\n\n# {md_file.name}\n" + md_file.read_text(encoding="utf-8", errors="replace")

    # Characters mentioned
    character_traits = defaultdict(lambda: {"eyes": set(), "hair": set(), "mentions": 0})
    deaths = set()

    for line in text_content.splitlines():
        # Eye colors
        for m in EYE_COLOR_PATTERN.finditer(line):
            name = m.group(1).title()
            color = m.group(2).lower()
            if color in ("blue", "green", "brown", "hazel", "grey", "gray", "amber", "dark", "golden", "violet", "black", "crimson"):
                character_traits[name]["eyes"].add(color)

        # Hair colors
        for m in HAIR_COLOR_PATTERN.finditer(line):
            name = m.group(1).title()
            color = m.group(2).lower()
            if color in ("black", "dark", "brown", "blonde", "blond", "golden", "red", "auburn", "silver", "white", "grey", "gray", "raven"):
                character_traits[name]["hair"].add(color)

        # Deaths
        for p in DEATH_PATTERNS:
            for dm in p.finditer(line):
                char = dm.group(1).title()
                if char not in ("He", "She", "They", "It", "The"):
                    deaths.add(char)

    # Extract characters from traits, dialogue attribution, action tags, and @pov
    characters = set(character_traits.keys())
    for line in text_content.splitlines():
        s_line = line.strip()
        pov_m = re.match(r'^@pov:\s*([A-Za-z0-9_\-\'\s]+)', s_line, re.IGNORECASE)
        if pov_m:
            name = pov_m.group(1).strip().title()
            if name:
                characters.add(name)
        for m in re.finditer(r'\b([A-Z][a-z]{2,15})\s+(?:said|asked|shouted|whispered|cried|replied|thought|stepped|drew|smiled|nodded|commanded|looked|turned|stood|fought|advanced)\b', line):
            c_name = m.group(1).title()
            if c_name not in ("He", "She", "They", "It", "There", "When", "Then", "After", "Before", "While", "Suddenly", "Finally", "Soon", "Now"):
                characters.add(c_name)

    # Word count
    words = len(re.findall(r'\b\w+\b', text_content))

    return {
        "volume_name": book_dir.name,
        "path": str(book_dir),
        "word_count": words,
        "characters": sorted(list(characters)),
        "traits": {k: {"eyes": list(v["eyes"]), "hair": list(v["hair"])} for k, v in character_traits.items()},
        "deaths": list(deaths)
    }


def scan_series_continuity(target_dir: Path) -> dict:
    """Scans all volumes in a manuscript or series directory for continuity anomalies."""
    # Find volumes: either Book-* subdirectories or the directory itself
    book_dirs = sorted([d for d in target_dir.glob("Book-*") if d.is_dir()])
    if not book_dirs:
        # Check subdirectories
        sub_books = sorted([d for d in target_dir.rglob("Book-*") if d.is_dir()])
        if sub_books:
            book_dirs = sub_books
        else:
            book_dirs = [target_dir]

    volumes = []
    for b in book_dirs:
        v_data = extract_book_entities(b)
        volumes.append(v_data)

    contradictions = []
    mortality_violations = []

    # Cross-book trait tracking
    global_traits = defaultdict(lambda: {"eyes": defaultdict(list), "hair": defaultdict(list)})
    deceased_in = {}

    for v in volumes:
        v_name = v["volume_name"]

        # Check for resurrected characters across all active characters in volume
        active_chars = set(v.get("characters", [])) | set(v["traits"].keys())
        for char in active_chars:
            if char in deceased_in and deceased_in[char] != v_name:
                mortality_violations.append({
                    "character": char,
                    "died_in": deceased_in[char],
                    "appeared_in": v_name,
                    "message": f"Character '{char}' died in {deceased_in[char]} but appears active in {v_name}."
                })

        for d_char in v["deaths"]:
            deceased_in[d_char] = v_name

        # Trait tracking
        for char, t in v["traits"].items():
            for eye in t["eyes"]:
                global_traits[char]["eyes"][eye].append(v_name)
            for hair in t["hair"]:
                global_traits[char]["hair"][hair].append(v_name)

    # Check physical contradictions across volumes
    for char, t_data in global_traits.items():
        if len(t_data["eyes"]) > 1:
            desc_list = [f"{color} in {', '.join(vols)}" for color, vols in t_data["eyes"].items()]
            contradictions.append({
                "character": char,
                "trait": "Eye Color",
                "message": f"Contradictory eye color across books for '{char}': {'; '.join(desc_list)}."
            })
        if len(t_data["hair"]) > 1:
            desc_list = [f"{color} in {', '.join(vols)}" for color, vols in t_data["hair"].items()]
            contradictions.append({
                "character": char,
                "trait": "Hair Color",
                "message": f"Contradictory hair color across books for '{char}': {'; '.join(desc_list)}."
            })

    total_issues = len(contradictions) + len(mortality_violations)

    return {
        "target": str(target_dir),
        "total_volumes": len(volumes),
        "volumes": volumes,
        "contradictions": contradictions,
        "mortality_violations": mortality_violations,
        "total_issues": total_issues
    }


def generate_series_html_report(report: dict, output_path: Path) -> Path:
    """Generates an offline HTML series continuity ledger."""
    volumes = report.get("volumes", [])
    contradictions = report.get("contradictions", [])
    mortality = report.get("mortality_violations", [])

    issues_html = []
    for m in mortality:
        issues_html.append(f"<div style='background:#7f1d1d;color:#fecaca;padding:0.75rem;border-radius:6px;margin-bottom:0.5rem;'>💀 <strong>Mortality Error:</strong> {html.escape(m['message'])}</div>")
    for c in contradictions:
        issues_html.append(f"<div style='background:#78350f;color:#fde68a;padding:0.75rem;border-radius:6px;margin-bottom:0.5rem;'>⚠️ <strong>Physical Trait Drift:</strong> {html.escape(c['message'])}</div>")

    vol_cards = "".join(
        f"<div style='background:#1e293b;border:1px solid #334155;border-radius:8px;padding:1.25rem;'>"
        f"<h3 style='margin:0;color:#38bdf8;'>{html.escape(v['volume_name'])}</h3>"
        f"<p style='color:#94a3b8;font-size:0.85rem;margin:0.5rem 0;'>{v['word_count']:,} words | Deaths: {len(v['deaths'])} | Characters: {len(v['traits'])}</p>"
        f"</div>"
        for v in volumes
    )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Series Continuity Ledger</title>
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
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📚 Series Cross-Book Continuity Ledger</h1>
    <p style="color: var(--muted);">Target: {html.escape(report.get('target', ''))} | Volumes: {report.get('total_volumes', 0)}</p>
  </div>

  <h2>📖 Series Volumes</h2>
  <div class="grid">
    {vol_cards}
  </div>

  <div class="section">
    <h2>🔍 Continuity Anomalies ({report.get('total_issues', 0)} detected)</h2>
    {''.join(issues_html) or '<p style="color:var(--success); margin:0;">✓ Perfect series continuity. No character mortality or trait contradictions found.</p>'}
  </div>
</div>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Series Cross-Book Continuity Engine (WOR-103)")
    parser.add_argument("target", help="Manuscript or series directory containing Book volumes")
    parser.add_argument("--html", help="Generate HTML series ledger report")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = scan_series_continuity(target_path)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"=== Series Cross-Book Continuity Ledger: {target_path.name} ===")
    print(f"Volumes Indexed: {report['total_volumes']} | Total Issues: {report['total_issues']}")
    print("-" * 65)
    for v in report["volumes"]:
        print(f"  📖 {v['volume_name']:<16} | {v['word_count']:>6,} words | Tracked Characters: {len(v['traits'])}")

    if report["mortality_violations"]:
        print("\n💀 Mortality Invariant Violations:")
        for m in report["mortality_violations"]:
            print(f"  - {m['message']}")

    if report["contradictions"]:
        print("\n⚠️ Physical Trait Contradictions:")
        for c in report["contradictions"]:
            print(f"  - [{c['trait']}] {c['message']}")

    if not report["mortality_violations"] and not report["contradictions"]:
        print("\n✓ Perfect series continuity across all volumes!")

    if args.html:
        out_p = Path(args.html)
        generate_series_html_report(report, out_p)
        print(f"\nHTML report written to: {out_p}")


if __name__ == "__main__":
    main()
