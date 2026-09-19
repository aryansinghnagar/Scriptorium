#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Backup Engine (REL-03)
# Purpose: Creates a decoupled, verified, compressed backup archive of a world
#          or manuscript with an immutable SHA-256 checksum manifest and metadata.
#          Supports dual-target backups (local project root + secure external/USB storage).
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Backup Engine — create a standalone, verified backup archive.

Usage:
  backup_world.sh [TARGET_NAME|TARGET_DIR] [OPTIONS]

Options:
  -w, --world NAME       World name or path
  -m, --manuscript NAME  Manuscript name or path
  -p, --project NAME     Project name or path
  -u, --universe NAME    Universe name (optional)
  -d, --dest DIR         Primary destination directory for archive
  -s, --secure-dest DIR  Explicit secure external/USB backup destination
  -n, --note NOTE        Optional backup note/label
  --no-local             Write only to secure external destination (skip local Backups/)
  -h, --help             Show this help and exit

Exit codes:
  0  backup created and checksum verified
  1  error (target not found, compression failure, checksum failure)
  2  usage error or destination path disallowed
  3  user abort (no target selected)
USAGE
}

WORLD_CLI=""
MANUSCRIPT_CLI=""
PROJECT_CLI=""
UNIVERSE_CLI=""
DEST_CLI=""
SECURE_DEST_CLI=""
NOTE_CLI=""
NO_LOCAL=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 2; }
            WORLD_CLI="$2"; shift 2 ;;
        -m|--manuscript)
            [ $# -ge 2 ] || { echo "Error: --manuscript requires a value." >&2; exit 2; }
            MANUSCRIPT_CLI="$2"; shift 2 ;;
        -p|--project)
            [ $# -ge 2 ] || { echo "Error: --project requires a value." >&2; exit 2; }
            PROJECT_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -d|--dest)
            [ $# -ge 2 ] || { echo "Error: --dest requires a value." >&2; exit 2; }
            DEST_CLI="$2"; shift 2 ;;
        -s|--secure-dest)
            [ $# -ge 2 ] || { echo "Error: --secure-dest requires a value." >&2; exit 2; }
            SECURE_DEST_CLI="$2"; shift 2 ;;
        -n|--note)
            [ $# -ge 2 ] || { echo "Error: --note requires a value." >&2; exit 2; }
            NOTE_CLI="$2"; shift 2 ;;
        --no-local)
            NO_LOCAL=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        --)
            shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *)
            POSITIONAL+=("$1"); shift ;;
    esac
done

TARGET_INPUT="${MANUSCRIPT_CLI:-${WORLD_CLI:-${PROJECT_CLI:-${POSITIONAL[0]:-}}}}"

if [ -z "${TARGET_INPUT}" ]; then
    if has_gui; then
        TARGET_INPUT=$(zenity --file-selection --directory \
            --title="Ars Arcanum — Select Project Directory to Back Up" \
            --filename="${HOME}/" || true)
    fi
fi

if [ -z "${TARGET_INPUT}" ]; then
    echo "No project directory specified. Aborting." >&2
    exit 3
fi

WORLD_DIR="$(resolve_target_dir "${TARGET_INPUT}" "${UNIVERSE_CLI}")"

