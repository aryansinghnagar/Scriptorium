# Ars Arcanum — Static World Wiki & Codex Exporter Guide
> **Engine**: `scripts/lib/codex_export.py` | **CLI**: `arcanum codex`

---

## 1. Overview & Purpose

The **Static World Wiki & Codex Exporter** compiles an Obsidian World Bible vault into a single-file, self-contained offline HTML encyclopedia. It resolves internal `[[Wikilinks]]`, renders structured frontmatter Infobox cards, inlines a client-side search index, and provides multiple reading themes (Dark, Light, Classic Sepia) without any external dependencies or network requests.

### Core Capabilities
- **Automated Taxonomy Categorization**: Scans `Characters/`, `Locations/`, `Factions/`, `Artifacts/`, `Bestiary/`, `Cosmology/`, `Languages/`, `MagicSystems/`, and `History/`.
- **Bidirectional Wikilink Resolution**: Resolves both `[[Article]]` and `[[Article|Display Label]]` into clickable in-page anchors.
- **Dynamic YAML Infobox Generation**: Parses frontmatter properties into wiki-style side infoboxes.
- **Client-Side Inverted Search**: Instant offline full-text search across article titles and excerpt bodies.
- **Multi-Theme Reader**: Dark Mode, Light Mode, and Sepia Papyrus themes with persistent state.

---

## 2. World Vault Folder Structure

Organize your World Bible with canonical taxonomy folders:
```
World/
├── Characters/
│   ├── Kaelen_Vane.md
│   └── Elena.md
├── Locations/
│   ├── High_Vale.md
│   └── Valenreach.md
├── Factions/
│   └── Silver_Concordat.md
├── MagicSystems/
│   └── Aether_Weaving.md
└── Artifacts/
    └── Obsidian_Crown.md
```

### Note Frontmatter & Wikilink Syntax
```markdown
---
name: Kaelen Vane
role: Major Protagonist
status: Active
faction: Silver Concordat
origin: High Vale
---
# Kaelen Vane

A master swordsman hailing from [[High_Vale|The High Vale]]. He serves as captain within the [[Silver_Concordat]].
```

---

## 3. CLI Command Reference

### Export Single-File Standalone Codex
```bash
# Export codex for the current world vault
arcanum codex World/

# Custom output file location
arcanum codex World/ -o exports/World_Codex.html
```

---

## 4. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`html`, `json`, `re`, `pathlib`).
- **Atomic Writing**: Output HTML is written using `atomic_write()` from `lib._bootstrap.py`.
- **Strict Content Security Policy**:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
