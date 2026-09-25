#!/usr/bin/env python3
"""
Unit test to verify that all Bash shell scripts in the repository have valid syntax (tests/test_shell_scripts_syntax.py).
Uses `bash -n` to perform static syntax checking without execution.
"""

import os
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestShellScriptsSyntax(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bash_exe = None
        for candidate in [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
            shutil.which("bash"),
        ]:
            if candidate and os.path.isfile(candidate):
                cls.bash_exe = candidate
                break

    def test_all_shell_scripts_syntax(self):
        if not self.bash_exe:
            self.skipTest("Bash executable not found on system.")

        sh_files = sorted(
            list((REPO_ROOT / "scripts").rglob("*.sh"))
            + list((REPO_ROOT / "tests").rglob("*.sh"))
        )
        self.assertGreater(len(sh_files), 10, "Should discover shell scripts")

        for script_file in sh_files:
            with self.subTest(script=script_file.name):
                res = subprocess.run(
                    [self.bash_exe, "-n", str(script_file)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    res.returncode,
                    0,
                    f"Syntax error in {script_file.relative_to(REPO_ROOT)}:\n{res.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
