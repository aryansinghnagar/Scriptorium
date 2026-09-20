#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Book Exporter
# Purpose: Compiles a novelWriter / Markdown manuscript into a print-ready PDF
#          (using Typst) and a distribution-ready EPUB (using Pandoc).
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Shared world discovery, resolution, and GUI helpers (Q-01)
# shellcheck source=scripts/lib/worlds.sh
source "${SCRIPT_DIR}/lib/worlds.sh"

# Escape backslashes and double quotes for Typst string literals (H3/D2: also strip CR/LF)
typst_escape() {
    local s="${1:-}"
    s="${s//$'\r'/ }"
    s="${s//$'\n'/ }"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    printf '%s' "$s"
}

# Produce a safe filename stem from an arbitrary book title (H3)
safe_filename() {
    local s="${1:-book}"
    # Keep alnum, space, dash, underscore; collapse spaces to underscores; trim
    s="$(printf '%s' "$s" | tr -cd 'A-Za-z0-9 _-' | sed -E 's/^ +//;s/ +$//;s/ +/_/g' | cut -c1-80)"
    [ -z "$s" ] && s="book"
    printf '%s' "$s"
}

usage() {
    cat << 'USAGE'
Ars Arcanum Book Exporter — compile a Markdown/novelWriter manuscript into
print-ready PDF (Typst), distribution EPUB (Pandoc), or submission DOCX (Pandoc).

Usage:
  export_book.sh [WORLD_DIR] [OPTIONS]

Options:
  -t, --title TITLE        Book title (default: world manifest or directory name)
  -a, --author NAME        Author name (default: world manifest or "Author Name")
  -b, --book VOLUME        Book volume to export (e.g., Book-01, Book-02, or "all")
  -d, --draft DRAFT        Draft version to export (e.g., Draft-01, Draft-02; default: active or latest)
  -s, --paper-size SIZE    Paper trim size (us-trade, trade, pocket; default: us-trade)
  -f, --format FORMAT      Output format: book (PDF+EPUB), submission (DOCX), all (default: book)
  --submission, --docx     Shortcut for --format submission
  -h, --help               Show this help and exit

Exit codes:
  0  success (at least one artifact produced, no compile errors)
  1  error (missing tools, compile failure, invalid directory)
  3  user abort (no world directory selected)

If WORLD_DIR is omitted, a directory picker is shown (GUI) or the script
aborts with exit code 3 (no GUI).
USAGE
}

# 1. Parse arguments (P-04: non-interactive use is first-class)
BOOK_TITLE_CLI=""
AUTHOR_NAME_CLI=""
BOOK_VOLUME_CLI=""
DRAFT_CLI=""
PAPER_SIZE_CLI=""
EXPORT_FORMAT_CLI="book"
POSITIONAL=()
while [ $# -gt 0 ]; do
    case "$1" in
        -t|--title)
            [ $# -ge 2 ] || { echo "Error: --title requires a value." >&2; exit 2; }
            BOOK_TITLE_CLI="$2"; shift 2 ;;
        -a|--author)
            [ $# -ge 2 ] || { echo "Error: --author requires a value." >&2; exit 2; }
            AUTHOR_NAME_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 2; }
            BOOK_VOLUME_CLI="$2"; shift 2 ;;
        -d|--draft)
            [ $# -ge 2 ] || { echo "Error: --draft requires a value." >&2; exit 2; }
            DRAFT_CLI="$2"; shift 2 ;;
        -s|--paper-size)
            [ $# -ge 2 ] || { echo "Error: --paper-size requires a value." >&2; exit 2; }
            PAPER_SIZE_CLI="$2"; shift 2 ;;
        -f|--format)
            [ $# -ge 2 ] || { echo "Error: --format requires a value." >&2; exit 2; }
            EXPORT_FORMAT_CLI="$2"; shift 2 ;;
        --submission|--docx)
            EXPORT_FORMAT_CLI="submission"; shift ;;
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

TARGET_DIR="${POSITIONAL[0]:-}"

