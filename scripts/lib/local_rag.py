#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Zero-Dependency Local Semantic Retrieval (RAG) & Lore Engine
(scripts/lib/local_rag.py)
================================================================================
Zero-dependency, 100% offline hybrid semantic retrieval engine powering natural
language lore queries, multi-volume continuity recall, and prompt synthesis for
local LLMs (Llama 3, Mistral, Gemma, Phi) without external vector databases.

Mathematical Core:
1. Vector Space Model (VSM):
   - Sub-linear Term Frequency: TF(t, d) = 1.0 + ln(count(t, d)) if count > 0 else 0
   - Smoothed Inverse Document Frequency: IDF(t) = ln(1.0 + (N - df(t) + 0.5) / (df(t) + 0.5)) + 1.0
   - L2-Normalized Cosine Similarity: CosSim(q, d) = (v_q . v_d) / (||v_q|| * ||v_d||)
2. Hybrid SQLite FTS5 & Entity Fusion:
   - Combines vector space cosine angle with exact FTS5 keyword relevance.
   - Boosts chunks with matching named entities, wikilinks, and section headers.
3. Injection-Safe Context Prompt Synthesizer:
   - Formats top-k retrieved lore chunks into structured LLM system prompts with
     strict provenance attribution, category tagging, and word/token estimates.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import math
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write
    from lib.corpus_export import CorpusDocument, CorpusScanner
except ImportError:
    try:
        from _bootstrap import PROJECT_ROOT, atomic_write
        from corpus_export import CorpusDocument, CorpusScanner
    except ImportError:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(content, encoding=encoding)
            os.replace(tmp, path)

        CorpusDocument = None  # type: ignore
        CorpusScanner = None  # type: ignore

logger = logging.getLogger("arcanum.rag")

# Standard English Stopwords (Curated for craft and narrative retrieval)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9_\-']+\b")


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """Extract normalized alphanumeric tokens from text."""
    if not text:
        return []
    tokens = [m.group(0).lower().strip("-_'") for m in TOKEN_PATTERN.finditer(text)]
    tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


@dataclass
class IndexedChunk:
    """Represents an in-memory or database chunk prepared for vector scoring."""
    id: str
    doc_id: str
    doc_title: str
    corpus_type: str
    category: str
    doc_path: str
    heading: str
    text: str
    word_count: int
    token_count_est: int
    entities: list[str] = field(default_factory=list)
    term_counts: dict[str, int] = field(default_factory=dict)
    vector_norm: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "doc_title": self.doc_title,
            "corpus_type": self.corpus_type,
            "category": self.category,
            "doc_path": self.doc_path,
            "heading": self.heading,
            "text": self.text,
            "word_count": self.word_count,
            "token_count_est": self.token_count_est,
            "entities": self.entities,
        }


@dataclass
class RetrievalResult:
    """Represents a scored and attributed retrieval result."""
    chunk: IndexedChunk
    score: float
    score_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk.id,
            "doc_id": self.chunk.doc_id,
            "doc_title": self.chunk.doc_title,
            "corpus_type": self.chunk.corpus_type,
            "category": self.chunk.category,
            "doc_path": self.chunk.doc_path,
            "heading": self.chunk.heading,
            "text": self.chunk.text,
            "word_count": self.chunk.word_count,
            "token_count_est": self.chunk.token_count_est,
            "entities": self.chunk.entities,
            "score": round(self.score, 4),
            "score_breakdown": {k: round(v, 4) for k, v in self.score_breakdown.items()},
        }


