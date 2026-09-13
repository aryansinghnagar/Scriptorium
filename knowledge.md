# Knowledge Base: Scriptorium Technical Ecosystem & Invariants

## 1. Operating System Details
- **Linux Mint XFCE**: Built on Ubuntu LTS base. Uses XFCE desktop environment. Extremely lightweight (idle RAM ~600MB - 900MB), lightning fast, highly customizable, and beginner friendly. Comes with LibreOffice pre-installed and Software Manager supporting both APT and Flatpak out of the box.
- **Debian 13 (Trixie) / 12 (Bookworm) XFCE**: Minimal ultra-stable base. Native Debian package ecosystem with low resource footprint.

## 2. Application Architecture & Interoperability
| Application | Format & Storage | Protocol / Extension | Role |
| :--- | :--- | :--- | :--- |
| **Obsidian** | Local folder of standard `.md` files | Markdown + Wikilinks (`[[Link]]`) | World Bible, Lore, Character & Location Wiki |
| **novelWriter** | Local folder of `.nwd` documents under `content/` + XML index (`.nwx`, fileVersion 1.5) | Markdown with `@tag` metadata | Story outlining, chapter/scene drafting, project stats |
| **FocusWriter** | Plain `.txt` or `.md` | Plaintext | Fullscreen distraction-free draft sprints |
| **LibreOffice Writer** | `.odt`, `.docx` | OpenDocument / Office Open XML | Editor collaboration, redlining, track changes |
| **Calibre** | `.epub`, `.azw3`, `.mobi` | EPUB / Open Container Format | Ebook generation, DRM-free cataloging, e-reader sync |
| **Typst** | `.typ` source files | Typst modern markup | Publication-grade typesetting, micro-typography, print-ready PDF |
| **Pandoc** | Universal markup converter | AST translation | Bridges Markdown manuscript files directly into Typst/EPUB |
| **Déjà Dup** | Duplicity / Restic backend | Encrypted incremental backup archives | Automated local external USB and cloud backups |
| **Git** | Distributed VCS | Local `.git` repository | Version control snapshots and instant rollbacks |
| **Scriptorium Engine** | Shell + Python3 | Standalone CLI & GUI Control Center | Unified management, backup verification, and diagnostics |

## 3. Typst vs. LaTeX for Fiction
- **Compilation Speed**: Typst compiles sub-second (instantaneous) compared to LaTeX's multi-pass builds.
- **Syntax Simplicity**: Typst uses clean, declarative syntax without cryptic LaTeX cascades.
- **Page Layout**: Native support for running headers with chapter titles, alternating recto/verso margins, gutter binding allowances, and custom page numbers.

## 4. novelWriter Markdown Conventions
- Headers: `# Title`, `## Chapter`, `### Scene`, `#### Section`.
- Metadata tags: `@pov: CharacterName`, `@focus: LocationName`, `@plot: PlotPoint`, `@status: Draft / Finished / Revision`, custom tags (`@theme: ...`).
- Tag stripping engine removes all `@tag:` and `%` comment lines during export so they never leak into consumer EPUBs or become unhandled citations in Typst.

## 5. Architectural & Safety Invariants
- **Multi-Tier Git Architecture**: 3-level version control hierarchy:
  1. *Universe Tier* (`~/Universes/<Name>/`): Houses `universe.yaml` and overarching continuity Git repo.
  2. *World Tier* (`~/Universes/<Name>/Worlds/<Name>/` or standalone `~/Worlds/<Name>/`): Houses `00-World-Bible` lore and assets with World Git repo and Obsidian Git auto-commit.
  3. *Manuscript Tier* (`01-Manuscript/<Book>/`): Discrete, isolated Git repo per book for granular revision histories and word-level diffing.
- **Pre-Configured Obsidian Plugin Suite**: Out-of-the-box writing and worldbuilding suite (`templates/world-bible/.obsidian/`):
  - *Longform*: Atomic scene organization and compiled manuscript export.
  - *Dataview*: Dynamic lore querying and relationship rollups (JS & DQL enabled).
  - *Metadata Menu*: Structured YAML validation with strict `fileClasses` (`Character`, `Location`, `Faction`, `TimelineEvent`).
  - *Calendarium*: Custom multi-moon and fantasy calendar systems.
  - *Storyteller Suite* & *Storyline*: Visual narrative graphs and scene beat progression.
  - *Novel Word Count*: Real-time word counts and chapter targets.
  - *Obsidian Git*: Automated background commits (10-minute interval) and backup on save.
- **Transactional Staging**: `init_world.sh` builds in a temporary directory, validates directory schemas and manifests, commits initial Git state, and atomically moves to destination. Intermediate failures leave no orphaned state.
- **Decoupled Data Safety**: Local Git version snapshots (`save_snapshot.sh`) are decoupled from standalone verified archives (`backup_world.sh` tarball + SHA-256 hash manifest). Disaster recovery is verified via `restore_world.sh`.
- **Installer Safety & Gating**: `setup_scriptorium.sh` performs OS distribution detection via `/etc/os-release`, gates unverified distros unless `--force` is passed, supports complete non-destructive `--dry-run` simulation, and provides `uninstall_scriptorium.sh` for rollback.
- **Independent Error Trapping**: Exporter traps Pandoc and Typst independently so that partial compilation outputs are preserved and detailed summaries are surfaced without early `set -e` termination.
- **Domain Diagnostics**: `scriptorium_doctor.sh` and `world_doctor.sh` enforce entity schema requirements, broken link resolution, duplicate alias collision detection, and timeline chronological consistency (`WLD-101` through `WLD-107`).
- **Unified Interface**: `scriptorium <command>` CLI dispatcher and `scriptorium-control-center.desktop` GUI provide unified access for terminal and desktop users alike.

