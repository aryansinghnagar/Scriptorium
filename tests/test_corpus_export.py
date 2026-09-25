#!/usr/bin/env python3
"""
Test Suite: Universal Structured Corpus & RAG Dataset Exporter
(tests/test_corpus_export.py)
================================================================================
Validates universe & manuscript scanning, semantic chunking, entity graph
extraction, and multi-format exports (JSONL, SQLite with FTS5, Markdown Digest).
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib.corpus_export import (
    CorpusScanner,
    chunk_document,
    export_jsonl,
    export_markdown_summary,
    export_sqlite,
    extract_wikilinks,
    main as corpus_main,
    sanitize_id,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCorpusExport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # 1. Create World Lore Vault
        self.world_dir = self.root / "Eldoria"
        self.chars_dir = self.world_dir / "Characters"
        self.locs_dir = self.world_dir / "Locations"
        self.factions_dir = self.world_dir / "Factions"

        self.chars_dir.mkdir(parents=True)
        self.locs_dir.mkdir(parents=True)
        self.factions_dir.mkdir(parents=True)

        (self.chars_dir / "Aeloria.md").write_text(
            """---
name: "Aeloria Vael"
aliases:
  - "Silver Blade"
  - "Aeloria"
type: "character"
faction: "[[Silver-Dawn]]"
current_location: "[[High-Sanctuary]]"
---

# Aeloria Vael

Aeloria is a champion swordsman of the [[Silver-Dawn]] guarding [[High-Sanctuary]].

## Background
Trained in arcane arts from youth.
""",
            encoding="utf-8",
        )

        (self.locs_dir / "High-Sanctuary.md").write_text(
            """---
name: "High Sanctuary"
type: "location"
---

# High Sanctuary

The floating citadel positioned high above the clouds.
""",
            encoding="utf-8",
        )

        (self.factions_dir / "Silver-Dawn.md").write_text(
            """---
name: "Silver Dawn"
type: "faction"
---

# Silver Dawn

An ancient knightly order sworn to uphold peace in [[High-Sanctuary]].
""",
            encoding="utf-8",
        )

        # 2. Create Manuscript
        self.ms_dir = self.root / "Manuscripts" / "Book-01" / "Draft-01"
        self.ms_dir.mkdir(parents=True)

        (self.ms_dir / "01_Chapter.md").write_text(
            """---
title: "The Awakening"
chapter: 1
pov: "[[Aeloria]]"
---

# Chapter 1: The Awakening

@pov: Aeloria
@location: High-Sanctuary

Aeloria stepped out upon the grand balcony of [[High-Sanctuary]].

