#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Static World Wiki Codex Exporter (scripts/lib/codex_export.py).
Validates:
- WOR-102: World Bible taxonomy scanning (Characters, Locations, Factions, etc.).
- Markdown Wikilinks conversion [[Target|Label]].
- Single-file standalone HTML codex bundle generation with inlined search.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.codex_export import (
    scan_world_vault,
    build_single_file_codex,
    _md_to_basic_html
)


class TestCodexExportEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name)
        (self.world_dir / "Characters").mkdir(parents=True)
        (self.world_dir / "Factions").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_wikilink_and_markdown_conversion(self):
        md = "# Header\n\nMeet [[Renée d'Anjou|Renée]] from the [[Solar Hegemony]].\n"
        html_res, fm = _md_to_basic_html(md)
        self.assertIn("<h1>Header</h1>", html_res)
        self.assertIn('<a href="#Renée_dAnjou" class="wikilink">Renée</a>', html_res)

    def test_scan_and_build_codex(self):
        char_f = self.world_dir / "Characters" / "Aethelgard.md"
        char_f.write_text("""---
name: "Aethelgard"
type: character
role: protagonist
---
A legendary warrior king.
""", encoding="utf-8")

        categories = scan_world_vault(self.world_dir)
        self.assertIn("Characters", categories)
        self.assertEqual(len(categories["Characters"]), 1)

        out_html = self.world_dir / "codex.html"
        build_single_file_codex(categories, "Eldoria", out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Eldoria Codex", content)
        self.assertIn("Aethelgard", content)

    def test_codex_cli_html(self):
        import subprocess
        char_f = self.world_dir / "Characters" / "Aethelgard.md"
        char_f.write_text("""---
name: "Aethelgard"
---
Warrior king.
""", encoding="utf-8")
        out_html = self.world_dir / "cli_codex.html"
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "lib" / "codex_export.py"), str(self.world_dir), "--html", str(out_html)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(out_html.is_file())


if __name__ == "__main__":
    unittest.main()
