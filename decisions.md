# Ars Arcanum (Scriptorium) — Architecture Decision Log

## ADR Index

| ADR | Title | Status | Date | Primary Driver |
| :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Single-Author Local-First Sovereign Operating Model | Accepted | 2026-09-01 | Sovereignty & Zero-Cloud Dependence |
| **ADR-022** | Decoupled Lore Bible and Manuscript Vault Architecture | Accepted | 2026-09-10 | Isolation of prose and worldbuilding |
| **ADR-037** | Atomic POSIX File Operations across all Engines | Accepted | 2026-09-21 | Crash-safety & corruption prevention |
| **ADR-038** | Phased Unified Python CLI & Dispatcher Consolidation | Accepted | 2026-09-21 | Single Authoritative Command Router |
| **ADR-039** | Stream-Verified Backup Archives & Supply-Chain CI Gates | Accepted | 2026-09-21 | Fail-Closed Security & Tamper Detection |
| **ADR-040** | WCAG 2.1 AA Palette Standardization for Redline Diffs | Accepted | 2026-09-21 | Accessibility & Universal Readability |
| **ADR-041** | Modular GTK 3 Package Deconstruction (`ui_gtk3/`) | Accepted | 2026-09-21 | Maintainability & Sub-800 Line Rule |
| **ADR-042** | Cross-Platform Non-Blocking File Locking (`lockfile.py`)| Accepted | 2026-09-21 | Concurrency Protection & Deadlock Prevention |
| **ADR-043** | Multi-Tier Git Submodule Architecture (`.gitmodules`) | Accepted | 2026-09-21 | Clean Git Nesting & CI Portability |
| **ADR-044** | Path Traversal Defense & Volume Sanitization Invariants | Accepted | 2026-09-21 | Safe Filesystem Boundaries & Injection Defense |
| **ADR-045** | Sovereign GPG Symmetric & Asymmetric Backup Encryption | Accepted | 2026-09-21 | Cryptographic Confidentiality & Disaster Recovery |
| **ADR-046** | Multi-Distribution Packaging Architecture (Debian, RPM, AUR) | Accepted | 2026-09-21 | Native Multi-Distro Package Availability |
| **ADR-047** | Automated Systemd User Backup Units (`arcanum-backup`) | Accepted | 2026-09-21 | Non-Intrusive Background Backups |
| **ADR-048** | Speculative Fiction & Worldbuilding Plugin Architecture | Accepted | 2026-09-21 | Extensibility & Zero-Pip Domain Linters |
| **ADR-049** | Universal Multi-Paradigm Story Structure Engine | Accepted | 2026-09-21 | 9 Canonical Narrative Models & East Asian Kishotenketsu |
| **ADR-050** | Interactive Visual Story Canvas & Drag-and-Drop Corkboard | Accepted | 2026-09-21 | Visual Brainstorming & Dynamic Pacing Harmony |
| **ADR-051** | Dual-Track Chronological vs. Narrative Timeline Synchronizer | Accepted | 2026-09-21 | Flashback Resolution & Bilocation Paradox Defense |
| **ADR-052** | Multi-Volume Series Omnibus Compilation Engine | Accepted | 2026-09-21 | Saga Assembly & Cross-Volume Dramatis Personae |
| **ADR-053** | Freedesktop AppStream 0.16+ Metainfo & Flathub Upstream | Accepted | 2026-09-21 | Universal Sandboxed Flathub Packaging |
| **ADR-054** | EPUB 3 SMIL Media Overlays & Synced Audio Narration Engine | Accepted | 2026-09-21 | W3C Media Overlays 3.0 & Offline Audio Proofreading |
| **ADR-055** | Universal Structured Corpus & Local RAG Dataset Exporter | Accepted | 2026-09-21 | Sovereign JSONL/SQLite Datasets for Local AI/RAG |
| **ADR-056** | Multi-Perspective Autonomous Editorial Council Engine | Accepted | 2026-09-21 | Multi-Persona Workshop & Consensus Scoring |
| **ADR-057** | Standalone Offline Zen Drafting Studio & Lore Drawer | Accepted | 2026-09-21 | Focused Typewriter Writing & In-Situ Lore Inspection |
| **ADR-058** | Sovereign Agentic Operating System Architecture & Contracts | Accepted | 2026-09-21 | AGENTS.md Invariants & Momentum Compounding |
| **ADR-059** | Sovereign Zero-Dependency Local Semantic Retrieval Engine | Accepted | 2026-09-21 | Hybrid TF-IDF & FTS5 Offline Lore Recall |
| **ADR-060** | Speculative Plugin Marketplace & Signed Catalog Architecture | Accepted | 2026-09-21 | Extensible Offline Plugin Ecosystem |
| **ADR-061** | Sovereign Local LLM Fine-Tuning & Dataset Synthesis Architecture | Accepted | 2026-09-21 | Private Canon Fine-Tuning & LoRA Dataset Generation |
| **ADR-062** | Interactive Branching Narrative DAG & Multi-Engine Exporter | Accepted | 2026-09-21 | HTML5 / Ink / Twine / Mermaid Gamebook Compilation |
| **ADR-063** | Sovereign Studio Hub & Unified Offline Local Webview Architecture | Accepted | 2026-09-21 | Unified Telemetry Cockpit & REST API for All Engines |
| **ADR-064** | Grand Tour End-to-End Lifecycle Verification Architecture | Accepted | 2026-09-21 | 13-Stage Full-Pipeline Integration Test Harness |
| **ADR-065** | Sovereign Writing Sprint & Session Analytics Architecture | Accepted | 2026-09-22 | Atomic Productivity Tracking & WPM Velocity Dashboard |
| **ADR-066** | Manuscript Revision Density & Churn Heatmap Engine | Accepted | 2026-09-22 | Snapshot Churn Analysis & Over/Under-Revision Detection |
| **ADR-067** | Causal DAG & Novikov Self-Consistency Architecture | Accepted | 2026-09-22 | Causal Loops, CTCs & Multiverse Branch Analysis |
| **ADR-068** | Prophecy Resolution Matrix & Arcane Inscription Tracker | Accepted | 2026-09-22 | Prophecy Clause Tracking & Chosen One Validation |
| **ADR-069** | 6D Sensory Palette Immersion & White Room Syndrome Architecture | Accepted | 2026-09-22 | 6D Sensory Analysis & White Room Syndrome Detection |
| **ADR-070** | Flathub Upstream Packaging Validation & Offline Bundle Pipeline | Accepted | 2026-09-22 | AppStream 0.16+ Standards Compliance & Flathub Upstream |
| **ADR-071** | Cosmos Archive Freeze & Cryptographic Provenance Sealer | Accepted | 2026-09-22 | Merkle-Root SHA-256 Vault Sealing & Tamper Detection |
| **ADR-072** | Multi-Volume Dramatis Personae & Universe Cast Matrix | Accepted | 2026-09-22 | Cross-Volume Character Dossiers & Lifecycle Continuity |
| **ADR-073** | Static World Wiki & Offline Codex Exporter Architecture | Accepted | 2026-09-22 | Standalone World Encylopedia & JSON Search Index |
| **ADR-074** | Hard Magic Systems & Arcane Constraint Matrix | Accepted | 2026-09-22 | Metaphysical Rules, Catalysts & Fatigue Validation |
| **ADR-075** | In-World Cryptographic Ciphers & Phonetic Rune Engine | Accepted | 2026-09-22 | Ciphers, Elder Futhark Runes & SVG Visual Cards |
| **ADR-076** | Dynastic Genealogies & Succession Lineage Architecture | Accepted | 2026-09-22 | Family Tree DAGs, Biological Paradoxes & Succession |
| **ADR-077** | Conlang Phonotactics & Historical Sound-Change Engine | Accepted | 2026-09-22 | Syllable Templates, Sound Laws & Lexicon Manager |
| **ADR-078** | Geopolitical Faction Matrix & Campaign Logistics Architecture | Accepted | 2026-09-22 | Diplomatic Triads, Lanchester Combat & Logistics |
| **ADR-079** | Custom Planetary Calendars & Multi-Moon Synodic Engine | Accepted | 2026-09-22 | Planetary Years, Synodic Phases & Conjunctions |
| **ADR-080** | In-World Macroeconomics & Anachronism Matrix Architecture | Accepted | 2026-09-22 | Purchasing Power Parity, Trade Margins & Tech Audits |
| **ADR-081** | Overland, Naval & Aerial Journey Expedition Modeler | Accepted | 2026-09-22 | Terrain Friction, Paces & Supply Consumption |
| **ADR-082** | Offline Vector Cartography & Interactive Map Viewer | Accepted | 2026-09-22 | Vector SVG Maps, Biomes & Interactive Pan/Zoom |
| **ADR-083** | Narrative Pacing, POV Balance & Tension Arc Modeling | Accepted | 2026-09-22 | Dialogue Density, POV Starvation & Tension Curves |
| **ADR-084** | Multi-Paradigm Story Structure & Beat Sheet Enforcer | Accepted | 2026-09-22 | 9 Narrative Models, Drift Windows & Harmony Scoring |
| **ADR-085** | Character Voice Profiler & Dialogue Fingerprint Engine | Accepted | 2026-09-22 | TTR, Formality, Contractions & Voice Bleed Alerts |
| **ADR-086** | Stylistics, Dialogue Mechanics & Readability Rhythm Engine | Accepted | 2026-09-22 | Said-Bookisms, Word Echoes & Readability Indices |
| **ADR-087** | Focus Ambient & Binaural Soundscape Generator | Accepted | 2026-09-24 | Procedural WAV Synthesis & Offline WebAudio Studio |
| **ADR-088** | Dynamic Tactical Combat & Monte Carlo Skirmish Engine | Accepted | 2026-09-24 | Unit Combat Attributes, Terrain Modifiers & Monte Carlo |
| **ADR-089** | Motivation-Reaction Unit (MRU) Scene Mechanics Analyzer | Accepted | 2026-09-24 | Swain & Butcher MRU Linters & Scene/Sequel Anatomy |
| **ADR-090** | Multi-Track Narrative Plot Grid & Subplot Matrix Engine | Accepted | 2026-09-24 | Subplot Health, Dormancy Alerts & SVG Plot Grid |
| **ADR-091** | Dual-Track Chronological vs. Narrative Timeline Synchronizer | Accepted | 2026-09-24 | Temporal Anchors, Flashbacks & Bilocation Paradoxes |
| **ADR-092** | Planetary Climate, Orographic Rain Shadow & Köppen Biomes | Accepted | 2026-09-24 | Insolation, Atmospheric Cells & Rain Shadow Deserts |
| **ADR-093** | Trophic Food Web Ecology & Biomass Efficiency Simulator | Accepted | 2026-09-24 | Food Web Graphs, Lindeman 10% Rule & Trophic Audits |
| **ADR-094** | Earth Idiom & Immersion-Breaking Eponym Linter | Accepted | 2026-09-24 | Eponyms, Myth References & In-World Suggestions |
| **ADR-095** | Back-Matter Concordance & Dramatis Personae Indexer | Accepted | 2026-09-24 | Automated Lore Back-Matter & Cross-Volume Concordance |
| **ADR-096** | Sovereign Zen Drafting Studio & In-Situ Lore Drawer | Accepted | 2026-09-24 | Standalone Offline Drafting & In-Situ World Lore |
| **ADR-097** | Visual Story Canvas & Multi-Paradigm Corkboard | Accepted | 2026-09-24 | 9 Story Paradigms, Drag-and-Drop & Pacing Harmony |
| **ADR-098** | Multi-Volume Series Omnibus Compilation Engine | Accepted | 2026-09-24 | Multi-Book Series Assembly & Master TOC Generation |
| **ADR-099** | Author Portfolio & Catalog Analytics Dashboard | Accepted | 2026-09-24 | Multi-Project Velocity, Rollups & Lifecycle Stages |
| **ADR-100** | EPUB 3 SMIL Media Overlays & Synchronized Narration Player | Accepted | 2026-09-24 | W3C SMIL 3.0 Audio Narration & Speech Synthesis |
| **ADR-101** | Smart Typography Normalizer & Punctuation Engine | Accepted | 2026-09-24 | Publication-Grade Quotes, Dashes & Whitespace Polish |
| **ADR-102** | ISBN-13 Vector SVG/PNG Barcode Engine | Accepted | 2026-09-24 | Pure-Python Vector EAN-13 & Bookland Barcodes |
| **ADR-103** | Interactive Branching Narrative DAG & Choice Engine | Accepted | 2026-09-25 | Multi-Engine Gamebook Compilation & Choice DAGs |
| **ADR-104** | Local Semantic Retrieval (RAG) & Lore Recall Engine | Accepted | 2026-09-25 | Zero-Pip Hybrid TF-IDF & SQLite FTS5 Vector Engine |
| **ADR-105** | Multi-Perspective Autonomous Editorial Council | Accepted | 2026-09-25 | Multi-Persona Workshop & Consensus Scoring |
| **ADR-106** | Local AI Fine-Tuning & Dataset Synthesizer | Accepted | 2026-09-25 | Private Instruction Fine-Tuning & Modelfiles |
| **ADR-107** | Universal Structured Corpus & RAG Dataset Exporter | Accepted | 2026-09-25 | JSONL, SQLite FTS5 & Markdown Executive Summaries |
| **ADR-108** | Offline Neural TTS & Audio Proofreader | Accepted | 2026-09-25 | Web SpeechSynthesis & Host Speech Toolchains |
| **ADR-109** | Multi-Platform Distribution Packaging Engine | Accepted | 2026-09-25 | Reader, Submission, ARC & Lore Codex Packaging |
| **ADR-110** | World Doctor & Cosmos Integrity Diagnostics | Accepted | 2026-09-25 | 8-Point Cross-Validation Diagnostics Suite |
| **ADR-111** | Granular Architectural Trimming and Redundancy Decommissioning | Accepted | 2026-09-26 | Streamlined Codebase & Dead Code Elimination |
| **ADR-112** | Non-Imposing Creative Advisory Paradigm | Accepted | 2026-09-26 | Advisory-First Diagnostics & Author Sovereignty |
| **ADR-113** | Expanded Astrophysics, Climate Linkages & Multi-Calendar Chronology | Accepted | 2026-09-26 | Exotic Planetary Systems & Continuous Epochs |
| **ADR-114** | Multi-POV Narrative Threading, Bidirectional Vault Restore & Interactive Cartography | Accepted | 2026-09-26 | Subway Maps, Graph Cartography & Vault Restore |
| **ADR-115** | Advisory-First Creative Freedom Architecture & Integrated Craft Documentation | Accepted | 2026-09-26 | Multi-Pathway Guidance, `arcanum doc` & Studio Craft Guide |

