#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Restore Engine (REL-03)
# Purpose: Validates archive checksum integrity, stages extraction safely,
#          and restores a world into ~/Universes/<Universe>/Worlds/ or ~/Worlds/.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Scriptorium World Restore Engine — restore a world from a verified backup archive.

Usage:
  restore_world.sh [ARCHIVE_PATH] [OPTIONS]

Options:
  -a, --archive PATH   Path to the .tar.gz backup archive
  -t, --target NAME    Restore with a specific world name (default: original name)
  -u, --universe NAME  Restore into a specific universe (e.g. ~/Universes/<Universe>/Worlds)
  -d, --dest DIR       Explicit destination parent directory
  -f, --force          Overwrite existing target world if it already exists
  -h, --help           Show this help and exit

Exit codes:
  0  world restored successfully
  1  error (archive missing, checksum mismatch, corruption, target exists)
  3  user abort
USAGE
}

ARCHIVE_CLI=""
TARGET_NAME_CLI=""
UNIVERSE_CLI=""
DEST_PARENT_CLI=""
FORCE_OVERWRITE=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -a|--archive)
            [ $# -ge 2 ] || { echo "Error: --archive requires a value." >&2; exit 2; }
            ARCHIVE_CLI="$2"; shift 2 ;;
        -t|--target)
            [ $# -ge 2 ] || { echo "Error: --target requires a value." >&2; exit 2; }
            TARGET_NAME_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -d|--dest)
            [ $# -ge 2 ] || { echo "Error: --dest requires a value." >&2; exit 2; }
            DEST_PARENT_CLI="$2"; shift 2 ;;
        -f|--force)
            FORCE_OVERWRITE=1; shift ;;
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

ARCHIVE_PATH="${ARCHIVE_CLI:-${POSITIONAL[0]:-}}"

if [ -z "${ARCHIVE_PATH}" ]; then
    if has_gui; then
        ARCHIVE_PATH=$(zenity --file-selection \
            --title="Scriptorium — Select Backup Archive (.tar.gz) to Restore" \
            --file-filter="Scriptorium Archives (*.tar.gz) | *.tar.gz" || true)
    fi
fi

if [ -z "${ARCHIVE_PATH}" ]; then
    echo "No backup archive selected. Aborting." >&2
    exit 3
fi

if [ ! -f "${ARCHIVE_PATH}" ]; then
    echo "Error: Archive file not found: ${ARCHIVE_PATH}" >&2
    exit 2
fi

ARCHIVE_DIR="$(cd "$(dirname "${ARCHIVE_PATH}")" && pwd)"
ARCHIVE_FILE="$(basename "${ARCHIVE_PATH}")"
BASE_NAME="${ARCHIVE_FILE%.tar.gz}"
SHA_FILE="${ARCHIVE_DIR}/${BASE_NAME}.sha256"

echo "Verifying archive integrity for: ${ARCHIVE_FILE} ..."

if [ -f "${SHA_FILE}" ]; then
    echo "[i] Verifying SHA-256 checksum against ${SHA_FILE}..."
    (
        cd "${ARCHIVE_DIR}"
        if ! sha256sum -c "${BASE_NAME}.sha256" >/dev/null 2>&1; then
            echo "[!] ERROR: SHA-256 Checksum verification failed! Archive may be corrupt." >&2
            exit 1
        fi
    )
    echo "[✓] Archive checksum matches manifest."
else
    echo "[!] Notice: No .sha256 manifest found beside archive; skipping hash check."
fi

SUCCESS=0
STAGING_DIR="$(mktemp -d)"

cleanup() {
    if [ "${SUCCESS}" -eq 0 ] && [ -n "${STAGING_DIR:-}" ] && [ -d "${STAGING_DIR}" ]; then
        rm -rf "${STAGING_DIR}"
    fi
}
trap cleanup EXIT INT TERM

echo "Extracting archive into staging..."

# S-04: refuse archives whose members could escape the staging root or
# execute code on the next git operation, before extracting anything.
# Note: .git/hooks/*.sample files ship with every 'git init' and appear in
# every legitimate Scriptorium backup; only non-sample hooks (which would
# execute on the next snapshot commit) are rejected. The co-located sha256
# manifest proves integrity against bit-rot, not authenticity: anyone who
# can replace the archive can regenerate the manifest.
ARCHIVE_MEMBERS="$(tar -tzf "${ARCHIVE_PATH}")" || {
    echo "Error: cannot list archive members (corrupt or non-gzip tarball)." >&2
    exit 1
}
# Absolute paths and '..' traversal components
if printf '%s\n' "${ARCHIVE_MEMBERS}" | grep -Eq '^/|(^|/)\.\.(/|$)'; then
    echo "Error: archive contains absolute or path-traversal members; refusing extraction." >&2
    exit 1
