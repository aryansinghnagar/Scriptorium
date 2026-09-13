#!/usr/bin/env bash
# ==============================================================================
# Scriptorium World Doctor (D-01 / Workstream 3.2)
# Purpose: Consistency checker for the Obsidian World Bible. Verifies wiki-link
#          integrity, typed frontmatter references, orphaned entities,
#          duplicate identities, and timeline chronology.
#
# Usage:
#   world_doctor.sh [WORLD_DIR] [OPTIONS]
#
# Options:
#   --json        Emit a machine-readable JSON report instead of text
#   -h, --help    Show this help
#
# Exit codes:
#   0  no findings / consistent world
#   1  findings reported (broken links, orphans, dangling references, etc.)
#   2  usage or environment error (world dir missing, python3 missing)
# ==============================================================================
set -euo pipefail

usage() {
    sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

WORLD_DIR=""
OUTPUT_JSON=0
while [ $# -gt 0 ]; do
    case "$1" in
        --json) OUTPUT_JSON=1; shift ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) WORLD_DIR="$1"; shift ;;
    esac
done

if [ -z "${WORLD_DIR}" ]; then
    WORLD_DIR="${HOME}/Worlds"
fi

if [ ! -d "${WORLD_DIR}" ]; then
    if [ -d "${HOME}/Universes" ]; then
        FOUND="$(find "${HOME}/Universes" -mindepth 3 -maxdepth 3 -type d -name "${WORLD_DIR}" 2>/dev/null | head -n 1 || true)"
        if [ -n "${FOUND}" ] && [ -d "${FOUND}" ]; then
            WORLD_DIR="${FOUND}"
        fi
    fi
    if [ ! -d "${WORLD_DIR}" ] && [ -d "${HOME}/Worlds/${WORLD_DIR}" ]; then
        WORLD_DIR="${HOME}/Worlds/${WORLD_DIR}"
    fi
fi

