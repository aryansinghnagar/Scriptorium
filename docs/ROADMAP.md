# Scriptorium Roadmap, Milestones & Operational Status

---

## 1. Project Charter & Executive Summary

Scriptorium is a purpose-built, distraction-free, low-effort writing and worldbuilding environment designed for authors, novelists, and worldbuilders running Linux (primarily Linux Mint XFCE edition or Debian 13/12 XFCE). It emphasizes open formats (plain Markdown), minimal system management overhead, ironclad data safety (full-disk encryption + 3-2-1 automated backups + verified restores), and publication-ready typesetting using modern tools (Typst, Pandoc, novelWriter, Obsidian, Calibre, FocusWriter).

---

## 2. Hardware & OS Baseline

- **Reference Platform**: Intel Core i5-1335U, 16 GB RAM, Iris Xe Graphics, NVMe SSD, dual-boot with Windows.
- **Primary Operating System**: Linux Mint (XFCE Edition, 64-bit, v21.x / v22.x).
- **Secondary / Minimal Alternative**: Debian 13 (Trixie) / 12 (Bookworm) XFCE.
- **Supported Architecture**: `x86_64` (Tier 1) and `aarch64` (Tier 2).

---

## 3. Non-Goals (Explicitly Out of Scope)

- No custom distribution or remastered ISO — stock Mint/Debian only.
- No per-app sandboxing profiles, Secure Boot key management, or USB device policies — LUKS + backups are the safety story.
- No mandatory cloud sync or third-party locking service — local multi-tier Git + external-drive backups only.
- No mobile companion workflow.

---

## 4. Master Milestone Roadmap (M0–M15)

### M0: Governance & Architecture Freeze
- [x] Security vulnerability disclosure policy (`SECURITY.md`).
- [x] OS support matrix (`docs/SUPPORT_MATRIX.md`) and toolchain compatibility baselines (`docs/COMPATIBILITY.md`).
- [x] `.editorconfig` formatting standards and immutable 40-char SHA pinning in CI.

### M1: Execution Foundation & Safety
- [x] Installer `--dry-run` simulation and OS distribution gating (`scripts/setup_scriptorium.sh`).
- [x] Automated rollback uninstaller (`scripts/uninstall_scriptorium.sh`).
- [x] Transactional staging for world creation (`scripts/init_world.sh`).
- [x] Independent Pandoc error trapping and non-zero artifact verification (`scripts/export_book.sh`).

### M2: Data Protection & Supply Chain Hardening
- [x] Standalone verified backup tarballs with SHA-256 manifests (`scripts/backup_world.sh`).
- [x] Verified disaster recovery engine (`scripts/restore_world.sh`).
- [x] Valid novelWriter `fileVersion 1.5` XML schema (`templates/manuscript/nwProject.nwx`).
- [x] Modernized test fixtures (`tests/fixtures/`).

### M3: Production Diagnostics & Domain Toolchain
- [x] Unified Scriptorium Doctor diagnostics (`scripts/scriptorium_doctor.sh`).
- [x] World Doctor with multi-era timeline and entity validation (`scripts/world_doctor.sh`).
- [x] Manuscript progress analytics and wordcount reporting (`scripts/wordcount_report.sh`).

### M4: Unified Authoring Platform & Verification Harness
- [x] Unified CLI entrypoint dispatcher (`scripts/scriptorium`).
- [x] Desktop Control Center GUI (`scripts/control_center.sh`, `launchers/scriptorium-control-center.desktop`).
- [x] Comprehensive 7-stage verification harness (`scripts/verify.sh`).

### M5: Narrative Universe Architecture & Out-of-the-Box Obsidian Suite
- [x] Multi-tier Git architecture (`init_universe.sh`, `init_world.sh --universe`, `save_snapshot.sh`).
- [x] Pre-configured Obsidian suite (`.obsidian/` configs, `Templates/fileClasses/`, Dataview JS/DQL, Obsidian Git 10-minute auto-commits).

### M6: Multi-Volume Manuscript Compilation Isolation
- [x] Volume discovery and explicit `-b, --book <Volume>` selector (`export_book.sh`, `scriptorium export`).
- [x] Interactive GUI volume picker and omnibus export support.

### M7: Professional Literary Typography & Typesetting Engine
- [x] Ornamental scene breaks mapping (`show line: it => scene-break()`), unindented opening paragraph helpers, epigraph support (`templates/typst/book_template.typ`).
- [x] Trade typography formatting and preview compilation.

### M8: Worldbuilding Taxonomy Expansion & Schema Enrichment
- [x] Bestiary taxonomy (`Bestiary/`, `fileClasses/Creature.md`).
- [x] Artifacts & Relics taxonomy (`Artifacts/`, `fileClasses/Artifact.md`).
- [x] Pantheons & Cosmology taxonomy (`Cosmology/`, `fileClasses/Cosmology.md`).
- [x] Dynamic Dataview tables in `World-Bible-Index.md` and `world_doctor.sh` validation.

### M9: Git Concurrency Resilience & Universe Index Hub
- [x] Transient `.git/index.lock` wait-and-retry handling in `save_snapshot.sh`.
- [x] Automated `Universe-Index.md` cosmos hub generation in `init_universe.sh`.

