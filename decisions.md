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

## ADR-005: Valid novelWriter Project Scaffolding
- **Context**: Placeholders that fail XML parsers create friction for authors attempting to open novelWriter directly.
- **Decision**: Ship a valid XML format conforming to novelWriter `fileVersion 1.5` schema (`<novelWriterXML>`) in `templates/manuscript/nwProject.nwx` and auto-generate it dynamically during `init_world.sh`.
- **Alternatives Considered**:
  - *Unstructured placeholder stub*: Aborts when parsed by standard XML utilities or novelWriter importers.
- **Consequences**: Valid XML schema validation in CI while maintaining plain Markdown starters as the source of truth for compilation.

## ADR-006: Tolerant Setup Provisioning
- **Context**: Font package names drift across Mint/Debian releases, Flatpak scope differs per machine, and ARM laptops need different Typst binaries. A single `apt-get install` line aborts the whole setup on one renamed package.
- **Decision**: Install core packages strictly, fonts tolerantly (Libertinus fallback + warning), detect `x86_64`/`aarch64` for Typst, prefer Flatpak `--system` with `--user` fallback, resolve the desktop dir via `xdg-user-dir`.
- **Consequences**: Setup degrades gracefully instead of failing; font gaps are reported, not fatal.

## ADR-007: Pandoc-First Export with Safe Filenames
- **Context**: Hand-rolled Markdown→Typst regex mangles body text, raw titles break Typst string literals and output paths, and a failed Typst compile used to skip EPUB generation and leak temp dirs.
- **Decision**: Prefer `pandoc -t typst` with a multi-level `sed` fallback, escape titles for Typst, derive collision-safe filename stems, `trap`-clean temp dirs, and let Typst failure fall through to Pandoc EPUB.
- **Consequences**: Real manuscripts convert faithfully; re-exports never overwrite silently.

## ADR-008: Transactional World Scaffolding via Temporary Staging (REL-01)
- **Context**: Direct directory creation in `~/Worlds/<name>` leaves orphaned or corrupt state if an intermediate failure occurs (e.g. disk full, signal interrupt, template error).
- **Decision**: Stage world creation in a temporary directory (`mktemp -d`), run structural validation checks, initialize Git, and atomically move (`mv`) the finished tree into `~/Worlds/<name>`. On any failure, the trap cleans up staging without touching `~/Worlds/`.
- **Consequences**: Zero risk of half-scaffolded or corrupt project folders.

## ADR-009: Decoupled Standalone Backups vs Local Git Snapshots (REL-03)
- **Context**: Authors conflate local Git commits (`save_snapshot.sh`) with external disaster recovery backups. If the local `.git` repository or drive is corrupted, all local commits are lost.
- **Decision**: Decouple version snapshots (Git) from standalone archive backups (`backup_world.sh` / `restore_world.sh`). Standalone backups produce timestamped `.tar.gz` archives with SHA-256 verification manifests and metadata JSON.
- **Consequences**: Complete 3-2-1 backup readiness and verified disaster recovery capability.

## ADR-010: OS Gating and Dry-Run Installation Safety (SEC-01, SEC-02)
- **Context**: Automated installers modifying root/user directories without simulation or platform checks risk breaking unverified distributions.
- **Decision**: Implement `/etc/os-release` gating (Linux Mint 21/22, Debian 12/13), require `--force` on other systems, implement a complete `--dry-run` simulation mode in `setup_scriptorium.sh`, and provide an automated rollback uninstaller (`uninstall_scriptorium.sh`).
- **Consequences**: Safe preview before mutation, protection against untested distro breakage, and clean uninstallation.

## ADR-011: Independent Export Error Trapping & Artifact Validation (AUD-02)
- **Context**: A Pandoc compilation failure previously triggered `set -e` aborts that suppressed summary logs and prevented users from accessing valid Typst/PDF outputs.
- **Decision**: Implement independent error trapping for Pandoc mirroring Typst, set `EXIT_STATUS=1` on non-fatal failures, validate that produced artifacts have non-zero byte size, and always present the summary ledger.
- **Consequences**: Robust multi-format compilation where partial successes are preserved and surfaced.

## ADR-012: Unified CLI Facade & Desktop Control Center (M4)
- **Context**: Discrete shell scripts require knowing individual script names, while daily authoring requires a centralized launcher.
- **Decision**: Provide `scripts/scriptorium` as a single unified CLI dispatcher and `launchers/scriptorium-control-center.desktop` / `control_center.sh` as an intuitive desktop GUI dashboard.
- **Consequences**: Seamless ergonomics for both terminal power users and GUI-first writers.

## ADR-013: Universe-World-Manuscript Multi-Tier Git Architecture
- **Context**: Complex narrative projects span interconnected worlds within a shared cosmos (e.g. Cosmere, solar systems), while individual books require discrete, granular revision histories that can be branched, tagged, and diffed without bloating the world bible lore repository.
- **Decision**: Implement a 3-tier version control hierarchy:
  1. *Universe Tier* (`~/Universes/<UniverseName>/`): Houses `universe.yaml` manifest and an overarching Git repository tracking world cataloging and cross-world continuity.
  2. *World Tier* (`~/Universes/<UniverseName>/Worlds/<WorldName>/` or standalone `~/Worlds/<WorldName>/`): Houses `00-World-Bible`, `02-Research`, `03-Outlines`, `04-Publishing`, with an active World Git repository and Obsidian Git auto-commit support.
  3. *Manuscript Tier* (`01-Manuscript/<BookName>/`): Each manuscript volume receives its own discrete, isolated Git repository for granular drafting commits, scene-level branching, and word-level diffs.
- **Consequences**: Complete narrative isolation, modular scaling across multi-volume series, clean git status across world bible vs manuscripts, and backward compatibility with standalone world directories.

## ADR-014: Out-of-the-Box Obsidian Worldbuilding & Drafting Plugin Suite
- **Context**: Setting up an Obsidian vault from scratch for worldbuilding and long-form novel writing requires tedious manual installation, configuration, and schema modeling, leading to UI bloat, plugin conflicts, and fragile YAML frontmatter.
- **Decision**: Pre-configure an opinionated, premier plugin suite in `templates/world-bible/.obsidian/` featuring:
  - **Longform**: Modular manuscript scene organization and direct compilation.
  - **Dataview**: Dynamic lore querying, character registries, and location rollups.
  - **Metadata Menu**: Structured frontmatter validation and strict `fileClasses` schemas (`Character`, `Location`, `Faction`, `TimelineEvent`).
  - **Calendarium**: Custom fantasy/sci-fi calendar engines with event tracking.
  - **Storyteller Suite**: Entity relationship graphs and interactive visual lore nodes.
  - **Storyline**: Timeline and scene beat structuring.
  - **Novel Word Count**: Real-time word counts and chapter targets.
  - **Obsidian Git**: Automated background commits (10-minute intervals) and backup on save.
  - **Templater & Style Settings / Minimal Theme**: Automated note instantiation and typographic styling.
- **Consequences**: Zero-setup vault initialization for writers, guaranteed schema consistency, automated local version control, and instant productivity upon running `init_world.sh`.

