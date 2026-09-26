# Changelog

All notable changes to Ars Arcanum are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Scope decisions
behind each wave are recorded in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## [4.1.0] - 2026-09-26

### Added (The Sovereign Cohesive Ecosystem & Creative Freedom Architecture — Phase 21)
- **Universal Engine Documentation & Discovery (`arcanum doc <engine>`)**:
  - Comprehensive in-CLI and interactive documentation for all 50 core and craft engines (`scripts/lib/cli.py`, `scripts/lib/registry.py`).
  - Detailed domain breakdowns for each engine: Scientific & Structural Foundations, Worldbuilding Relevance, Storytelling Relevance, and Prose Writing Relevance.
  - Bidirectional hyphen/underscore normalization and multi-word lookup parsing (e.g., `arcanum doc calc astro`, `arcanum doc magic-system`).
- **Advisory-First Creative Freedom Mechanics (`ADR-115`)**:
  - Non-imposing diagnostic alerts with multi-option resolution pathways: *Option A (Hard Realism)*, *Option B (Speculative Trope)*, and *Option C (Author Sovereignty)*.
  - Guarantees 100% authorial creative control without rigid blocker rules or forced tropes.
- **Studio Hub Interactive Craft Guide (`tab-guide`)**:
  - Dedicated Craft Guide explorer inside the offline Studio Hub (`scripts/lib/studio_hub.py`) with instant search, category filtering, and discipline tags (Worldbuilding, Craft, Diagnostics, Publishing, Tools).
- **Desktop GUI Craft Guide Integration**:
  - Integrated Craft & Lore Guide dialog across GTK 3 (`scripts/lib/ui_gtk3/dialogs.py`) and Libadwaita (`scripts/lib/ui_adw.py`) interfaces.
- **Quality & Test Elevation**:
  - Added unit test coverage in `tests/test_registry.py` and `tests/test_cli_dispatch.py`, elevating total passing tests to **687 tests** (0 failures, 2 skipped, 0 Ruff violations, clean Mypy typing).

## [4.0.0] - 2026-09-26

### Removed (Architectural Trimming & Decommissioning)
- **Pruned 8 Obsolete/Niche Engines**: Removed `fine_tuning.py`, `cipher.py`, `editorial_council.py`, `barcode.py`, `archive_freeze.py`, `tts_reader.py`, `media_overlay.py`, and `plugins.py`/`plugin_market.py` along with their corresponding unit tests, eliminating dead code and maintenance overhead.
- **Pruned Redundant Shell Scripts**: Removed 17 auxiliary single-line shell scripts in `scripts/`, standardizing repository execution exclusively on canonical `scripts/arcanum`, `scripts/verify.sh`, and `scripts/setup_arcanum.sh`.

### Changed & Consolidated
- **Consolidated Stylistics & Cultural Idioms**: Merged `idioms.py` directly into `scripts/lib/stylistics.py` as an optional cultural immersion check; consolidated duplicate frontmatter parsing into `frontmatter_builder.py`.
- **Non-Imposing Creative Advisory Doctrine**: Replaced rigid blocking validation with advisory diagnostic linters across magic systems, story structure paradigms, and tactical battle planning (`ADR-112`).
- **Synchronized Registry, CLI & Studio Hub**: Updated `registry.py`, `cli.py`, `studio_hub.py`, `ui_adw.py`, and `ui_gtk3` presentation packages to reflect the streamlined engine matrix.

### Added (Craft & Worldbuilding Engine Expansions)
- **Astrophysics & Exotic Planetary Configurations** (`scripts/lib/astrophysics.py`, `arcanum calc system-dossier`):
  - Support for non-standard planetary configurations: tidally locked eyeball worlds, habitable gas giant exomoons, brown dwarf worlds, circumbinary P/S-types, and hycean worlds.
  - Parameter tinkering sweet-spot calculation engine, scientific plausibility warning advisor, and Star System Dossier export with direct orbital insolation integration for `climate.py` (`ADR-113`).
- **Multi-Calendar & Multi-Era Chronology** (`scripts/lib/calendar.py`, `arcanum calendar`):
  - Multi-calendar registry with custom date syntax templates and era suffixes (no hardcoded dd/mm/yyyy or BC/AD).
  - Continuous underlying epoch timeline projection across arbitrary fictional calendar systems.
- **Multi-POV Narrative Thread & Convergence Subway Map** (`scripts/lib/branching_graph.py`, `arcanum branch`):
  - Reworked from gamebook choice DAGs into a Multi-POV Narrative Thread & Convergence Subway Map tracking character storyline splits, convergences, and timeline milestones (`ADR-114`).
- **Interactive HTML5/SVG Graphical Map Creator** (`scripts/lib/cartography.py`, `arcanum map --creator`):
  - In-browser interactive graphical world map editor and SVG/PNG exporter.
- **Bidirectional Structured Corpus & Vault Restore** (`scripts/lib/corpus_export.py`, `arcanum corpus restore`):
  - Full bidirectional restoration of World Bibles and Manuscripts from exported JSONL or SQLite archives.
