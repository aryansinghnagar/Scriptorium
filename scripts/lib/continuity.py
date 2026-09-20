#!/usr/bin/env python3
"""
Ars Arcanum Semantic Continuity Engine (scripts/lib/continuity.py)
==================================================================
Local-first, privacy-preserving narrative continuity and consistency analyzer.
Extracts character attributes, physical traits (eyes, hair, titles), and facts
from World Bible lore vaults, and cross-validates manuscript draft scenes to detect
character trait drift, physical contradictions, and chronological anomalies.

Zero external runtime dependencies; operates 100% offline.
"""

import sys
import re
import json
import argparse
import logging
from pathlib import Path

logger = logging.getLogger("arcanum.continuity")

TRAIT_PATTERNS = {
    "eye_color": [
        re.compile(r"\b(blue|green|hazel|brown|dark|amber|grey|gray|violet|golden|black|crimson|emerald|sapphire)\s+eyes?\b", re.IGNORECASE),
        re.compile(r"\beyes?\s+(?:were|of|as)\s+(blue|green|hazel|brown|dark|amber|grey|gray|violet|golden|black|crimson)\b", re.IGNORECASE),
        re.compile(r"^eyes?:\s*[\"']?([A-Za-z0-9_-]+)[\"']?", re.IGNORECASE | re.MULTILINE),
    ],
    "hair_color": [
        re.compile(r"\b(black|raven|dark|blonde|blond|golden|brown|auburn|red|silver|white|grey|gray)\s+hair\b", re.IGNORECASE),
        re.compile(r"\bhair\s+(?:was|of)\s+(black|raven|dark|blonde|blond|golden|brown|auburn|red|silver|white|grey|gray)\b", re.IGNORECASE),
        re.compile(r"^hair:\s*[\"']?([A-Za-z0-9_-]+)[\"']?", re.IGNORECASE | re.MULTILINE),
    ],
    "status": [
        re.compile(r"^status:\s*[\"']?(alive|dead|deceased|missing|imprisoned|exiled)[\"']?", re.IGNORECASE | re.MULTILINE),
    ],
    "title": [
        re.compile(r"^title:\s*[\"']?([^\"\n\r]+)[\"']?", re.IGNORECASE | re.MULTILINE),
    ]
}

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def normalize_trait(trait_type: str, raw_val: str) -> str:
    v = raw_val.lower().strip()
    if trait_type == "eye_color":
        if "blue" in v or "sapphire" in v:
            return "blue"
        if "green" in v or "emerald" in v:
            return "green"
        if "brown" in v or "dark" in v:
            return "brown"
        if "hazel" in v:
            return "hazel"
        if "grey" in v or "gray" in v:
            return "grey"
        if "black" in v:
            return "black"
        if "amber" in v or "golden" in v:
            return "amber"
    elif trait_type == "hair_color":
        if "black" in v or "raven" in v:
            return "black"
        if "blonde" in v or "blond" in v or "golden" in v:
            return "blonde"
        if "brown" in v or "brunette" in v:
            return "brown"
        if "red" in v or "auburn" in v or "ginger" in v:
            return "red"
        if "silver" in v or "white" in v:
            return "silver/white"
        if "grey" in v or "gray" in v:
            return "grey"
    elif trait_type == "status":
        if "dead" in v or "deceased" in v:
            return "deceased"
        if "alive" in v:
            return "alive"
    return v


def extract_traits_from_text(text: str) -> dict:
    found = {}
    for trait_name, patterns in TRAIT_PATTERNS.items():
        for pat in patterns:
            for m in pat.finditer(text):
                val = m.group(1) if m.groups() else m.group(0)
                norm = normalize_trait(trait_name, val)
                if trait_name not in found:
                    found[trait_name] = []
                if norm not in found[trait_name]:
                    found[trait_name].append(norm)
    return found