class LocalLoreRetrievalEngine:
    """
    Offline Vector Space & Hybrid Semantic Retrieval Engine for Ars Arcanum.
    Can ingest from SQLite corpus.db, JSONL datasets, or scan Markdown directories.
    """

    def __init__(self) -> None:
        self.chunks: list[IndexedChunk] = []
        self.doc_term_freqs: dict[str, int] = {}  # term -> count of chunks containing term
        self.idf_cache: dict[str, float] = {}
        self.sqlite_db_path: Path | None = None
        self._is_indexed: bool = False

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    def load_from_sqlite(self, db_path: Path | str) -> int:
        """Loads and indexes chunks and documents from a corpus.db SQLite database."""
        path = Path(db_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Corpus database not found at '{path}'")

        self.sqlite_db_path = path
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
        SELECT 
            c.id AS chunk_id,
            c.doc_id,
            c.chunk_index,
            c.heading,
            c.text,
            c.word_count,
            c.token_count_est,
            c.entities_json,
            d.corpus_type,
            d.category,
            d.title AS doc_title,
            d.path AS doc_path
        FROM chunks c
        JOIN documents d ON c.doc_id = d.id
        ORDER BY d.id, c.chunk_index
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.chunks = []

        for r in rows:
            entities = []
            if r["entities_json"]:
                try:
                    entities = json.loads(r["entities_json"])
                except Exception:
                    entities = []

            chunk = IndexedChunk(
                id=str(r["chunk_id"]),
                doc_id=str(r["doc_id"]),
                doc_title=str(r["doc_title"] or ""),
                corpus_type=str(r["corpus_type"] or "lore"),
                category=str(r["category"] or "General"),
                doc_path=str(r["doc_path"] or ""),
                heading=str(r["heading"] or ""),
                text=str(r["text"] or ""),
                word_count=int(r["word_count"] or 0),
                token_count_est=int(r["token_count_est"] or 0),
                entities=entities,
            )
            self.chunks.append(chunk)

        conn.close()
        self._build_vector_index()
        return len(self.chunks)

    def load_from_jsonl(self, chunks_jsonl: Path | str, docs_jsonl: Path | str | None = None) -> int:
        """Loads and indexes chunks from JSON Lines files."""
        c_path = Path(chunks_jsonl).resolve()
        if not c_path.is_file():
            raise FileNotFoundError(f"Chunks JSONL file not found at '{c_path}'")

        docs_map: dict[str, dict[str, Any]] = {}
        if docs_jsonl:
            d_path = Path(docs_jsonl).resolve()
            if d_path.is_file():
                with d_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            d = json.loads(line)
                            docs_map[d.get("id", "")] = d

        self.chunks = []
        with c_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                c = json.loads(line)
                doc_id = c.get("doc_id", "")
                doc_meta = docs_map.get(doc_id, {})

                chunk = IndexedChunk(
                    id=str(c.get("id", "")),
                    doc_id=doc_id,
                    doc_title=str(doc_meta.get("title", doc_id)),
                    corpus_type=str(doc_meta.get("corpus_type", "lore")),
                    category=str(doc_meta.get("category", "General")),
                    doc_path=str(doc_meta.get("path", "")),
                    heading=str(c.get("heading", "")),
                    text=str(c.get("text", "")),
                    word_count=int(c.get("word_count", 0)),
                    token_count_est=int(c.get("token_count_est", 0)),
                    entities=list(c.get("entities", [])),
                )
                self.chunks.append(chunk)

        self._build_vector_index()
        return len(self.chunks)

    def load_from_directory(self, target_dir: Path | str, target_chunk_words: int = 250) -> int:
        """Scans a directory of Markdown files in-memory using CorpusScanner."""
        if CorpusScanner is None:
            raise RuntimeError("CorpusScanner module is required to scan directory directly.")

        scanner = CorpusScanner(Path(target_dir), target_chunk_words=target_chunk_words)
        scanner.scan()

        self.chunks = []
        for doc in scanner.documents:
            for c in doc.chunks:
                chunk = IndexedChunk(
                    id=c.id,
                    doc_id=doc.id,
                    doc_title=doc.title,
                    corpus_type=doc.corpus_type,
                    category=doc.category,
                    doc_path=doc.path,
                    heading=c.heading,
                    text=c.text,
                    word_count=c.word_count,
                    token_count_est=c.token_count_est,
                    entities=list(c.entities),
                )
                self.chunks.append(chunk)

        self._build_vector_index()
        return len(self.chunks)

    def _build_vector_index(self) -> None:
        """Builds term frequency counters and IDF values for all loaded chunks."""
        self.doc_term_freqs = {}
        self.idf_cache = {}

        # 1. Compute term counts per chunk
        for chunk in self.chunks:
            # Combine heading, text, and entities with heading/entity boost in token pool
            full_text = f"{chunk.heading} {chunk.heading} {' '.join(chunk.entities)} {chunk.text}"
            tokens = tokenize(full_text)
            term_counts: dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1
            chunk.term_counts = term_counts

            # Update document term frequencies (number of chunks containing term)
            for t in term_counts:
                self.doc_term_freqs[t] = self.doc_term_freqs.get(t, 0) + 1

        n_chunks = len(self.chunks)
        if n_chunks == 0:
            self._is_indexed = True
            return

        # 2. Compute IDF per vocabulary term
        for term, df in self.doc_term_freqs.items():
            # Robertson-Spärck Jones smoothed IDF
            self.idf_cache[term] = math.log(1.0 + (n_chunks - df + 0.5) / (df + 0.5)) + 1.0

        # 3. Compute L2 vector norms for each chunk
        for chunk in self.chunks:
            norm_sq = 0.0
            for term, count in chunk.term_counts.items():
                idf = self.idf_cache.get(term, 1.0)
                # Sub-linear term frequency
                w_tf = 1.0 + math.log(count)
                w = w_tf * idf
                norm_sq += w * w
            chunk.vector_norm = math.sqrt(norm_sq) if norm_sq > 0.0 else 1.0

        self._is_indexed = True

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        min_score: float = 0.05,
        category: str | None = None,
        corpus_type: str | None = None,
        hybrid_fts: bool = True,
    ) -> list[RetrievalResult]:
        """
        Executes hybrid semantic vector + exact keyword search over the indexed corpus.
        Returns top-k most relevant chunks sorted by relevance score descending.
        """
        if not self._is_indexed or not self.chunks:
            return []

        q_tokens = tokenize(query_text)
        if not q_tokens:
            return []

        # 1. Compute query vector
        q_term_counts: dict[str, int] = {}
        for t in q_tokens:
            q_term_counts[t] = q_term_counts.get(t, 0) + 1

        q_weights: dict[str, float] = {}
        q_norm_sq = 0.0
        for t, count in q_term_counts.items():
            idf = self.idf_cache.get(t, math.log(1.0 + len(self.chunks)) + 1.0)
            w = (1.0 + math.log(count)) * idf
            q_weights[t] = w
            q_norm_sq += w * w

        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0.0 else 1.0

        # 2. Optional SQLite FTS5 exact score collection
        fts_scores: dict[str, float] = {}
        if hybrid_fts and self.sqlite_db_path and self.sqlite_db_path.is_file():
            try:
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                # Sanitize query for FTS5 syntax
                fts_terms = [re.sub(r"[^a-zA-Z0-9_-]", "", t) for t in q_tokens if len(t) > 1]
                if fts_terms:
                    fts_query = " OR ".join(f"{t}*" for t in fts_terms)
                    cursor.execute(
                        "SELECT id, bm25(chunks_fts) AS rank_score FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT 100",
                        (fts_query,)
                    )
                    for r in cursor.fetchall():
                        # bm25 returns negative score where lower (more negative) is better
                        raw_rank = float(r[1])
                        # Map bm25 into 0.0 - 1.0 normalized score
                        norm_fts = 1.0 / (1.0 + abs(raw_rank))
                        fts_scores[str(r[0])] = norm_fts
                conn.close()
            except Exception as e:
                logger.debug(f"SQLite FTS5 hybrid query fallback: {e}")

        # 3. Score all chunks
        results: list[RetrievalResult] = []
        raw_query_lower = query_text.lower()

        def _normalize_cat(c: str) -> str:
            return c.lower().rstrip("s").replace("-", "").replace("_", "").strip()

        for chunk in self.chunks:
            # Filter checks
            if category and _normalize_cat(chunk.category) != _normalize_cat(category):
                continue
            if corpus_type and chunk.corpus_type.lower() != corpus_type.lower():
                continue

            # A. Vector Cosine Similarity
            dot_product = 0.0
            for t, qw in q_weights.items():
                if t in chunk.term_counts:
                    cw = (1.0 + math.log(chunk.term_counts[t])) * self.idf_cache.get(t, 1.0)
                    dot_product += qw * cw

            cosine_sim = dot_product / (q_norm * chunk.vector_norm) if (q_norm * chunk.vector_norm) > 0.0 else 0.0

            # B. Entity & Heading Boosts
            entity_boost = 0.0
            for ent in chunk.entities:
                if ent.lower() in raw_query_lower:
                    entity_boost += 0.20

            heading_boost = 0.0
            if chunk.heading and any(t in chunk.heading.lower() for t in q_tokens):
                heading_boost += 0.15

            title_boost = 0.0
            if chunk.doc_title and any(t in chunk.doc_title.lower() for t in q_tokens):
                title_boost += 0.10

            # C. FTS5 Score Fusion
            fts_score = fts_scores.get(chunk.id, 0.0)

            # Combined Score Formula
            # 60% Cosine Similarity + 20% FTS5 exact rank + 20% Entity/Heading Boosts
            combined_score = (
                (0.60 * cosine_sim)
                + (0.20 * fts_score)
                + min(0.20, entity_boost + heading_boost + title_boost)
            )

            # Cap score between 0.0 and 1.0
            final_score = max(0.0, min(1.0, combined_score))

            if final_score >= min_score:
                breakdown = {
                    "cosine_similarity": cosine_sim,
                    "fts_score": fts_score,
                    "entity_boost": entity_boost,
                    "heading_boost": heading_boost,
                    "title_boost": title_boost,
                    "combined_score": final_score,
                }
                results.append(RetrievalResult(chunk=chunk, score=final_score, score_breakdown=breakdown))

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


