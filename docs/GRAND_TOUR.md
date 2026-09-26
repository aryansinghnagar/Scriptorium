# Ars Arcanum — The Grand Tour: 21-Stage Sovereign Lifecycle Verification

> `tests/test_grand_tour_e2e.py` · **v4.0.0 — The Sovereign Modernization Release** · Full-Pipeline Integration Harness

---

## Overview

The **Grand Tour** is the definitive end-to-end integration test harness for Ars Arcanum. It exercises all craft engines in a single ordered test (`TestGrandTourE2E.test_complete_grand_tour_lifecycle`), verifying that the full sovereign authoring pipeline operates as a coherent integrated system from Cosmos initialization through to multi-bundle release distribution and static telemetry cockpit export.

Each of the 21 stages asserts invariants before proceeding to the next, making it impossible for a downstream stage to silently mask an upstream failure.

---

## Why the Grand Tour Exists

Unit tests verify individual engine correctness in isolation. The Grand Tour answers the harder question: **do all 40+ engines work together as a sovereign authoring operating system?**

Specifically, the Grand Tour catches:

- **API contract regressions**: A parameter rename in `generate_words()` or `export_jsonl()` is caught immediately.
- **Data flow breakage**: If `BranchingNarrativeEngine.load_from_directory()` stops returning chapters, the Stage 9 assertion fails before Stage 10 runs.
- **Cross-engine pipeline integrity**: The corpus exported in Stage 10 and 21 must be consistent with the manuscript authored in Stage 3.
- **Strict offline CSP enforcement**: Verifies that every generated HTML report contains valid Content-Security-Policy headers without external CDNs.
- **Version consistency**: The Grand Tour runs against the current code on every `ruff check` + `mypy` + `unittest discover tests` sweep.

---

## Test Execution

```bash
# Run the Grand Tour standalone
python -m unittest tests/test_grand_tour_e2e.py

# Run as part of the full suite
python -m unittest discover tests
```

Expected output:
```
.
----------------------------------------------------------------------
Ran 1 test in 0.450s

OK
```

---

## The 21 Stages

### Stage 1 — Cosmos Universe & Manuscript Scaffolding
**Engine**: `scripts/lib/worlds.sh` / `scripts/arcanum`

Scaffolds a test Cosmos directory with the canonical directory layout:
```
Aethelgard-Cosmos/
├── universe.yaml
├── Aethelgard-Prime/
│   ├── world.yaml
│   ├── Characters/
│   ├── Places/
│   ├── Magic/
│   └── Factions/
└── Manuscripts/
    └── Book-01-The-Obsidian-Crown/
        └── Draft-01/
            ├── manuscript.yaml
            └── 01_Chapter_01.md
```

**Assert**: Manifests exist and parse cleanly.

---

### Stage 2 — Cosmos Lore Bible Population
**Engine**: Standardized YAML frontmatter note generation

Populates canonical lore entities across four categories:
- `Characters/Lyra_Vael.md`, `Characters/Lord_Malakar.md`
- `Places/Valenreach.md`
- `Magic/Aetheric_Resonance.md` (with hard magic limitations and costs)
- `Factions/Silver_Tribunal.md`

**Assert**: All entity files exist and contain expected frontmatter.

---

### Stage 3 — Multi-Chapter Manuscript Drafting with Directives
**Engine**: Markdown authoring with `@pov`, `@time`, `@choice`, `@state`, and `@req` directives

Authors multiple chapters with embedded narrative metadata and branching choice annotations.

**Assert**: Chapter markdown files exist and contain formatted headings and directives.

---

### Stage 4 — World Doctor Diagnostic Audit
**Engine**: `scripts/lib/world_doctor.py` → `check_world(world_dir)`

Runs deep diagnostic validation across link integrity, YAML schemas, and timeline invariants.

**Assert**: `doc_report["errors"] == 0`.

---

### Stage 5 — Dual-Track Timeline Synchronization
**Engine**: `scripts/lib/timeline_sync.py` → `extract_timeline_events()` + `analyze_timeline_synchronization()`

Extracts chronologic dates vs. narrative sequence and detects temporal bilocation paradoxes.

**Assert**: `total_events >= 2`, `len(paradoxes) == 0`.

---

