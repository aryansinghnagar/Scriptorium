#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Manuscript Revision & Draft Comparator
# Purpose: Compares any two manuscript drafts (e.g. Draft-02 vs Draft-01),
#          generating visual word-level Redline changelogs (HTML, Terminal, JSON)
#          or launching LibreOffice Writer track-changes comparison.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MANUSCRIPTS_BASE="${MANUSCRIPTS_BASE:-${HOME}/Manuscripts}"

# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Manuscript Draft Comparator — visual redline & changelog comparison.

Usage:
  compare_drafts.sh [MANUSCRIPT] [TARGET_DRAFT] [PRIOR_DRAFT] [OPTIONS]

Options:
  -m, --manuscript NAME     Manuscript project name or directory
  -b, --book VOLUME         Book volume directory (default: Book-01)
  --html [OUTPUT_FILE]      Generate standalone accessible HTML Redline report
  --browser                 Generate HTML report and open in default web browser
  --json                    Output machine-readable JSON change metrics
  --terminal                Print ANSI colored diff to terminal (default)
  --libreoffice             Export drafts and open LibreOffice Writer comparison
  -h, --help                Show this help and exit

Examples:
  arcanum compare My-Novel Draft-02 Draft-01 --browser
  arcanum compare My-Novel Draft-03 Draft-01 --html ./diff.html
  arcanum compare My-Novel --browser
USAGE
}

