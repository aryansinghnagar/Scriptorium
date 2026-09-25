#!/usr/bin/env python3
"""
Test Suite: Multi-Perspective Autonomous Editorial Council Engine
(tests/test_editorial_council.py)
================================================================================
Validates persona evaluations (Line Editor, Lore Inquisitor, Story Architect,
Continuity Overseer), consensus calculation, dissent detection, and dashboard outputs.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.editorial_council import (
    conduct_editorial_council,
    evaluate_continuity_overseer,
    evaluate_line_editor,
    evaluate_lore_inquisitor,
    evaluate_story_architect,
    generate_council_html_dashboard,
    generate_council_markdown_report,
    main as council_main,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestEditorialCouncil(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create mock world vault
        self.world_dir = self.root / "Eldoria-Prime"
        self.chars_dir = self.world_dir / "Characters"
        self.chars_dir.mkdir(parents=True)
        (self.chars_dir / "Aeloria.md").write_text(
            """---
name: "Aeloria Vael"
type: "character"
faction: "[[Silver-Dawn]]"
---
# Aeloria Vael
Champion of the floating citadel.
""",
            encoding="utf-8",
        )

        # Create mock manuscript
        self.ms_dir = self.root / "Book-01" / "Draft-01"
        self.ms_dir.mkdir(parents=True)

        (self.ms_dir / "01_Chapter.md").write_text(
            """---
title: "The Fractured Spire"
chapter: 1
pov: "[[Aeloria-Vael]]"
location: "[[High-Sanctuary]]"
---

# The Fractured Spire

Dawn broke over the floating citadel in brilliant shards of amber and cold azure light.

Aeloria stood upon the high ramparts, her fingertips grazing the icy hilt of her crystalline blade. A distant murmur of thunder echoed across the mountain peaks below.

"The resonance currents are trembling again," Archmage [[Archmage-Theron]] said calmly.

"Then we must prepare the [[Silver-Dawn]]," replied Aeloria.
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_evaluate_line_editor(self):
        sample_chaps = [{
            "file": "01_Chapter.md",
            "title": "The Fractured Spire",
            "word_count": 80,
            "body": "Dawn broke in azure light. Cold wind blew through the quiet valley. 'Ready?' he said.",
        }]
        review = evaluate_line_editor(sample_chaps)
        self.assertEqual(review.persona_id, "line_editor")
        self.assertGreater(review.score, 0)
        self.assertIn("Lady Cassian", review.name)
        self.assertTrue(len(review.strengths) > 0 or len(review.critiques) > 0)

    def test_evaluate_lore_inquisitor(self):
        sample_chaps = [{
            "file": "01_Chapter.md",
            "title": "The Fractured Spire",
            "word_count": 80,
            "body": "Aeloria visited [[High-Sanctuary]] and invoked [[Aether-Weaving]] with the [[Silver-Dawn]].",
        }]
        review = evaluate_lore_inquisitor(sample_chaps, world_path=self.world_dir)
        self.assertEqual(review.persona_id, "lore_inquisitor")
        self.assertGreaterEqual(review.score, 80)
        self.assertIn("Archon Vaelor", review.name)

    def test_evaluate_story_architect(self):
        sample_chaps = [{
            "file": "01_Chapter.md",
            "title": "The Fractured Spire",
            "word_count": 350,
            "body": 'He walked into the dark citadel. "We cannot stay here," she said. "The gate is closing." He nodded and drew his sword.',
        }]
        review = evaluate_story_architect(sample_chaps)
        self.assertEqual(review.persona_id, "story_architect")
        self.assertGreater(review.score, 0)
        self.assertIn("Grand Architect Soren", review.name)

    def test_evaluate_continuity_overseer(self):
        sample_chaps = [{
            "file": "01_Chapter.md",
            "title": "The Fractured Spire",
            "word_count": 80,
            "frontmatter": {"pov": "[[Aeloria]]", "location": "[[Sanctuary]]"},
            "body": "@pov: Aeloria\n@location: Sanctuary\nShe stood alone.",
        }]
        review = evaluate_continuity_overseer(sample_chaps)
        self.assertEqual(review.persona_id, "continuity_overseer")
        self.assertGreaterEqual(review.score, 80)
        self.assertIn("Chronicler Mirella", review.name)

    def test_conduct_full_editorial_council(self):
        report = conduct_editorial_council(self.ms_dir, world_path=self.world_dir)
        self.assertEqual(report.target_name, "Draft-01")
        self.assertEqual(report.total_chapters, 1)
        self.assertGreater(report.total_words, 0)
        self.assertGreater(report.consensus_score, 0)
        self.assertEqual(len(report.reviews), 4)

        # Validate Markdown Report
        md_text = generate_council_markdown_report(report)
        self.assertIn("Sovereign Editorial Council Consensus Report", md_text)
        self.assertIn("Lady Cassian", md_text)
        self.assertIn("Archon Vaelor", md_text)
        self.assertIn("Grand Architect Soren", md_text)
        self.assertIn("Chronicler Mirella", md_text)

        # Validate HTML Dashboard
        out_html = self.root / "council_dashboard.html"
        generate_council_html_dashboard(report, out_html)
        self.assertTrue(out_html.exists())
        html_content = out_html.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", html_content)
        self.assertIn("Sovereign Editorial Council", html_content)
        self.assertIn("Master Revision Action Items", html_content)

    def test_line_editor_said_bookisms_detection(self):
        """Verifies that excessive said-bookisms are flagged by Line Editor."""
        sample_chaps = [{
            "file": "01_Chapter.md",
            "title": "Noisy Dialogue",
            "word_count": 100,
            "body": '"Stop!" he screeched. "Never!" she bellowed. "Why?" he snarled. "Because!" she hissed.',
        }]
        review = evaluate_line_editor(sample_chaps)
        self.assertTrue(any("dialogue" in c.lower() or "said" in c.lower() or "bookism" in c.lower() for c in review.critiques))

    def test_lore_inquisitor_missing_world_dir(self):
        """Verifies that lore evaluation functions gracefully without a world directory."""
        sample_chaps = [{
            "file": "01_Chapter.md",
            "title": "Standalone Chapter",
            "word_count": 120,
            "body": "The hero crossed the river into the enchanted woods of [[Silvershade]].",
        }]
        review = evaluate_lore_inquisitor(sample_chaps, world_path=None)
        self.assertEqual(review.persona_id, "lore_inquisitor")
        self.assertGreater(review.score, 0)
        self.assertIsNotNone(review.verdict)

    def test_story_architect_pacing_detection(self):
        """Verifies story architect pacing evaluation across multiple scenes."""
        sample_chaps = [
            {"file": "01.md", "title": "Chap 1", "word_count": 1200, "body": "Introductory words." * 50},
            {"file": "02.md", "title": "Chap 2", "word_count": 1500, "body": "Rising action prose." * 60},
            {"file": "03.md", "title": "Chap 3", "word_count": 1800, "body": "Climactic battle." * 70},
        ]
        review = evaluate_story_architect(sample_chaps)
        self.assertEqual(review.persona_id, "story_architect")
        self.assertGreater(review.score, 0)

    def test_continuity_overseer_missing_pov_flag(self):
        """Verifies continuity overseer detects chapters lacking explicit POV tagging."""
        sample_chaps = [{
            "file": "01_Untagged.md",
            "title": "Untagged Passage",
            "word_count": 150,
            "frontmatter": {},
            "body": "A shadowy figure roamed the silent corridors without any identity.",
        }]
        review = evaluate_continuity_overseer(sample_chaps)
        self.assertEqual(review.persona_id, "continuity_overseer")
        self.assertGreater(len(review.critiques) + len(review.recommendations), 0)

    def test_council_dissent_and_consensus_metrics(self):
        """Verifies consensus calculation across varied persona scores."""
        report = conduct_editorial_council(self.ms_dir)
        self.assertIsInstance(report.consensus_score, int)
        self.assertTrue(0 <= report.consensus_score <= 100)
        self.assertIsInstance(report.dissenting_notes, list)

    def test_pristine_manuscript_high_score(self):
        """Verifies that rich multi-sensory text with strong POV receives high praise."""
        rich_ms = self.root / "RichManuscript"
        rich_ms.mkdir(parents=True, exist_ok=True)
        (rich_ms / "01_Rich.md").write_text(
            """---
title: "The Silver Citadel"
chapter: 1
pov: "[[Aeloria-Vael]]"
location: "[[High-Sanctuary]]"
---
@pov: Aeloria
@location: High-Sanctuary

Dawn broke over the high terrace in cold azure light. Aeloria touched the smooth steel hilt of her blade.
A sudden whisper of wind brought the sweet scent of pine and burning incense from the distant temple braziers.
"We move at midnight," she said softly.
""",
            encoding="utf-8",
        )
        report = conduct_editorial_council(rich_ms, world_path=self.world_dir)
        self.assertGreaterEqual(report.consensus_score, 70)

    def test_cli_editorial_council_execution(self):
        """Verifies CLI execution with HTML and JSON outputs."""
        from unittest.mock import patch
        out_html = self.root / "cli_council.html"
        out_md = self.root / "cli_council.md"

        with patch("sys.argv", [
            "editorial_council.py",
            str(self.ms_dir),
            "-w", str(self.world_dir),
            "--html", str(out_html),
            "--report", str(out_md),
        ]):
            council_main()
            self.assertTrue(out_html.exists())
            self.assertTrue(out_md.exists())

        with patch("sys.argv", [
            "editorial_council.py",
            str(self.ms_dir),
            "-w", str(self.world_dir),
            "--json",
        ]), patch("builtins.print") as mock_print:
            council_main()
            mock_print.assert_called()
            data = json.loads(mock_print.call_args[0][0])
            self.assertIn("consensus_score", data)
            self.assertIn("reviews", data)


if __name__ == "__main__":
    unittest.main()
