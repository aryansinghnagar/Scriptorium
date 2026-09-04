# Implementation Plan & Operational Roadmap: Scriptorium

## 1. Architectural Overview
The Scriptorium environment is organized into modular tiers:
1. **Core Documentation & Resource Catalog**: Links, commands, installation methods (Apt, Flatpak, AppImage, Python), and checksums.
2. **Automated Setup & Provisioning**: Single-command setup script (`setup_scriptorium.sh`) that provisions the complete OS environment, packages, and dependencies.
3. **World Directory Hierarchy & Starter Assets**: Automated generator (`init_world.sh`) that creates the canonical `~/Worlds/<WorldName>` structure with Obsidian vaults, templates, and novelWriter starter projects.
4. **Obsidian World Bible Suite**: Production-grade Markdown templates for characters, factions, locations, magic/tech systems, history, conlangs, and index pages with Dataview metadata.
5. **novelWriter Manuscript Structure**: Pre-configured chapter/scene hierarchies with metadata tags and outline templates.
6. **Book Export & Typesetting Engine**: Pandoc + Typst compilation pipeline (`export_book.sh`, `book_template.typ`, `export-book.desktop`) producing print-ready PDFs and EPUBs.
7. **Version History & Data Protection**: One-click Git snapshotting (`save_snapshot.sh`, `save-snapshot.desktop`) and Déjà Dup automated backup configurations.
8. **Distraction Control & Notification Management**: Ready-to-import LeechBlock NG configuration files and XFCE Do-Not-Disturb configurations.

## 2. Milestone Phases
- [x] **Phase 1: Canonical State & Specification**: Define project charter, roadmaps, task lists, and architectural records.
- [x] **Phase 2: Comprehensive Resource & Software Catalog**: Document exact software sources, Flatpak/Apt IDs, ISO download hubs, and optional creative extras.
- [x] **Phase 3: System Automation Scripts & Desktop Launchers**: Implement `setup_scriptorium.sh`, `init_world.sh`, `export_book.sh`, `save_snapshot.sh`, and `.desktop` launchers.
- [x] **Phase 4: Obsidian Vault & novelWriter Templates Pack**: Build complete worldbuilding templates with Dataview attributes and Markdown manuscript starters (nwProject.nwx is a documented placeholder; real project created via novelWriter GUI).
- [x] **Phase 5: Typst Typesetting Engine & Book Templates**: Develop high-end typographic book template in Typst with headers, margins, and Pandoc bridge (context-based headers, front-matter header suppression).
- [x] **Phase 6: Distraction Control & Backup Guides**: Generate LeechBlock JSON config and Déjà Dup runbooks (LeechBlock import must be live-verified on Firefox).
- [ ] **Phase 7: Master Documentation & Live Verification**: `README.md` synthesized; `bash -n` + Pandoc smoke test pass via `scripts/verify.sh` (Windows/Git Bash). Remaining Linux-only: `shellcheck`, `typst compile preview_sample.typ`, LeechBlock import, novelWriter project creation, full `setup_scriptorium.sh` run — see `Finishing_Touches.md`.
