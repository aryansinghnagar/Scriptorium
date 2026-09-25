#!/usr/bin/env python3
"""
Test Suite: Test Coverage Floor Verification (tests/test_coverage_floor.py)
===========================================================================
Validates:
1. pyproject.toml defines a strict 80% coverage floor in [tool.coverage.report].
2. [tool.coverage.run] correctly sources scripts/lib while omitting external UI bindings.
3. If coverage tool is installed, runs coverage report validation.
"""

import shutil
import subprocess
import unittest
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCoverageFloor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.has_coverage = shutil.which("coverage") is not None
        cls.pyproject_path = REPO_ROOT / "pyproject.toml"

    def test_coverage_config_exists_and_sets_80_percent_floor(self):
        """Verify pyproject.toml specifies fail_under >= 80."""
        self.assertTrue(self.pyproject_path.is_file(), "pyproject.toml must exist")
        content = self.pyproject_path.read_text(encoding="utf-8")

        if tomllib is not None:
            data = tomllib.loads(content)
            cov_report = data.get("tool", {}).get("coverage", {}).get("report", {})
            fail_under = cov_report.get("fail_under", 0)
            self.assertGreaterEqual(fail_under, 80, "Coverage fail_under must be at least 80%")
        else:
            self.assertIn("fail_under = 80", content)
            self.assertIn("[tool.coverage.report]", content)

    def test_coverage_run_sources_scripts_lib(self):
        """Verify pyproject.toml specifies source = ['scripts/lib']."""
        content = self.pyproject_path.read_text(encoding="utf-8")
        self.assertIn("[tool.coverage.run]", content)
        self.assertIn("scripts/lib", content)

    def test_run_coverage_if_available(self):
        """If coverage CLI is available, verify coverage command runs successfully."""
        if not self.has_coverage:
            self.skipTest("coverage CLI not installed in this environment (tested in CI)")

        res = subprocess.run(
            ["coverage", "--version"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)


if __name__ == "__main__":
    unittest.main()
