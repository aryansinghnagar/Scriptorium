#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Open-Source Governance & Sustainability Charters (tests/test_governance_docs.py).
Validates:
- P5-M1: Maintenance & Branch Protection specifications.
- P5-M2: Sustainability & Funding documentation.
- P5-M4: Project Governance charter.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestGovernanceDocs(unittest.TestCase):

    def test_governance_charter_exists_and_complete(self):
        gov_file = REPO_ROOT / "docs" / "GOVERNANCE.md"
        self.assertTrue(gov_file.is_file(), "docs/GOVERNANCE.md must exist")

        content = gov_file.read_text(encoding="utf-8")
        self.assertIn("Governance Principles", content)
        self.assertIn("Roles & Responsibilities", content)
        self.assertIn("Decision-Making & RFC Process", content)
        self.assertIn("Release Cadence & Versioning", content)
        self.assertIn("Security & Vulnerability Disclosure", content)

    def test_sustainability_model_exists_and_complete(self):
        sust_file = REPO_ROOT / "docs" / "SUSTAINABILITY.md"
        self.assertTrue(sust_file.is_file(), "docs/SUSTAINABILITY.md must exist")

        content = sust_file.read_text(encoding="utf-8")
        self.assertIn("Independence & Freedom Pledge", content)
        self.assertIn("Funding Streams & Financial Stewardship", content)
        self.assertIn("GitHub Sponsors", content)

    def test_funding_configuration_exists(self):
        funding_file = REPO_ROOT / ".github" / "FUNDING.yml"
        self.assertTrue(funding_file.is_file(), ".github/FUNDING.yml must exist")

        content = funding_file.read_text(encoding="utf-8")
        self.assertIn("github:", content)
        self.assertIn("open_collective:", content)


if __name__ == "__main__":
    unittest.main()
