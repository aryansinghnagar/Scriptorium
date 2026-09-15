#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Add Manuscript Volume Engine
# Purpose: Scaffolds a new manuscript volume (Book-02, Book-03, etc.) within
#          an existing world with 3-act structure, starter chapters, and a
#          discrete Git repository.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Scriptorium Add Book — scaffold a new manuscript volume in an existing world.

Usage:
  add_book.sh [WORLD_NAME|WORLD_DIR] [VOLUME_NAME] [OPTIONS]

Options:
  -w, --world NAME     World name or directory path
  -u, --universe NAME  Universe name (optional)
  -b, --book VOLUME    Volume name to create (e.g. Book-02, Book-03; auto-detected if omitted)
  -h, --help           Show this help and exit

Exit codes:
  0  book volume created successfully
  1  error (world not found, volume already exists, invalid name)
  3  user abort (no world selected)
USAGE
}

WORLD_CLI=""
UNIVERSE_CLI=""
BOOK_CLI=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 1; }
            WORLD_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 1; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 1; }
            BOOK_CLI="$2"; shift 2 ;;
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

TARGET_WORLD="${WORLD_CLI:-${POSITIONAL[0]:-}}"
VOLUME_NAME="${BOOK_CLI:-${POSITIONAL[1]:-}}"

# Discover worlds if not provided
discover_worlds WORLDS

if [ -z "${TARGET_WORLD}" ]; then
    if [ ${#WORLDS[@]} -eq 1 ]; then
        TARGET_WORLD="${WORLDS[0]}"
    elif has_gui && [ ${#WORLDS[@]} -gt 1 ]; then
        CHOICES=()
        for w in "${WORLDS[@]}"; do
            CHOICES+=("$(basename "$w")" "[Universe: $(universe_label "$w")] $w")
        done
        PICKED=$(zenity --list --title="Scriptorium — Select World for New Volume" \
            --text="Select the world to add a new manuscript volume to:" \
            --column="World Name" --column="Universe & Path" \
            --width=520 --height=320 \
            "${CHOICES[@]}" || true)
        [ -n "$PICKED" ] && TARGET_WORLD="$PICKED"
    elif [ -t 0 ] && [ ${#WORLDS[@]} -gt 1 ]; then
        echo "Select world to add book to:"
        select w in "${WORLDS[@]}"; do
            [ -n "${w:-}" ] && TARGET_WORLD="$w"
            break
        done
    fi
fi

if [ -z "${TARGET_WORLD}" ]; then
    echo "No world specified. Aborting." >&2
    exit 3
fi

WORLD_DIR="$(resolve_world_dir "${TARGET_WORLD}" "${UNIVERSE_CLI}")"

if [ -z "${WORLD_DIR}" ] || [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: World directory '${TARGET_WORLD}' not found." >&2
    exit 1
fi

WORLD_NAME="$(basename "${WORLD_DIR}")"
MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"
mkdir -p "${MANUSCRIPT_DIR}"

# Determine next volume name if not provided
if [ -z "${VOLUME_NAME}" ]; then
    MAX_NUM=0
    for bdir in "${MANUSCRIPT_DIR}"/Book-*; do
        if [ -d "$bdir" ]; then
            bname="$(basename "$bdir")"
            num="${bname#Book-}"
            if [[ "$num" =~ ^[0-9]+$ ]]; then
                num_val=$((10#$num))
                [ "$num_val" -gt "$MAX_NUM" ] && MAX_NUM=$num_val
            fi
        fi
    done
    NEXT_NUM=$((MAX_NUM + 1))
    DEFAULT_VOL="$(printf 'Book-%02d' "${NEXT_NUM}")"

    if has_gui; then
        VOLUME_NAME=$(zenity --entry \
            --title="Scriptorium — Add Manuscript Volume" \
            --text="Enter the volume name for '${WORLD_NAME}':" \
            --entry-text="${DEFAULT_VOL}" || true)
    else
        VOLUME_NAME="${DEFAULT_VOL}"
    fi
fi

if [ -z "${VOLUME_NAME}" ]; then
    echo "No volume name provided. Aborting." >&2
    exit 3
fi

# Sanitize volume name
VOLUME_NAME="$(printf '%s' "${VOLUME_NAME}" | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '-' | tr -cd 'A-Za-z0-9_-' | cut -c1-64)"

TARGET_VOL_DIR="${MANUSCRIPT_DIR}/${VOLUME_NAME}"

if [ -d "${TARGET_VOL_DIR}" ]; then
    echo "Error: Volume '${VOLUME_NAME}' already exists in ${WORLD_DIR}." >&2
    exit 1
fi

echo "Scaffolding new manuscript volume '${VOLUME_NAME}' in ${WORLD_NAME}..."

# Create 3-act structure
mkdir -p "${TARGET_VOL_DIR}/01_Act_I"
mkdir -p "${TARGET_VOL_DIR}/02_Act_II"
mkdir -p "${TARGET_VOL_DIR}/03_Act_III"

# Create starter chapters
cat << 'EOF' > "${TARGET_VOL_DIR}/01_Act_I/01_Chapter_01.md"
# Chapter 1: The New Horizon

@pov: Protagonist
@char: Protagonist
@location: Capital
@status: Draft

The quiet of dawn brought with it the realization that yesterday's peace was only a prelude. Every journey begins anew when the horizon shifts.
EOF

cat << 'EOF' > "${TARGET_VOL_DIR}/02_Act_II/01_Chapter_02.md"
# Chapter 2: The Rising Tension

@pov: Protagonist
@char: Protagonist
@status: Draft

The crossroads loomed ahead, each path demanding a price too steep to pay in coin alone.
EOF

cat << 'EOF' > "${TARGET_VOL_DIR}/03_Act_III/01_Chapter_03.md"
# Chapter 3: The Final Confrontation

@pov: Protagonist
@char: Protagonist
@status: Draft

In the crucible of the climax, what had been hidden was laid bare.
EOF

# Initialize discrete Git repository for the new volume
if command -v git &> /dev/null; then
    (
        cd "${TARGET_VOL_DIR}"
        git init -q
        git add .
        git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Initial manuscript drafting repository for ${VOLUME_NAME} in ${WORLD_NAME}" 2>/dev/null || true
    )

    # Track in World Git repo if present
    if [ -d "${WORLD_DIR}/.git" ]; then
        (
            cd "${WORLD_DIR}"
            git config advice.addEmbeddedRepo false
            git -c advice.addEmbeddedRepo=false add "01-Manuscript/${VOLUME_NAME}" 2>/dev/null || true
            git -c user.name="Scriptorium" -c user.email="scriptorium@localhost" commit -q -m "Scaffold manuscript volume ${VOLUME_NAME} in ${WORLD_NAME}" 2>/dev/null || true
        )
    fi
fi

MSG="Manuscript volume '${VOLUME_NAME}' scaffolded successfully in '${WORLD_NAME}'!\n\nPath:\n${TARGET_VOL_DIR}\n\n• 3 Acts initialized (01_Act_I, 02_Act_II, 03_Act_III)\n• Starter chapters created\n• Discrete Git repository initialized!"

if has_gui; then
    zenity --info --title="Volume Created" --text="${MSG}" --width=450
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit 0
