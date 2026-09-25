# Ars Arcanum Smart Typography Normalizer & Polish Engine (`docs/TYPOGRAPHY.md`)
> **Publication-Grade Punctuation, Quotes & Dash Normalization (PRO-104)** | Release v3.6.0

---

## 1. Overview & Publishing Standards

The **Typography Normalizer** (`arcanum typography` / `scripts/lib/typography_cleaner.py`) automates the transformation of raw draft prose into publication-standard literary typography.

Drafts typed in code editors, mobile note apps, or plain text often contain straight quotes (`"`, `'`), doubled hyphens (`--`), and raw dots (`...`). The Typography Normalizer converts these into elegant typographic glyphs while safeguarding markdown syntax, codeblocks, and frontmatter.

```mermaid
flowchart LR
    RAW["`**Raw Draft Text**<br>\"Hello,\" he said... 1914-1918--war`"] --> CLEANER{"Typography Engine"}
    CLEANER --> RULES["`**Smart Punctuation Rules**<br>• Curly Quotes & Apostrophes<br>• Em/En-Dashes<br>• Ellipses<br>• Whitespace Collapse`"]
    RULES --> POLISHED["`**Polished Literary Text**<br>“Hello,” he said… 1914–1918—war`"]
```

---

## 2. Transformation Rules Matrix

| Input Pattern | Typographic Replacement | Description |
| :--- | :--- | :--- |
| `"prose"` | `“prose”` | Smart opening & closing double curly quotes |
| `'prose'` | `‘prose’` | Smart opening & closing single curly quotes |
| `don't`, `it's` | `don’t`, `it’s` | Typographic apostrophes in contractions & possessives |
| `'tis`, `'90s` | `’tis`, `’90s` | Preserved leading apostrophes in archaic words & decades |
| `---` or `--` | `—` | Typographic em-dash for dramatic breaks |
| `1914-1918`, `pp. 20-25` | `1914–1918`, `pp. 20–25` | Typographic en-dash for numeric ranges and dates |
| `...` or `. . .` | `…` | Unicode horizontal ellipsis |
| `line   \n` | `line\n` | Strips trailing whitespace at line ends |
| `multiple   spaces` | `multiple spaces` | Collapses redundant consecutive whitespace inside sentences |

### Syntax Protection Invariants
- **YAML Frontmatter (`---`)**: Leading and trailing triple dashes around frontmatter blocks are never converted to em-dashes.
- **Codeblocks (```` ``` ````)**: Code blocks and indented code lines are completely excluded from typographic transformations.

---

## 3. CLI Invocation & Options

```bash
# Preview typographic changes with unified diff (dry-run mode)
arcanum typography ~/Manuscripts/My-Novel/Book-01/01_Chapter_01.md

# Apply changes in-place with automatic .bak backup files
arcanum typography ~/Manuscripts/My-Novel/Book-01/ -i

# Apply in-place without creating backup files
arcanum typography ~/Manuscripts/My-Novel/Book-01/ -i --no-backup

# Show full unified diffs for all modified files
arcanum typography ~/Manuscripts/My-Novel/Book-01/ --diff

# Output JSON summary statistics
arcanum typography ~/Manuscripts/My-Novel/Book-01/ --json
```

---

## 4. Safety & Idempotency Guarantees
- **Atomic File Writing**: In-place edits use `atomic_write()` to eliminate data loss risks during writes.
- **Strict Idempotency**: Running `arcanum typography` on an already-clean file produces 0 changes and identical output.
- **Zero-Pip Guarantee**: Built exclusively on standard library regex and difflib.
