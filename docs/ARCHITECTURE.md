# Scriptorium Technical Architecture & Architectural Decision Records (ADRs)

---

## 1. System Design Invariants & Philosophy

Scriptorium is a purpose-built, distraction-free authoring and worldbuilding environment running on Linux (primarily Linux Mint XFCE or Debian 13/12 XFCE). It adheres to strict foundational principles:

1. **Plain Text & Open Formats First**: Every character sheet, location note, outline, and manuscript scene is stored in standard Markdown (`.md`) and open text files. There is zero vendor lock-in; files remain readable and editable decades into the future.
2. **One Tool Per Creative Stage**:
   - *World Bible & Lore Wiki*: **Obsidian** (pure lore vault at `~/Universes/<Universe>/<World>` pre-configured with Dataview, Metadata Menu 9 `fileClasses` schemas, Calendarium, Storyteller Suite, Storyline, Novel Word Count, and Obsidian Git).
   - *Outlining & Drafting*: **novelWriter** or **Obsidian Longform** (structured project at `~/Manuscripts/<Manuscript>`, chapter/scene hierarchy, metadata tagging, focus mode).
   - *Deep Focus Sessions*: **FocusWriter** (full-screen distraction-free canvas).
   - *Editor Revisions / Redlines*: **LibreOffice Writer** (`.docx` / `.odt` with track changes).
   - *Ebook Compilation*: **Calibre** (EPUB generation, cover inspection, and e-reader sync).
   - *Typesetting & Print PDF*: **Typst + Pandoc** (sub-second modern typographic engine with trade trim sizes: `us-trade`, `trade`, `pocket`).
3. **Zero Terminal Requirement for Daily Work**: Every daily authoring workflow (writing, snapshotting, exporting, backing up, diagnostics, universe/world/manuscript creation) is accessible via the native GTK 3 desktop Control Center (`scripts/scriptorium_app.py`), desktop launchers (`launchers/`), Zenity dialog fallbacks (`control_center.sh`), and the visual Author's Field Manual (`docs/AUTHOR_MANUAL.md`).
4. **Targeted Distraction Control**: Preserves full browser capability for research while enforcing scheduled distraction blocking (LeechBlock NG) during writing hours and 1-click XFCE Do Not Disturb mode.
5. **Multi-Layer Data Protection**: Multi-tier Git version control, standalone verified archive backups (`backup_world.sh` tarball + SHA-256 manifest), full-disk LUKS encryption, and automated external Déjà Dup backups following the 3-2-1 rule.

---

## 2. Application Architecture & Interoperability

| Application | Format & Storage | Protocol / Extension | Primary Role |
| :--- | :--- | :--- | :--- |
| **Obsidian** | Local folder of standard `.md` files | Markdown + Wikilinks (`[[Link]]`) | World Bible, Lore, Character & Location Wiki |
| **novelWriter** | Local folder of `.nwd` documents under `content/` + XML index (`.nwx`, fileVersion 1.5) | Markdown with `@tag` metadata | Story outlining, chapter/scene drafting, project stats |
| **FocusWriter** | Plain `.txt` or `.md` | Plaintext | Fullscreen distraction-free draft sprints |
| **LibreOffice Writer** | `.odt`, `.docx` | OpenDocument / Office Open XML | Editor collaboration, redlining, track changes |
| **Calibre** | `.epub`, `.azw3`, `.mobi` | EPUB / Open Container Format | Ebook generation, DRM-free cataloging, e-reader sync |
| **Typst** | `.typ` source files | Typst modern markup | Publication-grade typesetting, micro-typography, print-ready PDF |
| **Pandoc** | Universal markup converter | AST translation | Bridges Markdown manuscript files directly into Typst/EPUB/DOCX |
| **Déjà Dup** | Duplicity / Restic backend | Encrypted incremental backup archives | Automated local external USB and cloud backups |
| **Git** | Distributed VCS | Local `.git` repository | Version control snapshots and instant rollbacks |
| **Scriptorium Engine** | Shell + Python 3 / GTK 3 | Standalone CLI & Desktop Control Center | Unified management, backup verification, and diagnostics |

