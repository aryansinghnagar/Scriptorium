# Universal Structured Corpus & RAG Dataset Exporter
`scripts/lib/corpus_export.py` / `arcanum corpus export`

---

## 1. Overview & Sovereign AI Philosophy

Modern authors and worldbuilders often wish to leverage **local, offline AI models** (e.g. Llama 3, Mistral, Gemma, Phi) or **local vector search/retrieval systems** (RAG) to query their expansive World Bibles, character arcs, and multi-volume manuscripts. However, uploading creative intellectual property or private manuscripts to third-party cloud APIs poses serious copyright, data privacy, and telemetry risks.

**Ars Arcanum's Universal Structured Corpus Exporter** transforms your sovereign writing vaults into standardized, high-performance datasets with **zero external dependencies and 100% offline privacy**:

- **JSON Lines (`.jsonl`)**: Standard data interchange format for embeddings, vector databases, and fine-tuning pipelines.
- **Relational SQLite Database (`.db`)**: Normalized schema with built-in **FTS5 full-text search**, foreign key relationships, and fast indexed queries.
- **Executive Corpus Summary Digest (`_corpus_summary.md`)**: A consolidated markdown catalog summarizing document metrics, dramatis personae frequencies, and taxonomy distributions.

---

## 2. CLI Usage

```bash
# Export demo cosmos to both JSONL and SQLite in dist/corpus
arcanum corpus export templates/demo-cosmos/Eldoria-Cosmos

# Export with specific format and output directory
arcanum corpus export ~/Universes/Cosmere --format sqlite -o dist/cosmere.db
arcanum corpus export ~/Manuscripts/The-Silver-Chronicles --format jsonl -o dist/dataset

# Dry-run inspection without writing files
arcanum corpus export ~/Universes/Eldoria --dry-run
arcanum corpus export ~/Universes/Eldoria --json
```

### Command Options

| Option | Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| `--format` | `-f` | `both` | Export format: `jsonl`, `sqlite`, `summary`, `both`, `all`. |
| `--output` | `-o` | `dist/corpus/<name>` | Target output directory or SQLite database file path. |
| `--chunk-size` | | `250` | Target semantic chunk size in words. |
| `--dry-run` | | `false` | Scan repository and display summary statistics without file I/O. |
| `--json` | | `false` | Output metadata summary as JSON to `stdout`. |

---

## 3. Structured Data Schema

### 3.1 JSON Lines Datasets

1. **`documents.jsonl`**:
   Contains top-level documents (World Bible entries, chapters, scenes, index files).
   ```json
   {
     "id": "eldoria-prime/characters/aeloria-vael",
     "corpus_type": "lore",
     "category": "Characters",
     "title": "Aeloria Vael",
     "path": "Eldoria-Prime/Characters/Aeloria-Vael.md",
     "word_count": 142,
     "token_count_est": 189,
     "frontmatter": { "name": "Aeloria Vael", "type": "character", "aliases": ["The Silver Blade"], "faction": "[[Order-of-the-Silver-Dawn]]" },
     "tags": { "pov": ["Aeloria-Vael"], "aliases": ["The Silver Blade"] },
     "entities_referenced": ["Order-of-the-Silver-Dawn", "High-Sanctuary", "Whispering-Vale", "Aether-Weaving"],
     "body": "..."
   }
   ```

2. **`chunks.jsonl`**:
   Semantic heading- and paragraph-aware chunks engineered for local vector embeddings:
   ```json
   {
     "id": "eldoria-prime/characters/aeloria-vael#chunk_001",
     "doc_id": "eldoria-prime/characters/aeloria-vael",
     "doc_title": "Aeloria Vael",
     "doc_category": "Characters",
     "corpus_type": "lore",
     "chunk_index": 1,
     "heading": "Personality & Motivation",
     "text": "Disciplined, observant, and fiercely loyal to the protection of [[High-Sanctuary]].",
     "word_count": 12,
     "token_count_est": 16,
     "entities": ["High-Sanctuary"]
   }
   ```

3. **`entities.jsonl`**:
   Cross-referenced entity graph with aliases, outgoing links, and mention frequency:
   ```json
   {
     "id": "aeloria_vael",
     "name": "Aeloria Vael",
     "entity_type": "character",
     "doc_id": "eldoria-prime/characters/aeloria-vael",
     "aliases": ["The Silver Blade", "Champion of the Spires"],
     "metadata": { "status": "active", "eyes": "violet" },
     "outgoing_references": ["Order-of-the-Silver-Dawn", "High-Sanctuary"],
     "mention_count": 14
   }
   ```

---

### 3.2 Relational SQLite Database (`corpus.db`)

The SQLite export creates a fully indexed relational database:

- `corpus_meta`: Vault metadata, timestamp, total document/word/entity counts.
- `documents`: Primary document records with JSON frontmatter and clean text bodies.
- `chunks`: Segmented chunks linked to parent documents via `FOREIGN KEY(doc_id)`.
- `entities`: Deduplicated entities with alias arrays and metadata payloads.
- `entity_mentions`: Specific mentions and links between source documents and entities.
- `relationships`: Typed edges between entities (e.g. `faction`, `origin`, `mentor`).
- `documents_fts` & `chunks_fts`: **SQLite FTS5 Full-Text Search** virtual tables for sub-millisecond keyword lookup:
  ```sql
  SELECT id, title FROM documents_fts WHERE documents_fts MATCH 'swordsman';
  ```

---

## 4. Local Python Query Example

```python
import sqlite3

conn = sqlite3.connect("dist/corpus/eldoria-cosmos/eldoria-cosmos.db")
cursor = conn.cursor()

# Find all chapters referencing High-Sanctuary
cursor.execute("""
    SELECT d.title, c.heading, c.text
    FROM chunks c
    JOIN documents d ON c.doc_id = d.id
    WHERE d.corpus_type = 'manuscript' AND c.entities_json LIKE '%High-Sanctuary%'
""")

for row in cursor.fetchall():
    print(f"[{row[0]} - {row[1]}]\n{row[2]}\n")
```
