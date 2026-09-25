#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Manuscript Draft Initializer & Forking Manager
# Purpose: Manages discrete draft versions for books (e.g. Draft-01, Draft-02)
#          within a Manuscript Project (~/Manuscripts/<Manuscript>/<Volume>/<Draft>).
#          Forks existing prose, updates active draft pointer, and tags Git milestones.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MANUSCRIPTS_BASE="${MANUSCRIPTS_BASE:-${HOME}/Manuscripts}"

# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

usage() {
    cat << 'USAGE'
Ars Arcanum Draft Initializer — create or fork a new manuscript draft version.

Usage:
  init_draft.sh [MANUSCRIPT] [DRAFT_NAME] [OPTIONS]

Options:
  -m, --manuscript NAME    Manuscript project name or directory
  -n, --name DRAFT_NAME    New draft name (e.g., Draft-02, Draft-03, Revision-A)
  -b, --book VOLUME        Book volume directory (default: Book-01)
  --from-draft DRAFT       Source draft to fork from (default: latest draft)
  -l, --list               List available drafts for the manuscript
  -h, --help               Show this help and exit

Exit codes:
  0  draft created/forked successfully
  1  error (invalid name, target exists, missing source)
  3  user abort (no manuscript selected)
USAGE
}

MANUSCRIPT_CLI=""
DRAFT_NAME_CLI=""
BOOK_VOLUME_CLI="Book-01"
FROM_DRAFT_CLI=""
LIST_MODE=0
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        -m|--manuscript)
            [ $# -ge 2 ] || { echo "Error: --manuscript requires a value." >&2; exit 2; }
            MANUSCRIPT_CLI="$2"; shift 2 ;;
        -n|--name)
            [ $# -ge 2 ] || { echo "Error: --name requires a value." >&2; exit 2; }
            DRAFT_NAME_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 2; }
            BOOK_VOLUME_CLI="$2"; shift 2 ;;
        --from-draft)
            [ $# -ge 2 ] || { echo "Error: --from-draft requires a value." >&2; exit 2; }
            FROM_DRAFT_CLI="$2"; shift 2 ;;
        -l|--list)
            LIST_MODE=1; shift ;;
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
            --title="Ars Arcanum — Select Manuscript Project for New Draft" \
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
arcanum_validate_volume_name "${BOOK_VOLUME_CLI}" || exit $?
BOOK_DIR="${MANUSCRIPT_DIR}/${BOOK_VOLUME_CLI}"

if [ ! -d "${BOOK_DIR}" ]; then
    echo "Error: Volume directory '${BOOK_VOLUME_CLI}' not found in ${MANUSCRIPT_DIR}." >&2
    exit 2
fi

# 2. Discover existing drafts in this Book volume
EXISTING_DRAFTS=()
while IFS= read -r -d '' d; do
    EXISTING_DRAFTS+=("$(basename "$d")")
done < <(find "${BOOK_DIR}" -mindepth 1 -maxdepth 1 -type d -name "Draft-*" -print0 2>/dev/null | sort -zV)

