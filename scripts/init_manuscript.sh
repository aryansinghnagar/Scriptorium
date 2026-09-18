#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Manuscript Project Initializer
# Purpose: Atomically creates a brand new Manuscript Project in ~/Manuscripts/<ManuscriptName>
#          with discrete Volume Git repositories, 3-Act structure, Outlines,
#          novelWriter project scaffolding, Typst export templates, and linking
#          to an optional World Lore Vault via manuscript.yaml.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MANUSCRIPTS_BASE="${HOME}/Manuscripts"

# Shared world discovery, resolution, and GUI helpers
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Manuscript Initializer — atomically scaffold a Manuscript Project.

Usage:
  init_manuscript.sh [MANUSCRIPT_NAME] [OPTIONS]

Options:
  -n, --name NAME        Manuscript project name (same as positional argument)
  -u, --universe NAME    Universe name to link (optional)
  -w, --world NAME       World Lore Vault to link (optional)
  -a, --author NAME      Author name (default: "Author Name")
  -l, --list             List discovered Manuscript projects
  -h, --help             Show this help and exit

Exit codes:
  0  manuscript created successfully
  1  error (invalid name, manuscript already exists, staging failure)
  3  user abort (no name provided)

Names are sanitized to [A-Za-z0-9_-] (max 64 chars); spaces become dashes.
USAGE
}

MANUSCRIPT_NAME_CLI=""
UNIVERSE_NAME_CLI=""
WORLD_NAME_CLI=""
AUTHOR_NAME_CLI=""
LIST_MODE=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -n|--name)
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 2; }
            MANUSCRIPT_NAME_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_NAME_CLI="$2"; shift 2 ;;
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 2; }
            WORLD_NAME_CLI="$2"; shift 2 ;;
        -a|--author)
            [ $# -ge 2 ] || { echo "Error: --author requires a value." >&2; exit 2; }
            AUTHOR_NAME_CLI="$2"; shift 2 ;;
        -l|--list)
            LIST_MODE=1; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

