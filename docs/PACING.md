# Ars Arcanum Narrative Pacing, POV Balance & Tension Arc Guide (`docs/PACING.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Pacing Engine** (`scripts/lib/pacing.py`) is an offline narrative analytics suite designed for speculative fiction novelists and story architects.

Maintaining proper pacing across a 100,000+ word manuscript is notoriously difficult. Writers often face:
1. **Pacing Sags & Exposition Traps**: Long consecutive stretches of monologue or lore dumping with low conflict and static syntax.
2. **POV Starvation**: Introducing multiple viewpoint protagonists only to leave one major character absent for 5–10 chapters.
3. **Stalled Subplots**: Subplots introduced early that disappear until the final climax without intermediate progression.
4. **Flat Tension Arcs**: Manuscripts lacking peaks and valleys, denying readers dynamic emotional release.

---

## 2. Pacing & Prose Rhythm Metrics

The engine scans chapter prose and calculates key syntactic and density dimensions:

### 2.1 Density Ratios
- **Dialogue Ratio**: Proportion of words contained within spoken dialogue quotes (`"..."` or `“...”`).
- **Exposition Ratio**: Proportion of descriptive or reflective prose, weighted by sentence length and lack of dialogue.
- **Action Ratio**: Proportion of kinetic, fast-paced prose, characterized by staccato sentences ($< 8$ words) and conflict verbs.

### 2.2 Sentence Length Cadence
- **Mean Sentence Length**: Average words per sentence.
- **Sentence Length Variance & Standard Deviation**: High variance indicates rhythmic, musical prose; low variance indicates monotonous cadence.

---

## 3. POV Distribution & Screen-Time Balance

Authors tag viewpoint characters at the top of scene notes using `@pov: CharacterName`:

```markdown
# Chapter 1: The Whispering Gallery
@pov: Elena
@thread: Royal-Conspiracy
@tension: 6.5

Elena crept along the marble corridor, holding her breath as the guards passed.
```

### POV Starvation Detection
The engine audits the distance between successive appearances of each viewpoint character:
- If a major character ($> 10\%$ total manuscript word count) is absent for **more than 3 consecutive chapters**, the engine flags a **POV Starvation Warning**.

---

## 4. Subplot Thread Momentum Matrix

Authors track secondary plots using `@thread: ThreadName` or `@plot: PlotName`:
- The engine maps which chapters advance each thread.
- Identifies dormant or abandoned threads that have not been touched for multiple acts.

---

## 5. Narrative Tension Arc Curve Modeling

The composite tension index ($0 \text{ to } 100$) per chapter is computed from:
1. **Conflict Keyword Density**: Frequency of battle, peril, stealth, emotional dread, and urgency terms.
2. **Syntactic Velocity**: Ratio of ultra-short sentences ($< 8$ words) vs. compound sentences ($> 24$ words).
3. **Dialogue Pacing**: Sharp, back-and-forth verbal confrontations increase tension.
4. **Directives & Climax**:
   - Explicit override: `@tension: 8.5` sets tension to $85.0$.
   - Climax tag: `@climax: true` or `@plot: climax` adds $+25.0$ tension boost.

---

## 6. Command-Line Interface (CLI)

```bash
# Scan full manuscript pacing and output terminal summary
arcanum pacing [MANUSCRIPT]

# Filter analysis to a specific book volume in a series
arcanum pacing [MANUSCRIPT] --book Book-01

# Export standalone offline HTML report with SVG tension charts
arcanum pacing [MANUSCRIPT] --html pacing_report.html

# Output raw JSON metrics for pipeline automation
arcanum pacing [MANUSCRIPT] --json
```

---

## 7. Security & Offline Guarantee

Generated HTML reports are self-contained with offline Content Security Policies:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```
