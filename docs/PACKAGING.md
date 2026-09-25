# Multi-Platform Distribution & Release Packaging Engine
> **Ars Arcanum Module**: `scripts/package_distribution.py` | **CLI**: `arcanum package` (alias: `dist-bundle`)

---

## 1. Overview & Capabilities (OPS-101)

The **Ars Arcanum Release Distribution Packager** compiles polished manuscripts, submission documents, advance reading copies, and interactive world lore into tamper-verified, publication-grade distribution bundles.

### Supported Package Targets

1. 📖 **Reader Edition Bundle**:
   - Contains finalized EPUB, PDF, offline HTML reading editions, and cover artwork in `Ebooks/` and `Art/`.
   - Includes standard `README.txt` with edition compilation metadata.
2. 🏛️ **Agent & Publisher Submission Package**:
   - Compiles standard industry `.docx`/`.pdf` manuscripts from `Exports/` into `Manuscripts/`.
   - Bundles query letter, synopsis, and chapter outlines from `Submissions/` into `Submission_Documents/`.
   - Generates `SUBMISSION_INFO.txt` with word count and format specs.
3. 🔒 **Advance Reading Copy (ARC)**:
   - Packages uncorrected advance proofs for beta readers and reviewers.
   - Bakes customized, reviewer-specific legal embargo notices into `ARC_LICENSE_NOTICE.txt` and embeds recipient watermarks into package archives.
4. 🗺️ **World Lore Codex Bundle**:
   - Compiles offline static HTML codices, SVG interactive maps, stylesheets, and lore indices into `Static_Codex/` and `Maps/`.
   - Generates `CODEX_INFO.txt` for worldbuilding companion distributions.

---

## 2. Integrity & Provenance Manifests

Every release packaging pass computes cryptographic **SHA-256 checksums** for all generated archive bundles and writes an authoritative `RELEASE_MANIFEST.json`:

```json
{
  "manuscript": "The_Silver_Chronicles",
  "generated_at": "2026-09-25T20:00:00.000000",
  "packages": [
    {
      "package_type": "reader",
      "archive_path": "Dist/The_Silver_Chronicles_Reader_Edition.zip",
      "filename": "The_Silver_Chronicles_Reader_Edition.zip",
      "files_count": 4,
      "size_bytes": 1258291,
      "sha256": "3a7b9c..."
    }
  ]
}
```

---

## 3. CLI Usage Reference

### 3.1 Generating Distribution Packages
```bash
# Generate all applicable distribution bundles into Dist/
arcanum package ~/Manuscripts/MyNovel/

# Generate only Reader Edition
arcanum package ~/Manuscripts/MyNovel/ -t reader -o dist/releases/

# Generate an Advance Reading Copy (ARC) for a specific reviewer
arcanum package ~/Manuscripts/MyNovel/ -t arc --reviewer "Elena Croft" -o dist/arcs/

# Generate Agent Submission Package
arcanum package ~/Manuscripts/MyNovel/ -t submission -o dist/submissions/

# Output machine-readable release manifest as JSON
arcanum package ~/Manuscripts/MyNovel/ --json
```

### 3.2 CLI Options

| Flag | Parameter | Default | Description |
| :--- | :--- | :--- | :--- |
| `-t`, `--type` | `reader`, `submission`, `arc`, `codex`, `all` | `all` | Package bundle type to generate. |
| `-o`, `--output` | `DIRECTORY` | `<target>/Dist` | Output destination directory for generated ZIP archives. |
| `--reviewer` | `NAME` | `Early Reviewer` | Custom recipient name watermarked into ARC bundles. |
| `--json` | | `false` | Output release manifest JSON to stdout. |

---

## 4. Directory Structure Mapping

```
Target_Manuscript/
├── Exports/                --> Reader / Submission / ARC Bundles (PDF, EPUB, DOCX)
├── Submissions/            --> Submission Package (Query.md, Synopsis.md)
├── Codex/                  --> World Lore Codex Bundle (index.html, styles.css)
├── Maps/                   --> World Lore Codex Bundle (*.svg)
├── 03-Art/                 --> Reader Bundle (Cover.png, illustrations)
└── Dist/
    ├── Novel_Reader_Edition.zip
    ├── Novel_Submission_Package.zip
    ├── Novel_ARC_Elena_Croft.zip
    ├── Novel_Codex_Bundle.zip
    └── RELEASE_MANIFEST.json
```

---

## 5. Architectural Invariants

- **Zero-Pip Guarantee**: Standard library Python (`zipfile`, `hashlib`, `argparse`, `json`, `datetime`).
- **Defensive Sanitization**: Reviewer filenames sanitized using `^[a-zA-Z0-9_-]+$`.
- **Atomic Manifest Generation**: Release metadata written with verified cryptographic digests.
