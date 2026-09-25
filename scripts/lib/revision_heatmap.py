#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Revision Density & Churn Heatmap Engine (scripts/lib/revision_heatmap.py)
=================================================================================================
Zero-dependency, offline revision density analyzer that measures manuscript churn
by comparing draft snapshots, flagging over-revised and under-revised chapters.

Capabilities:
1. Snapshot-Based Diffing:
   - scan_manuscript_snapshots(ms_dir): finds chapter .md files and computes line-level diff stats between
     the CURRENT draft and a BACKUP snapshot if available (from Backups/ dir or supplied snapshot_dir)
2. Churn Analysis:
   - analyze_revision_churn(chapter_stats): computes churn_ratio per chapter, flags outliers
   - REV-101: Over-Revised Chapter (churn_ratio > 3x average — rewriting instability)
   - REV-102: Under-Revised / Pristine Draft (no insertions OR deletions since initial — possibly forgotten)
3. Heatmap Visualization:
   - generate_revision_heatmap_html(churn_data, output_path): standalone offline CSP-compliant HTML heatmap
     with chapter-level colored churn bars (green=low, amber=medium, red=high)
4. CLI: main(argv) for 'arcanum revision-heatmap [MANUSCRIPT] [--export-html FILE] [--json] [--snapshot-dir DIR]'
"""

import argparse
import difflib
import html
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]

logger = logging.getLogger("arcanum.revision_heatmap")

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

_AT_TAG_RE = re.compile(r"^@[A-Za-z0-9_-]+:")
_HEADING_RE = re.compile(r"^#{1,6}\s")
_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)

# Directories to skip when scanning for chapters
_SKIP_DIRS = {"Front_Matter", "Back_Matter"}

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class ChapterRevisionStats:
    """Per-chapter revision statistics derived from snapshot diffing."""

    chapter: str       # chapter filename
    rel_path: str      # relative path from ms_dir
    word_count: int    # current word count
    insertions: int    # lines added vs snapshot (0 if no snapshot)
    deletions: int     # lines removed vs snapshot (0 if no snapshot)
    churn_score: int   # insertions + deletions
    churn_ratio: float  # churn_score / max(word_count, 1)
    has_snapshot: bool  # whether a snapshot was found for comparison
    flag: str          # '' | 'REV-101' | 'REV-102'


# ---------------------------------------------------------------------------
# Core text utilities
# ---------------------------------------------------------------------------


def count_words(text: str) -> int:
    """Count whitespace-separated words, ignoring @-tags and markdown headers.

    Lines that begin with '@tag:' syntax or '#' headings are excluded entirely
    from the word count, matching novelWriter metadata conventions.
    """
    kept_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _AT_TAG_RE.match(stripped):
            continue
        if _HEADING_RE.match(stripped):
            continue
        kept_lines.append(stripped)
    return len(_WORD_RE.findall("\n".join(kept_lines)))


def diff_line_counts(current_text: str, snapshot_text: str) -> tuple[int, int]:
    """Return (insertions, deletions) using difflib.unified_diff line comparison.

    Lines starting with '+' (but not '+++') are insertions.
    Lines starting with '-' (but not '---') are deletions.
    """
    current_lines = current_text.splitlines(keepends=True)
    snapshot_lines = snapshot_text.splitlines(keepends=True)

    insertions = 0
    deletions = 0

    for line in difflib.unified_diff(snapshot_lines, current_lines, lineterm=""):
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            insertions += 1
        elif line.startswith("-"):
            deletions += 1

    return insertions, deletions


# ---------------------------------------------------------------------------
# Snapshot scanning
# ---------------------------------------------------------------------------


def _build_snapshot_index(snapshot_dir: Path) -> dict[str, Path]:
    """Walk snapshot_dir recursively and map stem -> first matching path."""
    index: dict[str, Path] = {}
    try:
        for p in snapshot_dir.rglob("*.md"):
            if p.name.startswith("."):
                continue
            stem = p.stem
            if stem not in index:
                index[stem] = p
    except OSError as e:
        logger.debug("Cannot read snapshot_dir %s: %s", snapshot_dir, e)
    return index


def scan_manuscript_snapshots(
    ms_dir: Path,
    snapshot_dir: Path | None = None,
) -> list[ChapterRevisionStats]:
    """Scan all *.md chapter files in ms_dir recursively.

    For each chapter, looks for a matching snapshot in snapshot_dir
    (or ms_dir/Backups/ as default fallback).  Snapshot matching uses the
    chapter stem name searched anywhere in snapshot_dir.

    If no snapshot is found, insertions=word_count, deletions=0 (treats the
    entire current text as new / uncompared).

    Returns a list of ChapterRevisionStats sorted by rel_path.
    """
    ms_dir = ms_dir.resolve()

    # Determine snapshot directory
    effective_snapshot_dir = snapshot_dir or (ms_dir / "Backups")
    snapshot_index = _build_snapshot_index(effective_snapshot_dir) if effective_snapshot_dir.is_dir() else {}

    results: list[ChapterRevisionStats] = []

    try:
        all_md = sorted(ms_dir.rglob("*.md"))
    except OSError as e:
        logger.debug("Cannot rglob ms_dir %s: %s", ms_dir, e)
        return results

    for chapter_path in all_md:
        # Skip hidden files
        if chapter_path.name.startswith("."):
            continue

        # Skip skipped directories anywhere in the relative path
        rel = chapter_path.relative_to(ms_dir)
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue

        # Skip snapshots themselves if they live inside ms_dir/Backups
        try:
            chapter_path.relative_to(effective_snapshot_dir)
            continue  # this file lives inside the snapshot dir — skip it
        except ValueError:
            pass

        # Read current file
        try:
            current_text = chapter_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.debug("Skipping unreadable chapter %s: %s", chapter_path, e)
            continue

        wc = count_words(current_text)
        stem = chapter_path.stem
        snapshot_path = snapshot_index.get(stem)

        if snapshot_path is not None:
            try:
                snapshot_text = snapshot_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as e:
                logger.debug("Skipping unreadable snapshot %s: %s", snapshot_path, e)
                snapshot_path = None
                snapshot_text = ""
        else:
            snapshot_text = ""

        has_snapshot = snapshot_path is not None

        if has_snapshot:
            insertions, deletions = diff_line_counts(current_text, snapshot_text)
        else:
            # No snapshot: treat whole current text as new
            insertions = wc
            deletions = 0

        churn_score = insertions + deletions
        churn_ratio = churn_score / max(wc, 1)

        results.append(
            ChapterRevisionStats(
                chapter=chapter_path.name,
                rel_path=str(rel).replace("\\", "/"),
                word_count=wc,
                insertions=insertions,
                deletions=deletions,
                churn_score=churn_score,
                churn_ratio=churn_ratio,
                has_snapshot=has_snapshot,
                flag="",
            )
        )

    results.sort(key=lambda s: s.rel_path)
    return results


# ---------------------------------------------------------------------------
# Churn analysis & flag assignment
# ---------------------------------------------------------------------------


def analyze_revision_churn(
    stats: list[ChapterRevisionStats],
    over_revised_threshold: float = 3.0,
) -> dict:
    """Flag REV-101 and REV-102 on each ChapterRevisionStats in-place.

    Rules
    -----
    REV-101 (Over-Revised):
        chapter.churn_ratio > over_revised_threshold * avg_churn_ratio  AND  avg_churn_ratio > 0

    REV-102 (Pristine / Under-Revised):
        chapter.churn_score == 0  AND  chapter.word_count > 50  AND  chapter.has_snapshot is True

    Returns a summary dict with total_chapters, avg_churn_score, max_churn_score,
    and a 'findings' list of dicts for flagged chapters.
    """
    if not stats:
        return {
            "total_chapters": 0,
            "avg_churn_score": 0.0,
            "max_churn_score": 0,
            "avg_churn_ratio": 0.0,
            "findings": [],
        }

    total = len(stats)
    avg_churn_score = sum(s.churn_score for s in stats) / total
    max_churn_score = max(s.churn_score for s in stats)
    avg_churn_ratio = sum(s.churn_ratio for s in stats) / total

    findings: list[dict] = []

    for chapter in stats:
        chapter.flag = ""  # reset

        # REV-101: Over-Revised
        if avg_churn_ratio > 0 and chapter.churn_ratio > over_revised_threshold * avg_churn_ratio:
            chapter.flag = "REV-101"
            findings.append({
                "id": "REV-101",
                "code": "REV-101",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": (
                    f"Over-revised chapter: churn_ratio={chapter.churn_ratio:.3f} is "
                    f">{over_revised_threshold}x the average ({avg_churn_ratio:.3f}). "
                    "Consider stabilising this section."
                ),
            })
            continue  # only one flag per chapter

        # REV-102: Pristine Draft (no churn, has snapshot, non-trivial word count)
        if chapter.churn_score == 0 and chapter.word_count > 50 and chapter.has_snapshot:
            chapter.flag = "REV-102"
            findings.append({
                "id": "REV-102",
                "code": "REV-102",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": (
                    f"Under-revised chapter: zero churn detected against snapshot with "
                    f"{chapter.word_count} words. This chapter may have been forgotten in revision."
                ),
            })

    return {
        "total_chapters": total,
        "avg_churn_score": avg_churn_score,
        "max_churn_score": max_churn_score,
        "avg_churn_ratio": avg_churn_ratio,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# HTML heatmap generation
# ---------------------------------------------------------------------------

_CSP = (
    "default-src 'none'; "
    "style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; "
    "img-src data:; "
    "media-src data: blob:;"
)

_FLAG_LABELS: dict[str, str] = {
    "REV-101": "⚠ REV-101 Over-Revised",
    "REV-102": "🔵 REV-102 Pristine Draft",
    "": "",
}


def _churn_color(churn_ratio: float) -> str:
    """Map churn_ratio to a hex color for the heatmap bar."""
    if churn_ratio >= 0.5:
        return "#ef4444"  # red
    if churn_ratio >= 0.2:
        return "#f59e0b"  # amber
    return "#22c55e"  # green


def _bar_width(churn_score: int, max_score: int) -> int:
    """Compute a bar width percentage (1–100) relative to max_score."""
    if max_score == 0:
        return 1
    return max(1, min(100, round(churn_score / max_score * 100)))


def generate_revision_heatmap_html(
    churn_data: dict,
    output_path: Path,
) -> None:
    """Generate a standalone CSP-compliant offline HTML heatmap.

    Parameters
    ----------
    churn_data:
        Dict with keys: manuscript, chapters (list[ChapterRevisionStats]),
        findings, avg_churn_score, total_chapters, max_churn_score.
    output_path:
        Destination .html file path.
    """
    manuscript = html.escape(str(churn_data.get("manuscript", "Manuscript")))
    chapters: list[ChapterRevisionStats] = churn_data.get("chapters", [])
    findings: list[dict] = churn_data.get("findings", [])
    avg_churn = churn_data.get("avg_churn_score", 0.0)
    total = churn_data.get("total_chapters", len(chapters))
    max_score = churn_data.get("max_churn_score", 0)
    if max_score == 0 and chapters:
        max_score = max(c.churn_score for c in chapters)

    # Build chapter rows HTML
    rows_html_parts: list[str] = []
    for ch in chapters:
        color = _churn_color(ch.churn_ratio)
        bar_w = _bar_width(ch.churn_score, max_score)
        flag_label = _FLAG_LABELS.get(ch.flag, "")
        flag_badge = (
            f' <span style="font-size:0.75rem;padding:2px 6px;border-radius:4px;'
            f'background:{color};color:#fff;margin-left:8px;">{html.escape(flag_label)}</span>'
            if flag_label
            else ""
        )
        snapshot_indicator = (
            '<span style="color:#6b7280;font-size:0.75rem;"> (no snapshot)</span>'
            if not ch.has_snapshot
            else ""
        )
        rows_html_parts.append(
            f"""
      <tr>
        <td style="padding:6px 8px;font-family:monospace;font-size:0.85rem;max-width:280px;
                   overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
            title="{html.escape(ch.rel_path)}">
          {html.escape(ch.chapter)}{snapshot_indicator}{flag_badge}
        </td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.word_count:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.insertions:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.deletions:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.churn_score:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.churn_ratio:.3f}</td>
        <td style="padding:6px 16px;min-width:120px;">
          <div style="background:#e5e7eb;border-radius:4px;height:16px;width:100%;">
            <div style="background:{color};border-radius:4px;height:16px;width:{bar_w}%;"></div>
          </div>
        </td>
      </tr>"""
        )
    rows_html = "".join(rows_html_parts)

    # Build findings HTML
    findings_parts: list[str] = []
    for f in findings:
        code = html.escape(f.get("code", ""))
        msg = html.escape(f.get("message", ""))
        badge_color = "#ef4444" if code == "REV-101" else "#3b82f6"
        findings_parts.append(
            f"""<li style="margin:6px 0;">
        <span style="background:{badge_color};color:#fff;padding:2px 8px;border-radius:4px;
                     font-size:0.8rem;margin-right:8px;">{code}</span>
        {msg}
      </li>"""
        )
    findings_html = (
        "<ul style='list-style:none;padding:0;margin:0;'>" + "".join(findings_parts) + "</ul>"
        if findings_parts
        else "<p style='color:#6b7280;'>No revision flags raised.</p>"
    )

    # Legend items
    legend_items = [
        ("#22c55e", "Low churn (ratio &lt; 0.2)"),
        ("#f59e0b", "Medium churn (0.2 – 0.5)"),
        ("#ef4444", "High churn (ratio ≥ 0.5)"),
    ]
    legend_html = "".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:16px;">'
        f'<span style="display:inline-block;width:14px;height:14px;border-radius:3px;'
        f'background:{c};margin-right:6px;"></span>{label}</span>'
        for c, label in legend_items
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="{_CSP}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Revision Heatmap — {manuscript}</title>
  <style>
    *,*::before,*::after{{box-sizing:border-box;}}
    body{{font-family:system-ui,sans-serif;margin:0;padding:24px;
         background:#f9fafb;color:#111827;}}
    h1{{font-size:1.5rem;margin-bottom:4px;}}
    .subtitle{{color:#6b7280;font-size:0.9rem;margin-bottom:20px;}}
    .stats{{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:20px;}}
    .stat-card{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;
                padding:12px 20px;min-width:140px;}}
    .stat-label{{font-size:0.75rem;color:#6b7280;text-transform:uppercase;
                 letter-spacing:.05em;}}
    .stat-value{{font-size:1.5rem;font-weight:700;margin-top:4px;}}
    table{{width:100%;border-collapse:collapse;background:#fff;
           border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;
           margin-bottom:24px;}}
    thead tr{{background:#f3f4f6;}}
    th{{padding:8px 8px;text-align:left;font-size:0.75rem;text-transform:uppercase;
        letter-spacing:.05em;color:#6b7280;}}
    tbody tr:hover{{background:#f9fafb;}}
    tbody tr:nth-child(even){{background:#fdfdfd;}}
    .findings-box{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;
                  padding:16px 20px;margin-bottom:24px;}}
    .legend{{font-size:0.8rem;color:#374151;margin-bottom:20px;}}
    footer{{font-size:0.75rem;color:#9ca3af;margin-top:24px;}}
  </style>
</head>
<body>
  <h1>📊 Revision Heatmap — {manuscript}</h1>
  <p class="subtitle">Ars Arcanum · Manuscript Revision Density &amp; Churn Analysis</p>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">Total Chapters</div>
      <div class="stat-value">{total}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Avg Churn Score</div>
      <div class="stat-value">{avg_churn:.1f}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Max Churn Score</div>
      <div class="stat-value">{max_score}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Flags Raised</div>
      <div class="stat-value">{len(findings)}</div>
    </div>
  </div>

  <div class="legend">{legend_html}</div>

  <table>
    <thead>
      <tr>
        <th>Chapter</th>
        <th style="text-align:right;">Words</th>
        <th style="text-align:right;">Insertions</th>
        <th style="text-align:right;">Deletions</th>
        <th style="text-align:right;">Churn</th>
        <th style="text-align:right;">Ratio</th>
        <th>Heatmap</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="findings-box">
    <h2 style="font-size:1rem;margin:0 0 12px;">Revision Findings</h2>
    {findings_html}
  </div>

  <footer>Generated by Ars Arcanum revision-heatmap engine · offline, privacy-respecting</footer>
</body>
</html>"""

    atomic_write(output_path, page)
    logger.info("Revision heatmap written to %s", output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list | None = None) -> None:
    """Entry point: arcanum revision-heatmap [MANUSCRIPT] [--export-html FILE] [--json] [--snapshot-dir DIR]"""
    parser = argparse.ArgumentParser(
        prog="arcanum revision-heatmap",
        description="Manuscript Revision Density & Churn Heatmap Engine",
    )
    parser.add_argument(
        "manuscript",
        nargs="?",
        default=".",
        help="Path to manuscript directory (default: current directory)",
    )
    parser.add_argument(
        "--snapshot-dir",
        metavar="DIR",
        help="Directory containing snapshot files for comparison (default: <manuscript>/Backups/)",
    )
    parser.add_argument(
        "--export-html",
        metavar="FILE",
        help="Export heatmap to this HTML file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON to stdout",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        metavar="FACTOR",
        help="Over-revised detection multiplier (default: 3.0)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s  %(name)s  %(message)s",
    )

    ms_dir = Path(args.manuscript).resolve()
    if not ms_dir.is_dir():
        logger.error("Manuscript directory not found: %s", ms_dir)
        sys.exit(1)

    snapshot_dir = Path(args.snapshot_dir).resolve() if args.snapshot_dir else None

    # Scan
    chapter_stats = scan_manuscript_snapshots(ms_dir, snapshot_dir=snapshot_dir)
    if not chapter_stats:
        logger.warning("No chapter files found in %s", ms_dir)
        sys.exit(0)

    # Analyse
    summary = analyze_revision_churn(chapter_stats, over_revised_threshold=args.threshold)

    churn_data: dict = {
        "manuscript": ms_dir.name,
        "chapters": chapter_stats,
        "findings": summary["findings"],
        "avg_churn_score": summary["avg_churn_score"],
        "max_churn_score": summary["max_churn_score"],
        "avg_churn_ratio": summary["avg_churn_ratio"],
        "total_chapters": summary["total_chapters"],
    }

    if args.output_json:
        # Serialise dataclasses to plain dicts
        serialisable = {
            **{k: v for k, v in churn_data.items() if k != "chapters"},
            "chapters": [asdict(c) for c in chapter_stats],
        }
        print(json.dumps(serialisable, indent=2))
        return

    if args.export_html:
        out_path = Path(args.export_html).resolve()
        generate_revision_heatmap_html(churn_data, out_path)
        print(f"Heatmap exported → {out_path}")
        return

    # Terminal summary
    print(f"\n📊 Revision Heatmap — {ms_dir.name}")
    print(f"   Chapters analysed : {summary['total_chapters']}")
    print(f"   Avg churn score   : {summary['avg_churn_score']:.1f}")
    print(f"   Max churn score   : {summary['max_churn_score']}")
    print()

    _COLORS = {
        "green": "\033[92m",
        "amber": "\033[93m",
        "red": "\033[91m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    for ch in chapter_stats:
        if ch.churn_ratio >= 0.5:
            color = _COLORS["red"]
        elif ch.churn_ratio >= 0.2:
            color = _COLORS["amber"]
        else:
            color = _COLORS["green"]
        flag_str = f"  [{ch.flag}]" if ch.flag else ""
        bar = "█" * min(40, max(1, round(ch.churn_ratio * 40)))
        print(
            f"  {color}{bar:<40}{_COLORS['reset']} "
            f"{ch.chapter:<40} "
            f"ratio={ch.churn_ratio:.3f} "
            f"churn={ch.churn_score}{flag_str}"
        )

    if summary["findings"]:
        print(f"\n{_COLORS['bold']}Findings:{_COLORS['reset']}")
        for finding in summary["findings"]:
            print(f"  {finding['code']}  {finding['chapter']}  — {finding['message']}")
    else:
        print("\n✓ No revision flags raised.")


if __name__ == "__main__":
    main()
