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
  -a, --all              Back up all discovered worlds and manuscripts
  -d, --dest DIR         Primary destination directory for archive
  -s, --secure-dest DIR  Explicit secure external/USB backup destination
  -n, --note NOTE        Optional backup note/label
  -e, --encrypt [KEY_ID] Encrypt backup with GPG (asymmetric if KEY_ID given, else symmetric)
  --symmetric            Encrypt backup using GPG symmetric cipher (AES-256)
  --gpg-key KEY_ID       Recipient GPG key ID for asymmetric encryption
  --passphrase PASS      Passphrase for symmetric encryption (non-interactive)
  --passphrase-file FILE Passphrase file for symmetric encryption
  --no-local             Write only to secure external destination (skip local Backups/)
  -h, --help             Show this help and exit

Exit codes:
  0  backup created and checksum verified
  1  error (target not found, compression failure, checksum failure, encryption error)
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
ENCRYPTED_BACKUP=0
ENCRYPTION_TYPE="none"
GPG_KEY=""
PASSPHRASE_CLI=""
PASSPHRASE_FILE_CLI=""
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
        -e|--encrypt)
            ENCRYPTED_BACKUP=1
            if [ $# -ge 2 ] && [[ "$2" != -* ]]; then
                GPG_KEY="$2"; shift 2
            else
                shift
            fi ;;
        --symmetric)
            ENCRYPTED_BACKUP=1
            ENCRYPTION_TYPE="symmetric"; shift ;;
        --gpg-key)
            [ $# -ge 2 ] || { echo "Error: --gpg-key requires a value." >&2; exit 2; }
            ENCRYPTED_BACKUP=1
            GPG_KEY="$2"; shift 2 ;;
        --passphrase)
            [ $# -ge 2 ] || { echo "Error: --passphrase requires a value." >&2; exit 2; }
            PASSPHRASE_CLI="$2"; shift 2 ;;
        --passphrase-file)
            [ $# -ge 2 ] || { echo "Error: --passphrase-file requires a value." >&2; exit 2; }
            PASSPHRASE_FILE_CLI="$2"; shift 2 ;;
        --all)
            BACKUP_ALL=1; shift ;;
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

# Handle bulk --all mode
if [ "${BACKUP_ALL:-0}" -eq 1 ] || [ "${TARGET_INPUT}" = "--all" ] || [ "${TARGET_INPUT}" = "all" ]; then
    discover_worlds ALL_WORLDS
    discover_manuscripts ALL_MS
    echo "=== Ars Arcanum Bulk Backup Engine ==="
    TOTAL_PROCS=0
    for w in "${ALL_WORLDS[@]}"; do
        [ -d "$w" ] || continue
        echo "Backing up World: $(basename "$w") ..."
        bash "${SCRIPT_DIR}/backup_world.sh" -w "$w" ${DEST_CLI:+-d "$DEST_CLI"} ${SECURE_DEST_CLI:+-s "$SECURE_DEST_CLI"} || true
        TOTAL_PROCS=$((TOTAL_PROCS + 1))
    done
    for m in "${ALL_MS[@]}"; do
        [ -d "$m" ] || continue
        echo "Backing up Manuscript: $(basename "$m") ..."
        bash "${SCRIPT_DIR}/backup_world.sh" -m "$m" ${DEST_CLI:+-d "$DEST_CLI"} ${SECURE_DEST_CLI:+-s "$SECURE_DEST_CLI"} || true
        TOTAL_PROCS=$((TOTAL_PROCS + 1))
    done
    echo "[✓] Bulk backup completed for ${TOTAL_PROCS} project(s)."
    exit 0
fi

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

# Pre-verification: Ensure tar archive integrity is valid before calculating SHA-256
if ! tar -tzf "${ARCHIVE_TAR}" >/dev/null 2>&1; then
    echo "Error: Backup archive is corrupted or unreadable: ${ARCHIVE_TAR}" >&2
    rm -f "${ARCHIVE_TAR}"
    exit 1
fi

FINAL_ARCHIVE="${ARCHIVE_TAR}"
FINAL_ARCHIVE_NAME="${ARCHIVE_BASE}.tar.gz"