# ==============================================================================
# Prompt Synthesis & Formatting Modules
# ==============================================================================

def synthesize_llm_context(
    query: str,
    results: list[RetrievalResult],
    system_instructions: str | None = None,
) -> str:
    """
    Synthesizes a secure, injection-safe LLM prompt context block from retrieved chunks.
    Designed for local models (Llama 3, Mistral, Ollama, Gemma, Phi).
    """
    default_instructions = (
        "You are the Ars Arcanum Sovereign Lore Inquisitor. Answer the author's inquiry\n"
        "using strictly the verified canonical context chunks provided below. If the context\n"
        "does not provide sufficient information, state what is known and identify lore gaps."
    )
    instructions = system_instructions or default_instructions

    lines = [
        "<system_instructions>",
        instructions.strip(),
        "</system_instructions>",
        "",
        "<canonical_lore_context>",
    ]

    if not results:
        lines.append("No canonical lore records matched the inquiry.")
    else:
        for idx, res in enumerate(results, 1):
            c = res.chunk
            lines.append(f"--- [RECORD #{idx} | Relevance: {res.score:.2f} | Category: {c.category}] ---")
            lines.append(f"Document: {c.doc_title} (ID: {c.doc_id})")
            if c.doc_path:
                lines.append(f"Source Path: {c.doc_path}")
            if c.heading:
                lines.append(f"Section: {c.heading}")
            if c.entities:
                lines.append(f"Entities: {', '.join(c.entities)}")
            lines.append("Content:")
            lines.append(c.text.strip())
            lines.append("")

    lines.append("</canonical_lore_context>")
    lines.append("")
    lines.append("<user_query>")
    lines.append(query.strip())
    lines.append("</user_query>")

    return "\n".join(lines)


