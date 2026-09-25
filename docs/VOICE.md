# Ars Arcanum Character Voice Profiler & Dialogue Fingerprint Guide (`docs/VOICE.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Voice Engine** (`scripts/lib/voice.py`) is an offline character dialogue profiler and linguistic fingerprinting tool.

In ensemble speculative fiction, distinct character voices are paramount. When all characters speak with the author's own default cadence, vocabulary, and formality, dialogue feels homogeneous and artificial. The Voice Engine extracts character-attributed dialogue across chapters, computes quantifiable linguistic metrics, and detects **Voice Bleed** (character homogeneity) where distinct characters sound identical.

---

## 2. Dialogue Attribution Formats

The engine automatically parses dialogue from manuscript markdown files using three standard conventions:

### 2.1 Script Format
```markdown
Elena: "We must reach the vault before the eclipse."
Vance: "I don't think that's possible, Elena."
```

### 2.2 Post-Quote Attributions
```markdown
"We must reach the vault before the eclipse," said Elena.
"I don't think that's possible," muttered Vance.
```

### 2.3 Pre-Quote Attributions
```markdown
Elena whispered, "The runes are glowing."
Vance shouted, "Fall back to the archway!"
```

---

## 3. Linguistic Metrics & Voice Fingerprints

For every character with sufficient dialogue, the engine calculates:

| Metric | Code / Label | Description |
| :--- | :--- | :--- |
| **Lexical Richness** | `TTR` | Type-Token Ratio ($\frac{\text{Unique Words}}{\text{Total Words}}$). High TTR indicates an expansive vocabulary. |
| **Mean Utterance Length** | `MUL` | Average word count per dialogue line. Orators have high MUL; taciturn warriors have low MUL. |
| **Utterance Std Deviation** | `MUL StdDev` | Cadence variability. High variance indicates dynamic speech rhythms. |
| **Contraction Usage** | `Contraction Rate` | Percentage of words using contractions (`don't`, `can't`, `gonna`). Distinguishes colloquial vs. formal speech. |
| **Formality Score** | `Formality (0-100)` | Composite score derived from word length, sentence length, and contraction avoidance. |
| **Punctuation Cadence** | `? / ! / ... / —` | Ratios of interrogative, exclamatory, hesitant (ellipsis), and interrupted (em-dash) lines. |
| **Distinctive Lexicon** | `TF-IDF Top Words` | Words favored disproportionately by this character compared to the rest of the cast. |

---

## 4. Voice Bleed & Homogeneity Detection

The engine constructs a normalized 6-dimensional feature vector for each character:
$$\vec{V} = \left[ \text{TTR}, \frac{\text{MUL}}{30}, \frac{\text{ContractionRate}}{20}, \frac{\text{Formality}}{100}, \text{Q\_Ratio}, \text{Ex\_Ratio} \right]$$

It computes pairwise cosine similarity between all character vectors:
$$\text{Similarity}(A, B) = \frac{\vec{V}_A \cdot \vec{V}_B}{\|\vec{V}_A\| \|\vec{V}_B\|}$$

- If $\text{Similarity} \ge 0.92$ between major characters ($> 30$ words each), the engine generates a **Voice Bleed Warning**, recommending the author alter cadence, contractions, or sentence lengths.

---

## 5. Command-Line Interface (CLI)

```bash
# Scan full manuscript character voices and display terminal profiles
arcanum voice [MANUSCRIPT]

# Export standalone offline HTML report with fingerprint cards and similarity matrix
arcanum voice [MANUSCRIPT] --html voice_report.html

# Output JSON data
arcanum voice [MANUSCRIPT] --json
```

---

## 6. Security & Offline Guarantee

The HTML report generates interactive voice cards and an SVG similarity heatmap with strict offline headers:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```
