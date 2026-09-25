#!/usr/bin/env python3
"""
Ars Arcanum Conlang Phonotactics, Lexicography & Sound-Change Engine (scripts/lib/conlang.py)
===========================================================================================
Local-first linguistic generator, historical sound-shift applier, and lexicon management
tool for fictional constructed languages (conlangs).

Inspects `Languages/<Lang>.md`:
- Frontmatter: consonants, vowels, syllable structures, forbidden clusters, stress rules, sound changes
- Lexicon tables: Foreign Word, Part of Speech, Pronunciation, Translation, Cultural Connotation

Capabilities:
1. Phonotactically Valid Word & Name Generator:
   - Evaluates syllable templates (e.g. CV, CVC, CCV, V, VC)
   - Enforces consonant/vowel inventories and ban-lists on invalid phonetic clusters
2. Historical Sound Shift Rule Applier (Sound Law Engine):
   - Standard notation: A > B / X_Y (e.g. 'p > f / V_V', 'k > ch / _[e,i]', 's > h / #_', 'e > 0 / _#')
3. Lexicon Management & Vocabulary Auditor:
   - Parses, searches, and exports vocabulary tables to CSV, Markdown, or JSON

Zero external runtime dependencies; 100% offline privacy.
"""

import argparse
import csv
import json
import logging
import random
import re
import sys
from pathlib import Path

try:
    import lib._bootstrap  # noqa: F401
except ImportError:
    import _bootstrap  # noqa: F401

logger = logging.getLogger("arcanum.conlang")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)

DEFAULT_CONSONANTS = ["p", "t", "k", "b", "d", "g", "m", "n", "s", "z", "l", "r", "w", "j", "th", "sh", "ch"]
DEFAULT_VOWELS = ["a", "e", "i", "o", "u"]
DEFAULT_SYLLABLES = ["CV", "CVC", "V", "VC"]


try:
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from frontmatter import parse_yaml_frontmatter


def load_conlang_profile(world_dir: Path, lang_query: str) -> dict:
    """Loads language definition note from Languages/ matching query name."""
    dirs_to_check = [
        world_dir / "Languages",
        world_dir / "00-World-Bible" / "Languages",
    ]
    matched_file = None
    q_clean = lang_query.strip().lower()
    q_norm = re.sub(r"[^a-z0-9]", "", q_clean)

    for ldir in dirs_to_check:
        if not ldir.is_dir():
            continue
        for md_file in sorted(ldir.rglob("*.md")):
            if "Template" in md_file.name:
                continue
            stem_norm = re.sub(r"[^a-z0-9]", "", md_file.stem.lower())
            if q_norm in stem_norm or q_clean in md_file.stem.lower().replace("_", " "):
                matched_file = md_file
                break
            # Also check frontmatter name
            try:
                txt = md_file.read_text(encoding="utf-8", errors="replace")
                fm_temp = parse_yaml_frontmatter(txt)
                if fm_temp.get("name") and q_clean in fm_temp["name"].lower():
                    matched_file = md_file
                    break
            except Exception:
                pass
        if matched_file:
            break

    if not matched_file:
        raise FileNotFoundError(f"No language note found matching '{lang_query}' in {world_dir}")

    content = matched_file.read_text(encoding="utf-8", errors="replace")
    fm = parse_yaml_frontmatter(content)

    # Phoneme inventories
    consonants = fm.get("consonants") or DEFAULT_CONSONANTS
    if isinstance(consonants, str):
        consonants = [c.strip() for c in consonants.split(",") if c.strip()]

    vowels = fm.get("vowels") or DEFAULT_VOWELS
    if isinstance(vowels, str):
        vowels = [v.strip() for v in vowels.split(",") if v.strip()]

    syllables = fm.get("syllable_structures") or fm.get("syllables") or DEFAULT_SYLLABLES
    if isinstance(syllables, str):
        syllables = [s.strip() for s in syllables.split(",") if s.strip()]

    forbidden = fm.get("forbidden_clusters") or fm.get("banned_clusters") or []
    if isinstance(forbidden, str):
        forbidden = [f.strip() for f in forbidden.split(",") if f.strip()]

    sound_changes = fm.get("sound_changes") or fm.get("mutation_rules") or []
    if isinstance(sound_changes, str):
        sound_changes = [sc.strip() for sc in sound_changes.split(";") if sc.strip()]

    # Extract Lexicon table from markdown
    lexicon = []
    if "## 3. Essential Lexicon & Vocabulary" in content or "## Lexicon" in content:
        table_lines = []
        capture = False
        for line in content.splitlines():
            if "## 3. Essential Lexicon" in line or "## Lexicon" in line:
                capture = True
                continue
            if capture:
                if line.startswith("## ") or (line.startswith("---") and len(table_lines) > 2):
                    break
                if "|" in line:
                    table_lines.append(line)

        for row in table_lines[2:]:  # skip header and divider
            cols = [c.strip().strip("*") for c in row.split("|")[1:-1]]
            if len(cols) >= 4 and cols[0]:
                lexicon.append({
                    "word": cols[0],
                    "pos": cols[1] if len(cols) > 1 else "",
                    "ipa": cols[2] if len(cols) > 2 else "",
                    "translation": cols[3] if len(cols) > 3 else "",
                    "connotation": cols[4] if len(cols) > 4 else "",
                })

    return {
        "file": str(matched_file.relative_to(world_dir)).replace("\\", "/"),
        "name": fm.get("name") or matched_file.stem,
        "consonants": consonants,
        "vowels": vowels,
        "syllable_structures": syllables,
        "forbidden_clusters": forbidden,
        "stress_rule": fm.get("stress_rule", "penultimate"),
        "sound_changes": sound_changes,
        "lexicon": lexicon,
    }


