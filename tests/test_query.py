#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Query Letter & Submission Package Scaffolder (scripts/init_query.py).
Validates:
- PUB-106: Query letter, one-page synopsis, extended synopsis, loglines, and agent tracker scaffolding.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from init_query import (
    build_query_letter,
    scaffold_submission_package
)


class TestQueryScaffolder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_query_letter_content(self):
        letter = build_query_letter("Voidfall", "Jane Doe", "Space Opera", "DUNE and FOUNDATION", 90000)
        self.assertIn("VOIDFALL", letter)
        self.assertIn("90,000 words", letter)
        self.assertIn("DUNE and FOUNDATION", letter)

    def test_scaffold_submission_package(self):
        meta = {"title": "Voidfall", "author": "Jane Doe", "genre": "Sci-Fi", "comps": "DUNE", "word_count": 90000}
        res = scaffold_submission_package(self.target_dir, meta, force=True)
        self.assertEqual(res["created_count"], 6)

        sub_dir = self.target_dir / "Submissions"
        self.assertTrue((sub_dir / "01_Query_Letter.md").is_file())
        self.assertTrue((sub_dir / "02_One_Page_Synopsis.md").is_file())
        self.assertTrue((sub_dir / "04_Pitch_Loglines.md").is_file())
        self.assertTrue((sub_dir / "05_Agent_Tracker.csv").is_file())

    def test_cli_arg_precedence(self):
        import subprocess
        (self.target_dir / "manuscript.yaml").write_text("title: Old Title\nauthor: Old Author\nword_count: 50000\n", encoding="utf-8")
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "init_query.py"), str(self.target_dir), "--title", "New Title", "--words", "120000", "-f"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        query_content = (self.target_dir / "Submissions" / "01_Query_Letter.md").read_text(encoding="utf-8")
        self.assertIn("NEW TITLE", query_content)
        self.assertIn("120,000 words", query_content)


if __name__ == "__main__":
    unittest.main()
