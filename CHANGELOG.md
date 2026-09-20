# Changelog

All notable changes to Ars Arcanum are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Scope decisions
behind each wave are recorded in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## [Unreleased]

## [1.6.0] - 2026-09-20

### Added (Authorial Craft, Plot Matrix, Publishing Pre-Flight, Cartography & Audio Suites — M22–M28)
- **Milestone M22: Editorial Craft & Prose Stylistics (`scripts/lib/stylistics.py`, `scripts/lib/voice.py`, `scripts/lib/typography_cleaner.py`)**:
  - Implemented dialogue mechanics linter detecting said-bookisms (`DIA-101`), floating dialogue without physical beats (`DIA-102`), and adverb overload (`DIA-103`).
  - Added sliding-window word echo and proximity repetition scanner (`ECH-101`).
  - Added character voice lexical profiler computing Flesch-Kincaid / Coleman-Liau grade levels, sentence length variance, syllable complexity, and voice homogeneity alerts (`VOI-101`/`VOI-102`).
  - Added smart typography normalizer for curly quotes, en/em-dashes, ellipses, and locale-aware non-breaking spaces (`TYP-101` to `TYP-104`).
  - CLI subcommands: `arcanum audit dialogue`, `arcanum audit echoes`, `arcanum audit voice`, `arcanum polish typography`.
- **Milestone M23: Narrative Architecture, Plot Matrix & Scene Ergonomics (`scripts/lib/plot_matrix.py`, `scripts/lib/structure.py`, `scripts/lib/scene_mechanics.py`, `scripts/lib/ambient.py`)**:
  - Implemented 2D interactive multi-track plot matrix mapping `@thread:` subplots across chapters and acts with standalone HTML export.
  - Implemented story paradigm structure enforcer validating pacing against Save the Cat, Hero's Journey, 7-Point Structure, Story Circle, Kishōtenketsu, and 3-Act 9-Block (`STR-101` to `STR-103`).
  - Implemented scene mechanics linter for Goal-Conflict-Disaster / Motivation-Reaction Units (`SCN-101` to `SCN-103`).
  - Implemented procedural ambient audio generator for distraction-free focus (Rain, Crackling Hearth, Library Hum, Cosmic Drone, Clockwork) with HTML5 WebAudio player and offline WAV generator.
  - CLI subcommands: `arcanum plot`, `arcanum audit structure`, `arcanum audit scenes`, `arcanum ambient`.
- **Milestone M24: Pre-Flight Typesetting & Publishing Compliance (`scripts/lib/preflight.py`, `scripts/lib/barcode.py`, `scripts/lib/frontmatter_builder.py`, `scripts/init_query.py`)**:
  - Implemented print PDF and EPUB pre-flight compliance linter for trim size, gutter ratios, straight quote detection, cover art, and metadata (`PRF-101` to `PRF-105`).
  - Implemented pure vector SVG and high-resolution PNG ISBN-13/EAN-13 barcode generator with 5-digit price extensions.
  - Implemented front and back matter builder generating standardized Copyright pages, Dedications, Epigraphs, Also-by-Author catalogs, and Reader Magnet CTAs.
  - Implemented publishing query submission packager scaffolding 1-Page Synopsis, 3-Paragraph Query Letter, 250-Word Elevator Pitch, and Logline.
  - CLI subcommands: `arcanum preflight`, `arcanum barcode`, `arcanum frontmatter`, `arcanum query`.
- **Milestone M25: Interactive Cartography, Codex Wiki & Series Continuity (`scripts/lib/cartography.py`, `scripts/lib/codex_export.py`, `scripts/lib/series_continuity.py`, `scripts/lib/tactical_sim.py`)**:
  - Implemented offline interactive vector cartography with lore pin layers, distance measurement, and direct calculation piping into `journey.py`.
  - Implemented static world lore wiki & reader codex exporter compiling Markdown vaults into searchable offline HTML static wikis with spoiler filters.
  - Implemented cross-book series continuity validator tracking character traits, item lineages, and mortality invariants across multi-volume series (`SER-101` to `SER-104`).
  - Implemented dynamic tactical combat simulator combining Lanchester combat laws, terrain modifiers, and arcane fatigue.
  - CLI subcommands: `arcanum map`, `arcanum codex`, `arcanum continuity --series`, `arcanum sim battle`.
