#!/usr/bin/env bash
# ==============================================================================
# Scriptorium World Initializer
# Purpose: Creates a brand new world folder structure ~/Worlds/<WorldName>
#          with Obsidian World Bible templates, novelWriter project scaffolding,
#          maps/art/publishing directories, and Git tracking.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORLDS_BASE="${HOME}/Worlds"

mkdir -p "${WORLDS_BASE}"

# GUI detection works on both X11 and Wayland (M7)
has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

usage() {
    cat << 'USAGE'
Scriptorium World Initializer — scaffold ~/Worlds/<WorldName> with the
Obsidian World Bible, novelWriter manuscript, maps/art/publishing dirs,
and a local Git snapshot repository.

Usage:
  init_world.sh [WORLD_NAME] [OPTIONS]

Options:
  -n, --name NAME    World name (same as the positional argument)
  -h, --help         Show this help and exit

Exit codes:
  0  world created
  1  error (invalid name, world already exists)
  3  user abort (no name provided)

Names are sanitized to [A-Za-z0-9_-] (max 64 chars); spaces become dashes.
USAGE
}

# Prompt for World Name: CLI arg > GUI entry > TTY prompt (P-04)
WORLD_NAME=""
WORLD_NAME_CLI=""
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--name)
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 1; }
            WORLD_NAME_CLI="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        --) shift; [ $# -gt 0 ] && { WORLD_NAME_CLI="$1"; shift; } ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
        *) WORLD_NAME_CLI="$1"; shift ;;
    esac
done

if [ -n "${WORLD_NAME_CLI}" ]; then
    WORLD_NAME="${WORLD_NAME_CLI}"
elif has_gui; then
    WORLD_NAME=$(zenity --entry \
        --title="Scriptorium — New World Creator" \
        --text="Enter the name for your new World or Novel Project:\n(e.g., 'Eldoria', 'Cyberpunk-2099', 'The-Last-Archon')" \
        --entry-text="My-New-World" || true)
fi

if [ -z "${WORLD_NAME}" ]; then
    if [ -t 0 ]; then
        read -rp "Enter World / Novel Name: " WORLD_NAME
    else
        echo "No world name provided (no argument, no GUI, no TTY). Aborting."
        exit 3
    fi
fi

# Sanitize: trim, spaces->dashes, whitelist alnum/dash/underscore, cap length (H2/D1: dash last so tr has no 9-_ range)
WORLD_NAME="$(printf '%s' "${WORLD_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"

if [ -z "${WORLD_NAME}" ]; then
    echo "Invalid world name after sanitization (use letters, numbers, - _). Aborting."
    exit 1
fi

if [ "${WORLD_NAME}" = "." ] || [ "${WORLD_NAME}" = ".." ]; then
    echo "Invalid world name. Aborting."
    exit 1
fi

TARGET_DIR="${WORLDS_BASE}/${WORLD_NAME}"

if [ -d "${TARGET_DIR}" ]; then
    if has_gui; then
        zenity --error --title="Folder Exists" --text="A world named '${WORLD_NAME}' already exists in ${WORLDS_BASE}."
    else
        echo "Error: Directory '${TARGET_DIR}' already exists."
    fi
    exit 1
fi

echo "Scaffolding Scriptorium World: ${TARGET_DIR} ..."

# 1. Create canonical directory structure
mkdir -p "${TARGET_DIR}/00-World-Bible/Characters"
mkdir -p "${TARGET_DIR}/00-World-Bible/Locations"
mkdir -p "${TARGET_DIR}/00-World-Bible/Factions"
mkdir -p "${TARGET_DIR}/00-World-Bible/Magic-Technology"
mkdir -p "${TARGET_DIR}/00-World-Bible/History"
mkdir -p "${TARGET_DIR}/00-World-Bible/Languages"
mkdir -p "${TARGET_DIR}/00-World-Bible/Templates"
mkdir -p "${TARGET_DIR}/01-Manuscript/Book-01/01_Act_I"
mkdir -p "${TARGET_DIR}/01-Manuscript/Book-01/02_Act_II"
mkdir -p "${TARGET_DIR}/01-Manuscript/Book-01/03_Act_III"
mkdir -p "${TARGET_DIR}/01-Manuscript/Outlines"
mkdir -p "${TARGET_DIR}/02-Maps"
mkdir -p "${TARGET_DIR}/03-Art"
mkdir -p "${TARGET_DIR}/04-Publishing"
mkdir -p "${TARGET_DIR}/05-Backups"

# 2. Copy World Bible Templates (H1: include dotfiles via /. idiom)
if [ -d "${PROJECT_ROOT}/templates/world-bible" ]; then
    cp -a "${PROJECT_ROOT}/templates/world-bible/." "${TARGET_DIR}/00-World-Bible/" 2>/dev/null || true
fi

# 3. Copy Manuscript Templates
if [ -d "${PROJECT_ROOT}/templates/manuscript" ]; then
    cp -a "${PROJECT_ROOT}/templates/manuscript/." "${TARGET_DIR}/01-Manuscript/" 2>/dev/null || true
fi

# 4. Copy Typst Book Template into 04-Publishing
if [ -d "${PROJECT_ROOT}/templates/typst" ]; then
    mkdir -p "${TARGET_DIR}/04-Publishing/typst-template"
    cp -a "${PROJECT_ROOT}/templates/typst/." "${TARGET_DIR}/04-Publishing/typst-template/" 2>/dev/null || true
fi

# 5. Create .gitignore and world manifest (D-02) for the world
cat << 'EOF' > "${TARGET_DIR}/.gitignore"
# Scriptorium World Git Ignore
.obsidian/workspace.json
.obsidian/cache
*.bak
*.tmp
*.log
.DS_Store
05-Backups/
EOF

cat << EOF > "${TARGET_DIR}/scriptorium.yaml"
# Scriptorium world manifest — read by export_book.sh (flat key: value)
title: "${WORLD_NAME}"
author: "Author Name"
# Add one volume per line under 01-Manuscript/ (Book-01, Book-02, ...);
# export_book.sh auto-discovers Book-* directories in natural order.
EOF

# 6. Initialize local Git repository for snapshots (M11: explicit identity check)
if command -v git &> /dev/null; then
    cd "${TARGET_DIR}"
    git init -q
    git add .
    if git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial Scriptorium scaffolding for world: ${WORLD_NAME}" 2>/dev/null; then
        :
    else
        echo "[!] Git commit skipped (check git identity). Files are staged; run 'git commit' manually."
    fi
    if ! git config user.name &>/dev/null || ! git config user.email &>/dev/null; then
        echo "[i] Tip: set git identity: git config user.name 'Your Name' && git config user.email 'you@example.com'"
    fi
fi

# 7. Notify completion
MSG="World '${WORLD_NAME}' successfully created at:\n${TARGET_DIR}\n\n• Open Obsidian -> 'Open folder as vault' -> Select '00-World-Bible'\n• Open novelWriter -> 'New Project' in '01-Manuscript' (import Book-01 Markdown; nwProject.nwx is a placeholder)\n• Use 'Save Snapshot' on your desktop to record your progress anytime!"

if has_gui; then
    zenity --info --title="World Created Successfully!" --text="${MSG}" --width=450
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi
