#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Book Exporter
# Purpose: Compiles a novelWriter / Markdown manuscript into a print-ready PDF
#          (using Typst) and a distribution-ready EPUB (using Pandoc).
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORLDS_BASE="${HOME}/Worlds"

# GUI detection works on both X11 and Wayland (M7)
has_gui() {
    { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; } && command -v zenity &> /dev/null
}

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

# 1. Select World / Manuscript Folder
WORLD_DIR="${1:-}"

if [ -z "${WORLD_DIR}" ]; then
    if has_gui; then
        WORLD_DIR=$(zenity --file-selection --directory \
            --title="Scriptorium — Select World Directory to Export" \
            --filename="${WORLDS_BASE}/" || true)
    fi
fi

if [ -z "${WORLD_DIR}" ]; then
    echo "No world directory selected. Aborting."
    exit 0
fi

if [ ! -d "${WORLD_DIR}" ]; then
    echo "Error: Directory '${WORLD_DIR}' does not exist."
    exit 1
fi

WORLD_NAME=$(basename "${WORLD_DIR}")
MANUSCRIPT_DIR="${WORLD_DIR}/01-Manuscript"
PUBLISHING_DIR="${WORLD_DIR}/04-Publishing"
mkdir -p "${PUBLISHING_DIR}"

echo "Compiling publication files for: ${WORLD_NAME} ..."

# 2. Extract title & author from settings or prompt
BOOK_TITLE="${WORLD_NAME}"
AUTHOR_NAME="Author Name"

if has_gui; then
    METADATA=$(zenity --forms --title="Scriptorium — Book Metadata" \
        --text="Enter metadata for the compiled book:" \
        --add-entry="Book Title" \
        --add-entry="Author Name" || true)
    if [ -n "${METADATA}" ]; then
        # Split on first '|' so titles containing '|' degrade gracefully (H3)
        BOOK_TITLE="${METADATA%%|*}"
        if [[ "${METADATA}" == *"|"* ]]; then
            AUTHOR_NAME="${METADATA#*|}"
        else
            AUTHOR_NAME=""
        fi
        [ -z "${BOOK_TITLE}" ] && BOOK_TITLE="${WORLD_NAME}"
        [ -z "${AUTHOR_NAME}" ] && AUTHOR_NAME="Author Name"
    fi
fi

TEMP_WORK_DIR=$(mktemp -d)
# Ensure temp cleanup even if typst/pandoc fail (H4)
trap 'rm -rf "${TEMP_WORK_DIR:-}"' EXIT
COMBINED_MD="${TEMP_WORK_DIR}/manuscript.md"
TYPST_SRC="${TEMP_WORK_DIR}/book.typ"

# 3. Collect and concatenate all manuscript chapter files
echo "Collecting manuscript scenes..."
> "${COMBINED_MD}"

# Find all markdown files in 01-Manuscript/Book-01 sorted by natural path
if [ -d "${MANUSCRIPT_DIR}/Book-01" ]; then
    find "${MANUSCRIPT_DIR}/Book-01" -type f -name "*.md" | sort -V | while IFS= read -r file; do
        # Strip novelWriter metadata tags (@pov, @focus, @tag, @status, % comments) for clean publication
        echo "" >> "${COMBINED_MD}"
        sed -E '/^@(pov|focus|tag|status|char|location|object):/d; /^%/d' "${file}" >> "${COMBINED_MD}"
        echo -e "\n" >> "${COMBINED_MD}"
    done
elif [ -d "${MANUSCRIPT_DIR}" ]; then
    find "${MANUSCRIPT_DIR}" -type f -name "*.md" ! -path "*/Outlines/*" | sort -V | while IFS= read -r file; do
        echo "" >> "${COMBINED_MD}"
        sed -E '/^@(pov|focus|tag|status|char|location|object):/d; /^%/d' "${file}" >> "${COMBINED_MD}"
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

