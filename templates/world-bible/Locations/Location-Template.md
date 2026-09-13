---
type: location
name: "<% tp.file.title %>"
aliases: []
tags:
  - world/location
  - status/active
region: "[[Region-Name]]"
dominant_faction: "[[Faction-Name]]"
scale: "Continent / Realm / Nation / Province / Region / Settlement / City / Landmark / Site / Building / Interior"
climate_terrain: "Temperate Highland / Arid Desert / Dense Rainforest"
key_landmarks: []
danger_level: "Safe / Moderate / Perilous / Lethal"
---

# <% tp.file.title %>

> *"A sensory line describing the atmosphere upon entering this location."*

---

## 1. Overview & Geography
Brief description of where this location sits on the world map, its surrounding biomes, and its strategic or historical significance.

- **Coordinates / Map Grid**: See [[Map-World-Master]]
- **Terrain & Climate**:
- **Natural Resources**:

---

## 2. Sensory Palette (Sights, Sounds, Smells)
- **Visuals**: Architecture, lighting, dominant materials (black basalt, weathered timber, polished glass).
- **Soundscape**: Bustling marketplace shouts, hollow wind through spires, rhythmic forge hammers.
- **Smells & Tastes**: Burning cedar, salty sea brine, ozone, roasting meats, sewer dampness.

---

## 3. Society, Culture & Daily Life
- **Dominant Inhabitants & Demographics**:
- **Governance & Law Enforcement**:
- **Economy, Trade & Currency**:
- **Social Customs, Taboos & Superstitions**:
- **Cuisine & Local Delicacies**:

---

## 4. Notable Districts & Landmarks
1. **The Citadel / Center of Power**:
2. **The Common Quarter / Bazaar**:
3. **The Underbelly / Ruins**:

---

## 5. History, Lore & Rumors
- **Founding Lore**:
- **Major Past Conflicts**:
- **Tavern Rumors & Plot Hooks**:
  - *Rumor 1*:
  - *Rumor 2*:

---

## 6. Associated Characters & Factions
```dataview
TABLE role as "Role", faction as "Faction"
FROM #world/character
WHERE current_location = this.file.link OR origin = this.file.link
```
