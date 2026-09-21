#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Add Manuscript Volume Engine
# Purpose: Scaffolds a new manuscript volume (Book-02, Book-03, etc.) within
#          a manuscript project with 3-act structure, starter chapters, and a
#          discrete Git repository.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Add Volume — scaffold a new manuscript volume in a manuscript project.

Usage:
  add_book.sh [MANUSCRIPT_NAME|MANUSCRIPT_DIR] [VOLUME_NAME] [OPTIONS]

Options:
  -m, --manuscript NAME    Manuscript project name or directory path
  -w, --world NAME         Alias for --manuscript (backwards compatibility)
  -u, --universe NAME      Universe name (optional)
  -b, --book VOLUME        Volume name to create (e.g. Book-02, Book-03; auto-detected if omitted)
  -v, --volume VOLUME      Alias for --book
  -h, --help               Show this help and exit

Exit codes:
  0  book volume created successfully
  1  error (manuscript not found, volume already exists, invalid name)
  3  user abort (no manuscript selected)
USAGE
}

MANUSCRIPT_CLI=""
UNIVERSE_CLI=""
BOOK_CLI=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -m|--manuscript|-w|--world)
            [ $# -ge 2 ] || { echo "Error: $1 requires a value." >&2; exit 2; }
            MANUSCRIPT_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_CLI="$2"; shift 2 ;;
        -b|--book|-v|--volume)
            [ $# -ge 2 ] || { echo "Error: $1 requires a value." >&2; exit 2; }
            BOOK_CLI="$2"; shift 2 ;;
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

TARGET_INPUT="${MANUSCRIPT_CLI:-${POSITIONAL[0]:-}}"
VOLUME_NAME="${BOOK_CLI:-${POSITIONAL[1]:-}}"

# Discover manuscripts
discover_manuscripts MANUSCRIPTS
 
if [ -z "${TARGET_INPUT}" ]; then
    if [ ${#MANUSCRIPTS[@]} -eq 1 ]; then
        TARGET_INPUT="${MANUSCRIPTS[0]}"
    elif has_gui && [ ${#MANUSCRIPTS[@]} -gt 1 ]; then
        CHOICES=()
        for m in "${MANUSCRIPTS[@]}"; do
            CHOICES+=("$(basename "$m")" "$m")
        done
        PICKED=$(zenity --list --title="Ars Arcanum — Select Manuscript for New Volume" \
            --text="Select the manuscript project to add a new volume to:" \
            --column="Manuscript Name" --column="Path" \
            --width=520 --height=320 \
            "${CHOICES[@]}" || true)
        [ -n "$PICKED" ] && TARGET_INPUT="$PICKED"
    elif [ -t 0 ] && [ ${#MANUSCRIPTS[@]} -gt 1 ]; then
        echo "Select manuscript to add volume to:"
        select m in "${MANUSCRIPTS[@]}"; do
            [ -n "${m:-}" ] && TARGET_INPUT="$m"
            break
        done
    fi
fi

if [ -z "${TARGET_INPUT}" ]; then
    echo "No manuscript specified. Aborting." >&2
    exit 3
fi

MANUSCRIPT_DIR="$(resolve_manuscript_dir "${TARGET_INPUT}")"
if [ -z "${MANUSCRIPT_DIR}" ] || [ ! -d "${MANUSCRIPT_DIR}" ]; then
    # Fallback to world resolution if legacy world directory was passed
    MANUSCRIPT_DIR="$(resolve_world_dir "${TARGET_INPUT}" "${UNIVERSE_CLI}")"
fi

if [ -z "${MANUSCRIPT_DIR}" ] || [ ! -d "${MANUSCRIPT_DIR}" ]; then
    echo "Error: Manuscript directory '${TARGET_INPUT}' not found." >&2
    exit 2
fi

MANUSCRIPT_NAME="$(basename "${MANUSCRIPT_DIR}")"

# If legacy world with 01-Manuscript subfolder:
VOLUMES_PARENT="${MANUSCRIPT_DIR}"
if [ -d "${MANUSCRIPT_DIR}/01-Manuscript" ]; then
    VOLUMES_PARENT="${MANUSCRIPT_DIR}/01-Manuscript"
fi

# Determine next volume name if not provided
if [ -z "${VOLUME_NAME}" ]; then
    MAX_NUM=0
    for bdir in "${VOLUMES_PARENT}"/Book-*; do
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
            --title="Ars Arcanum — Add Manuscript Volume" \
            --text="Enter the volume name for '${MANUSCRIPT_NAME}':" \
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

TARGET_VOL_DIR="${VOLUMES_PARENT}/${VOLUME_NAME}"

if [ -d "${TARGET_VOL_DIR}" ]; then
    echo "Error: Volume '${VOLUME_NAME}' already exists in ${MANUSCRIPT_DIR}." >&2
    exit 1
fi

echo "Scaffolding new manuscript volume '${VOLUME_NAME}' in ${MANUSCRIPT_NAME}..."

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
@location: Crossroads
@status: Draft

The crossroads loomed ahead, each path demanding a price too steep to pay in coin alone.
EOF

cat << 'EOF' > "${TARGET_VOL_DIR}/03_Act_III/01_Chapter_03.md"
# Chapter 3: The Final Confrontation

@pov: Protagonist
@char: Protagonist
@location: Citadel
@status: Draft

In the crucible of the climax, what had been hidden was laid bare.
EOF

# Initialize discrete Git repository for the new volume (REL-04)
GIT_HISTORY="ok"
if command -v git &> /dev/null; then
    if ! (
        cd "${TARGET_VOL_DIR}"
        git init -q
        git add .
        git_commit_safe "Initial manuscript drafting repository for ${VOLUME_NAME} in ${MANUSCRIPT_NAME}"
    ); then
        echo "[!] Warning: volume initial Git commit failed. Volume created without initial history." >&2
        GIT_HISTORY="failed"
    fi

    # Track in Manuscript Git repo if present
    if [ -d "${MANUSCRIPT_DIR}/.git" ]; then
        if ! (
            cd "${MANUSCRIPT_DIR}"
            git config advice.addEmbeddedRepo false
            git -c advice.addEmbeddedRepo=false add "${TARGET_VOL_DIR#"${MANUSCRIPT_DIR}/"}" 2>/dev/null
            git_commit_safe "Scaffold manuscript volume ${VOLUME_NAME} in ${MANUSCRIPT_NAME}"
        ); then
            echo "[!] Warning: manuscript tracking commit failed for '${VOLUME_NAME}'. Volume itself is intact." >&2
            [ "${GIT_HISTORY}" = "ok" ] && GIT_HISTORY="failed"
        fi
    fi
else
    GIT_HISTORY="missing"
fi

if [ "${GIT_HISTORY}" = "ok" ]; then
    GIT_LINE="• Discrete Git repository initialized!"
elif [ "${GIT_HISTORY}" = "missing" ]; then
    GIT_LINE="• Created WITHOUT version history (git not installed)."
else
    GIT_LINE="• Created WITHOUT initial commit history (see warnings above)."
fi
MSG="Manuscript volume '${VOLUME_NAME}' scaffolded successfully in '${MANUSCRIPT_NAME}'!\n\nPath:\n${TARGET_VOL_DIR}\n\n• 3 Acts initialized (01_Act_I, 02_Act_II, 03_Act_III)\n• Starter chapters created\n${GIT_LINE}"

if has_gui; then
    zenity --info --title="Volume Created" --text="${MSG}" --width=450
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit 0
