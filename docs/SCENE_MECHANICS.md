# SCENE_MECHANICS — Scene Mechanics & MRU Analyzer

> **Module**: `scripts/lib/scene_mechanics.py`  
> **CLI Command**: `arcanum scene`  
> **Purpose**: Analyzes manuscript scenes for structural integrity using the Motivation-Reaction Unit (MRU) framework and the Scene/Sequel dichotomy. Detects inverted MRU sequences, missing goal/disaster beats, and classifies scenes as Proactive or Reactive.

---

## Table of Contents

1. [Overview](#overview)
2. [The MRU Framework](#the-mru-framework)
3. [Scene vs. Sequel](#scene-vs-sequel)
4. [CLI Usage](#cli-usage)
5. [Key API Reference](#key-api-reference)
6. [MRU Classification Logic](#mru-classification-logic)
7. [Diagnostic Codes](#diagnostic-codes)
8. [Behavioral Notes](#behavioral-notes)
9. [Example Workflow](#example-workflow)

---

## Overview

The `scene_mechanics` module is the **craft technique auditor** of the Ars Arcanum engine. It applies the Motivation-Reaction Unit (MRU) model — a sentence-level fiction craft principle — to detect prose ordering problems that break narrative momentum.

The MRU principle, formalized in genre fiction craft theory, states that a character's reaction to a stimulus must unfold in a biologically realistic sequence:

```
Stimulus → Visceral Reflex → Emotional Response → Cognitive Thought → Action/Dialogue
```

Violations — such as a character *thinking* before their body reacts, or speaking before the stimulus has registered — create subtle but persistent immersion breaks. The analyzer catches these inversions automatically.

At the scene level, the module also classifies each scene as a **Proactive Scene** (goal-driven, external action) or **Reactive Sequel** (internal processing, emotional integration), and checks for the presence of goal and disaster beats.

---

## The MRU Framework

### Ideal Reaction Order

| Step | MRU Phase | Example |
|---|---|---|
| 1 | **Action/Stimulus** | *The arrow struck the wall beside her head.* |
| 2 | **Visceral Reflex** | *Her heart lurched. Her breath stopped.* |
| 3 | **Emotional Response** | *Fear flooded her chest.* |
| 4 | **Cognitive Thought** | *She realized she had only one exit.* |
| 5 | **Action/Dialogue** | *"Run!" she screamed, bolting for the door.* |

Writing any step **before** an earlier step is an **inverted MRU** — a prose flaw. The most common inversion is placing Cognitive Thought before Visceral Reflex (the character has already processed the stimulus before their body has reacted).

### Inverted MRU Flaw Trigger

The analyzer flags a sequence as an **inverted MRU** when either:

- `Cognitive Thought` immediately precedes `Visceral Reflex` in a sentence pair, **or**
- `Action/Dialogue` immediately precedes `Visceral Reflex` in a sentence pair.

This catches the two most common prose-order violations without producing excessive false positives on normal prose.

---

## Scene vs. Sequel

Every narrative unit is classified as one of two structural types:

| Type | Definition | Dominant Sentence Types |
|---|---|---|
| **Proactive Scene** | Goal → Conflict → Disaster. External, action-driven. | Action/Stimulus, Action/Dialogue |
| **Reactive Sequel** | Reaction → Dilemma → Decision. Internal, emotion-driven. | Visceral Reflex, Emotional Response, Cognitive Thought |

The classifier computes:

```
external_weight = count(Action/Stimulus) + count(Action/Dialogue)
internal_weight = count(Visceral Reflex) + count(Emotional Response) + count(Cognitive Thought)
```

If `external_weight >= internal_weight` → **Proactive Scene**  
If `internal_weight > external_weight` → **Reactive Sequel**

---

## CLI Usage

```
arcanum scene [MANUSCRIPT] [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `MANUSCRIPT` | Path to the manuscript directory or a single `.md` scene file |

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--html OUT` | path | *(none)* | Generate an HTML report at the specified path |
| `--json` | flag | off | Output raw JSON result |

### Quick Examples

```powershell
# Analyze a full manuscript directory
arcanum scene Manuscript/

# Analyze a single scene file with HTML report
arcanum scene Manuscript/Act_2/Chapter_07.md --html reports/ch07_mru.html

# JSON output for scripting
arcanum scene Manuscript/ --json > scene_analysis.json
```

---

## Key API Reference

### `classify_sentence_mru`

```python
classify_sentence_mru(sentence: str) -> str
```

Classifies a single sentence into one of five MRU phase categories.

**Return values (exclusive):**

| Return Value | Description |
|---|---|
| `"Visceral Reflex"` | Body-level involuntary reaction |
| `"Action/Dialogue"` | Spoken dialogue or deliberate physical action |
| `"Emotional Response"` | Named emotion experienced by the POV character |
| `"Cognitive Thought"` | Internal reasoning, realization, or decision |
| `"Action/Stimulus"` | External event or physical description (default) |

Classification is applied in priority order: Visceral Reflex is checked first, then Dialogue, then Emotion, then Thought, with Action/Stimulus as the fallback default.

---

### `analyze_scene_text`

```python
analyze_scene_text(text: str, scene_title: str = "Scene") -> dict
```

Analyzes the full text of a single scene.

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `title` | `str` | Scene title passed via `scene_title` |
| `total_sentences` | `int` | Total sentences analyzed |
| `scene_type` | `str` | `"Proactive Scene"` or `"Reactive Sequel"` |
| `has_goal` | `bool` | True if goal-indicator keywords detected |
| `has_disaster` | `bool` | True if disaster-indicator keywords detected |
| `phase_distribution` | `dict[str, int]` | Count of each MRU phase across all sentences |
| `mru_flaws` | `list[dict]` | List of inverted MRU flaw records |
| `mru_sequence_sample` | `list[str]` | MRU phase label for each sentence (first 50) |

Each flaw record in `mru_flaws` contains:

| Field | Description |
|---|---|
| `sentence_index` | 0-based index of the triggering sentence |
| `phase_a` | Phase of the preceding sentence |
| `phase_b` | Phase of the offending sentence (Visceral Reflex) |
| `snippet` | First 80 characters of the offending sentence |

---

### `scan_manuscript_scenes`

```python
scan_manuscript_scenes(target_path: str | Path) -> dict
```

Scans all `.md` files in `target_path` recursively, treating each file as a scene, and aggregates the analysis.

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `target` | `str` | Resolved path of the scanned directory |
| `total_scenes` | `int` | Number of `.md` files analyzed |
| `proactive_scenes` | `int` | Count of Proactive Scenes |
| `reactive_sequels` | `int` | Count of Reactive Sequels |
| `total_mru_flaws` | `int` | Aggregate MRU flaw count across all scenes |
| `scenes` | `list[dict]` | Per-scene result dicts (same schema as `analyze_scene_text`) |

---

### `generate_scene_mechanics_html`

```python
generate_scene_mechanics_html(report: dict, output_path: str | Path) -> Path
```

Generates an HTML visualization of the scan report. The report must be the dict returned by `scan_manuscript_scenes`.

---

## MRU Classification Logic

Classification is keyword-based and applied sentence by sentence. Checks are evaluated in the following priority order:

### 1. Visceral Reflex (checked first)

Sentence contains any of the following words/phrases:

```
pulse, heart, breath, gasp, flinch, shiver, adrenaline,
spine, throat, stomach, goosebump, sweat, trembl, nausea, bile
```

### 2. Action/Dialogue (checked second)

Sentence contains quoted speech using `"..."` or `'...'` delimiters.

### 3. Emotional Response (checked third)

Sentence contains any of the following:

```
fear, dread, terror, rage, fury, grief, panic, anguish,
despair, horror, shame, guilt, joy, elation, sorrow
```

### 4. Cognitive Thought (checked fourth)

Sentence contains any of the following, **or** begins with `"he thought"` / `"she thought"` / `"they thought"`:

```
thought, realized, pondered, decided, understood, knew, considered,
wondered, remembered, figured, concluded, assumed, believed
```

### 5. Action/Stimulus (default fallback)

Any sentence not matching the above is classified as Action/Stimulus.

> [!NOTE]
> Classification is **case-insensitive** and uses substring matching, not whole-word matching. The word `"breathless"` will trigger Visceral Reflex because it contains `"breath"`. Design your prose accordingly, and use the whitelist if needed.

---

## Diagnostic Codes

| Code | Severity | Condition | Resolution |
|---|---|---|---|
| `MRU-001` | WARNING | Inverted MRU: Cognitive Thought precedes Visceral Reflex | Reorder sentences so the body reacts before the mind processes |
| `MRU-002` | WARNING | Inverted MRU: Action/Dialogue precedes Visceral Reflex | Let the character's body react before they speak or act |
| `MRU-010` | INFO | Scene has no detectable goal keywords | Ensure the POV character has a stated objective |
| `MRU-011` | INFO | Scene has no detectable disaster keywords | Consider whether the scene ends in a meaningful setback |
| `MRU-020` | INFO | Scene is overwhelmingly one-phase type (> 80%) | Variety in sentence types produces more dynamic prose |

---

## Behavioral Notes

- **Sentence splitting**: Text is split on `.`, `!`, and `?` followed by whitespace. Abbreviations (e.g., "Dr.", "U.S.") may cause spurious splits. This is a known limitation of the regex-based splitter.
- **Keyword false positives**: Because classification uses substring matching, words like `"breathless"`, `"thoughtful"`, or `"fearlessly"` will trigger their respective categories. Review flagged sentences in context before revising.
- **Goal detection keywords**: `must`, `need to`, `had to`, `wanted`, `plan`, `objective`, `mission` — present anywhere in the scene text.
- **Disaster detection keywords**: `suddenly`, `too late`, `failed`, `trap`, `ambush`, `explosion`, `betrayal` — present anywhere in the scene text.
- **File filtering**: When scanning a directory, only `*.md` files are processed. Files beginning with `.` are skipped. Subdirectory depth is unlimited.
- **Encoding**: All files are read as UTF-8. Files with different encodings may cause decode errors.
- **MRU sequence sample**: Only the first 50 sentences are included in `mru_sequence_sample` to keep JSON output manageable for long scenes.
- **Scene type balance**: A healthy manuscript typically alternates Proactive Scenes with Reactive Sequels in a roughly 60/40 ratio. An entirely proactive manuscript may feel relentless; an entirely reactive one may feel passive.

---

## Example Workflow

### Workflow 1: Full Manuscript Scan

```powershell
arcanum scene Manuscript/ --html reports/mru_report.html
```

Opens `reports/mru_report.html` in a browser — color-coded per-scene breakdown showing phase distribution bars, flaw highlights, and goal/disaster badges.

### Workflow 2: Single File Triage

```powershell
arcanum scene "Manuscript/Act_1/Chapter_03_The_Ambush.md" --json
```

**Sample JSON output (abridged):**
```json
{
  "title": "Chapter_03_The_Ambush",
  "total_sentences": 84,
  "scene_type": "Proactive Scene",
  "has_goal": true,
  "has_disaster": true,
  "phase_distribution": {
    "Action/Stimulus": 34,
    "Visceral Reflex": 12,
    "Emotional Response": 9,
    "Cognitive Thought": 18,
    "Action/Dialogue": 11
  },
  "mru_flaws": [
    {
      "sentence_index": 22,
      "phase_a": "Cognitive Thought",
      "phase_b": "Visceral Reflex",
      "snippet": "Her stomach dropped when she realised the gate was sealed."
    }
  ]
}
```

### Workflow 3: Python API Integration

```python
from scripts.lib.scene_mechanics import (
    analyze_scene_text,
    scan_manuscript_scenes,
    generate_scene_mechanics_html,
)

# Analyze a single scene
with open("Manuscript/Act_1/Chapter_03.md", encoding="utf-8") as f:
    text = f.read()

result = analyze_scene_text(text, scene_title="Chapter 3 — The Ambush")
print(f"Scene type: {result['scene_type']}")
print(f"MRU flaws: {len(result['mru_flaws'])}")
for flaw in result["mru_flaws"]:
    print(f"  Line ~{flaw['sentence_index']}: {flaw['phase_a']} → {flaw['phase_b']}")
    print(f"  Snippet: {flaw['snippet']}")

# Full manuscript scan + HTML report
report = scan_manuscript_scenes("Manuscript/")
generate_scene_mechanics_html(report, "reports/mru.html")
print(f"Total MRU flaws across manuscript: {report['total_mru_flaws']}")
```

### Workflow 4: Revision Loop

1. Run `arcanum scene Manuscript/ --html reports/mru.html`
2. Open the HTML report. Identify scenes with the most MRU flaws.
3. Open the flagged scene file. Locate each `MRU-001` or `MRU-002` flaw by sentence index.
4. Revise: move Visceral Reflex sentences immediately after the triggering Stimulus.
5. Re-run `arcanum scene` to confirm flaw count has decreased.

---

*Part of the **Ars Arcanum Scriptorium** craft engine. For platform-wide CLI reference, see `docs/CLI_REFERENCE.md`.*
