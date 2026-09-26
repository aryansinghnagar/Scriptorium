#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Unified Python CLI Dispatcher (tests/test_cli_dispatch.py)
===================================================================================
Validates command routing, alias dispatch, plugin listing, and error handling.
"""

from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import VERSION, main


class TestCliDispatch(unittest.TestCase):
    """Unit tests for lib.cli command routing."""

    def test_version_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["--version"])
            self.assertEqual(rc, 0)
            self.assertIn(f"Ars Arcanum v{VERSION}", mock_out.getvalue())

    def test_help_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["--help"])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum Unified CLI", mock_out.getvalue())
            self.assertIn("Core Authoring & Editorial Craft:", mock_out.getvalue())

    def test_engines_list_command(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["engines"])
            self.assertEqual(rc, 0)
            output = mock_out.getvalue()
            self.assertIn("Ars Arcanum Registered Plugins & Engines", output)
            self.assertIn("astrophysics", output)
            self.assertIn("cartography", output)

    
    def test_calc_subcommands_route_help(self):
        calc_targets = [
            "transit", "time-dilation", "orbit", "comms",
            "journey", "battle", "climate"
        ]
        for sub in calc_targets:
            with patch("sys.stdout", new_callable=StringIO):
                rc = main(["calc", sub, "--help"])
                self.assertIn(rc, (0, None))

    def test_calc_without_subcommand_shows_usage(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["calc"])
            self.assertEqual(rc, 2)
            self.assertIn("Usage: arcanum calc", mock_err.getvalue())

    def test_audit_subcommands_route_help(self):
        audit_targets = [
            "voice", "style", "dialogue", "echoes",
            "scenes", "structure", "idioms", "senses"
        ]
        for sub in audit_targets:
            with patch("sys.stdout", new_callable=StringIO):
                rc = main(["audit", sub, "--help"])
                self.assertIn(rc, (0, None))

    def test_speculative_craft_subcommands_route_help(self):
        subcmds = [
            ["magic-check", "--help"],
            ["magic-report", "--help"],
            ["genealogy", "--help"],
            ["lineage", "--help"],
            ["conlang", "--help"],
            ["calendar", "--help"],
            ["concordance", "--help"],
            ["series", "--help"],
            ["causality", "--help"],
            ["economy", "--help"],
            ["ecology", "--help"],
            ["faction", "--help"],
            ["plot", "--help"],
            ["structure", "--help"],
            ["ambient", "--help"],
            ["portfolio", "--help"],
            
            ["matter", "--help"],
            ["polish", "typography", "--help"],
            ["preflight", "--help"],
            ["docx", "--help"],
            ["pace", "--help"],
            ["tension", "--help"],
        ]
        for sub in subcmds:
            with patch("sys.stdout", new_callable=StringIO):
                rc = main(sub)
                self.assertIn(rc, (0, None))

    def test_doc_and_guide_commands(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc"])
            self.assertEqual(rc, 0)
            self.assertIn("Author Craft Guide & Advisory Matrix", mock_out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "astrophysics"])
            self.assertEqual(rc, 0)
            val = mock_out.getvalue()
            self.assertIn("ASTROPHYSICS & ORBITAL MECHANICS", val)
            self.assertIn("Engine Logic & Scientific / Structural Foundations:", val)
            self.assertIn("Advisory Mechanics & Creative Freedom Resolution Pathways:", val)

        # Multi-word command doc lookup
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "calc", "astro"])
            self.assertEqual(rc, 0)
            self.assertIn("ASTROPHYSICS & ORBITAL MECHANICS", mock_out.getvalue())

        # Hyphenated engine name lookup
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "magic-system"])
            self.assertEqual(rc, 0)
            self.assertIn("MAGIC SYSTEM CONSTRAINTS", mock_out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["guide", "climate"])
            self.assertEqual(rc, 0)
            self.assertIn("PLANETARY CLIMATE & KÖPPEN BIOMES", mock_out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["explain", "magic_system"])
            self.assertEqual(rc, 0)
            self.assertIn("MAGIC SYSTEM CONSTRAINTS", mock_out.getvalue())

    def test_doc_unknown_engine(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["doc", "totally_fake_engine"])
            self.assertEqual(rc, 1)
            self.assertIn("No documentation found for engine: 'totally_fake_engine'", mock_err.getvalue())

    def test_unknown_command_suggests_close_match(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["prefligt"])
            self.assertEqual(rc, 2)
            self.assertIn("Did you mean 'preflight'?", mock_err.getvalue())

    def test_unknown_command_generic_error(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["xyzabc123nonexistent"])
            self.assertEqual(rc, 2)
            self.assertIn("Error: Unknown command 'xyzabc123nonexistent'", mock_err.getvalue())


if __name__ == "__main__":
    unittest.main()

