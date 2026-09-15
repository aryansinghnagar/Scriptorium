#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Back-Matter Concordance & Dramatis Personae Engine
# Purpose: Automatically reads YAML frontmatter and lore definitions from
#          00-World-Bible/ (Characters, Languages, Bestiary, Artifacts, Factions)
#          and generates publication-ready Markdown back-matter files in
#          01-Manuscript/<Book>/04_Back_Matter/01_Dramatis_Personae.md and
#          01-Manuscript/<Book>/04_Back_Matter/02_Glossary_and_Concordance.md.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Scriptorium Concordance Generator — generate Dramatis Personae and Glossary back-matter.

Usage:
  generate_concordance.sh [WORLD_NAME|WORLD_DIR] [OPTIONS]

Options:
  -w, --world NAME     World name or directory path
  -b, --book VOLUME    Target book volume (e.g. Book-01, Book-02, or "all"; default: all volumes)
  -u, --universe NAME  Universe name (optional)
  -h, --help           Show this help and exit

Exit codes:
  0  concordance generated successfully
  1  error (world not found, invalid parameters)
  3  user abort (no world selected)
USAGE
}

WORLD_CLI=""
BOOK_CLI=""
UNIVERSE_CLI=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 1; }
            WORLD_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 1; }
            BOOK_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 1; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -h|--help)
            usage; exit 0 ;;
        --)
            shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
        *)
            POSITIONAL+=("$1"); shift ;;
    esac
done

TARGET_WORLD="${WORLD_CLI:-${POSITIONAL[0]:-}}"
TARGET_BOOK="${BOOK_CLI:-${POSITIONAL[1]:-}}"

# Discover worlds if not provided
discover_worlds WORLDS

