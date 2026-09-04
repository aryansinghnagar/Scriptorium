# Architecture Decision Records (ADRs): Scriptorium

## ADR-001: Selection of Linux Mint XFCE as Primary Distribution
- **Context**: The author needs a stable, lightweight, zero-maintenance operating system that runs smoothly on reference Intel Core i5 laptops, dual-boots easily with Windows, and requires no terminal interaction for daily tasks.
- **Decision**: Adopt Linux Mint XFCE edition.
- **Alternatives Considered**:
  - *Arch / Custom Minimal Distro*: High setup effort, risk of breakage during updates.
  - *Ubuntu Desktop (GNOME)*: Heavier resource consumption (~1.8 GB idle RAM) and snap dependency.
  - *Debian 13 XFCE*: Excellent lightweight alternative, but requires slightly more initial configuration for non-free codecs and Flatpak repositories. Documented as secondary option.
- **Consequences**: Out-of-the-box GUI software manager, pre-installed LibreOffice, native dual-boot installer, low RAM usage (~700MB idle).

## ADR-002: Plain Markdown Storage vs Proprietary Database (Scrivener / Notion)
- **Context**: Authors frequently lose access to work when proprietary software changes subscription models or becomes abandoned.
- **Decision**: Store all lore, characters, outlines, and manuscript prose in plain `.md` files in human-readable folders.
- **Alternatives Considered**:
  - *Scrivener*: Windows/macOS native, wine-dependent on Linux, proprietary `.scriv` XML bundles.
  - *Notion / Google Docs*: Cloud-locked, privacy-invasive, requires continuous internet access.
- **Consequences**: Total data sovereignty. Work can be read on any operating system 50 years from now.

## ADR-003: Typst + Pandoc for Typesetting vs LaTeX / InDesign / Vellum
- **Context**: Fiction writers need professional book-quality PDFs with proper trim size, margins, running headers, and clean typography without complex LaTeX syntax or Mac-exclusive tools like Vellum.
- **Decision**: Use Typst as the primary PDF typesetting engine, with Pandoc as the conversion bridge from Markdown.
- **Alternatives Considered**:
  - *LaTeX (memoir / book)*: Slow compile times, fragile package collisions, steep learning curve.
  - *LibreOffice PDF Export*: Lacks micro-typographic controls and automated running headers for alternating verso/recto pages.
  - *Vellum*: macOS only, closed source, expensive ($250).
- **Consequences**: Lightning-fast builds (<100ms), modern declarative syntax, beautiful book aesthetics, 100% open-source.

## ADR-004: LeechBlock NG & OS Do-Not-Disturb vs Total Internet Disconnection
- **Context**: Writers need online research and dictionary lookups, but are susceptible to social media and video rabbit holes.
- **Decision**: Install LeechBlock NG on Firefox with scheduled blocks during writing hours, paired with XFCE Do-Not-Disturb mode.
- **Alternatives Considered**:
  - *Physical Airplane Mode*: Cuts off dictionary, Wikipedia, and research access.
  - *Hardcore DNS block (hosts file)*: Inflexible and annoying to toggle.
- **Consequences**: Frictionless focus during writing blocks without crippling essential research capabilities.

## ADR-005: novelWriter Placeholder vs Generated Project File
- **Context**: A valid novelWriter project (fileVersion 1.5, `content/*.nwd`, `meta/`, `ToC.txt`) can only be produced by novelWriter itself; hand-authoring the XML risks shipping a file that opens nowhere.
- **Decision**: Ship `templates/manuscript/nwProject.nwx` as a documented placeholder and make the Markdown starters under `Book-01/` the source of truth for `export_book.sh`. Users create the real project via novelWriter → New Project and import the Markdown.
- **Consequences**: Export never depends on the placeholder; no false claim of a "standard project file."

## ADR-006: Tolerant Setup Provisioning
- **Context**: Font package names drift across Mint/Debian releases, Flatpak scope differs per machine, and ARM laptops need different Typst binaries. A single `apt-get install` line aborts the whole setup on one renamed package.
- **Decision**: Install core packages strictly, fonts tolerantly (Libertinus fallback + warning), detect `x86_64`/`aarch64` for Typst, prefer Flatpak `--system` with `--user` fallback, resolve the desktop dir via `xdg-user-dir`.
- **Consequences**: Setup degrades gracefully instead of failing; font gaps are reported, not fatal.

## ADR-007: Pandoc-First Export with Safe Filenames
- **Context**: Hand-rolled Markdown→Typst regex mangles body text, raw titles break Typst string literals and output paths, and a failed Typst compile used to skip EPUB generation and leak temp dirs.
- **Decision**: Prefer `pandoc -t typst` with a multi-level `sed` fallback, escape titles for Typst, derive collision-safe filename stems, `trap`-clean temp dirs, and let Typst failure fall through to Pandoc EPUB.
- **Consequences**: Real manuscripts convert faithfully; re-exports never overwrite silently.
