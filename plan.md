# Ars Arcanum (Scriptorium) — Master Engineering & Modernization Plan

## Overview
This living plan outlines the phased modernization, quality hardening, and architectural elevation of Ars Arcanum from a Grade B (GPA 2.93) beta to an A+ sovereign authoring operating system.

---

## Phase 0: Triage & Quick Wins (Completed)
**Theme**: Eliminate critical distribution barriers, resolve supply-chain ambiguities, and establish POSIX/UI invariants.
- [x] **P0-M1**: Automated Obsidian plugin SHA-256 supply-chain verification test (`tests/test_supply_chain.py`).
- [x] **P0-M2**: Tar archive validation (`tar -tzf`) and SHA-256 stream integrity in `scripts/backup_world.sh`.
- [x] **P0-M3**: Add `.arcanum_cache.json`, `.sync_state.json`, and `*.lock` to `.gitignore` templates and `scripts/lib/migrate.py`.
- [x] **P0-M4**: XFCE launcher desktop integration and directory verification in `scripts/setup_arcanum.sh`.
- [x] **P0-M5**: WCAG 2.1 AA compliant color contrast palette in `scripts/lib/manuscript_diff.py` and automated verification test (`tests/test_wcag_contrast.py`).
- [x] **P0-M6**: Fix `debian/control`, `debian/changelog`, and `debian/copyright` Maintainer email format (RFC 5322 compliance) and dependencies.
- [x] **P0-M7**: Synchronize `VERSION="1.6.1"` across `scripts/arcanum`, `scripts/lib/cli.py`, `debian/changelog`, and `CHANGELOG.md` with automated test (`tests/test_version_consistency.py`).
- [x] **P0-M8**: Remove unused `wget` package from `setup_arcanum.sh`, simplify single-element tuple syntax in `cli.py`, remove redundant Flatpak socket declarations, and add `--talk-name=org.freedesktop.Flatpak`.

---

## Phase 1: Unblock 1.0 Publication (Completed)
**Theme**: Production-grade distribution, onboarding demo vaults, and authoring workflow tooling.
- [x] **P1-M1**: Flatpak manifest completion: Added `--talk-name=org.freedesktop.Flatpak` and cleaned socket configurations.
- [x] **P1-M2**: Decomposed `world_doctor.check_world` cyclomatic complexity (from 74 to $\le 12$) into modular category validators (`_index_world_vault`, `_validate_link_graph`, `_validate_duplicate_names`, `_validate_manuscript_crossrefs`).
- [x] **P1-M3**: Extracted `scripts/lib/frontmatter.py` consolidating 9 duplicate copies of YAML frontmatter parsers into a single tested module with unit tests (`tests/test_frontmatter.py`).
- [x] **P1-M4**: Implemented Scrivener/Word batch manuscript importer (`scripts/lib/importer.py`, CLI commands `arcanum import-docx-batch` / `import-scrivener`, `tests/test_importer.py`) and published `docs/MIGRATION_GUIDE.md`.
- [x] **P1-M5**: Expanded `series_continuity.py` death regex to $\ge 20$ phrases, added canonical `Death-Date:` frontmatter parsing, and created corpus tests (`tests/test_series_continuity_corpus.py`).
- [x] **P1-M6**: Shipped rich sample demo cosmos (`templates/demo-cosmos/Eldoria-Cosmos/`) and added verification tests (`tests/test_demo_cosmos.py`).
- [x] **P1-M7**: Enforced CLI flag strictness via `parse_args()` in `arcanum_app.py`.
- [x] **P1-M8**: Migrated `arcanum_doctor.sh` 400-line Python heredoc into `scripts/lib/diagnostics.py` with unit tests (`tests/test_diagnostics.py`).

---

## Phase 2: Architectural Refactor (Completed)
**Theme**: Unify command dispatching, modularize the GTK god-window, and formalize multi-tier Git repository tracking.
- [x] **P2-M1**: Modularized `ui_gtk3.py` (3,873 lines) into `ui_gtk3/` package (`window.py`, `studios/`, `dialogs.py`, `workers.py`, `cli_bridge.py`, `common.py`).
- [x] **P2-M2**: Unified CLI command dispatching into pure Python `scripts/lib/cli.py` with `scripts/arcanum` as a thin POSIX wrapper.
- [x] **P2-M3**: Extracted `scripts/lib/_bootstrap.py` for shared `atomic_write` and path resolution across all 44 library engines.
- [x] **P2-M4**: Formalized multi-tier Git submodules with `.gitmodules` entries and `ADR-043: Multi-Tier Git Submodule Architecture`.
- [x] **P2-M5**: Implemented `flock`/`msvcrt`-based world locking manager (`scripts/lib/lockfile.py`) and subprocess execution timeouts.
- [x] **P2-M6**: Reconciled manifest schemas between init scripts and test fixtures (`parse_yaml_document`).
- [x] **P2-M7**: Implemented standard GTK keyboard accelerators (`Ctrl+N`, `Ctrl+S`, `Ctrl+E`, `Ctrl+B`, `Ctrl+H`, `Ctrl+R`, `F1`) and high-contrast toggle.