---

## 3. Exit-Code Contract & Process Boundaries

All Scriptorium command-line interfaces and automation scripts strictly adhere to a standardized 4-value exit code contract:

| Exit Code | Semantics | Description |
| :---: | :--- | :--- |
| `0` | **Success** | The requested operation completed successfully without errors. |
| `1` | **Runtime / Diagnostic Failure** | The command encountered an execution failure, unrecoverable runtime error, or diagnostic integrity violation (e.g. broken links, invalid schemas, missing build artifacts). |
| `2` | **Usage / Environment Error** | Invalid command-line arguments, unsupported platform/distro, missing prerequisite binaries, or unresolvable paths. |
| `3` | **Nothing to Act On** | No projects/worlds discovered, working tree already clean (no changes to snapshot), or operation skipped due to precondition. |

---

## 4. Multi-Tier Git Repository Doctrine

To balance granular revision tracking for prose against modular scaling for lore, Scriptorium implements a 3-tier version control hierarchy:

1. **Universe Tier (`~/Universes/<UniverseName>/`)**:
   - Manages high-level universe metadata (`universe.yaml`) and `Universe-Index.md`.
   - Active Universe Git repository tracks world registrations, global timelines, and overarching continuity.
2. **World Lore Tier (`~/Universes/<UniverseName>/<WorldName>/` or standalone `~/Worlds/<WorldName>/`)**:
   - Pure Obsidian vault containing `world.yaml`, `00_START_HERE.md`, `Characters/`, `Locations/`, `Factions/`, `History/`, `Magic-Technology/`, `Languages/`, `Bestiary/`, `Artifacts/`, `Cosmology/`, and `Templates/`.
   - Discrete World Git repository with automated background commits (every 10 minutes and on save via Obsidian Git).
3. **Manuscript Tier (`~/Manuscripts/<ManuscriptName>/` or legacy subfolders)**:
   - Houses `manuscript.yaml` linking the parent Universe and World Lore Vault, `nwProject.nwx`, and `Book-*` volumes (`01_Act_I/`, `02_Act_II/`, `03_Act_III/`, `04_Back_Matter/`).
   - Dedicated Manuscript Git repository tracking scene-level prose commits, act branches, and word-level diffs without bloating the world lore repository.

---

## 5. Architectural Decision Records (ADRs)

### ADR-001: Selection of Linux Mint XFCE as Primary Distribution
- **Context**: The author needs a stable, lightweight, zero-maintenance operating system that runs smoothly on reference Intel Core i5 laptops, dual-boots easily with Windows, and requires no terminal interaction for daily tasks.
- **Decision**: Adopt Linux Mint XFCE edition.
- **Alternatives Considered**:
  - *Arch / Custom Minimal Distro*: High setup effort, risk of breakage during updates.
  - *Ubuntu Desktop (GNOME)*: Heavier resource consumption (~1.8 GB idle RAM) and snap dependency.
  - *Debian 13 XFCE*: Excellent lightweight alternative, but requires slightly more initial configuration for non-free codecs and Flatpak repositories. Documented as secondary option.
- **Consequences**: Out-of-the-box GUI software manager, pre-installed LibreOffice, native dual-boot installer, low RAM usage (~700MB idle).

### ADR-002: Plain Markdown Storage vs Proprietary Database (Scrivener / Notion)
- **Context**: Authors frequently lose access to work when proprietary software changes subscription models or becomes abandoned.
- **Decision**: Store all lore, characters, outlines, and manuscript prose in plain `.md` files in human-readable folders.
- **Alternatives Considered**:
  - *Scrivener*: Windows/macOS native, wine-dependent on Linux, proprietary `.scriv` XML bundles.
  - *Notion / Google Docs*: Cloud-locked, privacy-invasive, requires continuous internet access.
- **Consequences**: Total data sovereignty. Work can be read on any operating system 50 years from now.

