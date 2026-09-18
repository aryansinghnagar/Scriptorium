# Changelog

All notable changes to Ars Arcanum are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Scope decisions
behind each wave are recorded in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## [Unreleased]

### Changed & Renamed (Ars Arcanum Transition)
- **Project Renaming**:
  - Renamed the project from "Scriptorium" to "Ars Arcanum" across the entire codebase, documentation, templates, desktop launchers, Debian packaging, and Git remote.
  - Provided new unified CLI commands `arcanum` and `ars-arcanum` with backward-compatible `scriptorium` fallback.
  - Renamed scripts: `setup_arcanum.sh`, `uninstall_arcanum.sh`, `arcanum_doctor.sh`, `arcanum_app.py`, `leechblock_arcanum_rules.json`.
  - Renamed performance cache artifact to `.arcanum_cache.json` with fallback support.
- **Privacy & Asset Provenance (Data Minimization & Attribution)**:
  - Added [PRIVACY.md](PRIVACY.md) specifying zero telemetry, local-only processing, and explicit consent policies.
  - Added [REFERENCES.md](REFERENCES.md) with complete Open Source / Creative Commons attribution records for non-commercial use.
  - Scrubbed personal identifiable information (PII) across the codebase in favor of generic maintainer identifiers and official repository links.

### Fixed & Hardened (Master Forensic Audit Remediation)
- **CLI & Diagnostics Robustness**:
  - Added `-m, --manuscript NAME` option parsing to `scripts/arcanum_doctor.sh` and option forwarding to `world_doctor.sh` (DEV-01).
  - Unmasked Stage 6k in `scripts/verify.sh` to enforce real doctor exit codes without `|| true` masking (DEV-02).
  - Fixed snapshot discovery lockout in `scripts/save_snapshot.sh` for authors with 0 world lore vaults (DEV-03).
  - Fixed unbound variable crashes under `set -u` in `scripts/export_book.sh` (line 217) and `scripts/generate_concordance.sh` (line 192).
  - Standardized CLI usage error exit codes to `2` across all 15 entry-point scripts per `docs/ARCHITECTURE.md` contract (CQA-01).
- **Typography & Publishing Polish**:
  - Suppressed running headers and page folios on blank verso pages in `templates/typst/book_template.typ` (TYP-01).
  - Added `-f markdown-citations+smart` to Pandoc EPUB compilation in `scripts/export_book.sh` and CI for curly quotes and em-dashes (TYP-03).
- **Template & Directory Invariants**:
  - Restored Dataview queries in `templates/manuscript/Outlines/Subplot-Thread-Matrix.md` to `FROM ""` for ADR-022 compatibility (AUT-01).
  - Scoped `is_template` in `scripts/world_doctor.sh` to validate `World-Bible-Index.md` while preventing false-positive orphan reports on `fileClasses/` and writing logs (WLD-01).
  - Initialized primary `~/Universes` and `~/Manuscripts` directory roots in `scripts/setup_arcanum.sh` (SYS-01).
  - Modernized `docs/AUTHOR_MANUAL.md` and `templates/world-bible/00_START_HERE.md` to remove legacy single-vault path assumptions (AUT-02, AUT-03).
- **Security & Discovery Hardening (ADR-023)**:
  - Hardened Typst binary installer in `scripts/setup_arcanum.sh` to fail closed (`TYPST_OK=0`) when SHA-256 digest is unavailable, preventing unverified binary installation.
  - Enhanced `scripts/lib/worlds.sh` to discover direct depth-2 (`~/Universes/<Universe>/<World>`), legacy subfolder depth-3 (`~/Universes/<Universe>/Worlds/<World>`), and legacy root (`~/Worlds/<World>`) structures without polluting discovery with the literal `"Worlds"` directory, and fixed `universe_label` for depth-3 worlds.
  - Expanded `world_doctor.sh` chronological paradox engine (`WLD-104`) with ISO 8601 calendar date parsing (`YYYY-MM-DD`, `YYYY-MM`, `YYYY/MM/DD`).
  - Added manuscript and outline indexing to Pass 3 of `world_doctor.sh` to resolve intra-manuscript wikilinks (e.g. `[[Master-Outline]]`) without false-positive `WLD-108` lore drift findings.
  - Added snapshot history reload to HeaderBar Quick Snapshot and protected YAML frontmatter during scene tag updates in `scripts/arcanum_app.py`.
- **Desktop & Python Ergonomics**:
  - Migrated external `which` subprocesses in `scripts/arcanum_app.py` to standard library `shutil.which`.
  - Standardized FreeDesktop categories across `launchers/*.desktop` to `Office;WordProcessor;Publishing;` (UX-01).
  - Integrated execution of all `tests/*.sh` regression test suites into GitHub Actions CI (`.github/workflows/ci.yml`).