if [ -z "${TARGET_DIR}" ]; then
    if has_gui; then
        PICKER_ROOT="${MANUSCRIPTS_BASE}"
        [ -d "${PICKER_ROOT}" ] || PICKER_ROOT="${UNIVERSES_BASE}"
        TARGET_DIR=$(zenity --file-selection --directory \
            --title="Ars Arcanum — Select Manuscript Directory to Export" \
            --filename="${PICKER_ROOT}/" || true)
    fi
fi

if [ -z "${TARGET_DIR}" ]; then
    echo "No manuscript directory selected. Aborting."
    exit 3
fi

if [ -n "${TARGET_DIR}" ] && [ ! -d "${TARGET_DIR}" ]; then
    RESOLVED="$(resolve_target_dir "${TARGET_DIR}")"
    if [ -n "${RESOLVED}" ]; then
        TARGET_DIR="${RESOLVED}"
    fi
fi

if [ ! -d "${TARGET_DIR}" ]; then
    echo "Error: Directory '${TARGET_DIR}' does not exist." >&2
    exit 2
fi

PROJECT_NAME=$(basename "${TARGET_DIR}")
if [ -d "${TARGET_DIR}/01-Manuscript" ]; then
    MANUSCRIPT_DIR="${TARGET_DIR}/01-Manuscript"
    PUBLISHING_DIR="${TARGET_DIR}/04-Publishing"
else
    MANUSCRIPT_DIR="${TARGET_DIR}"
    if [ -d "${TARGET_DIR}/04-Publishing" ]; then
        PUBLISHING_DIR="${TARGET_DIR}/04-Publishing"
    else
        PUBLISHING_DIR="${TARGET_DIR}/Exports"
    fi
fi
mkdir -p "${PUBLISHING_DIR}"

echo "Compiling publication files for: ${PROJECT_NAME} ..."

# 2. Extract title & author: CLI flags > manuscript/world manifest > GUI prompt > defaults
BOOK_TITLE="${BOOK_TITLE_CLI:-}"
AUTHOR_NAME="${AUTHOR_NAME_CLI:-}"

