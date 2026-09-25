#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Smart Typography Normalizer (scripts/lib/typography_cleaner.py).
Validates:
- PRO-104: Smart curly quote conversion for single and double quotes.
- Em-dash (--- or -- -> —) and en-dash (range hyphens -> –) normalization.
- Ellipsis (... -> …) conversion.
- Non-breaking spaces and trailing whitespace cleanup.
- Frontmatter and codeblock protection.
- In-place modification, backup creation, and directory batch cleaning.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.typography_cleaner import (
    clean_directory,
    clean_file,
    normalize_typography_text,
)


class TestTypographyCleanerEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Smart Double Quotes Conversion                                  #
    # ------------------------------------------------------------------ #
    def test_smart_double_quotes_conversion(self):
        """Straight double quotes must be converted to opening and closing curly pairs."""
        raw = '"Hello world," she said. "This is a test."'
        polished, stats = normalize_typography_text(raw)
        self.assertIn("“Hello world,”", polished)
        self.assertIn("“This is a test.”", polished)
        self.assertGreater(stats["curly_double_quotes"], 0)

    # ------------------------------------------------------------------ #
    # 2. Smart Single Quotes & Contractions                              #
    # ------------------------------------------------------------------ #
    def test_smart_single_quotes_and_apostrophes(self):
        """Single quotes and apostrophes in contractions must convert to typographic curls."""
        raw = "'Speak friend,' he whispered. Don't touch that 'tis dangerous."
        polished, stats = normalize_typography_text(raw)
        self.assertIn("‘Speak friend,’", polished)
        self.assertIn("Don’t", polished)
        self.assertIn("’tis", polished)
        self.assertGreater(stats["curly_single_quotes"], 0)

    # ------------------------------------------------------------------ #
    # 3. Em-Dashes, En-Dashes & Ellipses                                 #
    # ------------------------------------------------------------------ #
    def test_dashes_and_ellipses_normalization(self):
        """--- and -- convert to em-dash, number ranges convert to en-dash, dots to ellipsis."""
        raw = "The ancient war (1914-1918) ended---or so we thought... But then--suddenly--it returned."
        polished, stats = normalize_typography_text(raw)
        self.assertIn("1914–1918", polished)
        self.assertIn("ended—or", polished)
        self.assertIn("thought…", polished)
        self.assertIn("then—suddenly—it", polished)
        self.assertGreater(stats["em_dashes"], 0)
        self.assertGreater(stats["en_dashes"], 0)
        self.assertGreater(stats["ellipses"], 0)

    # ------------------------------------------------------------------ #
    # 4. In-Place File Cleaning with Backup Creation                     #
    # ------------------------------------------------------------------ #
    def test_file_cleaning_in_place_with_backup(self):
        """clean_file with in_place=True and make_backup=True must update file and create .bak."""
        f = self.target_dir / "01_Scene.md"
        f.write_text('"Wait," he said...   \n', encoding="utf-8")
        _stats, diff = clean_file(f, in_place=True, make_backup=True)

        self.assertTrue(bool(diff))
        cleaned_content = f.read_text(encoding="utf-8")
        self.assertIn("“Wait,”", cleaned_content)
        self.assertIn("said…", cleaned_content)

        # Check backup file exists
        bak_file = self.target_dir / "01_Scene.md.bak"
        self.assertTrue(bak_file.is_file())

    # ------------------------------------------------------------------ #
    # 5. Frontmatter Boundary Protection                                 #
    # ------------------------------------------------------------------ #
    def test_frontmatter_boundary_protection(self):
        """YAML frontmatter delimiters (---) must NOT be converted to em-dashes."""
        raw = "---\ntitle: \"The Quest\"\nchapter: 1\n---\n\"Let's go,\" he said."
        polished, _stats = normalize_typography_text(raw)
        self.assertTrue(polished.startswith("---"))
        self.assertIn("---", polished)

    # ------------------------------------------------------------------ #
    # 6. Codeblock Protection                                            #
    # ------------------------------------------------------------------ #
    def test_codeblock_protection(self):
        """Lines starting with ``` must be preserved without typography replacement."""
        raw = "```python\nx = \"hello world\"\n```\n\"Go,\" she said."
        polished, _stats = normalize_typography_text(raw)
        self.assertIn("```python", polished)
        self.assertIn("```", polished)

    # ------------------------------------------------------------------ #
    # 7. Trailing Whitespace Stripping                                   #
    # ------------------------------------------------------------------ #
    def test_trailing_whitespace_stripping(self):
        """Trailing spaces at line ends must be cleanly stripped."""
        raw = "A solitary spire stood upon the ridge.    \nAnother line. \t  \n"
        polished, stats = normalize_typography_text(raw)
        self.assertEqual(polished, "A solitary spire stood upon the ridge.\nAnother line.\n")
        self.assertEqual(stats["trailing_spaces_removed"], 2)

    # ------------------------------------------------------------------ #
    # 8. Idempotency on Already-Clean Text                               #
    # ------------------------------------------------------------------ #
    def test_typography_idempotency(self):
        """Re-running normalization on already clean text must produce zero changes."""
        clean_text = "“Hello world,” she said—with a quiet smile… “Don’t leave yet.”\n"
        polished, _stats = normalize_typography_text(clean_text)
        self.assertEqual(polished, clean_text)

    # ------------------------------------------------------------------ #
    # 9. Directory Batch Cleaning                                        #
    # ------------------------------------------------------------------ #
    def test_clean_directory_batch(self):
        """clean_directory must process all markdown files and return summary stats."""
        (self.target_dir / "01_ch.md").write_text('"Scene 1..."\n', encoding="utf-8")
        (self.target_dir / "02_ch.md").write_text('"Scene 2---end."\n', encoding="utf-8")

        result = clean_directory(self.target_dir, in_place=True, make_backup=False)
        self.assertEqual(result["summary"]["files_scanned"], 2)
        self.assertEqual(result["summary"]["files_modified"], 2)
        self.assertGreater(result["summary"]["curly_double_quotes"], 0)

    # ------------------------------------------------------------------ #
    # 10. Dry-Run Mode Without Disk Modification                         #
    # ------------------------------------------------------------------ #
    def test_dry_run_does_not_modify_disk(self):
        """clean_file with in_place=False must return diff without modifying target file."""
        f = self.target_dir / "dryrun.md"
        original = '"Testing dry run..."\n'
        f.write_text(original, encoding="utf-8")

        stats, diff = clean_file(f, in_place=False, make_backup=False)
        self.assertTrue(bool(diff))
        self.assertGreater(stats["ellipses"], 0)
        self.assertEqual(f.read_text(encoding="utf-8"), original)

    # ------------------------------------------------------------------ #
    # 11. Empty File Handling                                            #
    # ------------------------------------------------------------------ #
    def test_clean_empty_file(self):
        """clean_file on empty file must succeed and return empty diff."""
        f = self.target_dir / "empty.md"
        f.write_text("", encoding="utf-8")
        _stats, diff = clean_file(f, in_place=True, make_backup=False)
        self.assertEqual(diff, "")

    # ------------------------------------------------------------------ #
    # 12. Nonexistent File Handling                                      #
    # ------------------------------------------------------------------ #
    def test_clean_nonexistent_file(self):
        """clean_file on missing file must raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            clean_file(self.target_dir / "ghost.md")


if __name__ == "__main__":
    unittest.main()
