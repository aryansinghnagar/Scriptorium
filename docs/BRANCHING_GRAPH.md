# Interactive Branching Narrative Graph & Choice Engine
> **Ars Arcanum Module**: `scripts/lib/branching_graph.py` | **CLI**: `arcanum branch` (alias: `branching`)

---

## 1. Overview & Narrative Capabilities

The **Ars Arcanum Interactive Branching Narrative Graph Engine** allows authors of choose-your-own-adventure gamebooks, interactive fiction, and multi-pathway novels to write in plain Markdown while validating topological integrity and exporting to interactive narrative runtimes.

### Key Capabilities
1. **Plaintext Choice & State Directives**:
   - Write natural branching directives in any Markdown scene:
     - `@choice: "Descend into the crystal mines" -> Chapter_03`
     - `@choice: "Use the skeleton key" -> Treasure_Vault [req: has_key >= 1]`
     - `@state: courage + 1` or `@set: has_key = true`
     - `@ending: true`, `@death: true`, `@victory: true`
2. **Topological Integrity Diagnostics**:
   - `BRN-101`: Dead-End Leaf detection.
   - `BRN-102`: Orphan / Unreachable Passage detection.
   - `BRN-105`: Non-existent Choice Target detection.
3. **Multi-Engine Compilation**:
   - **Playable HTML5 Gamebook**: Self-contained offline reader with real-time passage state and choice buttons.
   - **Inkle Ink (`.ink`)**: Production-ready script for the Inkle Ink interactive fiction engine.
   - **Twine 2 / Twee 3 (`.twee`)**: Standard format for Twine interactive fiction engines (Harlowe, SugarCube).
   - **Obsidian Mermaid**: Visual decision flowchart.

---

## 2. CLI Usage Reference

### 2.1 Graph Inspection & Audit
```bash
# Scan and audit branching topology of an interactive manuscript
arcanum branch ~/Manuscripts/InteractiveGamebook/ --audit

# Output structured narrative DAG in JSON
arcanum branch ~/Manuscripts/InteractiveGamebook/ --json
```

### 2.2 Multi-Format Compilation
```bash
# Export to standalone playable HTML reader
arcanum branch ~/Manuscripts/InteractiveGamebook/ --html dist/gamebook.html

# Export to Inkle Ink narrative script
arcanum branch ~/Manuscripts/InteractiveGamebook/ --ink dist/story.ink

# Export to Twine 2 Twee 3 script
arcanum branch ~/Manuscripts/InteractiveGamebook/ --twine dist/story.twee

# Export to Obsidian Mermaid diagram
arcanum branch ~/Manuscripts/InteractiveGamebook/ --mermaid dist/flowchart.md
```

---

## 3. Playable HTML Reader Architecture

The generated HTML gamebook reader operates under a strict offline Content Security Policy:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
```
It bundles all scene text, choice routing logic, and ending state styling into a single standalone file that runs offline in any web browser.
