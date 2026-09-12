#!/usr/bin/env bash
# Scriptorium verification harness (D10)
# Usage: bash scripts/verify.sh
# Stages 1-5 are static checks; stage 6 exercises the full world lifecycle
# (init -> export -> snapshot) in a sandboxed HOME so integration defects
# cannot hide behind "syntax OK" (P-05).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP_VERIFY="$(mktemp -d)"
trap 'rm -rf "${TMP_VERIFY:-}"' EXIT

echo "[1/6] bash -n syntax..."
for f in scripts/*.sh; do bash -n "$f" && echo "  OK $f"; done

echo "[2/6] JSON/XML parse..."
python3 -c "import json; json.load(open('configs/leechblock_scriptorium_rules.json')); print('  OK leechblock JSON')"
python3 -c "import xml.etree.ElementTree as ET; ET.parse('templates/manuscript/nwProject.nwx'); print('  OK nwProject XML')"

echo "[3/6] Pandoc Markdown->Typst smoke test..."
if command -v pandoc >/dev/null; then
  if pandoc --list-output-formats | grep -q typst; then
    echo "  OK pandoc typst writer present"
  else
    echo "  WARN pandoc lacks typst writer"
    exit 1
  fi
  printf '# Ch1\n\nHello *world*.\n' | pandoc -f markdown-citations -t typst -o "${TMP_VERIFY}/body.typ" && echo "  OK pandoc conversion"
else
  echo "  SKIP pandoc missing"
fi

echo "[4/6] Typst compile (if installed)..."
if command -v typst >/dev/null; then
  (cd templates/typst && typst compile preview_sample.typ "${TMP_VERIFY}/preview.pdf") && echo "  OK typst compile" && ls -lh "${TMP_VERIFY}/preview.pdf"
else
  echo "  SKIP typst missing (install per resources/software_catalog.md)"
fi

echo "[5/6] Desktop entries..."
if command -v desktop-file-validate >/dev/null; then
  desktop-file-validate launchers/*.desktop && echo "  OK desktop files"
else
  grep -q '^TryExec=bash$' launchers/*.desktop && echo "  OK TryExec present (validator skipped)"
fi

echo "[6/6] Functional world lifecycle (sandboxed HOME)..."
export HOME="${TMP_VERIFY}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

WORLD="VerifyWorld"
bash scripts/init_world.sh "${WORLD}" >/dev/null
[ -d "${HOME}/Worlds/${WORLD}/00-World-Bible/Characters" ] || { echo "  FAIL world scaffold missing"; exit 1; }
echo "  OK init_world"

# Multi-volume + tag-poisoning fixture: proves Book-02 inclusion and
# novelWriter @time/@plot tag stripping on the export path.
mkdir -p "${HOME}/Worlds/${WORLD}/01-Manuscript/Book-02/01_Act_I"
cat > "${HOME}/Worlds/${WORLD}/01-Manuscript/Book-02/01_Act_I/01_Chapter_05.md" << 'EOF'
# Chapter 5: The Second Book Begins

This chapter lives in Book-02 and must appear in exports.

@time: 1899-03-14
@plot: The Heist
EOF

set +e
bash scripts/export_book.sh "${HOME}/Worlds/${WORLD}" --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export.log" 2>&1
EXPORT_RC=$?
set -e
if [ "${EXPORT_RC}" -ne 0 ]; then
  echo "  FAIL export_book exited ${EXPORT_RC}:"; tail -n 5 "${TMP_VERIFY}/export.log"; exit 1
fi
echo "  OK export_book (exit 0)"

PDF="$(find "${HOME}/Worlds/${WORLD}/04-Publishing" -name '*.pdf' -print -quit 2>/dev/null)"
EPUB="$(find "${HOME}/Worlds/${WORLD}/04-Publishing" -name '*.epub' -print -quit 2>/dev/null)"
[ -n "${PDF}" ] || { echo "  FAIL no PDF produced (typst path broken?)"; exit 1; }
[ -n "${EPUB}" ] || { echo "  FAIL no EPUB produced"; exit 1; }
echo "  OK PDF + EPUB produced"

python3 - "${EPUB}" << 'PYEOF'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
txt = ""
for n in z.namelist():
    if n.endswith((".xhtml", ".html", ".ncx", ".opf")):
        txt += z.read(n).decode("utf-8", "ignore")
assert "Second Book Begins" in txt, "Book-02 volume missing from export"
assert "1899-03-14" not in txt, "novelWriter @time tag leaked into export"
assert "The Heist" not in txt, "novelWriter @plot tag leaked into export"
print("  OK multi-volume + tag stripping verified in EPUB")
PYEOF

bash scripts/save_snapshot.sh --world "${WORLD}" --note "verify.sh lifecycle test" > "${TMP_VERIFY}/snapshot.log" 2>&1 \
  || { echo "  FAIL save_snapshot:"; tail -n 5 "${TMP_VERIFY}/snapshot.log"; exit 1; }
git -C "${HOME}/Worlds/${WORLD}" log --oneline | grep -q "verify.sh lifecycle test" \
  || { echo "  FAIL snapshot note not committed"; exit 1; }
echo "  OK save_snapshot (note recorded)"

echo "ALL-CHECKS-PASS"
