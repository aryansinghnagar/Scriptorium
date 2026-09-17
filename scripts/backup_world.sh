#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Backup Engine (REL-03)
# Purpose: Creates a decoupled, verified, compressed backup archive of a world
#          with an immutable SHA-256 checksum manifest and metadata.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Scriptorium World Backup Engine — create a standalone, verified backup archive.

Usage:
  backup_world.sh [WORLD_NAME|WORLD_DIR] [OPTIONS]

Options:
  -w, --world NAME     World name or path
  -u, --universe NAME  Universe name (optional)
  -d, --dest DIR       Destination directory for archive (default: <world>/05-Backups)
  -n, --note NOTE      Optional backup note/label
  -h, --help           Show this help and exit

Exit codes:
  0  backup created and checksum verified
  1  error (world not found, compression failure, checksum failure)
  3  user abort (no world selected)
USAGE
}

WORLD_CLI=""
MANUSCRIPT_CLI=""
PROJECT_CLI=""
UNIVERSE_CLI=""
DEST_CLI=""
NOTE_CLI=""
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
        -n|--note)
            [ $# -ge 2 ] || { echo "Error: --note requires a value." >&2; exit 2; }
            NOTE_CLI="$2"; shift 2 ;;
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
            --title="Scriptorium — Select World Directory to Back Up" \
            --filename="${HOME}/" || true)
    fi
fi

if [ -z "${TARGET_INPUT}" ]; then
    echo "No world directory specified. Aborting." >&2
    exit 3
fi

WORLD_DIR="$(resolve_world_dir "${TARGET_INPUT}" "${UNIVERSE_CLI}")"
if [ -z "${WORLD_DIR}" ] || [ ! -d "${WORLD_DIR}" ]; then
    WORLD_DIR="$(resolve_manuscript_dir "${TARGET_INPUT}")"
fi

if [ -z "${WORLD_DIR}" ] || [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: Directory not found: ${TARGET_INPUT}" >&2
    exit 2
fi

WORLD_NAME="$(basename "${WORLD_DIR}")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SAFE_NAME="$(sanitize_name "${WORLD_NAME}" "project")"

if [ -n "${DEST_CLI}" ]; then
    BACKUP_DIR="${DEST_CLI}"
elif [ -d "${WORLD_DIR}/05-Backups" ]; then
    BACKUP_DIR="${WORLD_DIR}/05-Backups"
else
    BACKUP_DIR="${WORLD_DIR}/Backups"
fi
mkdir -p "${BACKUP_DIR}"

ARCHIVE_BASE="${SAFE_NAME}-backup-${TIMESTAMP}"
ARCHIVE_TAR="${BACKUP_DIR}/${ARCHIVE_BASE}.tar.gz"
CHECKSUM_FILE="${BACKUP_DIR}/${ARCHIVE_BASE}.sha256"
META_FILE="${BACKUP_DIR}/${ARCHIVE_BASE}.meta.json"

echo "Creating verified backup archive for: ${WORLD_NAME} ..."

PARENT_DIR="$(dirname "${WORLD_DIR}")"
DIR_BASENAME="$(basename "${WORLD_DIR}")"

tar -czf "${ARCHIVE_TAR}" \
    -C "${PARENT_DIR}" \
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

# F-07: write metadata with proper JSON escaping. The previous heredoc
# interpolated the note directly, so any note containing quotes, backslashes,
# or newlines produced metadata no JSON consumer could parse. Values are
# passed as argv (never interpolated into Python source).
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
    cd "${BACKUP_DIR}"
    sha256sum -c "${ARCHIVE_BASE}.sha256" >/dev/null
)

echo "[✓] Backup archive created and verified:"
echo "    Archive:  ${ARCHIVE_TAR}"
echo "    SHA-256:  ${ACTUAL_SHA}"
echo "    Metadata: ${META_FILE}"

MSG="Backup created successfully for '${WORLD_NAME}'!\n\nArchive: ${ARCHIVE_TAR}\nSHA256: ${ACTUAL_SHA:0:16}...\nSize: $(( ARCHIVE_BYTES / 1024 )) KB"

if has_gui; then
    zenity --info --title="Backup Created Successfully" --text="${MSG}" --width=450
fi

exit 0