### Stage 6 — Character Cast & Entity Association
**Engine**: `scripts/lib/dramatis_personae.py` → `scan_character_profiles()`

Extracts all character dossiers and cross-references them against scene mentions.

**Assert**: Profiles extracted and cross-referenced.

---

### Stage 7 — Local Semantic Retrieval (RAG) Indexing & Query
**Engine**: `scripts/lib/local_rag.py` → `LocalLoreRetrievalEngine().load_from_directory()` + `.query()`

Loads the World Bible into hybrid TF-IDF / SQLite FTS5 search index and executes semantic lore queries.

**Assert**: Top match resolves to the queried lore document (`Aetheric_Resonance`).

---

### Stage 8 — Multi-Calendar & Era Chronology
**Engine**: `scripts/lib/calendar.py` → `load_calendar_spec()` + `get_moon_phase()`

Calculates astronomical moon phases and synodic cycles from world calendar configurations.

**Assert**: Moon phases calculate accurately with matching glyphs.

---

### Stage 9 — Interactive Branching Narrative DAG Compilation
**Engine**: `scripts/lib/branching_graph.py` → `BranchingNarrativeEngine().load_from_directory()` + multi-format export

Compiles interactive branching gamebook choices into standalone playable HTML, Ink scripts, Twine Twee, and Mermaid DAGs.

**Assert**: Playable HTML, Ink, Twine, and Mermaid exports generated.

---

### Stage 10 — Universal Corpus Exporter (JSONL, SQLite, Markdown)
**Engine**: `scripts/lib/corpus_export.py` → `CorpusScanner` + `export_jsonl()` + `export_sqlite()` + `export_markdown_summary()`

Scans the cosmos and exports structured JSONL datasets and SQLite databases with FTS5 search indexing.

**Assert**: JSONL, SQLite database, and Markdown digests exported cleanly.

---

### Stage 11 — Multi-Volume Series Omnibus Compilation
**Engine**: `scripts/lib/omnibus.py` → `discover_series_volumes()` + `compile_omnibus_manuscript()`

Discovers all series volumes and compiles an omnibus manuscript with unified frontmatter and unified Table of Contents.

**Assert**: Multi-volume content compiled with unified TOC.

---

### Stage 12 — Release Package Distribution & Manifest
**Engine**: `scripts/package_distribution.py` → `package_reader_edition()`, `package_submission_bundle()`, `package_arc_bundle()`

Packages manuscripts into distributable ZIP bundles with SHA-256 cryptographic verification manifests.

**Assert**: All 3 release packages exist with valid SHA-256 digests.

---

### Stage 13 — Sovereign Studio Desktop Hub Static Telemetry Compilation
**Engine**: `scripts/lib/studio_hub.py` → `collect_studio_hub_data()` + `export_static_studio_hub()`

Compiles live telemetry into a standalone, 100% offline CSP-compliant HTML telemetry dashboard.

**Assert**: HTML dashboard exported with strict Content Security Policy.

---

### Stage 14 — Sovereign Writing Sprint & Session Velocity Analytics
**Engine**: `scripts/lib/writing_sprint.py` → `start_sprint()`, `end_sprint()`, `compute_velocity_stats()`, `generate_sprint_report_html()`

Tracks writing sprint sessions, computes words-per-minute velocity, calculates daily streaks, and renders analytics HTML.

**Assert**: Sprint session state machine cycles cleanly and produces valid analytics.

---

### Stage 15 — Causal DAG Novikov Self-Consistency & Revision Density Heatmap
**Engine**: `scripts/lib/causality.py` + `scripts/lib/revision_heatmap.py`

Audits multi-paradigm causality timelines for closed timelike curves (CTCs) and generates chapter revision churn heatmaps.

**Assert**: Causal graph contains 0 critical paradoxes and revision heatmap generates cleanly.

---

### Stage 16 — Multi-Volume Dramatis Personae Synthesis
**Engine**: `scripts/lib/dramatis_personae.py` → `cross_reference_manuscripts()`, `generate_dramatis_personae_markdown()`, `generate_dramatis_personae_html()`

Synthesizes cross-volume character rosters into Markdown tables and interactive visual character galleries.

**Assert**: Markdown and CSP-compliant HTML cast galleries generated.

