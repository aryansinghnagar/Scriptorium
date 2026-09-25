# Sensory Palette — Author Guide

> **Command:** `arcanum senses`
> **Module:** `scripts/lib/senses.py`
> **Phase:** 13 — The Sovereign Craft Deepening

---

## Overview

The **6D Sensory Palette Engine** measures how richly a manuscript engages each of the six human sensory dimensions. Where most style checkers focus on word-count or readability, Ars Arcanum models *perceptual immersion*: does this scene ground the reader in felt, heard, smelled, tasted, and proprioceptive reality, or does it float in a visualonly abstraction?

The engine scans every scene file (`*.md`) in the Manuscript directory, tallies lexicon-matched sensory anchors per dimension, and reports scene-level and manuscript-level distributions. Scenes that fall below minimum thresholds for non-visual grounding trigger diagnostic findings.

---

## 6-Dimension Reference Table

| # | Dimension | Sense | Example Lexicon Words |
|---|-----------|-------|-----------------------|
| 1 | **Visual** | Sight | `crimson`, `azure`, `emerald`, `golden`, `shadow`, `glare`, `gloom`, `brilliant`, `shimmer`, `scarlet`, `luminous`, `vivid`, `murky`, `dazzling` |
| 2 | **Auditory** | Hearing | `roar`, `whisper`, `clang`, `echo`, `silence`, `deafening`, `hiss`, `murmur`, `rumble`, `shriek`, `cacophony`, `muffled`, `shrill`, `clamor` |
| 3 | **Olfactory** | Smell | `pungent`, `aroma`, `sulfur`, `fragrant`, `stench`, `musty`, `smoky`, `acrid`, `musk`, `fetid`, `incense`, `rancid`, `reek`, `putrid` |
| 4 | **Gustatory** | Taste | `bitter`, `sweet`, `sour`, `metallic`, `savory`, `acrid`, `tangy`, `salty`, `copper`, `tart`, `honey`, `astringent`, `cloying`, `briny` |
| 5 | **Tactile / Thermal** | Touch & Temperature | `freezing`, `rough`, `silken`, `coarse`, `blazing`, `icy`, `smooth`, `searing`, `damp`, `clammy`, `prickle`, `frost`, `gritty`, `velvety` |
| 6 | **Kinesthetic / Vestibular** | Body & Balance | `vertigo`, `stumble`, `momentum`, `lurch`, `recoil`, `sway`, `pulse`, `tremor`, `stagger`, `tingling`, `spinning`, `heaviness`, `aching`, `dizzy` |

> [!NOTE]
> The lexicon is intentionally author-style-agnostic: it matches common literary sensory anchors rather than highly technical or domain-specific vocabulary. If your genre uses specialist terms (e.g., combat proprioception cues), consider extending the lexicon in `senses.py`.

---

## Diagnostic Codes

### SNS-101 — White Room Syndrome

**Trigger:** A scene with more than **150 words** has fewer than **2 non-visual sensory anchors** (combined auditory + olfactory + gustatory + tactile_thermal + kinesthetic_vestibular).

**Interpretation:** The scene describes a space in visual terms only — dimensions, colour, light — without grounding the reader in texture, temperature, sound, scent, or bodily sensation. Readers may feel emotionally detached or fail to embody the POV character.

**Severity:** `WARNING`

**Remediation:**
- Identify the scene's dominant physical environment (e.g., a forge, a forest, a throne room) and add one or two characteristic non-visual anchors.
- Ask: *What does this space sound like? What does the air smell of? What does the character feel under their feet or fingertips?*
- Even a single anchoring sentence ("The air tasted of iron and old smoke") clears the finding.
- Avoid adding anchors arbitrarily — choose ones that reinforce mood or foreshadow theme.

---

### SNS-102 — Sensory Monotony / Extreme Visual Skew

**Trigger:** A scene with more than **300 words** and at least **5 total sensory anchors** has a visual percentage ≥ **90%**.

**Interpretation:** The prose uses sensory language almost exclusively for visual description. Even if the scene is rich in metaphor and imagery, it neglects the full perceptual register and risks feeling flat or cinematic rather than embodied.

**Severity:** `WARNING`

**Remediation:**
- Audit the scene for opportunities to layer in at least one auditory and one tactile or olfactory anchor per major beat.
- A useful heuristic: for every 100 words of heavily visual prose, insert one anchor from another dimension.
- Be wary of over-correcting by making every paragraph multi-sensory — rhythm and restraint matter.

---

## CLI Usage

```bash
arcanum senses [MANUSCRIPT] [OPTIONS]
```

| Argument / Option | Description |
|---|---|
| `MANUSCRIPT` | Path to manuscript draft directory (optional; auto-discovered if omitted) |
| `-m`, `--manuscript` | Explicit manuscript directory path |
| `--html PATH` | Export a standalone interactive HTML report to `PATH` |
| `--json` | Print machine-readable JSON audit data to stdout |

### Examples

```bash
# Auto-discover manuscript and run audit
arcanum senses

# Explicit manuscript path
arcanum senses ~/Manuscripts/MyNovel

# Export HTML report
arcanum senses ~/Manuscripts/MyNovel --html reports/senses.html

# Machine-readable output for CI pipelines
arcanum senses --json | jq '.findings'

# Analyse a specific chapter directory
arcanum senses ~/Manuscripts/MyNovel/Book-01
```

> [!TIP]
> Run `arcanum senses --json` in CI and fail the build if `findings` is non-empty to enforce a minimum sensory richness standard across your manuscript.

---

## Understanding the Output

### Terminal Output

```
=== Ars Arcanum 6-Dimensional Sensory Palette ===
Manuscript: MyNovel | Words: 87,432 | Sensory Anchors: 1,204

Sensory Distribution:
  👁️  Visual       :  62.3% (751 occurrences)
  👂 Auditory     :  14.1% (170 occurrences)
  👃 Olfactory    :   8.7% (105 occurrences)
  👅 Gustatory    :   4.2%  (51 occurrences)
  ✋ Tactile/Therm:   7.9%  (95 occurrences)
  🤸 Kinesthetic  :   2.7%  (32 occurrences)

Diagnostic Findings (2):
  ⚠️  [SNS-101] White Room Syndrome: Scene has 312 words but only 1 non-visual sensory anchor ...
     Location: Book-01/02_Act_II/14_Scene.md
```

### HTML Report Sections

1. **Manuscript Sensory Distribution** — Six-column stat grid showing percentage and raw count per dimension across the entire manuscript.
2. **White Room & Sensory Monotony Diagnostics** — Cards for each finding with scene location and remediation hint.
3. **Per-Scene Sensory Palette Breakdown** — Table listing every scene with its per-dimension percentages.

---

## Return Codes

| Code | Meaning |
|---|---|
| `0` | No findings; manuscript passes sensory audit |
| `1` | One or more SNS findings detected |
| `2` | Configuration error (no manuscript directory found) |
