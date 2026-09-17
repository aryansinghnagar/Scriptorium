# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

| Path | Purpose | Evidence |
|------|---------|----------|
| `.editorconfig` | Editor whitespace, indentation (tabs for shell, spaces for YAML/Python), and line ending configuration | [`.editorconfig`](file:///.editorconfig#L1-L15) |
| `.gitattributes` | Git line ending normalization (`eol=lf` for shell scripts) and export rules | [`.gitattributes`](file:///.gitattributes#L1-L12) |
| `.github/` | CI/CD automation workflows (continuous integration, ShellCheck lint, test runs) | [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L1-L75) |
| `configs/` | Application configuration templates and rules (e.g. LeechBlock NG focus schedule) | [`configs/leechblock_scriptorium_rules.json`](file:///configs/leechblock_scriptorium_rules.json#L1-L25) |
| `docs/` | Comprehensive technical architecture, author manual, compatibility matrices, roadmaps, audits, and user guides | [`docs/ARCHITECTURE.md`](file:///docs/ARCHITECTURE.md#L1-L490), [`docs/AUTHOR_MANUAL.md`](file:///docs/AUTHOR_MANUAL.md#L1-L349) |
| `docs/codebase/` | Standardized 7-document codebase knowledge base (Stack, Structure, Architecture, Conventions, Integrations, Testing, Concerns) | [`docs/codebase/STACK.md`](file:///docs/codebase/STACK.md#L1-L118) |
| `docs/guides/` | Topic-specific deep guides (Backups, Distraction Control, Obsidian Plugins, Optional Extras, Software Catalog, Typography) | [`docs/guides/SOFTWARE_CATALOG.md`](file:///docs/guides/SOFTWARE_CATALOG.md#L1-L132) |
| `docs/audits/` | Committed independent forensic audit reports and remediation verification trail | [`docs/audits/2026-09-16-external-audit.md`](file:///docs/audits/2026-09-16-external-audit.md#L1-L466) |
| `launchers/` | FreeDesktop `.desktop` GUI application shortcuts for Linux Mint / Debian desktop integration | [`launchers/scriptorium-control-center.desktop`](file:///launchers/scriptorium-control-center.desktop#L1-L15) |
| `scripts/` | Shell automation tools, GTK 3 desktop application, verification harness, and shared discovery libraries | [`scripts/scriptorium`](file:///scripts/scriptorium#L1-L126), [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L1575) |
| `scripts/lib/` | Reusable modular shell helper libraries (`worlds.sh`) for universe, world, and manuscript discovery | [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L247) |
| `templates/` | Starter skeletons and schemas for World Bibles (Obsidian), Manuscripts (novelWriter/Markdown), and Typst | [`templates/world-bible/`](file:///templates/world-bible/00_START_HERE.md#L1-L45), [`templates/manuscript/`](file:///templates/manuscript/nwProject.nwx#L1-L25) |
| `tests/` | Regression test suites, edge case harnesses, and mock file fixtures | [`tests/test_audit_fixes.sh`](file:///tests/test_audit_fixes.sh#L1-L331), [`tests/fixtures/`](file:///tests/fixtures/sample_universe/universe.yaml#L1-L10) |
| `CHANGELOG.md` | Chronological record of features, audit remediations, fixes, and architecture decisions | [`CHANGELOG.md`](file:///CHANGELOG.md#L1-L158) |
| `CONTRIBUTING.md` | Contribution guidelines, quality gate checklist, exit-code contract, and submission flow | [`CONTRIBUTING.md`](file:///CONTRIBUTING.md#L1-L93) |
| `LICENSE` | MIT Open Source license terms | [`LICENSE`](file:///LICENSE#L1-L25) |
| `README.md` | Primary project landing page, quick start, overview, and navigation index | [`README.md`](file:///README.md#L1-L182) |
| `SECURITY.md` | Security scope, installer privilege surface disclosure, and vulnerability reporting protocol | [`SECURITY.md`](file:///SECURITY.md#L1-L40) |

### 2) Entry Points

- **Main runtime entry (Desktop GUI)**: [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L50) — Native Python 3 / GTK 3 Control Center application with 5-tab authoring workflow, visual scene tag editing, live wordcount rollups, and async task runner.
- **Main runtime entry (CLI Facade)**: [`scripts/scriptorium`](file:///scripts/scriptorium#L1-L60) — Unified command dispatcher providing structured subcommands (`universe`, `world`, `manuscript`, `add-volume`, `export`, `snapshot`, `backup`, `restore`, `concordance`, `doctor`, `control-center`, `verify`).
- **Secondary entry points**:
  - [`scripts/control_center.sh`](file:///scripts/control_center.sh#L1-L50) — Lightweight Zenity-based graphical menu fallback when PyGObject/GTK 3 is not available.
  - [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L1-L50) — Automated system installer provisioning dependencies, fonts, binaries, and desktop launchers.
  - [`scripts/verify.sh`](file:///scripts/verify.sh#L1-L50) — 7-stage quality and regression test harness.
  - Standalone workflow scripts (`scripts/init_universe.sh`, `scripts/init_world.sh`, `scripts/init_manuscript.sh`, `scripts/add_book.sh`, `scripts/export_book.sh`, `scripts/save_snapshot.sh`, `scripts/backup_world.sh`, `scripts/restore_world.sh`, `scripts/generate_concordance.sh`, `scripts/world_doctor.sh`, `scripts/scriptorium_doctor.sh`, `scripts/wordcount_report.sh`, `scripts/uninstall_scriptorium.sh`).
- **How entry is selected**:
  - Desktop users click `.desktop` launchers in `~/Desktop` or `~/.local/share/applications/` (e.g. `launchers/scriptorium-control-center.desktop`).
  - Terminal users invoke `./scripts/scriptorium <subcommand> [args]` or individual `scripts/*.sh` executables.

### 3) Module Boundaries

| Boundary | What belongs here | What must not be here |
|----------|-------------------|------------------------|
| **GUI Presentation Layer** (`scripts/scriptorium_app.py`, `scripts/control_center.sh`) | GTK 3 widgets, async worker threads, user dialogs, form input gathering, visual treeviews, log viewers | Direct filesystem schema manipulation without going through helper functions; blocking synchronous subprocess calls on the GTK main UI thread |
| **CLI Facade** (`scripts/scriptorium`) | Command-line argument parsing, subcommand routing, help banners, forwarding arguments to underlying scripts | Core domain logic implementation; duplicating script tasks directly inside the dispatcher |
| **Discovery & Resolution Library** (`scripts/lib/worlds.sh`) | Universe/World/Manuscript directory discovery, path canonicalization, universe label extraction, GUI detection, TTY warning nudges | Mutating filesystem state; creating or deleting projects; invoking compiler tools |
| **Core Workflow Scripts** (`scripts/*.sh`) | Transactional directory scaffolding, Git commit/tag execution, compilation pipelines (Typst/Pandoc), backup archive creation, diagnostic rule checking | GUI toolkit dependencies (must remain runnable headlessly without X11/Wayland); hardcoded absolute user home paths |
| **Templates & Schemas** (`templates/`) | Obsidian `.obsidian/` configs, Dataview queries, Metadata Menu `fileClasses/` YAML schemas, novelWriter XML stubs, Typst typography styling rules | Shell script code; executable binaries; user-specific project data |
| **Test Fixtures & Harnesses** (`tests/`, `scripts/verify.sh`) | Sandboxed test execution, mock directory structures, regression edge cases, assertion checks | Permanent mutations to the real `~/Universes` or `~/Manuscripts` user directories |

### 4) Naming and Organization Rules

- **File naming pattern**:
  - Shell scripts: `snake_case.sh` (e.g. `init_universe.sh`, `save_snapshot.sh`) with POSIX `.sh` extension, except the CLI facade `scriptorium` (no extension).
  - Python scripts: `snake_case.py` (e.g. `scriptorium_app.py`).
  - Launcher files: `kebab-case.desktop` (e.g. `scriptorium-control-center.desktop`, `init-manuscript.desktop`).
  - Documentation files: `UPPER_SNAKE_CASE.md` (e.g. `AUTHOR_MANUAL.md`, `SUPPORT_MATRIX.md`) or `kebab-case.md` for date-stamped audit logs.
  - Template markdown files: `Pascal-Case-Hyphenated.md` (e.g. `Character-Template.md`, `Timeline-Event-Template.md`).
- **Directory organization pattern**:
  - `~/Universes/<UniverseName>/` — Narrative Universe root containing `universe.yaml` and `Universe-Index.md`.
  - `~/Universes/<UniverseName>/<WorldName>/` (or standalone `~/Worlds/<WorldName>/`) — Pure World Lore Vault (Obsidian vault).
  - `~/Manuscripts/<ManuscriptName>/` — Standalone Prose Manuscript Project containing `manuscript.yaml`, `nwProject.nwx`, `Book-*` volumes (`01_Act_I/`, `02_Act_II/`, `03_Act_III/`, `04_Back_Matter/`), `Outlines/`, `Exports/`, `Backups/`.
- **Import aliasing or path conventions**:
  - Shell scripts resolve library path relative to script directory: `source "$(dirname "$0")/lib/worlds.sh"`.
  - Python imports standard library modules and `gi.repository` (Gtk, GLib, Gdk, Pango).

### 5) Evidence

- [`scripts/scriptorium`](file:///scripts/scriptorium#L1-L60)
- [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L60)
- [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L60)
- [`templates/world-bible/`](file:///templates/world-bible/00_START_HERE.md#L1-L30)
- [`templates/manuscript/`](file:///templates/manuscript/nwProject.nwx#L1-L25)

## Extended Sections (Optional)

### Monorepo / Directory Subsystem Map

- `scripts/`:
  - `setup_scriptorium.sh`, `uninstall_scriptorium.sh`: System lifecycle installers.
  - `init_universe.sh`, `init_world.sh`, `init_manuscript.sh`, `add_book.sh`: Project scaffolding engines.
  - `save_snapshot.sh`, `backup_world.sh`, `restore_world.sh`: Version control and disaster recovery.
  - `export_book.sh`: Typst PDF, Pandoc EPUB, and submission DOCX compiler.
  - `generate_concordance.sh`: Automated Dramatis Personae and Glossary back-matter generator.
  - `world_doctor.sh`, `scriptorium_doctor.sh`, `wordcount_report.sh`: Diagnostic and analytics engines.
  - `control_center.sh`, `scriptorium_app.py`: User interface controllers.
- `templates/world-bible/`:
  - `Characters/`, `Locations/`, `Factions/`, `Magic-Technology/`, `Bestiary/`, `Artifacts/`, `Cosmology/`, `History/`, `Languages/`: Domain entity templates.
  - `Templates/fileClasses/`: Metadata Menu YAML schemas enforcing frontmatter structure.
  - `.obsidian/`: Out-of-the-box plugin configurations for Dataview, Obsidian Git, Calendarium, Storyteller, Longform, Novel Word Count.