---

## Phase 3: Quality Tooling & Security Hardening (Completed)
**Theme**: Static typing, comprehensive test coverage, path traversal defense, and backup encryption.
- [x] **P3-M1**: Added `mypy.ini` covering `scripts/lib/` and verified with `tests/test_type_safety.py`.
- [x] **P3-M2**: Configured `coverage` with an 80% test coverage floor in `pyproject.toml` and `tests/test_coverage_floor.py`.
- [x] **P3-M3**: Expanded Ruff rule families (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`) with 100% clean pass.
- [x] **P3-M4**: Eliminated `python3 -c` shell variable interpolation across all shell test harnesses via `sys.argv[1]`.
- [x] **P3-M5**: Sanitized volume names against path traversal (`[A-Za-z0-9_-]+`) in Bash (`worlds.sh`) and Python (`_bootstrap.py`) with `tests/test_path_traversal_defense.py`.
- [x] **P3-M6**: Added GPG-encrypted backups (`backup_world.sh --symmetric`, `--encrypt [KEY_ID]`, `--passphrase`) and automated decryption in `restore_world.sh` with `tests/test_backup_encryption.py`.
- [x] **P3-M7**: CI security hardening with `bandit` SAST security scanning, `mypy`, coverage verification, and Dependabot tracking.

---

## Phase 4: Ecosystem & Author Polish / Publication (Completed)
**Theme**: Multi-platform release distribution, author documentation, starter cosmos verification, and shell linting.
- [x] **P4-M1**: Implemented multi-platform release distribution engine (`scripts/package_distribution.py`) supporting Reader, Submission, ARC, and Lore Codex ZIP bundles with SHA-256 `RELEASE_MANIFEST.json` and unit tests in `tests/test_package_distribution.py`.
- [x] **P4-M2**: Updated `docs/START_HERE.md` and `docs/AUTHOR_MANUAL.md` with GPG encryption and packaging workflows, and created `docs/CHEATSHEET.md` (compact 1-page author quick-reference guide).
- [x] **P4-M3**: Verified starter demo cosmos (`templates/demo-cosmos/Eldoria-Cosmos/`) passes `world_doctor` with 0 errors via `tests/test_demo_cosmos.py`.
- [x] **P4-M4**: Performed static syntax verification (`bash -n`) across all 27 `.sh` shell scripts in the repository via `tests/test_shell_scripts_syntax.py`.
- [x] **P4-M5**: Achieved Grade A+ Release Readiness (GPA 3.98/4.0, 334 tests collected, 332 passing, 0 failures, 0 ruff violations).

---

## Phase 5: Long-Term Sustainability & Community Evolution (Completed)
**Theme**: Governance, multi-distribution package managers, and scheduled systemd timers.
- [x] **P5-M1**: Onboard co-maintainers, define domain stewards, and enforce branch protection in `docs/GOVERNANCE.md`.
- [x] **P5-M2**: Establish open-source sustainability funding model in `docs/SUSTAINABILITY.md` and `.github/FUNDING.yml`.
- [x] **P5-M3**: Automated unprivileged systemd user backup units (`configs/systemd/arcanum-backup.{service,timer}`) with `--enable-timer` support.
- [x] **P5-M4**: Multi-distribution package specs for Arch Linux AUR (`pkg/arch/PKGBUILD`) and RPM (`pkg/rpm/ars-arcanum.spec`).
- [x] **P5-M5**: Automated governance and multi-distro test suite (`tests/test_governance_docs.py`, `tests/test_multi_distro_packaging.py`).

---

## Phase 6: Advanced Extensibility & Story Paradigm Expansion (Completed)
**Theme**: Zero-dependency plugin architecture, speculative fiction linters, and universal narrative models.
- [x] **P6-M1**: Zero-dependency Speculative Fiction & Worldbuilding Plugin Architecture (`scripts/lib/plugins.py`, `docs/PLUGINS.md`, CLI: `arcanum plugin <list|info|run|create|enable|disable>`).
- [x] **P6-M2**: Production reference plugins: `speculative_naming` (phoneme collision & consonant clustering auditor), `magic_system_audit` (Sandersonian hard magic constraint validator), and `pacing_heat_map` (dialogue density & sensory distribution analyzer).
- [x] **P6-M3**: Universal Multi-Paradigm Story Structure expansion in `scripts/lib/structure.py` with 9 canonical narrative models: Three-Act, Save the Cat, Hero's Journey, Story Circle, 7-Point, 8-Sequence Method (Gulino/Daniel), Fichtean Curve, Kishōtenketsu (起承転結), and Freytag's Pyramid.
- [x] **P6-M4**: Flatpak manifest validation and sandbox permission verification suite (`tests/test_flatpak_manifest.py`).
- [x] **P6-M5**: Comprehensive unit test suites (`tests/test_plugins_framework.py`, `tests/test_story_paradigms_expanded.py`) bringing total test suite to 357 passing tests with 0 failures and 0 Ruff violations.

---

## Phase 7: Interactive Story Canvas, Dual-Track Timeline & Series Omnibus (Completed)
**Theme**: Browser-based visual corkboard crafting, dual-track timeline synchronization, and series omnibus compilation.
- [x] **P7-M1**: Standalone interactive HTML5/SVG Visual Story Canvas & Corkboard with client-side drag-and-drop, live structural harmony recalculation, and chapter reordering manifest export (`scripts/lib/story_canvas.py`, `tests/test_story_canvas.py`).
- [x] **P7-M2**: Dual-Track Chronological vs. Narrative Timeline Synchronizer with flashback detection, concurrent scene identification, and bilocation paradox checking (`scripts/lib/timeline_sync.py`, `tests/test_timeline_sync.py`).
- [x] **P7-M3**: Multi-Volume Series Omnibus Compiler synthesizing cross-volume Dramatis Personae, master TOC partitions, series timeline appendices, and combined HTML reader (`scripts/lib/omnibus.py`, `tests/test_omnibus.py`).
- [x] **P7-M4**: Comprehensive Author Manual & Visual Canvas Guide published in `docs/CANVAS_GUIDE.md` and updated `docs/CHEATSHEET.md`.
- [x] **P7-M5**: Full test suite elevation to 366 passing tests (0 failures, 0 Ruff violations, clean mypy static typing).

---

## Phase 8: Flathub Upstream Delivery, EPUB 3 Media Overlays & Universal Corpus Exporter (Completed)
**Theme**: Upstream Flathub AppStream metadata, EPUB 3 SMIL synchronized audiobook authoring, and universal sovereign AI dataset extraction.
- [x] **P8-M1**: Flathub AppStream 0.16+ XML metainfo created at `flatpak/org.arsarcanum.ArsArcanum.metainfo.xml`, registered in `org.arsarcanum.ArsArcanum.yaml`, and verified via `tests/test_flathub_upstream.py`.
- [x] **P8-M2**: EPUB 3 SMIL Media Overlays synthesizer and offline synchronized WebAudio player created at `scripts/lib/media_overlay.py` with unit tests in `tests/test_media_overlay.py`.
- [x] **P8-M3**: Universal Structured Corpus & RAG Dataset Exporter created at `scripts/lib/corpus_export.py` supporting JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`), relational SQLite 3 (`corpus.db` with FTS5 full-text search), and markdown summary digests (`_corpus_summary.md`) with unit tests in `tests/test_corpus_export.py`.
- [x] **P8-M4**: CLI dispatcher updated in `scripts/lib/cli.py` routing `overlay`/`smil` and `corpus` commands.
- [x] **P8-M5**: Complete technical documentation published in `docs/CORPUS_EXPORT.md`, `docs/FLATHUB_PACKAGING.md`, and updated `docs/CHEATSHEET.md`.
- [x] **P8-M6**: Architectural records logged in `decisions.md` (`ADR-053`, `ADR-054`, `ADR-055`).
- [x] **P8-M7**: Test suite verified at 381 tests (379 passed, 2 skipped, 0 failures), 100% clean Ruff linter pass, strict mypy type clean.

