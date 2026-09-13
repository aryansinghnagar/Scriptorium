# Obsidian Out-of-the-Box Plugin Suite Guide

Your Scriptorium World Bible comes pre-configured with a premier, modular suite of worldbuilding and authoring plugins enabled out-of-the-box.

---

## 🌟 Core Narrative & Manuscript Plugins

| Plugin | Primary Function | Pre-Configured Capabilities |
| :--- | :--- | :--- |
| **Storyline** | All-in-One Narrative Engine | Visual character relationship webs, event timeline boards, and narrative arc tracking linked directly to your `Characters/`, `Locations/`, and `History/` notes. |
| **Longform** | Manuscript Organization & Compilation | Atomic Markdown scene ordering, drag-and-drop drafting pane, inline comment stripping (`%% notes %%`), and direct compilation bridge to Typst/EPUB. |
| **Dataview** | Dynamic Lore Querying & Registries | DQL database queries across character scene appearances, faction rosters, and geographic registries with inline JS support enabled. |
| **Metadata Menu** | Structured Frontmatter & Schemas | Strict `fileClass` schemas in `Templates/fileClasses/` with dropdown validation for character status, location scales, faction influence, timeline years, and magic rules. |
| **Calendarium** | Fictional Time & Astronomical Mechanics | Non-Gregorian fictional calendars, custom month lengths, moon phase cycles, and in-world event agendas linked via `fc-date`. |
| **Storyteller Suite** | Interactive Spatial Cartography | Recursive nested map hierarchies (World -> Continent -> Province -> Settlement -> Floor Plan) in `02-Maps/` with pins linked directly to lore notes. |
| **Novel Word Count** | File Explorer Volume Analytics | Real-time word counts injected beside every folder and document in your File Explorer, rolling scene counts into chapter totals. |
| **Obsidian Git** | Automated In-Vault Version Control | Automatic background Git commits every 10 minutes and on save, status bar indicators, and seamless local versioning. |
| **Templater** | Dynamic Template Generation | Automatic templating triggered on note creation with date math, file title variables, and frontmatter automation. |
| **Style Settings & Minimal Theme** | Distraction-Free Author Typography | Literary typography (Linux Libertine, EB Garamond), line width optimization (42rem), and distraction-free focus modes. |

---

## 🛠️ Out-of-the-Box Configuration Details

1. **Automatic Git Tracking**:
   - Every note edit is tracked by the local World Git repository.
   - Background backups occur automatically every 10 minutes and when closing/switching files.

2. **Metadata Validation & Schemas**:
   - `Templates/fileClasses/` provides pre-built schemas for:
     - `Character.md`: Name, aliases, role, status (Alive/Deceased/Missing/Unknown), faction, location, origin.
     - `Location.md`: Name, region, dominant faction, scale (Continent to Interior).
     - `Faction.md`: Name, faction type, leader, headquarters, influence level.
     - `TimelineEvent.md`: Name, era, start_year, end_year, primary location, participants.
     - `Creature.md`: Name, classification, threat level, habitat, diet, domestication.
     - `Artifact.md`: Name, artifact type, rarity, creator, current bearer, location, attunement.
     - `Cosmology.md`: Name, concept type, domain, plane of origin, worship status, associated faction.
     - `MagicSystem.md`: Name, classification, power source, prevalence, danger/cost.
     - `Language.md`: Name, language family, spoken by, status, writing system.

3. **Manuscript & Maps Folders**:
   - `01-Manuscript/` contains discrete chapter files and Longform project indexes.
   - `02-Maps/` houses Storyteller Suite interactive maps and Azgaar/Krita exports.
   - `03-Art/` serves as the default attachment folder for visual character and location assets, and EPUB cover art.
