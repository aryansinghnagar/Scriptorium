#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Universe Initializer & Manager
# Purpose: Scaffolds a narrative Universe ~/Universes/<UniverseName> to house
#          and track multiple interconnected worlds with a Universe-level Git repository.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Universe Manager — scaffold and manage narrative Universes.

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
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 2; }
            UNIVERSE_NAME_CLI="$2"; shift 2 ;;
        -l|--list)
            LIST_MODE=1; shift ;;
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

mkdir -p "${UNIVERSES_BASE}"

if [ "${LIST_MODE}" -eq 1 ]; then
    echo "Discovered Universes in ${UNIVERSES_BASE}:"
    COUNT=0
    while IFS= read -r -d '' d; do
        UNAME="$(basename "$d")"
        WORLDS_COUNT=$(find "${d}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' ! -name '.git' 2>/dev/null | wc -l || echo 0)
        echo "  • ${UNAME} (${WORLDS_COUNT} worlds) -> ${d}"
        COUNT=$((COUNT + 1))
    done < <(find "${UNIVERSES_BASE}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -print0 2>/dev/null)
    if [ "${COUNT}" -eq 0 ]; then
        echo "  (No Universes found yet. Create one with: arcanum universe <name>)"
    fi
    exit 0
fi

UNIVERSE_NAME="${UNIVERSE_NAME_CLI:-${POSITIONAL[0]:-}}"

if [ -z "${UNIVERSE_NAME}" ]; then
    if has_gui; then
        UNIVERSE_NAME=$(zenity --entry \
            --title="Ars Arcanum — New Universe Creator" \
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

mkdir -p "${TARGET_UNIVERSE_DIR}"

# Create universe manifest & index note
cat << EOF > "${TARGET_UNIVERSE_DIR}/universe.yaml"
# Ars Arcanum Universe Manifest
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
All world lore bibles belonging to this universe reside directly in this directory (e.g., \`${UNIVERSE_NAME}/<WorldName>/\`). Open any individual world folder as a dedicated Obsidian vault, or open this root \`${UNIVERSE_NAME}\` directory as an overarching cosmic vault.
EOF

# Create .gitignore for universe root
cat << 'EOF' > "${TARGET_UNIVERSE_DIR}/.gitignore"
*.bak
*.tmp
*.log
.DS_Store
EOF

# Initialize Universe-level Git repository (REL-04: honest history reporting)
GIT_HISTORY="ok"
if command -v git &> /dev/null; then
    if ! (
        cd "${TARGET_UNIVERSE_DIR}"
        git init -q
        git add .
        git -c user.name="Ars Arcanum Maintainers" -c user.email="maintainers@arsarcanum.local" commit -q -m "Initial Ars Arcanum universe repository: ${UNIVERSE_NAME}" 2>/dev/null
    ); then
        echo "[!] Warning: universe initial Git commit failed. Universe created without initial history." >&2
        echo "    Repair with: git -C '${TARGET_UNIVERSE_DIR}' commit -m 'Initial commit'" >&2
        GIT_HISTORY="failed"
    fi
else
    GIT_HISTORY="missing"
fi

echo "[✓] Universe '${UNIVERSE_NAME}' created successfully at:"
echo "    ${TARGET_UNIVERSE_DIR}"

if [ "${GIT_HISTORY}" = "ok" ]; then
    GIT_LINE="Git version control initialized."
elif [ "${GIT_HISTORY}" = "missing" ]; then
    GIT_LINE="Created WITHOUT version history (git not installed)."
else
    GIT_LINE="Created WITHOUT initial commit history (see warning above)."
fi
MSG="Universe '${UNIVERSE_NAME}' created successfully!\n\nLocation:\n${TARGET_UNIVERSE_DIR}\n\nYou can now scaffold worlds inside this universe.\n${GIT_LINE}"

if has_gui; then
    zenity --info --title="Universe Created" --text="${MSG}" --width=450
fi

exit 0
