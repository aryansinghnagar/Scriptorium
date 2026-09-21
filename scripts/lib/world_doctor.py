#!/usr/bin/env python3
"""
Ars Arcanum World Doctor (scripts/lib/world_doctor.py)
=====================================================
Consistency and integrity checker for the Obsidian World Bible lore vaults.
Verifies:
- Wiki-link integrity (WLD-101)
- Typed frontmatter references (WLD-102)
- Missing required entity fields (WLD-103)
- Multi-era timeline chronology (WLD-104)
- Duplicate identities and conflicting aliases (WLD-105)
- Frontmatter parsing syntax (WLD-106)
- Orphaned lore notes (WLD-107)
- Manuscript entity name drift (WLD-108)
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

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


WIKI_LINK = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")
FRONTMATTER_DELIM = "---"
MAX_DEFAULT_BYTES = 2 * 1024 * 1024  # 2MB cap per file

TYPED_REF_FIELDS = {
    "faction", "origin", "current_location", "leader", "headquarters",
    "dominant_faction", "realm_region", "region", "rival", "ally", "mentor",
    "magic_ability", "key_landmarks", "habitat", "creator", "current_bearer",
    "associated_faction", "primary_location", "allies", "rivals", "vassals",
    "overlord", "treaties", "oracle", "target_entity", "dietary_prey",
}

REQUIRED_BY_TYPE = {
    "character": ("name",),
    "faction": ("name",),
    "location": ("name",),
    "magic_tech_system": ("name",),
    "timeline_event": ("name",),
    "language": ("name",),
    "creature": ("name",),
    "artifact": ("name",),
    "cosmology": ("name",),
    "economy": ("name",),
    "prophecy": ("name",),
}

ERA_ORDER = {
    '1e': 1, '1a': 1, 'first age': 1, 'age 1': 1, 'era 1': 1, 'first era': 1, 'fa': 1,
    '2e': 2, '2a': 2, 'second age': 2, 'age 2': 2, 'era 2': 2, 'second era': 2, 'sa': 2,
    '3e': 3, '3a': 3, 'third age': 3, 'age 3': 3, 'era 3': 3, 'third era': 3, 'ta': 3,
    '4e': 4, '4a': 4, 'fourth age': 4, 'age 4': 4, 'era 4': 4, 'fourth era': 4,
    '5e': 5, '5a': 5, 'fifth age': 5, 'age 5': 5, 'era 5': 5, 'fifth era': 5,
}

BC_PATTERN = re.compile(r'\b(bce|bc|b\.c\.e\.|b\.c\.|before common era|before era)\b', re.IGNORECASE)
CE_PATTERN = re.compile(r'\b(ce|ad|c\.e\.|a\.d\.|common era|anno domini)\b', re.IGNORECASE)
ISO_DATE_PATTERN = re.compile(r'^([+-]?\d{1,6})[-/](\d{1,2})(?:[-/](\d{1,2}))?$')

PLACEHOLDER_NAMES = {
    "protagonist", "antagonist", "capital", "capital city",
    "river crossing", "mountain fortress", "the high spire",
    "location-name", "faction-name", "character-name", "magic-tech-system",
    "character-a", "character-b", "character-c", "unknown", "none"
}


def read_capped(path: str, max_bytes: int = MAX_DEFAULT_BYTES) -> str:
    with open(path, "rb") as fh:
        data = fh.read(max_bytes + 1)
    if len(data) > max_bytes:
        print(f"[!] Warning: {path} exceeds {max_bytes // (1024 * 1024)} MB read cap; truncated.", file=sys.stderr)
        data = data[:max_bytes]
    return data.decode("utf-8", "ignore")


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], bool]:
    """Strict flat-subset YAML parser: key: value / key: [a, b] / lists with '-'."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, True
    fm: Dict[str, Any] = {}
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


def norm(name: Any) -> str:
    return re.sub(r'[\s_]+', ' ', str(name).strip().lower())


