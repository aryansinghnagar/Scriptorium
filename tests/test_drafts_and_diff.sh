#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Draft Management, Redline Comparator, & Secure Backup Integration Tests
# (tests/test_drafts_and_diff.sh)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "${TEST_DIR}"' EXIT

export HOME="${TEST_DIR}/home"
export XDG_CONFIG_HOME="${HOME}/.config"
mkdir -p "${HOME}/Manuscripts" "${HOME}/Universes" "${HOME}/SecureBackups"

MS_NAME="Chrono-Voyagers"
MS_DIR="${HOME}/Manuscripts/${MS_NAME}"
SECURE_DEST="${HOME}/SecureBackups"

echo "=== Stage 1: Scaffold Initial Manuscript Project ==="
bash "${SCRIPT_DIR}/scripts/init_manuscript.sh" "${MS_NAME}" --author "Test Author"
[ -d "${MS_DIR}/Book-01" ] || { echo "FAIL: Book-01 missing in ${MS_NAME}"; exit 1; }
[ -f "${MS_DIR}/manuscript.yaml" ] || { echo "FAIL: manuscript.yaml missing"; exit 1; }
echo "[✓] Initial manuscript project scaffolded."

echo "=== Stage 2: Initialize Discrete Drafts with init_draft.sh ==="
# Populate baseline chapter prose in Book-01
mkdir -p "${MS_DIR}/Book-01/01_Act_I"
cat << 'EOF' > "${MS_DIR}/Book-01/01_Act_I/01_Chapter_01.md"
# Chapter 1: The Departure

@pov: Kaelen
@location: Launch Pad
@status: Draft

The countdown began in the quiet hangar. Kaelen tightened his flight gloves and watched the storm clouds gathering over the horizon. Ten years of research came down to this single moment.
EOF

# Initialize Draft-02
bash "${SCRIPT_DIR}/scripts/init_draft.sh" "${MS_NAME}" "Draft-02" -b "Book-01"
[ -d "${MS_DIR}/Book-01/Draft-02/01_Act_I" ] || { echo "FAIL: Draft-02 act folder not created"; exit 1; }
[ -f "${MS_DIR}/Book-01/Draft-02/01_Act_I/01_Chapter_01.md" ] || { echo "FAIL: Draft-02 chapter not copied"; exit 1; }

# Verify manifest updated
grep -q 'active_draft: "Draft-02"' "${MS_DIR}/manuscript.yaml" || { echo "FAIL: manuscript.yaml active_draft not updated"; exit 1; }
echo "[✓] Draft-02 initialized and manifest updated."

# Modify Draft-02 prose (revise opening scene)
cat << 'EOF' > "${MS_DIR}/Book-01/Draft-02/01_Act_I/01_Chapter_01.md"
# Chapter 1: The Departure

@pov: Kaelen
@location: Launch Pad
@status: Revision

The quiet countdown echoed throughout the massive subterranean hangar. Kaelen secured his pressurized flight gloves and observed the violent storm clouds assembling along the northern horizon. A decade of clandestine quantum research culminated in this singular, dangerous test.
EOF

# Initialize Draft-03 auto-incrementing
bash "${SCRIPT_DIR}/scripts/init_draft.sh" "${MS_NAME}" -b "Book-01"
[ -d "${MS_DIR}/Book-01/Draft-03" ] || { echo "FAIL: Draft-03 auto-increment failed"; exit 1; }
grep -q 'active_draft: "Draft-03"' "${MS_DIR}/manuscript.yaml" || { echo "FAIL: manuscript.yaml active_draft not set to Draft-03"; exit 1; }
echo "[✓] Draft-03 auto-incremented successfully."

echo "=== Stage 3: Manuscript Comparison & Redline Diff with compare_drafts.sh ==="
# Test Terminal ANSI comparison
bash "${SCRIPT_DIR}/scripts/compare_drafts.sh" "${MS_NAME}" "Draft-02" "Draft-01" --terminal > "${TEST_DIR}/terminal_diff.txt"
grep -q "Ars Arcanum Manuscript Revision Comparison" "${TEST_DIR}/terminal_diff.txt" || { echo "FAIL: Terminal diff banner missing"; exit 1; }
grep -q "Chapter 1" "${TEST_DIR}/terminal_diff.txt" || { echo "FAIL: Chapter 1 missing from terminal diff"; exit 1; }
echo "[✓] Terminal ANSI comparison executed successfully."

# Test JSON metrics output
JSON_OUT="${TEST_DIR}/diff_metrics.json"
bash "${SCRIPT_DIR}/scripts/compare_drafts.sh" "${MS_NAME}" "Draft-02" "Draft-01" --json > "${JSON_OUT}"
python3 -c '
import sys, json
with open(sys.argv[1]) as f:
    data = json.load(f)
