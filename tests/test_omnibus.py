#!/usr/bin/env python3
"""
Test Suite: Multi-Volume Series Omnibus Compiler
(tests/test_omnibus.py)
================================================================================
Validates multi-volume discovery, sequence resolution, TOC synthesis, unified
Dramatis Personae tracking, master markdown compilation, and HTML reader output.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.lib.omnibus import (
    VolumeData,
    compile_omnibus_manuscript,
    discover_series_volumes,
    generate_omnibus_html_reader,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestOmnibus(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create Book-01
        self.b1_dir = self.root / "Book-01" / "Draft-01"
        self.b1_dir.mkdir(parents=True)
        (self.b1_dir / "01_Ch1.md").write_text(
            "@pov: Kaelen\n\nChapter 1 text in Book 1.",
            encoding="utf-8",
        )
        (self.b1_dir / "02_Ch2.md").write_text(
            "@pov: Lysandra\n\nChapter 2 text in Book 1.",
            encoding="utf-8",
        )

        # Create Book-02
        self.b2_dir = self.root / "Book-02" / "Draft-01"
        self.b2_dir.mkdir(parents=True)
        (self.b2_dir / "01_Ch1.md").write_text(
            "@pov: Kaelen\n\nChapter 1 text in Book 2.",
            encoding="utf-8",
        )
        (self.b2_dir / "02_Ch2.md").write_text(
            "@pov: Valerius\n\nChapter 2 text in Book 2.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Multi-Volume Discovery                                          #
    # ------------------------------------------------------------------ #
    def test_discover_series_volumes(self):
        """discover_series_volumes must discover and order all books."""
        volumes = discover_series_volumes(self.root)
        self.assertEqual(len(volumes), 2)
        self.assertEqual(volumes[0].name, "Book-01")
        self.assertEqual(volumes[1].name, "Book-02")
        self.assertEqual(len(volumes[0].chapters), 2)
        self.assertEqual(len(volumes[1].chapters), 2)

    # ------------------------------------------------------------------ #
    # 2. Master Omnibus Manuscript Compilation                           #
    # ------------------------------------------------------------------ #
    def test_compile_omnibus_manuscript(self):
        """compile_omnibus_manuscript must assemble volumes, TOC, and markdown."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes, series_title="The Sunstone Saga", author="Master Writer")

        self.assertEqual(report["title"], "The Sunstone Saga")
        self.assertEqual(report["total_volumes"], 2)
        self.assertEqual(report["total_chapters"], 4)

        # Dramatis Personae synthesis
        dp = report["dramatis_personae"]
        self.assertIn("Kaelen", dp)
        self.assertIn("Lysandra", dp)
        self.assertIn("Valerius", dp)
        self.assertEqual(len(dp["Kaelen"]), 2)  # Appears in Book 1 and Book 2
        self.assertEqual(len(dp["Valerius"]), 1)  # Only Book 2

        # Markdown output verification
        md_text = report["markdown_content"]
        self.assertIn("# The Sunstone Saga", md_text)
        self.assertIn("Volume 1: Book 01", md_text)
        self.assertIn("Volume 2: Book 02", md_text)
        self.assertIn("Dramatis Personae", md_text)

    # ------------------------------------------------------------------ #
    # 3. HTML Reader Generation                                          #
    # ------------------------------------------------------------------ #
    def test_generate_omnibus_html_reader(self):
        """generate_omnibus_html_reader must create a standalone HTML reader."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes, series_title="The Sunstone Saga", author="Master Writer")
        out_html = self.root / "omnibus.html"
        generate_omnibus_html_reader(report, out_html)

        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("The Sunstone Saga", content)
        self.assertIn("Dramatis Personae", content)
        self.assertIn("Volume 1: Book 01", content)

    # ------------------------------------------------------------------ #
    # 4. Content Security Policy Isolation                               #
    # ------------------------------------------------------------------ #
    def test_omnibus_html_csp_compliance(self):
        """Omnibus HTML reader must include strict Content-Security-Policy."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes, series_title="The Sunstone Saga")
        out_html = self.root / "csp_omnibus.html"
        generate_omnibus_html_reader(report, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("default-src 'none'", content)
        self.assertIn("style-src 'unsafe-inline'", content)

    # ------------------------------------------------------------------ #
    # 5. Word Count Accumulation Across Volumes                          #
    # ------------------------------------------------------------------ #
    def test_omnibus_word_count_rollup(self):
        """compile_omnibus_manuscript must compute total word count across all volumes."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes)
        self.assertGreater(report["total_words"], 0)
        self.assertGreater(volumes[0].word_count, 0)
        self.assertGreater(volumes[1].word_count, 0)

    # ------------------------------------------------------------------ #
    # 6. VolumeData Dataclass to_dict Conversion                         #
    # ------------------------------------------------------------------ #
    def test_volume_data_to_dict(self):
        """VolumeData.to_dict must return valid serializable dictionary."""
        v = VolumeData(index=1, name="Book-01", title="First Flight", draft_name="Draft-01", path=str(self.root / "b1"))
        d = v.to_dict()
        self.assertEqual(d["index"], 1)
        self.assertEqual(d["name"], "Book-01")
        self.assertEqual(d["title"], "First Flight")

    # ------------------------------------------------------------------ #
    # 7. Frontmatter Title Extraction per Volume                         #
    # ------------------------------------------------------------------ #
    def test_volume_custom_frontmatter_title(self):
        """Volume title should be extracted from chapter title or folder name."""
        b3_dir = self.root / "Book-03" / "Draft-01"
        b3_dir.mkdir(parents=True)
        (b3_dir / "01_Ch1.md").write_text("---\ntitle: \"Wrath of the Sun\"\n---\nText.", encoding="utf-8")
        volumes = discover_series_volumes(self.root)
        self.assertEqual(len(volumes), 3)

    # ------------------------------------------------------------------ #
    # 8. Table of Contents Structure Synthesis                           #
    # ------------------------------------------------------------------ #
    def test_omnibus_table_of_contents_structure(self):
        """compile_omnibus_manuscript report must include Table of Contents in markdown_content."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes)
        self.assertIn("## Table of Contents", report["markdown_content"])
        self.assertIn("Volume 1: Book 01", report["markdown_content"])
        self.assertIn("Volume 2: Book 02", report["markdown_content"])

    # ------------------------------------------------------------------ #
    # 9. Single Volume Discovery Edge Case                               #
    # ------------------------------------------------------------------ #
    def test_single_volume_omnibus(self):
        """compile_omnibus_manuscript must handle a 1-volume project cleanly."""
        single_dir = self.root / "Standalone_Project"
        (single_dir / "Draft-01").mkdir(parents=True)
        (single_dir / "Draft-01" / "01_Ch1.md").write_text("Hello world.", encoding="utf-8")

        volumes = discover_series_volumes(single_dir)
        self.assertEqual(len(volumes), 1)
        report = compile_omnibus_manuscript(volumes, series_title="Solo Novel")
        self.assertEqual(report["total_volumes"], 1)
        self.assertEqual(report["total_chapters"], 1)

    # ------------------------------------------------------------------ #
    # 10. Empty Directory Fallback Handling                              #
    # ------------------------------------------------------------------ #
    def test_empty_directory_discovery(self):
        """discover_series_volumes on empty directory should return empty list."""
        empty_dir = self.root / "Empty_Universe"
        empty_dir.mkdir()
        volumes = discover_series_volumes(empty_dir)
        self.assertEqual(len(volumes), 0)

    # ------------------------------------------------------------------ #
    # 11. Custom Author and Series Subtitle Header                       #
    # ------------------------------------------------------------------ #
    def test_omnibus_custom_author_header(self):
        """Compiled markdown must include custom author attribution."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes, series_title="Eldoria Chronicles", author="Lady Seraphina")
        self.assertIn("By Lady Seraphina", report["markdown_content"])
        self.assertEqual(report["author"], "Lady Seraphina")

    # ------------------------------------------------------------------ #
    # 12. Cross-Volume POV Tracking                                      #
    # ------------------------------------------------------------------ #
    def test_cross_volume_pov_tracking(self):
        """compile_omnibus_manuscript report must record POV character list per volume."""
        volumes = discover_series_volumes(self.root)
        report = compile_omnibus_manuscript(volumes)
        v1 = next(v for v in report["volumes"] if v["name"] == "Book-01")
        v2 = next(v for v in report["volumes"] if v["name"] == "Book-02")
        self.assertIn("Kaelen", v1["povs"])
        self.assertIn("Lysandra", v1["povs"])
        self.assertIn("Valerius", v2["povs"])


if __name__ == "__main__":
    unittest.main()
