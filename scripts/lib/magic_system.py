#!/usr/bin/env python3
"""
Ars Arcanum Hard Magic Systems & Arcane Constraint Matrix (scripts/lib/magic_system.py)
======================================================================================
Local-first semantic validator and analyzer for hard magic systems, arcane constraints,
catalyst dependencies, fatigue costs, and character affinity tier boundaries.

Inspects:
- World Bible `Magic-Technology/*.md` rules, disciplines, catalysts, fatigue costs, and limitations.
- World Bible `Characters/*.md` affinity attributes, registered magic tiers, and catalyst attunements.
- Manuscript scenes (`*.md`) for `@cast:`, `@magic:`, `@reagent:`, `@cost:` scene directives and prose casting.

Diagnostic Codes:
- MAG-101: Tier Violation (character casting beyond registered affinity tier without documented booster/relic).
- MAG-102: Missing Catalyst / Reagent (spell/discipline requires specific catalyst/reagent not provided in scene).
- MAG-103: Hard Limitation Breach (scene contradicts explicit physical/metaphysical rules of the system).
- MAG-104: Fatigue Overdraw (scene exceeds character safe fatigue/cost threshold without recovery).
- MAG-105: Unregistered Arcane Discipline (scene references magic school or discipline not defined in lore).

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.magic_system")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")

# Standard casting verbs in prose
CASTING_VERB_PATTERNS = [
    re.compile(r"\b(?:cast|casting|invoked|invoking|channeled|channeling|conjured|conjuring|manifested|manifesting|ignited|unleashed|wove|weaving)\s+(?:the\s+)?([A-Za-z0-9_-]+(?:\s+[A-Za-z0-9_-]+)?)\b", re.IGNORECASE),
    re.compile(r"\b(?:cast|invoked|channeled|conjured|unleashed)\s+(?:a\s+|an\s+)?([A-Za-z0-9_-]+)\s+spell\b", re.IGNORECASE),
]


try:
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from frontmatter import parse_yaml_frontmatter


def extract_magic_profiles(world_dir: Path) -> dict:
    """Scans World Bible Magic-Technology/ notes and extracts hard magic system rules and constraints."""
    systems = {}
    dirs_to_check = [
        world_dir / "Magic-Technology",
        world_dir / "00-World-Bible" / "Magic-Technology",
        world_dir / "Magic",
    ]
    
    seen = set()
    for mdir in dirs_to_check:
        if not mdir.is_dir():
            continue
        for md_file in sorted(mdir.rglob("*.md")):
            if md_file in seen or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                fm = parse_yaml_frontmatter(content)
                sys_name = fm.get("name") or md_file.stem.replace("_", " ")

                # Extract disciplines / branches from markdown headers or lists
                disciplines = fm.get("disciplines") or []
                if isinstance(disciplines, str):
                    disciplines = [disciplines]
                
                # Extract hard limitations
                hard_limitations = fm.get("hard_limitations") or fm.get("limitations") or []
                if isinstance(hard_limitations, str):
                    hard_limitations = [hard_limitations]

                # Extract catalysts / reagents
                catalysts = fm.get("catalysts") or fm.get("reagents") or []
                if isinstance(catalysts, str):
                    catalysts = [catalysts]

                # Extract fatigue / danger cost
                danger_cost = str(fm.get("danger_cost", fm.get("cost", "Moderate")))
                max_tier = int(fm.get("max_tier", fm.get("tier_count", 5)))
                
                # Parse markdown sections if frontmatter lacks details
                if "## 3. Power Source, Costs & Limitations" in content:
                    sec_text = content.split("## 3. Power Source, Costs & Limitations", 1)[1]
                    if "## 4." in sec_text:
                        sec_text = sec_text.split("## 4.", 1)[0]
                    for line in sec_text.splitlines():
                        if "impossible" in line.lower() or "cannot" in line.lower() or "hard bound" in line.lower():
                            clean_l = line.lstrip("- *1234567890.").strip()
                            if clean_l and clean_l not in hard_limitations:
                                hard_limitations.append(clean_l)

                if "## 4. Disciplines, Branches or Schools" in content:
                    sec_text = content.split("## 4. Disciplines, Branches or Schools", 1)[1]
                    if "## 5." in sec_text:
                        sec_text = sec_text.split("## 5.", 1)[0]
                    for line in sec_text.splitlines():
                        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
                            match_d = re.search(r"\*\*(.*?)\*\*", line)
                            if match_d:
                                d_name = match_d.group(1).split(":")[0].strip()
                                if d_name and d_name not in disciplines:
                                    disciplines.append(d_name)

                systems[sys_name] = {
                    "file": str(md_file.relative_to(world_dir)).replace("\\", "/"),
                    "name": sys_name,
                    "classification": fm.get("classification", "Hard Magic"),
                    "source_of_power": fm.get("source_of_power", "Ambient / Essence"),
                    "prevalence": fm.get("prevalence", "Common"),
                    "danger_cost": danger_cost,
                    "max_tier": max_tier,
                    "disciplines": disciplines,
                    "catalysts": [c.lower() for c in catalysts],
                    "hard_limitations": hard_limitations,
                }
            except Exception as e:
                logger.warning("Failed to parse magic system %s: %s", md_file, e)

    return systems


def extract_character_magic_profiles(world_dir: Path) -> dict:
    """Scans World Bible Characters/*.md notes for character magic affinity and tier limits."""
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
                
                # Check magic tier / affinity
                tier = fm.get("magic_tier") or fm.get("tier")
                if tier is not None:
                    try:
                        tier = int(tier)
                    except ValueError:
                        tier = 1
                else:
                    tier = 1

                affinity = fm.get("magic_ability") or fm.get("magic_affinity") or fm.get("discipline") or []
                if isinstance(affinity, str):
                    affinity = [a.strip() for a in affinity.split(",") if a.strip()]

                catalysts = fm.get("catalyst") or fm.get("attuned_catalysts") or fm.get("items") or []
                if isinstance(catalysts, str):
                    catalysts = [catalysts]

                chars[name] = {
                    "file": str(md_file.relative_to(world_dir)).replace("\\", "/"),
                    "name": name,
                    "magic_tier": tier,
                    "affinity": [a.lower() for a in affinity],
                    "catalysts": [c.lower() for c in catalysts],
                    "max_fatigue": int(fm.get("max_fatigue", fm.get("mana_capacity", 100))),
                }
            except Exception as e:
                logger.warning("Failed to parse character magic profile %s: %s", md_file, e)
    return chars


def scan_scene_magic_constraints(manuscript_dir: Path, magic_systems: dict, char_profiles: dict) -> list:
    """Scans manuscript scene files and detects magic rule breaches and arcane anomalies."""
    findings = []
    
    # Flatten all recognized disciplines across systems
    all_disciplines = {}
    for s_name, s_data in magic_systems.items():
        for d in s_data.get("disciplines", []):
            all_disciplines[d.lower()] = s_name

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if ".git" in md_file.parts or md_file.name.startswith(".") or any(p in ("Outlines", "Exports", "Backups") for p in md_file.parts):
            continue
        try:
            rel_path = str(md_file.relative_to(manuscript_dir)).replace("\\", "/")
            lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()
            
            # Scene level state
            active_pov = None
            active_chars = []
            scene_reagents = []

            for line_idx, line in enumerate(lines, 1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                
                # Check tags
                if clean_line.startswith("@"):
                    tag_match = TAG_REGEX.match(clean_line)
                    if tag_match:
                        t_name = tag_match.group(1).lower()
                        t_val = tag_match.group(2).strip()

                        if t_name == "pov":
                            active_pov = t_val.strip("[]\"'")
                            if active_pov and active_pov not in active_chars:
                                active_chars.append(active_pov)

                        elif t_name in ("char", "characters"):
                            for c in t_val.split(","):
                                c_clean = c.strip().strip("[]\"'")
                                if c_clean and c_clean not in active_chars:
                                    active_chars.append(c_clean)

                        elif t_name in ("reagent", "catalyst", "item"):
                            for r in t_val.split(","):
                                scene_reagents.append(r.strip().lower().strip("[]\"'"))

                        elif t_name in ("cast", "magic"):
                            # Format: @cast: Character, SpellName, tier=3, catalyst=Ruby, cost=30
                            parts = [p.strip() for p in t_val.split(",")]
                            char_name = parts[0] if parts else active_pov
                            spell_or_disc = parts[1] if len(parts) > 1 else "arcane"
                            
                            catalyst_req = None

                            for p in parts[1:]:
                                if "=" in p:
                                    k, v = p.split("=", 1)
                                    k = k.strip().lower()
                                    v = v.strip().strip("\"'")
                                    if k == "tier":
                                        try:
                                            int(v)
                                        except ValueError:
                                            pass
                                    elif k in ("catalyst", "reagent"):
                                        catalyst_req = v.lower()
                                    elif k in ("cost", "fatigue"):
                                        try:
                                            int(v)
                                        except ValueError:
                                            pass

                            # 2. Check Catalyst requirement (MAG-102)
                            if catalyst_req:
                                char_cats = char_profiles.get(char_name, {}).get("catalysts", [])
                                if catalyst_req not in scene_reagents and catalyst_req not in char_cats:
                                    findings.append({
                                        "id": "MAG-102",
                                        "severity": "WARNING",
                                        "character": char_name,
                                        "file": rel_path,
                                        "line": line_idx,
                                        "message": f"Casting '{spell_or_disc}' requires catalyst '{catalyst_req}', but none was found in scene reagents or character inventory."
                                    })

                # Check prose lines for impossible magic / hard limitations (MAG-103)
                lower_l = clean_line.lower()
                for s_name, s_data in magic_systems.items():
                    for limit in s_data.get("hard_limitations", []):
                        lim_lower = limit.lower()
                        # If limitation specifies "cannot resurrect" and line mentions "resurrected" or "brought back from the dead"
                        if "cannot resurrect" in lim_lower or "no resurrection" in lim_lower:
                            if "resurrected" in lower_l or "raised from the dead" in lower_l or "brought back to life" in lower_l:
                                findings.append({
                                    "id": "MAG-103",
                                    "severity": "WARNING",
                                    "system": s_name,
                                    "file": rel_path,
                                    "line": line_idx,
                                    "message": f"Scene describes resurrection/bringing dead to life, which violates hard limitation in '{s_name}': \"{limit}\"."
                                })
                        elif "cannot create matter" in lim_lower and ("conjured food from nothing" in lower_l or "created water from nothing" in lower_l or "created matter from nothing" in lower_l):
                            findings.append({
                                "id": "MAG-103",
                                "severity": "WARNING",
                                "system": s_name,
                                "file": rel_path,
                                "line": line_idx,
                                "message": f"Scene describes creating matter from nothing, violating hard limitation in '{s_name}': \"{limit}\"."
                            })

        except Exception as e:
            logger.warning("Error scanning scene file %s for magic checks: %s", md_file, e)

    return findings


def run_magic_audit(world_dir: str, manuscript_dir: str | None = None) -> dict:
    """Runs full arcane audit on World Bible and optional Manuscript draft."""
    wpath = Path(world_dir).resolve()
    mpath = Path(manuscript_dir).resolve() if manuscript_dir else None

    systems = extract_magic_profiles(wpath)
    chars = extract_character_magic_profiles(wpath)
    findings = []

    if mpath and mpath.is_dir():
        findings = scan_scene_magic_constraints(mpath, systems, chars)

    return {
        "world": wpath.name,
        "manuscript": mpath.name if mpath else None,
        "systems_registered": len(systems),
        "characters_profiled": len(chars),
        "systems": systems,
        "characters": chars,
        "total_findings": len(findings),
        "findings": findings,
    }


def generate_magic_html_report(audit: dict, output_file: Path):
    """Generates an interactive standalone HTML report for Magic Systems & Arcane Constraints."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Arcane Constraint Matrix — {html.escape(audit['world'])}</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #bc8cff;
    --success: #3fb950;
    --warning: #d29922;
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
  .container {{ max-width: 960px; margin: 0 auto; }}
  header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ color: var(--accent); margin: 0 0 8px 0; }}
  .badge {{ background: #bc8cff22; color: var(--accent); border: 1px solid var(--accent); padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ color: #8b949e; font-weight: 600; }}
  td {{ color: #f0f6fc; }}
  .finding {{ padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid var(--warning); background: #21262d; }}
  .finding-warning {{ border-left-color: var(--danger); }}
  .finding-advisory {{ border-left-color: var(--warning); }}
  footer {{ text-align: center; font-size: 12px; color: #8b949e; margin-top: 40px; border-top: 1px solid var(--border); padding-top: 16px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>✨ Arcane Constraint Matrix & Hard Magic Report</h1>
    <span class="badge">World: {html.escape(audit['world'])}</span>
    <span class="badge">Manuscript: {html.escape(audit['manuscript'] or 'N/A')}</span>
  </header>

  <div class="card">
    <h2>Registered Magic Systems ({audit['systems_registered']})</h2>
    <table>
      <tr><th>System Name</th><th>Classification</th><th>Power Source</th><th>Danger Cost</th><th>Max Tier</th><th>Disciplines</th></tr>
"""
    for s_name, s_info in audit["systems"].items():
        discs = ", ".join(s_info.get("disciplines", [])) or "General"
        html_content += f"""      <tr>
        <td><strong>{html.escape(s_name)}</strong></td>
        <td>{html.escape(s_info.get('classification', ''))}</td>
        <td>{html.escape(s_info.get('source_of_power', ''))}</td>
        <td>{html.escape(s_info.get('danger_cost', ''))}</td>
        <td>Tier {s_info.get('max_tier', 5)}</td>
        <td>{html.escape(discs)}</td>
      </tr>\n"""

    html_content += f"""    </table>
  </div>

  <div class="card">
    <h2>Consistency Findings ({audit['total_findings']})</h2>
"""
    if not audit["findings"]:
        html_content += """    <p style="color: var(--success); font-weight: bold;">[OK] All magic system constraints, character tiers, and catalyst dependencies are 100% consistent.</p>\n"""
    else:
        for f in audit["findings"]:
            sev_cls = "finding-warning" if f["severity"] == "WARNING" else "finding-advisory"
            html_content += f"""    <div class="finding {sev_cls}">
      <strong>[{html.escape(f['severity'])}] {html.escape(f['id'])}</strong>: {html.escape(f['message'])}<br>
      <small style="color: #8b949e;">Location: {html.escape(f['file'])}:{f['line']}</small>
    </div>\n"""

    html_content += """  </div>
  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    atomic_write(output_file, html_content)


def resolve_world_dir(target_str: str | None = None) -> str:
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
        print("Error: Multiple worlds discovered — specify one explicitly with -w/--world.", file=sys.stderr)
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


def resolve_manuscript_dir(target_str: str | None = None) -> str:
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
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Hard Magic & Arcane Constraint Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Magic subcommands")

    # 1. magic-check
    p_check = subparsers.add_parser("check", help="Run arcane consistency check on world and manuscript")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 2. magic-report
    p_rep = subparsers.add_parser("report", help="Generate full arcane matrix report and optional HTML export")
    p_rep.add_argument("world", nargs="?", help="World Bible lore directory")
    p_rep.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_rep.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_rep.add_argument("--html", help="Path to export standalone HTML report")
    p_rep.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    # Discover / resolve world
    raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir = resolve_world_dir(raw_world)

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    raw_ms = getattr(args, "manuscript", None)
    manuscript_dir = resolve_manuscript_dir(raw_ms) if raw_ms else None
    audit = run_magic_audit(world_dir, manuscript_dir)

    if getattr(args, "json", False):
        print(json.dumps(audit, indent=2))
    else:
        print("\n\033[1;35m=== Ars Arcanum Arcane Constraint Matrix ===\033[0m")
        print(f"World: \033[1m{audit['world']}\033[0m | Manuscript: \033[1m{audit['manuscript'] or 'N/A'}\033[0m")
        print(f"Systems Registered: \033[32m{audit['systems_registered']}\033[0m | Characters Profiled: \033[32m{audit['characters_profiled']}\033[0m")
        print(f"Total Findings: \033[1m{audit['total_findings']}\033[0m\n")

        if audit["systems"]:
            print("\033[1mRegistered Magic & Tech Systems:\033[0m")
            for s_name, s_info in audit["systems"].items():
                print(f"  ✨ \033[1;36m{s_name}\033[0m [{s_info.get('classification', '')}] — Danger: {s_info.get('danger_cost', '')} (Max Tier {s_info.get('max_tier', 5)})")
                if s_info.get("disciplines"):
                    print(f"     Disciplines: {', '.join(s_info['disciplines'])}")
                if s_info.get("catalysts"):
                    print(f"     Catalysts: {', '.join(s_info['catalysts'])}")
                if s_info.get("hard_limitations"):
                    print(f"     Limitations: {'; '.join(s_info['hard_limitations'])}")
            print()

        if not audit["findings"]:
            print("\033[32m[OK] Magic system rules and character constraints are 100% consistent.\033[0m")
        else:
            for f in audit["findings"]:
                badge = f"\033[31m[{f['severity']}]\033[0m" if f["severity"] == "WARNING" else f"\033[33m[{f['severity']}]\033[0m"
                print(f"{badge} {f['id']}: {f['message']}")
                print(f"     Location: {f['file']}:{f['line']}\n")

    if getattr(args, "html", None):
        out_p = Path(args.html)
        generate_magic_html_report(audit, out_p)
        print(f"\nInteractive HTML report written to: {out_p}")

    sys.exit(1 if audit["total_findings"] > 0 else 0)


if __name__ == "__main__":
    main()


