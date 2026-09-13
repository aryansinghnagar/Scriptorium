# Project Charter: Scriptorium — A Simple Linux Writing Setup

## 1. Executive Summary
Scriptorium is a purpose-built, distraction-free, low-effort writing and worldbuilding environment designed for authors, novelists, and worldbuilders running Linux (primarily Linux Mint XFCE edition or Debian 13/12 XFCE). It emphasizes open formats (plain Markdown), minimal system management overhead, ironclad data safety (full-disk encryption + 3-2-1 automated backups + verified restores), and publication-ready typesetting using modern tools (Typst, Pandoc, novelWriter, Obsidian, Calibre, FocusWriter).

## 2. Core Philosophy & Design Invariants
1. **Plain Text & Open Formats First**: Every word, outline, character sheet, and chapter is stored in standard Markdown and plain text files. No proprietary lock-in.
2. **One Tool Per Creative Stage**:
   - *World Bible & Local Wiki*: **Obsidian** (pre-configured with Longform, Dataview, Metadata Menu 9 `fileClasses` schemas: Character, Location, Faction, TimelineEvent, Creature, Artifact, Cosmology, MagicSystem, Language; Calendarium, Storyteller Suite, Storyline, Novel Word Count, and Obsidian Git).
   - *Outlining & Drafting*: **novelWriter** or **Obsidian Longform** (structured project hierarchy, plain Markdown storage, multi-volume `add-book` scaffolding, atomic scene compilation, focus mode).
   - *Deep Focus Sessions*: **FocusWriter** (full-screen distraction-free canvas).
   - *Revisions / Word Processing*: **LibreOffice Writer** (standard `.docx`/`.odt` track changes with editors).
   - *Ebook Compilation*: **Calibre** (EPUB generation, cover art inspection, and e-reader sync).
   - *Typesetting & Print PDF*: **Typst + Pandoc** (modern typographic engine producing Vellum-quality print PDFs with trade trim size options: us-trade, trade, pocket).
3. **Zero Terminal Requirement for Daily Work**: Every daily action (writing, snapshotting, exporting, backing up, diagnostics, universe/world creation) is executable via native GTK 3 desktop UI (`scriptorium_app.py`), desktop launchers, Zenity dialog fallbacks, and the comprehensive visual Author's Field Manual (`docs/AUTHOR_MANUAL.md`).
4. **Targeted Distraction Filtering**: Keep full browser capability for research, but enforce automated site blocking (LeechBlock NG) during designated writing hours and activate XFCE Do Not Disturb mode.
5. **Multi-Layer Data Protection & Version Control**: Multi-tier Git version control (Universe, World with Obsidian Git auto-commits, discrete Manuscript repos), standalone verified archive backups (`backup_world.sh` / `restore_world.sh`), full-disk LUKS encryption, and automated external Déjà Dup backups.

## 3. Hardware & OS Baseline
- **Reference Platform**: Intel Core i5-1335U, 16 GB RAM, Iris Xe Graphics, NVMe SSD, dual-boot with Windows.
- **Primary Operating System**: Linux Mint (XFCE Edition, 64-bit, v21.x / v22.x).
- **Secondary / Minimal Alternative**: Debian 13 (Trixie) / 12 (Bookworm) XFCE.
- **Supported Architecture**: x86_64 (Tier 1) and aarch64 (Tier 2).

## 4. Non-Goals (explicitly out of scope)
- No custom distribution or remastered ISO — stock Mint/Debian only.
- No per-app sandboxing profiles, Secure Boot key management, or USB device policies — LUKS + backups are the safety story.
- No mandatory cloud sync or third-party locking service — local multi-tier Git + external-drive backups only.
- No mobile companion workflow.

## 5. Constraints & Assumptions
- Daily work can be GUI-only (Python 3/GTK 3 Control Center, XFCE panel, desktop launchers, Zenity dialogs on X11 and Wayland) or CLI-driven via the unified `scriptorium` entrypoint.
- World initialization is strictly transactional: staged in temporary space, validated, and atomically moved into `~/Universes/<Universe>/Worlds/<name>` or `~/Worlds/<name>`.
- Multi-tier Git version control is automatically established during creation: Universe repo tracks high-level continuity, World repo tracks lore/assets with Obsidian Git, and individual Book folders receive isolated Git repos for granular manuscript revision histories.
- novelWriter projects (`nwProject.nwx`) conform to valid fileVersion 1.5 XML schema while Markdown chapter files under `Book-*` serve as the source of truth for Pandoc, Typst, and Longform.

## 6. Definition of Done
- `bash scripts/verify.sh` prints `ALL-CHECKS-PASS` across all 7 verification stages.
- `python3 -m py_compile scripts/scriptorium_app.py` compiles without syntax errors.
- `docs/AUTHOR_MANUAL.md` provides visual, plain-English guidance for all creative and technical workflows.
- `typst compile templates/typst/preview_sample.typ` produces a paginated PDF with clean front matter, ornamental scene breaks, and running headers.
- A test universe and world scaffold, export (PDF + EPUB), record multi-tier Git snapshots, and complete verified backup & restore drill without data loss.
- Zero warnings under `shellcheck -S warning scripts/*.sh scripts/scriptorium`.
