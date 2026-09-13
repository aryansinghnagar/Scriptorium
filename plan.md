# Implementation Plan & Operational Roadmap: Scriptorium

## 1. Architectural Overview
The Scriptorium environment is organized into modular tiers:
1. **Governance, Security Policy & Compatibility**: `SECURITY.md`, `docs/SUPPORT_MATRIX.md`, `docs/COMPATIBILITY.md`, `.editorconfig`, and immutable CI pinning.
2. **Automated Setup, Safety & Provisioning**: System installer (`setup_scriptorium.sh`) with `--dry-run` simulation, `/etc/os-release` distribution gating, and rollback uninstaller (`uninstall_scriptorium.sh`).
3. **Transactional World Provisioning & Assets**: Automated generator (`init_world.sh`) that stages in temporary space, validates directory schemas, writes valid novelWriter `fileVersion 1.5` XML (`nwProject.nwx`), and atomically moves to `~/Worlds/<WorldName>`.
4. **Obsidian World Bible Suite**: Production-grade Markdown templates with Dataview metadata and domain integrity checking (`world_doctor.sh`).
5. **novelWriter Manuscript Structure**: Pre-configured chapter/scene hierarchies with metadata tags, outline templates, and manuscript analytics (`wordcount_report.sh`).
6. **Book Export & Typesetting Engine**: Pandoc + Typst compilation pipeline (`export_book.sh`, `book_template.typ`, `export-book.desktop`) with independent error trapping, collision-safe naming, and artifact verification.
7. **Version History & Decoupled Data Protection**: One-click Git snapshotting (`save_snapshot.sh`) paired with decoupled standalone backup archives (`backup_world.sh`) and verified disaster recovery restores (`restore_world.sh`).
8. **Unified CLI & Desktop Control Center**: Unified `scriptorium` entrypoint CLI and `control_center.sh` / `.desktop` GUI dashboard.
9. **Multi-Tier Git & Narrative Universe Architecture**: 3-tier version control hierarchy (`~/Universes/<Name>/` -> `Worlds/<Name>/` -> `01-Manuscript/<Book>/`) with Universe manifests (`universe.yaml`) and discrete manuscript git repos.
10. **Pre-Configured Obsidian Worldbuilding & Drafting Suite**: Production-grade vault pre-configuration with Longform, Dataview, Metadata Menu (`fileClasses` schemas: Character, Location, Faction, TimelineEvent), Calendarium, Storyteller Suite, Storyline, Novel Word Count, and Obsidian Git (10-min interval auto-commits).
11. **Comprehensive 7-Stage Verification Harness**: `scripts/verify.sh` exercising syntax, schemas, transactional Universe & World init, exports, doctor diagnostics, wordcount reports, Git multi-tier snapshots, and backup/restore recovery drills.
12. **Unified GTK 3 Desktop Application & Author Field Manual**: Native Python 3/GTK 3 Control Center (`scripts/scriptorium_app.py`) with 5-tab author workflow, first-flight onboarding wizard, and comprehensive visual guide (`docs/AUTHOR_MANUAL.md`).

## 2. Milestone Execution Status
- [x] **M0: Governance & Architecture Freeze**: Security policy (`SECURITY.md`), OS matrix (`docs/SUPPORT_MATRIX.md`), compatibility baselines (`docs/COMPATIBILITY.md`), `.editorconfig`, CI 40-char SHA pinning (`ci.yml`), and README cleanup.
- [x] **M1: Execution Foundation & Safety**: Installer `--dry-run` simulation and OS gating (`setup_scriptorium.sh`), uninstaller (`uninstall_scriptorium.sh`), transactional staging (`init_world.sh`), and independent Pandoc error trapping (`export_book.sh`).
- [x] **M2: Data Protection & Supply Chain Hardening**: Standalone verified backups (`backup_world.sh`), verified restore engine (`restore_world.sh`), valid novelWriter XML (`templates/manuscript/nwProject.nwx`), and comprehensive test fixtures (`tests/fixtures/`).
- [x] **M3: Production Diagnostics & Domain Toolchain**: Unified Scriptorium Doctor (`scriptorium_doctor.sh`), enhanced World Doctor with timeline and entity validation (`world_doctor.sh`), and progress analytics (`wordcount_report.sh`).
- [x] **M4: Scriptorium Unified Authoring Platform**: Unified CLI entrypoint (`scripts/scriptorium`), desktop Control Center GUI (`control_center.sh`, `launchers/scriptorium-control-center.desktop`), and comprehensive 7-stage verification harness (`scripts/verify.sh`).
- [x] **M5: Narrative Universe Architecture & Out-of-the-Box Obsidian Suite**: Multi-tier Git architecture (`init_universe.sh`, `init_world.sh --universe`, `save_snapshot.sh`), pre-configured Obsidian worldbuilding & drafting suite (`.obsidian/` configs, `Templates/fileClasses/`, Dataview JS/DQL, Obsidian Git auto-commits), decluttered codebase, and ADR-013/ADR-014 documentation.
- [x] **M6: Multi-Volume Manuscript Compilation Isolation**: Volume discovery, explicit `-b, --book <Volume>` selector, interactive GUI volume picker, omnibus option, and volume-isolated output artifact stems (`export_book.sh`, `scriptorium export`, ADR-015).
- [x] **M7: Professional Literary Typography & Typesetting Engine**: Ornamental scene breaks mapping (`show line: it => scene-break()`), unindented opening paragraph helpers, epigraph support, and trade typography formatting (`book_template.typ`, `preview_sample.typ`).
- [x] **M8: Worldbuilding Taxonomy Expansion & Schema Enrichment**: Bestiary (`Bestiary/`, `fileClasses/Creature.md`), Artifacts/Relics (`Artifacts/`, `fileClasses/Artifact.md`), and Pantheons/Cosmology (`Cosmology/`, `fileClasses/Cosmology.md`) with Dataview dashboards and `world_doctor.sh` validation (ADR-016).
- [x] **M9: Git Concurrency Resilience & Universe Index Hub**: Transient `.git/index.lock` wait-and-retry handling in `save_snapshot.sh` and automated `Universe-Index.md` cosmos hub generation in `init_universe.sh`.
- [x] **M10: Architecture Documentation & Regression Suite**: Synchronized ADRs (ADR-001..ADR-016), updated charters, and 7-stage verification harness passing with `ALL-CHECKS-PASS`.
- [x] **M11: Unified GTK 3 Desktop Control Center & Author's Field Manual**: Native GTK 3 5-tab author dashboard (`scripts/scriptorium_app.py`), first-flight onboarding wizard with starter demo cosmos (*"The Chronicles of Eldoria"*), comprehensive 8-chapter Author's Field Manual (`docs/AUTHOR_MANUAL.md`), and ADR-017 documentation.