### ADR-003: Typst + Pandoc for Typesetting vs LaTeX / InDesign / Vellum
- **Context**: Fiction writers need professional book-quality PDFs with proper trim size, margins, running headers, and clean typography without complex LaTeX syntax or Mac-exclusive tools like Vellum.
- **Decision**: Use Typst as the primary PDF typesetting engine, with Pandoc as the conversion bridge from Markdown.
- **Alternatives Considered**:
  - *LaTeX (memoir / book)*: Slow compile times, fragile package collisions, steep learning curve.
  - *LibreOffice PDF Export*: Lacks micro-typographic controls and automated running headers for alternating verso/recto pages.
  - *Vellum*: macOS only, closed source, expensive ($250).
- **Consequences**: Lightning-fast builds (<100ms), modern declarative syntax, beautiful book aesthetics, 100% open-source.

### ADR-004: LeechBlock NG & OS Do-Not-Disturb vs Total Internet Disconnection
- **Context**: Writers need online research and dictionary lookups, but are susceptible to social media and video rabbit holes.
- **Decision**: Install LeechBlock NG on Firefox with scheduled blocks during writing hours, paired with XFCE Do-Not-Disturb mode.
- **Alternatives Considered**:
  - *Physical Airplane Mode*: Cuts off dictionary, Wikipedia, and research access.
  - *Hardcore DNS block (hosts file)*: Inflexible and annoying to toggle.
- **Consequences**: Frictionless focus during writing blocks without crippling essential research capabilities.

### ADR-005: Valid novelWriter Project Scaffolding
- **Context**: Placeholders that fail XML parsers create friction for authors attempting to open novelWriter directly.
- **Decision**: Ship a valid XML format conforming to novelWriter `fileVersion 1.5` schema (`<novelWriterXML>`) in `templates/manuscript/nwProject.nwx` and auto-generate it dynamically during `init_world.sh` and `init_manuscript.sh`.
- **Alternatives Considered**:
  - *Unstructured placeholder stub*: Aborts when parsed by standard XML utilities or novelWriter importers.
- **Consequences**: Valid XML schema validation in CI while maintaining plain Markdown starters as the source of truth for compilation.

### ADR-006: Tolerant Setup Provisioning
- **Context**: Font package names drift across Mint/Debian releases, Flatpak scope differs per machine, and ARM laptops need different Typst binaries. A single `apt-get install` line aborts the whole setup on one renamed package.
- **Decision**: Install core packages strictly, fonts tolerantly (Libertinus fallback + warning), detect `x86_64`/`aarch64` for Typst, prefer Flatpak `--system` with `--user` fallback, resolve the desktop dir via `xdg-user-dir`.
- **Consequences**: Setup degrades gracefully instead of failing; font gaps are reported, not fatal.

### ADR-007: Pandoc-First Export with Safe Filenames
- **Context**: Hand-rolled Markdown→Typst regex mangles body text, raw titles break Typst string literals and output paths, and a failed Typst compile used to skip EPUB generation and leak temp dirs.
- **Decision**: Prefer `pandoc -t typst` with a multi-level `sed` fallback, escape titles for Typst, derive collision-safe filename stems, `trap`-clean temp dirs, and let Typst failure fall through to Pandoc EPUB and DOCX.
- **Consequences**: Real manuscripts convert faithfully; re-exports never overwrite silently.

### ADR-008: Transactional World & Manuscript Scaffolding via Temporary Staging (REL-01)
- **Context**: Direct directory creation leaves orphaned or corrupt state if an intermediate failure occurs (e.g. disk full, signal interrupt, template error).
- **Decision**: Stage world/manuscript creation in a temporary directory (`mktemp -d`), run structural validation checks, initialize Git, and atomically move (`mv`) the finished tree into destination. On any failure, the trap cleans up staging without touching user directories.
- **Consequences**: Zero risk of half-scaffolded or corrupt project folders.

### ADR-009: Decoupled Standalone Backups vs Local Git Snapshots (REL-03)
- **Context**: Authors conflate local Git commits (`save_snapshot.sh`) with external disaster recovery backups. If the local `.git` repository or drive is corrupted, all local commits are lost.
- **Decision**: Decouple version snapshots (Git) from standalone archive backups (`backup_world.sh` / `restore_world.sh`). Standalone backups produce timestamped `.tar.gz` archives with SHA-256 verification manifests and metadata JSON.
- **Consequences**: Complete 3-2-1 backup readiness and verified disaster recovery capability.

