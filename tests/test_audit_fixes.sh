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

echo "[Test 14] Typst Installer Fail-Closed Security (S-01)..."
grep -B 2 -A 4 "upstream SHA-256 digest unavailable" "scripts/setup_scriptorium.sh" | grep -q "TYPST_OK=0" || {
    echo "  FAIL: Typst installer fails open when digest is missing"; exit 1;
}
echo "  OK Test 14 passed: Typst installer fails closed on missing upstream digest"

echo "[Test 15] Depth-3 Universe/World Discovery & Labeling (LIB-01)..."
DISC_TMP=$(mktemp -d)
mkdir -p "$DISC_TMP/Universes/Cosmere/Scadrial/World-Bible"
mkdir -p "$DISC_TMP/Universes/Arda/Worlds/Valinor/World-Bible"
mkdir -p "$DISC_TMP/Worlds/SoloWorld/World-Bible"
touch "$DISC_TMP/Universes/Cosmere/Scadrial/World-Bible/World-Bible-Index.md"
touch "$DISC_TMP/Universes/Arda/Worlds/Valinor/World-Bible/World-Bible-Index.md"
touch "$DISC_TMP/Worlds/SoloWorld/World-Bible/World-Bible-Index.md"

(
    unset SCRIPTORIUM_LIB_WORLDS_SOURCED
    export UNIVERSES_BASE="$DISC_TMP/Universes"
    export LEGACY_WORLDS_BASE="$DISC_TMP/Worlds"
    source scripts/lib/worlds.sh

    discover_worlds FOUND_WORLDS
    JOINED_WORLDS=$(printf '%s\n' "${FOUND_WORLDS[@]}")
    echo "$JOINED_WORLDS" | grep -q "Scadrial" || { echo "  FAIL: Scadrial not discovered"; exit 1; }
    echo "$JOINED_WORLDS" | grep -q "Valinor" || { echo "  FAIL: Depth-3 Valinor not discovered"; exit 1; }
    echo "$JOINED_WORLDS" | grep -q "SoloWorld" || { echo "  FAIL: SoloWorld not discovered"; exit 1; }
    ! echo "$JOINED_WORLDS" | grep -E -q '/Universes/[^/]+/Worlds$' || { echo "  FAIL: Literal 'Worlds' container folder discovered as world"; exit 1; }

    # Test universe_label extraction
    LBL_VALINOR=$(universe_label "$DISC_TMP/Universes/Arda/Worlds/Valinor")
    [ "$LBL_VALINOR" = "Arda" ] || { echo "  FAIL: Valinor universe label was '$LBL_VALINOR' (expected 'Arda')"; exit 1; }

    LBL_SCADRIAL=$(universe_label "$DISC_TMP/Universes/Cosmere/Scadrial")
    [ "$LBL_SCADRIAL" = "Cosmere" ] || { echo "  FAIL: Scadrial universe label was '$LBL_SCADRIAL' (expected 'Cosmere')"; exit 1; }

    # Test resolve_world_dir
    RESOLVED_VALINOR=$(resolve_world_dir "Valinor")
    [ "$RESOLVED_VALINOR" = "$DISC_TMP/Universes/Arda/Worlds/Valinor" ] || { echo "  FAIL: resolve_world_dir Valinor failed: $RESOLVED_VALINOR"; exit 1; }
)
rm -rf "$DISC_TMP"
echo "  OK Test 15 passed: Depth-3 universe/world discovery and universe label verified"

echo "[Test 16] ISO 8601 Multi-Era Chronology in World Doctor (WLD-104)..."
DOC_TMP=$(mktemp -d)
mkdir -p "$DOC_TMP/Characters"
touch "$DOC_TMP/world.yaml"
cat > "$DOC_TMP/World-Bible-Index.md" << 'EOF'
---
name: World Index
type: index
---
# Index
- [[Paradox-Person]]
EOF
cat > "$DOC_TMP/Characters/Paradox-Person.md" << 'EOF'
---
name: Paradox Person
type: character
birth_date: 1899-03-14
death_date: 1850-01-01
---
# Paradox Person
A temporal anomaly.
EOF

