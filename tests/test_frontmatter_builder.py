#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Modular Front & Back Matter Builder (scripts/lib/frontmatter_builder.py).
Validates:
- PUB-103: Standard front matter (Half-Title, Title, Copyright, Dedication, Epigraph).
- Standard back matter (Acknowledgments, About Author, Also By, Reading Group Questions, CTA).
- Scaffolding to manuscript directory.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.frontmatter_builder import (
    generate_frontmatter_modules,
    generate_backmatter_modules,
    scaffold_matter
)


class TestFrontmatterBuilder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_frontmatter_generation(self):
        meta = {"title": "The Starborn Gate", "author": "Valen Vance", "copyright_year": "2026"}
        modules = generate_frontmatter_modules(meta)
        self.assertIn("01_Half_Title.md", modules)
        self.assertIn("03_Copyright.md", modules)
        self.assertIn("The Starborn Gate", modules["01_Half_Title.md"])
        self.assertIn("Copyright © 2026", modules["03_Copyright.md"])

    def test_backmatter_generation(self):
        meta = {"title": "The Starborn Gate", "author": "Valen Vance"}
        modules = generate_backmatter_modules(meta)
        self.assertIn("01_Acknowledgments.md", modules)
        self.assertIn("02_About_the_Author.md", modules)
        self.assertIn("04_Discussion_Questions.md", modules)
        self.assertIn("Valen Vance", modules["02_About_the_Author.md"])

    def test_scaffold_matter_to_disk(self):
        meta = {"title": "The Starborn Gate", "author": "Valen Vance"}
        res = scaffold_matter(self.target_dir, meta, force=True)
        self.assertEqual(res["created_count"], 10)
        self.assertTrue((self.target_dir / "00_Front_Matter" / "03_Copyright.md").is_file())
        self.assertTrue((self.target_dir / "04_Back_Matter" / "01_Acknowledgments.md").is_file())

    def test_cli_arg_precedence(self):
        import subprocess
        # manuscript.yaml has 2024, CLI passes --year 2028
        (self.target_dir / "manuscript.yaml").write_text("title: Old Title\nauthor: Old Author\ncopyright_year: 2024\n", encoding="utf-8")
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "lib" / "frontmatter_builder.py"), "build", str(self.target_dir), "--title", "New Title", "--year", "2028", "-f"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        copyright_content = (self.target_dir / "00_Front_Matter" / "03_Copyright.md").read_text(encoding="utf-8")
        self.assertIn("Copyright © 2028", copyright_content)
        self.assertIn("by Old Author", copyright_content)


if __name__ == "__main__":
    unittest.main()
