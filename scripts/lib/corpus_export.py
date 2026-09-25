#!/usr/bin/env python3
"""
Ars Arcanum Universal Structured Corpus & RAG Dataset Exporter
(scripts/lib/corpus_export.py)
================================================================================
Zero-dependency, offline structured corpus compilation engine transforming
Obsidian World Bibles, Cosmos Universes, and multi-volume manuscripts into
sanitized JSONL, SQLite database, and Markdown datasets for local LLM
fine-tuning, vector search embeddings, and archival analysis.

Capabilities:
1. Universal Vault & Manuscript Traversal:
   - Scans World Bibles (Characters, Locations, Factions, MagicSystems, History, etc.)
   - Scans Manuscript Chapters, Scenes, Drafts, and Front/Back Matter.
   - Extracts YAML frontmatter, inline @tags, Obsidian [[wikilinks]], and headings.
2. Semantic Chunking for Local RAG:
   - Configurable paragraph/heading-aware semantic chunking with token estimates.
   - Preserves parent document metadata, section headers, and entity link graphs per chunk.
3. Multi-Format Sovereign Exports:
   - JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`).
   - Relational SQLite 3 Database (`corpus.db`) with normalized schema and FTS5 full-text search.
   - Master Corpus Markdown Digest (`_corpus_summary.md`).

Zero external dependencies; 100% offline privacy.
"""

import argparse
import datetime
import html
import json
import logging
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter

logger = logging.getLogger("arcanum.corpus")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")
TAG_REGEX = re.compile(r"@([a-zA-Z0-9_-]+):\s*([^\r\n]+)")
HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

LORE_TAXONOMIES = {
    "Characters", "Locations", "Factions", "Artifacts", "Bestiary",
    "Cosmology", "Languages", "MagicSystems", "Magic-Technology", "History",
    "Items", "Concepts", "Flora", "Fauna", "Religions", "Nations"
}


@dataclass
class CorpusChunk:
    id: str
    doc_id: str
    chunk_index: int
    heading: str
    text: str
    word_count: int
    token_count_est: int
    entities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorpusEntity:
    id: str
    name: str
    entity_type: str
    doc_id: str | None
    aliases: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    outgoing_references: list[str] = field(default_factory=list)
    mention_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorpusDocument:
    id: str
    corpus_type: str  # "lore", "manuscript", "meta"
    category: str     # "Characters", "Locations", "Chapter", "Universe", etc.
    title: str
    path: str
    word_count: int
    token_count_est: int
    frontmatter: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, list[str]] = field(default_factory=dict)
    entities_referenced: list[str] = field(default_factory=list)
    body: str = ""
    chunks: list[CorpusChunk] = field(default_factory=list)

    def to_dict(self, include_body: bool = True, include_chunks: bool = True) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "corpus_type": self.corpus_type,
            "category": self.category,
            "title": self.title,
            "path": self.path,
            "word_count": self.word_count,
            "token_count_est": self.token_count_est,
            "frontmatter": self.frontmatter,
            "tags": self.tags,
            "entities_referenced": self.entities_referenced,
        }
        if include_body:
            d["body"] = self.body
        if include_chunks:
            d["chunks"] = [c.to_dict() for c in self.chunks]
        return d


def sanitize_id(raw_str: str) -> str:
    """Converts a path or name into a safe, normalized identifier string."""
    clean = raw_str.replace("\\", "/").strip().lower()
    clean = re.sub(r"[^\w\-/.]", "_", clean)
    clean = re.sub(r"_+", "_", clean)
    return clean.strip("_")


def extract_wikilinks(text: str) -> list[str]:
    """Extracts unique targets from Obsidian wikilinks [[Target]] or [[Target|Label]]."""
    targets: list[str] = []
    for match in WIKILINK_REGEX.finditer(text):
        target = match.group(1).strip()
        if target and target not in targets:
            targets.append(target)
    return targets


