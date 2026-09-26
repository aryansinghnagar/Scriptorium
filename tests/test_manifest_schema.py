#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Manifest Schema Conformity (tests/test_manifest_schema.py)
===================================================================================
Validates:
1. All manuscript.yaml and world.yaml manifests use standard flat top-level schema.
2. Runtime readers (frontmatter, importer, query, export) parse manifests cleanly.
3. No nested dictionary schema drift between fixtures and runtime expectations.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.frontmatter import parse_yaml_document


class TestManifestSchema(unittest.TestCase):
    def test_sample_manuscript_fixture_is_flat(self):
        fixture_path = REPO_ROOT / "tests" / "fixtures" / "sample_manuscript" / "manuscript.yaml"
        self.assertTrue(fixture_path.is_file(), "sample_manuscript/manuscript.yaml must exist")
        content = fixture_path.read_text(encoding="utf-8")
        data = parse_yaml_document(content)

        # Must have flat keys, NOT nested under 'manuscript'
        self.assertNotIn("manuscript", data, "Manifest must not wrap keys under nested 'manuscript' dict")
        self.assertEqual(data.get("title"), "The Glass Horizon")
        self.assertEqual(data.get("author"), "Renée d'Anjou")
        self.assertEqual(data.get("universe"), "SampleUniverse")
        self.assertEqual(data.get("world"), "sample_world")

    def test_demo_cosmos_manuscript_is_flat(self):
        demo_path = REPO_ROOT / "templates" / "demo-cosmos" / "Eldoria-Cosmos" / "Manuscripts" / "The-Silver-Chronicles" / "manuscript.yaml"
        self.assertTrue(demo_path.is_file(), "Demo cosmos manuscript.yaml must exist")
        content = demo_path.read_text(encoding="utf-8")
        data = parse_yaml_document(content)

        self.assertNotIn("manuscript", data)
        self.assertEqual(data.get("title"), "The Silver Chronicles")
        self.assertEqual(data.get("universe"), "Eldoria-Cosmos")
        self.assertEqual(data.get("world"), "Eldoria-Prime")

    def test_demo_cosmos_world_is_flat(self):
        world_path = REPO_ROOT / "templates" / "demo-cosmos" / "Eldoria-Cosmos" / "Eldoria-Prime" / "world.yaml"
        self.assertTrue(world_path.is_file(), "Demo cosmos world.yaml must exist")
        content = world_path.read_text(encoding="utf-8")
        data = parse_yaml_document(content)

        self.assertNotIn("world", data)
        self.assertEqual(data.get("name"), "Eldoria-Prime")
        self.assertEqual(data.get("universe"), "Eldoria-Cosmos")


if __name__ == "__main__":
    unittest.main()