if [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: world directory not found: ${WORLD_DIR}" >&2
    exit 2
fi

BIBLE_DIR="${WORLD_DIR}/00-World-Bible"
if [ ! -d "${BIBLE_DIR}" ]; then
    echo "Error: no 00-World-Bible folder in ${WORLD_DIR} (is this a Scriptorium world?)" >&2
    exit 2
fi

command -v python3 &>/dev/null || { echo "Error: python3 is required." >&2; exit 2; }

BIBLE_DIR="${BIBLE_DIR}" OUTPUT_JSON="${OUTPUT_JSON}" python3 - << 'PYEOF'
import json
import os
import re
import sys

BIBLE = os.environ["BIBLE_DIR"]
JSON_OUT = os.environ["OUTPUT_JSON"] == "1"
MAX_BYTES = 2 * 1024 * 1024  # per-file read cap

WIKI_LINK = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")
FRONTMATTER_DELIM = "---"

TYPED_REF_FIELDS = {
    "faction", "origin", "current_location", "leader", "headquarters",
    "dominant_faction", "realm_region", "rival", "ally", "mentor",
    "magic_ability", "key_landmarks",
}

REQUIRED_BY_TYPE = {
    "character": ("name",),
    "faction": ("name",),
    "location": ("name",),
    "magic_tech_system": ("name",),
    "timeline_event": ("name",),
    "language": ("name",),
}

def read_capped(path):
    with open(path, "rb") as fh:
        return fh.read(MAX_BYTES).decode("utf-8", "ignore")

def parse_frontmatter(text):
    """Strict flat-subset parser: key: value / key: [a, b] / lists with '-'."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, True
    fm = {}
    i = 1
    n = len(lines)
    while i < n and lines[i].strip() != FRONTMATTER_DELIM:
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", stripped)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                items = []
                j = i + 1
                while j < n and re.match(r"^[ \t]+-[ \t]+", lines[j]):
                    items.append(re.sub(r"^[ \t]+-[ \t]+", "", lines[j]).strip().strip('"'))
                    j += 1
                if items:
                    fm[key] = items
                    i = j
                    continue
                fm[key] = ""
                i += 1
                continue
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = val.strip('"')
            i += 1
            continue
        return fm, False
    if i >= n:
        return fm, False
    return fm, True

def norm(name):
    return name.strip().lower()

# ---- Pass 1: Indexing & Frontmatter Validation ----
index = {}
aliases = {}
notes = []
fm_errors = []
required_errors = []
timeline_errors = []

for root, dirs, files in os.walk(BIBLE):
    dirs[:] = [d for d in dirs if d not in (".obsidian", ".git", "Templates")]
    for fname in sorted(files):
        if not fname.endswith(".md") or fname.startswith("."):
            continue
        path = os.path.join(root, fname)
        rel = os.path.relpath(path, BIBLE)
        stem = os.path.splitext(fname)[0]
        try:
            text = read_capped(path)
        except OSError:
            continue
        fm, ok = parse_frontmatter(text)
        if not ok:
            fm_errors.append(rel)
        index.setdefault(norm(stem), rel)
        for alias in (fm.get("aliases") or []):
            if isinstance(alias, str) and alias.strip():
                aliases.setdefault(norm(alias), rel)
        etype = fm.get("type", "")
        for req in REQUIRED_BY_TYPE.get(etype, ()):
            if not fm.get(req):
                required_errors.append((rel, etype, req))

        # Timeline chronological checks
        try:
            if "birth_year" in fm and "death_year" in fm:
                b = int(str(fm["birth_year"]).strip())
                d = int(str(fm["death_year"]).strip())
                if d < b:
                    timeline_errors.append((rel, f"Death year ({d}) precedes birth year ({b})"))
            if "start_year" in fm and "end_year" in fm:
                s = int(str(fm["start_year"]).strip())
                e = int(str(fm["end_year"]).strip())
                if e < s:
                    timeline_errors.append((rel, f"End year ({e}) precedes start year ({s})"))
        except (ValueError, TypeError):
            pass

        notes.append((rel, fm, text))

def resolve(target):
    key = norm(target)
    if key in index:
        return index[key]
    if key in aliases:
        return aliases[key]
    return None

def is_template(rel, fm):
    name = fm.get("name", "")
    return "Template" in rel or "<%" in str(name)

# ---- Pass 2: Link & Reference Integrity ----
broken_links = []
placeholder_links = []
dangling_refs = []
inbound = {rel: 0 for rel, _, _ in notes}
outbound = {}

for rel, fm, text in notes:
    templated = is_template(rel, fm)
    links = []
    for m in WIKI_LINK.finditer(text):
        target = m.group(1).strip()
        if not target or target.startswith("#"):
            continue
        target = target.split("#")[0].strip()
        if not target:
            continue
        links.append(target)
    outbound[rel] = set(links)
    for t in links:
        dest = resolve(t)
        if dest is None:
            if templated:
                placeholder_links.append((rel, t))
            else:
                broken_links.append((rel, t))
        elif dest in inbound:
            inbound[dest] += 1
    for field, val in fm.items():
        if field in TYPED_REF_FIELDS:
            vals = val if isinstance(val, list) else [val]
            for v in vals:
                for m in WIKI_LINK.finditer(str(v)):
                    t = m.group(1).strip()
                    if resolve(t) is None:
                        if templated:
                            placeholder_links.append((rel, t))
                        else:
                            dangling_refs.append((rel, field, t))

orphans = [rel for rel, fm, _ in notes
           if inbound.get(rel, 0) == 0 and not outbound.get(rel) and not is_template(rel, fm)]

claimed = {}
for rel, fm, _ in notes:
    if is_template(rel, fm):
        continue
    names = [n for n in [fm.get("name")] + (fm.get("aliases") or []) if isinstance(n, str) and n.strip()]
    for n in names:
        claimed.setdefault(norm(n), set()).add(rel)
duplicates = {n: sorted(rs) for n, rs in claimed.items() if len(rs) > 1}

findings = {
    "world": BIBLE,
    "notes": len(notes),
    "broken_links": [{"code": "WLD-101", "from": s, "missing": t} for s, t in broken_links],
    "dangling_frontmatter_refs": [{"code": "WLD-102", "from": s, "field": f, "missing": t} for s, f, t in dangling_refs],
    "unrenamed_templates": sorted(rel for rel, fm, _ in notes if is_template(rel, fm)),
    "placeholder_links": [{"from": s, "missing": t} for s, t in placeholder_links],
    "orphans": [{"code": "WLD-107", "file": rel} for rel in sorted(orphans)],
    "duplicate_identities": [{"code": "WLD-105", "name": n, "files": fs} for n, fs in duplicates.items()],
    "frontmatter_parse_errors": [{"code": "WLD-106", "file": f} for f in fm_errors],
    "missing_required_fields": [{"code": "WLD-103", "file": s, "type": t, "field": f} for s, t, f in required_errors],
    "timeline_errors": [{"code": "WLD-104", "file": s, "issue": iss} for s, iss in timeline_errors],
}

if JSON_OUT:
    print(json.dumps(findings, indent=2))
else:
    print(f"Scriptorium World Doctor — {BIBLE}")
    print(f"Notes scanned: {len(notes)}\n")

    def section(title, items):
        if not items:
            return
        print(f"{title}: {len(items)}")
        for it in items:
            print(f"  - {it}")
        print()

    section("Broken wiki-links [WLD-101]", [f"{s} -> [[{t}]]" for s, t in broken_links])
    section("Dangling frontmatter references [WLD-102]",
            [f"{s}: {f} -> [[{t}]]" for s, f, t in dangling_refs])
    section("Missing required fields [WLD-103]",
            [f"{s} ({t}) lacks '{f}'" for s, t, f in required_errors])
    section("Timeline chronological errors [WLD-104]",
            [f"{s}: {iss}" for s, iss in timeline_errors])
    section("Duplicate identities [WLD-105]",
            [f"'{n}' claimed by {', '.join(fs)}" for n, fs in duplicates.items()])
    section("Frontmatter parse errors [WLD-106]", fm_errors)
    section("Orphan notes (no links in or out) [WLD-107]", orphans)
    section("Unrenamed templates (placeholders still active)",
            sorted(rel for rel, fm, _ in notes if is_template(rel, fm)))

    if not any([broken_links, dangling_refs, orphans, duplicates, fm_errors, required_errors, timeline_errors]):
        print("No findings. World Bible is internally consistent.")

has_findings = any([
    broken_links, dangling_refs, orphans, duplicates, fm_errors, required_errors, timeline_errors,
])
sys.exit(1 if has_findings else 0)
PYEOF