def extract_inline_tags(text: str) -> dict[str, list[str]]:
    """Extracts key-value tags like @pov: Aeloria or @location: High-Sanctuary."""
    tags: dict[str, list[str]] = {}
    for match in TAG_REGEX.finditer(text):
        key = match.group(1).lower().strip()
        val = match.group(2).strip()
        if val:
            tags.setdefault(key, []).append(val)
    return tags


def chunk_document(
    doc_id: str,
    body: str,
    target_chunk_words: int = 250,
) -> list[CorpusChunk]:
    """
    Splits document body into heading- and paragraph-aware semantic chunks.
    Preserves heading context and extracts per-chunk entity wikilinks.
    """
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[CorpusChunk] = []
    current_heading = "General"
    current_chunk_paras: list[str] = []
    current_chunk_words = 0
    chunk_idx = 1

    def flush_chunk():
        nonlocal chunk_idx, current_chunk_paras, current_chunk_words
        if not current_chunk_paras:
            return
        chunk_text = "\n\n".join(current_chunk_paras).strip()
        word_cnt = len(re.findall(r"\b\w+\b", chunk_text))
        token_est = round(word_cnt * 1.33)
        chunk_entities = extract_wikilinks(chunk_text)

        chunks.append(CorpusChunk(
            id=f"{doc_id}#chunk_{chunk_idx:03d}",
            doc_id=doc_id,
            chunk_index=chunk_idx,
            heading=current_heading,
            text=chunk_text,
            word_count=word_cnt,
            token_count_est=token_est,
            entities=chunk_entities,
        ))
        chunk_idx += 1
        current_chunk_paras = []
        current_chunk_words = 0

    for para in paragraphs:
        # Check if paragraph is or starts with a heading
        h_match = re.match(r"^(#{1,6})\s+([^\r\n]+)", para)
        if h_match:
            # If we already have accumulated chunk content, flush before starting new section
            if current_chunk_paras:
                flush_chunk()
            current_heading = h_match.group(2).strip()

        para_words = len(re.findall(r"\b\w+\b", para))
        if current_chunk_words + para_words > target_chunk_words and current_chunk_paras:
            flush_chunk()

        current_chunk_paras.append(para)
        current_chunk_words += para_words

    flush_chunk()
    return chunks


