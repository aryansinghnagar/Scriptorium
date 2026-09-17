# External Integrations

## Core Sections (Required)

### 1) Integration Inventory

| System | Type | Purpose | Auth model | Criticality | Evidence |
|--------|------|---------|------------|-------------|----------|
| **Obsidian** | Desktop Application (Flatpak) | World Bible lore editing, graph view, and Dataview DQL querying | Local sandbox filesystem permissions (`$HOME`) | High (Primary Worldbuilding Tool) | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L28-L32), [`templates/world-bible/.obsidian/`](file:///templates/world-bible/.obsidian/community-plugins.json#L1-L15) |
| **novelWriter** | Desktop Application (Flatpak) | Structured novel drafting, chapter/scene tree management | Local sandbox filesystem permissions (`$HOME`) | High (Primary Drafting Tool) | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L28-L32), [`templates/manuscript/nwProject.nwx`](file:///templates/manuscript/nwProject.nwx#L1-L15) |
| **Typst** | CLI Binary (musl) | Sub-second book typesetting and print-ready PDF generation | System local execution (`/usr/local/bin/typst`) | High (Publishing Engine) | [`scripts/export_book.sh`](file:///scripts/export_book.sh#L340-L420), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L9-L21) |
| **Pandoc** | CLI Binary (APT) | Markdown AST conversion to Typst, EPUB, and submission DOCX | System local execution (`/usr/bin/pandoc`) | High (Universal Bridge) | [`scripts/export_book.sh`](file:///scripts/export_book.sh#L190-L330), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **Calibre** | Desktop Application (Flatpak) | Ebook inspection, metadata editing, e-reader device synchronization | Local sandbox filesystem permissions (`$HOME`) | Medium (Ebook Inspection) | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L28-L32), [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L142-L209) |
| **FocusWriter** | Desktop Application (APT/Flatpak) | Full-screen distraction-free draft sprints | System local execution | Medium (Deep Focus) | [`docs/guides/DISTRACTION_CONTROL.md`](file:///docs/guides/DISTRACTION_CONTROL.md#L30-L34) |
| **LibreOffice Writer** | Desktop Application (APT) | Professional editorial collaboration and track changes | System local execution | Medium (Editorial) | [`docs/guides/SOFTWARE_CATALOG.md`](file:///docs/guides/SOFTWARE_CATALOG.md#L66-L74) |
| **Git** | CLI Binary (APT) | Multi-tier repository version tracking and automated snapshots | Local file-based repository (.git) | High (Version Safety) | [`scripts/save_snapshot.sh`](file:///scripts/save_snapshot.sh#L1-L60) |
| **LeechBlock NG** | WebExtension (Firefox) | Scheduled distraction blocking during writing blocks | Firefox add-on local storage | Low (Focus Enforcement) | [`configs/leechblock_scriptorium_rules.json`](file:///configs/leechblock_scriptorium_rules.json#L1-L25) |
| **Déjà Dup** | Desktop Application (APT) | Automated encrypted external USB 3-2-1 backups | Local/removable drive permissions | High (Disaster Recovery) | [`docs/guides/BACKUP_SETUP.md`](file:///docs/guides/BACKUP_SETUP.md#L1-L53) |

### 2) Data Stores

| Store | Role | Access layer | Key risk | Evidence |
|-------|------|--------------|----------|----------|
| **Local Markdown (`.md`) Files** | Canonical storage for all lore, character sheets, outlines, and manuscript scenes | Direct POSIX filesystem I/O | Accidental deletion or overwriting (mitigated by Git snapshots and 3-2-1 backups) | [`templates/world-bible/`](file:///templates/world-bible/00_START_HERE.md#L1-L45), [`templates/manuscript/`](file:///templates/manuscript/Outlines/Master-Outline.md#L1-L30) |
| **Project Manifests (`.yaml`)** | Metadata linkage for universes (`universe.yaml`), world lore vaults (`world.yaml`), and manuscripts (`manuscript.yaml`) | Python `yaml` / Shell string parser | Schema drift or invalid formatting (mitigated by doctor diagnostics) | [`tests/fixtures/sample_universe/universe.yaml`](file:///tests/fixtures/sample_universe/universe.yaml#L1-L10), [`tests/fixtures/sample_manuscript/manuscript.yaml`](file:///tests/fixtures/sample_manuscript/manuscript.yaml#L1-L10) |
| **novelWriter Manifest (`.nwx`)** | XML project indexing file adhering to novelWriter `fileVersion 1.5` | novelWriter XML parser | Broken XML formatting on manual edit (mitigated by CI validation and valid template) | [`templates/manuscript/nwProject.nwx`](file:///templates/manuscript/nwProject.nwx#L1-L25) |
| **Git Object Database (`.git`)** | Historical revisions, commit logs, and branching for universes, worlds, and books | Standard `git` CLI commands | Concurrent lock contention (`.git/index.lock`, handled via retry loop) | [`scripts/save_snapshot.sh`](file:///scripts/save_snapshot.sh#L45-L75) |
| **Backup Tarballs (`.tar.gz`)** | Standalone point-in-time disaster recovery archives | `tar`, `gzip`, `sha256sum` | Archive corruption (mitigated by SHA-256 manifest verification and restore drills) | [`scripts/backup_world.sh`](file:///scripts/backup_world.sh#L1-L70), [`scripts/restore_world.sh`](file:///scripts/restore_world.sh#L1-L80) |

### 3) Secrets and Credentials Handling

- **Credential sources**: Scriptorium is a 100% offline, local-first system. No cloud API keys, access tokens, or database credentials are required, handled, or stored.
- **Hardcoding checks**: Clean. Static scanning confirms zero hardcoded secrets, passwords, or personal credentials across all source files and test fixtures.
- **Rotation or lifecycle notes**: Not applicable (no remote credentials).

### 4) Reliability and Failure Behavior

- **Retry/backoff behavior**: `scripts/save_snapshot.sh` implements an exponential backoff retry loop (5 attempts with 1-second intervals) when encountering transient `.git/index.lock` contention caused by Obsidian Git auto-commits.
- **Timeout policy**: Long-running background processes (compilation, diagnostics, backups) in the GTK Control Center run asynchronously on daemon worker threads with real-time UI logging.
- **Circuit-breaker or fallback behavior**:
  - `scripts/export_book.sh`: Falls back from Typst PDF compilation to Pandoc EPUB and DOCX generation if Typst encounters an error, ensuring partial artifact delivery.
  - `scripts/setup_scriptorium.sh`: Refuses binary installation and fails closed (`TYPST_OK=0`) if Typst upstream release digests cannot be fetched or verified via SHA-256.

### 5) Observability for Integrations

- **Logging around external calls**: All shell scripts output explicit step and progress markers (`[INFO]`, `[OK]`, `[ERROR]`) to stdout/stderr.
- **Diagnostics suites**:
  - `scripts/scriptorium_doctor.sh`: Verifies availability and executable status of all required and optional external tools (Typst, Pandoc, Git, Zenity, Calibre, novelWriter, Obsidian, fonts).
  - `scripts/world_doctor.sh`: Validates internal entity integrity, chronological timelines, and manuscript-to-lore cross references.
- **Missing visibility gaps**: None identified for local single-user operation.

### 6) Evidence

- [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L1-L62)
- [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L210-L270)
- [`scripts/export_book.sh`](file:///scripts/export_book.sh#L190-L480)
- [`scripts/save_snapshot.sh`](file:///scripts/save_snapshot.sh#L45-L75)
- [`scripts/scriptorium_doctor.sh`](file:///scripts/scriptorium_doctor.sh#L1-L357)

## Extended Sections (Optional)

### Tool Invocation Matrix

- `typst compile <src.typ> <out.pdf> --font-path <fonts_dir>`: Invoked during book publishing.
- `pandoc -f markdown -t typst <src.md> -o <out.typ>`: Converts scene files into Typst source.
- `pandoc -f markdown-citations+smart -o <out.epub> <src.md>`: Converts scenes into formatted EPUB.
- `pandoc -f markdown -o <out.docx> <src.md>`: Converts scenes into standard manuscript submission `.docx`.
- `flatpak run <AppID> [args]`: Launches sandboxed GUI applications (Obsidian, novelWriter, Calibre).
