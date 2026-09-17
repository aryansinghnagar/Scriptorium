#!/usr/bin/env python3
"""
Unit tests for Scriptorium Cache Engine (scripts/lib/cache.py).
Covers cache persistence, 0o600 permission hardening, frontmatter parsing,
novelWriter tag extraction, wikilink parsing, and mtime invalidation logic.
"""

import os
import sys
import stat
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cache import (  # noqa: E402
    CACHE_VERSION,
    CACHE_FILENAME,
    get_cache_path,
    load_cache,
    save_cache,
    parse_frontmatter,
    parse_markdown_file,
    scan_project,
    compute_wordcounts,
)


class TestCacheEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_cache_path(self):
        cache_path = get_cache_path(str(self.project_dir))
        self.assertEqual(cache_path, self.project_dir / CACHE_FILENAME)

    def test_load_cache_missing(self):
        cache = load_cache(str(self.project_dir))
        self.assertEqual(cache.get("version"), CACHE_VERSION)
        self.assertEqual(cache.get("files"), {})

    def test_load_cache_invalid_json(self):
        cache_file = self.project_dir / CACHE_FILENAME
        cache_file.write_text("invalid json content {", encoding="utf-8")
        cache = load_cache(str(self.project_dir))
        self.assertEqual(cache.get("version"), CACHE_VERSION)
        self.assertEqual(cache.get("files"), {})

    def test_save_and_load_cache(self):
        data = {
            "version": CACHE_VERSION,
            "files": {
                "chapter1.md": {"word_count": 120, "mtime": 12345.0, "size": 500}
            }
        }
        saved = save_cache(str(self.project_dir), data)
        self.assertTrue(saved)

        loaded = load_cache(str(self.project_dir))
        self.assertEqual(loaded.get("version"), CACHE_VERSION)
        self.assertIn("chapter1.md", loaded.get("files", {}))
        self.assertEqual(loaded["files"]["chapter1.md"]["word_count"], 120)

    def test_cache_file_permissions(self):
        if os.name == "posix":
            data = {"version": CACHE_VERSION, "files": {}}
            save_cache(str(self.project_dir), data)
            cache_file = self.project_dir / CACHE_FILENAME
            self.assertTrue(cache_file.is_file())
            file_mode = stat.S_IMODE(cache_file.stat().st_mode)
            self.assertEqual(file_mode & 0o777, 0o600)

    def test_parse_frontmatter(self):
        md_text = """---
name: "Renée d'Anjou"
type: character
role: protagonist
aliases: ["The Star Knight", "Renée"]
# Comment line
tags: [hero, knight]
---
# Chapter Content
"""
        fm = parse_frontmatter(md_text)
        self.assertEqual(fm.get("name"), "Renée d'Anjou")
        self.assertEqual(fm.get("type"), "character")
        self.assertEqual(fm.get("role"), "protagonist")
        self.assertEqual(fm.get("aliases"), ["The Star Knight", "Renée"])
        self.assertEqual(fm.get("tags"), ["hero", "knight"])

    def test_parse_frontmatter_empty(self):
        self.assertEqual(parse_frontmatter("No frontmatter here"), {})
        self.assertEqual(parse_frontmatter("---\n---"), {})

    def test_parse_markdown_file(self):
        test_file = self.project_dir / "scene.md"
        test_file.write_text("""---
title: "The Meeting"
status: Draft
---
# Act I Scene 1

@pov: Renée
@chars: Renée, Julian
@location: Sanctuaire des Étoiles
@thread: Holy Grail Arc
@time: 1420-05-12

Renée gazed across the [[Sanctuaire des Étoiles|Sanctuary]] and met [[Julian#Courtyard|Julian]].
```python
# Code block that should not count as prose words
ignored = 1234
```
A grand adventure awaits them in the citadel.
""", encoding="utf-8")

        res = parse_markdown_file(test_file)
        self.assertGreater(res["word_count"], 0)
        self.assertEqual(res["tags"].get("pov"), ["Renée"])
        self.assertEqual(res["tags"].get("characters"), ["Renée, Julian"])
        self.assertEqual(res["tags"].get("location"), ["Sanctuaire des Étoiles"])
        self.assertEqual(res["tags"].get("thread"), ["Holy Grail Arc"])
        self.assertEqual(res["tags"].get("time"), ["1420-05-12"])
        self.assertIn("Sanctuaire des Étoiles", res["wikilinks"])
        self.assertIn("Julian", res["wikilinks"])
        self.assertEqual(res["frontmatter"].get("title"), "The Meeting")

    def test_scan_project_and_wordcounts(self):
        sub_dir = self.project_dir / "Act_I"
        sub_dir.mkdir(parents=True)
        (sub_dir / "ch1.md").write_text("# Chapter 1\nFifty words in a scene " * 10, encoding="utf-8")
        (sub_dir / "ch2.md").write_text("# Chapter 2\nAnother twenty words in a scene " * 4, encoding="utf-8")

        cache = scan_project(str(self.project_dir))
        self.assertEqual(len(cache.get("files", {})), 2)

        wc_report = compute_wordcounts(str(self.project_dir))
        self.assertEqual(wc_report["total_files"], 2)
        self.assertGreater(wc_report["total_words"], 50)
        self.assertIn("Act_I", wc_report["by_folder"])

        # Test mtime cache invalidation on file modification
        ch1 = sub_dir / "ch1.md"
        ch1.write_text("# Short chapter", encoding="utf-8")
        cache2 = scan_project(str(self.project_dir))
        self.assertEqual(cache2["files"]["Act_I/ch1.md"]["word_count"], 2)

        # Test deleted file pruning from cache
        ch2 = sub_dir / "ch2.md"
        ch2.unlink()
        cache3 = scan_project(str(self.project_dir))
        self.assertNotIn("Act_I/ch2.md", cache3["files"])
        self.assertEqual(len(cache3["files"]), 1)

    def test_canonical_count_words_ana01(self):
        # ANA-01: frontmatter, codeblocks, @tags and % comments are not prose.
        from lib.cache import count_words
        text = """---
title: Test
---
# Heading

@pov: Kael
% a typst comment
```python
ignored code words here
```
Real prose words here.
"""
        self.assertEqual(count_words(text), 5)  # Heading + Real + prose + words + here

    def test_scan_excludes_generated_dirs_prf02(self):
        # PRF-02: Exports/Backups must not pollute the index or word counts.
        exp = self.project_dir / "Exports"
        exp.mkdir(parents=True)
        (exp / "compiled.md").write_text("Exported words " * 100, encoding="utf-8")
        (self.project_dir / "real.md").write_text("Real words here", encoding="utf-8")
        cache = scan_project(str(self.project_dir))
        self.assertIn("real.md", cache.get("files", {}))
        self.assertNotIn("Exports/compiled.md", cache.get("files", {}))
        self.assertTrue(cache.get("healthy", False))


if __name__ == "__main__":
    unittest.main()