- **Expanded Story Structure Paradigms** (`scripts/lib/structure.py`, `arcanum structure`):
  - Expanded advisory structural mapping across 11+ paradigms (Three-Act, Save the Cat, Hero's Journey, Dan Harmon Story Circle, Kishōtenketsu, 8-Sequence, Fichtean Curve, 7-Point, Freytag's Pyramid, Romancing the Beat, Virgin's Promise).
- **Fuzzy Dynastic Genealogies** (`scripts/lib/genealogy.py`, `arcanum genealogy`):
  - Relaxed generational builder supporting unrecorded/collapsed generations and disputed succession claims.
- **Multi-Paradigm Causality & Time-Travel Consistency** (`scripts/lib/causality.py`, `arcanum causality`):
  - Validates Fixed/Novikov self-consistency, Dynamic Butterfly divergence, Multiverse Branching, Time Loops, and Chrono-bubbles.
- **Custom Character Attributes & Cross-Volume Evolution** (`scripts/lib/series_continuity.py`, `arcanum continuity`):
  - Arbitrary user-defined character attribute tracking and cross-volume progression.

## [3.7.0] - 2026-09-25

### Added (The Sovereign Local Intelligence, Editorial Intelligence & Narrative Distribution Architecture — Phase 19)
- **Interactive Branching Narrative Graph & Choice Engine** (`scripts/lib/branching_graph.py`, `arcanum branch`):
  - Choice-driven interactive narrative DAG compiler with `@choice:`, `@state:`, `@req:`, and wikilink parsing.
  - Topological diagnostics (`BRN-101` dead ends, `BRN-102` unreachable orphans, `BRN-105` missing targets).
  - Multi-engine compilation to Playable HTML5 Reader, Inkle Ink (`.ink`), Twine 2 Twee 3 (`.twee`), and Obsidian Mermaid diagrams with 12 unit tests in `tests/test_branching_graph.py` and documentation in `docs/BRANCHING_GRAPH.md`.
- **Local Semantic Retrieval (RAG) & Lore Recall Engine** (`scripts/lib/local_rag.py`, `arcanum rag`):
  - Zero-dependency vector space model with TF-IDF sub-linear weighting, Robertson-Spärck Jones smoothed IDF, and SQLite FTS5 hybrid keyword rank fusion.
  - Injection-safe LLM prompt context synthesizer (`<system_instructions>`, `<canonical_lore_context>`, `<user_query>`) with 12 unit tests in `tests/test_local_rag.py` and documentation in `docs/LOCAL_RAG.md`.
- **Multi-Perspective Autonomous Editorial Council** (`scripts/lib/editorial_council.py`, `arcanum council`):
  - Four distinct sovereign editorial personas: The Master Line Editor (*Lady Cassian*), The Lore Inquisitor (*Archon Vaelor*), The Story Architect (*Grand Architect Soren*), and The Continuity Overseer (*Chronicler Mirella*).
  - Consensus readiness score ($0-100\%$), chamber dissent detection ($\ge 12\text{ pt}$ deviation), prioritized master action checklist, and interactive HTML5 dashboard with 12 unit tests in `tests/test_editorial_council.py` and documentation in `docs/EDITORIAL_COUNCIL.md`.
- **Local AI Fine-Tuning & Dataset Synthesizer** (`scripts/lib/fine_tuning.py`, `arcanum train-data`):
  - Multi-domain instruction tuning dataset compiler generating Alpaca, ShareGPT, and ChatML schemas from World Bibles, character sheets, and manuscripts.
  - Automated Ollama `Modelfile` generator and train/val split partitioner with 12 unit tests in `tests/test_fine_tuning.py` and documentation in `docs/FINE_TUNING.md`.
- **Universal Structured Corpus & RAG Dataset Exporter** (`scripts/lib/corpus_export.py`, `arcanum corpus`):
  - Repository-wide discovery and semantic chunking engine exporting to JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`), relational SQLite with FTS5 search, and executive Markdown summary digest with 12 unit tests in `tests/test_corpus_export.py` and documentation in `docs/CORPUS_EXPORT.md`.
- **Offline Neural TTS & Audio Proofreader** (`scripts/lib/tts_reader.py`, `arcanum tts`):
  - Standalone HTML5 Web SpeechSynthesis reader with sentence karaoke highlighting, playback speed controls ($0.5\times-2.5\times$), and phonetic name pronunciation dictionary.
  - Host speech toolchain discovery (`piper`, `espeak-ng`, `espeak`, `spd-say`, macOS `say`, Windows SAPI) with 12 unit tests in `tests/test_tts_reader.py` and documentation in `docs/TTS_READER.md`.
- **Multi-Platform Release Distribution Packaging Engine** (`scripts/package_distribution.py`, `arcanum package`):
  - Publication packaging engine assembling Reader Editions (EPUB+PDF+HTML), Publisher/Agent Submissions (DOCX+Query+Synopsis), watermarked Advance Reading Copies (ARCs), and World Lore Codex Bundles.
  - SHA-256 cryptographic archive verification and `RELEASE_MANIFEST.json` generation with 12 unit tests in `tests/test_package_distribution.py` and documentation in `docs/PACKAGING.md`.
- **World Doctor & Cosmos Integrity Diagnostics** (`scripts/lib/world_doctor.py`, `arcanum doctor`):
  - Deep lore vault consistency auditor checking broken wikilinks (`WLD-101`), dangling frontmatter (`WLD-102`), missing fields (`WLD-103`), timeline chronology inversions (`WLD-104`), duplicate identities (`WLD-105`), frontmatter parse syntax (`WLD-106`), orphan lore notes (`WLD-107`), and manuscript entity drift (`WLD-108`).
  - Multi-era timeline chronological comparison engine (BCE/CE, 1E/2E/3E, ordinal eras) with 12 unit tests in `tests/test_world_doctor.py` and documentation in `docs/WORLD_DOCTOR.md`.
- **Extended Integration Harness & Milestone Metrics**:
  - Reached 797 passing unit tests across repository with 0 failures and 0 linter violations.
  - Master Grand Tour E2E harness extended to 21 stages validating all intelligence, editorial, and distribution workflows.
  - Architectural Decision Records logged from ADR-103 to ADR-110.

## [3.6.0] - 2026-09-24

### Added (The Authoring Studios, Publishing Toolchains & Creative Scaffolding Expansion — Phase 18)
- **Back-Matter Concordance & Dramatis Personae Indexer** (`scripts/lib/concordance.py`, `arcanum concordance`):
  - World Lore Bible parser synthesizing publication-ready back-matter across Characters, Factions, Artifacts, Bestiary, Magic Systems, and Conlangs.
  - Automatic cross-referencing and multi-volume `04_Back_Matter/` generator with 12 unit tests in `tests/test_concordance.py` and author guide in `docs/CONCORDANCE.md`.
- **Sovereign Zen Drafting Studio & In-Situ Lore Drawer** (`scripts/lib/zen_studio.py`, `arcanum studio`):
  - Single-file standalone HTML5 distraction-free drafting cockpit with centered typewriter scrolling, live telemetry (words, reading time at 200 WPM, speaking time at 150 WPM), and slide-out World Bible search vault.
  - Client-side `localStorage` caching and one-click Markdown download with 12 unit tests in `tests/test_zen_studio.py` and author guide in `docs/ZEN_STUDIO.md`.
- **Visual Story Canvas & Multi-Paradigm Corkboard** (`scripts/lib/story_canvas.py`, `arcanum canvas`):
  - Interactive HTML5 drag-and-drop narrative beat board supporting 9 structural storytelling paradigms (Three-Act, Save the Cat, 8-Sequence, Hero's Journey, Kishōtenketsu, Fichtean Curve, 7-Point, Story Grid, Dan Harmon Circle).
  - Real-time client-side act pacing recalculation, POV swimlane filtering, and 12 unit tests in `tests/test_story_canvas.py` with author guide in `docs/CANVAS_GUIDE.md`.
- **Multi-Volume Series Omnibus Compiler** (`scripts/lib/omnibus.py`, `arcanum omnibus`):
  - Multi-book series compiler with automatic volume discovery, standardized book dividers, unified chapter re-indexing, and master Table of Contents.
  - Complete JSON rollup manifest exporter with 12 unit tests in `tests/test_omnibus.py` and author guide in `docs/OMNIBUS.md`.
- **Author Portfolio & Catalog Analytics Dashboard** (`scripts/lib/portfolio.py`, `arcanum portfolio`):
  - Multi-manuscript progress aggregator computing total catalog word counts, target completion milestones, and 5-tier editorial lifecycle stages (Scaffolding, Drafting Act I, Drafting Act II/III, Revisions, Publication-Ready).
  - Standalone HTML5 portfolio hub with 12 unit tests in `tests/test_portfolio.py` and author guide in `docs/PORTFOLIO.md`.
- **EPUB 3 SMIL Media Overlays & Synchronized Narration Player** (`scripts/lib/media_overlay.py`, `arcanum overlay`):
  - Paragraph-level audio-text synchronizer generating W3C EPUB 3 Media Overlay XML (`.smil`) with millisecond timestamp precision.
  - Standalone HTML5 browser player utilizing Web Speech Synthesis and audio timeline scrubbing with 12 unit tests in `tests/test_media_overlay.py` and author guide in `docs/MEDIA_OVERLAY.md`.
- **Smart Typography Normalizer & Punctuation Engine** (`scripts/lib/typography_cleaner.py`, `arcanum typography`):
  - Publication-grade typography formatter converting straight quotes to curly pairs, hyphens to em/en-dashes, dots to ellipses, and stripping trailing whitespace while protecting frontmatter and codeblocks.
  - In-place batch processing with `.bak` safety backups and unified diff preview with 12 unit tests in `tests/test_typography_cleaner.py` and author guide in `docs/TYPOGRAPHY.md`.
- **ISBN-13 Vector SVG/PNG Barcode Engine** (`scripts/lib/barcode.py`, `arcanum barcode`):
  - Pure-Python zero-dependency EAN-13 and Bookland barcode generator with Modulo-10 checksum validation and legacy ISBN-10 conversion.
  - Scalable vector SVG and pure-Python zlib-deflated PNG generation with 12 unit tests in `tests/test_barcode.py` and author guide in `docs/BARCODE.md`.
- **Extended Integration Harness & Milestone Metrics**:
  - Reached 750 passing unit tests across repository with 0 failures and 0 linter violations.
  - Master Grand Tour E2E harness extended to 20 stages validating all authoring, studio, and publishing workflows.
  - Architectural Decision Records logged from ADR-095 to ADR-102.

## [3.5.0] - 2026-09-24

### Added (The Worldbuilding Sciences & Narrative Mechanics Expansion — Phase 17)
- **Focus Ambient & Binaural Soundscape Generator** (`scripts/lib/ambient.py`, `arcanum ambient`):
  - Pure Python procedural audio synthesis with White, Pink ($1/f$), and Brown/Red (Brownian walk) noise filters.
  - Stereo phase-offset binaural beat generator across Alpha (8–12 Hz), Theta (4–8 Hz), Beta (13–30 Hz), and Gamma (40 Hz) cognitive bands.
  - Zero-dependency standalone HTML5 WebAudio synthesizer and 14 unit tests in `tests/test_ambient.py` with author guide in `docs/AMBIENT.md`.
- **Dynamic Tactical Combat & Monte Carlo Skirmish Simulator** (`scripts/lib/tactical_sim.py`, `arcanum tactical`):
  - Unit combatant modeling: HP, armor mitigation, attack bonuses, damage variance, agility dodge thresholds, weapon types, and morale collapse triggers.
  - Battlefield terrain modifiers (Open Field, Castle Walls, Dense Forest, Dungeon Corridor) with cover defense bonuses and ranged penalties.
  - Turn-by-turn blow-by-blow narrative fight log generator and Monte Carlo victory probability engine across 100+ simulated skirmishes.
  - 14 unit tests in `tests/test_tactical_sim.py` and author guide in `docs/TACTICAL_SIM.md`.
- **Motivation-Reaction Unit (MRU) Scene Mechanics Analyzer** (`scripts/lib/scene_mechanics.py`, `arcanum scene`):
  - Swain & Butcher craft mechanics linter: Stimulus $\to$ Visceral Reflex $\to$ Emotional Response $\to$ Cognitive Thought $\to$ Action/Dialogue.
  - Inverted/backwards MRU sequence flaw detector and Proactive Scene (Goal $\to$ Conflict $\to$ Disaster) vs. Reactive Sequel (Reaction $\to$ Dilemma $\to$ Decision) analyzer.
  - Standalone offline HTML visualizer and 12 unit tests in `tests/test_scene_mechanics.py` with author guide in `docs/SCENE_MECHANICS.md`.
- **Multi-Track Narrative Plot Grid & Subplot Matrix Engine** (`scripts/lib/plot_matrix.py`, `arcanum plot-matrix`):
  - Manuscript plot tag extractor (`@plot:`, `@thread:`, `@arc:`) tracking multiple storylines across chapters.
  - Plot health diagnostics: Abandoned/dormant thread alerts ($\ge 4$ chapter absence gaps), dangling unresolved plotline warnings, and chapter track density distribution.
  - Interactive SVG multi-lane timeline visualizer and 12 unit tests in `tests/test_plot_matrix.py` with author guide in `docs/PLOT_MATRIX.md`.
- **Dual-Track Chronological vs. Narrative Timeline Synchronizer** (`scripts/lib/timeline_sync.py`, `arcanum timeline`):
  - Dual-track temporal analyzer extracting `@time:`, `@pov:`, `@location:` metadata.
  - Automatic flashback/flashforward detection, chronological sequence sorting, and bilocation paradox detection.
  - Standalone HTML timeline viewer and 12 unit tests in `tests/test_timeline_sync.py` with author guide in `docs/TIMELINE_SYNC.md`.
- **Planetary Climate, Orographic Rain Shadows & Köppen Biomes** (`scripts/lib/climate.py`, `arcanum climate`):
  - Stellar insolation, orbital flux, Bond albedo, greenhouse warming, and blackbody equilibrium temperature modeling.
  - Atmospheric circulation cells (1-cell, 3-cell, 5-cell) and prevailing surface wind vector calculation.
  - Orographic precipitation and leeward Foehn rain-shadow desert simulator with 14 terrestrial Köppen biome classifications.
  - 12 unit tests in `tests/test_climate.py` and author guide in `docs/CLIMATE.md`.
- **Trophic Food Web Ecology & Biomass Efficiency Simulator** (`scripts/lib/ecology.py`, `arcanum ecology`):
  - World Bestiary and Flora trophic profile parser across 4 ecological levels (Producer, Herbivore, Carnivore, Apex Predator).
  - Food web graph integrity auditor detecting circular predation loops (`ECO-303`), orphaned predators (`ECO-301`), missing primary producers (`ECO-304`), and Lindeman 10% trophic biomass deficits (`ECO-302`).
  - Obsidian Mermaid.js food-web diagram generator, standalone HTML report, and 12 unit tests in `tests/test_ecology.py` with author guide in `docs/ECOLOGY.md`.
- **Earth Idiom & Immersion-Breaking Eponym Linter** (`scripts/lib/idioms.py`, `arcanum idioms`):
  - Automated manuscript prose scanner detecting Earth-specific eponyms (`IDM-101`), mythological/scriptural references (`IDM-102`), and biological cliches (`IDM-103`).
  - Historical origin annotations with in-world replacement suggestions, customizable `configs/idioms.json`, and runtime whitelist support.
  - Standalone HTML report and 12 unit tests in `tests/test_idioms.py` with author guide in `docs/IDIOMS.md`.
- **19-Stage Grand Tour Master Integration Lifecycle Harness** (`tests/test_grand_tour_e2e.py`):
  - Extended end-to-end integration test with Stage 19 validating all 8 new science, soundscape, combat, and narrative mechanics engines.

## [3.4.0] - 2026-09-22

### Added (The Sovereign Story Craft & Editorial Mastery — Phase 16)
- **In-World Macroeconomics & Anachronism Matrix** (`scripts/lib/economy.py`, `arcanum economy`):
  - World Bible economy profile parser, Purchasing Power Parity (PPP) relative exchange rate matrices, and trade cargo freight margin modeler (`calc_trade_margin`).
  - Manuscript price anomaly linter detecting severe inflation/deflation (`ECO-101`), unregistered currencies (`ECO-102`), and technological era anachronisms (`ECO-201`).
  - 12 comprehensive unit tests in `tests/test_economy.py` and author guide in `docs/ECONOMY.md`.
- **Overland, Naval & Aerial Journey Expedition Modeler** (`scripts/lib/journey.py`, `arcanum journey`):
  - Terrain friction multipliers across 14 biome types and 15 land/naval/aerial travel paces.
  - Mathematical party supply/ration/water consumption modeler with desert modifiers and day-by-day march itineraries with starvation risk warnings.
  - 12 unit tests in `tests/test_journey.py` and author guide in `docs/JOURNEY.md`.
- **Offline Vector Cartography & Interactive Map Viewer** (`scripts/lib/cartography.py`, `arcanum map`):
  - Automated vector SVG map generator with hexagonal and Cartesian grids, proximity-based trade route connection lines with travel time milestones, compass rose, and scale bars.
  - Standalone offline vanilla JS pan/zoom HTML map viewer with landmark search filters and CSP sandbox compliance.
  - 12 unit tests in `tests/test_cartography.py` and author guide in `docs/CARTOGRAPHY.md`.
- **Narrative Pacing, POV Balance & Tension Arc Analytics** (`scripts/lib/pacing.py`, `arcanum pacing`):
  - Syntactic cadence metrics: dialogue-to-exposition density ratios, sentence length variance, and staccato/flowing cadence factors.
  - Viewpoint screen-time distribution with consecutive absence / POV starvation warnings (>3 chapters without active scene).
  - Subplot thread momentum tracking (`@thread:`, `@plot:`) and composite chapter tension index modeling ($0 \text{ to } 100$).
  - 12 unit tests in `tests/test_pacing.py` and author guide in `docs/PACING.md`.
- **Multi-Paradigm Story Structure & Beat Sheet Enforcer** (`scripts/lib/structure.py`, `arcanum structure`):
  - Full structural alignment mapping across 9 canonical story architectures (Three-Act, Save the Cat, Hero's Journey, Story Circle, Seven-Point, 8-Sequence, Fichtean Curve, Kishōtenketsu, Freytag's Pyramid).
  - Target percentage milestone windows, structural drift penalties, and overall Structural Harmony scoring ($0 \text{ to } 100\%$).
  - 12 unit tests in `tests/test_structure.py` and author guide in `docs/STRUCTURE.md`.
- **Character Voice Profiler & Dialogue Fingerprint Engine** (`scripts/lib/voice.py`, `arcanum voice`):
  - Multi-convention dialogue attribution parser (script format, post-quote, pre-quote, `@pov:` blocks).
  - Linguistic metrics: Type-Token Ratio (TTR), mean utterance length (MUL) & variance, contraction formality ratios, punctuation cadence, and distinctive vocabulary via TF-IDF.
  - Pairwise cosine similarity matrix with Voice Bleed warnings ($\ge 92\%$) for character linguistic homogeneity.
  - 12 unit tests in `tests/test_voice.py` and author guide in `docs/VOICE.md`.
- **Stylistics, Dialogue Mechanics & Readability Rhythm Engine** (`scripts/lib/stylistics.py`, `arcanum stylistics`):
  - Overwrought said-bookisms detector, adverb-heavy dialogue tags, and quote punctuation/capitalization formatting linter (`PRO-101`).
  - Sliding-window word echo repetition scanner with built-in zero-dependency English morphological stemmer (`PRO-102`).
  - Readability rhythm analysis with staccato cluster alerts, monotone cadence warnings, and 4 standard readability metrics (Flesch Reading Ease, Flesch-Kincaid, Gunning Fog, Coleman-Liau).
  - 14 unit tests in `tests/test_stylistics.py` and author guide in `docs/STYLISTICS.md`.
- **Master Grand Tour Lifecycle Integration Harness** (`tests/test_grand_tour_e2e.py`):
  - Extended to **Stage 18: Story Craft, Prose Mechanics & Narrative Architecture**.
- **Architecture Decision Records**:
  - Recorded `ADR-080` through `ADR-086` in `decisions.md`.

## [3.3.0] - 2026-09-22

### Added (The Sovereign Worldbuilding Codex & Arcane Mastery — Phase 15)
- **Static World Wiki & Offline Codex Exporter** (`scripts/lib/codex_export.py`, `arcanum codex`):
  - Standalone single-file HTML encyclopedia generator with bidirectional Obsidian `[[Wikilinks]]` resolution.
  - Frontmatter YAML infobox generation, inlined JSON inverted search index, and multi-theme reading modes (Dark, Light, Classic Sepia).
  - 12 comprehensive unit tests in `tests/test_codex_export.py` and author guide in `docs/CODEX_EXPORT.md`.
- **Hard Magic Systems & Arcane Constraint Matrix** (`scripts/lib/magic_system.py`, `arcanum magic-check`, `arcanum magic-report`):
  - Sanderson's Laws of Magic enforcement: character tier limits (`MAG-101`), catalyst/reagent validation (`MAG-102`), physical/metaphysical hard limitations (`MAG-103`), and scene fatigue overdraw (`MAG-104`).
  - Standalone offline CSP-compliant HTML arcane audit dashboard.
  - 12 unit tests in `tests/test_magic_system.py` and author guide in `docs/MAGIC_SYSTEM.md`.
- **In-World Ciphers, Runes & SVG Inscription Generator** (`scripts/lib/cipher.py`, `arcanum cipher`):
  - Cryptographic transformations: Caesar (ROT-N), Atbash, Vigenère, Rail Fence, Columnar transposition, and line.word Book Ciphers.
  - Phonetic rune transliteration for Elder Futhark and Anglo-Saxon Futhorc with digraph handling and standalone SVG vector card generation.
  - 12 unit tests in `tests/test_cipher.py` and author guide in `docs/CIPHERS.md`.
- **Dynastic Genealogies & Succession Lineage Engine** (`scripts/lib/genealogy.py`, `arcanum genealogy`, `arcanum lineage`):
  - Resolves bidirectional royal/noble family DAG trees and validates monarchical succession rankings.
  - Biological and chronological paradox detection (`GEN-101`: lifespan inversions, premature conception, posthumous births, circular ancestry loops) and succession claim conflicts (`GEN-102`).
  - Native Mermaid.js flowchart generator, ASCII terminal tree visualizer, and offline HTML reports.
  - 12 unit tests in `tests/test_genealogy.py` and author guide in `docs/GENEALOGY.md`.
- **Conlang Phonotactics & Historical Sound-Change Engine** (`scripts/lib/conlang.py`, `arcanum conlang`):
  - Generates phonotactically valid words, names, and places across syllable templates (`CV`, `CVC`, `CCV`, etc.) with cluster filtering and deterministic seeding.
  - Historical sound law transformation engine ($A \to B / X\_Y$) for ordered language evolution.
  - Markdown lexicon table extraction, keyword querying, and CSV/JSON exporting.
  - 12 unit tests in `tests/test_conlang.py` and author guide in `docs/CONLANG.md`.
- **Geopolitical Faction Matrix & Campaign Logistics Architecture** (`scripts/lib/factions.py`, `arcanum faction`):
  - Multilateral geopolitical relationship matrix auditing asymmetric alliances (`FAC-101`), triad tensions (`FAC-102`), vassal treason (`FAC-103`), and self-references (`FAC-104`).
  - Lanchester combat equations (Square and Linear laws) with fortification multipliers and morale breakpoints.
  - Military campaign logistics modeler computing food/water burn rates, wagon train requirements, and Wagon Radius limits.
  - 12 unit tests in `tests/test_factions.py` and author guide in `docs/FACTIONS.md`.
- **Custom Planetary Calendars & Multi-Moon Phase Synchronizer** (`scripts/lib/calendar.py`, `arcanum calendar`):
  - Arbitrary planetary orbital cycles, non-standard year/day lengths, and custom month/weekday arithmetic.
  - Multi-moon synodic phase tracker with illumination percentages, Unicode glyphs, and celestial syzygy / eclipse detection.
  - Formatted ANSI monthly terminal calendar grids and standalone offline HTML reports.
  - 12 unit tests in `tests/test_calendar.py` and author guide in `docs/CALENDARS.md`.
- **Grand Tour Master E2E Lifecycle Verification Extension**:
  - Extended `tests/test_grand_tour_e2e.py` to 17 comprehensive stages incorporating static codex export and arcane hard magic validation.
- **Architectural Decision Records**:
  - Recorded ADR-073 through ADR-079 in `decisions.md`.

## [3.2.0] - 2026-09-22

### Added (The Sovereign Crown & Flathub Upstream Hardening — Phase 14)
- **Flathub Upstream Packaging Validation Suite** (`flatpak/flathub_submission_validate.py`):
  - Automated verification of AppStream 0.16+ XML metainfo compliance, HTTPS screenshot URLs, OARS 1.1 content ratings, and Flatpak manifest finish-args.
  - Comprehensive unit test suite in `tests/test_flathub_validation.py` (12 tests, 100% passing).
  - Dynamic versioning support in `flatpak/build_offline_bundle.sh`.
- **Cosmos Archive Freeze & Cryptographic Provenance Sealer** (`arcanum freeze`, `arcanum verify-archive`):
  - Implemented `scripts/lib/archive_freeze.py` providing Merkle-style root SHA-256 digests, `ARCHIVE_MANIFEST.json` and `PROVENANCE_SEAL.md` generation.
  - Comprehensive tamper and bit-rot detection (`FRZ-101`, `FRZ-102`, `FRZ-103`).
  - Unit test suite in `tests/test_archive_freeze.py` (15 tests) and author guide in `docs/ARCHIVE_FREEZE.md`.
- **Multi-Volume Dramatis Personae & Universe Cast Matrix** (`arcanum cast`, `arcanum dramatis-personae`):
  - Implemented `scripts/lib/dramatis_personae.py` providing automated cross-volume character dossier discovery (`World/Characters/*.md`).
  - Cross-references manuscript chapters (`@pov:`, `@char:`, `@cast:`, `@death:` tags) and flags `CAS-101` (Ghost Character), `CAS-102` (Post-Mortem Action), and `CAS-103` (Orphan Lore Character).
  - Publication-ready Markdown Dramatis Personae appendix compiler and offline CSP-compliant HTML character gallery.
  - Unit test suite in `tests/test_dramatis_personae.py` (15 tests) and author manual in `docs/DRAMATIS_PERSONAE.md`.
- **Grand Tour Master E2E Lifecycle Verification Extension**:
  - Extended `tests/test_grand_tour_e2e.py` to 16 comprehensive stages incorporating archive freeze verification and universal Dramatis Personae generation.
- **Architectural Decision Records**:
  - Recorded ADR-070 (Flathub Submission Validator), ADR-071 (Cosmos Archive Freeze), and ADR-072 (Multi-Volume Dramatis Personae) in `decisions.md`.

## [3.1.0] - 2026-09-22

### Added (The Sovereign Craft Deepening — Phase 13)
- **Sovereign Writing Sprint & Session Analytics** (`arcanum sprint`):
  - Implemented `scripts/lib/writing_sprint.py` providing session management, atomic `.sprint_state.json` sidecar tracking, and JSONL velocity logging (`.sprint_log.jsonl`).
  - Computes WPM velocity, daily writing streaks, and best session milestones.
  - Standalone offline CSP-compliant HTML velocity dashboard with progress metrics and streak indicators.
- **Manuscript Revision Density & Churn Heatmap** (`arcanum revision-heatmap`):
  - Implemented `scripts/lib/revision_heatmap.py` providing snapshot-based chapter churn analysis (`difflib` unified line diffs).
  - Flags over-revised chapters (`REV-101`) and pristine/untouched drafts (`REV-102`).
  - Offline CSP-compliant HTML heatmap with color-graded churn indicators (green/amber/red).
- **Causal DAG & Time-Travel Consistency Suite** (`arcanum causality`):
  - Comprehensive test suite in `tests/test_causality.py` (12 tests) and author documentation in `docs/CAUSALITY.md`.
  - Audits Grandfather paradoxes (`CAU-101`), unregistered bootstrap loops (`CAU-102`), Novikov violations (`CAU-103`), orphan timeline branches (`CAU-104`), and temporal inversions (`CAU-105`).
- **Prophecy Resolution Matrix & Arcane Inscription Tracker** (`arcanum prophecy`):
  - Expanded test suite in `tests/test_prophecy.py` (12 tests) and author documentation in `docs/PROPHECY.md`.
  - Cross-validates prophecy clause resolutions, chosen one mortality (`PRP-102`), and fulfillment status discrepancies (`PRP-103`).
- **6D Sensory Palette & White Room Syndrome Linter** (`arcanum senses`):
  - Expanded test suite in `tests/test_senses.py` (12 tests) and author documentation in `docs/SENSORY_PALETTE.md`.
  - Flags White Room Syndrome (`SNS-101`) and sensory monotony / extreme visual skew (`SNS-102`).
- **Expanded Craft Test Suites**:
  - Expanded `tests/test_climate.py`, `tests/test_ecology.py`, and `tests/test_idioms.py` to 10 tests each.
- **Architectural Decision Records**:
  - Recorded ADR-065 through ADR-069 in `decisions.md`.

## [3.0.0] - 2026-09-21

### Added (Sovereign Studio Desktop Hub, Grand Tour Lifecycle Verification & Offline Flatpak Runtime — Phase 12)
- **Sovereign Studio Desktop Hub** (`arcanum hub`):
  - Implemented `scripts/lib/studio_hub.py` providing a unified offline telemetry cockpit aggregating chapter word counts, lore entity summaries, timeline event counts, paradox detection results, and three-act pacing harmony across the entire Cosmos.
  - Single-file standalone CSP-compliant offline HTML dashboard auto-opens in the system browser with embedded REST API (`GET /api/hub`, `GET /api/chapters`, `GET /api/lore`, `GET /api/timeline`, `POST /api/refresh`).
  - Supports static HTML export (`--export-static FILE`), headless JSON data mode (`--json`), custom `--port` / `--host` binding, and `--no-browser` server mode.
  - Registered as `"studio_hub"` engine in `scripts/lib/registry.py` with CLI aliases: `hub`, `dashboard`, `gui-web`, `studio-hub`.
- **13-Stage Grand Tour End-to-End Lifecycle Verification** (`tests/test_grand_tour_e2e.py`):
  - Implemented the definitive single-test sovereign lifecycle harness covering all 40+ craft engines in sequence: Cosmos/Manuscript scaffolding → Lore Bible population → Multi-chapter authoring → World doctor → Timeline sync → Editorial council → Local RAG retrieval → Fine-tuning dataset synthesis → Branching narrative export → Corpus JSONL/SQLite export → Series omnibus compilation → SMIL media overlays → Release packaging → Studio Hub telemetry cockpit.
  - Validates end-to-end pipeline consistency with 0 world errors, 0 timeline paradoxes, 4 editorial reviews, corpus FTS5 with ≥5 documents, omnibus compilation, SHA-256 verified release archives, and branded CSP-compliant HTML export.
- **Sovereign Offline Flatpak Bundle Builder** (`flatpak/build_offline_bundle.sh`):
  - Implemented shell script generating fully self-contained offline `.flatpak` bundles with Python stdlib runtime module caching, AppStream validation, and `--dry-run` / `--verbose` flags for CI pipeline integration.
- **Documentation & Architectural Decision Records**:
  - Published author guides in `docs/STUDIO_HUB.md` and `docs/GRAND_TOUR.md`.
  - Recorded `ADR-063: Sovereign Studio Hub & Unified Offline Local Webview Architecture` and `ADR-064: Grand Tour End-to-End Lifecycle Verification Architecture` in `decisions.md`.
  - Updated `docs/CHEATSHEET.md` with `arcanum hub` quick reference.
- **Version Elevation**: Full v2.2.0 → v3.0.0 (`scripts/lib/cli.py`, `scripts/arcanum`, `debian/changelog`, `CHANGELOG.md`, `flatpak/org.arsarcanum.ArsArcanum.metainfo.xml`).

## [2.2.0] - 2026-09-21

### Added (Sovereign Local AI Fine-Tuning Studio, Interactive Branching Fiction Graph & Choice Engine — Phase 11)
- **Local AI Fine-Tuning Dataset Synthesizer**:
  - Implemented `scripts/lib/fine_tuning.py` (`arcanum train-data`, `arcanum lora-dataset`) generating fine-tuning datasets in `Alpaca`, `ShareGPT`, `ChatML`, and `Ollama Modelfile` formats from World Bibles and manuscripts.
  - Multi-domain craft instruction generators: Character Persona Q&A, Lore Inquisitor, Prose Continuation, and Arcane Rules Compliance.
  - Automated deterministic train/validation split (`train.jsonl` / `val.jsonl`), token distribution metrics, and draft tag stripping.
- **Interactive Branching Narrative Graph & Choice Engine**:
  - Built `scripts/lib/branching_graph.py` (`arcanum branch`, `arcanum branching`) parsing `@choice:`, `@state:`, `@req:`, and `@ending:` directives.
  - Built topological integrity diagnostics: Dead-End Leaf detection (`BRN-101`), Orphan/Unreachable Passage detection (`BRN-102`), and Missing Target detection (`BRN-105`).
  - Implemented multi-format interactive fiction compilation: Playable HTML5 reader with SVG graph visualizer, Inkle Ink (`.ink`), Twine 2 (`.twee`), and Obsidian Mermaid.
- **Documentation & Architectural Decision Records**:
  - Published author guides in `docs/FINE_TUNING.md` and `docs/BRANCHING_GRAPH.md`.
  - Recorded `ADR-061: Sovereign Local LLM Fine-Tuning & Dataset Synthesis Architecture` and `ADR-062: Interactive Branching Narrative DAG & Multi-Engine Exporter` in `decisions.md`.

## [2.1.0] - 2026-09-21

### Added (Sovereign Local Semantic Retrieval Engine, Speculative Plugin Marketplace & Intelligence — Phase 10)
- **Sovereign Local Semantic Retrieval (RAG) & Lore Engine**:
  - Implemented `scripts/lib/local_rag.py` (`arcanum rag`, `arcanum query-lore`) providing zero-dependency, 100% offline hybrid TF-IDF vector space model and SQLite FTS5 exact keyword retrieval.
  - Generates injection-safe context prompt blocks (`<system_instructions>`, `<canonical_lore_context>`, `<user_query>`) with document and entity attribution for local LLMs (Llama 3, Mistral, Gemma, Phi).
  - Produces multi-format outputs: LLM prompt context, rich Markdown reports, structured JSON datasets, and standalone offline interactive HTML dashboards with strict CSP.
- **Speculative Fiction Plugin Marketplace & Curated Catalog**:
  - Built `scripts/lib/plugin_market.py` (`arcanum market`) and `configs/plugin_catalog.json` featuring curated community craft plugins (`mythic_pantheon`, `linguistic_drift`, `trope_inversion`, `hard_sf_chronometry`, `grimdark_entropy`).
  - Added cryptographic schema verification, syntax checking, and atomic sandbox installation.
- **Documentation & Architectural Decision Records**:
  - Published author guides in `docs/LOCAL_RAG.md` and `docs/PLUGIN_MARKET.md`.
  - Recorded `ADR-059: Sovereign Zero-Dependency Local Semantic Retrieval Engine` and `ADR-060: Speculative Plugin Marketplace & Signed Catalog Architecture` in `decisions.md`.

## [2.0.0] - 2026-09-21

### Added (Sovereign Autonomous Editorial Council, Zen Drafting Studio & Agentic Project OS — Phase 9)
- **Multi-Perspective Autonomous Editorial Council**:
  - Implemented `scripts/lib/editorial_council.py` (`arcanum council`) convening 4 sovereign craft personas: The Master Line Editor (*Lady Cassian*), The Lore & Worldbuilding Inquisitor (*Archon Vaelor*), The Developmental Story Architect (*Grand Architect Soren*), and The Continuity & Canon Overseer (*Chronicler Mirella*).
  - Generates Markdown consensus audit reports and standalone interactive HTML5 visual council dashboards with dissent tracking and prioritized action checklists.
- **Standalone Offline Zen Drafting Studio**:
  - Built `scripts/lib/zen_studio.py` (`arcanum studio`) generating single-file offline HTML5 writing environments featuring distraction-free typewriter drafting, split-screen in-situ World Bible lore drawer, live telemetry, and local persistence.
- **Sovereign Agentic Operating System Manifesto**:
  - Published comprehensive `AGENTS.md` specifying deterministic agent contracts, atomic write guarantees, tool hooks, memory schemas, and self-improving verification pipelines.
  - Published full author guides in `docs/EDITORIAL_COUNCIL.md` and `docs/ZEN_STUDIO.md`.

## [1.9.0] - 2026-09-21

### Added (Flathub Upstream, EPUB 3 Media Overlays & Universal Corpus Exporter — Phase 8)
- **Flathub Upstream AppStream Compliance**:
  - Implemented standard Freedesktop AppStream 0.16+ XML metainfo at `flatpak/org.arsarcanum.ArsArcanum.metainfo.xml` with OARS 1.1 content ratings, metadata licensing (`CC0-1.0`), and release metadata.
  - Registered metainfo installation in `org.arsarcanum.ArsArcanum.yaml` and packaged `docs/FLATHUB_PACKAGING.md`.
- **EPUB 3 SMIL Media Overlays & Synced Audio Narration**:
  - Built `scripts/lib/media_overlay.py` generating standard W3C EPUB 3 `.smil` XML media overlay files pairing text paragraph anchors with audio offsets.
  - Implemented standalone offline interactive HTML5 WebAudio player with real-time karaoke sentence highlighting and speed controls.
- **Universal Structured Corpus & RAG Dataset Exporter**:
  - Built `scripts/lib/corpus_export.py` traversing Cosmos/Universe lore vaults and multi-volume manuscripts.
  - Added multi-format export pipeline: JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`), relational SQLite 3 database (`corpus.db`) with FTS5 full-text search, and master Markdown summary digest (`_corpus_summary.md`).
  - Added comprehensive documentation in `docs/CORPUS_EXPORT.md`.

## [1.6.1] - 2026-09-21

### Fixed & Hardened (Production-Readiness Audit Remediation — Phases 0–7)
- **CI / CD Supply Chain & Workflow Hardening**:
  - Corrected unresolvable action SHAs in `.github/workflows/ci.yml` for `setup-typst` (v4.0.1) and `gitleaks-action` (v2.3.8). Added `.github/dependabot.yml`.
  - Added multi-distribution CI matrix in containers (`ubuntu:22.04`, `ubuntu:24.04`, `debian:12`, `debian:13`, and ARM64).
  - Added headless Xvfb GUI startup verification under `G_DEBUG=fatal-criticals`.
- **Data Safety & Atomic File I/O**:
  - Implemented `atomic_write()` helper in `scripts/lib/fs_utils.py` (`mkstemp` $\to$ `fsync` $\to$ `os.replace` $\to$ parent directory `fsync`), replacing raw writes across all 40+ engines.
  - Re-architected DOCX bidirectional sync in `scripts/lib/docx_sync.py` with `.sync-state.json` hash tracking, safe non-destructive imports, and `.conflict.md` branch isolation.
  - Implemented `filter="data"` safe tar handling in backup/restore routines to prevent path traversal and symlink attacks.
- **Architecture, Maintainability & CLI Dispatch**:
  - Implemented `scripts/lib/registry.py` defining clean Core vs Craft plugin discovery.
  - Ported shell logic to pure-Python engines `scripts/lib/world_doctor.py` and `scripts/lib/concordance.py`.
  - Added unified Python CLI entry point `scripts/lib/cli.py` with rich argparse subcommands.
  - Added structured diagnostic logging with automatic author prose redaction in `scripts/lib/diagnostics.py`.
  - Decoupled GUI views from domain engines via `scripts/lib/ui_controller.py`.
  - Added schema version tracking and automated migration engine `scripts/lib/migrate.py` (`arcanum migrate`).
- **Security & Privacy Hardening**:
  - Created formal STRIDE-lite threat model in `docs/THREAT_MODEL.md`.
  - Injected strict offline Content Security Policy meta tags across all 27 HTML generator engines.
  - Removed static placeholder identities from git authoring in favor of dynamic author git extraction (`git_commit_safe`).
- **Engine Accuracy & Quality Benchmarks**:
  - Created `tests/test_domain_golden_values.py` validating astrophysics, orbital mechanics, planetary insolation, Lanchester combat, and calendar algorithms against scientific benchmarks.
  - Added minimum sample size warnings for short text samples in `scripts/lib/stylistics.py` and `scripts/lib/voice.py`.
  - Created `tests/test_prose_linter_corpus.py` testing precision/recall on labelled prose fixtures.
- **Governance & Packaging**:
  - Added GitHub Issue templates (`.github/ISSUE_TEMPLATE/`), `SUPPORT.md`, and `DEPRECATION.md`.
  - Updated Debian packaging metadata in `debian/control`, `debian/changelog` (v1.6.0-1), and `debian/copyright`.
  - Hardened user CLI symlink management in `scripts/setup_arcanum.sh` and `scripts/uninstall_arcanum.sh`.
  - Expanded test coverage to 281 passing unit tests across 23 test suites.

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


## Phase 3 Update
causality.py and series_continuity.py have been updated with multi-paradigm time-travel validation and custom attribute tracking.