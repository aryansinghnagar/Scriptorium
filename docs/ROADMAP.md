# Ars Arcanum Roadmap, Milestones & Operational Status

---

## 1. Project Charter & Executive Summary

Ars Arcanum is a purpose-built, distraction-free, low-effort writing and worldbuilding environment designed for authors, novelists, and worldbuilders running Linux (primarily Linux Mint XFCE edition or Debian 13/12 XFCE). It emphasizes open formats (plain Markdown), minimal system management overhead, ironclad data safety (full-disk encryption + 3-2-1 automated backups + verified restores), and publication-ready typesetting using modern tools (Typst, Pandoc, novelWriter, Obsidian, Calibre, FocusWriter).

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

## 4. Master Milestone Roadmap (M0–M19)

### M0: Governance & Architecture Freeze
- [x] Security vulnerability disclosure policy (`SECURITY.md`).
- [x] OS support matrix (`docs/SUPPORT_MATRIX.md`) and toolchain compatibility baselines (`docs/COMPATIBILITY.md`).
- [x] `.editorconfig` formatting standards and immutable 40-char SHA pinning in CI.

### M1: Execution Foundation & Safety
- [x] Installer `--dry-run` simulation and OS distribution gating (`scripts/setup_arcanum.sh`).
- [x] Automated rollback uninstaller (`scripts/uninstall_arcanum.sh`).
- [x] Transactional staging for world creation (`scripts/init_world.sh`).
- [x] Independent Pandoc error trapping and non-zero artifact verification (`scripts/export_book.sh`).

### M2: Data Protection & Supply Chain Hardening
- [x] Standalone verified backup tarballs with SHA-256 manifests (`scripts/backup_world.sh`).
- [x] Verified disaster recovery engine (`scripts/restore_world.sh`).
- [x] Valid novelWriter `fileVersion 1.5` XML schema (`templates/manuscript/nwProject.nwx`).
- [x] Modernized test fixtures (`tests/fixtures/`).

### M3: Production Diagnostics & Domain Toolchain
- [x] Unified Ars Arcanum Doctor diagnostics (`scripts/arcanum_doctor.sh`).
- [x] World Doctor with multi-era timeline and entity validation (`scripts/world_doctor.sh`).
- [x] Manuscript progress analytics and wordcount reporting (`scripts/wordcount_report.sh`).

### M4: Unified Authoring Platform & Verification Harness
- [x] Unified CLI entrypoint dispatcher (`scripts/arcanum` and alias `scripts/ars-arcanum`).
- [x] Desktop Control Center GUI (`scripts/control_center.sh`, `launchers/arcanum-control-center.desktop`).
- [x] Comprehensive 7-stage verification harness (`scripts/verify.sh`).

### M5: Narrative Universe Architecture & Out-of-the-Box Obsidian Suite
- [x] Multi-tier Git architecture (`init_universe.sh`, `init_world.sh --universe`, `save_snapshot.sh`).
- [x] Pre-configured Obsidian suite (`.obsidian/` configs, `Templates/fileClasses/`, Dataview JS/DQL, Obsidian Git 10-minute auto-commits).

### M6: Multi-Volume Manuscript Compilation Isolation
- [x] Volume discovery and explicit `-b, --book <Volume>` selector (`export_book.sh`, `arcanum export`).
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
- [x] Native Python 3 / PyGObject GTK 3 desktop dashboard (`scripts/arcanum_app.py`) with 5-tab author workflow.
- [x] First-Flight onboarding wizard with starter demo cosmos (*"The Chronicles of Eldoria"*).
- [x] Comprehensive 8-chapter Author's Field Manual (`docs/AUTHOR_MANUAL.md`).

### M12: Speculative Ontology Harmonization, Multi-Volume Engine & Publishing Polish
- [x] Harmonized frontmatter templates and `World-Bible-Index.md` with strict `fileClasses` schemas (`MagicSystem.md`, `Language.md`).
- [x] Multi-volume scaffolding (`scripts/add_book.sh`, `arcanum add-book`).
- [x] Paper trim size presets (`-s, --paper-size us-trade|trade|pocket`) and EPUB cover image auto-detection (`03-Art/cover.png`).

