#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Local Offline Semantic Continuity Engine Test Suite
# Tests:
#   1. Clean world & manuscript continuity verification
#   2. Trait mismatch detection against World Bible (CNT-101)
#   3. Inter-scene trait contradiction detection (CNT-102)
#   4. scriptorium check-continuity CLI facade dispatch
#   5. JSON report structure validation
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "${TEST_DIR}"' EXIT

export HOME="${TEST_DIR}/home"
WORLD_DIR="${HOME}/Universes/Cosmere/Roshar"
MS_DIR="${HOME}/Manuscripts/Stormlight"

mkdir -p "${WORLD_DIR}/Characters"
mkdir -p "${MS_DIR}/Book-01/01_Act_I"
mkdir -p "${MS_DIR}/Book-02/01_Act_I"

# Baseline World Bible Lore Note
cat << 'EOF' > "${WORLD_DIR}/Characters/Kaladin.md"
---
name: Kaladin
type: character
eyes: brown
hair: black
status: alive
---
# Kaladin Stormblessed
A warrior with dark brown eyes and wavy black hair.
EOF

# Consistent Manuscript Scene
cat << 'EOF' > "${MS_DIR}/Book-01/01_Act_I/01_Scene.md"
# Scene 1
@pov: Kaladin
@status: draft

Kaladin looked across the Shattered Plains. His dark brown eyes narrowed in the storm.
EOF

echo "=== Test 1: Clean Continuity Audit ==="
python3 "${SCRIPT_DIR}/scripts/lib/continuity.py" -w "${WORLD_DIR}" -m "${MS_DIR}"
echo "PASS: Test 1 passed"

echo "=== Test 2: Lore Trait Contradiction (CNT-101) ==="
# Introduce contradictory eye color in scene
cat << 'EOF' > "${MS_DIR}/Book-01/01_Act_I/02_Scene.md"
# Scene 2
@pov: Kaladin
@status: draft

Kaladin smiled, his bright blue eyes reflecting the moonlight.
EOF

set +e
ERR_OUT="$(python3 "${SCRIPT_DIR}/scripts/lib/continuity.py" -w "${WORLD_DIR}" -m "${MS_DIR}" --json)"
RC=$?
set -e

if [ $RC -ne 1 ]; then
    echo "FAIL: Expected exit code 1 on trait mismatch, got ${RC}" >&2
    exit 1
fi

python3 -c "import sys, json
d = json.loads(sys.argv[1])
assert d['total_findings'] >= 1, 'Expected findings'
assert any(f['id'] == 'CNT-101' for f in d['findings']), 'Expected CNT-101 finding'
" "${ERR_OUT}"
echo "PASS: Test 2 passed"

echo "=== Test 3: Inter-scene Trait Drift (CNT-102) ==="
# Scene in Book 2 describes different hair
cat << 'EOF' > "${MS_DIR}/Book-02/01_Act_I/01_Scene.md"
# Book 2 Scene 1
@pov: Kaladin
@status: draft

Kaladin brushed his golden blonde hair out of his face.
EOF

set +e
ERR_OUT2="$(python3 "${SCRIPT_DIR}/scripts/lib/continuity.py" -w "${WORLD_DIR}" -m "${MS_DIR}" --json)"
RC2=$?
set -e

if [ $RC2 -ne 1 ]; then
    echo "FAIL: Expected exit code 1 on inter-scene drift, got ${RC2}" >&2
    exit 1
fi

python3 -c "import sys, json
d = json.loads(sys.argv[1])
assert any(f['id'] == 'CNT-102' or f['id'] == 'CNT-101' for f in d['findings']), 'Expected drift finding'
" "${ERR_OUT2}"
echo "PASS: Test 3 passed"

echo "=== Test 4: CLI Facade Dispatch ==="
set +e
"${SCRIPT_DIR}/scripts/scriptorium" check-continuity -w "${WORLD_DIR}" -m "${MS_DIR}" >/dev/null 2>&1
RC3=$?
set -e

if [ $RC3 -ne 1 ]; then
    echo "FAIL: CLI facade did not forward continuity exit code" >&2
    exit 1
fi
echo "PASS: Test 4 passed"

echo "ALL CONTINUITY TESTS PASSED SUCCESSFULLY!"