- **Milestone M26: Distribution Packaging & Portfolio Dashboard (`scripts/package_distribution.py`, `scripts/lib/portfolio.py`)**:
  - Implemented direct-to-reader multi-platform distribution packager for Amazon KDP, IngramSpark, Apple Books, Kobo, and direct zip bundles with precise spine calculations.
  - Implemented executive author portfolio dashboard calculating wordcount velocity, drafting phase distributions, and publication readiness scores.
  - CLI subcommands: `arcanum package`, `arcanum portfolio`.
- **Milestone M27: Desktop UI 6-Studio Layout & Modernization (`scripts/lib/ui_gtk3.py`, `scripts/lib/ui_adw.py`)**:
  - Modernized GTK 3 desktop Control Center with 6 dedicated studios (Cosmos, Manuscripts, Speculative/Craft, Publishing, Safety, Doctor) and integrated tool dispatchers.
  - Enhanced GTK 4 / Libadwaita presentation layer with adaptive viewports, dark mode sync, and toast notifications.
- **Milestone M28: Sovereign Auditory Proofreading with Offline Neural TTS (`scripts/lib/tts_reader.py`)**:
  - Implemented local auditory proofreading player bridging Piper TTS / espeak-ng subprocesses with paragraph tracking and speed modulation (`0.75x` to `2.0x`).
  - CLI subcommand: `arcanum read [ms] [chapter]`.
- **Automated Test Coverage**:
  - Expanded Python unit test suite from 131 to 226 passing unit tests across 47 test modules.
  - Verified 100% pass rate in canonical 7-stage verification harness (`scripts/verify.sh`).
- **Wave 7: Geopolitical Faction Matrix & Campaign Logistics (`scripts/lib/factions.py`)**:
  - Implemented diplomatic relationship auditor and paradox detector (`FAC-101` to `FAC-104`).
  - Added Lanchester power-law combat casualty calculator supporting Square Law (ranged/aimed fire), Linear Law (unaimed/melee), fortification defense multipliers, and round-by-round force attrition curves.
  - Added campaign logistics modeler for infantry, cavalry, and camp followers, computing daily grain/water burn rates and wagon supply radii.
  - Added Obsidian Mermaid.js chord graphs and standalone interactive HTML network visualizer.
  - CLI subcommands: `arcanum faction [world]`, `arcanum calc battle`, `arcanum calc logistics`.
- **Wave 8: In-World Economy, Commodity PPP & Tech Era Anachronisms (`scripts/lib/economy.py`)**:
  - Implemented multi-currency Purchasing Power Parity (PPP) rate calculator using normalized commodity baskets.
  - Added manuscript price anomaly detector (`ECO-101`: extreme outlier $> 5\times$, `ECO-102`: unknown currency denomination).
  - Added historical technological era anachronism scanner (`ECO-201`) supporting 10 distinct technology tiers (`stone_age` through `space_age`).
  - Added trade route freight margin and tariff calculator.
  - CLI subcommands: `arcanum economy [world]`, `arcanum audit tech [ms]`, `arcanum calc trade`.
- **Wave 9: Causal DAGs, Time Travel Loops & Multiverse Branching (`scripts/lib/causality.py`)**:
  - Implemented causal event graph extractor and DFS cycle detector for grandfather (`CAU-101`) and bootstrap (`CAU-102`) paradoxes.
  - Added Novikov self-consistency validation (`CAU-103`) and orphan timeline divergence checks (`CAU-104`).
  - Added multiverse timeline branch coordinate generator and Obsidian Mermaid DAG exporter.
  - CLI subcommands: `arcanum causality [world] [ms]`, `arcanum causality branch <name>`.
- **Wave 10: Planetary Climate, Orographic Biomes & Trophic Food-Webs (`scripts/lib/climate.py`, `scripts/lib/ecology.py`)**:
  - Implemented planetary insolation ($W/m^2$), Stefan-Boltzmann equilibrium temperature, greenhouse warming offsets, and liquid-water habitable zone bounds.
  - Implemented Coriolis atmospheric circulation cell count derivation (Hadley, Ferrel, Polar).
  - Implemented adiabatic lapse rate orographic rain shadow and leeward desert simulation.
  - Implemented Bestiary trophic level profiler (1: Producers, 2: Herbivores, 3: Carnivores, 4: Apex Predators) with Lindeman 10% energy pyramid validation (`ECO-301` to `ECO-304`).
  - CLI subcommands: `arcanum calc climate`, `arcanum ecology [world]`.
