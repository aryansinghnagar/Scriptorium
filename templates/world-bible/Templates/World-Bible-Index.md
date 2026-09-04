---
type: dashboard
tags:
  - meta/index
---

# 📖 World Bible & Codex Index

Welcome to your central worldbuilding hub. Every note created in this vault is interconnected via wikilinks and indexed dynamically below using **Dataview**.

---

## 🏛️ Quick Navigation Links
- 👤 **[[Characters/Character-Template|Character Vault]]**
- 🗺️ **[[Locations/Location-Template|World Atlas & Geography]]**
- ⚔️ **[[Factions/Faction-Template|Factions & Guilds]]**
- ⚡ **[[Magic-Technology/Magic-Tech-System-Template|Magic & Tech Systems]]**
- ⏳ **[[History/Timeline-Event-Template|Historical Chronology]]**
- 🗣️ **[[Languages/Glossary-Conlang-Template|Linguistics & Glossaries]]**
- 📅 **[[Templates/Daily-Writing-Log|Writing Logs & Word Counts]]**

---

## 👤 Active Characters
```dataview
TABLE role as "Role", faction as "Faction", origin as "Origin"
FROM #world/character
SORT file.name ASC
```

---

## 🗺️ Key Locations & Realms
```dataview
TABLE realm_region as "Region", dominant_faction as "Ruling Faction", danger_level as "Danger"
FROM #world/location
SORT file.name ASC
```

---

## ⚔️ Factions & Power Structures
```dataview
TABLE leader as "Leader", headquarters as "HQ", ideology as "Ideology"
FROM #world/faction
SORT file.name ASC
```

---

## ⏳ Historical Timeline
```dataview
TABLE year_date as "Date", era as "Era", significance as "Significance"
FROM #world/history
SORT year_date ASC
```

---

## 📊 Recent Writing Logs
```dataview
TABLE words_written as "Words", writing_time_minutes as "Minutes", mood_focus as "Focus (1-5)"
FROM #meta/log
SORT date DESC
LIMIT 10
```