She looked out over the misty clouds below, thinking about the oath she swore to the [[Silver-Dawn]].
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sanitize_id(self):
        self.assertEqual(sanitize_id("Characters/Aeloria Vael.md"), "characters/aeloria_vael.md")
        self.assertEqual(sanitize_id("Book 01\\Draft 02"), "book_01/draft_02")

    def test_extract_wikilinks(self):
        text = "Hello [[World]] and [[Target|Label]] with [[Another]]"
        links = extract_wikilinks(text)
        self.assertEqual(links, ["World", "Target", "Another"])

    def test_chunk_document(self):
        body = """# Section One
This is the first paragraph of section one.

This is the second paragraph of section one with [[Aeloria]].

## Section Two
This is paragraph in section two with [[High-Sanctuary]].
"""
        chunks = chunk_document("doc1", body, target_chunk_words=10)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(any("Aeloria" in c.entities for c in chunks))
        self.assertTrue(any(c.heading == "Section Two" for c in chunks))

    def test_scanner_full_discovery(self):
        scanner = CorpusScanner(self.root)
        scanner.scan()

        self.assertEqual(len(scanner.documents), 4)
        doc_categories = {d.category for d in scanner.documents}
        self.assertIn("Characters", doc_categories)
        self.assertIn("Locations", doc_categories)
        self.assertIn("Factions", doc_categories)
        self.assertIn("Book-01", doc_categories)

        self.assertGreater(scanner.total_words(), 0)
        self.assertGreater(scanner.total_chunks(), 0)

        # Entity graph
        self.assertIn("Aeloria Vael", scanner.entities)
        self.assertIn("Silver Dawn", scanner.entities)
        self.assertIn("High Sanctuary", scanner.entities)

        # Mentions count
        aeloria_ent = scanner.entities["Aeloria Vael"]
        self.assertIn("Silver Blade", aeloria_ent.aliases)

    def test_export_jsonl(self):
        scanner = CorpusScanner(self.root)
        scanner.scan()

        out_dir = self.root / "dist" / "corpus"
        paths = export_jsonl(scanner, out_dir)

        self.assertTrue(paths["documents"].exists())
        self.assertTrue(paths["chunks"].exists())
        self.assertTrue(paths["entities"].exists())

        # Verify JSON lines format
        doc_lines = paths["documents"].read_text(encoding="utf-8").strip().split("\n")
        self.assertEqual(len(doc_lines), 4)
        doc0 = json.loads(doc_lines[0])
        self.assertIn("id", doc0)
        self.assertIn("title", doc0)
        self.assertIn("word_count", doc0)
        self.assertIn("frontmatter", doc0)

        chunk_lines = paths["chunks"].read_text(encoding="utf-8").strip().split("\n")
        self.assertGreaterEqual(len(chunk_lines), 4)
        chunk0 = json.loads(chunk_lines[0])
        self.assertIn("heading", chunk0)
        self.assertIn("text", chunk0)
        self.assertIn("token_count_est", chunk0)

    def test_export_sqlite(self):
        scanner = CorpusScanner(self.root)
        scanner.scan()

        db_file = self.root / "dist" / "corpus.db"
        export_sqlite(scanner, db_file)

        self.assertTrue(db_file.exists())

        conn = sqlite3.connect(str(db_file))
        cur = conn.cursor()

        # Meta table
        cur.execute("SELECT total_docs, total_words, version FROM corpus_meta")
        row = cur.fetchone()
        self.assertEqual(row[0], 4)
        self.assertEqual(row[2], "1.9.0")

        # Documents table
        cur.execute("SELECT COUNT(*) FROM documents")
        self.assertEqual(cur.fetchone()[0], 4)

        # FTS5 search
        cur.execute("SELECT id, title FROM documents_fts WHERE documents_fts MATCH 'swordsman'")
        fts_res = cur.fetchall()
        self.assertGreaterEqual(len(fts_res), 1)
        self.assertIn("aeloria", fts_res[0][0].lower())

        conn.close()

    def test_export_markdown_summary(self):
        scanner = CorpusScanner(self.root)
        scanner.scan()

        summary_file = self.root / "dist" / "_corpus_summary.md"
        export_markdown_summary(scanner, summary_file)

        self.assertTrue(summary_file.exists())
        content = summary_file.read_text(encoding="utf-8")
        self.assertIn("Corpus Summary Digest", content)
        self.assertIn("Corpus Metrics Overview", content)
        self.assertIn("Document Catalog", content)
        self.assertIn("Aeloria Vael", content)

    def test_empty_corpus_scan_and_export(self):
        """Verifies scanning and exporting an empty directory."""
        empty_dir = self.root / "EmptyCorpus"
        empty_dir.mkdir(parents=True, exist_ok=True)
        scanner = CorpusScanner(empty_dir)
        scanner.scan()

        self.assertEqual(len(scanner.documents), 0)
        self.assertEqual(scanner.total_words(), 0)
        self.assertEqual(scanner.total_chunks(), 0)

        out_dir = self.root / "empty_dist"
        paths = export_jsonl(scanner, out_dir)
        self.assertTrue(paths["documents"].exists())

    def test_chunking_with_custom_word_thresholds(self):
        """Verifies chunking with varied target chunk sizes."""
        long_body = "Paragraph one with some interesting words. " * 30 + "\n\n# Header Two\n\n" + "Paragraph two with more details. " * 30
        chunks_small = chunk_document("doc_small", long_body, target_chunk_words=50)
        chunks_large = chunk_document("doc_large", long_body, target_chunk_words=500)

        self.assertGreater(len(chunks_small), len(chunks_large))
        for c in chunks_small:
            self.assertGreater(c.token_count_est, 0)
            self.assertIsNotNone(c.heading)

    def test_sqlite_fts5_multi_term_query(self):
        """Verifies SQLite FTS5 multi-term matching on chunks and documents."""
        scanner = CorpusScanner(self.root)
        scanner.scan()

        db_file = self.root / "dist" / "search_test.db"
        export_sqlite(scanner, db_file)

        conn = sqlite3.connect(str(db_file))
        cur = conn.cursor()

        # Multi-term FTS query
        cur.execute("SELECT heading, text FROM chunks_fts WHERE chunks_fts MATCH 'Aeloria High'")
        rows = cur.fetchall()
        self.assertGreaterEqual(len(rows), 1)

        # Chunks table count
        cur.execute("SELECT COUNT(*) FROM chunks")
        count = cur.fetchone()[0]
        self.assertGreaterEqual(count, 4)
        conn.close()

    def test_entity_graph_cross_references(self):
        """Verifies entity cross-references and aliases in CorpusEntity."""
        scanner = CorpusScanner(self.root)
        scanner.scan()

        self.assertIn("Aeloria Vael", scanner.entities)
        aeloria = scanner.entities["Aeloria Vael"]
        self.assertIn("Silver Blade", aeloria.aliases)
        self.assertGreaterEqual(aeloria.mention_count, 1)

    def test_cli_corpus_export_execution(self):
        """Verifies CLI execution of corpus export tool with dry-run and json flags."""
        with (
            patch("sys.argv", ["corpus_export.py", str(self.root), "--json"]),
            patch("builtins.print") as mock_print,
        ):
            corpus_main()
            mock_print.assert_called()
            out_text = mock_print.call_args[0][0]
            data = json.loads(out_text)
            self.assertIn("total_documents", data)
            self.assertEqual(data["total_documents"], 4)
            self.assertIn("total_words", data)


if __name__ == "__main__":
    unittest.main()