if [ -z "${TARGET_WORLD}" ]; then
    if [ ${#WORLDS[@]} -eq 1 ]; then
        TARGET_WORLD="${WORLDS[0]}"
    elif has_gui && [ ${#WORLDS[@]} -gt 1 ]; then
        CHOICES=()
        for w in "${WORLDS[@]}"; do
            CHOICES+=("$(basename "$w")" "[Universe: $(universe_label "$w")] $w")
        done
        PICKED=$(zenity --list --title="Scriptorium — Select World for Concordance" \
            --text="Select the world to generate back-matter concordance for:" \
            --column="World Name" --column="Universe & Path" \
            --width=520 --height=320 \
            "${CHOICES[@]}" || true)
        [ -n "$PICKED" ] && TARGET_WORLD="$PICKED"
    elif [ -t 0 ] && [ ${#WORLDS[@]} -gt 1 ]; then
        echo "Select world to generate concordance for:"
        select w in "${WORLDS[@]}"; do
            [ -n "${w:-}" ] && TARGET_WORLD="$w"
            break
        done
    fi
fi

if [ -z "${TARGET_WORLD}" ]; then
    echo "No world specified. Aborting." >&2
    exit 3
fi

WORLD_DIR="$(resolve_world_dir "${TARGET_WORLD}" "${UNIVERSE_CLI}")"

if [ -z "${WORLD_DIR}" ] || [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: World directory '${TARGET_WORLD}' not found." >&2
    exit 1
fi

BIBLE_DIR="${WORLD_DIR}/00-World-Bible"
MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"

if [ ! -d "${BIBLE_DIR}" ]; then
    echo "Error: World Bible folder missing at ${BIBLE_DIR}." >&2
    exit 1
fi

if [ ! -d "${MANUSCRIPT_DIR}" ]; then
    echo "Error: Manuscript folder missing at ${MANUSCRIPT_DIR}." >&2
    exit 1
fi

command -v python3 &>/dev/null || { echo "Error: python3 is required." >&2; exit 1; }

echo "Generating Concordance & Dramatis Personae for $(basename "${WORLD_DIR}")..."

BIBLE_DIR="${BIBLE_DIR}" MANUSCRIPT_DIR="${MANUSCRIPT_DIR}" TARGET_BOOK="${TARGET_BOOK}" python3 - << 'PYEOF'
import os
import re
import sys
from pathlib import Path

bible_dir = Path(os.environ["BIBLE_DIR"])
ms_dir = Path(os.environ["MANUSCRIPT_DIR"])
target_book = os.environ.get("TARGET_BOOK", "").strip()

FRONTMATTER_DELIM = "---"

def clean_wikilinks(text):
    if not text:
        return ""
    # [[Link|Display]] -> Display
    text = re.sub(r'\[\[(?:[^\|\]]+\|)?([^\]]+)\]\]', r'\1', str(text))
    return text.strip()

def parse_frontmatter_and_body(file_path):
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}, ""
    lines = content.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, content
    fm = {}
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

def extract_summary_or_quote(body):
    lines = body.strip().splitlines()
    summary_lines = []
    in_summary = False
    quote = ""
    for line in lines:
        s = line.strip()
        if s.startswith(">"):
            if not quote:
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
    # Fallback to first non-header non-quote paragraph
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith(">") and not s.startswith("---") and not s.startswith("-") and not s.startswith("|"):
            return clean_wikilinks(s)
    return quote

def is_template(path, fm):
    if "Template" in path.name or "template" in path.name or "Templates" in path.parts:
        return True
    name = str(fm.get("name", ""))
    if "<%" in name:
        return True
    return False

# 1. Collect Characters
characters = []
char_dir = bible_dir / "Characters"
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
            role = str(fm.get("role", "Supporting")).strip()
            status = str(fm.get("status", "")).strip()
            faction = clean_wikilinks(fm.get("faction", ""))
            origin = clean_wikilinks(fm.get("origin", ""))
            species = str(fm.get("species_race", "")).strip()
            occupation = str(fm.get("occupation", "")).strip()
            summary = extract_summary_or_quote(body)
            characters.append({
                "name": name,
                "aliases": [clean_wikilinks(a) for a in aliases if a],
                "role": role,
                "status": status,
                "faction": faction,
                "origin": origin,
                "species": species,
                "occupation": occupation,
                "summary": summary
            })

# 2. Collect Factions
factions = []
fac_dir = bible_dir / "Factions"
if fac_dir.is_dir():
    for f in sorted(fac_dir.rglob("*.md")):
        if f.is_file():
            fm, body = parse_frontmatter_and_body(f)
            if is_template(f, fm):
                continue
            name = fm.get("name") or f.stem
            ftype = str(fm.get("faction_type", "Faction")).strip()
            leader = clean_wikilinks(fm.get("leader", ""))
            headquarters = clean_wikilinks(fm.get("headquarters", ""))
            motto = str(fm.get("motto", "")).strip()
            summary = extract_summary_or_quote(body)
            factions.append({
                "name": name,
                "type": ftype,
                "leader": leader,
                "headquarters": headquarters,
                "motto": motto,
                "summary": summary
            })

# 3. Collect Artifacts
artifacts = []
art_dir = bible_dir / "Artifacts"
if art_dir.is_dir():
    for f in sorted(art_dir.rglob("*.md")):
        if f.is_file():
            fm, body = parse_frontmatter_and_body(f)
            if is_template(f, fm):
                continue
            name = fm.get("name") or f.stem
            atype = str(fm.get("artifact_type", "Relic")).strip()
            rarity = str(fm.get("rarity", "")).strip()
            bearer = clean_wikilinks(fm.get("current_bearer", ""))
            creator = clean_wikilinks(fm.get("creator", ""))
            summary = extract_summary_or_quote(body)
            artifacts.append({
                "name": name,
                "type": atype,
                "rarity": rarity,
                "bearer": bearer,
                "creator": creator,
                "summary": summary
            })

# 4. Collect Bestiary
creatures = []
best_dir = bible_dir / "Bestiary"
if best_dir.is_dir():
    for f in sorted(best_dir.rglob("*.md")):
        if f.is_file():
            fm, body = parse_frontmatter_and_body(f)
            if is_template(f, fm):
                continue
            name = fm.get("name") or f.stem
            classification = str(fm.get("classification", "Creature")).strip()
            threat = str(fm.get("threat_level", "")).strip()
            habitat = clean_wikilinks(fm.get("habitat", ""))
            summary = extract_summary_or_quote(body)
            creatures.append({
                "name": name,
                "classification": classification,
                "threat": threat,
                "habitat": habitat,
                "summary": summary
            })

# 5. Collect Magic & Tech Systems
magic_systems = []
magic_dir = bible_dir / "Magic-Technology"
if magic_dir.is_dir():
    for f in sorted(magic_dir.rglob("*.md")):
        if f.is_file():
            fm, body = parse_frontmatter_and_body(f)
            if is_template(f, fm):
                continue
            name = fm.get("name") or f.stem
            classification = str(fm.get("classification", "Magic / Technology")).strip()
            source = clean_wikilinks(fm.get("source_of_power", ""))
            danger = str(fm.get("danger_cost", "")).strip()
            summary = extract_summary_or_quote(body)
            magic_systems.append({
                "name": name,
                "classification": classification,
                "source": source,
                "danger": danger,
                "summary": summary
            })

# 6. Collect Languages & Conlang Lexicons
languages = []
lang_dir = bible_dir / "Languages"
if lang_dir.is_dir():
    for f in sorted(lang_dir.rglob("*.md")):
        if f.is_file():
            fm, body = parse_frontmatter_and_body(f)
            if is_template(f, fm):
                continue
            name = fm.get("name") or f.stem
            family = str(fm.get("language_family", "")).strip()
            spoken_by = clean_wikilinks(fm.get("spoken_by", ""))
            status = str(fm.get("status", "")).strip()
            writing = str(fm.get("writing_system", "")).strip()
            summary = extract_summary_or_quote(body)
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
                "name": name,
                "family": family,
                "spoken_by": spoken_by,
                "status": status,
                "writing": writing,
                "summary": summary,
                "lexicon": lexicon
            })

# Generate Markdown content
# -------------------------------------------------------------
# A. Dramatis Personae
# -------------------------------------------------------------
dp_md = []
dp_md.append("# Dramatis Personae\n")
dp_md.append("A comprehensive register of key individuals, allies, rivals, and figures encountered throughout the narrative.\n")

# F-10: partition with explicit precedence so hybrid roles (e.g. "Major
# Rival") appear in exactly one section — antagonist wins, then protagonist,
# then supporting. Previously a role matching both patterns (e.g. "Major
# Rival") was double-listed under Protagonists AND Antagonists.
def is_antagonist(c):
    return re.search(r'antagonist|villain|rival|nemesis', c['role'], re.IGNORECASE)

def is_protagonist(c):
    return re.search(r'protagonist|major|lead', c['role'], re.IGNORECASE)

antagonists = [c for c in characters if is_antagonist(c)]
protagonists = [c for c in characters if is_protagonist(c) and not is_antagonist(c)]
supporting = [c for c in characters if not is_protagonist(c) and not is_antagonist(c)]

def format_character_block(c):
    lines = []
    alias_str = f" (*{', '.join(c['aliases'])}*)" if c['aliases'] else ""
    meta_parts = []
    if c['role'] and c['role'].lower() not in ("protagonist", "antagonist", "supporting"):
        meta_parts.append(c['role'])
    if c['species'] and c['species'].lower() != "human":
        meta_parts.append(c['species'])
    if c['occupation']:
        meta_parts.append(c['occupation'])
    if c['faction']:
        meta_parts.append(f"Affiliation: {c['faction']}")
    if c['origin']:
        meta_parts.append(f"Origin: {c['origin']}")
    if c['status'] and c['status'].lower() not in ("alive", "active", "unknown", ""):
        meta_parts.append(f"Status: {c['status']}")
    meta_str = f" — *{', '.join(meta_parts)}*" if meta_parts else ""
    lines.append(f"- **{c['name']}**{alias_str}{meta_str}")
    if c['summary']:
        lines.append(f"  {c['summary']}")
    return "\n".join(lines)

if protagonists:
    dp_md.append("## Protagonists & Major Figures\n")
    for c in sorted(protagonists, key=lambda x: x['name']):
        dp_md.append(format_character_block(c) + "\n")

if antagonists:
    dp_md.append("## Antagonists & Rivals\n")
    for c in sorted(antagonists, key=lambda x: x['name']):
        dp_md.append(format_character_block(c) + "\n")

if supporting:
    dp_md.append("## Supporting Personae & Affiliations\n")
    for c in sorted(supporting, key=lambda x: x['name']):
        dp_md.append(format_character_block(c) + "\n")

if not characters:
    dp_md.append("*No character dossiers registered in the World Bible.*\n")

dp_content = "\n".join(dp_md).strip() + "\n"

# -------------------------------------------------------------
# B. Glossary & Concordance
# -------------------------------------------------------------
gc_md = []
gc_md.append("# Glossary & Concordance\n")
gc_md.append("An encyclopedic concordance of world terminology, factions, legendary relics, magic systems, bestiary creatures, and linguistics.\n")

if factions:
    gc_md.append("## Factions & Sovereign Powers\n")
    for f in sorted(factions, key=lambda x: x['name']):
        details = []
        if f['type']: details.append(f['type'])
        if f['leader']: details.append(f"Led by {f['leader']}")
        if f['headquarters']: details.append(f"Seat: {f['headquarters']}")
        d_str = f" (*{', '.join(details)}*)" if details else ""
        m_str = f" Motto: *\"{f['motto']}\"*." if f['motto'] else ""
        gc_md.append(f"- **{f['name']}**{d_str}:{m_str}")
        if f['summary']:
            gc_md.append(f"  {f['summary']}\n")
        else:
            gc_md.append("")

if artifacts:
    gc_md.append("## Legendary Artifacts & Relics\n")
    for a in sorted(artifacts, key=lambda x: x['name']):
        details = []
        if a['type']: details.append(a['type'])
        if a['rarity']: details.append(a['rarity'])
        if a['bearer']: details.append(f"Bearer: {a['bearer']}")
        if a['creator']: details.append(f"Forged by {a['creator']}")
        d_str = f" (*{', '.join(details)}*)" if details else ""
        gc_md.append(f"- **{a['name']}**{d_str}:")
        if a['summary']:
            gc_md.append(f"  {a['summary']}\n")
        else:
            gc_md.append("")

if magic_systems:
    gc_md.append("## Magic & Arcane Disciplines\n")
    for m in sorted(magic_systems, key=lambda x: x['name']):
        details = []
        if m['classification']: details.append(m['classification'])
        if m['source']: details.append(f"Source: {m['source']}")
        if m['danger']: details.append(f"Cost: {m['danger']}")
        d_str = f" (*{', '.join(details)}*)" if details else ""
        gc_md.append(f"- **{m['name']}**{d_str}:")
        if m['summary']:
            gc_md.append(f"  {m['summary']}\n")
        else:
            gc_md.append("")

if creatures:
    gc_md.append("## Bestiary & Ecological Hazards\n")
    for cr in sorted(creatures, key=lambda x: x['name']):
        details = []
        if cr['classification']: details.append(cr['classification'])
        if cr['threat']: details.append(f"Threat: {cr['threat']}")
        if cr['habitat']: details.append(f"Habitat: {cr['habitat']}")
        d_str = f" (*{', '.join(details)}*)" if details else ""
        gc_md.append(f"- **{cr['name']}**{d_str}:")
        if cr['summary']:
            gc_md.append(f"  {cr['summary']}\n")
        else:
            gc_md.append("")

if languages:
    gc_md.append("## Linguistics & Conlang Lexicon\n")
    for lang in sorted(languages, key=lambda x: x['name']):
        meta = []
        if lang['family']: meta.append(f"Family: {lang['family']}")
        if lang['spoken_by']: meta.append(f"Spoken by: {lang['spoken_by']}")
        if lang['status']: meta.append(f"Status: {lang['status']}")
        if lang['writing']: meta.append(f"Script: {lang['writing']}")
        gc_md.append(f"### {lang['name']}\n")
        if meta:
            gc_md.append(f"*{' | '.join(meta)}*\n")
        if lang['summary']:
            gc_md.append(f"{lang['summary']}\n")
        if lang['lexicon']:
            gc_md.append("| Term | Part of Speech | Definition / Cultural Meaning |")
            gc_md.append("| :--- | :--- | :--- |")
            for term in lang['lexicon']:
                gc_md.append(f"| *{term['word']}* | {term['pos']} | {term['definition']} |")
            gc_md.append("")

if not (factions or artifacts or magic_systems or creatures or languages):
    gc_md.append("*No specialized concordance lore registered in the World Bible.*\n")

gc_content = "\n".join(gc_md).strip() + "\n"

# Determine target books
books_to_target = []
if target_book and target_book != "all":
    bdir = ms_dir / target_book
    if bdir.is_dir():
        books_to_target.append(bdir)
    else:
        bdir.mkdir(parents=True, exist_ok=True)
        books_to_target.append(bdir)
else:
    for b in sorted(ms_dir.glob("Book-*")):
        if b.is_dir():
            books_to_target.append(b)
    if not books_to_target:
        bdir = ms_dir / "Book-01"
        bdir.mkdir(parents=True, exist_ok=True)
        books_to_target.append(bdir)

count = 0
for bdir in books_to_target:
    bm_dir = bdir / "04_Back_Matter"
    bm_dir.mkdir(parents=True, exist_ok=True)
    
    dp_path = bm_dir / "01_Dramatis_Personae.md"
    gc_path = bm_dir / "02_Glossary_and_Concordance.md"
    
    dp_path.write_text(dp_content, encoding="utf-8")
    gc_path.write_text(gc_content, encoding="utf-8")
    count += 1
    print(f"[✓] Back-matter generated in: {bm_dir.relative_to(ms_dir.parent)}")

print(f"Concordance generation complete across {count} manuscript volume(s).")
PYEOF

MSG="Concordance and Dramatis Personae successfully generated for '$(basename "${WORLD_DIR}")'!\n\nFiles created under 01-Manuscript/<Book>/04_Back_Matter/:\n• 01_Dramatis_Personae.md\n• 02_Glossary_and_Concordance.md\n\nThese will be automatically compiled at the end of your Typst print PDFs and Pandoc EPUBs."

if has_gui; then
    zenity --info --title="Concordance Generated" --text="${MSG}" --width=480
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit 0
