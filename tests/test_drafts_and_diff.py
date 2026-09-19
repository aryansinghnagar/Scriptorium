#!/usr/bin/env python3
"""
Unit Test Suite for Ars Arcanum Manuscript Drafts, Redline Comparator, and Secure Backups
(tests/test_drafts_and_diff.py)
========================================================================================
Tests:
  1. Config engine (XDG persistence, backup-dest get/set/clear)
  2. Word tokenization and novelWriter metadata stripping
  3. Word-level diff sequence matcher (insertions, deletions, replacements)
  4. ManuscriptComparator on files and directory trees
  5. HTML Redline generator (accessible styles, WCAG contrast colors, chapter sidebar)
  6. JSON change metrics export
  7. ANSI terminal diff formatting
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts/lib to Python path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
SCRIPTS_LIB = PROJECT_ROOT / "scripts" / "lib"
sys.path.insert(0, str(SCRIPTS_LIB))

import config
import manuscript_diff


class TestConfigEngine(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="arcanum_test_config_")
        self.orig_xdg = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.tmp_dir

    def tearDown(self):
        if self.orig_xdg is not None:
            os.environ["XDG_CONFIG_HOME"] = self.orig_xdg
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_backup_dest_lifecycle(self):
        # Initial should be empty
        self.assertEqual(config.get_backup_dest(), "")

        # Set destination
        dest_path = str(Path(self.tmp_dir) / "secure_vault")
        self.assertTrue(config.set_backup_dest(dest_path))
        self.assertEqual(config.get_backup_dest(), str(Path(dest_path).resolve()))

        # Clear destination
        self.assertTrue(config.clear_backup_dest())
        self.assertEqual(config.get_backup_dest(), "")


class TestManuscriptDiffEngine(unittest.TestCase):
    def test_strip_nw_metadata(self):
        sample = (
            "@pov: Kaelen\n"
            "@char: Vance, Renée\n"
            "@location: The Citadel\n"
            "% This is a comment\n"
            "The rain fell silently against the ancient stone.\n"
            "@status: Draft\n"
            "He turned toward the gate.\n"
        )
        cleaned = manuscript_diff.strip_nw_metadata(sample)
        self.assertNotIn("@pov:", cleaned)
        self.assertNotIn("@char:", cleaned)
        self.assertNotIn("% This is a comment", cleaned)
        self.assertIn("The rain fell silently against the ancient stone.", cleaned)
        self.assertIn("He turned toward the gate.", cleaned)

    def test_word_diff_tokens(self):
        text_a = "The quick brown fox jumps over the lazy dog."
        text_b = "The swift brown fox leaps over a lazy sleeping dog."

        tokens_a = manuscript_diff.tokenize_words(text_a)
        tokens_b = manuscript_diff.tokenize_words(text_b)

        chunks, added, deleted = manuscript_diff.compute_word_diff(tokens_a, tokens_b)

        # "quick" cut, "swift" added; "jumps" cut, "leaps" added; "the" cut, "a" added; "sleeping" added
        self.assertGreater(added, 0)
        self.assertGreater(deleted, 0)

        # Check tag presence
        tags = [c["tag"] for c in chunks]
        self.assertIn("delete", tags)
        self.assertIn("insert", tags)
        self.assertIn("equal", tags)

    def test_single_file_comparator(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_diff_"))
        try:
            file_a = tmp_dir / "draft1.md"
            file_b = tmp_dir / "draft2.md"

            file_a.write_text("# Chapter 1\n\nOld opening paragraph with five words.", encoding="utf-8")
            file_b.write_text("# Chapter 1\n\nNew opening paragraph with ten great and descriptive words.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(file_a, file_b, "Draft-01", "Draft-02")
            summary = comp.compare()

            self.assertEqual(summary["chapter_count"], 1)
            self.assertGreater(summary["added_words"], 0)
            self.assertGreater(summary["deleted_words"], 0)
            self.assertGreater(summary["total_words_b"], summary["total_words_a"])
            self.assertTrue(0.0 <= summary["similarity_ratio"] <= 1.0)

            # Check JSON
            json_str = comp.to_json()
            data = json.loads(json_str)
            self.assertEqual(data["label_a"], "Draft-01")
            self.assertEqual(data["label_b"], "Draft-02")

            # Check HTML Redline
            html_out = comp.to_html()
            self.assertIn("<!DOCTYPE html>", html_out)
            self.assertIn("diff-ins", html_out)
            self.assertIn("diff-del", html_out)
            self.assertIn("Draft-01", html_out)
            self.assertIn("Draft-02", html_out)

            # Check Terminal ANSI
            ansi_out = comp.to_terminal_ansi()
            self.assertIn("Ars Arcanum Manuscript Revision Comparison", ansi_out)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_directory_tree_comparator(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_tree_diff_"))
        try:
            dir_a = tmp_dir / "Draft-01"
            dir_b = tmp_dir / "Draft-02"

            (dir_a / "01_Act_I").mkdir(parents=True)
            (dir_a / "02_Act_II").mkdir(parents=True)
            (dir_b / "01_Act_I").mkdir(parents=True)
            (dir_b / "02_Act_II").mkdir(parents=True)

            (dir_a / "01_Act_I" / "01_Chapter_01.md").write_text("# Chapter 1\n\nInitial draft scene prose.", encoding="utf-8")
            (dir_a / "02_Act_II" / "01_Chapter_02.md").write_text("# Chapter 2\n\nSecond scene draft prose.", encoding="utf-8")

            (dir_b / "01_Act_I" / "01_Chapter_01.md").write_text("# Chapter 1\n\nInitial revised scene prose with extra details.", encoding="utf-8")
            (dir_b / "02_Act_II" / "01_Chapter_02.md").write_text("# Chapter 2\n\nSecond scene thoroughly expanded draft prose.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(dir_a, dir_b, "Draft-01", "Draft-02")
            summary = comp.compare()

            self.assertEqual(summary["chapter_count"], 2)
            self.assertEqual(len(summary["chapters"]), 2)
            self.assertGreater(summary["total_words_b"], summary["total_words_a"])

            html_doc = comp.to_html()
            self.assertIn("Chapter 1", html_doc)
            self.assertIn("Chapter 2", html_doc)
            self.assertIn("Words Added", html_doc)
            self.assertIn("Words Cut", html_doc)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
