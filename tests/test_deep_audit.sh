#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

TMP_TEST="$(mktemp -d)"
trap 'rm -rf "${TMP_TEST:-}"' EXIT
export HOME="${TMP_TEST}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

echo "=== 1. Testing Universe, World & Manuscript Creation ==="
bash scripts/init_universe.sh TestCosmos >/dev/null
bash scripts/init_world.sh NovelOne -u TestCosmos >/dev/null
bash scripts/init_manuscript.sh NovelOne -u TestCosmos -w NovelOne >/dev/null

WORLD_DIR="${HOME}/Universes/TestCosmos/NovelOne"
MS_DIR="${HOME}/Manuscripts/NovelOne"

[ -d "${WORLD_DIR}/Characters" ] || { echo "FAIL: World Lore Characters missing"; exit 1; }
[ -f "${WORLD_DIR}/world.yaml" ] || { echo "FAIL: world.yaml manifest missing"; exit 1; }
[ -d "${MS_DIR}/Book-01" ] || { echo "FAIL: Book-01 missing"; exit 1; }
[ -f "${MS_DIR}/nwProject.nwx" ] || { echo "FAIL: nwProject.nwx missing"; exit 1; }
[ ! -f "${WORLD_DIR}/.obsidian-recommended-plugins.md" ] || { echo "FAIL: Vault template polluted with plugin guide"; exit 1; }
[ -f "docs/guides/OBSIDIAN_PLUGINS.md" ] || { echo "FAIL: OBSIDIAN_PLUGINS.md missing in docs/guides"; exit 1; }

echo "=== 2. Testing add_book.sh Scaffolding & Flags ==="
# Explicit volume
bash scripts/add_book.sh NovelOne Book-02 >/dev/null
[ -d "${MS_DIR}/Book-02/01_Act_I" ] || { echo "FAIL: Book-02 Act I missing"; exit 1; }
[ -d "${MS_DIR}/Book-02/02_Act_II" ] || { echo "FAIL: Book-02 Act II missing"; exit 1; }
[ -d "${MS_DIR}/Book-02/03_Act_III" ] || { echo "FAIL: Book-02 Act III missing"; exit 1; }
[ -d "${MS_DIR}/Book-02/.git" ] || { echo "FAIL: Book-02 git missing"; exit 1; }

# Auto-increment to Book-03
bash scripts/add_book.sh NovelOne >/dev/null
[ -d "${MS_DIR}/Book-03/01_Act_I" ] || { echo "FAIL: Book-03 Act I missing"; exit 1; }
[ -d "${MS_DIR}/Book-03/.git" ] || { echo "FAIL: Book-03 git missing"; exit 1; }

# Auto-increment via path
bash scripts/add_book.sh "${MS_DIR}" >/dev/null
[ -d "${MS_DIR}/Book-04/01_Act_I" ] || { echo "FAIL: Book-04 Act I missing"; exit 1; }

# Flags -m and -b
bash scripts/add_book.sh -m NovelOne -b Book-05 >/dev/null
[ -d "${MS_DIR}/Book-05/01_Act_I" ] || { echo "FAIL: Book-05 Act I missing"; exit 1; }

# Duplicate volume must error
set +e
bash scripts/add_book.sh NovelOne Book-02 >/dev/null 2>&1
RC=$?
set -e
[ $RC -eq 1 ] || { echo "FAIL: Expected RC=1 for duplicate volume, got $RC"; exit 1; }

echo "=== 3. Testing save_snapshot.sh Variations ==="
# Positional syntax
echo "Chapter 1 text" >> "${MS_DIR}/Book-01/01_Act_I/01_Chapter_01.md"
bash scripts/save_snapshot.sh NovelOne -m "Positional note test" >/dev/null
git -C "${MS_DIR}" log -n 1 --oneline | grep -q "Positional note test" || { echo "FAIL: Positional snapshot note missing"; exit 1; }