def parse_timeline_date(val: Any) -> Optional[Tuple[Optional[str], float, str]]:
    if val is None:
        return None
    s = str(val).strip().strip('"').strip("'")
    if not s:
        return None

    try:
        return (None, float(s), s)
    except ValueError:
        pass

    m_iso = ISO_DATE_PATTERN.match(s)
    if m_iso:
        yr = float(m_iso.group(1))
        mo = float(m_iso.group(2))
        dy = float(m_iso.group(3)) if m_iso.group(3) else 1.0
        dec_val = yr + (mo - 1.0) / 12.0 + (dy - 1.0) / 365.25
        return (None, dec_val, s)

    if BC_PATTERN.search(s):
        num_m = re.search(r'([+-]?\d+(?:\.\d+)?)', s)
        if num_m:
            num = float(num_m.group(1))
            return (None, -abs(num), s)

    if CE_PATTERN.search(s):
        num_m = re.search(r'([+-]?\d+(?:\.\d+)?)', s)
        if num_m:
            num = float(num_m.group(1))
            return (None, abs(num), s)

    m1 = re.match(r'^([+-]?\d+(?:\.\d+)?)\s+([A-Za-z0-9_\s\.\'-]+)$', s)
    if m1:
        num = float(m1.group(1))
        era = m1.group(2).strip().lower()
        return (era, num, s)

    m2 = re.match(r'^([A-Za-z0-9_\s\.\'-]+?)\s+([+-]?\d+(?:\.\d+)?)$', s)
    if m2:
        era = m2.group(1).strip().lower()
        num = float(m2.group(2))
        return (era, num, s)

    return None


def compare_timeline_dates(d1_val: Any, d2_val: Any) -> Optional[int]:
    p1 = parse_timeline_date(d1_val)
    p2 = parse_timeline_date(d2_val)
    if p1 is None or p2 is None:
        return None

    era1, num1, _ = p1
    era2, num2, _ = p2

    if era1 is None and era2 is None:
        if num1 < num2:
            return -1
        if num1 > num2:
            return 1
        return 0

    if era1 in ERA_ORDER and era2 in ERA_ORDER:
        o1 = ERA_ORDER[era1]
        o2 = ERA_ORDER[era2]
        if o1 < o2:
            return -1
        if o1 > o2:
            return 1
        if num1 < num2:
            return -1
        if num1 > num2:
            return 1
        return 0

    if era1 is not None and era2 is not None and era1 == era2:
        if num1 < num2:
            return -1
        if num1 > num2:
            return 1
        return 0

    return None


def is_template(rel: str, fm: Dict[str, Any]) -> bool:
    fname = os.path.basename(rel)
    if fname == "World-Bible-Index.md":
        return False
    name = fm.get("name", "")
    path_parts = [p.lower() for p in rel.replace('\\', '/').split('/')]
    return (
        "template" in fname.lower()
        or "templates" in path_parts
        or "start_here" in rel.lower()
        or "fileclasses" in path_parts
        or "daily-writing-log" in rel.lower()
        or "<%" in str(name)
        or "<%" in str(fm.get("date", ""))
        or fm.get("type") in ("guide", "template", "fileclass")
    )