def process_markdown_file(
    file_path: Path,
    root_path: Path,
    target_chunk_words: int = 250,
) -> CorpusDocument:
    """Parses a single Markdown document into a structured CorpusDocument with chunks."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    frontmatter = parse_yaml_frontmatter(content)
    body = FRONTMATTER_REGEX.sub("", content).strip()

    rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")
    doc_id = sanitize_id(rel_path.removesuffix(".md"))

    # Determine corpus type & category
    path_parts = file_path.parts
    corpus_type = "lore"
    category = "General"

    if "Manuscripts" in path_parts or "draft" in file_path.name.lower() or "chapter" in file_path.name.lower():
        corpus_type = "manuscript"
        category = "Manuscript"
        for part in path_parts:
            if part.startswith("Book-") or part.startswith("Volume-"):
                category = part
                break
    elif file_path.name in ("Universe-Index.md", "World-Bible-Index.md", "README.md", "SUMMARY.md"):
        corpus_type = "meta"
        category = "Index"
    else:
        # Check taxonomy folder
        for part in path_parts:
            if part in LORE_TAXONOMIES:
                category = part
                corpus_type = "lore"
                break
        else:
            if "type" in frontmatter:
                category = str(frontmatter["type"]).title()

    # Extract Title
    h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    title = str(
        frontmatter.get("name")
        or frontmatter.get("title")
        or (h1_match.group(1).strip() if h1_match else file_path.stem.replace("-", " ").replace("_", " ").title())
    )

    # Extract tags & wikilinks
    tags = extract_inline_tags(body)
    if "aliases" in frontmatter and isinstance(frontmatter["aliases"], list):
        tags["aliases"] = [str(a) for a in frontmatter["aliases"]]
    if "tags" in frontmatter:
        raw_tags = frontmatter["tags"]
        if isinstance(raw_tags, list):
            tags["tags"] = [str(t) for t in raw_tags]
        elif isinstance(raw_tags, str):
            tags["tags"] = [raw_tags]

    entities_referenced = extract_wikilinks(body)
    # Also include wikilinks from frontmatter values
    for v in frontmatter.values():
        if isinstance(v, str):
            for link in extract_wikilinks(v):
                if link not in entities_referenced:
                    entities_referenced.append(link)

    word_count = len(re.findall(r"\b\w+\b", body))
    token_count_est = round(word_count * 1.33)

    chunks = chunk_document(doc_id, body, target_chunk_words=target_chunk_words)

    return CorpusDocument(
        id=doc_id,
        corpus_type=corpus_type,
        category=category,
        title=title,
        path=rel_path,
        word_count=word_count,
        token_count_est=token_count_est,
        frontmatter=frontmatter,
        tags=tags,
        entities_referenced=entities_referenced,
        body=body,
        chunks=chunks,
    )


class CorpusScanner:
    """Scans a target directory or file and compiles all documents, chunks, and entities."""

    def __init__(self, target: Path, target_chunk_words: int = 250, include_drafts: bool = True):
        self.target = target.resolve()
        self.target_chunk_words = target_chunk_words
        self.include_drafts = include_drafts
        self.documents: list[CorpusDocument] = []
        self.entities: dict[str, CorpusEntity] = {}
        self.relationships: list[dict[str, str]] = []

    def scan(self) -> None:
        """Executes full repository discovery and entity resolution."""
        files: list[Path] = []
        if self.target.is_file() and self.target.suffix.lower() == ".md":
            files.append(self.target)
            root_path = self.target.parent
        else:
            root_path = self.target
            for p in sorted(self.target.rglob("*.md")):
                if p.name.startswith((".", "_")):
                    continue
                if "Backups" in p.parts or ".git" in p.parts or "node_modules" in p.parts:
                    continue
                if not self.include_drafts and "Back_Matter" in p.parts:
                    continue
                files.append(p)

        self.documents = [
            process_markdown_file(f, root_path, target_chunk_words=self.target_chunk_words)
            for f in files
        ]

        self._build_entity_graph()

    def _build_entity_graph(self) -> None:
        """Discovers declared entities and builds cross-document references."""
        # 1. Register declared entities from documents
        for doc in self.documents:
            # Lore documents or documents with explicit name/type define an entity
            is_entity_doc = (
                doc.corpus_type == "lore"
                or "type" in doc.frontmatter
                or doc.category in LORE_TAXONOMIES
            )
            if is_entity_doc:
                ent_name = str(doc.frontmatter.get("name", doc.title))
                ent_type = str(doc.frontmatter.get("type", doc.category)).lower()
                aliases = [str(a) for a in doc.frontmatter.get("aliases", []) if isinstance(a, str)]

                ent = CorpusEntity(
                    id=sanitize_id(ent_name),
                    name=ent_name,
                    entity_type=ent_type,
                    doc_id=doc.id,
                    aliases=aliases,
                    metadata=doc.frontmatter,
                    outgoing_references=list(doc.entities_referenced),
                    mention_count=0,
                )
                self.entities[ent_name] = ent
                # Map aliases too
                for a in aliases:
                    if a not in self.entities:
                        self.entities[a] = ent

                # Extract explicit frontmatter relationships
                for rel_key, rel_val in doc.frontmatter.items():
                    if isinstance(rel_val, str) and rel_val.startswith("[[") and rel_val.endswith("]]"):
                        target_ent = rel_val.strip("[]").split("|")[0].strip()
                        self.relationships.append({
                            "source": ent_name,
                            "target": target_ent,
                            "relation": rel_key,
                            "doc_id": doc.id,
                        })

        # 2. Count mentions and incoming links across all documents
        for doc in self.documents:
            for ref in doc.entities_referenced:
                if ref in self.entities:
                    self.entities[ref].mention_count += 1
                else:
                    # Discover implicit entity referenced by wikilink
                    self.entities[ref] = CorpusEntity(
                        id=sanitize_id(ref),
                        name=ref,
                        entity_type="inferred",
                        doc_id=None,
                        mention_count=1,
                    )

    def total_words(self) -> int:
        return sum(d.word_count for d in self.documents)

    def total_chunks(self) -> int:
        return sum(len(d.chunks) for d in self.documents)


def export_jsonl(scanner: CorpusScanner, output_dir: Path) -> dict[str, Path]:
    """Exports dataset to documents.jsonl, chunks.jsonl, and entities.jsonl."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    # 1. documents.jsonl
    docs_file = output_dir / "documents.jsonl"
    doc_lines = [json.dumps(d.to_dict(include_body=True, include_chunks=False)) for d in scanner.documents]
    atomic_write(docs_file, "\n".join(doc_lines) + "\n")
    paths["documents"] = docs_file

    # 2. chunks.jsonl
    chunks_file = output_dir / "chunks.jsonl"
    chunk_lines = []
    for d in scanner.documents:
        for c in d.chunks:
            chunk_dict = c.to_dict()
            chunk_dict["doc_title"] = d.title
            chunk_dict["doc_category"] = d.category
            chunk_dict["corpus_type"] = d.corpus_type
            chunk_lines.append(json.dumps(chunk_dict))
    atomic_write(chunks_file, "\n".join(chunk_lines) + "\n")
    paths["chunks"] = chunks_file

    # 3. entities.jsonl
    entities_file = output_dir / "entities.jsonl"
    unique_entities = {e.name: e for e in scanner.entities.values()}
    ent_lines = [json.dumps(e.to_dict()) for e in unique_entities.values()]
    atomic_write(entities_file, "\n".join(ent_lines) + "\n")
    paths["entities"] = entities_file

    return paths


