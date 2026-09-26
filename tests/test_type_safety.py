#!/usr/bin/env python3
"""
Test Suite: Type Safety & Static Contract Verification (tests/test_type_safety.py)
==================================================================================
Validates:
1. All critical craft and domain engines have valid type signatures on public interfaces.
2. If mypy is available in the environment, runs static analysis on scripts/lib/.
"""

import importlib
import inspect
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"


class TestTypeSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.has_mypy = shutil.which("mypy") is not None
        if str(REPO_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(REPO_ROOT / "scripts"))

    def test_mypy_static_type_check(self):
        """Run mypy on scripts/lib/ if mypy is installed."""
        if not self.has_mypy:
            self.skipTest("mypy is not installed in this environment (installed in CI)")

        res = subprocess.run(
            ["mypy", "--config-file", str(REPO_ROOT / "mypy.ini"), str(LIB_DIR)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0, f"Mypy reported type errors:\n{res.stdout}\n{res.stderr}")

    def test_public_engine_type_annotations(self):
        """Verify that core engines have return type annotations on primary public entry points."""
        modules_to_check = [
            ("lib.frontmatter", "parse_frontmatter"),
            ("lib.fs_utils", "atomic_write"),
            ("lib._bootstrap", "validate_volume_name"),
            ("lib.concordance", "generate_concordance"),
            ("lib.importer", "extract_docx_text"),
            ("lib.importer", "import_manuscript_batch"),
        ]

        for mod_name, func_name in modules_to_check:
            with self.subTest(module=mod_name, function=func_name):
                mod = importlib.import_module(mod_name)
                func = getattr(mod, func_name)
                sig = inspect.signature(func)
                self.assertIsNot(
                    sig.return_annotation,
                    inspect.Signature.empty,
                    f"Function {mod_name}.{func_name} should have a return type annotation",
                )


if __name__ == "__main__":
    unittest.main()