### Added
- **Centralized User Guides**: Unified all reference and setup documentation under `docs/guides/`:
  - `docs/guides/SOFTWARE_CATALOG.md`: Direct download URLs, APT/Flatpak package IDs, and installation instructions.
  - `docs/guides/TYPOGRAPHY_AND_FONTS.md`: High-quality open typefaces, installation commands, and Typst novel formatting rules.
  - `docs/guides/OBSIDIAN_PLUGINS.md`: Out-of-the-box Obsidian plugin suite and metadata schemas guide.
  - `docs/guides/OPTIONAL_EXTRAS.md`: Specialized cartography and lore tooling (Azgaar, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix).
  - `docs/guides/BACKUP_SETUP.md`: 3-2-1 backup implementation guide with Déjà Dup.
  - `docs/guides/DISTRACTION_CONTROL.md`: XFCE Do Not Disturb configuration and FocusWriter sprint tips.
- **Consolidated System Architecture & Roadmap**:
  - `docs/ARCHITECTURE.md`: Complete Architectural Decision Records (ADR-001 through ADR-023), system design invariants, C4 Mermaid architecture diagrams, subsystem deep dives, confidence assessment table, and local file citations.
  - `docs/ROADMAP.md`: Project charter, hardware baselines, milestones (M0–M15), and real-time operational status queues.
- **Modernized Desktop Launcher Suite**:
  - Added `launchers/init-manuscript.desktop` for 1-click Standalone Manuscript creation.
  - Standardized all launchers in `launchers/` with `TryExec=bash` and valid desktop categories.
  - Updated `scripts/setup_arcanum.sh`, `scripts/uninstall_arcanum.sh`, and `scripts/arcanum_doctor.sh` to install, check, and purge `init-manuscript.desktop`.
- **Modernized Test Fixtures**: Restructured `tests/fixtures/` into `sample_universe/`, `sample_world/`, and `sample_manuscript/` reflecting separated lore and manuscript architecture.
- **Separated Pure World Lore & Manuscript Architecture**:
  - `~/Universes/<UniverseName>/<WorldName>/`: World Lore Vaults are now pure, direct Obsidian vaults without nested `00-World-Bible` wrappers or mixed manuscript folders.
  - `~/Manuscripts/<ManuscriptName>/`: Independent Prose Manuscript Projects containing multi-volume 3-act drafting hierarchies (`Book-01/`, `Book-02/`), `Outlines/`, `Exports/`, `Backups/`, `nwProject.nwx`, and `manuscript.yaml` linking to universes and lore vaults.
- **Visual Scene Metadata Inspector in GTK Studio (Tab 2)**: Non-technical GUI control panel allowing authors to view and modify `@pov:`, `@char:`, `@location:`, `@thread:`, `@time:`, and `@status:` scene tags with safe in-place header rewrites.
- **Standardized Scene Tagging Protocol**: Promoted `@location:` as the standard tag across chapter templates, scene generators, novelWriter manifests, and diagnostic tooling (deprecating `@focus:`).
- **Expanded CLI Facade Subcommands**: `scriptorium manuscript`, `scriptorium world`, `scriptorium universe`, `scriptorium add-volume` with full listing flags (`--list`), discovery, and backwards compatibility.
- Standard Manuscript Submission Format (`.docx`): Pandoc export bridge in `scripts/export_book.sh`, `scriptorium export`, and Control Center GUI (Publishing Studio) supporting `--format submission` / `--docx` / `--format all` for agent and editorial submissions.
- `templates/world-bible/00_START_HERE.md` and `templates/world-bible/Characters/Character-Quickstart-Template.md`: Minimum Viable World Bible guide and streamlined 5-field character starter card for beginners.
- Manuscript-to-Lore Name Drift Detection (`WLD-108`) in `scripts/world_doctor.sh`: Cross-validates `@pov:`, `@char:`, `@location:`, `@faction:`, `@item:`, and wikilink entity references in manuscript draft scenes against World Bible dossiers and aliases.
- `tests/test_audit_claude_improvements.sh`: Comprehensive automated test suite verifying `obsidian-git` config, `WLD-108` name drift, beginner templates, standard submission `.docx` export, and deterministic multi-volume EPUB selection.
- `scripts/lib/worlds.sh` — shared world-discovery library (discover, resolve,
  universe labels, name sanitization, GUI detection), sourced by 11 entry-point
  scripts; removes ~300 lines of copy-pasted discovery logic and the
  identity-based "Standalone" heuristics (Q-01, F-03).
- `CONTRIBUTING.md` — ground rules, dev setup, the quality gate, exit-code
  contract, commit style, and submission flow (H-01).
- `SECURITY.md` — installer privilege-surface disclosure enumerating every
  `sudo` operation, plus the private vulnerability-reporting process (S-05).
