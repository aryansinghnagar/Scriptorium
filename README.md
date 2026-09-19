# Ars Arcanum — A Simple Linux Writing Setup

> **A low-effort, beginner-friendly system for novels and worldbuilding.**  
> Built for authors on Linux Mint (XFCE) & Debian. Everything in open Markdown. Zero terminal required for daily writing.

[![Status: Production Ready](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)](#)
[![Tests: 100% Passing](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)](#)
[![Audit: Grade A Verified](https://img.shields.io/badge/Audit-Grade%20A%20Verified-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> [!NOTE]
> ### 🛡️ PRODUCTION-READY & AUDIT-VERIFIED
> Ars Arcanum is a fully verified, local-first authoring platform tested across Tier 1 Linux distributions (**Linux Mint 21/22 XFCE** and **Debian 12/13 XFCE**).
>
> - **100% Verified Test Quality Gate**: All 5 test suites and the canonical 7-stage verification harness (`scripts/verify.sh`) pass with zero errors.
> - **Fail-Closed Security Posture**: Automated SHA-256 verification of binaries, transactional directory staging, path-traversal prevention, and unprivileged daily authoring.
> - **Zero Vendor Lock-In**: 100% open Markdown files (`.md`), YAML manifests, and local multi-tier Git version tracking.

> **Start here:** Consult the comprehensive [Author's Field Manual](docs/AUTHOR_MANUAL.md) for a visual step-by-step guide to worldbuilding, multi-volume drafting, automated concordance generation, and publishing. Run [Quick Start](#-quick-start-automated-setup) to install everything. Run `bash scripts/verify.sh` anytime for a comprehensive health check.

---

## 🌟 Overview & Architecture

Ars Arcanum provides everything an author needs to brainstorm lore, outline storylines, draft prose, revise manuscripts, compile ebooks, and typeset publication-grade print PDFs—without proprietary software locks or continuous maintenance.

```
~/Universes/<UniverseName>/
├── universe.yaml              → Overarching Universe manifest & continuity Git repository
├── Universe-Index.md          → Narrative cosmos hub & cross-world index
└── <WorldName>/               → Pure World Lore Vault (Direct Obsidian Vault with Git repository)
    ├── world.yaml             → World Lore manifest
    ├── Characters/            → Character profiles with Dataview metadata & relationship maps
    ├── Locations/             → Sensory regional palettes, cities, and landmarks
    ├── Factions/              → Guilds, empires, ideologies, and member rosters
    ├── Magic-Technology/     → Hard/soft magic rules, limitations, and costs
    ├── Bestiary/              → Creatures, apex predators, flora, and monster ecologies
    ├── Artifacts/             → Legendary relics, magical weapons, and focal items
    ├── Cosmology/             → Pantheons, deities, astral planes, and mythos
    ├── History/               → Historical eras, timelines, and catalytic events
    ├── Languages/             → Conlangs, phonetic rules, and world glossaries
    ├── Templates/             → fileClasses schemas, writing logs, scene cards, and central index
    └── .obsidian/             → Out-of-the-box plugin configs & fileClasses schemas

~/Manuscripts/<ManuscriptName>/
├── manuscript.yaml            → Project manifest linking Universe and World Lore Vault
├── nwProject.nwx              → novelWriter project manifest (fileVersion 1.5)
├── Book-01/                   → Discrete Git repository for Book-01 (Acts, Chapters, Scenes)
│   ├── 01_Act_I/
│   ├── 02_Act_II/
│   ├── 03_Act_III/
│   └── 04_Back_Matter/        → Automatically generated Dramatis Personae & Glossary
├── Outlines/                  → Three-act structural beats & Subplot-Thread-Matrix.md
├── Exports/                   → Exported print PDFs (Typst), EPUBs, and submission DOCXs (Pandoc)
└── Backups/                   → Standalone timestamped .tar.gz archives with SHA-256 digests
```

---

## 🚀 Quick Start (Automated Setup)

If you have booted into Linux Mint XFCE or Debian:

1. **Clone or download this repository** into your home folder:
   ```bash
   cd ~/Downloads
   git clone https://github.com/aryansinghnagar/Ars-Arcanum.git Ars-Arcanum
   cd Ars-Arcanum
   ```
2. **Run the automated setup installer**:
   ```bash
   bash scripts/setup_arcanum.sh
   ```
   *This single command tests your OS environment, installs Git, PyGObject, Zenity, LibreOffice, FocusWriter, Calibre, Obsidian, novelWriter, Typst, Pandoc, literary typography fonts, and installs desktop launchers.*

3. **Double-click "Ars Arcanum Control Center" on your Desktop** (or run `arcanum control-center`). On first launch, the welcoming wizard offers a 1-click starter cosmos (*"Cosmere / Scadrial / Mistborn-Era1"*) with pre-configured lore and starter chapters!

---

## 🛠️ Core Toolchain

| Creative Phase | Tool | Format | Role & Setup |
| :--- | :--- | :--- | :--- |
| **Desktop Control Center** | **Ars Arcanum App** | Native GTK 3 / Zenity | 5-tab author dashboard with global Universe, World Lore, and Manuscript selectors, Visual Scene Metadata Inspector, live word counts, 1-click Typst/Pandoc publishing, Git version snapshots, and Doctor diagnostics. |
| **World Bible & Wiki** | **Obsidian** | Markdown (`.md`) | Open `<WorldName>` directly as Vault. Comes pre-configured with **Longform**, **Dataview**, **Metadata Menu**, **Calendarium**, **Storyteller Suite**, **Storyline**, **Novel Word Count**, and **Obsidian Git** (10-min auto-commits). (See [Plugin Guide](docs/guides/OBSIDIAN_PLUGINS.md)) |
| **Outlining & Drafting** | **novelWriter** / **Longform** | Markdown (`.md`) + `nwProject.nwx` | Open `~/Manuscripts/<Manuscript>` to draft with novelWriter's structured project tree, status badges (`Draft`, `Revision`, `Finished`), and scene annotations (`@pov:`, `@location:`, `@char:`, `@thread:`, `@time:`, `@status:`). |
| **Deep Sprint Canvas** | **FocusWriter** | Plaintext (`.txt` / `.md`) | Minimalist full-screen distraction-free distraction sprint sessions (`F11`). |
| **Revisions & Collaboration**| **LibreOffice Writer** | `.odt` / `.docx` | Track changes with professional editors and redlining. |
| **Ebook Compilation** | **Calibre** | `.epub` / `.mobi` | Graphical EPUB inspection, metadata tagging, and e-reader sync. |
| **Typesetting & Print PDF** | **Typst + Pandoc** | `.typ` / Vector PDF | Compiles sub-second, publication-grade print PDFs with trade margins, alternating running headers, ornamental breaks, and front matter (half-title, title, copyright, dedication). |

---

## 🖥️ Desktop Launchers & Unified CLI (No Terminal Daily Work)

Ars Arcanum provides both intuitive GUI launchers and a unified CLI dispatcher (`arcanum` or `ars-arcanum`):

1. **`Ars Arcanum Control Center` (`arcanum control-center`)**: Native Python/GTK 3 dashboard with 5 tabs:
   - **🪐 Universes & Worlds**: Universe and World Lore Vault management, creation wizards, toolchain launchers.
   - **✍️ Manuscripts & Drafting**: Manuscript hierarchy tree, live word counts, and the **Visual Scene Metadata Inspector** for `@pov`, `@char`, `@location`, `@thread`, `@time`, `@status`.
   - **📚 Publishing & Exports**: 1-Click Typst PDF, Pandoc EPUB, and submission DOCX export, automated Back-Matter Concordance & Dramatis Personae generator, volume selector (`Book-01`, `Book-02`, Omnibus), trim size presets (6x9, 5.5x8.5, 5x8), live PDF viewer.
   - **🔒 Snapshots & Backups**: 1-Click Git version snapshot button with log viewer, standalone `.tar.gz` + SHA-256 backup creator, restore drill wizard.
   - **🩺 Diagnostics & Doctor**: Ars Arcanum toolchain status badges, World Bible lore consistency checks (`world-doctor`), 7-stage verification trigger.
2. **`Write & Open Workspace` (`arcanum write [target]`)**: Opens novelWriter (for manuscripts) or Obsidian (for world lore) directly without terminal management.
3. **`New Project Scaffolder` (`arcanum new <manuscript|world|universe|volume> <name>`)**: Scaffolds novels, world lore vaults, narrative universes, or subsequent manuscript volumes.
4. **`Save Snapshot` (`arcanum save [target] [-m "note"]` / `arcanum snapshot`)**: Records an instant timestamped Git version snapshot.
5. **`Publish & Export` (`arcanum publish [manuscript] [--format book|submission|all]` / `arcanum export`)**: Compiles print PDF (Typst), distribution EPUB (Pandoc), and standard submission DOCX in one command.
6. **`Words & Analytics` (`arcanum words [manuscript]` / `arcanum report`)**: Shows live word counts, chapter metrics, and status breakdowns.
7. **`Back-Matter Concordance` (`arcanum concordance <world> --manuscript <ms>`)**: Compiles publication-ready Dramatis Personae and Glossary back-matter.
8. **`Health & Diagnostics` (`arcanum check` / `arcanum doctor` / `arcanum continuity`)**: Runs system diagnostics, toolchain verification, and character consistency audits.
9. **`Fast Performance Cache` (`arcanum cache <scan|wordcounts|clear> [path]`)**: Manages mtime-keyed in-memory caching for sub-millisecond analytics.

---

## 🛑 Distraction Control & Focus Enforcement

1. **Firefox Site Blocker**:
   - Install **LeechBlock NG** from the [Firefox Add-ons Store](https://addons.mozilla.org/firefox/addon/leechblock-ng/).
   - Open LeechBlock Options -> **Import** -> Select `configs/leechblock_arcanum_rules.json`.
   - If import warns about schema, manually recreate one block set from the JSON (`sites`, `times 0900-1300,1400-1700`) — export format varies by LeechBlock version and must be live-verified.
   - Blocks YouTube, Reddit, Twitter/X, TikTok, and social media during your writing hours (09:00–13:00 and 14:00–17:00).
2. **OS Notification Muting**:
   - Click the Notification Bell icon in the Linux Mint panel and toggle **Do Not Disturb**.
   - See [XFCE DND Guide](docs/guides/DISTRACTION_CONTROL.md) for custom keyboard shortcut setup.

---

## 🔒 Data Safety: Multi-Tier Version Control & The 3-2-1 Rule

1. **Multi-Tier Git Version History**:
   - Every Universe, World, and individual Book manuscript has dedicated Git version control.
   - Obsidian Git automatically commits changes every 10 minutes and on manual saves.
   - Click **Save Snapshot** (`arcanum snapshot`) anytime to create milestone commits.
2. **Standalone Archive Backups**:
   - Run `arcanum backup` or use the Control Center to create timestamped `.tar.gz` archives with SHA-256 verification checksums stored in `05-Backups/` or external media.
   - Test full system recovery with `arcanum restore`.
3. **Full-Disk Encryption & Automated External Backups**:
   - During Linux Mint installation, tick *"Encrypt the new Linux Mint installation"* (LUKS).
   - Use **Déjà Dup** for automated offsite/USB backups (see [Déjà Dup Backup Guide](docs/guides/BACKUP_SETUP.md)).

---

## 📚 Complete Resource Index

- [Author's Field Manual](docs/AUTHOR_MANUAL.md) — Visual plain-English handbook for novel writing, worldbuilding, and publishing.
- [Technical Architecture & ADRs](docs/ARCHITECTURE.md) — System blueprint, technical deep-dives, exit codes, and Architectural Decision Records (ADR-001 through ADR-023).
- [Software Catalog & Download Links](docs/guides/SOFTWARE_CATALOG.md) — Exact packages, Flatpak IDs, ISOs, and commands.
- [Optional Extras Guide](docs/guides/OPTIONAL_EXTRAS.md) — Azgaar maps, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix.
- [Typography & Fonts Guide](docs/guides/TYPOGRAPHY_AND_FONTS.md) — Free literary typefaces (Linux Libertine, EB Garamond, Alegreya) and Typst formatting rules.
- [Obsidian Plugin Suite Guide](docs/guides/OBSIDIAN_PLUGINS.md) — Pre-configured Obsidian writing and worldbuilding suite.
- [Distraction Control Guide](docs/guides/DISTRACTION_CONTROL.md) — XFCE notification muting and FocusWriter tips.
- [Automated Backup Guide](docs/guides/BACKUP_SETUP.md) — 3-2-1 backup strategy with Déjà Dup.
- [Typst Book Template](templates/typst/book_template.typ) — Reusable novel layout engine.
- [Obsidian World Bible Index Dashboard](templates/world-bible/Templates/World-Bible-Index.md) — Dataview queries and lore hub.
- [Roadmap & Milestones](docs/ROADMAP.md) — Project charter, hardware baselines, milestones (M0–M15), and operational status.

---

## 🗺️ Project Docs (for contributors)

| Doc | What it is |
| :--- | :--- |
| [docs/AUTHOR_MANUAL.md](docs/AUTHOR_MANUAL.md) | Comprehensive Author's Field Manual for daily writing, lore building, and publication |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture, invariants, exit codes, and full ADR catalog (ADR-001 through ADR-023) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Project charter, milestones (M0–M15), hardware baseline, and real-time status queues |
| [CHANGELOG.md](CHANGELOG.md) | Notable changes: audit remediation series, separated architecture, and decluttering |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute: ground rules, exit-code contract, quality gate, commit style, submission flow |
| [SECURITY.md](SECURITY.md) | Security scope, installer privilege surface disclosure, and private vulnerability reporting |
| [PRIVACY.md](PRIVACY.md) | Privacy policy, offline data minimization, and zero telemetry guarantee |
| [REFERENCES.md](REFERENCES.md) | Asset provenance, Creative Commons / FOSS attribution index, and licensing references |
| [docs/SUPPORT_MATRIX.md](docs/SUPPORT_MATRIX.md) | Supported Linux distributions, desktop environments, architectures, and display servers |
| [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) | Toolchain version baselines, SHA-256 binary digests, and Flatpak application IDs |
| [scripts/verify.sh](scripts/verify.sh) | 7-stage automated health check: syntax, schema validation, Universe/World lifecycle, Git snapshots, and backup/restore drills |

