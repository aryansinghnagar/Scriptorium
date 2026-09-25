# Ars Arcanum Stylistics, Dialogue Mechanics & Readability Rhythm Guide (`docs/STYLISTICS.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Stylistics Engine** (`scripts/lib/stylistics.py`) is an offline prose linter, dialogue mechanics auditor, word echo detector, and readability rhythm analyzer.

Every novelist battles subtle stylistic traps during revision:
1. **Melodramatic Dialogue Tags & Said-Bookisms**: Relying on overwritten dialogue tags ("bellowed", "opined", "hissed") instead of strong action beats.
2. **Adverb Crutches**: Modifying basic dialogue tags with weak adverbs ("said angrily", "whispered quietly").
3. **Word Echoes**: Unintentionally repeating distinctive nouns or verbs within a tight 100–300 word window.
4. **Cadence Monotony & Staccato Bursts**: Prose lacking rhythmic variety, either through strings of identical-length sentences or excessive staccato fragments.

---

## 2. Dialogue Mechanics & Prose Formatting (`PRO-101`)

The engine classifies dialogue quotes and scans for common mechanical errors:

### 2.1 Overwrought Said-Bookisms
Flags dramatic, unnatural dialogue verbs:
- *Examples*: `ejaculated`, `opined`, `bellowed`, `pontificated`, `hissed`, `sneered`, `intoned`, `vociferated`, `averred`.
- *Recommendation*: Replace with neutral `"said"`, `"asked"`, or an evocative action beat.

### 2.2 Adverb-Heavy Dialogue Tags
Flags tags pairing verbs with `-ly` adverbs:
- *Examples*: `said angrily`, `whispered quietly`, `replied fiercely`.
- *Recommendation*: Let the spoken dialogue or character action convey the emotion.

### 2.3 Punctuation & Capitalization Linter
- **Period Before Tag**: `"Hello." said John.` $\to$ Flags improper period; recommends `"Hello," said John.`
- **Capitalized Pronoun Tag**: `"Hello," He said.` $\to$ Flags capitalized pronoun; recommends `"Hello," he said.`

---

## 3. Sliding-Window Word Echoes (`PRO-102`)

The engine identifies lexical repetitions within a configurable sliding window (default: 300 words).
- **Morphological Stemmer**: Utilizes a built-in English stemmer (`_simple_stem`) to match variations like *tremble*, *trembled*, and *trembling*.
- **Stopword Filtering**: Automatically ignores common functional words (pronouns, prepositions, articles).
- **Severity Scoring**:
  - **High**: Repeated within $< 50$ words.
  - **Medium**: Repeated within $50 \text{--} 150$ words.
  - **Low**: Repeated within $150 \text{--} 300$ words.

---

## 4. Readability Rhythm & Sentence Cadence (`PRO-105`)

The engine computes sentence length distributions and standard readability metrics:

### 4.1 Cadence Metrics
- **Mean Sentence Length (ASL)**: Words per sentence.
- **Cadence Variance & Standard Deviation ($\sigma$)**:
  - If $\sigma < 3.5$ across $\ge 10$ sentences, a **Monotone Cadence Alert** is issued.
- **Staccato Clusters**: Flags $3+$ consecutive sentences of $\le 6$ words each.

### 4.2 Standard Readability Formulas
- **Flesch Reading Ease**:
  $$\text{FRE} = 206.835 - 1.015 \left(\frac{\text{words}}{\text{sentences}}\right) - 84.6 \left(\frac{\text{syllables}}{\text{words}}\right)$$
- **Flesch-Kincaid Grade Level**:
  $$\text{FKGL} = 0.39 \left(\frac{\text{words}}{\text{sentences}}\right) + 11.8 \left(\frac{\text{syllables}}{\text{words}}\right) - 15.59$$
- **Gunning Fog Index**:
  $$\text{Fog} = 0.4 \left[ \left(\frac{\text{words}}{\text{sentences}}\right) + 100 \left(\frac{\text{complex words}}{\text{words}}\right) \right]$$
- **Coleman-Liau Index**:
  $$\text{CLI} = 0.0588 L - 0.296 S - 15.8$$

---

## 5. Command-Line Interface (CLI)

```bash
# Scan a single scene or entire manuscript directory
arcanum stylistics [TARGET]

# Export standalone offline HTML report with SVG sentence length histogram
arcanum stylistics [TARGET] --html stylistics_report.html

# Output JSON diagnostics
arcanum stylistics [TARGET] --json
```

---

## 6. Security & Offline Guarantee

The HTML report generates interactive histograms and word echo tables with strict Content Security Policies:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```
Operates 100% offline with zero external pip dependencies.
