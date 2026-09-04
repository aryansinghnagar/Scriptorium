# Project Charter: Scriptorium — A Simple Linux Writing Setup

## 1. Executive Summary
Scriptorium is a purpose-built, distraction-free, low-effort writing and worldbuilding environment designed for authors, novelists, and worldbuilders running Linux (primarily Linux Mint XFCE edition or Debian 13 XFCE). It emphasizes open formats (plain Markdown), minimal system management overhead, ironclad data safety (full-disk encryption + 3-2-1 automated backups), and publication-ready typesetting using modern tools (Typst, Pandoc, novelWriter, Obsidian, Calibre, FocusWriter).

## 2. Core Philosophy & Design Invariants
1. **Plain Text & Open Formats First**: Every word, outline, character sheet, and chapter is stored in standard Markdown and plain text files. No proprietary lock-in.
2. **One Tool Per Creative Stage**:
   - *World Bible / Local Wiki*: **Obsidian** (with Dataview, Templater, Kanban, Excalidraw).
   - *Outlining & Drafting*: **novelWriter** (structured project hierarchy, plain Markdown storage, focus mode).
   - *Deep Focus Sessions*: **FocusWriter** (full-screen distraction-free canvas).
   - *Revisions / Word Processing*: **LibreOffice Writer** (standard `.docx`/`.odt` track changes with editors).
   - *Ebook Compilation*: **Calibre** (EPUB generation and inspection).
   - *Typesetting & Print PDF*: **Typst + Pandoc** (modern typographic engine producing Vellum-quality print PDFs).
3. **Zero Terminal Requirement for Daily Work**: Every daily action (writing, snapshotting, exporting, backing up) is executable via GUI desktop launchers and intuitive interfaces.
4. **Targeted Distraction Filtering**: Keep full browser capability for research, but enforce automated site blocking (LeechBlock NG) during designated writing hours and activate XFCE Do Not Disturb mode.
5. **Multi-Layer Data Protection**: Full-disk LUKS encryption, automated weekly Déjà Dup backups to external drives, and one-click Git snapshots.

## 3. Hardware & OS Baseline
- **Reference Platform**: Intel Core i5-1335U, 16 GB RAM, Iris Xe Graphics, NVMe SSD, dual-boot with Windows.
- **Primary Operating System**: Linux Mint (XFCE Edition, 64-bit).
- **Secondary / Minimal Alternative**: Debian 13 (Trixie) XFCE.

## 4. Non-Goals (explicitly out of scope)
- No custom distribution or remastered ISO — stock Mint/Debian only.
- No per-app sandboxing profiles, Secure Boot key management, or USB device policies — LUKS + backups are the safety story.
- No cloud sync or collaboration service — local Git + external-drive backups only.
- No mobile companion workflow.

## 5. Constraints & Assumptions
- Target CPU is x86_64; ARM (aarch64) is supported for Typst via `setup_scriptorium.sh` arch detection but otherwise untested.
- Daily work must be GUI-only (XFCE panel, desktop launchers, Zenity dialogs on X11 and Wayland). Terminal is acceptable for one-time setup and verification (`scripts/verify.sh`).
- `templates/manuscript/nwProject.nwx` is a documented placeholder: real novelWriter projects (fileVersion 1.5, `content/*.nwd`) are created via the novelWriter GUI. The Markdown starters under `Book-01/` are the source of truth for `export_book.sh`.
- LeechBlock NG export formats vary by version; `configs/leechblock_scriptorium_rules.json` is a specification that must be live-verified on Firefox (see `Finishing_Touches.md` §6).

## 6. Definition of Done
- `bash scripts/verify.sh` prints `ALL-CHECKS-PASS` on Linux Mint XFCE.
- `typst compile templates/typst/preview_sample.typ` produces a paginated PDF with clean front matter and running headers.
- A test world scaffolds, exports (PDF + EPUB), and snapshots without terminal interaction.
- LeechBlock rules import (or are manually recreated) and block during writing hours.