if [ "${LIST_MODE}" -eq 1 ]; then
    echo "Discovered Manuscript Projects in ${MANUSCRIPTS_BASE}:"
    discover_manuscripts MANUSCRIPTS
    if [ ${#MANUSCRIPTS[@]} -eq 0 ]; then
        echo "  (No Manuscript projects found yet. Create one with: arcanum manuscript <name>)"
    else
        for m in "${MANUSCRIPTS[@]}"; do
            echo "  • $(basename "$m") -> $m"
        done
    fi
    exit 0
fi

MANUSCRIPT_NAME="${MANUSCRIPT_NAME_CLI:-${POSITIONAL[0]:-}}"
UNIVERSE_NAME="${UNIVERSE_NAME_CLI:-}"
WORLD_NAME="${WORLD_NAME_CLI:-}"
AUTHOR_NAME="${AUTHOR_NAME_CLI:-Author Name}"

mkdir -p "${MANUSCRIPTS_BASE}"

# 1. Resolve Manuscript Name
if [ -z "${MANUSCRIPT_NAME}" ]; then
    if has_gui; then
        MANUSCRIPT_NAME=$(zenity --entry \
            --title="Ars Arcanum — New Manuscript Creator" \
            --text="Enter the title for your new Manuscript Project:\n(e.g., 'Chronicles-of-Eldoria', 'The-Last-Archon')" \
            --entry-text="My-New-Novel" || true)
    fi
fi

if [ -z "${MANUSCRIPT_NAME}" ]; then
    if [ -t 0 ]; then
        read -rp "Enter Manuscript Name: " MANUSCRIPT_NAME
    else
        echo "No manuscript name provided (no argument, no GUI, no TTY). Aborting." >&2
        exit 3
    fi
fi

# Sanitize manuscript name
MANUSCRIPT_NAME="$(printf '%s' "${MANUSCRIPT_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"

if [ -z "${MANUSCRIPT_NAME}" ] || [ "${MANUSCRIPT_NAME}" = "." ] || [ "${MANUSCRIPT_NAME}" = ".." ]; then
    echo "Invalid manuscript name after sanitization (use letters, numbers, - _). Aborting." >&2
    exit 1
fi

TARGET_DIR="${MANUSCRIPTS_BASE}/${MANUSCRIPT_NAME}"

if [ -d "${TARGET_DIR}" ]; then
    if has_gui; then
        zenity --error --title="Folder Exists" --text="A manuscript named '${MANUSCRIPT_NAME}' already exists in ${MANUSCRIPTS_BASE}."
    else
        echo "Error: Directory '${TARGET_DIR}' already exists." >&2
    fi
    exit 1
fi

echo "Scaffolding Ars Arcanum Manuscript Project: ${MANUSCRIPT_NAME} ..."

# 2. Transactional Staging Architecture
SUCCESS=0
STAGING_DIR="$(mktemp -d)"

cleanup() {
    if [ "${SUCCESS}" -eq 0 ] && [ -n "${STAGING_DIR:-}" ] && [ -d "${STAGING_DIR}" ]; then
        rm -rf "${STAGING_DIR}"
    fi
}
trap cleanup EXIT INT TERM

# Create canonical structure in staging
mkdir -p "${STAGING_DIR}/Book-01/01_Act_I"
mkdir -p "${STAGING_DIR}/Book-01/02_Act_II"
mkdir -p "${STAGING_DIR}/Book-01/03_Act_III"
mkdir -p "${STAGING_DIR}/Outlines"
mkdir -p "${STAGING_DIR}/Exports"
mkdir -p "${STAGING_DIR}/Backups"

# Copy Manuscript Templates
if [ -d "${PROJECT_ROOT}/templates/manuscript" ]; then
    cp -a "${PROJECT_ROOT}/templates/manuscript/." "${STAGING_DIR}/"
fi

# DAT-02: XML-escape free-text fields before templating so ordinary input
# like `A & B`, `<Draft>`, or `"Quotes"` cannot produce malformed XML.
# NOTE: `\&` in the replacement is mandatory — in Bash pattern
# substitution an unescaped `&` expands to the matched text (like sed),
# which would corrupt every entity after the first (`&lt;` -> `<lt;`).
xml_escape() {
    local s="${1:-}"
    s="${s//&/\&amp;}"
    s="${s//</\&lt;}"
    s="${s//>/\&gt;}"
    s="${s//\"/\&quot;}"
    s="${s//\'/\&apos;}"
    printf '%s' "$s"
}
# YAML double-quoted scalar escape (backslash + double quote).
yaml_escape() {
    local s="${1:-}"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    printf '%s' "$s"
}
ESC_TITLE="$(xml_escape "${MANUSCRIPT_NAME}")"
ESC_AUTHOR="$(xml_escape "${AUTHOR_NAME}")"

# Generate Valid novelWriter Project Scaffolding
cat << EOF > "${STAGING_DIR}/nwProject.nwx"
<?xml version="1.0" encoding="UTF-8"?>
<novelWriterXML fileVersion="1.5" appVersion="2.0">
  <project>
    <title>${ESC_TITLE}</title>
    <author>${ESC_AUTHOR}</author>
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

# DAT-02: validate the generated XML immediately; a malformed project must
# fail staging, never ship to the author's library.
if command -v python3 &>/dev/null; then
    if ! python3 -c 'import sys, xml.etree.ElementTree as ET; ET.parse(sys.argv[1])' "${STAGING_DIR}/nwProject.nwx"; then
        echo "Error: generated nwProject.nwx failed XML validation. Aborting." >&2
        exit 1
    fi
fi

# Copy Typst Book Template into Exports/typst-template
if [ -d "${PROJECT_ROOT}/templates/typst" ]; then
    mkdir -p "${STAGING_DIR}/Exports/typst-template"
    cp -a "${PROJECT_ROOT}/templates/typst/." "${STAGING_DIR}/Exports/typst-template/"
fi

# Create .gitignore and manuscript manifests
cat << 'EOF' > "${STAGING_DIR}/.gitignore"
# Ars Arcanum Manuscript Git Ignore
*.bak
*.tmp
*.log
.DS_Store
Backups/
05-Backups/
Exports/
04-Publishing/
EOF

YAML_TITLE="$(yaml_escape "${MANUSCRIPT_NAME}")"
YAML_AUTHOR="$(yaml_escape "${AUTHOR_NAME}")"
YAML_UNIVERSE="$(yaml_escape "${UNIVERSE_NAME}")"
YAML_WORLD="$(yaml_escape "${WORLD_NAME}")"
cat << EOF > "${STAGING_DIR}/manuscript.yaml"
# Ars Arcanum Manuscript Project Manifest
title: "${YAML_TITLE}"
author: "${YAML_AUTHOR}"
universe: "${YAML_UNIVERSE}"
world: "${YAML_WORLD}"
created_at: "$(date +%Y-%m-%d)"
EOF

cat << EOF > "${STAGING_DIR}/arcanum.yaml"
# Ars Arcanum world manifest for backwards compatibility
title: "${YAML_TITLE}"
author: "${YAML_AUTHOR}"
universe: "${YAML_UNIVERSE}"
world: "${YAML_WORLD}"
EOF

# Run Validation Checks on Staged Structure
[ -d "${STAGING_DIR}/Book-01/01_Act_I" ] || { echo "Validation error: Book-01 directory missing" >&2; exit 1; }
[ -d "${STAGING_DIR}/Outlines" ] || { echo "Validation error: Outlines directory missing" >&2; exit 1; }
[ -f "${STAGING_DIR}/manuscript.yaml" ] || { echo "Validation error: manuscript.yaml manifest missing" >&2; exit 1; }

# 3. Multi-Tier Git Repository Initialization (REL-04: never claim history
# that does not exist — track commit health and report it honestly).
GIT_HISTORY="ok"
if command -v git &> /dev/null; then
    # 3a. Initialize discrete Manuscript Git repository for Book-01
    if ! (
        cd "${STAGING_DIR}/Book-01"
        git init -q
        git add .
        git -c user.name="Ars Arcanum Maintainers" -c user.email="maintainers@arsarcanum.local" commit -q -m "Initial drafting repository for Book-01 in ${MANUSCRIPT_NAME}" 2>/dev/null
    ); then
        echo "[!] Warning: Book-01 initial Git commit failed (lock contention or identity issue). Volume created without initial history." >&2
        GIT_HISTORY="failed"
    fi

    # 3b. Initialize Manuscript Root Git repository
    if ! (
        cd "${STAGING_DIR}"
        git init -q
        git config advice.addEmbeddedRepo false
        git -c advice.addEmbeddedRepo=false add . 2>/dev/null
        git -c user.name="Ars Arcanum Maintainers" -c user.email="maintainers@arsarcanum.local" commit -q -m "Initial Ars Arcanum manuscript repository: ${MANUSCRIPT_NAME}" 2>/dev/null
    ); then
        echo "[!] Warning: manuscript root initial Git commit failed. Project created without initial history." >&2
        echo "    Repair with: git -C '${STAGING_DIR}/Book-01' commit -m 'Initial commit' (after move: git -C \"\$HOME/Manuscripts/${MANUSCRIPT_NAME}/Book-01\" commit)" >&2
        GIT_HISTORY="failed"
    fi
else
    GIT_HISTORY="missing"
fi

# 4. Atomic Move into Destination
mkdir -p "${MANUSCRIPTS_BASE}"
mv "${STAGING_DIR}" "${TARGET_DIR}"
SUCCESS=1

# 5. Notify completion (REL-04: honest Git status)
if [ "${GIT_HISTORY}" = "ok" ]; then
    GIT_LINE="• Discrete Git version control initialized!"
elif [ "${GIT_HISTORY}" = "missing" ]; then
    GIT_LINE="• Created WITHOUT version history (git not installed — install git, then run: git -C '${TARGET_DIR}' init && git -C '${TARGET_DIR}' add -A && git -C '${TARGET_DIR}' commit -m 'Initial commit')."
else
    GIT_LINE="• Created WITHOUT initial commit history (Git commit failed — repair with: git -C '${TARGET_DIR}/Book-01' commit -m 'Initial commit')."
fi
MSG="Manuscript Project '${MANUSCRIPT_NAME}' successfully created!\n\nLocation:\n${TARGET_DIR}\n\n• Open novelWriter -> Open project in '${MANUSCRIPT_NAME}/nwProject.nwx'\n• Open FocusWriter / markdown editor in '${MANUSCRIPT_NAME}/Book-01'\n• Linked World Lore: '${WORLD_NAME:-None}' [Universe: '${UNIVERSE_NAME:-None}']\n${GIT_LINE}"

if has_gui; then
    zenity --info --title="Manuscript Created Successfully!" --text="${MSG}" --width=480
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit 0
