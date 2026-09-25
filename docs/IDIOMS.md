# IDIOMS — Earth Idiom & Immersion-Breaking Eponym Linter

> **Module**: `scripts/lib/idioms.py`  
> **CLI Command**: `arcanum idioms`  
> **Purpose**: Automated manuscript prose linter that scans for immersion-breaking Earth-specific eponyms, mythological/scriptural references, and biological cliches in secondary-world speculative fiction.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Usage](#cli-usage)
3. [Immersion Categories & Diagnostic Codes](#immersion-categories--diagnostic-codes)
4. [Built-in Detection Dictionary](#built-in-detection-dictionary)
5. [Custom Configuration Schema (`idioms.json`)](#custom-configuration-schema-idiomsjson)
6. [Whitelist Filtering](#whitelist-filtering)
7. [Standalone HTML Report](#standalone-html-report)
8. [Example Workflow](#example-workflow)

---

## Overview

When writing secondary-world fantasy or speculative fiction set on alien worlds, accidental inclusion of Earth-specific idioms, historical namesakes (eponyms), and terrestrial animal metaphors can shatter reader immersion. 

The `idioms` linter acts as an automated craft safety net:
- Scans all manuscript markdown chapters (`*.md`), ignoring non-prose metadata tags (`@pov:`, `@time:`) and YAML frontmatter.
- Flags Earth historical personages, Greek/Roman mythology, biblical idioms, and terrestrial biological idioms.
- Provides real-world historical origins alongside contextual in-world replacement suggestions.
- Supports granular custom dictionaries (`configs/idioms.json`) and run-time whitelisting for intentional stylistic choices.

---

## CLI Usage

```bash
arcanum idioms [MANUSCRIPT_DIR] [OPTIONS]
```

### Options

| Flag | Type | Description |
|---|---|---|
| `manuscript` / `-m PATH` | path | Path to the manuscript directory (defaults to auto-discovered manuscript) |
| `--config PATH` | path | Path to custom `idioms.json` configuration file |
| `--whitelist WORD [WORD ...]` | list | List of words or phrases to whitelist for this run |
| `--json` | flag | Output machine-readable JSON results |
| `--html PATH` | path | Export standalone interactive HTML report |

---

## Immersion Categories & Diagnostic Codes

| Code | Category | Description & Examples |
|---|---|---|
| `IDM-101` | **Earth-Specific Eponym** | Terms derived from real Earth historical figures or places.<br/>*Examples*: `pyrrhic`, `draconian`, `machiavellian`, `achilles heel`, `gordian knot`, `trojan horse`, `stockholm syndrome`, `sandwich`, `diesel`, `boycott`, `caesarean`. |
| `IDM-102` | **Earth Mythological / Scriptural** | References rooted in Earth-specific mythology, religion, or historical events.<br/>*Examples*: `by jove`, `devil's advocate`, `crossing the rubicon`, `pandora's box`, `good samaritan`, `damocles`, `midas touch`, `holy grail`. |
| `IDM-103` | **Flora / Fauna De-Immersion Cliché** | Metaphors and idioms referencing Earth-specific biological species or practices.<br/>*Examples*: `canary in a coal mine`, `elephant in the room`, `red herring`, `scapegoat`, `crocodile tears`, `barking up the wrong tree`. |

---

## Built-in Detection Dictionary

The engine includes a curated standard dictionary of over 30 pervasive Earth-specific terms:

### Eponyms (`IDM-101`)
- **Achilles' heel** *(Origin: Greek Hero Achilles)* $\to$ *vulnerable spot / mortal weakness*
- **Pyrrhic** *(Origin: King Pyrrhus of Epirus)* $\to$ *ruinous victory / costly triumph*
- **Draconian** *(Origin: Athenian Lawgiver Draco)* $\to$ *harsh / ruthless / merciless*
- **Spartan** *(Origin: City-state of Sparta)* $\to$ *austere / disciplined / bare*
- **Machiavellian** *(Origin: Niccolò Machiavelli)* $\to$ *cunning / scheming / duplicitous*
- **Gordian knot** *(Origin: King Gordias of Phrygia)* $\to$ *insoluble tangle / intricate knot*
- **Trojan horse** *(Origin: Trojan War / Homer)* $\to$ *covert infiltrator / subterfuge gift*
- **Sisyphean** *(Origin: Myth of Sisyphus)* $\to$ *futile labor / endless toil*
- **Boycott** *(Origin: Captain Charles Boycott)* $\to$ *embargo / shun / ostracize*
- **Sandwich** *(Origin: 4th Earl of Sandwich)* $\to$ *filled loaf / layered bread*
- **Diesel** *(Origin: Rudolf Diesel)* $\to$ *heavy fuel / compression engine*

### Mythological & Religious (`IDM-102`)
- **Devil's advocate** *(Origin: Catholic Canon Law)* $\to$ *contrarian stance / opposing argument*
- **Crossing the Rubicon** *(Origin: Julius Caesar 49 BCE)* $\to$ *point of no return*
- **Pandora's box** *(Origin: Greek Hesiod Myth)* $\to$ *forbidden casket / unleashed curse*
- **Good Samaritan** *(Origin: Gospel of Luke)* $\to$ *kind stranger / charitable traveler*
- **Sword of Damocles** *(Origin: Sicilian Anecdote)* $\to$ *impending doom / hanging blade*
- **Midas touch** *(Origin: King Midas)* $\to$ *golden touch / effortless wealth*
- **Holy Grail** *(Origin: Arthurian Legend)* $\to$ *ultimate prize / supreme artifact*

### Biological Clichés (`IDM-103`)
- **Canary in a coal mine** *(Origin: British Mining Practice)* $\to$ *early warning sign / harbinger*
- **Elephant in the room** *(Origin: Earth Mega-Fauna Idiom)* $\to$ *unspoken truth / unavoidable reality*
- **Red herring** *(Origin: Cured Fish Scent Metaphor)* $\to$ *false trail / misleading decoy*
- **Crocodile tears** *(Origin: Medieval Bestiary Myth)* $\to$ *feigned sorrow / false tears*
- **Scapegoat** *(Origin: Leviticus Day of Atonement)* $\to$ *fall guy / blamed innocent*

---

## Custom Configuration Schema (`idioms.json`)

You can override or extend the dictionary by placing an `idioms.json` file in `configs/idioms.json` or passing `--config`:

```json
{
  "eponyms": {
    "marathon": {
      "origin": "Battle of Marathon 490 BCE",
      "suggestion": "long-distance trek / test of endurance"
    }
  },
  "mythological_religious": {
    "mecca": {
      "origin": "Islamic Holy City",
      "suggestion": "pilgrimage site / cultural epicenter"
    }
  },
  "flora_fauna_cliches": {
    "black sheep": {
      "origin": "Earth Animal Husbandry",
      "suggestion": "outcast / family pariah"
    }
  },
  "whitelist": [
    "sandwich",
    "diesel"
  ]
}
```

---

## Whitelist Filtering

If your setting intentionally uses certain terms (e.g., dieselpunk fantasy using "diesel", or a portal-fantasy protagonist speaking in modern Earth idioms), you can whitelist them:

1. **In `configs/idioms.json`**:
   ```json
   {
     "whitelist": ["diesel", "sandwich", "pyrrhic"]
   }
   ```
2. **Via CLI argument**:
   ```bash
   arcanum idioms Cosmos/Manuscript --whitelist diesel sandwich
   ```

Whitelisted terms are completely ignored by the scanner and will not produce findings.

---

## Standalone HTML Report

The `--html` option generates a zero-dependency HTML report:
- Full Content-Security-Policy compliance (`default-src 'none'`).
- Grouped view by category (Eponyms, Mythological, Biological).
- Chapter and line number locations with highlighted prose snippets and suggested replacements.

---

## Example Workflow

```bash
# 1. Audit entire manuscript for immersion-breaking idioms
arcanum idioms Cosmos/Manuscript

# 2. Run audit with custom whitelist and output HTML report
arcanum idioms Cosmos/Manuscript --whitelist sandwich --html reports/idioms_audit.html

# 3. Export JSON report for CI/CD automated linting
arcanum idioms Cosmos/Manuscript --json > build/idioms.json
```
