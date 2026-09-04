# Master Task Graph: Scriptorium Resource Collection & Implementation

## Task Checklist

### 1. Project Filesystem & State Foundations
- [x] Create `project.md` (System charter and design rules)
- [x] Create `plan.md` (Operational roadmap and milestone phases)
- [x] Create `tasks.md` (Master task graph and definitions of done)
- [x] Create `knowledge.md` (Distilled tool ecosystem and technical invariants)
- [x] Create `decisions.md` (Architecture decision records)
- [x] Create `status.md` (Operational state and active momentum queues)

### 2. Software Resource Catalog & Documentation
- [x] Create `resources/software_catalog.md` (All core tools, download URLs, Flatpak/Apt commands, verification hashes)
- [x] Create `resources/optional_extras_guide.md` (Azgaar, Krita, Inkscape, Gramps, PolyGlot, Sigil, Kiwix)
- [x] Create `resources/typography_and_fonts_guide.md` (High-quality open fonts: Linux Libertine, EB Garamond, Alegreya, etc.)

### 3. Automation Scripts & Desktop Launchers
- [x] Create `scripts/setup_scriptorium.sh` (Unattended automated provisioning script for Linux Mint / Debian)
- [x] Create `scripts/init_world.sh` (Interactive/GUI generator for new world directories with full template scaffolding)
- [x] Create `scripts/export_book.sh` (Pandoc + Typst compilation engine for print PDF and Calibre EPUB)
- [x] Create `scripts/save_snapshot.sh` (One-click Git snapshot saver with desktop notification)
- [x] Create `launchers/export-book.desktop` (Desktop shortcut for book export)
- [x] Create `launchers/save-snapshot.desktop` (Desktop shortcut for Git snapshot)
- [x] Create `launchers/init-world.desktop` (Desktop shortcut for creating a new world)

### 4. Obsidian World Bible Starter Pack
- [x] Create `templates/world-bible/Characters/Character-Template.md` (Dataview YAML frontmatter, character arcs, relations)
- [x] Create `templates/world-bible/Locations/Location-Template.md` (Sensory details, geography, culture, maps)
- [x] Create `templates/world-bible/Factions/Faction-Template.md` (Hierarchy, goals, ideology, members)
- [x] Create `templates/world-bible/Magic-Technology/Magic-Tech-System-Template.md` (Hard/Soft rules, limitations, costs)
- [x] Create `templates/world-bible/History/Timeline-Event-Template.md` (Chronology, causes, consequences)
- [x] Create `templates/world-bible/Languages/Glossary-Conlang-Template.md` (Phonology, lexicon, phrases)
- [x] Create `templates/world-bible/Templates/Daily-Writing-Log.md` (Word counts, session notes, goals)
- [x] Create `templates/world-bible/Templates/Scene-Note-Template.md` (POV, goal, conflict, outcome)
- [x] Create `templates/world-bible/Templates/World-Bible-Index.md` (Central navigation dashboard with Dataview queries)
- [x] Create `templates/world-bible/.obsidian-recommended-plugins.md` (Setup instructions for Dataview, Templater, Kanban, Excalidraw)

### 5. novelWriter Manuscript Starter Pack
- [x] Create `templates/manuscript/nwProject.nwx` (Documented placeholder; real fileVersion 1.5 project must be created via novelWriter GUI — see header comment)
- [x] Create `templates/manuscript/Outlines/Master-Outline.md` (3-Act / Hero's Journey story structure)
- [x] Create `templates/manuscript/Book-01/01_Act_I/01_Chapter_01.md` (Starter chapter with novelWriter markdown tags)
- [x] Create `templates/manuscript/Book-01/01_Act_I/02_Chapter_02.md`
- [x] Create `templates/manuscript/Book-01/02_Act_II/01_Chapter_03.md`
- [x] Create `templates/manuscript/Book-01/03_Act_III/01_Chapter_04.md`

### 6. Typst Typesetting Engine & Book Templates
- [x] Create `templates/typst/book_template.typ` (Publication-grade novel layout: half-title, copyright, alternating running headers, front-matter pagination)
- [x] Create `templates/typst/preview_sample.typ` (Complete sample book with chapters to test rendering)

### 7. Distraction Control & Backup Runbooks
- [x] Create `configs/leechblock_scriptorium_rules.json` (Pre-configured LeechBlock NG export file)
- [x] Create `configs/xfce_dnd_setup.md` (XFCE Do-Not-Disturb & notification configuration)
- [x] Create `configs/deja_dup_backup_guide.md` (Automated weekly backup runbook with 3-2-1 rule)

### 8. Master Setup Guide & Verification
- [x] Create `README.md` (Comprehensive step-by-step documentation for installing and using Scriptorium)
- [x] Static hardening pass 2026-09-04 (Typst import, dotfiles, sanitization, trap, NUL-safe listing, git fallback, Wayland, Typst context, arch/XDG)
- [x] Create `scripts/verify.sh`, `LICENSE`, `.gitattributes`, root `.gitignore`, `Finishing_Touches.md` manual
- [x] Archive superseded `scriptorium_plan.md/.txt` to `docs/archive/` and refresh project/knowledge/decisions docs
- [ ] Live verify on Linux Mint XFCE per `Finishing_Touches.md` (`shellcheck`, `typst compile preview_sample.typ`, LeechBlock import, novelWriter GUI project, full setup run)
