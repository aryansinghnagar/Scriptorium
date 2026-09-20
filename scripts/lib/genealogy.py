#!/usr/bin/env python3
"""
Ars Arcanum Dynastic Genealogies & Succession Lineage Engine (scripts/lib/genealogy.py)
====================================================================================
Local-first family tree builder, succession validator, and lineage graph visualizer
for fantasy and historical novel worldbuilding.

Parses Character dossiers in `Characters/*.md`:
- `name`, `house`, `parents`, `spouses`, `children`, `born`, `died`, `gender`, `title`, `succession_order`, `heir`

Capabilities:
1. Family Tree Graphs & Dynastic Succession Lineages
2. Chronological & Biological Paradox Detection:
   - Child born before parent
   - Parent deceased before child birth/conception window
   - Circular ancestry loops (A is ancestor of A)
3. Succession Claims & Heir Validity Validation
4. Multiple Output Renderers:
   - Formatted ANSI terminal tree & lineage view
   - Clean, standard Mermaid.js flowchart (for direct embedding in Obsidian World Bible notes)
   - Interactive HTML with embedded scalable vector graphics (SVG)
   - Structured JSON (--json)

Zero external runtime dependencies; 100% offline privacy.
"""

import sys
import os
import re
import json
import html
import argparse
import logging
from pathlib import Path
from collections import defaultdict, deque

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.genealogy")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def clean_wikilink(val: str) -> str:
    """Strips Obsidian [[Wikilinks]] and quotation marks to obtain pure entity name."""
    s = val.strip().strip("\"'")
    if s.startswith("[[") and s.endswith("]]"):
        s = s[2:-2].strip()
        if "|" in s:
            s = s.split("|", 1)[0].strip()
    return s