def export_sqlite(scanner: CorpusScanner, db_path: Path) -> Path:
    """Exports structured SQLite database with relational schema and full-text search."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Schema creation
    cursor.executescript("""
    CREATE TABLE corpus_meta (
        corpus_name TEXT PRIMARY KEY,
        exported_at TEXT,
        total_docs INTEGER,
        total_words INTEGER,
        total_chunks INTEGER,
        total_entities INTEGER,
        version TEXT
    );

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
        entities_json TEXT,
        FOREIGN KEY(doc_id) REFERENCES documents(id)
    );

    CREATE TABLE entities (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE,
        entity_type TEXT,
        doc_id TEXT,
        aliases_json TEXT,
        mention_count INTEGER,
        metadata_json TEXT
    );

    CREATE TABLE entity_mentions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_name TEXT,
        source_doc_id TEXT,
        chunk_id TEXT,
        mention_type TEXT
    );

    CREATE TABLE relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_entity TEXT,
        target_entity TEXT,
        relation_type TEXT,
        doc_id TEXT
    );

    CREATE INDEX idx_docs_type ON documents(corpus_type);
    CREATE INDEX idx_docs_category ON documents(category);
    CREATE INDEX idx_chunks_doc ON chunks(doc_id);
    CREATE INDEX idx_entities_type ON entities(entity_type);
    CREATE INDEX idx_rel_source ON relationships(source_entity);
    CREATE INDEX idx_rel_target ON relationships(target_entity);
    """)

    # Try creating FTS5 virtual tables
    try:
        cursor.executescript("""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
            id UNINDEXED,
            title,
            body
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            id UNINDEXED,
            heading,
            text
        );
        """)
        has_fts5 = True
    except Exception as e:
        logger.warning(f"SQLite FTS5 virtual tables could not be created: {e}")
        has_fts5 = False

    # Insert metadata
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    unique_entities = {e.name: e for e in scanner.entities.values()}

    cursor.execute("""
    INSERT INTO corpus_meta (corpus_name, exported_at, total_docs, total_words, total_chunks, total_entities, version)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scanner.target.name,
        now_iso,
        len(scanner.documents),
        scanner.total_words(),
        scanner.total_chunks(),
        len(unique_entities),
        "1.9.0",
    ))

    # Insert documents & chunks
    for doc in scanner.documents:
        cursor.execute("""
        INSERT INTO documents (id, corpus_type, category, title, path, word_count, token_count_est, frontmatter_json, body)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.id,
            doc.corpus_type,
            doc.category,
            doc.title,
            doc.path,
            doc.word_count,
            doc.token_count_est,
            json.dumps(doc.frontmatter),
            doc.body,
        ))

        if has_fts5:
            cursor.execute("INSERT INTO documents_fts (id, title, body) VALUES (?, ?, ?)", (doc.id, doc.title, doc.body))

        for c in doc.chunks:
            cursor.execute("""
            INSERT INTO chunks (id, doc_id, chunk_index, heading, text, word_count, token_count_est, entities_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c.id,
                c.doc_id,
                c.chunk_index,
                c.heading,
                c.text,
                c.word_count,
                c.token_count_est,
                json.dumps(c.entities),
            ))

            if has_fts5:
                cursor.execute("INSERT INTO chunks_fts (id, heading, text) VALUES (?, ?, ?)", (c.id, c.heading, c.text))

            # Record chunk mentions
            for ent_ref in c.entities:
                cursor.execute("""
                INSERT INTO entity_mentions (entity_name, source_doc_id, chunk_id, mention_type)
                VALUES (?, ?, ?, ?)
                """, (ent_ref, doc.id, c.id, "wikilink"))

    # Insert entities
    for ent in unique_entities.values():
        cursor.execute("""
        INSERT OR REPLACE INTO entities (id, name, entity_type, doc_id, aliases_json, mention_count, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ent.id,
            ent.name,
            ent.entity_type,
            ent.doc_id,
            json.dumps(ent.aliases),
            ent.mention_count,
            json.dumps(ent.metadata),
        ))

    # Insert relationships
    for rel in scanner.relationships:
        cursor.execute("""
        INSERT INTO relationships (source_entity, target_entity, relation_type, doc_id)
        VALUES (?, ?, ?, ?)
        """, (rel["source"], rel["target"], rel["relation"], rel["doc_id"]))

    conn.commit()
    conn.close()
    return db_path


def export_markdown_summary(scanner: CorpusScanner, output_file: Path) -> Path:
    """Generates an executive Markdown corpus digest and data catalog."""
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    unique_entities = {e.name: e for e in scanner.entities.values()}

    # Categorize documents
    lore_docs = [d for d in scanner.documents if d.corpus_type == "lore"]
    manuscript_docs = [d for d in scanner.documents if d.corpus_type == "manuscript"]
    meta_docs = [d for d in scanner.documents if d.corpus_type == "meta"]

    top_entities = sorted(unique_entities.values(), key=lambda e: e.mention_count, reverse=True)[:15]

    lines = [
        f"# Corpus Summary Digest: {scanner.target.name}",
        "",
        f"> **Generated**: {now_str}  ",
        f"> **Target**: `{scanner.target}`  ",
        f"> **Total Documents**: {len(scanner.documents)} | **Total Words**: {scanner.total_words():,} | **Semantic Chunks**: {scanner.total_chunks():,} | **Entities**: {len(unique_entities):,}",
        "",
        "---",
        "",
        "## 1. Corpus Metrics Overview",
        "",
        "| Dimension | Count | Total Words | Est. Tokens (~1.33x) |",
        "| :--- | :--- | :--- | :--- |",
        f"| **World Bible & Lore** | {len(lore_docs)} | {sum(d.word_count for d in lore_docs):,} | {sum(d.token_count_est for d in lore_docs):,} |",
        f"| **Manuscripts & Chapters** | {len(manuscript_docs)} | {sum(d.word_count for d in manuscript_docs):,} | {sum(d.token_count_est for d in manuscript_docs):,} |",
        f"| **Meta & Indexes** | {len(meta_docs)} | {sum(d.word_count for d in meta_docs):,} | {sum(d.token_count_est for d in meta_docs):,} |",
        f"| **Total Unified Corpus** | **{len(scanner.documents)}** | **{scanner.total_words():,}** | **{round(scanner.total_words() * 1.33):,}** |",
        "",
        "---",
        "",
        "## 2. Most Frequently Mentioned Entities",
        "",
        "| Entity Name | Type | Mentions | Defined In | Aliases |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for ent in top_entities:
        doc_str = f"`{ent.doc_id}`" if ent.doc_id else "*Inferred*"
        alias_str = ", ".join(ent.aliases) if ent.aliases else "—"
        lines.append(f"| **{html.escape(ent.name)}** | `{ent.entity_type}` | {ent.mention_count} | {doc_str} | {alias_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Document Catalog",
        "",
        "| Path | Type | Category | Words | Chunks | Links |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for d in scanner.documents:
        lines.append(f"| `{d.path}` | `{d.corpus_type}` | {d.category} | {d.word_count:,} | {len(d.chunks)} | {len(d.entities_referenced)} |")

    lines.append("")
    atomic_write(output_file, "\n".join(lines))
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Universal Structured Corpus & RAG Dataset Exporter")
    parser.add_argument("target", help="Universe, World Bible, Manuscript directory or Markdown file")
    parser.add_argument("--format", "-f", choices=["jsonl", "sqlite", "summary", "both", "all"], default="both", help="Export format (default: both)")
    parser.add_argument("--output", "-o", help="Output directory or database file path")
    parser.add_argument("--chunk-size", type=int, default=250, help="Target semantic chunk word size (default: 250)")
    parser.add_argument("--json", action="store_true", help="Print export summary JSON to stdout")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report metrics without writing files")

    # If first argument is 'export', strip it for CLI consistency (e.g. arcanum corpus export <target>)
    raw_args = sys.argv[1:]
    if raw_args and raw_args[0] == "export":
        raw_args = raw_args[1:]

    args = parser.parse_args(raw_args)

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    scanner = CorpusScanner(target_path, target_chunk_words=args.chunk_size)
    scanner.scan()

    if args.dry_run or args.json:
        report = {
            "target": str(target_path),
            "total_documents": len(scanner.documents),
            "total_words": scanner.total_words(),
            "total_chunks": scanner.total_chunks(),
            "total_entities": len({e.name: e for e in scanner.entities.values()}),
            "categories": sorted(list({d.category for d in scanner.documents})),
        }
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Corpus Dry Run: {len(scanner.documents)} docs | {scanner.total_words():,} words | {scanner.total_chunks():,} chunks | {report['total_entities']} entities")
        return

    # Determine default output directory
    out_path = Path(args.output) if args.output else Path("dist") / "corpus" / target_path.stem

    fmt = args.format.lower()

    generated_files: list[str] = []

    if fmt in ("jsonl", "both", "all"):
        jsonl_paths = export_jsonl(scanner, out_path)
        generated_files.extend([str(p) for p in jsonl_paths.values()])

    if fmt in ("sqlite", "both", "all"):
        db_file = out_path if out_path.suffix == ".db" else out_path / f"{sanitize_id(target_path.stem)}.db"
        export_sqlite(scanner, db_file)
        generated_files.append(str(db_file))

    if fmt in ("summary", "both", "all"):
        summary_file = out_path / "_corpus_summary.md"
        export_markdown_summary(scanner, summary_file)
        generated_files.append(str(summary_file))

    print("=" * 75)
    print("  🏛️  Ars Arcanum Universal Corpus Exporter — v1.9.0")
    print("=" * 75)
    print(f"Target:          {target_path}")
    print(f"Total Documents: {len(scanner.documents)}")
    print(f"Total Words:     {scanner.total_words():,}")
    print(f"Total Chunks:    {scanner.total_chunks():,}")
    print(f"Total Entities:  {len({e.name: e for e in scanner.entities.values()}):,}")
    print(f"Output Path:     {out_path}")
    print("-" * 75)
    print("Generated Artifacts:")
    for f in generated_files:
        print(f"  • {f}")
    print("=" * 75)


if __name__ == "__main__":
    main()
