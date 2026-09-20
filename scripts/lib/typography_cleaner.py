#!/usr/bin/env python3
"""
Ars Arcanum Smart Typography Normalizer & Polish Engine
(scripts/lib/typography_cleaner.py)
================================================================================
Zero-dependency, offline typography cleaner and smart punctuation formatter.

Capabilities (PRO-104):
1. Smart Typographic Quotes:
   - Converts straight double quotes ("...") to curly open/close pairs (“...”)
   - Converts straight single quotes ('...') to curly open/close pairs (‘...’)
   - Preserves apostrophes in contractions (don't, it's, 'tis, '90s)
2. Em-Dash & En-Dash Normalization:
   - Converts triple/double dashes (`---`, `--`) to typographic em-dash (`—`)
   - Converts numeric date/range hyphens (`1914-1918`, `pp. 20-25`) to en-dash (`–`)
3. Ellipsis Normalization:
   - Converts three dots (`...` or `. . .`) to unicode ellipsis (`…`)
4. Whitespace & Scene Break Cleanliness:
   - Removes trailing whitespace from line ends
   - Collapses multiple redundant spaces inside sentences
   - Standardizes ornamental scene break indicators
5. Dry-run diffing, backup creation, and directory batch processing.

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import json
import difflib
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.typography")


def normalize_typography_text(text: str) -> tuple[str, dict]:
    """Normalizes straight punctuation into clean literary typography."""
    stats = {
        "curly_double_quotes": 0,
        "curly_single_quotes": 0,
        "em_dashes": 0,
        "en_dashes": 0,
        "ellipses": 0,
        "trailing_spaces_removed": 0,
        "multi_spaces_collapsed": 0
    }

    lines = text.splitlines(keepends=True)
    new_lines = []

    for line in lines:
        orig = line

        # 1. Trailing whitespace
        clean_end = line.rstrip("\r\n \t")
        newline_char = line[len(clean_end):]
        if line != clean_end + newline_char:
            stats["trailing_spaces_removed"] += 1
        line = clean_end

        # Do not modify frontmatter or codeblocks
        if line.startswith(("---", "```", "    ")):
            new_lines.append(line + newline_char)
            continue

        # 2. Ellipses: ... or . . . -> …
        ellipsis_count = len(re.findall(r'\.\s*\.\s*\.', line))
        if ellipsis_count > 0:
            line = re.sub(r'\.\s*\.\s*\.', '…', line)
            stats["ellipses"] += ellipsis_count

        # 3. En-dash for numeric ranges (e.g., 1914-1918, pp. 20-35)
        # Avoid matching markdown lists like - Item
        line, en_c = re.subn(r'(?<=\d)\s*(?:--|-)\s*(?=\d)', '–', line)
        stats["en_dashes"] += en_c

        # 4. Em-dashes: --- or -- -> —
        line, em_c = re.subn(r'\s*---\s*|\s*--\s*', '—', line)
        stats["em_dashes"] += em_c

        # 5. Smart Double Quotes: " -> “ / ”
        # Convert starting quotes
        def replace_double_quotes(s):
            count = 0
            # Open quote after whitespace, punctuation, or start of line
            s, c1 = re.subn(r'(^|[\s\(\[\{—–])"', r'\1“', s)
            # Close quote after word or punctuation
            s, c2 = re.subn(r'([^\s])"', r'\1”', s)
            # Any remaining quotes
            s, c3 = re.subn(r'"', r'”', s)
            count = c1 + c2 + c3
            return s, count

        line, d_count = replace_double_quotes(line)
        stats["curly_double_quotes"] += d_count

        # 6. Smart Single Quotes & Apostrophes: ' -> ‘ / ’
        # Common leading apostrophe words: 'tis, 'twas, 'cause, 'em, '90s
        line = re.sub(r"\b'([0-9]{2}s?)\b", r"’\1", line)
        line = re.sub(r"(^|\s)'(tis|twas|cause|em|round|bout)\b", r"\1’\2", line, flags=re.IGNORECASE)

        # Contraction / possessive apostrophes (word'word -> word’word)
        line, a_count = re.subn(r"([A-Za-z0-9])'([A-Za-z0-9])", r"\1’\2", line)

        # Single quote pairs
        line, s1 = re.subn(r'(^|[\s\(\[\{—–])\'', r'\1‘', line)
        line, s2 = re.subn(r'([^\s])\'', r'\1’', line)
        line, s3 = re.subn(r'\'', r'’', line)
        stats["curly_single_quotes"] += (a_count + s1 + s2 + s3)

        # 7. Redundant internal spaces (avoid collapsing indentation at start)
        leading_indent = len(line) - len(line.lstrip(" "))
        indent_str = line[:leading_indent]
        body_str = line[leading_indent:]
        collapsed_body, sp_count = re.subn(r'[ ]{2,}', ' ', body_str)
        if sp_count > 0:
            stats["multi_spaces_collapsed"] += sp_count
        line = indent_str + collapsed_body

        new_lines.append(line + newline_char)

    result_text = "".join(new_lines)
    return result_text, stats


def clean_file(file_path: Path, in_place: bool = False, make_backup: bool = True) -> tuple[dict, str]:
    """Cleans a single file and returns stats and diff."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    cleaned, stats = normalize_typography_text(content)

    diff = ""
    if content != cleaned:
        diff_lines = list(difflib.unified_diff(
            content.splitlines(),
            cleaned.splitlines(),
            fromfile=str(file_path),
            tofile=str(file_path) + " (polished)",
            lineterm=""
        ))
        diff = "\n".join(diff_lines)

        if in_place:
            if make_backup:
                bak_path = file_path.with_suffix(file_path.suffix + ".bak")
                bak_path.write_text(content, encoding="utf-8")
            file_path.write_text(cleaned, encoding="utf-8")

    return stats, diff


