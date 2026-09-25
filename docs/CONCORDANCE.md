# Ars Arcanum Concordance & Back-Matter Index Generator (`docs/CONCORDANCE.md`)
> **Epic Worldbuilding & Terminology Concordance Engine (GEN-104)** | Release v3.6.0

---

## 1. Overview & Architectural Mission

The **Concordance Engine** (`arcanum concordance` / `scripts/lib/concordance.py`) automates the synthesis of publication-ready glossaries, character indices (*Dramatis Personae*), faction registries, relic catalogs, bestiaries, and linguistic lexicons for speculative fiction series.

In multi-volume fantasy and science fiction, lore files live inside the sovereign `World/` directory tree across designated subdirectories:
- `Characters/` — Personages, aliases, honorifics, and origins.
- `Factions/` — Guilds, empires, religious orders, and secret societies.
- `Artifacts/` — Relics, superweapons, magical apparatus, and technology.
- `Creatures/` — Bestiary entries, monsters, fauna, and chimeras.
- `Magic-Technology/` — Spellcraft schools, thaumaturgical laws, and propulsion grids.
- `Languages/` — Conlang glossaries, etymologies, and colloquial phrases.

The Concordance Engine cross-references all universe lore entities against the manuscript chapter texts to compile a structured, alphabetized, and back-matter-compliant index with page-ready chapter cross-references.

---

## 2. Directory Layout & Lore Schema

Lore entries are standard markdown files with structured YAML frontmatter:

```markdown
---
name: "Dawnstrider"
type: "Relic"
category: "Solar Artifact"
description: "A blade forged from collapsed solarite crystal, attuned to the Bloodline of Theron."
aliases:
  - "The Sun-Cleaver"
  - "Blade of the Dawn"
first_appearance: "Book-01/01_Chapter_01.md"
---

# Dawnstrider

Forged in the Third Age by the Sun-Smiths of Elyria...
```

### Supported Lore Domains
| Dossier Directory | Domain | Concordance Section Heading |
| :--- | :--- | :--- |
| `World/Characters/` | Dramatis Personae | `### Dramatis Personae` |
| `World/Factions/` | Factions & Organizations | `### Factions & Organizations` |
| `World/Artifacts/` | Relics & Artifacts | `### Relics & Artifacts` |
| `World/Creatures/` | Bestiary & Fauna | `### Bestiary & Creatures` |
| `World/Magic-Technology/` | Magic Systems & Tech | `### Magic & Technology` |
| `World/Languages/` | Lexicon & Conlang | `### Lexicons & Conlang` |

---

## 3. CLI Invocation & Options

```bash
# Generate back-matter concordance for all volumes in a manuscript
arcanum concordance ~/Manuscripts/Solar-Saga/World ~/Manuscripts/Solar-Saga/Manuscript

# Write generated concordance to 04_Back_Matter/Concordance.md
arcanum concordance ~/Manuscripts/Solar-Saga/World ~/Manuscripts/Solar-Saga/Manuscript --write

# Output structured JSON summary
arcanum concordance ~/Manuscripts/Solar-Saga/World ~/Manuscripts/Solar-Saga/Manuscript --json

# Filter to specific domain (e.g. Characters only)
arcanum concordance ~/Manuscripts/Solar-Saga/World ~/Manuscripts/Solar-Saga/Manuscript --characters-only
```

---

## 4. Back-Matter Output Formatting

When generated with `--write`, the engine updates or creates `04_Back_Matter/Concordance.md` in each volume:

```markdown
# Concordance & Lore Index

## Dramatis Personae

- **Aeloria of Sunfall**: Crown Princess of the Elyrian Reach; wields the Sun-Cleaver (*Appears in: Ch. 1, Ch. 4, Ch. 12*).
- **Master Theron**: Archmage of the High Scriptorium; mentor to Aeloria (*Appears in: Ch. 1, Ch. 2, Ch. 7*).

## Relics & Artifacts

- **Dawnstrider**: A blade forged from collapsed solarite crystal (*Appears in: Ch. 1, Ch. 12*).
```

---

## 5. Offline Integrity & Invariants
- **Zero-Pip Guarantee**: Standard library string matching, regex, and YAML parsing.
- **Atomic POSIX/Windows Writes**: Uses `atomic_write()` to guarantee no corrupted half-written indexes.
- **Idempotency**: Re-running `arcanum concordance --write` cleanly replaces the generated back-matter section without touching authorial narrative files.