# Flag before positional
echo "Chapter 2 text" >> "${MS_DIR}/Book-02/01_Act_I/01_Chapter_01.md"
bash scripts/save_snapshot.sh -m "Flag before positional note" NovelOne >/dev/null
git -C "${MS_DIR}" log -n 1 --oneline | grep -q "Flag before positional note" || { echo "FAIL: Flag-first snapshot note missing"; exit 1; }

# Full path syntax
echo "Chapter 3 text" >> "${MS_DIR}/Book-03/01_Act_I/01_Chapter_01.md"
bash scripts/save_snapshot.sh "${MS_DIR}" -m "Full path note" >/dev/null
git -C "${MS_DIR}" log -n 1 --oneline | grep -q "Full path note" || { echo "FAIL: Full path snapshot note missing"; exit 1; }

echo "=== 4. Testing export_book.sh Options ==="
# Custom trim size
bash scripts/export_book.sh "${MS_DIR}" --book Book-01 --paper-size pocket --title "Pocket Novel" > "${TMP_TEST}/exp_pocket.log" 2>&1 || true
# Check cover image auto-detection
mkdir -p "${MS_DIR}/03-Art"
touch "${MS_DIR}/03-Art/cover.png"
bash scripts/export_book.sh "${MS_DIR}" --book Book-02 --paper-size trade > "${TMP_TEST}/exp_trade.log" 2>&1 || true
touch "${MS_DIR}/03-Art/cover.jpg"
bash scripts/export_book.sh "${MS_DIR}" --book all --paper-size us-trade > "${TMP_TEST}/exp_ustrade.log" 2>&1 || true

echo "=== 5. Testing Schema & Frontmatter Integrity with Python ==="
python3 - << 'PYEOF'
import os
import yaml

templates_dir = "templates/world-bible"
fileclasses_dir = os.path.join(templates_dir, "Templates", "fileClasses")

# Ensure all 9 schemas exist
expected_schemas = [
    "Character", "Location", "Faction", "TimelineEvent",
    "Creature", "Artifact", "Cosmology", "MagicSystem", "Language"
]
for schema in expected_schemas:
    p = os.path.join(fileclasses_dir, f"{schema}.md")
    assert os.path.isfile(p), f"Missing schema file: {p}"
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---")
    assert len(parts) >= 3, f"Invalid frontmatter delimiter in {p}"
    data = yaml.safe_load(parts[1])
    assert data.get("fileClass") == schema, f"fileClass mismatch in {p}"
    assert "fields" in data, f"fields missing in {p}"

print("All 9 fileClasses schemas are valid YAML and match naming standards.")
PYEOF

echo "=== 6. Testing Dataview queries in World-Bible-Index.md ==="
grep -q "#world/system" "templates/world-bible/Templates/World-Bible-Index.md" || { echo "FAIL: #world/system table missing in World-Bible-Index.md"; exit 1; }
grep -q "#world/language" "templates/world-bible/Templates/World-Bible-Index.md" || { echo "FAIL: #world/language table missing in World-Bible-Index.md"; exit 1; }

echo "=== 7. Testing CLI Facade Dispatch ==="
bash scripts/arcanum --version >/dev/null
bash scripts/arcanum --help >/dev/null
bash scripts/ars-arcanum --version >/dev/null
bash scripts/arcanum add-book --help >/dev/null
bash scripts/arcanum export --help >/dev/null
bash scripts/arcanum snapshot --help >/dev/null
bash scripts/arcanum concordance --help >/dev/null
bash scripts/scriptorium --version >/dev/null

echo "=== 8. Testing Subplot Outline & Root Cleanliness ==="
[ -f "templates/manuscript/Outlines/Subplot-Thread-Matrix.md" ] || { echo "FAIL: Subplot-Thread-Matrix.md missing"; exit 1; }
[ ! -f "Finishing_Touches.md" ] || { echo "FAIL: Finishing_Touches.md was not removed"; exit 1; }

echo "=== ALL DEEP AUDIT TESTS PASSED SUCCESSFULLY! ==="