cat << EOF > "${TYPST_SRC}"
#import "book_template.typ": book-layout, scene-break

#show: book-layout.with(
  title: "${ESC_TITLE}",
  author: "${ESC_AUTHOR}",
  subtitle: "",
  year: "$(date +%Y)",
  isbn: "978-0-000000-00-0",
  publisher: "Scriptorium Press",
  paper-size: "us-trade", // Options: "us-trade" (6x9in), "trade" (5.5x8.5in), "pocket" (5x8in)
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
  set document(title: title, author: author)
  set page(paper: "us-trade", margin: (inside: 0.8in, outside: 0.65in, top: 0.75in, bottom: 0.75in))
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
if command -v pandoc &> /dev/null; then
    if pandoc "${COMBINED_MD}" -t typst -o "${TEMP_WORK_DIR}/body.typ" 2>/dev/null; then
        cat "${TEMP_WORK_DIR}/body.typ" >> "${TYPST_SRC}"
    else
        sed -E -e 's/^#### +(.*)/==== \1/' -e 's/^### +(.*)/=== \1/' -e 's/^## +(.*)/== \1/' -e 's/^# +(.*)/= \1/' "${COMBINED_MD}" >> "${TYPST_SRC}"
    fi
else
    sed -E -e 's/^#### +(.*)/==== \1/' -e 's/^### +(.*)/=== \1/' -e 's/^## +(.*)/== \1/' -e 's/^# +(.*)/= \1/' "${COMBINED_MD}" >> "${TYPST_SRC}"
fi

# 5. Compile PDF with Typst (H3: safe filenames, D3: collision-safe)
SAFE_STEM="$(safe_filename "${BOOK_TITLE}")"
PDF_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.pdf"
EPUB_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.epub"
if [ -e "${PDF_OUTPUT}" ] || [ -e "${EPUB_OUTPUT}" ]; then
    SAFE_STEM="${SAFE_STEM}_$(date +%Y%m%d-%H%M%S)"
    PDF_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.pdf"
    EPUB_OUTPUT="${PUBLISHING_DIR}/${SAFE_STEM}.epub"
    echo "[i] Output collision detected, using timestamped stem: ${SAFE_STEM}"
fi

echo "Rendering print PDF with Typst..."
if command -v typst &> /dev/null; then
    if (cd "${TEMP_WORK_DIR}" && typst compile "${TYPST_SRC}" "${PDF_OUTPUT}"); then
        echo "[✓] PDF generated at: ${PDF_OUTPUT}"
    else
        echo "[!] Typst compile failed. See ${TYPST_SRC} and ${TEMP_WORK_DIR}/book_template.typ for details."
    fi
else
    echo "[!] Typst not found. Skipping PDF generation."
fi

# 6. Compile EPUB with Pandoc
if command -v pandoc &> /dev/null; then
    echo "Generating EPUB with Pandoc..."
    pandoc "${COMBINED_MD}" -o "${EPUB_OUTPUT}" \
        --metadata title="${BOOK_TITLE}" \
        --metadata author="${AUTHOR_NAME}" \
        --toc --toc-depth=2
    echo "[✓] EPUB generated at: ${EPUB_OUTPUT}"
fi

# Temp cleanup handled by EXIT trap (H4)

# 7. Notify user
MSG="Export Complete!\n\n• Print PDF: ${PDF_OUTPUT}\n• EPUB Ebook: ${EPUB_OUTPUT}"

if has_gui; then
    if [ -f "${PDF_OUTPUT}" ] && zenity --question --title="Export Complete" --text="${MSG}\n\nWould you like to open the PDF now?" --width=450; then
        xdg-open "${PDF_OUTPUT}" &
    elif [ ! -f "${PDF_OUTPUT}" ]; then
        zenity --info --title="Export Complete" --text="${MSG}" --width=450
    fi
else
    echo -e "\n============================================================"
    echo -e "${MSG}"
    echo "============================================================"
fi
