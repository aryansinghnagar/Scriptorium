#!/usr/bin/env bash
# ==============================================================================
# Scriptorium World Initializer (Multi-Tier Universe & Git Architecture)
# Purpose: Atomically creates a brand new world folder structure within a Universe:
#          ~/Universes/<UniverseName>/Worlds/<WorldName>
#          with Obsidian World Bible (pre-configured plugin suite), valid novelWriter
#          manuscript scaffolding, discrete Manuscript Git repository, World Git
#          repository, and Universe tracking.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
UNIVERSES_BASE="${HOME}/Universes"
LEGACY_WORLDS_BASE="${HOME}/Worlds"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Scriptorium World Initializer — atomically scaffold a world within a Universe.

Usage:
  init_world.sh [WORLD_NAME] [OPTIONS]

Options:
  -n, --name NAME        World name (same as positional argument)
  -u, --universe NAME    Universe name (default: Default-Universe or interactive selection)
  --legacy-worlds-dir    Scaffold directly in ~/Worlds/ instead of ~/Universes/<Universe>/Worlds/
  -h, --help             Show this help and exit

Exit codes:
  0  world created successfully
  1  error (invalid name, world already exists, staging failure)
  3  user abort (no name provided)

Names are sanitized to [A-Za-z0-9_-] (max 64 chars); spaces become dashes.
USAGE
}

WORLD_NAME_CLI=""
UNIVERSE_NAME_CLI=""
USE_LEGACY_DIR=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -n|--name)
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 1; }
            WORLD_NAME_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 1; }
            UNIVERSE_NAME_CLI="$2"; shift 2 ;;
        --legacy-worlds-dir)
            USE_LEGACY_DIR=1; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

WORLD_NAME="${WORLD_NAME_CLI:-${POSITIONAL[0]:-}}"
UNIVERSE_NAME="${UNIVERSE_NAME_CLI:-}"

mkdir -p "${UNIVERSES_BASE}"
mkdir -p "${LEGACY_WORLDS_BASE}"