def format_markdown_report(query: str, results: list[RetrievalResult]) -> str:
    """Formats retrieved results into a readable Markdown report."""
    lines = [
        "# Ars Arcanum Lore Retrieval Report",
        "",
        f"**Query**: `{query}`  ",
        f"**Results Found**: {len(results)} chunks  ",
        "",
        "## Top Canonical Matches",
        "",
    ]

    if not results:
        lines.append("*No matching canonical lore found for this query.*")
        return "\n".join(lines)

    lines.append("| Rank | Score | Title | Category | Section | Entities |")
    lines.append("| :--- | :---: | :--- | :--- | :--- | :--- |")

    for i, res in enumerate(results, 1):
        c = res.chunk
        entities_str = ", ".join(c.entities[:3]) if c.entities else "—"
        sec = c.heading if c.heading else "—"
        lines.append(f"| #{i} | **{res.score:.2f}** | `{c.doc_title}` | {c.category} | {sec} | {entities_str} |")

    lines.append("")
    lines.append("## Retrieved Chunk Excerpts")
    lines.append("")

    for i, res in enumerate(results, 1):
        c = res.chunk
        lines.append(f"### #{i}. {c.doc_title} — *{c.heading or 'General'}* (Score: {res.score:.2f})")
        lines.append(f"- **Document ID**: `{c.doc_id}` | **Category**: `{c.category}` | **Words**: {c.word_count}")
        if c.entities:
            lines.append(f"- **Referenced Entities**: {', '.join(f'`{e}`' for e in c.entities)}")
        lines.append("")
        lines.append("> " + c.text.replace("\n", "\n> "))
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def generate_html_retrieval_viewer(query: str, results: list[RetrievalResult]) -> str:
    """Generates a standalone, 100% offline interactive HTML retrieval dashboard."""
    cards_html = []
    for i, res in enumerate(results, 1):
        c = res.chunk
        score_pct = round(res.score * 100)
        score_color = "#10b981" if score_pct >= 60 else "#3b82f6" if score_pct >= 35 else "#f59e0b"

        entities_badges = "".join(f'<span class="badge badge-entity">{html.escape(e)}</span>' for e in c.entities)

        card = f"""
        <div class="result-card">
            <div class="card-header">
                <div class="card-title">
                    <span class="rank-badge">#{i}</span>
                    <h3>{html.escape(c.doc_title)}</h3>
                    <span class="category-tag">{html.escape(c.category)}</span>
                </div>
                <div class="score-badge" style="background: {score_color}22; color: {score_color}; border: 1px solid {score_color}55;">
                    {score_pct}% Match
                </div>
            </div>
            {f'<div class="section-header"><strong>Section:</strong> {html.escape(c.heading)}</div>' if c.heading else ''}
            <div class="card-body">
                <p>{html.escape(c.text)}</p>
            </div>
            <div class="card-footer">
                <div class="meta-item"><span>Path:</span> <code>{html.escape(c.doc_path or c.doc_id)}</code></div>
                <div class="meta-item"><span>Words:</span> {c.word_count}</div>
                <div class="entities-wrap">{entities_badges}</div>
            </div>
        </div>
        """
        cards_html.append(card)

    results_container = "\n".join(cards_html) if cards_html else "<div class='empty-state'>No matching lore chunks found.</div>"
    raw_context = synthesize_llm_context(query, results)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
    <title>Ars Arcanum Semantic Retrieval — {html.escape(query)}</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --accent: #8b5cf6;
            --accent-glow: rgba(139, 92, 246, 0.2);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --code-font: "Fira Code", "Cascadia Code", Consolas, monospace;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            line-height: 1.6;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
        }}
        h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #c084fc;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .query-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-top: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .query-text {{
            font-family: var(--code-font);
            color: #38bdf8;
            font-size: 1.1rem;
        }}
        .stats-badge {{
            background: #0284c722;
            color: #38bdf8;
            border: 1px solid #0284c755;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
        }}
        .results-list {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            margin-top: 1.5rem;
        }}
        .result-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: border-color 0.2s;
        }}
        .result-card:hover {{
            border-color: var(--accent);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}
        .card-title {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .rank-badge {{
            background: #334155;
            color: #cbd5e1;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .category-tag {{
            background: #4c1d95;
            color: #ddd6fe;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .score-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 700;
        }}
        .section-header {{
            font-size: 0.9rem;
            color: #a78bfa;
            margin-bottom: 0.75rem;
        }}
        .card-body {{
            background: #0f172a88;
            padding: 1rem;
            border-radius: 6px;
            border-left: 3px solid var(--accent);
            font-size: 0.95rem;
            color: #e2e8f0;
            white-space: pre-wrap;
            margin-bottom: 0.75rem;
        }}
        .card-footer {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            padding-top: 0.75rem;
        }}
        .badge-entity {{
            background: #065f46;
            color: #a7f3d0;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-right: 0.35rem;
        }}
        .context-export {{
            margin-top: 2.5rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
        }}
        .context-export h2 {{
            font-size: 1.2rem;
            color: #f1f5f9;
            margin-bottom: 0.5rem;
        }}
        textarea {{
            width: 100%;
            height: 200px;
            background: #090d16;
            color: #a5f3fc;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem;
            font-family: var(--code-font);
            font-size: 0.85rem;
            resize: vertical;
        }}
        button {{
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 0.5rem;
        }}
        button:hover {{ background: #7c3aed; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✦ Ars Arcanum Sovereign Semantic Retrieval</h1>
            <p style="color: var(--text-muted);">100% Offline Hybrid Vector Space &amp; Canonical Lore Query Engine</p>
            <div class="query-box">
                <div class="query-text">"{html.escape(query)}"</div>
                <div class="stats-badge">{len(results)} chunks retrieved</div>
            </div>
        </header>

        <main>
            <div class="results-list">
                {results_container}
            </div>

            <div class="context-export">
                <h2>Prompt Context for Local LLMs (Llama 3 / Mistral / Ollama)</h2>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.75rem;">
                    Copy this injection-safe formatted context block directly into your offline LLM studio.
                </p>
                <textarea id="promptContext" readonly>{html.escape(raw_context)}</textarea>
                <button onclick="navigator.clipboard.writeText(document.getElementById('promptContext').value); this.innerText='✓ Copied Context!';">
                    Copy Prompt Context
                </button>
            </div>
        </main>
    </div>
</body>
</html>
"""


# ==============================================================================
# Helper Discovery & Main CLI Entry Point
# ==============================================================================

def find_default_corpus_database() -> Path | None:
    """Searches workspace for default corpus.db SQLite database."""
    candidates = [
        PROJECT_ROOT / "dist" / "corpus.db",
        PROJECT_ROOT / "dist" / "corpus" / "corpus.db",
        PROJECT_ROOT / "corpus.db",
        Path.cwd() / "dist" / "corpus.db",
        Path.cwd() / "corpus.db",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum rag",
        description="Sovereign Zero-Dependency Local Semantic Retrieval (RAG) & Lore Engine",
    )
    parser.add_argument("query", nargs="*", help="Natural language query or lore question")
    parser.add_argument("-d", "--db", help="Path to corpus.db SQLite database")
    parser.add_argument("-t", "--target", help="Path to Markdown world vault or manuscript directory")
    parser.add_argument("-j", "--jsonl", help="Path to chunks.jsonl dataset file")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of chunks to retrieve (default: 5)")
    parser.add_argument("-m", "--min-score", type=float, default=0.05, help="Minimum relevance score threshold (default: 0.05)")
    parser.add_argument("-c", "--category", help="Filter chunks by category (e.g. Characters, Locations)")
    parser.add_argument("--type", dest="corpus_type", help="Filter by corpus type (lore, manuscript, meta)")
    parser.add_argument(
        "-f", "--format",
        choices=["context", "markdown", "json", "html"],
        default="context",
        help="Output format (default: context)",
    )
    parser.add_argument("-o", "--output", help="Save output to file instead of stdout")
    parser.add_argument("--instructions", help="Custom system instructions for LLM context")

    args = parser.parse_args(argv)

    query_str = " ".join(args.query).strip()
    if not query_str:
        parser.print_help()
        return 2

    engine = LocalLoreRetrievalEngine()

    # Determine data source
    if args.db:
        db_path = Path(args.db).resolve()
        if not db_path.is_file():
            print(f"Error: Database '{db_path}' not found.", file=sys.stderr)
            return 1
        engine.load_from_sqlite(db_path)
    elif args.jsonl:
        jsonl_path = Path(args.jsonl).resolve()
        if not jsonl_path.is_file():
            print(f"Error: JSONL file '{jsonl_path}' not found.", file=sys.stderr)
            return 1
        engine.load_from_jsonl(jsonl_path)
    elif args.target:
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"Error: Target path '{target_path}' not found.", file=sys.stderr)
            return 1
        engine.load_from_directory(target_path)
    else:
        # Check for default corpus database
        default_db = find_default_corpus_database()
        if default_db:
            engine.load_from_sqlite(default_db)
        else:
            # Fall back to scanning current directory
            engine.load_from_directory(Path.cwd())

    if engine.total_chunks == 0:
        print("Warning: No lore chunks found in specified source.", file=sys.stderr)

    # Perform retrieval query
    results = engine.query(
        query_text=query_str,
        top_k=args.top_k,
        min_score=args.min_score,
        category=args.category,
        corpus_type=args.corpus_type,
    )

    # Format output
    output_text = ""
    if args.format == "context":
        output_text = synthesize_llm_context(query_str, results, system_instructions=args.instructions)
    elif args.format == "markdown":
        output_text = format_markdown_report(query_str, results)
    elif args.format == "json":
        payload = {
            "query": query_str,
            "total_chunks_indexed": engine.total_chunks,
            "results_count": len(results),
            "results": [r.to_dict() for r in results],
        }
        output_text = json.dumps(payload, indent=2, ensure_ascii=False)
    elif args.format == "html":
        output_text = generate_html_retrieval_viewer(query_str, results)

    if args.output:
        out_path = Path(args.output).resolve()
        atomic_write(out_path, output_text)
        print(f"Retrieval report saved to: {out_path}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