---

## Phase 9: Sovereign Autonomous Editorial Council, Zen Drafting Studio & Agentic Project OS (Completed)
**Theme**: Autonomous multi-perspective editorial workshop, standalone offline Zen drafting studio, and sovereign agentic OS doctrine (v2.0.0 — The Sovereign Scriptorium Milestone).
- [x] **P9-M1**: Multi-Perspective Autonomous Editorial Council Engine created at `scripts/lib/editorial_council.py` (`arcanum council`) synthesizing Line, Lore, Story Architecture, and Continuity evaluations with unit tests in `tests/test_editorial_council.py`.
- [x] **P9-M2**: Standalone Offline Zen Drafting Studio & In-Situ Lore Inspector created at `scripts/lib/zen_studio.py` (`arcanum studio`) with unit tests in `tests/test_zen_studio.py`.
- [x] **P9-M3**: Sovereign Agentic Operating System Manifesto published in `AGENTS.md` and verified via `tests/test_agentic_doctrine.py`.
- [x] **P9-M4**: CLI dispatcher updated in `scripts/lib/cli.py` and `scripts/arcanum` to version 2.0.0, routing `council` and `studio` commands.
- [x] **P9-M5**: Technical documentation published in `docs/EDITORIAL_COUNCIL.md`, `docs/ZEN_STUDIO.md`, and updated `docs/CHEATSHEET.md`.
- [x] **P9-M6**: Architectural records logged in `decisions.md` (`ADR-056`, `ADR-057`, `ADR-058`).
- [x] **P9-M7**: Complete test suite elevation (388+ tests passing, 0 failures), 100% clean Ruff linter, strict mypy typing.

