# Ars Arcanum — The Grand Tour: 13-Stage Sovereign Lifecycle Verification

> `tests/test_grand_tour_e2e.py` · **v3.0.0 — The Sovereign Zenith Release** · Full-Pipeline Integration Harness

---

## Overview

The **Grand Tour** is the definitive end-to-end integration test harness for Ars Arcanum. It exercises all 40+ craft engines in a single ordered test (`TestGrandTourE2E.test_grand_tour_13_stage_lifecycle`), verifying that the full sovereign authoring pipeline operates as a coherent integrated system from Cosmos initialization through to Studio Hub telemetry cockpit export.

Each of the 13 stages asserts invariants before proceeding to the next, making it impossible for a downstream stage to silently mask an upstream failure.

---

## Why the Grand Tour Exists

Unit tests verify individual engine correctness in isolation. The Grand Tour answers the harder question: **do all 40+ engines work together as a sovereign authoring operating system?**

Specifically, the Grand Tour catches:

- **API contract regressions**: A parameter rename in `conduct_editorial_council()` or `export_fine_tuning_dataset()` is caught immediately.
- **Data flow breakage**: If `BranchingNarrativeEngine.load_from_directory()` stops returning chapters, the Stage 9 assertion fails before Stage 10 runs.
- **Cross-engine pipeline integrity**: The corpus exported in Stage 10 must be consistent with the manuscript authored in Stage 3.
- **Version consistency**: The Grand Tour runs against the current code on every `ruff check` + `mypy` + `unittest discover tests` sweep, ensuring no engine silently drifts out of contract.

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
Ran 1 test in 0.214s

