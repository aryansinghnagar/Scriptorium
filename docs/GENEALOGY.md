# Ars Arcanum — Dynastic Genealogies & Succession Lineages Guide
> **Engine**: `scripts/lib/genealogy.py` | **CLI**: `arcanum genealogy`, `arcanum lineage`

---

## 1. Overview & Purpose

The **Dynastic Genealogies & Succession Lineage Engine** analyzes royal houses, noble bloodlines, succession claims, and family trees across your World Bible. It parses character dossiers in `Characters/*.md`, detects biological and chronological paradoxes, validates monarchical succession rankings, and outputs diagrams in Obsidian-native Mermaid.js, ASCII terminal trees, or standalone offline HTML reports.

### Core Capabilities
- **Bidirectional Family Graph Construction**: Resolves parents, children, spouses, and consort relationships across wikilinked markdown dossiers.
- **Biological & Chronological Paradox Validation**: Detects impossible birth/death chronology, children born before parents, children conceived posthumously, and circular ancestry loops ($A \to B \to A$).
- **Dynastic Succession Ranking**: Validates crown inheritance orders (`succession_order`), identifying conflicting rank claims and line of succession rosters.
- **Multi-Format Visualizers**: Interactive offline HTML dossiers, clean Mermaid.js flowcharts for Obsidian, and ANSI colored terminal trees.

---

## 2. Character Dossier Schema & Frontmatter

To enable dynastic genealogy tracking, configure YAML frontmatter in `World/Characters/*.md`:

```markdown
---
name: "King Eldor I"
type: character
house: "House Vance"
title: "High King of the Spires"
gender: "Male"
born: "100 AC"
died: "165 AC"
succession_order: 1
parents: []
spouses: ["[[Queen Alyssa]]"]
children: ["[[Prince Valen]]", "[[Princess Lyra]]"]
---
# King Eldor I
Founder of the modern Spire dynasty.
```

### Child Note (`World/Characters/Prince_Valen.md`)
```markdown
---
name: "Prince Valen"
type: character
house: "House Vance"
title: "Crown Prince"
gender: "Male"
born: "125 AC"
died: "180 AC"
succession_order: 2
parents: ["[[King Eldor I]]", "[[Queen Alyssa]]"]
---
# Prince Valen
The fiery heir who led the Vanguard.
```

---

## 3. Diagnostic Codes Reference

| Code | Severity | Description | Remediation |
| :--- | :--- | :--- | :--- |
| **`GEN-101`** | `FATAL` / `WARNING` | **Chronological / Biological Paradox**: Circular ancestry loop ($A \to B \to A$), character died before birth, child born before parent, or child born $>1$ year after parent death. | Correct dates in character frontmatter or fix parent links. |
| **`GEN-102`** | `WARNING` | **Conflicting Succession Claim**: Multiple characters in the same house claim the same `succession_order` integer rank. | Reassign succession orders or declare pretender/claimant status in title. |

---

## 4. CLI Command Reference

### Build and Inspect Dynastic Family Tree
```bash
# View terminal family tree and lineage for a house
arcanum genealogy "House Vance" -w World/

# Output raw Mermaid.js flowchart for embedding into Obsidian notes
arcanum genealogy "House Vance" -w World/ --mermaid

# Export standalone interactive HTML family tree report
arcanum genealogy "House Vance" -w World/ --html exports/vance_tree.html
```

### Display Dynastic Lineage Roster
```bash
# Display chronological succession ranking
arcanum lineage "House Vance" -w World/

# Machine-readable JSON output
arcanum lineage "House Vance" -w World/ --json
```

---

## 5. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`re`, `html`, `json`, `pathlib`, `collections`).
- **Atomic Writing**: HTML reports written via `atomic_write()` from `lib._bootstrap.py`.
- **Strict Content Security Policy**:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
