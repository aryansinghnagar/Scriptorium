# Architecture

## Core Sections (Required)

### 1) Architectural Style

- **Primary style**: Modular Local-First Layered Architecture with UNIX CLI Facade + Desktop GUI Layer + Multi-Tier Distributed Git Version Control.
- **Why this classification**: The system strictly separates presentation (GTK 3 GUI and Zenity dialogs) from orchestration (CLI facade `scripts/scriptorium`), discovery (`scripts/lib/worlds.sh`), core procedural execution (`scripts/*.sh`), and persistence (plain Markdown, YAML manifests, novelWriter XML, and local Git repositories). There are zero remote server daemons or proprietary database layers.
- **Primary constraints**:
  1. **Plain Text & Open Formats Invariant**: All data must remain 100% human-readable and future-proof in standard Markdown (`.md`) without vendor lock-in.
  2. **Zero-Terminal Daily Authoring Requirement**: All daily author workflows (creation, writing, snapshotting, exporting, diagnostics) must be executable via GUI without requiring terminal access.
  3. **Transactional Safety & Disaster Recovery**: Directory scaffolding and recovery must be atomic/staged (`mktemp -d` and `trap`), fail closed on missing digests, and guarantee 3-2-1 backup compliance.

### 2) System Flow

```text
[Desktop Launcher / CLI Facade]
       │
       ▼
[Discovery Engine (lib/worlds.sh)]
       │
       ▼
[Workflow Orchestrator (scaffold / export / snapshot / doctor)]
       │
       ▼
[File Processing & Compilation (Typst / Pandoc / Git / Tar)]
       │
       ▼
[Verified Artifact / Snapshot Output & GUI Feedback]
```

1. **User Invocation & Entry Selection**: Author clicks a desktop launcher (`launchers/*.desktop`), launches the GTK Control Center (`scripts/scriptorium_app.py`), or invokes the CLI facade (`scripts/scriptorium`).
2. **Project Discovery & Validation**: Scriptorium invokes `scripts/lib/worlds.sh` (`discover_worlds`, `discover_universes`, `discover_manuscripts`) to scan `~/Universes/` and `~/Manuscripts/`, resolving paths and universe labels without identity-based heuristics.
3. **Execution & Staging**: Depending on the workflow, scripts create temporary staging environments (`mktemp -d`), execute structural actions (e.g. copying templates, initializing Git repos, parsing frontmatter), and validate integrity before making filesystem changes permanent.
4. **Processing & Compilation Engine**:
   - In **Export**, `scripts/export_book.sh` bridges Markdown chapters into Typst (`templates/typst/book_template.typ`) for PDF rendering, Pandoc for EPUB/DOCX, and auto-detects cover artwork.
   - In **Concordance**, `scripts/generate_concordance.sh` parses World Bible entity notes and outputs publication back-matter (`01_Dramatis_Personae.md`, `02_Glossary_and_Concordance.md`).
   - In **Diagnostics**, `scripts/world_doctor.sh` and `scripts/scriptorium_doctor.sh` run multi-era timeline paradox detection, lore-to-manuscript drift checks (`WLD-108`), and toolchain verification.
5. **Version Control & Persistence**: In-place edits are tracked by Git repositories (via Obsidian Git or `scripts/save_snapshot.sh`), and disaster recovery tarballs are hashed with SHA-256 (`scripts/backup_world.sh`).
6. **GUI / Console Feedback**: Process output is streamed asynchronously to the GTK 3 UI or emitted with standardized exit codes (`0` success, `1` diagnostic/runtime failure, `2` usage/environment error, `3` nothing to act on).

### 3) Layer/Module Responsibilities

