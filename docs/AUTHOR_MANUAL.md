# Ars Arcanum Author's Field Manual
### The Complete Plain-Language Guide to Local-First Novel Writing & Speculative Worldbuilding

Welcome to **Ars Arcanum**! Whether you are writing your debut novel, crafting a sprawling multi-volume epic fantasy cosmos, or organizing deep speculative science fiction lore, Ars Arcanum gives you a professional, distraction-free environment that is 100% private, open, and permanently yours.

Zero programming or terminal experience is required for daily writing. Everything is accessible through the **Ars Arcanum Control Center** desktop app.

---

## 📑 Table of Contents
1. [The Ars Arcanum Philosophy & Architecture](#1-the-ars-arcanum-philosophy--architecture)
2. [Quick Start: Your First 5 Minutes](#2-quick-start-your-first-5-minutes)
3. [The Desktop Control Center Tour (6 Studios)](#3-the-desktop-control-center-tour)
   - [Studio 1: Cosmos & Worlds](#studio-1-cosmos--worlds)
   - [Studio 2: Manuscripts & Drafting](#studio-2-manuscripts--drafting)
   - [Studio 3: Speculative Fiction & Craft](#studio-3-speculative-fiction--craft)
   - [Studio 4: Publishing & Typesetting](#studio-4-publishing--typesetting)
   - [Studio 5: Vault Safety & Backups](#studio-5-vault-safety--backups)
   - [Studio 6: Diagnostics & Doctor](#studio-6-diagnostics--doctor)
4. [Worldbuilding in Obsidian (The 9 Core Lore Vaults)](#4-worldbuilding-in-obsidian-the-9-core-lore-vaults)
5. [Drafting & Sprint Sessions](#5-drafting--sprint-sessions)
6. [Typesetting & Book Publishing (Typst & Pandoc)](#6-typesetting--book-publishing-typst--pandoc)
7. [Data Safety, Version History & The 3-2-1 Rule](#7-data-safety-version-history--the-3-2-1-rule)
8. [Author's Quick Reference & Troubleshooting FAQ](#8-authors-quick-reference--troubleshooting-faq)
9. [Speculative Fiction Authorial Workflow Suites (Waves 1–12)](#9-speculative-fiction-authorial-workflow-suites)
   - [Wave 1: Astrophysics & Relativistic Spaceflight](#wave-1-astrophysics--relativistic-spaceflight)
   - [Wave 2: Hard Magic Systems & Arcane Constraint Matrix](#wave-2-hard-magic-systems--arcane-constraint-matrix)
   - [Wave 3: Dynastic Genealogies & Succession Lineage Graphs](#wave-3-dynastic-genealogies--succession-lineage-graphs)
   - [Wave 4: Conlang Phonotactics, Lexicography & Sound-Change Applier](#wave-4-conlang-phonotactics-lexicography--sound-change-applier)
   - [Wave 5: Narrative Pacing, POV Balance & Tension Arc Analytics](#wave-5-narrative-pacing-pov-balance--tension-arc-analytics)
   - [Wave 6: Overland/Naval Journey Modeler & Custom Planetary Calendars](#wave-6-overlandnaval-journey-modeler--custom-planetary-calendars)
   - [Wave 7: Geopolitical Faction Matrix & Campaign Logistics](#wave-7-geopolitical-faction-matrix--campaign-logistics)
   - [Wave 8: In-World Economy, Commodity PPP & Tech Era Anachronisms](#wave-8-in-world-economy-commodity-ppp--tech-era-anachronisms)
   - [Wave 9: Causal DAGs, Time Travel Loops & Multiverse Branching](#wave-9-causal-dags-time-travel-loops--multiverse-branching)
   - [Wave 10: Planetary Climate, Orographic Biomes & Trophic Food-Webs](#wave-10-planetary-climate-orographic-biomes--trophic-food-webs)
   - [Wave 11: Earth-Eponym Scanner, Idiom De-Immersion & 6D Sensory Palette](#wave-11-earth-eponym-scanner-idiom-de-immersion--6d-sensory-palette)
   - [Wave 12: Inscriptions, In-World Ciphers & Prophecy Resolution](#wave-12-inscriptions-in-world-ciphers--prophecy-resolution)
10. [Authorial Craft, Editorial Linters, Plotting & Publishing Tools](#10-authorial-craft-editorial-linters-plotting--publishing-tools)

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
├── manuscript.yaml            → Project manifest linking Universe, World Vault & active draft
├── nwProject.nwx              → novelWriter project manifest
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

## 2. Quick Start: Your First 5 Minutes

### Step 1: Open Ars Arcanum Control Center
Double-click **"Ars Arcanum Control Center"** on your Desktop (or run `arcanum control-center` in a terminal).

### Step 2: Create or Explore a Project
- **Option A (Instant Exploration)**: Click **"✨ Generate Demo Cosmos"** in Tab 1. This creates the *"Eldoria-Cosmos / Eldoria-World"* and *"Chronicles-of-Eldoria"* projects, pre-loaded with characters, bestiaries, magic systems, and sample chapters.
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
- **Word Processing & DOCX Synchronization Toolbar**:
  - **Open in Word Processor**: 1-click button to launch your preferred word processor (Microsoft Word, Google Docs via browser, or LibreOffice Writer) directly with the active consolidated draft (`Draft-01_Manuscript.docx`) or selected chapter.
  - **Sync DOCX ↔ Markdown**: 1-click bidirectional synchronization engine. Reconciles prose changes between `.docx` files and Markdown scenes while preserving all narrative metadata tags (`@pov:`, `@location:`, etc.).
  - **DOCX Formatting Settings**: Modal dialog to configure global Word styling presets (`Standard Submission / Shunn`, `Modern Manuscript`, `Classic Trade`, or `Custom` font, line spacing, margins, and paragraph indents).
- **Manuscript Draft Revisions & Redline Comparator**:
  - Fork new draft versions (`+ Fork New Draft`) to maintain independent revisions (`Draft-01`, `Draft-02`).
  - View visual redline changelogs in your browser or LibreOffice Writer to see added/deleted prose between drafts.
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

### Draft Management & Visual Redline Comparison (`arcanum draft` / `arcanum compare`)
Ars Arcanum includes a first-class draft management and visual manuscript revision comparator (similar to MS Word Track Changes / Document Compare, but built for plain Markdown).

#### 1. Maintaining Multiple Draft Versions
Books can maintain discrete draft versions (`Draft-01`, `Draft-02`, `Draft-03`) directly inside their volume directory (`Book-01/Draft-01/`, `Book-01/Draft-02/`).
- To fork your current prose into a new revision draft, click **"+ Fork New Draft"** in Tab 2 of the Control Center, or run:
  ```bash
  arcanum draft My-Novel Draft-02
  ```
- This atomically copies all scenes into `Book-01/Draft-02/`, updates the active draft pointer in `manuscript.yaml`, and tags a Git milestone commit.

#### 2. Visual Redline Document Comparison
To see what was cut from an older draft and what was added in a newer revision:
- Open the Control Center (Tab 2 -> **Manuscript Draft Revisions & Redline Comparator**), pick your Target Draft (e.g. `Draft-02`) and Prior Draft (e.g. `Draft-01`), and click **"📊 View Redline Changelog"**.
- Or via CLI:
  ```bash
  arcanum compare My-Novel Draft-02 Draft-01 --browser
  ```
- **Accessible Design**: Additions appear in soft sage/mint highlights (`<ins>`) with underlines, while cut text appears in soft blush/rose highlights (`<del>`) with strikethrough—avoiding harsh, unreadable red fonts.
- **Interactive Features**:
  - Chapter sidebar with jump links and word delta pills (`+250 / -80 words`).
  - Dark mode and Light mode toggle switches.
  - "Highlight Changes Only" changelog mode (dims unchanged paragraphs).
  - Search bar to live-filter modified text.
  - One-click Print/PDF export.
- **LibreOffice Bridge**: Click **"📝 LibreOffice Writer"** (or `--libreoffice`) to open native side-by-side Track Changes comparison in LibreOffice Writer!

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

### Standard Word Processor Drafting & DOCX Dual-Synchronization

For authors who prefer drafting or revising in dedicated word processors—such as **Microsoft Word (365 / latest)**, **Google Docs**, or **LibreOffice Writer**—Ars Arcanum features a native, offline dual-synchronized OpenXML engine (`scripts/lib/docx_sync.py`).

#### 1. The Dual-Synchronized Hybrid Model
Ars Arcanum automatically maintains standard `.docx` documents alongside plain Markdown files:
- **Consolidated Draft Document**: `Book-01/Draft-01/Draft-01_Manuscript.docx` compiles all acts and chapters into a single continuous manuscript file for cohesive reading and global revisions.
- **Individual Chapter Documents**: Each chapter (e.g. `Book-01/Draft-01/01_Act_I/01_Chapter.docx`) is generated as a standalone `.docx` file for focused, scene-level editing.
- **Zero Dependencies**: 100% pure Python standard library OpenXML generator—requires zero external packages, no internet connection, and runs instantaneously.

#### 2. Distraction-Free Reading & Tag Preservation
- **Clean Body Prose**: Internal metadata tags (`@pov:`, `@location:`, `@char:`, `@thread:`, `@time:`, `@status:`) and HTML comments are automatically scrubbed from `.docx` body text, presenting a clean reading environment in MS Word and Google Docs.
- **Metadata Tag Preservation on Sync**: When you edit prose in MS Word and sync back to Markdown, Ars Arcanum automatically matches each chapter, extracts the modified body paragraphs, and reattaches the original metadata header tags safely!

#### 3. Opening & Editing in Word Processors
- **From the Control Center**:
  1. Open **Tab 2: Manuscripts & Drafting**.
  2. Click **"📝 Open in Word Processor"** to immediately open the consolidated manuscript in Microsoft Word (Windows/macOS), LibreOffice Writer (Linux), or your system default editor.
- **From the Command Line**:
  ```bash
  # Launch active manuscript draft in Word / LibreOffice
  arcanum word My-Novel
  
  # Or explicitly:
  arcanum docx open My-Novel
  ```

#### 4. Bidirectional Synchronization (`arcanum docx sync`)
Whenever you make edits in either format:
- **From GUI**: Click **"🔄 Sync DOCX ↔ Markdown"** in Tab 2.
- **From CLI**: Run `arcanum docx sync My-Novel` (or `arcanum docx-sync My-Novel`).
- **How It Works**: The sync engine compares modification timestamps (`mtime`):
  - If `.md` is newer than `.docx` → Rebuilds `.docx` with latest Markdown prose.
  - If `.docx` is newer than `.md` → Extracts updated prose from `.docx`, restores scene metadata tags, and updates `.md`.

#### 5. Configurable Formatting Presets
Customize how Word documents look using built-in typography presets:

| Preset | Font Family | Size | Spacing | Margins | First-Line Indent | Scene Break | Best For |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Standard Submission** | Times New Roman | 12 pt | 2.0x (Double) | 1.0 inch | 0.50 inch | `#` | Shunn industry standard for literary agents and publisher submissions |
| **Modern Manuscript** | Georgia | 11.5 pt | 1.35x | 1.0 inch | 0.35 inch | `* * *` | High-readability modern drafting and comfortable desktop reading |
| **Classic Trade** | EB Garamond | 12 pt | 1.50x | 1.0 inch | 0.40 inch | `✦ ✦ ✦` | Elegant book typography feel in word processors |
| **Custom** | *User choice* | *User* | *User* | *User* | *User* | *User* | Configured via GUI dialog or CLI |

- **To Change Preset in GUI**: Click **"⚙️ DOCX Formatting Settings"** in Tab 2 to open the modal configuration dialog.
- **To Change Preset in CLI**:
  ```bash
  # List available presets
  arcanum config docx-presets

  # Set active preset
  arcanum config docx-preset standard-submission

  # Rebuild DOCX files with new preset styling
  arcanum docx build My-Novel
  ```

#### 6. Collaborative Workflows with Google Docs & Editors
- **Working with Google Docs**: Upload `Draft-01_Manuscript.docx` to Google Drive, open with Google Docs, write or collaborate with beta readers, then download as `.docx` back into your manuscript folder and click **"Sync DOCX ↔ Markdown"**.
- **Importing Standalone Word Files**: If an editor sends back an edited chapter `.docx`:
  ```bash
  arcanum docx import /path/to/Edited_Chapter.docx My-Novel --target-chapter 01_Chapter.md
  ```

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

### 3. Dual-Target Standalone Archive Backups (The 3-2-1 Rule)
- **What it is**: A compressed `.tar.gz` archive containing your entire project (world lore, manuscripts, outlines, and Git history), accompanied by a cryptographic SHA-256 checksum (`.sha256`) and JSON metadata.
- **Dual-Target Secure Replication**:
  - Configure a persistent secondary destination (external USB drive, encrypted vault, secondary disk):
    - In Tab 4: Click **"📁 Choose External / USB Backup Directory..."**
    - Or via CLI: `arcanum backup-dest set /media/usb/backups`
  - When you click **"📦 Create Standalone Backup Archive"** (or run `arcanum backup <project>`), Ars Arcanum creates the verified archive locally in `05-Backups/` and automatically replicates it to your configured secure destination, verifying the SHA-256 checksum in both locations!

### 4. Verified Disaster Recovery
If you ever switch computers or want to rollback a project:
1. Open **Tab 4: Vault Safety**.
2. Click **"♻️ Restore World from Archive"**.
3. Select your `.tar.gz` archive file from your local disk or external USB drive.
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

#### Q: Can I write my entire novel in Microsoft Word or Google Docs?
**A**: Yes! Ars Arcanum automatically maintains `.docx` files for every draft and chapter (`Draft-01_Manuscript.docx`, `01_Chapter.docx`). You can open and edit them in Microsoft Word (Desktop/365), Google Docs, or LibreOffice Writer. Whenever you want to pull your changes back into Markdown and Git, simply click **"🔄 Sync DOCX ↔ Markdown"** in Tab 2 or run `arcanum docx sync <manuscript>`.

#### Q: How do I share a draft with my human editor for track changes?
**A**: Send them `Draft-01_Manuscript.docx` or an individual `Chapter.docx`. When they return the revised file with edits, save it in your manuscript folder and run `arcanum docx sync` (or use `arcanum docx import <path> <manuscript>`). You can then use **"📊 View Redline Changelog"** or `arcanum compare` to inspect all additions and deletions visually!

#### Q: Can I open Ars Arcanum without using the desktop app?
**A**: Yes! Ars Arcanum includes an intuitive command-line interface (`arcanum` or `ars-arcanum`):
- `arcanum write [target]` (or `arcanum open`) — launch your writing canvas
- `arcanum word [manuscript]` — launch active draft in Word / LibreOffice
- `arcanum docx <build|sync|import|open> [ms]` — manage Word documents & sync
- `arcanum new <manuscript|world|universe|volume> <name>` — scaffold any project type
- `arcanum draft <manuscript> [draft_name]` — fork a discrete revision draft
- `arcanum compare <ms> <draft_new> <draft_old>` — visual redline draft comparator
- `arcanum save [target] -m "Finished Act 1"` (or `arcanum snapshot`) — record a Git version
- `arcanum publish [manuscript] [--format book|submission|all]` (or `arcanum export`) — compile PDF, EPUB, DOCX
- `arcanum words [manuscript]` (or `arcanum count`, `arcanum report`, `arcanum words --pov`) — view live word counts & POV balance
- `arcanum concordance <world> --manuscript <ms>` — generate Dramatis Personae & Glossary
- `arcanum check` (or `arcanum doctor`) — run system & toolchain diagnostics
- `arcanum continuity -w <world> -m <ms>` — check narrative trait consistency
- `arcanum cache <scan|wordcounts|clear> [path]` — manage fast performance index
- `arcanum backup <target>` / `arcanum restore <archive>` — disaster-recovery backups
- `arcanum config <backup-dest|docx-preset|docx-presets|docx-config>` — manage settings
- `arcanum calc <transit|time-dilation|orbit|comms|habitability>` — relativistic spaceflight, orbital mechanics & astrophysics
- `arcanum magic-check -w <world> -m <ms>` / `arcanum magic-report` — validate hard magic system rules & constraints (MAG-101..104)
- `arcanum genealogy -w <world> [-f mermaid|html|json]` / `arcanum lineage` — dynastic family trees, DAG succession & paradox detection
- `arcanum conlang <generate|mutate|lexicon>` — conlang phonotactics word generation, sound-law mutations & lexicon exporter
- `arcanum pace <manuscript>` / `arcanum tension` — narrative pacing metrics, dialogue ratios & tension arc visualization
- `arcanum journey -t <terrain> -d <km> -p <party> -m <mode>` — overland and naval expedition speed, rations & day-by-day itineraries
- `arcanum calendar -w <world> [-d <day>]` — custom planetary calendars, multi-moon synodic phases, eclipses & syzygies

#### Q: Where are my exported books saved?
**A**: In your manuscript project folder under `Exports/` (e.g. `~/Manuscripts/Solaris-Rising/Exports/Solaris-Rising_Book-01.pdf`).

---

## 9. Speculative Fiction Authorial Workflow Suites

Ars Arcanum includes six built-in speculative authoring engines. Designed specifically for hard science fiction, epic fantasy, and worldbuilding novelists, these engines operate 100% locally with zero external dependencies and provide rigorous physical, linguistic, dynastic, and magical consistency checking.

---

### Wave 1: Astrophysics & Relativistic Spaceflight

The astrophysics suite (`scripts/lib/astrophysics.py` / `arcanum calc`) calculates real-world relativistic kinematics, orbital transfers, radio communication delays, and stellar habitability.

#### Key Features:
- **Brachistochrone Relativistic Trajectories**: Computes continuous acceleration/deceleration burns (e.g. 1g torch-ships).
  - Ship proper time ($\tau$) vs coordinate observer time ($t$).
  - Peak velocity ($v_{\max}/c$) and relativistic Lorentz factor ($\gamma$).
  - Relativistic Tsiolkovsky fuel mass ratio ($m_0/m_f = \exp(a \tau / v_e)$).
- **Hohmann Orbital Transfers**: Calculates $\Delta v_1$, $\Delta v_2$, total $\Delta v$, and transfer time between circular orbits for Earth, Mars, Moon, Jupiter, Saturn, or custom planetary bodies.
- **Interplanetary Communication Latencies**: Calculates light-speed one-way and round-trip communication delays at minimum, average, and maximum planetary conjunction distances.
- **Stellar Habitability & Planetary Surface Gravity**: Computes habitable zone inner/outer boundaries (AU) based on stellar luminosity and surface gravity ($g$) based on planet radius and mass.
- **Interactive HTML & SVG Reports**: Generates standalone visual flight profiles with embedded SVG charts.

#### Example Usage:
```bash
# Calculate 1g relativistic flight to Alpha Centauri (4.24 light-years) with an antimatter drive (Isp = 100,000 s)
arcanum calc transit --dist 4.24 --dist-unit ly --accel 1.0 --isp 100000

# Compute time dilation for a crew cruising at 0.95c for 5 ship years
arcanum calc time-dilation --v-frac 0.95 --time 5.0 --time-unit years

# Compute Hohmann transfer from LEO (300 km) to GEO (35,786 km)
arcanum calc orbit --body Earth --r1 300 --r2 35786

# Calculate communication delays to Mars
arcanum calc comms --body Mars

# Export comprehensive HTML flight dossier
arcanum calc transit --dist 5.9 --dist-unit au --accel 0.5 -o flight_dossier.html
```

---

### Wave 2: Hard Magic Systems & Arcane Constraint Matrix

The arcane constraint engine (`scripts/lib/magic_system.py` / `arcanum magic-check`, `arcanum magic-report`) applies Brandon Sanderson-style hard magic validation against your manuscript scenes and world lore dossiers.

#### Tag Conventions:
Include these tags in your scene headers or prose comments:
- `@magic: <SystemName>` — Declares active magic system for the scene.
- `@cast: <Character>: <Ability/Spell>` — Records a specific casting act.
- `@reagent: <Material1>, <Material2>` — Materials or catalysts consumed/present.
- `@fatigue: <Level>` — Current character arcane exhaustion.

#### Diagnostic Rules:
- **`MAG-101`**: Character Affinity Tier Violation (casting an ability higher than the character's licensed or biological tier in their dossier).
- **`MAG-102`**: Missing Catalyst / Reagent (casting a spell requiring material reagents not present or consumed in the scene).
- **`MAG-103`**: Hard Limitation Violation (attempting an action explicitly barred by world lore laws, e.g. affecting aluminum, raising true dead).
- **`MAG-104`**: Fatigue & Exhaustion Overflow (accumulating fatigue beyond threshold without scene rest).

#### Example Usage:
```bash
# Validate magic consistency across a manuscript
arcanum magic-check -w Scadrial -m Mistborn-Era1

# Generate an interactive HTML audit report
arcanum magic-report -w Scadrial -m Mistborn-Era1 -o magic_audit.html
```

---

### Wave 3: Dynastic Genealogies & Succession Lineage Graphs

The genealogy engine (`scripts/lib/genealogy.py` / `arcanum genealogy`, `arcanum lineage`) parses character dossiers to build family tree Directed Acyclic Graphs (DAGs), evaluate succession inheritance laws, and detect chronological/biological anomalies.

#### Dossier Frontmatter Conventions:
```yaml
---
name: Lord Valen Aethelgard
house: House Aethelgard
father: High Lord Justinian Aethelgard
mother: Lady Eleonora Aethelgard
born: 1002 4E
died: 1025 4E
gender: male
---
```

#### Diagnostic Rules & Features:
- **`GEN-101`**: Biological & Chronological Paradoxes:
  - Parent died before child birth (or child conceived > 9 months post-mortem).
  - Parent under minimum childbearing age (< 12 years old) at child birth.
  - Generational loop / cycle in DAG (e.g. A is ancestor of B and B is ancestor of A).
- **`GEN-102`**: Succession Claim Conflicts:
  - Disputed primogeniture or agnatic claims among rival heirs.
- **Export Formats**:
  - `mermaid`: Direct Mermaid.js flowchart markdown for Obsidian or GitHub rendering.
  - `html`: Standalone interactive visualization with pan/zoom and family branch styling.
  - `json`: Structured lineage database for custom tooling.

#### Example Usage:
```bash
# Output Mermaid diagram of royal lineage
arcanum genealogy -w Eldoria -f mermaid

# Export interactive HTML dynasty graph
arcanum genealogy -w Eldoria -f html -o royal_houses.html

# Compute inheritance succession order for a throne
arcanum lineage -w Eldoria --ruler "High Lord Justinian Aethelgard"
```

---

### Wave 4: Conlang Phonotactics, Lexicography & Sound-Change Applier

The conlang engine (`scripts/lib/conlang.py` / `arcanum conlang`) provides complete linguistic tooling for fantasy and sci-fi authors, from generating phonotactically consistent names to simulating centuries of historical sound change.

#### World Lore Language Profile:
Define your language in `Languages/<Language-Name>.md`:
```yaml
---
name: Archaic Valen
consonants: [p, t, k, b, d, g, m, n, s, r, l]
vowels: [a, e, i, o, u]
syllable_structures: ["(C)V", "(C)V(C)", "CV(C)"]
cluster_blacklist: ["pt", "kp", "bm", "sr", "ln"]
sound_laws:
  - "p > f / V_V"
  - "k > ch / _[e,i]"
  - "s > h / #_"
  - "e > 0 / _#"
---
```

#### Key Capabilities:
- **Phonotactic Word & Name Generator**: Synthesizes authentic vocabulary conforming strictly to your syllable templates and phoneme inventories while automatically discarding blacklisted consonant clusters.
- **Historical Sound-Law Applier**: Applies ordered regular sound shifts across millennia using standard linguistic notation (`target > replacement / environment`).
- **Lexicon Manager & Exporter**: Extracts conlang dictionaries and glossaries to Markdown tables, CSV, or JSON.

#### Example Usage:
```bash
# Generate 15 phonotactically valid character or place names
arcanum conlang generate -w Scadrial --lang "Archaic Valen" -n 15

# Apply historical sound laws to derive modern daughter language words
arcanum conlang mutate -w Scadrial --lang "Archaic Valen" --words "patre,kento,sol,bare"

# Export complete lexicon dictionary
arcanum conlang lexicon -w Scadrial --lang "Archaic Valen" -f markdown
```

---

### Wave 5: Narrative Pacing, POV Balance & Tension Arc Analytics

The pacing and tension engine (`scripts/lib/pacing.py` / `arcanum pace`, `arcanum tension`, `arcanum words --pov`) analyzes draft prose structure to ensure compelling narrative momentum and balanced character focus.

#### Key Metrics:
- **Prose Mode Distribution**: Accurately classifies sentences into Dialogue, Action, and Exposition using punctuation density and syntactic cues.
- **Rhythm & Sentence Length Variance**: Measures sentence length distribution, standard deviation, and identifies monotonous paragraph pacing.
- **POV Screen-Time Balance & Starvation Alerts**: Quantifies word count and chapter allocation per POV character; triggers starvation warnings if a key POV character goes unmentioned for > 3 consecutive chapters.
- **Tension Arc Modeling (0–100)**: Evaluates scene stakes using conflict vocabulary, action pacing, and dialogue urgency.
- **Embedded SVG Visualizer**: Generates self-contained HTML reports featuring SVG tension and pacing curves across the entire novel.

#### Example Usage:
```bash
# Analyze scene pacing and dialogue/action ratios across manuscript
arcanum pace Solaris-Rising

# Generate interactive tension arc graph
arcanum tension Solaris-Rising -o tension_arc.html

# View POV character word count distribution
arcanum words Solaris-Rising --pov
```

---

### Wave 6: Overland/Naval Journey Modeler & Custom Planetary Calendars

The expedition and calendar suite (`scripts/lib/journey.py`, `scripts/lib/calendar.py` / `arcanum journey`, `arcanum calendar`) handles realistic travel logistics and non-Earth temporal tracking.

#### Overland & Naval Journey Modeler:
- **14 Terrain Types**: Paved Road ($1.0$), Dirt Trail ($0.85$), Open Grassland ($0.75$), Dense Forest ($0.45$), Swamp/Marsh ($0.25$), Desert Dunes ($0.35$), Mountain Pass ($0.30$), River Downstream ($1.4$), Ocean Fair ($1.2$), Ocean Storm ($0.3$), etc.
- **8 Travel Modes**: Casual Walk, March, Forced March, Mounted Trot, Draft Wagon, Sled, Riverboat, Sailing Ship.
- **Supply Tracking**: Accurately computes party and pack animal ration (kg) and water (L) consumption, providing day-by-day itineraries and critical warning flags before starvation.

#### Custom Planetary Calendars & Multi-Moon Tracking:
- **Planetary Periods**: Custom year lengths, non-standard month lengths, leap rules, and customizable weekday names.
- **Multi-Moon Orbit Calculations**: Tracks multiple moons with independent synodic orbital periods and initial phase offsets.
- **Celestial Alignments**: Automatically detects Syzygy (grand conjunction when multiple moons align with the sun) and solar/lunar eclipses.
- **Visual ANSI & HTML Outputs**: Displays monthly calendar matrices in terminal and exports interactive astronomical charts.

#### Example Usage:
```bash
# Model a 350 km expedition through dense forest with 4 travelers and 2 pack horses
arcanum journey -d 350 -t "dense_forest" -m "foot_march" -p 4 --pack-animals 2

# Inspect planetary calendar and moon phases on day 145 of the year
arcanum calendar -w Scadrial -d 145

# Export interactive astronomical and calendar report
arcanum calendar -w Scadrial --html -o planetary_calendar.html
```

---

### Wave 7: Geopolitical Faction Matrix & Campaign Logistics

The geopolitical and military campaign engine (`scripts/lib/factions.py` / `arcanum faction`, `arcanum calc battle`, `arcanum calc logistics`) evaluates diplomatic relationship consistency across in-world factions and simulates realistic Lanchester combat attrition and march logistics.

#### World Lore Faction Profile:
Define your faction in `Factions/<Faction-Name>.md`:
```yaml
---
name: "Solar Empire"
type: faction
sphere_of_influence: "Inner Rim"
military_strength: 50000
allies: ["[[Lunar Dominion]]"]
rivals: ["[[Void Syndicate]]"]
vassals: []
treaties:
  - "Solar-Lunar Mutual Defense Pact"
---
```

#### Key Capabilities & Diagnostics:
- **Diplomatic Paradox Detection**:
  - `FAC-101`: Reciprocal Ally Contradiction (A considers B an ally, but B considers A a rival).
  - `FAC-102`: Asymmetric Alliance / Vassalage (A lists B as an ally, but B does not reciprocate).
  - `FAC-103`: Self-Relation (Faction listed as its own ally or rival).
  - `FAC-104`: Missing / Broken Faction Reference (Target wikilink note does not exist).
- **Lanchester Power-Law Combat Calculator**:
  - Simulates Lanchester Square Law (ranged/aimed fire) and Linear Law (unaimed/melee combat).
  - Computes force attrition, defender fortification multipliers ($1.0$ to $5.0\times$), combat effectiveness ratios, and round-by-round casualty curves.
- **Military Supply & Wagon Radius Modeler**:
  - Calculates daily grain/water consumption for infantry, cavalry, and camp followers.
  - Models wagon payload limits ($1{,}000\text{ kg}$), draft horse feed consumption, and the classical campaign supply radius before food exhaustion.
- **Visual Visualizers**: Exports Obsidian Mermaid chord graphs and standalone interactive HTML network diagrams.

#### Example Usage:
```bash
# Run geopolitical relationship audit across all world factions
arcanum faction Solaris-Prime

# Calculate Lanchester battle outcome (10,000 attackers vs 5,000 defenders behind 1.5x walls)
arcanum calc battle -a 10000 -d 5000 --fort 1.5 --law square

# Compute supply train and wagon requirements for 12,000 troops marching 250 km
arcanum calc logistics --infantry 10000 --cavalry 2000 --distance 250
```

---

### Wave 8: In-World Economy, Commodity PPP & Tech Era Anachronisms

The economic and anachronism suite (`scripts/lib/economy.py` / `arcanum economy`, `arcanum audit tech`, `arcanum calc trade`) models currency exchange rates, purchasing power parity (PPP), manuscript pricing consistency, and historical technological era constraints.

#### World Lore Economy Profile:
Define your currency in `Economies/<Economy-Name>.md`:
```yaml
---
name: "Imperial Standard"
base_currency: "Crown"
tech_era: "medieval"
exchange_rate_to_standard: 1.0
denominations:
  - "1 Crown = 10 Shillings"
  - "1 Shilling = 12 Pence"
commodity_basket:
  - "loaf_of_bread: 2"
  - "pint_of_ale: 1"
  - "horse: 500"
  - "sword: 150"
---
```

#### Key Capabilities & Diagnostics:
- **Commodity PPP & Exchange Rate Matrix**: Normalizes market purchasing power across distinct regional currencies using a standardized commodity basket.
- **Manuscript Price Anomaly Audit**:
  - `ECO-101`: Extreme Price Outlier (Manuscript price deviates $> 5.0\times$ from in-world lore baseline).
  - `ECO-102`: Unknown Currency Mentioned (Prose mentions a currency denomination not defined in world lore).
- **Technological Era Anachronism Scanner**:
  - `ECO-201`: Out-of-Era Technological Leak (Flags items like "telescope", "printing press", "gunpowder", "steam engine", or "radar" in eras where they do not belong: `stone_age`, `bronze_age`, `iron_age`, `classical`, `medieval`, `renaissance`, `steampunk`, `modern`, `cyberpunk`, `space_age`).
- **Trade Route Freight Calculator**: Models transport costs, transit distances, cargo payloads, and regional tariffs to determine profitable trade margins.

#### Example Usage:
```bash
# Display Purchasing Power Parity matrix across all world economies
arcanum economy Solaris-Prime

# Audit draft manuscript for out-of-era technological anachronisms (e.g. medieval baseline)
arcanum audit tech Solaris-Rising --era medieval

# Calculate trade route profitability (buy @ 10, sell @ 25, 100 tons over 500 km)
arcanum calc trade --buy 10 --sell 25 --cargo 100 --distance 500
```

---

### Wave 9: Causal DAGs, Time Travel Loops & Multiverse Branching

The causality engine (`scripts/lib/causality.py` / `arcanum causality`, `arcanum causality branch`) tracks causal timelines, detects time-travel paradoxes, enforces Novikov self-consistency, and organizes multiverse timeline divergences.

#### Scene & History Causal Annotations:
Annotate scene Markdown with causal metadata:
```markdown
# Chapter 12: The Grand Paradox
@event: assassination-attempt
@timeline: timeline-alpha
@causal-origin: prime-timeline-split
@causes: [war-outbreak, treaty-collapse]
```

#### Diagnostic Rules:
- **`CAU-101`**: Grandfather Paradox / Destructive Causal Cycle (An effect causally precedes or negates its own cause).
- **`CAU-102`**: Bootstrap / Ontological Paradox (Information or an object exists in a closed causal loop with no uncaused origin).
- **`CAU-103`**: Novikov Self-Consistency Violation (Contradictory state changes within a closed timelike curve).
- **`CAU-104`**: Orphan Divergence (Timeline branches from an unknown coordinate).
- **Visual DAGs**: Generates Obsidian Mermaid Directed Acyclic Graphs and standalone HTML interactive timeline charts.

#### Example Usage:
```bash
# Check manuscript and history for causal paradoxes and circular loops
arcanum causality Solaris-Prime Solaris-Rising

# Scaffold a new divergent multiverse timeline branch
arcanum causality branch "timeline-beta" --from-timeline "prime" --at-coord "Year 1042"
```

---

### Wave 10: Planetary Climate, Orographic Biomes & Trophic Food-Webs

The planetary ecology and climate suite (`scripts/lib/climate.py`, `scripts/lib/ecology.py` / `arcanum calc climate`, `arcanum ecology`) simulates planetary insolation, atmospheric circulation cells, orographic rain shadows, and trophic energy pyramids.

#### Planetary Climate & Orographic Simulator:
- **Stellar Insolation & Equilibrium Temperature**: Calculates stellar flux ($W/m^2$), Stefan-Boltzmann equilibrium temperature, greenhouse warming offsets, and liquid-water habitable zone bounds.
- **Atmospheric Circulation**: Derives Coriolis deflection and Hadley/Ferrel/Polar circulation cell counts based on planetary rotation velocity.
- **Orographic Rain Shadows**: Models adiabatic lapse rate temperature changes, moist air condensation, windward oceanic cloud forest precipitation, and leeward arid desert rain shadows.

#### Trophic Food-Web & Predator-Prey Balance:
- **Bestiary Trophic Roster**: Tracks trophic levels (1: Producers, 2: Herbivores, 3: Carnivores, 4: Apex Predators).
- **Lindeman 10% Energy Pyramid Rule**: Enforces the ecological rule where each successive trophic level sustains $\le 10\%$ of the lower tier's biomass.
- **Diagnostic Rules**:
  - `ECO-301`: Missing Primary Producers (No basal flora/plant biomass to support herbivores).
  - `ECO-302`: Unsustainable Predation (Prey species biomass is insufficient for predator population).
  - `ECO-303`: Trophic Inversion (Higher tier biomass exceeds lower tier energy bounds).
  - `ECO-304`: Isolated / Orphan Species (Creature has no recorded prey or predators).

#### Example Usage:
```bash
# Calculate planetary temperature and orographic rain shadow behind a 3000m ridge
arcanum calc climate --star-lum 1.0 --distance-au 1.0 --mountain-elevation 3000

# Validate ecosystem food web and trophic biomass pyramid in world lore
arcanum ecology Solaris-Prime
```

---

### Wave 11: Earth-Eponym Scanner, Idiom De-Immersion & 6D Sensory Palette

The immersion and sensory palette suite (`scripts/lib/idioms.py`, `scripts/lib/senses.py` / `arcanum audit idioms`, `arcanum audit senses`) identifies Earth-bound idioms that shatter reader immersion and balances sensory engagement across draft prose.

#### Earth Eponym & Immersion Scanner:
Scans draft manuscripts against a curated database of Earth eponyms, mythology, and geographic metaphors:
- **`IDM-101`**: Earth Eponyms (e.g. *cardigan*, *silhouette*, *boycott*, *guillotine*, *diesel*, *bowler hat*, *galvanize*, *sandwich*, *pasteurize*).
- **`IDM-102`**: Earth Mythological / Biblical Idioms (e.g. *Achilles' heel*, *Trojan horse*, *Pandora's box*, *Spartan*, *Draconian*, *Pyrrhic victory*, *babel*, *Good Samaritan*).
- **`IDM-103`**: Earth Clichés / Earth Fauna-Flora (e.g. *let the cat out of the bag*, *barking up the wrong tree*, *red herring*, *crocodile tears*).

#### 6-Dimensional Sensory Palette:
Analyzes sensory immersion across 6 distinct sensory modalities:
1. 👁️ **Visual** (Color, illumination, shape, silhouette)
2. 👂 **Auditory** (Volume, pitch, acoustics, timbre)
3. 👃 **Olfactory** (Aromas, scents, rot, ozone, incense)
4. 👅 **Gustatory** (Sweet, bitter, salty, metallic, sour)
5. ✋ **Tactile / Thermal** (Texture, temperature, pressure, dampness)
6. 🤸 **Kinesthetic / Vestibular** (Balance, vertigo, acceleration, tension)

- **`SNS-101`**: White Room Syndrome (Scenes lacking physical sensory grounding).
- **`SNS-102`**: Sensory Monotony (Over-reliance on pure visual description with zero auditory/tactile/olfactory anchoring).

#### Example Usage:
```bash
# Audit draft manuscript for immersion-breaking Earth eponyms
arcanum audit idioms Solaris-Rising

# Analyze 6D sensory distribution and detect White Room scenes
arcanum audit senses Solaris-Rising
```

---

### Wave 12: Inscriptions, In-World Ciphers & Prophecy Resolution

The in-world cipher and prophecy suite (`scripts/lib/cipher.py`, `scripts/lib/prophecy.py` / `arcanum cipher`, `arcanum prophecy`) encodes and translates ancient inscriptions into phonetic runes and tracks prophecy fulfillment across the narrative.

#### In-World Cipher & Phonetic Rune Engine:
- **Historical Cipher Algorithms**: Caesar shift, Atbash reflection, Vigenère polyalphabetic cipher, Rail Fence transposition, Columnar transposition.
- **Phonetic Runes**: Translates Latin script into authentic Elder Futhark (`ᚠᚢᚦᚨᚱᚲ`) and Anglo-Saxon Futhorc (`ᚠᚢᚦⲟᚱᚳ`).
- **Vector Inscription Cards**: Generates high-resolution standalone SVG artifact inscription cards for inclusion in World Bibles and reader-facing notes.

#### Prophecy Resolution Matrix:
Tracks ancient oracles and prophecies in `Cosmology/Prophecies/<Prophecy-Name>.md`:
```yaml
---
name: "Prophecy of the Eclipse"
type: prophecy
oracle: "Oracle of Delphi"
target_entity: "Prince Kael"
status: unfulfilled
clauses:
  - "When the twin suns align in the sixth month"
  - "The broken blade shall be reforged in dragonfire"
  - "The rightful heir shall reclaim the Solar Throne"
---
```
- **Manuscript Resolution Tracking**: Uses scene tags (`@prophecy: "Prophecy of the Eclipse", clause=1, status=fulfilled`) to verify that all prophecy clauses are satisfied before the novel concludes.
- **Diagnostic Rules**:
  - `PRP-101`: Unfulfilled Dangling Prophecy (Marked fulfilled in lore but never referenced in draft prose).
  - `PRP-102`: Premature / Contradictory Resolution (Resolved out of sequence or contradictory to established lore).
  - `PRP-103`: Missing Prophecy Reference (Scene references a prophecy that does not exist in lore).

#### Example Usage:
```bash
# Encode secret message using Vigenère cipher with an arcane keyword
arcanum cipher encode "THE VAULT OPENS AT MIDNIGHT" --type vigenere --key "SOLARIS"

# Translate text to phonetic Elder Futhark runes and export vector SVG card
arcanum cipher runes "Speak friend and enter" --alphabet futhark --svg rune_inscription.svg

# Audit prophecy resolution and fulfillment lifecycle across world and manuscript
arcanum prophecy Solaris-Prime Solaris-Rising
```

---

## 10. Authorial Craft, Editorial Linters, Plotting & Publishing Tools

Ars Arcanum includes a full suite of editorial linters, visual plotting matrix engines, publication pre-flight compliance checkers, interactive offline cartography, and auditory proofreaders.

---

### ✍️ Editorial Craft & Prose Stylistics

#### 1. Dialogue Attribution & Mechanics Linter (`scripts/lib/stylistics.py`)
Identifies common dialogue flaws before human editorial review:
- **`DIA-101` (Said-Bookisms)**: Overly dramatic dialogue tags (*"he ejaculated"*, *"she chortled"*, *"he barked"*).
- **`DIA-102` (Floating Dialogue)**: Consecutive dialogue lines without physical action beats or attributions.
- **`DIA-103` (Adverb Overload)**: Weak dialogue tags modified by adverbs (*"she said furiously"*, *"he whispered softly"*).

```bash
# Audit dialogue mechanics across a manuscript
arcanum audit dialogue Solaris-Rising
```

#### 2. Word Echo & Proximity Repetition Scanner (`scripts/lib/stylistics.py`)
Scans sliding paragraph windows (1–10 paragraphs) for duplicate non-trivial root words to prevent subconscious vocabulary repetition.

```bash
# Scan for words repeated within 3 paragraphs
arcanum audit echoes Solaris-Rising --window 3
```

#### 3. Character Voice Lexical Profiler (`scripts/lib/voice.py`)
Extracts dialogue by character tag (`@char:`) and computes distinct lexical metrics:
- Flesch-Kincaid & Coleman-Liau reading grade levels
- Average sentence length & syllable complexity
- Exclamation & question mark density
- Unique vocabulary frequency & voice homogenization alerts (`VOI-101` / `VOI-102`)

```bash
# Analyze character voice distinctiveness
arcanum audit voice Solaris-Rising
```

#### 4. Smart Typography & Punctuation Normalizer (`scripts/lib/typography_cleaner.py`)
Batch normalizes straight quotes (`"` $\to$ `“`/`”`), double hyphens (`--` $\to$ `—`), ellipses (`...` $\to$ `…`), and inserts locale-aware non-breaking spaces before punctuation.

```bash
# Preview typographic changes safely
arcanum polish typography Solaris-Rising --dry-run

# Apply smart typography across manuscript
arcanum polish typography Solaris-Rising
```

---

### 📐 Narrative Plotting, Structure & Scene Ergonomics

#### 1. Multi-Track Interactive Plot Grid (`scripts/lib/plot_matrix.py`)
Generates a 2D interactive matrix mapping `@thread:` subplots across chapters and acts, displaying scene status pills and exporting standalone interactive HTML reports.

```bash
# Generate standalone interactive plot matrix HTML
arcanum plot Solaris-Rising --html
```

#### 2. Story Paradigm Structure Enforcer (`scripts/lib/structure.py`)
Validates whether manuscript plot points align with classic storytelling milestones:
- **Supported Paradigms**: `save-the-cat` (15 beats), `heros-journey` (12 stages), `seven-point`, `story-circle`, `kishotenketsu`, `three-act-nine-block`.

```bash
# Check pacing alignment against Save the Cat beat sheet
arcanum audit structure Solaris-Rising --template save-the-cat
```

#### 3. Scene Mechanics & MRU Analyzer (`scripts/lib/scene_mechanics.py`)
Validates Dwight Swain / Jack Bickham Motivation-Reaction Units (Goal $\to$ Conflict $\to$ Disaster and Reaction $\to$ Dilemma $\to$ Decision).

```bash
# Audit scene turning points and character goal momentum
arcanum audit scenes Solaris-Rising
```

#### 4. Procedural Ambient Focus Audio (`scripts/lib/ambient.py`)
Generates distraction-free sound environments (Rain, Crackling Hearth, Library Hum, Cosmic Drone, Clockwork) with HTML5 WebAudio synthesis or offline WAV generation.

```bash
# Launch interactive browser ambient player
arcanum ambient rain --html

# Generate offline WAV audio file
arcanum ambient hearth --wav hearth.wav --duration 300
```

---

### 📚 Publishing Pre-Flight, Barcodes & Queries

#### 1. Publication Pre-Flight Compliance Linter (`scripts/lib/preflight.py`)
Validates print PDF and EPUB compliance: trim size dimensions (6x9, 5.5x8.5, 5x8), gutter margin ratios for target page count, unformatted straight quotes in prose, missing cover art, and metadata integrity.

```bash
# Run comprehensive pre-flight publication audit
arcanum preflight Solaris-Rising
```

#### 2. ISBN-13 & EAN-13 Vector Barcode Engine (`scripts/lib/barcode.py`)
Generates print-ready vector SVG and high-resolution PNG EAN-13 barcodes with dynamic ISBN prefixes (`978` or `979`) and optional 5-digit price extensions.

```bash
# Generate vector SVG barcode with price extension
arcanum barcode 978-1-234567-89-0 --price 19.99 --output cover-barcode.svg
```

#### 3. Front & Back Matter Modular Builder (`scripts/lib/frontmatter_builder.py`)
Generates standardized Copyright pages (Berne Convention, US Copyright, CC), Dedications, Epigraphs, Acknowledgments, Also-by-Author catalogs, and Reader Magnet CTAs.

```bash
# Generate publication front and back matter
arcanum frontmatter Solaris-Rising --inject
```

#### 4. Publishing Submission Query & Synopsis Scaffolder (`scripts/init_query.py`)
Scaffolds 1-Page Synopses, 3-Paragraph Query Letters, 250-Word Elevator Pitches, and Loglines from manuscript metadata.

```bash
# Generate agent query and pitch package
arcanum query Solaris-Rising
```

---

### 🗺️ Cartography, Codex & Series Continuity

#### 1. Offline Interactive Vector Cartography (`scripts/lib/cartography.py`)
Self-contained offline Leaflet/SVG interactive map viewer with lore pin layers (cities, borders, waypoints), distance measurements, and direct travel calculation piping into `journey.py`.

```bash
# Open interactive map or export standalone HTML
arcanum map Solaris-Prime --export world_map.html
```

#### 2. Static World Lore Wiki / Reader Codex Exporter (`scripts/lib/codex_export.py`)
Compiles the entire Obsidian World Lore Vault into a fast, searchable, responsive offline HTML static wiki with entity cards and spoiler toggles.

```bash
# Export static reader codex
arcanum codex Solaris-Prime --output ~/Public/Codex/
```

#### 3. Cross-Book Series Continuity Tracker (`scripts/lib/series_continuity.py`)
Validates character trait consistency, item lineages, and mortality invariants across multi-volume series (`Book-01`, `Book-02`, etc.).

```bash
# Audit cross-book continuity
arcanum continuity --series Solaris-Cosmos
```

#### 4. Dynamic Tactical Combat Simulator (`scripts/lib/tactical_sim.py`)
Combines Lanchester combat laws, terrain modifiers, and arcane fatigue to simulate multi-faction skirmishes.

```bash
# Simulate tactical battle
arcanum sim battle -a 10000 -d 5000 --fort 2
```

---

### 📦 Distribution Packaging & Audio Proofreading

#### 1. Multi-Platform Distribution Packager (`scripts/package_distribution.py`)
Packages ready-to-distribute bundles for Amazon KDP (with exact spine calculation), IngramSpark, Apple Books, Kobo, and direct sales.

```bash
# Package manuscript for all publishing platforms
arcanum package Solaris-Rising --target all
```

#### 2. Executive Author Portfolio Dashboard (`scripts/lib/portfolio.py`)
Scans all manuscripts and universes, providing wordcount velocity, stage breakdowns, and publication readiness scores.

```bash
# View portfolio executive summary
arcanum portfolio
```

#### 3. Offline Neural Audio Proofreader (`scripts/lib/tts_reader.py`)
Auditory proofreader using local Piper TTS / espeak-ng to read chapters aloud, catching cadence and rhythm hiccups by ear.

```bash
# Read chapter aloud at 1.25x speed
arcanum read Solaris-Rising 01_Chapter.md --speed 1.25
```

---

*Ars Arcanum — Built with passion for speculative worldbuilders and novelists.*

