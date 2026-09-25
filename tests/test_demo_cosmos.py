#!/usr/bin/env python3
"""
Unit and integration tests for the Eldoria Demo Cosmos template (tests/test_demo_cosmos.py).
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from world_doctor import check_world
from series_continuity import extract_book_entities

DEMO_COSMOS_DIR = REPO_ROOT / "templates" / "demo-cosmos" / "Eldoria-Cosmos"
DEMO_WORLD_DIR = DEMO_COSMOS_DIR / "Eldoria-Prime"
DEMO_MS_DIR = DEMO_COSMOS_DIR / "Manuscripts" / "The-Silver-Chronicles"


class TestDemoCosmos(unittest.TestCase):

    def test_demo_cosmos_files_exist(self):
        self.assertTrue(DEMO_COSMOS_DIR.is_dir(), "demo-cosmos directory must exist")
        self.assertTrue((DEMO_COSMOS_DIR / "universe.yaml").is_file())
        self.assertTrue((DEMO_COSMOS_DIR / "Universe-Index.md").is_file())
        self.assertTrue((DEMO_WORLD_DIR / "world.yaml").is_file())
        self.assertTrue((DEMO_WORLD_DIR / "World-Bible-Index.md").is_file())
        self.assertTrue((DEMO_MS_DIR / "manuscript.yaml").is_file())
        self.assertTrue((DEMO_MS_DIR / "nwProject.nwx").is_file())

    def test_world_doctor_passes_on_demo_cosmos(self):
        """Ensures that the demo cosmos lore vault passes world_doctor with zero broken links or missing fields."""
        findings = check_world(
            str(DEMO_WORLD_DIR),
            manuscript_dir=str(DEMO_MS_DIR / "Book-01" / "Draft-01"),
        )
        self.assertEqual(len(findings["broken_links"]), 0, f"Broken links found: {findings['broken_links']}")
        self.assertEqual(len(findings["missing_required_fields"]), 0, f"Missing fields: {findings['missing_required_fields']}")
        self.assertEqual(len(findings["frontmatter_parse_errors"]), 0, f"FM errors: {findings['frontmatter_parse_errors']}")
        self.assertEqual(len(findings["timeline_errors"]), 0, f"Timeline errors: {findings['timeline_errors']}")
        self.assertEqual(len(findings["manuscript_name_drift"]), 0, f"Manuscript drift: {findings['manuscript_name_drift']}")

    def test_series_continuity_extracts_demo_characters(self):
        entities = extract_book_entities(DEMO_MS_DIR / "Book-01")
        self.assertIn("Aeloria-Vael", entities["characters"])
        self.assertIn("Lord-Kaelen", entities["characters"])
        self.assertIn("Archmage-Theron", entities["characters"])


if __name__ == "__main__":
    unittest.main()
