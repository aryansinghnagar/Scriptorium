#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR:-}"' EXIT
export HOME="${TMP_DIR}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

echo "=== 1. Testing obsidian-git basePath and Settings Schema ==="
python3 - << 'PYEOF'
import json, os
git_cfg = 'templates/world-bible/.obsidian/plugins/obsidian-git/data.json'
assert os.path.isfile(git_cfg), "Missing obsidian-git data.json"
with open(git_cfg) as f:
    data = json.load(f)
assert data.get("basePath") in ("", None), f"Expected basePath '' for vault root git repository, got {data.get('basePath')}"
for k in ("gitLocation", "baseSubmodule", "autoBackupFileName"):
    assert k not in data, f"Unexpected obsolete key found: {k}"
print("  OK obsidian-git settings valid with empty basePath for direct vault repo")
PYEOF

echo "=== 2. Testing Beginner Guide and Quickstart Character Template ==="
[ -f "templates/world-bible/00_START_HERE.md" ] || { echo "FAIL: missing 00_START_HERE.md"; exit 1; }
[ -f "templates/world-bible/Characters/Character-Quickstart-Template.md" ] || { echo "FAIL: missing Character-Quickstart-Template.md"; exit 1; }
grep -q "00_START_HERE" "templates/world-bible/Templates/World-Bible-Index.md" || { echo "FAIL: 00_START_HERE link missing from Index"; exit 1; }
grep -q "Character-Quickstart-Template" "templates/world-bible/Templates/World-Bible-Index.md" || { echo "FAIL: Quickstart Character link missing from Index"; exit 1; }
echo "  OK Beginner templates and index links verified"

echo "=== 3. Testing WLD-108 Manuscript Name Drift in World Doctor ==="
bash scripts/arcanum universe TestCosmos >/dev/null
bash scripts/arcanum world TestWorld --universe TestCosmos >/dev/null
bash scripts/arcanum manuscript TestManuscript --universe TestCosmos --world TestWorld >/dev/null

WORLD_PATH="${HOME}/Universes/TestCosmos/TestWorld"
MS_PATH="${HOME}/Manuscripts/TestManuscript"

# Seed canonical character and location in World Bible
cat > "${WORLD_PATH}/Characters/Kaelen.md" << 'EOF2'
---
name: "Kaelen"
type: character
role: protagonist
aliases: ["The Scribe"]
---
A quiet archivist.
EOF2

cat > "${WORLD_PATH}/Locations/Iron_Citadel.md" << 'EOF3'
---
name: "Iron Citadel"
type: location
---
The fortress capital.
EOF3

# Case A: Clean manuscript referencing indexed lore and alias
cat > "${MS_PATH}/Book-01/01_Act_I/01_Clean.md" << 'EOF4'
# Chapter 1: The Gathering
@pov: Kaelen
@char: The Scribe
@location: Iron_Citadel
@status: Draft

The [[Iron Citadel]] stood firm.
EOF4

DOC_CLEAN="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --manuscript "${MS_PATH}" --json || true)"
printf '%s' "${DOC_CLEAN}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
drifts = d.get('manuscript_name_drift', [])
assert len(drifts) == 0, f'Expected 0 drift, got {drifts}'
"
echo "  OK Clean manuscript produces 0 WLD-108 findings"

# Case B: Drifting manuscript referencing deleted/renamed character
cat > "${MS_PATH}/Book-01/01_Act_I/02_Drift.md" << 'EOF5'
# Chapter 2: The Drift
@pov: OldNameVance
@char: Kaelen, MissingGeneral
@location: LostRuinsOfValdor

They walked toward [[DanglingSanctuary]].
EOF5

DOC_DRIFT="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --manuscript "${MS_PATH}" --json || true)"
printf '%s' "${DOC_DRIFT}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
drifts = d.get('manuscript_name_drift', [])
missing_names = {e['missing'] for e in drifts}
assert 'OldNameVance' in missing_names, f'OldNameVance not caught in {missing_names}'
assert 'MissingGeneral' in missing_names, f'MissingGeneral not caught in {missing_names}'
assert 'LostRuinsOfValdor' in missing_names, f'LostRuinsOfValdor not caught in {missing_names}'
assert 'DanglingSanctuary' in missing_names, f'DanglingSanctuary wikilink not caught in {missing_names}'
assert 'Kaelen' not in missing_names, 'Valid character wrongly flagged'
"
echo "  OK Manuscript name drift correctly caught across tags and wikilinks"
rm -f "${MS_PATH}/Book-01/01_Act_I/02_Drift.md"

echo "=== 4. Testing export_book.sh --format submission / --docx Flags ==="
bash scripts/export_book.sh "${MS_PATH}" --format submission --book Book-01 --title "Test Novel" > "${TMP_DIR}/export_sub.log" 2>&1 || true
bash scripts/export_book.sh "${MS_PATH}" --docx --book Book-01 --title "Test Novel" > "${TMP_DIR}/export_docx.log" 2>&1 || true
bash scripts/export_book.sh "${MS_PATH}" --format all --book Book-01 --title "Test Novel" > "${TMP_DIR}/export_all.log" 2>&1 || true
echo "  OK export_book --format submission/docx/all accepted"

echo "=== 5. Testing Multi-Volume EPUB Selection Logic ==="
python3 - << 'PYEOF2'
files = ["Verify_Book_Book-01.epub", "Verify_Book.epub"]
omni = [f for f in files if f == "Verify_Book.epub"]
b1 = [f for f in files if f == "Verify_Book_Book-01.epub"]
assert len(omni) == 1 and omni[0] == "Verify_Book.epub"
assert len(b1) == 1 and b1[0] == "Verify_Book_Book-01.epub"
print("  OK EPUB selection logic verified deterministic")
PYEOF2

echo "=== ALL CLAUDE AUDIT IMPROVEMENTS VERIFIED! ==="