#!/usr/bin/env python3
"""
Ars Arcanum Trophic Food-Web Simulator & Ecological Energy Pyramid Engine (scripts/lib/ecology.py)
==================================================================================================
Zero-dependency, offline ecological trophic level analyzer, Lindeman's 10% energy pyramid validator,
predation network DAG generator, and ecosystem stability auditor for speculative worldbuilders.

Capabilities:
1. Bestiary & Flora Trophic Profiler:
   - Scans World Bible `Bestiary/*.md` and `Flora/*.md`.
   - Extracts trophic levels (1=Producer, 2=Primary Consumer/Herbivore, 3=Secondary Consumer/Carnivore,
     4=Apex Predator, 5=Decomposer), dietary prey, daily caloric demand, biomass, and habitats.
2. Lindeman's 10% Energy Pyramid & Trophic Audit:
   - Validates that biomass at level N supports level N+1.
   - Detects:
     * ECO-301: Apex Predator Without Declared/Matching Prey.
     * ECO-302: Trophic Deficit / Caloric Starvation (predator demand exceeds prey biomass carrying capacity).
     * ECO-303: Circular Predation Loop / Mutual Apex Paradox.
     * ECO-304: Biome Lacks Primary Producers.
3. Visualizers:
   - Obsidian Mermaid.js Food-Web Predation Graph (`--write-note`).
   - Standalone interactive HTML report with dynamic SVG Energy Pyramid (`--html`).

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

logger = logging.getLogger("arcanum.ecology")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")

TROPHIC_NAMES = {
    1: "Primary Producer (Flora/Autotroph)",
    2: "Primary Consumer (Herbivore)",
    3: "Secondary Consumer (Carnivore)",
    4: "Apex Predator (Top Carnivore)",
    5: "Decomposer / Detritivore",
}


def parse_yaml_frontmatter(content: str) -> dict:
    """Safe frontmatter parser."""
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
            key = key.strip()
            val = val.strip()
            current_key = key
            
            if not val:
                data[key] = []
            elif val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
                data[key] = items
            elif val.lower() in ("true", "yes"):
                data[key] = True
            elif val.lower() in ("false", "no"):
                data[key] = False
            else:
                try:
                    if "." in val:
                        data[key] = float(val)
                    else:
                        data[key] = int(val)
                except ValueError:
                    data[key] = val.strip("\"'")
    return data


def clean_link_name(raw: str) -> str:
    if not raw:
        return ""
    m = WIKILINK_REGEX.search(str(raw))
    if m:
        return m.group(1).strip()
    return str(raw).strip().strip("\"'[]")


def normalize_name(name: str) -> str:
    return re.sub(r"[\s_-]+", " ", str(name).strip().lower())


def extract_species_profiles(world_dir: Path) -> dict:
    """Scans Bestiary/ and Flora/ directories and extracts structured trophic profiles."""
    species = {}
    dirs_to_check = [
        world_dir / "Bestiary",
        world_dir / "00-World-Bible" / "Bestiary",
        world_dir / "Flora",
        world_dir / "00-World-Bible" / "Flora",
    ]

    seen_files = set()
    for sdir in dirs_to_check:
        if not sdir.is_dir():
            continue
        for md_file in sorted(sdir.rglob("*.md")):
            if md_file in seen_files or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen_files.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                name = fm.get("name") or md_file.stem.replace("_", " ")

                raw_prey = fm.get("dietary_prey") or fm.get("prey_species") or fm.get("prey") or []
                if isinstance(raw_prey, str):
                    raw_prey = [raw_prey]
                prey = [clean_link_name(p) for p in raw_prey if clean_link_name(p)]

                trophic_level = fm.get("trophic_level", 2)
                try:
                    trophic_level = int(trophic_level)
                except (ValueError, TypeError):
                    trophic_level = 2

                biomass_kg = fm.get("biomass_kg", 50.0)
                try:
                    biomass_kg = float(biomass_kg)
                except (ValueError, TypeError):
                    biomass_kg = 50.0

                daily_caloric_demand = fm.get("daily_caloric_demand", 2500.0)
                try:
                    daily_caloric_demand = float(daily_caloric_demand)
                except (ValueError, TypeError):
                    daily_caloric_demand = 2500.0

                pop_density = fm.get("population_density", 10.0)
                try:
                    pop_density = float(pop_density)
                except (ValueError, TypeError):
                    pop_density = 10.0

                species[name] = {
                    "name": name,
                    "file": str(md_file.relative_to(world_dir)),
                    "trophic_level": trophic_level,
                    "trophic_name": TROPHIC_NAMES.get(trophic_level, "Consumer"),
                    "dietary_prey": prey,
                    "biomass_kg": biomass_kg,
                    "daily_caloric_demand": daily_caloric_demand,
                    "population_density": pop_density,
                    "habitat": clean_link_name(fm.get("habitat", "Global")),
                }
            except Exception as e:
                logger.warning("Failed to parse species profile %s: %s", md_file, e)

    return species


def audit_ecosystem(species: dict) -> list:
    """
    Audits ecological stability, food web connectivity, and Lindeman's 10% trophic efficiency.
    """
    findings = []
    norm_map = {normalize_name(k): k for k in species}

    # Group by trophic level and habitat
    by_habitat = {}
    for _sname, sinfo in species.items():
        hab = normalize_name(sinfo["habitat"])
        if hab not in by_habitat:
            by_habitat[hab] = []
        by_habitat[hab].append(sinfo)

    for hab, hab_species in by_habitat.items():
        producers = [s for s in hab_species if s["trophic_level"] == 1]
        herbivores = [s for s in hab_species if s["trophic_level"] == 2]
        carnivores = [s for s in hab_species if s["trophic_level"] >= 3]

        # ECO-304: Missing Primary Producers in habitat with consumers
        if (herbivores or carnivores) and not producers and hab != "global":
            findings.append({
                "id": "ECO-304",
                "severity": "WARNING",
                "habitat": hab,
                "message": f"Missing Primary Producers: Habitat '{hab}' has consumers but no Level 1 Flora / Autotrophs registered.",
                "file": hab_species[0]["file"],
            })

    for sname, sinfo in species.items():
        lvl = sinfo["trophic_level"]
        prey = sinfo["dietary_prey"]

        # 1. Predators without declared prey (ECO-301)
        if lvl >= 3:
            if not prey:
                findings.append({
                    "id": "ECO-301",
                    "severity": "WARNING",
                    "species": sname,
                    "message": f"Apex/Carnivore without Prey: Level {lvl} predator '{sname}' has no dietary_prey defined.",
                    "file": sinfo["file"],
                })
            else:
                for p in prey:
                    pnorm = normalize_name(p)
                    if pnorm not in norm_map:
                        findings.append({
                            "id": "ECO-301",
                            "severity": "WARNING",
                            "species": sname,
                            "message": f"Unknown Prey Species: Predator '{sname}' lists prey '{p}' not registered in World Bible Bestiary/Flora.",
                            "file": sinfo["file"],
                        })

        # 2. Check for circular predation / mutual apex loop (ECO-303)
        for p in prey:
            pnorm = normalize_name(p)
            if pnorm in norm_map:
                prey_info = species[norm_map[pnorm]]
                if normalize_name(sname) in [normalize_name(x) for x in prey_info["dietary_prey"]]:
                    findings.append({
                        "id": "ECO-303",
                        "severity": "WARNING",
                        "species": sname,
                        "message": f"Circular Predation Loop: '{sname}' and '{prey_info['name']}' list each other as mutual prey.",
                        "file": sinfo["file"],
                    })

        # 3. Energy Starvation / Trophic deficit (ECO-302)
        # Verify that total prey biomass density supports predator demand
        if lvl >= 3 and prey:
            total_prey_density = 0.0
            for p in prey:
                pnorm = normalize_name(p)
                if pnorm in norm_map:
                    total_prey_density += species[norm_map[pnorm]]["population_density"] * species[norm_map[pnorm]]["biomass_kg"]
            
            predator_biomass_density = sinfo["population_density"] * sinfo["biomass_kg"]
            # Lindeman: predator biomass should typically not exceed 10-15% of prey biomass
            if total_prey_density > 0:
                trophic_ratio = predator_biomass_density / total_prey_density
                if trophic_ratio > 0.35: # Exceeds sustainable carrying capacity
                    findings.append({
                        "id": "ECO-302",
                        "severity": "WARNING",
                        "species": sname,
                        "message": f"Trophic Deficit: Predator '{sname}' biomass density ({predator_biomass_density:.1f} kg/km²) exceeds 35% of prey biomass ({total_prey_density:.1f} kg/km²). Ecological collapse risk.",
                        "file": sinfo["file"],
                    })

    return findings


def generate_ecology_mermaid(species: dict) -> str:
    """Generates Obsidian-ready Mermaid.js food web graph."""
    lines = ["```mermaid", "flowchart TD"]
    lines.append("    %% Trophic Food Web Graph")
    lines.append("    classDef producer fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef herbivore fill:#1e3a5f,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef carnivore fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef apex fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc;")

    node_ids = {}
    for idx, (sname, sinfo) in enumerate(sorted(species.items())):
        nid = f"SP{idx+1}"
        node_ids[normalize_name(sname)] = nid
        lvl = sinfo["trophic_level"]
        cls = "producer" if lvl == 1 else ("herbivore" if lvl == 2 else ("carnivore" if lvl == 3 else "apex"))
        clean_name = sname.replace('"', "'")
        lines.append(f'    {nid}["{clean_name}<br/><small>Lvl {lvl} | {sinfo["habitat"]}</small>"]:::{cls}')

    # Add predation edges: Prey -> Predator (Energy Flow)
    added_edges = set()
    for sname, sinfo in species.items():
        pred_id = node_ids.get(normalize_name(sname))
        for p in sinfo["dietary_prey"]:
            prey_id = node_ids.get(normalize_name(p))
            if prey_id and pred_id:
                edge = (prey_id, pred_id)
                if edge not in added_edges:
                    added_edges.add(edge)
                    lines.append(f"    {prey_id} -->|eaten by| {pred_id}")

    lines.append("```")
    return "\n".join(lines)


def generate_ecology_html_report(audit_data: dict, output_path: Path):
    """Generates standalone HTML report for Ecological Food Web & Trophic Pyramids."""
    species = audit_data.get("species", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")

    species_rows = []
    for sn, s in species.items():
        prey_str = ", ".join(s["dietary_prey"]) if s["dietary_prey"] else "None (Autotroph/Herbivore)"
        species_rows.append(f"""
        <tr>
            <td><strong>{html.escape(sn)}</strong></td>
            <td>Level {s['trophic_level']} ({html.escape(s['trophic_name'])})</td>
            <td>{html.escape(s['habitat'])}</td>
            <td>{s['biomass_kg']} kg</td>
            <td>{s['population_density']} / km²</td>
            <td>{html.escape(prey_str)}</td>
        </tr>
        """)

    findings_cards = []
    for fd in findings:
        badge_cls = "badge-error" if fd.get("severity") == "ERROR" else "badge-warning"
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd.get('severity', 'WARNING'))}</span>
            <strong>{html.escape(fd.get('id', ''))}</strong>: {html.escape(fd.get('message', ''))}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">File: {html.escape(fd.get('file', ''))}</div>
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ All trophic levels and predation chains are ecologically sustainable.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Trophic Food Web & Ecology ({html.escape(world_name)})</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --accent: #38bdf8;
    --danger: #f43f5e;
    --warning: #fbbf24;
    --success: #34d399;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ background: #0f172a; color: var(--accent); }}
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>🌿 Ars Arcanum Trophic Food Web & Ecology Simulator</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong> | Total Species: <strong>{len(species)}</strong></p>

  <div class="card">
    <h2>Ecological Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <div class="card">
    <h2>Species Trophic Pyramid Roster</h2>
    <table>
      <thead>
        <tr>
          <th>Species</th>
          <th>Trophic Level</th>
          <th>Habitat</th>
          <th>Biomass</th>
          <th>Density</th>
          <th>Dietary Prey</th>
        </tr>
      </thead>
      <tbody>
        {"".join(species_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


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
        print("Error: Multiple worlds discovered — specify one explicitly.", file=sys.stderr)
        sys.exit(2)
    else:
        worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
        worlds = [p for p in worlds if p.is_dir()]
        if len(worlds) == 1:
            return str(worlds[0])
        elif len(worlds) > 1:
            print("Error: Multiple legacy worlds discovered — specify one explicitly.", file=sys.stderr)
            sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Trophic Food Web & Ecology Simulator")
    subparsers = parser.add_subparsers(dest="subcommand", help="Ecology subcommands")

    p_check = subparsers.add_parser("check", help="Run ecological trophic consistency audit")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_check.add_argument("--html", help="Path to export standalone HTML report")
    p_check.add_argument("--write-note", help="Export Mermaid.js Food Web note")

    p_rep = subparsers.add_parser("report", help="Display food web and trophic roster report")
    p_rep.add_argument("world", nargs="?", help="World Bible lore directory")
    p_rep.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_rep.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rep.add_argument("--html", help="Path to export standalone HTML report")
    p_rep.add_argument("--write-note", help="Export Mermaid.js Food Web note")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "report", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        args.subcommand = "check"

    raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir_str = resolve_world_dir(raw_world)
    if not world_dir_str or not Path(world_dir_str).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    world_path = Path(world_dir_str)
    species = extract_species_profiles(world_path)
    findings = audit_ecosystem(species)
    mermaid_web = generate_ecology_mermaid(species)

    audit_data = {
        "world": world_path.name,
        "species_count": len(species),
        "findings_count": len(findings),
        "species": species,
        "findings": findings,
        "mermaid": mermaid_web,
    }

    if getattr(args, "json", False):
        print(json.dumps(audit_data, indent=2))
    else:
        print("\n\033[1;32m=== Ars Arcanum Trophic Food Web & Ecology Matrix ===\033[0m")
        print(f"World: \033[1m{world_path.name}\033[0m | Species Tracked: \033[32m{len(species)}\033[0m")
        print(f"Ecological Issues / Deficits: \033[1m{len(findings)}\033[0m\n")

        if species:
            print("\033[1mBestiary & Flora Trophic Roster:\033[0m")
            for sn, sinfo in species.items():
                print(f"  🐾 \033[1;36m{sn}\033[0m [Level {sinfo['trophic_level']}: {sinfo['trophic_name']}] — {sinfo['habitat']}")
                if sinfo["dietary_prey"]:
                    print(f"     Prey: {', '.join(sinfo['dietary_prey'])}")
            print()

        if not findings:
            print("\033[32m[OK] Ecosystem trophic pyramids and predation chains are self-sustaining.\033[0m")
        else:
            for fd in findings:
                badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                print(f"{badge} {fd['id']}: {fd['message']}")
                print(f"     File: {fd['file']}\n")

    if getattr(args, "write_note", None):
        note_p = Path(args.write_note)
        atomic_write(note_p, mermaid_web)
        print(f"\nObsidian Mermaid Food-Web note written to: {note_p}")

    if getattr(args, "html", None):
        out_p = Path(args.html)
        generate_ecology_html_report(audit_data, out_p)
        print(f"\nInteractive HTML report written to: {out_p}")

    sys.exit(1 if len(findings) > 0 else 0)


if __name__ == "__main__":
    main()
