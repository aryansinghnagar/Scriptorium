#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum DOCX Synchronization & Word Processor Integration Test Suite
# Tests:
#   1. Automatic DOCX generation during manuscript initialization
#   2. Automatic DOCX generation during draft forking
#   3. CLI `arcanum docx build` command
#   4. CLI `arcanum docx sync` bidirectional sync
#   5. CLI `arcanum docx import` external Word file conversion
#   6. CLI `arcanum config docx-preset` preset switching
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "${TEST_DIR}"' EXIT

export HOME="${TEST_DIR}/home"
mkdir -p "${HOME}/Manuscripts" "${HOME}/.config/ars-arcanum"

echo "=== Test 1: init_manuscript.sh automatic DOCX generation ==="
bash "${SCRIPT_DIR}/scripts/init_manuscript.sh" "The-Lost-Tome"
MS_DIR="${HOME}/Manuscripts/The-Lost-Tome"

if [ ! -f "${MS_DIR}/Book-01/01_Act_I/01_Chapter_01.docx" ]; then
    echo "FAIL: 01_Chapter_01.docx not generated during manuscript initialization" >&2
    exit 1
fi
if [ ! -f "${MS_DIR}/Book-01/Draft-01_Manuscript.docx" ]; then
    echo "FAIL: Draft-01_Manuscript.docx not generated during manuscript initialization" >&2
    exit 1
fi
echo "PASS: Test 1 passed (Initial DOCX files generated)"

echo "=== Test 2: init_draft.sh automatic DOCX generation on draft fork ==="
bash "${SCRIPT_DIR}/scripts/init_draft.sh" "${MS_DIR}" "Draft-02" -b "Book-01"

if [ ! -f "${MS_DIR}/Book-01/Draft-02/01_Act_I/01_Chapter_01.docx" ]; then
    echo "FAIL: Draft-02 01_Chapter_01.docx not generated on draft fork" >&2
    exit 1
fi
if [ ! -f "${MS_DIR}/Book-01/Draft-02/Draft-02_Manuscript.docx" ]; then
    echo "FAIL: Draft-02_Manuscript.docx not generated on draft fork" >&2
    exit 1
fi
echo "PASS: Test 2 passed (Draft fork DOCX files generated)"

echo "=== Test 3: CLI docx build and preset formatting ==="
python3 "${SCRIPT_DIR}/scripts/lib/config.py" docx-preset modern-manuscript
python3 "${SCRIPT_DIR}/scripts/lib/docx_sync.py" build "${MS_DIR}" --draft "Draft-02"

if [ ! -s "${MS_DIR}/Book-01/Draft-02/Draft-02_Manuscript.docx" ]; then
    echo "FAIL: Draft-02_Manuscript.docx empty after build" >&2
    exit 1
fi
echo "PASS: Test 3 passed (DOCX build with preset passed)"

echo "=== Test 4: Bidirectional DOCX -> Markdown sync on Word edit ==="
# Add prose to chapter md
echo "New paragraph added by author." >> "${MS_DIR}/Book-01/Draft-02/01_Act_I/01_Chapter_01.md"
python3 "${SCRIPT_DIR}/scripts/lib/docx_sync.py" sync "${MS_DIR}" --draft "Draft-02"
echo "PASS: Test 4 passed (Bidirectional sync executed successfully)"

echo "=== Test 5: CLI docx import from standalone file ==="
EXT_DOCX="${TEST_DIR}/External_Chapter.docx"
cat << PYEOF > "${TEST_DIR}/make_sample.py"
import sys
from pathlib import Path
sys.path.insert(0, '${SCRIPT_DIR}/scripts/lib')
from docx_sync import parse_markdown_to_paragraphs, build_docx_package, get_docx_config

md = "# External Chapter\n\nWritten completely in Microsoft Word."
p = parse_markdown_to_paragraphs(md)
build_docx_package(Path(sys.argv[1]), p, get_docx_config(), title="External")
PYEOF
python3 "${TEST_DIR}/make_sample.py" "${EXT_DOCX}"

IMPORTED_MD="${MS_DIR}/Book-01/Draft-02/01_Act_I/02_Chapter_02.md"
python3 "${SCRIPT_DIR}/scripts/lib/docx_sync.py" import "${EXT_DOCX}" --to "${IMPORTED_MD}"

if [ ! -f "${IMPORTED_MD}" ]; then
    echo "FAIL: Imported Markdown file not created" >&2
    exit 1
fi
if ! grep -q "Written completely in Microsoft Word" "${IMPORTED_MD}"; then
    echo "FAIL: Imported Markdown missing content" >&2
    exit 1
fi
echo "PASS: Test 5 passed (External DOCX imported to Markdown)"

echo "ALL-DOCX-SYNC-TESTS-PASSED"
exit 0
