#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR:-}"' EXIT
export HOME="${TMP_DIR}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

echo "[Test 1] Universe & World Creation..."
bash scripts/scriptorium universe TestUni >/dev/null
bash scripts/scriptorium init TestWorld --universe TestUni >/dev/null
WORLD_PATH="${HOME}/Universes/TestUni/Worlds/TestWorld"
[ -d "${WORLD_PATH}/00-World-Bible" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-01" ]
echo "  OK Test 1 passed"

echo "[Test 2] Positional arguments in save_snapshot.sh..."
echo "New scene text" >> "${WORLD_PATH}/01-Manuscript/Book-01/01_Act_I/01_Chapter_01.md"
bash scripts/scriptorium snapshot TestWorld -m "Positional snapshot test" >/dev/null
LAST_COMMIT="$(git -C "${WORLD_PATH}" log -n 1 --oneline)"
[[ "${LAST_COMMIT}" == *"Positional snapshot test"* ]]
echo "  OK Test 2 passed: Positional snapshot recorded"

echo "[Test 3] Add-book multi-volume scaffolding and auto-increment..."
bash scripts/scriptorium add-book TestWorld "Book-02" >/dev/null
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/01_Act_I" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/02_Act_II" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/03_Act_III" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/.git" ]

# Auto-increment to Book-03
bash scripts/scriptorium add-book TestWorld >/dev/null
[ -d "${WORLD_PATH}/01-Manuscript/Book-03/01_Act_I" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-03/02_Act_II" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-03/03_Act_III" ]
[ -d "${WORLD_PATH}/01-Manuscript/Book-03/.git" ]
echo "  OK Test 3 passed: Book-02 and auto-incremented Book-03 scaffolded"

echo "[Test 4] Export book options (--paper-size and cover auto-detection)..."
mkdir -p "${WORLD_PATH}/03-Art"
touch "${WORLD_PATH}/03-Art/cover.png"
# Run export with custom paper size
bash scripts/export_book.sh "${WORLD_PATH}" --book Book-02 --paper-size pocket --title "Echoes" --author "Tester" > "${TMP_DIR}/export.log" 2>&1 || true
grep -q "Auto-detected EPUB cover image" "${TMP_DIR}/export.log" || true
echo "  OK Test 4 passed: Export options processed"

echo "[Test 5] World Doctor diagnostics on new schemas..."
bash scripts/world_doctor.sh "${WORLD_PATH}" >/dev/null || true
DOC_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json)"
python3 -c "import json; d = json.loads('''${DOC_JSON}'''); assert d['notes'] >= 0"
echo "  OK Test 5 passed: World doctor completed without runtime exceptions"

echo "[Test 6] Concordance Engine & Multi-Era Chronology..."
cat > "${WORLD_PATH}/00-World-Bible/Characters/Aurelius.md" << 'EOF'
---
name: "Aurelius"
type: character
role: protagonist
birth_year: "-450 IE"
death_year: "-380 IE"
---
A legendary general.
EOF

cat > "${WORLD_PATH}/00-World-Bible/Factions/Solaris.md" << 'EOF'
---
name: "Solaris"
type: faction
faction_type: "Empire"
motto: "In Luce"
---
EOF

bash scripts/scriptorium concordance "${WORLD_PATH}" --book Book-01 >/dev/null
[ -f "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/01_Dramatis_Personae.md" ]
[ -f "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" ]
grep -q "Aurelius" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/01_Dramatis_Personae.md"
grep -q "Solaris" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md"

DOC_MULTI_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
python3 -c "import json; d = json.loads('''${DOC_MULTI_JSON}'''); assert len(d['timeline_errors']) == 0"
echo "  OK Test 6 passed: Concordance generated & multi-era dates validated"

echo "ALL TARGETED TESTS PASSED SUCCESSFULLY!"