---

### ADR-038: Phased Unified Python CLI & Dispatcher Consolidation
- **Context**: The audit identified dual-dispatcher drift between `scripts/arcanum` (Bash, 725 lines) and `scripts/lib/cli.py` (Python).
- **Decision**: Make `scripts/lib/cli.py` the authoritative command router across all subcommands, reducing `scripts/arcanum` to a lightweight bootstrap script.
- **Consequences**: Single source of truth for argument parsing, rich help output, and zero duplicate dispatch tables.

### ADR-039: Stream-Verified Backup Archives & Supply-Chain CI Gates
- **Context**: Backup SHA-256 calculation was previously run on the archive file without verifying archive structure with `tar -tzf`, and plugin SHA-256 hashes were recorded in `dependencies.lock` without a dedicated CI verification test.
- **Decision**: Validate archive readability via `tar -tzf` before generating hashes and add automated test `tests/test_supply_chain.py` asserting all plugin digests on every CI push.
- **Consequences**: Tampered, incomplete, or corrupted archives are aborted immediately.

### ADR-041: Modular GTK 3 Package Deconstruction (`ui_gtk3/`)
- **Context**: `scripts/lib/ui_gtk3.py` had expanded into a 3,873-line monolith, violating maintainability limits and making UI extensions error-prone.
- **Decision**: Decompose into a structured presentation package `scripts/lib/ui_gtk3/` (`common.py`, `workers.py`, `cli_bridge.py`, `dialogs.py`, `window.py`, `studios/*.py`) with `ui_gtk3.py` acting as a backward-compatible facade.
- **Consequences**: Every file in the UI package is sub-800 lines with clean separation of concerns and testability.

### ADR-042: Cross-Platform Non-Blocking File Locking (`lockfile.py`)
- **Context**: Concurrent snapshots or background processes could race when modifying world or manuscript repositories.
- **Decision**: Implement `ArcanumLock` using POSIX `fcntl.flock` on Linux/macOS and `msvcrt.locking` on Windows, with configurable timeouts and RAII context management.
- **Consequences**: Race conditions and lock file staleness are prevented without external dependencies.

### ADR-043: Multi-Tier Git Submodule Architecture (`.gitmodules`)
- **Context**: Scaffolding scripts initialized nested Git repositories without registering them in `.gitmodules`, causing Git to treat them as untracked embedded gitlinks.
- **Decision**: Automatically write relative `.gitmodules` entries in parent repositories whenever nested child repositories (`Universes -> Worlds -> Manuscripts -> Books`) are created.
- **Consequences**: Standard Git tooling and CI environments can traverse and clone nested authorial projects without warnings.

