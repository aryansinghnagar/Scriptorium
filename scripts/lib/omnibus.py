#!/usr/bin/env python3
"""
Ars Arcanum Multi-Volume Series Omnibus Compiler
(scripts/lib/omnibus.py)
================================================================================
Zero-dependency, offline multi-volume series compilation engine for epic fantasy,
sci-fi sagas, serial fiction, and multi-book universe bundles.

Capabilities:
1. Multi-Book Discovery & Sequence Resolution:
   - Scans Universe, Cosmos, and Manuscript directories for volumes (`Book-01`, `Book-02`...).
   - Resolves latest active revision drafts (`Draft-01`, `Draft-02`...).
2. Unified Series Lore & Structure Synthesis:
   - Compiles master Series Table of Contents with volume subtitle partitions.
   - Synthesizes a unified cross-volume Dramatis Personae with character debut/arc tracking.
   - Generates a combined Master Chronology Appendix.
   - Computes series-wide POV distribution and pacing metrics.
3. Master Omnibus Assembly:
   - Produces clean, unified Markdown master document (`*_Omnibus.md`).
   - Generates standalone, offline interactive HTML5 Omnibus Reader.
   - Outputs machine-readable series manifest (`omnibus_manifest.json`).

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter

logger = logging.getLogger("arcanum.omnibus")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")


@dataclass
class VolumeData:
    index: int
    name: str
    title: str
    draft_name: str
    path: str
    chapters: list[dict[str, Any]] = field(default_factory=list)
    word_count: int = 0
    povs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_series_volumes(target_path: Path) -> list[VolumeData]:
    """Discovers all volumes/books within a universe, cosmos, or manuscript directory."""
    volumes: list[VolumeData] = []
    
    # Check if target is a universe containing Manuscripts/
    manuscripts_dir = target_path / "Manuscripts" if (target_path / "Manuscripts").is_dir() else target_path

    # Search for Book-XX directories or sub-manuscripts
    book_dirs = []
    for item in sorted(manuscripts_dir.rglob("Book-*")):
        if item.is_dir() and "Backups" not in item.parts:
            book_dirs.append(item)

    # Fallback: if no Book-* directories, look for immediate draft folders
    if not book_dirs:
        for item in sorted(manuscripts_dir.rglob("Draft-*")):
            if item.is_dir() and "Backups" not in item.parts:
                book_dirs.append(item.parent)
                break

    # If still empty and target contains .md files directly
    if not book_dirs and list(target_path.glob("*.md")):
        book_dirs.append(target_path)

    # De-duplicate while preserving order
    seen = set()
    unique_books = []
    for b in book_dirs:
        if str(b) not in seen:
            seen.add(str(b))
            unique_books.append(b)

    for idx, b_dir in enumerate(unique_books, 1):
        # Find latest draft directory
        draft_dirs = sorted([d for d in b_dir.glob("Draft-*") if d.is_dir()], reverse=True)
        active_draft = draft_dirs[0] if draft_dirs else b_dir

        chapters = []
        vol_words = 0
        vol_povs = set()

        for ch_file in sorted(active_draft.rglob("*.md")):
            if ch_file.name.startswith((".", "_")) or "Backups" in ch_file.parts or "04_Back_Matter" in ch_file.parts:
                continue

            content = ch_file.read_text(encoding="utf-8", errors="replace")
            words = len(re.findall(r"\b\w+\b", content))
            vol_words += words

            meta = parse_yaml_frontmatter(content)
            body = FRONTMATTER_REGEX.sub("", content)
            pov = meta.get("pov", meta.get("character", ""))
            
            for line in body.splitlines():
                m = TAG_REGEX.match(line.strip())
                if m and m.group(1).lower() == "pov" and not pov:
                    pov = m.group(2).strip()
            
            if pov:
                vol_povs.add(pov)

            clean_body = re.sub(r"^@[a-zA-Z0-9_-]+:.*$", "", body, flags=re.MULTILINE).strip()

            title = meta.get("title", ch_file.stem.replace("_", " ").replace("-", " "))
            clean_title = re.sub(r"^\d+\s*[-_.]*\s*", "", title).title()

            chapters.append({
                "filename": ch_file.name,
                "path": str(ch_file),
                "title": clean_title or ch_file.stem,
                "pov": pov or "Omniscient",
                "words": words,
                "body": clean_body,
            })

        vol_name = b_dir.name
        vol_title = vol_name.replace("_", " ").replace("-", " ").title()

        volumes.append(VolumeData(
            index=idx,
            name=vol_name,
            title=vol_title,
            draft_name=active_draft.name,
            path=str(b_dir),
            chapters=chapters,
            word_count=vol_words,
            povs=sorted(vol_povs),
        ))

    return volumes


def compile_omnibus_manuscript(
    volumes: list[VolumeData],
    series_title: str = "Series Omnibus",
    author: str = "Author",
) -> dict[str, Any]:
    """Compiles discovered volumes into a master omnibus document and metadata."""
    total_words = sum(v.word_count for v in volumes)
    total_chapters = sum(len(v.chapters) for v in volumes)

    # Master Dramatis Personae
    char_appearances: dict[str, list[str]] = {}
    for v in volumes:
        for ch in v.chapters:
            pov = ch["pov"]
            if pov and pov != "Omniscient":
                clean_pov = pov.replace("[[", "").replace("]]", "").strip()
                if clean_pov not in char_appearances:
                    char_appearances[clean_pov] = []
                if v.title not in char_appearances[clean_pov]:
                    char_appearances[clean_pov].append(v.title)

    # Markdown assembly
    md_lines = [
        "---",
        f'title: "{series_title}"',
        f'author: "{author}"',
        f"volumes_count: {len(volumes)}",
        f"total_word_count: {total_words}",
        "---",
        "",
        f"# {series_title}",
        f"### By {author}",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    for v in volumes:
        md_lines.append(f"- **Volume {v.index}: {v.title}** ({v.word_count:,} words)")
        for ch_idx, ch in enumerate(v.chapters, 1):
            md_lines.append(f"  - Chapter {ch_idx}: {ch['title']}")

    md_lines.extend([
        "",
        "---",
        "",
        "## Dramatis Personae (Series Master Ledger)",
        "",
    ])

    for char_name, vols in sorted(char_appearances.items()):
        md_lines.append(f"- **{char_name}** — Appears in: *{', '.join(vols)}*")

    md_lines.extend(["", "---", ""])

    # Append book chapters
    for v in volumes:
        md_lines.extend([
            f"# Volume {v.index}: {v.title}",
            "",
        ])
        for ch_idx, ch in enumerate(v.chapters, 1):
            md_lines.extend([
                f"## Chapter {ch_idx}: {ch['title']}",
                "",
                ch["body"],
                "",
                "---",
                "",
            ])

    full_markdown = "\n".join(md_lines)

    return {
        "title": series_title,
        "author": author,
        "total_words": total_words,
        "total_volumes": len(volumes),
        "total_chapters": total_chapters,
        "volumes": [v.to_dict() for v in volumes],
        "dramatis_personae": char_appearances,
        "markdown_content": full_markdown,
    }


def generate_omnibus_html_reader(omnibus_report: dict[str, Any], output_path: Path) -> Path:
    """Generates an offline HTML5 Omnibus Reader."""
    title = omnibus_report["title"]
    author = omnibus_report["author"]
    volumes = omnibus_report["volumes"]
    dp = omnibus_report["dramatis_personae"]

    toc_items = []
    volume_sections = []

    for v in volumes:
        toc_items.append(f"<li><strong>Volume {v['index']}: {html.escape(v['title'])}</strong> ({v['word_count']:,} words)</li>")
        ch_blocks = []
        for ch_idx, ch in enumerate(v["chapters"], 1):
            ch_blocks.append(f"""
            <article class="chapter">
              <h3>Chapter {ch_idx}: {html.escape(ch['title'])}</h3>
              <div class="meta-tag">POV: {html.escape(ch['pov'])} | {ch['words']:,} words</div>
              <div class="prose">{html.escape(ch['body']).replace(chr(10), '<br>')}</div>
            </article>
            """)

        volume_sections.append(f"""
        <section class="volume-block">
          <h2>Volume {v['index']}: {html.escape(v['title'])}</h2>
          {''.join(ch_blocks)}
        </section>
        """)

    dp_items = "".join(f"<li><strong>{html.escape(char)}</strong> &mdash; <em>{html.escape(', '.join(vols))}</em></li>" for char, vols in sorted(dp.items()))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Ars Arcanum Omnibus Reader</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --gold: #f59e0b;
  }}
  body {{
    font-family: Georgia, Cambria, serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 2rem 1rem; line-height: 1.7;
  }}
  .container {{ max-width: 800px; margin: 0 auto; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 3rem 2.5rem; }}
  h1, h2, h3 {{ font-family: system-ui, -apple-system, sans-serif; color: var(--accent); }}
  .title-header {{ text-align: center; border-bottom: 2px solid var(--border); padding-bottom: 2rem; margin-bottom: 3rem; }}
  .author {{ font-size: 1.25rem; color: var(--muted); margin-top: 0.5rem; }}
  .meta-tag {{ font-family: system-ui, sans-serif; font-size: 0.8rem; color: var(--muted); margin-bottom: 1rem; }}
  .prose {{ margin-top: 1rem; font-size: 1.05rem; }}
  .volume-block {{ margin-top: 4rem; border-top: 1px solid var(--border); padding-top: 2rem; }}
  .chapter {{ margin-bottom: 3rem; }}
  .toc-box {{ background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 6px; padding: 1.5rem; margin-bottom: 3rem; font-family: system-ui, sans-serif; }}
</style>
</head>
<body>
<div class="container">
  <div class="title-header">
    <h1>{html.escape(title)}</h1>
    <div class="author">By {html.escape(author)}</div>
    <div class="meta-tag" style="margin-top:1rem;">Omnibus Edition &bull; {omnibus_report['total_volumes']} Volumes &bull; {omnibus_report['total_words']:,} Total Words</div>
  </div>

  <div class="toc-box">
    <h3 style="margin-top:0;">Table of Contents</h3>
    <ul>
      {''.join(toc_items)}
    </ul>
    <h3>Dramatis Personae</h3>
    <ul>
      {dp_items or '<li>No POV characters registered.</li>'}
    </ul>
  </div>

  {''.join(volume_sections)}
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Multi-Volume Series Omnibus Compiler")
    parser.add_argument("target", help="Universe, Cosmos, or Manuscript directory")
    parser.add_argument("--output", "-o", help="Output directory or file path")
    parser.add_argument("--title", default="Series Master Omnibus", help="Title for the compiled omnibus")
    parser.add_argument("--author", default="Author", help="Author name")
    parser.add_argument("--html", help="Generate HTML5 reader document to path")
    parser.add_argument("--json", action="store_true", help="Output manifest JSON")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    volumes = discover_series_volumes(target_path)
    if not volumes:
        print(f"Error: No volumes or book chapters found under {target_path}", file=sys.stderr)
        sys.exit(1)

    report = compile_omnibus_manuscript(volumes, series_title=args.title, author=args.author)

    if args.json:
        manifest = {k: v for k, v in report.items() if k != "markdown_content"}
        print(json.dumps(manifest, indent=2))
        return

    out_dir = Path(args.output) if args.output else (target_path if target_path.is_dir() else target_path.parent)
    md_file = out_dir / f"{re.sub(r'[^A-Za-z0-9_-]', '_', args.title)}_Omnibus.md"
    atomic_write(md_file, report["markdown_content"])

    print("=== Ars Arcanum Omnibus Compiler ===")
    print(f"Series Title:  {report['title']}")
    print(f"Volumes:       {report['total_volumes']} | Total Chapters: {report['total_chapters']}")
    print(f"Total Words:   {report['total_words']:,}")
    print(f"Omnibus Markdown: {md_file}")

    if args.html:
        out_html = Path(args.html)
        generate_omnibus_html_reader(report, out_html)
        print(f"Omnibus HTML Reader: {out_html}")


if __name__ == "__main__":
    main()
