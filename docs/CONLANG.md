# Ars Arcanum — Conlang Phonotactics & Historical Sound-Change Engine Guide
> **Engine**: `scripts/lib/conlang.py` | **CLI**: `arcanum conlang generate`, `arcanum conlang mutate`, `arcanum conlang lexicon`

---

## 1. Overview & Purpose

The **Conlang Phonotactics, Lexicography & Sound-Change Engine** provides fantasy authors and worldbuilders with tools to design and evolve constructed languages (conlangs). It generates phonotactically valid words, names, and toponyms based on explicit phonetic inventories and syllable templates, applies historical sound laws ($A \to B / X\_Y$), and organizes in-world bilingual dictionaries.

### Core Capabilities
- **Phonotactic Word Generation**: Generates names, places, and vocabulary matching target syllable structures (e.g. `CV`, `CVC`, `CCV`, `V`, `VC`) while rejecting forbidden clusters.
- **Historical Sound Shift Law Applier**: Implements standard linguistic sound-change notations (`p > f / V_V`, `k > ch / _[e,i]`, `s > h / #_`, `e > 0 / _#`).
- **Lexicon Parsing & Vocabulary Management**: Scans vocabulary tables directly from Obsidian markdown notes and exports to CSV, Markdown, or JSON.
- **Deterministic Seeding**: Generates reproducible naming sets using `--seed`.

---

## 2. Language Profile Schema (`World/Languages/Solar_Tongue.md`)

```markdown
---
name: "Solar Tongue"
type: language
consonants: [k, l, r, m, n, s, v, th, p, t]
vowels: [a, e, i, o, u]
syllable_structures: ["CV", "CVC"]
forbidden_clusters: ["thk", "sr", "kp"]
stress_rule: "penultimate"
sound_changes:
  - "p > b / V_V"
  - "k > ch / _[e,i]"
  - "e > 0 / _#"
---
# Solar Tongue
The ceremonial language of the Solar Concordat.

## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Aethel* | Noun | /ˈaɪ.θəl/ | Sun King | Royal honorific |
| *Vaelor* | Noun | /ˈvaɪ.lɔːr/ | Shield | Military vow |
| *Solan* | Adj | /ˈsoʊ.læn/ | Luminous | Spiritual blessing |
```

---

## 3. Sound-Change Notation Reference

| Rule Notation | Linguistic Environment | Example Input $\to$ Output |
| :--- | :--- | :--- |
| `p > b / V_V` | Intervocalic voicing (between vowels) | `apata` $\to$ `abata` |
| `k > ch / _[e,i]` | Palatalization before front vowels | `keli` $\to$ `cheli` |
| `s > h / #_` | Debuccalization word-initially | `solas` $\to$ `holas` |
| `e > 0 / _#` | Apocope (word-final vowel loss) | `mate` $\to$ `mat` |
| `p > f / #_V` | Word-initial lenition before vowel | `pater` $\to$ `fater` |
| `p > f / C_#` | Post-consonantal word-final shift | `kasp` $\to$ `kasf` |

---

## 4. CLI Command Reference

### Generate Phonotactically Legal Names & Places
```bash
# Generate 15 character names
arcanum conlang generate "Solar" -w World/ -n 15 -t name

# Generate toponyms (places) with deterministic seed
arcanum conlang generate "Solar" -w World/ -n 10 -t place --seed 42
```

### Apply Historical Sound Changes to Prose or Lexicon
```bash
# Apply sound shifts defined in language note
arcanum conlang mutate "Solar" "pata keli mate" -w World/

# Apply ad-hoc custom sound law
arcanum conlang mutate "Solar" "solas" -w World/ -r "s > h / #_"
```

### Query and Export Lexicon
```bash
# Search dictionary by keyword or translation
arcanum conlang lexicon "Solar" -w World/ -q "shield"

# Export vocabulary table to CSV
arcanum conlang lexicon "Solar" -w World/ --export-csv exports/solar_lexicon.csv
```

---

## 5. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`csv`, `json`, `random`, `re`, `pathlib`).
- **Deterministic**: Given the same seed, phonotactic generator outputs identical vocabulary strings.
- **Offline & Private**: Zero cloud dictionaries or external linguistic APIs.
