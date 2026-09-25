#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Static World Wiki Codex Exporter (scripts/lib/codex_export.py).
Validates:
- WOR-102: World Bible taxonomy scanning (Characters, Locations, Factions, Artifacts, etc.).
- Markdown Wikilinks conversion [[Target|Label]] and [[Target]].
- Single-file standalone HTML codex bundle generation with inlined search.
- Offline CSP compliance and multi-theme rendering.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.codex_export import (
    _md_to_basic_html,
    build_single_file_codex,
    main,
    scan_world_vault,
)


class TestCodexExportEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name)
        (self.world_dir / "Characters").mkdir(parents=True)
        (self.world_dir / "Locations").mkdir(parents=True)
        (self.world_dir / "Factions").mkdir(parents=True)
        (self.world_dir / "Artifacts").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_wikilink_and_markdown_conversion(self) -> None:
        """Markdown headings, bold, italics, and wikilinks with aliases convert to HTML."""
        md = "# Header\n\nMeet [[Renée d'Anjou|Renée]] from the [[Solar Hegemony]].\n"
        html_res, _fm = _md_to_basic_html(md)
        self.assertIn("<h1>Header</h1>", html_res)
        self.assertIn('<a href="#Renée_dAnjou" class="wikilink">Renée</a>', html_res)
        self.assertIn('<a href="#Solar_Hegemony" class="wikilink">Solar Hegemony</a>', html_res)

    def test_scan_empty_world_vault(self) -> None:
        """Scanning a directory with empty taxonomies returns an empty dict."""
        empty_dir = Path(self.temp_dir.name) / "EmptyWorld"
        empty_dir.mkdir(parents=True, exist_ok=True)
        res = scan_world_vault(empty_dir)
        self.assertEqual(res, {})

    def test_scan_multiple_taxonomies(self) -> None:
        """Files in multiple taxonomy folders are properly grouped and indexed."""
        (self.world_dir / "Characters" / "Kaelen.md").write_text("# Kaelen\nA lone blade.", encoding="utf-8")
        (self.world_dir / "Locations" / "Valenreach.md").write_text("# Valenreach\nCitadel of spires.", encoding="utf-8")
        (self.world_dir / "Factions" / "Silver_Concordat.md").write_text("# Silver Concordat\nAlliance.", encoding="utf-8")

        categories = scan_world_vault(self.world_dir)
        self.assertIn("Characters", categories)
        self.assertIn("Locations", categories)
        self.assertIn("Factions", categories)
        self.assertEqual(len(categories["Characters"]), 1)
        self.assertEqual(categories["Characters"][0]["title"], "Kaelen")

    def test_frontmatter_infobox_extraction(self) -> None:
        """YAML frontmatter is parsed into metadata and infobox attributes."""
        content = """---
name: Kaelen Vane
role: Major Protagonist
status: Active
faction: Silver Concordat
---
# Kaelen Vane
Master swordsman.
"""
        (self.world_dir / "Characters" / "Kaelen_Vane.md").write_text(content, encoding="utf-8")
        categories = scan_world_vault(self.world_dir)

        item = categories["Characters"][0]
        self.assertEqual(item["frontmatter"]["role"], "Major Protagonist")
        self.assertEqual(item["frontmatter"]["status"], "Active")
        self.assertEqual(item["frontmatter"]["faction"], "Silver Concordat")

    def test_build_single_file_codex_creates_file(self) -> None:
        """build_single_file_codex produces an HTML file at the specified target path."""
        (self.world_dir / "Characters" / "Elena.md").write_text("# Elena\nSorceress.", encoding="utf-8")
        categories = scan_world_vault(self.world_dir)
        out_file = Path(self.temp_dir.name) / "codex.html"

        result_path = build_single_file_codex(categories, "Eldoria", out_file)
        self.assertTrue(result_path.exists())
        self.assertEqual(result_path, out_file)

    def test_codex_csp_compliance(self) -> None:
        """Exported codex enforces strict offline Content-Security-Policy."""
        categories = scan_world_vault(self.world_dir)
        out_file = Path(self.temp_dir.name) / "csp_codex.html"
        build_single_file_codex(categories, "TestWorld", out_file)

        content = out_file.read_text(encoding="utf-8")
        self.assertIn(
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; img-src data:; media-src data: blob:;">',
            content,
        )

    def test_codex_theme_support(self) -> None:
        """Generated codex contains dark, light, and sepia theme CSS variables."""
        out_file = Path(self.temp_dir.name) / "theme_codex.html"
        build_single_file_codex({}, "ThemeWorld", out_file)

        content = out_file.read_text(encoding="utf-8")
        self.assertIn(':root {', content)
        self.assertIn('body[data-theme="light"]', content)
        self.assertIn('body[data-theme="sepia"]', content)

    def test_inlined_search_index_present(self) -> None:
        """Generated HTML bundle contains the inlined JSON search index."""
        (self.world_dir / "Characters" / "Garrick.md").write_text("# Garrick\nVeteran captain.", encoding="utf-8")
        categories = scan_world_vault(self.world_dir)
        out_file = Path(self.temp_dir.name) / "search_codex.html"
        build_single_file_codex(categories, "SearchWorld", out_file)

        content = out_file.read_text(encoding="utf-8")
        self.assertIn("const index =", content)
        self.assertIn("Garrick", content)

    def test_html_escaping_in_titles_and_fields(self) -> None:
        """Potentially dangerous HTML characters in titles and fields are escaped."""
        (self.world_dir / "Characters" / "TestChar.md").write_text(
            """---
name: "<script>alert('xss')</script>"
role: "<b>Archon</b>"
---
# Dangerous
""",
            encoding="utf-8",
        )
        categories = scan_world_vault(self.world_dir)
        out_file = Path(self.temp_dir.name) / "xss_codex.html"
        build_single_file_codex(categories, "SafeWorld", out_file)

        content = out_file.read_text(encoding="utf-8")
        self.assertNotIn("<script>alert('xss')</script>", content)
        self.assertIn("&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;", content)

    def test_wikilink_without_alias(self) -> None:
        """Standard wikilink without pipe alias resolves to href with target text."""
        md = "See [[High_Vale]] for details."
        html_res, _ = _md_to_basic_html(md)
        self.assertIn('<a href="#High_Vale" class="wikilink">High_Vale</a>', html_res)

    def test_clean_id_generation(self) -> None:
        """Filenames with spaces and punctuation produce clean alphanumeric element IDs."""
        (self.world_dir / "Characters" / "Lord Vance III.md").write_text("# Lord Vance III\nNoble.", encoding="utf-8")
        categories = scan_world_vault(self.world_dir)
        item = categories["Characters"][0]
        self.assertEqual(item["id"], "LordVanceIII")

    def test_cli_main_codex_export(self) -> None:
        """CLI main function executes and outputs codex to default or custom path."""
        (self.world_dir / "Characters" / "Lyra.md").write_text("# Lyra\nChronomancer.", encoding="utf-8")
        out_file = Path(self.temp_dir.name) / "out" / "codex.html"

        exit_code = main([str(self.world_dir), "-o", str(out_file)])
        self.assertEqual(exit_code, 0)
        self.assertTrue(out_file.exists())
        self.assertIn("Lyra", out_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
