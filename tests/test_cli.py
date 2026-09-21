#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Unified CLI Dispatcher (scripts/lib/cli.py)
"""

import unittest
from pathlib import Path
import sys
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.cli import main


class TestCLI(unittest.TestCase):

    def test_version_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["--version"])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum v", mock_out.getvalue())

    def test_help_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["--help"])
            self.assertEqual(rc, 0)
            self.assertIn("✍️  Core Authoring & Editorial Craft:", mock_out.getvalue())

    def test_engines_subcommand(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["engines"])
            self.assertEqual(rc, 0)
            val = mock_out.getvalue()
            self.assertIn("Registered Plugins & Engines", val)
            self.assertIn("[CORE]", val)
            self.assertIn("[CRAFT]", val)

    def test_unknown_command(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["unknown_invalid_command_xyz"])
            self.assertEqual(rc, 2)
            self.assertIn("Unknown command", mock_err.getvalue())

    def test_doctor_dispatch(self):
        with patch("lib.diagnostics.main", return_value=0) as mock_diag:
            rc = main(["doctor", "--report"])
            self.assertEqual(rc, 0)
            mock_diag.assert_called_once_with(["--report"])


if __name__ == "__main__":
    unittest.main()
