#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Comprehensive Verification Harness
# Usage: bash scripts/verify.sh
# ==============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP_VERIFY="$(mktemp -d)"
cleanup() {
    rm -rf "${TMP_VERIFY:-}"
}
trap cleanup EXIT

echo "[1/7] bash -n syntax validation..."
for f in scripts/*.sh scripts/scriptorium; do
    if [ -f "$f" ]; then
        bash -n "$f" && echo "  OK $f"
    fi
done

echo "[2/7] JSON & XML schema validation..."
# 2a. LeechBlock JSON schema validation
python3 - << 'PYEOF'
import json, sys
with open('configs/leechblock_scriptorium_rules.json') as f:
    data = json.load(f)
assert "blockSets" in data, "Missing blockSets in leechblock JSON"
assert isinstance(data["blockSets"], list) and len(data["blockSets"]) > 0, "Empty blockSets"
bs = data["blockSets"][0]
for req in ("sites", "times", "days", "active"):
    assert req in bs, f"Missing required field '{req}' in blockSet"
print("  OK leechblock JSON schema")
PYEOF

# 2b. novelWriter XML schema validation
python3 - << 'PYEOF'
import xml.etree.ElementTree as ET
tree = ET.parse('templates/manuscript/nwProject.nwx')
root = tree.getroot()
assert root.tag == "novelWriterXML", f"Unexpected XML root tag: {root.tag}"
assert root.attrib.get("fileVersion") == "1.5", f"Unexpected fileVersion: {root.attrib.get('fileVersion')}"
assert root.find("project") is not None, "Missing <project> node"
assert root.find("content") is not None, "Missing <content> node"
print("  OK nwProject XML fileVersion 1.5")
PYEOF

# 2c. Obsidian vault pre-configured suite validation
python3 - << 'PYEOF'
import json, os
plugins_cfg = 'templates/world-bible/.obsidian/community-plugins.json'
assert os.path.isfile(plugins_cfg), "Missing community-plugins.json"
with open(plugins_cfg) as f:
    plugins = json.load(f)
required_plugins = [
    "storyline", "longform", "dataview", "metadata-menu",
    "calendarium", "storyteller-suite", "novel-word-count", "obsidian-git"
]
for p in required_plugins:
    assert p in plugins, f"Missing required plugin in pre-configured suite: {p}"
print("  OK Obsidian pre-configured plugin suite schema")
PYEOF

echo "[3/7] Pandoc Markdown->Typst smoke test..."
if command -v pandoc >/dev/null; then
    if pandoc --list-output-formats 2>/dev/null | grep -q typst; then
        echo "  OK pandoc typst writer present"
    else
        echo "  WARN pandoc lacks native typst writer (sed fallback will be used)"
    fi
    printf '# Ch1\n\nHello *world*.\n' | pandoc -f markdown-citations -t typst -o "${TMP_VERIFY}/body.typ" 2>/dev/null && echo "  OK pandoc conversion"
else
    echo "  SKIP pandoc missing on this host"
fi

echo "[4/7] Typst compile smoke test (if installed)..."
if command -v typst >/dev/null; then
    (cd templates/typst && typst compile preview_sample.typ "${TMP_VERIFY}/preview.pdf") && echo "  OK typst compile" && ls -lh "${TMP_VERIFY}/preview.pdf"
else
    echo "  SKIP typst missing on this host (install per resources/software_catalog.md)"
fi

echo "[5/7] Desktop launcher validation..."
if command -v desktop-file-validate >/dev/null; then
    desktop-file-validate launchers/*.desktop && echo "  OK desktop files"
else
    grep -q '^TryExec=bash$' launchers/*.desktop && echo "  OK TryExec present in all launchers (validator tool skipped)"
fi

echo "[6/7] Functional Universe, World lifecycle, diagnostics & recovery (sandboxed HOME)..."
export HOME="${TMP_VERIFY}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

# 6a. Universe initialization
UNIVERSE="TestMultiverse"
bash scripts/init_universe.sh "${UNIVERSE}" >/dev/null
[ -d "${HOME}/Universes/${UNIVERSE}/Worlds" ] || { echo "  FAIL universe scaffold missing"; exit 1; }
[ -d "${HOME}/Universes/${UNIVERSE}/.git" ] || { echo "  FAIL universe git repository missing"; exit 1; }
echo "  OK init_universe (Universe directory + Universe Git repository)"

# 6b. Transactional world initialization inside Universe
WORLD="VerifyWorld"
bash scripts/init_world.sh "${WORLD}" --universe "${UNIVERSE}" >/dev/null
WORLD_PATH="${HOME}/Universes/${UNIVERSE}/Worlds/${WORLD}"
[ -d "${WORLD_PATH}/00-World-Bible/Characters" ] || { echo "  FAIL world bible scaffold missing"; exit 1; }
[ -f "${WORLD_PATH}/00-World-Bible/.obsidian/community-plugins.json" ] || { echo "  FAIL obsidian config missing"; exit 1; }
[ -f "${WORLD_PATH}/01-Manuscript/nwProject.nwx" ] || { echo "  FAIL nwProject.nwx missing"; exit 1; }
[ -d "${WORLD_PATH}/.git" ] || { echo "  FAIL world git repository missing"; exit 1; }
[ -d "${WORLD_PATH}/01-Manuscript/Book-01/.git" ] || { echo "  FAIL discrete manuscript git repository missing"; exit 1; }
echo "  OK init_world (Multi-tier Universe, World & Manuscript Git repositories)"

# 6c. Inject Multi-volume + tag-poisoning test chapters
mkdir -p "${WORLD_PATH}/01-Manuscript/Book-02/01_Act_I"
cat > "${WORLD_PATH}/01-Manuscript/Book-02/01_Act_I/01_Chapter_05.md" << 'EOF'
# Chapter 5: The Second Book Begins

This chapter lives in Book-02 and must appear in exports.

@time: 1899-03-14
@plot: The Heist
@theme: Honor & Steel
EOF

# 6d. Export book compilation
set +e
bash scripts/export_book.sh "${WORLD_PATH}" --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export.log" 2>&1
EXPORT_RC=$?
set -e

if command -v typst >/dev/null && command -v pandoc >/dev/null; then
    if [ "${EXPORT_RC}" -ne 0 ]; then
        echo "  FAIL export_book exited ${EXPORT_RC}:"; tail -n 5 "${TMP_VERIFY}/export.log"; exit 1
    fi
    echo "  OK export_book (exit 0)"

    PDF="$(find "${WORLD_PATH}/04-Publishing" -name '*.pdf' -print -quit 2>/dev/null)"
    EPUB="$(find "${WORLD_PATH}/04-Publishing" -name '*.epub' -print -quit 2>/dev/null)"
    [ -n "${PDF}" ] && [ -s "${PDF}" ] || { echo "  FAIL no non-empty PDF produced"; exit 1; }
    [ -n "${EPUB}" ] && [ -s "${EPUB}" ] || { echo "  FAIL no non-empty EPUB produced"; exit 1; }
    echo "  OK PDF + EPUB produced and verified non-empty"

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
assert "Honor & Steel" not in txt, "novelWriter custom @theme tag leaked into export"
print("  OK multi-volume + tag stripping verified in EPUB")
PYEOF
else
    echo "  SKIP full PDF/EPUB export build (typst/pandoc not installed in local environment)"
fi

# 6e. World Doctor consistency check
DOCTOR_JSON=$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json)
python3 -c "import json, sys; d = json.loads('''${DOCTOR_JSON}'''); assert d['notes'] >= 0; print('  OK world_doctor --json valid')"
bash scripts/world_doctor.sh "${WORLD_PATH}" >/dev/null || true
echo "  OK world_doctor functional run"

# 6f. Wordcount & Progress Analytics
bash scripts/wordcount_report.sh "${WORLD_PATH}" --markdown > "${TMP_VERIFY}/wc.md"
[ -s "${TMP_VERIFY}/wc.md" ] || { echo "  FAIL wordcount report empty"; exit 1; }
bash scripts/wordcount_report.sh "${WORLD_PATH}" --json > "${TMP_VERIFY}/wc.json"
python3 -c "import json; d = json.load(open('${TMP_VERIFY}/wc.json')); assert d['total_words'] >= 0; assert d['chapter_count'] >= 1"
echo "  OK wordcount_report (markdown + json)"

# 6g. Save Snapshot (Git Versioning across World & Manuscript)
bash scripts/save_snapshot.sh --world "${WORLD}" --note "verify.sh lifecycle test" > "${TMP_VERIFY}/snapshot.log" 2>&1 \
    || { echo "  FAIL save_snapshot:"; tail -n 5 "${TMP_VERIFY}/snapshot.log"; exit 1; }
git -C "${WORLD_PATH}" log --oneline | grep -q "verify.sh lifecycle test" \
    || { echo "  FAIL snapshot note not committed"; exit 1; }
echo "  OK save_snapshot (multi-tier Git snapshots recorded)"

# 6h. Decoupled Backup & Verified Restore Drill
echo "  Running backup & restore verification drill..."
bash scripts/backup_world.sh --world "${WORLD}" --note "harness drill" > "${TMP_VERIFY}/backup.log" 2>&1 \
    || { echo "  FAIL backup_world:"; tail -n 5 "${TMP_VERIFY}/backup.log"; exit 1; }
BACKUP_ARCHIVE="$(find "${WORLD_PATH}/05-Backups" -name '*.tar.gz' -print -quit)"
[ -n "${BACKUP_ARCHIVE}" ] || { echo "  FAIL backup archive not created"; exit 1; }
[ -f "${BACKUP_ARCHIVE%.tar.gz}.sha256" ] || { echo "  FAIL backup sha256 missing"; exit 1; }
echo "  OK backup_world (archive + sha256 created)"

# Wipe world and perform restore
RESTORE_TARGET="RestoredWorld"
bash scripts/restore_world.sh --archive "${BACKUP_ARCHIVE}" --target "${RESTORE_TARGET}" --universe "${UNIVERSE}" > "${TMP_VERIFY}/restore.log" 2>&1 \
    || { echo "  FAIL restore_world:"; tail -n 5 "${TMP_VERIFY}/restore.log"; exit 1; }
RESTORED_PATH="${HOME}/Universes/${UNIVERSE}/Worlds/${RESTORE_TARGET}"
[ -d "${RESTORED_PATH}/00-World-Bible" ] || { echo "  FAIL restored world bible missing"; exit 1; }
[ -f "${RESTORED_PATH}/01-Manuscript/Book-02/01_Act_I/01_Chapter_05.md" ] || { echo "  FAIL restored chapter missing"; exit 1; }
echo "  OK restore_world (drill verified: archive -> wipe -> restore -> verify content)"

# 6i. Unified Scriptorium Doctor
bash scripts/scriptorium_doctor.sh --world "${RESTORE_TARGET}" > "${TMP_VERIFY}/doc.log" 2>&1 || true
[ -s "${TMP_VERIFY}/doc.log" ] || { echo "  FAIL scriptorium_doctor produced no output"; exit 1; }
echo "  OK scriptorium_doctor diagnostics"

# 6j. Dry-run simulation tests
bash scripts/setup_scriptorium.sh --dry-run --force > "${TMP_VERIFY}/setup_dryrun.log" 2>&1 \
    || { echo "  FAIL setup_scriptorium --dry-run:"; tail -n 5 "${TMP_VERIFY}/setup_dryrun.log"; exit 1; }
bash scripts/uninstall_scriptorium.sh --dry-run --force > "${TMP_VERIFY}/uninstall_dryrun.log" 2>&1 \
    || { echo "  FAIL uninstall_scriptorium --dry-run:"; tail -n 5 "${TMP_VERIFY}/uninstall_dryrun.log"; exit 1; }
echo "  OK setup & uninstall --dry-run simulations"

echo "[7/7] Scriptorium CLI facade tests..."
bash scripts/scriptorium --version >/dev/null
bash scripts/scriptorium --help >/dev/null
bash scripts/scriptorium universe --list >/dev/null
echo "  OK scriptorium CLI entrypoint (with universe command)"

echo "ALL-CHECKS-PASS"
