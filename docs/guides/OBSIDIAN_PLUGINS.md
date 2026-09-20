# Obsidian Out-of-the-Box Plugin Suite Guide

Your Ars Arcanum World Lore Vaults come pre-configured with a premier, modular suite of worldbuilding and authoring plugins enabled out-of-the-box.

---

## 🌟 Core Narrative & Worldbuilding Plugins

| Plugin | Primary Function | Pre-Configured Capabilities |
| :--- | :--- | :--- |
| **Storyline** | All-in-One Narrative Engine | Visual character relationship webs, event timeline boards, and narrative arc tracking linked directly to your `Characters/`, `Locations/`, and `History/` notes. |
| **Longform** | Manuscript Organization & Compilation | Atomic Markdown scene ordering, drag-and-drop drafting pane, inline comment stripping (`%% notes %%`), and direct compilation bridge to Typst/EPUB. |
| **Dataview** | Dynamic Lore Querying & Registries | DQL database queries across character scene appearances, faction rosters, and geographic registries with inline JS support enabled. |
| **Metadata Menu** | Structured Frontmatter & Schemas | Strict `fileClass` schemas in `Templates/fileClasses/` with dropdown validation for character status, location scales, faction influence, timeline years, and magic rules. |
| **Calendarium** | Fictional Time & Astronomical Mechanics | Non-Gregorian fictional calendars, custom month lengths, moon phase cycles, and in-world event agendas linked via `fc-date`. |
| **Storyteller Suite** | Interactive Spatial Cartography | Spatial relationship graphs and interactive visual lore nodes with pins linked directly to lore notes. |
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
     - `Economy.md`: Base currency, denominations, commodity basket PPP rates, trade routes.
     - `Prophecy.md`: Oracle/source, era given, prophecy clauses, fulfillment status, intended resolution.

3. **Pure Lore Vault Structure**:
   - `Characters/`, `Locations/`, `Factions/`, `Economies/`, `Magic-Technology/`, `History/`, `Languages/`, `Bestiary/`, `Artifacts/`, `Cosmology/` provide dedicated domain folders.
   - `Templates/` houses quickstart notes, fileClasses, and the central `World-Bible-Index.md` Dataview dashboard.
   - All frontmatter properties are automatically validated by `arcanum doctor` and `arcanum world_doctor` for semantic continuity, timeline paradoxes, and lore consistency.
