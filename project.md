# Ars Arcanum (Scriptorium) — Project Charter & System Architecture

## 1. Executive Summary & North Star
**Ars Arcanum** (repository: `Scriptorium`) is a sovereign, local-first, privacy-respecting speculative fiction authoring and worldbuilding operating platform designed for Linux. It orchestrates plain Markdown prose, OpenXML (`.docx`) bidirectional synchronization, multi-tier Git repository version tracking, deep worldbuilding simulation engines, automated Dramatis Personae concordance indexing, and publication-grade Typst PDF/EPUB compilation.

The North Star is total author data sovereignty:
- **Zero Telemetry**: Completely offline-first with strict `default-src 'none'` Content Security Policies.
- **Plain-Text Durability**: Plain Markdown and YAML format foundation that will remain readable for decades without proprietary lock-in.
- **Fail-Closed Security**: Cryptographic verification of all external dependencies and strict non-destructive backups.

---

## 2. Runtime Capability & Environment Profile
- **Target OS**: Linux Mint 21/22 XFCE, Debian 12/13 XFCE (Tier-1); Fedora / Arch / openSUSE (Tier-2).
- **Architecture**: POSIX shell orchestration (`scripts/arcanum`, `scripts/*.sh`), pure Python standard-library computational engines (`scripts/lib/*.py`), GTK 3 desktop interface (`scripts/lib/ui_gtk3.py`), and standard Linux desktop packaging (`debian/`, `org.arsarcanum.ArsArcanum.yaml`).
- **External Toolchain**:
  - **Git** ($\ge 2.34$): Version tracking and snapshotting.
  - **Pandoc** ($\ge 2.19$): Markdown $\leftrightarrow$ OpenXML (`.docx`) conversion.
  - **Typst** (`0.14.2` musl pinned): Publication-grade typography and sub-second PDF compilation.
  - **jq & Zenity**: Shell JSON processing and graphical dialog prompts.
  - **Obsidian & novelWriter**: Optional authoring frontend integrations.

---

## 3. Core Architectural Invariants
1. **POSIX Crash-Safety & Atomic I/O**: Every file write uses atomic replacement (`mkstemp` $\to$ `flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent directory `fsync`).
2. **Deterministic Rails**: Strict exit-code contracts (0: Success, 1: Operational failure, 2: Environment failure, 3: Argument failure). Shell scripts enforce `set -euo pipefail`.
3. **Golden-Value Domain Verification**: Astrophysics, orbital mechanics, Lanchester warfare models, and relativistic calculations are validated against peer-reviewed scientific references with cited formulas and tolerance assertions.
4. **Isolated Memory & Storage**: Project vaults separate narrative prose (`~/Manuscripts/`) from world lore bibles (`~/Universes/`) per ADR-022.