def extract_lore_profiles(world_dir: Path) -> dict:
    """Scans World Bible character files and extracts baseline entity profiles."""
    profiles = {}
    char_dirs = [world_dir / "Characters", world_dir / "00-World-Bible" / "Characters", world_dir]
    
    for cdir in char_dirs:
        if not cdir.is_dir():
            continue
        for md_file in cdir.glob("*.md"):
            if md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                entity_name = md_file.stem
                
                # Check YAML frontmatter name
                fm_match = FRONTMATTER_REGEX.match(content)
                if fm_match:
                    for line in fm_match.group(1).splitlines():
                        if line.startswith("name:"):
                            entity_name = line.split(":", 1)[1].strip().strip("\"'")
                            break

                traits = extract_traits_from_text(content)
                profiles[entity_name] = {
                    "file": str(md_file.relative_to(world_dir)).replace("\\", "/"),
                    "traits": traits
                }
            except Exception as e:
                logger.warning("Failed to read lore profile from %s: %s", md_file, e)
    return profiles


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

_WORD_BOUNDARY_CACHE: dict = {}
_POSSESSIVE_CACHE: dict = {}


def _get_word_boundary_regex(word: str) -> re.Pattern:
    pat = _WORD_BOUNDARY_CACHE.get(word)
    if pat is None:
        pat = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
        _WORD_BOUNDARY_CACHE[word] = pat
    return pat


def _get_possessive_regex(word: str) -> re.Pattern:
    pat = _POSSESSIVE_CACHE.get(word)
    if pat is None:
        pat = re.compile(r"\b" + re.escape(word) + r"(?:'s|'|’s)\b", re.IGNORECASE)
        _POSSESSIVE_CACHE[word] = pat
    return pat


def _chars_mentioned(text: str, candidates: list) -> list:
    return [c for c in candidates if _get_word_boundary_regex(c).search(text)]


def attribute_sentence_trait(sentence: str, scene_chars: list, profiles: dict) -> list:
    """CNT-01 sentence-level attribution.

    Returns [(char_name, confidence)] where confidence is 'high' (possessive
    binding or single explicit mention) or 'medium' (single @pov/@char
    context with no competing mention). Ambiguous multi-character
    sentences without possessive binding return [] — no contradiction is
    emitted when ownership is unclear. Pronouns are never resolved.
    """
    mentioned = _chars_mentioned(sentence, list(profiles.keys()) + scene_chars)
    # De-duplicate preserving order.
    seen = set()
    ordered = []
    for c in mentioned:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(c)
    # Canonicalise to profile names when case differs.
    canon = []
    lower_profiles = {p.lower(): p for p in profiles}
    for c in ordered:
        canon.append(lower_profiles.get(c.lower(), c))

    # 1. Possessive binding wins: "Alice's green eyes" -> Alice only.
    for c in canon:
        if _get_possessive_regex(c).search(sentence):
            return [(c, "high")]

    # 2. Exactly one known character in the sentence -> that character.
    profile_mentions = [c for c in canon if c in profiles]
    if len(profile_mentions) == 1:
        return [(profile_mentions[0], "high")]
    if len(profile_mentions) > 1:
        return []

    # 3. No explicit mention: fall back to scene context only when it is
    # unambiguous (exactly one active character).
    ctx = [c for c in scene_chars]
    if len(ctx) == 1:
        owner = lower_profiles.get(ctx[0].lower(), ctx[0])
        return [(owner, "medium")]
    return []


