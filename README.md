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

> **Start here:** [Quick Start](#-quick-start-automated-setup) installs everything. Remaining Linux-only checks (Typst compile, LeechBlock import, novelWriter project) are in [Finishing_Touches.md](Finishing_Touches.md). Run `bash scripts/verify.sh` anytime for a 30-second health check.

---

## 🌟 Overview & Architecture

Scriptorium provides everything an author needs to brainstorm lore, outline storylines, draft prose, revise manuscripts, compile ebooks, and typeset publication-grade print PDFs—without proprietary software locks or continuous maintenance.

```
~/Universes/<UniverseName>/
├── universe.yaml              → Universe manifest & overarching continuity repository
└── Worlds/<WorldName>/        → World repository (with Obsidian Git auto-commit)
    ├── 00-World-Bible/        → Pre-configured Obsidian Vault (Dataview, Longform, Metadata Menu, Calendarium, etc.)
    │   ├── .obsidian/         → Out-of-the-box plugin configs & fileClasses schemas
    │   ├── Characters/        → Character profiles with Dataview metadata & relationship maps
    │   ├── Locations/         → Sensory regional palettes, cities, and landmarks
    │   ├── Factions/          → Guilds, empires, ideologies, and member rosters
    │   ├── Magic-Technology/ → Hard/soft magic rules, limitations, and costs
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
   *This single command tests your OS environment, installs Git, Zenity, LibreOffice, FocusWriter, Calibre, Obsidian, novelWriter, Typst, Pandoc, literary typography fonts, and installs desktop launchers.*

3. **Double-click "Scriptorium Control Center" or "New World Creator" on your Desktop** (or run `scriptorium gui` / `scriptorium new`). Enter your novel's title (e.g. `Eldoria`) and universe. Your complete world folder is generated with all Obsidian plugins, fileClasses schemas, and multi-tier Git tracking enabled!

---

## 🛠️ Core Toolchain

| Creative Phase | Tool | Format | Role & Setup |
| :--- | :--- | :--- | :--- |
| **World Bible & Wiki** | **Obsidian** | Markdown (`.md`) | Open `00-World-Bible` as Vault. Comes pre-configured with **Longform**, **Dataview**, **Metadata Menu**, **Calendarium**, **Storyteller Suite**, **Storyline**, **Novel Word Count**, and **Obsidian Git** (10-min auto-commits). (See [Plugin Guide](templates/world-bible/.obsidian-recommended-plugins.md)) |
| **Outlining & Drafting** | **novelWriter** / **Longform** | Markdown (`.md`) + `nwProject.nwx` | In novelWriter choose `New Project` inside `01-Manuscript` or draft natively in Obsidian with Longform atomic scenes. In novelWriter, import `Book-01/*/*.md` starters with `@pov:` and `@tag:` annotations. Use full-screen Focus Mode. |
| **Deep Sprint Canvas** | **FocusWriter** | Plaintext (`.txt` / `.md`) | Minimalist full-screen distraction-free distraction sprint sessions (`F11`). |
| **Revisions & Collaboration**| **LibreOffice Writer** | `.odt` / `.docx` | Track changes with professional editors and redlining. |
| **Ebook Compilation** | **Calibre** | `.epub` / `.mobi` | Graphical EPUB inspection, metadata tagging, and e-reader sync. |
| **Typesetting & Print PDF** | **Typst + Pandoc** | `.typ` / Vector PDF | Compiles sub-second, publication-grade print PDFs with trade margins, alternating running headers, and front matter (half-title, title, copyright, dedication). |

---

## 🖥️ Desktop Launchers & Unified CLI (No Terminal Daily Work)

Scriptorium provides both intuitive GUI launchers and a unified CLI dispatcher (`scriptorium`):

1. **`Scriptorium Control Center` (`scriptorium gui`)**: Central dashboard to launch writing tools, create universes/worlds, save version snapshots, create standalone backups, run diagnostics, and compile books.
2. **`New World Creator` (`scriptorium new` / `scriptorium universe`)**: Graphical wizard to scaffold a new Universe or World with multi-tier Git repos and pre-configured Obsidian vault suites.
3. **`Export Book` (`scriptorium export`)**: Compiles your manuscript into a print-ready PDF via Typst and an EPUB via Pandoc in one click.
4. **`Save Snapshot` (`scriptorium snapshot`)**: Records timestamped Git version snapshots across your world and manuscript repositories.

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

- [Software Catalog & Download Links](resources/software_catalog.md) — Exact packages, Flatpak IDs, ISOs, and commands.
- [Optional Extras Guide](resources/optional_extras_guide.md) — Azgaar maps, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix.
- [Typography & Fonts Guide](resources/typography_and_fonts_guide.md) — Free literary typefaces (Linux Libertine, EB Garamond, Alegreya) and Typst formatting rules.
- [Typst Book Template](templates/typst/book_template.typ) — Reusable novel layout engine.
- [Obsidian World Bible Index Dashboard](templates/world-bible/Templates/World-Bible-Index.md) — Dataview queries and lore hub.
- [Architecture Decision Records](decisions.md) — ADRs covering OS selection, Markdown storage, Typst typesetting, Multi-tier Git, and Obsidian plugin architecture.

---

## 🗺️ Project Docs (for contributors)

| Doc | What it is |
| :--- | :--- |
| [project.md](project.md) | Charter: goals, design invariants, hardware baseline, non-goals |
| [plan.md](plan.md) | Build phases and what is done vs pending live verification |
| [tasks.md](tasks.md) | Checklist of every deliverable |
| [decisions.md](decisions.md) | Architecture decision records (why Mint, Markdown, Typst, Multi-tier Git, Obsidian plugins) |
| [knowledge.md](knowledge.md) | Tool ecosystem facts, multi-tier Git invariants, and script safety standards |
| [status.md](status.md) | Current state + momentum queues (now / next / blocked / improve / recurring) |
| [Finishing_Touches.md](Finishing_Touches.md) | Manual for live Linux verification and writer workflows |
| [scripts/verify.sh](scripts/verify.sh) | 7-stage automated health check: syntax, schema validation, Universe/World lifecycle, Git snapshots, and backup/restore drills |

