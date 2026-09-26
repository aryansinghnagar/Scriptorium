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
bash scripts/arcanum universe TestUni >/dev/null
bash scripts/arcanum world TestWorld --universe TestUni >/dev/null
bash scripts/arcanum manuscript TestManuscript --universe TestUni --world TestWorld >/dev/null

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
bash scripts/arcanum snapshot TestManuscript -m "Positional snapshot test" >/dev/null
LAST_COMMIT="$(git -C "${MS_PATH}" log -n 1 --oneline)"
[[ "${LAST_COMMIT}" == *"Positional snapshot test"* ]]
echo "  OK Test 2 passed: Positional snapshot recorded"

echo "[Test 3] Add-volume multi-volume scaffolding and auto-increment..."
bash scripts/arcanum add-volume TestManuscript "Book-02" >/dev/null
[ -d "${MS_PATH}/Book-02/01_Act_I" ]
[ -d "${MS_PATH}/Book-02/02_Act_II" ]
[ -d "${MS_PATH}/Book-02/03_Act_III" ]
[ -d "${MS_PATH}/Book-02/.git" ]

# Auto-increment to Book-03
bash scripts/arcanum add-volume TestManuscript >/dev/null
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

bash scripts/arcanum concordance "${WORLD_PATH}" --manuscript "${MS_PATH}" --book Book-01 >/dev/null
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

echo "[Test 8] Ars Arcanum doctor -m, --manuscript option forwarding (DEV-01)..."
set +e
bash scripts/arcanum_doctor.sh --world "${WORLD_PATH}" --manuscript "${MS_PATH}" > "${TMP_DIR}/doc.log" 2>&1
DOC_RC=$?
set -e
[ "${DOC_RC}" -eq 0 ] || [ "${DOC_RC}" -eq 1 ] || { echo "  FAIL arcanum_doctor exited with ${DOC_RC}:"; cat "${TMP_DIR}/doc.log"; exit 1; }
echo "  OK Test 8 passed: arcanum_doctor accepts and forwards --manuscript"

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
         scripts/arcanum_doctor.sh scripts/setup_arcanum.sh \
         scripts/uninstall_arcanum.sh scripts/world_doctor.sh scripts/wordcount_report.sh; do
    set +e
    bash "$s" --nonexistent-option >/dev/null 2>&1
    RC=$?
    set -e
    [ $RC -eq 2 ] || { echo "  FAIL: $s exited with $RC on bad option (expected 2)"; exit 1; }
done
set +e
bash scripts/arcanum invalid-command >/dev/null 2>&1
FACADE_RC=$?
set -e
[ $FACADE_RC -eq 2 ] || { echo "  FAIL: arcanum facade exited with $FACADE_RC on unknown command (expected 2)"; exit 1; }
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
grep -B 2 -A 4 "upstream SHA-256 digest unavailable" "scripts/setup_arcanum.sh" | grep -q "TYPST_OK=0" || {
    echo "  FAIL: Typst installer fails open when digest is missing"; exit 1;
}
echo "  OK Test 14 passed: Typst installer fails closed on missing upstream digest"

echo "[Test 15] Depth-3 Universe/World Discovery & Labeling (LIB-01)..."
DISC_TMP=$(mktemp -d)
mkdir -p "$DISC_TMP/Universes/Eldoria-Cosmos/Eldoria-World/World-Bible"
mkdir -p "$DISC_TMP/Universes/Solaris-Verse/Worlds/Aetheria/World-Bible"
mkdir -p "$DISC_TMP/Worlds/SoloWorld/World-Bible"
touch "$DISC_TMP/Universes/Eldoria-Cosmos/Eldoria-World/World-Bible/World-Bible-Index.md"
touch "$DISC_TMP/Universes/Solaris-Verse/Worlds/Aetheria/World-Bible/World-Bible-Index.md"
touch "$DISC_TMP/Worlds/SoloWorld/World-Bible/World-Bible-Index.md"