# ==============================================================================
# Phonotactic Word Generation
# ==============================================================================

def generate_syllable(structure: str, consonants: list, vowels: list, rng: random.Random) -> str:
    """Generates a single syllable matching the structural pattern (e.g. 'CVC', 'CCV')."""
    syl = []
    for char in structure:
        if char == "C":
            syl.append(rng.choice(consonants))
        elif char == "V":
            syl.append(rng.choice(vowels))
        else:
            syl.append(char)
    return "".join(syl)


def generate_words(lang_profile: dict, count: int = 10, num_syllables: int = 2,
                   word_type: str = "word", seed: int | None = None) -> list:
    """Generates phonotactically legal words or names according to the conlang rules."""
    rng = random.Random(seed) if seed is not None else random.Random()
    consonants = lang_profile["consonants"]
    vowels = lang_profile["vowels"]
    syllables = lang_profile["syllable_structures"]
    forbidden = lang_profile["forbidden_clusters"]

    results = []
    attempts = 0
    max_attempts = count * 200

    while len(results) < count and attempts < max_attempts:
        attempts += 1
        syl_count = num_syllables
        if word_type == "name" and num_syllables == 2:
            syl_count = rng.choice([2, 3])
        elif word_type == "place":
            syl_count = rng.choice([2, 3, 4])

        syls = [generate_syllable(rng.choice(syllables), consonants, vowels, rng) for _ in range(syl_count)]
        candidate = "".join(syls)

        # Check forbidden clusters
        is_legal = True
        for fc in forbidden:
            if fc and fc in candidate:
                is_legal = False
                break

        # Check triple repeating characters
        if re.search(r"(.)\1\1", candidate):
            is_legal = False

        if is_legal:
            if word_type in ("name", "place"):
                candidate = candidate.capitalize()
            if candidate not in results:
                results.append(candidate)

    return results


# ==============================================================================
# Historical Sound-Change Applier
# ==============================================================================