### M13: Automated Narrative Concordance, Multi-Era Chronology & Subplot Matrix
- [x] Automated Back-Matter Concordance & Dramatis Personae Engine (`scripts/generate_concordance.sh`, `arcanum concordance`).
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

### M16: Sovereign Privacy, Asset Provenance & Unified Rebranding
- [x] Full unified project rebranding to *Ars Arcanum* across CLI, scripts, desktop launchers, Debian packaging, and documentation.
- [x] Creation of `PRIVACY.md` detailing 100% offline local-first privacy, zero telemetry, and complete data sovereignty.
- [x] Cataloging all open-source & Creative Commons assets in `REFERENCES.md` with explicit creator attribution and zero-AI guarantee.

### M17: Intuitive Action-Oriented CLI & Fast Performance Cache
- [x] Action-first intuitive CLI design (`arcanum write`, `arcanum new`, `arcanum draft`, `arcanum save`, `arcanum publish`, `arcanum words`, `arcanum check`).
- [x] High-throughput mtime-keyed caching engine (`scripts/lib/cache.py`, `arcanum cache`) for sub-second wordcount and vault diagnostics.
- [x] Offline local-first semantic continuity analyzer (`scripts/lib/continuity.py`, `arcanum continuity`) for character trait and physical contradiction detection.

### M18: Multi-Draft Management, Visual Redline Comparator & Dual-Target Secure Backups
- [x] Discrete multi-draft versioning (`scripts/init_draft.sh`, `arcanum draft <ms> [draft_name]`) with automated Git milestone tagging.
- [x] Accessible, WCAG-compliant visual redline diffing (`scripts/lib/manuscript_diff.py`, `scripts/compare_drafts.sh`, `arcanum compare`) with soft pastel highlight palette, collapsible chapter sidebars, word delta pills, terminal changelog mode, and LibreOffice Writer bridge.
- [x] Dual-target backup replication to secondary external/USB locations with SHA-256 verification (`scripts/lib/config.py`, `scripts/backup_world.sh`, `arcanum backup-dest`).
- [x] Integration of draft revisions, visual comparator, and secure backup picker into GTK 3 desktop UI.

### M19: Standard DOCX Integration, Bidirectional Word Processor Sync & Formatting Presets
- [x] Zero-dependency OpenXML engine (`scripts/lib/docx_sync.py`) generating native `.docx` files compatible with Microsoft Word (365 / Desktop), Google Docs, and LibreOffice Writer.
- [x] Dual-synchronized manuscript model: auto-generates consolidated draft documents (`Draft-01_Manuscript.docx`) and chapter files (`01_Chapter.docx`) on manuscript scaffolding and draft forking.
- [x] Distraction-free prose generation with scene tag scrubbing (`@pov:`, `@location:`, etc.) and safe metadata restoration during bidirectional sync.
- [x] Configurable global typography presets (`Standard Submission` / Shunn, `Modern Manuscript`, `Classic Trade`, `Custom`) in `scripts/lib/config.py` and GTK modal dialog.
- [x] CLI and GUI integration (`arcanum docx <build|sync|import|open>`, `arcanum word`, Control Center Tab 2 toolbar).
- [x] Automated unit and end-to-end regression tests (`tests/test_docx_sync.py`, `tests/test_docx_sync.sh`, `scripts/verify.sh`).