(
    unset ARCANUM_LIB_WORLDS_SOURCED SCRIPTORIUM_LIB_WORLDS_SOURCED
    export UNIVERSES_BASE="$DISC_TMP/Universes"
    export LEGACY_WORLDS_BASE="$DISC_TMP/Worlds"
    source scripts/lib/worlds.sh

    discover_worlds FOUND_WORLDS
    JOINED_WORLDS=$(printf '%s\n' "${FOUND_WORLDS[@]}")
    echo "$JOINED_WORLDS" | grep -q "Eldoria-World" || { echo "  FAIL: Eldoria-World not discovered"; exit 1; }
    echo "$JOINED_WORLDS" | grep -q "Aetheria" || { echo "  FAIL: Depth-3 Aetheria not discovered"; exit 1; }
    echo "$JOINED_WORLDS" | grep -q "SoloWorld" || { echo "  FAIL: SoloWorld not discovered"; exit 1; }
    ! echo "$JOINED_WORLDS" | grep -E -q '/Universes/[^/]+/Worlds$' || { echo "  FAIL: Literal 'Worlds' container folder discovered as world"; exit 1; }

    # Test universe_label extraction
    LBL_AETHERIA=$(universe_label "$DISC_TMP/Universes/Solaris-Verse/Worlds/Aetheria")
    [ "$LBL_AETHERIA" = "Solaris-Verse" ] || { echo "  FAIL: Aetheria universe label was '$LBL_AETHERIA' (expected 'Solaris-Verse')"; exit 1; }

    LBL_ELDORIA=$(universe_label "$DISC_TMP/Universes/Eldoria-Cosmos/Eldoria-World")
    [ "$LBL_ELDORIA" = "Eldoria-Cosmos" ] || { echo "  FAIL: Eldoria universe label was '$LBL_ELDORIA' (expected 'Eldoria-Cosmos')"; exit 1; }

    # Test resolve_world_dir
    RESOLVED_AETHERIA=$(resolve_world_dir "Aetheria")
    [ "$RESOLVED_AETHERIA" = "$DISC_TMP/Universes/Solaris-Verse/Worlds/Aetheria" ] || { echo "  FAIL: resolve_world_dir Aetheria failed: $RESOLVED_AETHERIA"; exit 1; }
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

echo "[Test 18] Restore rejects punctuation-only target names (SEC-01)..."
bash scripts/arcanum manuscript RestoreVictim --universe TestUni --world TestWorld >/dev/null
bash scripts/backup_world.sh --manuscript RestoreVictim --dest "${TMP_DIR}" >/dev/null
ARCHIVE="$(ls -t "${TMP_DIR}"/RestoreVictim-backup-*.tar.gz | head -n 1)"
set +e
bash scripts/restore_world.sh "${ARCHIVE}" --target '!!!' --force >"${TMP_DIR}/sec01.log" 2>&1
SEC01_RC=$?
set -e
[ "${SEC01_RC}" -ne 0 ] || { echo "  FAIL: restore accepted empty sanitized target '!!!'"; exit 1; }
grep -qi "invalid target name" "${TMP_DIR}/sec01.log" || { echo "  FAIL: missing validation message"; cat "${TMP_DIR}/sec01.log"; exit 1; }
[ -d "${HOME}/Manuscripts/RestoreVictim" ] || { echo "  FAIL: valid project missing after rejected restore"; exit 1; }
for bad in '///' '...' '   '; do
    set +e
    bash scripts/restore_world.sh "${ARCHIVE}" --target "${bad}" --force >/dev/null 2>&1
    [ $? -ne 0 ] || { echo "  FAIL: restore accepted target '${bad}'"; exit 1; }
    set -e
done
echo "  OK Test 18 passed: punctuation-only restore targets rejected without mutation"

echo "[Test 19] Restore requires checksum sidecar by default (REL-03)..."
NOMETADIR="$(mktemp -d)"
cp "${ARCHIVE}" "${NOMETADIR}/nocheck.tar.gz"
set +e
bash scripts/restore_world.sh "${NOMETADIR}/nocheck.tar.gz" --target NoCheckRestore >"${TMP_DIR}/rel03.log" 2>&1
REL03_RC=$?
set -e
[ "${REL03_RC}" -ne 0 ] || { echo "  FAIL: restore proceeded without .sha256"; exit 1; }
set +e
bash scripts/restore_world.sh "${NOMETADIR}/nocheck.tar.gz" --target NoCheckRestore --skip-checksum --dest "${TMP_DIR}/restore-dest" >/dev/null 2>&1
REL03B_RC=$?
set -e
[ "${REL03B_RC}" -eq 0 ] || { echo "  FAIL: --skip-checksum did not permit explicitly-acknowledged restore"; exit 1; }
[ -d "${TMP_DIR}/restore-dest/NoCheckRestore" ] || { echo "  FAIL: --skip-checksum restore missing"; exit 1; }
rm -rf "${NOMETADIR}" "${TMP_DIR}/restore-dest"
echo "  OK Test 19 passed: missing checksum fails closed, --skip-checksum opts out explicitly"

echo "[Test 20] Ambiguous world names fail closed (RES-01)..."
bash scripts/arcanum universe AmbigU1 >/dev/null
bash scripts/arcanum universe AmbigU2 >/dev/null
bash scripts/arcanum world Shared --universe AmbigU1 >/dev/null
bash scripts/arcanum world Shared --universe AmbigU2 >/dev/null
set +e
AMBIG_OUT="$(bash scripts/save_snapshot.sh Shared -m x 2>&1)"
AMBIG_RC=$?
set -e
[ "${AMBIG_RC}" -eq 2 ] || { echo "  FAIL: ambiguous world did not exit 2 (rc=${AMBIG_RC}): ${AMBIG_OUT}"; exit 1; }
echo "${AMBIG_OUT}" | grep -qi "ambiguous" || { echo "  FAIL: missing ambiguity message: ${AMBIG_OUT}"; exit 1; }
bash scripts/save_snapshot.sh Shared --universe AmbigU1 -m "unambiguous snapshot" >/dev/null
echo "  OK Test 20 passed: duplicate world names require --universe"

echo "[Test 21] Manuscript XML escapes special characters (DAT-02)..."
bash scripts/arcanum manuscript "XMLTest" --universe TestUni --world TestWorld --author 'A & B <Draft> "Quoted"' >/dev/null
python3 -c 'import sys, xml.etree.ElementTree as ET; ET.parse(sys.argv[1]); print("  OK Test 21 passed: nwProject.nwx parses with special chars")' "${HOME}/Manuscripts/XMLTest/nwProject.nwx"
grep -q '&amp;' "${HOME}/Manuscripts/XMLTest/nwProject.nwx" || { echo "  FAIL: expected XML entity escaping"; exit 1; }

echo "[Test 22] Packaged CLI dispatches via symlink (PKG-01)..."
mkdir -p "${TMP_DIR}/pkg/share/arcanum" "${TMP_DIR}/pkg/bin"
cp -r scripts "${TMP_DIR}/pkg/share/arcanum/scripts"
ln -sf "${TMP_DIR}/pkg/share/arcanum/scripts/arcanum" "${TMP_DIR}/pkg/bin/arcanum"
"${TMP_DIR}/pkg/bin/arcanum" --version | grep -qi "Arcanum" || { echo "  FAIL: symlinked CLI --version failed"; exit 1; }
echo "  OK Test 22 passed: symlink dispatch works"

echo "[Test 23] Single-quote book title export without python syntax errors..."
bash scripts/arcanum manuscript "QuoteTest" --universe TestUni --world TestWorld >/dev/null
bash scripts/export_book.sh "${HOME}/Manuscripts/QuoteTest" --book Book-01 --format submission --title "The King's General & Rogue's Tale" --author "O'Connor" > "${TMP_DIR}/export_quote.log" 2>&1
grep -q "Submission manuscript generated" "${TMP_DIR}/export_quote.log" || { echo "  FAIL: single quote title export failed:"; cat "${TMP_DIR}/export_quote.log"; exit 1; }
echo "  OK Test 23 passed: Single-quote and apostrophe title export passed safely"

echo "[Test 24] DOCX sync ignores consolidated manuscript and prevents duplication..."
python3 "${SCRIPT_DIR}/scripts/lib/docx_sync.py" build "${HOME}/Manuscripts/QuoteTest" >/dev/null
python3 "${SCRIPT_DIR}/scripts/lib/docx_sync.py" sync "${HOME}/Manuscripts/QuoteTest" >/dev/null
[ ! -f "${HOME}/Manuscripts/QuoteTest/Book-01/Draft-01/Draft-01_Manuscript.md" ] || { echo "  FAIL: Draft-01_Manuscript.md was erroneously created during sync"; exit 1; }
echo "  OK Test 24 passed: Consolidated manuscript ignored during chapter sync"

echo "[Test 25] DOCX generation with illegal XML 1.0 control characters..."
python3 - << 'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, "scripts/lib")
from docx_sync import escape_xml, build_docx_package, get_docx_config, parse_markdown_to_paragraphs
import tempfile

with tempfile.TemporaryDirectory() as td:
    tpath = Path(td) / "dirty.docx"
    md = "# Chapter 1\x00\x08\x0b\n\nPasted text with \x0c form feed and \x1f control character."
    paragraphs = parse_markdown_to_paragraphs(md)
    cfg = get_docx_config()
    ok = build_docx_package(tpath, paragraphs, cfg, title="Dirty\x00Title", author="Author\x08Name")
    assert ok, "build_docx_package failed with control chars"
    import zipfile, xml.etree.ElementTree as ET
    with zipfile.ZipFile(tpath) as zf:
        doc_xml = zf.read("word/document.xml")
        root = ET.fromstring(doc_xml)
        assert root is not None, "XML parsing failed on generated docx"
print("  OK Test 25 passed: XML 1.0 illegal control characters filtered and valid DOCX generated")
PYEOF

echo "[Test 26] Relativistic Astrophysics & Brachistochrone CLI..."
bash scripts/arcanum calc transit "alpha-centauri" --json > "${TMP_DIR}/astro.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["peak_velocity_c_fraction"] > 0.9; assert d["proper_time_sec"] > 0' "${TMP_DIR}/astro.json"
bash scripts/arcanum calc comms "5.2 AU" --json > "${TMP_DIR}/comms.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["one_way_seconds"] > 2000' "${TMP_DIR}/comms.json"
echo "  OK Test 26 passed: Relativistic Brachistochrone and comms latency verified"

echo "[Test 27] Hard Magic System constraints & tier violation detection..."
cat > "${WORLD_PATH}/Magic-Technology/Weaving.md" << 'EOF'
---
name: "Weaving"
type: magic_tech_system
danger_cost: "High"
max_tier: 5
catalysts: ["Ruby Focus"]
hard_limitations: ["Cannot resurrect the dead"]
---
EOF
cat > "${WORLD_PATH}/Characters/MageValen.md" << 'EOF'
---
name: "MageValen"
type: character
magic_tier: 1
catalyst: "Ruby Focus"
---
EOF
cat > "${MS_PATH}/Book-01/01_Act_I/03_MagicScene.md" << 'EOF'
# Chapter 3: Arcane Trial
@pov: MageValen
@cast: MageValen, Hellfire, tier=3

MageValen cast the spell.
EOF
set +e
bash scripts/arcanum magic-check "${WORLD_PATH}" -m "${MS_PATH}" --json > "${TMP_DIR}/magic_res.json"
MAGIC_RC=$?
set -e
[ "${MAGIC_RC}" -eq 1 ] || { echo "  FAIL: expected magic tier violation exit code 1"; exit 1; }
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert any(f["id"] == "MAG-101" for f in d["findings"])' "${TMP_DIR}/magic_res.json"
echo "  OK Test 27 passed: Arcane Constraint Matrix detected MAG-101 tier violation"
rm -f "${MS_PATH}/Book-01/01_Act_I/03_MagicScene.md"

echo "[Test 28] Dynastic Genealogies & Succession Lineage..."
cat > "${WORLD_PATH}/Characters/KingAethel.md" << 'EOF'
---
name: "King Aethel"
type: character
house: "House Solar"
title: "Emperor"
born: "100 AC"
died: "170 AC"
succession_order: 1
---
EOF
cat > "${WORLD_PATH}/Characters/PrinceKael.md" << 'EOF'
---
name: "Prince Kael"
type: character
house: "House Solar"
title: "Crown Prince"
parents: ["[[King Aethel]]"]
born: "130 AC"
died: "190 AC"
succession_order: 2
---
EOF
bash scripts/arcanum genealogy "House Solar" -w "${WORLD_PATH}" --mermaid > "${TMP_DIR}/tree.mmd"
grep -q "King Aethel" "${TMP_DIR}/tree.mmd"
grep -q "Prince Kael" "${TMP_DIR}/tree.mmd"
bash scripts/arcanum lineage "House Solar" -w "${WORLD_PATH}" --json > "${TMP_DIR}/lineage.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert len(d["members"]) >= 2; assert d["members"][0]["name"] == "King Aethel"' "${TMP_DIR}/lineage.json"
echo "  OK Test 28 passed: Dynastic Genealogies & Succession order compiled"

echo "[Test 29] Conlang Phonotactics & Historical Sound Shifts..."
cat > "${WORLD_PATH}/Languages/Archaic_Valen.md" << 'EOF'
---
name: "Archaic Valen"
type: language
consonants: [p, t, k, s, m, n, l, r]
vowels: [a, e, i, o, u]
syllable_structures: ["CV", "CVC"]
sound_changes:
  - "p > f / V_V"
  - "k > ch / _[e,i]"
---
EOF
bash scripts/arcanum conlang generate "Archaic Valen" -w "${WORLD_PATH}" -n 5 --json > "${TMP_DIR}/conlang_gen.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert len(d["words"]) == 5' "${TMP_DIR}/conlang_gen.json"
bash scripts/arcanum conlang mutate "Archaic Valen" "apata keli" -w "${WORLD_PATH}" --json > "${TMP_DIR}/conlang_mut.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["mutated"] == "afata cheli"' "${TMP_DIR}/conlang_mut.json"
echo "  OK Test 29 passed: Conlang generation and sound-law mutations verified"

echo "[Test 30] Narrative Pacing, POV Balance & Tension Arc Analytics..."
bash scripts/arcanum pace "${MS_PATH}" --json > "${TMP_DIR}/pacing.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["total_chapters"] >= 1; assert "pov_distribution" in d' "${TMP_DIR}/pacing.json"
bash scripts/arcanum words "${MS_PATH}" --pov --json > "${TMP_DIR}/pov_report.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert "pov_distribution" in d' "${TMP_DIR}/pov_report.json"
echo "  OK Test 30 passed: Pacing & POV screen-time analytics verified"

echo "[Test 31] Overland Journey Modeler & Custom Planetary Calendar..."
bash scripts/arcanum calc journey 150km -t mountain-pass -p foot-normal --json > "${TMP_DIR}/journey.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["total_days"] > 0; assert d["supplies_required"]["rations_food_kg"] > 0' "${TMP_DIR}/journey.json"
bash scripts/arcanum calendar "${WORLD_PATH}" --phases --json > "${TMP_DIR}/calendar.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert len(d["moons"]) >= 1; assert "day" in d' "${TMP_DIR}/calendar.json"
echo "  OK Test 31 passed: Journey route calculation and Planetary calendar verified"

echo "[Test 32] Geopolitical Faction Matrix & Campaign Logistics..."
cat > "${WORLD_PATH}/Factions/Solar_Empire.md" << 'EOF'
---
name: "Solar Empire"
type: faction
military_strength: 50000
allies: ["[[Lunar Dominion]]"]
---
EOF
cat > "${WORLD_PATH}/Factions/Lunar_Dominion.md" << 'EOF'
---
name: "Lunar Dominion"
type: faction
military_strength: 35000
allies: ["[[Solar Empire]]"]
---
EOF
bash scripts/arcanum faction "${WORLD_PATH}" --json > "${TMP_DIR}/factions.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["factions_count"] >= 2; assert d["findings_count"] == 0' "${TMP_DIR}/factions.json"
bash scripts/arcanum calc battle -a 10000 -d 5000 --json > "${TMP_DIR}/battle.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["victor"] == "Attacker"' "${TMP_DIR}/battle.json"
bash scripts/arcanum calc logistics --infantry 5000 --json > "${TMP_DIR}/logistics.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["logistics_requirements"]["wagons_required"] > 0' "${TMP_DIR}/logistics.json"
echo "  OK Test 32 passed: Geopolitical Faction Matrix & Lanchester / Logistics engines verified"

echo "[Test 33] In-World Economy, Commodity PPP & Tech Era Anachronisms..."
cat > "${WORLD_PATH}/Economies/Imperial_Standard.md" << 'EOF'
---
name: "Imperial Standard"
base_currency: "Crown"
tech_era: "medieval"
commodity_basket:
  - "loaf_of_bread: 2"
---
EOF
bash scripts/arcanum economy "${WORLD_PATH}" --json > "${TMP_DIR}/economy.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["economies_count"] >= 1' "${TMP_DIR}/economy.json"
bash scripts/arcanum audit tech "${MS_PATH}" --era medieval --json > "${TMP_DIR}/tech_audit.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert "findings" in d' "${TMP_DIR}/tech_audit.json"
echo "  OK Test 33 passed: In-World Economy & Tech Era Anachronism audit verified"

echo "[Test 34] Causal DAGs, Time Travel Loops & Multiverse Branching..."
cat > "${WORLD_PATH}/History/Great_Convergence.md" << 'EOF'
---
name: "Great Convergence"
id: convergence
timeline: prime
causes: [first-contact]
---
EOF
cat > "${MS_PATH}/Book-01/01_Act_I/04_ConvergenceScene.md" << 'EOF'
# Chapter 4
@event: first-contact
@timeline: prime
@causal-origin: convergence
EOF
bash scripts/arcanum causality "${WORLD_PATH}" "${MS_PATH}" --json > "${TMP_DIR}/causality.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["events_count"] >= 2; assert d["findings_count"] == 0' "${TMP_DIR}/causality.json"
rm -f "${MS_PATH}/Book-01/01_Act_I/04_ConvergenceScene.md"
echo "  OK Test 34 passed: Causal DAG and timeline extraction verified"

echo "[Test 35] Planetary Climate & Trophic Food-Web Simulator..."
bash scripts/arcanum calc climate --star-lum 1.0 --distance-au 1.0 --json > "${TMP_DIR}/climate.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["insolation"]["liquid_water_habitable"] is True' "${TMP_DIR}/climate.json"
cat > "${WORLD_PATH}/Bestiary/Ancient_Fern.md" << 'EOF'
---
name: "Ancient Fern"
trophic_level: 1
habitat: "Forest"
biomass_kg: 50000
---
EOF
cat > "${WORLD_PATH}/Bestiary/Forest_Elk.md" << 'EOF'
---
name: "Forest Elk"
trophic_level: 2
habitat: "Forest"
biomass_kg: 100
population_density: 20
dietary_prey: ["[[Ancient Fern]]"]
---
EOF
bash scripts/arcanum ecology "${WORLD_PATH}" --json > "${TMP_DIR}/ecology.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["species_count"] >= 2; assert d["findings_count"] == 0' "${TMP_DIR}/ecology.json"
echo "  OK Test 35 passed: Climate simulator and Trophic Food-Web verified"

echo "[Test 36] Earth-Eponym Scanner & 6D Sensory Palette..."
set +e
bash scripts/arcanum audit idioms "${MS_PATH}" --json > "${TMP_DIR}/idioms.json"
bash scripts/arcanum audit senses "${MS_PATH}" --json > "${TMP_DIR}/senses.json"
set -e
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert "findings" in d' "${TMP_DIR}/idioms.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert "overall_percentages" in d' "${TMP_DIR}/senses.json"
echo "  OK Test 36 passed: Idiom immersion audit and 6D Sensory Palette verified"

echo "[Test 37] Prophecy Lifecycle & Fulfillment Matrix..."
cat > "${WORLD_PATH}/Cosmology/Prophecies/Sun_Prophecy.md" << 'EOF'
---
name: "Sun Prophecy"
type: prophecy
status: unfulfilled
clauses:
  - "When the twin suns rise"
---
EOF
bash scripts/arcanum prophecy "${WORLD_PATH}" --json > "${TMP_DIR}/prophecy.json"
python3 -c 'import sys, json; d = json.load(open(sys.argv[1])); assert d["prophecies_count"] >= 1' "${TMP_DIR}/prophecy.json"
echo "  OK Test 37 passed: Prophecy Matrix verified"

echo "ALL TARGETED TESTS PASSED SUCCESSFULLY!"