### ADR-010: OS Gating and Dry-Run Installation Safety (SEC-01, SEC-02)
- **Context**: Automated installers modifying root/user directories without simulation or platform checks risk breaking unverified distributions.
- **Decision**: Implement `/etc/os-release` gating (Linux Mint 21/22, Debian 12/13), require `--force` on other systems, implement a complete `--dry-run` simulation mode in `setup_scriptorium.sh`, and provide an automated rollback uninstaller (`uninstall_scriptorium.sh`).
- **Consequences**: Safe preview before mutation, protection against untested distro breakage, and clean uninstallation.

### ADR-011: Independent Export Error Trapping & Artifact Validation (AUD-02)
- **Context**: A Pandoc compilation failure previously triggered `set -e` aborts that suppressed summary logs and prevented users from accessing valid Typst/PDF outputs.
- **Decision**: Implement independent error trapping for Pandoc mirroring Typst, set `EXIT_STATUS=1` on non-fatal failures, validate that produced artifacts have non-zero byte size, and always present the summary ledger.
- **Consequences**: Robust multi-format compilation where partial successes are preserved and surfaced.

### ADR-012: Unified CLI Facade & Desktop Control Center (M4)
- **Context**: Discrete shell scripts require knowing individual script names, while daily authoring requires a centralized launcher.
- **Decision**: Provide `scripts/scriptorium` as a single unified CLI dispatcher and `launchers/scriptorium-control-center.desktop` / `control_center.sh` as an intuitive desktop GUI dashboard.
- **Consequences**: Seamless ergonomics for both terminal power users and GUI-first writers.

### ADR-013: Universe-World-Manuscript Multi-Tier Git Architecture
- **Context**: Complex narrative projects span interconnected worlds within a shared cosmos, while individual books require discrete, granular revision histories that can be branched, tagged, and diffed without bloating the world bible lore repository.
- **Decision**: Implement a 3-tier version control hierarchy: Universe (`~/Universes/<Universe>/`), World Lore Vault (`~/Universes/<Universe>/<World>/`), and Manuscript (`~/Manuscripts/<Manuscript>/`).
- **Consequences**: Complete narrative isolation, modular scaling across multi-volume series, clean git status across world bible vs manuscripts, and backward compatibility with standalone world directories.

### ADR-014: Out-of-the-Box Obsidian Worldbuilding & Drafting Plugin Suite
- **Context**: Setting up an Obsidian vault from scratch for worldbuilding and long-form novel writing requires tedious manual installation, configuration, and schema modeling, leading to UI bloat, plugin conflicts, and fragile YAML frontmatter.
- **Decision**: Pre-configure an opinionated, premier plugin suite in `templates/world-bible/.obsidian/` featuring Longform, Dataview, Metadata Menu (9 `fileClasses`), Calendarium, Storyteller Suite, Storyline, Novel Word Count, Obsidian Git (10-minute auto-commits), and Templater.
- **Consequences**: Zero-setup vault initialization for writers, guaranteed schema consistency, automated local version control, and instant productivity upon running `init_world.sh`.

### ADR-015: Multi-Volume Manuscript Compilation & Volume Isolation
- **Context**: Authors writing multi-book series within a single world project need the ability to compile discrete individual volumes (e.g. `Book-01`, `Book-02`) independently rather than always generating a monolithic omnibus PDF/EPUB.
- **Decision**: Implement volume discovery and selection in `export_book.sh` and `scriptorium export` (`-b, --book <Volume>`, GUI interactive picker, and Omnibus option).
- **Consequences**: Granular publication workflows, seamless series management, and prevention of multi-volume manuscript collisions.

