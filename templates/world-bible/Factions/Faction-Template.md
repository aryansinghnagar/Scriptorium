---
type: faction
name: "<% tp.file.title %>"
aliases: []
tags:
  - world/faction
  - status/active
leader: "[[Leader-Character]]"
headquarters: "[[Location-Name]]"
sphere_of_influence: "Global / Continental / City / Underground"
ideology: "Theocratic / Merchant Guild / Rebel Resistance / Imperial Order"
symbols_colors: "Silver Hawk on Indigo / Crimson Dragon"
motto: "In Ferro Veritas"
---

# <% tp.file.title %>

> *"Official motto or rallying battle cry of the faction."*

---

## 1. Executive Overview
What is this organization, why was it formed, and what power does it wield in the world?

---

## 2. Goals & Motives
- **Public Stated Goal**: What they claim to fight for.
- **Hidden / True Agenda**: What the high council or leadership actually seeks.
- **Primary Foes & Rival Factions**: See [[Rival-Faction]]
- **Key Alliances**:

---

## 3. Hierarchy & Organization
- **Leadership Council / Head of State**: [[Leader-Character]]
- **Command Structure / Tiers**:
  - *Tier 1 (Elites / Inner Circle)*:
  - *Tier 2 (Officers / Enforcers)*:
  - *Tier 3 (Foot Soldiers / Common Members)*:
- **Initiation Rites & Oaths**:

---

## 4. Resources & Assets
- **Military & Martial Strength**:
- **Financial & Commercial Wealth**:
- **Magic / Technological Assets**:
- **Intelligence & Espionage Network**:

---

## 5. Known Members
```dataview
TABLE role as "Role", species_race as "Species"
FROM #world/character
WHERE faction = this.file.link
```
