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
- 🐾 **[[Bestiary/Creature-Flora-Fauna-Template|Bestiary & Ecosystems]]**
- 🗡️ **[[Artifacts/Artifact-Relic-Template|Relics & Artifacts]]**
- ✨ **[[Cosmology/Deity-Cosmology-Template|Pantheons & Cosmology]]**
- ⏳ **[[History/Timeline-Event-Template|Historical Chronology]]**
- 🗣️ **[[Languages/Glossary-Conlang-Template|Linguistics & Glossaries]]**
- 📅 **[[Templates/Daily-Writing-Log|Writing Logs & Word Counts]]**

---

## 👤 Active Characters
```dataview
TABLE role as "Role", status as "Status", faction as "Faction", current_location as "Location"
FROM #world/character
SORT file.name ASC
```

---

## 🗺️ Key Locations & Realms
```dataview
TABLE region as "Region", dominant_faction as "Ruling Faction", scale as "Scale", danger_level as "Danger"
FROM #world/location
SORT file.name ASC
```

---

## ⚔️ Factions & Power Structures
```dataview
TABLE leader as "Leader", headquarters as "HQ", faction_type as "Type", influence_level as "Influence"
FROM #world/faction
SORT file.name ASC
```

---

## ⚡ Magic & Tech Systems
```dataview
TABLE classification as "Classification", source_of_power as "Power Source", prevalence as "Prevalence", danger_cost as "Cost / Danger"
FROM #world/system
SORT file.name ASC
```

---

## 🗣️ Languages & Dialects
```dataview
TABLE language_family as "Family", spoken_by as "Spoken By", status as "Status", writing_system as "Writing System"
FROM #world/language
SORT file.name ASC
```

---

## 🐾 Bestiary & Flora / Fauna
```dataview
TABLE classification as "Classification", threat_level as "Threat", habitat as "Habitat"
FROM #world/bestiary
SORT file.name ASC
```

---

## 🗡️ Legendary Artifacts & Relics
```dataview
TABLE artifact_type as "Type", rarity as "Rarity", current_bearer as "Bearer"
FROM #world/artifact
SORT file.name ASC
```

---

## ✨ Pantheons, Deities & Cosmology
```dataview
TABLE concept_type as "Type", domain as "Domain", worship_status as "Worship"
FROM #world/cosmology
SORT file.name ASC
```

---

## ⏳ Historical Timeline
```dataview
TABLE year as "Year", era as "Era", primary_location as "Location", significance as "Significance"
FROM #world/history
SORT year ASC
```

---

## 📊 Recent Writing Logs
```dataview
TABLE words_written as "Words", writing_time_minutes as "Minutes", mood_focus as "Focus (1-5)"
FROM #meta/log
SORT date DESC
LIMIT 10
```
