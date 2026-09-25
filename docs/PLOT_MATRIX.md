# PLOT_MATRIX — Multi-Track Plot Grid & Subplot Matrix

> **Module**: `scripts/lib/plot_matrix.py`  
> **CLI Command**: `arcanum plot-matrix`  
> **Purpose**: Scans manuscript chapters for plot, thread, and arc tags; builds a multi-track plot grid; detects dormant, dangling, and abandoned subplot tracks; and generates an interactive SVG timeline report.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Usage](#cli-usage)
3. [Tag & Frontmatter Reference](#tag--frontmatter-reference)
4. [Key API Reference](#key-api-reference)
5. [Track Health Diagnostics](#track-health-diagnostics)
6. [Behavioral Notes](#behavioral-notes)
7. [Example Workflow](#example-workflow)

---

## Overview

The `plot_matrix` module is the **structural continuity tracker** of the Ars Arcanum engine. Long manuscripts — especially multi-POV epics — suffer from subplot drift: a storyline introduced in Act 1 quietly disappears by Act 2 without resolution. The plot matrix maps every tagged plot thread across all chapters, computes gap lengths, and surfaces threads at risk of being abandoned.

**What it tracks:**

| Track Type | Tag | Description |
|---|---|---|
| `@plot` | Primary plot | The main narrative drive (the quest, the war, the mystery) |
| `@thread` | Subplot / B-story | Secondary storylines involving supporting characters |
| `@arc` | Character arc | A single character's internal transformation journey |

All three track types are treated uniformly by the gap and dangling-track analysis engine.

**Output options:**

- **Console summary** — dormant/dangling warnings printed to stdout
- **JSON** — machine-readable report for scripting
- **HTML** — interactive SVG multi-lane timeline with color-coded lanes, chapter markers, and gap highlights

---

## CLI Usage

```
arcanum plot-matrix [MANUSCRIPT] [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `MANUSCRIPT` | Path to the manuscript directory containing chapter `.md` files |

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--gap N` | int | `4` | Gap threshold: flag tracks absent for N or more consecutive chapters |
| `--html OUT` | path | *(none)* | Write an interactive SVG HTML report to the specified path |
| `--json` | flag | off | Output the full report as raw JSON |

### Quick Examples

```powershell
# Full manuscript scan with default 4-chapter gap threshold
arcanum plot-matrix Manuscript/

# Tighter gap threshold for a tightly plotted thriller
arcanum plot-matrix Manuscript/ --gap 2

# Generate HTML timeline report
arcanum plot-matrix Manuscript/ --gap 4 --html reports/plot_grid.html

# JSON output
arcanum plot-matrix Manuscript/ --json > plot_report.json
```

> [!TIP]
> Run with `--gap 3` during mid-draft review to catch threads drifting before they become structural problems. Reserve `--gap 2` for final manuscript passes.

---

## Tag & Frontmatter Reference

The module reads track information from two sources in each chapter file: **YAML frontmatter** and **inline tags**.

### YAML Frontmatter

```yaml
---
title: "The Burning of Ashveil"
pov: "Seraphine Dusk"
plot: "The Heist, The Betrayal"
thread: "Kael's Redemption"
arc: "Seraphine's Trust Arc"
---
```

### Inline Tags

```markdown
@plot: The Heist
@thread: Kael's Redemption, The Thieves' Guild Conspiracy
@arc: Seraphine's Trust Arc
```

### Tag Syntax Rules

| Rule | Detail |
|---|---|
| **Multiple values** | Comma-separated on a single tag line: `@plot: Plot A, Plot B` |
| **Whitespace** | Leading and trailing whitespace around each value is stripped |
| **Case sensitivity** | Track names are **case-sensitive**. `"The Heist"` and `"the heist"` are two different tracks |
| **YAML vs inline** | Both sources are merged. If a track appears in both frontmatter and inline tags in the same file, it is counted once |
| **No tag → no presence** | A chapter with no `@plot`/`@thread`/`@arc` tags contributes zero presences to any track |

> [!IMPORTANT]
> Track names must be **consistent** across all chapters. Even a minor spelling difference (e.g., `"Kael's Redemption"` vs `"Kael's Redemption Arc"`) creates a duplicate track entry in the matrix. Establish canonical track names in a notes file and copy-paste them.

---

## Key API Reference

### `extract_chapter_plot_metadata`

```python
extract_chapter_plot_metadata(
    file_path: str | Path,
    chapter_index: int
) -> dict
```

Parses a single chapter file and returns its plot track metadata.

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `index` | `int` | Chapter index (0-based, from `chapter_index`) |
| `file` | `str` | Absolute path to the chapter file |
| `filename` | `str` | Basename of the chapter file |
| `title` | `str` | Chapter title from frontmatter or filename |
| `pov` | `str` | POV character from frontmatter or `@pov:` tag |
| `word_count` | `int` | Approximate word count of the file |
| `plots` | `list[str]` | Primary plot track names |
| `threads` | `list[str]` | Subplot thread names |
| `arcs` | `list[str]` | Character arc names |
| `all_tracks` | `list[str]` | Combined list of all track names from all three types |
| `track_count` | `int` | Total number of distinct tracks in this chapter |

---

### `scan_manuscript_plot_matrix`

```python
scan_manuscript_plot_matrix(
    target_path: str | Path,
    max_gap_threshold: int = 4
) -> dict
```

Scans all chapter files in `target_path` and builds the full plot matrix.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `target_path` | `str \| Path` | Manuscript directory |
| `max_gap_threshold` | `int` | Number of consecutive absent chapters to trigger a Dormant/Gap alert |

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `target` | `str` | Resolved path of the scanned manuscript |
| `total_chapters` | `int` | Number of chapter files found |
| `total_tracks` | `int` | Total distinct track names discovered |
| `chapters` | `list[dict]` | Per-chapter metadata (from `extract_chapter_plot_metadata`) |
| `tracks` | `dict[str, dict]` | Per-track health report (see Track Report Fields below) |
| `abandoned_tracks` | `list[str]` | Track names with `status: "Abandoned"` |
| `dangling_tracks` | `list[str]` | Track names with `status: "Dangling"` |
| `density_histogram` | `dict[int, int]` | Maps chapter index → number of active tracks in that chapter |

### Per-Track Report Fields (inside `tracks`)

| Field | Type | Description |
|---|---|---|
| `first_chapter` | `int` | 0-based index of first appearance |
| `last_chapter` | `int` | 0-based index of most recent appearance |
| `occurrences` | `int` | Total number of chapters containing this track |
| `density` | `float` | `occurrences / total_chapters` |
| `max_gap` | `int` | Longest consecutive run of absent chapters |
| `status` | `str` | `"Healthy"`, `"Dormant"`, or `"Dangling"` |
| `chapters` | `list[int]` | All chapter indices where this track appears |

---

### `generate_plot_html_report`

```python
generate_plot_html_report(
    report: dict,
    output_path: str | Path
) -> Path
```

Generates a self-contained HTML file with an **interactive SVG multi-lane timeline**. Each track occupies its own horizontal lane. Chapters are represented as vertical columns with colored markers indicating presence; gaps are highlighted in amber; dangling tracks are labeled in red.

---

## Track Health Diagnostics

| Status | Condition | Severity |
|---|---|---|
| **Healthy** | `max_gap < max_gap_threshold` AND not dangling | ✅ No action needed |
| **Dormant / Gap Alert** | `max_gap >= max_gap_threshold` | ⚠️ WARNING |
| **Dangling Warning** | Last seen in first 60% of manuscript, appears fewer than 3 times, AND manuscript has ≥ 5 chapters total | ⚠️ WARNING |
| **Abandoned** | Both Dormant and Dangling conditions met simultaneously | 🔴 ERROR |

### Dormant Track Logic

A track is **Dormant** when its longest absence gap equals or exceeds `max_gap_threshold` (default: 4 chapters). This does **not** require the track to have disappeared — a track that vanishes for 4 chapters and then reappears is still flagged Dormant to alert the author to whether the absence was intentional.

### Dangling Track Logic

A track is **Dangling** when all three of the following are true:

1. Its `last_chapter` index falls within the first 60% of total chapters.
2. Its total `occurrences` is fewer than 3.
3. The manuscript has at least 5 chapters.

Rationale: a track that appears only 1–2 times in the early portion of a manuscript was likely introduced as a setup that was never paid off.

> [!WARNING]
> Dangling tracks are the most common structural flaw in long-form manuscripts. A track with `occurrences: 1` that appears in chapter 2 of a 20-chapter manuscript almost certainly requires either a follow-up chapter or removal of the original mention.

---

## Behavioral Notes

- **Chapter ordering**: Files are sorted alphabetically by filename. Use zero-padded numeric prefixes (e.g., `01_`, `02_`) to ensure correct order. Non-numeric prefixes may cause unexpected ordering.
- **File discovery**: Only `.md` files directly or recursively inside `target_path` are processed. Subdirectory depth is unlimited.
- **Frontmatter priority**: If both frontmatter and inline `@plot:` tags are present in the same file for the same track, the track is deduplicated — it counts only once.
- **Track name canonicalization**: No normalization is applied. Canonicalize track names manually in your source files.
- **Density histogram**: The `density_histogram` field is useful for identifying chapters that carry too many simultaneous plot threads (cognitive overload for readers) or chapters with no active threads (structural dead zones).
- **Minimum chapter count for Dangling**: The Dangling heuristic requires `total_chapters >= 5` to avoid false positives in short story collections or novellas under 4 chapters.
- **HTML report interactivity**: The SVG timeline is rendered client-side using inline SVG and CSS. No JavaScript framework is required. Hovering over a chapter marker shows the full list of active tracks for that chapter.

---

## Example Workflow

### Workflow 1: First-Draft Structure Audit

```powershell
arcanum plot-matrix Manuscript/ --html reports/plot_matrix.html
```

Open `reports/plot_matrix.html`. Each horizontal lane is a plot track. Amber columns are gap alerts. Red-labeled tracks are dangling.

### Workflow 2: Tight Deadline Pass

```powershell
arcanum plot-matrix Manuscript/ --gap 2 --json | python -c "
import sys, json
data = json.load(sys.stdin)
for name, t in data['tracks'].items():
    if t['status'] != 'Healthy':
        print(f'{t[\"status\"]}: {name} (gap={t[\"max_gap\"]}, seen={t[\"occurrences\"]}x)')
"
```

### Workflow 3: Python API

```python
from scripts.lib.plot_matrix import (
    scan_manuscript_plot_matrix,
    generate_plot_html_report,
)

report = scan_manuscript_plot_matrix("Manuscript/", max_gap_threshold=3)

print(f"Total tracks: {report['total_tracks']}")
print(f"Dangling: {report['dangling_tracks']}")
print(f"Abandoned: {report['abandoned_tracks']}")

# Print a density map
for ch_idx, count in sorted(report["density_histogram"].items()):
    bar = "█" * count
    chapter = report["chapters"][ch_idx]["filename"]
    print(f"  Ch {ch_idx+1:02d} [{count:2d} tracks] {bar}  {chapter}")

# Generate HTML
generate_plot_html_report(report, "reports/plot_matrix.html")
```

### Sample Chapter File

```markdown
---
title: "The Fractured Council"
pov: "Ambassador Lyren"
plot: "The War of Succession"
thread: "Lyren's Double Agent Arc, The Trade Guild Conspiracy"
arc: "Lyren's Loyalty Arc"
---

# The Fractured Council

@plot: The War of Succession
@thread: The Trade Guild Conspiracy

Ambassador Lyren entered the council chamber, keenly aware of how many eyes tracked her every step...
```

This file contributes to four tracks:
- `"The War of Succession"` (plot)
- `"Lyren's Double Agent Arc"` (thread, from frontmatter)
- `"The Trade Guild Conspiracy"` (thread, merged from frontmatter + inline)
- `"Lyren's Loyalty Arc"` (arc)

---

*Part of the **Ars Arcanum Scriptorium** craft engine. For platform-wide CLI reference, see `docs/CLI_REFERENCE.md`.*
