# Ars Arcanum — A Sovereign Linux Writing & Speculative Worldbuilding Ecosystem

> **A low-effort, beginner-friendly system for novels and speculative worldbuilding.**  
> Built for authors on Linux Mint (XFCE) & Debian. Everything in sovereign Markdown & OpenXML. Zero terminal required for daily writing.

[![Status: Production Ready](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)](#)
[![Unit Tests: 131 Passing](https://img.shields.io/badge/Unit%20Tests-131%2F131%20Passing-brightgreen.svg)](#)
[![Integration: 37 Stages](https://img.shields.io/badge/Integration-37%2F37%20Stages-brightgreen.svg)](#)
[![Verification: 7/7 Stages](https://img.shields.io/badge/Verification-ALL--CHECKS--PASS-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> [!NOTE]
> ### 🛡️ PRODUCTION-READY & AUDIT-VERIFIED
> Ars Arcanum is a fully verified, local-first authoring platform tested across Tier 1 Linux distributions (**Linux Mint 21/22 XFCE** and **Debian 12/13 XFCE**).
>
> - **100% Verified Quality Gate**: 131 automated Python unit tests, 37 targeted integration tests, and the canonical 7-stage verification harness (`scripts/verify.sh`) pass with zero errors.
> - **100% Offline Privacy & Zero Telemetry**: Operates strictly on your local machine with zero network calls, zero tracking, and pure Python standard library simulation engines.
> - **Fail-Closed Security Posture**: Automated SHA-256 binary digest checks, transactional directory staging, path-traversal prevention, and unprivileged daily authoring.
> - **Zero Vendor Lock-In**: Plain Markdown files (`.md`), standard OpenXML (`.docx`), YAML manifests, and local multi-tier Git version tracking.

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
    ├── Factions/              → Guilds, empires, ideologies, and military rosters
    ├── Economies/             → Currency systems, commodity baskets, and PPP definitions
    ├── Magic-Technology/     → Hard/soft magic rules, limitations, and costs
    ├── Bestiary/              → Creatures, apex predators, flora, and monster ecologies
    ├── Artifacts/             → Legendary relics, magical weapons, and focal items
    ├── Cosmology/             → Pantheons, deities, astral planes, and prophecies
    ├── History/               → Historical eras, timelines, and catalytic events
    ├── Languages/             → Conlangs, phonetic rules, sound laws, and world glossaries
    ├── Templates/             → fileClasses schemas, writing logs, scene cards, and central index
    └── .obsidian/             → Out-of-the-box plugin configs & fileClasses schemas

~/Manuscripts/<ManuscriptName>/
├── manuscript.yaml            → Project manifest linking Universe, World Lore Vault & active draft
├── nwProject.nwx              → novelWriter project manifest (fileVersion 1.5)
├── Book-01/                   → Discrete Git repository for Book-01
│   ├── Draft-01/              → Active discrete draft directory
│   │   ├── Draft-01_Manuscript.docx → Consolidated draft in standard MS Word / Google Docs format
│   │   ├── 01_Act_I/
│   │   │   ├── 01_Chapter.md  → Sovereign Plain Markdown source with scene metadata
│   │   │   └── 01_Chapter.docx → Individual chapter in standard Word format (auto-synchronized)
│   │   ├── 02_Act_II/
│   │   ├── 03_Act_III/
│   │   └── 04_Back_Matter/    → Automatically generated Dramatis Personae & Glossary
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
   git clone https://github.com/aryansinghnagar/Scriptorium.git Ars-Arcanum
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
| **Desktop Control Center** | **Ars Arcanum App** | Native GTK 3 / Zenity | 5-tab author dashboard with global Universe, World Lore, and Manuscript selectors, Visual Scene Metadata Inspector, live word counts, Word Processor toolbar, 1-click Typst/Pandoc publishing, Git version snapshots, 12 speculative fiction tools, and Doctor diagnostics. |
| **World Bible & Wiki** | **Obsidian** | Markdown (`.md`) | Open `<WorldName>` directly as Vault. Comes pre-configured with **Longform**, **Dataview**, **Metadata Menu**, **Calendarium**, **Storyteller Suite**, **Storyline**, **Novel Word Count**, and **Obsidian Git** (10-min auto-commits). (See [Plugin Guide](docs/guides/OBSIDIAN_PLUGINS.md)) |
| **Outlining & Drafting** | **novelWriter** / **Longform** | Markdown (`.md`) + `nwProject.nwx` | Open `~/Manuscripts/<Manuscript>` to draft with novelWriter's structured project tree, status badges (`Draft`, `Revision`, `Finished`), and scene annotations (`@pov:`, `@location:`, `@char:`, `@thread:`, `@time:`, `@status:`). |
| **Word Processor Drafting** | **Microsoft Word / Google Docs / LibreOffice** | Standard OpenXML (`.docx`) | Dual-synchronized `.docx` drafting for authors and editors. Pure Python zero-dependency OpenXML engine with bidirectional tag-preserving sync. |
| **Deep Sprint Canvas** | **FocusWriter** | Plaintext (`.txt` / `.md`) | Minimalist full-screen distraction-free distraction sprint sessions (`F11`). |
| **Revisions & Collaboration**| **LibreOffice Writer** | `.odt` / `.docx` | Track changes with professional editors and redlining. |
| **Ebook Compilation** | **Calibre** | `.epub` / `.mobi` | Graphical EPUB inspection, metadata tagging, and e-reader sync. |
| **Typesetting & Print PDF** | **Typst + Pandoc** | `.typ` / Vector PDF | Compiles sub-second, publication-grade print PDFs with trade margins, alternating running headers, ornamental breaks, and front matter (half-title, title, copyright, dedication). |

---

## 🔮 12-Suite Speculative Fiction Authorial Engine

Ars Arcanum includes 12 zero-dependency Python standard library engines tailored for science fiction, space opera, hard fantasy, grimdark, alternate history, and time travel authors:

| # | Domain & Engine | Key CLI Commands | Primary Capabilities |
|---|-----------------|------------------|----------------------|
| **1** | **Astrophysics & Relativistic Spaceflight** | `arcanum calc transit`, `arcanum calc time-dilation`, `arcanum calc orbit`, `arcanum calc comms` | $1g$ Brachistochrone trajectories ($\tau$ ship proper time vs $t$ coordinate time, peak $v/c$, fuel mass ratio), Lorentz time dilation ($\gamma$), Hohmann orbital transfers, speed-of-light comms latency. |
| **2** | **Hard Magic & Arcane Constraints** | `arcanum magic check`, `arcanum magic report` | Sanderson-style hard limitation checks (`MAG-101`), reagent/catalyst audit (`MAG-102`), cumulative arcane fatigue tracking (`MAG-104`), standalone HTML audit report. |
| **3** | **Dynastic Genealogies & Lineages** | `arcanum genealogy <House>`, `arcanum lineage <House>` | Family tree DAG builder, Obsidian Mermaid.js compilation (`--write-note`), interactive HTML/SVG trees (`--html`), biological/chronological paradox checks (`GEN-101`). |
| **4** | **Conlang Phonotactics & Sound Laws** | `arcanum conlang generate <Lang>`, `arcanum conlang mutate <Lang>`, `arcanum conlang lexicon <Lang>` | Syllable structure word generator (`(C)V(C)`), phoneme frequency weighting, cluster blacklist, historical sound-change mutation engine (`p > f / V_V`), dictionary exporter. |
| **5** | **Narrative Pacing & Tension Arcs** | `arcanum pace [ms]`, `arcanum tension [ms]`, `arcanum words --pov` | Dialogue vs action vs exposition ratios, sentence length variance, POV screen-time balance & starvation alerts, subplot momentum (`@thread:`), interactive HTML tension curve. |
| **6** | **Journeys & Planetary Calendars** | `arcanum calc journey`, `arcanum calendar [world]` | 14 terrain friction coefficients, 8 movement modes, party ration/water burn rates, custom day/year lengths, multi-moon synodic phase cycles, syzygies, and eclipses. |
| **7** | **Faction Matrix & Campaign Logistics** | `arcanum faction [world]`, `arcanum calc battle`, `arcanum calc logistics` | Alliance/rivalry chord diagrams, diplomatic paradox linter (`FAC-101`), Lanchester power-law combat calculator (square/linear laws), military supply wagon radius. |
| **8** | **Economy, PPP & Tech Anachronisms** | `arcanum economy [world]`, `arcanum audit tech [world] [ms]` | Multi-currency commodity basket Purchasing Power Parity (PPP), scene price outlier audits (`ECO-101`), interstellar trade viability, historical technological era anachronism linter. |
| **9** | **Causal DAGs & Multiverse Timelines** | `arcanum causality [world] [ms]`, `arcanum causality branch [name]` | Event DAG cycle detection, Novikov self-consistency, Grandfather (`CAU-101`) & Bootstrap (`CAU-102`) paradox linters, timeline split-and-merge DAG visualizers. |
| **10** | **Climate, Biomes & Trophic Webs** | `arcanum calc climate`, `arcanum ecology [world]` | Stellar insolation ($W/m^2$), atmospheric circulation cells (Hadley/Ferrel), orographic rain shadow modeler, Bestiary trophic profiler, Lindeman 10% energy pyramid validator. |
| **11** | **Earth-Eponyms & Sensory Palette** | `arcanum audit idioms [ms]`, `arcanum audit senses [ms]` | Earth-eponym scanner (*Achilles heel*, *Pandora's box*, *boycott*, *diesel*) with custom whitelist, 6D sensory balance analyzer (Visual, Auditory, Olfactory, Gustatory, Tactile, Kinesthetic) to flag "white room" scenes. |
| **12** | **Ciphers, Runes & Prophecy Matrix** | `arcanum cipher encode|decode|runes`, `arcanum prophecy [world] [ms]` | Classical ciphers (Caesar, Atbash, Vigenère, Rail Fence), Elder Futhark rune vector SVG renderer, prophecy clause lifecycle tracker (`Cosmology/Prophecies/*.md`) auditing resolution across chapters. |

---

## 🖥️ Desktop Launchers & Unified CLI (No Terminal Daily Work)

Ars Arcanum provides both intuitive GUI launchers and a unified CLI dispatcher (`arcanum` or `ars-arcanum`):

1. **`Ars Arcanum Control Center` (`arcanum control-center`)**: Native Python/GTK 3 dashboard with 5 tabs:
   - **🪐 Universes & Worlds**: Universe and World Lore Vault management, creation wizards, toolchain launchers.
   - **✍️ Manuscripts & Drafting**: Manuscript hierarchy tree, live word counts, **Word Processing Toolbar** ("Open in Word Processor", "Sync DOCX ↔ Markdown", "DOCX Formatting Settings"), **Manuscript Draft Revisions & Redline Comparator** (fork drafts, visual diff, LibreOffice bridge), and the **Visual Scene Metadata Inspector** for `@pov`, `@char`, `@location`, `@thread`, `@time`, `@status`.
   - **📚 Publishing & Exports**: 1-Click Typst PDF, Pandoc EPUB, and submission DOCX export, automated Back-Matter Concordance & Dramatis Personae generator, volume selector (`Book-01`, `Book-02`, Omnibus), trim size presets (6x9, 5.5x8.5, 5x8), live PDF viewer.
   - **🔒 Snapshots & Backups**: 1-Click Git version snapshot button with log viewer, standalone `.tar.gz` + SHA-256 backup creator, **Dual-Target Secure External/USB Backup destination manager**, restore drill wizard.
   - **🩺 Diagnostics & Doctor**: Ars Arcanum toolchain status badges, World Bible lore consistency checks (`world-doctor`), 7-stage verification trigger.
2. **`Write & Open Workspace` (`arcanum write [target]`)**: Opens novelWriter (for manuscripts) or Obsidian (for world lore) directly without terminal management.
3. **`Word Processor Drafting & Sync` (`arcanum word [ms]` / `arcanum docx <build|sync|import|open> [ms]`)**:
   - `arcanum word [ms]`: Opens active manuscript draft in Microsoft Word, Google Docs, or LibreOffice Writer.
   - `arcanum docx sync [ms]`: Bidirectionally syncs prose changes between `.docx` and Markdown while preserving scene metadata tags.
   - `arcanum config docx-preset <preset>`: Switches global formatting preset (`standard-submission`, `modern-manuscript`, `classic-trade`, `custom`).
4. **`New Project Scaffolder` (`arcanum new <manuscript|draft|world|universe|volume> <name>`)**: Scaffolds novels, drafts, world lore vaults, narrative universes, or subsequent manuscript volumes.
5. **`Manuscript Drafts & Redline Comparison` (`arcanum draft <ms>` / `arcanum compare <ms> <target_draft> <prior_draft>`)**:
   - `arcanum draft <ms> [name]`: Atomically forks existing prose into discrete draft folders (`Draft-01`, `Draft-02`, `Draft-03`), updates active draft pointer, and tags Git milestone.
   - `arcanum compare <ms> [d2] [d1] --browser`: Generates accessible, high-contrast standalone HTML Redline reports with soft pastel deletion/addition styling, word delta metrics, chapter navigation sidebar, and search filtering.
   - `arcanum compare <ms> [d2] [d1] --libreoffice`: Launches native LibreOffice Writer Track Changes comparison.
6. **`Save Snapshot` (`arcanum save [target] [-m "note"]` / `arcanum snapshot`)**: Records an instant timestamped Git version snapshot.
7. **`Dual-Target Secure Backups` (`arcanum backup [target]` / `arcanum backup-dest set <path>`)**:
   - `arcanum backup-dest set /media/usb/backups`: Configures a persistent secure secondary destination (USB, encrypted vault, external mount).
   - `arcanum backup <target>`: Creates standalone verified `.tar.gz` archive with SHA-256 sidecar, simultaneously replicating to both local `05-Backups/` and the configured secure destination with dual integrity verification.
8. **`Publish & Export` (`arcanum publish [manuscript] [--format book|submission|all]` / `arcanum export`)**: Compiles print PDF (Typst), distribution EPUB (Pandoc), and standard submission DOCX in one command.
9. **`Words & Analytics` (`arcanum words [manuscript]` / `arcanum report`)**: Shows live word counts, chapter metrics, and status breakdowns.
10. **`Back-Matter Concordance` (`arcanum concordance <world> --manuscript <ms>`)**: Compiles publication-ready Dramatis Personae and Glossary back-matter.
11. **`Health & Diagnostics` (`arcanum check` / `arcanum doctor` / `arcanum continuity`)**: Runs system diagnostics, toolchain verification, character consistency audits, and all 12 speculative fiction lore checks.
12. **`Fast Performance Cache` (`arcanum cache <scan|wordcounts|clear> [path]`)**: Manages mtime-keyed in-memory caching for sub-millisecond analytics.

---

## 🛑 Distraction Control & Focus Enforcement

1. **Firefox Site Blocker**:
   - Install **LeechBlock NG** from the [Firefox Add-ons Store](https://addons.mozilla.org/firefox/addon/leechblock-ng/).
   - Open LeechBlock Options -> **Import** -> Select `configs/leechblock_arcanum_rules.json`.
   - Blocks YouTube, Reddit, Twitter/X, TikTok, and social media during writing hours (09:00–13:00 and 14:00–17:00).
2. **OS Notification Muting**:
   - Click the Notification Bell icon in the Linux Mint panel and toggle **Do Not Disturb**.
   - See [XFCE DND Guide](docs/guides/DISTRACTION_CONTROL.md) for custom keyboard shortcut setup.

---

## 🔒 Data Safety: Multi-Tier Version Control & The 3-2-1 Rule

1. **Multi-Tier Git Version History**:
   - Every Universe, World, and individual Book manuscript has dedicated Git version control.
   - Obsidian Git automatically commits changes every 10 minutes and on manual saves.
   - Click **Save Snapshot** (`arcanum snapshot`) anytime to create milestone commits.
2. **Dual-Target Standalone Archive Backups**:
   - Configure external backup target with `arcanum backup-dest set /media/usb/backups` or via Control Center.
   - Run `arcanum backup <project>` to create timestamped `.tar.gz` archives with SHA-256 verification checksums stored simultaneously in local `05-Backups/` and replicated to external media.
   - Test full system recovery with `arcanum restore`.
3. **Full-Disk Encryption & Automated External Backups**:
   - During Linux Mint installation, tick *"Encrypt the new Linux Mint installation"* (LUKS).
   - Use **Déjà Dup** for automated offsite/USB backups (see [Déjà Dup Backup Guide](docs/guides/BACKUP_SETUP.md)).

---

## 📚 Complete Resource Index

- [Author's Field Manual](docs/AUTHOR_MANUAL.md) — Visual plain-English handbook for novel writing, worldbuilding, and publishing.
- [Technical Architecture & ADRs](docs/ARCHITECTURE.md) — System blueprint, technical deep-dives, exit codes, and Architectural Decision Records (ADR-001 through ADR-028).
- [Software Catalog & Download Links](docs/guides/SOFTWARE_CATALOG.md) — Exact packages, Flatpak IDs, ISOs, and commands.
- [Optional Extras Guide](docs/guides/OPTIONAL_EXTRAS.md) — Azgaar maps, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix, and native standard library tools.
- [Typography & Fonts Guide](docs/guides/TYPOGRAPHY_AND_FONTS.md) — Free literary typefaces (Linux Libertine, EB Garamond, Alegreya), DOCX styling presets, and Typst formatting rules.
- [Obsidian Plugin Suite Guide](docs/guides/OBSIDIAN_PLUGINS.md) — Pre-configured Obsidian writing and worldbuilding suite with Metadata Menu schemas.
- [Distraction Control Guide](docs/guides/DISTRACTION_CONTROL.md) — XFCE notification muting and FocusWriter tips.
- [Automated Backup Guide](docs/guides/BACKUP_SETUP.md) — 3-2-1 backup strategy with Déjà Dup and native dual-target replication.
- [Typst Book Template](templates/typst/book_template.typ) — Reusable novel layout engine.
- [Obsidian World Bible Index Dashboard](templates/world-bible/Templates/World-Bible-Index.md) — Dataview queries and lore hub.
- [Roadmap & Milestones](docs/ROADMAP.md) — Project charter, hardware baselines, milestones (M0–M21), and operational status.

---

## 🗺️ Project Docs (for contributors)

| Doc | What it is |
| :--- | :--- |
| [docs/AUTHOR_MANUAL.md](docs/AUTHOR_MANUAL.md) | Comprehensive Author's Field Manual for daily writing, lore building, DOCX dual-sync, 12 speculative engines, and publication |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture, invariants, exit codes, and full ADR catalog (ADR-001 through ADR-028) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Project charter, milestones (M0–M21), hardware baseline, and real-time status queues |
| [CHANGELOG.md](CHANGELOG.md) | Notable changes: audit remediation series, separated architecture, multi-drafts, DOCX sync, and 12 speculative fiction engines |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute: ground rules, exit-code contract, quality gate, commit style, submission flow |
| [SECURITY.md](SECURITY.md) | Security scope, installer privilege surface disclosure, and private vulnerability reporting |
| [PRIVACY.md](PRIVACY.md) | Privacy policy, offline data minimization, and zero telemetry guarantee |
| [REFERENCES.md](REFERENCES.md) | Asset provenance, Creative Commons / FOSS attribution index, and licensing references |
| [docs/SUPPORT_MATRIX.md](docs/SUPPORT_MATRIX.md) | Supported Linux distributions, desktop environments, architectures, and display servers |
| [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) | Toolchain version baselines, SHA-256 binary digests, and Flatpak application IDs |
| [scripts/verify.sh](scripts/verify.sh) | 7-stage automated health check: syntax, schema validation, Universe/World lifecycle, Git snapshots, and backup/restore drills |

