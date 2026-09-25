#!/usr/bin/env python3
"""
Unit test for gitignore templates and runtime cache isolation (tests/test_gitignore.py).
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INIT_WORLD = REPO_ROOT / "scripts" / "init_world.sh"
INIT_MANUSCRIPT = REPO_ROOT / "scripts" / "init_manuscript.sh"
ROOT_GITIGNORE = REPO_ROOT / ".gitignore"


class TestGitignoreTemplates(unittest.TestCase):
    """Ensures runtime cache and temporary files are excluded in templates and repository root."""

    def test_root_gitignore_contains_cache_entries(self):
        self.assertTrue(ROOT_GITIGNORE.is_file())
        text = ROOT_GITIGNORE.read_text(encoding="utf-8")
        self.assertIn(".arcanum_cache.json", text)
        self.assertIn(".sync_state.json", text)

    def test_init_world_gitignore_contains_cache_entries(self):
        self.assertTrue(INIT_WORLD.is_file())
        text = INIT_WORLD.read_text(encoding="utf-8")
        self.assertIn(".arcanum_cache.json", text)
        self.assertIn(".sync_state.json", text)

    def test_init_manuscript_gitignore_contains_cache_entries(self):
        self.assertTrue(INIT_MANUSCRIPT.is_file())
        text = INIT_MANUSCRIPT.read_text(encoding="utf-8")
        self.assertIn(".arcanum_cache.json", text)
        self.assertIn(".sync_state.json", text)


if __name__ == "__main__":
    unittest.main()
