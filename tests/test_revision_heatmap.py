#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Manuscript Revision Density & Churn Heatmap Engine (scripts/lib/revision_heatmap.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.revision_heatmap import (
    ChapterRevisionStats,
    analyze_revision_churn,
    count_words,
    diff_line_counts,
    generate_revision_heatmap_html,
    scan_manuscript_snapshots,
)


class TestRevisionHeatmapEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.snapshot_dir = Path(self.temp_dir.name) / "Snapshots"
        self.ms_dir.mkdir(parents=True)
        self.snapshot_dir.mkdir(parents=True)
        (self.ms_dir / "Book-01" / "Draft-01").mkdir(parents=True)
        (self.snapshot_dir / "Book-01" / "Draft-01").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, base_dir: Path, rel_path: str, content: str) -> Path:
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_count_words(self):
        """Headers and @tags are excluded from word count."""
        text = """# Chapter 1
@pov: Kaelen
@location: Obsidian Citadel

The silver blade hummed in the dark.
@thread: main
"""
        wc = count_words(text)
        self.assertEqual(wc, 7)

    def test_diff_line_counts_identical(self):
        """Identical text produces zero insertions and deletions."""
        text = "Line 1\nLine 2\nLine 3\n"
        ins, dels = diff_line_counts(text, text)
        self.assertEqual(ins, 0)
        self.assertEqual(dels, 0)

    def test_diff_line_counts_additions_and_deletions(self):
        """Modifications produce non-zero insertions and deletions."""
        snap = "Line 1\nLine 2\nLine 3\n"
        curr = "Line 1\nLine 2 modified\nLine 3\nLine 4\n"
        ins, dels = diff_line_counts(curr, snap)
        self.assertEqual(ins, 2)
        self.assertEqual(dels, 1)

    def test_scan_no_snapshots(self):
        """When no snapshot exists, chapter has has_snapshot=False."""
        self._write(
            self.ms_dir,
            "Book-01/Draft-01/01_Chapter.md",
            "# Chapter 1\nThe wind howled over the jagged stones.",
        )
        stats = scan_manuscript_snapshots(self.ms_dir, snapshot_dir=None)
        self.assertEqual(len(stats), 1)
        self.assertFalse(stats[0].has_snapshot)
        self.assertGreater(stats[0].word_count, 0)

    def test_scan_with_snapshot_identical(self):
        """Identical snapshot gives 0 insertions, 0 deletions, and 0 churn_score."""
        content = "# Chapter 1\nThe wind howled over the jagged stones."
        self._write(self.ms_dir, "Book-01/Draft-01/01_Chapter.md", content)
        self._write(self.snapshot_dir, "Book-01/Draft-01/01_Chapter.md", content)

        stats = scan_manuscript_snapshots(self.ms_dir, snapshot_dir=self.snapshot_dir)
        self.assertEqual(len(stats), 1)
        self.assertTrue(stats[0].has_snapshot)
        self.assertEqual(stats[0].insertions, 0)
        self.assertEqual(stats[0].deletions, 0)
        self.assertEqual(stats[0].churn_score, 0)

    def test_scan_with_snapshot_changed(self):
        """Changed chapter calculates churn score and ratio against snapshot."""
        snap = "Ancient stone gates stood silent."
        curr = "Ancient stone gates stood silent.\nA shadow stepped through the mist.\n"
        self._write(self.ms_dir, "Book-01/Draft-01/01_Chapter.md", curr)
        self._write(self.snapshot_dir, "Book-01/Draft-01/01_Chapter.md", snap)

        stats = scan_manuscript_snapshots(self.ms_dir, snapshot_dir=self.snapshot_dir)
        self.assertEqual(len(stats), 1)
        self.assertTrue(stats[0].has_snapshot)
        self.assertGreater(stats[0].insertions, 0)
        self.assertGreater(stats[0].churn_score, 0)

    def test_analyze_churn_no_flags(self):
        """Chapters with balanced churn show zero outlier flags."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 10, 5, 15, 0.03, True, ""),
            ChapterRevisionStats("ch2.md", "ch2.md", 500, 12, 6, 18, 0.036, True, ""),
            ChapterRevisionStats("ch3.md", "ch3.md", 500, 8, 4, 12, 0.024, True, ""),
        ]
        result = analyze_revision_churn(stats)
        self.assertEqual(len(result["findings"]), 0)

    def test_analyze_churn_rev101_over_revised(self):
        """Chapter with extreme churn ratio is flagged with REV-101."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 5, 5, 10, 0.02, True, ""),
            ChapterRevisionStats("ch2.md", "ch2.md", 500, 5, 5, 10, 0.02, True, ""),
            ChapterRevisionStats("ch3.md", "ch3.md", 500, 5, 5, 10, 0.02, True, ""),
            ChapterRevisionStats("ch4.md", "ch4.md", 500, 5, 5, 10, 0.02, True, ""),
            ChapterRevisionStats("ch5.md", "ch5.md", 500, 5, 5, 10, 0.02, True, ""),
            ChapterRevisionStats("ch6.md", "ch6.md", 500, 250, 150, 400, 0.80, True, ""),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-101", ids)
        self.assertEqual(stats[5].flag, "REV-101")

    def test_analyze_churn_rev102_pristine(self):
        """Substantial chapter with snapshot and zero churn is flagged with REV-102."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 20, 10, 30, 0.06, True, ""),
            ChapterRevisionStats("ch2.md", "ch2.md", 250, 0, 0, 0, 0.0, True, ""),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-102", ids)
        self.assertEqual(stats[1].flag, "REV-102")

    def test_generate_heatmap_html_exists(self):
        """generate_revision_heatmap_html creates the destination file."""
        stats = [
            ChapterRevisionStats("01_Chapter.md", "01_Chapter.md", 300, 15, 5, 20, 0.067, True, "")
        ]
        churn_data = analyze_revision_churn(stats)
        churn_data["chapters"] = stats
        churn_data["manuscript"] = "Test Manuscript"

        html_out = Path(self.temp_dir.name) / "heatmap.html"
        generate_revision_heatmap_html(churn_data, html_out)
        self.assertTrue(html_out.is_file())

    def test_html_csp_compliance(self):
        """Generated HTML includes offline strict Content-Security-Policy meta tag."""
        stats = [
            ChapterRevisionStats("01_Chapter.md", "01_Chapter.md", 300, 10, 2, 12, 0.04, True, "")
        ]
        churn_data = analyze_revision_churn(stats)
        churn_data["chapters"] = stats
        churn_data["manuscript"] = "Test Manuscript"

        html_out = Path(self.temp_dir.name) / "heatmap_csp.html"
        generate_revision_heatmap_html(churn_data, html_out)
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    def test_html_contains_chapter_names(self):
        """Chapter filenames appear in the generated HTML table."""
        stats = [
            ChapterRevisionStats("01_Dawn_Awakening.md", "01_Dawn_Awakening.md", 420, 30, 10, 40, 0.095, True, "")
        ]
        churn_data = analyze_revision_churn(stats)
        churn_data["chapters"] = stats
        churn_data["manuscript"] = "Test Manuscript"

        html_out = Path(self.temp_dir.name) / "heatmap_names.html"
        generate_revision_heatmap_html(churn_data, html_out)
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("01_Dawn_Awakening.md", content)


if __name__ == "__main__":
    unittest.main()
