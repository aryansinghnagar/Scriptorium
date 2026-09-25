# Ars Arcanum — Geopolitical Faction Matrix & Campaign Logistics Guide
> **Engine**: `scripts/lib/factions.py` | **CLI**: `arcanum faction check`, `arcanum faction battle`, `arcanum faction logistics`

---

## 1. Overview & Purpose

The **Geopolitical Faction Matrix & Campaign Logistics Engine** models political intrigue, diplomatic treaties, military power curves, and realistic medieval/speculative army supply chains. It scans World Bible `Factions/*.md` dossiers, verifies multilateral alliance networks against diplomatic paradoxes, calculates Lanchester power-law battles, and computes realistic wagon-train radii for military campaigns.

### Core Capabilities
- **Diplomatic Alignment Matrix**: Tracks allies, rivals, vassals, overlords, treaties, and military strength across world factions.
- **Diplomatic Paradox Detection**: Uncovers asymmetric alliances, contradictory rivalries, triad tensions (allies of enemies), and vassal treason.
- **Lanchester Combat Simulator**: Simulates aimed ranged fire (Square Law) and direct melee engagements (Linear Law) with fortification and morale multipliers.
- **Military Campaign Logistics Calculator**: Quantifies soldier rations, mount/draft fodder, wagon payloads, and operational "Wagon Radius" limits.
- **Visual Graph & HTML Dashboards**: Exports Obsidian-ready Mermaid.js flowcharts and standalone dark-themed HTML dossiers.

---

## 2. Faction Dossier Schema (`World/Factions/Solar_Empire.md`)

```markdown
---
name: "Solar Empire"
type: faction
faction_type: "Empire"
leader: "[[Emperor Sol]]"
headquarters: "[[Valenreach]]"
influence_level: "Continental"
military_strength: 50000
allies:
  - "[[Lunar Kingdom]]"
rivals:
  - "[[Void Syndicate]]"
vassals:
  - "[[House Vance]]"
treaties:
  - "Treaty of the Spires"
---
# Solar Empire
The dominant hegemony spanning the eastern continents.
```

---

## 3. Diagnostic Codes Reference

| Code | Severity | Description | Remediation |
| :--- | :--- | :--- | :--- |
| **`FAC-101`** | `ERROR` / `WARNING` | **Diplomatic Contradiction / Asymmetry**: Faction $A$ claims alliance with $B$, but $B$ lists $A$ as a rival or fails to reciprocate. | Synchronize frontmatter alliances across both faction files. |
| **`FAC-102`** | `WARNING` | **Triad Tension Paradox**: Faction $A$ allies $B$, $B$ allies $C$, but $A$ and $C$ are declared rivals. | Acknowledge diplomatic tension in lore or dissolve conflicting treaty. |
| **`FAC-103`** | `ERROR` | **Vassal Allegiance Conflict**: Vassal of $A$ is allied with a declared rival/enemy of $A$. | Strip vassal alliance or document vassal rebellion/betrayal. |
| **`FAC-104`** | `WARNING` | **Self-Reference**: Faction lists itself in its own `allies` or `rivals` list. | Remove self-reference from frontmatter list. |

---

## 4. CLI Command Reference

### Check Geopolitical Consistency & Paradoxes
```bash
# Audit diplomatic relations across factions
arcanum faction check World/

# Export Mermaid relationship flowchart to markdown note
arcanum faction check World/ --write-note World/Factions/Relationship_Graph.md

# Generate standalone interactive HTML report
arcanum faction check World/ --html exports/faction_matrix.html
```

### Lanchester Combat Simulation (`battle`)
```bash
# Simulate ranged/firepower battle (Square Law: 10,000 vs 5,000 with 3x Fortification)
arcanum faction battle -a 10000 -d 5000 --fort 3.0 --law square

# Simulate melee battle (Linear Law: 4,000 vs 4,000)
arcanum faction battle -a 4000 -d 4000 --law linear
```

### Campaign Logistics & Wagon Radius Calculator (`logistics`)
```bash
# Calculate supply requirements for 10,000 infantry + 2,000 cavalry over 200 km
arcanum faction logistics --infantry 10000 --cavalry 2000 --distance 200 --speed 20
```

---

## 5. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`math`, `html`, `json`, `re`, `pathlib`).
- **Atomic Writing**: HTML reports written via `atomic_write()` from `lib._bootstrap.py`.
- **Strict Content Security Policy**:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