---

## Phase 10: Sovereign Local Semantic Retrieval, Plugin Marketplace & Intelligence (Completed)
**Theme**: Sovereign zero-dependency local semantic retrieval (RAG) & lore query engine, curated speculative fiction plugin marketplace, and release packaging (v2.1.0 — The Sovereign Intelligence Milestone).
- [x] **P10-M1**: Sovereign Zero-Dependency Local Semantic Retrieval Engine created at `scripts/lib/local_rag.py` (`arcanum rag`, `arcanum query-lore`) providing hybrid TF-IDF vector space model and SQLite FTS5 exact keyword retrieval with unit tests in `tests/test_local_rag.py`.
- [x] **P10-M2**: Speculative Fiction Plugin Marketplace and curated catalog created at `scripts/lib/plugin_market.py` (`arcanum market`) and `configs/plugin_catalog.json` featuring curated community craft plugins (`mythic_pantheon`, `linguistic_drift`, `trope_inversion`, `hard_sf_chronometry`, `grimdark_entropy`) with unit tests in `tests/test_plugin_market.py`.
- [x] **P10-M3**: Automated LLM Prompt Context Synthesizer formatting canonical lore context with source document and entity provenance attribution for local LLMs (Llama 3, Mistral, Gemma, Phi).
- [x] **P10-M4**: CLI routing registered in `scripts/lib/cli.py` and `scripts/arcanum` for `rag` and `market`, with version bumped to v2.1.0 across `debian/changelog` and `CHANGELOG.md`.
- [x] **P10-M5**: Comprehensive technical documentation published in `docs/LOCAL_RAG.md`, `docs/PLUGIN_MARKET.md`, and updated `docs/CHEATSHEET.md`.
- [x] **P10-M6**: Architectural records logged in `decisions.md` (`ADR-059`, `ADR-060`).
- [x] **P10-M7**: Full regression test suite elevated to **403 tests collected (401 passed, 2 skipped, 0 failures)**, 100% clean Ruff pass (0 violations), and clean mypy static type checking across all 73 source modules.

---

## Phase 11: Sovereign Local AI Fine-Tuning Studio & Interactive Branching Fiction Graph (Completed)
**Theme**: Private-canon local LLM fine-tuning dataset synthesis and multi-platform interactive branching narrative compilation (v2.2.0 — The Sovereign Synthesis Release).
- [x] **P11-M1**: Sovereign Local AI Fine-Tuning Dataset Synthesizer created at `scripts/lib/fine_tuning.py` (`arcanum train-data`, `arcanum lora-dataset`) generating `Alpaca`, `ShareGPT`, `ChatML`, and `Ollama Modelfile` datasets across four craft instruction domains with unit tests in `tests/test_fine_tuning.py`.
- [x] **P11-M2**: Interactive Branching Narrative Graph & Choice Engine created at `scripts/lib/branching_graph.py` (`arcanum branch`, `arcanum branching`) parsing `@choice:`, `@state:`, `@req:`, and `@ending:` tags with topological DAG reachability validation and unit tests in `tests/test_branching_graph.py`.
- [x] **P11-M3**: Multi-format interactive fiction compilation: standalone offline HTML5 gamebook reader with embedded SVG graph, Inkle Ink (`.ink`), Twine 2 (`.twee`), and Obsidian Mermaid flowchart.
- [x] **P11-M4**: CLI routing registered in `scripts/lib/cli.py` and `scripts/arcanum` for `train-data`/`lora-dataset` and `branch`/`branching`, with version bumped to v2.2.0.
- [x] **P11-M5**: Technical documentation published in `docs/FINE_TUNING.md`, `docs/BRANCHING_GRAPH.md`, and updated `docs/CHEATSHEET.md`.
- [x] **P11-M6**: Architectural records logged in `decisions.md` (`ADR-061`, `ADR-062`).
- [x] **P11-M7**: Full regression test suite elevated to **416 tests collected (414 passed, 2 skipped, 0 failures)**, 100% clean Ruff pass (0 violations), and clean mypy static type checking across 76 source modules.

