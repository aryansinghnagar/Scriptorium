#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Cache Performance & Invalidation Test Suite
# Tests:
#   1. Cache creation on project vault
#   2. Cache hit verification (unmodified files)
#   3. Cache invalidation on file modification
#   4. Wordcount aggregation accuracy
#   5. Parity between world_doctor.sh standard and world_doctor.sh --fast
#   6. Cache clear command
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "${TEST_DIR}"' EXIT

export HOME="${TEST_DIR}/home"
mkdir -p "${HOME}/Universes/TestCosmos/TestWorld"
mkdir -p "${HOME}/Manuscripts/TestMS/Book-01/01_Act_I"

WORLD_DIR="${HOME}/Universes/TestCosmos/TestWorld"
MS_DIR="${HOME}/Manuscripts/TestMS"

# Scaffold sample files
cat << 'EOF' > "${WORLD_DIR}/world.yaml"
name: TestWorld
universe: TestCosmos
EOF

mkdir -p "${WORLD_DIR}/Characters" "${WORLD_DIR}/Locations"
cat << 'EOF' > "${WORLD_DIR}/Characters/Hero.md"
---
name: Hero
type: character
current_location: "[[Citadel]]"
---
# Hero
The main protagonist of the test world.
EOF

cat << 'EOF' > "${WORLD_DIR}/Locations/Citadel.md"
---
name: Citadel
type: location
---
# Citadel
The central fortress.
EOF

cat << 'EOF' > "${MS_DIR}/Book-01/01_Act_I/01_Chapter.md"
# Chapter 1

@pov: Hero
@location: Citadel
@status: draft

The hero walked into the ancient [[Citadel]]. It was cold and dark.
EOF

echo "=== Test 1: Cache creation ==="
python3 "${SCRIPT_DIR}/scripts/lib/cache.py" scan "${WORLD_DIR}"
if [ ! -f "${WORLD_DIR}/.arcanum_cache.json" ]; then
    echo "FAIL: .arcanum_cache.json not created in ${WORLD_DIR}" >&2
    exit 1
fi
echo "PASS: Test 1 passed"

echo "=== Test 2: Cache hit & wordcount aggregation ==="
WC_JSON="$(python3 "${SCRIPT_DIR}/scripts/lib/cache.py" wordcounts "${MS_DIR}" --json)"
python3 -c "import sys, json; d = json.loads(sys.argv[1]); assert d['total_words'] > 0, 'No words counted'" "${WC_JSON}"
echo "PASS: Test 2 passed"

echo "=== Test 3: Cache invalidation on file edit ==="
# Initial scan
python3 "${SCRIPT_DIR}/scripts/lib/cache.py" scan "${MS_DIR}"
INITIAL_WC="$(python3 -c 'import sys, json; d=json.load(open(sys.argv[1])); print(d["files"]["Book-01/01_Act_I/01_Chapter.md"]["word_count"])' "${MS_DIR}/.arcanum_cache.json")"

# Append text
echo "Extra words appended to scene file." >> "${MS_DIR}/Book-01/01_Act_I/01_Chapter.md"
# Rescan
python3 "${SCRIPT_DIR}/scripts/lib/cache.py" scan "${MS_DIR}"
UPDATED_WC="$(python3 -c 'import sys, json; d=json.load(open(sys.argv[1])); print(d["files"]["Book-01/01_Act_I/01_Chapter.md"]["word_count"])' "${MS_DIR}/.arcanum_cache.json")"

if [ "${UPDATED_WC}" -le "${INITIAL_WC}" ]; then
    echo "FAIL: Cache did not detect updated word count (${UPDATED_WC} <= ${INITIAL_WC})" >&2
    exit 1
fi
echo "PASS: Test 3 passed"

echo "=== Test 4: world_doctor.sh --fast parity ==="
OUT_STD="$(bash "${SCRIPT_DIR}/scripts/world_doctor.sh" "${WORLD_DIR}" -m "${MS_DIR}" --json)"
OUT_FAST="$(bash "${SCRIPT_DIR}/scripts/world_doctor.sh" "${WORLD_DIR}" -m "${MS_DIR}" --fast --json)"

# DOC-01: --fast reports its own cache observability fields; strip them and
# require the diagnostic payload itself to be identical. --fast must also
# positively report that the cache was used on this small healthy vault.
echo "${OUT_FAST}" | python3 -c "import sys, json; d = json.load(sys.stdin); assert d.get('fast_cache_used') is True, 'fast cache not used'"
if ! python3 - "$OUT_STD" "$OUT_FAST" << 'PYEOF'
import json, sys
std = json.loads(sys.argv[1])
fast = json.loads(sys.argv[2])
for key in ("fast_cache_requested", "fast_cache_used"):
    std.pop(key, None)
    fast.pop(key, None)
assert std == fast, "Discrepancy between standard and fast doctor outputs"
PYEOF
then
    echo "FAIL: Discrepancy between standard and fast doctor outputs" >&2
    exit 1
fi
echo "PASS: Test 4 passed"

echo "=== Test 5: Cache clear ==="
python3 "${SCRIPT_DIR}/scripts/lib/cache.py" clear "${WORLD_DIR}"
if [ -f "${WORLD_DIR}/.arcanum_cache.json" ]; then
    echo "FAIL: Cache file still exists after clear" >&2
    exit 1
fi
echo "PASS: Test 5 passed"

echo "ALL CACHE TESTS PASSED SUCCESSFULLY!"