### M20: Speculative Fiction Authorial Workflow Suites (Waves 1–6)
- [x] **Wave 1: Astrophysics & Relativistic Spaceflight** (`scripts/lib/astrophysics.py`, `arcanum calc transit|time-dilation|orbit|comms|habitability`): Brachistochrone 1g constant-acceleration trajectory calculator ($\tau$ proper vs $t$ coordinate time, peak $v/c$, Lorentz $\gamma$, fuel mass ratio), Hohmann orbital transfers, comms latencies, habitability & gravity, standalone HTML flight report.
- [x] **Wave 2: Hard Magic Systems & Arcane Constraint Matrix** (`scripts/lib/magic_system.py`, `arcanum magic-check|magic-report|magic`): Sanderson-style arcane rules, character tier limit checks (`MAG-101`), catalyst/reagent validation (`MAG-102`), hard limitation enforcement (`MAG-103`), cumulative fatigue tracking (`MAG-104`), HTML audit report.
- [x] **Wave 3: Dynastic Genealogies & Succession Lineage Graphs** (`scripts/lib/genealogy.py`, `arcanum genealogy|lineage`): Family tree Directed Acyclic Graph (DAG) parser, chronological/biological paradox detection (`GEN-101`), succession claim conflict validation (`GEN-102`), Mermaid.js flowchart markdown, interactive HTML tree visualizer.
- [x] **Wave 4: Conlang Phonotactics, Lexicography & Sound-Change Applier** (`scripts/lib/conlang.py`, `arcanum conlang generate|mutate|lexicon`): Syllable template phonotactic word/name generator, cluster blacklist filter, historical sound law mutation engine (`p > f / V_V`, `k > ch / _[e,i]`), lexicon dictionary parser & multi-format exporter (Markdown, CSV, JSON).
- [x] **Wave 5: Narrative Pacing, POV Balance & Tension Arc Analytics** (`scripts/lib/pacing.py`, `arcanum pace`, `arcanum tension`, `arcanum words --pov`): Prose mode classification (dialogue/action/exposition), sentence rhythm and variance metrics, POV screen-time balance & starvation alerts, tension arc modeling (0–100), embedded SVG chart visualizer.
- [x] **Wave 6: Overland/Naval Journey Modeler & Custom Planetary Calendars** (`scripts/lib/journey.py`, `scripts/lib/calendar.py`, `arcanum journey`, `arcanum calendar`): 14 terrain friction coefficients, 8 travel modes, ration/water burn rates, day-by-day itineraries, custom planetary calendar arithmetic, multi-moon synodic phase cycles, syzygies, and eclipses.
- [x] Full GTK 3 Control Center GUI integration in Tab 1 and Tab 2 (`scripts/lib/ui_gtk3.py`).
- [x] 100% standard library implementation with zero external pip dependencies and 100% offline privacy.
- [x] Comprehensive test suites (48 unit tests across `tests/test_*.py` + end-to-end CLI tests 26–31 in `tests/test_audit_fixes.sh`).

### M21: Speculative Fiction Authorial Workflow Suites (Waves 7–12 / Phase 2)
- [x] **Wave 7: Geopolitical Faction Matrix & Campaign Logistics** (`scripts/lib/factions.py`, `arcanum faction`, `arcanum calc battle`, `arcanum calc logistics`): Diplomatic alliance/rivalry paradox detection (`FAC-101` to `FAC-104`), Lanchester power-law combat calculator (square and linear laws, wall fortification multipliers), military campaign supply train and wagon radius calculator, Mermaid/HTML visualizers.
- [x] **Wave 8: In-World Economy, Commodity PPP & Tech Era Anachronisms** (`scripts/lib/economy.py`, `arcanum economy`, `arcanum audit tech`, `arcanum calc trade`): Multi-currency commodity basket Purchasing Power Parity (PPP), manuscript price outlier audit (`ECO-101`/`ECO-102`), historical technological era anachronism audit (`ECO-201`), trade route freight and tariff margin calculator.
- [x] **Wave 9: Causal DAGs, Time Travel Loops & Multiverse Branching** (`scripts/lib/causality.py`, `arcanum causality`, `arcanum causality branch`): Event causal graph extractor, cycle/paradox detection for grandfather (`CAU-101`) and bootstrap (`CAU-102`) paradoxes, Novikov self-consistency, multiverse timeline branch coordinate generator, Mermaid DAG exporter.
- [x] **Wave 10: Planetary Climate, Orographic Biomes & Trophic Food-Webs** (`scripts/lib/climate.py`, `scripts/lib/ecology.py`, `arcanum calc climate`, `arcanum ecology`): Stellar insolation ($W/m^2$), equilibrium temperature and habitability, atmospheric circulation cell derived Coriolis, adiabatic orographic rain shadow and leeward desert modeler, Bestiary trophic profiler, and Lindeman 10% energy pyramid validator (`ECO-301` to `ECO-304`).
- [x] **Wave 11: Earth-Eponym Scanner, Idiom De-Immersion & 6D Sensory Palette** (`scripts/lib/idioms.py`, `scripts/lib/senses.py`, `arcanum audit idioms`, `arcanum audit senses`): Earth-eponym scanner (`IDM-101` to `IDM-103`), 6-dimensional sensory distribution analyzer (visual, auditory, olfactory, gustatory, tactile/thermal, kinesthetic/vestibular), White Room syndrome (`SNS-101`), sensory monotony alerts (`SNS-102`).
- [x] **Wave 12: Inscriptions, In-World Ciphers & Prophecy Resolution** (`scripts/lib/cipher.py`, `scripts/lib/prophecy.py`, `arcanum cipher`, `arcanum prophecy`): Historical ciphers (Caesar, Atbash, Vigenère, Rail Fence, Columnar), Elder Futhark / Anglo-Saxon Futhorc phonetic rune translation, standalone vector SVG inscription cards, prophecy clause resolution lifecycle tracking (`PRP-101` to `PRP-103`).
- [x] Complete test suites across 20 test modules (131 unit tests across `tests/test_*.py` + 37 end-to-end integration tests in `tests/test_audit_fixes.sh`).

