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
    build_manuscript_docx, sync_manuscript_docx
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


if __name__ == "__main__":
    unittest.main()