- **Wave 11: Earth-Eponym Scanner, Idiom De-Immersion & 6D Sensory Palette (`scripts/lib/idioms.py`, `scripts/lib/senses.py`)**:
  - Implemented Earth-eponym and myth/cliché scanner (`configs/idioms.json`) detecting immersion leaks (`IDM-101` to `IDM-103`).
  - Implemented 6-dimensional sensory distribution analyzer (Visual, Auditory, Olfactory, Gustatory, Tactile/Thermal, Kinesthetic/Vestibular).
  - Added White Room syndrome (`SNS-101`) and sensory monotony (`SNS-102`) scene diagnostics.
  - CLI subcommands: `arcanum audit idioms [ms]`, `arcanum audit senses [ms]`.
- **Wave 12: Inscriptions, In-World Ciphers & Prophecy Resolution (`scripts/lib/cipher.py`, `scripts/lib/prophecy.py`)**:
  - Implemented classical ciphers (Caesar, Atbash, Vigenère, Rail Fence, Columnar) with encode/decode pipelines.
  - Implemented phonetic Elder Futhark and Anglo-Saxon Futhorc rune transliterator with standalone vector SVG inscription card generator.
  - Implemented prophecy resolution matrix tracking oracle clauses against scene annotations (`PRP-101` to `PRP-103`).
  - CLI subcommands: `arcanum cipher encode|decode|runes`, `arcanum prophecy [world] [ms]`.
- **Templates & FileClasses Enrichment**:
  - Created `Economies/Economy-Template.md`, `Cosmology/Prophecy-Template.md`.
  - Created Metadata Menu schemas `fileClasses/Economy.md`, `fileClasses/Prophecy.md`.
  - Upgraded `fileClasses/Faction.md` and `fileClasses/Creature.md` with trophic and alliance fields.
- **Automated Test Coverage**:
  - Added 44 unit tests across `tests/test_factions.py`, `tests/test_economy.py`, `tests/test_causality.py`, `tests/test_climate.py`, `tests/test_ecology.py`, `tests/test_idioms.py`, `tests/test_senses.py`, `tests/test_cipher.py`, `tests/test_prophecy.py` (131 total unit tests).
  - Added integration tests 32–37 in `tests/test_audit_fixes.sh` (37 total integration tests passing).

### Added (Speculative Fiction Authorial Workflow Suites — Waves 1–6)
- **Wave 1: Astrophysics & Relativistic Spaceflight (`scripts/lib/astrophysics.py`)**:
  - Implemented exact relativistic Brachistochrone 1g constant-acceleration trajectory calculator ($\tau$ proper vs $t$ coordinate time, peak $v/c$, Lorentz factor $\gamma$, fuel mass ratios via relativistic Tsiolkovsky equations).
  - Added Hohmann orbital transfer calculations, interplanetary communication latencies (one-way/round-trip), stellar habitability zones, and surface gravity calculations.
  - Added interactive visual HTML flight profile report export with embedded SVG velocity curves.
  - CLI subcommands: `arcanum calc transit`, `arcanum calc time-dilation`, `arcanum calc orbit`, `arcanum calc comms`, `arcanum calc habitability`.
- **Wave 2: Hard Magic Systems & Arcane Constraint Matrix (`scripts/lib/magic_system.py`)**:
  - Implemented Sanderson-style hard magic validation against scene metadata and lore dossiers.
  - Diagnostic rules: `MAG-101` (Character Affinity Tier Limits), `MAG-102` (Missing Catalyst/Reagents), `MAG-103` (Hard Limitations Enforcement), `MAG-104` (Fatigue & Arcane Exhaustion Accumulation).
  - CLI subcommands: `arcanum magic-check -w <world> -m <ms>`, `arcanum magic-report`, `arcanum magic`.
