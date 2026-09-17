#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Comprehensive Verification Harness
# Usage: bash scripts/verify.sh
# ==============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TMP_VERIFY="$(mktemp -d)"
# TST-02: save/restore HOME around the sandboxed lifecycle stage.
ORIG_HOME="${HOME:-}"
cleanup() {
    rm -rf "${TMP_VERIFY:-}"
    if [ -n "${ORIG_HOME:-}" ]; then
        HOME="${ORIG_HOME}"
        export HOME
    fi
}
trap cleanup EXIT

echo "[1/7] Script syntax & Python compilation validation..."
# TST-02: same bash -n file set as CI (ci.yml) — scripts + lib + facade + tests.
for f in scripts/*.sh scripts/lib/*.sh scripts/scriptorium tests/*.sh; do
    if [ -f "$f" ]; then
        if ! bash -n "$f"; then
            echo "  FAIL $f (bash syntax)" >&2
            exit 1
        fi
        echo "  OK $f"
    fi
done
if command -v python3 >/dev/null; then
    for py in scripts/scriptorium_app.py scripts/lib/*.py; do
        if [ -f "$py" ]; then
            if ! python3 -m py_compile "$py"; then
                echo "  FAIL $py (Python compilation)" >&2
                exit 1
            fi
            echo "  OK $py (Python syntax valid)"
        fi
    done
    if ! python3 -m unittest discover -s tests -p "test_*.py" > "${TMP_VERIFY}/py_unit.log" 2>&1; then
        echo "  FAIL Python unit tests (unittest discover tests/test_*.py)" >&2
        cat "${TMP_VERIFY}/py_unit.log" >&2
        exit 1
    fi
    echo "  OK Python unit tests (unittest discover tests/test_*.py)"
fi

echo "[2/7] JSON, XML & Documentation schema validation..."
# 2a. Author Manual verification
[ -f "docs/AUTHOR_MANUAL.md" ] || { echo "  FAIL missing docs/AUTHOR_MANUAL.md"; exit 1; }
python3 - << 'PYEOF'
with open('docs/AUTHOR_MANUAL.md', 'r', encoding='utf-8') as f:
    text = f.read()
assert len(text) > 5000, "docs/AUTHOR_MANUAL.md is unexpectedly short"
for ch in ("## 1. ", "## 2. ", "## 3. ", "## 4. ", "## 5. ", "## 6. ", "## 7. ", "## 8. "):
    assert ch in text, f"Missing section {ch} in docs/AUTHOR_MANUAL.md"
print("  OK Author's Field Manual structure & chapter integrity")
PYEOF

# 2b. LeechBlock JSON schema validation
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

# 2c. novelWriter XML schema validation
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

# 2d. Obsidian vault pre-configured suite validation
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

# Validate fileClasses schemas
for fc in ("Character", "Location", "Faction", "TimelineEvent", "Creature", "Artifact", "Cosmology", "MagicSystem", "Language"):
    fc_path = f"templates/world-bible/Templates/fileClasses/{fc}.md"
    assert os.path.isfile(fc_path), f"Missing fileClass schema: {fc_path}"
    with open(fc_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert f"fileClass: {fc}" in content, f"Invalid fileClass header in {fc_path}"

# Validate obsidian-git settings schema
git_cfg = 'templates/world-bible/.obsidian/plugins/obsidian-git/data.json'
assert os.path.isfile(git_cfg), "Missing obsidian-git data.json"
with open(git_cfg) as f:
    gdata = json.load(f)
assert gdata.get("basePath") in ("", None), "obsidian-git basePath must be empty for direct vault repository root"
for dead_key in ("gitLocation", "baseSubmodule", "autoBackupFileName"):
    assert dead_key not in gdata, f"Dead/invalid key '{dead_key}' found in obsidian-git settings"

# Validate Beginner Onboarding notes
assert os.path.isfile("templates/world-bible/00_START_HERE.md"), "Missing 00_START_HERE.md"
assert os.path.isfile("templates/world-bible/Characters/Character-Quickstart-Template.md"), "Missing Character-Quickstart-Template.md"

print("  OK Obsidian pre-configured plugin, obsidian-git basePath, fileClasses & quickstart schemas")
PYEOF

# 2e. Subplot Outline & Decluttering verification
[ -f "templates/manuscript/Outlines/Subplot-Thread-Matrix.md" ] || { echo "  FAIL missing Subplot-Thread-Matrix.md"; exit 1; }
[ ! -f "Finishing_Touches.md" ] || { echo "  FAIL obsolete Finishing_Touches.md must be removed"; exit 1; }
grep -q "@thread:" "templates/manuscript/Outlines/Subplot-Thread-Matrix.md" || { echo "  FAIL missing @thread: tag conventions in Subplot-Thread-Matrix.md"; exit 1; }
echo "  OK Subplot & Narrative Thread Matrix template & root decluttering"

echo "[3/7] Pandoc Markdown->Typst smoke test..."
if command -v pandoc >/dev/null; then
    if pandoc --list-output-formats 2>/dev/null | grep -q typst; then
        echo "  OK pandoc typst writer present"
    else
        echo "  WARN pandoc lacks native typst writer (sed fallback will be used)"
    fi
    if ! printf '# Ch1\n\nHello *world*.\n' | pandoc -f markdown-citations+smart -t typst -o "${TMP_VERIFY}/body.typ" 2>/dev/null; then
        echo "  FAIL pandoc markdown->typst conversion" >&2
        exit 1
    fi
    echo "  OK pandoc conversion"
else
    echo "  SKIP pandoc missing on this host"
fi

echo "[4/7] Typst compile smoke test (if installed)..."
if command -v typst >/dev/null; then
    if ! (cd templates/typst && typst compile preview_sample.typ "${TMP_VERIFY}/preview.pdf"); then
        echo "  FAIL typst compile of preview_sample.typ" >&2
        exit 1
    fi
    echo "  OK typst compile"
    ls -lh "${TMP_VERIFY}/preview.pdf"
else
    echo "  SKIP typst missing on this host (install per docs/guides/SOFTWARE_CATALOG.md)"
fi

echo "[5/7] Desktop launcher validation..."
if command -v desktop-file-validate >/dev/null; then
    if ! desktop-file-validate launchers/*.desktop; then
        echo "  FAIL desktop launcher validation" >&2
        exit 1
    fi
    echo "  OK desktop files"
else
    TRYEXEC_FAIL=0
    for lf in launchers/*.desktop; do
        if ! grep -q '^TryExec=bash$' "$lf"; then
            echo "  FAIL missing TryExec=bash in $lf" >&2
            TRYEXEC_FAIL=1
        fi
    done
    if [ "${TRYEXEC_FAIL}" -ne 0 ]; then
        exit 1
    fi
    echo "  OK TryExec present in all launchers (validator tool skipped)"
fi

echo "[6/7] Functional Universe, World & Manuscript lifecycle, diagnostics & recovery (sandboxed HOME)..."
export HOME="${TMP_VERIFY}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

# 6a. Universe initialization
UNIVERSE="TestMultiverse"
bash scripts/init_universe.sh "${UNIVERSE}" >/dev/null
[ -d "${HOME}/Universes/${UNIVERSE}" ] || { echo "  FAIL universe directory missing"; exit 1; }
[ -d "${HOME}/Universes/${UNIVERSE}/.git" ] || { echo "  FAIL universe git repository missing"; exit 1; }
[ -f "${HOME}/Universes/${UNIVERSE}/universe.yaml" ] || { echo "  FAIL universe yaml manifest missing"; exit 1; }
[ -f "${HOME}/Universes/${UNIVERSE}/Universe-Index.md" ] || { echo "  FAIL universe index note missing"; exit 1; }
echo "  OK init_universe (Universe directory + Universe Git repository + Index Hub)"

# 6b. Pure World Lore Vault initialization inside Universe
WORLD="VerifyWorld"
bash scripts/init_world.sh "${WORLD}" --universe "${UNIVERSE}" >/dev/null
WORLD_PATH="${HOME}/Universes/${UNIVERSE}/${WORLD}"
[ -d "${WORLD_PATH}/Characters" ] || { echo "  FAIL world Characters taxonomy missing"; exit 1; }
[ -d "${WORLD_PATH}/Bestiary" ] || { echo "  FAIL world Bestiary taxonomy missing"; exit 1; }
[ -d "${WORLD_PATH}/Artifacts" ] || { echo "  FAIL world Artifacts taxonomy missing"; exit 1; }
[ -d "${WORLD_PATH}/Cosmology" ] || { echo "  FAIL world Cosmology taxonomy missing"; exit 1; }
[ -f "${WORLD_PATH}/.obsidian/community-plugins.json" ] || { echo "  FAIL obsidian config missing"; exit 1; }
[ -f "${WORLD_PATH}/world.yaml" ] || { echo "  FAIL world.yaml missing"; exit 1; }
[ -d "${WORLD_PATH}/.git" ] || { echo "  FAIL world lore git repository missing"; exit 1; }
echo "  OK init_world (Pure World Lore Vault + Obsidian Plugin Suite + Discrete Lore Git Repository)"

# 6c. Standalone Manuscript Project initialization linked to Universe & World
MANUSCRIPT="VerifyManuscript"
bash scripts/init_manuscript.sh "${MANUSCRIPT}" --universe "${UNIVERSE}" --world "${WORLD}" >/dev/null
MS_PATH="${HOME}/Manuscripts/${MANUSCRIPT}"
[ -f "${MS_PATH}/manuscript.yaml" ] || { echo "  FAIL manuscript.yaml manifest missing"; exit 1; }
[ -f "${MS_PATH}/nwProject.nwx" ] || { echo "  FAIL nwProject.nwx missing"; exit 1; }
[ -d "${MS_PATH}/Book-01/01_Act_I" ] || { echo "  FAIL Book-01 Act I missing"; exit 1; }
[ -d "${MS_PATH}/Book-01/02_Act_II" ] || { echo "  FAIL Book-01 Act II missing"; exit 1; }
[ -d "${MS_PATH}/Book-01/03_Act_III" ] || { echo "  FAIL Book-01 Act III missing"; exit 1; }
[ -d "${MS_PATH}/Book-01/.git" ] || { echo "  FAIL discrete Book-01 git repository missing"; exit 1; }
[ -d "${MS_PATH}/.git" ] || { echo "  FAIL manuscript root git repository missing"; exit 1; }
echo "  OK init_manuscript (Manuscript root repo + Book-01 discrete volume repo + 3-Act structure)"

# 6d. Test add-volume volume scaffolding & tag-poisoning test chapters
bash scripts/scriptorium add-volume "${MS_PATH}" "Book-02" >/dev/null
[ -d "${MS_PATH}/Book-02/01_Act_I" ] || { echo "  FAIL Book-02 Act I missing"; exit 1; }
[ -d "${MS_PATH}/Book-02/02_Act_II" ] || { echo "  FAIL Book-02 Act II missing"; exit 1; }
[ -d "${MS_PATH}/Book-02/03_Act_III" ] || { echo "  FAIL Book-02 Act III missing"; exit 1; }
[ -d "${MS_PATH}/Book-02/.git" ] || { echo "  FAIL Book-02 discrete git repo missing"; exit 1; }
echo "  OK add-volume volume scaffolding (Acts + discrete Git repo)"

cat > "${MS_PATH}/Book-02/01_Act_I/01_Chapter_05.md" << 'EOF'
# Chapter 5: The Second Book Begins

This chapter lives in Book-02 and must appear in exports.

@location: SunCitadel
@time: 1899-03-14
@plot: The Heist
@theme: Honor & Steel
EOF

# 6e. Export book compilation (Testing specific volume selection, paper size, submission format & omnibus)
set +e
bash scripts/export_book.sh "${MS_PATH}" --book Book-01 --paper-size trade --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export_b1.log" 2>&1
EXPORT_B1_RC=$?
bash scripts/export_book.sh "${MS_PATH}" --book all --paper-size us-trade --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export_all.log" 2>&1
EXPORT_ALL_RC=$?
bash scripts/export_book.sh "${MS_PATH}" --book Book-01 --format submission --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export_docx.log" 2>&1
EXPORT_DOCX_RC=$?
set -e

if command -v typst >/dev/null && command -v pandoc >/dev/null; then
    if [ "${EXPORT_B1_RC}" -ne 0 ] || [ "${EXPORT_ALL_RC}" -ne 0 ] || [ "${EXPORT_DOCX_RC}" -ne 0 ]; then
        echo "  FAIL export_book failed (B1=${EXPORT_B1_RC}, ALL=${EXPORT_ALL_RC}, DOCX=${EXPORT_DOCX_RC})"
        tail -n 5 "${TMP_VERIFY}/export_b1.log"
        tail -n 5 "${TMP_VERIFY}/export_all.log"
        tail -n 5 "${TMP_VERIFY}/export_docx.log"
        exit 1
    fi
    echo "  OK export_book (exit 0 across volume-isolated, omnibus, and submission formats)"

    PDF_OMNI="${MS_PATH}/Exports/Verify_Book.pdf"
    EPUB_OMNI="${MS_PATH}/Exports/Verify_Book.epub"
    PDF_B1="${MS_PATH}/Exports/Verify_Book_Book-01.pdf"
    EPUB_B1="${MS_PATH}/Exports/Verify_Book_Book-01.epub"
    DOCX_B1="${MS_PATH}/Exports/Verify_Book_Book-01_Submission.docx"

    [ -s "${PDF_OMNI}" ] || { echo "  FAIL missing or empty omnibus PDF: ${PDF_OMNI}"; exit 1; }
    [ -s "${EPUB_OMNI}" ] || { echo "  FAIL missing or empty omnibus EPUB: ${EPUB_OMNI}"; exit 1; }
    [ -s "${PDF_B1}" ] || { echo "  FAIL missing or empty Book-01 PDF: ${PDF_B1}"; exit 1; }
    [ -s "${EPUB_B1}" ] || { echo "  FAIL missing or empty Book-01 EPUB: ${EPUB_B1}"; exit 1; }
    [ -s "${DOCX_B1}" ] || { echo "  FAIL missing or empty Book-01 submission DOCX: ${DOCX_B1}"; exit 1; }
    echo "  OK PDF + EPUB + DOCX produced and verified non-empty"

    python3 - "${EPUB_OMNI}" "${EPUB_B1}" << 'PYEOF'
import sys, zipfile

def read_epub_text(path):
    z = zipfile.ZipFile(path)
    txt = ""
    for n in z.namelist():
        if n.endswith((".xhtml", ".html", ".ncx", ".opf")):
            txt += z.read(n).decode("utf-8", "ignore")
    return txt

omni_txt = read_epub_text(sys.argv[1])
b1_txt = read_epub_text(sys.argv[2])

# Omnibus checks
assert "Second Book Begins" in omni_txt, "Book-02 volume missing from omnibus export"
assert "1899-03-14" not in omni_txt, "novelWriter @time tag leaked into omnibus export"
assert "The Heist" not in omni_txt, "novelWriter @plot tag leaked into omnibus export"
assert "Honor & Steel" not in omni_txt, "novelWriter custom @theme tag leaked into omnibus export"

# Volume-isolated checks
assert "Second Book Begins" not in b1_txt, "Book-02 volume improperly leaked into Book-01 export"
assert "1899-03-14" not in b1_txt, "novelWriter @time tag leaked into Book-01 export"

print("  OK multi-volume isolation + omnibus inclusion + tag stripping verified in EPUB")
PYEOF
else
    echo "  SKIP full PDF/EPUB/DOCX export build (typst/pandoc not installed in local environment)"
fi

# 6f. Multi-Era World Doctor consistency check
cat > "${WORLD_PATH}/Characters/Aethelgard.md" << 'EOF'
---
name: "Aethelgard"
type: character
role: protagonist
birth_year: "450 BCE"
death_year: "380 BCE"
---
A legendary general from the classical era.
EOF

cat > "${WORLD_PATH}/History/The_Great_Sundering.md" << 'EOF'
---
name: "The Great Sundering"
type: timeline_event
start_year: "-450 IE"
end_year: "-400 IE"
---
An ancient cataclysm reshaping the realms.
EOF

# TST-03: explicit exit-code handling — 0/1 are valid doctor outcomes
# (clean/findings); 2+ is a harness failure and must abort loudly.
set +e
DOCTOR_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json 2>"${TMP_VERIFY}/doctor1.err")"
DOCTOR_RC=$?
set -e
if [ "${DOCTOR_RC}" -gt 1 ]; then
    echo "  FAIL world_doctor valid-timeline run exited ${DOCTOR_RC}" >&2
    cat "${TMP_VERIFY}/doctor1.err" >&2
    exit 1
fi
printf '%s' "${DOCTOR_JSON}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['notes'] >= 0
assert len(d['timeline_errors']) == 0
print('  OK world_doctor multi-era valid timeline passed')
"

# Test chronological paradox detection
cat > "${WORLD_PATH}/Characters/ParadoxLord.md" << 'EOF'
---
name: "ParadoxLord"
type: character
role: antagonist
birth_year: "Age of Fire 500"
death_year: "Age of Fire 410"
---
A chronologically inverted paradox lord.
EOF

set +e
DOCTOR_ERR_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json 2>"${TMP_VERIFY}/doctor2.err")"
DOCTOR_RC=$?
set -e
if [ "${DOCTOR_RC}" -gt 1 ]; then
    echo "  FAIL world_doctor paradox run exited ${DOCTOR_RC}" >&2
    cat "${TMP_VERIFY}/doctor2.err" >&2
    exit 1
fi
printf '%s' "${DOCTOR_ERR_JSON}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert any('ParadoxLord' in e['file'] for e in d['timeline_errors'])
print('  OK world_doctor multi-era chronological paradox error caught')
"
rm -f "${WORLD_PATH}/Characters/ParadoxLord.md"

# Test WLD-108 manuscript name drift detection
cat > "${MS_PATH}/Book-01/01_Act_I/02_Drift_Scene.md" << 'EOF'
# Chapter 2: The Ghosted City
@pov: GhostHero
@location: NonExistentCitadel

A scene referencing unindexed lore entities.
EOF

set +e
DOCTOR_DRIFT_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --manuscript "${MS_PATH}" --json 2>"${TMP_VERIFY}/doctor3.err")"
DOCTOR_RC=$?
set -e
if [ "${DOCTOR_RC}" -gt 1 ]; then
    echo "  FAIL world_doctor drift run exited ${DOCTOR_RC}" >&2
    cat "${TMP_VERIFY}/doctor3.err" >&2
    exit 1
fi
printf '%s' "${DOCTOR_DRIFT_JSON}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert any('GhostHero' in e['missing'] for e in d.get('manuscript_name_drift', [])), 'WLD-108 missed GhostHero drift'
assert any('NonExistentCitadel' in e['missing'] for e in d.get('manuscript_name_drift', [])), 'WLD-108 missed NonExistentCitadel drift'
print('  OK world_doctor WLD-108 manuscript name drift detected correctly')
"
rm -f "${MS_PATH}/Book-01/01_Act_I/02_Drift_Scene.md"

# 6g. Back-Matter Concordance & Dramatis Personae Engine
cat > "${WORLD_PATH}/Factions/Solar_Hegemony.md" << 'EOF'
---
name: "Solar Hegemony"
type: faction
faction_type: "Empire"
leader: "[[Aethelgard]]"
headquarters: "Sun Citadel"
motto: "Light Eternal"
---
## 1. Executive Overview
The dominant star empire ruling the core worlds.
EOF

cat > "${WORLD_PATH}/Artifacts/Solar_Scepter.md" << 'EOF'
---
name: "Solar Scepter"
type: artifact
artifact_type: "Relic"
rarity: "Legendary"
current_bearer: "[[Aethelgard]]"
---
## 1. Physical Description
A radiant staff focusing cosmic energy.
EOF

cat > "${WORLD_PATH}/Bestiary/Void_Stalker.md" << 'EOF'
---
name: "Void Stalker"
type: creature
classification: "Apex Predator"
threat_level: "Lethal"
habitat: "Outer Rim"
---
## 1. Physical Anatomy
Lethal shadow beasts navigating vacuum.
EOF

cat > "${WORLD_PATH}/Languages/Solar_Tongue.md" << 'EOF'
---
name: "Solar Tongue"
type: language
language_family: "High Archaic"
spoken_by: "[[Solar_Hegemony]]"
---
## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Aethel* | Noun | /ˈaɪ.θəl/ | Sun King | Royal honorific |
| *Vaelor* | Noun | /ˈvaɪ.lɔːr/ | Eternal Shield | Military vow |
EOF

bash scripts/scriptorium concordance "${WORLD_PATH}" --manuscript "${MS_PATH}" --book Book-01 >/dev/null
[ -f "${MS_PATH}/Book-01/04_Back_Matter/01_Dramatis_Personae.md" ] || { echo "  FAIL missing 01_Dramatis_Personae.md"; exit 1; }
[ -f "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" ] || { echo "  FAIL missing 02_Glossary_and_Concordance.md"; exit 1; }
grep -q "Aethelgard" "${MS_PATH}/Book-01/04_Back_Matter/01_Dramatis_Personae.md" || { echo "  FAIL Aethelgard missing from Dramatis Personae"; exit 1; }
grep -q "Solar Hegemony" "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Solar Hegemony missing from Glossary"; exit 1; }
grep -q "Solar Scepter" "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Solar Scepter missing from Glossary"; exit 1; }
grep -q "Void Stalker" "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Void Stalker missing from Glossary"; exit 1; }
grep -q "Aethel" "${MS_PATH}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Aethel lexicon term missing from Glossary"; exit 1; }
echo "  OK generate_concordance (Dramatis Personae + Glossary back-matter)"

# 6h. Wordcount & Progress Analytics
bash scripts/wordcount_report.sh "${MS_PATH}" --markdown > "${TMP_VERIFY}/wc.md"
[ -s "${TMP_VERIFY}/wc.md" ] || { echo "  FAIL wordcount report empty"; exit 1; }
bash scripts/wordcount_report.sh "${MS_PATH}" --json > "${TMP_VERIFY}/wc.json"
python3 -c "import json; d = json.load(open('${TMP_VERIFY}/wc.json')); assert d['total_words'] >= 0; assert d['chapter_count'] >= 1"
echo "  OK wordcount_report (markdown + json)"

# 6i. Save Snapshot (Git Versioning across Lore & Manuscript with positional syntax)
bash scripts/save_snapshot.sh "${WORLD}" --note "verify.sh world snapshot test" > "${TMP_VERIFY}/snap_world.log" 2>&1 \
    || { echo "  FAIL save_snapshot world:"; tail -n 5 "${TMP_VERIFY}/snap_world.log"; exit 1; }
git -C "${WORLD_PATH}" log --oneline | grep -q "verify.sh world snapshot test" \
    || { echo "  FAIL snapshot note not committed to world"; exit 1; }

bash scripts/save_snapshot.sh "${MANUSCRIPT}" --note "verify.sh manuscript snapshot test" > "${TMP_VERIFY}/snap_ms.log" 2>&1 \
    || { echo "  FAIL save_snapshot manuscript:"; tail -n 5 "${TMP_VERIFY}/snap_ms.log"; exit 1; }
git -C "${MS_PATH}" log --oneline | grep -q "verify.sh manuscript snapshot test" \
    || { echo "  FAIL snapshot note not committed to manuscript"; exit 1; }
echo "  OK save_snapshot (multi-tier Git snapshots recorded)"

# 6j. Decoupled Backup & Verified Restore Drill
echo "  Running backup & restore verification drill..."
bash scripts/backup_world.sh --world "${WORLD}" --note "harness drill" > "${TMP_VERIFY}/backup_w.log" 2>&1 \
    || { echo "  FAIL backup_world:"; tail -n 5 "${TMP_VERIFY}/backup_w.log"; exit 1; }
BACKUP_ARCHIVE="$(find "${WORLD_PATH}/Backups" -name '*.tar.gz' -print -quit)"
[ -n "${BACKUP_ARCHIVE}" ] || { echo "  FAIL backup archive not created"; exit 1; }
[ -f "${BACKUP_ARCHIVE%.tar.gz}.sha256" ] || { echo "  FAIL backup sha256 missing"; exit 1; }

bash scripts/backup_world.sh --manuscript "${MANUSCRIPT}" --note "ms drill" > "${TMP_VERIFY}/backup_m.log" 2>&1 \
    || { echo "  FAIL backup manuscript:"; tail -n 5 "${TMP_VERIFY}/backup_m.log"; exit 1; }
MS_BACKUP_ARCHIVE="$(find "${MS_PATH}/Backups" -name '*.tar.gz' -print -quit)"
[ -n "${MS_BACKUP_ARCHIVE}" ] || { echo "  FAIL ms backup archive not created"; exit 1; }
[ -f "${MS_BACKUP_ARCHIVE%.tar.gz}.sha256" ] || { echo "  FAIL ms backup sha256 missing"; exit 1; }
echo "  OK backup_world (world & manuscript archives + sha256 created)"

# Restore drill
RESTORE_TARGET="RestoredWorld"
bash scripts/restore_world.sh --archive "${BACKUP_ARCHIVE}" --target "${RESTORE_TARGET}" --universe "${UNIVERSE}" > "${TMP_VERIFY}/restore.log" 2>&1 \
    || { echo "  FAIL restore_world:"; tail -n 5 "${TMP_VERIFY}/restore.log"; exit 1; }
RESTORED_PATH="${HOME}/Universes/${UNIVERSE}/${RESTORE_TARGET}"
[ -d "${RESTORED_PATH}/Characters" ] || { echo "  FAIL restored world bible missing"; exit 1; }
[ -f "${RESTORED_PATH}/Characters/Aethelgard.md" ] || { echo "  FAIL restored character missing"; exit 1; }
echo "  OK restore_world (drill verified: archive -> restore -> verify content)"

# 6k. Unified Scriptorium Doctor
set +e
bash scripts/scriptorium_doctor.sh --world "${RESTORE_TARGET}" --manuscript "${MANUSCRIPT}" > "${TMP_VERIFY}/doc.log" 2>&1
DOC_RC=$?
set -e
[ "${DOC_RC}" -eq 0 ] || [ "${DOC_RC}" -eq 1 ] || { echo "  FAIL scriptorium_doctor failed with exit code ${DOC_RC}:"; cat "${TMP_VERIFY}/doc.log"; exit 1; }
[ -s "${TMP_VERIFY}/doc.log" ] || { echo "  FAIL scriptorium_doctor produced no output"; exit 1; }
echo "  OK scriptorium_doctor diagnostics (exit ${DOC_RC})"

# 6l. Performance Cache & Continuity Engine Regression Tests
bash tests/test_performance_cache.sh > "${TMP_VERIFY}/cache_test.log" 2>&1 \
    || { echo "  FAIL test_performance_cache.sh:"; tail -n 5 "${TMP_VERIFY}/cache_test.log"; exit 1; }
echo "  OK performance cache & mtime invalidation tests"

bash tests/test_continuity_engine.sh > "${TMP_VERIFY}/continuity_test.log" 2>&1 \
    || { echo "  FAIL test_continuity_engine.sh:"; tail -n 5 "${TMP_VERIFY}/continuity_test.log"; exit 1; }
echo "  OK narrative continuity & trait contradiction tests"

# 6m. Dry-run simulation tests
bash scripts/setup_scriptorium.sh --dry-run --force > "${TMP_VERIFY}/setup_dryrun.log" 2>&1 \
    || { echo "  FAIL setup_scriptorium --dry-run:"; tail -n 5 "${TMP_VERIFY}/setup_dryrun.log"; exit 1; }
bash scripts/uninstall_scriptorium.sh --dry-run --force > "${TMP_VERIFY}/uninstall_dryrun.log" 2>&1 \
    || { echo "  FAIL uninstall_scriptorium --dry-run:"; tail -n 5 "${TMP_VERIFY}/uninstall_dryrun.log"; exit 1; }
echo "  OK setup & uninstall --dry-run simulations"

echo "[7/7] Scriptorium CLI facade tests..."
bash scripts/scriptorium --version >/dev/null
bash scripts/scriptorium --help >/dev/null
bash scripts/scriptorium universe --list >/dev/null
bash scripts/scriptorium world --list >/dev/null
bash scripts/scriptorium manuscript --list >/dev/null
bash scripts/scriptorium add-volume --help >/dev/null
bash scripts/scriptorium concordance --help >/dev/null
bash scripts/scriptorium export --help >/dev/null
bash scripts/scriptorium snapshot --help >/dev/null
bash scripts/scriptorium backup --help >/dev/null
bash scripts/scriptorium restore --help >/dev/null
bash scripts/scriptorium report --help >/dev/null
bash scripts/scriptorium doctor --help >/dev/null
bash scripts/scriptorium world-doctor --help >/dev/null
bash scripts/scriptorium check-continuity --help >/dev/null
echo "  OK scriptorium CLI entrypoints and subcommands"

echo "ALL-CHECKS-PASS"
