#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Smart Typography Normalizer (scripts/lib/typography_cleaner.py).
Validates:
- PRO-104: Smart curly quote conversion for single and double quotes.
- Em-dash (--- or -- -> —) and en-dash (range hyphens -> –) normalization.
- Ellipsis (... -> …) conversion.
- In-place modification and backup creation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.typography_cleaner import (
    normalize_typography_text,
    clean_file,
    clean_target
)


class TestTypographyCleanerEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_smart_double_quotes_conversion(self):
        raw = '"Hello world," she said. "This is a test."'
        polished, stats = normalize_typography_text(raw)
        self.assertIn("“Hello world,”", polished)
        self.assertIn("“This is a test.”", polished)
        self.assertGreater(stats["curly_double_quotes"], 0)

    def test_smart_single_quotes_and_apostrophes(self):
        raw = "'Speak friend,' he whispered. Don't touch that 'tis dangerous."
        polished, stats = normalize_typography_text(raw)
        self.assertIn("‘Speak friend,’", polished)
        self.assertIn("Don’t", polished)
        self.assertIn("’tis", polished)
        self.assertGreater(stats["curly_single_quotes"], 0)

    def test_dashes_and_ellipses_normalization(self):
        raw = "The ancient war (1914-1918) ended---or so we thought... But then--suddenly--it returned."
        polished, stats = normalize_typography_text(raw)
        self.assertIn("1914–1918", polished)
        self.assertIn("ended—or", polished)
        self.assertIn("thought…", polished)
        self.assertIn("then—suddenly—it", polished)
        self.assertGreater(stats["em_dashes"], 0)
        self.assertGreater(stats["en_dashes"], 0)
        self.assertGreater(stats["ellipses"], 0)

    def test_file_cleaning_in_place_with_backup(self):
        f = self.target_dir / "01_Scene.md"
        f.write_text('"Wait," he said...   \n', encoding="utf-8")
        stats, diff = clean_file(f, in_place=True, make_backup=True)
        
        self.assertTrue(bool(diff))
        cleaned_content = f.read_text(encoding="utf-8")
        self.assertIn("“Wait,”", cleaned_content)
        self.assertIn("said…", cleaned_content)

        # Check backup file exists
        bak_file = self.target_dir / "01_Scene.md.bak"
        self.assertTrue(bak_file.is_file())


if __name__ == "__main__":
    unittest.main()
