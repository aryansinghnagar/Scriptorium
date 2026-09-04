# Knowledge Base: Scriptorium Technical Ecosystem & Invariants

## 1. Operating System Details
- **Linux Mint XFCE**: Built on Ubuntu LTS base. Uses XFCE desktop environment. Extremely lightweight (idle RAM ~600MB - 900MB), lightning fast, highly customizable, and beginner friendly. Comes with LibreOffice pre-installed and Software Manager supporting both APT and Flatpak out of the box.
- **Debian 13 (Trixie) XFCE**: Even lighter minimal base. Suitable for advanced users seeking an ultra-stable Debian baseline (stable release, not rolling).

## 2. Application Architecture & Interoperability
| Application | Format & Storage | Protocol / Extension | Role |
| :--- | :--- | :--- | :--- |
| **Obsidian** | Local folder of standard `.md` files | Markdown + Wikilinks (`[[Link]]`) | World Bible, Lore, Character & Location Wiki |
| **novelWriter** | Local folder of `.nwd` documents under `content/` + XML index (`.nwx`, fileVersion 1.5) | Markdown with `@tag` metadata | Story outlining, chapter/scene drafting, project stats |
| **FocusWriter** | Plain `.txt` or `.md` | Plaintext | Fullscreen distraction-free draft sprints |
| **LibreOffice Writer** | `.odt`, `.docx` | OpenDocument / Office Open XML | Editor collaboration, redlining, track changes |
| **Calibre** | `.epub`, `.azw3`, `.mobi` | EPUB / Open Container Format | Ebook generation, DRM-free cataloging, e-reader sync |
| **Typst** | `.typ` source files | Typst modern markup | Publication-grade typesetting, micro-typography, print-ready PDF |
| **Pandoc** | Universal markup converter | AST translation | Bridges Markdown manuscript files directly into Typst/EPUB |
| **Déjà Dup** | Duplicity / Restic backend | Encrypted incremental backup archives | Automated local external USB and cloud backups |
| **Git** | Distributed VCS | Local `.git` repository | Version control snapshots and instant rollbacks |

## 3. Typst vs. LaTeX for Fiction
- **Compilation Speed**: Typst compiles sub-second (instantaneous) compared to LaTeX's multi-pass 5-15 second builds.
- **Syntax Simplicity**: Typst uses clean, Python/Markdown-inspired syntax without cryptic backslash cascades.
- **Page Layout**: Native support for running headers with chapter titles, alternating recto/verso margins, gutter binding allowances, and pure custom page numbers.

## 4. novelWriter Markdown Conventions
- Headers: `# Title`, `## Chapter`, `### Scene`, `#### Section`.
- Metadata tags:
  - `@pov: CharacterName`
  - `@focus: LocationName`
  - `@tag: PlotPoint`
  - `@status: Draft / Finished / Revision`
- NovelWriter stores scenes as individual `.nwd` files under `content/` (hex-handle filenames) with an XML manifest (`nwProject.nwx`, fileVersion 1.5) keeping chapter order. The repo's `templates/manuscript/nwProject.nwx` is a documented placeholder; `export_book.sh` reads the human-readable `Book-01/*/*.md` starters directly, so the placeholder never blocks PDF/EPUB output.

## 5. Script Safety Invariants (post-hardening, 2026-09-04)
- World names are whitelisted to `[A-Za-z0-9_-]`, max 64 chars (`init_world.sh`).
- Book titles are escaped for Typst string literals and mapped to collision-safe filename stems (`export_book.sh`).
- Temp dirs are `trap`-cleaned on EXIT; Typst failure never skips the Pandoc EPUB step.
- World discovery is NUL-safe (`find -print0`); Git commits fall back to an ephemeral `Scriptorium@localhost` identity so `set -e` never aborts silently.
- GUI detection covers X11 and Wayland (`DISPLAY` or `WAYLAND_DISPLAY` + Zenity).
- Setup detects `x86_64` vs `aarch64` for Typst, installs fonts tolerantly (Libertinus fallback), prefers Flatpak `--system` with `--user` fallback, and respects `xdg-user-dir DESKTOP`.
- Health check: `bash scripts/verify.sh` (syntax, JSON/XML, Pandoc→Typst smoke test, Typst compile if present, desktop entries).