assert data["label_a"] == "Draft-01"
assert data["label_b"] == "Draft-02"
assert data["added_words"] > 0
assert data["deleted_words"] > 0
assert 0.0 <= data["similarity_ratio"] <= 1.0
assert len(data["chapters"]) >= 1
' "${JSON_OUT}"
echo "[✓] JSON metrics output validated."

# Test Standalone HTML Redline report generation
HTML_OUT="${TEST_DIR}/redline_report.html"
bash "${SCRIPT_DIR}/scripts/compare_drafts.sh" "${MS_NAME}" "Draft-02" "Draft-01" --html "${HTML_OUT}"
[ -f "${HTML_OUT}" ] || { echo "FAIL: HTML redline report not generated"; exit 1; }
grep -q "<!DOCTYPE html>" "${HTML_OUT}" || { echo "FAIL: Invalid HTML doctype"; exit 1; }
grep -q 'class="diff-ins"' "${HTML_OUT}" || { echo "FAIL: Missing diff-ins tags in HTML"; exit 1; }
grep -q 'class="diff-del"' "${HTML_OUT}" || { echo "FAIL: Missing diff-del tags in HTML"; exit 1; }
grep -q 'Ars Arcanum Redline' "${HTML_OUT}" || { echo "FAIL: Redline title missing"; exit 1; }
echo "[✓] HTML Redline report validated."

echo "=== Stage 4: Dual-Target Secure External Backup Replication ==="
# Configure secure external backup directory
python3 "${SCRIPT_DIR}/scripts/lib/config.py" backup-dest set "${SECURE_DEST}"
GET_DEST="$(python3 "${SCRIPT_DIR}/scripts/lib/config.py" backup-dest get)"
[ "${GET_DEST}" = "${SECURE_DEST}" ] || { echo "FAIL: backup-dest get mismatch: '${GET_DEST}' != '${SECURE_DEST}'"; exit 1; }

# Execute backup on manuscript
bash "${SCRIPT_DIR}/scripts/backup_world.sh" "${MS_NAME}"

# Verify local archive exists
LOCAL_BACKUPS="${MS_DIR}/Backups"
[ -d "${LOCAL_BACKUPS}" ] || LOCAL_BACKUPS="${MS_DIR}/05-Backups"
LOCAL_ARCHIVE="$(find "${LOCAL_BACKUPS}" -name "*.tar.gz" | head -n 1)"
[ -n "${LOCAL_ARCHIVE}" ] || { echo "FAIL: Local backup archive not found in ${LOCAL_BACKUPS}"; exit 1; }

# Verify secure external archive exists and checksum verifies
SECURE_ARCHIVE="$(find "${SECURE_DEST}" -name "*.tar.gz" | head -n 1)"
[ -n "${SECURE_ARCHIVE}" ] || { echo "FAIL: Secure external backup archive not found in ${SECURE_DEST}"; exit 1; }
SECURE_SHA="$(find "${SECURE_DEST}" -name "*.sha256" | head -n 1)"
[ -n "${SECURE_SHA}" ] || { echo "FAIL: Secure external SHA-256 not found in ${SECURE_DEST}"; exit 1; }

(
    cd "${SECURE_DEST}"
    sha256sum -c "$(basename "${SECURE_SHA}")"
)
echo "[✓] Dual-target secure external backup created and verified with SHA-256."

echo "=== Stage 5: Unified CLI Facade Dispatching ==="
# Test arcanum draft
bash "${SCRIPT_DIR}/scripts/arcanum" draft "${MS_NAME}" "Draft-04" -b "Book-01"
[ -d "${MS_DIR}/Book-01/Draft-04" ] || { echo "FAIL: arcanum draft failed to scaffold Draft-04"; exit 1; }

# Test arcanum new draft
bash "${SCRIPT_DIR}/scripts/arcanum" new draft "${MS_NAME}" "Draft-05" -b "Book-01"
[ -d "${MS_DIR}/Book-01/Draft-05" ] || { echo "FAIL: arcanum new draft failed to scaffold Draft-05"; exit 1; }

# Test arcanum compare
bash "${SCRIPT_DIR}/scripts/arcanum" compare "${MS_NAME}" "Draft-02" "Draft-01" --json > "${TEST_DIR}/cli_diff.json"
python3 -c '
import sys, json
with open(sys.argv[1]) as f:
    data = json.load(f)
assert data["label_a"] == "Draft-01"
assert data["label_b"] == "Draft-02"
' "${TEST_DIR}/cli_diff.json"

# Test arcanum backup-dest get
bash "${SCRIPT_DIR}/scripts/arcanum" backup-dest get | grep -q "${SECURE_DEST}" || { echo "FAIL: arcanum backup-dest get failed"; exit 1; }

echo "=== ALL DRAFT MANAGEMENT, DIFF COMPARATOR, AND SECURE BACKUP TESTS PASSED ==="
exit 0