if [ "${LIST_MODE}" -eq 1 ]; then
    echo "Existing Drafts for '${MS_NAME}' [${BOOK_VOLUME_CLI}]:"
    if [ ${#EXISTING_DRAFTS[@]} -eq 0 ]; then
        if [ -d "${BOOK_DIR}/01_Act_I" ]; then
            echo "  • Draft-01 (Baseline unversioned structure)"
        else
            echo "  (No drafts found)"
        fi
    else
        for d in "${EXISTING_DRAFTS[@]}"; do
            echo "  • ${d}"
        done
    fi
    exit 0
fi

# 3. Determine next default draft name and source draft
NEXT_DRAFT_NUM=1
LATEST_DRAFT=""

if [ ${#EXISTING_DRAFTS[@]} -gt 0 ]; then
    LATEST_DRAFT="${EXISTING_DRAFTS[$((${#EXISTING_DRAFTS[@]} - 1))]}"
    # Extract number from Draft-XX
    if [[ "${LATEST_DRAFT}" =~ Draft-([0-9]+) ]]; then
        NEXT_NUM=$(( 10#${BASH_REMATCH[1]} + 1 ))
        NEXT_DRAFT_NUM=$(printf "%02d" "${NEXT_NUM}")
    else
        NEXT_DRAFT_NUM=$(printf "%02d" $((${#EXISTING_DRAFTS[@]} + 1)))
    fi
elif [ -d "${BOOK_DIR}/01_Act_I" ]; then
    LATEST_DRAFT="baseline"
    NEXT_DRAFT_NUM="02"
fi

DEFAULT_NEW_DRAFT="Draft-${NEXT_DRAFT_NUM}"
NEW_DRAFT_NAME="${DRAFT_NAME_CLI:-${POSITIONAL[1]:-}}"

if [ -z "${NEW_DRAFT_NAME}" ]; then
    if has_gui; then
        NEW_DRAFT_NAME=$(zenity --entry \
            --title="Ars Arcanum — Initialize New Manuscript Draft" \
            --text="Enter draft identifier for '${MS_NAME}' (${BOOK_VOLUME_CLI}):" \
            --entry-text="${DEFAULT_NEW_DRAFT}" || true)
    fi
fi

if [ -z "${NEW_DRAFT_NAME}" ]; then
    if [ -t 0 ]; then
        read -rp "Enter new draft name [${DEFAULT_NEW_DRAFT}]: " NEW_DRAFT_NAME
        NEW_DRAFT_NAME="${NEW_DRAFT_NAME:-${DEFAULT_NEW_DRAFT}}"
    else
        NEW_DRAFT_NAME="${DEFAULT_NEW_DRAFT}"
    fi
fi

# Sanitize draft name
NEW_DRAFT_NAME="$(sanitize_name "${NEW_DRAFT_NAME}" "${DEFAULT_NEW_DRAFT}")"

NEW_DRAFT_DIR="${BOOK_DIR}/${NEW_DRAFT_NAME}"
if [ -d "${NEW_DRAFT_DIR}" ]; then
    echo "Error: Draft directory '${NEW_DRAFT_DIR}' already exists." >&2
    if has_gui; then
        zenity --error --title="Draft Exists" --text="Draft '${NEW_DRAFT_NAME}' already exists for volume ${BOOK_VOLUME_CLI}."
    fi
    exit 1
fi

# 4. Resolve source draft to copy from
SOURCE_DRAFT_NAME="${FROM_DRAFT_CLI:-${LATEST_DRAFT}}"

SOURCE_DIR=""
if [ -n "${SOURCE_DRAFT_NAME}" ] && [ "${SOURCE_DRAFT_NAME}" != "baseline" ]; then
    SOURCE_DIR="${BOOK_DIR}/${SOURCE_DRAFT_NAME}"
elif [ -d "${BOOK_DIR}/Draft-01" ]; then
    SOURCE_DIR="${BOOK_DIR}/Draft-01"
elif [ -d "${BOOK_DIR}/01_Act_I" ]; then
    SOURCE_DIR="${BOOK_DIR}"
fi

echo "Scaffolding manuscript draft '${NEW_DRAFT_NAME}' for ${MS_NAME} (${BOOK_VOLUME_CLI}) ..."

# 5. Establish Draft-01 baseline if migrating from flat structure
if [ ! -d "${BOOK_DIR}/Draft-01" ] && [ -d "${BOOK_DIR}/01_Act_I" ] && [ "${NEW_DRAFT_NAME}" != "Draft-01" ]; then
    echo "Establishing discrete 'Draft-01' baseline folder from existing scenes..."
    mkdir -p "${BOOK_DIR}/Draft-01"
    for act in "${BOOK_DIR}"/0[1-9]_Act_*; do
        if [ -d "${act}" ]; then
            cp -a "${act}" "${BOOK_DIR}/Draft-01/"
        fi
    done
    for md in "${BOOK_DIR}"/*.md; do
        if [ -f "${md}" ]; then
            cp -a "${md}" "${BOOK_DIR}/Draft-01/"
        fi
    done
    if [ "${SOURCE_DIR}" = "${BOOK_DIR}" ] || [ -z "${SOURCE_DIR}" ]; then
        SOURCE_DIR="${BOOK_DIR}/Draft-01"
    fi
fi

# 6. Fork / initialize draft directory
mkdir -p "${NEW_DRAFT_DIR}"

if [ -n "${SOURCE_DIR}" ] && [ -d "${SOURCE_DIR}" ]; then
    echo "Forking prose from source: $(basename "${SOURCE_DIR}") ..."
    # Copy all Act folders or Markdown files from source to new draft
    if [ "${SOURCE_DIR}" = "${BOOK_DIR}" ]; then
        # Copy Act folders from flat structure
        for act in "${BOOK_DIR}"/0[1-9]_Act_*; do
            if [ -d "${act}" ]; then
                cp -a "${act}" "${NEW_DRAFT_DIR}/"
            fi
        done
        for md in "${BOOK_DIR}"/*.md; do
            if [ -f "${md}" ]; then
                cp -a "${md}" "${NEW_DRAFT_DIR}/"
            fi
        done
    else
        cp -a "${SOURCE_DIR}/." "${NEW_DRAFT_DIR}/"
    fi
else
    # Scaffold fresh standard Act layout
    mkdir -p "${NEW_DRAFT_DIR}/01_Act_I"
    mkdir -p "${NEW_DRAFT_DIR}/02_Act_II"
    mkdir -p "${NEW_DRAFT_DIR}/03_Act_III"
    cat << 'EOF' > "${NEW_DRAFT_DIR}/01_Act_I/01_Chapter_01.md"
# Chapter 1: The Inciting Spark

Write your new draft opening scene here...
EOF
fi

# 6. Update manuscript.yaml manifest with active draft
MANIFEST="${MANUSCRIPT_DIR}/manuscript.yaml"
if [ -f "${MANIFEST}" ] && command -v python3 &>/dev/null; then
    python3 -c '
import sys, re
manifest_path = sys.argv[1]
draft_name = sys.argv[2]
try:
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
    if re.search(r"^active_draft:", content, flags=re.MULTILINE):
        new_content = re.sub(r"^active_draft:.*$", f"active_draft: \"{draft_name}\"", content, flags=re.MULTILINE)
    else:
        new_content = content.rstrip() + f"\nactive_draft: \"{draft_name}\"\n"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(new_content)
except Exception as e:
    sys.stderr.write(f"Warning: could not update manuscript.yaml: {e}\n")
' "${MANIFEST}" "${NEW_DRAFT_NAME}"
fi

# 7. Multi-tier Git versioning & milestone tagging
if command -v git &>/dev/null; then
    (
        cd "${BOOK_DIR}"
        if [ -d ".git" ]; then
            git add . 2>/dev/null || true
            git_commit_safe "Initialize ${NEW_DRAFT_NAME} milestone for ${BOOK_VOLUME_CLI}" || true
            git tag -a "v-${BOOK_VOLUME_CLI}-${NEW_DRAFT_NAME}" -m "Draft milestone: ${NEW_DRAFT_NAME}" 2>/dev/null || true
        fi
    )
    (
        cd "${MANUSCRIPT_DIR}"
        if [ -d ".git" ]; then
            git -c advice.addEmbeddedRepo=false add . 2>/dev/null || true
            git_commit_safe "Forked ${NEW_DRAFT_NAME} in ${BOOK_VOLUME_CLI}" || true
        fi
    )
fi

# 8. Build and synchronize DOCX files for new draft
if command -v python3 &>/dev/null && [ -f "${SCRIPT_DIR}/lib/docx_sync.py" ]; then
    python3 "${SCRIPT_DIR}/lib/docx_sync.py" build "${MANUSCRIPT_DIR}" --draft "${NEW_DRAFT_NAME}" 2>/dev/null || true
fi

MSG="Draft '${NEW_DRAFT_NAME}' successfully initialized for '${MS_NAME}'!\n\nVolume: ${BOOK_VOLUME_CLI}\nPath: ${NEW_DRAFT_DIR}\nActive Draft: Set to '${NEW_DRAFT_NAME}' in manifest.\nWord Processor DOCX: Synced in ${NEW_DRAFT_DIR}/${NEW_DRAFT_NAME}_Manuscript.docx"

echo -e "\n[✓] ${MSG}\n"

if has_gui; then
    zenity --info --title="Draft Initialized" --text="${MSG}" --width=450
fi

exit 0
