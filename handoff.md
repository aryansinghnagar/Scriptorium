# Ars Arcanum (Scriptorium) — Agent Continuation & Handoff State

## Current Milestone State
- **Completed**: Phases 0 through 20 (137/137 milestones). All trimming, modernization, engine expansions, and documentation milestones complete.
- **Active Branch/Workspace**: Main workspace `c:\Users\Aryan\OneDrive\Desktop\Coding Projects\7-Scriptorium`.
- **Release Version**: `v4.0.0` — Grade A+ Sovereign Authoring Operating System (GPA 4.0/4.0).
- **Test Baseline**: **681 tests collected, 681 passing, 2 skipped, 0 failures** (`python -m unittest discover tests`).
- **Linter Baseline**: `ruff check .` **100% Clean (0 violations)** across expanded rule suite (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`).
- **Static Typing**: `mypy` strict type checking passing across all 70 `scripts/lib` modules and test suites (`tests/test_type_safety.py`).
- **Security Baseline**: Path traversal defense (`validate_volume_name`), GPG AES-256 backup encryption, Bandit SAST scanner in CI.

---

## Architecture & Codebase Summary
1. **Core Dispatcher & CLI**: Pure Python modular CLI dispatcher in `scripts/lib/cli.py` + canonical POSIX bootstrap `scripts/arcanum` with built-in subroutines and smart typo suggestions.
2. **Modular GUI**: GTK3 Control Center decomposed into `scripts/lib/ui_gtk3/` package (`window.py`, `studios/`, `dialogs.py`, `workers.py`, `cli_bridge.py`, `common.py`) and modern Libadwaita interface (`ui_adw.py`).
3. **Sovereignty & Privacy**: 100% offline, zero external pip dependencies, pure standard library OpenXML (`docx_sync.py`), Pandoc/Typst export, atomic writes (`atomic_write`).
4. **Data Protection & Interop**: Multi-tier Git repositories (`.gitmodules`), automated background backups with SHA-256 stream integrity, GPG symmetric/asymmetric encryption, cross-platform file locking (`lockfile.py`), and universal JSONL/SQLite corpus exporter with bidirectional vault restore.
5. **Craft & Simulation Engines**: 70 typed modules in `scripts/lib/` covering astrophysics (eyeball/brown dwarf worlds), climate & Köppen biomes, multi-calendar chronology, interactive cartography, Multi-POV narrative subway graphs, conlang phonetics, fuzzy genealogy, causal DAG time-travel validation, and 11+ advisory story structure models.
6. **Author Documentation & Blueprint**: Master architecture reference in `docs/ARCHITECTURE.md`, 21-stage E2E Grand Tour manual in `docs/GRAND_TOUR.md`, and 1-page cheatsheet in `docs/CHEATSHEET.md`.

---

## Invariants & Guardrails
- **Zero-Pip Guarantee**: Core authoring functionality requires only Python standard library + optional PyGObject.
- **Crash Resistance**: Atomic file writes (`atomic_write`) prevent file corruption during power outages or process kills.
- **Strict Path Defense**: Volume, world, and draft names must strictly match `^[A-Za-z0-9_-]+$`.
- **Architectural ADR Log**: ADR-001 through ADR-114 recorded in `decisions.md`.
