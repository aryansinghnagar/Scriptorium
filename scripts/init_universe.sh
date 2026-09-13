#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Universe Initializer & Manager
# Purpose: Scaffolds a narrative Universe ~/Universes/<UniverseName> to house
#          and track multiple interconnected worlds with a Universe-level Git repository.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
UNIVERSES_BASE="${HOME}/Universes"

has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

usage() {
    cat << 'USAGE'
Scriptorium Universe Manager — scaffold and manage narrative Universes.

Usage:
  init_universe.sh [UNIVERSE_NAME] [OPTIONS]

Options:
  -n, --name NAME    Universe name (same as positional argument)
  -l, --list         List all discovered Universes in ~/Universes
  -h, --help         Show this help and exit

Exit codes:
  0  universe created or listed successfully
  1  error (invalid name, universe already exists)
  3  user abort
USAGE
}

LIST_MODE=0
UNIVERSE_NAME_CLI=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -n|--name)
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 1; }
            UNIVERSE_NAME_CLI="$2"; shift 2 ;;
        -l|--list)
            LIST_MODE=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        --)
            shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 1 ;;
        *)
            POSITIONAL+=("$1"); shift ;;
    esac
done

mkdir -p "${UNIVERSES_BASE}"

if [ "${LIST_MODE}" -eq 1 ]; then
    echo "Discovered Universes in ${UNIVERSES_BASE}:"
    COUNT=0
    while IFS= read -r -d '' d; do
        UNAME="$(basename "$d")"
        WORLDS_COUNT=$(find "${d}/Worlds" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l || echo 0)
        echo "  • ${UNAME} (${WORLDS_COUNT} worlds) -> ${d}"
        COUNT=$((COUNT + 1))
    done < <(find "${UNIVERSES_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    if [ "${COUNT}" -eq 0 ]; then
        echo "  (No Universes found yet. Create one with: scriptorium universe <name>)"
    fi
    exit 0
fi

UNIVERSE_NAME="${UNIVERSE_NAME_CLI:-${POSITIONAL[0]:-}}"

if [ -z "${UNIVERSE_NAME}" ]; then
    if has_gui; then
        UNIVERSE_NAME=$(zenity --entry \
            --title="Scriptorium — New Universe Creator" \
            --text="Enter the name for your narrative Universe:\n(e.g., 'Cosmere', 'Solaris-Prime', 'High-Fantasy-Multiverse')" \
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

# Sanitize name
UNIVERSE_NAME="$(printf '%s' "${UNIVERSE_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"

if [ -z "${UNIVERSE_NAME}" ] || [ "${UNIVERSE_NAME}" = "." ] || [ "${UNIVERSE_NAME}" = ".." ]; then
    echo "Error: Invalid universe name after sanitization." >&2
    exit 1
fi

TARGET_UNIVERSE_DIR="${UNIVERSES_BASE}/${UNIVERSE_NAME}"

if [ -d "${TARGET_UNIVERSE_DIR}" ]; then
    echo "Universe '${UNIVERSE_NAME}' already exists at: ${TARGET_UNIVERSE_DIR}"
    exit 0
fi

echo "Scaffolding Narrative Universe: ${UNIVERSE_NAME} ..."

mkdir -p "${TARGET_UNIVERSE_DIR}/Worlds"

# Create universe manifest & index note
cat << EOF > "${TARGET_UNIVERSE_DIR}/universe.yaml"
# Scriptorium Universe Manifest
name: "${UNIVERSE_NAME}"
created_at: "$(date +%Y-%m-%d)"
description: "Narrative Universe housing interconnected worlds and lore."
EOF

cat << EOF > "${TARGET_UNIVERSE_DIR}/Universe-Index.md"
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
All world bibles and manuscript repositories belonging to this universe reside in \`Worlds/\`:
- Open individual world folders under \`Worlds/<WorldName>/00-World-Bible\` as separate Obsidian vaults, or open this root \`${UNIVERSE_NAME}\` directory as an overarching cosmic vault.
EOF

# Create .gitignore for universe root
cat << 'EOF' > "${TARGET_UNIVERSE_DIR}/.gitignore"
*.bak
*.tmp
*.log
.DS_Store
EOF

# Initialize Universe-level Git repository
if command -v git &> /dev/null; then
    (
        cd "${TARGET_UNIVERSE_DIR}"
        git init -q
        git add .
        git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial Scriptorium universe repository: ${UNIVERSE_NAME}" 2>/dev/null || true
    )
fi

echo "[✓] Universe '${UNIVERSE_NAME}' created successfully at:"
echo "    ${TARGET_UNIVERSE_DIR}"

MSG="Universe '${UNIVERSE_NAME}' created successfully!\n\nLocation:\n${TARGET_UNIVERSE_DIR}\n\nYou can now scaffold worlds inside this universe."

if has_gui; then
    zenity --info --title="Universe Created" --text="${MSG}" --width=450
fi

exit 0