def check_world(
    bible_dir: str,
    manuscript_dir: Optional[str] = None,
    use_cache: bool = False,
    max_bytes: int = MAX_DEFAULT_BYTES,
) -> Dict[str, Any]:
    """Execute deep consistency audit across the World Bible and optional Manuscript."""
    bible_path = Path(bible_dir).resolve()
    if not bible_path.exists():
        raise FileNotFoundError(f"World directory not found: {bible_dir}")

    # Determine real Bible directory
    if (bible_path / "00-World-Bible").is_dir():
        actual_bible = bible_path / "00-World-Bible"
    else:
        actual_bible = bible_path

    index: Dict[str, str] = {}
    aliases: Dict[str, str] = {}
    notes: List[Tuple[str, Dict[str, Any], str]] = []
    fm_errors: List[str] = []
    required_errors: List[Tuple[str, str, str]] = []
    timeline_errors: List[Tuple[str, str]] = []

    cached_files: Dict[str, Any] = {}
    cache_used = False
    if use_cache:
        try:
            from lib import cache as cache_engine
            b_cache = cache_engine.scan_project(str(actual_bible))
            if manuscript_dir:
                cache_engine.scan_project(str(manuscript_dir))
            files = (b_cache or {}).get("files", {})
            if files and b_cache.get("healthy", True):
                cached_files = files
                cache_used = True
        except Exception:
            pass

    cached_rels: Set[str] = set()
    if cache_used:
        for rel, entry in sorted(cached_files.items()):
            if not rel.endswith(".md"):
                continue
            base = os.path.basename(rel)
            if base.startswith("."):
                continue
            fm = entry.get("frontmatter") or {}
            links = list(entry.get("wikilinks") or [])
            pseudo = "\n".join(f"[[{t}]]" for t in links)
            stem = os.path.splitext(base)[0]
            rel_no_ext = os.path.splitext(rel)[0]
            index.setdefault(norm(stem), rel)
            index.setdefault(norm(rel_no_ext), rel)
            index.setdefault(norm(rel_no_ext.replace('\\', '/')), rel)
            if fm.get("name") and isinstance(fm["name"], str) and fm["name"].strip():
                index.setdefault(norm(fm["name"]), rel)
            for alias in (fm.get("aliases") or []):
                if isinstance(alias, str) and alias.strip():
                    aliases.setdefault(norm(alias), rel)
            etype = fm.get("type", "")
            for req in REQUIRED_BY_TYPE.get(etype, ()):
                if not fm.get(req):
                    required_errors.append((rel, etype, req))
            for (b_key, d_key, label) in [("birth_year", "death_year", "Death year ({d}) precedes birth year ({b})"),
                                          ("birth_date", "death_date", "Death date ({d}) precedes birth date ({b})"),
                                          ("start_year", "end_year", "End year ({e}) precedes start year ({s})"),
                                          ("start_date", "end_date", "End date ({e}) precedes start date ({s})")]:
                if b_key in fm and d_key in fm:
                    cmp = compare_timeline_dates(fm[b_key], fm[d_key])
                    if cmp is not None and cmp > 0:
                        msg = label.replace("{b}", str(fm[b_key])).replace("{d}", str(fm[d_key])).replace("{s}", str(fm[b_key])).replace("{e}", str(fm[d_key]))
                        timeline_errors.append((rel, msg))
            notes.append((rel, fm, pseudo))
            cached_rels.add(rel)

    # Walk files on disk
    for root, dirs, files in os.walk(str(actual_bible)):
        dirs[:] = [d for d in dirs if d not in (".obsidian", ".git")]
        for fname in sorted(files):
            if not fname.endswith(".md") or fname.startswith("."):
                continue
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, str(actual_bible))
            if rel in cached_rels:
                continue
            stem = os.path.splitext(fname)[0]
            try:
                text = read_capped(path, max_bytes=max_bytes)
            except OSError:
                continue
            fm, ok = parse_frontmatter(text)
            if not ok:
                fm_errors.append(rel)
            rel_no_ext = os.path.splitext(rel)[0]
            index.setdefault(norm(stem), rel)
            index.setdefault(norm(rel_no_ext), rel)
            index.setdefault(norm(rel_no_ext.replace('\\', '/')), rel)
            if fm.get("name") and isinstance(fm["name"], str) and fm["name"].strip():
                index.setdefault(norm(fm["name"]), rel)
            for alias in (fm.get("aliases") or []):
                if isinstance(alias, str) and alias.strip():
                    aliases.setdefault(norm(alias), rel)
            etype = fm.get("type", "")
            for req in REQUIRED_BY_TYPE.get(etype, ()):
                if not fm.get(req):
                    required_errors.append((rel, etype, req))

            for (b_key, d_key, label) in [("birth_year", "death_year", "Death year ({d}) precedes birth year ({b})"),
                                          ("birth_date", "death_date", "Death date ({d}) precedes birth date ({b})"),
                                          ("start_year", "end_year", "End year ({e}) precedes start year ({s})"),
                                          ("start_date", "end_date", "End date ({e}) precedes start date ({s})")]:
                if b_key in fm and d_key in fm:
                    b_val = fm[b_key]
                    d_val = fm[d_key]
                    cmp = compare_timeline_dates(b_val, d_val)
                    if cmp is not None and cmp > 0:
                        msg = label.replace("{b}", str(b_val)).replace("{d}", str(d_val)).replace("{s}", str(b_val)).replace("{e}", str(d_val))
                        timeline_errors.append((rel, msg))

            notes.append((rel, fm, text))

    def resolve(target: str) -> Optional[str]:
        key = norm(target)
        if key in index:
            return index[key]
        if key in aliases:
            return aliases[key]
        return None

    # Pass 2: Links & Frontmatter Ref Integrity
    broken_links: List[Tuple[str, str]] = []
    placeholder_links: List[Tuple[str, str]] = []
    dangling_refs: List[Tuple[str, str, str]] = []
    inbound = {rel: 0 for rel, _, _ in notes}
    outbound: Dict[str, Set[str]] = {}

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

    claimed: Dict[str, Set[str]] = {}
    for rel, fm, _ in notes:
        if is_template(rel, fm):
            continue
        names = [n for n in [fm.get("name")] + (fm.get("aliases") or []) if isinstance(n, str) and n.strip()]
        for n in names:
            claimed.setdefault(norm(n), set()).add(rel)
    duplicates = {n: sorted(rs) for n, rs in claimed.items() if len(rs) > 1}

    # Pass 3: Manuscript Entity Cross-Validation
    manuscript_errors: List[Tuple[str, str, str]] = []
    ms_files_scanned = 0
    ms_index: Set[str] = set()

    if manuscript_dir and os.path.isdir(manuscript_dir):
        # Index all manuscript markdown files
        for root, dirs, files in os.walk(manuscript_dir):
            dirs[:] = [d for d in dirs if d not in (".git", ".obsidian")]
            for fname in sorted(files):
                if not fname.endswith(".md") or fname.startswith("."):
                    continue
                path = os.path.join(root, fname)
                rel = os.path.relpath(path, manuscript_dir)
                stem = os.path.splitext(fname)[0]
                rel_no_ext = os.path.splitext(rel)[0]
                ms_index.add(norm(stem))
                ms_index.add(norm(rel_no_ext))
                ms_index.add(norm(rel_no_ext.replace('\\', '/')))
                try:
                    txt = read_capped(path, max_bytes=max_bytes)
                    fm, _ = parse_frontmatter(txt)
                    if fm.get("name") and isinstance(fm["name"], str):
                        ms_index.add(norm(fm["name"]))
                    for al in (fm.get("aliases") or []):
                        if isinstance(al, str):
                            ms_index.add(norm(al))
                except Exception:
                    pass

        # Scan manuscript scenes for entity tags and prose lore links
        for root, dirs, files in os.walk(manuscript_dir):
            dirs[:] = [d for d in dirs if d not in (".git", "Outlines", ".obsidian")]
            for fname in sorted(files):
                if not fname.endswith(".md") or fname.startswith("."):
                    continue
                path = os.path.join(root, fname)
                rel = os.path.relpath(path, manuscript_dir)
                try:
                    text = read_capped(path, max_bytes=max_bytes)
                except OSError:
                    continue
                ms_files_scanned += 1

                for line in text.splitlines():
                    stripped = line.strip()
                    m_tag = re.match(r"^@(pov|char|character|location|focus|faction|item|artifact|prophecy):\s*(.+)$", stripped, re.IGNORECASE)
                    if m_tag:
                        tag_type = m_tag.group(1).lower()
                        raw_val = m_tag.group(2).strip()
                        items = [v.strip().strip('"').strip("'") for v in raw_val.split(",") if v.strip()]
                        for item in items:
                            if not item or norm(item) in PLACEHOLDER_NAMES:
                                continue
                            wl_m = WIKI_LINK.match(item)
                            target = wl_m.group(1).split("#")[0].strip() if wl_m else item
                            if not target or norm(target) in PLACEHOLDER_NAMES:
                                continue
                            if resolve(target) is None and norm(target) not in ms_index:
                                manuscript_errors.append((rel, f"@{tag_type}", target))
                    elif stripped.startswith("@"):
                        continue
                    else:
                        for m_wl in WIKI_LINK.finditer(stripped):
                            target = m_wl.group(1).split("#")[0].strip()
                            if not target or norm(target) in PLACEHOLDER_NAMES:
                                continue
                            if resolve(target) is None and norm(target) not in ms_index:
                                manuscript_errors.append((rel, "[[link]]", target))

    findings: Dict[str, Any] = {
        "world": str(actual_bible),
        "notes": len(notes),
        "manuscript_files": ms_files_scanned,
        "fast_cache_requested": bool(use_cache),
        "fast_cache_used": bool(cache_used),
        "broken_links": [{"code": "WLD-101", "from": s, "missing": t} for s, t in broken_links],
        "dangling_frontmatter_refs": [{"code": "WLD-102", "from": s, "field": f, "missing": t} for s, f, t in dangling_refs],
        "unrenamed_templates": sorted(rel for rel, fm, _ in notes if is_template(rel, fm)),
        "placeholder_links": [{"from": s, "missing": t} for s, t in placeholder_links],
        "orphans": [{"code": "WLD-107", "file": rel} for rel in sorted(orphans)],
        "duplicate_identities": [{"code": "WLD-105", "name": n, "files": fs} for n, fs in duplicates.items()],
        "frontmatter_parse_errors": [{"code": "WLD-106", "file": f} for f in fm_errors],
        "missing_required_fields": [{"code": "WLD-103", "file": s, "type": t, "field": f} for s, t, f in required_errors],
        "timeline_errors": [{"code": "WLD-104", "file": s, "issue": iss} for s, iss in timeline_errors],
        "manuscript_name_drift": [{"code": "WLD-108", "file": s, "ref_type": r, "missing": t} for s, r, t in manuscript_errors],
    }

    return findings