- **Wave 3: Dynastic Genealogies & Succession Lineage Graphs (`scripts/lib/genealogy.py`)**:
  - Implemented family tree Directed Acyclic Graph (DAG) parser for character dossiers.
  - Diagnostic rules: `GEN-101` (Chronological/biological paradoxes: post-mortem conception, underage parentage, generational loops), `GEN-102` (Succession claim conflicts: competing primogeniture/agnatic heirs).
  - Export formats: Mermaid.js flowchart markdown, standalone interactive HTML visualizer, and JSON.
  - CLI subcommands: `arcanum genealogy -w <world> [-f mermaid|html|json]`, `arcanum lineage`.
- **Wave 4: Conlang Phonotactics, Lexicography & Sound-Change Applier (`scripts/lib/conlang.py`)**:
  - Implemented syllable template phonotactic word/name generator (`(C)V(C)`, etc.) with consonant cluster blacklist filtering.
  - Implemented historical sound law mutation engine supporting ordered phonetic transformations (`target > replacement / environment`).
  - Added lexicon extraction and export to Markdown tables, CSV, and JSON.
  - CLI subcommands: `arcanum conlang generate`, `arcanum conlang mutate`, `arcanum conlang lexicon`.
- **Wave 5: Narrative Pacing, POV Balance & Tension Arc Analytics (`scripts/lib/pacing.py`)**:
  - Implemented prose mode classification (Dialogue, Action, Exposition) via sentence structure and punctuation density analysis.
  - Added sentence length variance and pacing rhythm metrics.
  - Added POV screen-time balance analysis with starvation alerts (> 3 consecutive chapters unmentioned).
  - Implemented tension score modeling (0–100) and standalone HTML visualizer with embedded SVG curves.
  - CLI subcommands: `arcanum pace <manuscript>`, `arcanum tension <manuscript>`, `arcanum words <manuscript> --pov`.
- **Wave 6: Overland/Naval Journey Modeler & Custom Planetary Calendars (`scripts/lib/journey.py`, `scripts/lib/calendar.py`)**:
  - Implemented expedition journey modeler with 14 terrain friction coefficients, 8 travel modes, ration/water burn rates, and day-by-day itineraries.
  - Implemented custom planetary calendar arithmetic supporting arbitrary year lengths, custom months/weekdays, multi-moon synodic phase cycle tracking, syzygies (grand conjunctions), and eclipses.
  - CLI subcommands: `arcanum journey`, `arcanum calendar`.
- **Control Center GUI & World Bible Integration**:
  - Integrated all 6 speculative tool buttons and dialogs into GTK 3 desktop UI (`scripts/lib/ui_gtk3.py`).
  - Enriched world-bible templates and Metadata Menu schemas (`Magic-Tech-System-Template.md`, `Glossary-Conlang-Template.md`, `Deity-Cosmology-Template.md`, `Character-Template.md`, `fileClasses/*.md`).
- **Comprehensive Automated Test Coverage**:
  - Added 48 unit tests across `tests/test_astrophysics.py`, `tests/test_magic_system.py`, `tests/test_genealogy.py`, `tests/test_conlang.py`, `tests/test_pacing.py`, `tests/test_journey.py`, `tests/test_calendar.py` (82 total unit tests discovery).
  - Added end-to-end integration tests 26–31 in `tests/test_audit_fixes.sh`.

### Fixed & Hardened (Full-Spectrum Forensic Audit & Resilience Upgrades)
- **DOCX Synchronization Consolidated Manuscript Filtering (`scripts/lib/docx_sync.py`)**:
  - Fixed stem evaluation condition (`not f.stem.endswith("_Manuscript")`) in `sync_manuscript_docx` to correctly ignore consolidated draft DOCX files during chapter discovery, preventing spurious `Draft-01_Manuscript.md` duplication.
- **Subprocess String Interpolation Boundary Hardening (`scripts/export_book.sh`)**:
  - Refactored native Python OpenXML fallback builder to pass paths and metadata (`${BOOK_TITLE}`, `${AUTHOR_NAME}`) via `sys.argv`, preventing `SyntaxError` crashes on manuscript titles with apostrophes or single quotes.
- **XML 1.0 Illegal Control Character Sanitization (`scripts/lib/docx_sync.py`)**:
  - Added strict control character regex filtering in `escape_xml()` (`\x00-\x08`, `\x0b-\x0c`, `\x0e-\x1f`) to prevent OpenXML schema corruption on pasted raw text.