| Layer or module | Owns | Must not own | Evidence |
|-----------------|------|--------------|----------|
| **Presentation Layer** (`scripts/scriptorium_app.py`, `scripts/control_center.sh`) | GTK 3 widgets, async worker thread management, visual scene tag editing, live word count display, desktop notifications | Hardcoded domain logic; synchronous blocking calls on UI thread | [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L100) |
| **CLI Dispatcher** (`scripts/scriptorium`) | Argument parsing, subcommand dispatch, command usage banners | Reimplementing script business logic; running unverified shell code | [`scripts/scriptorium`](file:///scripts/scriptorium#L1-L80) |
| **Discovery Library** (`scripts/lib/worlds.sh`) | Scanning `~/Universes` and `~/Manuscripts`, path resolution, name sanitization, GUI environment detection | Mutating project files; initiating long-running tasks | [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L150) |
| **Core Workflow Engines** (`scripts/*.sh`) | Scaffolding projects, multi-tier Git snapshotting, compilation pipelines, backup/restore drills, diagnostics | GUI toolkit dependencies; hardcoded usernames or absolute paths | [`scripts/init_world.sh`](file:///scripts/init_world.sh#L1-L80), [`scripts/export_book.sh`](file:///scripts/export_book.sh#L1-L100) |
| **Templates & Schemas** (`templates/`) | Obsidian vault configurations, Dataview queries, `fileClasses` schemas, novelWriter project XML stubs, Typst layouts | Shell script execution logic; dynamic user runtime state | [`templates/world-bible/`](file:///templates/world-bible/00_START_HERE.md#L1-L40), [`templates/typst/book_template.typ`](file:///templates/typst/book_template.typ#L1-L50) |

### 4) Reused Patterns

| Pattern | Where found | Why it exists |
|---------|-------------|---------------|
| **Transactional Staging & Atomic Swap** | `init_world.sh`, `init_manuscript.sh`, `backup_world.sh`, `restore_world.sh` | Prevents corrupted or partial project directories if an operation is interrupted mid-execution ([ADR-008](file:///docs/ARCHITECTURE.md#adr-008-transactional-world--manuscript-scaffolding-via-temporary-staging-rel-01)). |
| **Exit-Code Contract (4 Values)** | All `scripts/*.sh` and `scripts/scriptorium` | Guarantees predictable behavior across CLI, GUI wrappers, and automated test runners ([ADR-021](file:///docs/ARCHITECTURE.md#adr-021-re-audit-follow-ups-root-decluttering--authorship-reset)). |
| **Shared Library Sourcing** | All 11 entry-point scripts sourcing `scripts/lib/worlds.sh` | Eliminates duplicated path discovery code and ensures unified universe/world resolution ([ADR-020](file:///docs/ARCHITECTURE.md#adr-020-external-audit-remediation--shared-discovery-library--fail-closed-hardening)). |
| **Fail-Closed Verification** | `setup_scriptorium.sh`, `verify.sh`, `restore_world.sh` | Refuses execution or unverified binary installation when digests or integrity checks fail ([ADR-020](file:///docs/ARCHITECTURE.md#adr-020-external-audit-remediation--shared-discovery-library--fail-closed-hardening), [ADR-023](file:///docs/ARCHITECTURE.md#adr-023-forensic-audit-hardening--fail-closed-security-depth-3-universe-discovery-iso-8601-chronology-and-intra-manuscript-link-resolution)). |
| **Daemon Worker Threading** | `scripts/scriptorium_app.py` (`_start_worker`) | Keeps the GTK 3 desktop UI responsive during long-running builds, exports, or doctor diagnostics ([ADR-020](file:///docs/ARCHITECTURE.md#adr-020-external-audit-remediation--shared-discovery-library--fail-closed-hardening)). |

### 5) Known Architectural Risks

- **Flatpak vs Host Path Isolation Risk**: Sandboxed Flatpak applications (Obsidian, novelWriter, Calibre) require filesystem permissions to access `~/Universes` and `~/Manuscripts`. Default Flatpak configurations grant access to `$HOME`, but custom sandboxing permissions could restrict subfolder reads.
- **Git Concurrency in Obsidian**: Obsidian Git auto-commits every 10 minutes. Concurrent execution of CLI `scripts/save_snapshot.sh` could encounter temporary `.git/index.lock` contention. Mitigated by retry-loop logic in `save_snapshot.sh` ([ADR-009](file:///docs/ARCHITECTURE.md#adr-009-decoupled-standalone-backups-vs-local-git-snapshots-rel-03)).

### 6) Evidence

- [`docs/ARCHITECTURE.md`](file:///docs/ARCHITECTURE.md#L1-L490)
- [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L1575)
- [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L247)
- [`scripts/export_book.sh`](file:///scripts/export_book.sh#L1-L540)
- [`scripts/world_doctor.sh`](file:///scripts/world_doctor.sh#L1-L577)

## Extended Sections (Optional)

### Resilience & Failure Posture

1. **Signal Trapping**: Shell scripts register cleanup traps (`trap cleanup EXIT INT TERM`) to purge temporary staging directories in `/tmp` upon error, abort, or interruption.
2. **Directory Traversal Protection**: `restore_world.sh` inspects archive tarballs prior to extraction to reject malicious entries containing `..` or non-sample git hooks.
3. **Multi-Era Timeline Chronology**: `world_doctor.sh` parses non-Gregorian fantasy eras, astronomical decimal years, and ISO 8601 dates to calculate chronological bounds without numeric casting errors.
