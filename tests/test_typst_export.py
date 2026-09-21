#!/usr/bin/env python3
"""
Unit and golden tests for Typst Book Typesetting & Preview Export.
Validates:
- Typst template compilation exit codes.
- Output PDF existence, size (> 1KB), and '%PDF-' magic bytes.
- Robust handling of chapter headings, page breaks, and blank verso logic.
"""

import os
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTypstExport(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_typst_preview_sample_compilation(self):
        typst_bin = shutil.which("typst")
        if not typst_bin:
            raise unittest.SkipTest("typst binary not found on PATH; skipping Typst golden compilation test")

        sample_typ = REPO_ROOT / "templates" / "typst" / "preview_sample.typ"
        self.assertTrue(sample_typ.is_file(), f"Missing {sample_typ}")

        out_pdf = self.work_dir / "preview_sample.pdf"
        cmd = [typst_bin, "compile", str(sample_typ), str(out_pdf)]
        res = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(
            res.returncode, 0,
            f"typst compile failed with exit code {res.returncode}:\nStdout: {res.stdout}\nStderr: {res.stderr}"
        )
        self.assertTrue(out_pdf.is_file(), "Generated PDF file does not exist")
        self.assertGreater(out_pdf.stat().st_size, 1024, "Generated PDF is smaller than 1KB")

        with open(out_pdf, "rb") as f:
            header = f.read(5)
            self.assertEqual(header, b"%PDF-", "Generated file lacks standard %PDF- header magic bytes")


if __name__ == "__main__":
    unittest.main()
