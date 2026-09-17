# Subplot & Narrative Thread Pacing Matrix
### A Multi-Thread Pacing & Scene Architecture Engine for Novelists

---

## 1. Overview & Narrative Thread Doctrine

Modern speculative fiction and complex novels weave multiple concurrent narrative threads across acts. Tracking their pacing, scene frequency, and convergence points ensures that:
- Subplots do not vanish for 50,000 words only to be abruptly resolved.
- Tension rises smoothly across major plot turns and act climaxes.
- POV characters maintain clear, distinct narrative stakes.

---

## 2. Tagging Conventions (`@thread:` & Metadata)

When drafting scene markdown files in `<Book>/...` (e.g. `Book-01/01_Act_I/01_Chapter_01.md`), use novelWriter metadata tags at the top of each scene file. Scriptorium's publication export engine automatically strips these tags during compilation so they remain strictly for internal planning and Dataview tracking.

### Core Scene Metadata Headers
```markdown
# Chapter 3: The Broken Seal

@pov: Renée
@char: Renée, Kaelen
@location: Sanctuaire_des_Étoiles
@thread: Main-Plot-Seals, Subplot-Romance, Subplot-Ancient-Order
@pacing: High-Tension
@status: Draft
```

### Recommended Thread Naming Taxonomy
| Thread Identifier | Narrative Role | Recommended Pacing / Frequency |
| :--- | :--- | :--- |
| `@thread: Main-Plot-Conspiracy` | Central narrative arc (A-Plot) | Present in 60–70% of scenes |
| `@thread: Subplot-Romance` | Emotional & character relationship arc (B-Plot) | Woven through 20–30% of scenes |
| `@thread: Subplot-Heist-Relic` | Secondary objective / artifact quest (C-Plot) | Escalates in Act II-A to Midpoint |
| `@thread: Subplot-Faction-Rivalry`| Political / world tension | Informs antagonist counter-moves |
| `@thread: Lore-Discovery` | Worldbuilding revelations & ancient history | Peaks at Midpoint & Dark Night |

---

## 3. Dynamic Dataview Pacing Dashboards

*(These tables render automatically inside Obsidian when viewing this outline note)*

### A. Master Narrative Thread & Scene Matrix
```dataview
TABLE 
  pov as "POV",
  thread as "Active Plot Threads",
  location as "Location",
  pacing as "Pacing Beat",
  status as "Status"
FROM ""
WHERE !contains(file.path, "Outlines") AND file.name != "nwProject.nwx"
SORT file.path ASC
```

---

### B. Subplot Continuity & Deep-Focus Filter
*(Filter scenes touching a specific subplot, e.g. Romance or Heist)*
```dataview
TABLE 
  pov as "POV",
  location as "Location",
  status as "Draft Status"
FROM ""
WHERE (contains(thread, "Subplot-Romance") OR contains(file.tags, "#thread/romance")) AND !contains(file.path, "Outlines") AND file.name != "nwProject.nwx"
SORT file.path ASC
```

---

### C. POV Scene Distribution & Thread Balance
```dataview
TABLE count(file.link) as "Total Scenes", rows.file.link as "Scene Files"
FROM ""
WHERE !contains(file.path, "Outlines") AND file.name != "nwProject.nwx"
GROUP BY pov
```

---

## 4. Multi-Thread Pacing Architecture (3-Act Grid)

| Milestone / Act Range | A-Plot (Main Conflict) | B-Plot (Character / Subplot) | C-Plot (World / Antagonist) |
| :--- | :--- | :--- | :--- |
| **Act I (0% – 25%)** | Ordinary World disrupted; Call received; Threshold crossed | Inciting seed planted; first meaningful encounter | Distant rumblings; thematic shadow introduced |
| **Act II-A (25% – 50%)** | Trials, learning new rules, early tactical wins | Reluctant partnership forms; friction & vulnerability | Antagonist's plan advances in background |
| **Midpoint Shift (50%)** | Active offensive shift; false victory or catastrophe | Midpoint intimacy / major relationship shift | Antagonist strikes directly; stakes become existential |
| **Act II-B (50% – 75%)** | Pressure mounts; allies fractured; Dark Night of the Soul | Subplot crisis; trust broken or sacrifice demanded | Antagonist takes dominant ground |
| **Act III (75% – 100%)** | True Need unlocked; Climax showdown & resolution | Subplot climax / emotional resolution | Order restored or world permanently transformed |

---

## 5. Clean Compilation Invariant

Scriptorium's exporter (`scripts/export_book.sh` / `scriptorium export`) ensures that all `@thread:`, `@pov:`, `@char:`, `@location:`, and `@status:` tag lines are stripped prior to rendering Typst print PDFs and Pandoc EPUBs. You can freely annotate your draft files without fear of internal development tags leaking into your published books.