### ADR-044: Path Traversal Defense & Volume Sanitization Invariants
- **Context**: CLI volume parameters and chapter targets (`-b`, `--book`) were passed directly to filesystem joins without strict path traversal checks, posing directory traversal risks.
- **Decision**: Implement strict regex token validation `[A-Za-z0-9_-]+` and reject `..`, `/`, `\` in both Bash (`arcanum_validate_volume_name`) and Python (`validate_volume_name`), validating all inputs before filesystem resolution across export, diff, concordance, draft init, and pacing engines.
- **Consequences**: Deterministic isolation of manuscript volumes and complete protection against path escape and directory traversal attacks.

### ADR-045: Sovereign GPG Symmetric & Asymmetric Backup Encryption
- **Context**: Backups contained raw unencrypted prose and lore files, creating potential privacy exposures on remote mirrors or unencrypted USB targets.
- **Decision**: Provide optional GPG encryption in `backup_world.sh` (`--symmetric`, `--encrypt [KEY_ID]`, `--passphrase`) producing `.tar.gz.gpg` archives, with verified SHA-256 sidecars, encryption metadata in `.meta.json`, and automated decryption in `restore_world.sh`.
- **Consequences**: Authors gain military-grade AES-256/RSA privacy for sensitive unpublished manuscripts and lore with zero external pip dependencies.

### ADR-046: Multi-Distribution Packaging Architecture (Debian, RPM, Arch AUR)
- **Context**: Tier-1 distribution was limited to Debian/Ubuntu `apt`, blocking installation on Fedora/RHEL (`dnf`), Arch Linux (`pacman`), and openSUSE (`zypper`).
- **Decision**: Implement native multi-distribution package management in `setup_arcanum.sh`, build-ready Arch Linux AUR `pkg/arch/PKGBUILD`, and RPM spec file `pkg/rpm/ars-arcanum.spec` with unified file layout and permissions.
- **Consequences**: Authors on any major Linux distribution can install Ars Arcanum natively through their distro package manager.

### ADR-047: Automated Systemd User Backup Units (`arcanum-backup.{service,timer}`)
- **Context**: Authors required scheduled, non-intrusive background backups without cron daemon complexity or third-party background services.
- **Decision**: Ship unprivileged systemd user unit definitions in `configs/systemd/` (`arcanum-backup.service` and `arcanum-backup.timer`) that trigger `arcanum backup --all` with idle IO scheduling priority, with 1-click activation via `setup_arcanum.sh --enable-timer`.
- **Consequences**: Robust, low-overhead daily background backups that run automatically in user space without requiring root privileges.

### ADR-048: Speculative Fiction & Worldbuilding Plugin Architecture (`scripts/lib/plugins.py`)
- **Context**: Community worldbuilders and speculative fiction authors needed to write custom validation rules, world lore linters, and craft metrics without modifying core codebase files.
- **Decision**: Implement a zero-pip, declarative plugin architecture (`plugin.json` + `plugin.py`) supporting multi-tier search paths (`configs/plugins/`, `~/.config/ars-arcanum/plugins/`, `/usr/share/ars-arcanum/plugins/`), error-isolated lifecycle hooks (`hook_validate_entity`, `hook_validate_manuscript`, `hook_custom_metric`), scaffolding tools, and reference plugins (`speculative_naming`, `magic_system_audit`, `pacing_heat_map`).
- **Consequences**: Authors can create and distribute domain-specific speculative craft plugins that run safely without risking application crashes or manuscript corruption.

### ADR-049: Universal Multi-Paradigm Story Structure Engine (`scripts/lib/structure.py`)
- **Context**: Narrative structure was previously limited to five Western paradigms, excluding non-conflict structures and standard cinematic sequence models.
- **Decision**: Expand `structure.py` and the CLI (`arcanum structure`) to nine canonical narrative models, adding the 8-Sequence Method (Gulino/Daniel), Fichtean Curve, Kishōtenketsu (起承転結), and Freytag's Dramatic Pyramid, with proportional word count mapping and interactive HTML beat maps.
- **Consequences**: Writers working across global narrative traditions (East Asian Kishōtenketsu, Hollywood 8-Sequence, classic dramatic arcs) have precise mathematical pacing tools tailored to their structural philosophy.

### ADR-050: Interactive Visual Story Canvas & Offline Drag-and-Drop Corkboard (`scripts/lib/story_canvas.py`)
- **Context**: Authors required a visual, intuitive corkboard to arrange scenes, inspect POV pacing, and adjust narrative beats without leaving their local environment or requiring internet connectivity.
- **Decision**: Ship `scripts/lib/story_canvas.py` producing self-contained HTML5/SVG interactive corkboards with client-side drag-and-drop, dynamic act/beat lane alignment, live pacing harmony score recalculation, and chapter reordering manifest export.
- **Consequences**: Writers can visually brainstorm and restructure manuscripts in their favorite browser with 100% offline privacy and zero external JavaScript dependencies.

### ADR-051: Dual-Track Chronological vs. Narrative Timeline Synchronization (`scripts/lib/timeline_sync.py`)
- **Context**: Non-linear narratives, flashbacks, and multi-POV epics often develop temporal discrepancies between reading order and in-universe chronological history.
- **Decision**: Implement `scripts/lib/timeline_sync.py` parsing `@time:` directives, calendar epochs, and scene sequences into parallel Narrative and Chronological timelines, with automatic flashback/flash-forward detection and bilocation paradox validation.
- **Consequences**: Authors have automated consistency verification for complex timelines and parallel character movements across their universes.

### ADR-052: Multi-Volume Series Omnibus Compilation Engine (`scripts/lib/omnibus.py`)
- **Context**: Compiling multi-book series into unified omnibus editions required manual chapter concatenation, duplicate frontmatter scrubbing, and tedious character index reconciliation.
- **Decision**: Create `scripts/lib/omnibus.py` discovering all volumes/books in a universe/cosmos, synthesizing a master Table of Contents with subtitle partitions, compiling a unified cross-volume Dramatis Personae, and assembling publication-ready master Markdown and HTML reader documents.
- **Consequences**: Series authors can publish complete saga bundles with one command while preserving canonical continuity and formatting integrity.

### ADR-053: Freedesktop AppStream 0.16+ Metainfo & Flathub Upstream Delivery (`flatpak/org.arsarcanum.ArsArcanum.metainfo.xml`)
- **Context**: Distributing Ars Arcanum on Flathub and modern Linux software centers (GNOME Software, KDE Discover) requires compliant AppStream metainfo, CC0-1.0 metadata licensing, OARS 1.1 age ratings, screenshots, and semver release history.
- **Decision**: Create `flatpak/org.arsarcanum.ArsArcanum.metainfo.xml` conforming strictly to AppStream 0.16+ specifications, install it to `/app/share/metainfo/` in `org.arsarcanum.ArsArcanum.yaml`, and enforce validity with `tests/test_flathub_upstream.py`.
- **Consequences**: Ars Arcanum is directly submit-ready to Flathub upstream and renders rich metadata across all Linux app stores.

### ADR-054: EPUB 3 SMIL Media Overlays & Synced Audio Narration Engine (`scripts/lib/media_overlay.py`)
- **Context**: Authors and audiobook producers require synchronized text and audio playback for proofreading, accessible reading, and professional EPUB 3.0 Media Overlay production without relying on cloud transcription services.
- **Decision**: Build `scripts/lib/media_overlay.py` to synthesize IDPF/W3C standard `.smil` XML files linking XHTML paragraph IDs to audio clip offsets, and generate self-contained offline HTML5 WebAudio narration players with real-time sentence karaoke highlighting.
- **Consequences**: Writers have offline, zero-telemetry synchronized audio proofreading and production-grade EPUB 3 Media Overlays compliant with major ereaders.

### ADR-055: Universal Structured Corpus & Local RAG Dataset Compilation Architecture (`scripts/lib/corpus_export.py`)
- **Context**: Authors need to query and analyze vast lore bibles and manuscripts using offline local LLMs (e.g. Llama, Mistral, Gemma) or vector search engines without leaking private creative intellectual property to third-party cloud APIs.
- **Decision**: Create `scripts/lib/corpus_export.py` (`arcanum corpus export`) providing automated repository scanning, heading-aware semantic chunking, entity cross-reference graph extraction, and multi-format exports to JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`), SQLite 3 relational database (`corpus.db` with FTS5 full-text search), and markdown summary digests (`_corpus_summary.md`).
- **Consequences**: Complete sovereignty over creative AI datasets, sub-millisecond local full-text search, and standardized dataset structures for embedding models and archival research.

### ADR-056: Multi-Perspective Autonomous Editorial Council Engine (`scripts/lib/editorial_council.py`)
- **Context**: Comprehensive manuscript revision requires evaluating prose at multiple distinct altitudes (sentence rhythm, sensory palette, worldbuilding rules, narrative paradigm beats, and canon continuity), which single-pass audits fail to adequately represent.
- **Decision**: Implement `scripts/lib/editorial_council.py` (`arcanum council`) convening four autonomous craft personas (Line Editor, Lore Inquisitor, Story Architect, Continuity Overseer), calculating a weighted readiness score ($0-100\%$), flagging chamber dissents ($\ge 12$ pt variance), and generating both Markdown and interactive HTML5 dashboards with actionable checklists.
- **Consequences**: Authors receive multi-perspective workshop feedback locally with zero telemetry, complete privacy, and prioritized revision steps.

### ADR-057: Standalone Offline Zen Drafting Studio & In-Situ Lore Inspector (`scripts/lib/zen_studio.py`)
- **Context**: Authors drafting new scenes need distraction-free typewriter environments without losing instant access to character sheets, faction allegiances, and worldbuilding lore.
- **Decision**: Create `scripts/lib/zen_studio.py` (`arcanum studio`) compiling manuscripts and World Bibles into a single-file offline HTML5 application featuring typewriter scrolling, split-pane lore search, real-time reading/narration telemetry, and browser localStorage persistence with one-click Markdown export.
- **Consequences**: Authors have a zero-install, portable writing studio that runs anywhere in modern browsers under strict Content Security Policies.

### ADR-058: Sovereign Agentic Operating System Architecture & Contracts (`AGENTS.md`)
- **Context**: Building and maintaining a complex, multi-tiered authoring operating system requires explicit engineering contracts, momentum compounding, and deterministic rails across all tool interactions and subagent delegations.
- **Decision**: Codify repository doctrine in `AGENTS.md` declaring atomic write invariants, cross-platform file locking (`ArcanumLock`), regex path traversal defense, 100% offline zero-pip execution, and persistent momentum queues (`now`, `next`, `blocked`, `improve`, `recurring`).
- **Consequences**: The repository operates under rigorous agentic software engineering standards with zero regressions, guaranteed reproducibility, and compounding architectural capability.

### ADR-059: Sovereign Zero-Dependency Local Semantic Retrieval Engine (`scripts/lib/local_rag.py`)
- **Context**: Authors querying extensive World Bibles and multi-volume sagas need natural language semantic retrieval and LLM context synthesis without sending confidential unpublished creative IP to cloud vector databases (e.g. Pinecone, ChromaDB Cloud, OpenAI).
- **Decision**: Implement `scripts/lib/local_rag.py` (`arcanum rag`, `arcanum query-lore`) using standard library Python math (`math`, `collections.Counter`) and SQLite FTS5 for hybrid vector cosine similarity + exact keyword scoring. Synthesize injection-safe prompt context blocks (`<system_instructions>`, `<canonical_lore_context>`, `<user_query>`) with document and entity provenance for local LLMs (Llama 3, Mistral, Gemma, Phi).
- **Consequences**: Authors gain sub-millisecond offline semantic lore recall and standardized prompt extraction with 0 pip dependencies and 100% data privacy.

### ADR-060: Speculative Plugin Marketplace & Signed Catalog Architecture (`scripts/lib/plugin_market.py`)
- **Context**: Distributing community-crafted narrative tools, speculative fiction validators (pantheons, conlang drift, trope subverters), and custom metrics required a standardized discovery catalog with integrity verification and sandbox installation.
- **Decision**: Build `scripts/lib/plugin_market.py` (`arcanum market`) and `configs/plugin_catalog.json` providing offline catalog inspection, category filtering, AST syntax verification, and atomic user-space installation to `configs/plugins/` or `~/.config/ars-arcanum/plugins/`.
- **Consequences**: The Ars Arcanum plugin ecosystem is easily extensible and safe from corrupted or malformed community plugins.

### ADR-061: Sovereign Local LLM Fine-Tuning & Dataset Synthesis Architecture (`scripts/lib/fine_tuning.py`)
- **Context**: Authors training or fine-tuning local open-weights LLMs (via LoRA, QLoRA, Unsloth, Ollama) on their private fictional universe required automated generation of instruction-tuning prompt/completion pairs without cloud telemetry.
- **Decision**: Implement `scripts/lib/fine_tuning.py` (`arcanum train-data`, `arcanum lora-dataset`) generating `Alpaca`, `ShareGPT`, `ChatML`, and `Ollama Modelfile` datasets across four craft domains (character persona, lore Q&A, scene prose continuation, and magic constraint rules) with automated deterministic train/val splits and draft directive sanitization.
- **Consequences**: Creative writers can train custom offline LLMs directly on their personal canon with zero leakage of private creative intellectual property.

### ADR-062: Interactive Branching Narrative DAG & Multi-Engine Exporter (`scripts/lib/branching_graph.py`)
- **Context**: Interactive fiction, gamebook, and choose-your-own-adventure authors needed a unified way to write branching choices in standard Markdown while validating graph reachability, dead-ends, and compiling to standard engines (Playable HTML, Ink, Twine, Mermaid).
- **Decision**: Build `scripts/lib/branching_graph.py` (`arcanum branch`, `arcanum branching`) parsing `@choice:`, `@state:`, `@req:`, and `@ending:` tags, verifying graph connectivity via breadth-first search reachability, and compiling to standalone offline HTML5 gamebooks, Inkle Ink (`.ink`), Twine 2 (`.twee`), and Mermaid flowcharts.
- **Consequences**: Authors have an industrial-grade branching narrative pipeline that catches structural writing defects early and produces multi-platform playable interactive fiction with 0 external dependencies.

### ADR-063: Sovereign Studio Hub & Unified Offline Local Webview Architecture (`scripts/lib/studio_hub.py`)
- **Context**: With 40+ specialized craft engines spanning lore, timeline, editorial, RAG retrieval, fine-tuning, branching narrative, corpus export, omnibus, and media overlays, authors needed a single unified dashboard to monitor the health, productivity metrics, and pacing harmony of their entire Cosmos without switching between individual engine commands.
- **Decision**: Implement `scripts/lib/studio_hub.py` (`arcanum hub`) using Python's standard library `http.server` and `threading` to serve a zero-dependency single-file offline HTML5 telemetry cockpit. The dashboard aggregates chapter word counts, lore entity summaries by category, timeline event counts with paradox alerts, three-act structure pacing curves, and real-time engine status from the live filesystem. Expose a REST API (`GET /api/hub`, `GET /api/chapters`, `GET /api/lore`, `GET /api/timeline`, `POST /api/refresh`) for programmatic integration. Register CLI aliases `hub`, `dashboard`, `gui-web`, `studio-hub`.
- **Consequences**: Authors get a live at-a-glance telemetry view of their sovereign writing OS from a single browser tab. The `--export-static FILE` mode generates a shareable, self-contained offline HTML snapshot. The `--json` mode enables headless CI telemetry collection without opening a browser.

### ADR-064: Grand Tour End-to-End Lifecycle Verification Architecture (`tests/test_grand_tour_e2e.py`)
- **Context**: With 40+ interconnected craft engines, individual unit tests provided adequate coverage of engine correctness but could not verify that the full sovereign authoring pipeline — from Cosmos initialization through to Studio Hub telemetry — operated as an integrated system without silent data loss or API contract breakage between engines.
- **Decision**: Implement a single comprehensive end-to-end test (`TestGrandTourE2E.test_grand_tour_13_stage_lifecycle`) exercising 13 ordered lifecycle stages: (1) Cosmos/Manuscript scaffolding, (2) Lore Bible population with Characters/Places/Magic/Factions, (3) Multi-chapter authoring with `@choice`/`@state` directives, (4) `check_world()` validation, (5) Timeline event extraction and paradox analysis, (6) Four-persona Editorial Council, (7) Local RAG lore retrieval by `doc_path`, (8) Fine-tuning dataset synthesis (`Alpaca` + Modelfile), (9) Branching narrative graph export to HTML/Ink/Twine/Mermaid, (10) Corpus JSONL/SQLite FTS5 export, (11) Series omnibus compilation with SMIL media overlays, (12) Release packaging (Reader/Submission/ARC ZIP bundles with SHA-256), (13) Studio Hub telemetry collection and CSP-compliant static HTML export. Each stage asserts invariants before proceeding to the next.
- **Consequences**: Any regression in an individual engine's public API contract or data contract with a downstream engine will be caught immediately by the Grand Tour harness, providing a single authoritative signal for sovereign pipeline integrity.

### ADR-065: Sovereign Writing Sprint & Session Analytics Architecture (`scripts/lib/writing_sprint.py`)
- **Context**: Writers seeking structured focus sessions (e.g. Pomodoro, 15/30-minute word sprints) lacked an offline, atomic tracking mechanism integrated with the project filesystem that could calculate words-per-minute (WPM) velocity and writing streaks without background daemons.
- **Decision**: Implement `scripts/lib/writing_sprint.py` (`arcanum sprint`) using atomic filesystem state (`.sprint_state.json`) and an append-only JSONL log (`.sprint_log.jsonl`). Provide commands for starting, ending, querying status, calculating velocity stats, and rendering offline CSP-compliant HTML sprint reports with daily streaks and WPM trend indicators.
- **Consequences**: Authors have an offline productivity tracker tightly scoped to each manuscript project with zero external dependencies or cloud telemetry.

### ADR-066: Manuscript Revision Density & Churn Heatmap Engine (`scripts/lib/revision_heatmap.py`)
- **Context**: During manuscript editing, authors need objective visibility into which chapters are undergoing extensive rewriting (potential structural instability) and which chapters remain untouched since the initial draft (potential continuity drift).
- **Decision**: Implement `scripts/lib/revision_heatmap.py` (`arcanum revision-heatmap`) comparing active draft files against milestone backups using standard library `difflib.unified_diff`. Calculate normalized churn ratios and assign diagnostic codes: `REV-101` (Over-Revised chapter $> 3\times$ average churn) and `REV-102` (Pristine chapter with 0 modifications on $>50$ words). Render offline CSP-compliant color-graded HTML heatmaps.
- **Consequences**: Authors gain structural editing clarity and can balance editorial effort across the manuscript without third-party version control plugins.

### ADR-067: Causal DAG & Novikov Self-Consistency Architecture (`scripts/lib/causality.py`)
- **Context**: Speculative fiction narratives featuring time travel, alternate timelines, or non-linear causality require rigorous topological sorting and closed timelike curve (CTC) loop detection to distinguish intentional bootstrap paradoxes from accidental grandfather contradictions.
- **Decision**: Formalize `scripts/lib/causality.py` (`arcanum causality`) with comprehensive test verification (`tests/test_causality.py`) and documentation (`docs/CAUSALITY.md`). Audit causal cycles using depth-first cycle detection, classifying `CAU-101` (Grandfather paradox), `CAU-102` (Unregistered bootstrap loop), `CAU-103` (Novikov violation), `CAU-104` (Orphan timeline), and `CAU-105` (Temporal inversion). Render interactive Mermaid.js DAG graphs and offline HTML reports.
- **Consequences**: Speculative worldbuilders can design complex causal loop architectures with mathematical consistency verification.

### ADR-068: Prophecy Resolution Matrix & Arcane Inscription Tracker (`scripts/lib/prophecy.py`)
- **Context**: Epic fantasy and speculative narratives frequently rely on oracles, divine prophecies, and sworn oaths whose fulfillment clauses must be systematically tracked across long manuscripts to avoid dropped plot threads or premature character deaths.
- **Decision**: Formalize `scripts/lib/prophecy.py` (`arcanum prophecy`) with complete unit test coverage (`tests/test_prophecy.py`) and documentation (`docs/PROPHECY.md`). Cross-validate `Cosmology/Prophecies/*.md` lore definitions against manuscript `@prophecy:` scene tags, detecting `PRP-101` (Orphan prophecy), `PRP-102` (Dead Chosen One), and `PRP-103` (Fulfillment status discrepancy).
- **Consequences**: Narrative designers ensure every prophetic condition is resolved, subverted, or broken deliberately with full structural traceability.

### ADR-069: 6D Sensory Palette Immersion & White Room Syndrome Architecture (`scripts/lib/senses.py`)
- **Context**: Authors frequently suffer from "White Room Syndrome" (scenes devoid of physical, auditory, or olfactory grounding) or extreme sensory monotony (over-reliance on purely visual descriptions).
- **Decision**: Formalize `scripts/lib/senses.py` (`arcanum senses`) with expanded test coverage (`tests/test_senses.py`) and documentation (`docs/SENSORY_PALETTE.md`). Classify prose against six sensory lexicons (Visual, Auditory, Olfactory, Gustatory, Tactile/Thermal, Kinesthetic/Vestibular), detecting `SNS-101` (White Room Syndrome) and `SNS-102` (Sensory Monotony / $>90\%$ visual skew).
- **Consequences**: Writers receive actionable stylistic feedback to deepen reader immersion and balance perceptual dimensions across all chapters.

### ADR-070: Flathub Upstream Packaging Validation & Offline Bundle Pipeline (`flatpak/flathub_submission_validate.py`)
- **Context**: Upstream submission to Flathub requires adherence to strict Freedesktop AppStream 0.16+ XML specifications, HTTPS screenshot URIs, Open Age Rating System (OARS 1.1) content classifications, and properly scoped sandbox finish-args.
- **Decision**: Implement `flatpak/flathub_submission_validate.py` with standalone linting and verification, automated unit tests (`tests/test_flathub_validation.py`), and dynamic version resolution in `flatpak/build_offline_bundle.sh`.
- **Consequences**: Continuous verification guarantees zero regressions when packaging sandboxed Flatpak bundles for global Flathub distribution.

### ADR-071: Cosmos Archive Freeze & Cryptographic Provenance Sealer (`scripts/lib/archive_freeze.py`)
- **Context**: Authors producing substantial intellectual property across long-term creative projects need mathematically provable cryptographic milestones, bit-rot detection, and immutable proof of authorship without cloud timestamping services.
- **Decision**: Implement `scripts/lib/archive_freeze.py` (`arcanum freeze`, `arcanum verify-archive`) computing deterministic SHA-256 and SHA-512 per-file digests alongside a Merkle-style root hash. Generate human-readable `PROVENANCE_SEAL.md` and machine-verifiable `ARCHIVE_MANIFEST.json`. Audit vaults for `FRZ-101` (Tampered File), `FRZ-102` (Missing File), and `FRZ-103` (Untracked File).
- **Consequences**: Creators establish indisputable, offline cryptographic provenance seals across their universe archives.

### ADR-072: Multi-Volume Dramatis Personae & Universe Cast Matrix Architecture (`scripts/lib/dramatis_personae.py`)
- **Context**: Complex narrative universes with dozens of characters across multi-volume series require automated synchronization between World Bible character dossiers and in-manuscript appearances to detect ghost characters, dead characters acting post-mortem, and unreferenced lore dossiers.
- **Decision**: Implement `scripts/lib/dramatis_personae.py` (`arcanum cast`, `arcanum dramatis-personae`) scanning `World/Characters/*.md` dossiers and cross-referencing `@char:`, `@pov:`, and `@death:` tags across all manuscript volumes. Detect `CAS-101` (Ghost Character), `CAS-102` (Post-Mortem Action), and `CAS-103` (Orphan Character), while compiling publication-grade Markdown appendices and standalone offline CSP-compliant HTML galleries.
- **Consequences**: Authors maintain seamless character continuity across entire multi-volume sagas with zero manual bookkeeping.

### ADR-073: Static World Wiki & Offline Codex Exporter Architecture (`scripts/lib/codex_export.py`)
- **Context**: Worldbuilders need an offline, single-file distribution format for their world encyclopedias that compiles Obsidian markdown notes, preserves internal `[[Wikilinks]]`, renders structured infobox cards, and provides full-text search without external server dependencies.
- **Decision**: Formalize `scripts/lib/codex_export.py` (`arcanum codex`) with unit test verification (`tests/test_codex_export.py`) and documentation (`docs/CODEX_EXPORT.md`). Convert markdown hierarchies into category tabs, build dynamic infoboxes from YAML frontmatter, inline a JSON search index, and enforce strict offline Content Security Policies.
- **Consequences**: Authors can distribute standalone, interactive world codexes to readers, editors, and collaborators with zero privacy or hosting overhead.

### ADR-074: Hard Magic Systems & Arcane Constraint Matrix (`scripts/lib/magic_system.py`)
- **Context**: Speculative fiction narratives built on hard magic systems require mathematical and metaphysical consistency across dozens of scenes to prevent accidental plot holes, power creep, and rule contradictions.
- **Decision**: Formalize `scripts/lib/magic_system.py` (`arcanum magic-check`, `arcanum magic-report`) with unit tests (`tests/test_magic_system.py`) and documentation (`docs/MAGIC_SYSTEM.md`). Validate character magic tiers against spell requirements (`MAG-101`), verify catalyst presence (`MAG-102`), enforce metaphysical hard limits (`MAG-103`), and audit scene fatigue accumulation (`MAG-104`).
- **Consequences**: Authors ensure absolute fidelity to their established magic rules with automated pre-flight scene checking.

### ADR-075: In-World Cryptographic Ciphers & Phonetic Rune Engine (`scripts/lib/cipher.py`)
- **Context**: Fantasy and sci-fi worldbuilders frequently include coded messages, secret cult missives, temple inscriptions, and runic carvings that need deterministic encoding/decoding and publication-grade visual representations.
- **Decision**: Formalize `scripts/lib/cipher.py` (`arcanum cipher`) with unit tests (`tests/test_cipher.py`) and documentation (`docs/CIPHERS.md`). Implement monoalphabetic, polyalphabetic, and transposition ciphers (Caesar, Atbash, Vigenère, Rail Fence, Columnar, Book Cipher) and Elder Futhark / Futhorc phonetic rune translation with standalone vector SVG card generation.
- **Consequences**: Narrative designers can generate authentic in-universe cryptograms and publication-ready runic artifacts 100% offline.

### ADR-076: Dynastic Genealogies & Succession Lineage Architecture (`scripts/lib/genealogy.py`)
- **Context**: Multi-generational epic sagas involving noble houses and royal dynasties require rigorous family tree DAG validation to detect biological paradoxes, chronological impossibilities, and conflicting inheritance claims.
- **Decision**: Formalize `scripts/lib/genealogy.py` (`arcanum genealogy`, `arcanum lineage`) with unit tests (`tests/test_genealogy.py`) and documentation (`docs/GENEALOGY.md`). Build family DAGs from markdown frontmatter, detect biological paradoxes (`GEN-101`) and succession conflicts (`GEN-102`), and output clean Obsidian Mermaid flowcharts, ANSI terminal trees, and interactive HTML dossiers.
- **Consequences**: Authors maintain unshakeable dynastic continuity and can visually inspect royal lineages across centuries.

### ADR-077: Conlang Phonotactics & Historical Sound-Change Engine (`scripts/lib/conlang.py`)
- **Context**: Authors crafting constructed languages require consistent phonetic rules, realistic name generation, and orderly historical sound evolution ($A \to B / X\_Y$) to simulate linguistic drift across regions and eras.
- **Decision**: Formalize `scripts/lib/conlang.py` (`arcanum conlang`) with unit tests (`tests/test_conlang.py`) and documentation (`docs/CONLANG.md`). Implement syllable template generators with forbidden cluster filters, sound law mutation processors, and markdown lexicon table extractors with CSV/JSON export.
- **Consequences**: Worldbuilders achieve authentic linguistic realism without external software or specialized computational linguistics tools.

### ADR-078: Geopolitical Faction Matrix & Campaign Logistics Architecture (`scripts/lib/factions.py`)
- **Context**: Epic narratives with complex geopolitical factions and military campaigns require validation of diplomatic networks and realistic operational constraints for troop movements.
- **Decision**: Formalize `scripts/lib/factions.py` (`arcanum faction`) with unit tests (`tests/test_factions.py`) and documentation (`docs/FACTIONS.md`). Audit multilateral diplomatic ties for contradictions (`FAC-101`), triad tensions (`FAC-102`), and vassal conflicts (`FAC-103`). Simulate Lanchester combat curves (Square/Linear laws) and model campaign supply wagon radii.
- **Consequences**: Authors ground large-scale conflicts and political intrigues in rigorous mathematical and diplomatic rails.

### ADR-079: Custom Planetary Calendars & Multi-Moon Synodic Engine (`scripts/lib/calendar.py`)
- **Context**: Speculative fiction set on secondary worlds or extraterrestrial planets often features non-standard orbital periods, multi-moon synodic cycles, and astronomical events (syzygies, eclipses) that drive in-world rituals and calendar systems.
- **Decision**: Formalize `scripts/lib/calendar.py` (`arcanum calendar`) with unit tests (`tests/test_calendar.py`) and documentation (`docs/CALENDARS.md`). Implement custom planetary calendar date arithmetic, multi-moon synodic phase tracking with Unicode glyphs and illumination percentages, and celestial conjunction detection.
- **Consequences**: Authors calculate exact celestial configurations and chronological dates across imaginary planets with complete mathematical consistency.

### ADR-080: In-World Macroeconomics & Anachronism Matrix Architecture (`scripts/lib/economy.py`)
- **Context**: Secondary-world speculative fiction requires economic coherence (consistent commodity prices and currency denominations) and technological era consistency to prevent jarring anachronisms.
- **Decision**: Formalize `scripts/lib/economy.py` (`arcanum economy`) with unit tests (`tests/test_economy.py`) and documentation (`docs/ECONOMY.md`). Calculate Purchasing Power Parity (PPP) exchange rate matrices across regional economies, model trade freight margins and transit costs, detect manuscript price inflation/deflation anomalies (`ECO-101`), unregistered currencies (`ECO-102`), and technological era anachronisms (`ECO-201`).
- **Consequences**: Authors maintain unshakeable economic realism and prevent accidental modern concepts from infiltrating historical or low-tech settings.

### ADR-081: Overland, Naval & Aerial Journey Expedition Modeler (`scripts/lib/journey.py`)
- **Context**: Overland expeditions and voyages across large fictional landmasses often suffer from unrealistic travel times and ignored logistical supply constraints.
- **Decision**: Formalize `scripts/lib/journey.py` (`arcanum journey`) with unit tests (`tests/test_journey.py`) and documentation (`docs/JOURNEY.md`). Model terrain friction coefficients, 15 travel paces (foot, mount, ship, aerial), food/water/mount feed consumption math, desert multipliers, and day-by-day expedition itineraries with starvation risk warnings.
- **Consequences**: Writers ground character travel in authentic physical logistics and generate publication-ready expedition route schedules.

### ADR-082: Offline Vector Cartography & Interactive Map Viewer (`scripts/lib/cartography.py`)
- **Context**: Authors require spatial clarity to visualize world landmarks, kingdom borders, trade routes, and distances without external GIS or online map software.
- **Decision**: Formalize `scripts/lib/cartography.py` (`arcanum map`) with unit tests (`tests/test_cartography.py`) and documentation (`docs/CARTOGRAPHY.md`). Extract YAML location coordinates, render standalone scalable vector graphics (SVG) with hex/square grids, automatic trade route lines with travel milestones, and generate interactive vanilla JS pan/zoom HTML viewers with offline CSP protection.
- **Consequences**: Worldbuilders gain interactive vector mapping and spatial distance validation 100% offline.

### ADR-083: Narrative Pacing, POV Balance & Tension Arc Modeling (`scripts/lib/pacing.py`)
- **Context**: Long novel manuscripts frequently suffer from pacing sags, uneven viewpoint character distribution (POV starvation), abandoned subplots, and flat tension curves.
- **Decision**: Formalize `scripts/lib/pacing.py` (`arcanum pacing`) with unit tests (`tests/test_pacing.py`) and documentation (`docs/PACING.md`). Calculate dialogue-to-exposition density ratios, sentence length variance, POV screen-time balance with starvation alerts for $>3$ chapter absences, subplot thread momentum tracking, and composite tension index modeling ($0 \text{ to } 100$).
- **Consequences**: Authors receive quantitative structural feedback on narrative rhythm and character pacing across entire manuscripts.

### ADR-084: Multi-Paradigm Story Structure & Beat Sheet Enforcer (`scripts/lib/structure.py`)
- **Context**: Authors need to assess whether major turning points and narrative beats align with classic and contemporary story paradigms across their chapters.
- **Decision**: Formalize `scripts/lib/structure.py` (`arcanum structure`) with unit tests (`tests/test_structure.py`) and documentation (`docs/STRUCTURE.md`). Map proportional word counts against ideal percentage windows across 9 canonical Western and Eastern paradigms (Three-Act, Save the Cat, Hero's Journey, Story Circle, Seven-Point, 8-Sequence, Fichtean Curve, Kishōtenketsu, Freytag's Pyramid), computing drift penalties and an overall Structural Harmony score.
- **Consequences**: Writers evaluate manuscript architecture against diverse storytelling traditions with mathematical precision.

### ADR-085: Character Voice Profiler & Dialogue Fingerprint Engine (`scripts/lib/voice.py`)
- **Context**: In multi-character ensembles, dialogue frequently suffers from author voice bleed and character linguistic homogeneity.
- **Decision**: Formalize `scripts/lib/voice.py` (`arcanum voice`) with unit tests (`tests/test_voice.py`) and documentation (`docs/VOICE.md`). Extract dialogue across script and prose tag conventions, compute Type-Token Ratio (TTR), mean utterance length, contraction formality ratios, punctuation cadences, distinctive vocabulary via TF-IDF approximation, and pairwise cosine similarity to warn when distinct characters sound identical.
- **Consequences**: Authors develop distinct, quantifiable linguistic fingerprints for every character in their universe.

### ADR-086: Stylistics, Dialogue Mechanics & Readability Rhythm Engine (`scripts/lib/stylistics.py`)
- **Context**: Prose revision requires rigorous detection of said-bookisms, adverb-heavy tags, punctuation errors, sliding-window word echoes, and cadence monotony.
- **Decision**: Formalize `scripts/lib/stylistics.py` (`arcanum stylistics`) with unit tests (`tests/test_stylistics.py`) and documentation (`docs/STYLISTICS.md`). Detect overwrought dialogue verbs (`PRO-101`), adverb tags, quotation punctuation issues, morphological sliding-window word echoes (`PRO-102`), staccato clusters, monotone cadence alerts, and standard readability indices (Flesch, Flesch-Kincaid, Gunning Fog, Coleman-Liau).
- **Consequences**: Authors automate line-level prose diagnostics, eliminating stylistic crutches and polishing cadence for publication.

### ADR-087: Focus Ambient & Binaural Soundscape Generator (`scripts/lib/ambient.py`)
- **Context**: Writers benefit from immersive auditory environments tailored to cognitive flow states, but relying on online streaming violates the sovereign offline-first principle.
- **Decision**: Formalize `scripts/lib/ambient.py` (`arcanum ambient`) with unit tests (`tests/test_ambient.py`) and documentation (`docs/AMBIENT.md`). Synthesize procedural stereo 16-bit 44.1 kHz WAV audio with White, Pink, and Brown noise filters, paired with phase-offset binaural beat frequencies across Alpha, Theta, Beta, and Gamma bands. Provide standalone offline HTML5 WebAudio synthesizers.
- **Consequences**: Authors generate private, zero-network ambient soundscapes directly integrated with writing sessions.

### ADR-088: Dynamic Tactical Combat & Monte Carlo Skirmish Engine (`scripts/lib/tactical_sim.py`)
- **Context**: Narrative action sequences and military skirmishes often suffer from unrealistic outcomes, plot armor inconsistencies, or unclear blow-by-blow choreography.
- **Decision**: Formalize `scripts/lib/tactical_sim.py` (`arcanum tactical`) with unit tests (`tests/test_tactical_sim.py`) and documentation (`docs/TACTICAL_SIM.md`). Model individual combatant attributes (HP, armor mitigation, attack bonuses, agility dodge thresholds, morale collapse), battlefield terrain cover and ranged modifiers, turn-by-turn narrative prose logs, and Monte Carlo probability distributions across 100+ simulations.
- **Consequences**: Authors mathematically test military realism and generate granular combat logs for scene inspiration.

### ADR-089: Motivation-Reaction Unit (MRU) Scene Mechanics Analyzer (`scripts/lib/scene_mechanics.py`)
- **Context**: Scene craft suffers when character reactions violate psychological sequencing (Swain/Butcher MRUs) or when scenes lack clear Goal/Conflict/Disaster structures.
- **Decision**: Formalize `scripts/lib/scene_mechanics.py` (`arcanum scene`) with unit tests (`tests/test_scene_mechanics.py`) and documentation (`docs/SCENE_MECHANICS.md`). Classify sentence-level MRU phases (Stimulus, Visceral Reflex, Emotional Response, Cognitive Thought, Action/Dialogue), flag inverted sequence flaws (action/thought preceding reflex), and evaluate Proactive Scene vs. Reactive Sequel balance.
- **Consequences**: Authors identify structural scene pacing flaws and inverted visceral reactions before manuscript editing.

### ADR-090: Multi-Track Narrative Plot Grid & Subplot Matrix Engine (`scripts/lib/plot_matrix.py`)
- **Context**: Complex multi-POV epics frequently lose track of secondary subplots, leading to accidental abandonment, long chapter absence gaps, or clustered resolutions.
- **Decision**: Formalize `scripts/lib/plot_matrix.py` (`arcanum plot-matrix`) with unit tests (`tests/test_plot_matrix.py`) and documentation (`docs/PLOT_MATRIX.md`). Scan chapter plot tags (`@plot:`, `@thread:`, `@arc:`), flag dormant plot threads ($\ge 4$ chapter gaps), detect dangling unresolved subplots, generate chapter density histograms, and render interactive SVG multi-lane timeline grids.
- **Consequences**: Narrative designers visualize subplot momentum and track storyline density across multi-chapter arcs.

### ADR-091: Dual-Track Chronological vs. Narrative Timeline Synchronizer (`scripts/lib/timeline_sync.py`)
- **Context**: Non-linear narratives with flashbacks, flashforwards, and dual-track timelines risk chronology errors and character bilocation paradoxes.
- **Decision**: Formalize `scripts/lib/timeline_sync.py` (`arcanum timeline`) with unit tests (`tests/test_timeline_sync.py`) and documentation (`docs/TIMELINE_SYNC.md`). Parse epoch years, day offsets, and relative temporal markers into normalized sort coordinates, identify non-linear flashback events, detect impossible bilocation paradoxes, and export interactive dual-track HTML timelines.
- **Consequences**: Authors maintain strict narrative vs. chronological coherence across non-linear storytelling structures.

### ADR-092: Planetary Climate, Orographic Rain Shadow & Köppen Biomes (`scripts/lib/climate.py`)
- **Context**: Speculative worldbuilding maps frequently place biomes and precipitation patterns in climatically impossible configurations.
- **Decision**: Formalize `scripts/lib/climate.py` (`arcanum climate`) with unit tests (`tests/test_climate.py`) and documentation (`docs/CLIMATE.md`). Compute stellar insolation, equilibrium surface temperatures, 1/3/5-cell atmospheric circulation regimes, prevailing surface wind bands, adiabatic orographic rain-shadow heating and precipitation collapse, and 14 Köppen biome classifications.
- **Consequences**: Worldbuilders ground their geography in astrophysical and atmospheric physics with zero guesswork.

### ADR-093: Trophic Food Web Ecology & Biomass Efficiency Simulator (`scripts/lib/ecology.py`)
- **Context**: Speculative bestiaries and flora lore often describe top predators without viable prey bases, circular predation loops, or impossible biomass pyramids.
- **Decision**: Formalize `scripts/lib/ecology.py` (`arcanum ecology`) with unit tests (`tests/test_ecology.py`) and documentation (`docs/ECOLOGY.md`). Extract trophic profiles (Levels 1–4) across Bestiary and Flora dossiers, audit Lindeman 10% trophic biomass efficiency (`ECO-302`), detect orphaned apex predators (`ECO-301`) and circular predation (`ECO-303`), and generate Obsidian Mermaid.js food-web relationship diagrams.
- **Consequences**: Worldbuilders ensure their speculative ecosystems are biologically coherent and thermodynamically sustainable.

### ADR-094: Earth Idiom & Immersion-Breaking Eponym Linter (`scripts/lib/idioms.py`)
- **Context**: In secondary-world speculative fiction, Earth-specific historical eponyms, mythological references, and terrestrial animal clichés break reader immersion.
- **Decision**: Formalize `scripts/lib/idioms.py` (`arcanum idioms`) with unit tests (`tests/test_idioms.py`) and documentation (`docs/IDIOMS.md`). Scan prose for Earth eponyms (`IDM-101`), mythological references (`IDM-102`), and biological clichés (`IDM-103`), providing historical origin explanations and in-world replacement suggestions with customizable JSON dictionaries and runtime whitelisting.
- **Consequences**: Authors preserve secondary-world illusion by catching Earth-specific idioms before publication.

### ADR-095: Back-Matter Concordance & Dramatis Personae Indexer (`scripts/lib/concordance.py`)
- **Context**: Authors of epic speculative fiction need to generate structured back-matter (character cast indexes, faction glossaries, relic catalogs, bestiaries, conlang lexicons) synchronized with active manuscripts.
- **Decision**: Formalize `scripts/lib/concordance.py` (`arcanum concordance`) with 12 unit tests (`tests/test_concordance.py`) and documentation (`docs/CONCORDANCE.md`). Scan `World/` lore files, cross-reference against manuscript chapters, and compile structured `04_Back_Matter/01_Dramatis_Personae.md` and `04_Back_Matter/02_Glossary_and_Concordance.md` files.
- **Consequences**: Authors automate publication back-matter assembly with 100% canon consistency across all volumes.

### ADR-096: Sovereign Zen Drafting Studio & In-Situ Lore Drawer (`scripts/lib/zen_studio.py`)
- **Context**: Distraction-free authoring requires a focused typography canvas paired with instant access to world dossiers without switching windows or exposing drafts to cloud tools.
- **Decision**: Formalize `scripts/lib/zen_studio.py` (`arcanum studio`) with 12 unit tests (`tests/test_zen_studio.py`) and documentation (`docs/ZEN_STUDIO.md`). Compile a zero-dependency, single-file HTML5 application with typewriter scrolling, live telemetry (words, reading time at 200 WPM, speaking time at 150 WPM), a searchable Lore Vault drawer, and client-side `localStorage` persistence.
- **Consequences**: Authors gain an ultra-fast, 100% offline drafting cockpit with real-time worldbuilding reference.

### ADR-097: Visual Story Canvas & Multi-Paradigm Corkboard (`scripts/lib/story_canvas.py`)
- **Context**: Writers need a visual, tactile corkboard to manipulate scene cards across act beats, balance POV distribution, and experiment with alternative story structures.
- **Decision**: Formalize `scripts/lib/story_canvas.py` (`arcanum canvas`) with 12 unit tests (`tests/test_story_canvas.py`) and documentation (`docs/CANVAS_GUIDE.md`). Support 9 narrative paradigms (Three-Act, Save the Cat, 8-Sequence, Hero's Journey, Kishōtenketsu, Fichtean Curve, 7-Point, Story Grid, Dan Harmon Circle), client-side drag-and-drop, and live pacing recalculation.
- **Consequences**: Authors visually design complex plots with real-time mathematical pacing feedback offline.

### ADR-098: Multi-Volume Series Omnibus Compilation Engine (`scripts/lib/omnibus.py`)
- **Context**: Assembling a multi-book series into an omnibus release requires tedious chapter concatenation, volume divider insertion, and unified master table of contents construction.
- **Decision**: Formalize `scripts/lib/omnibus.py` (`arcanum omnibus`) with 12 unit tests (`tests/test_omnibus.py`) and documentation (`docs/OMNIBUS.md`). Discover all `Book-*` volumes, synthesize formatted book divider pages, re-index sequential chapters, and compile unified master Markdown, TOC, and JSON manifests.
- **Consequences**: Multi-volume sagas can be compiled and verified in seconds for distributor and reader editions.

### ADR-099: Author Portfolio & Catalog Analytics Dashboard (`scripts/lib/portfolio.py`)
- **Context**: Authors managing multiple projects, universes, and standalone novels lack a unified catalog dashboard to track total output, pacing velocity, and editorial stages.
- **Decision**: Formalize `scripts/lib/portfolio.py` (`arcanum portfolio`) with 12 unit tests (`tests/test_portfolio.py`) and documentation (`docs/PORTFOLIO.md`). Aggregate catalog words, chapter counts, and target completion percentages across 5 lifecycle tiers (Scaffolding, Drafting Act I, Drafting Act II/III, Revisions, Publication-Ready) with standalone HTML and CLI reporting.
- **Consequences**: Authors maintain an executive high-altitude overview of their complete creative output.

### ADR-100: EPUB 3 SMIL Media Overlays & Synchronized Narration Player (`scripts/lib/media_overlay.py`)
- **Context**: Producing enhanced, accessible EPUB 3 audio-eBooks requires W3C SMIL 3.0 synchronization files linking spoken audio timestamps to individual paragraph elements.
- **Decision**: Formalize `scripts/lib/media_overlay.py` (`arcanum overlay`) with 12 unit tests (`tests/test_media_overlay.py`) and documentation (`docs/MEDIA_OVERLAY.md`). Segment chapter paragraphs, calculate non-overlapping millisecond timestamps, generate W3C SMIL 3.0 XML (`<seq>`, `<par>`), and build an offline HTML5 narration player with Web Speech Synthesis.
- **Consequences**: Authors produce standard-compliant accessible audio-synced publications with zero external toolchains.

### ADR-101: Smart Typography Normalizer & Punctuation Engine (`scripts/lib/typography_cleaner.py`)
- **Context**: Plain-text manuscript drafting often leaves straight quotes, doubled hyphens, and loose dots that violate professional publishing standards.
- **Decision**: Formalize `scripts/lib/typography_cleaner.py` (`arcanum typography`) with 12 unit tests (`tests/test_typography_cleaner.py`) and documentation (`docs/TYPOGRAPHY.md`). Convert straight quotes to curly pairs, hyphens to em/en-dashes, dots to ellipses, and strip trailing whitespace while strictly protecting YAML frontmatter and codeblocks.
- **Consequences**: Authors polish raw drafts into publication-standard literary typography with atomic file safety and `.bak` backups.

### ADR-102: ISBN-13 Vector SVG/PNG Barcode Engine (`scripts/lib/barcode.py`)
- **Context**: Print book cover design requires high-contrast vector EAN-13 / Bookland barcodes, typically forcing authors to use untrusted online barcode generators.
- **Decision**: Formalize `scripts/lib/barcode.py` (`arcanum barcode`) with 12 unit tests (`tests/test_barcode.py`) and documentation (`docs/BARCODE.md`). Implement pure-Python Modulo-10 checksum validation, legacy ISBN-10 conversion, EAN-13 binary parity encoding, scalable vector SVG generation, and pure-Python zlib-deflated PNG generation.
- **Consequences**: Authors generate print-ready, publication-grade vector barcodes locally with 100% privacy and zero external dependencies.

### ADR-103: Interactive Branching Narrative Graph & Choice Engine (`scripts/lib/branching_graph.py`)
- **Context**: Gamebook and interactive fiction authors writing non-linear narratives need plaintext branching syntax, topological reachability validation, and multi-format compilation into production narrative runtimes.
- **Decision**: Formalize `scripts/lib/branching_graph.py` (`arcanum branch`) with 12 unit tests (`tests/test_branching_graph.py`) and documentation (`docs/BRANCHING_GRAPH.md`). Support `@choice:`, `@state:`, `@req:`, `@ending:` tags, detect dead-end leaves (`BRN-101`), unreachable orphans (`BRN-102`), missing targets (`BRN-105`), and compile to Playable HTML5 reader, Inkle Ink (`.ink`), Twine 2 Twee 3 (`.twee`), and Obsidian Mermaid.
- **Consequences**: Authors write complex choice trees in Markdown with guaranteed topological integrity and multi-engine export capability.

### ADR-104: Local Semantic Retrieval (RAG) & Lore Recall Engine (`scripts/lib/local_rag.py`)
- **Context**: Speculative fiction authors need instant natural language search and lore recall across multi-volume World Bibles without exposing proprietary worldbuilding IP to third-party cloud vector databases.
- **Decision**: Formalize `scripts/lib/local_rag.py` (`arcanum rag`) with 12 unit tests (`tests/test_local_rag.py`) and documentation (`docs/LOCAL_RAG.md`). Implement zero-pip vector space cosine similarity with Robertson-Spärck Jones smoothed IDF, TF-IDF term frequency, SQLite FTS5 hybrid keyword rank fusion, and injection-safe prompt context synthesis.
- **Consequences**: Authors query complex lore archives locally with sub-second retrieval latency and absolute privacy.

### ADR-105: Multi-Perspective Autonomous Editorial Council (`scripts/lib/editorial_council.py`)
- **Context**: Authors benefit from diverse editorial viewpoints (line rhythm, lore constraints, dramatic pacing, continuity) throughout different stages of manuscript revision.
- **Decision**: Formalize `scripts/lib/editorial_council.py` (`arcanum council`) with 12 unit tests (`tests/test_editorial_council.py`) and documentation (`docs/EDITORIAL_COUNCIL.md`). Convene four sovereign editorial personas (Lady Cassian, Archon Vaelor, Grand Architect Soren, Chronicler Mirella), calculate consensus readiness scores ($0-100\%$), detect chamber dissent ($\ge 12\text{ pt}$ deviation), and generate prioritized action checklists with standalone HTML5 dashboards.
- **Consequences**: Authors receive balanced, multi-dimensional craft evaluations offline before submission.

### ADR-106: Local AI Fine-Tuning & Dataset Synthesizer (`scripts/lib/fine_tuning.py`)
- **Context**: Fine-tuning local open-weights LLMs on an author's lore, characters, and prose rhythm requires standardized instruction-following training datasets.
- **Decision**: Formalize `scripts/lib/fine_tuning.py` (`arcanum train-data`) with 12 unit tests (`tests/test_fine_tuning.py`) and documentation (`docs/FINE_TUNING.md`). Synthesize multi-category training pairs across persona, lore, prose continuation, and magic system constraints, exporting to Alpaca, ShareGPT, ChatML schemas, and automated Ollama `Modelfile` profiles.
- **Consequences**: Authors can train sovereign local LLMs tailored to their creative worlds without cloud exposure.

### ADR-107: Universal Structured Corpus & RAG Dataset Exporter (`scripts/lib/corpus_export.py`)
- **Context**: Modern authoring workflows require structured, indexed representations of entire universes and manuscripts for local search, embeddings, and archival backup.
- **Decision**: Formalize `scripts/lib/corpus_export.py` (`arcanum corpus`) with 12 unit tests (`tests/test_corpus_export.py`) and documentation (`docs/CORPUS_EXPORT.md`). Implement repository-wide traversal, heading-aware semantic chunking, and multi-format exports to JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`), relational SQLite with FTS5 search, and executive Markdown summary digests.
- **Consequences**: Creative vaults are universally portable and structured for local AI, embeddings, and database queries.

### ADR-108: Offline Neural TTS & Audio Proofreader (`scripts/lib/tts_reader.py`)
- **Context**: Listening to prose read aloud reveals cadence flaws, unintentional repetition, and dialogue rhythm issues that are easily missed during visual reading.
- **Decision**: Formalize `scripts/lib/tts_reader.py` (`arcanum tts`) with 12 unit tests (`tests/test_tts_reader.py`) and documentation (`docs/TTS_READER.md`). Implement markdown prose sanitization, custom phonetic pronunciation dictionaries, host toolchain auto-discovery (`piper`, `espeak-ng`, `spd-say`, macOS `say`, Windows SAPI), and a standalone HTML5 Web SpeechSynthesis player with sentence karaoke highlighting.
- **Consequences**: Authors access private, zero-dependency audio proofreading tools to polish prose cadence.

### ADR-109: Multi-Platform Distribution Packaging Engine (`scripts/package_distribution.py`)
- **Context**: Finalizing manuscripts for readers, beta reviewers, and agents requires creating distinct ZIP bundles with specific layouts, metadata notices, and checksum manifests.
- **Decision**: Formalize `scripts/package_distribution.py` (`arcanum package`) with 12 unit tests (`tests/test_package_distribution.py`) and documentation (`docs/PACKAGING.md`). Assemble Reader Editions (EPUB/PDF/HTML), Submission Packages (DOCX/Query/Synopsis), watermarked Advance Reading Copies (ARCs), and World Lore Codex Bundles, with SHA-256 manifest calculation in `RELEASE_MANIFEST.json`.
- **Consequences**: Authors package and verify publication bundles in seconds with cryptographic integrity guarantees.

### ADR-110: World Doctor & Cosmos Integrity Diagnostics (`scripts/lib/world_doctor.py`)
- **Context**: Expansive fictional worlds accumulate broken wikilinks, timeline inversions, duplicate character names, and dangling frontmatter over multi-year drafting cycles.
- **Decision**: Formalize `scripts/lib/world_doctor.py` (`arcanum doctor`) with 12 unit tests (`tests/test_world_doctor.py`) and documentation (`docs/WORLD_DOCTOR.md`). Implement 8-point deep diagnostics (`WLD-101` to `WLD-108`), multi-era calendar date parsing (BCE/CE, 1E/2E/3E, ordinal ages), manuscript cross-validation, and fast in-memory caching.
- **Consequences**: Worldbuilders maintain mathematically coherent, fully linked speculative universes with zero broken references.













### ADR-111: Granular Architectural Trimming and Redundancy Decommissioning
- **Context**: Over iterative development phases, speculative sub-features (offline AI fine-tuning datasets, synthetic speech readers, classical ciphers, barcode generators, plugin marketplace, editorial council personas, Merkle freeze provenance, and redundant single-command shell wrappers) introduced architectural weight and maintenance overhead without commensurate everyday authoring utility.
- **Decision**: Decommission 8 obsolete/niche engines (`fine_tuning.py`, `cipher.py`, `editorial_council.py`, `barcode.py`, `archive_freeze.py`, `tts_reader.py`, `media_overlay.py`, `plugins.py`/`plugin_market.py`) and 17 auxiliary shell scripts in `scripts/`. Consolidate `idioms.py` directly into `stylistics.py` and consolidate frontmatter parsing into `frontmatter_builder.py`.
- **Consequences**: Streamlines repository surface area, eliminates dead code, reduces unit test execution time, and focuses the codebase on core speculative worldbuilding, drafting, manuscript syncing, and publishing workflows.

### ADR-112: Non-Imposing Creative Advisory Paradigm
- **Context**: Worldbuilding and authoring tools that rigidly reject creative choices (such as hard magic limits, strict 3-act percentage targets, or strict Lanchester combat models) restrict narrative flow and conflict with speculative fiction flexibility.
- **Decision**: Establish a non-imposing creative advisor doctrine across all craft engines (`magic_system.py`, `structure.py`, `tactical_sim.py`, `astrophysics.py`). Engines provide helpful diagnostic warnings, plausibility advice, and consistency detection without enforcing artificial blockers on creative drafts.
- **Consequences**: Authors maintain full creative sovereignty while receiving mathematically sound, context-aware suggestions and contradiction warnings.

### ADR-113: Expanded Astrophysics, Climate Linkages & Multi-Calendar Chronology
- **Context**: Sci-fi and fantasy worldbuilders require non-standard planetary configurations (tidally locked eyeball worlds, habitable gas giant moons, brown dwarf systems, circumbinaries, hycean worlds) and complex in-universe calendar systems with custom date templates and epoch numbering.
- **Decision**: Enhance `astrophysics.py` with non-standard planetary configurations, parameter tinkering sweet-spot guidance, Star System Dossier export, and direct orbital insolation integration with `climate.py`. Enhance `calendar.py` with multi-calendar and multi-era registries, customizable date formatting syntax, and continuous epoch timeline projection.
- **Consequences**: Worldbuilders can simulate exotic astrophysical systems and track intricate multi-era chronologies with precision and ease.

### ADR-114: Multi-POV Narrative Threading, Bidirectional Vault Restore & Interactive Cartography
- **Context**: Multi-POV novels and complex series require tracking character thread divergences and convergences, interactive map design, and complete data mobility between exported structured datasets and live lore vaults.
- **Decision**: Refactor `branching_graph.py` into a Multi-POV Narrative Thread & Convergence Subway Map engine (`arcanum branch`). Refactor `cartography.py` to include an interactive HTML5/SVG graphical map creator and editor. Implement bidirectional vault restore in `corpus_export.py` (`arcanum corpus restore <archive>`). Enhance `genealogy.py` with fuzzy generational lineages supporting unrecorded generations and disputed succession claims.
- **Consequences**: Comprehensive narrative tracking, visual cartographic tools, and resilient bidirectional data roundtripping across the entire Ars Arcanum ecosystem.

### ADR-115: Advisory-First Creative Freedom Architecture & Integrated Craft Engine Documentation
- **Context**: Speculative fiction authors and worldbuilders need rich, actionable documentation on the mathematical, structural, and narrative logic behind every engine directly within their authoring environment (CLI, Web Studio Hub, and Desktop GUI). Furthermore, rigid validation rules that block or reject non-standard worldbuilding (e.g. FTL travel without warp fields, impossible orbits, paradoxical time loops, unconventional magic surges) frustrate authors and hinder creative freedom.
- **Decision**: Formalize the Advisory-First Creative Freedom Architecture across all 50 engines in `scripts/lib/registry.py`, `scripts/lib/cli.py`, `scripts/lib/studio_hub.py`, `scripts/lib/ui_gtk3/`, and `scripts/lib/ui_adw.py`. When an unconventional configuration is encountered, the system never enforces blockers; it issues an informative diagnostic alert with multiple creative resolution pathways (Option A: Hard Realism, Option B: Speculative Trope, Option C: Author Sovereignty). Implement unified `arcanum doc <engine>` CLI lookups supporting multi-word commands and hyphen normalization, and add the interactive Craft & Lore Guide to both the Web Studio Hub and Desktop GUI.
- **Consequences**: Authors maintain 100% creative sovereignty with full transparency into engine logic, scientific formulas, worldbuilding implications, and narrative mechanics, completely offline with zero external dependencies.