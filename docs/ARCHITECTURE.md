# Ars Arcanum Technical Architecture & System Blueprint

> **One definitive, audited architecture reference for Ars Arcanum — an open, distraction-free authoring and worldbuilding platform on Linux.**

---

## Part 1 — Whole-Repo Technical Deep-Dive

### 1.1 What Ars Arcanum Is
Ars Arcanum is a purpose-built, distraction-free authoring and speculative worldbuilding environment designed for Linux workstations (Linux Mint XFCE editions 21/22 and Debian 12/13 XFCE) ([`README.md#L1-L25`](file:///README.md#L1-L25), [`docs/AUTHOR_MANUAL.md#L1-L42`](file:///docs/AUTHOR_MANUAL.md#L1-L42)). It combines standard open-source tools (Obsidian, novelWriter, FocusWriter, LibreOffice Writer, Calibre, Typst, Pandoc, and Git) into a unified, zero-terminal desktop experience. All prose, character dossiers, lore notes, and timelines are stored in standard plain Markdown (`.md`) and open formats on the author's local hard drive with zero vendor lock-in, automated multi-tier version control, and 3-2-1 verified disaster recovery.

### 1.2 Tech-Stack Detection Table

| Layer | Technology | Evidence (File & Line) |
| :--- | :--- | :--- |
| **Desktop Application GUI** | Python 3 + PyGObject (`Gtk 3.0`, `GLib`, `Gdk`, `Pango`) + GTK 4/Libadwaita | [`scripts/arcanum_app.py#L1-L50`](file:///scripts/arcanum_app.py#L1-L50), [`scripts/lib/ui_gtk3.py#L1-L60`](file:///scripts/lib/ui_gtk3.py#L1-L60), [`scripts/lib/ui_adw.py#L1-L60`](file:///scripts/lib/ui_adw.py#L1-L60) |
| **Fallback Graphical Dialogs** | Zenity (GTK dialog utility) | [`scripts/control_center.sh#L1-L30`](file:///scripts/control_center.sh#L1-L30), [`scripts/lib/worlds.sh#L40-L45`](file:///scripts/lib/worlds.sh#L40-L45) |
| **CLI Dispatcher & Tooling** | POSIX Shell / Bash 4+ | [`scripts/arcanum#L1-L40`](file:///scripts/arcanum#L1-L40), [`scripts/setup_arcanum.sh#L1-L30`](file:///scripts/setup_arcanum.sh#L1-L30) |
| **Shared Discovery Engine** | Modular Shell Library (`scripts/lib/worlds.sh`) | [`scripts/lib/worlds.sh#L1-L45`](file:///scripts/lib/worlds.sh#L1-L45) |
| **Fast Performance Cache** | mtime-keyed JSON/SQLite Cache Engine | [`scripts/lib/cache.py#L1-L50`](file:///scripts/lib/cache.py#L1-L50) |
| **Semantic Continuity Engine** | Offline Attribute & Lore Consistency Validator | [`scripts/lib/continuity.py#L1-L50`](file:///scripts/lib/continuity.py#L1-L50) |
| **Multi-Draft & Redline Comparator** | Discrete Draft Manager + Difflib Visual Redline Engine | [`scripts/init_draft.sh#L1-L40`](file:///scripts/init_draft.sh#L1-L40), [`scripts/lib/manuscript_diff.py#L1-L60`](file:///scripts/lib/manuscript_diff.py#L1-L60), [`scripts/compare_drafts.sh#L1-L40`](file:///scripts/compare_drafts.sh#L1-L40) |
| **Configuration & Secure Replication** | JSON Configuration Engine + Dual-Target Backup Manager | [`scripts/lib/config.py#L1-L40`](file:///scripts/lib/config.py#L1-L40), [`scripts/backup_world.sh#L1-L60`](file:///scripts/backup_world.sh#L1-L60) |
| **Word Processor & DOCX Engine** | Pure Python OpenXML Generator & Hardened Bidirectional Sync Engine | [`scripts/lib/docx_sync.py#L1-L60`](file:///scripts/lib/docx_sync.py#L1-L60) |
| **Prose Stylistics & Dialogue Linter** | AST Tokenizer, Dialogue Attribution & Echo Scanner | [`scripts/lib/stylistics.py#L1-L60`](file:///scripts/lib/stylistics.py#L1-L60) |
| **Character Voice Profiler** | Lexical Fingerprint Analyzer & Grade Level Scorer | [`scripts/lib/voice.py#L1-L60`](file:///scripts/lib/voice.py#L1-L60) |
| **Smart Typography Normalizer** | Locale-Aware Quotation & Punctuation Engine | [`scripts/lib/typography_cleaner.py#L1-L60`](file:///scripts/lib/typography_cleaner.py#L1-L60) |
| **Plot Matrix & Structure Enforcer** | Multi-Track Plot Grid & Narrative Beat Alignment | [`scripts/lib/plot_matrix.py#L1-L60`](file:///scripts/lib/plot_matrix.py#L1-L60), [`scripts/lib/structure.py#L1-L60`](file:///scripts/lib/structure.py#L1-L60) |
| **Scene Mechanics & Focus Engine** | Motivation-Reaction Units (MRU) & Ambient Audio Generator | [`scripts/lib/scene_mechanics.py#L1-L60`](file:///scripts/lib/scene_mechanics.py#L1-L60), [`scripts/lib/ambient.py#L1-L60`](file:///scripts/lib/ambient.py#L1-L60) |
| **Publishing Pre-Flight & Barcodes** | PDF/EPUB Compliance Linter & EAN-13 Vector Barcode Generator | [`scripts/lib/preflight.py#L1-L60`](file:///scripts/lib/preflight.py#L1-L60), [`scripts/lib/barcode.py#L1-L60`](file:///scripts/lib/barcode.py#L1-L60) |
| **Front/Back Matter & Query Builder** | Copyright/Catalog Builder & 1-Page Synopsis Scaffolder | [`scripts/lib/frontmatter_builder.py#L1-L60`](file:///scripts/lib/frontmatter_builder.py#L1-L60), [`scripts/init_query.py#L1-L60`](file:///scripts/init_query.py#L1-L60) |
| **Cartography & Static Codex Wiki** | Offline Vector Map Scraper & Static HTML Reader Wiki | [`scripts/lib/cartography.py#L1-L60`](file:///scripts/lib/cartography.py#L1-L60), [`scripts/lib/codex_export.py#L1-L60`](file:///scripts/lib/codex_export.py#L1-L60) |
| **Series Continuity & Tactical Sim** | Cross-Book Inventory/Canon & Lanchester Combat Simulator | [`scripts/lib/series_continuity.py#L1-L60`](file:///scripts/lib/series_continuity.py#L1-L60), [`scripts/lib/tactical_sim.py#L1-L60`](file:///scripts/lib/tactical_sim.py#L1-L60) |
| **Distribution Packager & Portfolio** | KDP/Ingram Multi-Platform Bundler & Executive Portfolio | [`scripts/package_distribution.py#L1-L60`](file:///scripts/package_distribution.py#L1-L60), [`scripts/lib/portfolio.py#L1-L60`](file:///scripts/lib/portfolio.py#L1-L60) |
| **Audio Proofreading Engine** | Offline Neural TTS Player (Piper/espeak-ng subprocess bridge) | [`scripts/lib/tts_reader.py#L1-L60`](file:///scripts/lib/tts_reader.py#L1-L60) |
| **Astrophysics & Flight Engine** | Pure Python Relativistic Kinematics, Orbit & Comms Engine | [`scripts/lib/astrophysics.py#L1-L60`](file:///scripts/lib/astrophysics.py#L1-L60) |
| **Hard Magic & Constraint Matrix** | Offline Arcane Rule, Reagent & Fatigue Diagnostic Engine | [`scripts/lib/magic_system.py#L1-L60`](file:///scripts/lib/magic_system.py#L1-L60) |
| **Dynastic Genealogy Engine** | Family Tree DAG Builder, Succession & Paradox Validator | [`scripts/lib/genealogy.py#L1-L60`](file:///scripts/lib/genealogy.py#L1-L60) |
| **Conlang & Sound Mutation Engine** | Phonotactic Syllable Generator & Sound Shift Applier | [`scripts/lib/conlang.py#L1-L60`](file:///scripts/lib/conlang.py#L1-L60) |
| **Narrative Pacing & Tension Engine** | Prose Mode Classifier, POV Balance & Tension Arc Model | [`scripts/lib/pacing.py#L1-L60`](file:///scripts/lib/pacing.py#L1-L60) |
| **Journey Modeler & Planetary Calendar** | Terrain Friction Expedition Engine & Multi-Moon Planetary Calendar | [`scripts/lib/journey.py#L1-L60`](file:///scripts/lib/journey.py#L1-L60), [`scripts/lib/calendar.py#L1-L60`](file:///scripts/lib/calendar.py#L1-L60) |
| **Faction Matrix & Campaign Logistics** | Lanchester Combat Equations, Wagon Radius & Alliance Paradox Detector | [`scripts/lib/factions.py#L1-L60`](file:///scripts/lib/factions.py#L1-L60) |
| **Economy & Commodity PPP Matrix** | Multi-Currency Basket PPP, Trade Route Margins & Tech Era Audit | [`scripts/lib/economy.py#L1-L60`](file:///scripts/lib/economy.py#L1-L60) |
| **Causal DAG & Multiverse Engine** | Event DAG Cycle Detection, Novikov Self-Consistency & Timeline Branching | [`scripts/lib/causality.py#L1-L60`](file:///scripts/lib/causality.py#L1-L60) |
| **Planetary Climate & Trophic Food Web** | Insolation, Orographic Rain Shadow & Lindeman 10% Biomass Pyramids | [`scripts/lib/climate.py#L1-L60`](file:///scripts/lib/climate.py#L1-L60), [`scripts/lib/ecology.py#L1-L60`](file:///scripts/lib/ecology.py#L1-L60) |
| **Earth Eponyms & 6D Sensory Palette** | Immersion De-Eponym Scanner & 6-Dimensional Sensory Palette Engine | [`scripts/lib/idioms.py#L1-L60`](file:///scripts/lib/idioms.py#L1-L60), [`scripts/lib/senses.py#L1-L60`](file:///scripts/lib/senses.py#L1-L60) |
| **Ciphers & Prophecy Resolution Matrix** | Classical Ciphers, Phonetic Runes & Oracle Fulfillment Lifecycle | [`scripts/lib/cipher.py#L1-L60`](file:///scripts/lib/cipher.py#L1-L60), [`scripts/lib/prophecy.py#L1-L60`](file:///scripts/lib/prophecy.py#L1-L60) |
| **Typesetting & PDF Engine** | Typst `0.14.2` pinned (musl static binary) | [`docs/COMPATIBILITY.md#L9-L21`](file:///docs/COMPATIBILITY.md#L9-L21), [`scripts/export_book.sh#L340-L420`](file:///scripts/export_book.sh#L340-L420) |
| **Document AST Converter** | Pandoc (`3.1.x` / `2.19.x`) | [`scripts/export_book.sh#L190-L330`](file:///scripts/export_book.sh#L190-L330), [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **World Bible Vault** | Obsidian (`md.obsidian.Obsidian` via Flathub) + 10 Vendored Plugins | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32), [`templates/world-bible/.obsidian/`](file:///templates/world-bible/.obsidian/community-plugins.json#L1-L15) |
| **Manuscript Outlining & Drafting** | novelWriter (`io.gitlab.novelwriter.novelWriter` via Flathub) | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32), [`templates/manuscript/nwProject.nwx#L1-L15`](file:///templates/manuscript/nwProject.nwx#L1-L15) |
| **Ebook Compilation & Inspection** | Calibre (`com.calibre_ebook.calibre` via Flathub) | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32), [`scripts/setup_arcanum.sh#L142-L209`](file:///scripts/setup_arcanum.sh#L142-L209) |
| **Distraction Control** | FocusWriter (distraction-free) + LeechBlock NG (Firefox) | [`docs/guides/DISTRACTION_CONTROL.md#L1-L34`](file:///docs/guides/DISTRACTION_CONTROL.md#L1-L34), [`configs/leechblock_arcanum_rules.json#L1-L25`](file:///configs/leechblock_arcanum_rules.json#L1-L25) |
| **Version Control & Backups** | Git (local multi-tier) + Tar / Gzip / SHA-256 | [`scripts/save_snapshot.sh#L1-L60`](file:///scripts/save_snapshot.sh#L1-L60), [`scripts/backup_world.sh#L1-L60`](file:///scripts/backup_world.sh#L1-L60) |

### 1.3 Entry Points

1. **Desktop GUI Application**: [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py#L1-L50) / [`scripts/lib/ui_gtk3.py`](file:///scripts/lib/ui_gtk3.py#L1-L60) / [`scripts/lib/ui_adw.py`](file:///scripts/lib/ui_adw.py#L1-L60). Provides a 6-studio authoring dashboard with live word counts, Visual Scene Metadata Inspector, Word Processor toolbar, Draft Revisions & Redline Comparator, 1-click publishing, 18 craft/speculative fiction tools, first-run wizard, and diagnostics.
2. **Unified CLI Facade**: [`scripts/arcanum`](file:///scripts/arcanum#L1-L60) (executable dispatcher routing subcommands: `write`, `new`, `draft`, `compare`, `save`, `publish`, `words`, `word`, `docx`, `docx-sync`, `config`, `universe`, `world`, `concordance`, `continuity`, `faction`, `economy`, `causality`, `ecology`, `climate`, `idioms`, `senses`, `cipher`, `prophecy`, `backup`, `backup-dest`, `restore`, `doctor`, `cache`, `calc`, `magic-check`, `magic-report`, `magic`, `genealogy`, `lineage`, `conlang`, `pace`, `tension`, `journey`, `calendar`, `gui`, `verify`, `audit`, `polish`, `plot`, `preflight`, `barcode`, `frontmatter`, `query`, `map`, `codex`, `package`, `portfolio`, `ambient`, `sim`, `read`).
3. **Zenity Fallback GUI**: [`scripts/control_center.sh`](file:///scripts/control_center.sh#L1-L40) (lightweight dialog menu invoked when GTK 3 is not present).
4. **Desktop Application Launchers**: [`launchers/*.desktop`](file:///launchers/arcanum-control-center.desktop#L1-L15) installed to `~/Desktop` and `~/.local/share/applications/`.
5. **System Installer**: [`scripts/setup_arcanum.sh`](file:///scripts/setup_arcanum.sh#L1-L50) (provisions packages, fonts, Typst musl binary, and desktop shortcuts).

### 1.4 Commands & Verification Inventory

| Command | Purpose | Verification Source / Evidence | Trigger / Enforcement |
| :--- | :--- | :--- | :--- |
| `bash scripts/setup_arcanum.sh` | Automated system setup & package installer | [`scripts/setup_arcanum.sh#L1-L343`](file:///scripts/setup_arcanum.sh#L1-L343) | Manual install / Initial provisioning |
| `bash scripts/setup_arcanum.sh --dry-run` | Safe preview simulation of setup installer | [`scripts/setup_arcanum.sh#L35-L60`](file:///scripts/setup_arcanum.sh#L35-L60) | Verified in `verify.sh` Stage 6m |
| `bash scripts/verify.sh` | Canonical 7-stage quality and regression test harness | [`scripts/verify.sh#L1-L496`](file:///scripts/verify.sh#L1-L496) | Pre-commit gate & CI required workflow |
| `bash tests/test_audit_fixes.sh` | Regression suite for forensic audit remediations (Tests 1–37) | [`tests/test_audit_fixes.sh#L1-L550`](file:///tests/test_audit_fixes.sh#L1-L550) | Executed in CI ([`.github/workflows/ci.yml#L50-L55`](file:///.github/workflows/ci.yml#L50-L55)) |
| `bash tests/test_deep_audit.sh` | Deep integration suite for schemas, Dataview DQL, and CLI | [`tests/test_deep_audit.sh#L1-L125`](file:///tests/test_deep_audit.sh#L1-L125) | Executed in CI ([`.github/workflows/ci.yml#L50-L55`](file:///.github/workflows/ci.yml#L50-L55)) |
| `bash tests/test_concordance_edge_cases.sh` | Edge-case tests for concordance generator & multi-era dates | [`tests/test_concordance_edge_cases.sh#L1-L200`](file:///tests/test_concordance_edge_cases.sh#L1-L200) | Executed in CI ([`.github/workflows/ci.yml#L50-L55`](file:///.github/workflows/ci.yml#L50-L55)) |
| `bash tests/test_audit_claude_improvements.sh` | Obsidian Git, WLD-108 name drift, and submission format tests | [`tests/test_audit_claude_improvements.sh#L1-L120`](file:///tests/test_audit_claude_improvements.sh#L1-L120) | Executed in CI ([`.github/workflows/ci.yml#L50-L55`](file:///.github/workflows/ci.yml#L50-L55)) |
| `bash tests/test_continuity_engine.sh` | Semantic continuity trait and contradiction detection tests | [`tests/test_continuity_engine.sh#L1-L150`](file:///tests/test_continuity_engine.sh#L1-L150) | Executed in `verify.sh` Stage 6j |
| `bash tests/test_performance_cache.sh` | Fast performance cache and mtime invalidation tests | [`tests/test_performance_cache.sh#L1-L140`](file:///tests/test_performance_cache.sh#L1-L140) | Executed in `verify.sh` Stage 6j |
| `bash tests/test_drafts_and_diff.sh` | Multi-draft lifecycle, visual redline diff, and dual backup tests | [`tests/test_drafts_and_diff.sh#L1-L130`](file:///tests/test_drafts_and_diff.sh#L1-L130) | Executed in `verify.sh` Stage 6k |
| `bash tests/test_docx_sync.sh` | OpenXML DOCX generation and bidirectional sync tests | [`tests/test_docx_sync.sh#L1-L130`](file:///tests/test_docx_sync.sh#L1-L130) | Executed in `verify.sh` Stage 6l |
| `python -m unittest discover -s tests -p "test_*.py"` | Python unit test suite (282 tests across 50 test modules) | [`tests/test_*.py`](file:///tests/) | Executed in `verify.sh` Stage 1 |
| `ruff check .` | Fast Python linter enforcing PEP8, security, and bug prevention | [`pyproject.toml#L1-L30`](file:///pyproject.toml#L1-L30) | Executed in CI lint step (0 errors enforced) |
| `shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/arcanum` | Shell static analysis and linting (zero warnings enforced) | [`.github/workflows/ci.yml#L28-L36`](file:///.github/workflows/ci.yml#L28-L36) | Executed in CI lint step |
| `python3 -m py_compile scripts/arcanum_app.py scripts/lib/*.py` | Python bytecode syntax and compilation check | [`.github/workflows/ci.yml#L37-L40`](file:///.github/workflows/ci.yml#L37-L40), [`scripts/verify.sh#L27-L33`](file:///scripts/verify.sh#L27-L33) | Executed in CI & `verify.sh` Stage 1 |
| `bash -n scripts/*.sh scripts/lib/*.sh scripts/arcanum` | Bash syntax validation | [`scripts/verify.sh#L18-L26`](file:///scripts/verify.sh#L18-L26) | Executed in `verify.sh` Stage 1 |

*CI Enforcement Note*: GitHub Actions workflow [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) runs on every push and pull request to `main`. Required status check enforcement is managed via repository branch protection rules (GitHub Settings -> Branches -> Branch Protection Rules).

### 1.5 Directory Layout & Purpose

```text
7-Scriptorium/
├── .github/workflows/     → CI/CD automation workflows (ci.yml)
├── configs/               → Distraction control and external tool config templates
├── debian/                → Debian packaging metadata (control, rules, changelog, copyright)
├── docs/                  → Master technical architecture, manuals, support matrices, roadmaps
│   └── guides/            → Topic-specific deep guides (Backups, Typography, Plugins, Catalog)
├── launchers/             → FreeDesktop .desktop launcher files for desktop integration
├── scripts/               → Scriptorium CLI facade, GTK 3 desktop application, workflow scripts
│   └── lib/               → Modular libraries (astrophysics.py, magic_system.py, genealogy.py, conlang.py, pacing.py, journey.py, calendar.py, docx_sync.py, manuscript_diff.py, config.py, cache.py, continuity.py, worlds.sh)
├── templates/             → Scaffolding templates for World Bibles, Manuscripts, and Typst
│   ├── manuscript/        → 3-Act volume hierarchies, outlines, and novelWriter XML schemas
│   ├── typst/             → Publication-grade Typst novel templates and sample previews
│   └── world-bible/       → Pure Obsidian lore vault templates, fileClasses, and vendored plugins
└── tests/                 → Automated regression test suites, edge case suites, and fixtures
    └── fixtures/          → Sample mock universes, world lore vaults, and manuscripts
```

### 1.6 Deployment & Runtime Surface

| Runtime / Component | Pinned Version / Source | Target Scope | Evidence |
| :--- | :--- | :--- | :--- |
| **Linux Distribution** | Linux Mint `21.x` / `22.x` (Wilma), Debian `12` / `13` (Trixie), Ubuntu `24.04` LTS | Host Operating System (Tier 1) | [`docs/SUPPORT_MATRIX.md#L9-L18`](file:///docs/SUPPORT_MATRIX.md#L9-L18) |
| **Python Runtime** | `3.10+` (tested on `3.12.x`) | Host APT (`python3`, `python3-gi`) | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **GTK 3 Toolkit** | `3.24+` (`gir1.2-gtk-3.0`) | Host Desktop UI | [`scripts/arcanum_app.py#L20-L30`](file:///scripts/arcanum_app.py#L20-L30) |
| **Typst Typesetter** | `0.14.2` pinned (`x86_64`/`aarch64-unknown-linux-musl`) | Binary in `/usr/local/bin/typst` (SHA-256 verified) | [`dependencies.lock#L1-L15`](file:///dependencies.lock#L1-L15), [`docs/COMPATIBILITY.md#L9-L21`](file:///docs/COMPATIBILITY.md#L9-L21) |
| **Pandoc Converter** | `>= 2.16.0` (`3.1.x` / `2.19.x`) | Host APT (`pandoc`) | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **Obsidian Vault App** | `md.obsidian.Obsidian` (Flathub stable) | Flatpak container | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32) |
| **novelWriter Editor** | `io.gitlab.novelwriter.novelWriter` (Flathub stable) | Flatpak container | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32) |
| **Calibre Suite** | `com.calibre_ebook.calibre` (Flathub stable) | Flatpak container | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32) |
| **CI Runner Image** | `ubuntu-24.04` (pinned) | GitHub Actions CI | [`.github/workflows/ci.yml#L15-L25`](file:///.github/workflows/ci.yml#L15-L25) |

### 1.7 EOL / Dead-Dependency Scan

- **Python 2.x**: Fully absent. All Python code is strictly modern Python 3.10+ using standard library and PyGObject introspection ([`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py#L1-L35)).
- **GTK 2 / PyGTK**: Fully absent. Modern GTK 3.0 introspection is enforced (`gi.require_version("Gtk", "3.0")`).
- **LaTeX / PDFTeX**: Explicitly rejected in favor of Typst ([ADR-003](#adr-003-typst--pandoc-for-typesetting-vs-latex--indesign--vellum)).
- **Legacy Flatpak ID (`com.calibre_ebook.Calibre`)**: Remediated in ADR-020 to official Flathub ID `com.calibre_ebook.calibre` ([`docs/COMPATIBILITY.md#L32`](file:///docs/COMPATIBILITY.md#L32)).
- **Legacy Nested Vault Structure (`00-World-Bible` / `01-Manuscript`)**: Deprecated and replaced with separated pure World Lore Vaults (`~/Universes/<Universe>/<World>`) and standalone Prose Manuscripts (`~/Manuscripts/<Manuscript>`) ([ADR-022](#adr-022-separated-lore--manuscript-architecture-visual-scene-metadata-inspector-and-standardized-tagging-protocol)).

### 1.8 Data & Storage Architecture
Ars Arcanum operates with a 100% local, plain-text and open-standard storage model. There are no relational database daemons (e.g. Postgres/MySQL) or proprietary binary document formats.
- **Markdown (`.md`) Files**: Primary storage for world dossiers, scene prose, and chapter outlines.
- **YAML Manifests (`.yaml`)**: Flat key-value linkage files at universe (`universe.yaml`), world lore vault (`world.yaml`), and manuscript project (`manuscript.yaml`) roots.
- **novelWriter Manifest (`nwProject.nwx`)**: Conforms to `fileVersion 1.5` XML schema for structured drafting compatibility.
- **Git Object Database (`.git`)**: Local revision tracking across the 3-tier hierarchy.
- **Tarball Archives (`.tar.gz`)**: Point-in-time disaster recovery snapshots with SHA-256 manifests.

### 1.9 APIs, Plugins & Desktop Extensions
- **Vendored Obsidian Community Plugins**: All 10 community plugins are fully vendored with `manifest.json`, `main.js`, and `styles.css` under `templates/world-bible/.obsidian/plugins/` (Dataview, Metadata Menu, Calendarium, Storyline, Storyteller Suite, Longform, Novel Word Count, Obsidian Git, Templater, Obsidian Style Settings) with exact release digests recorded in `dependencies.lock`.
- **Browser Distraction Blocking**: Firefox WebExtension export schema (`configs/leechblock_arcanum_rules.json`).
- **Desktop Launchers**: Standard FreeDesktop `.desktop` files conforming to category `Office;WordProcessor;Publishing;`.

### 1.10 Background Jobs & Concurrency Architecture
- **Async GUI Workers**: Long-running subprocesses (exports, doctor scans, git commits) execute via Python daemon worker threads (`_start_worker`) communicating back to GTK main loop via `GLib.idle_add` ([ADR-020](#adr-020-external-audit-remediation--shared-discovery-library--fail-closed-hardening)).
- **Git Concurrency Retry**: CLI `scripts/save_snapshot.sh` implements an exponential backoff retry loop (5 attempts) to handle `.git/index.lock` contention caused by Obsidian Git auto-commits ([ADR-009](#adr-009-decoupled-standalone-backups-vs-local-git-snapshots-rel-03)).

### 1.11 CI/CD & Testing Infrastructure Overview
All repository changes are gated through continuous integration ([`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml)) executing on push and PR to `main`. The gate runs Ruff linting (0 errors), ShellCheck linting, Python syntax validation, the 7-stage `verify.sh` harness, and 282 unit tests in `tests/`.

---

## Part 2 — Context & Ecosystem

### 2.1 Local Checkout Identity

| Field | Value | Evidence |
| :--- | :--- | :--- |
| **Repository Remote** | `https://github.com/aryansinghnagar/Scriptorium.git` | `git remote -v` |
| **Active Branch** | `main` | `git branch --show-current` |
| **Head Commit** | `32d77f22bc81d14d401ac66442dd1560f0641029` | `git log -1` |
| **Software Version** | `1.6.0` (CLI Facade v1.6.0 / Core Platform Production-Ready Grade A Audit Verified) | [`scripts/arcanum#L15`](file:///scripts/arcanum#L15), [`docs/ROADMAP.md#L115-L120`](file:///docs/ROADMAP.md#L115-L120) |
| **License** | MIT License | [`LICENSE#L1-L25`](file:///LICENSE#L1-L25) |

### 2.2 Contributor & Governance Rules

- **Strict Non-Destructive Operations**: Scripts must never overwrite or delete user prose or lore without explicit confirmation or transactional staging ([`CONTRIBUTING.md#L8-L24`](file:///CONTRIBUTING.md#L8-L24)).
- **Safe Handling of Arbitrary Filenames**: All paths and filenames with spaces, Unicode characters, or special punctuation must be quoted and handled via NUL-delimited streams (`find -print0 | while IFS= read -r -d ''`) ([`CONTRIBUTING.md#L10-L16`](file:///CONTRIBUTING.md#L10-L16)).
- **4-Value Exit Code Contract**: Every script and CLI dispatcher adheres strictly to exit codes `0`, `1`, `2`, and `3` ([`docs/ARCHITECTURE.md#L300-L315`](file:///docs/ARCHITECTURE.md#L300-L315), [`CONTRIBUTING.md#L24-L37`](file:///CONTRIBUTING.md#L24-L37)).
- **Privilege Minimization**: Only `setup_arcanum.sh` may invoke `sudo` for explicitly declared system packages; writing scripts and daily authoring run unprivileged ([`SECURITY.md#L12-L22`](file:///SECURITY.md#L12-L22)).

### 2.3 Developer Gotchas & Operational Notes

- **Headless Test Execution**: Ars Arcanum test harnesses explicitly sandbox `$HOME` (`TEST_HOME=$(mktemp -d)`) and unset `$DISPLAY` / `$WAYLAND_DISPLAY` so that tests execute cleanly without spawning GUI windows ([`tests/test_audit_fixes.sh#L10-L30`](file:///tests/test_audit_fixes.sh#L10-L30)).
- **Git Concurrency in Obsidian**: Obsidian Git creates periodic background auto-commits. CLI scripts interacting with Git (`scripts/save_snapshot.sh`) implement a wait-and-retry loop to handle transient `.git/index.lock` contention ([`scripts/save_snapshot.sh#L45-L65`](file:///scripts/save_snapshot.sh#L45-L65)).
- **Trap-Based Staging Cleanup**: Scaffolding scripts stage files in `/tmp` and register traps (`trap cleanup EXIT INT TERM`) to guarantee that partial or failed operations never pollute user project directories ([`scripts/init_world.sh#L20-L40`](file:///scripts/init_world.sh#L20-L40)).

### 2.4 Ecosystem Relationships & External Boundaries
Ars Arcanum acts as an orchestration layer over standalone desktop tools. It interfaces with external applications via standard filesystem structures and CLI subprocesses without embedding third-party code directly.

---

## Part 3 — Architectural Blueprint

### 3.1 C4-Style System Architecture Diagrams

#### Level 1: System Context Diagram

```mermaid
C4Context
    title System Context: Ars Arcanum Authoring Platform

    Person(author, "Fiction Author / Worldbuilder", "Drafts novels, builds lore bibles, compiles ebooks and print PDFs.")

    System(arcanum, "Ars Arcanum Platform", "Local-first desktop and CLI ecosystem orchestrating authoring, lore, versioning, and publishing.")

    System_Ext(obsidian, "Obsidian Vault Engine", "Manages Markdown lore wikis, relationship graphs, and Dataview queries.")
    System_Ext(novelwriter, "novelWriter / FocusWriter", "Manages structured novel drafting trees and distraction-free canvases.")
    System_Ext(typst_pandoc, "Typst & Pandoc", "Typesets print-ready trade PDFs and compiles EPUB / DOCX formats.")
    System_Ext(git_vcs, "Local Git VCS", "Maintains multi-tier distributed revision history and snapshots.")
    System_Ext(dejadup, "Déjà Dup Backup", "Performs encrypted automated 3-2-1 backups to external media.")

    Rel(author, arcanum, "Controls workflows via GTK 3 Desktop App / CLI")
    Rel(arcanum, obsidian, "Scaffolds & launches Pure World Lore Vaults")
    Rel(arcanum, novelwriter, "Scaffolds & launches Prose Manuscript Projects")
    Rel(arcanum, typst_pandoc, "Compiles print PDFs, EPUBs, and DOCXs")
    Rel(arcanum, git_vcs, "Executes multi-tier snapshots and rollbacks")
    Rel(arcanum, dejadup, "Backs up ~/Universes and ~/Manuscripts")
```

#### Level 2: Container Diagram

```mermaid
C4Container
    title Container Diagram: Ars Arcanum Components

    Container(gtk_app, "Control Center GUI", "Python 3 / PyGObject (GTK 3)", "5-tab desktop dashboard with visual scene tag editor and live word count rollups.")
    Container(cli_facade, "Ars Arcanum CLI Facade", "POSIX Shell", "Unified command-line dispatcher (arcanum) for all operations.")
    Container(lib_worlds, "Discovery Engine (lib/worlds.sh)", "POSIX Shell", "Scans and resolves universes, world vaults, and manuscripts.")
    Container(scaffold_engine, "Scaffolding Engines", "Shell Scripts", "Transactional universe, world, manuscript, and volume initializers.")
    Container(pub_engine, "Publishing Engine", "Shell + Typst + Pandoc", "Compiles multi-volume manuscripts into PDF, EPUB, and submission DOCX.")
    Container(concordance_engine, "Concordance Engine", "Shell / Regex", "Generates Dramatis Personae and Glossary back-matter.")
    Container(diag_engine, "Doctor & Diagnostic Engines", "Shell Scripts", "Validates toolchains, multi-era timelines, and lore consistency.")
    Container(backup_engine, "Backup & Restore Engine", "Shell + Tar + SHA-256", "Creates verified disaster recovery archives and executes drills.")

    ContainerDb(fs_lore, "World Lore Vaults", "Local Filesystem", "~/Universes/<Universe>/<World>/ (Markdown + YAML + fileClasses)")
    ContainerDb(fs_ms, "Manuscript Projects", "Local Filesystem", "~/Manuscripts/<Manuscript>/ (Acts, Scenes, nwProject.nwx)")
    ContainerDb(fs_git, "Multi-Tier Git Repos", "Local .git objects", "Discrete repositories at Universe, World, and Manuscript levels")

    Rel(gtk_app, lib_worlds, "Queries projects")
    Rel(gtk_app, pub_engine, "Triggers export")
    Rel(gtk_app, diag_engine, "Runs health checks")
    Rel(cli_facade, lib_worlds, "Queries projects")
    Rel(cli_facade, scaffold_engine, "Dispatches creation")
    Rel(cli_facade, pub_engine, "Dispatches export")
    Rel(cli_facade, backup_engine, "Dispatches backups")
    Rel(scaffold_engine, fs_lore, "Scaffolds lore vaults")
    Rel(scaffold_engine, fs_ms, "Scaffolds manuscripts")
    Rel(pub_engine, fs_ms, "Reads scenes")
    Rel(concordance_engine, fs_lore, "Reads lore notes")
    Rel(concordance_engine, fs_ms, "Writes back-matter")
    Rel(backup_engine, fs_git, "Archives repos")
```

#### Level 3: Request & Lifecycle Diagram (Export & Publishing Pipeline)

```mermaid
sequenceDiagram
    autonumber
    actor Author
    participant GUI as Control Center (GTK 3)
    participant Engine as export_book.sh
    participant Concordance as generate_concordance.sh
    participant Pandoc as Pandoc Engine
    participant Typst as Typst Engine
    participant FS as Local Filesystem

    Author->>GUI: Click "1-Click Publish" (Selected Volume & Trim Size)
    GUI->>Engine: Invoke export_book.sh with options (-b Book-01 -s trade --format all)
    Engine->>Concordance: Generate updated Dramatis Personae & Glossary
    Concordance->>FS: Write 04_Back_Matter/*.md
    Engine->>FS: Aggregate Act I, Act II, Act III, and Back Matter Markdown
    Engine->>Pandoc: Convert concatenated Markdown to Typst AST
    Engine->>Typst: Compile Typst source + book_template.typ into PDF
    Typst-->>Engine: PDF Generated (<100ms)
    Engine->>Pandoc: Compile EPUB with cover art & smart typography
    Pandoc-->>Engine: EPUB Generated
    Engine->>Pandoc: Compile Submission DOCX
    Pandoc-->>Engine: DOCX Generated
    Engine->>FS: Move artifacts to ~/Manuscripts/<Manuscript>/Exports/
    Engine-->>GUI: Stream completion & artifact ledger (Exit 0)
    GUI-->>Author: Display PDF Preview & open folder launcher
```

### 3.3 Layering and Dependency Rules

1. **Presentation Layer (`scripts/arcanum_app.py`, `scripts/control_center.sh`)**:
   - May depend on: Discovery Library (`scripts/lib/worlds.sh`), Core Scripts (`scripts/*.sh`), Standard Python libraries, PyGObject.
   - May NOT depend on: Direct raw database drivers, hardcoded filesystem paths.
2. **CLI Facade (`scripts/arcanum`)**:
   - May depend on: Core Scripts (`scripts/*.sh`), Discovery Library (`scripts/lib/worlds.sh`).
   - May NOT depend on: GUI toolkits, interactive X11 displays.
3. **Discovery Engine (`scripts/lib/worlds.sh`)**:
   - May depend on: Standard POSIX utilities (`find`, `sort`, `sed`, `grep`).
   - May NOT depend on: Mutating project state, compilation tools.
4. **Core Workflow Engines (`scripts/*.sh`)**:
   - May depend on: Discovery Library (`scripts/lib/worlds.sh`), CLI binaries (`typst`, `pandoc`, `git`, `tar`).
   - May NOT depend on: GUI libraries, Python GUI code.
5. **Storage Layer (`~/Universes`, `~/Manuscripts`)**:
   - Passive plain-text Markdown, YAML, and XML files on disk.

### 3.4 Cross-Cutting Concerns Table

| Concern | Implementation & Strategy | Evidence (File & Line) |
| :--- | :--- | :--- |
| **Authentication & Privileges** | Unprivileged single-user execution; explicit sudo scoping in installer only | [`SECURITY.md#L12-L22`](file:///SECURITY.md#L12-L22), [`scripts/setup_arcanum.sh#L106-L209`](file:///scripts/setup_arcanum.sh#L106-L209) |
| **Configuration Management** | Flat YAML manifests (`universe.yaml`, `world.yaml`, `manuscript.yaml`) & JSON configs | [`docs/COMPATIBILITY.md#L54-L62`](file:///docs/COMPATIBILITY.md#L54-L62) |
| **Logging & Output** | Standardized stdout/stderr formatting with category markers (`[INFO]`, `[OK]`, `[WARN]`, `[ERROR]`) | [`scripts/export_book.sh#L20-L40`](file:///scripts/export_book.sh#L20-L40), [`scripts/verify.sh#L18-L35`](file:///scripts/verify.sh#L18-L35) |
| **Metrics & Analytics** | Real-time scene, chapter, and book wordcount rollups; status badge summaries | [`scripts/wordcount_report.sh#L1-L80`](file:///scripts/wordcount_report.sh#L1-L80), [`scripts/arcanum_app.py#L400-L550`](file:///scripts/arcanum_app.py#L400-L550) |
| **Secrets Management** | Zero cloud credentials or hardcoded keys; GPG package and SHA-256 binary validation | [`SECURITY.md#L3-L11`](file:///SECURITY.md#L3-L11), [`scripts/setup_arcanum.sh#L210-L270`](file:///scripts/setup_arcanum.sh#L210-L270) |
| **Error Handling & Traps** | 4-value exit code contract (`0`, `1`, `2`, `3`); temporary staging with trap cleanups | [`docs/ARCHITECTURE.md#L300-L315`](file:///docs/ARCHITECTURE.md#L300-L315), [`scripts/init_world.sh#L20-L40`](file:///scripts/init_world.sh#L20-L40) |
| **Feature Flags / Modes** | `--dry-run`, `--force`, `--paper-size`, `--format book|submission|all`, `--book <Volume>` | [`scripts/setup_arcanum.sh#L35-L60`](file:///scripts/setup_arcanum.sh#L35-L60), [`scripts/export_book.sh#L45-L95`](file:///scripts/export_book.sh#L45-L95) |

### 3.5 Governance & Enforcement Mechanisms
- **Automated Continuous Integration**: Every push/PR triggers [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) running ShellCheck (`-S warning`), `py_compile`, `verify.sh`, and `tests/*.sh`.
- **4-Value Exit-Code Contract**: Standardized exit codes (`0`, `1`, `2`, `3`) enforced across all CLI scripts and tested in `tests/test_audit_fixes.sh` Test 11.
- **Fail-Closed Verification**: Binary installation and test verification halt execution on unverified digests or schema mismatches.

### 3.6 "How to Add a Feature" Guide & Common Pitfalls

#### Step-by-Step Feature Implementation Workflow
1. **Create the Script**: Author `scripts/your_feature.sh` with `#!/usr/bin/env bash`, `set -euo pipefail`, and source `scripts/lib/worlds.sh`.
2. **Implement the 4-Value Exit Code**: Ensure `0` (success), `1` (runtime/diagnostic failure), `2` (usage error), `3` (nothing to act on).
3. **Register in CLI Facade**: Add subcommand routing in `scripts/arcanum`.
4. **Register in GUI**: If user-facing, add button/action in `scripts/arcanum_app.py` executed via `_start_worker`.
5. **Add Automated Tests**: Add test assertions in `tests/` and wire into `scripts/verify.sh` Stage 6.
6. **Update Docs**: Update `docs/AUTHOR_MANUAL.md`, `CHANGELOG.md`, and knowledge base.

#### Common Developer Pitfalls
- ❌ **Unquoted variable expansions**: Always write `"$VAR"` instead of `$VAR`.
- ❌ **Blocking the GTK UI thread**: Never execute CLI commands directly in UI callbacks; use `_start_worker`.
- ❌ **Hardcoded user paths**: Always use `$HOME` and discovery helpers; never hardcode `/home/username`.
- ❌ **Swallowing exit codes**: Avoid `cmd || true` in verification harnesses; fail closed.

---

## Part 4 — Subsystem Deep-Dives

### 4.1 Subsystem 1: GTK 3 Desktop Control Center & Visual Scene Metadata Inspector

```mermaid
flowchart TD
    A[Author opens Tab 2: Manuscripts & Drafting] --> B[GTK TreeView lists Acts & Scene Files]
    B --> C{Author selects Scene Note}
    C --> D[Parser reads Scene Header & YAML Frontmatter]
    D --> E[Display Form: @pov, @char, @location, @thread, @time, @status]
    E --> F[Author edits tags in GUI & clicks 'Save Metadata']
    F --> G[Atomic Rewrite Engine]
    G --> H[Preserve top YAML frontmatter block]
    G --> I[Format standardized @tag lines]
    G --> J[Write updated scene file atomically]
    J --> K[Trigger Live Word Count Rollup]
```

- **Internal Structure**: Implemented in Python 3 using PyGObject GTK 3 (`scripts/arcanum_app.py#L40-L1575`). Organized into 5 tab workflows: Cosmos, Drafting, Publishing, Safety, and Diagnostics.
- **Worker Threading**: All long-running tasks (compilation, diagnostics, git snapshotting) execute on daemon background threads (`_start_worker`) communicating back to the GTK main loop via `GLib.idle_add` to ensure zero UI freezes ([ADR-017](#adr-017-unified-python-gtk-desktop-control-center--author-onboarding-architecture), [ADR-020](#adr-020-external-audit-remediation--shared-discovery-library--fail-closed-hardening)).
- **Visual Scene Metadata Inspector**: Allows non-technical authors to inspect and rewrite scene metadata annotations (`@pov:`, `@char:`, `@location:`, `@thread:`, `@time:`, `@status:`) directly in the GUI while preserving existing YAML frontmatter and prose integrity ([ADR-022](#adr-022-separated-lore--manuscript-architecture-visual-scene-metadata-inspector-and-standardized-tagging-protocol), [ADR-023](#adr-023-forensic-audit-hardening--fail-closed-security-depth-3-universe-discovery-iso-8601-chronology-and-intra-manuscript-link-resolution)).

### 4.2 Subsystem 2: Narrative Concordance & Multi-Era Chronological Validation Engine

```mermaid
flowchart LR
    A[World Bible Lore Vault] --> B[world_doctor.sh Pass 1: YAML Schemas]
    A --> C[world_doctor.sh Pass 2: Multi-Era Timeline]
    C --> D[parse_timeline_date: BC/BCE, CE/AD, 1E..5E, ISO 8601]
    D --> E{Chronological Paradox?}
    E -- Yes --> F[Report WLD-104 Paradox Finding]
    E -- No --> G[Pass Valid Timeline]
    A --> H[generate_concordance.sh]
    H --> I[Parse Characters & Locations]
    I --> J[01_Dramatis_Personae.md]
    I --> K[02_Glossary_and_Concordance.md]
```

- **Narrative Concordance Engine (`scripts/generate_concordance.sh`)**: Automatically scans World Bible notes (`Characters/`, `Locations/`, `Factions/`, `Magic-Technology/`, `Cosmology/`) to construct publication back-matter formatted in clean Markdown for direct inclusion into book exports ([ADR-019](#adr-019-automated-narrative-concordance--multi-era-chronological-parsing-engine)).
- **Multi-Era Chronological Parser (`scripts/world_doctor.sh`)**: Evaluates fantasy era notation (e.g. `1E 450`, `Age of Fire 120`), BC/BCE astronomical years, and ISO 8601 calendar dates (`YYYY-MM-DD`) to detect timeline paradoxes (e.g. death before birth, event duration inversion) without integer parsing exceptions ([ADR-019](#adr-019-automated-narrative-concordance--multi-era-chronological-parsing-engine), [ADR-023](#adr-023-forensic-audit-hardening--fail-closed-security-depth-3-universe-discovery-iso-8601-chronology-and-intra-manuscript-link-resolution)).
- **Manuscript Lore Drift Detection (`WLD-108`)**: Cross-validates manuscript draft scene tags and wikilinks against indexed lore files while cleanly resolving intra-manuscript outline references without false positives ([ADR-022](#adr-022-separated-lore--manuscript-architecture-visual-scene-metadata-inspector-and-standardized-tagging-protocol), [ADR-023](#adr-023-forensic-audit-hardening--fail-closed-security-depth-3-universe-discovery-iso-8601-chronology-and-intra-manuscript-link-resolution)).

### 4.3 Subsystem 3: Multi-Tier Git Architecture & Disaster Recovery Pipeline

```mermaid
graph TD
    subgraph Universe Tier
        U[~/Universes/Eldoria-Cosmos/ - universe.yaml + Git Repo]
    end
    subgraph World Lore Tier
        W[~/Universes/Eldoria-Cosmos/Eldoria-World/ - Pure Lore Vault + Git Repo]
    end
    subgraph Manuscript Tier
        M[~/Manuscripts/Chronicles-of-Eldoria/ - manuscript.yaml + Git Repo]
        B1[Book-01/ - Discrete Volume Git Repo]
        B2[Book-02/ - Discrete Volume Git Repo]
    end
    U --> W
    M -. links .-> U
    M -. links .-> W
    M --> B1
    M --> B2
```

- **3-Tier Version Control Hierarchy**:
  1. *Universe Tier*: Tracks high-level cosmos registry and global continuity (`init_universe.sh`).
  2. *World Lore Tier*: Tracks lore dossiers, maps, and entity notes with 10-minute auto-commits via Obsidian Git (`init_world.sh`).
  3. *Manuscript Tier*: Tracks volume acts, chapters, and scene prose with milestone commit tags (`init_manuscript.sh`, `add_book.sh`, `save_snapshot.sh`).
- **Disaster Recovery Pipeline (`scripts/backup_world.sh` / `scripts/restore_world.sh`)**: Generates timestamped `.tar.gz` archive snapshots with SHA-256 integrity manifests, path-traversal prevention, and verified monthly restore drill support ([ADR-009](#adr-009-decoupled-standalone-backups-vs-local-git-snapshots-rel-03), [ADR-020](#adr-020-external-audit-remediation--shared-discovery-library--fail-closed-hardening)).

---

## Part 5 — Complete Architectural Decision Records (ADR-001 through ADR-023)

### ADR-001: Selection of Linux Mint XFCE as Primary Distribution
- **Context**: The author needs a stable, lightweight, zero-maintenance operating system that runs smoothly on reference Intel Core i5 laptops, dual-boots easily with Windows, and requires no terminal interaction for daily tasks.
- **Decision**: Adopt Linux Mint XFCE edition as Tier 1 reference platform.
- **Alternatives Considered**: Arch/Custom Minimal Distro (high maintenance), Ubuntu GNOME (resource heavy, snap dependency), Debian 13 XFCE (documented as secondary Tier 1 option).
- **Consequences**: Out-of-the-box GUI software manager, pre-installed LibreOffice, native dual-boot installer, low RAM usage (~700MB idle).

### ADR-002: Plain Markdown Storage vs Proprietary Database
- **Context**: Authors frequently lose access to work when proprietary software changes subscription models or becomes abandoned.
- **Decision**: Store all lore, characters, outlines, and manuscript prose in plain `.md` files in human-readable folders.
- **Alternatives Considered**: Scrivener (proprietary XML bundle), Notion / Google Docs (cloud-locked, privacy risks).
- **Consequences**: Total data sovereignty. Work can be read on any operating system 50 years from now.

### ADR-003: Typst + Pandoc for Typesetting vs LaTeX / InDesign / Vellum
- **Context**: Fiction writers need professional book-quality PDFs with proper trim size, margins, running headers, and clean typography without complex LaTeX syntax or Mac-exclusive tools.
- **Decision**: Use Typst as the primary PDF typesetting engine, with Pandoc as the conversion bridge from Markdown.
- **Alternatives Considered**: LaTeX (slow compile times, fragile packages), LibreOffice PDF (lacks micro-typography), Vellum (macOS only, closed source).
- **Consequences**: Lightning-fast builds (<100ms), modern declarative syntax, beautiful book aesthetics, 100% open-source.

### ADR-004: LeechBlock NG & OS Do-Not-Disturb vs Total Internet Disconnection
- **Context**: Writers need online research and dictionary lookups, but are susceptible to social media rabbit holes.
- **Decision**: Install LeechBlock NG on Firefox with scheduled blocks during writing hours, paired with XFCE Do-Not-Disturb mode.
- **Alternatives Considered**: Airplane mode (cuts off research), Hosts file DNS blocks (inflexible).
- **Consequences**: Frictionless focus during writing blocks without crippling essential research capabilities.

### ADR-005: Valid novelWriter Project Scaffolding
- **Context**: Placeholders that fail XML parsers create friction for authors opening novelWriter directly.
- **Decision**: Ship a valid XML format conforming to novelWriter `fileVersion 1.5` schema (`<novelWriterXML>`) in `templates/manuscript/nwProject.nwx`.
- **Consequences**: Valid XML schema validation in CI while maintaining plain Markdown starters as the source of truth for compilation.

### ADR-006: Tolerant Setup Provisioning
- **Context**: Font package names drift across Mint/Debian releases, Flatpak scope differs per machine, and ARM laptops need different Typst binaries.
- **Decision**: Install core packages strictly, fonts tolerantly (Libertinus fallback + warning), detect `x86_64`/`aarch64` for Typst, prefer Flatpak `--system` with `--user` fallback.
- **Consequences**: Setup degrades gracefully instead of failing; font gaps are reported, not fatal.

### ADR-007: Pandoc-First Export with Safe Filenames
- **Context**: Hand-rolled Markdown→Typst regex mangles body text, raw titles break Typst string literals, and failed Typst compiles leaked temp dirs.
- **Decision**: Prefer `pandoc -t typst` with a multi-level `sed` fallback, escape titles for Typst, derive collision-safe filename stems, and `trap`-clean temp dirs.
- **Consequences**: Real manuscripts convert faithfully; re-exports never overwrite silently.

### ADR-008: Transactional World & Manuscript Scaffolding via Temporary Staging (REL-01)
- **Context**: Direct directory creation leaves orphaned or corrupt state if an intermediate failure occurs.
- **Decision**: Stage world/manuscript creation in a temporary directory (`mktemp -d`), run structural validation checks, initialize Git, and atomically move (`mv`) the finished tree into destination.
- **Consequences**: Zero risk of half-scaffolded or corrupt project folders.

### ADR-009: Decoupled Standalone Backups vs Local Git Snapshots (REL-03)
- **Context**: Authors conflate local Git commits with external disaster recovery backups.
- **Decision**: Decouple version snapshots (Git) from standalone archive backups (`backup_world.sh` / `restore_world.sh`) with SHA-256 manifests.
- **Consequences**: Complete 3-2-1 backup readiness and verified disaster recovery capability.

### ADR-010: OS Gating and Dry-Run Installation Safety (SEC-01, SEC-02)
- **Context**: Automated installers modifying root/user directories without simulation risk breaking unverified distributions.
- **Decision**: Implement `/etc/os-release` gating (Linux Mint 21/22, Debian 12/13), require `--force` on other systems, and provide `--dry-run` simulation mode.
- **Consequences**: Safe preview before mutation, protection against untested distro breakage, and clean uninstallation.

### ADR-011: Independent Export Error Trapping & Artifact Validation (AUD-02)
- **Context**: Pandoc compilation failures previously triggered `set -e` aborts that suppressed summary logs.
- **Decision**: Implement independent error trapping for Pandoc mirroring Typst, set `EXIT_STATUS=1` on non-fatal failures, and validate non-zero artifact byte sizes.
- **Consequences**: Robust multi-format compilation where partial successes are preserved and surfaced.

### ADR-012: Unified CLI Facade & Desktop Control Center (M4)
- **Context**: Discrete shell scripts require memorizing individual script names.
- **Decision**: Provide `scripts/arcanum` as a single unified CLI dispatcher and `scripts/control_center.sh` / `arcanum-control-center.desktop` as desktop dashboards.
- **Consequences**: Seamless ergonomics for both terminal power users and GUI-first writers.

### ADR-013: Universe-World-Manuscript Multi-Tier Git Architecture
- **Context**: Complex narrative projects span interconnected worlds, while individual books require discrete revision histories.
- **Decision**: Implement a 3-tier version control hierarchy: Universe (`~/Universes/<Universe>/`), World Lore Vault (`~/Universes/<Universe>/<World>/`), and Manuscript (`~/Manuscripts/<Manuscript>/`).
- **Consequences**: Complete narrative isolation, modular scaling across multi-volume series, and clean git status.

### ADR-014: Out-of-the-Box Obsidian Worldbuilding & Drafting Plugin Suite
- **Context**: Setting up an Obsidian vault from scratch requires tedious manual installation and schema modeling.
- **Decision**: Pre-configure an opinionated plugin suite in `templates/world-bible/.obsidian/` featuring Longform, Dataview, Metadata Menu (9 `fileClasses`), Calendarium, Storyteller Suite, Storyline, Novel Word Count, and Obsidian Git.
- **Consequences**: Zero-setup vault initialization for writers, guaranteed schema consistency, and automated 10-minute auto-commits.

### ADR-015: Multi-Volume Manuscript Compilation & Volume Isolation
- **Context**: Authors writing multi-book series need to compile discrete individual volumes (e.g. `Book-01`, `Book-02`) independently.
- **Decision**: Implement volume discovery and selection in `export_book.sh` (`-b, --book <Volume>`, GUI interactive picker, and Omnibus option).
- **Consequences**: Granular publication workflows, seamless series management, and prevention of multi-volume manuscript collisions.

### ADR-016: Speculative Fiction Taxonomic Expansion (Bestiary, Relics, Cosmology)
- **Context**: Worldbuilding across epic fantasy and sci-fi requires dedicated ontologies beyond characters, locations, and factions.
- **Decision**: Expand canonical World Bible taxonomy to include `Bestiary/` (`Creature.md`), `Artifacts/` (`Artifact.md`), and `Cosmology/` (`Cosmology.md`).
- **Consequences**: Rich ontological coverage for speculative fiction with dynamic Dataview dashboards.

### ADR-017: Unified Python GTK Desktop Control Center & Author Onboarding Architecture
- **Context**: Terminal commands intimidate non-technical authors; basic Zenity dialogs lack rich state and live analytics.
- **Decision**: Implement a native desktop GUI dashboard in Python 3 + PyGObject / GTK 3 (`scripts/arcanum_app.py`) organized across a 5-tab author workflow with First-Flight onboarding wizard.
- **Consequences**: Zero terminal barrier to entry for creative authors, rich visual feedback, and safe async background processing.

### ADR-018: Speculative Ontology Harmonization, Multi-Volume Scaffolding & Publishing Polish
- **Context**: Ontological divergence between frontmatter templates and `fileClasses` schemas caused inconsistent Dataview reporting.
- **Decision**: Harmonize all frontmatter templates with strict `fileClasses`, add `MagicSystem.md` and `Language.md`, introduce `scripts/add_book.sh`, wire `-s, --paper-size`, and auto-detect EPUB covers (`03-Art/cover.png`).
- **Consequences**: Complete ontological consistency across the 9 World Bible domains, frictionless multi-volume series authoring, publication-grade cover and trim sizing.

### ADR-019: Automated Narrative Concordance & Multi-Era Chronological Parsing Engine
- **Context**: Authors manually assemble Dramatis Personae rosters and glossaries, while timeline consistency checking previously failed on non-integer fantasy era notation.
- **Decision**: Implement `scripts/generate_concordance.sh` for automated back-matter generation, and implement a regex-based multi-era chronological parser in `world_doctor.sh` supporting BC/BCE, CE/AD, numbered eras (1E..5E), and named eras (`Age of Fire`, `IE`).
- **Consequences**: Zero manual toil generating book back-matter, automated synchronization between world lore and published glossaries, and robust chronological diagnostics.

### ADR-020: External Audit Remediation — Shared Discovery Library & Fail-Closed Hardening
- **Context**: An external audit identified functional bugs (invalid Calibre Flathub ID), injection/fail-open weaknesses in diagnostics, developer identity leakage, and duplicated discovery code.
- **Decision**: Extract `scripts/lib/worlds.sh` as single source of truth for discovery, make `verify.sh` fail closed, harden `restore_world.sh` against directory traversal, correct Calibre Flathub ID, move GUI background tasks to worker threads, and exclude `04-Publishing/` from snapshot history.
- **Consequences**: Centralized discovery logic, hardened security posture, reliable verification harness, and responsive GUI.

### ADR-021: Re-Audit Follow-Ups, Root Decluttering & Authorship Reset
- **Context**: An independent re-audit verified all 22 original findings closed (Grade A) and registered 5 new observations regarding exit-code documentation, legacy deprecation nudges, and root hygiene.
- **Decision**: Document standardized 4-value exit-code contract, extract `warn_if_legacy_root`, centralize daemon thread spawning, remove dead fallback branches, and declutter root repository.
- **Consequences**: Contract matches code, consistent user experience, clean thread management, and uncluttered repository root.

### ADR-022: Separated Lore & Manuscript Architecture, Visual Scene Metadata Inspector, and Standardized Tagging Protocol
- **Context**: Nesting manuscripts inside world bible folders created friction for authors using novelWriter or Obsidian independently. Tag naming was fragmented (`@focus:` vs `@location:`), and standard submission format (`.docx`) was missing.
- **Decision**:
  - Separate Pure World Lore Vaults (`~/Universes/<Universe>/<World>`) as direct Obsidian vaults from Standalone Prose Manuscripts (`~/Manuscripts/<Manuscript>`) with `manuscript.yaml` linking.
  - Standardize `@location:` across all templates, novelWriter scene headers, and diagnostics.
  - Implement Visual Scene Metadata Inspector in GTK Control Center Tab 2 for in-place tag editing.
  - Add Standard Manuscript Submission Format (`.docx`) export via Pandoc and `WLD-108` lore cross-reference diagnostics.
- **Consequences**: Clean separation of worldbuilding lore and manuscript prose, effortless tag consistency, intuitive in-GUI scene metadata management, and industry-standard submission capability.

### ADR-023: Forensic Audit Hardening — Fail-Closed Security, Depth-3 Universe Discovery, ISO 8601 Chronology, and Intra-Manuscript Link Resolution
- **Context**: Security and operational auditing identified key edge-case gaps in Typst SHA-256 verification, depth-3 universe discovery, ISO 8601 timeline parsing, intra-manuscript wikilinks, and GUI snapshot history reloads.
- **Decision**:
  - Convert `setup_arcanum.sh` to fail closed (`TYPST_OK=0`) when SHA-256 digests cannot be verified.
  - Upgrade `scripts/lib/worlds.sh` to index direct depth-2, legacy depth-3, and legacy root worlds without polluting results with literal `"Worlds"` directories, and fix `universe_label` for depth-3 worlds.
  - Implement ISO 8601 calendar date parsing (`YYYY-MM-DD`, `YYYY-MM`, `YYYY/MM/DD`) in `world_doctor.sh` (`WLD-104`).
  - Index all manuscript markdown files and outlines into `ms_index` in Pass 3 of `world_doctor.sh` to resolve intra-manuscript references without false-positive `WLD-108` findings.
  - Reload snapshot history after Quick Snapshots and preserve YAML frontmatter during scene tag updates in `arcanum_app.py`.
### ADR-024: Discrete Multi-Draft Architecture & Accessible Visual Redline Comparator
- **Context**: Authors require discrete draft version tracking (`Draft-01`, `Draft-02`, `Draft-03`) across novel revisions, clean draft forking without losing historical scenes, and word-processor-style visual redline comparison showing prose additions and deletions across drafts.
- **Decision**:
  - Implement `scripts/init_draft.sh` for multi-draft version scaffolding and automated Git milestone tagging.
  - Implement `scripts/lib/manuscript_diff.py` and `scripts/compare_drafts.sh` using Python's `difflib` with word-level tokenization. Generate standalone, accessible HTML redline reports (with soft pastel colors `#f8d7da` / `#d4edda` meeting WCAG contrast ratios, dark/light theme toggle, and collapsible chapter sidebars), terminal changelog mode, JSON metrics, and a LibreOffice Writer bridge.
  - Integrate Draft Revisions and Redline Comparator directly into GTK 3 Desktop UI Tab 2.
  - Update `scripts/export_book.sh` and `scripts/wordcount_report.sh` to seamlessly resolve active draft hierarchies.
- **Consequences**: 100% offline local diffing, zero proprietary lock-in, accessible WCAG-compliant redline visualization, and intuitive multi-draft lifecycle management.

### ADR-025: Dual-Target Secure External & USB Backup Replication
- **Context**: Relying solely on internal disk backups poses severe disaster recovery risks; authors need automated dual-target replication to external secure drives (USB disks, secondary drives, network mounts) with persistent configuration.
- **Decision**:
  - Implement `scripts/lib/config.py` for managing author preferences in `~/.config/ars-arcanum/config.json`.
  - Enhance `scripts/backup_world.sh` with dual-target replication: whenever a backup archive is created and SHA-256 verified in the primary backup directory, it is automatically replicated to the configured external destination if available (or warned gracefully if unmounted).
  - Provide CLI commands (`arcanum backup-dest <get|set|clear>`) and GTK UI configuration picker.
- **Consequences**: Automated 3-2-1 backup compliance, zero data loss risk on primary drive failure, and seamless plug-and-play USB external drive synchronization.

### ADR-026: Dual-Synchronized DOCX Architecture, Bidirectional Word Processor Sync Engine & Configurable Manuscript Formatting Presets
- **Context**: While plain Markdown is ideal for local version control, authors frequently collaborate with editors, beta readers, and publishers using Microsoft Word, Google Docs, and LibreOffice Writer, or prefer drafting directly in standard word processors.
- **Decision**:
  - Implement a hybrid, dual-synchronized storage model maintaining both consolidated full-draft `.docx` (`Draft-01_Manuscript.docx`) and individual chapter `.docx` files (`01_Chapter.docx`) alongside Markdown.
  - Build a 100% offline, pure Python OpenXML generator and synchronization engine (`scripts/lib/docx_sync.py`) that generates standard Word documents compliant with Microsoft Word (365 / latest), Google Docs, and LibreOffice Writer.
  - Implement configurable submission formatting presets in `scripts/lib/config.py` (`Standard Submission / Shunn`, `Modern Manuscript`, `Classic Trade`, and `Custom`) adjustable via CLI (`arcanum config docx-preset`) and the GTK 3 Control Center.
  - Strip visible scene metadata tags (`@pov:`, `@location:`, etc.) from `.docx` body text to keep prose distraction-free while preserving tags during bidirectional synchronization back to Markdown.
- **Consequences**: Seamless interoperability with standard word processors, zero proprietary lock-in, effortless collaboration with editors, and customizable submission formatting.

### ADR-027: Speculative Fiction Authorial Workflow Suites (Waves 1–6)
- **Context**: Speculative fiction novelists (hard SF, epic fantasy, space opera) require rigorous domain calculations (relativistic kinematics, orbital mechanics, conlang phonotactics, dynastic inheritance DAGs, hard magic constraints, expedition logistics, custom multi-moon planetary calendars) without relying on cloud APIs, telemetry, or external pip dependencies.
- **Decision**:
  - Implement 6 modular pure Python standard library engines in `scripts/lib/`:
    - `astrophysics.py`: Relativistic Brachistochrone 1g constant-acceleration trajectory calculator ($\tau$ vs $t$, $v/c$, $\gamma$, fuel mass ratios), Hohmann orbital transfers, comms latencies, habitability & gravity, and visual HTML flight profiles.
    - `magic_system.py`: Hard magic rules, character affinity tier limits (`MAG-101`), catalyst requirements (`MAG-102`), hard limitations enforcement (`MAG-103`), and fatigue tracking (`MAG-104`).
    - `genealogy.py`: Family tree Directed Acyclic Graph (DAG) parser, chronological/biological paradoxes (`GEN-101`), succession claim conflicts (`GEN-102`), Mermaid.js flowchart generator, and interactive HTML exporter.
    - `conlang.py`: Syllable template phonotactic word/name generator, cluster filtering, historical sound law mutation engine (`p > f / V_V`, `k > ch / _[e,i]`), and lexicon parser/exporter (Markdown, CSV, JSON).
    - `pacing.py`: Prose mode classification (Dialogue, Action, Exposition), sentence length variance, POV screen-time balance with starvation alerts, tension arc modeling (0–100), and embedded SVG chart generator.
    - `journey.py` & `calendar.py`: Overland/naval journey modeler (14 terrain frictions, 8 travel modes, ration/water burn rates, daily itineraries) and custom planetary calendars (arbitrary year lengths, custom months/weekdays, multi-moon synodic phase cycles, syzygies, and eclipses).
  - Provide unified CLI routing via `scripts/arcanum` (`calc`, `magic-check`, `magic-report`, `magic`, `genealogy`, `lineage`, `conlang`, `pace`, `tension`, `journey`, `calendar`).
  - Integrate all 6 speculative tool buttons and dialogs into the GTK 3 Control Center GUI (`scripts/lib/ui_gtk3.py`).
  - Enrich world-bible templates and schemas (`fileClasses/MagicSystem.md`, `fileClasses/Language.md`, `fileClasses/Cosmology.md`, `fileClasses/Character.md`).
- **Consequences**: 100% offline, privacy-first speculative calculation and consistency checking with zero external pip dependencies.

### ADR-028: Speculative Fiction Authorial Workflow Suites (Waves 7–12 / Phase 2)
- **Context**: In addition to astrophysics, conlangs, and magic systems, deep worldbuilding and speculative plotting require geopolitical relationship paradox audits, campaign supply logistics, economic purchasing power parity, tech-era anachronism detection, causal loop DAG analysis, planetary climate/rain shadow simulation, trophic biomass webs, Earth-eponym de-immersion, 6D sensory grounding, and prophecy lifecycle resolution.
- **Decision**:
  - Implement 6 modular pure Python standard library engines in `scripts/lib/`:
    - `factions.py`: Geopolitical alliance and vassalage graph auditor (`FAC-101` to `FAC-104`), Lanchester power-law battle casualty simulator (square/linear laws, fortification multipliers), campaign grain/water supply wagon radius calculator, and Mermaid/HTML chord visualizers.
    - `economy.py`: Multi-currency commodity basket Purchasing Power Parity (PPP) matrix, manuscript price outlier scanner (`ECO-101`/`ECO-102`), historical tech era anachronism detector (`ECO-201`), and trade route freight margin calculator.
    - `causality.py`: Event causal graph extractor, cycle/paradox detection for grandfather (`CAU-101`) and bootstrap (`CAU-102`) paradoxes, Novikov consistency verification, multiverse branch coordinate scaffolding, and Mermaid DAG exporter.
    - `climate.py` & `ecology.py`: Stellar insolation, equilibrium surface temperature, atmospheric circulation cells, adiabatic orographic rain shadow modeler, Bestiary trophic level profiler, and Lindeman 10% energy pyramid validator (`ECO-301` to `ECO-304`).
    - `idioms.py` & `senses.py`: Earth-eponym scanner (`IDM-101` to `IDM-103`), 6-dimensional sensory palette analyzer (visual, auditory, olfactory, gustatory, tactile/thermal, kinesthetic/vestibular), White Room syndrome (`SNS-101`), and sensory monotony alerts (`SNS-102`).
    - `cipher.py` & `prophecy.py`: Caesar, Atbash, Vigenère, Rail Fence, and Columnar ciphers, phonetic Elder Futhark / Anglo-Saxon Futhorc rune translation with vector SVG cards, and prophecy clause resolution tracking (`PRP-101` to `PRP-103`).
  - Route all engines through `scripts/arcanum` (`faction`, `economy`, `causality`, `ecology`, `climate`, `idioms`, `senses`, `cipher`, `prophecy`, `calc battle`, `calc logistics`, `calc climate`, `audit idioms`, `audit senses`, `audit tech`).
  - Add world-bible templates and Metadata Menu schemas (`Economies/Economy-Template.md`, `Cosmology/Prophecy-Template.md`, `fileClasses/Economy.md`, `fileClasses/Prophecy.md`, upgraded `fileClasses/Faction.md` and `fileClasses/Creature.md`).
- **Consequences**: Complete 12-suite speculative fiction toolchain operating 100% offline with zero external pip dependencies.

### ADR-029: Editorial Craft, Dialogue Attribution & Proximity Echo Linters
- **Context**: Authors require deep prose analysis to identify dialogue attribution mechanics (said-bookisms, floating dialogue, excessive adverbs), lexical voice variations per character, and word echo / proximity repetitions before sending manuscripts to human editors.
- **Decision**:
  - Implement `scripts/lib/stylistics.py` with dialogue AST tokenizer, said-bookism detector (`DIA-101`), floating dialogue linter (`DIA-102`), adverb overload monitor (`DIA-103`), and sliding-window word echo scanner (`ECH-101`).
  - Implement `scripts/lib/voice.py` for character voice lexical profiling: extracts dialogue per `@char:` tag, computes Flesch-Kincaid / Coleman-Liau reading grade levels, sentence complexity, and voice homogeneity alerts (`VOI-101`/`VOI-102`).
  - Implement `scripts/lib/typography_cleaner.py` for smart punctuation normalization (curly quotes, en/em-dashes, ellipses, non-breaking spaces).
  - Expose CLI subcommands: `arcanum audit dialogue`, `arcanum audit echoes`, `arcanum audit voice`, `arcanum polish typography`.
- **Consequences**: 100% offline stylistics diagnostics without external NLP dependencies or cloud telemetry.

### ADR-030: Multi-Track Plot Matrix, Story Structure Paradigms & Scene Mechanics (MRU)
- **Context**: Authors need visual plot tracking across concurrent subplots, alignment against standard storytelling paradigms, and scene-level Motivation-Reaction Unit (MRU) validation.
- **Decision**:
  - Implement `scripts/lib/plot_matrix.py` generating interactive 2D timeline grids mapping `@thread:` subplots across chapters with color-coded status pills and standalone HTML export.
  - Implement `scripts/lib/structure.py` validating manuscript pacing against 6 narrative templates (Save the Cat, Hero's Journey, 7-Point Structure, Story Circle, Kishōtenketsu, 3-Act 9-Block) with interval-containment midpoint matching.
  - Implement `scripts/lib/scene_mechanics.py` for Dwight Swain / Jack Bickham Goal-Conflict-Disaster validation.
  - Implement `scripts/lib/ambient.py` procedural audio synthesizer with WebAudio HTML5 and offline WAV generation.
- **Consequences**: Rich plot visualization and structural pacing enforcement running entirely locally.

### ADR-031: Publication Pre-Flight Compliance Gate & Vector Barcode Generation
- **Context**: Indie authors preparing for print and ebook publication require automated pre-flight checks (trim sizes, margins, straight quotes in prose, cover art) and standard EAN-13 barcodes with price extensions.
- **Decision**:
  - Implement `scripts/lib/preflight.py` checking PDF/EPUB trim size, gutter ratios, straight quote presence outside codeblocks, and metadata compliance.
  - Implement `scripts/lib/barcode.py` generating pure vector SVG and high-resolution PNG EAN-13 barcodes with dynamic ISBN prefixes and 5-digit price extensions.
  - Implement `scripts/lib/frontmatter_builder.py` and `scripts/init_query.py` for automated copyright pages, promotional catalogs, and publishing query submission packages.
- **Consequences**: Publication-ready self-publishing compliance without proprietary desktop typesetting suites.

### ADR-032: Offline Interactive Cartography & Static Lore Codex Wiki Exporter
- **Context**: Worldbuilders need offline interactive map visualization linked to journey calculations, and the ability to export the entire Obsidian World Lore Vault into a reader-facing codex.
- **Decision**:
  - Implement `scripts/lib/cartography.py` providing self-contained offline Leaflet/SVG interactive map viewer with pin layers (cities, borders, waypoints), distance measurements, and direct piping into `journey.py`.
  - Implement `scripts/lib/codex_export.py` compiling Markdown vaults into searchable, responsive offline HTML static wikis with spoiler filters.
- **Consequences**: Sovereign cartography and reader codex distribution without cloud hosting requirements.

### ADR-033: Cross-Book Series Continuity & Tactical Battle Simulator
- **Context**: Multi-volume series require continuity validation for character traits, item ownership, and mortality across books, alongside tactical skirmish calculations.
- **Decision**:
  - Implement `scripts/lib/series_continuity.py` tracking character trait consistency, item lineages, and mortality invariants across `Book-01`, `Book-02`, etc.
  - Implement `scripts/lib/tactical_sim.py` simulating multi-faction battles using Lanchester combat laws, terrain modifiers, and arcane fatigue.
- **Consequences**: Automated series-level canon enforcement and combat simulation.

### ADR-034: Multi-Platform Distribution Packager & Portfolio Executive Dashboard
- **Context**: Authors managing multiple manuscripts and universes need platform-specific distribution bundles (Amazon KDP, IngramSpark, Apple Books, Kobo) with spine calculations and cross-project portfolio tracking.
- **Decision**:
  - Implement `scripts/package_distribution.py` generating distribution packages with exact spine width formulas based on page count and paper stock.
  - Implement `scripts/lib/portfolio.py` scanning all manuscripts and universes to calculate aggregate wordcounts, velocity, and publication readiness.
- **Consequences**: Streamlined indie author operations and multi-project visibility.

### ADR-035: Sovereign Auditory Proofreading with Offline Neural TTS
- **Context**: Authors catch typos, rhythm issues, and awkward syntax much more effectively by listening to their prose read aloud.
- **Decision**:
  - Implement `scripts/lib/tts_reader.py` bridging local neural TTS engines (Piper TTS / espeak-ng) via unprivileged subprocess pipes.
  - Provide paragraph tracking, speed modulation (`0.75x` to `2.0x`), and offline WAV compilation via `arcanum read [ms] [chapter]`.
- **Consequences**: Zero-cloud auditory proofreading preserving complete author privacy.

### ADR-036: Complete Vendoring of Obsidian Community Plugins & Lockfile Digest Verification
- **Context**: Relying on post-install download scripts for Obsidian community plugins causes offline install failures and non-deterministic environments for authors.
- **Decision**:
  - Vendor all 10 essential Obsidian community plugins (`dataview`, `templater-obsidian`, `longform`, `metadata-menu`, `calendarium`, `storyline`, `storyteller-suite`, `novel-word-count`, `obsidian-git`, `obsidian-style-settings`) with complete `manifest.json`, `main.js`, and `styles.css` directly in `templates/world-bible/.obsidian/plugins/<id>/`.
  - Record exact upstream release tags and SHA-256 digests in `dependencies.lock` under `[obsidian.plugins]`.
  - Add automated asset existence and size assertions to `scripts/verify.sh` Stage 5.
- **Consequences**: 100% offline out-of-the-box Obsidian world bible experience with cryptographically verified plugin assets.

### ADR-037: Pure Python OpenXML Security Hardening & XXE Defenses
- **Context**: Word documents (`.docx`) from external collaborators (editors, beta readers) are untrusted zip/XML inputs that could introduce XML External Entity (XXE), billion laughs entity expansion, or zip bomb attacks.
- **Decision**:
  - Enforce a 20 MB file size cap and a 50 MB uncompressed payload ceiling on all `.docx` import streams in `scripts/lib/docx_sync.py`.
  - Proactively scan XML byte streams before parsing, rejecting any content containing `<!DOCTYPE` or `<!ENTITY` declarations.
  - Retain pure Python standard library core (`xml.etree.ElementTree` with `# noqa: S314` triage) without adding external `defusedxml` pip dependencies.
  - Ensure 3-way synchronization conflicts create timestamped conflict sidecars (`.conflict_<timestamp>.md`) without silent prose overwrites.
- **Consequences**: Hardened import/sync pipeline resilient to malicious payloads while remaining 100% pip-dependency-free.

---

## Subsystem Deep-Dives

### Subsystem 1: Bidirectional DOCX Sync & Hardened OpenXML Pipeline (`scripts/lib/docx_sync.py`)

The DOCX synchronization engine provides seamless bidirectional interchange between plain Markdown chapter scenes and standard Microsoft Word `.docx` documents.

```mermaid
flowchart TD
    A["Raw .docx File"] --> B{"Size Checks (<20MB Archive, <50MB Uncompressed)"}
    B -- "Exceeded" --> C["Raise ValueError / Reject File"]
    B -- "OK" --> D["Extract word/document.xml"]
    D --> E{"Scan for <!DOCTYPE or <!ENTITY"}
    E -- "Found" --> F["Raise ValueError (XXE / Entity Injection Refused)"]
    E -- "Clean" --> G["xml.etree.ElementTree Parse"]
    G --> H["AST Run & Paragraph Tokenization"]
    H --> I["Three-Way SHA-256 Hash Comparison (.sync_state.json)"]
    I -- "Both Changed Independently" --> J["Branch to <chapter>.conflict_<timestamp>.md"]
    I -- "Clean Update" --> K["Atomically Update Markdown / DOCX via atomic_write()"]
```

**Key Types & Functions**:
- `strip_scene_tags_and_frontmatter(text: str)`: Isolates YAML frontmatter, `@tags:`, and `% comments` from prose body text.
- `convert_docx_to_markdown(docx_path: str | Path)`: Extracts formatted paragraphs, italic/bold runs, and heading hierarchies while enforcing XXE guards.
- `sync_manuscript_docx(ms_path, draft)`: Manages 3-way hash synchronization state and prevents silent data loss.

### Subsystem 2: Multi-Tier Versioning & Disaster Recovery (`scripts/save_snapshot.sh`, `scripts/backup_world.sh`, `scripts/restore_world.sh`)

Ars Arcanum enforces a 3-tier local Git architecture combined with standalone verified tarball archives.

```mermaid
sequenceDiagram
    autonumber
    actor Author
    participant CLI as arcanum save / backup
    participant Git as Local Git Engine (.git)
    participant Tar as Tarball Engine (tar.gz)
    participant Disk as Local Backup (Backups/)
    participant Ext as Secure External Target

    Author->>CLI: arcanum save "Completed Act I"
    CLI->>Git: Check .git/index.lock (exponential retry loop up to 5 attempts)
    Git->>Git: Stage modified Markdown & create milestone commit
    Author->>CLI: arcanum backup
    CLI->>Tar: Create gzip-compressed tarball archive
    Tar->>Disk: Write <project>_<timestamp>.tar.gz
    CLI->>Disk: Compute SHA-256 and write companion .sha256 sidecar
    opt External Destination Configured
        CLI->>Ext: Replicate archive & .sha256 sidecar to external mount
    end
```

### Subsystem 3: Speculative Constraint & Consistency Engine (`continuity.py`, `world_doctor.py`, `magic_system.py`)

The speculative analysis subsystem parses worldbuilding entities, relationships, and manuscript prose to detect canon contradictions and hard magic violations.

```mermaid
flowchart LR
    Lore["World Lore Vaults\n(Characters, Locations, Factions)"] --> Doctor["World Doctor\n(WLD-101 to WLD-108)"]
    Prose["Manuscript Scenes\n(@tags, dialogue, prose)"] --> Continuity["Continuity Engine\n(Trait & Timeline Linter)"]
    Magic["Magic System Schemas\n(Affinity tiers, catalysts, limits)"] --> MagicCheck["Arcane Constraint Matrix\n(MAG-101 to MAG-104)"]

    Doctor --> Report["Interactive HTML / SVG & CLI Diagnostics"]
    Continuity --> Report
    MagicCheck --> Report
```

---

## Part 7 — Confidence Assessment Table

| Claim Area | Confidence Level | Evidence / Verification Method |
| :--- | :--- | :--- |
| **Directory Scaffolding & Git Lifecycle** | **High** | Verified through 7-stage test harness (`verify.sh`) Stage 6 & `tests/test_audit_fixes.sh` Test 1. |
| **Exit Code Standardization (0, 1, 2, 3)** | **High** | Verified through `tests/test_audit_fixes.sh` Test 11 across all scripts. |
| **Multi-Draft & Redline Comparator** | **High** | Verified through `tests/test_drafts_and_diff.py` (21 unit tests) and `tests/test_drafts_and_diff.sh`. |
| **DOCX Sync & Word Processor Integration** | **High** | Verified through `tests/test_docx_sync.py` (7 unit tests) and `tests/test_docx_sync.sh`. |
| **Editorial Craft & Stylistics Linters** | **High** | Verified through `tests/test_stylistics.py`, `tests/test_voice.py`, `tests/test_typography_cleaner.py`. |
| **Plot Matrix & Story Paradigms** | **High** | Verified through `tests/test_plot_matrix.py`, `tests/test_structure.py`, `tests/test_scene_mechanics.py`. |
| **Pre-Flight Compliance & Barcodes** | **High** | Verified through `tests/test_preflight.py`, `tests/test_barcode.py`, `tests/test_frontmatter_builder.py`, `tests/test_query.py`. |
| **Cartography & Static Codex Wiki** | **High** | Verified through `tests/test_cartography.py`, `tests/test_codex_export.py`. |
| **Series Continuity & Tactical Sim** | **High** | Verified through `tests/test_series_continuity.py`, `tests/test_tactical_sim.py`. |
| **Distribution Packaging & Portfolio** | **High** | Verified through `tests/test_package_distribution.py`, `tests/test_portfolio.py`. |
| **Audio Proofreader & Ambient Engine** | **High** | Verified through `tests/test_tts_reader.py`, `tests/test_ambient.py`. |
| **Speculative Fiction Workflow Suites (1–12)** | **High** | Verified through dedicated unit tests (`tests/test_*.py`). Total 282 unit tests passing across 50 test modules. |
| **Dual-Target Secure Backup Replication** | **High** | Verified via real tarball replication, SHA-256 validation, and config test cases. |
| **Typesetting & Pandoc Compilation Bridge** | **High** | Verified through Typst 0.14.2 preview compilation and Pandoc AST testing in `export_book.sh`. |
| **Multi-Era & ISO 8601 Chronological Parsing** | **High** | Verified through unit test matrix in `tests/test_concordance_edge_cases.sh` Test 2 (17 permutations). |
| **Shared Discovery Library (`lib/worlds.sh`)** | **High** | Verified across depth-2, depth-3, and legacy root paths in `tests/test_audit_fixes.sh` Test 15. |
| **Backup Creation & Restore Drill Integrity** | **High** | Verified via real tarball extraction and SHA-256 hash comparison in `verify.sh` Stage 6h/6i. |
| **Flatpak Remote Availability on Non-Mint Distros** | **Inferred** | Flathub remote configuration is automated via `--if-not-exists`, but dependent on upstream network reachability. |
| **LeechBlock NG Rule Import Compatibility** | **Inferred** | JSON schema format is validated, but browser add-on UI import depends on Firefox version. |

---

## Part 8 — Local File Citations & Footnotes

1. [`scripts/arcanum`](file:///scripts/arcanum) — Unified CLI dispatcher handling subcommand routing for all 18 craft, speculative, publishing, and diagnostic tools.
2. [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py) / [`scripts/lib/ui_gtk3.py`](file:///scripts/lib/ui_gtk3.py) / [`scripts/lib/ui_adw.py`](file:///scripts/lib/ui_adw.py) — Desktop application with 6-studio author workflow, Visual Scene Inspector, first-run wizard, and Speculative Fiction Suite integration.
3. [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh) — Canonical shared project discovery and resolution library.
4. [`scripts/lib/cache.py`](file:///scripts/lib/cache.py) — High-throughput mtime-keyed performance cache and canonical word counter.
5. [`scripts/lib/continuity.py`](file:///scripts/lib/continuity.py) — Local-first, privacy-preserving narrative continuity and trait contradiction engine.
6. [`scripts/lib/manuscript_diff.py`](file:///scripts/lib/manuscript_diff.py) & [`scripts/compare_drafts.sh`](file:///scripts/compare_drafts.sh) — Word-level draft diffing and WCAG-compliant visual redline comparator.
7. [`scripts/lib/config.py`](file:///scripts/lib/config.py) — Author preferences, DOCX presets, and secondary backup destination configuration manager.
8. [`scripts/lib/docx_sync.py`](file:///scripts/lib/docx_sync.py) — Bidirectional DOCX synchronization engine and OpenXML manuscript generator with XXE defenses.
9. [`scripts/lib/stylistics.py`](file:///scripts/lib/stylistics.py) — Dialogue mechanics linter (`DIA-101` to `DIA-103`) and sliding-window word echo scanner (`ECH-101`).
10. [`scripts/lib/voice.py`](file:///scripts/lib/voice.py) — Character voice lexical profiler, syllable complexity, and reading grade analyzer.
11. [`scripts/lib/typography_cleaner.py`](file:///scripts/lib/typography_cleaner.py) — Locale-aware smart quotation, dash, and punctuation normalizer.
12. [`scripts/lib/plot_matrix.py`](file:///scripts/lib/plot_matrix.py) — 2D storyline subplot matrix visualizer with standalone HTML export.
13. [`scripts/lib/structure.py`](file:///scripts/lib/structure.py) — Story paradigm structure enforcer for 6 narrative models.
14. [`scripts/lib/scene_mechanics.py`](file:///scripts/lib/scene_mechanics.py) — Goal-Conflict-Disaster and MRU structural analyzer.
15. [`scripts/lib/ambient.py`](file:///scripts/lib/ambient.py) — Procedural WebAudio and offline WAV distraction-free sound generator.
16. [`scripts/lib/preflight.py`](file:///scripts/lib/preflight.py) — Print PDF and EPUB pre-flight compliance linter.
17. [`scripts/lib/barcode.py`](file:///scripts/lib/barcode.py) — Vector SVG and PNG ISBN-13/EAN-13 barcode engine.
18. [`scripts/lib/frontmatter_builder.py`](file:///scripts/lib/frontmatter_builder.py) & [`scripts/init_query.py`](file:///scripts/init_query.py) — Copyright/catalog builder and query submission scaffolder.
19. [`scripts/lib/cartography.py`](file:///scripts/lib/cartography.py) & [`scripts/lib/codex_export.py`](file:///scripts/lib/codex_export.py) — Offline interactive vector map viewer and static HTML reader codex generator.
20. [`scripts/lib/series_continuity.py`](file:///scripts/lib/series_continuity.py) & [`scripts/lib/tactical_sim.py`](file:///scripts/lib/tactical_sim.py) — Cross-book series canon validator and tactical combat simulator.
21. [`scripts/package_distribution.py`](file:///scripts/package_distribution.py) & [`scripts/lib/portfolio.py`](file:///scripts/lib/portfolio.py) — Multi-platform distribution packager and executive portfolio dashboard.
22. [`scripts/lib/tts_reader.py`](file:///scripts/lib/tts_reader.py) — Offline neural auditory proofreading player.
23. [`scripts/lib/astrophysics.py`](file:///scripts/lib/astrophysics.py) — Relativistic spaceflight kinematics, orbital mechanics, comms latencies, and habitability calculations.
24. [`scripts/lib/magic_system.py`](file:///scripts/lib/magic_system.py) — Brandon Sanderson-style hard magic constraint matrix, reagent validation, and fatigue tracking.
25. [`scripts/lib/genealogy.py`](file:///scripts/lib/genealogy.py) — Dynastic family tree DAG builder, biological paradox validator, succession engine, and Mermaid/HTML exporter.
26. [`scripts/lib/conlang.py`](file:///scripts/lib/conlang.py) — Conlang phonotactic word/name generator, historical sound-law mutation applier, and lexicon exporter.
27. [`scripts/lib/pacing.py`](file:///scripts/lib/pacing.py) — Prose mode classification (dialogue/action/exposition), sentence rhythm, POV screen-time balance, and tension arc modeler.
28. [`scripts/lib/journey.py`](file:///scripts/lib/journey.py) — Overland/naval expedition modeler with terrain friction, travel modes, ration/water tracking, and itineraries.
29. [`scripts/lib/calendar.py`](file:///scripts/lib/calendar.py) — Custom planetary calendar arithmetic, multi-moon synodic phase tracker, syzygy and eclipse conjunction engine.
30. [`scripts/lib/factions.py`](file:///scripts/lib/factions.py) — Geopolitical faction matrix, Lanchester battle calculator, and campaign logistics engine.
31. [`scripts/lib/economy.py`](file:///scripts/lib/economy.py) — In-world economy, PPP conversion matrix, price anomaly detector, and tech era anachronism audit.
32. [`scripts/lib/causality.py`](file:///scripts/lib/causality.py) — Causal DAG extractor, grandfather/bootstrap paradox detection, and multiverse branch engine.
33. [`scripts/lib/climate.py`](file:///scripts/lib/climate.py) & [`scripts/lib/ecology.py`](file:///scripts/lib/ecology.py) — Planetary insolation/climate simulator, orographic rain shadow, and trophic food-web energy pyramid modeler.
34. [`scripts/lib/idioms.py`](file:///scripts/lib/idioms.py) & [`scripts/lib/senses.py`](file:///scripts/lib/senses.py) — Earth-eponym immersion audit and 6D sensory distribution analyzer.
35. [`scripts/lib/cipher.py`](file:///scripts/lib/cipher.py) & [`scripts/lib/prophecy.py`](file:///scripts/lib/prophecy.py) — In-world cipher encoder/decoder, phonetic rune translator with SVG cards, and prophecy resolution matrix.
36. [`scripts/setup_arcanum.sh`](file:///scripts/setup_arcanum.sh) — OS-gated system installer with dry-run and fail-closed SHA-256 binary verification.
37. [`scripts/export_book.sh`](file:///scripts/export_book.sh) — Multi-format publication compiler (Typst PDF, Pandoc EPUB, submission DOCX) with draft-aware resolution.
38. [`scripts/generate_concordance.sh`](file:///scripts/generate_concordance.sh) — Automated Dramatis Personae and Glossary back-matter generator.
39. [`scripts/world_doctor.sh`](file:///scripts/world_doctor.sh) — Multi-era timeline validator, schema linter, and lore drift diagnostic engine.
40. [`scripts/backup_world.sh`](file:///scripts/backup_world.sh) — Dual-target standalone verified archive backup creator with SHA-256 checksums.
41. [`scripts/restore_world.sh`](file:///scripts/restore_world.sh) — Secure archive restoration engine with path traversal protections.
42. [`scripts/verify.sh`](file:///scripts/verify.sh) — Canonical 7-stage quality and regression test harness.
43. [`templates/typst/book_template.typ`](file:///templates/typst/book_template.typ) — Professional publication typography layout rules for trade books.
44. [`templates/world-bible/`](file:///templates/world-bible/) — Obsidian World Bible templates, 10 vendored community plugins, and 11 Metadata Menu `fileClasses` schemas.
45. [`templates/manuscript/`](file:///templates/manuscript/) — Standalone manuscript project hierarchy, outlines, and novelWriter XML schema.
46. [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) — GitHub Actions continuous integration quality gate on `ubuntu-24.04`.
47. [`dependencies.lock`](file:///dependencies.lock) — Pinned lockfile with SHA-256 digests for Typst and all 10 vendored Obsidian plugins.

