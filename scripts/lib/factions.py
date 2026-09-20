#!/usr/bin/env python3
"""
Ars Arcanum Geopolitical Faction Matrix & Campaign Logistics Engine (scripts/lib/factions.py)
=============================================================================================
Zero-dependency, offline geopolitical relationship matrix, diplomatic paradox detector,
Lanchester power-law combat simulator, and military campaign logistics calculator.

Capabilities:
1. Geopolitical Faction Matrix & Relationship Graphs:
   - Scans World Bible `Factions/*.md` frontmatter.
   - Normalizes diplomatic ties (allies, rivals, vassals, overlords, treaties).
   - Detects diplomatic paradoxes:
     * FAC-101: Asymmetric Diplomatic Link (A lists B as ally, B lists A as rival/none).
     * FAC-102: Triad Tension Paradox (A allies B, B allies C, but A and C are declared rivals).
     * FAC-103: Vassal Allegiance Conflict (Vassal of A is allied with Rival of A).
     * FAC-104: Self-Contradiction / Self-Reference (Faction allied or rival with itself).
2. Obsidian Mermaid.js Relationship Visualizer:
   - Emits Obsidian-ready Mermaid flowcharts with color-coded allegiance links.
3. Standalone Interactive HTML/SVG Matrix:
   - Standalone dark-themed report with relationship chord matrix and network visualization.
4. Lanchester Power-Law Combat Calculator (`calc battle`):
   - Simulates Linear Law (un-aimed/isolated melee) and Square Law (concentrated/aimed ranged fire).
   - Incorporates fortification defense multipliers, combat effectiveness coefficients, and morale break points.
5. Military Campaign Logistics Calculator (`calc logistics`):
   - Computes daily soldier rations (food & water) and cavalry mount fodder requirements.
   - Calculates wagon train requirements, draft animal consumption, and maximum "Wagon Radius" operating distance.

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import math
import json
import html
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.factions")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")


def parse_yaml_frontmatter(content: str) -> dict:
    """Lightweight, safe YAML frontmatter parser supporting key-value, lists, and inline arrays."""
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
        
        # Check list item under current key
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
    """Extracts entity name from wikilink or plain string."""
    if not raw:
        return ""
    m = WIKILINK_REGEX.search(str(raw))
    if m:
        return m.group(1).strip()
    return str(raw).strip().strip("\"'[]")


def normalize_name(name: str) -> str:
    """Normalizes string for comparison."""
    return re.sub(r"[\s_-]+", " ", str(name).strip().lower())


def extract_faction_profiles(world_dir: Path) -> dict:
    """Scans World Bible Factions/ directory and extracts structured profiles."""
    factions = {}
    dirs_to_check = [
        world_dir / "Factions",
        world_dir / "00-World-Bible" / "Factions",
    ]
    
    seen_files = set()
    for fdir in dirs_to_check:
        if not fdir.is_dir():
            continue
        for md_file in sorted(fdir.rglob("*.md")):
            if md_file in seen_files or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen_files.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                name = fm.get("name") or md_file.stem.replace("_", " ").replace("-", " ")
                
                # Extract allies
                raw_allies = fm.get("allies") or fm.get("ally") or []
                if isinstance(raw_allies, str):
                    raw_allies = [raw_allies]
                allies = [clean_link_name(a) for a in raw_allies if clean_link_name(a)]
                
                # Extract rivals
                raw_rivals = fm.get("rivals") or fm.get("rival") or fm.get("enemies") or []
                if isinstance(raw_rivals, str):
                    raw_rivals = [raw_rivals]
                rivals = [clean_link_name(r) for r in raw_rivals if clean_link_name(r)]
                
                # Extract vassals
                raw_vassals = fm.get("vassals") or fm.get("vassal") or []
                if isinstance(raw_vassals, str):
                    raw_vassals = [raw_vassals]
                vassals = [clean_link_name(v) for v in raw_vassals if clean_link_name(v)]
                
                # Extract overlord
                overlord = clean_link_name(fm.get("overlord") or fm.get("suzerain") or "")
                
                # Extract treaties
                raw_treaties = fm.get("treaties") or fm.get("pacts") or []
                if isinstance(raw_treaties, str):
                    raw_treaties = [raw_treaties]
                treaties = [clean_link_name(t) for t in raw_treaties if clean_link_name(t)]

                # Strength / military
                military_strength = fm.get("military_strength", 1000)
                try:
                    military_strength = float(military_strength)
                except (ValueError, TypeError):
                    military_strength = 1000.0

                factions[name] = {
                    "name": name,
                    "file": str(md_file.relative_to(world_dir)),
                    "faction_type": str(fm.get("faction_type", "Faction")),
                    "leader": clean_link_name(fm.get("leader", "Unknown")),
                    "headquarters": clean_link_name(fm.get("headquarters", "Unknown")),
                    "influence_level": str(fm.get("influence_level", "Regional")),
                    "military_strength": military_strength,
                    "allies": allies,
                    "rivals": rivals,
                    "vassals": vassals,
                    "overlord": overlord,
                    "treaties": treaties,
                }
            except Exception as e:
                logger.warning("Failed to parse %s: %s", md_file, e)

    return factions


def audit_faction_diplomacy(factions: dict) -> list:
    """Detects diplomatic paradoxes and asymmetric alliances across factions."""
    findings = []
    norm_map = {normalize_name(k): k for k in factions.keys()}

    for fname, f_info in factions.items():
        fn_norm = normalize_name(fname)

        # 1. Self-reference check (FAC-104)
        for a in f_info["allies"]:
            if normalize_name(a) == fn_norm:
                findings.append({
                    "id": "FAC-104",
                    "severity": "WARNING",
                    "faction": fname,
                    "message": f"Faction '{fname}' lists itself as an ally.",
                    "file": f_info["file"],
                })
        for r in f_info["rivals"]:
            if normalize_name(r) == fn_norm:
                findings.append({
                    "id": "FAC-104",
                    "severity": "WARNING",
                    "faction": fname,
                    "message": f"Faction '{fname}' lists itself as a rival.",
                    "file": f_info["file"],
                })

        # 2. Asymmetric Alliance / Rivalry check (FAC-101)
        for ally in f_info["allies"]:
            anorm = normalize_name(ally)
            if anorm in norm_map:
                target_real = norm_map[anorm]
                target_info = factions[target_real]
                target_allies_norm = [normalize_name(x) for x in target_info["allies"]]
                target_rivals_norm = [normalize_name(x) for x in target_info["rivals"]]
                
                if fn_norm in target_rivals_norm:
                    findings.append({
                        "id": "FAC-101",
                        "severity": "ERROR",
                        "faction": fname,
                        "message": f"Contradiction: '{fname}' lists '{target_real}' as an ally, but '{target_real}' lists '{fname}' as a rival.",
                        "file": f_info["file"],
                    })
                elif fn_norm not in target_allies_norm:
                    findings.append({
                        "id": "FAC-101",
                        "severity": "WARNING",
                        "faction": fname,
                        "message": f"Asymmetric Alliance: '{fname}' claims alliance with '{target_real}', but '{target_real}' does not reciprocate in frontmatter.",
                        "file": f_info["file"],
                    })

        # 3. Triad Paradox: Ally of Enemy (FAC-102)
        # If A is ally with B, and B is ally with C, but A is rival with C
        for b_name in f_info["allies"]:
            bnorm = normalize_name(b_name)
            if bnorm in norm_map:
                b_info = factions[norm_map[bnorm]]
                for c_name in b_info["allies"]:
                    cnorm = normalize_name(c_name)
                    if cnorm == fn_norm:
                        continue
                    # Check if A considers C a rival
                    if cnorm in [normalize_name(x) for x in f_info["rivals"]]:
                        c_real = norm_map.get(cnorm, c_name)
                        b_real = norm_map[bnorm]
                        findings.append({
                            "id": "FAC-102",
                            "severity": "WARNING",
                            "faction": fname,
                            "message": f"Triad Tension Paradox: '{fname}' is allied with '{b_real}', who is allied with '{c_real}', but '{fname}' and '{c_real}' are declared rivals.",
                            "file": f_info["file"],
                        })

        # 4. Vassal Allegiance Conflict (FAC-103)
        for v_name in f_info["vassals"]:
            vnorm = normalize_name(v_name)
            if vnorm in norm_map:
                v_info = factions[norm_map[vnorm]]
                v_allies_norm = [normalize_name(x) for x in v_info["allies"]]
                # Check if vassal is allied with any of overlord's rivals
                for r_name in f_info["rivals"]:
                    rnorm = normalize_name(r_name)
                    if rnorm in v_allies_norm:
                        v_real = norm_map[vnorm]
                        r_real = norm_map.get(rnorm, r_name)
                        findings.append({
                            "id": "FAC-103",
                            "severity": "ERROR",
                            "faction": fname,
                            "message": f"Vassal Conflict: Vassal '{v_real}' of overlord '{fname}' is allied with overlord's rival '{r_real}'.",
                            "file": f_info["file"],
                        })

    return findings


def generate_faction_mermaid(factions: dict) -> str:
    """Generates Obsidian-ready Mermaid.js relationship graph."""
    lines = ["```mermaid", "flowchart LR"]
    lines.append("    %% Faction Geopolitical Matrix")
    lines.append("    classDef empire fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef guild fill:#1e293b,stroke:#4ade80,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef cult fill:#1e293b,stroke:#f43f5e,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef defaultNode fill:#0f172a,stroke:#64748b,stroke-width:1px,color:#f8fafc;")

    node_ids = {}
    for idx, fname in enumerate(sorted(factions.keys())):
        nid = f"F{idx+1}"
        node_ids[normalize_name(fname)] = (nid, fname)
        ftype = factions[fname]["faction_type"]
        safe_name = fname.replace('"', "'")
        lines.append(f'    {nid}["{safe_name}<br/><small><i>{ftype}</i></small>"]')

    processed_edges = set()

    for fname, finfo in factions.items():
        src_entry = node_ids.get(normalize_name(fname))
        if not src_entry:
            continue
        src_id = src_entry[0]

        # Alliances
        for a in finfo["allies"]:
            tgt_entry = node_ids.get(normalize_name(a))
            if tgt_entry:
                tgt_id = tgt_entry[0]
                edge_pair = tuple(sorted([src_id, tgt_id]))
                if ("ally", edge_pair) not in processed_edges:
                    processed_edges.add(("ally", edge_pair))
                    lines.append(f"    {src_id} <==>|Ally| {tgt_id}")

        # Rivalries
        for r in finfo["rivals"]:
            tgt_entry = node_ids.get(normalize_name(r))
            if tgt_entry:
                tgt_id = tgt_entry[0]
                edge_pair = tuple(sorted([src_id, tgt_id]))
                if ("rival", edge_pair) not in processed_edges:
                    processed_edges.add(("rival", edge_pair))
                    lines.append(f"    {src_id} -.->|Rival| {tgt_id}")

        # Vassalage
        for v in finfo["vassals"]:
            tgt_entry = node_ids.get(normalize_name(v))
            if tgt_entry:
                tgt_id = tgt_entry[0]
                lines.append(f"    {src_id} ==>|Vassal| {tgt_id}")

    lines.append("```")
    return "\n".join(lines)


def calc_lanchester_battle(
    attacker_force: float,
    defender_force: float,
    attacker_eff: float = 1.0,
    defender_eff: float = 1.0,
    fort_bonus: float = 1.0,
    law: str = "square",
    rounds: int = 20,
    morale_threshold: float = 0.5
) -> dict:
    """
    Computes Lanchester combat engagement casualty curves and victor prediction.
    
    Laws:
    - square: Modern/aimed ranged firepower. dA/dt = -beta * D, dD/dt = -alpha * A
    - linear: Melee/un-aimed area fire. dA/dt = -beta * (A*D) / D or constant rate
    """
    a = float(attacker_force)
    d = float(defender_force)
    alpha = float(attacker_eff)
    beta = float(defender_eff) * float(fort_bonus)
    
    a_initial = a
    d_initial = d
    a_morale_limit = a_initial * (1.0 - morale_threshold)
    d_morale_limit = d_initial * (1.0 - morale_threshold)

    history = [{
        "round": 0,
        "attacker_remaining": round(a),
        "defender_remaining": round(d),
        "attacker_casualties": 0,
        "defender_casualties": 0,
    }]

    dt = 0.1
    current_time = 0.0
    victor = "Draw"
    outcome_reason = "Max rounds reached"

    total_steps = rounds * 10
    for step in range(1, total_steps + 1):
        if a <= 0 or d <= 0 or a <= a_morale_limit or d <= d_morale_limit:
            break
        
        if law == "square":
            da = beta * d * dt
            dd = alpha * a * dt
        else:
            # Linear law: Melee front line engagement bounded by contact width min(a, d)
            contact = min(a, d)
            da = beta * contact * dt
            dd = alpha * contact * dt

        a = max(0.0, a - da)
        d = max(0.0, d - dd)
        current_time += dt

        if step % 10 == 0:
            history.append({
                "round": step // 10,
                "attacker_remaining": round(a),
                "defender_remaining": round(d),
                "attacker_casualties": round(a_initial - a),
                "defender_casualties": round(d_initial - d),
            })

    if a <= a_morale_limit and d <= d_morale_limit:
        victor = "Mutual Morale Collapse / Pyrrhic Draw"
        outcome_reason = "Both forces suffered critical morale breakage (>50% casualties)."
    elif a <= a_morale_limit or a <= 0:
        victor = "Defender"
        outcome_reason = "Attacker broken or destroyed."
    elif d <= d_morale_limit or d <= 0:
        victor = "Attacker"
        outcome_reason = "Defender broken or destroyed."
    else:
        victor = "Attacker" if (a / a_initial) > (d / d_initial) else "Defender"
        outcome_reason = "Inconclusive engagement; advantage based on casualty ratio."

    return {
        "law": law,
        "initial_attacker": round(a_initial),
        "initial_defender": round(d_initial),
        "final_attacker": round(a),
        "final_defender": round(d),
        "attacker_loss_pct": round((a_initial - a) / a_initial * 100, 1) if a_initial else 0,
        "defender_loss_pct": round((d_initial - d) / d_initial * 100, 1) if d_initial else 0,
        "victor": victor,
        "outcome_reason": outcome_reason,
        "rounds_simulated": len(history) - 1,
        "history": history,
    }


def calc_campaign_logistics(
    infantry: int,
    cavalry: int,
    support: int = 0,
    distance_km: float = 200.0,
    march_speed_km_day: float = 20.0,
    ration_kg_soldier: float = 1.5,
    water_liters_soldier: float = 3.0,
    fodder_kg_mount: float = 10.0,
    wagon_payload_kg: float = 500.0,
    draft_horses_per_wagon: int = 2,
    forage_pct: float = 0.0
) -> dict:
    """
    Calculates campaign supply requirements, daily consumption, wagon train logistics,
    and the theoretical operational 'Wagon Radius' (point of self-starvation).
    """
    total_soldiers = infantry + cavalry + support
    total_mounts = cavalry + (draft_horses_per_wagon * 0) # Base mounts

    # Daily consumption
    daily_food_kg = total_soldiers * ration_kg_soldier * (1.0 - forage_pct)
    daily_water_liters = total_soldiers * water_liters_soldier
    daily_fodder_kg = total_mounts * fodder_kg_mount * (1.0 - forage_pct)
    
    total_daily_supply_kg = daily_food_kg + daily_water_liters + daily_fodder_kg
    daily_metric_tons = total_daily_supply_kg / 1000.0

    days_one_way = distance_km / max(1.0, march_speed_km_day)
    total_campaign_days = days_one_way * 2.0 # Round trip supply expectation

    # Wagon train calculation
    # Each wagon carries wagon_payload_kg. Draft animals also consume fodder!
    draft_animal_consumption_day_per_wagon = draft_horses_per_wagon * fodder_kg_mount * (1.0 - forage_pct)
    
    # Wagon Radius formula: R_max = (Wagon Payload / (2 * Draft Animal Daily Fodder)) * March Speed
    if draft_animal_consumption_day_per_wagon > 0:
        max_wagon_days = wagon_payload_kg / (2.0 * draft_animal_consumption_day_per_wagon)
        max_wagon_radius_km = max_wagon_days * march_speed_km_day
    else:
        max_wagon_days = 999.0
        max_wagon_radius_km = 99999.0

    total_supplies_needed_kg = total_daily_supply_kg * total_campaign_days
    # Extra draft horses needed for wagons
    wagons_needed = math.ceil(total_supplies_needed_kg / max(1.0, wagon_payload_kg))
    draft_horses_total = wagons_needed * draft_horses_per_wagon

    feasible = distance_km <= max_wagon_radius_km

    return {
        "army_composition": {
            "infantry": infantry,
            "cavalry": cavalry,
            "support": support,
            "total_personnel": total_soldiers,
            "cavalry_mounts": cavalry,
            "draft_horses": draft_horses_total,
        },
        "campaign_parameters": {
            "distance_km": distance_km,
            "march_speed_km_day": march_speed_km_day,
            "duration_days_one_way": round(days_one_way, 1),
            "duration_days_round_trip": round(total_campaign_days, 1),
            "forage_discount_pct": round(forage_pct * 100, 1),
        },
        "daily_consumption": {
            "food_kg": round(daily_food_kg, 1),
            "water_liters": round(daily_water_liters, 1),
            "cavalry_fodder_kg": round(daily_fodder_kg, 1),
            "total_daily_supply_tons": round(daily_metric_tons, 2),
        },
        "logistics_requirements": {
            "total_campaign_supply_tons": round(total_supplies_needed_kg / 1000.0, 2),
            "wagons_required": wagons_needed,
            "draft_horses_required": draft_horses_total,
            "wagon_radius_limit_km": round(max_wagon_radius_km, 1),
            "is_within_wagon_radius": feasible,
            "logistics_verdict": "Feasible without intermediate depots" if feasible else "SUPPLY FAILURE: Exceeds wagon radius limit. Depots or forage required.",
        }
    }


def generate_faction_html_report(audit_data: dict, output_path: Path):
    """Generates a standalone dark-mode HTML report for the Faction Matrix & Campaign Logistics."""
    factions = audit_data.get("factions", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")

    rows = []
    for fn, f in factions.items():
        allies_str = ", ".join(f["allies"]) if f["allies"] else "None"
        rivals_str = ", ".join(f["rivals"]) if f["rivals"] else "None"
        vassals_str = ", ".join(f["vassals"]) if f["vassals"] else "None"
        rows.append(f"""
        <tr>
            <td><strong>{html.escape(fn)}</strong></td>
            <td><span class="badge badge-type">{html.escape(f['faction_type'])}</span></td>
            <td>{html.escape(f['leader'])}</td>
            <td>{f['military_strength']:,.0f}</td>
            <td style="color: #4ade80;">{html.escape(allies_str)}</td>
            <td style="color: #f87171;">{html.escape(rivals_str)}</td>
            <td style="color: #cbd5e1;">{html.escape(vassals_str)}</td>
        </tr>
        """)

    findings_rows = []
    for fd in findings:
        badge_cls = "badge-error" if fd["severity"] == "ERROR" else "badge-warning"
        findings_rows.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd['severity'])}</span>
            <strong>{html.escape(fd['id'])}</strong>: {html.escape(fd['message'])}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">Faction: {html.escape(fd.get('faction', ''))} | File: {html.escape(fd.get('file', ''))}</div>
        </div>
        """)

    findings_html = "".join(findings_rows) if findings_rows else "<div style='color: #4ade80;'>✓ No diplomatic paradoxes detected across factions.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Geopolitical Faction Matrix ({html.escape(world_name)})</title>
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
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }}
  th, td {{
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{ background: #0f172a; color: var(--accent); }}
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-type {{ background: #0369a1; color: #fff; }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>⚔️ Ars Arcanum Geopolitical Faction Matrix</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong> | Total Factions: <strong>{len(factions)}</strong></p>

  <div class="card">
    <h2>Diplomatic Paradox Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <div class="card">
    <h2>Faction Diplomatic Roster</h2>
    <table>
      <thead>
        <tr>
          <th>Faction</th>
          <th>Type</th>
          <th>Leader</th>
          <th>Military Strength</th>
          <th>Allies</th>
          <th>Rivals</th>
          <th>Vassals</th>
        </tr>
      </thead>
      <tbody>
        {"".join(rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")


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
    parser = argparse.ArgumentParser(description="Ars Arcanum Geopolitical Faction Matrix & Campaign Logistics Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Faction subcommands")

    # 1. matrix / audit (default)
    p_audit = subparsers.add_parser("check", help="Run diplomatic consistency audit on faction relations")
    p_audit.add_argument("world", nargs="?", help="World Bible lore directory")
    p_audit.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_audit.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_audit.add_argument("--html", help="Path to export standalone HTML report")
    p_audit.add_argument("--write-note", help="Export Mermaid.js relationship graph to note")

    p_matrix = subparsers.add_parser("matrix", help="Display faction matrix and relationship graph")
    p_matrix.add_argument("world", nargs="?", help="World Bible lore directory")
    p_matrix.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_matrix.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_matrix.add_argument("--html", help="Path to export standalone HTML report")
    p_matrix.add_argument("--write-note", help="Export Mermaid.js relationship graph to note")

    # 2. calc battle
    p_battle = subparsers.add_parser("battle", help="Lanchester power-law combat calculator")
    p_battle.add_argument("-a", "--attacker", type=float, required=True, help="Attacker starting force")
    p_battle.add_argument("-d", "--defender", type=float, required=True, help="Defender starting force")
    p_battle.add_argument("--attacker-eff", type=float, default=1.0, help="Attacker combat effectiveness (default 1.0)")
    p_battle.add_argument("--defender-eff", type=float, default=1.0, help="Defender combat effectiveness (default 1.0)")
    p_battle.add_argument("--fort", type=float, default=1.0, help="Fortification defense multiplier (default 1.0)")
    p_battle.add_argument("--law", choices=["square", "linear"], default="square", help="Lanchester law (square or linear)")
    p_battle.add_argument("--rounds", type=int, default=20, help="Max combat rounds (default 20)")
    p_battle.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. calc logistics
    p_log = subparsers.add_parser("logistics", help="Military campaign supply and wagon radius calculator")
    p_log.add_argument("--infantry", type=int, default=10000, help="Infantry troop count")
    p_log.add_argument("--cavalry", type=int, default=2000, help="Cavalry mounted troops count")
    p_log.add_argument("--support", type=int, default=1000, help="Support/camp follower count")
    p_log.add_argument("--distance", type=float, default=200.0, help="Campaign distance in km (default 200)")
    p_log.add_argument("--speed", type=float, default=20.0, help="March speed in km/day (default 20)")
    p_log.add_argument("--forage", type=float, default=0.0, help="Local forage fraction 0.0 to 1.0 (default 0.0)")
    p_log.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "matrix", "battle", "logistics", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        # Default to matrix check if world argument passed or no subcommand
        args.subcommand = "check"

    if args.subcommand in ("check", "matrix"):
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = resolve_world_dir(raw_world)
        if not world_dir_str or not Path(world_dir_str).is_dir():
            print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        world_path = Path(world_dir_str)
        factions = extract_faction_profiles(world_path)
        findings = audit_faction_diplomacy(factions)
        mermaid_graph = generate_faction_mermaid(factions)

        audit_data = {
            "world": world_path.name,
            "factions_count": len(factions),
            "findings_count": len(findings),
            "factions": factions,
            "findings": findings,
            "mermaid": mermaid_graph,
        }

        if getattr(args, "json", False):
            print(json.dumps(audit_data, indent=2))
        else:
            print(f"\n\033[1;36m=== Ars Arcanum Geopolitical Faction Matrix ===\033[0m")
            print(f"World: \033[1m{world_path.name}\033[0m | Total Factions: \033[32m{len(factions)}\033[0m")
            print(f"Diplomatic Paradoxes / Issues: \033[1m{len(findings)}\033[0m\n")

            if factions:
                print("\033[1mRegistered Factions & Diplomatic Alignments:\033[0m")
                for fn, finfo in factions.items():
                    print(f"  👑 \033[1;33m{fn}\033[0m [{finfo['faction_type']}] — Military Strength: {finfo['military_strength']:,.0f}")
                    if finfo["allies"]:
                        print(f"     Allies : \033[32m{', '.join(finfo['allies'])}\033[0m")
                    if finfo["rivals"]:
                        print(f"     Rivals : \033[31m{', '.join(finfo['rivals'])}\033[0m")
                    if finfo["vassals"]:
                        print(f"     Vassals: \033[34m{', '.join(finfo['vassals'])}\033[0m")
                print()

            if not findings:
                print("\033[32m[OK] Diplomatic matrix is internally consistent (no paradoxes).\033[0m")
            else:
                for fd in findings:
                    badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                    print(f"{badge} {fd['id']}: {fd['message']}")
                    print(f"     File: {fd['file']}\n")

        if getattr(args, "write_note", None):
            note_p = Path(args.write_note)
            note_p.write_text(mermaid_graph, encoding="utf-8")
            print(f"\nObsidian Mermaid note written to: {note_p}")

        if getattr(args, "html", None):
            out_p = Path(args.html)
            generate_faction_html_report(audit_data, out_p)
            print(f"\nInteractive HTML report written to: {out_p}")

        sys.exit(1 if len(findings) > 0 else 0)

    elif args.subcommand == "battle":
        result = calc_lanchester_battle(
            attacker_force=args.attacker,
            defender_force=args.defender,
            attacker_eff=args.attacker_eff,
            defender_eff=args.defender_eff,
            fort_bonus=args.fort,
            law=args.law,
            rounds=args.rounds,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n\033[1;35m=== Lanchester Combat Simulation ({args.law.capitalize()} Law) ===\033[0m")
            print(f"Initial Forces : Attacker \033[1;31m{result['initial_attacker']:,}\033[0m vs Defender \033[1;34m{result['initial_defender']:,}\033[0m (Fort bonus: {args.fort}x)")
            print(f"Final Forces   : Attacker \033[1;31m{result['final_attacker']:,}\033[0m (-{result['attacker_loss_pct']}%) | Defender \033[1;34m{result['final_defender']:,}\033[0m (-{result['defender_loss_pct']}%)")
            print(f"Outcome        : \033[1;32m{result['victor']}\033[0m — {result['outcome_reason']}")
            print(f"Combat Rounds  : {result['rounds_simulated']}\n")
        sys.exit(0)

    elif args.subcommand == "logistics":
        result = calc_campaign_logistics(
            infantry=args.infantry,
            cavalry=args.cavalry,
            support=args.support,
            distance_km=args.distance,
            march_speed_km_day=args.speed,
            forage_pct=args.forage,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            comp = result["army_composition"]
            cons = result["daily_consumption"]
            req = result["logistics_requirements"]
            param = result["campaign_parameters"]

            print(f"\n\033[1;36m=== Military Campaign Logistics & Supply Calculator ===\033[0m")
            print(f"Personnel      : {comp['total_personnel']:,} ({comp['infantry']:,} inf, {comp['cavalry']:,} cav, {comp['support']:,} support)")
            print(f"Campaign March : {param['distance_km']} km @ {param['march_speed_km_day']} km/day ({param['duration_days_one_way']} days one-way)")
            print(f"Daily Demand   : {cons['food_kg']:,} kg food, {cons['water_liters']:,} L water, {cons['cavalry_fodder_kg']:,} kg fodder ({cons['total_daily_supply_tons']} metric tons/day)")
            print(f"Wagon Train    : {req['wagons_required']:,} wagons ({req['draft_horses_required']:,} draft horses)")
            print(f"Wagon Radius   : \033[1m{req['wagon_radius_limit_km']} km\033[0m maximum operational limit")
            verdict_col = "\033[32m" if req["is_within_wagon_radius"] else "\033[31m"
            print(f"Verdict        : {verdict_col}{req['logistics_verdict']}\033[0m\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
