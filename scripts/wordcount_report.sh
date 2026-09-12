#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Wordcount & Progress Report (D-03)
# Purpose: Single-pass manuscript analytics: word counts per chapter, act and
#          book, plus novelWriter @status breakdown. Read-only; never touches
#          manuscript files.
#
# Usage:
#   wordcount_report.sh [WORLD_DIR] [OPTIONS]
#
# Options:
#   --markdown    Emit a Markdown table (for pasting into the Daily Writing Log)
#   -h, --help    Show this help
#
# Exit codes:
#   0  report produced (even if counts are zero)
#   1  internal error
#   2  usage/environment error (world dir missing, python3 missing)
# ==============================================================================
set -euo pipefail

usage() {
    sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

WORLD_DIR=""
MARKDOWN=0
while [ $# -gt 0 ]; do
    case "$1" in
        --markdown) MARKDOWN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) WORLD_DIR="$1"; shift ;;
    esac
done

[ -d "${WORLD_DIR}" ] || { echo "Error: world directory not found: ${WORLD_DIR}" >&2; exit 2; }
MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"
[ -d "${MANUSCRIPT_DIR}" ] || { echo "Error: no 01-Manuscript folder in ${WORLD_DIR}" >&2; exit 2; }
command -v python3 &>/dev/null || { echo "Error: python3 is required." >&2; exit 2; }

MANUSCRIPT_DIR="${MANUSCRIPT_DIR}" MARKDOWN="${MARKDOWN}" python3 - << 'PYEOF'
import os
import re
import sys

MS = os.environ["MANUSCRIPT_DIR"]
MD = os.environ["MARKDOWN"] == "1"
MAX_BYTES = 8 * 1024 * 1024
TAG = re.compile(r"^@[A-Za-z0-9_-]+:\s*(.*)$", re.M)
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
                text = fh.read(MAX_BYTES).decode("utf-8", "ignore")
        except OSError:
            continue
        # strip novelWriter metadata lines and % comments before counting
        body = re.sub(r"^@[A-Za-z0-9_-]+:.*$", "", text, flags=re.M)
        body = re.sub(r"^%.*$", "", body, flags=re.M)
        words = len(WORD.findall(body))
        m = re.search(r"^@status:\s*(.+)$", text, re.M)
        status = m.group(1).strip() if m else "-"
        rows.append((book, act, stem, words, status))

rows.sort(key=lambda r: (r[0], r[1], r[2]))

def sum_by(idx):
    agg = {}
    for r in rows:
        agg[r[idx]] = agg.get(r[idx], 0) + r[3]
    return agg

by_book = sum_by(0)
by_status = sum_by(4)
total = sum(r[3] for r in rows)
chapters = len(rows)
draft, revision, finished = (by_status.get(s, 0) for s in ("Draft", "Revision", "Finished"))

if MD:
    print("| Book | Act | Chapter | Words | Status |")
    print("|---|---|---|---:|---|")
    for book, act, ch, w, st in rows:
        print(f"| {book} | {act} | {ch} | {w} | {st} |")
    print(f"| **Total** |  | {chapters} chapters | **{total}** |  |")
else:
    print(f"Scriptorium Wordcount Report — {MS}")
    print(f"Chapters: {chapters}    Total words: {total:,}\n")
    print("By volume:")
    for b in sorted(by_book):
        print(f"  {b:<12} {by_book[b]:>10,} words")
    print("\nBy @status (words):")
    for s in sorted(by_status):
        print(f"  {s:<12} {by_status[s]:>10,}")
    print("\nPer chapter:")
    for book, act, ch, w, st in rows:
        print(f"  {book}/{act}/{ch}  {w:>7,}  [{st}]")

sys.exit(0)
PYEOF