def compile_sound_rule(rule_str: str, vowels: list, consonants: list):
    """
    Parses linguistic sound change rule e.g. 'p > f / V_V' or 'k > ch / _[e,i]'.
    Returns a transformer function: word -> mutated_word.
    """
    rule = rule_str.strip()
    if ">" not in rule:
        return lambda w: w

    parts = rule.split(">", 1)
    source = parts[0].strip()
    target_and_env = parts[1].split("/", 1)
    target = target_and_env[0].strip()
    if target in ("0", "null", "none", "Ø"):
        target = ""

    env = target_and_env[1].strip() if len(target_and_env) > 1 else "_"

    v_set = "|".join(re.escape(v) for v in sorted(vowels, key=len, reverse=True))
    c_set = "|".join(re.escape(c) for c in sorted(consonants, key=len, reverse=True))

    left_env, right_env = env.split("_", 1) if "_" in env else ("", "")

    def prep_env(e_str: str, is_left: bool) -> str:
        if not e_str:
            return ""
        s = e_str
        s = s.replace("#", "^") if is_left else s.replace("#", "$")
        s = re.sub(r"(?<!\\)V", f"(?:{v_set})", s)
        s = re.sub(r"(?<!\\)C", f"(?:{c_set})", s)
        def _repl_b(m):
            items = [re.escape(x.strip()) for x in m.group(1).split(",") if x.strip()]
            return f"(?:{'|'.join(items)})"
        s = re.sub(r"\[(.*?)\]", _repl_b, s)
        return s

    left_re = prep_env(left_env, True)
    right_re = prep_env(right_env, False)

    if source == "V":
        src_re = f"(?:{v_set})"
    elif source == "C":
        src_re = f"(?:{c_set})"
    else:
        src_re = re.escape(source)

    full_pattern = f"(?i)({left_re})({src_re})({right_re})"

    try:
        compiled_re = re.compile(full_pattern)
    except re.error as e:
        logger.warning("Failed to compile sound change rule '%s': %s", rule_str, e)
        return lambda w: w

    def apply_rule(word: str) -> str:
        return compiled_re.sub(lambda m: (m.group(1) or "") + target + (m.group(3) or ""), word)

    return apply_rule


