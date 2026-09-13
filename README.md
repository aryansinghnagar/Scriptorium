# Scriptorium — A Simple Linux Writing Setup

> **A low-effort, beginner-friendly system for novels and worldbuilding.**  
> Built for authors on Linux Mint (XFCE) & Debian. Everything in open Markdown. Zero terminal required for daily writing.

[![Status: Work in Progress](https://img.shields.io/badge/Status-Work--In--Progress-orange.svg)](#)
[![Testing: Untested](https://img.shields.io/badge/Testing-Untested-red.svg)](#)
[![Stability: Experimental](https://img.shields.io/badge/Stability-Experimental-red.svg)](#)

> [!CAUTION]
> ### ⚠️ EXPERIMENTAL & UNTESTED — WORK IN PROGRESS
> This repository is an active **Work-In-Progress (WIP)** and is currently **untested across standard Linux distributions**.
>
> - **Experimental Setup Scripts**: The automated setup and environment scripts (`setup.sh`, `verify.sh`, package installations) are experimental and may overwrite or conflict with local desktop configurations.
> - **Not for General End Users**: This workspace template is not intended for non-technical users or mission-critical authoring without prior independent backups.
> - **Use at Your Own Risk**: Automated system scripts and configuration adjustments could alter local system packages, fonts, or desktop settings unexpectedly.

> **Start here:** Consult the comprehensive [Author's Field Manual](docs/AUTHOR_MANUAL.md) for a visual step-by-step guide to worldbuilding, multi-volume drafting, automated concordance generation, and publishing. Run [Quick Start](#-quick-start-automated-setup) to install everything. Run `bash scripts/verify.sh` anytime for a comprehensive health check.

---

## 🌟 Overview & Architecture

Scriptorium provides everything an author needs to brainstorm lore, outline storylines, draft prose, revise manuscripts, compile ebooks, and typeset publication-grade print PDFs—without proprietary software locks or continuous maintenance.

```
~/Universes/<UniverseName>/
├── universe.yaml              → Universe manifest & overarching continuity repository
├── Universe-Index.md          → Narrative cosmos hub & cross-world index
└── Worlds/<WorldName>/        → World repository (with Obsidian Git auto-commit)
    ├── 00-World-Bible/        → Pre-configured Obsidian Vault (Dataview, Longform, Metadata Menu, etc.)
    │   ├── .obsidian/         → Out-of-the-box plugin configs & fileClasses schemas
    │   ├── Characters/        → Character profiles with Dataview metadata & relationship maps
    │   ├── Locations/         → Sensory regional palettes, cities, and landmarks
    │   ├── Factions/          → Guilds, empires, ideologies, and member rosters
    │   ├── Magic-Technology/ → Hard/soft magic rules, limitations, and costs
    │   ├── Bestiary/          → Creatures, apex predators, flora, and monster ecologies
    │   ├── Artifacts/         → Legendary relics, magical weapons, and focal items
    │   ├── Cosmology/         → Pantheons, deities, astral planes, and mythos
    │   ├── History/           → Historical eras, timelines, and catalytic events
    │   ├── Languages/         → Conlangs, phonetic rules, and world glossaries
    │   └── Templates/         → fileClasses schemas, writing logs, scene cards, and central index
    ├── 01-Manuscript/         → Manuscript drafting volume storage
    │   ├── Book-01/           → Discrete Git repository for Book-01 (Acts, Chapters, Scenes)
    │   │   ├── 01_Act_I/
    │   │   ├── 02_Act_II/
    │   │   └── 03_Act_III/
    │   ├── Outlines/          → Three-act structural beats & scene goals
    │   └── nwProject.nwx      → novelWriter project manifest (fileVersion 1.5)
    ├── 02-Maps/               → Cartography assets (Azgaar exports, Krita paintings, Inkscape vectors)
    ├── 03-Art/                → Visual references, character sketches, cover mockups
    ├── 04-Publishing/         → Exported print PDFs (Typst) and distribution EPUBs (Pandoc)
    └── 05-Backups/            → Standalone timestamped .tar.gz archives with SHA-256 digests
```

---

## 🚀 Quick Start (Automated Setup)

If you have booted into Linux Mint XFCE or Debian:

1. **Clone or download this repository** into your home folder:
   ```bash
   cd ~/Downloads
   git clone https://github.com/aryansinghnagar/Scriptorium.git Scriptorium
   cd Scriptorium
   ```
2. **Run the automated setup installer**:
   ```bash
   bash scripts/setup_scriptorium.sh
   ```
   *This single command tests your OS environment, installs Git, PyGObject, Zenity, LibreOffice, FocusWriter, Calibre, Obsidian, novelWriter, Typst, Pandoc, literary typography fonts, and installs desktop launchers.*

3. **Double-click "Scriptorium Control Center" on your Desktop** (or run `scriptorium gui`). On first launch, the welcoming wizard offers a 1-click starter cosmos (*"The Chronicles of Eldoria"*) with pre-configured lore and starter chapters!

---

## 🛠️ Core Toolchain

| Creative Phase | Tool | Format | Role & Setup |
| :--- | :--- | :--- | :--- |
| **Desktop Control Center** | **Scriptorium App** | Native GTK 3 / Zenity | 5-tab author dashboard for Cosmos management, live word count analytics, 1-click Typst/Pandoc publishing, Git version snapshots, and Doctor diagnostics. |
| **World Bible & Wiki** | **Obsidian** | Markdown (`.md`) | Open `00-World-Bible` as Vault. Comes pre-configured with **Longform**, **Dataview**, **Metadata Menu**, **Calendarium**, **Storyteller Suite**, **Storyline**, **Novel Word Count**, and **Obsidian Git** (10-min auto-commits). (See [Plugin Guide](docs/OBSIDIAN_PLUGINS_GUIDE.md)) |
| **Outlining & Drafting** | **novelWriter** / **Longform** | Markdown (`.md`) + `nwProject.nwx` | In novelWriter choose `New Project` inside `01-Manuscript` or draft natively in Obsidian with Longform atomic scenes. In novelWriter, import `Book-01/*/*.md` starters with `@pov:` and `@tag:` annotations. Use full-screen Focus Mode. |
| **Deep Sprint Canvas** | **FocusWriter** | Plaintext (`.txt` / `.md`) | Minimalist full-screen distraction-free distraction sprint sessions (`F11`). |
| **Revisions & Collaboration**| **LibreOffice Writer** | `.odt` / `.docx` | Track changes with professional editors and redlining. |
| **Ebook Compilation** | **Calibre** | `.epub` / `.mobi` | Graphical EPUB inspection, metadata tagging, and e-reader sync. |
| **Typesetting & Print PDF** | **Typst + Pandoc** | `.typ` / Vector PDF | Compiles sub-second, publication-grade print PDFs with trade margins, alternating running headers, ornamental breaks, and front matter (half-title, title, copyright, dedication). |

---

## 🖥️ Desktop Launchers & Unified CLI (No Terminal Daily Work)

Scriptorium provides both intuitive GUI launchers and a unified CLI dispatcher (`scriptorium`):

1. **`Scriptorium Control Center` (`scriptorium gui`)**: Native Python/GTK 3 dashboard with 5 tabs:
   - **Cosmos & Projects**: Universe and World management, creation wizards, toolchain launchers.
   - **Writing & Analytics**: Manuscript hierarchy tree, live word counts, act rollups, session pacing.
   - **Publishing Studio**: 1-Click Typst PDF & Pandoc EPUB export, automated Back-Matter Concordance & Dramatis Personae generator, volume selector (`Book-01`, `Book-02`, Omnibus), trim size presets (6x9, 5.5x8.5, 5x8), live PDF viewer.
   - **Vault Safety & Backups**: 1-Click Git version snapshot button with log viewer, standalone `.tar.gz` + SHA-256 backup creator, restore drill wizard.
   - **Doctor Diagnostics**: Scriptorium toolchain status badges, World Bible lore consistency checks (`world_doctor`), 7-stage verification trigger.
2. **`New World Creator` (`scriptorium init <name>` / `scriptorium universe`)**: Graphical wizard to scaffold a new Universe or World with multi-tier Git repos and pre-configured Obsidian vault suites.
3. **`Add Book Volume` (`scriptorium add-book <world> [book]`)**: Scaffolds subsequent manuscript volumes (`Book-02`, `Book-03`, etc.) with three acts, sample chapters, and discrete Git repos.
4. **`Back-Matter Concordance` (`scriptorium concordance <world> [-b Book-01|all]`)**: Automatically parses World Bible lore into publication-ready `01_Dramatis_Personae.md` and `02_Glossary_and_Concordance.md` back-matter.
5. **`Export Book` (`scriptorium export <world> [-b Book-01|all] [-s us-trade|trade|pocket]`)**: Compiles your manuscript or specific volume into a print-ready PDF via Typst and an EPUB via Pandoc in one click (with trim size presets, auto-detected EPUB cover art in `03-Art/cover.png` or `.jpg`, and interactive volume picker when multiple books exist).
6. **`Save Snapshot` (`scriptorium snapshot <world> [-m note]`)**: Records timestamped Git version snapshots across your world and manuscript repositories.

---

## 🛑 Distraction Control & Focus Enforcement

1. **Firefox Site Blocker**:
   - Install **LeechBlock NG** from the [Firefox Add-ons Store](https://addons.mozilla.org/firefox/addon/leechblock-ng/).
   - Open LeechBlock Options -> **Import** -> Select `configs/leechblock_scriptorium_rules.json`.
   - If import warns about schema, manually recreate one block set from the JSON (`sites`, `times 0900-1300,1400-1700`) — export format varies by LeechBlock version and must be live-verified.
   - Blocks YouTube, Reddit, Twitter/X, TikTok, and social media during your writing hours (09:00–13:00 and 14:00–17:00).
2. **OS Notification Muting**:
   - Click the Notification Bell icon in the Linux Mint panel and toggle **Do Not Disturb**.
   - See [XFCE DND Guide](configs/xfce_dnd_setup.md) for custom keyboard shortcut setup.

---

## 🔒 Data Safety: Multi-Tier Version Control & The 3-2-1 Rule

1. **Multi-Tier Git Version History**:
   - Every Universe, World, and individual Book manuscript has dedicated Git version control.
   - Obsidian Git automatically commits changes every 10 minutes and on manual saves.
   - Click **Save Snapshot** (`scriptorium snapshot`) anytime to create milestone commits.
2. **Standalone Archive Backups**:
   - Run `scriptorium backup` or use the Control Center to create timestamped `.tar.gz` archives with SHA-256 verification checksums stored in `05-Backups/` or external media.
   - Test full system recovery with `scriptorium restore`.
3. **Full-Disk Encryption & Automated External Backups**:
   - During Linux Mint installation, tick *"Encrypt the new Linux Mint installation"* (LUKS).
   - Use **Déjà Dup** for automated offsite/USB backups (see [Déjà Dup Backup Guide](configs/deja_dup_backup_guide.md)).

---

## 📚 Complete Resource Index

- [Author's Field Manual](docs/AUTHOR_MANUAL.md) — Visual plain-English handbook for novel writing, worldbuilding, and publishing.
- [Software Catalog & Download Links](resources/software_catalog.md) — Exact packages, Flatpak IDs, ISOs, and commands.
- [Optional Extras Guide](resources/optional_extras_guide.md) — Azgaar maps, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix.
- [Typography & Fonts Guide](resources/typography_and_fonts_guide.md) — Free literary typefaces (Linux Libertine, EB Garamond, Alegreya) and Typst formatting rules.
- [Typst Book Template](templates/typst/book_template.typ) — Reusable novel layout engine.
- [Obsidian World Bible Index Dashboard](templates/world-bible/Templates/World-Bible-Index.md) — Dataview queries and lore hub.
- [Architecture Decision Records](decisions.md) — ADRs covering OS selection, Markdown storage, Typst typesetting, Multi-tier Git, Obsidian plugin architecture, and GTK Control Center.

---

## 🗺️ Project Docs (for contributors)

| Doc | What it is |
| :--- | :--- |
| [docs/AUTHOR_MANUAL.md](docs/AUTHOR_MANUAL.md) | Comprehensive Author's Field Manual for daily writing, lore building, and publication |
| [project.md](project.md) | Charter: goals, design invariants, hardware baseline, non-goals |
| [plan.md](plan.md) | Build phases and what is done vs pending live verification |
| [tasks.md](tasks.md) | Checklist of every deliverable |
| [decisions.md](decisions.md) | Architecture decision records (why Mint, Markdown, Typst, Multi-tier Git, Obsidian plugins, GTK App) |
| [knowledge.md](knowledge.md) | Tool ecosystem facts, multi-tier Git invariants, and script safety standards |
| [status.md](status.md) | Current state + momentum queues (now / next / blocked / improve / recurring) |
| [scripts/verify.sh](scripts/verify.sh) | 7-stage automated health check: syntax, schema validation, Universe/World lifecycle, Git snapshots, and backup/restore drills |