- `CHANGELOG.md` — this file.
- CI hardening: least-privilege `permissions: contents: read`, Typst toolchain
  pinned to `0.13` with a documented bump policy, weekly drift run, and
  `tests/*.sh` joined to the ShellCheck scope (C-01, C-02, C-03).
- Regression coverage: hostile-filename injection probe, archive
  traversal/hook-planting refusal, empty-manuscript export guard, hybrid-role
  Dramatis Personae dedup, multi-world resolution, and the legacy-root
  auto-select nudge (Test 7).

### Changed
- Repository root decluttered to the standard OSS entry set (README, CHANGELOG,
  LICENSE, CONTRIBUTING, SECURITY) and all cross-links updated (ADR-021).
- The exit-code contract is documented as the four values the code actually
  uses — 0 success, 1 runtime/diagnostic failure, 2 usage/environment error,
  3 nothing to act on — replacing the stale "0/1/3" wording (N-01).
- A bare invocation that auto-selects a single world living under the legacy
  `~/Worlds` root now prints the same deprecation nudge as by-name resolution;
  the message is centralized in `warn_if_legacy_root` (Q-03, N-03).
- GTK app threading polish: thread creation centralized in `_start_worker`
  with `daemon=True` so quitting mid-operation no longer leaves the process
  lingering; the five external-app launch chains (and their `flatpak info` /
  `which` probes) run on daemon workers instead of the GUI thread; snapshot
  default notes use `datetime.now()` instead of a `date` subprocess (F-04, N-04).
- The Typst installer requires a matching GitHub-published SHA-256 digest
  before `sudo install` and refuses otherwise; GitHub API rate-limiting now
  warns explicitly instead of silently skipping (S-01).
- Backup metadata is written with `json.dump` instead of an unescaped heredoc
  (F-07); wordcount reports an explicit warning when a file exceeds the 8 MB
  read cap instead of truncating silently (F-08); manuscript snapshotting
  surfaces git index-lock contention instead of dropping commits silently (Q-04).

### Fixed
- `scripts/verify.sh` stage 6d: Fixed EPUB selection race where arbitrary file order picked volume-scoped exports instead of the omnibus build; both volume-isolated and omnibus outputs are now explicitly inspected.
- `templates/world-bible/.obsidian/plugins/obsidian-git/data.json`: Set `"basePath": ""` so Obsidian Git targets the direct vault repository root (DOC-03 correction: earlier text claimed `".."`); removed dead settings keys (`gitLocation`, `baseSubmodule`, `autoBackupFileName`).
- Calibre installs under its real Flathub ID `com.calibre_ebook.calibre`
  (the previous ID never existed, so setup could never install Calibre)
  across setup, doctor, uninstaller, app, and both compatibility docs (F-01).
- The verification harness fails closed: stages report failures instead of
  being swallowed by `set -e` + `cmd && echo` chains, and the CI
  syntax-validation step follows the same pattern (F-02).
- World-doctor JSON crosses the shell/Python boundary via stdin
  (`json.load(sys.stdin)`) instead of interpolation into `python3 -c` source,
  eliminating code injection through crafted filenames (S-02).
- All doctor subprocess invocations use list argv without `shell=True` (S-03).
- Archive restore is hardened: absolute paths, `..` traversal, unexpected root
  entries, and non-sample `.git/hooks` members are refused before extraction;
  extraction neutralizes ownership/permission restoration (S-04).
- Bare doctor/wordcount invocations discover worlds (auto-select when exactly
  one exists, list with universe labels and exit 2 when ambiguous) instead of
  defaulting to `~/Worlds`, which is a container of worlds (F-05).
- Exporting a fully empty manuscript hard-fails with "no manuscript content
  found" instead of fabricating sample prose (F-06).
- `04-Publishing/` outputs are ignored by the root and generated world
  `.gitignore`s so compiled PDFs/EPUBs stop accumulating in snapshot history (F-09).
- Hybrid roles (e.g. "Major Rival") appear exactly once in the Dramatis
  Personae under the documented precedence (F-10).

### Removed
- Dead legacy Calibre Flathub ID (`com.calibredesk.calibre`) from the app's
  launch chain — a branch that could never match (N-05).
- Hardcoded developer username (`"aryan"`) heuristics from all scripts,
  replaced by structural path-prefix detection (F-03).
- Four pre-existing dead `PROJECT_ROOT` variable declarations that would have
  failed the tightened ShellCheck gate (SC2034).

### Security
- CI actions pinned by full commit SHA; workflow limited to `contents: read`.
- Co-located `sha256.manifest` backups are documented as integrity-only
  (bit-rot protection), not authenticity — stated plainly in SECURITY.md and
  the backup code comments.
