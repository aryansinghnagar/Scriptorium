#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Wordcount & Progress Report (D-03 / Workstream 3.3)
# Purpose: Single-pass manuscript analytics: word counts per chapter, act, and
#          book, plus novelWriter @status breakdown. Read-only; never touches
#          manuscript files.
#
# Usage:
#   wordcount_report.sh [WORLD_DIR] [OPTIONS]
#
# Options:
#   --markdown    Emit a Markdown table (for pasting into the Daily Writing Log)
#   --json        Emit machine-readable JSON analytics
#   -h, --help    Show this help
#
# Exit codes:
#   0  report produced (even if counts are zero)
#   1  internal error
#   2  usage/environment error (world dir missing, python3 missing)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01, F-05)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

WORLD_DIR=""
MARKDOWN=0
JSON_OUT=0
while [ $# -gt 0 ]; do
    case "$1" in
        --markdown) MARKDOWN=1; shift ;;
        --json) JSON_OUT=1; shift ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) WORLD_DIR="$1"; shift ;;
    esac
done

# F-05: a bare invocation now discovers worlds (auto-selecting when exactly
# one exists) instead of defaulting to ~/Worlds, which is a container of
# worlds and never itself a world.
if [ -z "${WORLD_DIR}" ]; then
    discover_worlds FOUND_WORLDS
    if [ ${#FOUND_WORLDS[@]} -eq 1 ]; then
        WORLD_DIR="${FOUND_WORLDS[0]}"
    elif [ ${#FOUND_WORLDS[@]} -gt 1 ]; then
        {
            echo "Multiple worlds discovered — specify one:"
            for w in "${FOUND_WORLDS[@]}"; do
                echo "  - $(basename "$w")  [$(universe_label "$w")]  ${w}"
            done
            echo "Usage: wordcount_report.sh <WORLD_DIR|WORLD_NAME> [--markdown|--json]"
        } >&2
        exit 2
    else
        echo "Error: no worlds found under ~/Universes or ~/Worlds. Create one first (scriptorium init <name>)." >&2
        exit 2
    fi
else
    RESOLVED="$(resolve_world_dir "${WORLD_DIR}")"
    if [ -n "${RESOLVED}" ]; then
        WORLD_DIR="${RESOLVED}"
    fi
fi

[ -d "${WORLD_DIR}" ] || { echo "Error: world directory not found: ${WORLD_DIR}" >&2; exit 2; }
MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"
[ -d "${MANUSCRIPT_DIR}" ] || { echo "Error: no 01-Manuscript folder in ${WORLD_DIR}" >&2; exit 2; }
command -v python3 &>/dev/null || { echo "Error: python3 is required." >&2; exit 2; }

MANUSCRIPT_DIR="${MANUSCRIPT_DIR}" MARKDOWN="${MARKDOWN}" JSON_OUT="${JSON_OUT}" python3 - << 'PYEOF'
import os
import re
import sys
import json

MS = os.environ["MANUSCRIPT_DIR"]
MD = os.environ["MARKDOWN"] == "1"
IS_JSON = os.environ["JSON_OUT"] == "1"
MAX_BYTES = 8 * 1024 * 1024
WORD = re.compile(r"\S+")

rows = []  # (book, act, chapter, words, status)
for root, dirs, files in os.walk(MS):
    dirs[:] = sorted(d for d in dirs if d != "Outlines")
    for fname in sorted(files):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(root, fname)
        rel = os.path.relpath(path, MS)
        parts = rel.split(os.sep)
        book = parts[0] if parts[0].startswith("Book-") else "(root)"
        act = parts[1] if len(parts) >= 3 else "-"
        stem = os.path.splitext(fname)[0]
        try:
            with open(path, "rb") as fh:
                data = fh.read(MAX_BYTES + 1)
        except OSError:
            continue
        if len(data) > MAX_BYTES:
            # F-08: surface silent truncation instead of under-counting.
            print(f"[!] Warning: {path} exceeds the {MAX_BYTES // (1024 * 1024)} MB read cap; word counts truncated at the cap.", file=sys.stderr)
            data = data[:MAX_BYTES]
        text = data.decode("utf-8", "ignore")
        body = re.sub(r"^@[A-Za-z0-9_-]+:.*$", "", text, flags=re.M)
        body = re.sub(r"^%.*$", "", body, flags=re.M)
        words = len(WORD.findall(body))
        m = re.search(r"^@status:\s*(.+)$", text, re.M)
        status = m.group(1).strip() if m else "Draft"
        rows.append((book, act, stem, words, status))

rows.sort(key=lambda r: (r[0], r[1], r[2]))

def sum_by(idx):
    agg = {}
    for r in rows:
        agg[r[idx]] = agg.get(r[idx], 0) + r[3]
    return agg

by_book = sum_by(0)
by_status = sum_by(4)
total_words = sum(r[3] for r in rows)
chapter_count = len(rows)

if IS_JSON:
    report = {
        "manuscript_dir": MS,
        "total_words": total_words,
        "chapter_count": chapter_count,
        "by_volume": by_book,
        "by_status": by_status,
        "chapters": [
            {"volume": b, "act": a, "chapter": c, "words": w, "status": s}
            for b, a, c, w, s in rows
        ]
    }
    print(json.dumps(report, indent=2))
elif MD:
    print("| Volume | Act | Chapter | Words | Status |")
    print("|---|---|---|---:|---|")
    for book, act, ch, w, st in rows:
        print(f"| {book} | {act} | {ch} | {w:,} | {st} |")
    print(f"| **Total** | | **{chapter_count} chapters** | **{total_words:,} words** | |")
else:
    print(f"Scriptorium Wordcount Report — {MS}")
    print(f"Chapters: {chapter_count:<8} Total words: {total_words:,}\n")
    print("By Volume:")
    for b in sorted(by_book):
        print(f"  {b:<16} {by_book[b]:>10,} words")
    print("\nBy Status:")
    for s in sorted(by_status):
        print(f"  {s:<16} {by_status[s]:>10,} words")
    print("\nChapter Breakdown:")
    for book, act, ch, w, st in rows:
        print(f"  {book}/{act}/{ch:<25} {w:>7,}  [{st}]")

sys.exit(0)
PYEOF
