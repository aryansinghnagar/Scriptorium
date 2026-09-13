# Scriptorium Author's Field Manual
### The Complete Plain-Language Guide to Local-First Novel Writing & Speculative Worldbuilding

Welcome to **Scriptorium**! Whether you are writing your debut novel, crafting a sprawling multi-volume epic fantasy cosmos, or organizing deep speculative science fiction lore, Scriptorium gives you a professional, distraction-free environment that is 100% private, open, and permanently yours.

Zero programming or terminal experience is required for daily writing. Everything is accessible through the **Scriptorium Control Center** desktop app.

---

## 📑 Table of Contents
1. [The Scriptorium Philosophy & Architecture](#1-the-scriptorium-philosophy--architecture)
2. [Quick Start: Your First 5 Minutes](#2-quick-start-your-first-5-minutes)
3. [The Desktop Control Center Tour](#3-the-desktop-control-center-tour)
   - [Tab 1: Cosmos & Projects](#tab-1-cosmos--projects)
   - [Tab 2: Writing & Analytics](#tab-2-writing--analytics)
   - [Tab 3: Publishing Studio](#tab-3-publishing-studio)
   - [Tab 4: Vault Safety & Backups](#tab-4-vault-safety--backups)
   - [Tab 5: Doctor Diagnostics](#tab-5-doctor-diagnostics)
4. [Worldbuilding in Obsidian (The 9 Core Lore Vaults)](#4-worldbuilding-in-obsidian-the-9-core-lore-vaults)
5. [Drafting & Sprint Sessions](#5-drafting--sprint-sessions)
6. [Typesetting & Book Publishing (Typst & Pandoc)](#6-typesetting--book-publishing-typst--pandoc)
7. [Data Safety, Version History & The 3-2-1 Rule](#7-data-safety-version-history--the-3-2-1-rule)
8. [Author's Quick Reference & Troubleshooting FAQ](#8-authors-quick-reference--troubleshooting-faq)

---

## 1. The Scriptorium Philosophy & Architecture

### Why Scriptorium Exists
Most modern writing software locks your words into proprietary database formats, monthly cloud subscriptions, or closed operating systems. If the company changes pricing or shuts down, your work is in jeopardy.

Scriptorium is built on **Four Unbreakable Invariants**:
1. **Sovereign Plain Markdown (`.md`)**: Every word, outline, character bio, and chapter is stored in human-readable plain text files on your own hard drive. You can open and read your work 50 years from now on any computer.
2. **One Premier Tool Per Creative Stage**:
   - **Obsidian**: For your World Bible, character dossiers, maps, and timeline wikis.
   - **novelWriter / FocusWriter**: For distraction-free deep drafting sprints.
   - **LibreOffice Writer**: For collaborative editing and track-changes with editors.
   - **Typst + Pandoc**: For sub-second, Vellum-quality print PDF and EPUB typesetting.
   - **Calibre**: For graphical ebook inspection and e-reader synchronization.
3. **Zero Terminal Requirement**: Everything you do on a daily basis is executable with a single click in the graphical desktop app.
4. **Ironclad 3-2-1 Data Safety**: Automatic background version control, 1-click milestone snapshots, and standalone verified USB backups protect your life's work against hardware failure or accidental deletion.

```
~/Universes/<UniverseName>/
├── universe.yaml              → Overarching Universe manifest & continuity Git repository
├── Universe-Index.md          → Narrative cosmos hub & cross-world index
└── Worlds/<WorldName>/        → World repository (with Obsidian Git auto-commit)
    ├── 00-World-Bible/        → Pre-configured Obsidian Vault (Lore, Characters, Maps)
    │   ├── Characters/        → Character dossiers & psychological arcs
    │   ├── Locations/         → Atlas, sensory palettes, and regional maps
    │   ├── Factions/          → Guilds, empires, sects & member rosters
    │   ├── Magic-Technology/ → Hard/soft magic rules, limitations & costs
    │   ├── Bestiary/          → Creatures, apex predators, flora, and monster ecologies
    │   ├── Artifacts/         → Legendary relics, magical weapons, and focal items
    │   ├── Cosmology/         → Pantheons, deities, astral planes, and mythos
    │   ├── History/           → Historical eras, timelines, and catalytic events
    │   ├── Languages/         → Conlangs, phonetic rules, and world glossaries
    │   └── Templates/         → Dropdown schema forms, writing logs, and index dashboard
    ├── 01-Manuscript/         → Manuscript volume drafting folders
    │   ├── Book-01/           → Discrete Git repository for Book-01 (Acts, Chapters, Scenes)
    │   │   ├── 01_Act_I/
    │   │   ├── 02_Act_II/
    │   │   └── 03_Act_III/
    │   ├── Outlines/          → Three-act structural beats & scene goals
    │   └── nwProject.nwx      → novelWriter project manifest
    ├── 02-Maps/               → Cartography assets & interactive Storyteller Suite maps
    ├── 03-Art/                → Visual references, character sketches, cover mockups
    ├── 04-Publishing/         → Exported print PDFs (Typst) and distribution EPUBs (Pandoc)
    └── 05-Backups/            → Standalone timestamped .tar.gz archives with SHA-256 digests
```

---

## 2. Quick Start: Your First 5 Minutes

### Step 1: Open Scriptorium Control Center
Double-click **"Scriptorium Control Center"** on your Desktop (or run `scriptorium gui` in a terminal).

### Step 2: Create or Explore a Project
- **Option A (Instant Exploration)**: Click **"✨ Generate Demo Cosmos"** in Tab 1. This creates *"The Chronicles of Eldoria"*, pre-loaded with characters, bestiaries, magic systems, and sample chapters.
- **Option B (Your Own Story)**: Click **"+ New World"**, enter your novel's title (e.g. `Solaris-Rising`), choose a Universe, and click **OK**.

### Step 3: Start Writing!
- Click **"📖 Open World Bible"** to view and edit lore in Obsidian.
- Click **"✍️ Drafting Studio"** to write your scenes in novelWriter or Longform.
- Click **"⚡ Sprint Canvas"** to enter full-screen distraction-free mode in FocusWriter.

---

## 3. The Desktop Control Center Tour

The Scriptorium desktop application is organized into **5 intuitive tabs**:

### Tab 1: Cosmos & Projects
- **Universe & World Selector**: Switch between different narrative universes and book series seamlessly.
- **Project Creation**: Create new Universe containers (`+ New Universe`) or new worlds (`+ New World`) with automated multi-tier Git tracking.
- **Creative Studio Launchers**: 1-click buttons to launch Obsidian, novelWriter, FocusWriter, LibreOffice, Calibre, or your project's file manager.

### Tab 2: Writing & Analytics
- **Live Word Count Dashboard**: Displays total manuscript word counts, scene counts, and daily pacing metrics.
- **Manuscript Explorer**: An interactive tree view listing every Volume (`Book-01`, `Book-02`), Act, Chapter, and Scene file with individual word count tallies.
- **Refresh Stats**: Instantly recalculates word counts after a writing session.

### Tab 3: Publishing Studio
- **1-Click Typesetting**: Turn your Markdown manuscript into a print-ready vector PDF and an EPUB ebook in seconds.
- **Volume Selector**: Choose to compile an individual volume (`Book-01`, `Book-02`) or the entire series omnibus.
- **Trim Size Presets**:
  - `US Trade (6 × 9 in)`: Standard commercial fiction and fantasy trade paperback.
  - `Trade (5.5 × 8.5 in)`: Compact novel trim size.
  - `Pocket (5 × 8 in)`: Mass-market paperback size.
- **Instant Preview**: Click **"📄 Open PDF"** or **"📱 Open EPUB"** immediately upon compilation.

### Tab 4: Vault Safety & Backups
- **Version Milestone Snapshot (Git)**: Type a short progress note (e.g. `Finished Chapter 4 battle`) and click **"📷 Save Snapshot"**.
- **Milestone History**: View recent Git commits across your world and manuscript repositories.
- **Standalone Archive Backup**: Click **"📦 Create Standalone Backup Archive"** to generate a compressed `.tar.gz` bundle with an immutable SHA-256 verification manifest in `05-Backups/` or onto an external USB drive.
- **Disaster Recovery Restore**: Click **"♻️ Restore World from Archive"** to safely unpack and verify any past backup archive.

### Tab 5: Doctor Diagnostics
- **System Toolchain Badges**: Live indicators confirming that Git, Pandoc, Typst, and Python 3 are installed and functional.
- **World Doctor**: Audits your Obsidian vault for broken wikilinks, dangling character/faction references, and chronological timeline anomalies (e.g. death dates before birth dates).
- **Verification Harness**: Run the automated 7-stage test suite to verify project integrity.

---

## 4. Worldbuilding in Obsidian (The 9 Core Lore Vaults)

Your World Bible (`00-World-Bible`) comes pre-configured with the premier worldbuilding and writing plugins enabled out of the box: **Dataview**, **Metadata Menu**, **Calendarium**, **Storyteller Suite**, **Storyline**, **Novel Word Count**, and **Obsidian Git**.

### The 9 Lore Categories

| Category | Folder | Template | What Goes Here |
| :--- | :--- | :--- | :--- |
| **Characters** | `Characters/` | `Character-Template.md` | Character dossiers, physical traits, Want vs Need, The Lie, wounds, and 3-act arcs. |
| **Locations** | `Locations/` | `Location-Template.md` | Cities, regions, landmarks, sensory regional palettes, and danger ratings. |
| **Factions** | `Factions/` | `Faction-Template.md` | Guilds, empires, religious cults, rebel factions, leaders, and power structures. |
| **Magic & Tech** | `Magic-Technology/` | `Magic-Tech-System-Template.md` | Hard/soft magic rules, Sanderson's 3 laws, power sources, limitations, costs, and taboos. |
| **Bestiary** | `Bestiary/` | `Creature-Flora-Fauna-Template.md` | Monsters, beasts, flora, fauna, habitat, ecology, harvestable reagents, and threat levels. |
| **Artifacts** | `Artifacts/` | `Artifact-Relic-Template.md` | Legendary weapons, grimoires, relics, focal tech, creators, bearers, and curses. |
| **Cosmology** | `Cosmology/` | `Deity-Cosmology-Template.md` | Pantheons, celestial spheres, astral planes, creation myths, and sacred rites. |
| **History** | `History/` | `Timeline-Event-Template.md` | Historical eras, cataclysms, wars, treaties, and catalytic dates. |
| **Languages** | `Languages/` | `Glossary-Conlang-Template.md` | Conlangs, phonetic rules, root words, idioms, proverbs, and naming conventions. |

### How to Use Metadata Menu Forms (No YAML Editing!)
Instead of manually writing YAML headers, Scriptorium includes pre-built **`fileClasses`** schemas in `Templates/fileClasses/`.
1. In Obsidian, open any note.
2. Click the **Metadata Menu** icon or press the note's action menu.
3. Select attributes from intuitive dropdown menus (e.g. select Status: `Alive / Deceased / Missing`, Threat: `Lethal`, Scale: `Continent / City`).

### Dynamic Dashboards with Dataview
The central dashboard in `Templates/World-Bible-Index.md` automatically updates. Whenever you create a note tagged `#world/character` or `#world/bestiary`, it instantly appears in your master index table without any manual indexing!

---

## 5. Drafting & Sprint Sessions

### Three-Act Manuscript Hierarchy
Your manuscript in `01-Manuscript/Book-01/` is structured for long-form narrative pacing:
- `01_Act_I/`: Setup, status quo, inciting incident, and Plot Point 1.
- `02_Act_II/`: Rising action, trials, midpoint escalation, and Dark Night of the Soul.
- `03_Act_III/`: Climax, final confrontation, and resolution.

### Drafting with Longform or novelWriter
- **Longform (Obsidian)**: Organize atomic Markdown scenes in your left sidebar, drag-and-drop to reorder chapters, and draft directly in your vault.
- **novelWriter**: Open `01-Manuscript` to use novelWriter's structured project tree, status badges (`Draft`, `Revision`, `Finished`), and POV annotations (`@pov: CharacterName`).

### Scene Breaks in Trade Typography
To insert a scene break within a chapter, use standard Markdown:
```markdown
The castle gates slammed shut behind them.

* * *

Morning brought no comfort to the besieged city.
```
When compiled with Scriptorium's Typst engine, `* * *` or `***` or `---` is automatically transformed into an elegant, publication-grade ornament (`✦ ✦ ✦`).

### Distraction-Free Sprints (FocusWriter)
Click **"⚡ Sprint Canvas"** in the Control Center to launch FocusWriter.
- Press **`F11`** to enter full-screen distraction-free mode.
- Set a daily word count target (e.g. 1,000 words) with live ambient typing sounds and custom themes.

---

## 6. Typesetting & Book Publishing (Typst & Pandoc)

Scriptorium includes an automated publishing pipeline that eliminates complex LaTeX scripts and expensive Mac-only tools like Vellum.

### How Compilation Works
1. In the Control Center, open **Tab 3: Publishing Studio**.
2. Select your book volume (`Book-01` or `All Books (Omnibus)`).
3. Select your paper size (`US Trade 6x9 in`, `Trade 5.5x8.5 in`, or `Pocket 5x8 in`).
4. Click **"🚀 Compile Book"**.

### What Typst Automatically Formats
- **Front Matter**: Formats Half-Title, Full Title, Copyright page (with ISBN and copyright notice), Dedication, and Epigraph without page numbers or headers.
- **Running Headers & Footers**: Verso (Left) pages display the Author Name; Recto (Right) pages display the Book Title.
- **Gutter Binding Margins**: Alternates inside margin (`0.85 in`) and outside margin (`0.70 in`) so text never disappears into the book's glued spine.
- **Clean Tag Stripping**: Automatically scrubs internal `@pov:` or `%` notes so they never leak into consumer PDFs or EPUBs.
- **Flush-Left First Paragraphs**: Automatically keeps opening paragraphs after chapter headings and scene breaks flush-left according to traditional fiction typesetting standards.

---

## 7. Data Safety, Version History & The 3-2-1 Rule

Scriptorium enforces strict data sovereignty. You will never lose a word of your writing.

### 1. Automated Background Saves (Obsidian Git)
Obsidian Git is pre-configured to automatically commit changes in your World Bible in the background **every 10 minutes** and whenever you save a file.

### 2. Version Milestone Snapshots (Git)
Whenever you reach a milestone (e.g. finishing a chapter or rewriting an act), click **"📷 Quick Snapshot"** in the top bar or use **Tab 4**. This creates an immutable restore point in your local Git history.

### 3. Standalone Archive Backups (The 3-2-1 Rule)
- **What it is**: A compressed `.tar.gz` archive containing your entire world, lore, maps, and manuscripts, accompanied by a cryptographic SHA-256 checksum (`.sha256`).
- **How to use**: Click **"📦 Create Standalone Backup Archive"** in Tab 4.
- **Recommendation**: Copy your backup archives from `05-Backups/` to an external USB drive or secondary hard drive once a week.

### 4. Verified Disaster Recovery
If you ever switch computers or want to rollback a project:
1. Open **Tab 4: Vault Safety**.
2. Click **"♻️ Restore World from Archive"**.
3. Select your `.tar.gz` archive file.
4. Scriptorium verifies the SHA-256 hash to ensure zero file corruption, stages the restoration safely, and registers your world.

---

## 8. Author's Quick Reference & Troubleshooting FAQ

### Markdown Formatting Cheat Sheet

| Style | What You Type | How It Renders |
| :--- | :--- | :--- |
| **Chapter Title** | `# Chapter 1: The Beginning` | Chapter Heading (Recto pagebreak in Typst) |
| **Section Header** | `## Act I: The Gathering` | Centered Sub-Heading |
| **Scene Break** | `* * *` or `***` | Ornamental Divider (`✦ ✦ ✦`) |
| **Italics** | `*whispered thoughts*` | *whispered thoughts* |
| **Bold** | `**heavy impact**` | **heavy impact** |
| **Wiki Link** | `[[Kaelen Vance]]` | Clickable connection to Character Note |
| **Internal Tag** | `@pov: Kaelen` | novelWriter metadata (scrubbed on export) |

### Troubleshooting & FAQ

#### Q: A tool in Tab 5 says "Missing" (e.g. Typst or Pandoc). What should I do?
**A**: Run the Scriptorium setup installer:
```bash
scriptorium setup
```
Or install the individual tool via your package manager (see `resources/software_catalog.md`).

#### Q: How do I share a draft with my human editor for track changes?
**A**: Open the chapter or compiled Markdown file in **LibreOffice Writer** (Tab 1 launcher), click **Edit -> Track Changes -> Record**, and save as `.docx` or `.odt`.

#### Q: Can I open Scriptorium without using the desktop app?
**A**: Yes! Scriptorium includes a full command-line interface:
- `scriptorium export <world> --book Book-01`
- `scriptorium snapshot <world> -m "Note"`
- `scriptorium backup <world>`
- `scriptorium doctor`

#### Q: Where are my exported books saved?
**A**: In your world folder under `04-Publishing/` (e.g. `~/Worlds/Eldoria/04-Publishing/Eldoria_Book-01.pdf`).

---

*Scriptorium — Built with passion for speculative worldbuilders and novelists.*
