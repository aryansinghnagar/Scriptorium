#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Book Exporter
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
Scriptorium Book Exporter — compile a Markdown/novelWriter manuscript into
print-ready PDF (Typst) and distribution EPUB (Pandoc).

Usage:
  export_book.sh [WORLD_DIR] [OPTIONS]

Options:
  -t, --title TITLE        Book title (default: world manifest or directory name)
  -a, --author NAME        Author name (default: world manifest or "Author Name")
  -b, --book VOLUME        Book volume to export (e.g., Book-01, Book-02, or "all")
  -s, --paper-size SIZE    Paper trim size (us-trade, trade, pocket; default: us-trade)
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
PAPER_SIZE_CLI=""
POSITIONAL=()
while [ $# -gt 0 ]; do
    case "$1" in
        -t|--title)
            [ $# -ge 2 ] || { echo "Error: --title requires a value." >&2; exit 1; }
            BOOK_TITLE_CLI="$2"; shift 2 ;;
        -a|--author)
            [ $# -ge 2 ] || { echo "Error: --author requires a value." >&2; exit 1; }
            AUTHOR_NAME_CLI="$2"; shift 2 ;;
        -b|--book)
            [ $# -ge 2 ] || { echo "Error: --book requires a value." >&2; exit 1; }
            BOOK_VOLUME_CLI="$2"; shift 2 ;;
        -s|--paper-size)
            [ $# -ge 2 ] || { echo "Error: --paper-size requires a value." >&2; exit 1; }
            PAPER_SIZE_CLI="$2"; shift 2 ;;
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

WORLD_DIR="${POSITIONAL[0]:-}"

if [ -z "${WORLD_DIR}" ]; then
    if has_gui; then
        # F-06: pickers default to the canonical ~/Universes root, falling
        # back to the legacy ~/Worlds root when it does not exist yet.
        PICKER_ROOT="${UNIVERSES_BASE}"
        [ -d "${PICKER_ROOT}" ] || PICKER_ROOT="${WORLDS_BASE}"
        WORLD_DIR=$(zenity --file-selection --directory \
            --title="Scriptorium — Select World Directory to Export" \
            --filename="${PICKER_ROOT}/" || true)
    fi
fi

if [ -z "${WORLD_DIR}" ]; then
    echo "No world directory selected. Aborting."
    exit 3
fi

if [ -n "${WORLD_DIR}" ] && [ ! -d "${WORLD_DIR}" ]; then
    RESOLVED="$(resolve_world_dir "${WORLD_DIR}")"
    if [ -n "${RESOLVED}" ]; then
        WORLD_DIR="${RESOLVED}"
    fi
fi

if [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: Directory '${WORLD_DIR}' does not exist." >&2
    exit 1
fi

WORLD_NAME=$(basename "${WORLD_DIR}")
MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"
PUBLISHING_DIR="${WORLD_DIR}/04-Publishing"
mkdir -p "${PUBLISHING_DIR}"

echo "Compiling publication files for: ${WORLD_NAME} ..."

# 2. Extract title & author: CLI flags > world manifest (D-02) > GUI prompt > defaults
BOOK_TITLE="${BOOK_TITLE_CLI:-}"
AUTHOR_NAME="${AUTHOR_NAME_CLI:-}"

# Read world manifest (scriptorium.yaml) if present — flat `key: value` pairs only
MANIFEST="${WORLD_DIR}/scriptorium.yaml"
if [ -f "${MANIFEST}" ]; then
    if [ -z "${BOOK_TITLE}" ]; then
        BOOK_TITLE=$(sed -n -E 's/^title:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi
    if [ -z "${AUTHOR_NAME}" ]; then
        AUTHOR_NAME=$(sed -n -E 's/^author:[[:space:]]*"?([^"#]+)"?[[:space:]]*(#.*)?$/\1/p' "${MANIFEST}" | head -n 1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi
fi

if has_gui && { [ -z "${BOOK_TITLE}" ] || [ -z "${AUTHOR_NAME}" ]; }; then
    METADATA=$(zenity --forms --title="Scriptorium — Book Metadata" \
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

[ -z "${BOOK_TITLE}" ] && BOOK_TITLE="${WORLD_NAME}"
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
    elif [ -d "${MANUSCRIPT_DIR}/${BOOK_VOLUME_CLI}" ]; then
        SELECTED_VOLUME="${BOOK_VOLUME_CLI}"
    else
        echo "Error: Requested book volume '${BOOK_VOLUME_CLI}' not found in ${MANUSCRIPT_DIR}." >&2
        exit 1
    fi
elif [ ${#AVAILABLE_BOOKS[@]} -gt 1 ]; then
    if has_gui; then
        CHOICES=()
        for b in "${AVAILABLE_BOOKS[@]}"; do
            CHOICES+=("$b" "Volume $b")
        done
        CHOICES+=("All (Omnibus)" "Compile entire series omnibus")
        PICKED=$(zenity --list --title="Scriptorium — Select Volume to Export" \
            --text="Multiple book volumes detected in '${WORLD_NAME}'.\nWhich volume would you like to export?" \
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

if [ "${SELECTED_VOLUME}" = "all" ]; then
    find "${MANUSCRIPT_DIR}" -type f -name "*.md" ! -path "*/Outlines/*" \
        -path "*/Book-*/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
        echo "" >> "${COMBINED_MD}"
        strip_nw_tags "${file}" >> "${COMBINED_MD}"
        echo -e "\n" >> "${COMBINED_MD}"
    done
elif [ "${SELECTED_VOLUME}" != "single" ] && [ -d "${MANUSCRIPT_DIR}/${SELECTED_VOLUME}" ]; then
    find "${MANUSCRIPT_DIR}/${SELECTED_VOLUME}" -type f -name "*.md" ! -path "*/Outlines/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
        echo "" >> "${COMBINED_MD}"
        strip_nw_tags "${file}" >> "${COMBINED_MD}"
        echo -e "\n" >> "${COMBINED_MD}"
    done
elif [ -d "${MANUSCRIPT_DIR}" ]; then
    find "${MANUSCRIPT_DIR}" -type f -name "*.md" ! -path "*/Outlines/*" -print0 | sort -zV | while IFS= read -r -d '' file; do
        echo "" >> "${COMBINED_MD}"
        strip_nw_tags "${file}" >> "${COMBINED_MD}"
        echo -e "\n" >> "${COMBINED_MD}"
    done
fi

# Fallback if empty
if [ ! -s "${COMBINED_MD}" ]; then
    echo "No content found in manuscript. Creating sample chapter."
    cat << 'EOF' > "${COMBINED_MD}"
# Chapter 1: The Beginning

The morning sun broke across the ancient spires of the city, casting long amber shadows over the cobblestones. In the quiet sanctuary of the scriptorium, ink met parchment once again.

Every journey of a thousand leagues begins not with a step, but with the courage to envision the path ahead.
EOF
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
  publisher: "Scriptorium Press",
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
    if pandoc -f markdown-citations "${COMBINED_MD}" -t typst -o "${TEMP_WORK_DIR}/body.typ" 2>/dev/null; then
        cat "${TEMP_WORK_DIR}/body.typ" >> "${TYPST_SRC}"
    else
        sed -E -e 's/^#### +(.*)/==== \1/' -e 's/^### +(.*)/=== \1/' -e 's/^## +(.*)/== \1/' -e 's/^# +(.*)/= \1/' -e 's/^@([A-Za-z0-9_-]+):/\1:/' "${COMBINED_MD}" >> "${TYPST_SRC}"
    fi
else
    sed -E -e 's/^#### +(.*)/==== \1/' -e 's/^### +(.*)/=== \1/' -e 's/^## +(.*)/== \1/' -e 's/^# +(.*)/= \1/' -e 's/^@([A-Za-z0-9_-]+):/\1:/' "${COMBINED_MD}" >> "${TYPST_SRC}"
fi

# 5. Compile PDF with Typst (H3: safe filenames, D3: collision-safe)
if [ "${SELECTED_VOLUME}" != "all" ] && [ "${SELECTED_VOLUME}" != "single" ] && [ -n "${SELECTED_VOLUME}" ]; then
    SAFE_STEM="$(safe_filename "${BOOK_TITLE}_${SELECTED_VOLUME}")"
else
    SAFE_STEM="$(safe_filename "${BOOK_TITLE}")"
fi
PDF_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.pdf"
EPUB_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.epub"
if [ -e "${PDF_OUTPUT}" ] || [ -e "${EPUB_OUTPUT}" ]; then
    SAFE_STEM="${SAFE_STEM}_$(date +%Y%m%d-%H%M%S)"
    PDF_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.pdf"
    EPUB_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.epub"
    echo "[i] Output collision detected, using timestamped stem: ${SAFE_STEM}"
fi

EXIT_STATUS=0

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

# 6. Compile EPUB with Pandoc (AUD-02: Dedicated error trap & Cover auto-detection)
echo "Generating EPUB with Pandoc..."
if command -v pandoc &> /dev/null; then
    PANDOC_ARGS=(
        "${COMBINED_MD}"
        -o "${EPUB_OUTPUT}"
        --metadata title="${BOOK_TITLE}"
        --metadata author="${AUTHOR_NAME}"
        --toc
        --toc-depth=2
    )

    COVER_IMAGE=""
    if [ -f "${WORLD_DIR}/03-Art/cover.png" ]; then
        COVER_IMAGE="${WORLD_DIR}/03-Art/cover.png"
    elif [ -f "${WORLD_DIR}/03-Art/cover.jpg" ]; then
        COVER_IMAGE="${WORLD_DIR}/03-Art/cover.jpg"
    elif [ -f "${WORLD_DIR}/03-Art/cover.jpeg" ]; then
        COVER_IMAGE="${WORLD_DIR}/03-Art/cover.jpeg"
    fi

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

# Temp cleanup handled by EXIT trap (H4)

# 7. Notify user
MSG="Export Summary for: ${BOOK_TITLE}\n"
[ -f "${PDF_OUTPUT}" ] && MSG="${MSG}\n• Print PDF: ${PDF_OUTPUT}"
[ -f "${EPUB_OUTPUT}" ] && MSG="${MSG}\n• EPUB Ebook: ${EPUB_OUTPUT}"
[ "${EXIT_STATUS}" -ne 0 ] && MSG="${MSG}\n\n[!] Note: One or more formats had compilation warnings or errors."

if has_gui; then
    if [ -f "${PDF_OUTPUT}" ] && zenity --question --title="Export Summary" --text="${MSG}\n\nWould you like to open the PDF now?" --width=450; then
        xdg-open "${PDF_OUTPUT}" &
    else
        zenity --info --title="Export Summary" --text="${MSG}" --width=450
    fi
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi

exit "${EXIT_STATUS}"