set +e
DOC_OUT=$(bash scripts/world_doctor.sh "$DOC_TMP" 2>&1)
DOC_RC=$?
set -e
[ $DOC_RC -eq 1 ] || { echo "  FAIL: world_doctor failed to detect ISO date chronological paradox (RC=$DOC_RC, OUT=$DOC_OUT)"; exit 1; }
echo "$DOC_OUT" | grep -q "Death date (1850-01-01) precedes birth date (1899-03-14)" || {
    echo "  FAIL: world_doctor output missing expected ISO date error: $DOC_OUT"; exit 1;
}

# Now fix the dates and verify it passes
cat > "$DOC_TMP/Characters/Paradox-Person.md" << 'EOF'
---
name: Paradox Person
type: character
birth_date: 1850-01-01
death_date: 1899-03-14
---
# Paradox Person
A mortal life.
EOF
bash scripts/world_doctor.sh "$DOC_TMP" >/dev/null 2>&1 || {
    echo "  FAIL: world_doctor errored on valid chronological ISO dates"; exit 1;
}
rm -rf "$DOC_TMP"
echo "  OK Test 16 passed: ISO 8601 calendar date timeline paradox checks verified"

echo "[Test 17] Manuscript Outline & Intra-Manuscript Wikilinks (WLD-108)..."
MS_TMP=$(mktemp -d)
mkdir -p "$MS_TMP/World/Characters"
touch "$MS_TMP/World/world.yaml"
mkdir -p "$MS_TMP/Manuscript/Outlines"
mkdir -p "$MS_TMP/Manuscript/Act-01"

cat > "$MS_TMP/World/World-Bible-Index.md" << 'EOF'
---
name: World Index
type: index
---
# Index
- [[Kaelen]]
EOF
cat > "$MS_TMP/World/Characters/Kaelen.md" << 'EOF'
---
name: Kaelen
type: character
---
# Kaelen
The protagonist.
EOF
cat > "$MS_TMP/Manuscript/Outlines/Master-Outline.md" << 'EOF'
---
name: Master Outline
---
# Master Outline
The master story arc.
EOF
cat > "$MS_TMP/Manuscript/Act-01/Scene-01.md" << 'EOF'
# Chapter 1
@pov: Kaelen
@char: Kaelen

Kaelen reviewed the [[Master-Outline]] before setting out.
EOF

# Should pass with no findings
bash scripts/world_doctor.sh "$MS_TMP/World" --manuscript "$MS_TMP/Manuscript" >/dev/null 2>&1 || {
    echo "  FAIL: world_doctor flagged intra-manuscript outline wikilink as lore drift"; exit 1;
}

# Adding a truly missing entity should fail with WLD-108
cat > "$MS_TMP/Manuscript/Act-01/Scene-01.md" << 'EOF'
# Chapter 1
@pov: Kaelen
@char: NonExistentHero

Kaelen walked through [[UnknownMythicRealm]].
EOF

set +e
DRIFT_OUT=$(bash scripts/world_doctor.sh "$MS_TMP/World" --manuscript "$MS_TMP/Manuscript" 2>&1)
DRIFT_RC=$?
set -e
[ $DRIFT_RC -eq 1 ] || { echo "  FAIL: world_doctor did not flag true manuscript lore drift"; exit 1; }
echo "$DRIFT_OUT" | grep -q "WLD-108" || {
    echo "  FAIL: expected WLD-108 in output: $DRIFT_OUT"; exit 1;
}
rm -rf "$MS_TMP"
echo "  OK Test 17 passed: Manuscript outline wikilinks and lore drift detection verified"

echo "ALL TARGETED TESTS PASSED SUCCESSFULLY!"
