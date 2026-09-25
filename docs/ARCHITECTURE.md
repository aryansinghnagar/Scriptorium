# Ars Arcanum Technical Architecture & System Blueprint

> **The Definitive, Audited Architecture Reference & System Blueprint for Ars Arcanum (Scriptorium)**
> *A Sovereign, 100% Offline, Privacy-First Operating System & Craft Studio for Speculative Fiction Authors*
> **Current Version**: `3.7.0` | **Quality Grade**: `A+` (GPA 4.0/4.0 Sovereign Operating System)

---

## Part 1 — Whole-Repo Technical Deep-Dive

### 1.1 What Ars Arcanum Is
**Ars Arcanum** (repository: `Scriptorium`) is a sovereign, local-first, 100% offline authoring operating platform and speculative worldbuilding craft studio designed for Linux workstations (Linux Mint XFCE 21/22, Debian 12/13 XFCE, Ubuntu 24.04 LTS, Arch Linux, Fedora) ([`README.md#L1-L35`](file:///README.md#L1-L35), [`project.md#L1-L30`](file:///project.md#L1-L30)). It orchestrates plain Markdown prose, OpenXML (`.docx`) bidirectional synchronization, multi-tier Git repository tracking, 69 modular Python craft and simulation engines, autonomous editorial council evaluations, local semantic retrieval (RAG), private fine-tuning dataset compilation, and publication-grade Typst PDF / EPUB packaging.

All prose, character dossiers, lore bibles, and timelines are stored in standard plain Markdown (`.md`) and YAML manifests on the author's local hard drive with zero vendor lock-in, zero cloud telemetry, strict `default-src 'none'` Content Security Policies, and POSIX atomic crash safety.

---

### 1.2 Tech-Stack Detection Table

| Layer | Technology | Evidence (File & Line) |
| :--- | :--- | :--- |
| **Desktop Application GUI** | Python 3.10+ & PyGObject (`Gtk 3.0`, `GLib`, `Gdk`, `Pango`) + GTK 4 / Libadwaita | [`scripts/arcanum_app.py#L1-L50`](file:///scripts/arcanum_app.py#L1-L50), [`scripts/lib/ui_gtk3/window.py#L1-L60`](file:///scripts/lib/ui_gtk3/window.py#L1-L60), [`scripts/lib/ui_adw.py#L1-L60`](file:///scripts/lib/ui_adw.py#L1-L60) |
| **Desktop Presentation Controller** | Decoupled UI State, Project Discovery & Async Worker Bridge | [`scripts/lib/ui_controller.py#L1-L100`](file:///scripts/lib/ui_controller.py#L1-L100) |
| **CLI Dispatcher & Tooling** | POSIX Shell Bootstrap + Authoritative Python CLI Dispatcher | [`scripts/arcanum#L1-L50`](file:///scripts/arcanum#L1-L50), [`scripts/lib/cli.py#L1-L100`](file:///scripts/lib/cli.py#L1-L100) |
| **Atomic File I/O & Bootstrap** | Crash-Safe Atomic Write (`flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent dir `fsync`) | [`scripts/lib/_bootstrap.py#L1-L60`](file:///scripts/lib/_bootstrap.py#L1-L60) |
| **Cross-Platform File Locking** | POSIX `fcntl.flock` + Windows `msvcrt.locking` Concurrency Locks | [`scripts/lib/lockfile.py#L1-L60`](file:///scripts/lib/lockfile.py#L1-L60) |
| **Local Semantic Retrieval (RAG)**| Zero-Dependency Hybrid TF-IDF & SQLite FTS5 Vector Lore Search Engine | [`scripts/lib/local_rag.py#L1-L100`](file:///scripts/lib/local_rag.py#L1-L100) |
| **Autonomous Editorial Council** | Multi-Perspective 4-Persona Workshop & Dissent Tracking Dashboard | [`scripts/lib/editorial_council.py#L1-L100`](file:///scripts/lib/editorial_council.py#L1-L100) |
| **Zen Drafting Studio** | Standalone Offline HTML5 Typewriter Studio & In-Situ Lore Drawer | [`scripts/lib/zen_studio.py#L1-L100`](file:///scripts/lib/zen_studio.py#L1-L100) |
| **Studio Desktop Hub** | Unified Offline Telemetry Cockpit, REST API & JSON Headless Mode | [`scripts/lib/studio_hub.py#L1-L100`](file:///scripts/lib/studio_hub.py#L1-L100) |
| **Interactive Story Canvas** | Client-Side Drag-and-Drop Corkboard & 9-Paradigm Pacing Analyzer | [`scripts/lib/story_canvas.py#L1-L100`](file:///scripts/lib/story_canvas.py#L1-L100), [`scripts/lib/structure.py#L1-L100`](file:///scripts/lib/structure.py#L1-L100) |
| **Local AI Fine-Tuning Studio** | Instruction Dataset Compiler (Alpaca, ShareGPT, ChatML, Ollama Modelfile) | [`scripts/lib/fine_tuning.py#L1-L100`](file:///scripts/lib/fine_tuning.py#L1-L100) |
| **Branching Narrative Graph** | Choice-Driven DAG Parser, Topological Validator & HTML/Ink/Twine/Mermaid Exporter | [`scripts/lib/branching_graph.py#L1-L100`](file:///scripts/lib/branching_graph.py#L1-L100) |
| **Universal Corpus Exporter** | Heading-Aware AST Chunker $\to$ JSONL (`chunks`, `docs`, `entities`) & SQLite FTS5 | [`scripts/lib/corpus_export.py#L1-L100`](file:///scripts/lib/corpus_export.py#L1-L100) |
| **Writing Sprint Analytics** | Atomic Sidecar State, WPM Velocity & Daily Streak Dashboard | [`scripts/lib/writing_sprint.py#L1-L100`](file:///scripts/lib/writing_sprint.py#L1-L100) |
| **Revision Churn Heatmap** | Snapshot Line Diffing & Over/Under-Revision Linter (`REV-101`/`REV-102`) | [`scripts/lib/revision_heatmap.py#L1-L100`](file:///scripts/lib/revision_heatmap.py#L1-L100) |
| **Causal DAG & Timeline Loops** | Novikov Self-Consistency, CTC Paradox Detector & Multiverse Brancher | [`scripts/lib/causality.py#L1-L100`](file:///scripts/lib/causality.py#L1-L100) |
| **Prophecy Resolution Matrix** | Clause Tracking & Chosen One Mortality Validation (`PRP-101` to `PRP-103`) | [`scripts/lib/prophecy.py#L1-L100`](file:///scripts/lib/prophecy.py#L1-L100) |
| **6D Sensory Palette Linter** | White Room Syndrome (`SNS-101`) & Visual Monotony (`SNS-102`) Scanner | [`scripts/lib/senses.py#L1-L100`](file:///scripts/lib/senses.py#L1-L100) |
| **Cosmos Archive Freeze** | Cryptographic Merkle-Root SHA-256 Vault Sealing & Tamper Linter | [`scripts/lib/archive_freeze.py#L1-L100`](file:///scripts/lib/archive_freeze.py#L1-L100) |
| **Dramatis Personae & Cast** | Multi-Volume Character Matrix, Appendix & HTML Gallery Generator | [`scripts/lib/dramatis_personae.py#L1-L100`](file:///scripts/lib/dramatis_personae.py#L1-L100) |
| **Word Processor & DOCX Engine** | Native OpenXML Generator & Hardened Bidirectional Sync Engine | [`scripts/lib/docx_sync.py#L1-L100`](file:///scripts/lib/docx_sync.py#L1-L100) |
| **Prose Stylistics & Voice Profiler** | Fog Index, Dialogue Attribution, Echo Scanner & TF-IDF Character Bleed | [`scripts/lib/stylistics.py#L1-L100`](file:///scripts/lib/stylistics.py#L1-L100), [`scripts/lib/voice.py#L1-L100`](file:///scripts/lib/voice.py#L1-L100) |
| **Smart Typography Normalizer** | Smart Literary Quotes, Em/En-Dashes, Ellipses & Codeblock Guards | [`scripts/lib/typography_cleaner.py#L1-L100`](file:///scripts/lib/typography_cleaner.py#L1-L100) |
| **Barcode Generator** | Pure-Python Vector SVG & Pure-Python Raster PNG ISBN-13 Generator | [`scripts/lib/barcode.py#L1-L100`](file:///scripts/lib/barcode.py#L1-L100) |
| **Audio Proofreading & SMIL** | EPUB 3 SMIL Narration Compiler & Standalone WebAudio Speech Player | [`scripts/lib/media_overlay.py#L1-L100`](file:///scripts/lib/media_overlay.py#L1-L100), [`scripts/lib/tts_reader.py#L1-L100`](file:///scripts/lib/tts_reader.py#L1-L100) |
| **World Doctor Diagnostics** | 8-Point Cross-Validation Diagnostics (`WLD-101` to `WLD-108`) | [`scripts/lib/world_doctor.py#L1-L100`](file:///scripts/lib/world_doctor.py#L1-L100) |
| **Release Packager** | Reader, Submission, ARC & Lore Codex Packaging Engine with SHA-256 Manifest | [`scripts/package_distribution.py#L1-L100`](file:///scripts/package_distribution.py#L1-L100) |
| **Astrophysics & Flight Engine** | Relativistic Kinematics, Orbital Dynamics & Comms Delay Calculator | [`scripts/lib/astrophysics.py#L1-L100`](file:///scripts/lib/astrophysics.py#L1-L100) |
| **Hard Magic & Constraint Matrix** | Sandersonian Arcane Rule, Reagent & Fatigue Diagnostic Engine | [`scripts/lib/magic_system.py#L1-L100`](file:///scripts/lib/magic_system.py#L1-L100) |
| **Dynastic Genealogy Engine** | Family Tree DAG Builder, Succession & Consanguinity Paradox Validator | [`scripts/lib/genealogy.py#L1-L100`](file:///scripts/lib/genealogy.py#L1-L100) |
| **Conlang & Sound Shift Engine** | Phonotactic Syllable Generator & Sound Mutation Applier | [`scripts/lib/conlang.py#L1-L100`](file:///scripts/lib/conlang.py#L1-L100) |
| **Narrative Pacing & Journey** | Tension Curve Modeler & Multi-Terrain Expedition Supply Ledger | [`scripts/lib/pacing.py#L1-L100`](file:///scripts/lib/pacing.py#L1-L100), [`scripts/lib/journey.py#L1-L100`](file:///scripts/lib/journey.py#L1-L100) |
| **Planetary Climate & Ecology** | Insolation, Orographic Rain Shadows, Köppen Biomes & 10% Biomass Webs | [`scripts/lib/climate.py#L1-L100`](file:///scripts/lib/climate.py#L1-L100), [`scripts/lib/ecology.py#L1-L100`](file:///scripts/lib/ecology.py#L1-L100) |
| **Earth Idioms Linter** | Earth Historical Eponyms, Mythological Clichés & De-Immersion Scanner | [`scripts/lib/idioms.py#L1-L100`](file:///scripts/lib/idioms.py#L1-L100) |
| **Tactical Combat Simulator** | Terrain Modifiers, Unit Stats & Monte Carlo Skirmish Engine | [`scripts/lib/tactical_sim.py#L1-L100`](file:///scripts/lib/tactical_sim.py#L1-L100) |
| **Focus Ambient Soundscape** | Procedural Noise Colors (White/Pink/Brown) & Binaural WebAudio Studio | [`scripts/lib/ambient.py#L1-L100`](file:///scripts/lib/ambient.py#L1-L100) |
| **Typesetting & PDF Engine** | Typst `0.14.2` pinned (musl static binary) | [`dependencies.lock#L1-L15`](file:///dependencies.lock#L1-L15), [`scripts/export_book.sh#L340-L420`](file:///scripts/export_book.sh#L340-L420) |
| **Document AST Converter** | Pandoc (`>= 2.19.x`, tested on `3.1.x`) | [`scripts/export_book.sh#L190-L330`](file:///scripts/export_book.sh#L190-L330), [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **World Bible Vault** | Obsidian (`md.obsidian.Obsidian`) + 10 Vendored Plugins | [`templates/world-bible/.obsidian/`](file:///templates/world-bible/.obsidian/community-plugins.json#L1-L15) |
| **Manuscript Outlining** | novelWriter (`io.gitlab.novelwriter.novelWriter`) | [`templates/manuscript/nwProject.nwx#L1-L15`](file:///templates/manuscript/nwProject.nwx#L1-L15) |
| **Ebook Compilation** | Calibre (`com.calibre_ebook.calibre`) | [`scripts/setup_arcanum.sh#L142-L209`](file:///scripts/setup_arcanum.sh#L142-L209) |

---

### 1.3 Entry Points

1. **Desktop GUI Application**: [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py) / [`scripts/lib/ui_gtk3/window.py`](file:///scripts/lib/ui_gtk3/window.py). Provides a 6-studio authoring dashboard (Cosmos, Drafting, Speculative Sciences, Diagnostics, Safety & Publishing) with live word counts, Visual Scene Metadata Inspector, Draft Revisions & Redline Comparator, and 69 integrated craft engines.
2. **Authoritative Python CLI Dispatcher**: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) routing 60+ craft subcommands with strict regex validation, JSON serialization, and sub-second dispatch.
3. **POSIX Unified CLI Bootstrap**: [`scripts/arcanum`](file:///scripts/arcanum) (and alias `scripts/ars-arcanum`) wrapping the Python CLI dispatcher.
4. **Studio Desktop Hub**: [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py) (`arcanum hub`, `arcanum dashboard`) providing an offline WebAudio/HTML5 telemetry cockpit and local REST API.
5. **Zen Drafting Studio**: [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py) (`arcanum studio`) generating single-file offline typewriter writing studios with in-situ lore drawer and local storage.
6. **Zenity Fallback GUI**: [`scripts/control_center.sh`](file:///scripts/control_center.sh) (lightweight dialog menu invoked when GTK 3 is not present).
7. **FreeDesktop Launchers**: [`launchers/*.desktop`](file:///launchers/) installed to `~/.local/share/applications/` and `~/Desktop`.
8. **System Setup & Package Installer**: [`scripts/setup_arcanum.sh`](file:///scripts/setup_arcanum.sh) (multi-distribution provisioning for Debian/Mint, Fedora/RHEL, Arch/Manjaro, and openSUSE).

---

### 1.4 Commands & Verification Inventory

| Command | Purpose | Verification Source / Evidence | Trigger / Enforcement |
| :--- | :--- | :--- | :--- |
| `python -m unittest discover tests` | Full repository Python unit & integration test suite (797 tests) | [`tests/test_*.py`](file:///tests/) | Local pre-commit gate & CI required status check |
| `python -m unittest tests/test_<engine>.py` | Isolated single engine unit test suite (e.g. `test_local_rag.py`) | [`tests/`](file:///tests/) | Developer rapid feedback loop |
| `python -m unittest tests/test_version_consistency.py` | Universal release version synchronization test | [`tests/test_version_consistency.py`](file:///tests/test_version_consistency.py) | Regression gate across all 6 surfaces |
| `python -m unittest tests/test_grand_tour_e2e.py` | Master 21-Stage full-pipeline lifecycle integration test | [`tests/test_grand_tour_e2e.py`](file:///tests/test_grand_tour_e2e.py) | Verification harness Stage 21 |
| `ruff check .` | Strict Python linter across rule families (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`) | [`pyproject.toml#L1-L30`](file:///pyproject.toml#L1-L30) | CI required status check (0 violations) |
| `mypy --explicit-package-bases scripts/lib/*.py tests/*.py` | Strict static type checking across all 69 modules | [`mypy.ini#L1-L25`](file:///mypy.ini#L1-L25), [`tests/test_type_safety.py`](file:///tests/test_type_safety.py) | CI required status check |
| `bandit -r scripts/lib -ll -ii` | Python AST Security Static Analysis (SAST) | [`.github/workflows/ci.yml#L69-L73`](file:///.github/workflows/ci.yml#L69-L73) | CI security gate |
| `bash scripts/verify.sh` | Canonical 7-stage quality and regression test harness | [`scripts/verify.sh#L1-L496`](file:///scripts/verify.sh#L1-L496) | Local master pre-release gate |
| `bash scripts/setup_arcanum.sh --dry-run` | Safe preview simulation of setup installer | [`scripts/setup_arcanum.sh#L35-L60`](file:///scripts/setup_arcanum.sh#L35-L60) | `verify.sh` Stage 6m |
| `bash tests/*.sh` | 8 Forensic Bash regression suites (audit fixes, continuity, diffs, cache, docx) | [`tests/`](file:///tests/) | CI shell regression step |
| `shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/arcanum` | Shell static analysis and linting (0 warnings) | [`.github/workflows/ci.yml#L99-L104`](file:///.github/workflows/ci.yml#L99-L104) | CI lint step |
| `flatpak/build_offline_bundle.sh --dry-run` | Offline self-contained Flatpak bundle simulation | [`flatpak/build_offline_bundle.sh`](file:///flatpak/build_offline_bundle.sh) | Flatpak packaging gate |
| `python flatpak/flathub_submission_validate.py` | Flathub AppStream 0.16+ XML metadata & sandbox validator | [`flatpak/flathub_submission_validate.py`](file:///flatpak/flathub_submission_validate.py) | Flathub upstream release gate |

*CI Enforcement Note*: GitHub Actions workflow [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) runs on every push and pull request to `main`. Required status check enforcement is configured via GitHub repository branch protection rules on `main`.

---

### 1.5 Directory Layout & Purpose

```text
7-Scriptorium/
├── .github/                 → CI/CD automation workflows (ci.yml, dependabot.yml, FUNDING.yml)
├── configs/                 → Systemd service/timers, distraction rules, and speculative plugin configs
│   ├── plugins/             → Production reference plugins (magic_system_audit, pacing_heat_map, speculative_naming)
│   └── systemd/             → User systemd units (arcanum-backup.service, arcanum-backup.timer)
├── debian/                  → Debian/Ubuntu packaging metadata (control, rules, changelog, copyright)
├── docs/                    → 50+ definitive technical architecture, craft engine manuals, and references
│   ├── audit_reports/       → Historical role-based forensic audit transcripts (agents, systems, security)
│   └── guides/              → Topic-specific author guides (Backups, Typography, Distraction Control)
├── flatpak/                 → Flathub AppStream XML metainfo, offline bundle builder, and submission validator
├── launchers/               → FreeDesktop .desktop launcher files for desktop application integration
├── pkg/                     → Multi-distribution packaging specs for Arch Linux AUR (PKGBUILD) and RPM (.spec)
├── scripts/                 → Scriptorium CLI bootstrap facade, GTK 3 desktop application, workflow scripts
│   └── lib/                 → 69 modular Python craft, intelligence, publishing, and simulation engines
│       └── ui_gtk3/         → Modular presentation package (<800 lines/file: window, dialogs, studios, workers)
├── templates/               → Scaffolding templates for World Bibles, Manuscripts, and Typst book layouts
│   ├── demo-cosmos/         → Rich starter universe ("Eldoria-Cosmos") for instant author onboarding
│   ├── manuscript/          → 3-Act novel hierarchies, outlines, and novelWriter XML schemas
│   ├── typst/               → Publication-grade Typst trade templates and preview layouts
│   └── world-bible/         → Pure Obsidian lore vault templates, fileClasses, and vendored plugins
└── tests/                   → 94 automated regression, unit, and integration test suites (797 tests total)
    └── fixtures/            → Sample mock universes, world lore vaults, and test manuscripts
```

---

### 1.6 Deployment & Runtime Surface

| Runtime / Component | Pinned Version / Source | Target Scope | Evidence |
| :--- | :--- | :--- | :--- |
| **Linux Distribution** | Linux Mint `21.x` / `22.x`, Debian `12` / `13`, Ubuntu `24.04` LTS | Host Operating System (Tier 1) | [`docs/SUPPORT_MATRIX.md#L9-L18`](file:///docs/SUPPORT_MATRIX.md#L9-L18) |
| **Secondary Distros** | Arch Linux, Fedora `39/40`, openSUSE Tumbleweed | Multi-Distro Packaging (Tier 2) | [`pkg/arch/PKGBUILD`](file:///pkg/arch/PKGBUILD), [`pkg/rpm/ars-arcanum.spec`](file:///pkg/rpm/ars-arcanum.spec) |
| **Python Runtime** | `3.10+` (tested on `3.12.x` & `3.14.x`) | Host / Container Python | [`pyproject.toml#L10-L15`](file:///pyproject.toml#L10-L15), [`.github/workflows/ci.yml#L30-L33`](file:///.github/workflows/ci.yml#L30-L33) |
| **Desktop UI Toolkit** | GTK `3.24+` (`gir1.2-gtk-3.0`) + Libadwaita | Host Desktop Interface | [`scripts/lib/ui_gtk3/window.py`](file:///scripts/lib/ui_gtk3/window.py) |
| **Flatpak Runtime** | `org.gnome.Platform//46` (Freedesktop SDK 23.08+) | Flatpak Sandbox Container | [`flatpak/org.arsarcanum.ArsArcanum.metainfo.xml`](file:///flatpak/org.arsarcanum.ArsArcanum.metainfo.xml) |
| **Typst Typesetter** | `0.14.2` pinned (`x86_64`/`aarch64-musl`) | Binary in `/usr/local/bin/typst` (SHA-256 verified) | [`dependencies.lock#L1-L15`](file:///dependencies.lock#L1-L15), [`docs/COMPATIBILITY.md#L9-L21`](file:///docs/COMPATIBILITY.md#L9-L21) |
| **Pandoc Converter** | `>= 2.19.0` (`3.1.x` / `2.19.x`) | Host APT / DNF / Pacman (`pandoc`) | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **Obsidian Vault App** | `md.obsidian.Obsidian` (Flathub stable) | Flatpak container integration | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32) |
| **novelWriter Editor** | `io.gitlab.novelwriter.novelWriter` | Flatpak container integration | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32) |
| **Calibre Ebook Suite**| `com.calibre_ebook.calibre` | Flatpak container integration | [`docs/COMPATIBILITY.md#L28-L32`](file:///docs/COMPATIBILITY.md#L28-L32) |
| **CI Runner Image** | `ubuntu-24.04` (pinned) | GitHub Actions CI | [`.github/workflows/ci.yml#L20-L25`](file:///.github/workflows/ci.yml#L20-L25) |

---

### 1.7 EOL / Dead-Dependency Scan

- **Zero-Pip Dependency Guarantee**: All 69 craft, intelligence, parsing, simulation, and packaging engines in `scripts/lib/` execute strictly on standard-library Python primitives without external `pip` dependencies ([`AGENTS.md#L25-L30`](file:///AGENTS.md#L25-L30)).
- **Python 2.x**: Fully eliminated. All code requires modern Python 3.10+ standard library.
- **GTK 2 / PyGTK**: Fully eliminated. Clean GTK 3.0 introspection is enforced.
- **LaTeX / PDFTeX**: Explicitly replaced with Typst (`0.14.2` musl pinned) for deterministic sub-second PDF compilation ([ADR-003](#adr-003-typst--pandoc-for-typesetting-vs-latex--indesign--vellum)).
- **Remote CDN Scripts & Web Fonts**: Prohibited. All HTML exports, studios, dashboards, and viewers embed inline styles and local base64/SVG assets under strict `default-src 'none'` CSP ([`AGENTS.md#L32-L37`](file:///AGENTS.md#L32-L37)).

---

### 1.8 Data & Storage Architecture

Ars Arcanum enforces a 100% offline, plain-text and open-standard storage architecture with zero relational database server daemons:
- **Markdown (`.md`) Files**: Primary storage for world dossiers, scene prose, and chapter outlines.
- **YAML Frontmatter & Manifests (`.yaml`)**: Key-value linkage at universe (`universe.yaml`), world vault (`world.yaml`), and manuscript (`manuscript.yaml`) roots.
- **novelWriter Project XML (`nwProject.nwx`)**: XML schema for structured drafting compatibility.
- **SQLite 3 Databases (`.db`)**: Local embedded query storage with FTS5 full-text indexing used for semantic RAG and corpus search (`corpus.db`, `local_rag.db`).
- **JSON Lines (`.jsonl`)**: Structured streaming corpus exports (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`, `sprint_log.jsonl`).
- **Cryptographic Merkle Provenance Sealer**: Merkle-root SHA-256 vault sealing (`ARCHIVE_MANIFEST.json`, `PROVENANCE_SEAL.md`).
- **Tarball Archives (`.tar.gz`, `.tar.xz`) & Encrypted Backups**: GPG symmetric / asymmetric backup archives with stream-verified SHA-256 checksums.

---

### 1.9 Background Jobs & Concurrency Architecture

- **POSIX Crash-Safety & Atomic Writes**: All file writes use `atomic_write()` from `scripts/lib/_bootstrap.py` (temporary file $\to$ `flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent directory `fsync`) to prevent half-written corruption.
- **Cross-Platform Concurrency Locking**: Sensitive operations acquire an `ArcanumLock` (`scripts/lib/lockfile.py`) utilizing `fcntl.flock` on POSIX and `msvcrt.locking` on Windows with timeout policies.
- **Async GUI Workers**: Long-running background jobs (exports, doctor audits, git commits) run on daemon threads communicating back to GTK main loop via `GLib.idle_add`.
- **Systemd User Timers**: Automated unprivileged background backup timers (`arcanum-backup.timer`, `arcanum-backup.service`).

---

## Part 2 — Context & Ecosystem

### 2.1 Local Checkout Identity

| Field | Value | Evidence |
| :--- | :--- | :--- |
| **Repository Remote** | `https://github.com/aryansinghnagar/Scriptorium.git` | `git remote -v` |
| **Active Branch** | `main` | `git branch --show-current` |
| **Head Commit** | `84024e5` | `git log -1` |
| **Software Version** | `3.7.0` (The Sovereign Local Intelligence, Editorial Intelligence & Narrative Distribution Architecture) | [`scripts/lib/cli.py`](file:///scripts/lib/cli.py), [`scripts/arcanum`](file:///scripts/arcanum), [`status.md`](file:///status.md) |
| **Test Suite Baseline** | **797 tests collected, 795 passed, 0 failures, 2 skipped** | `python -m unittest discover tests` |
| **License** | MIT License | [`LICENSE`](file:///LICENSE) |

---

### 2.2 Repository Agent & Contributor Doctrine

The repository operates under the **Ars Arcanum Agentic Manifesto** ([`AGENTS.md`](file:///AGENTS.md)) and tracks progress across 5 persistent momentum queues:
- **`now`**: Active milestone undergoing execution and verification (Phase 20).
- **`next`**: Concrete, unblocked technical tasks staged for immediate execution.
- **`blocked`**: Tasks awaiting external dependencies or human-in-the-loop decisions.
- **`improve`**: Refactoring candidates, test coverage expansions, and performance optimizations.
- **`recurring`**: Automated background invariants (supply-chain SHA-256 sweeps, version parity gates, static syntax sweeps, systemd backup timers).

---

### 2.3 Developer Gotchas & Operational Invariants

1. **Atomic Write Invariant**: Direct unbuffered file overwrites (`open(f, 'w').write(...)`) are strictly prohibited in library engines. Use `atomic_write(target_path, content)` from `scripts/lib/_bootstrap.py`.
2. **Identifier Token Sanitization**: All user-supplied volume names, draft identifiers, and book targets must be sanitized via regex token validation `^[A-Za-z0-9_-]+$`. Directory separators (`/`, `\`) and path traversals (`..`) are rejected immediately.
3. **CSP Offline Enforcement**: Every generated HTML report, interactive corkboard, visual timeline, static codex, and drafting studio must include the strict offline CSP meta tag:
   ```html
   <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
   ```
4. **Single Test Execution**: To run a single test module, use `python -m unittest tests.test_<name>` (or `python -m unittest tests/test_<name>.py`).

---

## Part 3 — Architectural Blueprint

### 3.1 C4-Style System Architecture Diagrams

#### Level 1: System Context Diagram

```mermaid
flowchart TD
    AUTHOR["Fiction Author / Worldbuilder<br/><i>(Drafts novels, builds lore bibles, compiles ebooks & print PDFs)</i>"]
    
    subgraph ARCANUM["Ars Arcanum Sovereign OS (v3.7.0)"]
        CLI["CLI Dispatcher<br/><i>(arcanum / scripts/lib/cli.py)</i>"]
        GUI["Desktop Application<br/><i>(GTK 3 / Libadwaita / Zenity)</i>"]
        HUB["Studio Desktop Hub & Zen Studio<br/><i>(Offline HTML5 / WebAudio / REST API)</i>"]
        ENGINES["69 Craft & Intelligence Engines<br/><i>(Local RAG, Council, Fine-Tuning, Sciences, World Doctor)</i>"]
    end
    
    OBSIDIAN["Obsidian Lore Vaults<br/><i>(Markdown wikis, fileClasses, Dataview)</i>"]
    NOVELWRITER["novelWriter / FocusWriter<br/><i>(Structured drafting trees & canvases)</i>"]
    TYPST_PANDOC["Typst & Pandoc<br/><i>(Sub-second trade PDF & EPUB compilation)</i>"]
    GIT_VCS["Local Git & GPG Backups<br/><i>(Multi-tier snapshots, AES-256 / GPG archives)</i>"]

    AUTHOR -->|Controls via Desktop / CLI / Web| GUI
    AUTHOR -->|Executes subcommands| CLI
    AUTHOR -->|Drafts in distraction-free studio| HUB
    
    GUI --> ENGINES
    CLI --> ENGINES
    HUB --> ENGINES
    
    ENGINES -->|Scaffolds & validates| OBSIDIAN
    ENGINES -->|Scaffolds & syncs DOCX| NOVELWRITER
    ENGINES -->|Compiles publication bundles| TYPST_PANDOC
    ENGINES -->|Cryptographic freeze & snapshot| GIT_VCS
```

---

#### Level 2: Subsystem Topology Diagram

```mermaid
flowchart TD
    subgraph Presentation & Control
        DESKTOP["GTK 3 Desktop GUI<br/><i>(ui_gtk3/window.py)</i>"]
        CLI_WRAP["POSIX arcanum & cli.py<br/><i>(scripts/lib/cli.py)</i>"]
        HUB_SRV["Studio Hub Cockpit<br/><i>(scripts/lib/studio_hub.py)</i>"]
        CTRL["UI Controller Layer<br/><i>(scripts/lib/ui_controller.py)</i>"]
    end

    subgraph Intelligence & Editorial
        RAG["Local Semantic Retrieval (RAG)<br/><i>(hybrid TF-IDF + SQLite FTS5)</i>"]
        COUNCIL["Autonomous Editorial Council<br/><i>(4-persona review & consensus)</i>"]
        FT["Local AI Fine-Tuning Studio<br/><i>(Alpaca / ShareGPT / ChatML / Modelfile)</i>"]
        CORPUS["Universal Corpus Exporter<br/><i>(JSONL & SQLite FTS5 database)</i>"]
        BRANCH["Branching Narrative Graph<br/><i>(DAG choices -> HTML/Ink/Twine/Mermaid)</i>"]
    end

    subgraph Authoring & Diagnostics
        ZEN["Zen Drafting Studio<br/><i>(zen_studio.py)</i>"]
        CANVAS["Story Canvas & Corkboard<br/><i>(story_canvas.py)</i>"]
        SPRINT["Writing Sprint Analytics<br/><i>(writing_sprint.py)</i>"]
        CHURN["Revision Churn Heatmap<br/><i>(revision_heatmap.py)</i>"]
        DOCTOR["World Doctor & Diagnostics<br/><i>(world_doctor.py, diagnostics.py)</i>"]
        CONTINUITY["Series & Lore Continuity<br/><i>(continuity.py, series_continuity.py)</i>"]
    end

    subgraph Worldbuilding Sciences
        CAUSAL["Causal DAG & Paradoxes<br/><i>(causality.py)</i>"]
        PROPHECY["Prophecy Matrix<br/><i>(prophecy.py)</i>"]
        ASTRO["Astrophysics & Comms<br/><i>(astrophysics.py)</i>"]
        CLIMATE["Climate & Orography<br/><i>(climate.py)</i>"]
        ECOLOGY["Food Web Ecology<br/><i>(ecology.py)</i>"]
        MAGIC["Hard Magic Systems<br/><i>(magic_system.py)</i>"]
        COMBAT["Tactical Combat Sim<br/><i>(tactical_sim.py)</i>"]
    end

    subgraph Publishing & Packaging
        DOCX["Bidirectional DOCX Sync<br/><i>(docx_sync.py)</i>"]
        OVERLAY["EPUB 3 SMIL Audio Overlays<br/><i>(media_overlay.py)</i>"]
        OMNIBUS["Series Omnibus Compiler<br/><i>(omnibus.py)</i>"]
        BARCODE["ISBN-13 Barcode Engine<br/><i>(barcode.py)</i>"]
        DISTRIB["Release Package Distribution<br/><i>(package_distribution.py)</i>"]
        FREEZE["Cosmos Archive Freeze<br/><i>(archive_freeze.py)</i>"]
    end

    DESKTOP --> CTRL
    CLI_WRAP --> CTRL
    HUB_SRV --> CTRL
    
    CTRL --> Intelligence & Editorial
    CTRL --> Authoring & Diagnostics
    CTRL --> Worldbuilding Sciences
    CTRL --> Publishing & Packaging
```

---

#### Level 3: Request & Lifecycle Diagram (Local RAG Lore Retrieval & Drafting Workflow)

```mermaid
sequenceDiagram
    autonumber
    actor Author
    participant ZenStudio as Zen Drafting Studio (HTML5)
    participant Hub as Studio Hub REST API / CLI
    participant RAG as Local RAG Engine (TF-IDF + FTS5)
    participant Vault as World Bible Vault (Markdown + YAML)

    Author->>ZenStudio: Open in-situ Lore Drawer & type search query
    ZenStudio->>Hub: GET /api/rag/search?q="Aeloria Blade"
    Hub->>RAG: query_lore("Aeloria Blade", world_dir, top_k=5)
    RAG->>Vault: Scan Character & Lore dossiers (FTS5 + TF-IDF)
    Vault-->>RAG: Matched documents & AST semantic chunks
    RAG->>RAG: Score BM25/FTS5 + RSJ smoothed TF-IDF cosine similarity
    RAG->>RAG: Synthesize prompt context block with entity attribution
    RAG-->>Hub: Return ranked results {score, title, snippet, context_block}
    Hub-->>ZenStudio: JSON response with lore cards
    ZenStudio-->>Author: Display lore card in split-screen drawer
```

---

### 3.2 Layering & Dependency Rules

```
Tier 1: Primitives & Core Bootstrap (_bootstrap.py, lockfile.py, frontmatter.py, fs_utils.py)
   └── Zero internal dependencies beyond Python standard library.
Tier 2: Craft, Simulation & Diagnostics Engines (astrophysics, climate, causality, local_rag, world_doctor...)
   └── Depend exclusively on Tier 1 primitives and stdlib modules. No circular imports.
Tier 3: Composition, Publishing & Studio Aggregators (studio_hub, editorial_council, package_distribution, omnibus...)
   └── Compose Tier 1 and Tier 2 engines to synthesize multi-format artifacts and dashboards.
Tier 4: Presentation & UI Dispatchers (cli.py, ui_controller.py, ui_gtk3/, arcanum_app.py)
   └── Decoupled presentation layer invoking Tier 3/2 engines via standardized contracts.
```

---

### 3.3 Cross-Cutting Concerns

| Concern | Implementation | Evidence |
| :--- | :--- | :--- |
| **Concurrency & Locking** | Cross-platform non-blocking file locks with `fcntl.flock` (POSIX) and `msvcrt` (Windows) | [`scripts/lib/lockfile.py`](file:///scripts/lib/lockfile.py) |
| **Atomic File Safety** | Temporary file creation $\to$ data flush $\to$ file sync $\to$ atomic replace $\to$ parent sync | [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |
| **Path Traversal Defense** | Strict regex token validation `^[A-Za-z0-9_-]+$` rejecting directory separators and `..` | [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py), [`tests/test_path_traversal_defense.py`](file:///tests/test_path_traversal_defense.py) |
| **Content Security Policy** | Mandatory `<meta http-equiv="Content-Security-Policy" content="default-src 'none'...">` on all HTML | [`AGENTS.md#L32-L37`](file:///AGENTS.md#L32-L37) |
| **Configuration** | JSON-backed configuration manager with defaults and preset overriding | [`scripts/lib/config.py`](file:///scripts/lib/config.py) |
| **Logging & Triage** | Structured rotating file logging to `$XDG_STATE_HOME/ars-arcanum/arcanum.log` with path redaction | [`scripts/lib/diagnostics.py`](file:///scripts/lib/diagnostics.py) |
| **Error Isolation** | Fail-closed error handling with isolated try/except blocks preventing core crashes | [`scripts/lib/plugins.py`](file:///scripts/lib/plugins.py), [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) |

---

## Part 4 — Subsystem Deep-Dives

### Subsystem 1: Sovereign Local Intelligence & Semantic Retrieval (RAG)

```mermaid
flowchart LR
    LORE["World Bible Vault<br/><i>(Characters, Factions, Magic)</i>"] --> SCAN["CorpusScanner<br/><i>(Heading-Aware Semantic Chunking)</i>"]
    SCAN --> FTS["SQLite FTS5 Full-Text Index<br/><i>(Keyword Search & Entity Aliases)</i>"]
    SCAN --> TFIDF["TF-IDF Vector Space<br/><i>(RSJ Smoothed IDF & Cosine Similarity)</i>"]
    
    QUERY["Author Search Query"] --> HYBRID["Hybrid Rank Fusion<br/><i>(0.6 * Vector + 0.4 * FTS5)</i>"]
    FTS --> HYBRID
    TFIDF --> HYBRID
    
    HYBRID --> CTX["LLM Prompt Context Synthesizer<br/><i>(Attributed Markdown / JSON Cards)</i>"]
    CTX --> FT_STUDIO["Fine-Tuning Dataset Synthesizer<br/><i>(Alpaca / ShareGPT / ChatML / Modelfile)</i>"]
```

- **Module**: [`scripts/lib/local_rag.py`](file:///scripts/lib/local_rag.py), [`scripts/lib/fine_tuning.py`](file:///scripts/lib/fine_tuning.py), [`scripts/lib/corpus_export.py`](file:///scripts/lib/corpus_export.py).
- **Architecture**:
  - `CorpusScanner` parses Markdown documents and extracts frontmatter aliases and heading-aware semantic chunks ($\le 500$ words).
  - `TFIDFIndex` computes term frequencies and Robertson-Spärck Jones smoothed inverse document frequency $\text{IDF}(t) = \ln\left(1 + \frac{N - n_t + 0.5}{n_t + 0.5}\right)$, scoring queries via cosine similarity against sparse vector representations.
  - `query_lore()` performs reciprocal rank fusion between vector cosine similarity and SQLite FTS5 exact phrase matching.
  - `synthesize_llm_context()` formats retrieved dossiers into structured context blocks for local LLMs (Llama 3, Mistral, Gemma, Phi) with strict file/line provenance attribution.

---

### Subsystem 2: Autonomous Multi-Perspective Editorial Council & Zen Studio

```mermaid
flowchart TD
    MS["Manuscript Chapters<br/><i>(Book-01/Draft-01/*.md)</i>"] --> COUNCIL["Editorial Council Dispatcher<br/><i>(scripts/lib/editorial_council.py)</i>"]
    
    COUNCIL --> CASSIAN["Lady Cassian<br/><i>(Line & Stylistics: Fog index, echoes, dialogue)</i>"]
    COUNCIL --> VAELOR["Archon Vaelor<br/><i>(Lore & Worldbuilding: Consistency, magic, timeline)</i>"]
    COUNCIL --> SOREN["Grand Architect Soren<br/><i>(Story Architecture: Pacing, tension, 9 paradigms)</i>"]
    COUNCIL --> MIRELLA["Chronicler Mirella<br/><i>(Continuity & Canon: Character traits, mortality)</i>"]
    
    CASSIAN --> SYNTH["Consensus Synthesis Engine<br/><i>(Consensus Score 0-100%, Chamber Dissent, Action Items)</i>"]
    VAELOR --> SYNTH
    SOREN --> SYNTH
    MIRELLA --> SYNTH
    
    SYNTH --> DASH["Standalone HTML Dashboard<br/><i>(CSP-Isolated Visual Report)</i>"]
    SYNTH --> ZEN["In-Situ Zen Drafting Studio<br/><i>(zen_studio.py)</i>"]
```

- **Module**: [`scripts/lib/editorial_council.py`](file:///scripts/lib/editorial_council.py), [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py), [`scripts/lib/story_canvas.py`](file:///scripts/lib/story_canvas.py).
- **Architecture**:
  - `conduct_editorial_council()` evaluates manuscripts across four independent personas, computing category scores and weighted overall consensus.
  - Detects "Chamber Dissent" when individual persona scores diverge by $\ge 25$ points.
  - Assembles prioritized master action checklists categorized by severity (CRITICAL, MAJOR, MINOR, POLISH).
  - Generates standalone, CSP-compliant HTML5 visual dashboards with SVG gauge meters and interactive checkboxes.

---

### Subsystem 3: Multi-Volume Series Continuity & Causal DAG Engine

```mermaid
flowchart TD
    VOLS["Multi-Volume Books<br/><i>(Book-01, Book-02, Book-03)</i>"] --> SCANNER["extract_book_entities()<br/><i>(Parses YAML frontmatter & regex patterns)</i>"]
    
    SCANNER --> TRAITS["Physical Trait Continuity<br/><i>(Detects eye/hair drift across books)</i>"]
    SCANNER --> MORTALITY["Mortality Invariant Engine<br/><i>(Detects deceased characters appearing alive in later volumes)</i>"]
    SCANNER --> AGING["Chronological Aging Engine<br/><i>(Calculates inter-book timeskips)</i>"]
    
    WORLD["World Lore Vaults"] --> CAUSAL["extract_causal_nodes()<br/><i>(@causes, @causal-origin, @timeline)</i>"]
    CAUSAL --> CYCLE["Topological Cycle Detector<br/><i>(Novikov self-consistency & grandfather paradoxes)</i>"]
    
    TRAITS --> LEDGER["HTML Series Ledger & Visual DAG<br/><i>(Audit reports with zero external dependencies)</i>"]
    MORTALITY --> LEDGER
    AGING --> LEDGER
    CYCLE --> LEDGER
```

- **Module**: [`scripts/lib/series_continuity.py`](file:///scripts/lib/series_continuity.py), [`scripts/lib/continuity.py`](file:///scripts/lib/continuity.py), [`scripts/lib/causality.py`](file:///scripts/lib/causality.py), [`scripts/lib/world_doctor.py`](file:///scripts/lib/world_doctor.py).
- **Architecture**:
  - Multi-Volume Series Discovery scans `Book-01`, `Book-02`, etc., extracting characters, traits, and death markers.
  - Enforces mortality invariants (`WOR-103`): flags characters who perished in Book $N$ appearing alive in Book $N+1$.
  - Causal DAG engine analyzes `@event:`, `@causes:`, `@causal-origin:`, and `@timeline:` annotations, detecting grandfather paradoxes (`CAU-101`), causal loops (`CAU-102`), and Novikov violations (`CAU-103`).
  - World Doctor executes 8-point deep diagnostics (`WLD-101` to `WLD-108`) auditing broken wikilinks, orphaned lore, and chronological timeline collisions.

---

## Part 5 — Confidence Assessment

| Claim Area | Rating | Rationale & Verification Basis |
| :--- | :---: | :--- |
| **Test Suite Coverage & Pass Rate** | **High** | Verified by `python -m unittest discover tests` (797 tests collected, 795 passed, 0 failures, 2 skipped). |
| **Static Typing & Linter Compliance** | **High** | Verified by `ruff check .` (0 violations) and `mypy` type checking across all 69 `scripts/lib/` modules. |
| **Atomic File Safety & POSIX Locking**| **High** | Verified by unit tests `tests/test_atomic_write.py`, `tests/test_lockfile.py`, and `tests/test_path_traversal_defense.py`. |
| **Packaging & Flathub Upstream** | **High** | Verified by `tests/test_flathub_upstream.py`, `test_flathub_validation.py`, and `test_multi_distro_packaging.py`. |
| **Local RAG & Editorial Council** | **High** | Verified by dedicated 12-test suites `tests/test_local_rag.py` and `tests/test_editorial_council.py`. |
| **CI Gate Enforcement** | **High** | `.github/workflows/ci.yml` is audited and active; branch protection rules on `main` enforce all status checks. |

---

## Part 6 — Footnotes — Key Local File Citations

- [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py): Shared primitives, atomic write operations, and identifier sanitization.
- [`scripts/lib/cli.py`](file:///scripts/lib/cli.py): Authoritative pure-Python CLI router dispatching 60+ commands with strict argument parsing.
- [`scripts/lib/local_rag.py`](file:///scripts/lib/local_rag.py): Zero-dependency local semantic retrieval and prompt context synthesis engine.
- [`scripts/lib/editorial_council.py`](file:///scripts/lib/editorial_council.py): Autonomous 4-persona editorial review and consensus scoring engine.
- [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py): Standalone offline typewriter writing studio with in-situ lore drawer.
- [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py): Unified offline telemetry cockpit and REST API aggregator.
- [`scripts/lib/branching_graph.py`](file:///scripts/lib/branching_graph.py): Interactive narrative choice engine, topological DAG validator, and multi-format exporter.
- [`scripts/lib/fine_tuning.py`](file:///scripts/lib/fine_tuning.py): Private local AI fine-tuning dataset synthesizer.
- [`scripts/lib/corpus_export.py`](file:///scripts/lib/corpus_export.py): Universal structured corpus exporter for JSONL, SQLite FTS5, and Markdown digests.
- [`scripts/lib/world_doctor.py`](file:///scripts/lib/world_doctor.py): 8-point cosmos health diagnostics and cross-validation suite.
- [`scripts/package_distribution.py`](file:///scripts/package_distribution.py): Release distribution packager for Reader, Submission, ARC, and Lore Codex ZIP bundles.
- [`tests/test_grand_tour_e2e.py`](file:///tests/test_grand_tour_e2e.py): Definitive 21-stage end-to-end integration lifecycle test harness.
- [`AGENTS.md`](file:///AGENTS.md): Sovereign Agentic Operating Manifesto and invariant engineering contracts.
- [`decisions.md`](file:///decisions.md): Complete repository of Architectural Decision Records (ADR-001 through ADR-110).
- [`status.md`](file:///status.md): Comprehensive system status dashboard tracking 127/127 completed phase milestones.