---

## Phase 12: Sovereign Studio Desktop Hub, Grand Tour Lifecycle Verification & Offline Flatpak Runtime Bundle (Completed)
**Theme**: Unified offline telemetry cockpit aggregating all 40+ craft engines, definitive 13-stage end-to-end lifecycle test harness, and sovereign offline Flatpak bundle builder (v3.0.0 — The Sovereign Zenith Release).
- [x] **P12-M1**: Sovereign Studio Desktop Hub created at `scripts/lib/studio_hub.py` (`arcanum hub`, `arcanum dashboard`) with unified offline HTML5 telemetry cockpit, embedded REST API, static HTML export, JSON headless mode, and unit tests in `tests/test_studio_hub.py`.
- [x] **P12-M2**: Sovereign Offline Flatpak Bundle Builder created at `flatpak/build_offline_bundle.sh` with Python stdlib caching, AppStream validation, `--dry-run`, and `--verbose` flags with tests in `tests/test_flatpak_offline.py`.
- [x] **P12-M3**: Definitive 13-Stage Grand Tour End-to-End Lifecycle Test created at `tests/test_grand_tour_e2e.py` exercising all 40+ craft engines in a single ordered integration harness from Cosmos scaffolding through Studio Hub telemetry export.
- [x] **P12-M4**: CLI routing registered in `scripts/lib/cli.py` and `scripts/arcanum` for `hub`, `dashboard`, `gui-web`, `studio-hub`, with version elevated to v3.0.0.
- [x] **P12-M5**: Technical documentation published in `docs/STUDIO_HUB.md`, `docs/GRAND_TOUR.md`, and updated `docs/CHEATSHEET.md` with `arcanum hub` quick reference.
- [x] **P12-M6**: Architectural records logged in `decisions.md` (`ADR-063`, `ADR-064`).
- [x] **P12-M7**: Full regression test suite elevated to **439 tests collected (437 passed, 2 skipped, 0 failures)**, 100% clean Ruff pass (0 violations), and clean mypy static type checking across 76 source modules.

---

## Phase 13: The Sovereign Craft Deepening & Productivity Intelligence (Completed)
**Theme**: Writing sprint session analytics, revision churn density heatmap, verification of causality/prophecy/senses suites, thin-test expansion, and 15-stage Grand Tour elevation (v3.1.0 — The Sovereign Craft Deepening).
- [x] **P13-M1**: Sovereign Writing Sprint & Session Analytics engine created at `scripts/lib/writing_sprint.py` (`arcanum sprint`) with atomic sidecar state, WPM velocity metrics, daily streak tracking, and unit tests in `tests/test_writing_sprint.py`.
- [x] **P13-M2**: Manuscript Revision Density & Churn Heatmap engine created at `scripts/lib/revision_heatmap.py` (`arcanum revision-heatmap`) with snapshot line diffing, `REV-101`/`REV-102` detection, and unit tests in `tests/test_revision_heatmap.py`.
- [x] **P13-M3**: Comprehensive verification and documentation for Causal DAG & Time-Travel Consistency Validator (`scripts/lib/causality.py`, `arcanum causality`, `tests/test_causality.py`, `docs/CAUSALITY.md`).
- [x] **P13-M4**: Comprehensive verification and documentation for Prophecy Resolution Matrix (`scripts/lib/prophecy.py`, `arcanum prophecy`, `tests/test_prophecy.py`, `docs/PROPHECY.md`).
- [x] **P13-M5**: Comprehensive verification and documentation for 6D Sensory Palette & White Room Syndrome Linter (`scripts/lib/senses.py`, `arcanum senses`, `tests/test_senses.py`, `docs/SENSORY_PALETTE.md`).
- [x] **P13-M6**: Expanded craft test suites for planetary climate (`tests/test_climate.py`), food web ecology (`tests/test_ecology.py`), and earth idiom linters (`tests/test_idioms.py`) to 10 tests each; Grand Tour elevated to 15 stages (`tests/test_grand_tour_e2e.py`).
- [x] **P13-M7**: Full regression test suite elevated to **504 tests collected (502 passed, 2 skipped, 0 failures)**, 100% clean Ruff pass (0 violations), and clean mypy static type checking across 78 source modules; version bumped to v3.1.0.