---

### Stage 17 — World Codex, Arcane Constraints, Genealogy, Conlang, Factions & Battles
**Engine**:
- `scripts/lib/codex_export.py` (Static single-file offline encyclopedia wiki)
- `scripts/lib/magic_system.py` (Arcane rule consistency validator)
- `scripts/lib/genealogy.py` (Dynastic lineage flowcharts & validation)
- `scripts/lib/conlang.py` (Phonotactics & historical sound shift engine)
- `scripts/lib/factions.py` (Geopolitical diplomacy audit, Lanchester battle simulator, campaign logistics)
- `scripts/lib/calendar.py` (Multi-moon synodic phase calculations)

**Assert**: All 6 craft engines execute with valid outputs and zero fatal errors.

---

### Stage 18 — Story Craft, Journey Modeler, Cartography, Pacing, Structure, Voice & Stylistics
**Engine**:
- `scripts/lib/economy.py` (In-world economy, PPP commodity baskets, tech anachronisms)
- `scripts/lib/journey.py` (Overland travel calculations and journey reports)
- `scripts/lib/cartography.py` (Vector SVG map generation and interactive map viewer)
- `scripts/lib/pacing.py` (Dialogue density, action rhythm, tension curves)
- `scripts/lib/structure.py` (Multi-paradigm structural beat mapping: 3-Act, Save the Cat, Kishōtenketsu)
- `scripts/lib/voice.py` (Character dialogue voice distinctiveness & fingerprinting)
- `scripts/lib/stylistics.py` (Prose craft linting: said-bookisms, adverb tags, word echoes)

**Assert**: All reports generate cleanly with CSP headers.

---

### Stage 19 — Worldbuilding Sciences & Narrative Mechanics Expansion
**Engine**:
- `scripts/lib/ambient.py` (Focus soundscape generator & synthesizer)
- `scripts/lib/tactical_sim.py` (Monte Carlo tactical combat simulator)
- `scripts/lib/scene_mechanics.py` (Motivation-Reaction Unit / MRU analyzer)
- `scripts/lib/plot_matrix.py` (Multi-track plot grid and subplot matrix)
- `scripts/lib/timeline_sync.py` (Narrative vs chronological timeline report)
- `scripts/lib/climate.py` (Planetary insolation, atmospheric circulation, orographic rain shadows)
- `scripts/lib/ecology.py` (Trophic energy pyramids, 10% rule, food-web Mermaid graphs)
- `scripts/lib/stylistics.py` (Cultural idiom and Earth-eponym immersion checker)

**Assert**: Simulation calculations, ecological pyramids, and climate models generate accurately.

---

### Stage 20 — Authoring Studios, Publishing Toolchains & Creative Scaffolding
**Engine**:
- `scripts/lib/concordance.py` (Automatic back-matter glossary and dramatis personae generator)
- `scripts/lib/zen_studio.py` (Distraction-free typewriter studio with in-situ lore drawer)
- `scripts/lib/story_canvas.py` (Interactive visual corkboard and scene card organizer)
- `scripts/lib/omnibus.py` (Multi-volume series omnibus compiler)
- `scripts/lib/portfolio.py` (Multi-manuscript catalog dashboard and velocity analytics)
- `scripts/lib/typography_cleaner.py` (Curly quotes, em-dashes, and ellipsis normalizer)

**Assert**: Generated HTML studios and typography cleaners operate with 100% precision.

---

### Stage 21 — Local Intelligence & Distribution Verification
**Engine**:
- `scripts/lib/branching_graph.py` (Multi-POV narrative subway map exporter)
- `scripts/lib/local_rag.py` (Local semantic retrieval viewer)
- `scripts/lib/corpus_export.py` (Universal corpus JSONL, SQLite database, and Markdown digest)
- `scripts/package_distribution.py` (Codex ZIP release bundle packager)
- `scripts/lib/world_doctor.py` (Deep cosmos integrity audit)

**Assert**: Full suite passes with 0 broken links and verified SHA-256 archive digests.

---

## Verification Pipeline

```bash
# Run the complete test suite
python -m unittest discover tests

# Verify zero lint errors
ruff check .

# Verify type safety
mypy --config-file mypy.ini scripts/lib
```
