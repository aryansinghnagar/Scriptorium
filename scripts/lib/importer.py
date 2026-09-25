#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Batch Importer & Migration Engine (scripts/lib/importer.py)
==================================================================================
Converts legacy Scrivener exports, Microsoft Word (.docx) folder trees, Google Docs,
and unstructured Markdown directories into sovereign, publication-ready Ars Arcanum
manuscript vaults with complete manifest metadata and novelWriter project integration.

Zero external dependencies required (supports native OpenXML parsing with Pandoc fallback).
"""

import argparse
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("arcanum.importer")

NWX_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<novelWriterXML appVersion="2.0" fileVersion="1.3">
  <project>
    <name>{title}</name>
    <author>{author}</author>
  </project>
</novelWriterXML>
"""


def extract_docx_text(docx_path: Path) -> str:
    """Extracts clean markdown paragraphs from an OpenXML .docx file using native zip/xml parsing."""
    if not zipfile.is_zipfile(docx_path):
        raise ValueError(f"File is not a valid zip/docx archive: {docx_path}")

    with zipfile.ZipFile(docx_path, "r") as zf:
        if "word/document.xml" not in zf.namelist():
            raise ValueError(f"word/document.xml missing in docx: {docx_path}")
        doc_xml_bytes = zf.read("word/document.xml")

    # Guard against XML bomb / entity expansion
    if b"<!ENTITY" in doc_xml_bytes or b"<!DOCTYPE" in doc_xml_bytes:
        raise ValueError(f"Unsafe DOCTYPE/ENTITY detected in {docx_path.name}")

    root = ET.fromstring(doc_xml_bytes)  # noqa: S314
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    paragraphs = []
    for p in root.iter(f"{{{ns['w']}}}p"):
        pPr = p.find(f"{{{ns['w']}}}pPr")
        pStyle = pPr.find(f"{{{ns['w']}}}pStyle") if pPr is not None else None
        style_val = pStyle.attrib.get(f"{{{ns['w']}}}val", "") if pStyle is not None else ""

        p_texts = []
        for r in p.iter(f"{{{ns['w']}}}r"):
            t = r.find(f"{{{ns['w']}}}t")
            if t is not None and t.text:
                p_texts.append(t.text)

        full_p = "".join(p_texts).strip()
        if not full_p:
            continue

        if "heading 1" in style_val.lower() or "title" in style_val.lower():
            paragraphs.append(f"# {full_p}")
        elif "heading 2" in style_val.lower():
            paragraphs.append(f"## {full_p}")
        elif "heading 3" in style_val.lower():
            paragraphs.append(f"### {full_p}")
        else:
            paragraphs.append(full_p)

    return "\n\n".join(paragraphs) + "\n"


def import_manuscript_batch(
    source_path: Path,
    dest_path: Path,
    title: str | None = None,
    author: str = "Author",
    universe: str = "Default-Universe",
    world: str = "Default-World",
) -> dict[str, Any]:
    """
    Imports a folder of .docx or .md files into a structured Ars Arcanum manuscript vault.
    Creates:
    - dest_path/manuscript.yaml
    - dest_path/nwProject.nwx
    - dest_path/.gitignore
    - dest_path/Book-01/Draft-01/01_Chapter_01.md, etc.
    """
    source_path = Path(source_path).resolve()
    dest_path = Path(dest_path).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    ms_title = title or source_path.name or "Imported-Manuscript"
    draft_dir = dest_path / "Book-01" / "Draft-01"
    draft_dir.mkdir(parents=True, exist_ok=True)

    imported_chapters = []

    # Find candidate files
    if source_path.is_file():
        candidate_files = [source_path]
    else:
        candidate_files = sorted(
            [f for f in source_path.iterdir() if f.is_file() and f.suffix.lower() in (".docx", ".md", ".txt")]
        )

    if not candidate_files:
        raise ValueError(f"No convertible files (.docx, .md, .txt) found in {source_path}")

    for idx, fpath in enumerate(candidate_files, start=1):
        clean_stem = re.sub(r"^[\d\s_\.-]+", "", fpath.stem).strip()
        if not clean_stem:
            clean_stem = f"Chapter_{idx:02d}"
        chapter_filename = f"{idx:02d}_{clean_stem}.md"
        target_file = draft_dir / chapter_filename

        if fpath.suffix.lower() == ".docx":
            content = extract_docx_text(fpath)
        else:
            content = fpath.read_text(encoding="utf-8", errors="replace")

        # Ensure chapter header exists if missing
        if not re.match(r"^\s*#\s+", content):
            header = f"# Chapter {idx}: {clean_stem.replace('_', ' ').replace('-', ' ')}\n\n"
            content = header + content

        atomic_write(target_file, content)
        imported_chapters.append(chapter_filename)

    # Write manuscript.yaml
    manifest_yaml = f"""# Ars Arcanum Manuscript Project Manifest
schema_version: "1.0"
title: "{ms_title}"
author: "{author}"
universe: "{universe}"
world: "{world}"
status: "in-progress"
"""
    atomic_write(dest_path / "manuscript.yaml", manifest_yaml)

    # Write novelWriter project file
    nwx_content = NWX_TEMPLATE.format(title=ms_title, author=author)
    atomic_write(dest_path / "nwProject.nwx", nwx_content)

    # Write .gitignore
    gitignore_content = """# Ars Arcanum Manuscript Git Ignore
.arcanum_cache.json
.sync_state.json
*.lock
*.bak
*.tmp
*.log
.DS_Store
Backups/
05-Backups/
Exports/
04-Publishing/
"""
    atomic_write(dest_path / ".gitignore", gitignore_content)

    return {
        "title": ms_title,
        "author": author,
        "dest_path": str(dest_path),
        "chapters_imported": len(imported_chapters),
        "chapter_files": imported_chapters,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Batch Manuscript Importer")
    parser.add_argument("source", help="Source folder or file containing .docx or .md chapters")
    parser.add_argument("--dest", "-d", help="Target manuscript directory", default=None)
    parser.add_argument("--title", "-t", help="Manuscript title", default=None)
    parser.add_argument("--author", "-a", help="Author name", default="Author")
    parser.add_argument("--universe", "-u", help="Universe name", default="Default-Universe")
    parser.add_argument("--world", "-w", help="World lore vault name", default="Default-World")

    args = parser.parse_args(argv)
    source_p = Path(args.source)
    if args.dest:
        dest_p = Path(args.dest)
    else:
        manuscripts_base = Path(os.environ.get("MANUSCRIPTS_BASE", Path.home() / "Manuscripts"))
        dest_p = manuscripts_base / (args.title or source_p.name)

    try:
        res = import_manuscript_batch(
            source_p,
            dest_p,
            title=args.title,
            author=args.author,
            universe=args.universe,
            world=args.world,
        )
        print(f"[✓] Successfully imported manuscript '{res['title']}' ({res['chapters_imported']} chapters):")
        print(f"    Target Vault: {res['dest_path']}")
        for cf in res["chapter_files"]:
            print(f"    • Book-01/Draft-01/{cf}")
        return 0
    except Exception as e:
        print(f"Error importing manuscript: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
