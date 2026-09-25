#!/usr/bin/env python3
"""
Ars Arcanum Back-Matter Concordance & Dramatis Personae Engine (scripts/lib/concordance.py)
========================================================================================
Parses character dossiers, factions, artifacts, bestiary, magic systems, and linguistics
from the World Bible (00-World-Bible/) and generates publication-ready back-matter:
- 01_Dramatis_Personae.md
- 02_Glossary_and_Concordance.md
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, validate_volume_name
except ImportError:
    from _bootstrap import atomic_write, validate_volume_name


FRONTMATTER_DELIM = "---"


def clean_wikilinks(text: Any) -> str:
    if not text:
        return ""
    text = re.sub(r'\[\[(?:[^\|\]]+\|)?([^\]]+)\]\]', r'\1', str(text))
    return text.strip()


def parse_frontmatter_and_body(file_path: Path) -> tuple[dict[str, Any], str]:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}, ""
    lines = content.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, content
    fm: dict[str, Any] = {}
    i = 1
    n = len(lines)
    while i < n and lines[i].strip() != FRONTMATTER_DELIM:
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                items = []
                j = i + 1
                while j < n and re.match(r"^[ \t]+-[ \t]+", lines[j]):
                    items.append(re.sub(r"^[ \t]+-[ \t]+", "", lines[j]).strip().strip('"').strip("'"))
                    j += 1
                if items:
                    fm[key] = items
                    i = j
                    continue
                fm[key] = ""
                i += 1
                continue
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = val.strip('"').strip("'")
            i += 1
            continue
        i += 1
    body = "\n".join(lines[i+1:]) if i < n else ""
    return fm, body


def extract_summary_or_quote(body: str) -> str:
    lines = body.strip().splitlines()
    summary_lines = []
    in_summary = False
    quote = ""
    for line in lines:
        s = line.strip()
        if s.startswith(">") and not quote:
            quote = clean_wikilinks(s.lstrip(">").strip().strip('*').strip('"'))
        if re.match(r"^##\s+.*(Summary|Overview|Description)", s, re.IGNORECASE):
            in_summary = True
            continue
        elif in_summary:
            if s.startswith("##") or s.startswith("---"):
                break
            if s and not s.startswith("- **") and not s.startswith(">"):
                summary_lines.append(s)
    if summary_lines:
        return clean_wikilinks(" ".join(summary_lines))
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">") and not s.startswith("---") and not s.startswith("-") and not s.startswith("|"):
            return clean_wikilinks(s)
    return quote


def is_template(path: Path, fm: dict[str, Any]) -> bool:
    if "Template" in path.name or "template" in path.name or "Templates" in path.parts:
        return True
    name = str(fm.get("name", ""))
    return "<%" in name


def build_dramatis_personae_markdown(characters: list[dict[str, Any]]) -> str:
    dp_md = [
        "# Dramatis Personae\n",
        "A comprehensive register of key individuals, allies, rivals, and figures encountered throughout the narrative.\n"
    ]

    def is_antagonist(c: dict[str, Any]) -> bool:
        return bool(re.search(r'antagonist|villain|rival|nemesis', c.get('role', ''), re.IGNORECASE))

    def is_protagonist(c: dict[str, Any]) -> bool:
        return bool(re.search(r'protagonist|major|lead', c.get('role', ''), re.IGNORECASE))

    antagonists = [c for c in characters if is_antagonist(c)]
    protagonists = [c for c in characters if is_protagonist(c) and not is_antagonist(c)]
    supporting = [c for c in characters if not is_protagonist(c) and not is_antagonist(c)]

    def format_character_block(c: dict[str, Any]) -> str:
        lines = []
        alias_str = f" (*{', '.join(c['aliases'])}*)" if c.get('aliases') else ""
        meta_parts = []
        role = c.get('role', '')
        if role and role.lower() not in ("protagonist", "antagonist", "supporting"):
            meta_parts.append(role)
        species = c.get('species', '')
        if species and species.lower() != "human":
            meta_parts.append(species)
        occupation = c.get('occupation', '')
        if occupation:
            meta_parts.append(occupation)
        faction = c.get('faction', '')
        if faction:
            meta_parts.append(f"Affiliation: {faction}")
        origin = c.get('origin', '')
        if origin:
            meta_parts.append(f"Origin: {origin}")
        status = c.get('status', '')
        if status and status.lower() not in ("alive", "active", "unknown", ""):
            meta_parts.append(f"Status: {status}")
        meta_str = f" — *{', '.join(meta_parts)}*" if meta_parts else ""
        lines.append(f"- **{c['name']}**{alias_str}{meta_str}")
        if c.get('summary'):
            lines.append(f"  {c['summary']}")
        return "\n".join(lines)

    if protagonists:
        dp_md.append("## Protagonists & Major Figures\n")
        for c in sorted(protagonists, key=lambda x: str(x['name'])):
            dp_md.append(format_character_block(c) + "\n")

    if antagonists:
        dp_md.append("## Antagonists & Rivals\n")
        for c in sorted(antagonists, key=lambda x: str(x['name'])):
            dp_md.append(format_character_block(c) + "\n")

    if supporting:
        dp_md.append("## Supporting Personae & Affiliations\n")
        for c in sorted(supporting, key=lambda x: str(x['name'])):
            dp_md.append(format_character_block(c) + "\n")

    if not characters:
        dp_md.append("*No character dossiers registered in the World Bible.*\n")

    return "\n".join(dp_md).strip() + "\n"


def build_glossary_markdown(
    factions: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    magic_systems: list[dict[str, Any]],
    creatures: list[dict[str, Any]],
    languages: list[dict[str, Any]],
) -> str:
    gc_md = [
        "# Glossary & Concordance\n",
        "An encyclopedic concordance of world terminology, factions, legendary relics, magic systems, bestiary creatures, and linguistics.\n"
    ]

    if factions:
        gc_md.append("## Factions & Sovereign Powers\n")
        for f in sorted(factions, key=lambda x: str(x['name'])):
            details = []
            if f.get('type'):
                details.append(f['type'])
            if f.get('leader'):
                details.append(f"Led by {f['leader']}")
            if f.get('headquarters'):
                details.append(f"Seat: {f['headquarters']}")
            d_str = f" (*{', '.join(details)}*)" if details else ""
            m_str = f" Motto: *\"{f['motto']}\"*." if f.get('motto') else ""
            gc_md.append(f"- **{f['name']}**{d_str}:{m_str}")
            if f.get('summary'):
                gc_md.append(f"  {f['summary']}\n")
            else:
                gc_md.append("")

    if artifacts:
        gc_md.append("## Legendary Artifacts & Relics\n")
        for a in sorted(artifacts, key=lambda x: str(x['name'])):
            details = []
            if a.get('type'):
                details.append(a['type'])
            if a.get('rarity'):
                details.append(a['rarity'])
            if a.get('bearer'):
                details.append(f"Bearer: {a['bearer']}")
            if a.get('creator'):
                details.append(f"Forged by {a['creator']}")
            d_str = f" (*{', '.join(details)}*)" if details else ""
            gc_md.append(f"- **{a['name']}**{d_str}:")
            if a.get('summary'):
                gc_md.append(f"  {a['summary']}\n")
            else:
                gc_md.append("")

    if magic_systems:
        gc_md.append("## Magic & Arcane Disciplines\n")
        for m in sorted(magic_systems, key=lambda x: str(x['name'])):
            details = []
            if m.get('classification'):
                details.append(m['classification'])
            if m.get('source'):
                details.append(f"Source: {m['source']}")
            if m.get('danger'):
                details.append(f"Cost: {m['danger']}")
            d_str = f" (*{', '.join(details)}*)" if details else ""
            gc_md.append(f"- **{m['name']}**{d_str}:")
            if m.get('summary'):
                gc_md.append(f"  {m['summary']}\n")
            else:
                gc_md.append("")

    if creatures:
        gc_md.append("## Bestiary & Ecological Hazards\n")
        for cr in sorted(creatures, key=lambda x: str(x['name'])):
            details = []
            if cr.get('classification'):
                details.append(cr['classification'])
            if cr.get('threat'):
                details.append(f"Threat: {cr['threat']}")
            if cr.get('habitat'):
                details.append(f"Habitat: {cr['habitat']}")
            d_str = f" (*{', '.join(details)}*)" if details else ""
            gc_md.append(f"- **{cr['name']}**{d_str}:")
            if cr.get('summary'):
                gc_md.append(f"  {cr['summary']}\n")
            else:
                gc_md.append("")

    if languages:
        gc_md.append("## Linguistics & Conlang Lexicon\n")
        for lang in sorted(languages, key=lambda x: str(x['name'])):
            meta = []
            if lang.get('family'):
                meta.append(f"Family: {lang['family']}")
            if lang.get('spoken_by'):
                meta.append(f"Spoken by: {lang['spoken_by']}")
            if lang.get('status'):
                meta.append(f"Status: {lang['status']}")
            if lang.get('writing'):
                meta.append(f"Script: {lang['writing']}")
            gc_md.append(f"### {lang['name']}\n")
            if meta:
                gc_md.append(f"*{' | '.join(meta)}*\n")
            if lang.get('summary'):
                gc_md.append(f"{lang['summary']}\n")
            if lang.get('lexicon'):
                gc_md.append("| Term | Part of Speech | Definition / Cultural Meaning |")
                gc_md.append("| :--- | :--- | :--- |")
                for term in lang['lexicon']:
                    gc_md.append(f"| *{term['word']}* | {term['pos']} | {term['definition']} |")
                gc_md.append("")

    if not (factions or artifacts or magic_systems or creatures or languages):
        gc_md.append("*No specialized concordance lore registered in the World Bible.*\n")

    return "\n".join(gc_md).strip() + "\n"


def generate_concordance(
    bible_dir: Path,
    ms_dir: Path,
    target_book: str = "all",
) -> dict[str, Any]:
    """Parse World Bible lore and compile back-matter files for target manuscript volume(s)."""
    bible_path = Path(bible_dir).resolve()
    ms_path = Path(ms_dir).resolve()

    if not bible_path.is_dir():
        raise FileNotFoundError(f"World Bible directory not found: {bible_dir}")

    # 1. Characters
    characters: list[dict[str, Any]] = []
    char_dir = bible_path / "Characters"
    if char_dir.is_dir():
        for f in sorted(char_dir.rglob("*.md")):
            if f.is_file():
                fm, body = parse_frontmatter_and_body(f)
                if is_template(f, fm):
                    continue
                name = fm.get("name") or f.stem
                aliases = fm.get("aliases", [])
                if isinstance(aliases, str):
                    aliases = [a.strip() for a in aliases.split(",") if a.strip()] if aliases else []
                characters.append({
                    "name": name,
                    "aliases": [clean_wikilinks(a) for a in aliases if a],
                    "role": str(fm.get("role", "Supporting")).strip(),
                    "status": str(fm.get("status", "")).strip(),
                    "faction": clean_wikilinks(fm.get("faction", "")),
                    "origin": clean_wikilinks(fm.get("origin", "")),
                    "species": str(fm.get("species_race", "")).strip(),
                    "occupation": str(fm.get("occupation", "")).strip(),
                    "summary": extract_summary_or_quote(body)
                })

    # 2. Factions
    factions: list[dict[str, Any]] = []
    fac_dir = bible_path / "Factions"
    if fac_dir.is_dir():
        for f in sorted(fac_dir.rglob("*.md")):
            if f.is_file():
                fm, body = parse_frontmatter_and_body(f)
                if is_template(f, fm):
                    continue
                factions.append({
                    "name": fm.get("name") or f.stem,
                    "type": str(fm.get("faction_type", "Faction")).strip(),
                    "leader": clean_wikilinks(fm.get("leader", "")),
                    "headquarters": clean_wikilinks(fm.get("headquarters", "")),
                    "motto": str(fm.get("motto", "")).strip(),
                    "summary": extract_summary_or_quote(body)
                })

    # 3. Artifacts
    artifacts: list[dict[str, Any]] = []
    art_dir = bible_path / "Artifacts"
    if art_dir.is_dir():
        for f in sorted(art_dir.rglob("*.md")):
            if f.is_file():
                fm, body = parse_frontmatter_and_body(f)
                if is_template(f, fm):
                    continue
                artifacts.append({
                    "name": fm.get("name") or f.stem,
                    "type": str(fm.get("artifact_type", "Relic")).strip(),
                    "rarity": str(fm.get("rarity", "")).strip(),
                    "bearer": clean_wikilinks(fm.get("current_bearer", "")),
                    "creator": clean_wikilinks(fm.get("creator", "")),
                    "summary": extract_summary_or_quote(body)
                })

    # 4. Bestiary
    creatures: list[dict[str, Any]] = []
    best_dir = bible_path / "Bestiary"
    if best_dir.is_dir():
        for f in sorted(best_dir.rglob("*.md")):
            if f.is_file():
                fm, body = parse_frontmatter_and_body(f)
                if is_template(f, fm):
                    continue
                creatures.append({
                    "name": fm.get("name") or f.stem,
                    "classification": str(fm.get("classification", "Creature")).strip(),
                    "threat": str(fm.get("threat_level", "")).strip(),
                    "habitat": clean_wikilinks(fm.get("habitat", "")),
                    "summary": extract_summary_or_quote(body)
                })

    # 5. Magic Systems
    magic_systems: list[dict[str, Any]] = []
    magic_dir = bible_path / "Magic-Technology"
    if magic_dir.is_dir():
        for f in sorted(magic_dir.rglob("*.md")):
            if f.is_file():
                fm, body = parse_frontmatter_and_body(f)
                if is_template(f, fm):
                    continue
                magic_systems.append({
                    "name": fm.get("name") or f.stem,
                    "classification": str(fm.get("classification", "Magic / Technology")).strip(),
                    "source": clean_wikilinks(fm.get("source_of_power", "")),
                    "danger": str(fm.get("danger_cost", "")).strip(),
                    "summary": extract_summary_or_quote(body)
                })

    # 6. Languages
    languages: list[dict[str, Any]] = []
    lang_dir = bible_path / "Languages"
    if lang_dir.is_dir():
        for f in sorted(lang_dir.rglob("*.md")):
            if f.is_file():
                fm, body = parse_frontmatter_and_body(f)
                if is_template(f, fm):
                    continue
                lexicon = []
                for line in body.splitlines():
                    if line.strip().startswith("|") and not line.strip().startswith("| :---") and not line.strip().startswith("| Foreign Word") and not line.strip().startswith("| Term"):
                        cells = [clean_wikilinks(c.strip().strip('*')) for c in line.strip().split("|")[1:-1]]
                        if len(cells) >= 2 and cells[0] and cells[0] != "Foreign Word":
                            word = cells[0]
                            pos = cells[1] if len(cells) > 1 else ""
                            definition = cells[3] if len(cells) > 3 else (cells[2] if len(cells) > 2 else "")
                            lexicon.append({"word": word, "pos": pos, "definition": definition})
                languages.append({
                    "name": fm.get("name") or f.stem,
                    "family": str(fm.get("language_family", "")).strip(),
                    "spoken_by": clean_wikilinks(fm.get("spoken_by", "")),
                    "status": str(fm.get("status", "")).strip(),
                    "writing": str(fm.get("writing_system", "")).strip(),
                    "summary": extract_summary_or_quote(body),
                    "lexicon": lexicon
                })

    dp_content = build_dramatis_personae_markdown(characters)
    gc_content = build_glossary_markdown(factions, artifacts, magic_systems, creatures, languages)

    # Determine target books
    books_to_target = []
    if target_book and target_book.lower() not in ("all", "all-books"):
        valid_book = validate_volume_name(target_book)
        bdir = ms_path / valid_book
        bdir.mkdir(parents=True, exist_ok=True)
        books_to_target.append(bdir)
    else:
        for b in sorted(ms_path.glob("Book-*")):
            if b.is_dir():
                books_to_target.append(b)
        if not books_to_target:
            bdir = ms_path / "Book-01"
            bdir.mkdir(parents=True, exist_ok=True)
            books_to_target.append(bdir)

    generated_files: list[Path] = []
    for bdir in books_to_target:
        bm_dir = bdir / "04_Back_Matter"
        bm_dir.mkdir(parents=True, exist_ok=True)

        dp_path = bm_dir / "01_Dramatis_Personae.md"
        gc_path = bm_dir / "02_Glossary_and_Concordance.md"

        atomic_write(dp_path, dp_content)
        atomic_write(gc_path, gc_content)
        generated_files.extend([dp_path, gc_path])

    return {
        "characters_count": len(characters),
        "factions_count": len(factions),
        "artifacts_count": len(artifacts),
        "creatures_count": len(creatures),
        "magic_systems_count": len(magic_systems),
        "languages_count": len(languages),
        "volumes_updated": len(books_to_target),
        "generated_files": [str(p) for p in generated_files],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ars Arcanum Concordance Generator — Dramatis Personae and Glossary Back-Matter",
        prog="concordance",
    )
    parser.add_argument("target", nargs="?", help="World Lore Vault or Manuscript directory")
    parser.add_argument("-m", "--manuscript", help="Manuscript project directory")
    parser.add_argument("-w", "--world", help="World Lore Vault directory")
    parser.add_argument("-b", "--book", default="all", help="Target book volume (default: all)")

    args = parser.parse_args(argv)

    world_dir = args.world or os.environ.get("BIBLE_DIR")
    ms_dir = args.manuscript or os.environ.get("MANUSCRIPT_DIR")

    if not world_dir and args.target:
        p = Path(args.target)
        if (p / "00-World-Bible").is_dir() or (p / "Characters").is_dir():
            world_dir = str(p)
        else:
            ms_dir = str(p)

    if not world_dir:
        print("Error: World Bible directory not specified (see --help)", file=sys.stderr)
        return 2

    if not ms_dir:
        w_path = Path(world_dir)
        ms_dir = str(w_path / "01-Manuscript") if (w_path / "01-Manuscript").is_dir() else str(w_path)

    try:
        res = generate_concordance(
            bible_dir=Path(world_dir),
            ms_dir=Path(ms_dir),
            target_book=args.book,
        )
        print(f"[✓] Concordance generated across {res['volumes_updated']} volume(s).")
        print(f"    Characters: {res['characters_count']}, Factions: {res['factions_count']}, Artifacts: {res['artifacts_count']}")
        return 0
    except Exception as e:
        print(f"Error generating concordance: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
