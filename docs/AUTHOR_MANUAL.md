# Ars Arcanum Author's Field Manual
### The Complete Plain-Language Guide to Local-First Novel Writing & Speculative Worldbuilding

Welcome to **Ars Arcanum**! Whether you are writing your debut novel, crafting a sprawling multi-volume epic fantasy cosmos, or organizing deep speculative science fiction lore, Ars Arcanum gives you a professional, distraction-free environment that is 100% private, open, and permanently yours.

Zero programming or terminal experience is required for daily writing. Everything is accessible through the **Ars Arcanum Control Center** desktop app.

---

## 📑 Table of Contents
1. [The Ars Arcanum Philosophy & Architecture](#1-the-ars-arcanum-philosophy--architecture)
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

## 1. The Ars Arcanum Philosophy & Architecture

### Why Ars Arcanum Exists
Most modern writing software locks your words into proprietary database formats, monthly cloud subscriptions, or closed operating systems. If the company changes pricing or shuts down, your work is in jeopardy.

Ars Arcanum is built on **Four Unbreakable Invariants**:
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
└── <WorldName>/               → Pure World Lore Vault (Direct Obsidian Vault with Git repository)
    ├── world.yaml             → World Lore manifest
    ├── Characters/            → Character dossiers & psychological arcs
    ├── Locations/             → Atlas, sensory palettes, and regional maps
    ├── Factions/              → Guilds, empires, sects & member rosters
    ├── Magic-Technology/     → Hard/soft magic rules, limitations & costs
    ├── Bestiary/              → Creatures, apex predators, flora, and monster ecologies
    ├── Artifacts/             → Legendary relics, magical weapons, and focal items
    ├── Cosmology/             → Pantheons, deities, astral planes, and mythos
    ├── History/               → Historical eras, timelines, and catalytic events
    ├── Languages/             → Conlangs, phonetic rules, and world glossaries
    ├── Templates/             → Dropdown schema forms, writing logs, and index dashboard
    └── .obsidian/             → Pre-configured plugin suite (Storyline, Longform, Dataview, etc.)

~/Manuscripts/<ManuscriptName>/
├── manuscript.yaml            → Project manifest linking Universe and World Lore Vault
├── nwProject.nwx              → novelWriter project manifest
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

## 2. Quick Start: Your First 5 Minutes

### Step 1: Open Ars Arcanum Control Center
Double-click **"Ars Arcanum Control Center"** on your Desktop (or run `arcanum control-center` in a terminal).

### Step 2: Create or Explore a Project
- **Option A (Instant Exploration)**: Click **"✨ Generate Demo Cosmos"** in Tab 1. This creates the *"Cosmere / Scadrial"* and *"Mistborn-Era1"* projects, pre-loaded with characters, bestiaries, magic systems, and sample chapters.
- **Option B (Your Own Story)**:
  1. Click **"+ New Universe"** to name your cosmos (e.g. `Solaris-Verse`).
  2. Click **"+ New World"** to create your dedicated lore vault (e.g. `Solaris-Prime`).
  3. Click **"+ New Manuscript"** to create your book project (e.g. `Solaris-Rising`) linked to your world lore vault.

### Step 3: Start Writing!
- Click **"📖 Open World Bible"** to view and edit lore directly in Obsidian.
- Click **"✍️ Drafting Studio"** to write your scenes in novelWriter or Longform.
- Click **"⚡ Sprint Canvas"** to enter full-screen distraction-free mode in FocusWriter.

---

## 3. The Desktop Control Center Tour

The Ars Arcanum desktop application is organized into **5 intuitive tabs** with global project selectors across the top:

### Top Selector Bar
- **Universe Selector**: Switch between different narrative universes.
- **World Lore Vault Selector**: Choose which direct lore bible is active for lore exploration.
- **Manuscript Project Selector**: Choose which novel/book project is active for drafting, metrics, and exports.
- **Quick Snapshot**: 1-click Git checkpoint across your entire active universe, world, and manuscript.

### Tab 1: 🪐 Universes & Worlds
- **Direct Lore Vault Management**: Open your World Lore Vault directly in Obsidian with all pre-configured plugins enabled.
- **Cosmos Index Hub**: Open `Universe-Index.md` to manage overarching continuity across multiple planets/realms.
- **Creative Tool Launchers**: 1-click buttons to launch Obsidian, novelWriter, FocusWriter, LibreOffice, Calibre, or your file manager.

### Tab 2: ✍️ Manuscripts & Drafting
- **Live Word Count Dashboard**: Displays total manuscript word counts, scene counts, and volume progress.
- **Manuscript Tree Explorer**: Interactive tree view listing Volumes (`Book-01`, `Book-02`), Acts, Chapters, and Scenes.
- **Visual Scene Metadata Inspector**: A non-technical visual control panel for inspecting and modifying scene headers:
  - **POV Character**: Set `@pov: CharacterName`
  - **Characters Present**: Set `@char: CharA, CharB`
  - **Location**: Set `@location: LocationName` (standardized; replaces deprecated `@focus:`)
  - **Narrative Thread**: Set `@thread: Main-Plot` or `@thread: Subplot-Heist`
  - **Story Time**: Set `@time: 1899-03-14`
  - **Scene Status**: Dropdown selector (`Draft`, `Revision`, `Finished`)
  - **Safe Header Updater**: Click **"💾 Update Scene Tags"** to rewrite the metadata header safely in place while preserving the scene prose!
- **Add New Volume**: 1-Click button (`📚 Add Volume`) to scaffold subsequent manuscript books with 3-act structures and isolated Git repositories.

### Tab 3: 📚 Publishing & Exports
- **1-Click Typesetting & Export**: Turn your Markdown manuscript into a print-ready vector PDF, an EPUB ebook, or a standard industry submission document (`.docx`) in seconds.
- **Export Format Options**:
  - `Print Book (PDF + EPUB)`: Typesets ready-to-print paperback PDFs (via Typst) and distributor-ready ebooks (via Pandoc).
  - `Submission Manuscript (.docx)`: Formats standard manuscript format (12pt, double-spaced, clean chapter breaks) for literary agents, editors, and anthologies.
  - `Complete Package (PDF + EPUB + DOCX)`: Builds all publication and submission formats simultaneously.
- **Generate Concordance**: 1-Click button (`📖 Generate Concordance`) to automatically extract characters, factions, relics, bestiary creatures, and linguistics from your World Bible into publication-grade `01_Dramatis_Personae.md` and `02_Glossary_and_Concordance.md` back-matter.
- **Volume Selector**: Choose to compile an individual volume (`Book-01`, `Book-02`) or the entire series omnibus.
- **Trim Size Presets**:
  - `US Trade (6 × 9 in)`: Standard commercial fiction and fantasy trade paperback.
  - `Trade (5.5 × 8.5 in)`: Compact novel trim size.
  - `Pocket (5 × 8 in)`: Mass-market paperback size.
- **Instant Preview**: Click **"📄 Open PDF"**, **"📱 Open EPUB"**, or **"📝 Open DOCX"** immediately upon compilation.

### Tab 4: 🔒 Snapshots & Backups
- **Version Milestone Snapshot (Git)**: Type a short progress note (e.g. `Finished Chapter 4 battle`) and click **"📷 Save Snapshot"**.
- **Milestone History**: View recent Git commits across your world and manuscript repositories.
- **Standalone Archive Backup**: Click **"📦 Create Standalone Backup Archive"** to generate a compressed `.tar.gz` bundle with an immutable SHA-256 verification manifest in `Backups/` or onto an external USB drive.
- **Disaster Recovery Restore**: Click **"♻️ Restore World from Archive"** to safely unpack and verify any past backup archive.

### Tab 5: 🩺 Diagnostics & Doctor
- **System Toolchain Badges**: Live indicators confirming that Git, Pandoc, Typst, and Python 3 are installed and functional.
- **World & Manuscript Doctor**: Audits your Obsidian vault for broken wikilinks, dangling character/faction references, chronological timeline anomalies, and manuscript-to-lore name drift (`WLD-108`).
- **Verification Harness**: Run the automated 7-stage test suite to verify project integrity.

---

## 4. Worldbuilding in Obsidian (The 9 Core Lore Vaults)

Your World Lore Vault (`~/Universes/<Universe>/<World>`) comes pre-configured with the premier worldbuilding and writing plugins enabled out of the box: **Dataview**, **Metadata Menu**, **Calendarium**, **Storyteller Suite**, **Storyline**, **Novel Word Count**, and **Obsidian Git**.

### The Minimum Viable World Bible (Zero Overwhelm)
If you are just getting started, open **`00_START_HERE.md`** inside your World Bible. You do **not** need to populate all 9 categories at once.
- **Step 1**: Use **`Character-Quickstart-Template.md`** for a lightweight 5-field protagonist card.
- **Step 2**: Create 1 starting location with `Location-Template.md`.
- **Step 3**: Start drafting in your manuscript project (`~/Manuscripts/<Manuscript>`) right away! Expand into factions, magic systems, bestiaries, and cosmology organically as your plot requires.

### The 9 Lore Categories

| Category | Folder | Template | What Goes Here |
| :--- | :--- | :--- | :--- |
| **Characters** | `Characters/` | `Character-Template.md` / `Character-Quickstart-Template.md` | Character dossiers, physical traits, Want vs Need, The Lie, wounds, and 3-act arcs. |
| **Locations** | `Locations/` | `Location-Template.md` | Cities, regions, landmarks, sensory regional palettes, and danger ratings. |
| **Factions** | `Factions/` | `Faction-Template.md` | Guilds, empires, religious cults, rebel factions, leaders, and power structures. |
| **Magic & Tech** | `Magic-Technology/` | `Magic-Tech-System-Template.md` | Hard/soft magic rules, Sanderson's 3 laws, power sources, limitations, costs, and taboos. |
| **Bestiary** | `Bestiary/` | `Creature-Flora-Fauna-Template.md` | Monsters, beasts, flora, fauna, habitat, ecology, harvestable reagents, and threat levels. |
| **Artifacts** | `Artifacts/` | `Artifact-Relic-Template.md` | Legendary weapons, grimoires, relics, focal tech, creators, bearers, and curses. |
| **Cosmology** | `Cosmology/` | `Deity-Cosmology-Template.md` | Pantheons, celestial spheres, astral planes, creation myths, and sacred rites. |
| **History** | `History/` | `Timeline-Event-Template.md` | Historical eras, cataclysms, wars, treaties, and catalytic dates. |
| **Languages** | `Languages/` | `Glossary-Conlang-Template.md` | Conlangs, phonetic rules, root words, idioms, proverbs, and naming conventions. |

### How to Use Metadata Menu Forms (No YAML Editing!)
Instead of manually writing YAML headers, Ars Arcanum includes pre-built **`fileClasses`** schemas in `Templates/fileClasses/`.
1. In Obsidian, open any note.
2. Click the **Metadata Menu** icon or press the note's action menu.
3. Select attributes from intuitive dropdown menus (e.g. select Status: `Alive / Deceased / Missing`, Threat: `Lethal`, Scale: `Continent / City`).

### Dynamic Dashboards with Dataview
The central dashboard in `Templates/World-Bible-Index.md` automatically updates. Whenever you create a note tagged `#world/character` or `#world/bestiary`, it instantly appears in your master index table without any manual indexing!

---

## 5. Drafting & Sprint Sessions

### Three-Act Manuscript Hierarchy
Your manuscript in `~/Manuscripts/<Manuscript>/Book-01/` is structured for long-form narrative pacing:
- `01_Act_I/`: Setup, status quo, inciting incident, and Plot Point 1.
- `02_Act_II/`: Rising action, trials, midpoint escalation, and Dark Night of the Soul.
- `03_Act_III/`: Climax, final confrontation, and resolution.

### Drafting with Longform or novelWriter
- **Longform (Obsidian)**: Organize atomic Markdown scenes in your left sidebar, drag-and-drop to reorder chapters, and draft directly in your vault.
- **novelWriter**: Open your manuscript project (`~/Manuscripts/<Manuscript>`) to use novelWriter's structured project tree, status badges (`Draft`, `Revision`, `Finished`), and POV annotations (`@pov: CharacterName`).

### Multi-Volume Series Scaffolding (`add-book`)
When writing sequels, trilogies, or serials, you can scaffold subsequent volumes in your world with 1 click or a single command:
```bash
arcanum add-book My-Manuscript Book-02
```
This automatically scaffolds:
- `Book-02/01_Act_I`
- `Book-02/02_Act_II`
- `Book-02/03_Act_III`
- Starter chapters for each act
- A discrete, isolated Git repository for granular drafting commits in `Book-02`!

### Scene Breaks in Trade Typography
To insert a scene break within a chapter, use standard Markdown:
```markdown
The castle gates slammed shut behind them.

* * *

Morning brought no comfort to the besieged city.
```
### Subplot & Narrative Thread Pacing (`Subplot-Thread-Matrix.md`)
For complex speculative narratives with multiple intertwining plotlines, consult `Outlines/Subplot-Thread-Matrix.md` in your manuscript project.
- Annotate your scenes with `@thread: Main-Plot`, `@thread: Subplot-Romance`, or `@thread: Subplot-Heist`.
- Dynamic Dataview queries provide a live matrix showing which subplots advance in each act and ensure that minor threads never vanish mid-book.
- All `@thread:` tags are completely scrubbed during export.

### Distraction-Free Sprints (FocusWriter)
Click **"⚡ Sprint Canvas"** in the Control Center to launch FocusWriter.
- Press **`F11`** to enter full-screen distraction-free mode.
- Set a daily word count target (e.g. 1,000 words) with live ambient typing sounds and custom themes.

---

## 6. Typesetting & Book Publishing (Typst & Pandoc)

Ars Arcanum includes an automated publishing pipeline that eliminates complex LaTeX scripts and expensive Mac-only tools like Vellum.

### How Compilation Works
1. In the Control Center, open **Tab 3: Publishing Studio**.
2. Select your book volume (`Book-01`, `Book-02`, or `All Books (Omnibus)`).
3. Select your output format (`Print Book`, `Submission Manuscript (.docx)`, or `Complete Package`).
4. Select your paper trim size (for print PDFs).
5. Click **"🚀 Compile Book"**.

### Standard Manuscript Submission Format (.docx)
For authors pitching literary agents, submitting to short fiction anthologies, or working with editors in traditional publishing workflows:
- Ars Arcanum exports industry-standard Shunn-compliant `.docx` manuscripts via Pandoc.
- Automatically strips inline `@tag:` metadata and internal notes.
- Applies standard double-spacing, 1-inch margins, running headers, and clean chapter demarcations.
- Available via the Control Center dropdown or via CLI:
  ```bash
  arcanum export <manuscript> --format submission --book Book-01
  # or shortcut:
  arcanum export <manuscript> --docx -b Book-01
  ```

### Automated Back-Matter Concordance & Dramatis Personae
Click **"📖 Generate Concordance"** (or run `arcanum concordance <world>`). Ars Arcanum's concordance engine reads all registered dossiers across your World Bible (`Characters/`, `Languages/`, `Bestiary/`, `Artifacts/`, and `Factions/`) and automatically creates:
- `<Manuscript>/<Book>/04_Back_Matter/01_Dramatis_Personae.md`
- `<Manuscript>/<Book>/04_Back_Matter/02_Glossary_and_Concordance.md`

Because of Ars Arcanum's natural alphabetical collation order, `04_Back_Matter` files are seamlessly compiled at the end of your Typst print PDFs, Pandoc EPUBs, and submission DOCXs with zero manual copy-pasting.

### Automated Cover Image Detection
Place your book's cover art in `03-Art/cover.png` or `03-Art/cover.jpg`. When exporting to EPUB, Pandoc automatically detects and embeds your cover image (`--epub-cover-image`) into the ebook manifest.

### What Typst Automatically Formats
- **Front Matter**: Formats Half-Title, Full Title, Copyright page (with ISBN and copyright notice), Dedication, and Epigraph without page numbers or headers.
- **Running Headers & Footers**: Verso (Left) pages display the Author Name; Recto (Right) pages display the Book Title.
- **Gutter Binding Margins**: Alternates inside margin (`0.85 in`) and outside margin (`0.70 in`) so text never disappears into the book's glued spine.
- **Clean Tag Stripping**: Automatically scrubs internal `@pov:`, `@thread:`, or `%` notes so they never leak into consumer PDFs or EPUBs.
- **Flush-Left First Paragraphs**: Automatically keeps opening paragraphs after chapter headings and scene breaks flush-left according to traditional fiction typesetting standards.

---

## 7. Data Safety, Version History & The 3-2-1 Rule

Ars Arcanum enforces strict data sovereignty. You will never lose a word of your writing.

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
4. Ars Arcanum verifies the SHA-256 hash to ensure zero file corruption, stages the restoration safely, and registers your world.

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
| **POV Tag** | `@pov: Kaelen` | novelWriter metadata (scrubbed on export) |
| **Location Tag** | `@location: SunCitadel` | Standardized scene location |
| **Character Tag** | `@char: Vance, Scribe` | Characters present in scene |
| **Thread Tag** | `@thread: Main-Plot` | Subplot matrix tracking |
| **Time Tag** | `@time: 1899-03-14` | Story timeline chronological anchor |
| **Status Tag** | `@status: Draft` | Scene drafting workflow status |

### Troubleshooting & FAQ

#### Q: A tool in Tab 5 says "Missing" (e.g. Typst or Pandoc). What should I do?
**A**: Run the Ars Arcanum setup installer:
```bash
arcanum setup
```
Or install the individual tool via your package manager (see `docs/guides/SOFTWARE_CATALOG.md`).

#### Q: How do I share a draft with my human editor for track changes?
**A**: Open the chapter or compiled Markdown file in **LibreOffice Writer** (Tab 1 launcher), click **Edit -> Track Changes -> Record**, and save as `.docx` or `.odt`.

#### Q: Can I open Ars Arcanum without using the desktop app?
**A**: Yes! Ars Arcanum includes an intuitive command-line interface (`arcanum` or `ars-arcanum`):
- `arcanum write [target]` (or `arcanum open`) — launch your writing canvas
- `arcanum new <manuscript|world|universe|volume> <name>` — scaffold any project type
- `arcanum save [target] -m "Finished Act 1"` (or `arcanum snapshot`) — record a Git version
- `arcanum publish [manuscript] [--format book|submission|all]` (or `arcanum export`) — compile PDF, EPUB, DOCX
- `arcanum words [manuscript]` (or `arcanum count`, `arcanum report`) — view live word counts
- `arcanum concordance <world> --manuscript <ms>` — generate Dramatis Personae & Glossary
- `arcanum check` (or `arcanum doctor`) — run system & toolchain diagnostics
- `arcanum continuity -w <world> -m <ms>` — check narrative trait consistency
- `arcanum cache <scan|wordcounts|clear> [path]` — manage fast performance index
- `arcanum backup <target>` / `arcanum restore <archive>` — disaster-recovery backups

#### Q: Where are my exported books saved?
**A**: In your manuscript project folder under `Exports/` (e.g. `~/Manuscripts/Solaris-Rising/Exports/Solaris-Rising_Book-01.pdf`).

---

*Ars Arcanum — Built with passion for speculative worldbuilders and novelists.*
