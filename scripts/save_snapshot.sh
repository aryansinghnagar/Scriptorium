#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Save Snapshot (Git Version History)
# Purpose: One-click tool to stage and record an immutable version snapshot
#          of your world and manuscripts without needing the terminal.
# ==============================================================================

set -euo pipefail

WORLDS_BASE="${HOME}/Worlds"
UNIVERSES_BASE="${HOME}/Universes"

# GUI detection works on both X11 and Wayland (M7)
has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

usage() {
    cat << 'USAGE'
Scriptorium Save Snapshot — one-click Git version snapshot of a world.

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
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 1; }
            WORLD_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 1; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -m|--note)
            [ $# -ge 2 ] || { echo "Error: --note requires a value." >&2; exit 1; }
            NOTE_CLI="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        --)
            shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

TARGET_INPUT="${WORLD_CLI:-${POSITIONAL[0]:-}}"
WORLD_CLI="${TARGET_INPUT}"

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed or not in PATH. Install git to snapshot." >&2
    exit 1
fi

# Discover all worlds across ~/Universes/*/Worlds/* and ~/Worlds/*
WORLDS=()
while IFS= read -r -d '' d; do
    [ -d "$d" ] && WORLDS+=("$d")
done < <(find "${UNIVERSES_BASE}" -mindepth 3 -maxdepth 3 -type d -path '*/Worlds/*' -print0 2>/dev/null)

while IFS= read -r -d '' d; do
    [ -d "$d" ] && WORLDS+=("$d")
done < <(find "${WORLDS_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)

if [ ${#WORLDS[@]} -eq 0 ] && [ -z "${WORLD_CLI}" ]; then
    if has_gui; then
        zenity --warning --title="No Worlds Found" --text="No world folders found in ~/Universes or ~/Worlds.\nCreate one first with 'New World Creator'."
    else
        echo "No world directories found." >&2
    fi
    exit 3
fi

SELECTED_WORLD=""

if [ -n "${WORLD_CLI}" ]; then
    if [ -d "${WORLD_CLI}" ]; then
        SELECTED_WORLD="$(cd "${WORLD_CLI}" && pwd)"
    elif [ -n "${UNIVERSE_CLI}" ] && [ -d "${UNIVERSES_BASE}/${UNIVERSE_CLI}/Worlds/${WORLD_CLI}" ]; then
        SELECTED_WORLD="${UNIVERSES_BASE}/${UNIVERSE_CLI}/Worlds/${WORLD_CLI}"
    elif [ -d "${WORLDS_BASE}/${WORLD_CLI}" ]; then
        SELECTED_WORLD="${WORLDS_BASE}/${WORLD_CLI}"
    else
        for w in "${WORLDS[@]}"; do
            if [ "$(basename "$w")" = "${WORLD_CLI}" ]; then
                SELECTED_WORLD="$w"
                break
            fi
        done
    fi

    if [ -z "${SELECTED_WORLD}" ] || [ ! -d "${SELECTED_WORLD}" ]; then
        echo "Error: World '${WORLD_CLI}' not found." >&2
        exit 1
    fi
elif [ ${#WORLDS[@]} -eq 1 ]; then
    SELECTED_WORLD="${WORLDS[0]}"
else
    if has_gui; then
        CHOICE_LIST=()
        for w in "${WORLDS[@]}"; do
            UNAME="$(basename "$(dirname "$(dirname "$w")")")"
            [ "$UNAME" = "home" ] || [ "$UNAME" = "aryan" ] && UNAME="Standalone"
            CHOICE_LIST+=("$(basename "$w")" "[Universe: ${UNAME}] $w")
        done
        SELECTED_DISPLAY=$(zenity --list --title="Select World to Snapshot" \
            --column="World Name" --column="Universe & Path" \
            --width=520 --height=320 \
            "${CHOICE_LIST[@]}" || true)
        if [ -n "${SELECTED_DISPLAY}" ]; then
            for w in "${WORLDS[@]}"; do
                if [ "$(basename "$w")" = "${SELECTED_DISPLAY}" ]; then
                    SELECTED_WORLD="$w"
                    break
                fi
            done
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
    echo "No world selected. Aborting snapshot." >&2
    exit 3
fi

WORLD_NAME=$(basename "${SELECTED_WORLD}")
cd "${SELECTED_WORLD}"

# Helper to handle transient index lock contention (e.g. background Obsidian Git commits)
wait_for_git_lock() {
    local repo_dir="${1:-.}"
    local lock_file="${repo_dir}/.git/index.lock"
    local attempts=0
    while [ -f "${lock_file}" ] && [ $attempts -lt 6 ]; do
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
05-Backups/
EOF
    git -c advice.addEmbeddedRepo=false add .
    if ! git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial repository creation for ${WORLD_NAME}" 2>/dev/null; then
        echo "[!] Initial commit skipped (git identity missing). Files staged."
    fi
fi

# Also snapshot discrete manuscript repositories if present under 01-Manuscript/
if [ -d "01-Manuscript" ]; then
    for ms_repo in 01-Manuscript/*/; do
        if [ -d "${ms_repo}.git" ]; then
            (
                cd "${ms_repo}"
                wait_for_git_lock "."
                git add -A
                if ! git diff --cached --quiet; then
                    git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Manuscript snapshot: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
                fi
            )
        fi
    done
fi

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
        notify-send "Scriptorium Snapshot" "${MSG}" -i document-save 2>/dev/null || true
    else
        echo "${MSG}"
    fi
    exit 0
fi

if ! git commit -q -m "${NOTE}" 2>/dev/null; then
    if ! git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "${NOTE}"; then
        echo "[!] Snapshot failed: git commit rejected the change." >&2
        exit 1
    fi
fi

MSG="Snapshot saved successfully for '${WORLD_NAME}'!\n\nNote: ${NOTE}"

if command -v notify-send &> /dev/null; then
    notify-send "Scriptorium Snapshot Saved" "${NOTE}" -i document-save 2>/dev/null || true
fi

if has_gui; then
    zenity --info --title="Snapshot Recorded" --text="${MSG}" --timeout=4
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi
