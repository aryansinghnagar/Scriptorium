#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum DOCX Synchronization & Typesetting Engine (scripts/lib/docx_sync.py).
"""

import os
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from lib.config import (
    DOCX_PRESETS, get_docx_config, set_docx_preset, set_docx_option,
    get_active_docx_preset_name, list_docx_presets
)
from lib.docx_sync import (
    parse_markdown_to_paragraphs, strip_scene_tags_and_frontmatter,
    build_docx_package, convert_docx_to_markdown,
    build_manuscript_docx, sync_manuscript_docx, escape_xml
)


class TestDocxSyncEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_docx_presets_and_config(self):
        """Test preset retrieval, switching, and custom options."""
        presets = list_docx_presets()
        self.assertIn("standard-submission", presets)
        self.assertIn("modern-manuscript", presets)
        self.assertIn("classic-trade", presets)
        self.assertIn("custom", presets)

        self.assertTrue(set_docx_preset("modern-manuscript"))
        self.assertEqual(get_active_docx_preset_name(), "modern-manuscript")
        cfg = get_docx_config()
        self.assertEqual(cfg["font_family"], "Georgia")
        self.assertEqual(cfg["active_preset"], "modern-manuscript")

        # Custom override
        self.assertTrue(set_docx_option("font_size_pt", 14.0))
        cfg_custom = get_docx_config()
        self.assertEqual(cfg_custom["font_size_pt"], 14.0)
        self.assertEqual(cfg_custom["active_preset"], "custom")

        # Reset to standard submission
        self.assertTrue(set_docx_preset("standard-submission"))
        self.assertEqual(get_active_docx_preset_name(), "standard-submission")

    def test_strip_scene_tags_and_frontmatter(self):
        """Test tag and frontmatter extraction without corrupting prose."""
        sample_md = """---
title: "The Archon's Keep"
status: draft
---
@pov: Kaelen
@location: High Citadel
@thread: Arcane Heist
% Internal author scratchpad comment

# Chapter 1: The Inciting Spark

The bells of the citadel tolled three times in the freezing rain.

* * *

He crept along the parapet without making a sound.
"""
        prose, meta, headers = strip_scene_tags_and_frontmatter(sample_md)
        self.assertEqual(meta.get("title"), "The Archon's Keep")
        self.assertEqual(meta.get("pov"), "Kaelen")
        self.assertEqual(meta.get("location"), "High Citadel")
        self.assertEqual(meta.get("thread"), "Arcane Heist")
        self.assertIn("@pov: Kaelen", headers)
        self.assertIn("% Internal author scratchpad comment", headers)
        self.assertNotIn("@pov:", prose)
        self.assertNotIn("@location:", prose)
        self.assertIn("# Chapter 1: The Inciting Spark", prose)
        self.assertIn("The bells of the citadel", prose)

    def test_parse_markdown_to_paragraphs(self):
        """Test Markdown block parsing into structured paragraph tokens."""
        md = """# Chapter 1

First body paragraph with **bold text** and *italic words*.

## Scene 1

Another paragraph.

* * *

Final scene after break.
"""
        paragraphs = parse_markdown_to_paragraphs(md)
        self.assertEqual(len(paragraphs), 6)
        self.assertEqual(paragraphs[0]["type"], "heading1")
        self.assertEqual(paragraphs[0]["text"], "Chapter 1")
        self.assertEqual(paragraphs[1]["type"], "body")
        self.assertIn("**bold text**", paragraphs[1]["text"])
        self.assertEqual(paragraphs[2]["type"], "heading2")
        self.assertEqual(paragraphs[3]["type"], "body")
        self.assertEqual(paragraphs[4]["type"], "scene_break")
        self.assertEqual(paragraphs[5]["type"], "body")

    def test_build_and_extract_docx_package(self):
        """Test compiling OpenXML .docx file and verifying internal structure."""
        out_docx = self.root / "Test_Chapter.docx"
        md = """# The Awakening

The ancient runes glowed softly in the darkness.

**"Who goes there?"** a voice echoed.

* * *

No answer returned from the shadows.
"""
        paragraphs = parse_markdown_to_paragraphs(md)
        cfg = get_docx_config()
        self.assertTrue(build_docx_package(out_docx, paragraphs, cfg, title="Test Story", author="Arthur"))
        self.assertTrue(out_docx.is_file())
        self.assertGreater(out_docx.stat().st_size, 500)

        # Inspect ZIP structure
        with zipfile.ZipFile(out_docx, "r") as zf:
            files = zf.namelist()
            self.assertIn("[Content_Types].xml", files)
            self.assertIn("word/document.xml", files)
            self.assertIn("word/styles.xml", files)
            self.assertIn("docProps/core.xml", files)

            doc_xml = zf.read("word/document.xml").decode("utf-8")
            self.assertIn("The Awakening", doc_xml)
            self.assertIn("The ancient runes glowed softly", doc_xml)
            self.assertIn("<w:b/>", doc_xml)

        # Test extraction back to markdown
        extracted_md = convert_docx_to_markdown(out_docx)
        self.assertIn("# The Awakening", extracted_md)
        self.assertIn("The ancient runes glowed softly", extracted_md)
        self.assertIn('**"Who goes there?"**', extracted_md)
        self.assertIn("* * *", extracted_md)

    def test_build_and_sync_manuscript_docx(self):
        """Test manuscript-level draft building and bidirectional sync."""
        ms_dir = self.root / "TestNovel"
        draft_dir = ms_dir / "01-Manuscript" / "Book-01" / "Draft-01" / "01_Act_I"
        draft_dir.mkdir(parents=True, exist_ok=True)

        # Write manuscript manifest
        (ms_dir / "manuscript.yaml").write_text("title: \"Test Novel\"\nauthor: \"Writer\"\nactive_draft: \"Draft-01\"\n", encoding="utf-8")

        # Write scene
        scene_1 = draft_dir / "01_Chapter_01.md"
        scene_1.write_text("""@pov: Hero
@location: Forest

# Chapter 1: The Woods

The trees whispered in the quiet dawn.
""", encoding="utf-8")

        # 1. Build DOCX
        res_build = build_manuscript_docx(ms_dir)
        self.assertEqual(len(res_build["chapters_built"]), 1)
        self.assertIsNotNone(res_build["consolidated_built"])

        ch_docx = draft_dir / "01_Chapter_01.docx"
        cons_docx = ms_dir / "01-Manuscript" / "Book-01" / "Draft-01" / "Draft-01_Manuscript.docx"
        self.assertTrue(ch_docx.is_file())
        self.assertTrue(cons_docx.is_file())

        # 2. Modify DOCX to simulate editing in Word
        edited_md = """# Chapter 1: The Woods

The trees shouted loudly in the wild tempest.
"""
        paragraphs = parse_markdown_to_paragraphs(edited_md)
        cfg = get_docx_config()
        build_docx_package(ch_docx, paragraphs, cfg, title="Test Novel", author="Writer")

        # Advance mtime of ch_docx by 5 seconds
        future_time = scene_1.stat().st_mtime + 5.0
        os.utime(ch_docx, (future_time, future_time))

        # 3. Sync DOCX -> MD
        res_sync = sync_manuscript_docx(ms_dir)
        self.assertIn("01-Manuscript/Book-01/Draft-01/01_Act_I/01_Chapter_01.md", res_sync["docx_to_md"])

        # Check that scene tags were preserved while prose was updated
        updated_md = scene_1.read_text(encoding="utf-8")
        self.assertIn("@pov: Hero", updated_md)
        self.assertIn("@location: Forest", updated_md)
        self.assertIn("The trees shouted loudly in the wild tempest", updated_md)
        self.assertNotIn("The trees whispered in the quiet dawn", updated_md)

    def test_escape_xml_illegal_control_characters(self):
        """Test that illegal XML 1.0 control characters are stripped cleanly."""
        dirty_input = "Hello\x00 World\x08!\x0b Newline\n Tab\t FormFeed\x0c Quote\" & Amp<>"
        escaped = escape_xml(dirty_input)
        self.assertNotIn("\x00", escaped)
        self.assertNotIn("\x08", escaped)
        self.assertNotIn("\x0b", escaped)
        self.assertNotIn("\x0c", escaped)
        self.assertIn("Hello World!", escaped)
        self.assertIn("Newline\n", escaped)
        self.assertIn("Tab\t", escaped)
        self.assertIn("&quot;", escaped)
        self.assertIn("&amp;", escaped)
        self.assertIn("&lt;&gt;", escaped)

    def test_consolidated_manuscript_not_duplicated_as_chapter(self):
        """Test that Draft-01_Manuscript.docx is ignored during chapter discovery and not duplicated as a chapter .md."""
        ms_dir = self.root / "NovelSyncTest"
        draft_dir = ms_dir / "Book-01" / "Draft-01" / "01_Act_I"
        draft_dir.mkdir(parents=True, exist_ok=True)

        (ms_dir / "manuscript.yaml").write_text("title: \"Novel Sync\"\nauthor: \"Writer\"\n", encoding="utf-8")
        scene = draft_dir / "01_Chapter_01.md"
        scene.write_text("# Chapter 1\n\nSome great prose.\n", encoding="utf-8")

        build_manuscript_docx(ms_dir)
        cons_docx = ms_dir / "Book-01" / "Draft-01" / "Draft-01_Manuscript.docx"
        self.assertTrue(cons_docx.is_file())

        res_sync = sync_manuscript_docx(ms_dir)
        cons_md = ms_dir / "Book-01" / "Draft-01" / "Draft-01_Manuscript.md"
        self.assertFalse(cons_md.exists())
        self.assertNotIn("Book-01/Draft-01/Draft-01_Manuscript.md", res_sync["docx_to_md"])

    def test_sync_conflict_branching(self):
        """Test that conflicting modifications in both MD and DOCX create a conflict branch without overwriting."""
        ms_dir = self.root / "ConflictNovel"
        draft_dir = ms_dir / "Book-01" / "Draft-01" / "01_Act_I"
        draft_dir.mkdir(parents=True, exist_ok=True)

        (ms_dir / "manuscript.yaml").write_text("title: \"Conflict Novel\"\nauthor: \"Writer\"\n", encoding="utf-8")
        scene = draft_dir / "01_Chapter_01.md"
        scene.write_text("# Chapter 1\n\nOriginal scene prose.\n", encoding="utf-8")

        # 1. Initial build creates DOCX and sync state
        build_manuscript_docx(ms_dir)
        sync_manuscript_docx(ms_dir)

        # 2. Modify MD
        scene.write_text("# Chapter 1\n\nModified in text editor.\n", encoding="utf-8")

        # 3. Modify DOCX independently
        chapter_docx = draft_dir / "01_Chapter_01.docx"
        new_paras = [{"type": "heading1", "text": "Chapter 1"}, {"type": "paragraph", "text": "Modified in MS Word independently."}]
        build_docx_package(chapter_docx, new_paras, get_docx_config(), title="Conflict Novel")

        # 4. Run sync -> Conflict should be detected
        res_sync = sync_manuscript_docx(ms_dir)
        self.assertEqual(len(res_sync["conflicts"]), 1)
        self.assertEqual(res_sync["conflicts"][0]["stem"], "01_Chapter_01")

        # Ensure MD file was NOT overwritten
        self.assertIn("Modified in text editor.", scene.read_text(encoding="utf-8"))

        # Ensure conflict file was created
        conflict_files = list(draft_dir.glob("01_Chapter_01.conflict_*.md"))
        self.assertEqual(len(conflict_files), 1)
        self.assertIn("Modified in MS Word independently.", conflict_files[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
