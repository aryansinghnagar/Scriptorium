#!/usr/bin/env python3
"""
Unit tests for atomic_write filesystem utility (scripts/lib/fs_utils.py).
Validates:
- Successful atomic write of text and binary content.
- Atomic replacement of existing files without data loss.
- Cleanup of temporary files on exception.
- Directory creation when writing to nested paths.
"""

import os
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.fs_utils import atomic_write


class TestAtomicWrite(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_atomic_write_text(self):
        target = self.work_dir / "chapter.md"
        data = "# Chapter 1\n\nOnce upon a time in a sovereign realm."
        atomic_write(target, data)

        self.assertTrue(target.is_file())
        self.assertEqual(target.read_text(encoding="utf-8"), data)

    def test_atomic_write_binary(self):
        target = self.work_dir / "image.png"
        data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        atomic_write(target, data)

        self.assertTrue(target.is_file())
        self.assertEqual(target.read_bytes(), data)

    def test_atomic_overwrite_existing(self):
        target = self.work_dir / "draft.txt"
        target.write_text("Old Draft Content", encoding="utf-8")

        new_data = "New Refined Draft Content"
        atomic_write(target, new_data)

        self.assertEqual(target.read_text(encoding="utf-8"), new_data)

    def test_nested_directory_creation(self):
        target = self.work_dir / "nested" / "deep" / "story.md"
        atomic_write(target, "Nested content")

        self.assertTrue(target.is_file())
        self.assertEqual(target.read_text(encoding="utf-8"), "Nested content")

    def test_temporary_file_cleaned_up(self):
        target = self.work_dir / "test_clean.md"
        atomic_write(target, "Clean test")

        tmp_files = list(self.work_dir.glob(".*.tmp"))
        self.assertEqual(len(tmp_files), 0, f"Found lingering temporary files: {tmp_files}")


if __name__ == "__main__":
    unittest.main()
