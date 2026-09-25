#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Local Semantic Retrieval Engine
(tests/test_local_rag.py)
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.lib.local_rag import (
    IndexedChunk,
    LocalLoreRetrievalEngine,
    format_markdown_report,
    generate_html_retrieval_viewer,
    main as rag_main,
    synthesize_llm_context,
    tokenize,
)


class TestLocalSemanticRetrieval(unittest.TestCase):
    """Validates vector space retrieval, hybrid scoring, and context synthesis."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create sample markdown vault for testing
        self.vault_dir = self.root / "World_Vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        # Document 1: Character (Valerius)
        char_file = self.vault_dir / "Valerius.md"
        char_file.write_text(
            "---\n"
            "name: Archon Valerius\n"
            "type: Character\n"
            "category: Characters\n"
            "aliases: [The Dawnstrider]\n"
            "---\n"
            "# Archon Valerius\n\n"
            "Valerius is the High Archon of the Sunfire Citadel. He wields the legendary blade Dawnstrider.\n"
            "During the Battle of the Crimson Rift, Valerius channeled radiant solar energy to seal the void.\n",
            encoding="utf-8",
        )

        # Document 2: Location (Sunfire Citadel)
        loc_file = self.vault_dir / "Sunfire_Citadel.md"
        loc_file.write_text(
            "---\n"
            "name: Sunfire Citadel\n"
            "type: Location\n"
            "category: Locations\n"
            "---\n"
            "# Sunfire Citadel\n\n"
            "The Sunfire Citadel is an ancient fortress constructed atop the Solar Spire.\n"
            "It houses the High Archon and the Council of Radiance. The citadel was besieged during the Void Incursion.\n",
            encoding="utf-8",
        )

        # Document 3: Magic System (Aether Resonance)
        magic_file = self.vault_dir / "Aether_Resonance.md"
        magic_file.write_text(
            "---\n"
            "name: Aether Resonance\n"
            "type: MagicSystem\n"
            "category: MagicSystems\n"
            "---\n"
            "# Aether Resonance\n\n"
            "Aether resonance requires harmonic alignment between the caster's soulstone and the atmospheric leylines.\n"
            "Overchanneling causes crystal calcification of the blood vessels.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_tokenization_and_stopwords(self) -> None:
        """Verifies text tokenization, lowercase conversion, and stopword stripping."""
        text = "The High Archon wields Dawnstrider in the Sunfire Citadel!"
        tokens = tokenize(text, remove_stopwords=True)
        self.assertIn("high", tokens)
        self.assertIn("archon", tokens)
        self.assertIn("wields", tokens)
        self.assertIn("dawnstrider", tokens)
        self.assertIn("sunfire", tokens)
        self.assertIn("citadel", tokens)
        # Stopwords removed
        self.assertNotIn("the", tokens)
        self.assertNotIn("in", tokens)

    def test_in_memory_directory_indexing_and_query(self) -> None:
        """Verifies directory ingestion and cosine similarity vector retrieval."""
        engine = LocalLoreRetrievalEngine()
        count = engine.load_from_directory(self.vault_dir)
        self.assertGreaterEqual(count, 3)
        self.assertEqual(engine.total_chunks, count)

        # Query for Dawnstrider weapon
        results = engine.query("Who wields the legendary blade Dawnstrider?", top_k=2)
        self.assertGreater(len(results), 0)
        top_res = results[0]
        self.assertIn("Valerius", top_res.chunk.doc_title)
        self.assertGreater(top_res.score, 0.20)
        self.assertIn("cosine_similarity", top_res.score_breakdown)

    def test_category_and_type_filtering(self) -> None:
        """Verifies filtering results by lore category."""
        engine = LocalLoreRetrievalEngine()
        engine.load_from_directory(self.vault_dir)

        # Query with category filter
        results = engine.query("Aether soulstone resonance", category="MagicSystems")
        self.assertEqual(len(results), 1)
        self.assertIn("Aether", results[0].chunk.doc_title)

    def test_sqlite_corpus_ingestion_and_fts5_fusion(self) -> None:
        """Verifies loading from SQLite corpus.db and FTS5 ranking fusion."""
        db_path = self.root / "test_corpus.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.executescript("""
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            corpus_type TEXT,
            category TEXT,
            title TEXT,
            path TEXT,
            word_count INTEGER,
            token_count_est INTEGER,
            frontmatter_json TEXT,
            body TEXT
        );
        CREATE TABLE chunks (
            id TEXT PRIMARY KEY,
            doc_id TEXT,
            chunk_index INTEGER,
            heading TEXT,
            text TEXT,
            word_count INTEGER,
            token_count_est INTEGER,
            entities_json TEXT
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            id UNINDEXED,
            heading,
            text
        );
        """)

        # Insert test document and chunk
        cursor.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("doc_kallor", "lore", "Characters", "Lord Kallor", "Characters/Kallor.md", 150, 200, "{}", "Lord Kallor ruled the High Kingdom.")
        )
        cursor.execute(
            "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("chunk_kallor_1", "doc_kallor", 0, "The Tyrant's Curse", "Lord Kallor laid waste to seven cities with blood sorcery.", 12, 16, json.dumps(["Lord Kallor", "Blood Sorcery"]))
        )
        cursor.execute(
            "INSERT INTO chunks_fts VALUES (?, ?, ?)",
            ("chunk_kallor_1", "The Tyrant's Curse", "Lord Kallor laid waste to seven cities with blood sorcery.")
        )
        conn.commit()
        conn.close()

        engine = LocalLoreRetrievalEngine()
        loaded = engine.load_from_sqlite(db_path)
        self.assertEqual(loaded, 1)

        results = engine.query("seven cities blood sorcery", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk.id, "chunk_kallor_1")
        self.assertIn("Lord Kallor", results[0].chunk.entities)

    def test_jsonl_dataset_ingestion(self) -> None:
        """Verifies indexing chunks from JSON Lines files."""
        chunks_file = self.root / "chunks.jsonl"
        docs_file = self.root / "documents.jsonl"

        doc_data = {
            "id": "doc_elysia",
            "title": "Elysia the Chronomancer",
            "corpus_type": "lore",
            "category": "Characters",
            "path": "Characters/Elysia.md",
        }
        docs_file.write_text(json.dumps(doc_data) + "\n", encoding="utf-8")

        chunk_data = {
            "id": "chunk_elysia_1",
            "doc_id": "doc_elysia",
            "heading": "Temporal Anchor",
            "text": "Elysia weaves temporal dilation fields to decelerate enemy projectiles.",
            "word_count": 9,
            "token_count_est": 12,
            "entities": ["Elysia", "Temporal Dilation"],
        }
        chunks_file.write_text(json.dumps(chunk_data) + "\n", encoding="utf-8")

        engine = LocalLoreRetrievalEngine()
        loaded = engine.load_from_jsonl(chunks_file, docs_jsonl=docs_file)
        self.assertEqual(loaded, 1)

        results = engine.query("temporal dilation projectiles")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk.doc_title, "Elysia the Chronomancer")

    def test_llm_prompt_context_synthesis(self) -> None:
        """Verifies synthesis of injection-safe LLM prompt context block."""
        chunk = IndexedChunk(
            id="c_1",
            doc_id="d_valerius",
            doc_title="Archon Valerius",
            corpus_type="lore",
            category="Characters",
            doc_path="Characters/Valerius.md",
            heading="Solar Blade",
            text="Valerius forged Dawnstrider in the core of the star.",
            word_count=10,
            token_count_est=13,
            entities=["Valerius", "Dawnstrider"],
        )
        res = LocalLoreRetrievalEngine()
        res.chunks = [chunk]
        res._build_vector_index()
        results = res.query("Dawnstrider star forge")

        prompt = synthesize_llm_context("Where was Dawnstrider forged?", results)
        self.assertIn("<system_instructions>", prompt)
        self.assertIn("<canonical_lore_context>", prompt)
        self.assertIn("<user_query>", prompt)
        self.assertIn("Archon Valerius", prompt)
        self.assertIn("Dawnstrider", prompt)

    def test_markdown_and_html_generation(self) -> None:
        """Verifies generation of readable markdown and offline HTML dashboard."""
        chunk = IndexedChunk(
            id="c_1",
            doc_id="d_valerius",
            doc_title="Archon Valerius",
            corpus_type="lore",
            category="Characters",
            doc_path="Characters/Valerius.md",
            heading="Solar Blade",
            text="Valerius forged Dawnstrider in the core of the star.",
            word_count=10,
            token_count_est=13,
            entities=["Valerius", "Dawnstrider"],
        )
        res = LocalLoreRetrievalEngine()
        res.chunks = [chunk]
        res._build_vector_index()
        results = res.query("Dawnstrider")

        # Markdown
        md = format_markdown_report("Dawnstrider", results)
        self.assertIn("# Ars Arcanum Lore Retrieval Report", md)
        self.assertIn("Archon Valerius", md)

        # HTML
        html_view = generate_html_retrieval_viewer("Dawnstrider", results)
        self.assertIn("<!DOCTYPE html>", html_view)
        self.assertIn("Content-Security-Policy", html_view)
        self.assertIn("default-src 'none'", html_view)
        self.assertIn("Archon Valerius", html_view)

    def test_cli_execution(self) -> None:
        """Verifies CLI execution with various output formats."""
        out_json = self.root / "result.json"
        code = rag_main([
            "Valerius solar blade",
            "-t", str(self.vault_dir),
            "-f", "json",
            "-o", str(out_json),
        ])
        self.assertEqual(code, 0)
        self.assertTrue(out_json.is_file())

        with out_json.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("query", data)
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)

    def test_empty_vault_and_no_match_query(self) -> None:
        """Verifies handling of empty directory indexing and queries with 0 matches."""
        empty_dir = self.root / "Empty_Vault"
        empty_dir.mkdir(parents=True, exist_ok=True)

        engine = LocalLoreRetrievalEngine()
        count = engine.load_from_directory(empty_dir)
        self.assertEqual(count, 0)
        self.assertEqual(engine.total_chunks, 0)

        results = engine.query("Nonexistent query about dragons")
        self.assertEqual(len(results), 0)

    def test_min_score_threshold_and_top_k(self) -> None:
        """Verifies top_k limiting and score bounds."""
        engine = LocalLoreRetrievalEngine()
        engine.load_from_directory(self.vault_dir)

        # Top k = 1 should strictly return at most 1 result
        top_1 = engine.query("Valerius citadel", top_k=1)
        self.assertEqual(len(top_1), 1)

        # Top k = 10 on 3-document vault returns at most 3
        top_all = engine.query("Valerius citadel aether", top_k=10)
        self.assertLessEqual(len(top_all), 3)

    def test_tokenization_special_cases(self) -> None:
        """Verifies edge cases for tokenizer: empty strings, numbers, symbols."""
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   "), [])
        self.assertEqual(tokenize("123 4567 89"), [])
        self.assertEqual(tokenize("!@#$%^&*()"), [])
        toks = tokenize("knight-commander's sword", remove_stopwords=False)
        self.assertTrue(any("knight" in t for t in toks))

    def test_cli_markdown_and_html_output(self) -> None:
        """Verifies CLI execution producing markdown and HTML outputs."""
        out_md = self.root / "report.md"
        out_html = self.root / "report.html"

        code_md = rag_main([
            "Aether leylines",
            "-t", str(self.vault_dir),
            "-f", "markdown",
            "-o", str(out_md),
        ])
        self.assertEqual(code_md, 0)
        self.assertTrue(out_md.is_file())
        self.assertIn("Aether Resonance", out_md.read_text(encoding="utf-8"))

        code_html = rag_main([
            "Aether leylines",
            "-t", str(self.vault_dir),
            "-f", "html",
            "-o", str(out_html),
        ])
        self.assertEqual(code_html, 0)
        self.assertTrue(out_html.is_file())
        self.assertIn("Content-Security-Policy", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
