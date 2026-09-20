#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Stylistics, Dialogue Mechanics & Readability Rhythm Engine
(scripts/lib/stylistics.py).
Validates:
- PRO-101: Dialogue tag classification, said-bookisms detection, adverb tag alerts, quote punctuation.
- PRO-102: Word echoes repetition detection within sliding windows.
- PRO-105: Readability rhythm metrics (sentence variance, Flesch-Kincaid, Flesch Reading Ease, Fog index).
- Standalone HTML report generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.stylistics import (
    analyze_dialogue_mechanics,
    analyze_word_echoes,
    analyze_readability_rhythm,
    scan_text_or_path,
    generate_stylistics_html_report,
    count_syllables
)


class TestStylisticsEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dialogue_mechanics_said_bookisms(self):
        text = """
        "We must breach the citadel," Vaelor bellowed.
        "Never in this lifetime," Malakar sneered.
        "Then prepare yourself," Vaelor opined.
        """
        dia = analyze_dialogue_mechanics(text)
        self.assertGreater(dia["said_bookisms_count"], 1)
        bookism_words = [b["word"].lower() for b in dia["said_bookisms"]]
        self.assertIn("bellowed", bookism_words)
        self.assertIn("sneered", bookism_words)
        self.assertIn("opined", bookism_words)

    def test_dialogue_adverb_tags(self):
        text = """
        "Drop the blade," she said angrily.
        "Make me," he replied fiercely.
        "As you wish," she whispered quietly.
        """
        dia = analyze_dialogue_mechanics(text)
        self.assertEqual(dia["adverb_tags_count"], 3)
        adverbs = [a["adverb"].lower() for a in dia["adverb_tags"]]
        self.assertIn("angrily", adverbs)
        self.assertIn("fiercely", adverbs)
        self.assertIn("quietly", adverbs)

    def test_dialogue_punctuation_formatting(self):
        text = """
        "I will go alone." said Vance.
        "No you will not," He said.
        """
        dia = analyze_dialogue_mechanics(text)
        self.assertEqual(dia["formatting_issues_count"], 2)
        issue_types = [i["type"] for i in dia["formatting_issues"]]
        self.assertIn("period_before_tag", issue_types)
        self.assertIn("capitalized_tag_pronoun", issue_types)

    def test_word_echoes_detection(self):
        text = """
        The obsidian fortress rose menacingly above the desolate plateau.
        The wind howled across the crags as they looked toward the fortress.
        Within moments, the dark obsidian stone began to tremble.
        """
        echoes_res = analyze_word_echoes(text, window_size=50)
        self.assertGreater(echoes_res["echo_count"], 0)
        echo_words = [e["word"].lower() for e in echoes_res["echoes"]]
        self.assertTrue("fortress" in echo_words or "obsidian" in echo_words)

    def test_readability_rhythm_metrics(self):
        text = """
        The ancient archivist walked along the silent corridor. He carried a heavy iron lantern in his trembling hand. Every step echoed against the cold stone floor of the subterranean library. He paused before the gilded oak doorway and inserted the tarnished key into the lock.
        """
        rhythm = analyze_readability_rhythm(text)
        self.assertEqual(rhythm["sentence_count"], 4)
        self.assertGreater(rhythm["mean_sentence_length"], 10.0)
        self.assertGreater(rhythm["flesch_reading_ease"], 0.0)
        self.assertGreater(rhythm["flesch_kincaid_grade"], 0.0)

    def test_staccato_cluster_detection(self):
        text = "Run now. Stop here. Look up. Fire away. He fell."
        rhythm = analyze_readability_rhythm(text)
        self.assertGreater(len(rhythm["staccato_clusters"]), 0)

    def test_full_scan_and_html_generation(self):
        sample_file = self.target_dir / "01_Chapter.md"
        sample_file.write_text("""# Chapter 1\n"Halt," Vance shouted angrily. Vance stared at the fortress.\nHe saw the fortress again.""", encoding="utf-8")
        report = scan_text_or_path(sample_file)
        self.assertEqual(report["total_files"], 1)

        out_html = self.target_dir / "stylistics_report.html"
        generate_stylistics_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        html_text = out_html.read_text(encoding="utf-8")
        self.assertIn("Stylistics, Dialogue Mechanics & Readability Report", html_text)
        self.assertIn("<svg", html_text)

    def test_syllable_counter(self):
        self.assertEqual(count_syllables("cat"), 1)
        self.assertEqual(count_syllables("palace"), 2)
        self.assertEqual(count_syllables("astrophysics"), 4)


if __name__ == "__main__":
    unittest.main()