fi
# Members outside the single root world directory
if printf '%s\n' "${ARCHIVE_MEMBERS}" | grep -Ev '^[^/]+/' | grep -q .; then
    echo "Error: archive contains unexpected root-level entries; refusing extraction." >&2
    exit 1
fi
# Non-sample git hooks planted in the world repository
if printf '%s\n' "${ARCHIVE_MEMBERS}" | grep -E '/\.git/hooks/[^/]+$' | grep -vq '\.sample$'; then
    echo "Error: archive contains non-sample .git/hooks members; refusing extraction (code-execution risk)." >&2
    exit 1
fi

tar -xzf "${ARCHIVE_PATH}" -C "${STAGING_DIR}" --no-same-owner --no-same-permissions

EXTRACTED_DIR="$(find "${STAGING_DIR}" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
if [ -z "${EXTRACTED_DIR}" ] || [ ! -d "${EXTRACTED_DIR}" ]; then
    echo "Error: Archive did not contain a root world directory." >&2
    exit 1
fi

ORIGINAL_NAME="$(basename "${EXTRACTED_DIR}")"
FINAL_WORLD_NAME="${TARGET_NAME_CLI:-${ORIGINAL_NAME}}"

FINAL_WORLD_NAME="$(printf '%s' "${FINAL_WORLD_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"

DEST_PARENT=""
if [ -n "${DEST_PARENT_CLI}" ]; then
    DEST_PARENT="${DEST_PARENT_CLI}"
elif [ -n "${UNIVERSE_CLI}" ]; then
    RESOLVED_U="$(resolve_universe_dir "${UNIVERSE_CLI}")"
    if [ -n "${RESOLVED_U}" ]; then
        DEST_PARENT="${RESOLVED_U}"
    else
        DEST_PARENT="${UNIVERSES_BASE}/${UNIVERSE_CLI}"
    fi
elif [ -f "${EXTRACTED_DIR}/manuscript.yaml" ] || [ -d "${EXTRACTED_DIR}/Book-01" ]; then
    DEST_PARENT="${MANUSCRIPTS_BASE}"
elif [ -d "${UNIVERSES_BASE}/Default-Universe" ]; then
    DEST_PARENT="${UNIVERSES_BASE}/Default-Universe"
else
    DEST_PARENT="${UNIVERSES_BASE}/Default-Universe"
fi

TARGET_FINAL_DIR="${DEST_PARENT}/${FINAL_WORLD_NAME}"

if [ ! -d "${EXTRACTED_DIR}/Characters" ] && [ ! -d "${EXTRACTED_DIR}/00-World-Bible" ] && \
   [ ! -d "${EXTRACTED_DIR}/01-Manuscript" ] && [ ! -d "${EXTRACTED_DIR}/Book-01" ] && \
   [ ! -f "${EXTRACTED_DIR}/world.yaml" ] && [ ! -f "${EXTRACTED_DIR}/manuscript.yaml" ] && \
   [ ! -f "${EXTRACTED_DIR}/scriptorium.yaml" ]; then
    echo "Error: Archive contents do not appear to be a valid Scriptorium project." >&2
    exit 1
fi

if [ -d "${TARGET_FINAL_DIR}" ]; then
    if [ "${FORCE_OVERWRITE}" -eq 1 ]; then
        echo "[!] Target directory exists. Overwriting due to --force..."
        rm -rf "${TARGET_FINAL_DIR}"
    else
        echo "Error: Target directory '${TARGET_FINAL_DIR}' already exists. Use --force to overwrite." >&2
        exit 1
    fi
fi

mkdir -p "${DEST_PARENT}"
mv "${EXTRACTED_DIR}" "${TARGET_FINAL_DIR}"
SUCCESS=1

echo "[✓] World successfully restored to:"
echo "    ${TARGET_FINAL_DIR}"

MSG="World '${FINAL_WORLD_NAME}' successfully restored!\n\nLocation:\n${TARGET_FINAL_DIR}"

if has_gui; then
    zenity --info --title="World Restored Successfully" --text="${MSG}" --width=450
fi

exit 0
