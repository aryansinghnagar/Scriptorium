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
  - **Metadata Menu**: Structured frontmatter validation and strict `fileClasses` schemas (`Character`, `Location`, `Faction`, `TimelineEvent`, `Creature`, `Artifact`, `Cosmology`).
  - **Calendarium**: Custom fantasy/sci-fi calendar engines with event tracking.
  - **Storyteller Suite**: Entity relationship graphs and interactive visual lore nodes.
  - **Storyline**: Timeline and scene beat structuring.
  - **Novel Word Count**: Real-time word counts and chapter targets.
  - **Obsidian Git**: Automated background commits (10-minute intervals) and backup on save.
  - **Templater & Style Settings / Minimal Theme**: Automated note instantiation and typographic styling.
- **Consequences**: Zero-setup vault initialization for writers, guaranteed schema consistency, automated local version control, and instant productivity upon running `init_world.sh`.

## ADR-015: Multi-Volume Manuscript Compilation & Volume Isolation
- **Context**: Authors writing multi-book series within a single world project need the ability to compile discrete individual volumes (e.g. `Book-01`, `Book-02`) independently rather than always generating a monolithic omnibus PDF/EPUB.
- **Decision**: Implement volume discovery and selection in `export_book.sh` and `scriptorium export`:
  - Add `-b, --book <Volume>` CLI flag allowing explicit target specification.
  - In GUI mode when multiple `Book-*` volumes exist, prompt the author with an interactive volume selector including an "All (Omnibus)" option.
  - In non-interactive runs, default gracefully to the first volume (`Book-01`).
  - Derive volume-aware output filenames (`<Title>_<Volume>.pdf`).
- **Consequences**: Granular publication workflows, seamless series management, and prevention of multi-volume manuscript collisions.

## ADR-016: Speculative Fiction Taxonomic Expansion (Bestiary, Relics, Cosmology)
- **Context**: Worldbuilding across epic fantasy and science fiction requires dedicated, first-class ontologies for creatures/flora/fauna, legendary artifacts/relics, and pantheons/cosmologies beyond standard characters, locations, and factions.
- **Decision**: Expand the canonical World Bible taxonomy to include:
  - `00-World-Bible/Bestiary/` (`Creature-Flora-Fauna-Template.md`, `fileClasses/Creature.md`).
  - `00-World-Bible/Artifacts/` (`Artifact-Relic-Template.md`, `fileClasses/Artifact.md`).
  - `00-World-Bible/Cosmology/` (`Deity-Cosmology-Template.md`, `fileClasses/Cosmology.md`).
## ADR-017: Unified Python GTK Desktop Control Center & Author Onboarding Architecture
- **Context**: Authors and worldbuilders with average computer experience find terminal CLI commands intimidating or friction-heavy for daily creative sprints. While Zenity dialogs provide basic graphical interaction, they lack rich state management, hierarchical manuscript progress trees, live word count rollups, asynchronous background task streaming, and visual toolchain diagnostics.
- **Decision**:
  - Implement a native desktop GUI dashboard in Python 3 + PyGObject / GTK 3 (`scripts/scriptorium_app.py`) conforming to modern desktop ergonomics.
  - Organize functionality across a 5-tab author workflow:
    1. *Cosmos & Projects*: Universe & World management, creation wizards, toolchain launchers.
    2. *Writing & Analytics*: Manuscript hierarchy tree, live word counts, act rollups, session pacing.
    3. *Publishing Studio*: 1-Click Typst PDF & Pandoc EPUB export, volume selector (`Book-01`, `Book-02`, Omnibus), trim size presets (6x9, 5.5x8.5, 5x8), live PDF viewer.
    4. *Vault Safety & Backups*: 1-Click Git version snapshot button with log viewer, standalone `.tar.gz` + SHA-256 backup creator, restore drill wizard.
    5. *Doctor Diagnostics*: Scriptorium toolchain status badges, World Bible lore consistency checks (`world_doctor`), 7-stage verification trigger.
  - Provide a First-Flight onboarding wizard detecting unconfigured environments with 1-click demo cosmos generation (*"The Chronicles of Eldoria"*).
  - Maintain a multi-tier fallback architecture: `scriptorium_app.py` -> Zenity dialogs (`control_center.sh`) -> CLI (`scriptorium`).
  - Link the in-app menu directly to the plain-English author handbook (`docs/AUTHOR_MANUAL.md`).
- **Consequences**: Zero terminal barrier to entry for creative authors, rich visual feedback during writing and export, safe async background processing, and complete system resilience across all environments.

## ADR-018: Speculative Ontology Harmonization, Multi-Volume Scaffolding & Publishing Polish
- **Context**: Ontological divergence between frontmatter templates (`Character`, `Location`, `Faction`, `TimelineEvent`) and `fileClasses` schemas caused inconsistent Dataview reporting. Additionally, authoring multi-book series required manual volume folder and Git repo setup, while publishing lacked cover image auto-detection and paper trim size configurability.
- **Decision**:
  - Harmonize all frontmatter templates and `Templates/World-Bible-Index.md` Dataview tables with strict `fileClasses` definitions.
  - Create formal `fileClasses` schemas for `MagicSystem.md` and `Language.md` completing the 9 core lore ontologies.
  - Relocate `.obsidian-recommended-plugins.md` to `docs/OBSIDIAN_PLUGINS_GUIDE.md` to keep newly scaffolded world vaults clean.
  - Introduce `scripts/add_book.sh` and `scriptorium add-book <world> [book]` to scaffold subsequent manuscript volumes with 3 acts, sample chapters, and isolated Git repositories.
  - Wire `-s, --paper-size <us-trade|trade|pocket>` across `export_book.sh` and `scriptorium_app.py`, and implement EPUB cover image auto-detection (`03-Art/cover.png` or `03-Art/cover.jpg`).
  - Anchor root `.gitignore` entries to prevent unintended swallowing of test fixture directories.