# Read manifest (manuscript.yaml, arcanum.yaml, or scriptorium.yaml) if present — flat `key: value` pairs only
MANIFEST="${TARGET_DIR}/manuscript.yaml"
[ -f "${MANIFEST}" ] || MANIFEST="${TARGET_DIR}/arcanum.yaml"
[ -f "${MANIFEST}" ] || MANIFEST="${TARGET_DIR}/scriptorium.yaml"
ACTIVE_DRAFT_CONFIG=""
if [ -f "${MANIFEST}" ]; then
    if [ -z "${BOOK_TITLE}" ]; then
        BOOK_TITLE=$(sed -n -E 's/^title:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi
    if [ -z "${AUTHOR_NAME}" ]; then
        AUTHOR_NAME=$(sed -n -E 's/^author:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi
    ACTIVE_DRAFT_CONFIG=$(sed -n -E 's/^active_draft:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
fi

if has_gui && { [ -z "${BOOK_TITLE}" ] || [ -z "${AUTHOR_NAME}" ]; }; then
    METADATA=$(zenity --forms --title="Ars Arcanum — Book Metadata" \
        --text="Enter metadata for the compiled book:" \
        --add-entry="Book Title" \
        --add-entry="Author Name" || true)
    if [ -n "${METADATA}" ]; then
        # Split on first '|' so titles containing '|' degrade gracefully (H3)
        METADATA_TITLE="${METADATA%%|*}"
        if [[ "${METADATA}" == *"|"* ]]; then
            METADATA_AUTHOR="${METADATA#*|}"
        else
            METADATA_AUTHOR=""
        fi
        [ -z "${BOOK_TITLE}" ] && [ -n "${METADATA_TITLE}" ] && BOOK_TITLE="${METADATA_TITLE}"
        [ -z "${AUTHOR_NAME}" ] && [ -n "${METADATA_AUTHOR}" ] && AUTHOR_NAME="${METADATA_AUTHOR}"
    fi
fi

[ -z "${BOOK_TITLE}" ] && BOOK_TITLE="${PROJECT_NAME}"
[ -z "${AUTHOR_NAME}" ] && AUTHOR_NAME="Author Name"

TEMP_WORK_DIR=$(mktemp -d)
# Ensure temp cleanup even if typst/pandoc fail (H4)
trap 'rm -rf "${TEMP_WORK_DIR:-}"' EXIT
COMBINED_MD="${TEMP_WORK_DIR}/manuscript.md"
TYPST_SRC="${TEMP_WORK_DIR}/book.typ"

# 3. Discover and Select Manuscript Volume(s)
AVAILABLE_BOOKS=()
if [ -d "${MANUSCRIPT_DIR}" ]; then
    while IFS= read -r -d '' bdir; do
        AVAILABLE_BOOKS+=("$(basename "$bdir")")
    done < <(find "${MANUSCRIPT_DIR}" -mindepth 1 -maxdepth 1 -type d -name "Book-*" -print0 2>/dev/null | sort -zV)
fi

SELECTED_VOLUME=""
if [ -n "${BOOK_VOLUME_CLI}" ]; then
    if [ "${BOOK_VOLUME_CLI}" = "all" ] || [ "${BOOK_VOLUME_CLI}" = "ALL" ] || [ "${BOOK_VOLUME_CLI}" = "omnibus" ]; then
        SELECTED_VOLUME="all"
    else
        # Reject path traversal components (Issue 5)
        if [[ "${BOOK_VOLUME_CLI}" == *".."* ]] || [[ "${BOOK_VOLUME_CLI}" == *"/"* ]] || [[ "${BOOK_VOLUME_CLI}" == *"\\"* ]]; then
            echo "Error: Invalid volume name '${BOOK_VOLUME_CLI}'. Volume name cannot contain path traversal components ('..') or slashes." >&2
            exit 2
        fi
        if [ -d "${MANUSCRIPT_DIR}/${BOOK_VOLUME_CLI}" ]; then
            SELECTED_VOLUME="${BOOK_VOLUME_CLI}"
        else
            echo "Error: Requested book volume '${BOOK_VOLUME_CLI}' not found in ${MANUSCRIPT_DIR}." >&2
            exit 2
        fi
    fi
elif [ ${#AVAILABLE_BOOKS[@]} -gt 1 ]; then
    if has_gui; then
        CHOICES=()
        for b in "${AVAILABLE_BOOKS[@]}"; do
            CHOICES+=("$b" "Volume $b")
        done
        CHOICES+=("All (Omnibus)" "Compile entire series omnibus")
        PICKED=$(zenity --list --title="Ars Arcanum — Select Volume to Export" \
            --text="Multiple book volumes detected in '${PROJECT_NAME}'.\nWhich volume would you like to export?" \
            --column="Volume" --column="Description" \
            --hide-column=2 \
            --width=420 --height=280 \
            "${CHOICES[@]}" || true)
        if [ "$PICKED" = "All (Omnibus)" ]; then
            SELECTED_VOLUME="all"
        elif [ -n "$PICKED" ]; then
            SELECTED_VOLUME="$PICKED"
        else
            echo "Volume selection aborted." >&2
            exit 3
        fi
    else
        # CLI non-interactive default: Book-01
        SELECTED_VOLUME="${AVAILABLE_BOOKS[0]}"
    fi
elif [ ${#AVAILABLE_BOOKS[@]} -eq 1 ]; then
    SELECTED_VOLUME="${AVAILABLE_BOOKS[0]}"
else
    SELECTED_VOLUME="single"
fi

echo "Collecting manuscript scenes for: ${SELECTED_VOLUME}..."
: > "${COMBINED_MD}"

# novelWriter tag stripping: ANY line-start `@tag:` is novelWriter metadata
# (novelWriter supports @pov, @char, @plot, @location, @time, @object, @entity
# AND user-defined tags). Strips metadata and comment lines.
strip_nw_tags() {
    sed -E '/^@[A-Za-z0-9_-]+:/d; /^%/d' "$1"
}

# Resolve which directory within a book volume contains the active or desired draft
resolve_volume_content_dir() {
    local vdir="$1"
    local req_draft="${DRAFT_CLI:-}"
    
    local drafts=()
    while IFS= read -r -d '' d; do
        drafts+=("$(basename "$d")")
    done < <(find "$vdir" -mindepth 1 -maxdepth 1 -type d -name "Draft-*" -print0 2>/dev/null | sort -zV)

    if [ ${#drafts[@]} -eq 0 ]; then
        printf '%s' "$vdir"
        return
    fi

    if [ -n "$req_draft" ]; then
        if [ -d "$vdir/$req_draft" ]; then
            printf '%s' "$vdir/$req_draft"
            return
        else
            echo "[!] Warning: Draft '${req_draft}' not found in $(basename "$vdir"), falling back to active/latest draft." >&2
        fi
    fi

    if [ -n "${ACTIVE_DRAFT_CONFIG:-}" ] && [ -d "$vdir/${ACTIVE_DRAFT_CONFIG}" ]; then
        printf '%s' "$vdir/${ACTIVE_DRAFT_CONFIG}"
        return
    fi

    local latest_idx=$((${#drafts[@]} - 1))
    local latest_draft="${drafts[$latest_idx]}"
    printf '%s' "$vdir/$latest_draft"
}

if [ "${SELECTED_VOLUME}" = "all" ]; then
    if [ ${#AVAILABLE_BOOKS[@]} -gt 0 ]; then
        for bvol in "${AVAILABLE_BOOKS[@]}"; do
            bpath="${MANUSCRIPT_DIR}/${bvol}"
            cpath="$(resolve_volume_content_dir "${bpath}")"
            find "${cpath}" -type f -name "*.md" ! -path "*/Outlines/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
                echo "" >> "${COMBINED_MD}"
                strip_nw_tags "${file}" >> "${COMBINED_MD}"
                echo -e "\n" >> "${COMBINED_MD}"
            done
        done
    else
        find "${MANUSCRIPT_DIR}" -type f -name "*.md" ! -path "*/Outlines/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
            echo "" >> "${COMBINED_MD}"
            strip_nw_tags "${file}" >> "${COMBINED_MD}"
            echo -e "\n" >> "${COMBINED_MD}"
        done
    fi
elif [ "${SELECTED_VOLUME}" != "single" ] && [ -d "${MANUSCRIPT_DIR}/${SELECTED_VOLUME}" ]; then
    cpath="$(resolve_volume_content_dir "${MANUSCRIPT_DIR}/${SELECTED_VOLUME}")"
    find "${cpath}" -type f -name "*.md" ! -path "*/Outlines/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
        echo "" >> "${COMBINED_MD}"
        strip_nw_tags "${file}" >> "${COMBINED_MD}"
        echo -e "\n" >> "${COMBINED_MD}"
    done
elif [ -d "${MANUSCRIPT_DIR}" ]; then
    cpath="$(resolve_volume_content_dir "${MANUSCRIPT_DIR}")"
    find "${cpath}" -type f -name "*.md" ! -path "*/Outlines/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
        echo "" >> "${COMBINED_MD}"
        strip_nw_tags "${file}" >> "${COMBINED_MD}"
        echo -e "\n" >> "${COMBINED_MD}"
    done
fi

# F-06: hard-fail on empty manuscripts. The previous behavior fabricated a
# sample chapter and compiled it into a real PDF/EPUB, which masked
# wrong-world selection mistakes and could ship filler prose into a
# publishable artifact.
if [ ! -s "${COMBINED_MD}" ]; then
    echo "Error: no manuscript content found for '${SELECTED_VOLUME}' under ${MANUSCRIPT_DIR}." >&2
    echo "       Add chapters first (arcanum add-book <world>, novelWriter, or plain .md files)." >&2
    exit 1
fi

# 4. Generate Typst Book File
TEMPLATE_FILE="${PROJECT_ROOT}/templates/typst/book_template.typ"
if [ ! -f "${TEMPLATE_FILE}" ]; then
    TEMPLATE_FILE="${PUBLISHING_DIR}/typst-template/book_template.typ"
fi

# Escape user input for Typst string literals (H3)
ESC_TITLE="$(typst_escape "${BOOK_TITLE}")"
ESC_AUTHOR="$(typst_escape "${AUTHOR_NAME}")"

# Resolve and validate paper size
PAPER_SIZE="${PAPER_SIZE_CLI:-us-trade}"
case "${PAPER_SIZE}" in
    us-trade|trade|pocket) ;;
    *)
        echo "[!] Warning: Unknown paper size '${PAPER_SIZE}', defaulting to 'us-trade'." >&2
        PAPER_SIZE="us-trade"
        ;;
esac

cat << EOF > "${TYPST_SRC}"
#import "book_template.typ": book-layout, scene-break, unindented

#show: book-layout.with(
  title: "${ESC_TITLE}",
  author: "${ESC_AUTHOR}",
  subtitle: "",
  year: "$(date +%Y)",
  isbn: "978-0-000000-00-0",
  publisher: "Ars Arcanum Press",
  paper-size: "${PAPER_SIZE}", // Options: "us-trade" (6x9in), "trade" (5.5x8.5in), "pocket" (5x8in)
  body-font: "Linux Libertine",
)

EOF

# Copy template into work dir
if [ -f "${TEMPLATE_FILE}" ]; then
    cp "${TEMPLATE_FILE}" "${TEMP_WORK_DIR}/book_template.typ"
else
    # Fallback minimal template if missing
    cat << 'EOF' > "${TEMP_WORK_DIR}/book_template.typ"
#let book-layout(
  title: "",
  author: "",
  subtitle: "",
  year: "",
  isbn: "",
  publisher: "",
  paper-size: "us-trade",
  body-font: "Linux Libertine",
  body
) = {
  let (width, height) = if paper-size == "trade" {
    (5.5in, 8.5in)
  } else if paper-size == "pocket" {
    (5in, 8in)
  } else {
    (6in, 9in)
  }
  set document(title: title, author: author)
  set page(width: width, height: height, margin: (inside: 0.8in, outside: 0.65in, top: 0.75in, bottom: 0.75in))
  set text(font: body-font, size: 10.5pt, lang: "en")
  set par(justify: true, first-line-indent: 1.25em, leading: 0.7em)
  
  // Title Page
  align(center + horizon)[
    #text(size: 24pt, weight: "bold", title)
    #v(1em)
    #text(size: 14pt, style: "italic", author)
  ]
  pagebreak()
  body
}
#let chapter-title(title) = {
  pagebreak()
  v(2in)
  align(center)[#text(size: 18pt, weight: "bold", title)]
  v(1in)
}
EOF
fi

# Convert Markdown headings into Typst markup (M1)
# Prefer Pandoc's native Typst writer when available; fall back to sed for
# # / ## / ### levels. Handles the common novel structure without mangling body text.
# P-02: `-f markdown-citations` disables pandoc's `@key` citation syntax so a
# stray `@word` in prose can never compile into a fatal #cite(...) call.
if command -v pandoc &> /dev/null; then
    if pandoc -f markdown-citations+smart "${COMBINED_MD}" -t typst -o "${TEMP_WORK_DIR}/body.typ" 2>/dev/null; then
        cat "${TEMP_WORK_DIR}/body.typ" >> "${TYPST_SRC}"
    else
        sed -E -e 's/^#### +(.*)/==== \1/' -e 's/^### +(.*)/=== \1/' -e 's/^## +(.*)/== \1/' -e 's/^# +(.*)/= \1/' -e 's/^@([A-Za-z0-9_-]+):/\1:/' "${COMBINED_MD}" >> "${TYPST_SRC}"
    fi
else
    sed -E -e 's/^#### +(.*)/==== \1/' -e 's/^### +(.*)/=== \1/' -e 's/^## +(.*)/== \1/' -e 's/^# +(.*)/= \1/' -e 's/^@([A-Za-z0-9_-]+):/\1:/' "${COMBINED_MD}" >> "${TYPST_SRC}"
fi

BUILD_PDF=0
BUILD_EPUB=0
BUILD_DOCX=0

case "${EXPORT_FORMAT_CLI}" in
    book)
        BUILD_PDF=1; BUILD_EPUB=1 ;;
    submission|docx|standard)
        BUILD_DOCX=1 ;;
    all)
        BUILD_PDF=1; BUILD_EPUB=1; BUILD_DOCX=1 ;;
    *)
        echo "[!] Warning: Unknown export format '${EXPORT_FORMAT_CLI}', defaulting to 'book'." >&2
        BUILD_PDF=1; BUILD_EPUB=1 ;;
esac

# 5. Output Filename Stems (H3: safe filenames, D3: collision-safe)
if [ "${SELECTED_VOLUME}" != "all" ] && [ "${SELECTED_VOLUME}" != "single" ] && [ -n "${SELECTED_VOLUME}" ]; then
    SAFE_STEM="$(safe_filename "${BOOK_TITLE}_${SELECTED_VOLUME}")"
else
    SAFE_STEM="$(safe_filename "${BOOK_TITLE}")"
fi
PDF_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.pdf"
EPUB_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.epub"
DOCX_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}_Submission.docx"
if [ -e "${PDF_OUTPUT}" ] || [ -e "${EPUB_OUTPUT}" ] || [ -e "${DOCX_OUTPUT}" ]; then
    SAFE_STEM="${SAFE_STEM}_$(date +%Y%m%d-%H%M%S)"
    PDF_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.pdf"
    EPUB_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.epub"
    DOCX_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}_Submission.docx"
    echo "[i] Output collision detected, using timestamped stem: ${SAFE_STEM}"
fi

EXIT_STATUS=0

# 6. Compile PDF with Typst
if [ "${BUILD_PDF}" -eq 1 ]; then
    echo "Rendering print PDF with Typst..."
    if command -v typst &> /dev/null; then
        if (cd "${TEMP_WORK_DIR}" && typst compile "${TYPST_SRC}" "${PDF_OUTPUT}"); then
            if [ -s "${PDF_OUTPUT}" ]; then
                echo "[✓] PDF generated at: ${PDF_OUTPUT}"
            else
                echo "[!] Typst compile finished but PDF artifact is empty (0 bytes)." >&2
                EXIT_STATUS=1
            fi
        else
            echo "[!] Typst compile failed. See ${TYPST_SRC} and ${TEMP_WORK_DIR}/book_template.typ for details." >&2
            EXIT_STATUS=1
        fi
    else
        echo "[!] Typst not found. Skipping PDF generation." >&2
        EXIT_STATUS=1
    fi
fi

# 7. Compile EPUB with Pandoc (AUD-02: Dedicated error trap & Cover auto-detection)
if [ "${BUILD_EPUB}" -eq 1 ]; then
    echo "Generating EPUB with Pandoc..."
    if command -v pandoc &> /dev/null; then
        PANDOC_ARGS=(
            "${COMBINED_MD}"
            -o "${EPUB_OUTPUT}"
            -f markdown-citations+smart
            --metadata title="${BOOK_TITLE}"
            --metadata author="${AUTHOR_NAME}"
            --toc
            --toc-depth=2
        )

        COVER_IMAGE=""
        for cdir in "${PUBLISHING_DIR}" "${TARGET_DIR}/03-Art" "${TARGET_DIR}/Art" "${TARGET_DIR}"; do
            for ext in png jpg jpeg PNG JPG JPEG; do
                if [ -f "${cdir}/cover.${ext}" ]; then
                    COVER_IMAGE="${cdir}/cover.${ext}"
                    break 2
                fi
            done
        done

        if [ -n "${COVER_IMAGE}" ]; then
            echo "[i] Auto-detected EPUB cover image: ${COVER_IMAGE}"
            PANDOC_ARGS+=(--epub-cover-image="${COVER_IMAGE}")
        fi

        if pandoc "${PANDOC_ARGS[@]}" 2>"${TEMP_WORK_DIR}/pandoc_err.log"; then
            if [ -s "${EPUB_OUTPUT}" ]; then
                echo "[✓] EPUB generated at: ${EPUB_OUTPUT}"
            else
                echo "[!] Pandoc completed but EPUB artifact is empty (0 bytes)." >&2
                EXIT_STATUS=1
            fi
        else
            echo "[!] Pandoc EPUB export failed." >&2
            if [ -s "${TEMP_WORK_DIR}/pandoc_err.log" ]; then
                cat "${TEMP_WORK_DIR}/pandoc_err.log" >&2
            fi
            EXIT_STATUS=1
        fi
    else
        echo "[!] Pandoc not found. Skipping EPUB generation." >&2
        EXIT_STATUS=1
    fi
fi

# 8. Compile Standard Manuscript Submission Format (.docx) with Pandoc / native engine
if [ "${BUILD_DOCX}" -eq 1 ]; then
    echo "Generating Standard Manuscript Submission document (.docx)..."
    DOCX_COMPILED=0
    if command -v pandoc &> /dev/null; then
        PANDOC_DOCX_ARGS=(
            -f markdown-citations+smart
            "${COMBINED_MD}"
            -t docx
            -o "${DOCX_OUTPUT}"
            --metadata title="${BOOK_TITLE}"
            --metadata author="${AUTHOR_NAME}"
            --metadata date="$(date +%Y-%m-%d)"
        )

        if pandoc "${PANDOC_DOCX_ARGS[@]}" 2>"${TEMP_WORK_DIR}/pandoc_docx_err.log"; then
            if [ -s "${DOCX_OUTPUT}" ]; then
                echo "[✓] Submission manuscript generated at: ${DOCX_OUTPUT}"
                DOCX_COMPILED=1
            fi
        fi
    fi

    # Native Python OpenXML builder fallback if pandoc is missing or didn't run
    if [ "${DOCX_COMPILED}" -eq 0 ] && command -v python3 &>/dev/null && [ -f "${SCRIPT_DIR}/lib/docx_sync.py" ]; then
        if python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '${SCRIPT_DIR}/lib')
from docx_sync import parse_markdown_to_paragraphs, build_docx_package, get_docx_config

md_text = Path('${COMBINED_MD}').read_text(encoding='utf-8')
paragraphs = parse_markdown_to_paragraphs(md_text)
config = get_docx_config()
build_docx_package(Path('${DOCX_OUTPUT}'), paragraphs, config, title='${BOOK_TITLE}', author='${AUTHOR_NAME}', is_full_manuscript=True)
" 2>/dev/null; then
            if [ -s "${DOCX_OUTPUT}" ]; then
                echo "[✓] Submission manuscript generated with native engine at: ${DOCX_OUTPUT}"
                DOCX_COMPILED=1
            fi
        fi
    fi

    if [ "${DOCX_COMPILED}" -eq 0 ]; then
        echo "[!] DOCX export failed or generator missing." >&2
        EXIT_STATUS=1
    fi
fi

# 9. Notify user
MSG="Export Summary for: ${BOOK_TITLE}\n"
[ "${BUILD_PDF}" -eq 1 ] && [ -f "${PDF_OUTPUT}" ] && MSG="${MSG}\n• Print PDF: ${PDF_OUTPUT}"
[ "${BUILD_EPUB}" -eq 1 ] && [ -f "${EPUB_OUTPUT}" ] && MSG="${MSG}\n• EPUB Ebook: ${EPUB_OUTPUT}"
[ "${BUILD_DOCX}" -eq 1 ] && [ -f "${DOCX_OUTPUT}" ] && MSG="${MSG}\n• Standard Submission (.docx): ${DOCX_OUTPUT}"
[ "${EXIT_STATUS}" -ne 0 ] && MSG="${MSG}\n\n[!] Note: One or more formats had compilation warnings or errors."

if has_gui; then
    if [ -f "${PDF_OUTPUT}" ] && zenity --question --title="Export Summary" --text="${MSG}\n\nWould you like to open the PDF now?" --width=450; then
        xdg-open "${PDF_OUTPUT}" &
    elif [ -f "${DOCX_OUTPUT}" ] && [ "${BUILD_PDF}" -eq 0 ] && zenity --question --title="Export Summary" --text="${MSG}\n\nWould you like to open the Submission document now?" --width=450; then
        xdg-open "${DOCX_OUTPUT}" &
    else
        zenity --info --title="Export Summary" --text="${MSG}" --width=450
    fi
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit "${EXIT_STATUS}"
