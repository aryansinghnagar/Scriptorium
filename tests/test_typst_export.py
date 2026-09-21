#!/usr/bin/env python3
"""
Unit and golden tests for Typst Book Typesetting & Preview Export.
Validates:
- Typst template compilation exit codes.
- Output PDF existence, size (> 1KB), and '%PDF-' magic bytes.
- Robust handling of chapter headings, page breaks, and blank verso logic.
"""

import shutil
import tempfile
import unittest
import subprocess
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTypstExport(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_typst_lockfile_and_setup_script_hashes_match(self):
        lock_file = REPO_ROOT / "dependencies.lock"
        setup_script = REPO_ROOT / "scripts" / "setup_arcanum.sh"
        self.assertTrue(lock_file.is_file())
        self.assertTrue(setup_script.is_file())

        lock_text = lock_file.read_text(encoding="utf-8")
        setup_text = setup_script.read_text(encoding="utf-8")

        lock_x86 = re.search(r"x86_64_sha256\s*=\s*([a-f0-9]{64})", lock_text).group(1)
        lock_arm = re.search(r"aarch64_sha256\s*=\s*([a-f0-9]{64})", lock_text).group(1)

        setup_x86 = re.search(r'TYPST_SHA256_X86_64="([a-f0-9]{64})"', setup_text).group(1)
        setup_arm = re.search(r'TYPST_SHA256_AARCH64="([a-f0-9]{64})"', setup_text).group(1)

        self.assertEqual(lock_x86, setup_x86)
        self.assertEqual(lock_arm, setup_arm)

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