### M10: Architecture Documentation & Regression Suite
- [x] Synchronized ADRs (ADR-001 through ADR-023 in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)).
- [x] 7-stage verification harness passing with `ALL-CHECKS-PASS`.

### M11: Unified GTK 3 Desktop Control Center & Author's Field Manual
- [x] Native Python 3 / PyGObject GTK 3 desktop dashboard (`scripts/scriptorium_app.py`) with 5-tab author workflow.
- [x] First-Flight onboarding wizard with starter demo cosmos (*"The Chronicles of Eldoria"*).
- [x] Comprehensive 8-chapter Author's Field Manual (`docs/AUTHOR_MANUAL.md`).

### M12: Speculative Ontology Harmonization, Multi-Volume Engine & Publishing Polish
- [x] Harmonized frontmatter templates and `World-Bible-Index.md` with strict `fileClasses` schemas (`MagicSystem.md`, `Language.md`).
- [x] Multi-volume scaffolding (`scripts/add_book.sh`, `scriptorium add-book`).
- [x] Paper trim size presets (`-s, --paper-size us-trade|trade|pocket`) and EPUB cover image auto-detection (`03-Art/cover.png`).

### M13: Automated Narrative Concordance, Multi-Era Chronology & Subplot Matrix
- [x] Automated Back-Matter Concordance & Dramatis Personae Engine (`scripts/generate_concordance.sh`, `scriptorium concordance`).
- [x] Multi-era chronological timeline parsing in `world_doctor.sh` (`WLD-104`).
- [x] Subplot & Narrative Thread Pacing Matrix (`templates/manuscript/Outlines/Subplot-Thread-Matrix.md`) with `@thread:` tags.

### M14: Claude Audit Remediation & Publishing Bridge
- [x] Shared world discovery library (`scripts/lib/worlds.sh`).
- [x] Flathub ID corrections, fail-closed verification, and traversal hardening in `restore_world.sh`.
- [x] Standard Manuscript Submission Format (`.docx`) export.
- [x] Lore-to-manuscript cross-reference diagnostics (`WLD-108`).

### M15: Standardized Integrated Environment & Separated Architecture (Wave 2)
- [x] Separated Pure World Lore Vaults (`~/Universes/<Universe>/<World>`) and Standalone Prose Manuscript Projects (`~/Manuscripts/<Manuscript>`).
- [x] Standardized `@location:` tagging protocol (deprecating `@focus:`).
- [x] Visual Scene Metadata Inspector in GTK Control Center Tab 2 for in-place tag inspection and editing.
- [x] Dedicated `init_manuscript.sh` with `manuscript.yaml` manifest.
- [x] Centralized guides in `docs/guides/` and consolidated architecture docs in `docs/ARCHITECTURE.md` and `docs/ROADMAP.md`.

---

## 5. Real-Time Operational Status & Momentum Queues

### Operational State
- **Active Status**: Production-Ready / All 15 Milestones Complete & Verified (Grade A).
- **Verification**: 100% Pass Rate across all 5 test harnesses (`scripts/verify.sh`, `tests/test_audit_fixes.sh`, `tests/test_deep_audit.sh`, `tests/test_concordance_edge_cases.sh`, `tests/test_audit_claude_improvements.sh`).
- **Code Quality**: Zero ShellCheck warnings, zero Python syntax errors, valid XML/JSON schemas.

### Momentum Queues

#### `now` (Immediate Focus)
- [x] Modernize and synchronize all repository documentation, C4 architecture diagrams, and complete ADR-001 through ADR-023 catalog.
- [x] Pass all automated test suites and quality gates.

#### `next` (Ready to Execute)
- [ ] Implement native `.deb` and Flatpak packaging.
- [ ] Physical machine deployment and first-flight testing on Linux Mint 22 (XFCE) / Debian 13 (XFCE).

#### `improve` (Post-GA Enhancements)
- [ ] Implement mtime-based live wordcount caching in `scripts/scriptorium_app.py` for massive omnibus manuscripts.
- [ ] Add optional local semantic continuity checking.
- [ ] Port Desktop Control Center to GTK 4 / Libadwaita.

#### `recurring` (Continuous Health)
- [ ] Run `bash scripts/verify.sh` on every change and pull request.
- [ ] Maintain ShellCheck zero-warning policy across scripts.

---

## 6. Definition of Done

- `bash scripts/verify.sh` prints `ALL-CHECKS-PASS` across all 7 verification stages.
- `python3 -m py_compile scripts/scriptorium_app.py` compiles without syntax errors.
- `docs/AUTHOR_MANUAL.md` provides visual, plain-English guidance for all creative and technical workflows.
- `typst compile templates/typst/preview_sample.typ` produces a paginated PDF with clean front matter, ornamental scene breaks, and running headers.
- Test universes, pure world lore vaults, and standalone manuscripts scaffold, export (PDF, EPUB, DOCX), snapshot, and restore cleanly without data loss.
- Zero warnings under `shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/scriptorium`.