### ADR-016: Speculative Fiction Taxonomic Expansion (Bestiary, Relics, Cosmology)
- **Context**: Worldbuilding across epic fantasy and science fiction requires dedicated, first-class ontologies for creatures/flora/fauna, legendary artifacts/relics, and pantheons/cosmologies beyond standard characters, locations, and factions.
- **Decision**: Expand canonical World Bible taxonomy to include `Bestiary/` (`Creature.md`), `Artifacts/` (`Artifact.md`), and `Cosmology/` (`Cosmology.md`).
- **Consequences**: Rich ontological coverage for speculative fiction with dynamic Dataview dashboards and `world_doctor.sh` validation.

### ADR-017: Unified Python GTK Desktop Control Center & Author Onboarding Architecture
- **Context**: Authors with average computer experience find terminal CLI commands intimidating. While Zenity dialogs provide basic graphical interaction, they lack rich state management, hierarchical manuscript progress trees, live word count rollups, asynchronous background task streaming, and visual toolchain diagnostics.
- **Decision**: Implement a native desktop GUI dashboard in Python 3 + PyGObject / GTK 3 (`scripts/scriptorium_app.py`) organized across a 5-tab author workflow with First-Flight onboarding wizard.
- **Consequences**: Zero terminal barrier to entry for creative authors, rich visual feedback during writing and export, safe async background processing, and complete system resilience across all environments.

### ADR-018: Speculative Ontology Harmonization, Multi-Volume Scaffolding & Publishing Polish
- **Context**: Ontological divergence between frontmatter templates and `fileClasses` schemas caused inconsistent Dataview reporting. Additionally, authoring multi-book series required manual volume folder and Git repo setup, while publishing lacked cover image auto-detection and paper trim size configurability.
- **Decision**: Harmonize all frontmatter templates and Dataview tables with strict `fileClasses`, add `MagicSystem.md` and `Language.md`, introduce `scripts/add_book.sh`, wire `-s, --paper-size`, and auto-detect EPUB covers (`03-Art/cover.png`).
- **Consequences**: Complete ontological consistency across the 9 World Bible domains, frictionless multi-volume series authoring, publication-grade cover and trim sizing.

### ADR-019: Automated Narrative Concordance & Multi-Era Chronological Parsing Engine
- **Context**: Authors manually assemble Dramatis Personae rosters and world glossaries at publication time, leading to desynchronization with World Bible lore notes. Furthermore, timeline consistency checking in `world_doctor.sh` previously relied on strict integer casting, failing on fantasy/sci-fi era notation.
- **Decision**: Implement `scripts/generate_concordance.sh` for automated back-matter generation (`01_Dramatis_Personae.md` and `02_Glossary_and_Concordance.md` in `04_Back_Matter/`), and implement a regex-based multi-era chronological parser in `world_doctor.sh` supporting BC/BCE, CE/AD, numbered eras (1E..5E), and named eras (`Age of Fire`, `IE`).
- **Consequences**: Zero manual toil generating book back-matter, automated synchronization between world lore and published glossaries, and robust chronological diagnostics.

### ADR-020: External Audit Remediation — Shared Discovery Library & Fail-Closed Hardening
- **Context**: An external audit of commit `9d34fae` identified functional bugs (invalid Calibre Flathub ID), injection/fail-open weaknesses in diagnostics and verification, developer identity leakage, and ~300 lines of duplicated discovery code.
- **Decision**: Extract `scripts/lib/worlds.sh` as the single source of truth for discovery and path resolution, make `verify.sh` fail closed, harden `restore_world.sh` against directory traversal, correct Calibre Flathub ID, move background GUI tasks to worker threads, and exclude `04-Publishing/` from snapshot history.
- **Consequences**: Centralized discovery logic, hardened security posture, reliable verification harness, and responsive GUI.

### ADR-021: Re-Audit Follow-Ups, Root Decluttering & Authorship Reset
- **Context**: An independent re-audit of the remediation series verified all 22 original findings closed (Grade A) and registered 5 new observations regarding exit-code documentation, legacy deprecation nudges, daemon worker threads, and root directory hygiene.
- **Decision**: Document standardized 4-value exit-code contract, extract `warn_if_legacy_root`, centralize daemon thread spawning, remove dead fallback branches, and declutter root repository.
- **Consequences**: Contract matches code, consistent user experience across selection paths, clean thread management, and uncluttered repository root.

