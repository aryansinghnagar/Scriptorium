#!/usr/bin/env python3
"""
Unit test for version consistency across CLI, package definitions, and documentation (tests/test_version_consistency.py).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARCANUM_BASH = REPO_ROOT / "scripts" / "arcanum"
CLI_PY = REPO_ROOT / "scripts" / "lib" / "cli.py"
DEBIAN_CHANGELOG = REPO_ROOT / "debian" / "changelog"
CHANGELOG_MD = REPO_ROOT / "CHANGELOG.md"


class TestVersionConsistency(unittest.TestCase):
    """Ensures version numbers across all dispatchers and packaging manifests are synchronized."""

    def test_version_strings_match(self):
        # 1. Read Bash dispatcher version
        self.assertTrue(ARCANUM_BASH.is_file())
        bash_text = ARCANUM_BASH.read_text(encoding="utf-8")
        bash_match = re.search(r'VERSION="([^"]+)"', bash_text)
        self.assertIsNotNone(bash_match, "Could not find VERSION in scripts/arcanum")
        bash_version = bash_match.group(1)

        # 2. Read Python CLI version
        self.assertTrue(CLI_PY.is_file())
        py_text = CLI_PY.read_text(encoding="utf-8")
        py_match = re.search(r'VERSION\s*=\s*"([^"]+)"', py_text)
        self.assertIsNotNone(py_match, "Could not find VERSION in scripts/lib/cli.py")
        py_version = py_match.group(1)

        # 3. Read Debian changelog version
        self.assertTrue(DEBIAN_CHANGELOG.is_file())
        deb_text = DEBIAN_CHANGELOG.read_text(encoding="utf-8")
        deb_match = re.search(r'ars-arcanum\s*\(([0-9.]+)(?:-[0-9]+)?\)', deb_text)
        self.assertIsNotNone(deb_match, "Could not find version in debian/changelog")
        deb_version = deb_match.group(1)

        # 4. Check CHANGELOG.md top released version
        self.assertTrue(CHANGELOG_MD.is_file())
        changelog_text = CHANGELOG_MD.read_text(encoding="utf-8")
        cl_match = re.search(r'##\s*\[([0-9.]+)\]', changelog_text)
        self.assertIsNotNone(cl_match, "Could not find version header in CHANGELOG.md")
        cl_version = cl_match.group(1)

        # Assert all versions match
        self.assertEqual(
            bash_version,
            py_version,
            f"Bash version ({bash_version}) does not match Python CLI version ({py_version})"
        )
        self.assertEqual(
            py_version,
            deb_version,
            f"Python CLI version ({py_version}) does not match Debian changelog ({deb_version})"
        )
        self.assertEqual(
            py_version,
            cl_version,
            f"Python CLI version ({py_version}) does not match CHANGELOG.md ({cl_version})"
        )


if __name__ == "__main__":
    unittest.main()
