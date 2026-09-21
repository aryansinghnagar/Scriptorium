#!/usr/bin/env python3
"""
Unit and integration tests for Ars Arcanum Threat Model & Security Posture (tests/test_threat_model.py)
"""

import unittest
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
SCRIPTS_DIR = REPO_ROOT / "scripts"
DOCS_DIR = REPO_ROOT / "docs"


class TestThreatModelAndSecurity(unittest.TestCase):

    def test_threat_model_document_exists(self):
        tm = DOCS_DIR / "THREAT_MODEL.md"
        self.assertTrue(tm.is_file(), "docs/THREAT_MODEL.md must exist")
        content = tm.read_text(encoding="utf-8")
        self.assertIn("STRIDE-Lite", content)
        self.assertIn("Spoofing Identity", content)
        self.assertIn("Tampering with Data", content)
        self.assertIn("Repudiation", content)
        self.assertIn("Information Disclosure", content)
        self.assertIn("Denial of Service", content)
        self.assertIn("Elevation of Privilege", content)
        self.assertIn("Content Security Policy", content)

    def test_all_html_generators_contain_csp(self):
        """Verify that every module generating HTML includes Content-Security-Policy meta tags."""
        html_files_checked = 0
        for py_file in LIB_DIR.glob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            if "<!DOCTYPE html>" in text or "<head>" in text:
                self.assertIn(
                    "Content-Security-Policy",
                    text,
                    f"{py_file.name} generates HTML but is missing Content-Security-Policy meta tag."
                )
                self.assertIn(
                    "default-src 'none'",
                    text,
                    f"{py_file.name} CSP does not declare strict default-src 'none'."
                )
                html_files_checked += 1

        self.assertGreaterEqual(html_files_checked, 25, "Expected at least 25 HTML generator modules")

    def test_no_external_cdn_scripts_in_library(self):
        """Verify zero external CDN scripts or stylesheet tags in library code."""
        cdn_patterns = [
            re.compile(r'https?://cdn\.', re.IGNORECASE),
            re.compile(r'https?://cdnjs\.', re.IGNORECASE),
            re.compile(r'https?://unpkg\.com', re.IGNORECASE),
            re.compile(r'https?://ajax\.googleapis\.com', re.IGNORECASE),
        ]
        for py_file in LIB_DIR.glob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            for pat in cdn_patterns:
                m = pat.search(text)
                self.assertIsNone(
                    m,
                    f"External CDN URL found in {py_file.name}: {m.group(0) if m else ''}"
                )

    def test_no_hardcoded_maintainers_email_in_scripts(self):
        """Verify no hardcoded maintainers@arsarcanum.local git author commits in scripts."""
        for sh_file in SCRIPTS_DIR.glob("*.sh"):
            text = sh_file.read_text(encoding="utf-8")
            self.assertNotIn(
                "maintainers@arsarcanum.local",
                text,
                f"Hardcoded maintainer email found in {sh_file.name}; use git_commit_safe instead."
            )

    def test_worlds_sh_defines_git_commit_safe(self):
        worlds_sh = LIB_DIR / "worlds.sh"
        self.assertTrue(worlds_sh.is_file())
        content = worlds_sh.read_text(encoding="utf-8")
        self.assertIn("git_commit_safe()", content)


if __name__ == "__main__":
    unittest.main()
