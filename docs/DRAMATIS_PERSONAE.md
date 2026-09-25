# Ars Arcanum — Multi-Volume Dramatis Personae & Universe Cast Matrix Guide
> **Engine**: `scripts/lib/dramatis_personae.py` | **CLI**: `arcanum dramatis-personae`, `arcanum cast`

---

## 1. Overview & Purpose

The **Multi-Volume Dramatis Personae & Universe Cast Matrix** provides narrative designers and series authors with an automated character tracking, continuity auditing, and publication-ready appendix compiler. It bridges worldbuilding character dossiers (`World/Characters/*.md`) with manuscript chapters across multi-volume series, keeping track of appearances, POV scenes, allegiances, and character lifecycles.

### Core Capabilities
- **Multi-Volume Cast Discovery**: Scans World Bible dossiers and indexes names, aliases, allegiances, roles, statuses, and origins.
- **Manuscript Cross-Referencing**: Tracks `@char:`, `@cast:`, `@pov:`, `@character:`, and `@death:` directives across all chapters and volumes.
- **Continuity & Lifecycle Audits**:
  - `CAS-101`: **Ghost Character**: Character mentioned in manuscript without an existing World Bible dossier.
  - `CAS-102`: **Post-Mortem Action**: Deceased character appears or takes action in subsequent chapters after a recorded death event.
  - `CAS-103`: **Orphan Lore Character**: Character defined in World Bible dossiers with zero manuscript appearances.
- **Publication Exports**:
  - Formatted **Markdown Dramatis Personae** appendix grouped by faction.
  - Offline, CSP-compliant **Interactive HTML Character Gallery**.

---

## 2. Character Lore Schema & In-Prose Directives

### Character Dossier Frontmatter (`World/Characters/*.md`)
```markdown
---
name: Kaelen Vane
aliases:
  - The Ghostblade
  - Shade of Oakhaven
role: Major Protagonist
status: Active
faction: Silver Concordat
origin: High Vale
---
# Kaelen Vane
Master swordsman of the northern reaches...
```

### In-Manuscript Directives
```markdown
---
title: The Fall of High Vale
pov: Kaelen Vane
characters:
  - Marcus
  - Lyra
---
@char: Garrick, Elena
The swords clashed against the stone gates.

@death: Marcus
Marcus fell before the citadel gates.
```

| Directive | Description | Example |
|:---|:---|:---|
| `@pov: Character` | Designates the point-of-view character for the scene or chapter. | `@pov: Kaelen Vane` |
| `@char: Char1, Char2` | Registers characters present in the scene. | `@char: Lyra, Garrick` |
| `@cast: Char1; Char2` | Alternative alias for `@char:`. | `@cast: Elena; Marcus` |
| `@death: Character` | Marks a canonical death event for the character. | `@death: Marcus` |

---

## 3. CLI Command Reference

### Basic Cast Extraction & Console Table
```bash
# Analyze cast across universe directory
arcanum cast Universes/Eldoria-Cosmos

# Equivalent full command
arcanum dramatis-personae Universes/Eldoria-Cosmos
```

### Exporting Publication Appendices
```bash
# Export formatted Markdown Dramatis Personae appendix
arcanum cast Universes/Eldoria-Cosmos --markdown Manuscripts/Book-01/Back_Matter/DRAMATIS_PERSONAE.md

# Export standalone offline HTML character gallery
arcanum cast Universes/Eldoria-Cosmos --html reports/cast_gallery.html

# Machine-readable JSON output for integrations
arcanum cast Universes/Eldoria-Cosmos --json
```

---

## 4. Continuity Diagnostic Codes Reference

| Code | Severity | Name | Description | Remediation |
|:---|:---|:---|:---|:---|
| `CAS-101` | **WARNING** | **Ghost Character** | A character is tagged in manuscript scenes but lacks a corresponding dossier in `World/Characters/`. | Create a character dossier in `World/Characters/` or add an alias to an existing character profile. |
| `CAS-102` | **ERROR** | **Post-Mortem Action** | A character appears in a chapter after their recorded `@death:` event chapter. | Verify scene ordering, remove accidental appearances, or mark resurrected characters with updated lore status. |
| `CAS-103` | **INFO** | **Orphan Lore Character** | A character has a detailed lore dossier in `World/Characters/` but never appears in the manuscript. | Integrate character into manuscript scenes or archive unused background lore dossiers. |

---

## 5. Architectural Invariants

- **Zero-Pip Guarantee**: Pure Python standard library implementation (`json`, `html`, `re`, `dataclasses`, `pathlib`).
- **Atomic Writes**: Uses `atomic_write()` from `lib._bootstrap.py` for all markdown and HTML exports.
- **Offline CSP Enforcement**: Generated HTML gallery includes strict `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">`.