- **Recursive Character Dossier Discovery (`scripts/lib/continuity.py`)**:
  - Upgraded `extract_lore_profiles()` to traverse character subdirectories recursively (`cdir.rglob("*.md")`) with deduplication, supporting nested dossier taxonomies (`Characters/Protagonists/`, `Characters/Antagonists/`).
- **Recursive Lore Vault Entity Counting (`scripts/lib/ui_gtk3.py`)**:
  - Updated GTK dashboard entity counting to use `fdir.rglob("*.md")`, accurately reflecting nested lore notes.
- **Automated Test Coverage**:
  - Added comprehensive unit tests and regression assertions in `tests/test_docx_sync.py`, `tests/test_continuity.py`, and `tests/test_audit_fixes.sh` (34 passing unit tests, 25/25 integration tests).

### Added (Standard DOCX Integration, Bidirectional Word Processor Sync & Formatting Presets)
- **Zero-Dependency Native OpenXML Engine (`scripts/lib/docx_sync.py`)**:
  - Implemented pure Python standard library (`zipfile`, `xml.etree.ElementTree`) `.docx` builder and extractor, operating 100% offline with zero external pip dependencies.
  - Generates OpenXML packages fully compatible with Microsoft Word (365 / Desktop / Web), Google Docs, and LibreOffice Writer.
  - Supports Markdown headings (`#`, `##`), italic/bold/bold-italic formatting (`*`, `**`, `***`), scene breaks (`* * *`, `#`, `✦ ✦ ✦`), and paragraph-level styles.
- **Dual-Synchronized Hybrid Manuscript Architecture**:
  - Automatically generates both consolidated draft documents (`Draft-01_Manuscript.docx`) and individual chapter files (`01_Chapter.docx`) on `init_manuscript.sh` and `init_draft.sh`.
  - Strips distracting internal metadata tags (`@pov:`, `@location:`, `@char:`, `@thread:`, `@time:`, `@status:`) and HTML comments from `.docx` files for a clean reading experience in word processors.
  - Bidirectional sync engine (`arcanum docx sync <ms>`) compares file modification timestamps (`mtime`), extracting updated prose from `.docx` and safely reattaching original scene metadata headers into `.md`.
- **Configurable Typography & Submission Presets (`scripts/lib/config.py`)**:
  - Added four global formatting presets:
    - `Standard Submission` (Shunn): Times New Roman 12pt, double-spaced, 1" margins, 0.5" first-line indent, `#` scene breaks.
    - `Modern Manuscript`: Georgia 11.5pt, 1.35x spacing, 1" margins, 0.35" indent, `* * *` scene breaks.
    - `Classic Trade`: EB Garamond 12pt, 1.5x spacing, 1" margins, 0.4" indent, `✦ ✦ ✦` scene breaks.
    - `Custom`: Fully customizable via CLI or GUI.
  - CLI configuration commands: `arcanum config docx-presets`, `arcanum config docx-preset <name>`, `arcanum config docx-config <key> <val>`.
- **Desktop Control Center GUI Integration (`scripts/lib/ui_gtk3.py`)**:
  - Added **Word Processing & DOCX Synchronization** toolbar to Tab 2 with "Open in Word Processor", "Sync DOCX ↔ Markdown", and "DOCX Formatting Settings" buttons.
  - Created modal DOCX Formatting Settings dialog allowing authors to switch presets and preview typography settings visually.
- **Action-Oriented CLI Subcommands (`scripts/arcanum`)**:
  - Added `arcanum docx <build|sync|import|open> [ms]` and shortcut `arcanum word [ms]` for 1-click word processor launching.
  - Added `arcanum docx-sync` and `arcanum sync-docx` aliases.
- **Automated Test Coverage**:
  - Added `tests/test_docx_sync.py` (5 unit tests covering OpenXML paragraph building, XML escaping, tag extraction, preset rendering, and roundtrip conversion).
  - Added `tests/test_docx_sync.sh` (end-to-end integration test verifying scaffolding, draft forking, preset build, bidirectional sync, and external file import).
  - Integrated into 7-stage verification harness (`scripts/verify.sh`).

