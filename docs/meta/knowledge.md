# Knowledge Base: Scriptorium Technical Ecosystem & Invariants

## 1. Operating System Details
- **Linux Mint XFCE**: Built on Ubuntu LTS base. Uses XFCE desktop environment. Extremely lightweight (idle RAM ~600MB - 900MB), lightning fast, highly customizable, and beginner friendly. Comes with LibreOffice pre-installed and Software Manager supporting both APT and Flatpak out of the box.
- **Debian 13 (Trixie) / 12 (Bookworm) XFCE**: Minimal ultra-stable base. Native Debian package ecosystem with low resource footprint.

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
| **Scriptorium Engine** | Shell + Python3 | Standalone CLI & GUI Control Center | Unified management, backup verification, and diagnostics |

## 3. Typst vs. LaTeX for Fiction
- **Compilation Speed**: Typst compiles sub-second (instantaneous) compared to LaTeX's multi-pass builds.
- **Syntax Simplicity**: Typst uses clean, declarative syntax without cryptic LaTeX cascades.
- **Page Layout**: Native support for running headers with chapter titles, alternating recto/verso margins, gutter binding allowances, and custom page numbers.

## 4. novelWriter Markdown Conventions
- Headers: `# Title`, `## Chapter`, `### Scene`, `#### Section`.
- Metadata tags: `@pov: CharacterName`, `@focus: LocationName`, `@plot: PlotPoint`, `@status: Draft / Finished / Revision`, custom tags (`@theme: ...`).
- Tag stripping engine removes all `@tag:` and `%` comment lines during export so they never leak into consumer EPUBs or become unhandled citations in Typst.

## 5. Architectural & Safety Invariants
- **Multi-Tier Git Architecture**: 3-level version control hierarchy:
  1. *Universe Tier* (`~/Universes/<Name>/`): Houses `universe.yaml` and overarching continuity Git repo.
  2. *World Tier* (`~/Universes/<Name>/Worlds/<Name>/` or standalone `~/Worlds/<Name>/`): Houses `00-World-Bible` lore and assets with World Git repo and Obsidian Git auto-commit.
  3. *Manuscript Tier* (`01-Manuscript/<Book>/`): Discrete, isolated Git repo per book for granular revision histories and word-level diffing.
- **Pre-Configured Obsidian Plugin Suite**: Out-of-the-box writing and worldbuilding suite (`templates/world-bible/.obsidian/`):
  - *Longform*: Atomic scene organization and compiled manuscript export.
  - *Dataview*: Dynamic lore querying and relationship rollups (JS & DQL enabled).
  - *Metadata Menu*: Structured YAML validation with strict `fileClasses` (`Character`, `Location`, `Faction`, `TimelineEvent`, `Creature`, `Artifact`, `Cosmology`, `MagicSystem`, `Language`).
  - *Calendarium*: Custom multi-moon and fantasy calendar systems.
  - *Storyteller Suite* & *Storyline*: Visual narrative graphs and scene beat progression.
  - *Novel Word Count*: Real-time word counts and chapter targets.
  - *Obsidian Git*: Automated background commits (10-minute interval) and backup on save.
- **Multi-Volume Compilation & Trade Typography**:
  - `export_book.sh` supports discrete volume isolation via `-b, --book <Volume>`, paper trim size presets (`-s, --paper-size us-trade|trade|pocket`), EPUB cover image auto-detection (`03-Art/cover.png` or `.jpg`), and GUI volume pickers.
  - `add_book.sh` / `scriptorium add-book <world> [book]` provides 1-click multi-volume scaffolding (`Book-02`, `Book-03`, etc.) with three acts and discrete Git repositories.
  - `book_template.typ` provides trade geometries (6x9, 5.5x8.5, 5x8), automatic ornamental scene breaks (`show line: it => scene-break()`), and flush-left opening paragraph conventions.
- **Transactional Staging**: `init_world.sh` builds in a temporary directory, validates directory schemas and manifests, commits initial Git state, and atomically moves to destination. Intermediate failures leave no orphaned state.
- **Decoupled Data Safety & Concurrency**: Local Git version snapshots (`save_snapshot.sh` with index lock retry loops) are decoupled from standalone verified archives (`backup_world.sh` tarball + SHA-256 hash manifest). Disaster recovery is verified via `restore_world.sh`.
- **Installer Safety & Gating**: `setup_scriptorium.sh` performs OS distribution detection via `/etc/os-release`, gates unverified distros unless `--force` is passed, supports complete non-destructive `--dry-run` simulation, and provides `uninstall_scriptorium.sh` for rollback.
- **Independent Error Trapping**: Exporter traps Pandoc and Typst independently so that partial compilation outputs are preserved and detailed summaries are surfaced without early `set -e` termination.
- **Automated Back-Matter Concordance & Multi-Era Diagnostics**:
  - `generate_concordance.sh` (`scriptorium concordance`) parses structured YAML frontmatter from `Characters/`, `Languages/`, `Bestiary/`, `Artifacts/`, and `Factions/` to generate `01_Dramatis_Personae.md` and `02_Glossary_and_Concordance.md` in `01-Manuscript/<Book>/04_Back_Matter/`, which are automatically compiled at the end of Typst PDFs and EPUBs.
  - `world_doctor.sh` implements multi-era chronological parsing (`WLD-104`) with regex extraction supporting BC/BCE negative year coordinates, CE/AD, sequential numbered eras (1E..5E), and named custom eras (`Age of Fire`, `IE`).
  - `Subplot-Thread-Matrix.md` establishes `@thread:` tag conventions for novelWriter / Obsidian with dynamic Dataview dashboards.
- **Unified Interface & Desktop Control Center**: `scripts/scriptorium_app.py` (Python 3/GTK 3) provides a 5-tab author GUI (Cosmos & Projects, Writing & Analytics, Publishing Studio, Vault Safety, Doctor Diagnostics) with First-Flight onboarding, backed by Zenity dialog fallbacks and the `scriptorium <command>` CLI dispatcher.
- **Author's Field Manual**: `docs/AUTHOR_MANUAL.md` provides an 8-chapter visual guide explaining the entire worldbuilding, drafting, version control, and publication workflow in plain English.