# 1. Resolve Universe Name (if not using legacy dir)
if [ "${USE_LEGACY_DIR}" -eq 0 ]; then
    if [ -z "${UNIVERSE_NAME}" ]; then
        EXISTING_UNIS=()
        while IFS= read -r -d '' d; do
            EXISTING_UNIS+=("$(basename "$d")")
        done < <(find "${UNIVERSES_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)

        if has_gui; then
            if [ ${#EXISTING_UNIS[@]} -gt 0 ]; then
                CHOICES=()
                for u in "${EXISTING_UNIS[@]}"; do
                    CHOICES+=("$u" "Existing Universe")
                done
                CHOICES+=("+ Create New Universe" "New Universe Container")
                SELECTED_UNI=$(zenity --list --title="Scriptorium — Select Universe" \
                    --text="Which Universe does this world belong to?" \
                    --column="Universe" --column="Type" \
                    --hide-column=2 \
                    --width=400 --height=300 \
                    "${CHOICES[@]}" || true)
                if [ "$SELECTED_UNI" = "+ Create New Universe" ] || [ -z "$SELECTED_UNI" ]; then
                    UNIVERSE_NAME=$(zenity --entry --title="New Universe" --text="Enter name for the new Universe:" --entry-text="Default-Universe" || true)
                else
                    UNIVERSE_NAME="$SELECTED_UNI"
                fi
            else
                UNIVERSE_NAME=$(zenity --entry --title="Scriptorium — Universe Context" \
                    --text="Enter the Universe for this world (e.g., 'Cosmere', 'Solaris-Prime'):" \
                    --entry-text="Default-Universe" || true)
            fi
        fi

        if [ -z "${UNIVERSE_NAME}" ]; then
            if [ -t 0 ]; then
                read -rp "Enter Universe Name (default: Default-Universe): " UNIVERSE_NAME
                [ -z "${UNIVERSE_NAME}" ] && UNIVERSE_NAME="Default-Universe"
            else
                UNIVERSE_NAME="Default-Universe"
            fi
        fi
    fi

    # Sanitize universe name
    UNIVERSE_NAME="$(printf '%s' "${UNIVERSE_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"
    [ -z "${UNIVERSE_NAME}" ] && UNIVERSE_NAME="Default-Universe"

    UNIVERSE_DIR="${UNIVERSES_BASE}/${UNIVERSE_NAME}"
    WORLDS_BASE="${UNIVERSE_DIR}/Worlds"

    # Initialize Universe if new
    if [ ! -d "${UNIVERSE_DIR}" ]; then
        mkdir -p "${WORLDS_BASE}"
        cat << EOF > "${UNIVERSE_DIR}/universe.yaml"
name: "${UNIVERSE_NAME}"
created_at: "$(date +%Y-%m-%d)"
description: "Narrative Universe housing interconnected worlds."
EOF
        cat << 'EOF' > "${UNIVERSE_DIR}/.gitignore"
*.bak
*.tmp
*.log
.DS_Store
EOF
        if command -v git &> /dev/null; then
            (
                cd "${UNIVERSE_DIR}"
                git init -q
                git add .
                git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial universe repository: ${UNIVERSE_NAME}" 2>/dev/null || true
            )
        fi
    fi
else
    WORLDS_BASE="${LEGACY_WORLDS_BASE}"
    UNIVERSE_NAME="Standalone"
fi

# 2. Resolve World Name
if [ -z "${WORLD_NAME}" ]; then
    if has_gui; then
        WORLD_NAME=$(zenity --entry \
            --title="Scriptorium — New World Creator" \
            --text="Enter the name for your new World or Novel Project:\n(e.g., 'Eldoria', 'Cyberpunk-2099', 'The-Last-Archon')" \
            --entry-text="My-New-World" || true)
    fi
fi

if [ -z "${WORLD_NAME}" ]; then
    if [ -t 0 ]; then
        read -rp "Enter World / Novel Name: " WORLD_NAME
    else
        echo "No world name provided (no argument, no GUI, no TTY). Aborting." >&2
        exit 3
    fi
fi

# Sanitize world name
WORLD_NAME="$(printf '%s' "${WORLD_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"

if [ -z "${WORLD_NAME}" ] || [ "${WORLD_NAME}" = "." ] || [ "${WORLD_NAME}" = ".." ]; then
    echo "Invalid world name after sanitization (use letters, numbers, - _). Aborting." >&2
    exit 1
fi

TARGET_DIR="${WORLDS_BASE}/${WORLD_NAME}"

if [ -d "${TARGET_DIR}" ]; then
    if has_gui; then
        zenity --error --title="Folder Exists" --text="A world named '${WORLD_NAME}' already exists in ${WORLDS_BASE}."
    else
        echo "Error: Directory '${TARGET_DIR}' already exists." >&2
    fi
    exit 1
fi

echo "Scaffolding Scriptorium World: ${WORLD_NAME} [Universe: ${UNIVERSE_NAME}] ..."

# 3. Transactional Staging Architecture (REL-01)
SUCCESS=0
STAGING_DIR="$(mktemp -d)"

cleanup() {
    if [ "${SUCCESS}" -eq 0 ] && [ -n "${STAGING_DIR:-}" ] && [ -d "${STAGING_DIR}" ]; then
        rm -rf "${STAGING_DIR}"
    fi
}
trap cleanup EXIT INT TERM

# Create canonical directory structure in staging
mkdir -p "${STAGING_DIR}/00-World-Bible/Characters"
mkdir -p "${STAGING_DIR}/00-World-Bible/Locations"
mkdir -p "${STAGING_DIR}/00-World-Bible/Factions"
mkdir -p "${STAGING_DIR}/00-World-Bible/Magic-Technology"
mkdir -p "${STAGING_DIR}/00-World-Bible/Bestiary"
mkdir -p "${STAGING_DIR}/00-World-Bible/Artifacts"
mkdir -p "${STAGING_DIR}/00-World-Bible/Cosmology"
mkdir -p "${STAGING_DIR}/00-World-Bible/History"
mkdir -p "${STAGING_DIR}/00-World-Bible/Languages"
mkdir -p "${STAGING_DIR}/00-World-Bible/Templates/fileClasses"
mkdir -p "${STAGING_DIR}/01-Manuscript/Book-01/01_Act_I"
mkdir -p "${STAGING_DIR}/01-Manuscript/Book-01/02_Act_II"
mkdir -p "${STAGING_DIR}/01-Manuscript/Book-01/03_Act_III"
mkdir -p "${STAGING_DIR}/01-Manuscript/Outlines"
mkdir -p "${STAGING_DIR}/02-Maps"
mkdir -p "${STAGING_DIR}/03-Art"
mkdir -p "${STAGING_DIR}/04-Publishing"
mkdir -p "${STAGING_DIR}/05-Backups"

# Copy World Bible Templates
if [ -d "${PROJECT_ROOT}/templates/world-bible" ]; then
    cp -a "${PROJECT_ROOT}/templates/world-bible/." "${STAGING_DIR}/00-World-Bible/"
fi

# Copy Manuscript Templates
if [ -d "${PROJECT_ROOT}/templates/manuscript" ]; then
    cp -a "${PROJECT_ROOT}/templates/manuscript/." "${STAGING_DIR}/01-Manuscript/"
fi

# Generate Valid novelWriter Project Scaffolding (UX-01)
cat << EOF > "${STAGING_DIR}/01-Manuscript/nwProject.nwx"
<?xml version="1.0" encoding="UTF-8"?>
<novelWriterXML fileVersion="1.5" appVersion="2.0">
  <project>
    <title>${WORLD_NAME}</title>
    <author>Author Name</author>
    <saveCount>1</saveCount>
    <autoCount>0</autoCount>
    <editTime>0</editTime>
  </project>
  <settings>
    <spellChecking>true</spellChecking>
    <autoSave>true</autoSave>
  </settings>
  <content>
    <item id="root" parent="None" root="None" type="Root" handle="root">
      <name>Novel Root</name>
    </item>
  </content>
</novelWriterXML>
EOF

# Copy Typst Book Template into 04-Publishing
if [ -d "${PROJECT_ROOT}/templates/typst" ]; then
    mkdir -p "${STAGING_DIR}/04-Publishing/typst-template"
    cp -a "${PROJECT_ROOT}/templates/typst/." "${STAGING_DIR}/04-Publishing/typst-template/"
fi

# Create .gitignore and world manifest (D-02)
cat << 'EOF' > "${STAGING_DIR}/.gitignore"
# Scriptorium World Git Ignore
.obsidian/workspace.json
.obsidian/cache
*.bak
*.tmp
*.log
.DS_Store
05-Backups/
# F-09: compiled artifacts are outputs, not source; committing them bloats
# every snapshot with multi-megabyte binaries on each re-export.
04-Publishing/
EOF

cat << EOF > "${STAGING_DIR}/scriptorium.yaml"
# Scriptorium world manifest — read by export_book.sh (flat key: value)
title: "${WORLD_NAME}"
author: "Author Name"
universe: "${UNIVERSE_NAME}"
# Add one volume per line under 01-Manuscript/ (Book-01, Book-02, ...);
# export_book.sh auto-discovers Book-* directories in natural order.
EOF

# Run Validation Checks on Staged Structure
[ -d "${STAGING_DIR}/00-World-Bible/Characters" ] || { echo "Validation error: World Bible missing" >&2; exit 1; }
[ -d "${STAGING_DIR}/00-World-Bible/Bestiary" ] || { echo "Validation error: Bestiary directory missing" >&2; exit 1; }
[ -d "${STAGING_DIR}/01-Manuscript/Book-01" ] || { echo "Validation error: Manuscript directory missing" >&2; exit 1; }
[ -f "${STAGING_DIR}/scriptorium.yaml" ] || { echo "Validation error: scriptorium.yaml manifest missing" >&2; exit 1; }

# 4. Multi-Tier Git Repository Initialization
if command -v git &> /dev/null; then
    # 4a. Initialize discrete Manuscript Git repository for Book-01
    (
        cd "${STAGING_DIR}/01-Manuscript/Book-01"
        git init -q
        git add .
        git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial manuscript drafting repository for Book-01 in ${WORLD_NAME}" 2>/dev/null || true
    )

    # 4b. Initialize World Git repository
    (
        cd "${STAGING_DIR}"
        git init -q
        git config advice.addEmbeddedRepo false
        git -c advice.addEmbeddedRepo=false add . 2>/dev/null || true
        git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial Scriptorium world repository: ${WORLD_NAME} [Universe: ${UNIVERSE_NAME}]" 2>/dev/null || true
    )
fi

# 5. Atomic Move into Destination
mkdir -p "${WORLDS_BASE}"
mv "${STAGING_DIR}" "${TARGET_DIR}"
SUCCESS=1

# 6. Track new world in Universe Git repo if applicable
if [ "${USE_LEGACY_DIR}" -eq 0 ] && [ -d "${UNIVERSE_DIR}/.git" ] && command -v git &> /dev/null; then
    (
        cd "${UNIVERSE_DIR}"
        git add "Worlds/${WORLD_NAME}" 2>/dev/null || true
        git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Add world '${WORLD_NAME}' to universe '${UNIVERSE_NAME}'" 2>/dev/null || true
    )
fi

# 7. Notify completion
MSG="World '${WORLD_NAME}' successfully created in Universe '${UNIVERSE_NAME}'!\n\nLocation:\n${TARGET_DIR}\n\n• Open Obsidian -> 'Open folder as vault' -> Select '00-World-Bible'\n• Out-of-the-box plugins enabled: Storyline, Longform, Dataview, Metadata Menu, Calendarium, Storyteller Suite, Novel Word Count, Obsidian Git\n• Open novelWriter -> Open project in '01-Manuscript/nwProject.nwx'\n• Discrete Git version control initialized for Universe, World, and Manuscript!"

if has_gui; then
    zenity --info --title="World Created Successfully!" --text="${MSG}" --width=480
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi
