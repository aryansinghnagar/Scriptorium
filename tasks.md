# Ars Arcanum (Scriptorium) — Momentum Queues & Task Backlog

## Live Momentum Queues

### `now` (Current Execution Focus)
- [x] Complete Phase 0 (Triage & Quick Wins - 8/8).
- [x] Complete Phase 1 (Unblock 1.0 Publication - 8/8).
- [x] Complete Phase 2 (Architectural Refactor - 7/7).
- [x] Complete Phase 3 (Quality Tooling & Security Hardening - 7/7).
- [x] Complete Phase 4 (Ecosystem & Author Polish / Publication - 5/5).
- [x] Complete Phase 5 (Sustainability, Multi-Distro & Systemd Timers - 5/5).
- [x] Complete Phase 6 (Extensibility Plugin Architecture & Expanded Story Paradigms - 5/5).
- [x] Complete Phase 7 (Interactive Story Canvas, Dual-Track Timeline & Series Omnibus - 5/5).
- [x] Complete Phase 8 (Flathub Upstream Delivery, EPUB 3 Media Overlays & Universal Corpus Exporter - 7/7).
- [x] Complete Phase 9 (Sovereign Autonomous Editorial Council, Zen Drafting Studio & Agentic Project OS - 7/7).
- [x] Complete Phase 10 (Sovereign Local Semantic Retrieval Engine, Speculative Plugin Marketplace & Intelligence - 7/7).
- [x] Complete Phase 11 (Sovereign Local AI Fine-Tuning Studio & Interactive Branching Fiction Graph - 7/7).
- [x] Complete Phase 12 (Sovereign Studio Desktop Hub, Grand Tour Lifecycle Verification & Offline Flatpak Runtime - 7/7).
- [x] Complete Phase 13 (The Sovereign Craft Deepening & Productivity Intelligence - 7/7).
- [x] Achieve Sovereign OS Grade A+ Release Readiness across 504 tests (502 passed, 2 skipped, 0 failures) — v3.1.0 The Sovereign Craft Deepening.

### `next` (Post-3.1.0 Ecosystem & Community Growth)
1. **Flathub Submission**: Submit finalized Flathub pull request with `flatpak/build_offline_bundle.sh` offline bundle.
2. **Community Plugin Submissions**: Accept third-party speculative fiction plugins into the verified catalog.
3. **Local LLM Fine-Tuning Pipeline**: Automated LoRA dataset formatting from exported SQLite/JSONL corpus.

### `blocked`
- *None.* All 13 modernization, extensibility, craft, and sovereign AI phases complete with 100% test pass rate across 504 tests (502 passed, 2 skipped, 0 failures). v3.1.0 released.

### `improve` (Evaluation & Quality Backlog)
- [x] Add `mypy` type checking in CI and local test suite (`tests/test_type_safety.py`).
- [x] Add coverage floor at 80% in `pyproject.toml` and `tests/test_coverage_floor.py`.
- [x] Ruff expanded rules (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`) with 100% clean pass.
- [x] Path traversal defense with volume sanitization (`tests/test_path_traversal_defense.py`).
- [x] Optional GPG-encrypted backup and restore (`tests/test_backup_encryption.py`).
- [x] Multi-platform release packaging engine (`tests/test_package_distribution.py`).
- [x] Shell script static syntax verification (`tests/test_shell_scripts_syntax.py`).
- [x] Comprehensive author field manual & cheatsheet (`docs/CHEATSHEET.md`).
- [x] Open-source governance charter & funding model (`docs/GOVERNANCE.md`, `docs/SUSTAINABILITY.md`).
- [x] Multi-distribution package management (Debian, Fedora, Arch AUR, openSUSE).
- [x] Automated systemd user backup timer (`configs/systemd/arcanum-backup.timer`).

### `recurring` (Automated Sweeps & Invariants)
- **CI Supply-Chain Sweep**: Daily verification of all 10 Obsidian plugin digests via `tests/test_supply_chain.py`.
- **Version Parity Check**: Verification of release version synchronization across all surfaces via `tests/test_version_consistency.py`.
- **Contrast Regression Gate**: Automated WCAG AA ratio calculation via `tests/test_wcag_contrast.py`.
- **Demo Cosmos Health Check**: Verification that demo cosmos passes doctor with 0 issues via `tests/test_demo_cosmos.py`.
- **Shell Syntax Gate**: Static `bash -n` verification of all 27 `.sh` scripts via `tests/test_shell_scripts_syntax.py`.
- **Packaging Integrity Gate**: Automated check of Arch PKGBUILD, RPM spec, and systemd units via `tests/test_multi_distro_packaging.py`.