### Optimized & Streamlined (Performance, Resource Efficiency & Uncluttering)
- **Regex Compilation Optimization & Cache Throughput**:
  - Pre-compiled all hot regex patterns at module scope across `scripts/lib/cache.py` (`FENCED_CODE_REGEX`, `WORD_REGEX`, `NW_TAG_LINE_REGEX`, `FRONTMATTER_REGEX`), eliminating repeated per-call regex compilation overhead during large repository scans.
  - Pre-compiled tokenization and filtering regexes in `scripts/lib/manuscript_diff.py` (`TOKEN_REGEX`, `WORD_REGEX`, `STEM_CLEAN_REGEX`, `NW_TAG_REGEX`).
  - Added module-level regex caching in `scripts/lib/continuity.py` for word boundary candidate searches and possessive bindings, eliminating redundant regex compilation across thousands of sentences.
  - Upfront directory pruning in `scripts/wordcount_report.sh` to skip excluded directories (`Outlines`, `.git`, `04-Publishing`, `Exports`, etc.) before traversal.
- **Draft-Aware Export & Analytics Resolution**:
  - Upgraded `scripts/export_book.sh` with `-d, --draft <name>` support and automatic `active_draft` resolution from `manuscript.yaml` / latest draft directory, preventing scene duplication across draft iterations during PDF/EPUB/DOCX compilation.
  - Upgraded `scripts/wordcount_report.sh` to gracefully parse multi-draft directory hierarchies (`Book-01/Draft-01/01_Act_I/01_Chapter.md`) while preserving flat hierarchy compatibility.
- **Documentation Modernization & ADR Synchronization**:
  - Added **ADR-024** (Discrete Multi-Draft Architecture & Accessible Visual Redline Comparator) and **ADR-025** (Dual-Target Secure External & USB Backup Replication) to `docs/ARCHITECTURE.md`.
  - Updated Tech-Stack detection table, C4 system context, and entry points in `docs/ARCHITECTURE.md`.
  - Added Milestones **M16** (Sovereign Privacy & Asset Provenance), **M17** (Intuitive Action-Oriented CLI & Fast Performance Cache), and **M18** (Multi-Draft Management, Visual Redline Comparator & Dual-Target Secure Backups) to `docs/ROADMAP.md`.
  - Synchronized `docs/guides/BACKUP_SETUP.md` with native dual-target replication commands and GTK picker instructions.
- **Repository Hygiene & Local Decluttering**:
  - Verified and hardened `.gitignore` exclusions for `.arcanum_cache.json`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `*.tmp`, `*.bak`, and `*.log`.
  - Cleaned up untracked artifacts and temporary test files across the repository.

### Added (Draft Management, Visual Redline Comparator & Dual-Target Secure Backups)
- **Discrete Multi-Draft Manuscript Management (`scripts/init_draft.sh`)**:
  - Implemented discrete draft version hierarchy (`~/Manuscripts/<Novel>/Book-01/Draft-01/`, `Draft-02/`, `Draft-03/`) preserving 100% open Markdown readability.
  - Added 1-click draft forking (`arcanum draft <ms> [name]`, `arcanum new draft <ms>`) that automatically copies scenes into the new draft directory, updates the `active_draft` pointer in `manuscript.yaml`, and tags a Git milestone commit.
  - Backward compatible baseline resolution: existing flat structures (`Book-01/01_Act_I/`) are seamlessly detected and established as `Draft-01`.
- **Accessible Visual Manuscript Revision Comparator (`scripts/lib/manuscript_diff.py` & `scripts/compare_drafts.sh`)**:
  - Built a fast word-level token diffing engine using Python `difflib.SequenceMatcher` tailored for fiction manuscripts.
  - Generates standalone, accessible HTML Redline changelog reports with:
    - Soft rose/blush (`#f8d7da` / dark mode `#3a1e22`) background highlight with dark text and strikethrough for deleted text (`<del class="diff-del">`).
    - Soft mint/sage (`#d4edda` / dark mode `#1e3a29`) background highlight with dark text and underline for added text (`<ins class="diff-ins">`).
    - Chapter sidebar with jump-to-section navigation, chapter-level word delta pills (`+X / -Y words`), and similarity match scoring.
    - Interactive dark/light mode toggle, live search filter, and "Highlight Changes Only" changelog view (dimming unchanged paragraphs).
    - Print-to-PDF stylesheet support.
  - Added terminal ANSI color output (`arcanum compare <ms> <d2> <d1> --terminal`) and machine-readable JSON metrics (`--json`).
  - Added native LibreOffice Writer Track Changes bridge (`arcanum compare <ms> <d2> <d1> --libreoffice`).