OK
```

---

## The 13 Stages

### Stage 1 — Cosmos & Manuscript Scaffolding
**Engine**: `scripts/lib/worlds.py` (`init_world()`) + `scripts/lib/manuscripts.py` (`init_manuscript()`)

Scaffolds a test Cosmos directory with the canonical directory layout:
```
Aethelgard-Cosmos/
├── Universes/
│   └── Aethelgard-Universe/
│       └── Worlds/
│           └── Aethelgard-World/
├── Manuscripts/
│   └── Book-01-The-Obsidian-Crown/
│       └── Draft-01/
│           └── (chapters placed here)
```

**Assert**: Directories exist. `manuscript.yaml` present with `universe` and `world` keys.

---

### Stage 2 — Lore Bible Population
**Engine**: Filesystem (`pathlib.Path.write_text` + frontmatter)

Creates canonical YAML-frontmattered lore entities across four categories:

| Category | Example Entity |
| :--- | :--- |
| `Characters/` | `Kaelen_Vance.md` with `name`, `role`, `affiliation` |
| `Places/` | `SunCitadel.md` with `name`, `type`, `era` |
| `Magic/` | `Aetheric_Resonance.md` with `name`, `type`, `rules` |
| `Factions/` | `The_Obsidian_Court.md` with `name`, `alignment`, `members` |

**Assert**: All 4 entity files exist and contain expected frontmatter.

---

### Stage 3 — Multi-Chapter Authoring with @-Directives
**Engine**: Filesystem + `@choice`, `@state`, `@time` scene metadata directives

Authors 3 chapters with embedded scene metadata:

```markdown
@pov: Kaelen Vance
@time: 1422 3E, Dawn
@choice: Confront the Archon | Flee through the library
```

**Assert**: All 3 chapter `.md` files exist. Combined word count > 50 words.

---

### Stage 4 — World Doctor Validation
**Engine**: `scripts/lib/world_doctor.py` → `check_world(world_dir)`

Runs the full World Bible validator against the populated lore vault.

**Assert**: `result["errors"]` is an empty list (0 world errors).

---

### Stage 5 — Timeline Extraction & Paradox Analysis
**Engine**: `scripts/lib/timeline_sync.py` → `extract_timeline_events()` + `analyze_timeline_synchronization()`

Extracts all `@time:` directive events from chapters and runs the dual-track synchronizer.

**Assert**: `total_events >= 1`. `len(result["paradoxes"]) == 0` (no bilocation paradoxes).

---

### Stage 6 — Four-Persona Editorial Council
**Engine**: `scripts/lib/editorial_council.py` → `conduct_editorial_council(ms_dir, world_path=world_dir)`

Convenes Lady Cassian (Line Editor), Archon Vaelor (Lore Inquisitor), Grand Architect Soren (Story Architect), and Chronicler Mirella (Continuity Overseer) for a full manuscript review.

**Assert**: `len(report.reviews) == 4`. `report.consensus_score >= 0.0`.

---

### Stage 7 — Local Lore RAG Retrieval
**Engine**: `scripts/lib/local_rag.py` → `LocalLoreRetrievalEngine().load_from_directory()` + `.query()`

Loads the World Bible vault into the hybrid TF-IDF / SQLite FTS5 retrieval engine and queries for the `Aetheric_Resonance` magic entity.

**Assert**: `docs_loaded >= 1`. At least one result has `result.chunk.doc_path` containing `Aetheric_Resonance`.

---

### Stage 8 — Fine-Tuning Dataset Synthesis
**Engine**: `scripts/lib/fine_tuning.py` → `DatasetSynthesizer(cosmos_dir).scan_and_synthesize()` + `export_fine_tuning_dataset(...)`

Synthesizes Alpaca-format instruction-tuning examples from the Cosmos and exports `train.jsonl`, `val.jsonl`, and `Modelfile`.

**Assert**: `examples_count >= 1`. `train.jsonl` exists. `Modelfile` exists.

---

### Stage 9 — Branching Narrative Graph Export
**Engine**: `scripts/lib/branching_graph.py` → `BranchingNarrativeEngine().load_from_directory()` + multi-format export

Loads the manuscript (which contains `@choice:` directives) into the branching narrative engine and compiles to 4 export formats.

**Assert**: `chapters_loaded >= 1`. HTML export string non-empty. Ink export contains `=== `. Twine export contains `:: `. Mermaid export contains `flowchart`.

---

### Stage 10 — Corpus JSONL / SQLite FTS5 Export
**Engine**: `scripts/lib/corpus_export.py` → `CorpusScanner(cosmos_dir).scan()` + `export_jsonl()` + `export_sqlite()` + `export_markdown_summary()`

Scans the entire Cosmos and exports the structured corpus in three formats.

**Assert**: `scanner.documents >= 5`. `documents.jsonl` exists. `corpus.db` exists with FTS5 full-text search. `_corpus_summary.md` exists.

---

### Stage 11 — Series Omnibus & SMIL Media Overlays
**Engine**: `scripts/lib/omnibus.py` → `discover_series_volumes()` + `compile_omnibus_manuscript()` + `scripts/lib/media_overlay.py` → `build_chapter_overlay()` + `generate_smil_xml()`

Discovers the `Book-01` volume, compiles a series omnibus with merged Dramatis Personae, and generates a W3C EPUB 3 SMIL media overlay for the first chapter.

**Assert**: `len(volumes) >= 1`. `omnibus["total_words"] > 0`. SMIL XML contains `<smil`, `<body`, `<seq`.

---

### Stage 12 — Release Packaging
**Engine**: `scripts/lib/package_distribution.py` → `package_reader_edition()` + `package_submission_bundle()` + `package_arc_bundle()`

Packages the manuscript into three release formats with SHA-256 verified archives.

**Assert**: All 3 ZIP archives exist on disk. All 3 `sha256` values are 64-character hex strings.

---

### Stage 13 — Studio Hub Telemetry & Static Export
**Engine**: `scripts/lib/studio_hub.py` → `collect_studio_hub_data()` + `export_static_studio_hub()`

Collects live telemetry from the completed Cosmos and exports a branded CSP-compliant offline HTML dashboard.

**Assert**: `data["project_name"] == "Aethelgard-Cosmos"`. `data["total_chapters"] >= 3`. Static HTML file exists. HTML contains `default-src 'none'` (CSP header). HTML contains `Aethelgard` (project branding).

---

## Test File Location

```
tests/test_grand_tour_e2e.py
```

The test uses `tempfile.mkdtemp()` for all filesystem operations and cleans up after itself regardless of test pass/fail via `addCleanup`.

---

## Adding New Stages

When a new Phase adds a major new engine (e.g. a Phase 13 Conlang Drift Synthesizer), add a **Stage 14** to the Grand Tour:

1. Create lore/manuscript fixtures required by the new engine in an early setup stage.
2. Invoke the new engine's public API functions.
3. Assert the expected invariants (non-empty output, correct schema, no errors).
4. Document the new stage in this file.

---

## Architectural Decision Records

- **ADR-064**: Grand Tour End-to-End Lifecycle Verification Architecture — see [`decisions.md`](../decisions.md).