def mutate_text(text: str, rules: list, vowels: list, consonants: list) -> str:
    """Applies a sequence of historical sound change rules to a word or prose text."""
    compiled_rules = [compile_sound_rule(r, vowels, consonants) for r in rules if r.strip()]
    
    def mutate_single_word(w: str) -> str:
        is_cap = w.istitle()
        curr = w.lower()
        for rule_fn in compiled_rules:
            curr = rule_fn(curr)
        return curr.capitalize() if is_cap else curr

    # Match words preserving punctuation and spacing
    return re.sub(r"[A-Za-z]+", lambda m: mutate_single_word(m.group(0)), text)


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

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
        print("Error: Multiple worlds discovered — specify one with -w/--world.", file=sys.stderr)
        sys.exit(2)
    else:
        worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
        worlds = [p for p in worlds if p.is_dir()]
        if len(worlds) == 1:
            return str(worlds[0])
        elif len(worlds) > 1:
            print("Error: Multiple legacy worlds discovered — specify one with -w/--world.", file=sys.stderr)
            sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Conlang Phonotactics & Sound Law Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Conlang subcommands")

    # 1. generate
    p_gen = subparsers.add_parser("generate", help="Generate phonotactically legal words, names or places")
    p_gen.add_argument("language", help="Language name (matches Languages/<Lang>.md)")
    p_gen.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_gen.add_argument("-n", "--count", type=int, default=10, help="Number of items to generate (default: 10)")
    p_gen.add_argument("-s", "--syllables", type=int, default=2, help="Number of syllables (default: 2)")
    p_gen.add_argument("-t", "--type", choices=["word", "name", "place"], default="name", help="Type of generation")
    p_gen.add_argument("--seed", type=int, help="Optional deterministic random seed")
    p_gen.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 2. mutate
    p_mut = subparsers.add_parser("mutate", help="Apply historical sound changes and phonological shifts")
    p_mut.add_argument("language", help="Language name")
    p_mut.add_argument("input", nargs="?", help="Word or text string to mutate")
    p_mut.add_argument("--text", help="Text passage to mutate")
    p_mut.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_mut.add_argument("-r", "--rule", action="append", help="Ad-hoc sound change rule (e.g. 'p > f / V_V')")
    p_mut.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. lexicon
    p_lex = subparsers.add_parser("lexicon", help="Inspect and search language lexicon table")
    p_lex.add_argument("language", help="Language name")
    p_lex.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_lex.add_argument("-q", "--query", help="Search word or English translation")
    p_lex.add_argument("--export-csv", help="Export lexicon to CSV file")
    p_lex.add_argument("--markdown", action="store_true", help="Print as Markdown table")
    p_lex.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    # Discover world
    raw_w = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir = resolve_world_dir(raw_w)

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    try:
        profile = load_conlang_profile(Path(world_dir), args.language)

        if args.subcommand == "generate":
            generated = generate_words(
                profile,
                count=args.count,
                num_syllables=args.syllables,
                word_type=args.type,
                seed=args.seed
            )
            if args.json:
                print(json.dumps({
                    "language": profile["name"],
                    "type": args.type,
                    "syllables": args.syllables,
                    "words": generated
                }, indent=2))
            else:
                print(f"\n\033[1;36m=== Conlang Generator: {profile['name']} ===\033[0m")
                print(f"Syllable Structures: \033[32m{', '.join(profile['syllable_structures'])}\033[0m | Stress: \033[33m{profile['stress_rule']}\033[0m")
                print(f"Generated {args.count} {args.type}s:\n")
                for w in generated:
                    print(f"  ✨ \033[1m{w}\033[0m")
                print()

        elif args.subcommand == "mutate":
            target_text = args.input or args.text or ""
            rules = args.rule or profile.get("sound_changes", [])
            if not rules:
                print("Note: No sound-change rules defined in language note or --rule arguments.", file=sys.stderr)

            mutated = mutate_text(target_text, rules, profile["vowels"], profile["consonants"])

            if args.json:
                print(json.dumps({
                    "language": profile["name"],
                    "original": target_text,
                    "mutated": mutated,
                    "rules_applied": rules
                }, indent=2))
            else:
                print(f"\n\033[1;36m=== Sound-Change Mutation: {profile['name']} ===\033[0m")
                print(f"Rules Applied: \033[33m{'; '.join(rules) if rules else 'None'}\033[0m\n")
                print(f"  Original: \033[90m{target_text}\033[0m")
                print(f"  Shifted:  \033[1;32m{mutated}\033[0m\n")

        elif args.subcommand == "lexicon":
            lex = profile.get("lexicon", [])
            if args.query:
                q = args.query.lower()
                lex = [entry for entry in lex if q in entry["word"].lower() or q in entry["translation"].lower() or q in entry.get("connotation", "").lower()]

            if args.export_csv:
                csv_path = Path(args.export_csv)
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["word", "pos", "ipa", "translation", "connotation"])
                    writer.writeheader()
                    writer.writerows(lex)
                print(f"Exported {len(lex)} lexicon entries to: {csv_path}")

            elif args.json:
                print(json.dumps({"language": profile["name"], "count": len(lex), "lexicon": lex}, indent=2))
            elif args.markdown:
                print("\n| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |")
                print("| :--- | :--- | :--- | :--- | :--- |")
                for e in lex:
                    print(f"| *{e['word']}* | {e['pos']} | {e['ipa']} | {e['translation']} | {e['connotation']} |")
            else:
                print(f"\n\033[1;36m=== Conlang Lexicon: {profile['name']} ({len(lex)} Entries) ===\033[0m\n")
                for e in lex:
                    print(f"  \033[1;32m{e['word']:<14}\033[0m \033[90m[{e['pos']}]\033[0m \033[36m{e['ipa']:<12}\033[0m -> \033[1m{e['translation']}\033[0m \033[33m({e['connotation']})\033[0m")
                print()

    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
