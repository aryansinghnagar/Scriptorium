#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Interactive Branching Narrative Graph
(tests/test_branching_graph.py)
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.branching_graph import (
    BranchingNarrativeEngine,
    main as branching_main,
)


class TestBranchingNarrativeGraph(unittest.TestCase):
    """Validates choice parsing, DAG topological validation, and multi-format compilation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # 1. Root / Start Node
        node_start = self.root / "01_Start.md"
        node_start.write_text(
            "---\n"
            "id: start\n"
            "title: The Crossroads\n"
            "root: true\n"
            "---\n"
            "You stand at a mist-shrouded crossroads. Two ancient paths diverge into the whispering forest.\n\n"
            "@choice: \"Take the high mountain trail\" -> mountain_pass\n"
            "@choice: \"Enter the sunken subterranean catacombs\" -> catacombs\n",
            encoding="utf-8",
        )

        # 2. Mountain Pass Node
        node_mountain = self.root / "Mountain_Pass.md"
        node_mountain.write_text(
            "---\n"
            "id: mountain_pass\n"
            "title: The High Ridge\n"
            "---\n"
            "A freezing gale buffets the narrow cliff edge. You discover an ancient eagle shrine.\n\n"
            "@state: courage + 1\n"
            "@choice: \"Climb to the Sun Sanctuary summit\" -> sanctuary [req: courage >= 1]\n"
            "@choice: \"Descend into the canyon abyss\" -> death_chasm\n",
            encoding="utf-8",
        )

        # 3. Catacombs Node
        node_catacombs = self.root / "Catacombs.md"
        node_catacombs.write_text(
            "---\n"
            "id: catacombs\n"
            "title: The Crypt of Echoes\n"
            "---\n"
            "Damp moss blankets the crumbling sarcophagi. You hear skittering in the shadows.\n\n"
            "@choice: \"Search the gilded sarcophagus\" -> sanctuary\n",
            encoding="utf-8",
        )

        # 4. Sanctuary Node (Victory Ending)
        node_sanctuary = self.root / "Sanctuary.md"
        node_sanctuary.write_text(
            "---\n"
            "id: sanctuary\n"
            "title: The Solar Sanctuary\n"
            "victory: true\n"
            "---\n"
            "Golden light floods the marble terrace as you claim the Sunstone Crown.\n\n"
            "@victory: true\n",
            encoding="utf-8",
        )

        # 5. Death Chasm Node (Death Ending)
        node_death = self.root / "Death_Chasm.md"
        node_death.write_text(
            "---\n"
            "id: death_chasm\n"
            "title: The Abyssal Pit\n"
            "death: true\n"
            "---\n"
            "The scree crumbles beneath your boots and you plunge into the darkness.\n\n"
            "@death: true\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_and_parse_branching_nodes(self) -> None:
        """Verifies parsing of nodes, choices, and root identification."""
        engine = BranchingNarrativeEngine()
        count = engine.load_from_directory(self.root)
        self.assertEqual(count, 5)
        self.assertEqual(engine.root_node_id, "start")

        start_node = engine.nodes["start"]
        self.assertEqual(len(start_node.choices), 2)
        self.assertEqual(start_node.choices[0].target_id, "mountain_pass")
        self.assertEqual(start_node.choices[1].target_id, "catacombs")

        mountain_node = engine.nodes["mountain_pass"]
        self.assertEqual(len(mountain_node.state_mutations), 1)
        self.assertEqual(mountain_node.state_mutations[0]["var"], "courage")

        sanctuary_node = engine.nodes["sanctuary"]
        self.assertTrue(sanctuary_node.is_victory)
        self.assertTrue(sanctuary_node.is_ending)

        death_node = engine.nodes["death_chasm"]
        self.assertTrue(death_node.is_death)
        self.assertTrue(death_node.is_ending)

    def test_topological_diagnostics_clean_graph(self) -> None:
        """Verifies zero diagnostics on a well-formed branching graph."""
        engine = BranchingNarrativeEngine()
        engine.load_from_directory(self.root)
        errors = [d for d in engine.diagnostics if d.severity == "error"]
        self.assertEqual(len(errors), 0)

    def test_detect_orphan_and_dead_end_nodes(self) -> None:
        """Verifies detection of unreachable nodes and untagged dead-ends."""
        # Add an orphan node
        orphan = self.root / "Orphan_Cave.md"
        orphan.write_text(
            "---\nid: orphan_cave\ntitle: Forgotten Cave\n---\n"
            "Nobody can ever reach this cave.\n\n"
            "@choice: \"Wait\" -> start\n",
            encoding="utf-8",
        )

        # Add a dead-end node (no choices and not marked ending)
        dead_end = self.root / "Dead_End.md"
        dead_end.write_text(
            "---\nid: dead_end\ntitle: Broken Bridge\n---\n"
            "You are stuck here forever.\n",
            encoding="utf-8",
        )

        engine = BranchingNarrativeEngine()
        engine.load_from_directory(self.root)

        codes = [d.code for d in engine.diagnostics]
        self.assertIn("BRN-102", codes)  # Orphan node
        self.assertIn("BRN-101", codes)  # Dead-end leaf

    def test_mermaid_export(self) -> None:
        """Verifies Obsidian Mermaid flowchart export."""
        engine = BranchingNarrativeEngine()
        engine.load_from_directory(self.root)
        mermaid = engine.export_mermaid()

        self.assertIn("```mermaid", mermaid)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("start", mermaid)
        self.assertIn("mountain_pass", mermaid)
        self.assertIn("sanctuary", mermaid)

    def test_ink_and_twine_export(self) -> None:
        """Verifies Inkle Ink and Twine 2 Twee export."""
        engine = BranchingNarrativeEngine()
        engine.load_from_directory(self.root)

        # Ink
        ink = engine.export_ink()
        self.assertIn("=== start ===", ink)
        self.assertIn("+ Take the high mountain trail -> mountain_pass", ink)
        self.assertIn("-> END // VICTORY", ink)

        # Twine
        twine = engine.export_twine_twee()
        self.assertIn(":: start", twine)
        self.assertIn("[[Take the high mountain trail->mountain_pass]]", twine)

    def test_playable_html_export(self) -> None:
        """Verifies playable standalone offline HTML5 reader generation with CSP."""
        engine = BranchingNarrativeEngine()
        engine.load_from_directory(self.root)
        html_doc = engine.export_playable_html()

        self.assertIn("<!DOCTYPE html>", html_doc)
        self.assertIn("Content-Security-Policy", html_doc)
        self.assertIn("default-src 'none'", html_doc)
        self.assertIn("The Crossroads", html_doc)

    def test_cli_execution(self) -> None:
        """Verifies CLI execution with multi-format outputs."""
        out_html = self.root / "gamebook.html"
        out_ink = self.root / "story.ink"
        out_twine = self.root / "story.twee"

        code = branching_main([
            str(self.root),
            "--html", str(out_html),
            "--ink", str(out_ink),
            "--twine", str(out_twine),
            "--audit",
        ])
        self.assertEqual(code, 0)
        self.assertTrue(out_html.is_file())
        self.assertTrue(out_ink.is_file())
        self.assertTrue(out_twine.is_file())

    def test_detect_missing_target_brn105(self) -> None:
        """Verifies BRN-105 error detection when choice points to non-existent node."""
        broken_node = self.root / "Broken_Bridge.md"
        broken_node.write_text(
            "---\nid: broken_bridge\ntitle: Broken Bridge\n---\n"
            "@choice: \"Jump across the void\" -> non_existent_destination\n",
            encoding="utf-8",
        )
        engine = BranchingNarrativeEngine()
        engine.load_from_directory(self.root)

        codes = [d.code for d in engine.diagnostics]
        self.assertIn("BRN-105", codes)
        diag = next(d for d in engine.diagnostics if d.code == "BRN-105")
        self.assertEqual(diag.severity, "error")
        self.assertIn("non_existent_destination", diag.message)

    def test_wikilink_choice_fallback(self) -> None:
        """Verifies fallback extraction of [[Target|Choice text]] wikilinks."""
        sub_dir = self.root / "WikiBranch"
        sub_dir.mkdir(parents=True, exist_ok=True)
        (sub_dir / "01_Start.md").write_text(
            "---\nid: entry\ntitle: Portal Room\nroot: true\n---\n"
            "You see two doors.\n\n"
            "[[Chamber_A|Open the left door]]\n"
            "[[Chamber_B|Open the right door]]\n",
            encoding="utf-8",
        )
        (sub_dir / "Chamber_A.md").write_text(
            "---\nid: Chamber_A\ntitle: Left Chamber\nending: true\n---\n"
            "A peaceful chamber.\n",
            encoding="utf-8",
        )
        (sub_dir / "Chamber_B.md").write_text(
            "---\nid: Chamber_B\ntitle: Right Chamber\nending: true\n---\n"
            "A treasure trove.\n",
            encoding="utf-8",
        )

        engine = BranchingNarrativeEngine()
        count = engine.load_from_directory(sub_dir)
        self.assertEqual(count, 3)
        entry_node = engine.nodes["entry"]
        self.assertEqual(len(entry_node.choices), 2)
        self.assertEqual(entry_node.choices[0].target_id, "Chamber_A")
        self.assertEqual(entry_node.choices[0].text, "Open the left door")

    def test_state_mutation_and_requirement_parsing(self) -> None:
        """Verifies parsing of @state and @req directives."""
        sub_dir = self.root / "StateVault"
        sub_dir.mkdir(parents=True, exist_ok=True)
        (sub_dir / "Node1.md").write_text(
            "---\nid: node_1\nroot: true\n---\n"
            "@state: gold += 50\n"
            "@set: has_lantern = true\n"
            "@req: keys >= 2\n"
            "@choice: \"Proceed\" -> node_2\n",
            encoding="utf-8",
        )
        (sub_dir / "Node2.md").write_text(
            "---\nid: node_2\nending: true\n---\n"
            "@ending: true\nDone.\n",
            encoding="utf-8",
        )

        engine = BranchingNarrativeEngine()
        engine.load_from_directory(sub_dir)
        node1 = engine.nodes["node_1"]
        self.assertEqual(len(node1.state_mutations), 2)
        self.assertEqual(node1.state_mutations[0]["var"], "gold")
        self.assertEqual(node1.state_mutations[0]["op"], "+=")
        self.assertEqual(node1.state_mutations[0]["val"], "50")
        self.assertEqual(len(node1.requirements), 1)
        self.assertIn("keys >= 2", node1.requirements)

    def test_root_auto_detection_fallback(self) -> None:
        """Verifies auto-detection of root node when no root: true is explicitly specified."""
        sub_dir = self.root / "NoRoot"
        sub_dir.mkdir(parents=True, exist_ok=True)
        (sub_dir / "Alpha.md").write_text(
            "---\nid: alpha\n---\n"
            "@choice: \"Go to Beta\" -> beta\n",
            encoding="utf-8",
        )
        (sub_dir / "Beta.md").write_text(
            "---\nid: beta\nending: true\n---\n"
            "@ending: true\nEnd.\n",
            encoding="utf-8",
        )

        engine = BranchingNarrativeEngine()
        count = engine.load_from_directory(sub_dir)
        self.assertEqual(count, 2)
        self.assertIsNotNone(engine.root_node_id)
        self.assertIn(engine.root_node_id, ["alpha", "beta"])

    def test_cli_json_and_mermaid_flags(self) -> None:
        """Verifies CLI execution with --mermaid and --json output."""
        from unittest.mock import patch
        out_mermaid = self.root / "output_graph.mermaid"

        # 1. Test Mermaid export
        code = branching_main([
            str(self.root),
            "--mermaid", str(out_mermaid),
            "--audit",
        ])
        self.assertEqual(code, 0)
        self.assertTrue(out_mermaid.is_file())

        # 2. Test JSON output
        with patch("builtins.print") as mock_print:
            code_json = branching_main([
                str(self.root),
                "--json",
            ])
            self.assertEqual(code_json, 0)
            mock_print.assert_called()
            printed_str = mock_print.call_args[0][0]
            data = json.loads(printed_str)
            self.assertIn("total_nodes", data)
            self.assertIn("diagnostics", data)
            self.assertEqual(data["total_nodes"], 5)


if __name__ == "__main__":
    unittest.main()
