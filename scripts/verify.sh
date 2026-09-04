#!/usr/bin/env bash
# Scriptorium verification harness (D10)
# Usage: bash scripts/verify.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[1/5] bash -n syntax..."
for f in scripts/*.sh; do bash -n "$f" && echo "  OK $f"; done

echo "[2/5] JSON/XML parse..."
python3 -c "import json; json.load(open('configs/leechblock_scriptorium_rules.json')); print('  OK leechblock JSON')"
python3 -c "import xml.etree.ElementTree as ET; ET.parse('templates/manuscript/nwProject.nwx'); print('  OK nwProject XML')"

echo "[3/5] Pandoc Markdown->Typst smoke test..."
if command -v pandoc >/dev/null; then
  pandoc --list-output-formats | grep -q typst && echo "  OK pandoc typst writer present" || { echo "  WARN pandoc lacks typst writer"; exit 1; }
  printf '# Ch1\n\nHello *world*.\n' | pandoc -f markdown -t typst -o /tmp/scriptorium-verify-body.typ && echo "  OK pandoc conversion"
else
  echo "  SKIP pandoc missing"
fi

echo "[4/5] Typst compile (if installed)..."
if command -v typst >/dev/null; then
  (cd templates/typst && typst compile preview_sample.typ /tmp/scriptorium-preview.pdf) && echo "  OK typst compile" && ls -lh /tmp/scriptorium-preview.pdf
else
  echo "  SKIP typst missing (install per resources/software_catalog.md)"
fi

echo "[5/5] Desktop entries..."
if command -v desktop-file-validate >/dev/null; then
  desktop-file-validate launchers/*.desktop && echo "  OK desktop files"
else
  grep -q '^TryExec=bash$' launchers/*.desktop && echo "  OK TryExec present (validator skipped)"
fi

echo "ALL-CHECKS-PASS"