- **Dual-Target Secure External & USB Backups (`scripts/lib/config.py` & `scripts/backup_world.sh`)**:
  - Added persistent XDG configuration manager (`~/.config/ars-arcanum/config.json`) supporting `arcanum backup-dest get|set|clear`.
  - Upgraded `scripts/backup_world.sh` with dual-target replication: verified `.tar.gz` archives and SHA-256 sidecars are created locally in `05-Backups/` and automatically synced to the configured secure destination (USB drives, external mounts, secondary drives).
  - Validates destination paths against path traversal attacks (`..`).
- **Desktop Control Center GUI Integration (`scripts/lib/ui_gtk3.py`)**:
  - Added **Manuscript Draft Revisions & Redline Comparator** frame to Tab 2 (Manuscript & Drafting) with volume and draft selectors, "+ Fork New Draft" dialog, "View Redline Changelog (Browser)" launcher, and LibreOffice comparison button.
  - Added **Dual-Target Secure Backup Destination** frame to Tab 4 (Snapshots & Backups) with interactive directory picker and clear destination controls.
- **Comprehensive Automated Test Coverage**:
  - Added `tests/test_drafts_and_diff.py` (unit tests for config persistence, word diff tokenization, SequenceMatcher, HTML redline styling, JSON metrics).
  - Added `tests/test_drafts_and_diff.sh` (end-to-end integration test for `init_draft.sh`, `compare_drafts.sh`, dual-target `backup_world.sh`, and CLI dispatching).
  - Integrated both suites into `scripts/verify.sh` with zero regressions.
- **Project Renaming**:
  - Renamed the project from "Scriptorium" to "Ars Arcanum" across the entire codebase, documentation, templates, desktop launchers, Debian packaging, and Git remote.
  - Provided new unified CLI commands `arcanum` and `ars-arcanum` with backward-compatible `scriptorium` fallback.
  - Renamed scripts: `setup_arcanum.sh`, `uninstall_arcanum.sh`, `arcanum_doctor.sh`, `arcanum_app.py`, `leechblock_arcanum_rules.json`.
  - Renamed performance cache artifact to `.arcanum_cache.json` with fallback support.
- **Privacy & Asset Provenance (Data Minimization & Attribution)**:
  - Added [PRIVACY.md](PRIVACY.md) specifying zero telemetry, local-only processing, and explicit consent policies.
  - Added [REFERENCES.md](REFERENCES.md) with complete Open Source / Creative Commons attribution records for non-commercial use.
  - Scrubbed personal identifiable information (PII) across the codebase in favor of generic maintainer identifiers and official repository links.
- **Intuitive & Simple CLI Ergonomics**:
  - Reorganized `arcanum` CLI into natural authoring action verbs: `arcanum new <type> <name>`, `arcanum write [target]`, `arcanum save [target]`, `arcanum publish [ms]`, `arcanum words [ms]`, and `arcanum check`.
  - Added smart typo correction and fuzzy suggestions (e.g. `arcanum docter` -> `Did you mean 'doctor'?`).
  - Streamlined `--help` manual with structured visual workflow categories and quick-start copy-pasteable examples.
- **Cross-Platform Robustness & CLI Performance Upgrades**:
  - Upgraded YAML frontmatter regex and word count parsing across `scripts/lib/cache.py`, `scripts/lib/continuity.py`, and `scripts/wordcount_report.sh` to seamlessly handle both CRLF (`\r\n`) and LF (`\n`) line endings.
  - Expanded `arcanum` CLI with dedicated `cache` subcommands (`arcanum cache <scan|wordcounts|clear>`, `arcanum cache-scan`, `arcanum cache-clear`).
  - Upgraded `scripts/arcanum_doctor.sh` System Diagnostics to validate and report existence and write permissions for `~/Universes` and `~/Manuscripts` directory roots.
  - Added automated unit test suite `test_crlf_frontmatter_and_word_counts` in `tests/test_cache.py` (21/21 passing).

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
