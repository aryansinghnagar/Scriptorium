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
~/Worlds/<WorldName>/
├── 00-World-Bible/        → Open this folder as an Obsidian vault (Lore, Characters, Atlas)
│   ├── Characters/        → Character profiles with Dataview metadata & relationship maps
│   ├── Locations/         → Sensory regional palettes, cities, and landmarks
│   ├── Factions/          → Guilds, empires, ideologies, and member rosters
│   ├── Magic-Technology/ → Hard/soft magic rules, limitations, and costs
│   ├── History/           → Historical eras, timelines, and catalytic events
│   ├── Languages/         → Conlangs, phonetic rules, and world glossaries
│   └── Templates/         → Daily writing logs, scene cards, and central index
├── 01-Manuscript/         → Create a novelWriter project here, then import the starters
│   ├── Book-01/           → Chapters & scenes structured by Act/Chapter
│   │   ├── 01_Act_I/
│   │   ├── 02_Act_II/
│   │   └── 03_Act_III/
│   ├── Outlines/          → Three-act structural beats & scene goals
│   └── nwProject.nwx      → novelWriter project manifest
├── 02-Maps/               → Cartography assets (Azgaar exports, Krita paintings, Inkscape vectors)
├── 03-Art/                → Visual references, character sketches, cover mockups
├── 04-Publishing/         → Exported print PDFs (Typst) and distribution EPUBs (Pandoc)
└── 05-Backups/            → Local snapshot archives (Git & Déjà Dup targets)
```

---

## 🚀 Quick Start (Automated Setup)

If you have booted into Linux Mint XFCE or Debian:

1. **Clone or download this repository** into your home folder:
   ```bash
   cd ~/Downloads
   git clone https://github.com/<your-username>/7-Scriptorium.git Scriptorium
   cd Scriptorium
   ```
   > Replace `<your-username>` with your GitHub username after pushing this project.
2. **Run the automated setup installer**:
   ```bash
   bash scripts/setup_scriptorium.sh
   ```
   *This single command installs Git, Zenity, LibreOffice, FocusWriter, Calibre, Obsidian, novelWriter, Typst, Pandoc, high-end book typography fonts, and installs desktop launchers.*

3. **Double-click "New World Creator" on your Desktop** (or run `./scripts/init_world.sh`). Enter your novel's title (e.g. `Eldoria`). Your complete world folder is generated with all templates and Git tracking enabled!

---

## 🛠️ Core Toolchain

| Creative Phase | Tool | Format | Role & Setup |
| :--- | :--- | :--- | :--- |
| **World Bible & Wiki** | **Obsidian** | Markdown (`.md`) | Open `00-World-Bible` as Vault. Enable community plugins: Dataview, Templater, Kanban, Excalidraw. (See [Plugin Guide](templates/world-bible/.obsidian-recommended-plugins.md)) |
| **Outlining & Drafting** | **novelWriter** | Markdown (`.md`) + `nwProject.nwx` | In novelWriter choose `New Project` inside `01-Manuscript` and import the `Book-01/*/*.md` starters (`nwProject.nwx` in repo is a documented placeholder; real format is fileVersion 1.5 with `content/*.nwd`). Structure acts, chapters, and scenes with `@pov:` and `@tag:` annotations. Use full-screen Focus Mode. |
| **Deep Sprint Canvas** | **FocusWriter** | Plaintext (`.txt` / `.md`) | Minimalist full-screen distraction-free distraction sprint sessions (`F11`). |
| **Revisions & Collaboration**| **LibreOffice Writer** | `.odt` / `.docx` | Track changes with professional editors and redlining. |
| **Ebook Compilation** | **Calibre** | `.epub` / `.mobi` | Graphical EPUB inspection, metadata tagging, and e-reader sync. |
| **Typesetting & Print PDF** | **Typst + Pandoc** | `.typ` / Vector PDF | Compiles sub-second, publication-grade print PDFs with trade margins, alternating running headers, and front matter (half-title, title, copyright, dedication). |

---

## 🖥️ Desktop Launchers (No Terminal Daily Work)

Scriptorium installs three simple desktop launchers:

1. **`New World Creator`**: Graphical wizard to scaffold a new world or novel series in `~/Worlds/`.
2. **`Export Book`**: Compiles your manuscript into a print-ready PDF via Typst and an EPUB via Pandoc in one click.
3. **`Save Snapshot`**: Records a timestamped Git version snapshot of your entire world and manuscript (local history; encryption comes from full-disk LUKS + Déjà Dup password-protected backups, not from Git itself).

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

## 🔒 Data Safety: The 3-2-1 Rule

1. **Full-Disk Encryption**: During Linux Mint installation, tick *"Encrypt the new Linux Mint installation"* (LUKS). Protects against lost or stolen hardware.
2. **Automated Weekly Backups**:
   - Plug in an external USB drive.
   - Open **Backups** (Déjà Dup).
   - Set source to `~/Worlds` (or `~`), set destination to the USB drive, enable password protection, and turn on the weekly schedule.
   - See [Déjà Dup Backup Guide](configs/deja_dup_backup_guide.md).
3. **Instant Version History**:
   - Click **Save Snapshot** whenever you finish a writing sprint. You can roll back to any past version anytime.

---

## 📚 Complete Resource Index

- [Software Catalog & Download Links](resources/software_catalog.md) — Exact packages, Flatpak IDs, ISOs, and commands.
- [Optional Extras Guide](resources/optional_extras_guide.md) — Azgaar maps, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix.
- [Typography & Fonts Guide](resources/typography_and_fonts_guide.md) — Free literary typefaces (Linux Libertine, EB Garamond, Alegreya) and Typst formatting rules.
- [Typst Book Template](templates/typst/book_template.typ) — Reusable novel layout engine.
- [Obsidian World Bible Index Dashboard](templates/world-bible/Templates/World-Bible-Index.md) — Dataview queries and lore hub.

---

## 🗺️ Project Docs (for contributors)

| Doc | What it is |
| :--- | :--- |
| [project.md](project.md) | Charter: goals, design invariants, hardware baseline, non-goals |
| [plan.md](plan.md) | Build phases and what is done vs pending live verification |
| [tasks.md](tasks.md) | Checklist of every deliverable |
| [decisions.md](decisions.md) | Architecture decision records (why Mint, Markdown, Typst, LeechBlock, placeholders, hardening) |
| [knowledge.md](knowledge.md) | Tool ecosystem facts and script safety invariants |
| [status.md](status.md) | Current state + momentum queues (now / next / blocked / improve / recurring) |
| [Finishing_Touches.md](Finishing_Touches.md) | Manual for the remaining Linux-only checks |
| [scripts/verify.sh](scripts/verify.sh) | 30-second health check: `bash -n`, JSON/XML parse, Pandoc→Typst smoke test, Typst compile if installed, desktop-entry check |
| [docs/archive/](docs/archive/) | Superseded early drafts (`LEGACY_scriptorium_plan.*`), kept for history |