if [ -z "${WORLD_DIR}" ] || [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: Directory not found: ${TARGET_INPUT}" >&2
    exit 2
fi

WORLD_NAME="$(basename "${WORLD_DIR}")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SAFE_NAME="$(sanitize_name "${WORLD_NAME}" "project")"

# Validate destination path against path traversal
validate_destination() {
    local raw_dest="$1"
    local resolved
    resolved="$(python3 -c 'import os, sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "${raw_dest}" 2>/dev/null || realpath -m "${raw_dest}" 2>/dev/null || echo "${raw_dest}")"
    
    # Reject explicit traversal tokens
    if [[ "${raw_dest}" == *".."* ]]; then
        echo "Error: Backup destination contains path traversal ('..')." >&2
        return 1
    fi
    printf '%s' "${resolved}"
}

# Resolve local and secure external backup directories
LOCAL_BACKUP_DIR=""
if [ -d "${WORLD_DIR}/05-Backups" ]; then
    LOCAL_BACKUP_DIR="${WORLD_DIR}/05-Backups"
else
    LOCAL_BACKUP_DIR="${WORLD_DIR}/Backups"
fi

# Check global secure backup destination setting
CONFIG_SECURE_DEST=""
if [ -f "${SCRIPT_DIR}/lib/config.py" ] && command -v python3 &>/dev/null; then
    CONFIG_SECURE_DEST="$(python3 "${SCRIPT_DIR}/lib/config.py" backup-dest get 2>/dev/null || true)"
fi

SECURE_BACKUP_DIR=""
if [ -n "${SECURE_DEST_CLI}" ]; then
    SECURE_BACKUP_DIR="$(validate_destination "${SECURE_DEST_CLI}")" || exit 2
elif [ -n "${DEST_CLI}" ]; then
    SECURE_BACKUP_DIR="$(validate_destination "${DEST_CLI}")" || exit 2
elif [ -n "${CONFIG_SECURE_DEST}" ]; then
    SECURE_BACKUP_DIR="$(validate_destination "${CONFIG_SECURE_DEST}")" || exit 2
fi

# Determine primary writing target
PRIMARY_BACKUP_DIR="${LOCAL_BACKUP_DIR}"
if [ "${NO_LOCAL}" -eq 1 ] && [ -n "${SECURE_BACKUP_DIR}" ]; then
    PRIMARY_BACKUP_DIR="${SECURE_BACKUP_DIR}"
fi
mkdir -p "${PRIMARY_BACKUP_DIR}"

ARCHIVE_BASE="${SAFE_NAME}-backup-${TIMESTAMP}"
ARCHIVE_TAR="${PRIMARY_BACKUP_DIR}/${ARCHIVE_BASE}.tar.gz"
CHECKSUM_FILE="${PRIMARY_BACKUP_DIR}/${ARCHIVE_BASE}.sha256"
META_FILE="${PRIMARY_BACKUP_DIR}/${ARCHIVE_BASE}.meta.json"

echo "Creating verified backup archive for: ${WORLD_NAME} ..."
echo "[i] Policy: .git history IS included (disaster-recovery restores keep version history)."

PARENT_DIR="$(dirname "${WORLD_DIR}")"
DIR_BASENAME="$(basename "${WORLD_DIR}")"

# Pre-flight free-space check
SRC_BYTES="$(du -sb "${WORLD_DIR}" 2>/dev/null | cut -f1 || echo 0)"
AVAIL_BYTES="$(df -B1 "${PRIMARY_BACKUP_DIR}" 2>/dev/null | awk 'NR==2 {print $4}' || echo 0)"
if [ "${SRC_BYTES}" -gt 0 ] && [ "${AVAIL_BYTES}" -gt 0 ] && [ "${AVAIL_BYTES}" -lt "${SRC_BYTES}" ]; then
    echo "Error: insufficient disk space in '${PRIMARY_BACKUP_DIR}' (need ~${SRC_BYTES} B, have ${AVAIL_BYTES} B)." >&2
    exit 1
fi

# Deterministic member order & archive creation
tar -czf "${ARCHIVE_TAR}" \
    -C "${PARENT_DIR}" \
    --sort=name \
    --owner=0 --group=0 --numeric-owner \
    --exclude="${DIR_BASENAME}/05-Backups" \
    --exclude="${DIR_BASENAME}/Backups" \
    --exclude="${DIR_BASENAME}/Exports" \
    --exclude="${DIR_BASENAME}/04-Publishing" \
    --exclude="${DIR_BASENAME}/.obsidian/workspace.json" \
    --exclude="${DIR_BASENAME}/.obsidian/cache" \
    --exclude="*.bak" \
    --exclude="*.tmp" \
    --exclude="*.log" \
    "${DIR_BASENAME}"

if [ ! -s "${ARCHIVE_TAR}" ]; then
    echo "Error: Backup archive creation failed or is empty: ${ARCHIVE_TAR}" >&2
    exit 1
fi

ACTUAL_SHA="$(sha256sum "${ARCHIVE_TAR}" | cut -d' ' -f1)"
echo "${ACTUAL_SHA}  ${ARCHIVE_BASE}.tar.gz" > "${CHECKSUM_FILE}"

GIT_COMMIT="none"
if [ -d "${WORLD_DIR}/.git" ] && command -v git &>/dev/null; then
    GIT_COMMIT="$(git -C "${WORLD_DIR}" rev-parse HEAD 2>/dev/null || echo "none")"
fi

ARCHIVE_BYTES="$(wc -c < "${ARCHIVE_TAR}" | tr -d ' ')"

python3 -c '
import json, sys
meta = {
    "world": sys.argv[1],
    "timestamp": sys.argv[2],
    "archive": sys.argv[3],
    "sha256": sys.argv[4],
    "size_bytes": int(sys.argv[5]),
    "git_commit": sys.argv[6],
    "note": sys.argv[7],
}
with open(sys.argv[8], "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)
    f.write("\n")
' "${WORLD_NAME}" "${TIMESTAMP}" "${ARCHIVE_BASE}.tar.gz" "${ACTUAL_SHA}" "${ARCHIVE_BYTES}" "${GIT_COMMIT}" "${NOTE_CLI:-auto-backup}" "${META_FILE}"

(
    cd "${PRIMARY_BACKUP_DIR}"
    sha256sum -c "${ARCHIVE_BASE}.sha256" >/dev/null
)

echo "[✓] Primary backup archive created and verified:"
echo "    Archive:  ${ARCHIVE_TAR}"
echo "    SHA-256:  ${ACTUAL_SHA}"
echo "    Metadata: ${META_FILE}"

# Dual-target replication to secure external/USB destination
SECURE_SYNCED=0
if [ -n "${SECURE_BACKUP_DIR}" ] && [ "${SECURE_BACKUP_DIR}" != "${PRIMARY_BACKUP_DIR}" ]; then
    echo "Replicating backup to secure external destination: ${SECURE_BACKUP_DIR} ..."
    if mkdir -p "${SECURE_BACKUP_DIR}" 2>/dev/null; then
        cp "${ARCHIVE_TAR}" "${SECURE_BACKUP_DIR}/"
        cp "${CHECKSUM_FILE}" "${SECURE_BACKUP_DIR}/"
        cp "${META_FILE}" "${SECURE_BACKUP_DIR}/"
        (
            cd "${SECURE_BACKUP_DIR}"
            sha256sum -c "${ARCHIVE_BASE}.sha256" >/dev/null
        )
        echo "[✓] Secure external backup verified at: ${SECURE_BACKUP_DIR}/${ARCHIVE_BASE}.tar.gz"
        SECURE_SYNCED=1
    else
        echo "[!] Warning: Could not write to secure external destination '${SECURE_BACKUP_DIR}' (device unmounted or permission denied)." >&2
    fi
fi

MSG="Backup created successfully for '${WORLD_NAME}'!\n\nLocal Archive: ${ARCHIVE_TAR}\nSHA256: ${ACTUAL_SHA:0:16}...\nSize: $(( ARCHIVE_BYTES / 1024 )) KB"
if [ "${SECURE_SYNCED}" -eq 1 ]; then
    MSG="${MSG}\n\n[✓] Secure External Backup Synced:\n${SECURE_BACKUP_DIR}/${ARCHIVE_BASE}.tar.gz"
fi

if has_gui; then
    zenity --info --title="Backup Created Successfully" --text="${MSG}" --width=500
fi

exit 0