- **Consequences**: Complete ontological consistency across the 9 World Bible domains, frictionless multi-volume series authoring, publication-grade cover and trim sizing, and robust test suite isolation.

## ADR-019: Automated Narrative Concordance & Multi-Era Chronological Parsing Engine
- **Context**: Authors of speculative fiction and epic sagas manually assemble Dramatis Personae rosters and world glossaries at publication time, leading to desynchronization with World Bible lore notes. Furthermore, timeline consistency checking in `world_doctor.sh` (`WLD-104`) previously relied on strict integer casting, failing or silently bypassing fantasy/sci-fi era notation (e.g. `-450 IE`, `1422 3E`, `Age of Fire 410`, `500 BCE`).
- **Decision**:
  - Implement `scripts/generate_concordance.sh` (`scriptorium concordance <world> [--book Book-01]`) to automatically parse structured YAML frontmatter from `Characters/`, `Languages/`, `Bestiary/`, `Artifacts/`, and `Factions/` and generate publication-ready `01_Dramatis_Personae.md` and `02_Glossary_and_Concordance.md` in `01-Manuscript/<Book>/04_Back_Matter/`.
  - Seamlessly position `04_Back_Matter/` so natural sorting in `export_book.sh` automatically compiles Dramatis Personae and Glossary at the end of Typst print PDFs and Pandoc EPUBs.
  - Implement a regex-based multi-era chronological parser and comparator in `scripts/world_doctor.sh` supporting BC/BCE negative intervals, CE/AD, sequential numbered eras (1E..5E, First..Fifth Age), and custom named eras (`Age of Fire`, `IE`).
  - Introduce `templates/manuscript/Outlines/Subplot-Thread-Matrix.md` with `@thread:` tag standards and dynamic Dataview dashboards.
  - Integrate 1-click "Add New Volume" and "Generate Concordance" buttons directly into the GTK Desktop Control Center (`scriptorium_app.py`).
  - Safely remove obsolete `Finishing_Touches.md` and harmonize documentation.
- **Consequences**: Zero manual toil generating book back-matter, automated synchronization between world lore and published glossaries, robust chronological diagnostics across speculative timelines, and a decluttered root repository.


## ADR-020: External Audit Remediation — Shared Discovery Library & Fail-Closed Hardening
- **Context**: A line-by-line external audit of commit `9d34fae` (report committed as `AUDIT.md`; 22 findings — 1 High, 7 Medium, 11 Low, 3 Info) confirmed the engineering discipline but identified one high-impact functional bug (the Calibre Flathub ID `com.calibredesk.calibre` does not exist, so setup could never install Calibre), several injection/fail-open weaknesses (world-doctor JSON interpolated into `python3 -c` source strings, verification stages built on `set -e` + `cmd && echo` that were structurally unable to fail, a Typst installer that failed open on missing digests), identity leakage (the developer's username hardcoded as a heuristic in four scripts), and roughly 300 lines of copy-pasted world-discovery logic across five scripts with partial copies in five more.
- **Decision**:
  - Extract `scripts/lib/worlds.sh` as the single source of truth for world discovery (`discover_worlds`), input resolution (`resolve_world_dir`, documented precedence: path > universe > canonical basename > legacy root), and labels (`universe_label`). "Standalone" detection is structural (path prefix under `~/Worlds`), never identity-based, so it is correct for every user.
  - Make `scripts/verify.sh` and the CI syntax-validation step fail closed; all data crossing the shell/Python boundary flows through stdin or argv, never through interpolated source strings.
  - Fail closed on unverifiable Typst release binaries and warn explicitly when the GitHub API is rate-limited rather than silently skipping installation.
  - Harden `restore_world.sh`: refuse archives with absolute or `..` traversal members, unexpected root entries, or non-sample `.git/hooks` payloads (blanket-rejecting all hooks would break legitimate backups, since `git init` ships `*.sample` hooks); extract with `--no-same-owner --no-same-permissions`.
  - Correct the Calibre Flathub ID to `com.calibre_ebook.calibre` in setup, doctor, uninstaller, GTK app, and both compatibility docs.
  - Move universe/world scaffolding in the GTK app off the main thread via the existing `_run_async_command` worker pattern.
  - Exclude `04-Publishing/` from generated world `.gitignore`s so compiled PDF/EPUB binaries stop accumulating in snapshot history. Existing worlds adopt this with `echo "04-Publishing/" >> <world>/.gitignore`; stripping already-committed artifacts is a history rewrite (`git filter-repo`) left to each author's discretion.
  - Licensing posture clarification (audit §6): the stack is FOSS with **one optional proprietary component — Obsidian**. Because all data lives in plain Markdown with wikilinks and every Scriptorium feature works without Obsidian, the honest claim is *"no data locks; one optional proprietary tool"* rather than "without proprietary software."
- **Consequences**: ~300 lines of duplication removed and future path-policy changes are single-site; the verification harness can actually fail; the platform behaves correctly for every user rather than the original developer; GUI no longer freezes during scaffolding; exports fail loudly instead of fabricating sample prose; and the audit report itself is committed for transparency.