def scan_manuscript_scenes(manuscript_dir: Path, profiles: dict) -> list:
    """Scans manuscript scene files and detects narrative trait contradictions."""
    findings = []
    warnings: list = []

    # Store scene-level character trait mentions across chapters
    scene_mentions = {}  # {entity_name: [(file, line_no, trait_type, trait_val)]}

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if ".git" in md_file.parts or md_file.name.startswith("."):
            continue
        try:
            rel_path = str(md_file.relative_to(manuscript_dir)).replace("\\", "/")
            try:
                lines = md_file.read_text(encoding="utf-8", errors="strict").splitlines()
            except (OSError, UnicodeError) as e:
                # CNT-02: surface unreadable files instead of silently skipping.
                warnings.append({"file": rel_path, "error": f"unreadable scene file: {e}"})
                logger.warning("Skipping unreadable scene file %s: %s", md_file, e)
                continue

            # Find active POV / Characters in scene
            scene_chars = []
            for line in lines[:20]:
                if line.lower().startswith("@pov:") or line.lower().startswith("@char:") or line.lower().startswith("@characters:"):
                    raw_chars = line.split(":", 1)[1].split(",")
                    for c in raw_chars:
                        c_clean = c.strip().strip("[]\"'")
                        if c_clean and c_clean not in scene_chars:
                            scene_chars.append(c_clean)

            # If no tags, check mentions of known characters
            if not scene_chars:
                full_text = "\n".join(lines)
                for entity in profiles:
                    if _get_word_boundary_regex(entity).search(full_text):
                        scene_chars.append(entity)

            # Analyze text for trait assertions (sentence-level, CNT-01)
            for line_idx, line in enumerate(lines, 1):
                if line.startswith("@") or line.startswith("#") or not line.strip():
                    continue

                for sentence in SENTENCE_SPLIT.split(line):
                    if not sentence.strip():
                        continue
                    sent_traits = extract_traits_from_text(sentence)
                    if not sent_traits:
                        continue
                    targets = attribute_sentence_trait(sentence, scene_chars, profiles)
                    if not targets:
                        continue
                    for trait_type, vals in sent_traits.items():
                        for val in vals:
                            for char_name, confidence in targets:
                                if char_name not in scene_mentions:
                                    scene_mentions[char_name] = []
                                scene_mentions[char_name].append((rel_path, line_idx, trait_type, val))

                                # Compare against World Bible truth
                                if char_name in profiles:
                                    bible_traits = profiles[char_name]["traits"].get(trait_type, [])
                                    if bible_traits and val not in bible_traits:
                                        if confidence == "high":
                                            findings.append({
                                                "id": "CNT-101",
                                                "severity": "WARNING",
                                                "entity": char_name,
                                                "trait": trait_type,
                                                "expected": "/".join(bible_traits),
                                                "found": val,
                                                "file": rel_path,
                                                "line": line_idx,
                                                "confidence": confidence,
                                                "message": f"Character '{char_name}' has lore {trait_type} '{'/'.join(bible_traits)}' in World Bible, but scene asserts '{val}'."
                                            })
                                        else:
                                            findings.append({
                                                "id": "CNT-101",
                                                "severity": "ADVISORY",
                                                "entity": char_name,
                                                "trait": trait_type,
                                                "expected": "/".join(bible_traits),
                                                "found": val,
                                                "file": rel_path,
                                                "line": line_idx,
                                                "confidence": confidence,
                                                "message": f"Character '{char_name}' has lore {trait_type} '{'/'.join(bible_traits)}' in World Bible, but scene (single-character context) asserts '{val}'."
                                            })
        except Exception as e:
            warnings.append({"file": str(md_file), "error": str(e)})
            logger.warning("Failed to scan scene file %s: %s", md_file, e)

    # Compare inter-scene trait consistency (e.g. Book 1 vs Book 2)
    for char_name, mentions in scene_mentions.items():
        by_trait = {}
        for file_path, line_no, t_type, val in mentions:
            if t_type not in by_trait:
                by_trait[t_type] = []
            by_trait[t_type].append((file_path, line_no, val))

        for t_type, occurrences in by_trait.items():
            distinct_vals = set(val for _, _, val in occurrences)
            if len(distinct_vals) > 1:
                # Contradiction across scenes!
                first_f, first_l, first_v = occurrences[0]
                for file_path, line_no, v in occurrences[1:]:
                    if v != first_v:
                        findings.append({
                            "id": "CNT-102",
                            "severity": "ADVISORY",
                            "entity": char_name,
                            "trait": t_type,
                            "expected": first_v,
                            "found": v,
                            "file": file_path,
                            "line": line_no,
                            "message": f"Character '{char_name}' has conflicting {t_type} assertions across scenes: '{first_v}' in {first_f}:{first_l} vs '{v}' in {file_path}:{line_no}."
                        })
                        break

    # Attach warnings for callers that surface them (CNT-02).
    scan_manuscript_scenes.last_warnings = warnings  # type: ignore[attr-defined]
    return findings


