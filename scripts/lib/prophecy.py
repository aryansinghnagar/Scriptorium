#!/usr/bin/env python3
"""
Ars Arcanum In-World Prophecy Resolution Matrix & Arcane Inscription Engine (scripts/lib/prophecy.py)
=====================================================================================================
Zero-dependency, offline prophecy tracking system that scans World Bible `Cosmology/Prophecies/*.md`
and cross-validates manuscript chapters for prophecy clause resolutions, subversions, and broken oaths.

Capabilities:
1. Prophecy Lore Extraction:
   - Scans `Cosmology/Prophecies/*.md` (or `Prophecies/*.md`).
   - Extracts oracle source, chosen entities, status (`unfulfilled`, `partially_fulfilled`, `fulfilled`, `subverted`, `broken`),
     and predictive clauses / conditions.
2. Manuscript Resolution Cross-Validation:
   - Scans manuscript draft chapters for clause resolutions, fulfillment tokens, and `@prophecy:` scene tags.
   - Detects:
     * PRP-101: Orphan Prophecy (Prophecy exists in lore but is unreferenced / forgotten in manuscript).
     * PRP-102: Dead Chosen One / Prerequisite Contradiction (Prophecy target dies before fulfillment condition is met).
     * PRP-103: Resolution Status Discrepancy (World Bible marks prophecy fulfilled without manuscript evidence).
3. Visualizers:
   - Obsidian Mermaid.js Prophecy Lifecycle & State Machine diagram (`--write-note`).
   - Standalone interactive HTML report (`--html`).

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

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.prophecy")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")
TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")


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


def extract_prophecies(world_dir: Path) -> dict:
    """Scans Cosmology/Prophecies/ and Prophecies/ directories."""
    prophecies = {}
    dirs_to_check = [
        world_dir / "Cosmology" / "Prophecies",
        world_dir / "00-World-Bible" / "Cosmology" / "Prophecies",
        world_dir / "Prophecies",
        world_dir / "00-World-Bible" / "Prophecies",
        world_dir / "Cosmology",
    ]

    seen_files = set()
    for pdir in dirs_to_check:
        if not pdir.is_dir():
            continue
        for md_file in sorted(pdir.rglob("*.md")):
            if md_file in seen_files or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen_files.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                ptype = fm.get("type", "").lower()
                if "prophecy" not in ptype and "prophecy" not in str(md_file).lower() and "oracle" not in ptype:
                    continue

                name = fm.get("name") or md_file.stem.replace("_", " ")
                oracle = clean_link_name(fm.get("source") or fm.get("oracle") or "Ancient Oracle")
                target = clean_link_name(fm.get("target_entity") or fm.get("chosen_one") or "The Realm")
                status = str(fm.get("status") or "unfulfilled").lower()
                date_uttered = str(fm.get("date_uttered") or fm.get("era") or "")

                raw_clauses = fm.get("clauses") or fm.get("conditions") or []
                if isinstance(raw_clauses, str):
                    raw_clauses = [raw_clauses]
                clauses = [str(c).strip().strip("\"'") for c in raw_clauses if str(c).strip()]

                prophecies[name] = {
                    "name": name,
                    "file": str(md_file.relative_to(world_dir)),
                    "oracle": oracle,
                    "target_entity": target,
                    "status": status,
                    "date_uttered": date_uttered,
                    "clauses": clauses,
                    "resolution_criteria": fm.get("resolution_criteria", ""),
                }
            except Exception as e:
                logger.warning("Failed to parse prophecy %s: %s", md_file, e)

    return prophecies


def audit_prophecy_resolution(prophecies: dict, manuscript_dir: Path = None, world_dir: Path = None) -> list:
    """Cross-validates prophecy clauses, character status, and resolution status against manuscript chapters."""
    findings = []

    # Check for deceased target entities / chosen ones (PRP-102)
    dead_entities = set()
    if world_dir and world_dir.is_dir():
        for char_dir in (world_dir / "Characters", world_dir / "00-World-Bible" / "Characters"):
            if not char_dir.is_dir():
                continue
            for md_file in sorted(char_dir.rglob("*.md")):
                if md_file.name.startswith(".") or "Template" in md_file.name:
                    continue
                try:
                    c_txt = md_file.read_text(encoding="utf-8", errors="ignore")
                    c_fm = parse_yaml_frontmatter(c_txt)
                    c_name = c_fm.get("name") or md_file.stem.replace("_", " ")
                    c_status = str(c_fm.get("status", "")).lower()
                    if c_status in ("dead", "deceased", "killed") or c_fm.get("death_year") or c_fm.get("death_date") or c_fm.get("died"):
                        dead_entities.add(normalize_name(c_name))
                except Exception:
                    pass

    # If manuscript provided, extract scene texts and @prophecy: tags
    ms_text_corpus = ""
    scene_prophecy_tags = {}
    if manuscript_dir and manuscript_dir.is_dir():
        for md_file in sorted(manuscript_dir.rglob("*.md")):
            if md_file.name.startswith(".") or "Front_Matter" in md_file.parts or "Back_Matter" in md_file.parts:
                continue
            try:
                txt = md_file.read_text(encoding="utf-8", errors="ignore")
                ms_text_corpus += " " + txt
                rel_p = str(md_file.relative_to(manuscript_dir))
                for line in txt.splitlines():
                    m = TAG_REGEX.match(line.strip())
                    if m and m.group(1).lower() in ("prophecy", "prophecy-fulfilled", "prophecy-subverted"):
                        tag_val = m.group(2).strip()
                        if tag_val not in scene_prophecy_tags:
                            scene_prophecy_tags[tag_val] = []
                        scene_prophecy_tags[tag_val].append(rel_p)
            except Exception as e:
                logger.warning("Failed to read manuscript scene %s: %s", md_file, e)

    ms_corpus_lower = ms_text_corpus.lower()

    for pname, pinfo in prophecies.items():
        pname_norm = normalize_name(pname)
        status = pinfo["status"]
        clauses = pinfo["clauses"]
        target = pinfo.get("target_entity", "")
        target_norm = normalize_name(target)

        # 1. Dead Chosen One / Prerequisite Contradiction (PRP-102)
        if target_norm in dead_entities and status in ("unfulfilled", "active", "partially_fulfilled"):
            findings.append({
                "id": "PRP-102",
                "severity": "ERROR",
                "prophecy": pname,
                "target": target,
                "message": f"Dead Chosen One Contradiction: Target entity '{target}' of unfulfilled prophecy '{pname}' is marked deceased in World Bible lore.",
                "file": pinfo["file"],
            })

        # Check if prophecy is mentioned in manuscript
        in_manuscript = (pname_norm in ms_corpus_lower) or (any(normalize_name(pname) in normalize_name(tag) for tag in scene_prophecy_tags))

        # 2. Orphan Prophecy (PRP-101)
        if manuscript_dir and manuscript_dir.is_dir() and not in_manuscript:
            findings.append({
                "id": "PRP-101",
                "severity": "WARNING",
                "prophecy": pname,
                "message": f"Orphan Prophecy: Lore prophecy '{pname}' is never referenced or fulfilled anywhere in the manuscript.",
                "file": pinfo["file"],
            })

        # 3. Status Discrepancy (PRP-103)
        if manuscript_dir and manuscript_dir.is_dir() and status in ("fulfilled", "subverted"):
            has_tag = any(pname_norm in normalize_name(tag) for tag in scene_prophecy_tags)
            if not has_tag and "fulfilled" not in ms_corpus_lower and "prophecy" not in ms_corpus_lower:
                findings.append({
                    "id": "PRP-103",
                    "severity": "WARNING",
                    "prophecy": pname,
                    "message": f"Resolution Status Discrepancy: Prophecy '{pname}' is marked '{status}' in lore, but no scene resolution tag was found in manuscript.",
                    "file": pinfo["file"],
                })

    return findings


def generate_prophecy_mermaid(prophecies: dict) -> str:
    """Generates Obsidian-ready Mermaid state/lifecycle diagram."""
    lines = ["```mermaid", "stateDiagram-v2"]
    lines.append("    %% Prophecy Lifecycle State Matrix")
    for pname, pinfo in sorted(prophecies.items()):
        safe_name = pname.replace('"', "'").replace(" ", "_")
        status = pinfo["status"].upper()
        lines.append(f"    [*] --> {safe_name}_Uttered : Uttered by {pinfo['oracle']}")
        if "fulfilled" in pinfo["status"]:
            lines.append(f"    {safe_name}_Uttered --> {safe_name}_Fulfilled : Criteria Met")
            lines.append(f"    {safe_name}_Fulfilled --> [*]")
        elif "subverted" in pinfo["status"]:
            lines.append(f"    {safe_name}_Uttered --> {safe_name}_Subverted : Irony / Subversion")
            lines.append(f"    {safe_name}_Subverted --> [*]")
        elif "broken" in pinfo["status"]:
            lines.append(f"    {safe_name}_Uttered --> {safe_name}_Broken : Failed Precondition")
            lines.append(f"    {safe_name}_Broken --> [*]")
        else:
            lines.append(f"    {safe_name}_Uttered --> {safe_name}_Active : In Progress")
    lines.append("```")
    return "\n".join(lines)


def generate_prophecy_html_report(audit_data: dict, output_path: Path):
    """Generates standalone HTML report for In-World Prophecies."""
    prophecies = audit_data.get("prophecies", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")

    prophecy_cards = []
    for pn, p in prophecies.items():
        clauses_html = "".join([f"<li>{html.escape(c)}</li>" for c in p["clauses"]]) if p["clauses"] else "<li>No specific clauses defined.</li>"
        status_col = "#34d399" if "fulfilled" in p["status"] else ("#f59e0b" if "partially" in p["status"] else ("#f43f5e" if "broken" in p["status"] else "#38bdf8"))
        prophecy_cards.append(f"""
        <div class="card">
            <h3 style="margin-top:0;">📜 {html.escape(pn)}</h3>
            <p><strong>Oracle:</strong> {html.escape(p['oracle'])} | <strong>Target:</strong> {html.escape(p['target_entity'])}</p>
            <p><strong>Status:</strong> <span style="color: {status_col}; font-weight:bold; text-transform:uppercase;">{html.escape(p['status'])}</span></p>
            <p><strong>Prophetic Clauses:</strong></p>
            <ul>{clauses_html}</ul>
        </div>
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

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #34d399;'>✓ All lore prophecies are actively tracked and resolved consistently.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Prophecy Resolution Matrix ({html.escape(world_name)})</title>
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
  .container {{ max-width: 1000px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
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
  ul {{ padding-left: 1.2rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>📜 Ars Arcanum Prophecy Resolution Matrix</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong> | Total Prophecies: <strong>{len(prophecies)}</strong></p>

  <div class="card">
    <h2>Prophecy Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <h2>Registered In-World Prophecies</h2>
  {"".join(prophecy_cards)}
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
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Prophecy Resolution Matrix")
    subparsers = parser.add_subparsers(dest="subcommand", help="Prophecy subcommands")

    p_check = subparsers.add_parser("check", help="Run prophecy clause fulfillment and consistency audit")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_check.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_check.add_argument("--html", help="Path to export standalone HTML report")
    p_check.add_argument("--write-note", help="Export Mermaid.js Prophecy Lifecycle note")

    p_rep = subparsers.add_parser("report", help="Display prophecy roster and fulfillment report")
    p_rep.add_argument("world", nargs="?", help="World Bible lore directory")
    p_rep.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_rep.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_rep.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_rep.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rep.add_argument("--html", help="Path to export standalone HTML report")
    p_rep.add_argument("--write-note", help="Export Mermaid.js Prophecy Lifecycle note")

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
    raw_ms = getattr(args, "manuscript", None) or getattr(args, "manuscript_pos", None)
    ms_dir_str = resolve_manuscript_dir(raw_ms) if raw_ms else None
    ms_path = Path(ms_dir_str) if ms_dir_str else None

    prophecies = extract_prophecies(world_path)
    findings = audit_prophecy_resolution(prophecies, ms_path, world_path)
    mermaid_diag = generate_prophecy_mermaid(prophecies)

    audit_data = {
        "world": world_path.name,
        "manuscript": ms_path.name if ms_path else None,
        "prophecies_count": len(prophecies),
        "findings_count": len(findings),
        "prophecies": prophecies,
        "findings": findings,
        "mermaid": mermaid_diag,
    }

    if getattr(args, "json", False):
        print(json.dumps(audit_data, indent=2))
    else:
        print(f"\n\033[1;35m=== Ars Arcanum Prophecy Resolution Matrix ===\033[0m")
        print(f"World: \033[1m{world_path.name}\033[0m | Manuscript: \033[1m{ms_path.name if ms_path else 'N/A'}\033[0m")
        print(f"Prophecies Tracked: \033[32m{len(prophecies)}\033[0m | Findings: \033[1m{len(findings)}\033[0m\n")

        if prophecies:
            print("\033[1mIn-World Prophecies & Fulfillment Status:\033[0m")
            for pn, pinfo in prophecies.items():
                print(f"  📜 \033[1;36m{pn}\033[0m [{pinfo['status'].upper()}] — Oracle: {pinfo['oracle']} (Target: {pinfo['target_entity']})")
                for c in pinfo["clauses"]:
                    print(f"     • \"{c}\"")
            print()

        if not findings:
            print("\033[32m[OK] Prophecy resolution tracking is consistent with lore and manuscript.\033[0m")
        else:
            for fd in findings:
                badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                print(f"{badge} {fd['id']}: {fd['message']}")
                print(f"     File: {fd['file']}\n")

    if getattr(args, "write_note", None):
        note_p = Path(args.write_note)
        note_p.write_text(mermaid_diag, encoding="utf-8")
        print(f"\nObsidian Mermaid Prophecy Lifecycle written to: {note_p}")

    if getattr(args, "html", None):
        out_p = Path(args.html)
        generate_prophecy_html_report(audit_data, out_p)
        print(f"\nInteractive HTML report written to: {out_p}")

    sys.exit(1 if len(findings) > 0 else 0)


if __name__ == "__main__":
    main()
