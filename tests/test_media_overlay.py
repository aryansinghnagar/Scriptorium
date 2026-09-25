#!/usr/bin/env python3
"""
Test Suite: EPUB 3 SMIL Media Overlays & Synchronized Narration Engine
(tests/test_media_overlay.py)
================================================================================
Validates paragraph segmentation, SMIL timestamp generation, W3C EPUB 3 XML
compliance, SpeechSynthesis player output, and Content Security Policy sandboxing.
"""

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.media_overlay import (
    ChapterOverlay,
    OverlayParagraph,
    build_chapter_overlay,
    format_smil_timestamp,
    generate_smil_xml,
    generate_synchronized_player_html,
)


class TestMediaOverlay(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.sample_chapter = self.root / "01_The_First_Dawn.md"
        self.sample_chapter.write_text(
            """---
title: "The First Dawn"
chapter: 1
pov: "[[Aeloria]]"
---

# The First Dawn

The crystalline spires of the floating sanctuary gleamed in the early morning twilight.

Aeloria adjusted her grip upon the hilt of Dawnstrider. The wind carried whispers of ancient sorcery from the valley below.

"Are you ready?" asked Master Theron.
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. SMIL Timestamp Formatting                                       #
    # ------------------------------------------------------------------ #
    def test_format_smil_timestamp(self):
        """format_smil_timestamp must convert float seconds into HH:MM:SS.mmm format."""
        self.assertEqual(format_smil_timestamp(0.0), "00:00:00.000")
        self.assertEqual(format_smil_timestamp(45.2), "00:00:45.200")
        self.assertEqual(format_smil_timestamp(65.5), "00:01:05.500")
        self.assertEqual(format_smil_timestamp(3661.123), "01:01:01.123")

    # ------------------------------------------------------------------ #
    # 2. Chapter Overlay Paragraph Segmentation                          #
    # ------------------------------------------------------------------ #
    def test_build_chapter_overlay(self):
        """build_chapter_overlay must extract paragraphs and calculate non-overlapping clips."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1, wpm=150)
        self.assertEqual(overlay.chapter_index, 1)
        self.assertEqual(overlay.title, "The First Dawn")
        self.assertEqual(overlay.xhtml_file, "01_The_First_Dawn.xhtml")
        self.assertEqual(overlay.smil_file, "01_The_First_Dawn.smil")
        self.assertEqual(overlay.audio_file, "audio/01_The_First_Dawn.mp3")

        # 4 paragraphs (1 title header + 3 prose paragraphs)
        self.assertEqual(len(overlay.paragraphs), 4)
        self.assertEqual(overlay.paragraphs[0].id, "p_1")
        self.assertEqual(overlay.paragraphs[0].text, "The First Dawn")
        self.assertEqual(overlay.paragraphs[0].clip_begin, 0.0)
        self.assertGreater(overlay.paragraphs[0].clip_end, 0.0)
        self.assertGreater(overlay.total_duration, 0.0)

        # Paragraph 2 starts where paragraph 1 ended
        self.assertAlmostEqual(overlay.paragraphs[1].clip_begin, overlay.paragraphs[0].clip_end, places=2)

    # ------------------------------------------------------------------ #
    # 3. SMIL 3.0 XML Structure & Tags                                   #
    # ------------------------------------------------------------------ #
    def test_generate_smil_xml_validity(self):
        """generate_smil_xml must output valid W3C SMIL XML with seq and par elements."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1, wpm=150)
        smil_xml = generate_smil_xml(overlay)

        self.assertIn('<smil xmlns="http://www.w3.org/ns/SMIL"', smil_xml)
        self.assertIn('<seq id="seq_1" epub:textref="01_The_First_Dawn.xhtml">', smil_xml)
        self.assertIn('<par id="par_1">', smil_xml)
        self.assertIn('<text src="01_The_First_Dawn.xhtml#p_1"/>', smil_xml)
        self.assertIn('clipBegin="00:00:00.000"', smil_xml)

        # Parse XML tree
        root = ET.fromstring(smil_xml)  # noqa: S314
        self.assertTrue(root.tag.endswith("smil"))
        body = root.find("{http://www.w3.org/ns/SMIL}body")
        self.assertIsNotNone(body)

    # ------------------------------------------------------------------ #
    # 4. Synchronized Audio Player HTML                                  #
    # ------------------------------------------------------------------ #
    def test_generate_synchronized_player_html(self):
        """generate_synchronized_player_html must output player with SpeechSynthesis."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1, wpm=150)
        out_html = self.root / "player.html"
        generate_synchronized_player_html([overlay], out_html)

        self.assertTrue(out_html.exists())
        html_content = out_html.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", html_content)
        self.assertIn("Synchronized Audio Media Overlay Player", html_content)
        self.assertIn("The First Dawn", html_content)
        self.assertIn("p_1", html_content)
        self.assertIn("speechSynthesis", html_content)

    # ------------------------------------------------------------------ #
    # 5. Content Security Policy Compliance                              #
    # ------------------------------------------------------------------ #
    def test_player_csp_compliance(self):
        """HTML audio player must declare strict offline CSP."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1)
        out_html = self.root / "csp_player.html"
        generate_synchronized_player_html([overlay], out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("default-src 'none'", content)
        self.assertIn("style-src 'unsafe-inline'", content)
        self.assertIn("script-src 'unsafe-inline'", content)

    # ------------------------------------------------------------------ #
    # 6. WPM Speed Calibration (100 WPM vs 200 WPM)                      #
    # ------------------------------------------------------------------ #
    def test_wpm_speed_calibration(self):
        """Lower WPM must produce longer total duration than higher WPM."""
        slow = build_chapter_overlay(self.sample_chapter, index=1, wpm=100)
        fast = build_chapter_overlay(self.sample_chapter, index=1, wpm=200)
        self.assertGreater(slow.total_duration, fast.total_duration)

    # ------------------------------------------------------------------ #
    # 7. OverlayParagraph to_dict Serialization                          #
    # ------------------------------------------------------------------ #
    def test_overlay_paragraph_to_dict(self):
        """OverlayParagraph.to_dict must include formatted clip strings."""
        p = OverlayParagraph(id="p_1", index=1, text="Hello world.", words=2, clip_begin=0.0, clip_end=0.8)
        d = p.to_dict()
        self.assertEqual(d["id"], "p_1")
        self.assertEqual(d["clip_begin_formatted"], "00:00:00.000")
        self.assertEqual(d["clip_end_formatted"], "00:00:00.800")

    # ------------------------------------------------------------------ #
    # 8. ChapterOverlay to_dict Serialization                            #
    # ------------------------------------------------------------------ #
    def test_chapter_overlay_to_dict(self):
        """ChapterOverlay.to_dict must produce complete chapter metadata dictionary."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1)
        self.assertIsInstance(overlay, ChapterOverlay)
        d = overlay.to_dict()
        self.assertEqual(d["title"], "The First Dawn")
        self.assertEqual(d["chapter_index"], 1)
        self.assertIn("total_duration_formatted", d)
        self.assertEqual(len(d["paragraphs"]), 4)

    # ------------------------------------------------------------------ #
    # 9. Multi-Chapter Playback Playlist in Player                       #
    # ------------------------------------------------------------------ #
    def test_multi_chapter_player_playlist(self):
        """generate_synchronized_player_html must render multi-chapter playlist buttons."""
        ch2 = self.root / "02_Second_Chapter.md"
        ch2.write_text("# Chapter Two\n\nMore prose here.", encoding="utf-8")
        o1 = build_chapter_overlay(self.sample_chapter, index=1)
        o2 = build_chapter_overlay(ch2, index=2)

        out_html = self.root / "multi_player.html"
        generate_synchronized_player_html([o1, o2], out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("The First Dawn", content)
        self.assertIn("Chapter Two", content)

    # ------------------------------------------------------------------ #
    # 10. SMIL Audio Element Filename Consistency                       #
    # ------------------------------------------------------------------ #
    def test_smil_audio_src_attribute(self):
        """SMIL XML audio element src attribute must point to expected audio file."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1)
        smil_xml = generate_smil_xml(overlay)
        self.assertIn('<audio src="audio/01_The_First_Dawn.mp3"', smil_xml)

    # ------------------------------------------------------------------ #
    # 11. Empty Chapter File Graceful Handling                           #
    # ------------------------------------------------------------------ #
    def test_empty_chapter_file(self):
        """build_chapter_overlay on empty file must produce valid zero-duration overlay."""
        empty_ch = self.root / "empty.md"
        empty_ch.write_text("", encoding="utf-8")
        overlay = build_chapter_overlay(empty_ch, index=99)
        self.assertEqual(len(overlay.paragraphs), 0)
        self.assertEqual(overlay.total_duration, 0.0)

    # ------------------------------------------------------------------ #
    # 12. Scrub Bar & Playback Rate Controls in Player HTML              #
    # ------------------------------------------------------------------ #
    def test_player_scrub_and_rate_controls(self):
        """HTML player must include playback rate selectors and timeline progress bar."""
        overlay = build_chapter_overlay(self.sample_chapter, index=1)
        out_html = self.root / "controls_player.html"
        generate_synchronized_player_html([overlay], out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("speedSelect", content)
        self.assertIn("scrubber", content)


if __name__ == "__main__":
    unittest.main()