if [ "${ENCRYPTED_BACKUP}" -eq 1 ]; then
    if ! command -v gpg &>/dev/null && ! command -v gpg2 &>/dev/null; then
        echo "Error: GPG is required for encrypted backups but was not found in PATH." >&2
        rm -f "${ARCHIVE_TAR}"
        exit 1
    fi
    GPG_CMD="gpg"
    command -v gpg &>/dev/null || GPG_CMD="gpg2"
    
    ARCHIVE_GPG="${PRIMARY_BACKUP_DIR}/${ARCHIVE_BASE}.tar.gz.gpg"
    GPG_ARGS=(--batch --yes)
    
    if [ -n "${PASSPHRASE_CLI}" ]; then
        GPG_ARGS+=(--pinentry-mode loopback --passphrase "${PASSPHRASE_CLI}")
    elif [ -n "${PASSPHRASE_FILE_CLI}" ]; then
        GPG_ARGS+=(--pinentry-mode loopback --passphrase-file "${PASSPHRASE_FILE_CLI}")
    fi
    
    if [ -n "${GPG_KEY}" ]; then
        ENCRYPTION_TYPE="asymmetric"
        "${GPG_CMD}" "${GPG_ARGS[@]}" --encrypt --recipient "${GPG_KEY}" -o "${ARCHIVE_GPG}" "${ARCHIVE_TAR}"
    else
        ENCRYPTION_TYPE="symmetric"
        "${GPG_CMD}" "${GPG_ARGS[@]}" --symmetric --cipher-algo AES256 -o "${ARCHIVE_GPG}" "${ARCHIVE_TAR}"
    fi
    
    rm -f "${ARCHIVE_TAR}"
    FINAL_ARCHIVE="${ARCHIVE_GPG}"
    FINAL_ARCHIVE_NAME="${ARCHIVE_BASE}.tar.gz.gpg"
fi

ACTUAL_SHA="$(sha256sum "${FINAL_ARCHIVE}" | cut -d' ' -f1)"
echo "${ACTUAL_SHA}  ${FINAL_ARCHIVE_NAME}" > "${CHECKSUM_FILE}"

GIT_COMMIT="none"
if [ -d "${WORLD_DIR}/.git" ] && command -v git &>/dev/null; then
    GIT_COMMIT="$(git -C "${WORLD_DIR}" rev-parse HEAD 2>/dev/null || echo "none")"
fi

ARCHIVE_BYTES="$(wc -c < "${FINAL_ARCHIVE}" | tr -d ' ')"

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
    "encrypted": sys.argv[8] == "1",
    "encryption_type": sys.argv[9],
    "gpg_recipient": sys.argv[10],
}
with open(sys.argv[11], "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)
    f.write("\n")
' "${WORLD_NAME}" "${TIMESTAMP}" "${FINAL_ARCHIVE_NAME}" "${ACTUAL_SHA}" "${ARCHIVE_BYTES}" "${GIT_COMMIT}" "${NOTE_CLI:-auto-backup}" "${ENCRYPTED_BACKUP}" "${ENCRYPTION_TYPE}" "${GPG_KEY:-none}" "${META_FILE}"

(
    cd "${PRIMARY_BACKUP_DIR}"
    sha256sum -c "${ARCHIVE_BASE}.sha256" >/dev/null
)

echo "[✓] Primary backup archive created and verified:"
echo "    Archive:  ${FINAL_ARCHIVE}"
echo "    SHA-256:  ${ACTUAL_SHA}"
echo "    Metadata: ${META_FILE}"

# Dual-target replication to secure external/USB destination
SECURE_SYNCED=0
if [ -n "${SECURE_BACKUP_DIR}" ] && [ "${SECURE_BACKUP_DIR}" != "${PRIMARY_BACKUP_DIR}" ]; then
    echo "Replicating backup to secure external destination: ${SECURE_BACKUP_DIR} ..."
    if mkdir -p "${SECURE_BACKUP_DIR}" 2>/dev/null; then
        cp "${FINAL_ARCHIVE}" "${SECURE_BACKUP_DIR}/"
        cp "${CHECKSUM_FILE}" "${SECURE_BACKUP_DIR}/"
        cp "${META_FILE}" "${SECURE_BACKUP_DIR}/"
        (
            cd "${SECURE_BACKUP_DIR}"
            sha256sum -c "${ARCHIVE_BASE}.sha256" >/dev/null
        )
        echo "[✓] Secure external backup verified at: ${SECURE_BACKUP_DIR}/${FINAL_ARCHIVE_NAME}"
        SECURE_SYNCED=1
    else
        echo "[!] Warning: Could not write to secure external destination '${SECURE_BACKUP_DIR}' (device unmounted or permission denied)." >&2
    fi
fi

MSG="Backup created successfully for '${WORLD_NAME}'!\n\nLocal Archive: ${FINAL_ARCHIVE}\nSHA256: ${ACTUAL_SHA:0:16}...\nSize: $(( ARCHIVE_BYTES / 1024 )) KB"
if [ "${SECURE_SYNCED}" -eq 1 ]; then
    MSG="${MSG}\n\n[✓] Secure External Backup Synced:\n${SECURE_BACKUP_DIR}/${FINAL_ARCHIVE_NAME}"
fi

if has_gui; then
    zenity --info --title="Backup Created Successfully" --text="${MSG}" --width=500
fi

exit 0
