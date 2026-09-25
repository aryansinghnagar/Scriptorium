#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Diagnostics Engine (scripts/lib/diagnostics.py)
"""

import unittest
from pathlib import Path
import sys
import logging

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.diagnostics import (
    get_state_dir,
    setup_logging,
    redact_sensitive_paths,
    get_toolchain_diagnostics,
    generate_diagnostic_report,
    format_diagnostic_report_markdown,
)


class TestDiagnostics(unittest.TestCase):

    def test_get_state_dir(self):
        state_dir = get_state_dir()
        self.assertTrue(state_dir.is_dir())
        self.assertIn("ars-arcanum", str(state_dir))

    def test_setup_logging(self):
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        logger.info("Test diagnostics log entry")

    def test_redact_sensitive_paths(self):
        home_path = str(Path.home())
        sensitive_text = f"Error in file: {home_path}/Documents/SecretNovel.md"
        redacted = redact_sensitive_paths(sensitive_text)
        self.assertNotIn(home_path, redacted)
        self.assertIn("~/Documents/SecretNovel.md", redacted)

    def test_get_toolchain_diagnostics(self):
        tc = get_toolchain_diagnostics()
        self.assertIn("tools", tc)
        self.assertIn("python", tc["tools"])
        self.assertTrue(tc["tools"]["python"]["available"])

    def test_generate_diagnostic_report(self):
        report = generate_diagnostic_report()
        self.assertIn("version", report)
        self.assertIn("system", report)
        self.assertIn("toolchain", report)

        md = format_diagnostic_report_markdown(report)
        self.assertIn("Ars Arcanum Diagnostic Triage Report", md)
        self.assertIn("Toolchain & Dependencies", md)

    def test_run_doctor_report(self):
        from lib.diagnostics import run_doctor_report
        rc = run_doctor_report(as_json=True)
        self.assertIn(rc, (0, 1))


if __name__ == "__main__":
    unittest.main()
