# World Doctor & Cosmos Integrity Diagnostics
> **Ars Arcanum Module**: `scripts/lib/world_doctor.py` | **CLI**: `arcanum doctor` (alias: `check-world`)

---

## 1. Overview & Health Auditing Philosophy

Speculative fiction universes, fantasy world bibles, and multi-volume series often span hundreds of character profiles, faction histories, and magic system constraints. Over years of drafting, wikilinks break, character death dates precede birth dates, template notes are forgotten, and manuscript prose drifts away from established canon.

**Ars Arcanum World Doctor** is a sovereign, deterministic cosmos integrity checker that deeply audits Obsidian World Bibles and cross-validates manuscripts with **zero external dependencies and 100% offline privacy**.

---

## 2. Diagnostic Codes Reference

| Code | Category | Severity | Description & Remediation |
| :--- | :--- | :--- | :--- |
| **`WLD-101`** | `Link Integrity` | **ERROR** | **Broken Wiki-Link**: A `[[Target]]` or `[[Target\|Label]]` reference points to a non-existent note in the World Bible. |
| **`WLD-102`** | `Frontmatter` | **ERROR** | **Dangling Frontmatter Reference**: A typed YAML field (e.g. `faction: "[[The Silver Dawn]]"`) references an unregistered entity. |
| **`WLD-103`** | `Schema` | **ERROR** | **Missing Required Field**: An entity note lacks mandatory fields defined by its `type` (e.g. `type: character` lacking `name`). |
| **`WLD-104`** | `Chronology` | **ERROR** | **Timeline Chronological Inversion**: Death date precedes birth date, or historical era ordering is chronologically inverted across numbered eras (1E, 2E, 3E) or BCE/CE coordinates. |
| **`WLD-105`** | `Identity` | **ERROR** | **Duplicate Identity Claim**: Multiple files claim the same canonical character or location name. |
| **`WLD-106`** | `Syntax` | **ERROR** | **Frontmatter Syntax Error**: Unclosed YAML delimiters (`---`) or malformed key-value structures. |
| **`WLD-107`** | `Taxonomy` | **WARNING** | **Orphan Lore Note**: A note exists in the vault with zero incoming or outgoing links or mentions. |
| **`WLD-108`** | `Cross-Ref` | **WARNING** | **Manuscript Entity Drift**: A manuscript scene references characters, locations, or factions that do not exist in the World Bible. |

---

## 3. Multi-Era Timeline Parsing (WLD-104)

World Doctor supports multi-era calendar synchronization across diverse speculative formats:

- **BCE / CE**: `500 BCE` (parsed as $-500.0$), `1422 CE` ($+1422.0$).
- **Ordinal Eras**: `1422 3E` (Era 3, Year 1422), `100 2E` (Era 2, Year 100).
- **Named Ages**: `First Age`, `Second Age`, `Third Era`, `4a`, `5e`.
- **ISO-8601 Fractional Dates**: `1042-04-12` (fractional decimal year).

---

## 4. CLI Usage Reference

### 4.1 Running Diagnostics
```bash
# Audit World Bible integrity
arcanum doctor ~/Universes/Eldoria/00-World-Bible/

# Cross-validate World Bible against manuscript scenes
arcanum doctor ~/Universes/Eldoria/00-World-Bible/ -m ~/Manuscripts/Novel/

# Accelerate audit using fast mtime-keyed caching
arcanum doctor ~/Universes/Eldoria/00-World-Bible/ --fast

# Output machine-readable JSON report for CI/CD gates
arcanum doctor ~/Universes/Eldoria/00-World-Bible/ --json
```

### 4.2 CLI Options

| Flag | Parameter | Default | Description |
| :--- | :--- | :--- | :--- |
| `world_dir` | `DIRECTORY` | `$WORLD_DIR` | Path to Obsidian World Bible directory. |
| `-m`, `--manuscript` | `DIRECTORY` | `None` | Manuscript directory to cross-reference for entity drift (`WLD-108`). |
| `--fast` | | `false` | Enable mtime-keyed in-memory caching for large vaults. |
| `--json` | | `false` | Emit structured JSON findings report to stdout. |

---

## 5. Architectural Invariants

- **Zero-Pip Guarantee**: Powered by Python standard library (`re`, `json`, `os`, `sys`, `pathlib`).
- **Memory-Safe Capping**: Reads capped at 2 MB per note to prevent runaway memory usage on corrupt binary files.
- **Deterministic Validation**: Identical vault contents produce byte-for-byte identical findings.