### ADR-022: Separated Lore & Manuscript Architecture, Visual Scene Metadata Inspector, and Standardized Tagging Protocol
- **Context**: Nesting manuscripts inside world bible folders (`00-World-Bible` / `01-Manuscript`) created friction for authors using novelWriter or Obsidian independently. Furthermore, tag naming was fragmented (`@focus:` vs `@location:`), editing scene metadata required opening raw Markdown in a text editor, and standard submission formats (`.docx`) were missing.
- **Decision**:
  - Separate Pure World Lore Vaults (`~/Universes/<Universe>/<World>`) as direct Obsidian vaults from Standalone Prose Manuscript Projects (`~/Manuscripts/<Manuscript>`) with `manuscript.yaml` linking.
  - Standardize `@location:` across all templates, novelWriter scene headers, and diagnostic passes (deprecating `@focus:`).
  - Implement a Visual Scene Metadata Inspector in GTK Control Center Tab 2 allowing authors to inspect and rewrite scene metadata tags (`@pov:`, `@char:`, `@location:`, `@thread:`, `@time:`, `@status:`) in place.
  - Add Standard Manuscript Submission Format (`.docx`) export via Pandoc and integrate `WLD-108` lore cross-reference diagnostics into `world_doctor.sh`.
- **Consequences**: Clean separation of worldbuilding lore and manuscript prose, effortless tag consistency, intuitive in-GUI scene metadata management, and industry-standard submission capability.

### ADR-023: Forensic Audit Hardening — Fail-Closed Security, Depth-3 Universe Discovery, ISO 8601 Chronology, and Intra-Manuscript Link Resolution
- **Context**: Comprehensive security and operational auditing identified key edge-case gaps:
  1. The Typst binary installer in `scripts/setup_scriptorium.sh` had a fail-open branch (`TYPST_OK=1`) when upstream SHA-256 digests were unavailable.
  2. The shared discovery library `scripts/lib/worlds.sh` did not cleanly discover legacy depth-3 subfolder worlds (`~/Universes/<Universe>/Worlds/<World>`) or falsely discovered the container directory `"Worlds"`, while `universe_label` extracted `"Worlds"` instead of the owning universe name.
  3. Chronological paradox analysis in `world_doctor.sh` (`WLD-104`) was limited to era strings or raw numbers and failed on ISO 8601 calendar dates (`YYYY-MM-DD`, `YYYY-MM`, `YYYY/MM/DD`).
  4. Manuscript diagnostics in `world_doctor.sh` (`WLD-108`) flagged intra-manuscript wikilinks (e.g. `[[Master-Outline]]`, chapter links) as missing lore entities because only World Bible notes were indexed.
  5. The GTK Desktop GUI (`scripts/scriptorium_app.py`) did not trigger snapshot history reload after HeaderBar Quick Snapshots and risked misplacing YAML frontmatter when rewriting scene tags.
- **Decision**:
  - Convert `setup_scriptorium.sh` to fail closed (`TYPST_OK=0`) when SHA-256 digests cannot be verified, refusing unverified binary installation per `SECURITY.md` and S-01.
  - Upgrade `scripts/lib/worlds.sh` to index direct depth-2, legacy subfolder depth-3, and legacy root worlds without polluting results with literal `"Worlds"` directories, and fix `universe_label` for depth-3 worlds.
  - Implement ISO 8601 calendar date parsing (`ISO_DATE_PATTERN`) in `parse_timeline_date` to calculate decimal astronomical years for timeline paradox comparison.
  - Index all manuscript markdown files and outlines into `ms_index` in Pass 3 of `world_doctor.sh` to resolve intra-manuscript references without false-positive `WLD-108` lore drift findings.
  - Pass `refresh_snapshot_history` to HeaderBar Quick Snapshot in `scriptorium_app.py` and preserve YAML frontmatter at the top of markdown scene files during tag saves.
- **Consequences**: Strict fail-closed binary installation security, flawless multi-tier universe and world vault discovery, robust ISO 8601 and fantasy era chronological validation, accurate manuscript-to-lore diagnostics without false positives, and rock-solid frontmatter preservation in the desktop GUI.

