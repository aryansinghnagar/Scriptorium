#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum World Initializer (Pure World Lore Vault Architecture)
# Purpose: Atomically creates a brand new World Lore Vault within a Universe:
#          ~/Universes/<UniverseName>/<WorldName>
#          Direct Obsidian vault with pre-configured plugin suite,
#          structured world taxonomy, world.yaml manifest, and Git repository.
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
Ars Arcanum World Initializer — atomically scaffold a World Lore Vault in a Universe.

Usage:
  init_world.sh [WORLD_NAME] [OPTIONS]

Options:
  -n, --name NAME        World name (same as positional argument)
  -u, --universe NAME    Universe name (default: Default-Universe or interactive selection)
  -l, --list             List discovered World Lore Vaults
  --legacy-worlds-dir    Scaffold directly in ~/Worlds/ instead of ~/Universes/<Universe>/
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
LIST_MODE=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -n|--name)
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 2; }
            WORLD_NAME_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_NAME_CLI="$2"; shift 2 ;;
        -l|--list)
            LIST_MODE=1; shift ;;
        --legacy-worlds-dir)
            USE_LEGACY_DIR=1; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

if [ "${LIST_MODE}" -eq 1 ]; then
    echo "Discovered World Lore Vaults:"
    discover_worlds WORLDS
    if [ ${#WORLDS[@]} -eq 0 ]; then
        echo "  (No World Lore Vaults found yet. Create one with: arcanum world <name>)"
    else
        for w in "${WORLDS[@]}"; do
            echo "  • $(basename "$w") -> $w"
        done
    fi
    exit 0
fi

WORLD_NAME="${WORLD_NAME_CLI:-${POSITIONAL[0]:-}}"
UNIVERSE_NAME="${UNIVERSE_NAME_CLI:-}"

mkdir -p "${UNIVERSES_BASE}"

# 1. Resolve Universe Name (if not using legacy dir)
if [ "${USE_LEGACY_DIR}" -eq 0 ]; then
    if [ -z "${UNIVERSE_NAME}" ]; then
        EXISTING_UNIS=()
        while IFS= read -r -d '' d; do
            EXISTING_UNIS+=("$(basename "$d")")
        done < <(find "${UNIVERSES_BASE}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null)

        if has_gui; then
            if [ ${#EXISTING_UNIS[@]} -gt 0 ]; then
                CHOICES=()
                for u in "${EXISTING_UNIS[@]}"; do
                    CHOICES+=("$u" "Existing Universe")
                done
                CHOICES+=("+ Create New Universe" "New Universe Container")
                SELECTED_UNI=$(zenity --list --title="Ars Arcanum — Select Universe" \
                    --text="Which Universe does this world lore vault belong to?" \
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
                UNIVERSE_NAME=$(zenity --entry --title="Ars Arcanum — Universe Context" \
                    --text="Enter the Universe for this world lore vault (e.g., 'Cosmere', 'Solaris-Prime'):" \
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
    WORLDS_BASE="${UNIVERSE_DIR}"

    # Initialize Universe if new
    if [ ! -d "${UNIVERSE_DIR}" ]; then
        mkdir -p "${UNIVERSE_DIR}"
        cat << EOF > "${UNIVERSE_DIR}/universe.yaml"
name: "${UNIVERSE_NAME}"
created_at: "$(date +%Y-%m-%d)"
description: "Narrative Universe housing interconnected worlds."
EOF
        cat << EOF > "${UNIVERSE_DIR}/Universe-Index.md"
---
type: universe_index
universe: "${UNIVERSE_NAME}"
created: "$(date +%Y-%m-%d)"
tags:
  - meta/universe
---

# 🌌 ${UNIVERSE_NAME} — Narrative Universe Hub

**Universe**: \`${UNIVERSE_NAME}\`  
**Created**: $(date +%Y-%m-%d)  

This central index coordinates all interconnected worlds, overarching continuity, shared celestial mechanics, and cross-world lore across the **${UNIVERSE_NAME}** cosmos.

---

## 🪐 Worlds in this Universe
All world lore bibles belonging to this universe reside directly in this directory (e.g., \`${UNIVERSE_NAME}/<WorldName>/\`). Open any individual world folder as a dedicated Obsidian vault, or open this root \`${UNIVERSE_NAME}\` directory as an overarching cosmic vault.
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
                git_commit_safe "Initial universe repository: ${UNIVERSE_NAME}" || true
            )
        fi
    fi
else
    WORLDS_BASE="${LEGACY_WORLDS_BASE}"
    mkdir -p "${LEGACY_WORLDS_BASE}"
    UNIVERSE_NAME="Standalone"
fi

# 2. Resolve World Name
if [ -z "${WORLD_NAME}" ]; then
    if has_gui; then
        WORLD_NAME=$(zenity --entry \
            --title="Ars Arcanum — New World Lore Creator" \
            --text="Enter the name for your new World Lore Vault:\n(e.g., 'Eldoria', 'Cyberpunk-2099', 'The-Last-Archon')" \
            --entry-text="My-New-World" || true)
    fi
fi

if [ -z "${WORLD_NAME}" ]; then
    if [ -t 0 ]; then
        read -rp "Enter World Name: " WORLD_NAME
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

echo "Scaffolding Ars Arcanum World Lore Vault: ${WORLD_NAME} [Universe: ${UNIVERSE_NAME}] ..."

# 3. Transactional Staging Architecture (REL-01)
SUCCESS=0
STAGING_DIR="$(mktemp -d)"

cleanup() {
    if [ "${SUCCESS}" -eq 0 ] && [ -n "${STAGING_DIR:-}" ] && [ -d "${STAGING_DIR}" ]; then
        rm -rf "${STAGING_DIR}"
    fi
}
trap cleanup EXIT INT TERM

# Create canonical taxonomy directories in staging
mkdir -p "${STAGING_DIR}/Characters"
mkdir -p "${STAGING_DIR}/Locations"
mkdir -p "${STAGING_DIR}/Factions"
mkdir -p "${STAGING_DIR}/Economies"
mkdir -p "${STAGING_DIR}/Magic-Technology"
mkdir -p "${STAGING_DIR}/Bestiary"
mkdir -p "${STAGING_DIR}/Artifacts"
mkdir -p "${STAGING_DIR}/Cosmology/Prophecies"
mkdir -p "${STAGING_DIR}/History"
mkdir -p "${STAGING_DIR}/Languages"
mkdir -p "${STAGING_DIR}/Templates/fileClasses"

# Copy World Bible Templates directly into staging root (direct Obsidian Vault)
if [ -d "${PROJECT_ROOT}/templates/world-bible" ]; then
    cp -a "${PROJECT_ROOT}/templates/world-bible/." "${STAGING_DIR}/"
fi

# Create .gitignore and world manifest (world.yaml & arcanum.yaml for compatibility)
cat << 'EOF' > "${STAGING_DIR}/.gitignore"
# Ars Arcanum World Git Ignore
.obsidian/workspace.json
.obsidian/cache
*.bak
*.tmp
*.log
.DS_Store
Backups/
05-Backups/
EOF

cat << EOF > "${STAGING_DIR}/world.yaml"
# Ars Arcanum World Lore Vault Manifest
schema_version: "1.0"
name: "${WORLD_NAME}"
universe: "${UNIVERSE_NAME}"
created_at: "$(date +%Y-%m-%d)"
description: "World Lore Vault for ${WORLD_NAME}"
EOF

cat << EOF > "${STAGING_DIR}/arcanum.yaml"
# Ars Arcanum world manifest
title: "${WORLD_NAME}"
author: "Author Name"
universe: "${UNIVERSE_NAME}"
EOF

# Run Validation Checks on Staged Structure
[ -d "${STAGING_DIR}/Characters" ] || { echo "Validation error: Characters directory missing" >&2; exit 1; }
[ -d "${STAGING_DIR}/Bestiary" ] || { echo "Validation error: Bestiary directory missing" >&2; exit 1; }
[ -d "${STAGING_DIR}/Locations" ] || { echo "Validation error: Locations directory missing" >&2; exit 1; }
[ -f "${STAGING_DIR}/world.yaml" ] || { echo "Validation error: world.yaml manifest missing" >&2; exit 1; }

# 4. Git Repository Initialization (REL-04: honest history reporting)
GIT_HISTORY="ok"
if command -v git &> /dev/null; then
    if ! (
        cd "${STAGING_DIR}"
        git init -q
        git config advice.addEmbeddedRepo false
        git -c advice.addEmbeddedRepo=false add . 2>/dev/null
        git_commit_safe "Initial Ars Arcanum world lore repository: ${WORLD_NAME} [Universe: ${UNIVERSE_NAME}]"
    ); then
        echo "[!] Warning: world initial Git commit failed. World created without initial history." >&2
        echo "    Repair with: git -C \"\$HOME/Universes/<Universe>/${WORLD_NAME}\" commit -m 'Initial commit'" >&2
        GIT_HISTORY="failed"
    fi
else
    GIT_HISTORY="missing"
fi

# 5. Atomic Move into Destination
mkdir -p "${WORLDS_BASE}"
mv "${STAGING_DIR}" "${TARGET_DIR}"
SUCCESS=1

# 6. Track new world in Universe Git repo if applicable
if [ "${USE_LEGACY_DIR}" -eq 0 ] && [ -d "${UNIVERSE_DIR}/.git" ] && command -v git &> /dev/null; then
    if ! (
        cd "${UNIVERSE_DIR}"
        git add "${WORLD_NAME}" 2>/dev/null
        git_commit_safe "Add world '${WORLD_NAME}' to universe '${UNIVERSE_NAME}'"
    ); then
        echo "[!] Warning: universe tracking commit failed for '${WORLD_NAME}'. World itself is intact." >&2
        [ "${GIT_HISTORY}" = "ok" ] && GIT_HISTORY="failed"
    fi
fi

# 7. Notify completion (REL-04)
if [ "${GIT_HISTORY:-ok}" = "ok" ]; then
    GIT_LINE="• Discrete Git version control initialized!"
elif [ "${GIT_HISTORY}" = "missing" ]; then
    GIT_LINE="• Created WITHOUT version history (git not installed)."
else
    GIT_LINE="• Created WITHOUT initial commit history (see warnings above for repair commands)."
fi
MSG="World Lore Vault '${WORLD_NAME}' successfully created in Universe '${UNIVERSE_NAME}'!\n\nLocation:\n${TARGET_DIR}\n\n• Open Obsidian -> 'Open folder as vault' -> Select '${WORLD_NAME}'\n• Out-of-the-box plugins enabled: Storyline, Longform, Dataview, Metadata Menu, Calendarium, Storyteller Suite, Novel Word Count, Obsidian Git\n${GIT_LINE}"

if has_gui; then
    zenity --info --title="World Lore Vault Created" --text="${MSG}" --width=480
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit 0
