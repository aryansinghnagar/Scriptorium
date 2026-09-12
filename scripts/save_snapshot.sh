#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Save Snapshot (Git Version History)
# Purpose: One-click tool to stage and record an immutable version snapshot
#          of your world and manuscripts without needing the terminal.
# ==============================================================================

set -euo pipefail

WORLDS_BASE="${HOME}/Worlds"

# GUI detection works on both X11 and Wayland (M7)
has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

if [ ! -d "${WORLDS_BASE}" ]; then
    mkdir -p "${WORLDS_BASE}"
fi

usage() {
    cat << 'USAGE'
Scriptorium Save Snapshot — one-click Git version snapshot of a world.

Usage:
  save_snapshot.sh [OPTIONS]

Options:
  -w, --world NAME    World directory name under ~/Worlds (skips picker)
  -m, --note NOTE     Snapshot note (default: "Snapshot: <date>")
  -h, --help          Show this help and exit

Exit codes:
  0  snapshot saved (or nothing to commit)
  1  error (git missing, commit rejected)
  3  user abort (no world selected)
USAGE
}

WORLD_CLI=""
NOTE_CLI=""
while [ $# -gt 0 ]; do
    case "$1" in
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 1; }
            WORLD_CLI="$2"; shift 2 ;;
        -m|--note)
            [ $# -ge 2 ] || { echo "Error: --note requires a value." >&2; exit 1; }
            NOTE_CLI="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
        *) echo "Error: unexpected argument: $1 (see --help)" >&2; exit 1 ;;
    esac
done

# P-04: a snapshot without git is a hard error, not a set -e crash
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed or not in PATH. Install git to snapshot."
    exit 1
fi

# Find available worlds (H5: NUL-safe, space-safe)
WORLDS=()
while IFS= read -r -d '' d; do
    WORLDS+=("$d")
done < <(find "${WORLDS_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)

if [ ${#WORLDS[@]} -eq 0 ]; then
    if has_gui; then
        zenity --warning --title="No Worlds Found" --text="No world folders found in ${WORLDS_BASE}.\nCreate one first with 'New World Creator'."
    else
        echo "No world directories found in ${WORLDS_BASE}."
    fi
    exit 3
fi

SELECTED_WORLD=""

if [ -n "${WORLD_CLI}" ]; then
    SELECTED_WORLD="${WORLDS_BASE}/${WORLD_CLI}"
    if [ ! -d "${SELECTED_WORLD}" ]; then
        echo "Error: world '${WORLD_CLI}' not found in ${WORLDS_BASE}."
        exit 1
    fi
elif [ ${#WORLDS[@]} -eq 1 ]; then
    SELECTED_WORLD="${WORLDS[0]}"
else
    # Build list for Zenity or CLI
    if has_gui; then
        CHOICE_LIST=()
        for w in "${WORLDS[@]}"; do
            CHOICE_LIST+=("$(basename "$w")" "$w")
        done
        SELECTED_NAME=$(zenity --list --title="Select World to Snapshot" \
            --column="World Name" --column="Path" \
            --hide-column=2 \
            "${CHOICE_LIST[@]}" || true)
        if [ -n "${SELECTED_NAME}" ]; then
            SELECTED_WORLD="${WORLDS_BASE}/${SELECTED_NAME}"
        fi
    else
        echo "Select world to snapshot:"
        select w in "${WORLDS[@]}"; do
            if [ -n "${w:-}" ]; then
                SELECTED_WORLD="$w"
            fi
            break
        done
    fi
fi

if [ -z "${SELECTED_WORLD}" ] || [ ! -d "${SELECTED_WORLD}" ]; then
    echo "No world selected. Aborting snapshot."
    exit 3
fi

WORLD_NAME=$(basename "${SELECTED_WORLD}")
cd "${SELECTED_WORLD}"

# Ensure Git is initialized (M11: explicit identity handling)
if [ ! -d ".git" ]; then
    git init -q
    cat << 'EOF' > .gitignore
.obsidian/workspace.json
.obsidian/cache
*.bak
*.tmp
*.log
.DS_Store
05-Backups/
EOF
    git add .
    if ! git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial repository creation for ${WORLD_NAME}" 2>/dev/null; then
        echo "[!] Initial commit skipped (git identity missing). Files staged."
    fi
fi

# Prompt for snapshot notes (P-04: --note flag is honored headlessly)
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

# Stage all files and commit
git add -A

if git diff --cached --quiet; then
    MSG="No changes detected in '${WORLD_NAME}' since last snapshot."
    if command -v notify-send &> /dev/null; then
        notify-send "Scriptorium Snapshot" "${MSG}" -i document-save
    else
        echo "${MSG}"
    fi
    exit 0
fi

# H6: guarded commit so set -e does not abort silently; falls back to ephemeral identity
if ! git commit -q -m "${NOTE}"; then
    echo "[i] No git identity configured, retrying with ephemeral Scriptorium identity..."
    if ! git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "${NOTE}"; then
        echo "[!] Snapshot failed: git commit rejected the change."
        exit 1
    fi
fi

MSG="Snapshot saved successfully for '${WORLD_NAME}'!\n\nNote: ${NOTE}"

if command -v notify-send &> /dev/null; then
    notify-send "Scriptorium Snapshot Saved" "${NOTE}" -i document-save
fi

if has_gui; then
    zenity --info --title="Snapshot Recorded" --text="${MSG}" --timeout=4
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi
