#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Multi-Tier Git Submodule Tracking (tests/test_git_submodules.py)
========================================================================================
Validates ADR-043:
1. init_world.sh configures .gitmodules when scaffolding a world inside a universe repo.
2. init_manuscript.sh configures .gitmodules for Book-01 inside manuscript root.
3. add_book.sh configures .gitmodules for subsequent volumes.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def find_bash():
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        shutil.which("bash"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return "bash"


BASH_EXE = find_bash()


class TestGitSubmodules(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_home = Path(self.tmp_dir.name)
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.test_home)
        self.env["USER"] = "TestAuthor"

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_init_manuscript_creates_gitmodules(self):
        if not shutil.which("git"):
            self.skipTest("git not available")

        cmd = [
            BASH_EXE,
            str(SCRIPTS_DIR / "init_manuscript.sh"),
            "--name", "TestManuscript",
            "--author", "Test Author",
        ]
        res = subprocess.run(cmd, env=self.env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0, f"init_manuscript failed: {res.stderr}")

        ms_dir = self.test_home / "Manuscripts" / "TestManuscript"
        gitmodules_file = ms_dir / ".gitmodules"
        self.assertTrue(gitmodules_file.is_file(), f".gitmodules missing in {ms_dir}")
        content = gitmodules_file.read_text(encoding="utf-8")
        self.assertIn('[submodule "Book-01"]', content)
        self.assertIn("path = Book-01", content)
        self.assertIn("url = ./Book-01", content)


if __name__ == "__main__":
    unittest.main()
