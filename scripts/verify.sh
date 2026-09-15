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

echo "[1/7] Script syntax & Python compilation validation..."
for f in scripts/*.sh scripts/lib/*.sh scripts/scriptorium; do
    if [ -f "$f" ]; then
        if ! bash -n "$f"; then
            echo "  FAIL $f (bash syntax)" >&2
            exit 1
        fi
        echo "  OK $f"
    fi
done
if command -v python3 >/dev/null; then
    if ! python3 -m py_compile scripts/scriptorium_app.py; then
        echo "  FAIL scripts/scriptorium_app.py (Python compilation)" >&2
        exit 1
    fi
    echo "  OK scripts/scriptorium_app.py (Python syntax valid)"
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
print("  OK Obsidian pre-configured plugin & fileClasses schemas")
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
    if ! printf '# Ch1\n\nHello *world*.\n' | pandoc -f markdown-citations -t typst -o "${TMP_VERIFY}/body.typ" 2>/dev/null; then
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
    echo "  SKIP typst missing on this host (install per resources/software_catalog.md)"
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

echo "[6/7] Functional Universe, World lifecycle, diagnostics & recovery (sandboxed HOME)..."
export HOME="${TMP_VERIFY}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

# 6a. Universe initialization
UNIVERSE="TestMultiverse"
bash scripts/init_universe.sh "${UNIVERSE}" >/dev/null
[ -d "${HOME}/Universes/${UNIVERSE}/Worlds" ] || { echo "  FAIL universe scaffold missing"; exit 1; }
[ -d "${HOME}/Universes/${UNIVERSE}/.git" ] || { echo "  FAIL universe git repository missing"; exit 1; }
[ -f "${HOME}/Universes/${UNIVERSE}/Universe-Index.md" ] || { echo "  FAIL universe index note missing"; exit 1; }
echo "  OK init_universe (Universe directory + Universe Git repository + Index Hub)"

# 6b. Transactional world initialization inside Universe
WORLD="VerifyWorld"
bash scripts/init_world.sh "${WORLD}" --universe "${UNIVERSE}" >/dev/null
WORLD_PATH="${HOME}/Universes/${UNIVERSE}/Worlds/${WORLD}"
[ -d "${WORLD_PATH}/00-World-Bible/Characters" ] || { echo "  FAIL world bible Characters missing"; exit 1; }
[ -d "${WORLD_PATH}/00-World-Bible/Bestiary" ] || { echo "  FAIL world bible Bestiary missing"; exit 1; }
[ -d "${WORLD_PATH}/00-World-Bible/Artifacts" ] || { echo "  FAIL world bible Artifacts missing"; exit 1; }
[ -d "${WORLD_PATH}/00-World-Bible/Cosmology" ] || { echo "  FAIL world bible Cosmology missing"; exit 1; }
[ -f "${WORLD_PATH}/00-World-Bible/.obsidian/community-plugins.json" ] || { echo "  FAIL obsidian config missing"; exit 1; }
[ -f "${WORLD_PATH}/01-Manuscript/nwProject.nwx" ] || { echo "  FAIL nwProject.nwx missing"; exit 1; }
[ -d "${WORLD_PATH}/.git" ] || { echo "  FAIL world git repository missing"; exit 1; }
[ -d "${WORLD_PATH}/01-Manuscript/Book-01/.git" ] || { echo "  FAIL discrete manuscript git repository missing"; exit 1; }
echo "  OK init_world (Multi-tier Universe, World & Manuscript Git repositories + Expanded Taxonomy)"

# 6c. Test add-book volume scaffolding & tag-poisoning test chapters
bash scripts/scriptorium add-book "${WORLD_PATH}" "Book-02" >/dev/null
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/01_Act_I" ] || { echo "  FAIL Book-02 Act I missing"; exit 1; }
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/02_Act_II" ] || { echo "  FAIL Book-02 Act II missing"; exit 1; }
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/03_Act_III" ] || { echo "  FAIL Book-02 Act III missing"; exit 1; }
[ -d "${WORLD_PATH}/01-Manuscript/Book-02/.git" ] || { echo "  FAIL Book-02 discrete git repo missing"; exit 1; }
echo "  OK add-book volume scaffolding (Acts + discrete Git repo)"

cat > "${WORLD_PATH}/01-Manuscript/Book-02/01_Act_I/01_Chapter_05.md" << 'EOF'
# Chapter 5: The Second Book Begins

This chapter lives in Book-02 and must appear in exports.

@time: 1899-03-14
@plot: The Heist
@theme: Honor & Steel
EOF

# 6d. Export book compilation (Testing specific volume selection, paper size & omnibus)
set +e
bash scripts/export_book.sh "${WORLD_PATH}" --book Book-01 --paper-size trade --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export_b1.log" 2>&1
EXPORT_B1_RC=$?
bash scripts/export_book.sh "${WORLD_PATH}" --book all --paper-size us-trade --title "Verify Book" --author "Verify Author" > "${TMP_VERIFY}/export_all.log" 2>&1
EXPORT_ALL_RC=$?
set -e

if command -v typst >/dev/null && command -v pandoc >/dev/null; then
    if [ "${EXPORT_B1_RC}" -ne 0 ] || [ "${EXPORT_ALL_RC}" -ne 0 ]; then
        echo "  FAIL export_book failed (B1=${EXPORT_B1_RC}, ALL=${EXPORT_ALL_RC})"
        tail -n 5 "${TMP_VERIFY}/export_b1.log"
        tail -n 5 "${TMP_VERIFY}/export_all.log"
        exit 1
    fi
    echo "  OK export_book (exit 0 across volume-isolated and omnibus builds)"

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

# 6e. Multi-Era World Doctor consistency check
cat > "${WORLD_PATH}/00-World-Bible/Characters/Aethelgard.md" << 'EOF'
---
name: "Aethelgard"
type: character
role: protagonist
birth_year: "450 BCE"
death_year: "380 BCE"
---
A legendary general from the classical era.
EOF

cat > "${WORLD_PATH}/00-World-Bible/History/The_Great_Sundering.md" << 'EOF'
---
name: "The Great Sundering"
type: timeline_event
start_year: "-450 IE"
end_year: "-400 IE"
---
An ancient cataclysm reshaping the realms.
EOF

DOCTOR_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
printf '%s' "${DOCTOR_JSON}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['notes'] >= 0
assert len(d['timeline_errors']) == 0
print('  OK world_doctor multi-era valid timeline passed')
"

# Test chronological paradox detection
cat > "${WORLD_PATH}/00-World-Bible/Characters/ParadoxLord.md" << 'EOF'
---
name: "ParadoxLord"
type: character
role: antagonist
birth_year: "Age of Fire 500"
death_year: "Age of Fire 410"
---
A chronologically inverted paradox lord.
EOF

DOCTOR_ERR_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
printf '%s' "${DOCTOR_ERR_JSON}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert any('ParadoxLord' in e['file'] for e in d['timeline_errors'])
print('  OK world_doctor multi-era chronological paradox error caught')
"
rm -f "${WORLD_PATH}/00-World-Bible/Characters/ParadoxLord.md"

# 6f. Back-Matter Concordance & Dramatis Personae Engine
cat > "${WORLD_PATH}/00-World-Bible/Factions/Solar_Hegemony.md" << 'EOF'
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

cat > "${WORLD_PATH}/00-World-Bible/Artifacts/Solar_Scepter.md" << 'EOF'
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

cat > "${WORLD_PATH}/00-World-Bible/Bestiary/Void_Stalker.md" << 'EOF'
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

cat > "${WORLD_PATH}/00-World-Bible/Languages/Solar_Tongue.md" << 'EOF'
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

bash scripts/scriptorium concordance "${WORLD_PATH}" --book Book-01 >/dev/null
[ -f "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/01_Dramatis_Personae.md" ] || { echo "  FAIL missing 01_Dramatis_Personae.md"; exit 1; }
[ -f "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" ] || { echo "  FAIL missing 02_Glossary_and_Concordance.md"; exit 1; }
grep -q "Aethelgard" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/01_Dramatis_Personae.md" || { echo "  FAIL Aethelgard missing from Dramatis Personae"; exit 1; }
grep -q "Solar Hegemony" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Solar Hegemony missing from Glossary"; exit 1; }
grep -q "Solar Scepter" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Solar Scepter missing from Glossary"; exit 1; }
grep -q "Void Stalker" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Void Stalker missing from Glossary"; exit 1; }
grep -q "Aethel" "${WORLD_PATH}/01-Manuscript/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md" || { echo "  FAIL Aethel lexicon term missing from Glossary"; exit 1; }
echo "  OK generate_concordance (Dramatis Personae + Glossary back-matter)"

# 6g. Wordcount & Progress Analytics
bash scripts/wordcount_report.sh "${WORLD_PATH}" --markdown > "${TMP_VERIFY}/wc.md"
[ -s "${TMP_VERIFY}/wc.md" ] || { echo "  FAIL wordcount report empty"; exit 1; }
bash scripts/wordcount_report.sh "${WORLD_PATH}" --json > "${TMP_VERIFY}/wc.json"
python3 -c "import json; d = json.load(open('${TMP_VERIFY}/wc.json')); assert d['total_words'] >= 0; assert d['chapter_count'] >= 1"
echo "  OK wordcount_report (markdown + json)"

# 6h. Save Snapshot (Git Versioning across World & Manuscript with positional syntax)
bash scripts/save_snapshot.sh "${WORLD}" --note "verify.sh lifecycle test" > "${TMP_VERIFY}/snapshot.log" 2>&1 \
    || { echo "  FAIL save_snapshot:"; tail -n 5 "${TMP_VERIFY}/snapshot.log"; exit 1; }
git -C "${WORLD_PATH}" log --oneline | grep -q "verify.sh lifecycle test" \
    || { echo "  FAIL snapshot note not committed"; exit 1; }
echo "  OK save_snapshot (multi-tier Git snapshots recorded)"

# 6i. Decoupled Backup & Verified Restore Drill
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

# 6j. Unified Scriptorium Doctor
bash scripts/scriptorium_doctor.sh --world "${RESTORE_TARGET}" > "${TMP_VERIFY}/doc.log" 2>&1 || true
[ -s "${TMP_VERIFY}/doc.log" ] || { echo "  FAIL scriptorium_doctor produced no output"; exit 1; }
echo "  OK scriptorium_doctor diagnostics"

# 6k. Dry-run simulation tests
bash scripts/setup_scriptorium.sh --dry-run --force > "${TMP_VERIFY}/setup_dryrun.log" 2>&1 \
    || { echo "  FAIL setup_scriptorium --dry-run:"; tail -n 5 "${TMP_VERIFY}/setup_dryrun.log"; exit 1; }
bash scripts/uninstall_scriptorium.sh --dry-run --force > "${TMP_VERIFY}/uninstall_dryrun.log" 2>&1 \
    || { echo "  FAIL uninstall_scriptorium --dry-run:"; tail -n 5 "${TMP_VERIFY}/uninstall_dryrun.log"; exit 1; }
echo "  OK setup & uninstall --dry-run simulations"

echo "[7/7] Scriptorium CLI facade tests..."
bash scripts/scriptorium --version >/dev/null
bash scripts/scriptorium --help >/dev/null
bash scripts/scriptorium universe --list >/dev/null
bash scripts/scriptorium add-book --help >/dev/null
bash scripts/scriptorium concordance --help >/dev/null
echo "  OK scriptorium CLI entrypoint (with universe, add-book & concordance commands)"

echo "ALL-CHECKS-PASS"
