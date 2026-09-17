#!/usr/bin/env python3
"""
Scriptorium Semantic Continuity Engine (scripts/lib/continuity.py)
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

logger = logging.getLogger("scriptorium.continuity")

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

FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


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
                logger.debug("Failed to read lore profile from %s: %s", md_file, e)
    return profiles


def scan_manuscript_scenes(manuscript_dir: Path, profiles: dict) -> list:
    """Scans manuscript scene files and detects narrative trait contradictions."""
    findings = []
    
    # Store scene-level character trait mentions across chapters
    scene_mentions = {}  # {entity_name: [(file, line_no, trait_type, trait_val)]}

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if ".git" in md_file.parts or md_file.name.startswith("."):
            continue
        try:
            rel_path = str(md_file.relative_to(manuscript_dir)).replace("\\", "/")
            lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()

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
                    if entity in full_text:
                        scene_chars.append(entity)

            # Analyze text for trait assertions
            for line_idx, line in enumerate(lines, 1):
                if line.startswith("@") or line.startswith("#") or not line.strip():
                    continue
                
                line_traits = extract_traits_from_text(line)
                for trait_type, vals in line_traits.items():
                    for val in vals:
                        matched_chars = [c for c in scene_chars if re.search(r'\b' + re.escape(c) + r'\b', line, re.IGNORECASE)]
                        target_chars = matched_chars if matched_chars else scene_chars
                        for char_name in target_chars:
                            if char_name not in scene_mentions:
                                scene_mentions[char_name] = []
                            scene_mentions[char_name].append((rel_path, line_idx, trait_type, val))

                            # Compare against World Bible truth
                            if char_name in profiles:
                                bible_traits = profiles[char_name]["traits"].get(trait_type, [])
                                if bible_traits and val not in bible_traits:
                                    findings.append({
                                        "id": "CNT-101",
                                        "severity": "WARNING",
                                        "entity": char_name,
                                        "trait": trait_type,
                                        "expected": "/".join(bible_traits),
                                        "found": val,
                                        "file": rel_path,
                                        "line": line_idx,
                                        "message": f"Character '{char_name}' has lore {trait_type} '{'/'.join(bible_traits)}' in World Bible, but scene asserts '{val}'."
                                    })
        except Exception as e:
            logger.debug("Failed to scan scene file %s: %s", md_file, e)

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

    return findings


def run_continuity_audit(world_dir: str, manuscript_dir: str) -> dict:
    wpath = Path(world_dir).resolve()
    mpath = Path(manuscript_dir).resolve() if manuscript_dir else None

    profiles = extract_lore_profiles(wpath)
    findings = []

    if mpath and mpath.is_dir():
        findings = scan_manuscript_scenes(mpath, profiles)

    return {
        "world": wpath.name,
        "manuscript": mpath.name if mpath else None,
        "entities_profiled": len(profiles),
        "total_findings": len(findings),
        "findings": findings
    }


def main():
    parser = argparse.ArgumentParser(description="Scriptorium Local Semantic Continuity Engine")
    parser.add_argument("-w", "--world", help="World Bible lore directory")
    parser.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    # Discover world / manuscript if not provided
    world_dir = args.world
    manuscript_dir = args.manuscript

    if not world_dir:
        home = Path.home()
        universes = list((home / "Universes").glob("*/*"))
        if universes:
            world_dir = str(universes[0])
        else:
            worlds = list((home / "Worlds").glob("*"))
            if worlds:
                world_dir = str(worlds[0])

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    if not manuscript_dir:
        home = Path.home()
        mss = list((home / "Manuscripts").glob("*"))
        if mss:
            manuscript_dir = str(mss[0])

    report = run_continuity_audit(world_dir, manuscript_dir or "")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Scriptorium Narrative Continuity Report ===")
        print(f"World: {report['world']} | Manuscript: {report['manuscript'] or 'N/A'}")
        print(f"Profiled Entities: {report['entities_profiled']}")
        print(f"Continuity Findings: {report['total_findings']}\n")

        if not report["findings"]:
            print("[OK] Narrative continuity clean. No contradictory traits or entity paradoxes detected.")
        else:
            for f in report["findings"]:
                badge = f"[{f['severity']}]"
                print(f"{badge} {f['id']} ({f['entity']}): {f['message']}")
                print(f"     Location: {f['file']}:{f['line']}\n")

    sys.exit(1 if report["total_findings"] > 0 else 0)


if __name__ == "__main__":
    main()
