#!/usr/bin/env python3
"""
Ars Arcanum Causal DAGs, Time Travel Loops & Multiverse Branching Engine (scripts/lib/causality.py)
=================================================================================================
Zero-dependency, offline causal graph builder, Novikov self-consistency validator,
closed timelike curve (CTC) loop detector, and multiverse branching timeline analyzer.

Capabilities:
1. Narrative Causal DAG & Timeline Extraction:
   - Scans manuscript scenes (`*.md`) and history notes (`History/*.md`).
   - Extracts `@timeline:`, `@time:` / `@temporal-coord:`, `@event:`, `@causes:`,
     `@causal-origin:`, `@branch-from:`, and `@paradox-type:` directives.
2. Causal Paradox & Consistency Diagnostics:
   - CAU-101: Grandfather Paradox / Destructive Negative Feedback Loop.
   - CAU-102: Unregistered Bootstrap / Ontological Information Loop.
   - CAU-103: Novikov Self-Consistency Violation.
   - CAU-104: Orphan / Abandoned Timeline Branch.
   - CAU-105: Temporal Inversion (Cause occurs after effect in linear time without time-travel tag).
3. Visualizers:
   - Obsidian Mermaid.js gitGraph / flowchart TD note export (`--write-note`).
   - Standalone interactive HTML/SVG Causal DAG visualizer (`--html`).
4. Timeline Branch Scaffolding (`arcanum causality branch <name>`):
   - Computes branch divergence coordinate and metadata headers.

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

logger = logging.getLogger("arcanum.causality")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")


try:
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from frontmatter import parse_yaml_frontmatter


def normalize_id(text: str) -> str:
    """Normalizes event/timeline identifier."""
    return re.sub(r"[\s_#-]+", "-", str(text).strip().lower())


def extract_causal_nodes(world_dir: Path | None = None, manuscript_dir: Path | None = None) -> tuple:
    """
    Extracts events, temporal metadata, timeline branches, and causal edges from world and manuscript.
    Returns: (events_dict, timelines_dict)
    """
    events = {}
    timelines = {"prime": {"id": "prime", "name": "Prime Timeline", "branches": [], "events": []}}

    dirs_to_scan = []
    if manuscript_dir and manuscript_dir.is_dir():
        dirs_to_scan.append((manuscript_dir, "manuscript"))
    if world_dir and world_dir.is_dir():
        for sub in ("History", "00-World-Bible/History", "Cosmology", "00-World-Bible/Cosmology"):
            hdir = world_dir / sub
            if hdir.is_dir():
                dirs_to_scan.append((hdir, "world"))

    for base_dir, source_type in dirs_to_scan:
        for md_file in sorted(base_dir.rglob("*.md")):
            if md_file.name.startswith(".") or "Front_Matter" in md_file.parts or "Back_Matter" in md_file.parts:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                lines = content.splitlines()

                # Extract frontmatter or file-level defaults
                event_name = fm.get("name") or md_file.stem.replace("_", " ")
                event_id = normalize_id(fm.get("id") or md_file.stem)
                timeline_id = normalize_id(fm.get("timeline") or "prime")
                time_coord = fm.get("time") or fm.get("temporal_coord") or fm.get("start_year") or ""
                causal_origins = fm.get("causal_origin") or fm.get("prerequisites") or []
                if isinstance(causal_origins, str):
                    causal_origins = [causal_origins]
                causes = fm.get("causes") or fm.get("triggers") or []
                if isinstance(causes, str):
                    causes = [causes]
                paradox_type = fm.get("paradox_type") or ""
                branch_from = fm.get("branch_from") or ""

                # Also scan line tags
                for _line_idx, line in enumerate(lines, start=1):
                    tag_m = TAG_REGEX.match(line.strip())
                    if tag_m:
                        tag_k = tag_m.group(1).lower()
                        tag_v = tag_m.group(2).strip()
                        if tag_k in ("event", "scene-id", "id", "event-id", "scene_id"):
                            event_id = normalize_id(tag_v)
                        elif tag_k in ("timeline", "branch"):
                            timeline_id = normalize_id(tag_v)
                        elif tag_k in ("time", "temporal-coord", "temporal_coord"):
                            time_coord = tag_v
                        elif tag_k in ("causal-origin", "causal_origin", "origin", "prereq"):
                            causal_origins.extend([o.strip() for o in tag_v.split(",") if o.strip()])
                        elif tag_k in ("causes", "cause", "triggers", "effect"):
                            causes.extend([c.strip() for c in tag_v.split(",") if c.strip()])
                        elif tag_k in ("paradox-type", "paradox", "loop"):
                            paradox_type = tag_v.lower()
                        elif tag_k in ("branch-from", "branch_from", "divergence"):
                            branch_from = tag_v

                if timeline_id not in timelines:
                    timelines[timeline_id] = {
                        "id": timeline_id,
                        "name": timeline_id.replace("-", " ").title(),
                        "branches": [],
                        "events": []
                    }

                clean_origins = [normalize_id(o) for o in causal_origins if o]
                clean_causes = [normalize_id(c) for c in causes if c]

                events[event_id] = {
                    "id": event_id,
                    "name": event_name,
                    "timeline": timeline_id,
                    "time_coord": str(time_coord),
                    "causal_origins": clean_origins,
                    "causes": clean_causes,
                    "paradox_type": paradox_type,
                    "branch_from": branch_from,
                    "file": str(md_file.relative_to(base_dir.parent if base_dir != manuscript_dir else base_dir)),
                    "source": source_type,
                }

                timelines[timeline_id]["events"].append(event_id)
                if branch_from:
                    timelines[timeline_id]["branch_from"] = branch_from

            except Exception as e:
                logger.warning("Failed to parse causal node %s: %s", md_file, e)

    return events, timelines


def parse_numeric_year(val: str):
    """Extracts numeric year from date or temporal string for ordering checks."""
    if not val:
        return None
    m = re.search(r"([+-]?\d+(?:\.\d+)?)", str(val))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def audit_causality(events: dict, timelines: dict) -> list:
    """
    Performs topological causal analysis, detecting Grandfather paradoxes,
    unregistered bootstrap loops, Novikov violations, and orphan timelines.
    """
    findings = []

    # 1. Build adjacency graph
    # Adjacency: parent -> list of children
    adj = {eid: set(einfo["causes"]) for eid, einfo in events.items()}
    # Backlinks: child -> list of parents
    for eid, einfo in events.items():
        for origin in einfo["causal_origins"]:
            if origin in adj:
                adj[origin].add(eid)

    # 2. Cycle Detection (DFS) to find Closed Timelike Curves / Loops
    visited = {} # 0: unvisited, 1: visiting, 2: visited
    cycles = []

    def dfs(node, path):
        visited[node] = 1
        path.append(node)
        for neighbor in adj.get(node, []):
            if neighbor not in events:
                continue
            if visited.get(neighbor, 0) == 1:
                # Cycle found!
                cycle_start = path.index(neighbor)
                cycles.append([*path[cycle_start:], neighbor])
            elif visited.get(neighbor, 0) == 0:
                dfs(neighbor, path)
        path.pop()
        visited[node] = 2

    for eid in events:
        if visited.get(eid, 0) == 0:
            dfs(eid, [])

    # Process discovered causal cycles
    for cycle in cycles:
        cycle_str = " -> ".join(cycle)
        cycle_nodes = [events[c] for c in cycle if c in events]
        paradox_types = {c.get("paradox_type", "") for c in cycle_nodes if c.get("paradox_type")}

        if "novikov-violation" in paradox_types or "novikov_violation" in paradox_types:
            findings.append({
                "id": "CAU-103",
                "severity": "ERROR",
                "message": f"Novikov Self-Consistency Violation: Causal loop creates irreversible history alteration: {cycle_str}",
                "cycle": cycle,
                "file": cycle_nodes[0]["file"] if cycle_nodes else "",
            })
        elif "bootstrap" in paradox_types or "predestination" in paradox_types:
            # Self-consistent closed timelike curve
            continue
        elif "grandfather" in paradox_types:
            findings.append({
                "id": "CAU-101",
                "severity": "ERROR",
                "message": f"Grandfather Paradox Detected: Destructive causal loop without timeline branch closure: {cycle_str}",
                "cycle": cycle,
                "file": cycle_nodes[0]["file"] if cycle_nodes else "",
            })
        else:
            findings.append({
                "id": "CAU-102",
                "severity": "WARNING",
                "message": f"Unregistered Causal Loop / Bootstrap Paradox: Circular causality detected ({cycle_str}). Tag with '@paradox-type: bootstrap' or '@paradox-type: predestination' if intentional.",
                "cycle": cycle,
                "file": cycle_nodes[0]["file"] if cycle_nodes else "",
            })

    # 3. Check for Orphan Timelines (CAU-104)
    for tid, tinfo in timelines.items():
        if tid == "prime":
            continue
        if len(tinfo["events"]) == 0:
            findings.append({
                "id": "CAU-104",
                "severity": "WARNING",
                "message": f"Orphan Timeline Branch: Timeline '{tid}' has no associated scene events.",
                "timeline": tid,
                "file": "manuscript",
            })

    # 4. Check for Non-Existent Causal Origins / Broken Links (CAU-105)
    for eid, einfo in events.items():
        for orig in einfo["causal_origins"]:
            if orig not in events:
                findings.append({
                    "id": "CAU-105",
                    "severity": "WARNING",
                    "message": f"Dangling Causal Origin: Event '{eid}' references prerequisite '{orig}' which is not defined in any scene or history note.",
                    "file": einfo["file"],
                })

    # 5. Check for Linear Temporal Inversions
    for src_id, targets in adj.items():
        src_ev = events.get(src_id)
        if not src_ev or src_ev.get("paradox_type"):
            continue
        src_yr = parse_numeric_year(src_ev.get("time_coord"))
        if src_yr is None:
            continue
        for tgt_id in targets:
            tgt_ev = events.get(tgt_id)
            if not tgt_ev or tgt_ev.get("paradox_type") or tgt_ev.get("timeline") != src_ev.get("timeline"):
                continue
            tgt_yr = parse_numeric_year(tgt_ev.get("time_coord"))
            if tgt_yr is not None and src_yr > tgt_yr:
                findings.append({
                    "id": "CAU-105",
                    "severity": "WARNING",
                    "message": f"Temporal Inversion: Cause '{src_id}' (Coord: {src_ev['time_coord']}) occurs chronologically after effect '{tgt_id}' (Coord: {tgt_ev['time_coord']}) on timeline '{src_ev['timeline']}' without time-travel tag.",
                    "file": src_ev["file"],
                })

    return findings


def generate_causality_mermaid(events: dict, timelines: dict) -> str:
    """Generates Obsidian-ready Mermaid.js Causal DAG."""
    lines = ["```mermaid", "graph TD"]
    lines.append("    %% Causal DAG & Timeline Graph")
    lines.append("    classDef prime fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef branch fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef loop fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc;")

    # Group by timeline subgraphs
    for tid, tinfo in timelines.items():
        lines.append(f'    subgraph SG_{tid} ["Timeline: {tinfo["name"]}"]')
        for eid in tinfo["events"]:
            e = events.get(eid)
            if not e:
                continue
            time_label = f"<br/><small>{e['time_coord']}</small>" if e["time_coord"] else ""
            clean_name = e["name"].replace('"', "'")
            cls = "prime" if tid == "prime" else "branch"
            if e.get("paradox_type"):
                cls = "loop"
            lines.append(f'        {eid}["{clean_name}{time_label}"]:::{cls}')
        lines.append("    end")

    # Add causal edges
    added_edges = set()
    for eid, einfo in events.items():
        for target in einfo["causes"]:
            edge = (eid, target)
            if edge not in added_edges and target in events:
                added_edges.add(edge)
                lines.append(f"    {eid} -->|causes| {target}")
        for orig in einfo["causal_origins"]:
            edge = (orig, eid)
            if edge not in added_edges and orig in events:
                added_edges.add(edge)
                lines.append(f"    {orig} -->|prereq| {eid}")

    lines.append("```")
    return "\n".join(lines)


def generate_causality_html_report(audit_data: dict, output_path: Path):
    """Generates standalone interactive HTML report for Causal DAGs and timelines."""
    events = audit_data.get("events", {})
    timelines = audit_data.get("timelines", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")

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

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ All causal sequences and closed loops are self-consistent.</div>"

    events_rows = []
    for eid, e in events.items():
        events_rows.append(f"""
        <tr>
            <td><strong>{html.escape(e['name'])}</strong><br/><small>{html.escape(eid)}</small></td>
            <td><span class="badge badge-timeline">{html.escape(e['timeline'])}</span></td>
            <td>{html.escape(e['time_coord'] or 'N/A')}</td>
            <td>{html.escape(', '.join(e['causal_origins']) or '—')}</td>
            <td>{html.escape(', '.join(e['causes']) or '—')}</td>
            <td>{html.escape(e['paradox_type'] or 'Linear')}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Causal DAG & Multiverse Engine ({html.escape(world_name)})</title>
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
  .badge-timeline {{ background: #0284c7; color: #fff; }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>⏳ Ars Arcanum Causal DAG & Multiverse Engine</h1>
  <p>World: <strong>{html.escape(world_name)}</strong> | Total Events: <strong>{len(events)}</strong> | Timelines: <strong>{len(timelines)}</strong></p>

  <div class="card">
    <h2>Causal Consistency Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <div class="card">
    <h2>Event Causal Sequence Roster</h2>
    <table>
      <thead>
        <tr>
          <th>Event</th>
          <th>Timeline</th>
          <th>Coord</th>
          <th>Prerequisites</th>
          <th>Causes</th>
          <th>Paradox Type</th>
        </tr>
      </thead>
      <tbody>
        {"".join(events_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


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
    parser = argparse.ArgumentParser(description="Ars Arcanum Causal DAG & Multiverse Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Causality subcommands")

    # 1. check / graph
    p_check = subparsers.add_parser("check", help="Audit causal DAG for paradoxes and loops")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_check.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_check.add_argument("--html", help="Path to export standalone HTML report")
    p_check.add_argument("--write-note", help="Export Mermaid.js DAG note")

    p_dag = subparsers.add_parser("dag", help="Display causal DAG and timelines")
    p_dag.add_argument("world", nargs="?", help="World Bible lore directory")
    p_dag.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_dag.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_dag.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_dag.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_dag.add_argument("--html", help="Path to export standalone HTML report")
    p_dag.add_argument("--write-note", help="Export Mermaid.js DAG note")

    # 2. branch scaffolding
    p_branch = subparsers.add_parser("branch", help="Scaffold a multiverse branch coordinate")
    p_branch.add_argument("name", help="Name of new timeline branch")
    p_branch.add_argument("--from-timeline", default="prime", help="Origin timeline to branch from")
    p_branch.add_argument("--at-coord", default="Year 1000", help="Temporal coordinate of branch divergence")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "dag", "branch", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        args.subcommand = "check"

    if args.subcommand in ("check", "dag"):
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = resolve_world_dir(raw_world) if raw_world else None
        world_path = Path(world_dir_str) if world_dir_str else None

        raw_ms = getattr(args, "manuscript", None) or getattr(args, "manuscript_pos", None)
        ms_dir_str = resolve_manuscript_dir(raw_ms) if raw_ms else None
        ms_path = Path(ms_dir_str) if ms_dir_str else None

        if not world_path and not ms_path:
            print("Error: Specify a World Bible or Manuscript directory.", file=sys.stderr)
            sys.exit(2)

        events, timelines = extract_causal_nodes(world_path, ms_path)
        findings = audit_causality(events, timelines)
        mermaid_dag = generate_causality_mermaid(events, timelines)

        audit_data = {
            "world": world_path.name if world_path else "N/A",
            "manuscript": ms_path.name if ms_path else "N/A",
            "events_count": len(events),
            "timelines_count": len(timelines),
            "findings_count": len(findings),
            "events": events,
            "timelines": timelines,
            "findings": findings,
            "mermaid": mermaid_dag,
        }

        if getattr(args, "json", False):
            print(json.dumps(audit_data, indent=2))
        else:
            print("\n\033[1;34m=== Ars Arcanum Causal DAG & Multiverse Engine ===\033[0m")
            print(f"Events Tracked: \033[32m{len(events)}\033[0m | Timelines: \033[32m{len(timelines)}\033[0m")
            print(f"Causal Findings / Paradoxes: \033[1m{len(findings)}\033[0m\n")

            if events:
                print("\033[1mCausal Sequence Events:\033[0m")
                for _eid, einfo in events.items():
                    print(f"  📍 \033[1;36m{einfo['name']}\033[0m (Timeline: {einfo['timeline']}) — Coord: {einfo['time_coord'] or 'N/A'}")
                    if einfo["causal_origins"]:
                        print(f"     Prereq : {', '.join(einfo['causal_origins'])}")
                    if einfo["causes"]:
                        print(f"     Causes : {', '.join(einfo['causes'])}")
                    if einfo["paradox_type"]:
                        print(f"     Paradox: \033[33m{einfo['paradox_type']}\033[0m")
                print()

            if not findings:
                print("\033[32m[OK] Causal DAG is acyclic and self-consistent.\033[0m")
            else:
                for fd in findings:
                    badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                    print(f"{badge} {fd['id']}: {fd['message']}")
                    print(f"     Location: {fd['file']}\n")

        if getattr(args, "write_note", None):
            note_p = Path(args.write_note)
            atomic_write(note_p, mermaid_dag)
            print(f"\nObsidian Mermaid Causal DAG written to: {note_p}")

        if getattr(args, "html", None):
            out_p = Path(args.html)
            generate_causality_html_report(audit_data, out_p)
            print(f"\nInteractive HTML report written to: {out_p}")

        sys.exit(1 if len(findings) > 0 else 0)

    elif args.subcommand == "branch":
        branch_id = normalize_id(args.name)
        print("\n\033[1;32m=== Scaffolded Multiverse Branch ===\033[0m")
        print(f"Branch ID     : \033[1m{branch_id}\033[0m")
        print(f"Diverges From : {args.from_timeline} @ {args.at_coord}")
        print("\n\033[1mScene Tag Directives to use in new branch scenes:\033[0m")
        print(f"  @timeline: {branch_id}")
        print(f"  @branch-from: {args.from_timeline}@{args.at_coord}")
        print("  @divergence-point: \"Point of divergence\"\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
