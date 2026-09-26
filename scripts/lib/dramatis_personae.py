#!/usr/bin/env python3
"""
Ars Arcanum — Multi-Volume Dramatis Personae & Universe Cast Matrix
(scripts/lib/dramatis_personae.py)
================================================================================
Zero-dependency cross-volume character cast extractor, continuity auditor,
and publication-ready Dramatis Personae compiler.

Capabilities:
1. Multi-Volume Cast Discovery:
   - Scans World Bible character dossiers (`World/Characters/*.md`).
   - Extracts character names, aliases, allegiances, roles, and status.
   - Cross-references manuscript chapters across all series volumes (`@pov:`,
     `@char:`, `@cast:`, `@character:`, `@death:`).
2. Cast Lifecycle & Continuity Audit:
   - Tracks first appearance, last appearance, and total chapter mentions.
   - Flags CAS-101 (Ghost Character — mentioned in manuscript without lore profile),
     CAS-102 (Post-Mortem Action — deceased character acting after recorded death),
     CAS-103 (Orphan Character — lore profile with zero manuscript appearances).
3. Publication-Ready Compilation:
   - Exports formatted Markdown Dramatis Personae appendices grouped by faction/role.
   - Exports standalone offline CSP-compliant interactive HTML character gallery.
4. CLI Dispatch:
   - `arcanum dramatis-personae [UNIVERSE] [--html OUT] [--markdown OUT] [--json]`
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]
    from frontmatter import parse_yaml_frontmatter  # type: ignore[no-redef]

logger = logging.getLogger("arcanum.dramatis_personae")

_TAG_SPLIT_REGEX = re.compile(r"[,;|]")
_WIKILINK_REGEX = re.compile(r"\[\[(.*?)\]\]")


@dataclass
class AppearanceRecord:
    """Records a single character appearance in a volume/chapter."""

    volume: str
    chapter: str
    is_pov: bool
    is_death_event: bool = False


@dataclass
class CharacterProfile:
    """Comprehensive cross-volume character profile and appearance matrix."""

    id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    category: str = "Major"
    role: str = "Protagonist"
    status: str = "Active"  # Active | Deceased | Missing | Ascended
    faction: str = "Unaffiliated"
    origin: str = "Unknown"
    lore_file: str = ""
    total_appearances: int = 0
    pov_count: int = 0
    first_appearance: str = "Unseen"
    last_appearance: str = "Unseen"
    death_chapter: str = ""
    appearances: list[AppearanceRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_name(name: str) -> str:
    """Normalizes character name for robust case-insensitive matching."""
    cleaned = _WIKILINK_REGEX.sub(r"\1", name)
    cleaned = cleaned.split("|")[-1].strip().lower()
    return re.sub(r"[\s_-]+", " ", cleaned)


def scan_character_profiles(world_dir: Path | None) -> dict[str, CharacterProfile]:
    """Scans world character dossiers and initializes CharacterProfile objects."""
    characters: dict[str, CharacterProfile] = {}
    if not world_dir or not world_dir.exists():
        return characters

    dirs_to_check = [
        world_dir / "Characters",
        world_dir / "00-World-Bible" / "Characters",
        world_dir / "People",
        world_dir / "Dramatis_Personae",
    ]

    seen_paths: set[Path] = set()
    for cdir in dirs_to_check:
        if not cdir.is_dir():
            continue
        for p in sorted(cdir.rglob("*.md")):
            if p in seen_paths or p.name.startswith((".", "_")) or "Template" in p.name:
                continue
            seen_paths.add(p)

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                meta = parse_yaml_frontmatter(content)
                name = meta.get("name") or meta.get("title") or p.stem.replace("_", " ")

                raw_aliases = meta.get("aliases") or []
                if isinstance(raw_aliases, str):
                    raw_aliases = [raw_aliases]
                aliases = [a.strip() for a in raw_aliases if isinstance(a, str) and a.strip()]

                status = str(meta.get("status") or meta.get("Status") or "Active").strip().title()
                role = str(meta.get("role") or meta.get("Role") or "Character").strip().title()
                faction = str(meta.get("faction") or meta.get("allegiance") or meta.get("Faction") or "Unaffiliated").strip()
                origin = str(meta.get("origin") or meta.get("homeland") or "Unknown").strip()

                norm = normalize_name(name)
                char_id = re.sub(r"[^a-z0-9]+", "-", norm).strip("-")

                characters[norm] = CharacterProfile(
                    id=char_id,
                    name=name,
                    aliases=aliases,
                    category="Major" if "major" in role.lower() or "protagonist" in role.lower() else "Supporting",
                    role=role,
                    status=status,
                    faction=faction,
                    origin=origin,
                    lore_file=str(p.relative_to(world_dir)).replace("\\", "/"),
                )
            except (OSError, UnicodeDecodeError) as e:
                logger.debug("Could not parse character file %s: %s", p, e)

    return characters


def cross_reference_manuscripts(
    characters: dict[str, CharacterProfile],
    series_dir: Path | None,
) -> tuple[dict[str, CharacterProfile], list[dict[str, Any]]]:
    """Cross-references characters against all manuscript volume chapter markdown files."""
    if not series_dir or not series_dir.exists():
        return characters, []

    # Map aliases and name variants to canonical normalized character key
    alias_map: dict[str, str] = {}
    for norm_key, prof in characters.items():
        alias_map[norm_key] = norm_key
        for alias in prof.aliases:
            alias_map[normalize_name(alias)] = norm_key

    all_chapters: list[Path] = []
    for p in sorted(series_dir.rglob("*.md")):
        if p.name.startswith((".", "_")) or "Backups" in p.parts or "Front_Matter" in p.parts or "Back_Matter" in p.parts:
            continue
        all_chapters.append(p)

    all_chapters.sort(key=lambda p: str(p.relative_to(series_dir)).replace("\\", "/"))

    untracked_characters: dict[str, list[str]] = {}

    for chapter_path in all_chapters:
        try:
            content = chapter_path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError) as e:
            logger.debug("Could not read chapter for cast analysis %s: %s", chapter_path, e)
            continue

        rel_parts = chapter_path.relative_to(series_dir).parts
        vol_name = rel_parts[0] if len(rel_parts) > 1 else "Volume 1"
        ch_name = chapter_path.name

        meta = parse_yaml_frontmatter(content)
        pov_raw = meta.get("pov") or meta.get("POV") or ""
        pov_norm = normalize_name(pov_raw) if pov_raw else ""

        # Scan for tagged character mentions
        present_norms: set[str] = set()
        if pov_norm:
            present_norms.add(pov_norm)

        # Frontmatter character lists
        char_list = meta.get("characters") or meta.get("chars") or meta.get("cast") or []
        if isinstance(char_list, str):
            char_list = _TAG_SPLIT_REGEX.split(char_list)
        for c in char_list:
            if isinstance(c, str) and c.strip():
                present_norms.add(normalize_name(c))

        # Inline @char: @cast: @pov: @death: tags
        death_events: set[str] = set()
        for line in content.splitlines():
            s = line.strip()
            if s.startswith(("@char:", "@cast:", "@character:")):
                val = s.split(":", 1)[1]
                for item in _TAG_SPLIT_REGEX.split(val):
                    if item.strip():
                        present_norms.add(normalize_name(item))
            elif s.startswith("@pov:"):
                val = s.split(":", 1)[1].strip()
                if val:
                    present_norms.add(normalize_name(val))
                    pov_norm = normalize_name(val)
            elif s.startswith("@death:"):
                val = s.split(":", 1)[1].strip()
                if val:
                    norm_val = normalize_name(val)
                    death_events.add(norm_val)
                    present_norms.add(norm_val)

        # Record appearances
        for norm_candidate in present_norms:
            canonical_key = alias_map.get(norm_candidate)
            if canonical_key and canonical_key in characters:
                prof = characters[canonical_key]
                is_pov = (norm_candidate == pov_norm)
                is_death = (norm_candidate in death_events)
                prof.appearances.append(
                    AppearanceRecord(
                        volume=vol_name,
                        chapter=ch_name,
                        is_pov=is_pov,
                        is_death_event=is_death,
                    )
                )
                prof.total_appearances += 1
                if is_pov:
                    prof.pov_count += 1
                loc_label = f"{vol_name} / {ch_name}"
                if prof.first_appearance == "Unseen":
                    prof.first_appearance = loc_label
                prof.last_appearance = loc_label
                if is_death:
                    prof.status = "Deceased"
                    prof.death_chapter = loc_label
            else:
                if norm_candidate not in untracked_characters:
                    untracked_characters[norm_candidate] = []
                untracked_characters[norm_candidate].append(f"{vol_name}/{ch_name}")

    # Generate continuity audit findings
    findings = audit_cast_continuity(list(characters.values()), untracked_characters)

    return characters, findings


def audit_cast_continuity(
    characters: list[CharacterProfile],
    untracked_mentions: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Audits character lifecycle continuity and flags CAS-101, CAS-102, CAS-103."""
    findings: list[dict[str, Any]] = []

    # CAS-101: Ghost Characters (mentioned in manuscript without character dossier)
    for unk_name, locations in untracked_mentions.items():
        if len(unk_name) > 2 and unk_name not in ("scene", "none", "unknown", "all"):
            findings.append({
                "id": "CAS-101",
                "severity": "WARNING",
                "character": unk_name.title(),
                "message": (
                    f"Ghost Character: '{unk_name.title()}' appears in {len(locations)} chapters "
                    f"({', '.join(locations[:3])}) but has no dossier in World/Characters/."
                ),
            })

    for prof in characters:
        # CAS-103: Orphan Characters (dossier created but 0 manuscript appearances)
        if prof.total_appearances == 0:
            findings.append({
                "id": "CAS-103",
                "severity": "INFO",
                "character": prof.name,
                "message": f"Orphan Lore Character: '{prof.name}' is defined in {prof.lore_file} but has 0 manuscript appearances.",
            })

        # CAS-102: Post-Mortem Action (acts after death event)
        if prof.death_chapter:
            saw_death = False
            for app in prof.appearances:
                if app.is_death_event:
                    saw_death = True
                    continue
                if saw_death:
                    findings.append({
                        "id": "CAS-102",
                        "severity": "ERROR",
                        "character": prof.name,
                        "message": (
                            f"Post-Mortem Action: Character '{prof.name}' died in {prof.death_chapter} "
                            f"but has subsequent appearance in {app.volume}/{app.chapter}."
                        ),
                    })
                    break

    return findings


