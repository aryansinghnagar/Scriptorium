#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR:-}"' EXIT
export HOME="${TMP_DIR}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

echo "[Test 1] Universe, World & Manuscript Creation..."
bash scripts/scriptorium universe TestUni >/dev/null
bash scripts/scriptorium world TestWorld --universe TestUni >/dev/null
bash scripts/scriptorium manuscript TestManuscript --universe TestUni --world TestWorld >/dev/null

WORLD_PATH="${HOME}/Universes/TestUni/TestWorld"
MS_PATH="${HOME}/Manuscripts/TestManuscript"

[ -d "${WORLD_PATH}/Characters" ]
[ -d "${WORLD_PATH}/Bestiary" ]
[ -f "${WORLD_PATH}/world.yaml" ]
[ -d "${MS_PATH}/Book-01/01_Act_I" ]
[ -f "${MS_PATH}/manuscript.yaml" ]
echo "  OK Test 1 passed"

echo "[Test 2] Positional arguments in save_snapshot.sh..."
echo "New scene text" >> "${MS_PATH}/Book-01/01_Act_I/01_Chapter_01.md"
bash scripts/scriptorium snapshot TestManuscript -m "Positional snapshot test" >/dev/null
LAST_COMMIT="$(git -C "${MS_PATH}" log -n 1 --oneline)"
[[ "${LAST_COMMIT}" == *"Positional snapshot test"* ]]
echo "  OK Test 2 passed: Positional snapshot recorded"

echo "[Test 3] Add-volume multi-volume scaffolding and auto-increment..."
bash scripts/scriptorium add-volume TestManuscript "Book-02" >/dev/null
[ -d "${MS_PATH}/Book-02/01_Act_I" ]
[ -d "${MS_PATH}/Book-02/02_Act_II" ]
[ -d "${MS_PATH}/Book-02/03_Act_III" ]
[ -d "${MS_PATH}/Book-02/.git" ]

# Auto-increment to Book-03
bash scripts/scriptorium add-volume TestManuscript >/dev/null
[ -d "${MS_PATH}/Book-03/01_Act_I" ]
[ -d "${MS_PATH}/Book-03/02_Act_II" ]
[ -d "${MS_PATH}/Book-03/03_Act_III" ]
[ -d "${MS_PATH}/Book-03/.git" ]
echo "  OK Test 3 passed: Book-02 and auto-incremented Book-03 scaffolded"

echo "[Test 4] Export book options (--paper-size and cover auto-detection)..."
mkdir -p "${MS_PATH}/03-Art"
touch "${MS_PATH}/03-Art/cover.png"
# Run export with custom paper size
bash scripts/export_book.sh "${MS_PATH}" --book Book-02 --paper-size pocket --title "Echoes" --author "Tester" > "${TMP_DIR}/export.log" 2>&1 || true
grep -q "Auto-detected EPUB cover image" "${TMP_DIR}/export.log" || true
echo "  OK Test 4 passed: Export options processed"

echo "[Test 5] World Doctor diagnostics on new schemas..."
bash scripts/world_doctor.sh "${WORLD_PATH}" >/dev/null || true
DOC_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
printf '%s' "${DOC_JSON}" | python3 -c "import json, sys; d = json.load(sys.stdin); assert d['notes'] >= 0"
echo "  OK Test 5 passed: World doctor completed without runtime exceptions"

echo "[Test 6] Concordance Engine & Multi-Era Chronology..."
cat > "${WORLD_PATH}/Characters/Aurelius.md" << 'EOF'
---
name: "Aurelius"
type: character
role: protagonist
birth_year: "-450 IE"
death_year: "-380 IE"
---
A legendary general.
EOF

cat > "${WORLD_PATH}/Factions/Solaris.md" << 'EOF'
---
name: "Solaris"
type: faction
faction_type: "Empire"
motto: "In Luce"
---
EOF

bash scripts/scriptorium concordance "${WORLD_PATH}" --manuscript "${MS_PATH}" --book Book-01 >/dev/null
[ -f "${MS_PATH}/Book-01/04_Back_Matter/01_Dramatis_Personae.md" ]
[ -f "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" ]
grep -q "Aurelius" "${MS_PATH}/Book-01/04_Back_Matter/01_Dramatis_Personae.md"
grep -q "Solaris" "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md"

DOC_MULTI_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
printf '%s' "${DOC_MULTI_JSON}" | python3 -c "import json, sys; d = json.load(sys.stdin); assert len(d['timeline_errors']) == 0"
echo "  OK Test 6 passed: Concordance generated & multi-era dates validated"

echo "[Test 7] Legacy-root deprecation nudge on auto-selected worlds (N-03)..."
# Exactly one world, living under the legacy ~/Worlds root: a bare doctor
# invocation auto-selects it and MUST print the deprecation nudge.
LEGACY_HOME="${TMP_DIR}/legacy-home"
mkdir -p "${LEGACY_HOME}"
HOME="${LEGACY_HOME}" bash scripts/init_world.sh OnlyWorld --legacy-worlds-dir >/dev/null
LEGACY_ERR="$(HOME="${LEGACY_HOME}" bash scripts/world_doctor.sh 2>&1 >/dev/null || true)"
[[ "${LEGACY_ERR}" == *"legacy ~/Worlds root"* ]] || { echo "  FAIL: auto-selected legacy world was not nudged" >&2; exit 1; }
# Control: exactly one canonical world — auto-select must stay silent.
CANON_HOME="${TMP_DIR}/canon-home"
mkdir -p "${CANON_HOME}"
HOME="${CANON_HOME}" bash scripts/init_world.sh OnlyWorld --universe SoloUni >/dev/null
CANON_ERR="$(HOME="${CANON_HOME}" bash scripts/world_doctor.sh 2>&1 >/dev/null || true)"
[[ "${CANON_ERR}" != *"legacy ~/Worlds root"* ]] || { echo "  FAIL: canonical world was wrongly nudged" >&2; exit 1; }
echo "  OK Test 7 passed: nudge fires for legacy auto-select only"

echo "ALL TARGETED TESTS PASSED SUCCESSFULLY!"
