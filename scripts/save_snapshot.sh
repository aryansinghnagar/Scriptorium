#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Save Snapshot (Git Version History)
# Purpose: One-click tool to stage and record an immutable version snapshot
#          of your world and manuscripts without needing the terminal.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Save Snapshot — one-click Git version snapshot of a world.

Usage:
  save_snapshot.sh [WORLD_NAME|WORLD_DIR] [OPTIONS]

Options:
  -w, --world NAME     World directory name or path (skips picker)
  -u, --universe NAME  Universe name (optional filter)
  -m, --note NOTE      Snapshot note (default: "Snapshot: <date>")
  -h, --help           Show this help and exit

Exit codes:
  0  snapshot saved (or nothing to commit)
  1  error (git missing, commit rejected)
  3  user abort (no world selected)
USAGE
}

WORLD_CLI=""
UNIVERSE_CLI=""
NOTE_CLI=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 2; }
            WORLD_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -m|--note)
            [ $# -ge 2 ] || { echo "Error: --note requires a value." >&2; exit 2; }
            NOTE_CLI="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        --)
            shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

TARGET_INPUT="${WORLD_CLI:-${POSITIONAL[0]:-}}"
WORLD_CLI="${TARGET_INPUT}"

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed or not in PATH. Install git to snapshot." >&2
    exit 2
fi

# Discover all worlds and manuscripts
discover_worlds WORLDS
discover_manuscripts MANUSCRIPTS

if [ ${#WORLDS[@]} -eq 0 ] && [ ${#MANUSCRIPTS[@]} -eq 0 ] && [ -z "${WORLD_CLI}" ]; then
    if has_gui; then
        zenity --warning --title="No Projects Found" --text="No world or manuscript folders found in ~/Universes, ~/Worlds, or ~/Manuscripts.\nCreate one first."
    else
        echo "No world or manuscript directories found." >&2
    fi
    exit 3
fi

SELECTED_WORLD=""

if [ -n "${WORLD_CLI}" ]; then
    SELECTED_WORLD="$(resolve_target_dir "${WORLD_CLI}" "${UNIVERSE_CLI}")"
    if [ -z "${SELECTED_WORLD}" ] || [ ! -d "${SELECTED_WORLD}" ]; then
        echo "Error: Target '${WORLD_CLI}' not found." >&2
        exit 2
    fi
elif [ ${#WORLDS[@]} -eq 1 ] && [ ${#MANUSCRIPTS[@]} -eq 0 ]; then
    SELECTED_WORLD="${WORLDS[0]}"
    warn_if_legacy_root "${SELECTED_WORLD}"
elif [ ${#WORLDS[@]} -eq 0 ] && [ ${#MANUSCRIPTS[@]} -eq 1 ]; then
    SELECTED_WORLD="${MANUSCRIPTS[0]}"
else
    if has_gui; then
        CHOICE_LIST=()
        for m in "${MANUSCRIPTS[@]}"; do
            CHOICE_LIST+=("$(basename "$m")" "[Manuscript] $m")
        done
        for w in "${WORLDS[@]}"; do
            CHOICE_LIST+=("$(basename "$w")" "[World Lore] $w")
        done
        SELECTED_DISPLAY=$(zenity --list --title="Select Target to Snapshot" \
            --column="Name" --column="Type & Path" \
            --width=520 --height=320 \
            "${CHOICE_LIST[@]}" || true)
        if [ -n "${SELECTED_DISPLAY}" ]; then
            SELECTED_WORLD="$(resolve_manuscript_dir "${SELECTED_DISPLAY}")"
            [ -z "${SELECTED_WORLD}" ] && SELECTED_WORLD="$(resolve_world_dir "${SELECTED_DISPLAY}")"
        fi
    else
        ALL_TARGETS=("${MANUSCRIPTS[@]}" "${WORLDS[@]}")
        if [ ${#ALL_TARGETS[@]} -eq 1 ]; then
            SELECTED_WORLD="${ALL_TARGETS[0]}"
        else
            # TST-03: never block on `select` without a TTY (CI/headless
            # hangs forever). Fail closed with an actionable listing.
            if [ ! -t 0 ]; then
                {
                    echo "Error: Multiple projects discovered — specify one (non-interactive shell, no --world given):"
                    for t in "${ALL_TARGETS[@]}"; do
                        echo "  - ${t}"
                    done
                    echo "Usage: save_snapshot.sh --world <NAME|PATH> [-m note]"
                } >&2
                exit 2
            fi
            echo "Select project to snapshot:"
            select w in "${ALL_TARGETS[@]}"; do
                if [ -n "${w:-}" ]; then
                    SELECTED_WORLD="$w"
                fi
                break
            done
        fi
    fi
fi

if [ -z "${SELECTED_WORLD}" ] || [ ! -d "${SELECTED_WORLD}" ]; then
    echo "No target selected. Aborting snapshot." >&2
    exit 3
fi

WORLD_NAME=$(basename "${SELECTED_WORLD}")
cd "${SELECTED_WORLD}"

# Acquire advisory world lock (F-28)
arcanum_lock_dir "${SELECTED_WORLD}" 10 "snapshot" || exit 1
trap 'arcanum_unlock_dir "${SELECTED_WORLD}"' EXIT INT TERM

# Helper to handle transient index lock contention (e.g. background Obsidian Git commits)
wait_for_git_lock() {
    local repo_dir="${1:-.}"
    local lock_file="${repo_dir}/.git/index.lock"
    local attempts=0
    while [ -f "${lock_file}" ] && [ $attempts -lt 12 ]; do
        sleep 0.5
        attempts=$((attempts + 1))
    done
}

# Ensure Git is initialized
if [ ! -d ".git" ]; then
    git init -q
    git config advice.addEmbeddedRepo false
    cat << 'EOF' > .gitignore
.obsidian/workspace.json
.obsidian/cache
*.bak
*.tmp
*.log
.DS_Store
Backups/
05-Backups/
Exports/
04-Publishing/
EOF
    git -c advice.addEmbeddedRepo=false add .
    if ! git_commit_safe "Initial repository creation for ${WORLD_NAME}"; then
        echo "[!] Initial commit skipped. Files staged."
    fi
fi

# Also snapshot discrete volume repositories if present
# TST-03: nullglob so a non-matching pattern expands to nothing instead of
# the literal string "Book-*/".
shopt -s nullglob
for ms_repo in Book-*/ 01-Manuscript/*/; do
    if [ -d "${ms_repo}.git" ]; then
        (
            cd "${ms_repo}"
            wait_for_git_lock "."
            git add -A
            if ! git diff --cached --quiet; then
                if ! git_commit_safe "Volume snapshot: $(date '+%Y-%m-%d %H:%M')"; then
                    echo "[!] Warning: volume commit skipped for '${ms_repo}' (git lock contention); world snapshot may reference a stale state." >&2
                fi
            fi
        )
    fi
done

TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
DEFAULT_MSG="Snapshot: ${TIMESTAMP}"
NOTE="${NOTE_CLI:-}"

if [ -z "${NOTE}" ] && has_gui; then
    NOTE=$(zenity --entry \
        --title="Save Snapshot — ${WORLD_NAME}" \
        --text="Enter a note describing what you wrote or changed (optional):" \
        --entry-text="${DEFAULT_MSG}" || true)
fi

if [ -z "${NOTE}" ]; then
    NOTE="${DEFAULT_MSG}"
fi

wait_for_git_lock "."
git -c advice.addEmbeddedRepo=false add -A

if git diff --cached --quiet; then
    MSG="No uncommitted changes in '${WORLD_NAME}' since last snapshot."
    if command -v notify-send &> /dev/null; then
        notify-send "Ars Arcanum Snapshot" "${MSG}" -i document-save 2>/dev/null || true
    else
        echo "${MSG}"
    fi
    exit 0
fi

if ! git_commit_safe "${NOTE}"; then
    echo "[!] Snapshot failed: git commit rejected the change." >&2
    exit 1
fi

MSG="Snapshot saved successfully for '${WORLD_NAME}'!\n\nNote: ${NOTE}"

if command -v notify-send &> /dev/null; then
    notify-send "Ars Arcanum Snapshot Saved" "${NOTE}" -i document-save 2>/dev/null || true
fi

if has_gui; then
    zenity --info --title="Snapshot Recorded" --text="${MSG}" --timeout=4
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi
