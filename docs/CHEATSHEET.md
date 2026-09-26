# Ars Arcanum / Scriptorium — Author's Quick Reference Cheatsheet
> **100% Offline, Sovereign Writing & Speculative Worldbuilding Studio** | Version 3.7.0

---

## ⌨️ Desktop Keyboard Accelerators

| Shortcut | Action | Scope / Studio |
| :--- | :--- | :--- |
| `Ctrl + N` | **+ New Project Wizard** (Manuscript / World / Universe) | Global Scaffolding |
| `Ctrl + S` | **Quick Version Snapshot** (Git commit with milestone prompt) | Global Versioning |
| `Ctrl + E` | **Compile & Export Book** (Print PDF / EPUB / DOCX) | Studio 4: Publishing |
| `Ctrl + B` | **Create Standalone Backup Archive** (`.tar.gz` / `.tar.gz.gpg`) | Studio 5: Safety |
| `Ctrl + H` | **Toggle High-Contrast Mode** (WCAG 2.1 AA compliant palette) | Accessibility |
| `Ctrl + R` | **Refresh Project Discovery** (Reload universes & manuscripts) | Top Selector Bar |
| `F1` | **Open Author's Field Manual** | Offline Reference |

---

## ✍️ Markdown Scene Metadata Headers

Place these optional tags in your chapter scenes (or edit via the GUI Scene Inspector). All tags are automatically scrubbed during export to print/ebook formats:

```markdown
@pov: Kaelen Vance
@char: Vance, Lysandra, Archon Scribe
@location: SunCitadel Archives
@plot: Main-Heist
@thread: Arcane-Romance
@arc: Vance-Redemption
@time: 1422 3E, Night
@status: Draft
@magic: Aether-Weaving
@cast: Kaelen: Light-Shield
@reagent: Lumic Crystal, Silver Dust
@fatigue: 45

# Chapter 1: Into the Vault

Prose begins here...
```

---

## 🚀 Essential CLI Commands

```bash
# Core Authoring & Project Management
arcanum write [TARGET]               # Open writing workspace in novelWriter / Obsidian (alias: open)
arcanum studio [MS] [-w WORLD]       # Standalone offline Zen drafting studio & in-situ lore drawer
arcanum portfolio [ROOT] [--html]    # Author portfolio dashboard, catalog velocity & progress rollups
arcanum typography [TARGET] [-i]     # Smart typography normalizer (curly quotes, em/en-dashes, ellipses)
arcanum corpus <export|restore> [TARGET] # Universal structured corpus (JSONL/SQLite) and vault restore
arcanum word [MS]                    # Open manuscript in Microsoft Word / LibreOffice (alias: writer)
arcanum docx sync [MS]               # Bidirectional synchronization between Word (.docx) & Markdown
arcanum new <manuscript|world|universe|volume> <NAME>  # Scaffold new project components
arcanum draft <MS> [DRAFT_NAME]      # Fork discrete revision draft (e.g. Draft-02)
arcanum compare <MS> [NEW] [OLD]     # Visual Redline changelog comparison in browser
arcanum save [TARGET] -m "Note"      # Save Git version milestone snapshot (alias: snapshot)
arcanum words [MS] [--pov|--json]    # Live word count report and POV balance breakdown

# Local AI Semantic Lore Retrieval & Craft Engines
arcanum rag <QUERY> [-d DB] [-f FMT] # Sovereign hybrid TF-IDF/FTS5 semantic lore retrieval & LLM context
arcanum branch [MS] [--subway]       # Multi-POV narrative thread subway map & storyline convergence tracker
arcanum ambient [PROFILE]            # Procedural focus soundscape loop player (Rain, Campfire, Drone)
arcanum hub [TARGET] [--port PORT]   # Sovereign Studio Desktop Hub — unified offline telemetry cockpit
arcanum sprint <start|stop|status|stats|report> # Writing sprint timer, WPM velocity analytics & dashboard
arcanum revision-heatmap [MS] [--html] # Snapshot revision churn heatmap & over-revised chapter detector
arcanum causality [MS] [-w WORLD]     # Causal DAG builder, Novikov self-consistency & loop detector
arcanum prophecy [MS] [-w WORLD]      # Prophecy resolution matrix & clause cross-validation
arcanum senses [MS] [--html]          # 6D sensory palette immersion analyzer & White Room linter
arcanum cast [UNIVERSE] [--html|--md] # Multi-volume Dramatis Personae & Universe Cast Matrix
arcanum codex [WORLD] [-o OUT.html]   # Single-file standalone offline World Wiki & Codex exporter
arcanum magic-check [WORLD] [-m MS]   # Sanderson hard magic tier, catalyst & fatigue constraint validator
arcanum faction <check|battle|logistics> # Geopolitical relations, Lanchester combat & campaign logistics
arcanum economy <check|ppp|trade>     # Macroeconomic commodity PPP, trade freight margins & anachronisms
arcanum journey --dist <D> --mode <M> # Overland/naval expedition modeler, terrain friction & supply math
arcanum map [WORLD] [--svg|--html]    # Offline vector SVG cartography & interactive HTML map viewer
arcanum pacing [MS] [--html]          # Narrative pacing, POV balance, thread momentum & tension curves
arcanum structure [MS] -p <PARADIGM>  # 11-Paradigm story structure & beat window enforcer (3-Act, STC, Kisho...)
arcanum voice [MS] [--html]           # Character dialogue profiler, TTR, formality & voice bleed detector
arcanum stylistics [TARGET] [--html]  # Prose linter, said-bookisms, word echoes & readability rhythm
arcanum ambient [--profile P] [--html]# Procedural focus soundscapes & offline WebAudio studio
arcanum tactical [--terrain T] [--runs N] # Dynamic tactical combat & Monte Carlo skirmish engine
arcanum scene [MS] [--html]           # Motivation-Reaction Unit (MRU) scene mechanics & inversion linter
arcanum plot-matrix [MS] [--html]     # Multi-track narrative plot grid, subplot matrix & dormancy alerts
arcanum climate [--star-lum L] [--html]# Planetary climate, orographic rain shadows & Köppen biomes
arcanum ecology [WORLD] [--html|--note]# Trophic food web auditor, Lindeman 10% efficiency & Mermaid diagrams
arcanum idioms [MS] [--html|--whitelist]# Earth-specific eponym & immersion cliché linter

# Speculative Worldbuilding, Editorial Council & Consistency Checks
arcanum concordance -w [W] -m [MS]   # Back-matter concordance, Dramatis Personae & glossary generator
arcanum council [MS] [-w WORLD]      # Multi-perspective autonomous editorial council review
arcanum world-doctor [WORLD]         # Deep lore vault validation, broken links, trait anomalies
arcanum continuity -w [W] -m [MS]    # Multi-book character trait & narrative continuity check
arcanum canvas [MS]                  # Interactive visual story canvas & drag-and-drop corkboard
arcanum timeline [MS|WORLD]          # Dual-track chronological vs narrative timeline synchronizer
arcanum omnibus <UNIVERSE>           # Compile multi-volume series omnibus with unified lore
arcanum corpus export <TARGET>       # Universal structured JSONL, SQLite & RAG dataset exporter
arcanum overlay [MS] [--html]        # EPUB 3 SMIL Media Overlays & synchronized narration player
arcanum plugin <list|run|create>     # Manage speculative fiction community plugins (docs/PLUGINS.md)
arcanum audit plugin <NAME> [TARGET] # Run custom craft validator (e.g. magic_system_audit, speculative_naming)
arcanum genealogy -w [W] [-f mermaid]# Dynastic family trees, succession DAGs & paradox scanner
arcanum conlang generate -w [W] -l [L]# Conlang phonotactics word/name generator
arcanum calendar [WORLD] [--phases]  # Planetary calendar arithmetic, seasons & moon syzygies
arcanum calc transit --dist [D]      # Relativistic 1g spaceflight, time dilation & orbital mechanics

# Publishing, Distribution & Backups
arcanum publish [MS] [--format all]  # Compile print PDF (Typst), EPUB (Pandoc), submission DOCX
arcanum preflight [MS]               # Typesetting pre-flight validator (PUB-101)
arcanum package [MS] [-t TARGET]     # Bundler: reader, submission, arc, codex, or all (OPS-101)
arcanum backup [TARGET] [--symmetric]# Standalone archive backup (supports GPG AES-256 encryption)
arcanum restore [ARCHIVE]            # Disaster recovery restoration with SHA-256 verification
arcanum doctor                       # System diagnostic & toolchain health check
```

---

## 📦 Release Packaging Targets (`arcanum package`)

| Target | Flag | Contents |
| :--- | :--- | :--- |
| **Reader Edition** | `-t reader` | Formatted EPUB + Print PDF + HTML reader + Cover art (`*_Reader_Edition.zip`) |
| **Submission Packet** | `-t submission` | Standard Submission DOCX + Query Letter + Synopsis (`*_Submission_Package.zip`) |
| **Advance Reading Copy** | `-t arc` | Watermarked ARC documents + Reviewer license notice (`*_ARC_<Reviewer>.zip`) |
| **Lore Codex Bundle** | `-t codex` | Standalone static offline HTML lore wiki + SVG vector maps (`*_Codex_Bundle.zip`) |
| **All Packages** | `-t all` | Generates all applicable bundles + SHA-256 `RELEASE_MANIFEST.json` |

---

## 🔒 3-2-1 Data Safety & GPG Encryption

```bash
# Standard backup with dual-target secondary replication
arcanum backup My-World

# Encrypted backup with GPG symmetric AES-256 passphrase
arcanum backup My-World --symmetric

# Encrypted backup with recipient GPG public key ID
arcanum backup My-World --encrypt "author@example.com"

# Set persistent external USB backup drive
arcanum backup-dest set /media/usb/backups

# Safe verified restore
arcanum restore /path/to/My-World_2026-09-21.tar.gz.gpg
```

---

## 📂 Project Directory Structure

```
~/Universes/<UniverseName>/
  ├── universe.yaml            # Overarching narrative cosmos manifest
  └── <WorldName>/             # Obsidian World Lore Vault (Characters, Factions, Magic, Bestiary...)

~/Manuscripts/<ManuscriptName>/
  ├── manuscript.yaml          # Manuscript manifest linking Universe & World
  ├── Book-01/
  │   └── Draft-01/
  │       ├── Draft-01_Manuscript.docx  # Auto-synced Word master document
  │       ├── 01_Act_I/        # Markdown chapters & scenes
  │       ├── 02_Act_II/
  │       └── 03_Act_III/
  ├── Exports/                 # Output PDFs, EPUBs, and submission DOCXs
  ├── Dist/                    # Packaging archives & RELEASE_MANIFEST.json
  └── Backups/                 # Standalone timestamped .tar.gz / .tar.gz.gpg archives
```
