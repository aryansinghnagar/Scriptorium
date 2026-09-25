#!/usr/bin/env python3
"""
Unit tests for the Unified Frontmatter Engine (tests/test_frontmatter.py).
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from frontmatter import parse_yaml_frontmatter, parse_frontmatter, extract_frontmatter_and_body


class TestFrontmatterEngine(unittest.TestCase):

    def test_parse_empty_or_no_frontmatter(self):
        self.assertEqual(parse_yaml_frontmatter(""), {})
        self.assertEqual(parse_yaml_frontmatter("# Heading\nSome text"), {})

    def test_parse_scalars_and_types(self):
        doc = """---
name: "Aeloria Vael"
age: 124
height_meters: 1.82
is_active: true
is_deceased: false
title: Lord Protector
alias: 'The Silver Blade'
empty_key:
---
# Chapter Body
"""
        fm = parse_yaml_frontmatter(doc)
        self.assertEqual(fm["name"], "Aeloria Vael")
        self.assertEqual(fm["age"], 124)
        self.assertAlmostEqual(fm["height_meters"], 1.82)
        self.assertIs(fm["is_active"], True)
        self.assertIs(fm["is_deceased"], False)
        self.assertEqual(fm["title"], "Lord Protector")
        self.assertEqual(fm["alias"], "The Silver Blade")
        self.assertEqual(fm["empty_key"], "")

    def test_parse_inline_and_block_lists(self):
        doc = """---
tags: [fantasy, epic, magic]
aliases:
  - "The White Tower"
  - 'Silver Spire'
  - High Sanctuary
empty_list: []
---
Body text here.
"""
        fm = parse_yaml_frontmatter(doc)
        self.assertEqual(fm["tags"], ["fantasy", "epic", "magic"])
        self.assertEqual(fm["aliases"], ["The White Tower", "Silver Spire", "High Sanctuary"])
        self.assertEqual(fm["empty_list"], [])

    def test_extract_frontmatter_and_body(self):
        doc = """---
title: The Sundered Crown
chapter: 1
---

In the frozen dawn, the legions assembled.
"""
        fm, body = extract_frontmatter_and_body(doc)
        self.assertEqual(fm["title"], "The Sundered Crown")
        self.assertEqual(fm["chapter"], 1)
        self.assertIn("In the frozen dawn", body)
        self.assertNotIn("title: The Sundered Crown", body)

    def test_parse_frontmatter_strict(self):
        doc = """---
name: Eldoria
type: world
events:
  - Year 100
  - Year 200
---
Text
"""
        fm, ok = parse_frontmatter(doc)
        self.assertTrue(ok)
        self.assertEqual(fm["name"], "Eldoria")
        self.assertEqual(fm["type"], "world")
        self.assertEqual(fm["events"], ["Year 100", "Year 200"])


if __name__ == "__main__":
    unittest.main()
