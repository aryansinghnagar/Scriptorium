#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Back-Matter Concordance & Dramatis Personae Engine
# Purpose: Automatically reads YAML frontmatter and lore definitions from
#          00-World-Bible/ (Characters, Languages, Bestiary, Artifacts, Factions)
#          and generates publication-ready Markdown back-matter files in
#          01-Manuscript/<Book>/04_Back_Matter/01_Dramatis_Personae.md and
#          01-Manuscript/<Book>/04_Back_Matter/02_Glossary_and_Concordance.md.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Concordance Generator — generate Dramatis Personae and Glossary back-matter.

Usage:
  generate_concordance.sh [MANUSCRIPT|WORLD] [OPTIONS]

Options:
  -m, --manuscript NAME  Manuscript project name or directory path
  -w, --world NAME       World Lore Vault name or directory path
  -b, --book VOLUME      Target book volume (e.g. Book-01, Book-02, or "all"; default: all volumes)
  -u, --universe NAME    Universe name (optional)
  -h, --help             Show this help and exit

Exit codes:
  0  concordance generated successfully
  1  error (world/manuscript not found, invalid parameters)
  3  user abort (no target selected)
USAGE
}

MANUSCRIPT_CLI=""
WORLD_CLI=""
BOOK_CLI=""
UNIVERSE_CLI=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -m|--manuscript)
            [ $# -ge 2 ] || { echo "Error: --manuscript requires a value." >&2; exit 2; }
            MANUSCRIPT_CLI="$2"; shift 2 ;;
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 2; }
            WORLD_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 2; }
            BOOK_CLI="$2"; shift 2 ;;
        -u|--universe)
            [ $# -ge 2 ] || { echo "Error: --universe requires a value." >&2; exit 2; }
            UNIVERSE_CLI="$2"; shift 2 ;;
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

TARGET_BOOK="${BOOK_CLI:-${POSITIONAL[1]:-all}}"

RESOLVED_MS=""
RESOLVED_WORLD=""

if [ -n "${MANUSCRIPT_CLI}" ]; then
    RESOLVED_MS="$(resolve_manuscript_dir "${MANUSCRIPT_CLI}")"
fi

if [ -n "${WORLD_CLI}" ]; then
    RESOLVED_WORLD="$(resolve_world_dir "${WORLD_CLI}" "${UNIVERSE_CLI}")"
fi

if [ -z "${RESOLVED_MS}" ] && [ -z "${RESOLVED_WORLD}" ] && [ ${#POSITIONAL[@]} -gt 0 ]; then
    POS_INPUT="${POSITIONAL[0]}"
    RESOLVED_MS="$(resolve_manuscript_dir "${POS_INPUT}")"
    if [ -z "${RESOLVED_MS}" ]; then
        RESOLVED_WORLD="$(resolve_world_dir "${POS_INPUT}" "${UNIVERSE_CLI}")"
    fi
fi

if [ -z "${RESOLVED_MS}" ] && [ -z "${RESOLVED_WORLD}" ]; then
    discover_manuscripts MANUSCRIPTS
    discover_worlds WORLDS
    if [ ${#MANUSCRIPTS[@]} -eq 1 ]; then
        RESOLVED_MS="${MANUSCRIPTS[0]}"
    elif [ ${#WORLDS[@]} -eq 1 ]; then
        RESOLVED_WORLD="${WORLDS[0]}"
        warn_if_legacy_root "${RESOLVED_WORLD}"
    elif has_gui && { [ ${#MANUSCRIPTS[@]} -gt 0 ] || [ ${#WORLDS[@]} -gt 0 ]; }; then
        CHOICES=()
        for m in "${MANUSCRIPTS[@]}"; do
            CHOICES+=("$(basename "$m")" "[Manuscript] $m")
        done
        for w in "${WORLDS[@]}"; do
            CHOICES+=("$(basename "$w")" "[World Lore] $w")
        done
        PICKED=$(zenity --list --title="Ars Arcanum — Select Project for Concordance" \
            --text="Select the manuscript or world to generate back-matter concordance for:" \
            --column="Name" --column="Type & Path" \
            --width=520 --height=320 \
            "${CHOICES[@]}" || true)
        if [ -n "$PICKED" ]; then
            RESOLVED_MS="$(resolve_manuscript_dir "$PICKED")"
            [ -z "${RESOLVED_MS}" ] && RESOLVED_WORLD="$(resolve_world_dir "$PICKED" "${UNIVERSE_CLI}")"
        fi
    fi
fi

BIBLE_DIR=""
MANUSCRIPT_DIR=""

if [ -n "${RESOLVED_MS}" ] && [ -d "${RESOLVED_MS}" ]; then
    if [ -d "${RESOLVED_MS}/01-Manuscript" ]; then
        MANUSCRIPT_DIR="${RESOLVED_MS}/01-Manuscript"
    else
        MANUSCRIPT_DIR="${RESOLVED_MS}"
    fi

    LINKED_WORLD=""
    LINKED_UNI=""
    MANIFEST="${RESOLVED_MS}/manuscript.yaml"
    [ -f "${MANIFEST}" ] || MANIFEST="${RESOLVED_MS}/arcanum.yaml"
    [ -f "${MANIFEST}" ] || MANIFEST="${RESOLVED_MS}/scriptorium.yaml"
    if [ -f "${MANIFEST}" ]; then
        LINKED_WORLD=$(sed -n -E 's/^world:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        LINKED_UNI=$(sed -n -E 's/^universe:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi

    if [ -n "${RESOLVED_WORLD}" ] && [ -d "${RESOLVED_WORLD}" ]; then
        if [ -d "${RESOLVED_WORLD}/00-World-Bible" ]; then
            BIBLE_DIR="${RESOLVED_WORLD}/00-World-Bible"
        else
            BIBLE_DIR="${RESOLVED_WORLD}"
        fi
    elif [ -n "${LINKED_WORLD}" ]; then
        BIBLE_DIR="$(resolve_world_dir "${LINKED_WORLD}" "${LINKED_UNI}")"
    fi

    if [ -z "${BIBLE_DIR}" ] || [ ! -d "${BIBLE_DIR}" ]; then
        if [ -d "${RESOLVED_MS}/00-World-Bible" ]; then
            BIBLE_DIR="${RESOLVED_MS}/00-World-Bible"
        elif [ -d "${RESOLVED_MS}/Characters" ]; then
            BIBLE_DIR="${RESOLVED_MS}"
        fi
    fi
elif [ -n "${RESOLVED_WORLD}" ] && [ -d "${RESOLVED_WORLD}" ]; then
    if [ -d "${RESOLVED_WORLD}/00-World-Bible" ]; then
        BIBLE_DIR="${RESOLVED_WORLD}/00-World-Bible"
    else
        BIBLE_DIR="${RESOLVED_WORLD}"
    fi

    if [ -d "${RESOLVED_WORLD}/01-Manuscript" ]; then
        MANUSCRIPT_DIR="${RESOLVED_WORLD}/01-Manuscript"
    else
        discover_manuscripts MANUSCRIPTS
        WNAME="$(basename "${RESOLVED_WORLD}")"
        for m in "${MANUSCRIPTS[@]}"; do
            m_manifest="${m}/manuscript.yaml"
            [ -f "${m_manifest}" ] || m_manifest="${m}/arcanum.yaml"
            [ -f "${m_manifest}" ] || m_manifest="${m}/scriptorium.yaml"
            if [ -f "${m_manifest}" ]; then
                mw=$(sed -n -E 's/^world:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${m_manifest}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                if [ "$mw" = "$WNAME" ]; then
                    MANUSCRIPT_DIR="$m"
                    break
                fi
            fi
        done
        if [ -z "${MANUSCRIPT_DIR}" ]; then
            MANUSCRIPT_DIR="${RESOLVED_WORLD}/01-Manuscript"
            mkdir -p "${MANUSCRIPT_DIR}"
        fi
    fi
fi

if [ -z "${BIBLE_DIR}" ] || [ ! -d "${BIBLE_DIR}" ]; then
    echo "Error: World Bible lore folder not found for '${POS_INPUT:-${RESOLVED_WORLD:-${RESOLVED_MS:-unknown}}}'." >&2
    exit 2
fi

if [ -z "${MANUSCRIPT_DIR}" ] || [ ! -d "${MANUSCRIPT_DIR}" ]; then
    mkdir -p "${MANUSCRIPT_DIR}"
fi

echo "Generating Concordance & Dramatis Personae from $(basename "${BIBLE_DIR}") for $(basename "${MANUSCRIPT_DIR}")..."

python3 "${SCRIPT_DIR}/lib/concordance.py" -w "${BIBLE_DIR}" -m "${MANUSCRIPT_DIR}" -b "${TARGET_BOOK}"

MSG="Concordance and Dramatis Personae successfully generated for '$(basename "${BIBLE_DIR}")'!\n\nFiles created under 04_Back_Matter/:\n• 01_Dramatis_Personae.md\n• 02_Glossary_and_Concordance.md\n\nThese will be automatically compiled at the end of your Typst print PDFs and Pandoc EPUBs."

if has_gui; then
    zenity --info --title="Concordance Generated" --text="${MSG}" --width=480 2>/dev/null || echo -e "\n${MSG}"
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit 0
