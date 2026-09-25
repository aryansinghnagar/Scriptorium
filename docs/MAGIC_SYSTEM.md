# Ars Arcanum — Hard Magic Systems & Arcane Constraint Matrix Guide
> **Engine**: `scripts/lib/magic_system.py` | **CLI**: `arcanum magic-check`, `arcanum magic-report`

---

## 1. Overview & Purpose

The **Hard Magic Systems & Arcane Constraint Matrix** is a local-first semantic validator and analyzer designed for authors constructing hard magic systems, rationalist fantasy rules, and metaphysical power limits. It automatically enforces Brandon Sanderson's Laws of Magic by verifying that characters operate strictly within their defined tier boundaries, consume mandatory catalysts/reagents, respect hard metaphysical limitations, and track safe fatigue thresholds across manuscript scenes.

### Core Capabilities
- **Magic System Rule Extraction**: Analyzes `Magic-Technology/*.md` for power sources, danger costs, maximum tiers, branches/disciplines, required catalysts, and explicit negative constraints (`hard_limitations`).
- **Character Arcane Attunement Profiling**: Reads `Characters/*.md` to extract character magic tiers, discipline affinities, bound focus items/catalysts, and maximum fatigue capacities.
- **Scene-Level Semantic Casting Audit**: Verifies `@cast:`, `@magic:`, `@reagent:`, and `@cost:` tags within manuscript scenes alongside natural prose casting descriptions.
- **Offline HTML & JSON Reporting**: Generates interactive visual audit dashboards with strict offline Content Security Policies.

---

## 2. World Vault & Manuscript Directives

### A. Magic System Definition (`World/Magic-Technology/Aether_Weaving.md`)
```markdown
---
name: "Aether Weaving"
type: magic_tech_system
classification: "Hard Magic"
source_of_power: "Atmospheric Aether"
danger_cost: "High"
max_tier: 5
disciplines:
  - "Pyromancy"
  - "Chronomancy"
catalysts:
  - "Ruby Focus"
  - "Silver Thread"
hard_limitations:
  - "Cannot resurrect the dead"
  - "Cannot create matter from nothing"
---
# Aether Weaving
## 1. Core Concept & Fundamental Rules
Energy must be conserved at all times.
```

### B. Character Magic Attunement (`World/Characters/Valen.md`)
```markdown
---
name: "Valen Vance"
type: character
role: Protagonist
magic_tier: 2
magic_ability: "Pyromancy"
catalyst: "Ruby Focus"
max_fatigue: 80
---
# Valen Vance
A promising initiate attuned to flame.
```

### C. Manuscript Scene Casting Directives (`Manuscript/Book-01/01_Scene.md`)
```markdown
# Chapter 1: The Breach
@pov: Valen Vance
@reagent: Ruby Focus
@cast: Valen Vance, Firebolt, tier=2, catalyst=Ruby Focus, cost=25

Valen channeled the ambient aether through his focus crystal, releasing a burst of heat.
```

---

## 3. Diagnostic Codes Reference

| Code | Severity | Description | Remediation |
| :--- | :--- | :--- | :--- |
| **`MAG-101`** | `WARNING` | **Tier Limit Violation**: Character attempted to cast a spell/discipline higher than their registered magic tier without an amplifying relic. | Elevate character tier in lore or lower scene spell tier requirement. |
| **`MAG-102`** | `WARNING` | **Missing Catalyst / Reagent**: Spell requires a specific catalyst not present in character inventory or scene reagents. | Add `@reagent:` tag to scene or equip catalyst in character frontmatter. |
| **`MAG-103`** | `WARNING` | **Hard Limitation Breach**: Scene prose describes an action explicitly prohibited by the magic system (e.g. resurrection, spontaneous matter generation). | Revise prose to conform to metaphysical law or explain through separate cosmological phenomenon. |
| **`MAG-104`** | `ADVISORY` | **Fatigue Overdraw**: Accumulated scene fatigue exceeds the character's safe threshold without rest/recovery. | Introduce rest beats, divide casting load among allies, or reduce fatigue cost. |

---

## 4. CLI Command Reference

### Run Arcane Consistency Check
```bash
# Check magic consistency across world and manuscript
arcanum magic-check World/ -m Manuscript/

# Machine-readable JSON output
arcanum magic-check World/ -m Manuscript/ --json
```

### Generate Visual Arcane Report
```bash
# Generate interactive HTML dashboard
arcanum magic-report World/ -m Manuscript/ --html exports/magic_report.html
```

---

## 5. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`re`, `html`, `json`, `pathlib`).
- **Atomic File Writing**: Reports written via `atomic_write()` from `lib._bootstrap.py`.
- **Strict Content Security Policy**:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