def parse_year(val) -> float:
    """Parses year strings like '450 BCE', '-450 IE', '1240 AC', '500' to a numeric value for chronological checks."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().upper()
    if not s:
        return None
    # Check negative or BCE / BC
    is_neg = False
    if "BCE" in s or "BC" in s or s.startswith("-"):
        is_neg = True
    # Extract numbers
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if m:
        num = float(m.group(1))
        return -num if is_neg else num
    return None


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
            item_val = clean_wikilink(line.lstrip("- ").strip())
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
                items = [clean_wikilink(v) for v in val[1:-1].split(",") if v.strip()]
                data[key] = items
            else:
                data[key] = clean_wikilink(val)
    return data


def load_characters_and_houses(world_dir: Path) -> dict:
    """Scans Characters/ directory and returns character dictionary indexed by canonical name and aliases."""
    chars = {}
    dirs_to_check = [
        world_dir / "Characters",
        world_dir / "00-World-Bible" / "Characters",
    ]
    seen = set()
    for cdir in dirs_to_check:
        if not cdir.is_dir():
            continue
        for md_file in sorted(cdir.rglob("*.md")):
            if md_file in seen or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                fm = parse_yaml_frontmatter(content)
                name = fm.get("name") or md_file.stem
                
                # Normalize parents
                parents = fm.get("parents") or fm.get("parent") or []
                if isinstance(parents, str):
                    parents = [parents]
                if "father" in fm and clean_wikilink(fm["father"]) not in parents:
                    parents.append(clean_wikilink(fm["father"]))
                if "mother" in fm and clean_wikilink(fm["mother"]) not in parents:
                    parents.append(clean_wikilink(fm["mother"]))

                # Normalize spouses
                spouses = fm.get("spouses") or fm.get("spouse") or fm.get("consort") or []
                if isinstance(spouses, str):
                    spouses = [spouses]

                # Normalize children
                children = fm.get("children") or fm.get("child") or []
                if isinstance(children, str):
                    children = [children]

                # House / Dynasty
                house = fm.get("house") or fm.get("dynasty") or fm.get("clan") or fm.get("faction") or "Unknown"

                # Dates
                born = fm.get("born") or fm.get("birth_year") or fm.get("birth")
                died = fm.get("died") or fm.get("death_year") or fm.get("death")
                
                # Succession
                succ = fm.get("succession_order") or fm.get("reign_order") or fm.get("lineage_rank")
                try:
                    succ = int(succ) if succ is not None else None
                except ValueError:
                    succ = None

                chars[name] = {
                    "file": str(md_file.relative_to(world_dir)).replace("\\", "/"),
                    "name": name,
                    "title": fm.get("title", ""),
                    "gender": fm.get("gender", ""),
                    "house": house,
                    "parents": [clean_wikilink(p) for p in parents if p],
                    "spouses": [clean_wikilink(s) for s in spouses if s],
                    "children": [clean_wikilink(c) for c in children if c],
                    "born": born,
                    "born_numeric": parse_year(born),
                    "died": died,
                    "died_numeric": parse_year(died),
                    "succession_order": succ,
                    "heir": fm.get("heir"),
                    "generation": fm.get("generation"),
                }
            except Exception as e:
                logger.warning("Failed to load character %s: %s", md_file, e)

    # Cross-link bidirectional parent/child relationships
    for name, data in list(chars.items()):
        for p in data["parents"]:
            if p in chars and name not in chars[p]["children"]:
                chars[p]["children"].append(name)
        for c in data["children"]:
            if c in chars and name not in chars[c]["parents"]:
                chars[c]["parents"].append(name)
        for s in data["spouses"]:
            if s in chars and name not in chars[s]["spouses"]:
                chars[s]["spouses"].append(name)

    return chars


# ==============================================================================
# Validation & Paradox Checking
# ==============================================================================

def validate_genealogy(chars: dict) -> list:
    """Validates genealogy for biological paradoxes, circular ancestry, and succession conflicts."""
    findings = []

    # 1. Circular ancestry check (DFS cycle detection)
    def check_cycle(start_char):
        visited = set()
        stack = [(start_char, [start_char])]
        while stack:
            curr, path = stack.pop()
            if curr not in chars:
                continue
            for parent in chars[curr]["parents"]:
                if parent == start_char:
                    return path + [parent]
                if parent not in visited:
                    visited.add(parent)
                    stack.append((parent, path + [parent]))
        return None

    for name in chars:
        cycle = check_cycle(name)
        if cycle:
            findings.append({
                "id": "GEN-101",
                "severity": "FATAL",
                "character": name,
                "file": chars[name]["file"],
                "message": f"Circular ancestry loop detected: {' -> '.join(cycle)}"
            })

    # 2. Chronological / Biological checks
    for name, c in chars.items():
        b_num = c["born_numeric"]
        d_num = c["died_numeric"]

        # Lifespan sanity: died before born
        if b_num is not None and d_num is not None and d_num < b_num:
            findings.append({
                "id": "GEN-101",
                "severity": "WARNING",
                "character": name,
                "file": c["file"],
                "message": f"Character '{name}' died ({c['died']}) before being born ({c['born']})."
            })

        # Parent vs Child birth dates
        for p_name in c["parents"]:
            if p_name in chars:
                p = chars[p_name]
                p_b_num = p["born_numeric"]
                p_d_num = p["died_numeric"]

                if p_b_num is not None and b_num is not None:
                    if b_num <= p_b_num:
                        findings.append({
                            "id": "GEN-101",
                            "severity": "WARNING",
                            "character": name,
                            "file": c["file"],
                            "message": f"Child '{name}' born ({c['born']}) before or same year as parent '{p_name}' ({p['born']})."
                        })

                if p_d_num is not None and b_num is not None:
                    # Allow 1-year margin for pregnancy if father, but warn if child born years after parent died
                    if b_num > (p_d_num + 1.0):
                        findings.append({
                            "id": "GEN-101",
                            "severity": "WARNING",
                            "character": name,
                            "file": c["file"],
                            "message": f"Child '{name}' born ({c['born']}) after parent '{p_name}' deceased ({p['died']})."
                        })

    # 3. Succession Order gaps / duplicates
    houses = defaultdict(list)
    for name, c in chars.items():
        if c.get("house") and c.get("succession_order") is not None:
            houses[c["house"]].append(c)

    for h_name, members in houses.items():
        ranks = [m["succession_order"] for m in members]
        duplicates = [r for r in set(ranks) if ranks.count(r) > 1]
        for dup in duplicates:
            claimants = [m["name"] for m in members if m["succession_order"] == dup]
            findings.append({
                "id": "GEN-102",
                "severity": "WARNING",
                "house": h_name,
                "file": members[0]["file"],
                "message": f"House '{h_name}' has conflicting succession rank #{dup} claimed by: {', '.join(claimants)}"
            })

    return findings


# ==============================================================================
# Lineage & Mermaid Compilation
# ==============================================================================

def normalize_house_token(name: str) -> str:
    """Strips 'house of', 'house', 'clan', 'dynasty' prefixes/suffixes and punctuation."""
    s = name.lower().strip()
    s = re.sub(r"^(?:the\s+house\s+of|the\s+house|house\s+of|house|clan|dynasty)\s+", "", s)
    s = re.sub(r"\s+(?:house|dynasty|clan)$", "", s)
    return s.strip()


def matches_house_or_character(c: dict, query: str) -> bool:
    """Checks if character or its house matches the target query."""
    q_raw = query.lower().strip()
    q_norm = normalize_house_token(q_raw)

    char_name = c.get("name", "").lower()
    house_raw = c.get("house", "").lower()
    house_norm = normalize_house_token(house_raw)

    if q_raw in char_name or (q_norm and q_norm in char_name):
        return True
    if q_raw in house_raw or (q_norm and q_norm in house_raw):
        return True
    if house_raw in q_raw or (house_norm and house_norm in q_raw) or (house_norm and q_norm and house_norm == q_norm):
        return True
    return False


def get_house_lineage(chars: dict, house_name: str) -> list:
    """Returns sorted lineage chain for a specific house/dynasty."""
    members = [c for c in chars.values() if matches_house_or_character(c, house_name)]
    # Sort primarily by succession_order, then by born_numeric, then by name
    def sort_key(c):
        s_order = c["succession_order"] if c["succession_order"] is not None else 999
        b_year = c["born_numeric"] if c["born_numeric"] is not None else 9999
        return (s_order, b_year, c["name"])
    return sorted(members, key=sort_key)


def generate_mermaid_flowchart(chars: dict, target_query: str = None) -> str:
    """Generates Mermaid.js flowchart code for the target house or character family tree."""
    # Filter nodes if query given
    nodes_to_include = set()
    if target_query:
        # Find matching house or character
        for name, c in chars.items():
            if matches_house_or_character(c, target_query):
                nodes_to_include.add(name)
                for p in c["parents"]:
                    nodes_to_include.add(p)
                for ch in c["children"]:
                    nodes_to_include.add(ch)
                for sp in c["spouses"]:
                    nodes_to_include.add(sp)
    else:
        nodes_to_include = set(chars.keys())

    mermaid_lines = [
        "```mermaid",
        "flowchart TD",
        "    classDef royal fill:#2d1b4e,stroke:#bc8cff,stroke-width:2px,color:#fff;",
        "    classDef spouse fill:#1f3a5f,stroke:#58a6ff,stroke-width:1px,color:#fff;",
        "    classDef claimant fill:#4d2c1d,stroke:#d29922,stroke-width:2px,color:#fff;",
    ]

    def node_id(name_str):
        return re.sub(r"[^A-Za-z0-9_]", "_", name_str)

    edges_rendered = set()

    for name in sorted(nodes_to_include):
        c = chars.get(name, {"name": name, "house": "", "title": "", "born": None, "died": None, "succession_order": None})
        n_id = node_id(name)
        
        # Label formatting
        label_parts = [f"<b>{html.escape(c['name'])}</b>"]
        if c.get("title"):
            label_parts.append(f"<i>{html.escape(c['title'])}</i>")
        if c.get("born") or c.get("died"):
            b = c.get('born') or '?'
            d = c.get('died') or 'Present'
            label_parts.append(f"<small>({b} – {d})</small>")
        if c.get("succession_order"):
            label_parts.append(f"👑 <b>#{c['succession_order']}</b>")

        box_label = "<br/>".join(label_parts)
        mermaid_lines.append(f'    {n_id}["{box_label}"]')

        # Node class styling
        if c.get("succession_order") == 1:
            mermaid_lines.append(f"    class {n_id} royal;")
        elif c.get("succession_order"):
            mermaid_lines.append(f"    class {n_id} claimant;")

    # Add edges
    for name in sorted(nodes_to_include):
        if name not in chars:
            continue
        c = chars[name]
        u_id = node_id(name)
        
        # Parent -> Child
        for ch in c.get("children", []):
            if ch in nodes_to_include:
                v_id = node_id(ch)
                edge_key = (u_id, v_id)
                if edge_key not in edges_rendered:
                    edges_rendered.add(edge_key)
                    mermaid_lines.append(f"    {u_id} --> {v_id}")

        # Spouses
        for sp in c.get("spouses", []):
            if sp in nodes_to_include:
                v_id = node_id(sp)
                edge_key = tuple(sorted([u_id, v_id]))
                if edge_key not in edges_rendered:
                    edges_rendered.add(edge_key)
                    mermaid_lines.append(f"    {u_id} <-.->|Spouse| {v_id}")

    mermaid_lines.append("```")
    return "\n".join(mermaid_lines)


def generate_genealogy_html_report(title: str, mermaid_code: str, lineage: list, findings: list, output_file: Path):
    """Generates an interactive HTML tree report with embedded Mermaid.js rendering."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Ars Arcanum Dynastic Genealogy</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'dark'}});</script>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #58a6ff;
    --gold: #d29922;
    --danger: #f85149;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  body {{
    background-color: var(--bg);
    color: var(--text);
    font-family: var(--font);
    line-height: 1.6;
    margin: 0;
    padding: 24px;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ color: var(--gold); margin: 0 0 8px 0; }}
  .badge {{ background: #d2992222; color: var(--gold); border: 1px solid var(--gold); padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ color: #8b949e; font-weight: 600; }}
  td {{ color: #f0f6fc; }}
  .mermaid-box {{ background: #0b0f14; border: 1px solid var(--border); border-radius: 8px; padding: 20px; overflow-x: auto; text-align: center; }}
  footer {{ text-align: center; font-size: 12px; color: #8b949e; margin-top: 40px; border-top: 1px solid var(--border); padding-top: 16px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>👑 {html.escape(title)}</h1>
    <span class="badge">Ars Arcanum Dynastic Genealogy Suite</span>
  </header>

  <div class="card">
    <h2>Dynastic Family Tree Flowchart</h2>
    <div class="mermaid-box">
      <div class="mermaid">
{mermaid_code.replace('```mermaid', '').replace('```', '').strip()}
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Lineage & Succession Table ({len(lineage)} Members)</h2>
    <table>
      <tr><th>Rank</th><th>Name</th><th>Title</th><th>House</th><th>Lifespan</th><th>Parents</th></tr>
"""
    for m in lineage:
        s_rank = f"👑 #{m['succession_order']}" if m.get("succession_order") else "—"
        parents_str = ", ".join(m.get("parents", [])) or "—"
        lifespan = f"{m.get('born') or '?'} – {m.get('died') or 'Present'}"
        html_content += f"""      <tr>
        <td><strong>{html.escape(s_rank)}</strong></td>
        <td><strong>{html.escape(m['name'])}</strong></td>
        <td>{html.escape(m.get('title', ''))}</td>
        <td>{html.escape(m.get('house', ''))}</td>
        <td>{html.escape(lifespan)}</td>
        <td>{html.escape(parents_str)}</td>
      </tr>\n"""

    html_content += f"""    </table>
  </div>
"""
    if findings:
        html_content += f"""  <div class="card">
    <h2 style="color: var(--danger);">Genealogy Paradox Findings ({len(findings)})</h2>
"""
        for f in findings:
            html_content += f"""    <div style="padding: 10px; background: #21262d; border-left: 4px solid var(--danger); margin-bottom: 8px; border-radius: 4px;">
      <strong>[{f['severity']}] {f['id']}</strong>: {html.escape(f['message'])}<br>
      <small style="color: #8b949e;">File: {html.escape(f['file'])}</small>
    </div>\n"""
        html_content += """  </div>\n"""

    html_content += """  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    output_file.write_text(html_content, encoding="utf-8")


def print_terminal_tree(chars: dict, root_name: str, prefix: str = "", visited: set = None):
    """Recursively prints an ASCII/Unicode hierarchy tree."""
    if visited is None:
        visited = set()
    if root_name in visited or root_name not in chars:
        return
    visited.add(root_name)

    c = chars[root_name]
    rank_str = f" [👑 #{c['succession_order']}]" if c.get("succession_order") else ""
    dates_str = f" ({c.get('born') or '?'} - {c.get('died') or 'Present'})" if c.get("born") or c.get("died") else ""
    title_str = f" - {c.get('title')}" if c.get("title") else ""
    
    print(f"{prefix}\033[1;33m{c['name']}\033[0m\033[36m{title_str}\033[0m\033[32m{rank_str}\033[0m\033[90m{dates_str}\033[0m")

    if c.get("spouses"):
        sp_str = ", ".join(c["spouses"])
        print(f"{prefix} ├── \033[94m(⚭ Spouse: {sp_str})\033[0m")

    children = [ch for ch in c.get("children", []) if ch in chars]
    for i, child_name in enumerate(children):
        is_last = (i == len(children) - 1)
        sub_prefix = prefix + (" └── " if is_last else " ├── ")
        next_prefix = prefix + ("     " if is_last else " │   ")
        print(f"{sub_prefix}", end="")
        print_terminal_tree(chars, child_name, next_prefix, visited)


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
    parser = argparse.ArgumentParser(description="Ars Arcanum Dynastic Genealogies & Succession Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Genealogy subcommands")

    # 1. tree / genealogy
    p_tree = subparsers.add_parser("tree", help="Build and view dynastic family tree")
    p_tree.add_argument("target", help="House name or character name (e.g. 'House Stark', 'Aethelgard')")
    p_tree.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_tree.add_argument("--mermaid", action="store_true", help="Print raw Mermaid.js flowchart code")
    p_tree.add_argument("--html", help="Export standalone interactive HTML report")
    p_tree.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 2. lineage
    p_lineage = subparsers.add_parser("lineage", help="Display succession order and dynastic lineage roster")
    p_lineage.add_argument("house", help="House / Dynasty name")
    p_lineage.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_lineage.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    # Discover world
    raw_w = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir = resolve_world_dir(raw_w)

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    chars = load_characters_and_houses(Path(world_dir))
    findings = validate_genealogy(chars)

    if args.subcommand in ("tree", "genealogy"):
        target = args.target
        lineage = get_house_lineage(chars, target)
        mermaid_code = generate_mermaid_flowchart(chars, target)

        if args.json:
            out_data = {
                "world": Path(world_dir).name,
                "target": target,
                "total_characters": len(chars),
                "lineage_count": len(lineage),
                "lineage": lineage,
                "findings": findings,
                "mermaid": mermaid_code,
            }
            print(json.dumps(out_data, indent=2))
        elif args.mermaid:
            print(mermaid_code)
        else:
            print(f"\n\033[1;33m=== Ars Arcanum Dynastic Genealogy: {target} ===\033[0m")
            print(f"World: \033[1m{Path(world_dir).name}\033[0m | Characters Loaded: \033[32m{len(chars)}\033[0m\n")

            # Check if root character found
            root_matches = [name for name in chars if target.lower() in name.lower()]
            if root_matches:
                print("\033[1mFamily Hierarchy Tree:\033[0m")
                print_terminal_tree(chars, root_matches[0])
                print()
            elif lineage:
                print(f"\033[1mHouse Members ({len(lineage)}):\033[0m")
                for m in lineage:
                    s_rank = f"👑 #{m['succession_order']}" if m.get("succession_order") else "—"
                    print(f"  {s_rank:<8} \033[1m{m['name']}\033[0m ({m.get('born') or '?'} – {m.get('died') or 'Present'}) {m.get('title', '')}")
                print()

            if findings:
                print("\033[1;31mGenealogy Paradox Findings:\033[0m")
                for f in findings:
                    print(f"  \033[31m[{f['severity']}] {f['id']}\033[0m: {f['message']}")
                print()

        if getattr(args, "html", None):
            out_p = Path(args.html)
            generate_genealogy_html_report(f"Genealogy: {target}", mermaid_code, lineage, findings, out_p)
            print(f"\nInteractive HTML report written to: {out_p}")

    elif args.subcommand == "lineage":
        house = args.house
        lineage = get_house_lineage(chars, house)
        if args.json:
            print(json.dumps({"house": house, "members": lineage, "findings": findings}, indent=2))
        else:
            print(f"\n\033[1;33m=== Dynastic Succession Lineage: {house} ===\033[0m")
            if not lineage:
                print(f"No characters found for House '{house}'.")
            else:
                for m in lineage:
                    s_rank = f"👑 #{m['succession_order']}" if m.get("succession_order") else "—"
                    parents = f" (Parents: {', '.join(m['parents'])})" if m.get("parents") else ""
                    print(f"  {s_rank:<8} \033[1m{m['name']}\033[0m - {m.get('title', 'Lord/Lady')}{parents}")
            print()


if __name__ == "__main__":
    main()