def generate_dramatis_personae_markdown(
    characters: list[CharacterProfile],
    title: str = "Dramatis Personae",
) -> str:
    """Compiles a publication-ready Markdown Dramatis Personae appendix."""
    lines = [
        f"# {title}",
        "",
        "> Master character cast register, allegiances, and appearance index across the series.",
        "",
        "---",
        "",
    ]

    # Group by faction
    by_faction: dict[str, list[CharacterProfile]] = {}
    for c in characters:
        by_faction.setdefault(c.faction, []).append(c)

    for faction_name in sorted(by_faction.keys()):
        lines.append(f"## {faction_name}")
        lines.append("")
        lines.append("| Character | Role | Status | Origin | First Seen | POV |")
        lines.append("|:---|:---|:---|:---|:---|:---:|")

        for c in sorted(by_faction[faction_name], key=lambda x: x.name):
            status_icon = "🟢" if c.status == "Active" else ("🔴" if c.status == "Deceased" else "🟡")
            pov_icon = "✓" if c.pov_count > 0 else "—"
            lines.append(
                f"| **{c.name}** | {c.role} | {status_icon} {c.status} | {c.origin} | {c.first_appearance} | {pov_icon} |"
            )
        lines.append("")

    return "\n".join(lines)


def generate_dramatis_personae_html(
    data: dict[str, Any],
    output_path: Path,
) -> None:
    """Generates standalone offline CSP-compliant HTML character gallery."""
    characters: list[CharacterProfile] = data.get("characters", [])
    findings: list[dict[str, Any]] = data.get("findings", [])
    universe_name = data.get("universe", "Sovereign Universe")

    cards_html = []
    for c in sorted(characters, key=lambda x: x.name):
        badge_cls = "badge-active" if c.status == "Active" else ("badge-deceased" if c.status == "Deceased" else "badge-missing")
        aliases_str = f"<small class='aliases'>AKA: {', '.join(c.aliases)}</small>" if c.aliases else ""
        cards_html.append(f"""
        <div class="card character-card">
            <div class="card-header">
                <div>
                    <h3>{html.escape(c.name)}</h3>
                    {aliases_str}
                </div>
                <span class="badge {badge_cls}">{html.escape(c.status)}</span>
            </div>
            <div class="meta-row">
                <span class="pill">🏛️ {html.escape(c.faction)}</span>
                <span class="pill">🎭 {html.escape(c.role)}</span>
                <span class="pill">🌍 {html.escape(c.origin)}</span>
            </div>
            <div class="appearances">
                <strong>Appearances:</strong> {c.total_appearances} chapters ({c.pov_count} POV)<br/>
                <small>First: {html.escape(c.first_appearance)} · Last: {html.escape(c.last_appearance)}</small>
            </div>
        </div>
        """)

    findings_html = []
    for f in findings:
        f_cls = "finding-error" if f.get("severity") == "ERROR" else "finding-warn"
        findings_html.append(f"""
        <div class="finding {f_cls}">
            <strong>[{html.escape(f.get('severity', ''))}] {html.escape(f.get('id', ''))}</strong>: {html.escape(f.get('message', ''))}
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ars Arcanum · Dramatis Personae ({html.escape(universe_name)})</title>
  <style>
    :root {{
      --bg: #0f111a;
      --card-bg: #1a1d2d;
      --border: #2c3249;
      --accent: #8b5cf6;
      --text: #f1f5f9;
      --muted: #94a3b8;
      --active: #10b981;
      --deceased: #ef4444;
      --warn: #f59e0b;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 2rem;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ color: var(--accent); margin-bottom: 0.25rem; }}
    .subtitle {{ color: var(--muted); margin-bottom: 2rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }}
    .card-header h3 {{ margin: 0; font-size: 1.2rem; }}
    .aliases {{ color: var(--muted); display: block; margin-top: 2px; }}
    .meta-row {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.75rem; }}
    .pill {{ background: #24293e; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: var(--text); }}
    .badge {{ padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: bold; }}
    .badge-active {{ background: #064e3b; color: #34d399; }}
    .badge-deceased {{ background: #450a0a; color: #f87171; }}
    .badge-missing {{ background: #451a03; color: #fbbf24; }}
    .appearances {{ font-size: 0.85rem; border-top: 1px solid var(--border); padding-top: 0.5rem; color: var(--muted); }}
    .finding {{ padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.75rem; font-size: 0.9rem; }}
    .finding-error {{ background: #450a0a; border-left: 4px solid var(--deceased); }}
    .finding-warn {{ background: #451a03; border-left: 4px solid var(--warn); }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🎭 Dramatis Personae & Cast Matrix</h1>
    <div class="subtitle">Universe: {html.escape(universe_name)} · {len(characters)} Characters Tracked</div>

    {'<h2>Continuity Diagnostics</h2>' + ''.join(findings_html) if findings_html else ''}

    <h2>Character Roster</h2>
    <div class="grid">
      {''.join(cards_html) if cards_html else '<p>No character dossiers discovered.</p>'}
    </div>
  </div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Multi-Volume Dramatis Personae & Universe Cast Matrix")
    parser.add_argument("target", nargs="?", default=".", help="Universe or Cosmos directory path")
    parser.add_argument("--html", type=Path, default=None, help="Export interactive HTML character gallery")
    parser.add_argument("--markdown", type=Path, default=None, help="Export formatted Markdown Dramatis Personae appendix")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON cast matrix")

    args = parser.parse_args(argv)
    root = Path(args.target).resolve()

    world_dir = root / "World" if (root / "World").exists() else root
    series_dir = root / "Manuscripts" if (root / "Manuscripts").exists() else (root / "Manuscript" if (root / "Manuscript").exists() else root)

    characters_map = scan_character_profiles(world_dir)
    characters_map, findings = cross_reference_manuscripts(characters_map, series_dir)
    char_list = list(characters_map.values())

    data = {
        "universe": root.name,
        "total_characters": len(char_list),
        "characters": [c.to_dict() for c in char_list],
        "findings": findings,
    }

    if args.markdown:
        md_text = generate_dramatis_personae_markdown(char_list, title=f"Dramatis Personae — {root.name}")
        atomic_write(args.markdown, md_text)
        print(f"Markdown Dramatis Personae exported to: {args.markdown}")

    if args.html:
        generate_dramatis_personae_html({"universe": root.name, "characters": char_list, "findings": findings}, args.html)
        print(f"HTML Character Gallery exported to: {args.html}")

    if args.json:
        print(json.dumps(data, indent=2))
    elif not args.markdown and not args.html:
        print("=" * 80)
        print(f"🎭 Ars Arcanum — Dramatis Personae Cast Matrix ({root.name})")
        print("=" * 80)
        print(f"Total Characters: {len(char_list)}")
        print(f"Findings:         {len(findings)}")
        print("-" * 80)
        for c in char_list:
            print(f"  {c.name:<24} | {c.faction:<18} | {c.status:<10} | {c.total_appearances} ch ({c.pov_count} POV)")
        print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())