def run_continuity_audit(world_dir: str, manuscript_dir: str) -> dict:
    wpath = Path(world_dir).resolve()
    mpath = Path(manuscript_dir).resolve() if manuscript_dir else None

    profiles = extract_lore_profiles(wpath)
    findings = []
    warnings: list = []

    if mpath and mpath.is_dir():
        findings = scan_manuscript_scenes(mpath, profiles)
        warnings = list(getattr(scan_manuscript_scenes, "last_warnings", []))

    return {
        "world": wpath.name,
        "manuscript": mpath.name if mpath else None,
        "entities_profiled": len(profiles),
        "total_findings": len(findings),
        "findings": findings,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Local Semantic Continuity Engine")
    parser.add_argument("-w", "--world", help="World Bible lore directory")
    parser.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    # Discover world / manuscript if not provided (CNT-02: deterministic,
    # ambiguity-failing — never silently pick universes[0] / mss[0]).
    world_dir = args.world
    manuscript_dir = args.manuscript

    if not world_dir:
        home = Path.home()
        universes = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
        # Filter out non-world dirs (files named Worlds, dotfiles already excluded by glob).
        universes = [p for p in universes if p.is_dir() and p.name not in ("Worlds", ".git")]
        if len(universes) == 1:
            world_dir = str(universes[0])
        elif len(universes) > 1:
            print("Error: Multiple worlds discovered — specify one with -w/--world:", file=sys.stderr)
            for p in universes:
                print(f"  - {p.name}  [{p.parent.name}]  {p}", file=sys.stderr)
            sys.exit(2)
        else:
            worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
            worlds = [p for p in worlds if p.is_dir()]
            if len(worlds) == 1:
                world_dir = str(worlds[0])
            elif len(worlds) > 1:
                print("Error: Multiple legacy worlds discovered — specify one with -w/--world:", file=sys.stderr)
                for p in worlds:
                    print(f"  - {p}", file=sys.stderr)
                sys.exit(2)

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    if not manuscript_dir:
        home = Path.home()
        mss = sorted((home / "Manuscripts").glob("*"), key=lambda p: str(p))
        mss = [p for p in mss if p.is_dir()]
        if len(mss) == 1:
            manuscript_dir = str(mss[0])
        elif len(mss) > 1:
            print("Note: Multiple manuscripts discovered; auditing without manuscript cross-check.", file=sys.stderr)
            print("Re-run with -m/--manuscript to select one:", file=sys.stderr)
            for p in mss:
                print(f"  - {p.name}  {p}", file=sys.stderr)
            manuscript_dir = ""

    report = run_continuity_audit(world_dir, manuscript_dir or "")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Ars Arcanum Narrative Continuity Report ===")
        print(f"World: {report['world']} | Manuscript: {report['manuscript'] or 'N/A'}")
        print(f"Profiled Entities: {report['entities_profiled']}")
        print(f"Continuity Findings: {report['total_findings']}")
        if report.get("warnings"):
            print(f"File Warnings: {len(report['warnings'])}")
        print()

        if not report["findings"]:
            print("[OK] Narrative continuity clean. No contradictory traits or entity paradoxes detected.")
        else:
            for f in report["findings"]:
                badge = f"[{f['severity']}]"
                print(f"{badge} {f['id']} ({f['entity']}): {f['message']}")
                print(f"     Location: {f['file']}:{f['line']}\n")
        if report.get("warnings"):
            print("Warnings (incomplete audit — files skipped):")
            for w in report["warnings"]:
                print(f"  [!] {w.get('file')}: {w.get('error')}")

    sys.exit(1 if report["total_findings"] > 0 else 0)


if __name__ == "__main__":
    main()