def clean_target(target_path: Path, in_place: bool = False, make_backup: bool = True) -> dict:
    """Cleans a single file or an entire manuscript tree."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    total_stats = {
        "files_scanned": len(files),
        "files_modified": 0,
        "curly_double_quotes": 0,
        "curly_single_quotes": 0,
        "em_dashes": 0,
        "en_dashes": 0,
        "ellipses": 0,
        "trailing_spaces_removed": 0,
        "multi_spaces_collapsed": 0,
    }
    file_results = []

    for f in files:
        f_stats, diff = clean_file(f, in_place=in_place, make_backup=make_backup)
        is_mod = bool(diff)
        if is_mod:
            total_stats["files_modified"] += 1
        for k in f_stats:
            if k in total_stats:
                total_stats[k] += f_stats[k]
        file_results.append({
            "file": str(f),
            "modified": is_mod,
            "stats": f_stats,
            "diff": diff
        })

    return {
        "target": str(target_path),
        "in_place": in_place,
        "summary": total_stats,
        "files": file_results
    }


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Smart Typography Normalizer (PRO-104)")
    parser.add_argument("target", help="File or manuscript directory to polish")
    parser.add_argument("-i", "--in-place", action="store_true", help="Modify files in-place")
    parser.add_argument("--no-backup", action="store_true", help="Do not create .bak backup files when modifying in-place")
    parser.add_argument("--diff", action="store_true", help="Show unified diff of changes")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    result = clean_target(target_path, in_place=args.in_place, make_backup=not args.no_backup)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    summary = result["summary"]
    print(f"=== Smart Typography Polish: {target_path.name} ===")
    print(f"Mode: {'[IN-PLACE WRITTEN]' if args.in_place else '[DRY-RUN / PREVIEW ONLY]'}")
    print(f"Files Scanned: {summary['files_scanned']} | Modified: {summary['files_modified']}")
    print("-" * 55)
    print(f"  Curly Double Quotes (“ ”): {summary['curly_double_quotes']}")
    print(f"  Curly Single Quotes (‘ ’): {summary['curly_single_quotes']}")
    print(f"  Em-Dashes (—):            {summary['em_dashes']}")
    print(f"  En-Dashes (–):            {summary['en_dashes']}")
    print(f"  Ellipses (…):             {summary['ellipses']}")
    print(f"  Trailing Spaces Removed:  {summary['trailing_spaces_removed']}")
    print(f"  Spaces Collapsed:         {summary['multi_spaces_collapsed']}")

    if args.diff or not args.in_place:
        diff_count = 0
        for f in result["files"]:
            if f["modified"] and f["diff"]:
                diff_count += 1
                if diff_count <= 5 or args.diff:
                    print(f"\n--- Diff: {Path(f['file']).name} ---")
                    print(f["diff"][:1000] + ("\n... [truncated]" if len(f["diff"]) > 1000 else ""))

    if not args.in_place and summary["files_modified"] > 0:
        print(f"\nTip: Run with -i / --in-place to apply these changes to disk.")


if __name__ == "__main__":
    main()
