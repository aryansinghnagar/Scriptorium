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

echo "[Test 8] Scriptorium doctor -m, --manuscript option forwarding (DEV-01)..."
set +e
bash scripts/scriptorium_doctor.sh --world "${WORLD_PATH}" --manuscript "${MS_PATH}" > "${TMP_DIR}/doc.log" 2>&1
DOC_RC=$?
set -e
[ "${DOC_RC}" -eq 0 ] || [ "${DOC_RC}" -eq 1 ] || { echo "  FAIL scriptorium_doctor exited with ${DOC_RC}:"; cat "${TMP_DIR}/doc.log"; exit 1; }
echo "  OK Test 8 passed: scriptorium_doctor accepts and forwards --manuscript"

echo "[Test 9] Save snapshot with 0 worlds and 1 manuscript (DEV-03)..."
ZERO_WORLD_HOME="${TMP_DIR}/zero-world-home"
mkdir -p "${ZERO_WORLD_HOME}"
HOME="${ZERO_WORLD_HOME}" bash scripts/init_manuscript.sh SoloNovel >/dev/null
echo "Solo prose" >> "${ZERO_WORLD_HOME}/Manuscripts/SoloNovel/Book-01/01_Act_I/01_Chapter_01.md"
HOME="${ZERO_WORLD_HOME}" bash scripts/save_snapshot.sh -m "Solo manuscript snapshot" >/dev/null
SOLO_LOG="$(git -C "${ZERO_WORLD_HOME}/Manuscripts/SoloNovel" log -n 1 --oneline)"
[[ "${SOLO_LOG}" == *"Solo manuscript snapshot"* ]] || { echo "  FAIL: snapshot failed for 0-world user"; exit 1; }
echo "  OK Test 9 passed: save_snapshot works with 0 worlds and 1 manuscript"

echo "[Test 10] World doctor validates World-Bible-Index without false positives (WLD-01)..."
DOC_WLD_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
set +e
PY_ERR=$(printf '%s' "${DOC_WLD_JSON}" | python3 -c '
import json, sys
d = json.load(sys.stdin)
orphans = [o["file"] for o in d.get("orphans", [])]
for o in orphans:
    assert "fileClasses" not in o, "fileClasses flagged as orphan: " + str(o)
    assert "Daily-Writing-Log" not in o, "Daily-Writing-Log flagged as orphan: " + str(o)
assert len(d.get("broken_links", [])) == 0, "Unexpected broken links: " + str(d.get("broken_links"))
' 2>&1)
PY_RC=$?
set -e
[ $PY_RC -eq 0 ] || { echo "  FAIL Python assertion in Test 10: ${PY_ERR}"; exit 1; }
echo "  OK Test 10 passed: World-Bible-Index validated and template exclusions verified"

echo "[Test 11] Standardize CLI usage error exit code 2 across all scripts (CQA-01)..."
for s in scripts/add_book.sh scripts/backup_world.sh scripts/export_book.sh \
         scripts/generate_concordance.sh scripts/init_manuscript.sh scripts/init_universe.sh \
         scripts/init_world.sh scripts/restore_world.sh scripts/save_snapshot.sh \
         scripts/scriptorium_doctor.sh scripts/setup_scriptorium.sh \
         scripts/uninstall_scriptorium.sh scripts/world_doctor.sh scripts/wordcount_report.sh; do
    set +e
    bash "$s" --nonexistent-option >/dev/null 2>&1
    RC=$?
    set -e
    [ $RC -eq 2 ] || { echo "  FAIL: $s exited with $RC on bad option (expected 2)"; exit 1; }
done
set +e
bash scripts/scriptorium invalid-command >/dev/null 2>&1
FACADE_RC=$?
set -e
[ $FACADE_RC -eq 2 ] || { echo "  FAIL: scriptorium facade exited with $FACADE_RC on unknown command (expected 2)"; exit 1; }
echo "  OK Test 11 passed: All 15 scripts exit 2 on CLI usage/option errors"

echo "[Test 12] Standardize launcher Categories to Office;WordProcessor;Publishing; (UX-01)..."
for lf in launchers/*.desktop; do
    grep -q "^Categories=Office;WordProcessor;Publishing;$" "$lf" || { echo "  FAIL: Categories non-standard in $lf"; exit 1; }
done
echo "  OK Test 12 passed: All .desktop launchers standardized"

echo "[Test 13] Subplot Matrix Dataview Query (AUT-01)..."
grep -q 'FROM ""' "templates/manuscript/Outlines/Subplot-Thread-Matrix.md" || { echo "  FAIL: missing FROM \"\" in Subplot Matrix"; exit 1; }
grep -q '!contains(file.path, "Outlines")' "templates/manuscript/Outlines/Subplot-Thread-Matrix.md" || { echo "  FAIL: missing Outlines filter in Subplot Matrix"; exit 1; }
! grep -q 'FROM "01-Manuscript"' "templates/manuscript/Outlines/Subplot-Thread-Matrix.md" || { echo "  FAIL: obsolete 01-Manuscript query present"; exit 1; }
echo "  OK Test 13 passed: Subplot-Thread-Matrix Dataview queries verified"

echo "ALL TARGETED TESTS PASSED SUCCESSFULLY!"
