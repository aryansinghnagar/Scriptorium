# TIMELINE_SYNC — Dual-Track Narrative vs Chronological Timeline Synchronizer

> **Module**: `scripts/lib/timeline_sync.py`  
> **CLI Command**: `arcanum timeline`  
> **Purpose**: Parses time-coordinate tags from manuscript chapters to build two parallel timelines — narrative order (reading order) and chronological order (in-world order) — then detects paradoxes, flashbacks, flashforwards, and bilocation anomalies.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Usage](#cli-usage)
3. [Key API Reference](#key-api-reference)
4. [Time Format Reference](#time-format-reference)
5. [Source Tags Scanned](#source-tags-scanned)
6. [TimelineEvent Dataclass](#timelineevent-dataclass)
7. [Paradox Detection](#paradox-detection)
8. [Diagnostic Codes](#diagnostic-codes)
9. [Behavioral Notes](#behavioral-notes)
10. [Example Workflow](#example-workflow)

---

## Overview

The `timeline_sync` module is the **temporal continuity auditor** of the Ars Arcanum engine. In multi-POV, non-linear narratives, scenes jump between time periods, perspectives, and locations. The timeline synchronizer pulls `@time:` tags from each chapter, normalises them to a shared numeric coordinate space, and renders both the narrative reading order and the true chronological order side by side.

**What the module detects:**

| Detection | Description |
|---|---|
| **Flashbacks** | Chapters set earlier in time than the narrative "current" position |
| **Flashforwards** | Chapters set later in time than the narrative current position |
| **Non-linear narration** | Whether the manuscript is told in strict chronological order |
| **Bilocation paradoxes** | The same POV character appearing at the same time coordinate but in two different locations |

**Output formats:**

- Console summary of event counts and paradox flags
- JSON export of the full event list and analysis
- HTML dual-track timeline (narrative lane vs chronological lane) with event cards

---

## CLI Usage

```
arcanum timeline [MANUSCRIPT] [OPTIONS]
```

### Arguments

| Argument | Description |
|---|---|
| `MANUSCRIPT` | Path to the manuscript directory |

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--html OUT` | path | *(none)* | Generate HTML dual-track timeline report |
| `--json` | flag | off | Output raw JSON analysis |
| `--paradox-only` | flag | off | Print only chapters with detected paradoxes |

### Quick Examples

```powershell
# Full timeline analysis
arcanum timeline Manuscript/

# Generate HTML report
arcanum timeline Manuscript/ --html reports/timeline.html

# Print only paradox-flagged chapters
arcanum timeline Manuscript/ --paradox-only

# JSON output
arcanum timeline Manuscript/ --json > timeline_data.json
```

> [!TIP]
> Use `--paradox-only` for a fast CI-style check during revision. If it outputs nothing, your temporal continuity is clean.

---

## Key API Reference

### `parse_time_coordinate`

```python
parse_time_coordinate(
    raw_time: str,
    fallback_idx: int
) -> tuple[float, bool, bool]
```

Parses a raw time string into a normalized numeric coordinate.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `raw_time` | `str` | The raw time string from a `@time:` tag or frontmatter `time:` field |
| `fallback_idx` | `int` | Chapter index used as fallback if parsing fails |

**Returns**: A tuple of `(numeric_coord, is_flashback, is_flashforward)`

| Element | Type | Description |
|---|---|---|
| `numeric_coord` | `float` | Normalised chronological position (see Time Format Reference) |
| `is_flashback` | `bool` | True if the time string explicitly declares a flashback |
| `is_flashforward` | `bool` | True if the time string explicitly declares a flashforward |

---

### `extract_timeline_events`

```python
extract_timeline_events(target_path: str | Path) -> list[TimelineEvent]
```

Scans all `.md` files in `target_path`, reads their time, POV, location, character, and summary metadata, and returns a list of `TimelineEvent` dataclass instances sorted by narrative order (file system sort order).

---

### `analyze_timeline_synchronization`

```python
analyze_timeline_synchronization(events: list[TimelineEvent]) -> dict
```

Takes the event list from `extract_timeline_events` and computes the full dual-track analysis.

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `total_events` | `int` | Total number of timeline events (chapters with `@time:` tags) |
| `flashback_count` | `int` | Number of events flagged as flashbacks |
| `flashforward_count` | `int` | Number of events flagged as flashforwards |
| `is_linear` | `bool` | True if narrative order equals chronological order (no non-linear jumps) |
| `paradoxes` | `list[dict]` | List of paradox records (see Paradox Detection) |
| `chronological_events` | `list[TimelineEvent]` | Events sorted by `normalized_time` (ascending) |
| `narrative_events` | `list[TimelineEvent]` | Events in original narrative (reading) order |

---

### `generate_timeline_html_report`

```python
generate_timeline_html_report(
    report: dict,
    output_path: str | Path
) -> Path
```

Generates a dual-lane HTML timeline report. The top lane shows narrative (reading) order; the bottom lane shows chronological order. Events are rendered as labeled cards connected by lines showing temporal displacement. Flashbacks appear in blue; flashforwards in amber; paradoxes in red.

---

## Time Format Reference

The `@time:` tag (or YAML `time:` field) accepts multiple time expression formats:

### Year / Epoch Format

```
@time: 1422 3E
@time: Year 304
@time: Year -500
```

| Pattern | Numeric Coordinate | Notes |
|---|---|---|
| `1422 3E` | `1422.0` | Epoch suffix (`3E`, `4E`, `2A`) is stripped; the numeric year is used |
| `Year 304` | `304.0` | `Year` prefix is stripped |
| `Year -500` | `-500.0` | Negative values represent pre-era dates |

### Day Offset Format

```
@time: Day 14
@time: Day 14, 08:00
```

| Pattern | Numeric Coordinate | Notes |
|---|---|---|
| `Day 14` | `14.0` | Fractional day not added |
| `Day 14, 08:00` | `14.333...` | Hour converted to fraction: 8/24 ≈ 0.333 |

### Relative / Narrative Format

```
@time: Flashback: 10 years earlier
@time: 5 years later
@time: 200 years before the Sundering
```

| Pattern | `is_flashback` | `is_flashforward` | Coordinate |
|---|---|---|---|
| `Flashback: ...` | `True` | `False` | `fallback_idx - extracted_years` |
| `... years earlier` | `True` | `False` | `fallback_idx - extracted_years` |
| `... years later` | `False` | `True` | `fallback_idx + extracted_years` |

> [!NOTE]
> Relative time expressions are resolved **relative to the chapter's narrative position** (`fallback_idx`), not to an absolute calendar anchor. For absolute precision, use Year or Day formats.

### ISO Date Format

```
@time: 2045-10-12
```

Parsed as `float(year) + (day_of_year / 365)`. Suitable for science fiction or alternate-history settings using real-world dates.

### Unrecognised Format

If the raw time string does not match any known format, `numeric_coord` is set to `float(fallback_idx)` and neither `is_flashback` nor `is_flashforward` is set.

---

## Source Tags Scanned

Each chapter file may declare timeline metadata via YAML frontmatter or inline tags. Both sources are merged.

### YAML Frontmatter

```yaml
---
title: "Embers of the First Age"
pov: "Archivist Theron"
location: "The Sunken Library, Kalrath"
time: "Year -500"
characters:
  - "Archivist Theron"
  - "High Keeper Mael"
---
```

### Inline Tags

```markdown
@pov: Archivist Theron
@location: The Sunken Library, Kalrath
@time: Year -500
@char: Archivist Theron
@char: High Keeper Mael
```

### Tag Priority

If a tag appears in both frontmatter and as an inline tag, the **frontmatter value takes precedence** for `pov`, `location`, and `time`. For `characters` / `@char:`, values from both sources are merged into a deduplicated list.

---

## TimelineEvent Dataclass

```python
@dataclass
class TimelineEvent:
    id: int                    # Sequential event ID (1-based)
    narrative_index: int       # Position in reading/file-sort order (0-based)
    title: str                 # Chapter title
    filename: str              # Basename of source file
    path: Path                 # Absolute path to source file
    pov: str                   # POV character name
    location: str              # Scene location string
    raw_time: str              # Original unparsed time string
    normalized_time: float     # Numeric chronological coordinate
    is_flashback: bool         # True if declared as flashback
    is_flashforward: bool      # True if declared as flashforward
    characters: list[str]      # All characters present in the scene
    summary: str               # First non-empty, non-tag paragraph (auto-extracted)
```

---

## Paradox Detection

### Bilocation Paradox

The **bilocation** paradox is currently the only automated paradox type detected.

**Condition**: Two or more `TimelineEvent` objects satisfy all of the following:

1. They share the same `pov` character name (case-insensitive comparison).
2. Their `normalized_time` values are **equal** (within floating-point tolerance: `abs(a - b) < 0.01`).
3. Their `location` strings are **different** (case-insensitive comparison).

**Interpretation**: The same POV character appears in two different places at the exact same moment in the world's chronology. This is almost always an authoring error — either the `@time:` tag is wrong in one chapter, or two chapters that were written separately have accidentally been placed at the same in-world date.

**Paradox record fields:**

| Field | Description |
|---|---|
| `type` | `"bilocation"` |
| `pov` | The POV character involved |
| `time` | The shared `normalized_time` coordinate |
| `events` | List of event IDs involved in the paradox |
| `locations` | List of distinct locations at that time |
| `filenames` | List of source files contributing to the paradox |

---

## Diagnostic Codes

| Code | Severity | Condition | Resolution |
|---|---|---|---|
| `TL-001` | ERROR | Bilocation paradox detected | Correct `@time:` tag in one of the conflicting chapters |
| `TL-002` | INFO | Chapter has no `@time:` tag | Add a `@time:` tag for full timeline coverage |
| `TL-003` | INFO | Unrecognised time format; using fallback index | Use a supported time format (see Time Format Reference) |
| `TL-010` | INFO | Manuscript is non-linear | Expected for stories with flashbacks; noted for awareness |
| `TL-011` | WARNING | Flashback count exceeds 30% of total events | High flashback density can confuse readers; review pacing |

---

## Behavioral Notes

- **Chapter sort order**: Files are sorted alphabetically by filename. Use zero-padded chapter numbers in filenames to guarantee correct narrative order.
- **Missing `@time:` tags**: Chapters without a `@time:` tag are still included in `narrative_events` but are excluded from `chronological_events`. Their `normalized_time` is set to `float(narrative_index)`.
- **Bilocation tolerance**: Two times are considered equal if they differ by less than `0.01` in normalized space. For Day-format coordinates, this means events within ~15 minutes of each other are treated as simultaneous.
- **Character list deduplication**: `@char:` tags and YAML `characters:` lists are merged and deduplicated with case-sensitive comparison.
- **Summary auto-extraction**: The `summary` field is populated by extracting the first paragraph of prose text after the frontmatter block, skipping blank lines and lines beginning with `@` or `#`.
- **`is_linear` determination**: The manuscript is flagged `is_linear: False` if any event's `normalized_time` is lower than the `normalized_time` of the event immediately preceding it in narrative order.
- **Pre-era negative coordinates**: Year `-500` is a valid coordinate. Negative values sort correctly before positive values in chronological order.

---

## Example Workflow

### Workflow 1: Full Timeline with HTML Report

```powershell
arcanum timeline Manuscript/ --html reports/timeline.html
```

The HTML report renders two lanes:
- **Narrative lane** (top): chapters in reading order, left to right
- **Chronological lane** (bottom): same chapters sorted by `normalized_time`

Connecting arcs show how chapters jump forward or backward in time.

### Workflow 2: Paradox Audit

```powershell
arcanum timeline Manuscript/ --paradox-only
```

**Sample output:**
```
[TL-001] BILOCATION PARADOX
  POV: Archivist Theron
  Time: -500.0 (Year -500)
  Files:
    - 04_Embers_of_the_First_Age.md  → Location: "The Sunken Library"
    - 11_The_Archivist_at_Sea.md     → Location: "The Storm Galley, Sea of Verath"
  Resolution: Correct the @time: tag in one of the above files.
```

### Workflow 3: Python API

```python
from scripts.lib.timeline_sync import (
    extract_timeline_events,
    analyze_timeline_synchronization,
    generate_timeline_html_report,
)

events = extract_timeline_events("Manuscript/")
report = analyze_timeline_synchronization(events)

print(f"Total events: {report['total_events']}")
print(f"Flashbacks:   {report['flashback_count']}")
print(f"Flashforwards:{report['flashforward_count']}")
print(f"Is linear:    {report['is_linear']}")

if report["paradoxes"]:
    for p in report["paradoxes"]:
        print(f"\n⚠ PARADOX [{p['type'].upper()}]: {p['pov']} at t={p['time']}")
        for fn in p["filenames"]:
            print(f"   - {fn}")
else:
    print("\n✓ No temporal paradoxes detected.")

generate_timeline_html_report(report, "reports/timeline.html")
```

### Workflow 4: Annotating a Chapter

```markdown
---
title: "The Last Council of Kalrath"
pov: "High Keeper Mael"
location: "The Grand Spire, Kalrath"
time: "Year 1422 3E"
characters:
  - "High Keeper Mael"
  - "Tribune Sorvaine"
---

@pov: High Keeper Mael
@location: The Grand Spire, Kalrath
@time: 1422 3E

The council chamber fell silent as High Keeper Mael raised the Seal of Continuance...
```

This chapter will appear at `normalized_time: 1422.0` in the chronological lane.

---

*Part of the **Ars Arcanum Scriptorium** craft engine. For platform-wide CLI reference, see `docs/CLI_REFERENCE.md`.*