def format_report_text(findings: Dict[str, Any]) -> str:
    lines = [
        f"Ars Arcanum World Doctor — {findings['world']}",
        f"Notes scanned: {findings['notes']}" + (" (fast cache)" if findings.get("fast_cache_used") else ""),
    ]
    if findings.get("manuscript_files", 0) > 0:
        lines.append(f"Manuscript scenes scanned: {findings['manuscript_files']}")
    lines.append("")

    def add_section(title: str, items: List[str]):
        if not items:
            return
        lines.append(f"{title}: {len(items)}")
        for it in items:
            lines.append(f"  - {it}")
        lines.append("")

    add_section("Broken wiki-links [WLD-101]", [f"{x['from']} -> [[{x['missing']}]]" for x in findings["broken_links"]])
    add_section("Dangling frontmatter references [WLD-102]",
                [f"{x['from']}: {x['field']} -> [[{x['missing']}]]" for x in findings["dangling_frontmatter_refs"]])
    add_section("Dangling manuscript entity references [WLD-108]",
                [f"{x['file']} ({x['ref_type']}): entity '{x['missing']}' not found in World Bible" for x in findings["manuscript_name_drift"]])
    add_section("Missing required fields [WLD-103]",
                [f"{x['file']} ({x['type']}) lacks '{x['field']}'" for x in findings["missing_required_fields"]])
    add_section("Timeline chronological errors [WLD-104]",
                [f"{x['file']}: {x['issue']}" for x in findings["timeline_errors"]])
    add_section("Duplicate identities [WLD-105]",
                [f"'{x['name']}' claimed by {', '.join(x['files'])}" for x in findings["duplicate_identities"]])
    add_section("Frontmatter parse errors [WLD-106]", [x["file"] for x in findings["frontmatter_parse_errors"]])
    add_section("Orphan notes (no links in or out) [WLD-107]", [x["file"] for x in findings["orphans"]])
    add_section("Unrenamed templates (placeholders still active)", findings["unrenamed_templates"])

    has_findings = any([
        findings["broken_links"], findings["dangling_frontmatter_refs"], findings["orphans"],
        findings["duplicate_identities"], findings["frontmatter_parse_errors"],
        findings["missing_required_fields"], findings["timeline_errors"], findings["manuscript_name_drift"],
    ])

    if not has_findings:
        lines.append("No findings. World Bible and manuscript are internally consistent.")

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ars Arcanum World Doctor — World Bible Consistency Checker",
        prog="world_doctor",
    )
    parser.add_argument("world_dir", nargs="?", help="World Lore Vault directory")
    parser.add_argument("-m", "--manuscript", help="Manuscript directory for cross-validation")
    parser.add_argument("--fast", action="store_true", help="Accelerate scans using mtime-keyed in-memory caching")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    args = parser.parse_args(argv)

    world_dir = args.world_dir
    if not world_dir:
        # Check environment or default discovery
        world_dir = os.environ.get("BIBLE_DIR") or os.environ.get("WORLD_DIR")

    if not world_dir:
        print("Error: World directory not specified (see --help)", file=sys.stderr)
        return 2

    try:
        findings = check_world(
            bible_dir=world_dir,
            manuscript_dir=args.manuscript,
            use_cache=args.fast,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error running world doctor: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print(format_report_text(findings))

    has_findings = any([
        findings["broken_links"], findings["dangling_frontmatter_refs"], findings["orphans"],
        findings["duplicate_identities"], findings["frontmatter_parse_errors"],
        findings["missing_required_fields"], findings["timeline_errors"], findings["manuscript_name_drift"],
    ])
    return 1 if has_findings else 0


if __name__ == "__main__":
    sys.exit(main())