MANUSCRIPT_CLI=""
BOOK_VOLUME_CLI="Book-01"
DRAFT_A_CLI=""
DRAFT_B_CLI=""
OUTPUT_HTML_CLI=""
OPEN_BROWSER=0
OUTPUT_JSON=0
OUTPUT_TERMINAL=0
USE_LIBREOFFICE=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -m|--manuscript)
            [ $# -ge 2 ] || { echo "Error: --manuscript requires a value." >&2; exit 2; }
            MANUSCRIPT_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 2; }
            BOOK_VOLUME_CLI="$2"; shift 2 ;;
        --html)
            if [ $# -ge 2 ] && [[ "$2" != -* ]]; then
                OUTPUT_HTML_CLI="$2"; shift 2
            else
                OUTPUT_HTML_CLI="auto"; shift
            fi ;;
        --browser)
            OPEN_BROWSER=1; shift ;;
        --json)
            OUTPUT_JSON=1; shift ;;
        --terminal)
            OUTPUT_TERMINAL=1; shift ;;
        --libreoffice)
            USE_LIBREOFFICE=1; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; while [ $# -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

TARGET_INPUT="${MANUSCRIPT_CLI:-${POSITIONAL[0]:-}}"

# 1. Resolve manuscript target directory
if [ -z "${TARGET_INPUT}" ]; then
    if has_gui; then
        TARGET_INPUT=$(zenity --file-selection --directory \
            --title="Ars Arcanum — Select Manuscript Project to Compare Drafts" \
            --filename="${MANUSCRIPTS_BASE}/" || true)
    fi
fi

if [ -z "${TARGET_INPUT}" ]; then
    discover_manuscripts FOUND_MS
    if [ ${#FOUND_MS[@]} -eq 1 ]; then
        TARGET_INPUT="${FOUND_MS[0]}"
    elif [ ${#FOUND_MS[@]} -gt 1 ]; then
        echo "Multiple Manuscript projects discovered — please specify one:"
        for m in "${FOUND_MS[@]}"; do
            echo "  • $(basename "$m")  [$m]"
        done
        exit 3
    else
        echo "No Manuscript projects found. Create one first with: arcanum new manuscript <name>" >&2
        exit 3
    fi
fi

RESOLVED_MS="$(resolve_manuscript_dir "${TARGET_INPUT}")"
if [ -n "${RESOLVED_MS}" ]; then
    MANUSCRIPT_DIR="${RESOLVED_MS}"
elif [ -d "${TARGET_INPUT}" ]; then
    MANUSCRIPT_DIR="${TARGET_INPUT}"
else
    echo "Error: Manuscript project directory not found: ${TARGET_INPUT}" >&2
    exit 2
fi

MS_NAME="$(basename "${MANUSCRIPT_DIR}")"
BOOK_DIR="${MANUSCRIPT_DIR}/${BOOK_VOLUME_CLI}"

if [ ! -d "${BOOK_DIR}" ]; then
    echo "Error: Volume directory '${BOOK_VOLUME_CLI}' not found in ${MANUSCRIPT_DIR}." >&2
    exit 2
fi

# 2. Discover available drafts
AVAILABLE_DRAFTS=()
while IFS= read -r -d '' d; do
    AVAILABLE_DRAFTS+=("$(basename "$d")")
done < <(find "${BOOK_DIR}" -mindepth 1 -maxdepth 1 -type d -name "Draft-*" -print0 2>/dev/null | sort -zV)

if [ ${#AVAILABLE_DRAFTS[@]} -eq 0 ] && [ -d "${BOOK_DIR}/01_Act_I" ]; then
    AVAILABLE_DRAFTS=("Draft-01 (Baseline)")
fi

if [ ${#AVAILABLE_DRAFTS[@]} -lt 2 ]; then
    if [ ${#AVAILABLE_DRAFTS[@]} -eq 1 ] && [ "${AVAILABLE_DRAFTS[0]}" = "Draft-01 (Baseline)" ]; then
        echo "Note: '${MS_NAME}' currently has only a single baseline draft."
        echo "Create a second draft first with: arcanum new draft ${MS_NAME}"
    else
        echo "Note: Only ${#AVAILABLE_DRAFTS[@]} draft(s) found in '${MS_NAME}' [${BOOK_VOLUME_CLI}]."
        echo "Create another draft first with: arcanum new draft ${MS_NAME}"
    fi
    if has_gui; then
        zenity --info --title="Need Multiple Drafts" --text="At least two drafts are required to perform a comparison.\n\nInitialize a new draft with:\n  arcanum new draft ${MS_NAME}" --width=420
    fi
    exit 1
fi

# 3. Resolve Target Draft (Newer, Draft B) and Prior Draft (Older, Draft A)
TARGET_DRAFT="${DRAFT_B_CLI:-${POSITIONAL[1]:-}}"
PRIOR_DRAFT="${DRAFT_A_CLI:-${POSITIONAL[2]:-}}"

if [ -z "${TARGET_DRAFT}" ] || [ -z "${PRIOR_DRAFT}" ]; then
    if has_gui; then
        DRAFT_LIST=()
        for d in "${AVAILABLE_DRAFTS[@]}"; do
            DRAFT_LIST+=("$d" "Draft $d")
        done

        if [ -z "${TARGET_DRAFT}" ]; then
            TARGET_DRAFT=$(zenity --list --title="Select Target (Newer) Draft" \
                --text="Select the newer draft you are revising (e.g. Draft-02, Draft-03):" \
                --column="Draft" --column="Description" --hide-column=2 \
                --width=380 --height=260 "${DRAFT_LIST[@]}" || true)
        fi

        if [ -n "${TARGET_DRAFT}" ] && [ -z "${PRIOR_DRAFT}" ]; then
            PRIOR_DRAFT=$(zenity --list --title="Select Prior (Older) Draft to Compare Against" \
                --text="Select the earlier baseline draft (e.g. Draft-01):" \
                --column="Draft" --column="Description" --hide-column=2 \
                --width=380 --height=260 "${DRAFT_LIST[@]}" || true)
        fi
    fi
fi

if [ -z "${TARGET_DRAFT}" ] || [ -z "${PRIOR_DRAFT}" ]; then
    # CLI default: latest draft vs draft immediately before it
    if [ ${#AVAILABLE_DRAFTS[@]} -ge 2 ]; then
        TARGET_DRAFT="${AVAILABLE_DRAFTS[$((${#AVAILABLE_DRAFTS[@]} - 1))]}"
        PRIOR_DRAFT="${AVAILABLE_DRAFTS[$((${#AVAILABLE_DRAFTS[@]} - 2))]}"
    else
        echo "Error: Please specify both drafts to compare: compare_drafts.sh <ms> <target_draft> <prior_draft>" >&2
        exit 2
    fi
fi

# Resolve paths
RESOLVE_DRAFT_PATH() {
    local dname="$1"
    if [ -d "${BOOK_DIR}/${dname}" ]; then
        echo "${BOOK_DIR}/${dname}"
    elif [ "$dname" = "Draft-01 (Baseline)" ] || [ "$dname" = "Draft-01" ] || [ "$dname" = "Draft-1" ] || [ "$dname" = "baseline" ]; then
        if [ -d "${BOOK_DIR}/Draft-01" ]; then
            echo "${BOOK_DIR}/Draft-01"
        elif [ -d "${BOOK_DIR}/01_Act_I" ]; then
            echo "${BOOK_DIR}"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

PATH_A="$(RESOLVE_DRAFT_PATH "${PRIOR_DRAFT}")"
PATH_B="$(RESOLVE_DRAFT_PATH "${TARGET_DRAFT}")"

if [ -z "${PATH_A}" ] || [ ! -d "${PATH_A}" ]; then
    echo "Error: Prior draft directory '${PRIOR_DRAFT}' not found in ${BOOK_DIR}." >&2
    exit 2
fi

if [ -z "${PATH_B}" ] || [ ! -d "${PATH_B}" ]; then
    echo "Error: Target draft directory '${TARGET_DRAFT}' not found in ${BOOK_DIR}." >&2
    exit 2
fi

DIFF_ENGINE="${SCRIPT_DIR}/lib/manuscript_diff.py"
if [ ! -f "${DIFF_ENGINE}" ]; then
    echo "Error: Manuscript diff engine not found at ${DIFF_ENGINE}." >&2
    exit 1
fi

# 4. Execute selected output format
if [ "${OUTPUT_JSON}" -eq 1 ]; then
    python3 "${DIFF_ENGINE}" "${PATH_A}" "${PATH_B}" \
        --label-a "${PRIOR_DRAFT}" --label-b "${TARGET_DRAFT}" --json
elif [ "${USE_LIBREOFFICE}" -eq 1 ]; then
    echo "Launching LibreOffice Writer Track Changes comparison..."
    python3 "${DIFF_ENGINE}" "${PATH_A}" "${PATH_B}" \
        --label-a "${PRIOR_DRAFT}" --label-b "${TARGET_DRAFT}" --libreoffice
elif [ -n "${OUTPUT_HTML_CLI}" ] || [ "${OPEN_BROWSER}" -eq 1 ] || has_gui; then
    HTML_OUT="${OUTPUT_HTML_CLI}"
    if [ -z "${HTML_OUT}" ] || [ "${HTML_OUT}" = "auto" ]; then
        EXPORTS_DIR="${MANUSCRIPT_DIR}/Exports"
        mkdir -p "${EXPORTS_DIR}"
        HTML_OUT="${EXPORTS_DIR}/Changelog-${PRIOR_DRAFT}-vs-${TARGET_DRAFT}.html"
    fi

    python3 "${DIFF_ENGINE}" "${PATH_A}" "${PATH_B}" \
        --label-a "${PRIOR_DRAFT}" --label-b "${TARGET_DRAFT}" --html "${HTML_OUT}"

    if [ "${OPEN_BROWSER}" -eq 1 ] || has_gui; then
        echo "Opening Redline changelog in browser..."
        if command -v xdg-open &>/dev/null; then
            xdg-open "${HTML_OUT}" 2>/dev/null &
        elif command -v sensible-browser &>/dev/null; then
            sensible-browser "${HTML_OUT}" 2>/dev/null &
        elif command -v start &>/dev/null; then
            start "${HTML_OUT}" 2>/dev/null || true
        fi
    fi
else
    # Terminal ANSI output
    python3 "${DIFF_ENGINE}" "${PATH_A}" "${PATH_B}" \
        --label-a "${PRIOR_DRAFT}" --label-b "${TARGET_DRAFT}" --terminal
fi

exit 0
