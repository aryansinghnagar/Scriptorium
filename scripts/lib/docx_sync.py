#!/usr/bin/env python3
"""
Ars Arcanum DOCX Synchronization & Typesetting Engine (scripts/lib/docx_sync.py)
================================================================================
Bidirectional Word processor synchronization and native OpenXML manuscript generator.
Enables authors to draft, review, and edit manuscripts seamlessly in Microsoft Word,
Google Docs, and LibreOffice Writer while preserving Markdown integrity.

Zero external dependencies; operates 100% offline.
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("arcanum.docx_sync")

try:
    from lib.config import get_active_docx_preset_name, get_docx_config
except Exception:
    try:
        from config import get_active_docx_preset_name, get_docx_config
    except Exception:
        def get_docx_config():
            return {
                "name": "Standard Submission (Shunn / Industry)",
                "font_family": "Times New Roman",
                "font_size_pt": 12.0,
                "line_spacing": 2.0,
                "margin_inches": 1.0,
                "first_line_indent_inches": 0.5,
                "scene_break_symbol": "#",
                "page_break_chapters": True,
                "include_header_slug": True,
            }
        def get_active_docx_preset_name():
            return "standard-submission"


FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
NW_TAG_REGEX = re.compile(r"^@[A-Za-z0-9_-]+:", re.MULTILINE)
MD_BOLD_ITALIC_REGEX = re.compile(r"(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|___[^_]+___|__[^_]+__|_[^_]+_)")
_ILLEGAL_XML_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def escape_xml(text: str) -> str:
    """Escapes XML special characters and strips illegal XML 1.0 control characters."""
    clean = _ILLEGAL_XML_CHARS.sub("", str(text))
    return (
        clean
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def inches_to_dxa(inches: float) -> int:
    """Converts inches to twentieths of a point (dxa). 1 in = 1440 dxa."""
    return round(inches * 1440)


def pt_to_half_pt(pt: float) -> int:
    """Converts points to half-points. 12 pt = 24."""
    return round(pt * 2)


def line_spacing_to_val(line_spacing: float) -> tuple:
    """Returns (w:line, w:lineRule) for Word OpenXML paragraph spacing."""
    if line_spacing >= 2.0:
        return (480, "auto")
    elif line_spacing >= 1.5:
        return (360, "auto")
    elif line_spacing >= 1.3:
        return (round(240 * line_spacing), "auto")
    else:
        return (240, "auto")


def strip_scene_tags_and_frontmatter(text: str) -> tuple:
    """Strips YAML frontmatter and novelWriter metadata tags from prose.
    
    Returns (clean_prose, metadata_dict, raw_header_lines)
    """
    metadata = {}
    header_lines = []
    
    # Extract YAML frontmatter if present
    clean_text = text
    fm_match = FRONTMATTER_REGEX.match(text)
    if fm_match:
        fm_content = fm_match.group(1)
        for line in fm_content.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip().lower()] = v.strip().strip("\"'")
        clean_text = FRONTMATTER_REGEX.sub("", text, count=1)

    prose_lines = []
    for line in clean_text.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("@") and NW_TAG_REGEX.match(trimmed):
            header_lines.append(trimmed)
            if ":" in trimmed:
                tag_name, tag_val = trimmed[1:].split(":", 1)
                metadata[tag_name.strip().lower()] = tag_val.strip().strip("\"'")
        elif trimmed.startswith("%"):
            # Comment line
            header_lines.append(trimmed)
        else:
            prose_lines.append(line)

    return ("\n".join(prose_lines), metadata, header_lines)


def parse_markdown_to_paragraphs(md_text: str) -> list:
    """Parses markdown text into structured paragraph tokens for DOCX generation."""
    clean_text, _, _ = strip_scene_tags_and_frontmatter(md_text)
    paragraphs = []
    
    # Split by blank lines or multiple newlines
    raw_blocks = re.split(r"\n\s*\n", clean_text)
    for block in raw_blocks:
        b = block.strip()
        if not b:
            continue
        
        # Check for headings
        if b.startswith("# "):
            paragraphs.append({"type": "heading1", "text": b[2:].strip()})
        elif b.startswith("## "):
            paragraphs.append({"type": "heading2", "text": b[3:].strip()})
        elif b.startswith("### "):
            paragraphs.append({"type": "heading3", "text": b[4:].strip()})
        elif b in ("#", "* * *", "***", "---", "___", "- - -"):
            paragraphs.append({"type": "scene_break", "text": b})
        else:
            # Body paragraph with potential inline formatting
            # Join single line breaks within a paragraph with space
            single_line_text = " ".join([ln.strip() for ln in b.splitlines() if ln.strip()])
            paragraphs.append({"type": "body", "text": single_line_text})
            
    return paragraphs


def format_runs_xml(text: str, font_family: str, font_size_half_pt: int) -> str:
    """Parses inline Markdown formatting (**bold**, *italic*) and returns OpenXML <w:r> tags."""
    runs_xml = []
    
    # Tokenize text by markdown delimiters
    tokens = re.split(r"(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|___[^_]+___|__[^_]+__|_[^_]+_)", text)
    
    for tok in tokens:
        if not tok:
            continue
        
        is_bold = False
        is_italic = False
        inner_text = tok
        
        if (tok.startswith("***") and tok.endswith("***")) or (tok.startswith("___") and tok.endswith("___")):
            is_bold = True
            is_italic = True
            inner_text = tok[3:-3]
        elif (tok.startswith("**") and tok.endswith("**")) or (tok.startswith("__") and tok.endswith("__")):
            is_bold = True
            inner_text = tok[2:-2]
        elif (tok.startswith("*") and tok.endswith("*")) or (tok.startswith("_") and tok.endswith("_")):
            is_italic = True
            inner_text = tok[1:-1]
            
        rpr_parts = [
            f'<w:rFonts w:ascii="{escape_xml(font_family)}" w:hAnsi="{escape_xml(font_family)}" w:cs="{escape_xml(font_family)}"/>',
            f'<w:sz w:val="{font_size_half_pt}"/>',
            f'<w:szCs w:val="{font_size_half_pt}"/>',
        ]
        if is_bold:
            rpr_parts.append('<w:b/><w:bCs/>')
        if is_italic:
            rpr_parts.append('<w:i/><w:iCs/>')
            
        rpr_str = "".join(rpr_parts)
        t_xml = f'<w:t xml:space="preserve">{escape_xml(inner_text)}</w:t>'
        runs_xml.append(f'<w:r><w:rPr>{rpr_str}</w:rPr>{t_xml}</w:r>')
        
    return "".join(runs_xml)


def generate_docx_xml_body(parsed_paragraphs: list, config: dict, is_full_manuscript: bool = False) -> str:
    """Generates the OpenXML <w:body> XML string from parsed paragraphs."""
    font_family = config.get("font_family", "Times New Roman")
    font_size_pt = float(config.get("font_size_pt", 12.0))
    font_size_half_pt = pt_to_half_pt(font_size_pt)
    heading1_size_half_pt = pt_to_half_pt(font_size_pt + 4.0)
    heading2_size_half_pt = pt_to_half_pt(font_size_pt + 2.0)
    
    line_spacing = float(config.get("line_spacing", 2.0))
    line_val, line_rule = line_spacing_to_val(line_spacing)
    
    margin_in = float(config.get("margin_inches", 1.0))
    margin_dxa = inches_to_dxa(margin_in)
    
    indent_in = float(config.get("first_line_indent_inches", 0.5))
    indent_dxa = inches_to_dxa(indent_in)
    
    scene_break_sym = config.get("scene_break_symbol", "#")
    page_break_chapters = bool(config.get("page_break_chapters", True))
    
    body_xml_parts = []
    chapter_index = 0
    
    for p in parsed_paragraphs:
        ptype = p["type"]
        ptext = p["text"]
        
        if ptype == "heading1":
            chapter_index += 1
            pPr_parts = [
                '<w:pStyle w:val="Heading1"/>',
                '<w:jc w:val="center"/>',
                f'<w:spacing w:before="720" w:after="360" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            # Add page break before subsequent chapters in full manuscript
            if is_full_manuscript and chapter_index > 1 and page_break_chapters:
                pPr_parts.append('<w:pageBreakBefore/>')
                
            r_xml = format_runs_xml(ptext, font_family, heading1_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')
            
        elif ptype == "heading2":
            pPr_parts = [
                '<w:pStyle w:val="Heading2"/>',
                '<w:jc w:val="left"/>',
                f'<w:spacing w:before="360" w:after="180" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            r_xml = format_runs_xml(ptext, font_family, heading2_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')
            
        elif ptype == "heading3":
            pPr_parts = [
                '<w:pStyle w:val="Heading3"/>',
                '<w:jc w:val="left"/>',
                f'<w:spacing w:before="240" w:after="120" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            r_xml = format_runs_xml(ptext, font_family, font_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')
            
        elif ptype == "scene_break":
            # Centered scene break
            symbol = scene_break_sym if scene_break_sym else "#"
            pPr_parts = [
                '<w:jc w:val="center"/>',
                f'<w:spacing w:before="360" w:after="360" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            r_xml = format_runs_xml(symbol, font_family, font_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')
            
        else:
            # Body paragraph
            pPr_parts = [
                f'<w:ind w:firstLine="{indent_dxa}"/>',
                f'<w:spacing w:before="0" w:after="0" w:line="{line_val}" w:lineRule="{line_rule}"/>',
                '<w:jc w:val="both"/>',
            ]
            r_xml = format_runs_xml(ptext, font_family, font_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')
            
    # Section properties (Page layout, size & margins)
    # Letter / Trade size: 8.5 x 11 inches = 12240 x 15840 dxa
    sect_pr = (
        f'<w:sectPr>'
        f'<w:pgSz w:w="12240" w:h="15840"/>'
        f'<w:pgMar w:top="{margin_dxa}" w:right="{margin_dxa}" w:bottom="{margin_dxa}" w:left="{margin_dxa}" w:header="720" w:footer="720" w:gutter="0"/>'
        f'<w:cols w:space="720"/>'
        f'<w:docGrid w:linePitch="360"/>'
        f'</w:sectPr>'
    )
    body_xml_parts.append(sect_pr)
    
    return "".join(body_xml_parts)


def build_docx_package(output_path: Path, parsed_paragraphs: list, config: dict, title: str = "", author: str = "", is_full_manuscript: bool = False) -> bool:
    """Builds a fully compliant OpenXML .docx file package."""
    font_family = config.get("font_family", "Times New Roman")
    font_size_pt = float(config.get("font_size_pt", 12.0))
    font_size_half_pt = pt_to_half_pt(font_size_pt)
    
    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

    word_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    styles_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="{escape_xml(font_family)}" w:hAnsi="{escape_xml(font_family)}" w:cs="{escape_xml(font_family)}"/>
        <w:sz w:val="{font_size_half_pt}"/>
        <w:szCs w:val="{font_size_half_pt}"/>
        <w:lang w:val="en-US"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault/>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="{font_size_half_pt + 8}"/>
      <w:szCs w:val="{font_size_half_pt + 8}"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="{font_size_half_pt + 4}"/>
      <w:szCs w:val="{font_size_half_pt + 4}"/>
    </w:rPr>
  </w:style>
</w:styles>"""

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core_props_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape_xml(title)}</dc:title>
  <dc:creator>{escape_xml(author or 'Author')}</dc:creator>
  <cp:lastModifiedBy>Ars Arcanum</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now_iso}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now_iso}</dcterms:modified>
</cp:coreProperties>"""

    app_props_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Ars Arcanum</Application>
  <DocSecurity>0</DocSecurity>
  <Company>Ars Arcanum Studio</Company>
</Properties>"""

    body_xml = generate_docx_xml_body(parsed_paragraphs, config, is_full_manuscript=is_full_manuscript)
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body_xml}
  </w:body>
</w:document>"""

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_zip = output_path.with_suffix(".docx.tmp")
        
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_xml)
            zf.writestr("_rels/.rels", root_rels_xml)
            zf.writestr("word/_rels/document.xml.rels", word_rels_xml)
            zf.writestr("word/document.xml", document_xml)
            zf.writestr("word/styles.xml", styles_xml)
            zf.writestr("docProps/core.xml", core_props_xml)
            zf.writestr("docProps/app.xml", app_props_xml)
            
        if tmp_zip.is_file():
            tmp_zip.replace(output_path)
            return True
    except Exception as e:
        logger.error("Failed to compile DOCX package at %s: %s", output_path, e)
        if tmp_zip.is_file():
            tmp_zip.unlink(missing_ok=True)
            
    return False


MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024  # 50 MB safety limit
MAX_DOCX_FILE_BYTES = 20 * 1024 * 1024  # 20 MB safety limit


def convert_docx_to_markdown(docx_path: Path) -> str:
    """Extracts prose from a DOCX file and converts it into clean Markdown."""
    if not docx_path.is_file():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
    if docx_path.stat().st_size > MAX_DOCX_FILE_BYTES:
        raise ValueError(f"DOCX file exceeds maximum allowed size ({MAX_DOCX_FILE_BYTES // (1024*1024)} MB): {docx_path}")
        
    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            total_uncompressed = sum(info.file_size for info in zf.infolist())
            if total_uncompressed > MAX_DOCX_UNCOMPRESSED_BYTES:
                raise ValueError(f"DOCX uncompressed payload exceeds safety threshold ({MAX_DOCX_UNCOMPRESSED_BYTES // (1024*1024)} MB)")
            doc_xml_bytes = zf.read("word/document.xml")
            
        if b"<!ENTITY" in doc_xml_bytes or b"<!DOCTYPE" in doc_xml_bytes:
            raise ValueError("Unsafe XML entity/DOCTYPE declaration detected in DOCX document.xml")
            
        root = ET.fromstring(doc_xml_bytes)  # noqa: S314
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        
        md_paragraphs = []
        for p in root.iter(f"{{{ns['w']}}}p"):
            # Check for style
            pPr = p.find(f"{{{ns['w']}}}pPr")
            style_val = ""
            if pPr is not None:
                pStyle = pPr.find(f"{{{ns['w']}}}pStyle")
                if pStyle is not None:
                    style_val = pStyle.attrib.get(f"{{{ns['w']}}}val", "").lower()
                    
            p_runs = []
            for r in p.iter(f"{{{ns['w']}}}r"):
                rPr = r.find(f"{{{ns['w']}}}rPr")
                is_bold = rPr is not None and rPr.find(f"{{{ns['w']}}}b") is not None
                is_italic = rPr is not None and rPr.find(f"{{{ns['w']}}}i") is not None
                
                t_elem = r.find(f"{{{ns['w']}}}t")
                if t_elem is not None and t_elem.text:
                    r_text = t_elem.text
                    if is_bold and is_italic:
                        p_runs.append(f"***{r_text}***")
                    elif is_bold:
                        p_runs.append(f"**{r_text}**")
                    elif is_italic:
                        p_runs.append(f"*{r_text}*")
                    else:
                        p_runs.append(r_text)
                        
            p_text = "".join(p_runs).strip()
            if not p_text:
                continue
                
            if "heading1" in style_val or "heading 1" in style_val:
                md_paragraphs.append(f"# {p_text}")
            elif "heading2" in style_val or "heading 2" in style_val:
                md_paragraphs.append(f"## {p_text}")
            elif "heading3" in style_val or "heading 3" in style_val:
                md_paragraphs.append(f"### {p_text}")
            elif p_text in ("#", "* * *", "***", "---"):
                md_paragraphs.append("* * *")
            else:
                md_paragraphs.append(p_text)
                
        return "\n\n".join(md_paragraphs) + "\n"
        
    except Exception as e:
        logger.error("Failed to convert DOCX to Markdown for %s: %s", docx_path, e)
        raise


def resolve_active_draft_dir(manuscript_dir: Path, requested_draft: str | None = None) -> Path:
    """Finds the active or requested draft directory in a manuscript project."""
    ms_dir = manuscript_dir / "01-Manuscript" if (manuscript_dir / "01-Manuscript").is_dir() else manuscript_dir
    
    # Check volume Book-01 or books
    book_dirs = sorted([d for d in ms_dir.glob("Book-*") if d.is_dir()])
    target_vol = book_dirs[0] if book_dirs else ms_dir
    
    draft_dirs = sorted([d for d in target_vol.glob("Draft-*") if d.is_dir()])
    if not draft_dirs:
        return target_vol
        
    if requested_draft:
        match = [d for d in draft_dirs if d.name.lower() == requested_draft.lower()]
        if match:
            return match[0]
            
    # Check manifest
    manifest = manuscript_dir / "manuscript.yaml"
    if manifest.is_file():
        try:
            content = manifest.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("active_draft:"):
                    ad = line.split(":", 1)[1].strip().strip("\"'")
                    match = [d for d in draft_dirs if d.name.lower() == ad.lower()]
                    if match:
                        return match[0]
        except Exception:
            pass
            
    return draft_dirs[-1]


def build_manuscript_docx(manuscript_dir: Path, draft_name: str | None = None, preset_name: str | None = None) -> dict:
    """Builds both per-chapter .docx files and consolidated draft .docx files for a manuscript."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    config = get_docx_config()
    
    # Read title and author from manifest
    title = mpath.name
    author = "Author"
    manifest = mpath / "manuscript.yaml"
    if manifest.is_file():
        try:
            content = manifest.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip("\"'")
                elif line.startswith("author:"):
                    author = line.split(":", 1)[1].strip().strip("\"'")
        except Exception:
            pass

    results = {
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "chapters_built": [],
        "consolidated_built": None,
        "errors": []
    }
    
    consolidated_paragraphs = []
    
    # Find all Markdown scenes
    md_files = sorted(draft_dir.rglob("*.md"))
    valid_scenes = [f for f in md_files if not f.name.startswith(".") and "Outlines" not in f.parts]
    
    for scene_file in valid_scenes:
        try:
            content = scene_file.read_text(encoding="utf-8", errors="replace")
            parsed = parse_markdown_to_paragraphs(content)
            if not parsed:
                continue
                
            # If no heading1 present, add scene title as heading1
            if not any(p["type"] == "heading1" for p in parsed):
                clean_title = scene_file.stem.replace("_", " ").replace("-", " ")
                # Strip leading numbers (e.g. 01 Chapter 01 -> Chapter 01)
                clean_title = re.sub(r"^\d+\s*", "", clean_title)
                parsed.insert(0, {"type": "heading1", "text": clean_title})
                
            # 1. Build individual chapter .docx
            ch_docx_path = scene_file.with_suffix(".docx")
            if build_docx_package(ch_docx_path, parsed, config, title=title, author=author, is_full_manuscript=False):
                results["chapters_built"].append(str(ch_docx_path.relative_to(mpath)).replace("\\", "/"))
                
            # Accumulate for consolidated draft manuscript
            consolidated_paragraphs.extend(parsed)
            
        except Exception as e:
            err = f"Failed to build chapter DOCX for {scene_file}: {e}"
            logger.error(err)
            results["errors"].append(err)
            
    # 2. Build consolidated full draft .docx
    if consolidated_paragraphs:
        draft_label = draft_dir.name if draft_dir.name.startswith("Draft-") else "Draft-01"
        consolidated_docx_name = f"{draft_label}_Manuscript.docx"
        consolidated_path = draft_dir / consolidated_docx_name
        
        if build_docx_package(consolidated_path, consolidated_paragraphs, config, title=title, author=author, is_full_manuscript=True):
            results["consolidated_built"] = str(consolidated_path.relative_to(mpath)).replace("\\", "/")
            
    return results


def get_file_sha256(path: Path) -> str:
    """Calculates SHA-256 hash of a file."""
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_sync_state(draft_dir: Path) -> dict:
    state_file = draft_dir / ".sync_state.json"
    if state_file.is_file():
        try:
            with open(state_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.debug("Failed to read sync state %s: %s", state_file, e)
    return {}


def save_sync_state(draft_dir: Path, state: dict) -> None:
    state_file = draft_dir / ".sync_state.json"
    atomic_write(state_file, json.dumps(state, indent=2))


def sync_manuscript_docx(manuscript_dir: Path, draft_name: str | None = None) -> dict:
    """Performs 3-way hash-verified bidirectional synchronization between .md and .docx files."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    config = get_docx_config()
    
    sync_report = {
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "md_to_docx": [],
        "docx_to_md": [],
        "conflicts": [],
        "errors": []
    }
    
    state = load_sync_state(draft_dir)
    state_updated = False
    
    # 1. Discover all pairs
    md_files = {f.stem: f for f in draft_dir.rglob("*.md") if not f.name.startswith(".") and "Outlines" not in f.parts}
    docx_files = {f.stem: f for f in draft_dir.rglob("*.docx") if not f.name.startswith(".") and not f.stem.endswith("_Manuscript")}
    
    all_stems = set(md_files.keys()).union(set(docx_files.keys()))
    
    for stem in sorted(all_stems):
        md_path = md_files.get(stem)
        docx_path = docx_files.get(stem)
        stem_state = state.get(stem, {})
        stored_md_hash = stem_state.get("md_sha256")
        stored_docx_hash = stem_state.get("docx_sha256")
        
        if md_path and not docx_path:
            # MD exists, DOCX missing -> Build DOCX
            target_docx = md_path.with_suffix(".docx")
            try:
                content = md_path.read_text(encoding="utf-8", errors="replace")
                parsed = parse_markdown_to_paragraphs(content)
                if not any(p["type"] == "heading1" for p in parsed):
                    clean_title = re.sub(r"^\d+\s*", "", md_path.stem.replace("_", " ").replace("-", " "))
                    parsed.insert(0, {"type": "heading1", "text": clean_title})
                if build_docx_package(target_docx, parsed, config, title=mpath.name, is_full_manuscript=False):
                    sync_report["md_to_docx"].append(str(target_docx.relative_to(mpath)).replace("\\", "/"))
                    state[stem] = {
                        "md_sha256": get_file_sha256(md_path),
                        "docx_sha256": get_file_sha256(target_docx),
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    }
                    state_updated = True
            except Exception as e:
                sync_report["errors"].append(f"Error compiling {target_docx}: {e}")
                
        elif docx_path and not md_path:
            # DOCX exists, MD missing -> Import to MD
            target_md = docx_path.with_suffix(".md")
            try:
                prose = convert_docx_to_markdown(docx_path)
                atomic_write(target_md, prose)
                sync_report["docx_to_md"].append(str(target_md.relative_to(mpath)).replace("\\", "/"))
                state[stem] = {
                    "md_sha256": get_file_sha256(target_md),
                    "docx_sha256": get_file_sha256(docx_path),
                    "synced_at": datetime.now(timezone.utc).isoformat()
                }
                state_updated = True
            except Exception as e:
                sync_report["errors"].append(f"Error importing {docx_path}: {e}")
                
        elif md_path and docx_path:
            cur_md_hash = get_file_sha256(md_path)
            cur_docx_hash = get_file_sha256(docx_path)
            
            md_changed = (stored_md_hash is not None and cur_md_hash != stored_md_hash)
            docx_changed = (stored_docx_hash is not None and cur_docx_hash != stored_docx_hash)
            
            # Initial baseline when no state was recorded
            if stored_md_hash is None or stored_docx_hash is None:
                md_mtime = md_path.stat().st_mtime
                docx_mtime = docx_path.stat().st_mtime
                if docx_mtime > md_mtime + 2.0:
                    docx_changed = True
                elif md_mtime > docx_mtime + 2.0:
                    md_changed = True
                else:
                    state[stem] = {
                        "md_sha256": cur_md_hash,
                        "docx_sha256": cur_docx_hash,
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    }
                    state_updated = True
                    continue
            
            if md_changed and docx_changed:
                # Conflict detected! Do not overwrite either file.
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                conflict_md = md_path.parent / f"{md_path.stem}.conflict_{ts}.md"
                new_prose = convert_docx_to_markdown(docx_path)
                atomic_write(conflict_md, f"<!-- SYNC CONFLICT from {docx_path.name} -->\n\n{new_prose}")
                sync_report["conflicts"].append({
                    "stem": stem,
                    "md_file": str(md_path.relative_to(mpath)).replace("\\", "/"),
                    "docx_file": str(docx_path.relative_to(mpath)).replace("\\", "/"),
                    "conflict_file": str(conflict_md.relative_to(mpath)).replace("\\", "/")
                })
                logger.warning("Sync conflict on %s: both Markdown and DOCX modified independently.", stem)
            elif docx_changed:
                # DOCX was updated in Word Processor -> Update MD prose while preserving tags
                try:
                    old_content = md_path.read_text(encoding="utf-8", errors="replace")
                    _, _, raw_headers = strip_scene_tags_and_frontmatter(old_content)
                    new_prose = convert_docx_to_markdown(docx_path)
                    
                    combined_lines = []
                    if raw_headers:
                        combined_lines.extend(raw_headers)
                        combined_lines.append("")
                    combined_lines.append(new_prose.strip())
                    combined_lines.append("")
                    
                    atomic_write(md_path, "\n".join(combined_lines))
                    state[stem] = {
                        "md_sha256": get_file_sha256(md_path),
                        "docx_sha256": cur_docx_hash,
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    }
                    state_updated = True
                    sync_report["docx_to_md"].append(str(md_path.relative_to(mpath)).replace("\\", "/"))
                except Exception as e:
                    sync_report["errors"].append(f"Error syncing {docx_path} -> {md_path}: {e}")
            elif md_changed:
                # MD was updated in editor -> Rebuild DOCX
                try:
                    content = md_path.read_text(encoding="utf-8", errors="replace")
                    parsed = parse_markdown_to_paragraphs(content)
                    if not any(p["type"] == "heading1" for p in parsed):
                        clean_title = re.sub(r"^\d+\s*", "", md_path.stem.replace("_", " ").replace("-", " "))
                        parsed.insert(0, {"type": "heading1", "text": clean_title})
                    if build_docx_package(docx_path, parsed, config, title=mpath.name, is_full_manuscript=False):
                        state[stem] = {
                            "md_sha256": cur_md_hash,
                            "docx_sha256": get_file_sha256(docx_path),
                            "synced_at": datetime.now(timezone.utc).isoformat()
                        }
                        state_updated = True
                        sync_report["md_to_docx"].append(str(docx_path.relative_to(mpath)).replace("\\", "/"))
                except Exception as e:
                    sync_report["errors"].append(f"Error syncing {md_path} -> {docx_path}: {e}")
            else:
                state[stem] = {
                    "md_sha256": cur_md_hash,
                    "docx_sha256": cur_docx_hash,
                    "synced_at": stem_state.get("synced_at") or datetime.now(timezone.utc).isoformat()
                }
                
    if state_updated:
        save_sync_state(draft_dir, state)
        
    # Update consolidated manuscript DOCX
    build_manuscript_docx(mpath, draft_name=draft_dir.name)
    return sync_report


def open_in_word_processor(file_path: Path) -> bool:
    """Launches the specified DOCX document in the default word processor."""
    fpath = Path(file_path).resolve()
    if not fpath.is_file():
        logger.error("File does not exist: %s", fpath)
        return False
        
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(fpath))  # noqa: S606
            return True
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(fpath)])
            return True
        else:
            # Linux: Check for LibreOffice Writer / word processor
            if shutil.which("libreoffice"):
                subprocess.Popen(["libreoffice", "--writer", str(fpath)])
                return True
            elif shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", str(fpath)])
                return True
    except Exception as e:
        logger.error("Failed to launch word processor for %s: %s", fpath, e)
        
    return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum DOCX Synchronization & Typesetting Engine")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # build
    build_p = subparsers.add_parser("build", help="Build/refresh .docx files for manuscript")
    build_p.add_argument("manuscript", help="Path to manuscript directory")
    build_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01, Draft-02)")
    
    # sync
    sync_p = subparsers.add_parser("sync", help="Bidirectional sync between .docx and .md")
    sync_p.add_argument("manuscript", help="Path to manuscript directory")
    sync_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01)")
    
    # import
    import_p = subparsers.add_parser("import", help="Import external .docx into clean Markdown")
    import_p.add_argument("docx_file", help="Path to source .docx file")
    import_p.add_argument("--to", required=True, help="Target markdown file path")
    
    # open
    open_p = subparsers.add_parser("open", help="Open manuscript in default word processor")
    open_p.add_argument("manuscript", help="Path to manuscript directory")
    open_p.add_argument("-d", "--draft", help="Specific draft name")
    open_p.add_argument("-c", "--chapter", help="Specific chapter file name or path")

    args = parser.parse_args()
    
    if args.subcommand == "build":
        res = build_manuscript_docx(Path(args.manuscript), draft_name=args.draft)
        print("=== Ars Arcanum DOCX Build ===")
        print(f"Manuscript: {res['manuscript']} ({res['draft']})")
        print(f"Chapters Built: {len(res['chapters_built'])}")
        if res['consolidated_built']:
            print(f"Consolidated Draft: {res['consolidated_built']}")
        if res['errors']:
            print(f"Errors: {len(res['errors'])}")
            for err in res['errors']:
                print(f"  [!] {err}")
            sys.exit(1)
        sys.exit(0)
        
    elif args.subcommand == "sync":
        res = sync_manuscript_docx(Path(args.manuscript), draft_name=args.draft)
        print("=== Ars Arcanum DOCX Sync ===")
        print(f"Manuscript: {res['manuscript']} ({res['draft']})")
        print(f"Markdown -> DOCX Updated: {len(res['md_to_docx'])}")
        print(f"DOCX -> Markdown Updated: {len(res['docx_to_md'])}")
        if res['errors']:
            print(f"Errors: {len(res['errors'])}")
            for err in res['errors']:
                print(f"  [!] {err}")
            sys.exit(1)
        sys.exit(0)
        
    elif args.subcommand == "import":
        try:
            prose = convert_docx_to_markdown(Path(args.docx_file))
            target_path = Path(args.to)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target_path, prose)
            print(f"[✓] Successfully imported {args.docx_file} -> {args.to}")
            sys.exit(0)
        except Exception as e:
            print(f"[!] Error importing DOCX: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.subcommand == "open":
        mpath = Path(args.manuscript).resolve()
        draft_dir = resolve_active_draft_dir(mpath, args.draft)
        target_file = None
        
        if args.chapter:
            ch_candidates = list(draft_dir.rglob(f"*{args.chapter}*.docx"))
            if ch_candidates:
                target_file = ch_candidates[0]
                
        if not target_file:
            # Check consolidated draft docx
            cons = list(draft_dir.glob("*_Manuscript.docx"))
            if cons:
                target_file = cons[0]
            else:
                docxs = list(draft_dir.rglob("*.docx"))
                if docxs:
                    target_file = docxs[0]
                    
        if target_file and target_file.is_file():
            print(f"Launching word processor for: {target_file}")
            if open_in_word_processor(target_file):
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            # Build first if missing
            print("No .docx files found. Generating .docx package first...")
            build_manuscript_docx(mpath, draft_name=args.draft)
            cons = list(draft_dir.glob("*_Manuscript.docx"))
            if cons:
                open_in_word_processor(cons[0])
                sys.exit(0)
            sys.exit(1)


if __name__ == "__main__":
    main()