---

## 5. Real-Time Operational Status & Momentum Queues

### Operational State
- **Active Status**: Production-Ready / All 21 Milestones Complete & Verified (Grade A).
- **Verification**: 100% Pass Rate across all test harnesses (`scripts/verify.sh`, `tests/test_audit_fixes.sh`, `tests/test_deep_audit.sh`, `tests/test_concordance_edge_cases.sh`, `tests/test_audit_claude_improvements.sh`, `tests/test_performance_cache.sh`, `tests/test_continuity_engine.sh`, `tests/test_drafts_and_diff.py`, `tests/test_drafts_and_diff.sh`, `tests/test_docx_sync.py`, `tests/test_docx_sync.sh`, `tests/test_astrophysics.py`, `tests/test_magic_system.py`, `tests/test_genealogy.py`, `tests/test_conlang.py`, `tests/test_pacing.py`, `tests/test_journey.py`, `tests/test_calendar.py`, `tests/test_factions.py`, `tests/test_economy.py`, `tests/test_causality.py`, `tests/test_climate.py`, `tests/test_ecology.py`, `tests/test_idioms.py`, `tests/test_senses.py`, `tests/test_cipher.py`, `tests/test_prophecy.py`).
- **Code Quality**: Zero ShellCheck warnings, zero Python syntax errors, valid XML/JSON schemas, pre-compiled regex performance optimizations.

### Momentum Queues

#### `now` (Immediate Focus)
- [x] Modernize and synchronize all repository documentation, C4 architecture diagrams, and complete ADR-001 through ADR-028 catalog.
- [x] Pass all automated test suites and quality gates.

#### `next` (Ready to Execute)
- [ ] Build and verify native `.deb` package and Flatpak manifest (`org.arsarcanum.ArsArcanum.yaml`).
- [ ] Physical machine deployment and first-flight testing on Linux Mint 22 (XFCE) / Debian 13 (XFCE).

#### `improve` (Post-GA Enhancements)
- [ ] Port Desktop Control Center to GTK 4 / Libadwaita.
- [ ] Add EPUB visual preview bridge in GTK 3 Control Center.

#### `recurring` (Continuous Health)
- [ ] Run `bash scripts/verify.sh` on every change and pull request.
- [ ] Maintain ShellCheck zero-warning policy across scripts.

---

## 6. Definition of Done

- `bash scripts/verify.sh` prints `ALL-CHECKS-PASS` across all 7 verification stages.
- `python3 -m py_compile scripts/arcanum_app.py` compiles without syntax errors.
- `docs/AUTHOR_MANUAL.md` provides visual, plain-English guidance for all creative and technical workflows.
- `typst compile templates/typst/preview_sample.typ` produces a paginated PDF with clean front matter, ornamental scene breaks, and running headers.
- Test universes, pure world lore vaults, and standalone manuscripts scaffold, export (PDF, EPUB, DOCX), snapshot, and restore cleanly without data loss.
- Zero warnings under `shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/arcanum scripts/ars-arcanum`.
