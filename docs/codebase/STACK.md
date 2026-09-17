# Technology Stack

## Core Sections (Required)

### 1) Runtime Summary

| Area | Value | Evidence |
|------|-------|----------|
| Primary language | Shell (POSIX / Bash 4+) & Python (3.10+) | [`scripts/scriptorium`](file:///scripts/scriptorium#L1-L2), [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L2), [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L2) |
| Runtime + version | Bash `>= 4.3` (tested on 5.x) & Python `>= 3.10.0` (tested on 3.12.x) | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L9-L16), [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L20) |
| Package manager | APT (`apt-get`) for core binaries/fonts + Flathub Flatpak (`flatpak`) for sandboxed GUI desktop apps | [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L130-L240), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L24-L37) |
| Module/build system | POSIX Shell modular sourcing (`scripts/lib/worlds.sh`), Typst (`0.13.0` pinned), and Pandoc (`3.1.x`/`2.19.x`) | [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L20), [`scripts/export_book.sh`](file:///scripts/export_book.sh#L1-L30), [`templates/typst/book_template.typ`](file:///templates/typst/book_template.typ#L1-L20) |

### 2) Production Frameworks and Dependencies

List only high-impact production dependencies (frameworks, data, transport, auth).

| Dependency | Version | Role in system | Evidence |
|------------|---------|----------------|----------|
| **PyGObject / GTK 3** | `3.42+` (GTK `3.24+`) | Native GUI desktop Control Center with 5-tab author workflow and Visual Scene Metadata Inspector | [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L35), [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L106-L130) |
| **Zenity** | `>= 3.32.0` (tested `3.44.x`) | Fallback lightweight graphical dialogs for terminal/desktop launcher scripts | [`scripts/control_center.sh`](file:///scripts/control_center.sh#L1-L30), [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L40-L45) |
| **Typst** | `0.13.0` pinned (musl binary) | Sub-second, modern typographic typesetting engine compiling Markdown manuscripts into print-ready trade PDFs | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L9-L21), [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L210-L270), [`scripts/export_book.sh`](file:///scripts/export_book.sh#L340-L420) |
| **Pandoc** | `>= 2.16.0` (tested `3.1.x`/`2.19.x`) | Universal document conversion engine bridging Markdown into Typst, EPUB, and submission DOCX | [`scripts/export_book.sh`](file:///scripts/export_book.sh#L190-L330), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L9-L16) |
| **Obsidian** | `md.obsidian.Obsidian` (Flathub stable) | Local-first Markdown World Bible and lore repository with pre-configured plugin suite | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L28-L32), [`templates/world-bible/.obsidian/`](file:///templates/world-bible/.obsidian/community-plugins.json#L1-L15) |
| **novelWriter** | `io.gitlab.novelwriter.novelWriter` (Flathub stable) | Structured manuscript editor, chapter/scene tree organizer, and focus drafting tool | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L28-L32), [`templates/manuscript/nwProject.nwx`](file:///templates/manuscript/nwProject.nwx#L1-L15) |
| **Calibre** | `com.calibre_ebook.calibre` (Flathub stable) | Graphical EPUB inspection, metadata validation, and e-reader synchronization | [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L28-L32), [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L142-L209) |
| **FocusWriter** | `fonts-linuxlibertine` / Flatpak | Distraction-free full-screen drafting canvas | [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L123-L130), [`docs/guides/DISTRACTION_CONTROL.md`](file:///docs/guides/DISTRACTION_CONTROL.md#L30-L34) |
| **LibreOffice Writer** | `libreoffice-writer` | Professional editorial collaboration, redlining, and track changes | [`docs/guides/SOFTWARE_CATALOG.md`](file:///docs/guides/SOFTWARE_CATALOG.md#L66-L74) |
| **Git** | `>= 2.34.0` (tested `2.43.x`) | Distributed version control engine powering multi-tier snapshots, auto-commits, and milestone tags | [`scripts/save_snapshot.sh`](file:///scripts/save_snapshot.sh#L1-L40), [`docs/ARCHITECTURE.md`](file:///docs/ARCHITECTURE.md#L261-L288) |
| **LeechBlock NG** | `1.5.2` (Firefox WebExtension) | Scheduled distraction blocking during writing blocks | [`configs/leechblock_scriptorium_rules.json`](file:///configs/leechblock_scriptorium_rules.json#L1-L25), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L56-L62) |

### 3) Development Toolchain

| Tool | Purpose | Evidence |
|------|---------|----------|
| **ShellCheck** (`0.9.x`/`0.10.x`) | Static analysis and linting for all shell scripts (`-S warning`) | [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L28-L36), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L16) |
| **Python py_compile / Syntax Check** | Static bytecode compilation validation for `scripts/scriptorium_app.py` | [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L37-L40), [`scripts/verify.sh`](file:///scripts/verify.sh#L27-L33) |
| **Bash Syntax Validator (`bash -n`)** | Syntax integrity verification across all shell scripts, libraries, and CLI entry points | [`scripts/verify.sh`](file:///scripts/verify.sh#L18-L26), [`CONTRIBUTING.md`](file:///CONTRIBUTING.md#L55-L63) |
| **Custom 7-Stage Verification Harness (`verify.sh`)** | Full end-to-end integration, schema, lifecycle, snapshot, and backup/restore verification | [`scripts/verify.sh`](file:///scripts/verify.sh#L1-L496), [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L45-L55) |
| **Targeted Regression Suites (`tests/*.sh`)** | Targeted edge-case tests for forensic fixes, concordance engine, multi-era chronology, and discovery | [`tests/test_audit_fixes.sh`](file:///tests/test_audit_fixes.sh#L1-L331), [`tests/test_deep_audit.sh`](file:///tests/test_deep_audit.sh#L1-L125), [`tests/test_concordance_edge_cases.sh`](file:///tests/test_concordance_edge_cases.sh#L1-L200), [`tests/test_audit_claude_improvements.sh`](file:///tests/test_audit_claude_improvements.sh#L1-L120) |

### 4) Key Commands

```bash
# Automated setup installer (provisions packages, fonts, Typst musl, desktop launchers)
bash scripts/setup_scriptorium.sh

# Dry-run installation simulation (inspects actions without root changes)
bash scripts/setup_scriptorium.sh --dry-run

# Run primary 7-stage quality verification harness
bash scripts/verify.sh

# Run targeted test suites
bash tests/test_audit_fixes.sh
bash tests/test_deep_audit.sh
bash tests/test_concordance_edge_cases.sh
bash tests/test_audit_claude_improvements.sh

# Lint shell scripts and compile Python app
shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/scriptorium
python3 -m py_compile scripts/scriptorium_app.py

# Launch native GTK 3 Desktop Control Center
./scripts/scriptorium control-center
# Or directly:
python3 scripts/scriptorium_app.py
```

### 5) Environment and Config

- **Config sources**:
  - `configs/leechblock_scriptorium_rules.json` — LeechBlock NG export rules for focus hours.
  - `templates/world-bible/.obsidian/` — Obsidian app, core, community plugin, and plugin configuration files.
  - `templates/world-bible/Templates/fileClasses/` — Metadata Menu 9 structured entity schemas.
  - `templates/manuscript/nwProject.nwx` — novelWriter project template XML (`fileVersion 1.5`).
  - `.editorconfig` — Repository formatting and whitespace standards.
  - `universe.yaml`, `world.yaml`, `manuscript.yaml` — Flat YAML project manifests.
- **Required env vars**:
  - `HOME` — User home directory for finding `~/Universes`, `~/Manuscripts`, and `~/.local/share/applications` (sandboxed in test harnesses).
  - `DISPLAY` / `WAYLAND_DISPLAY` — GUI display server handles for GTK 3 and Zenity (gracefully degraded to headless/CLI when unset).
  - `XDG_DATA_HOME` / `XDG_CONFIG_HOME` — Standard XDG directory resolution paths.
- **Deployment/runtime constraints**:
  - Primary OS: Linux Mint 21/22 XFCE edition and Debian 12/13 XFCE (`x86_64` Tier 1, `aarch64` Tier 2).
  - Requires standard Linux utility packages: `bash`, `coreutils`, `tar`, `gzip`, `sha256sum`, `git`, `python3`, `zenity`, `typst`, `pandoc`.

### 6) Evidence

- [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L1-L343)
- [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L1-L62)
- [`docs/SUPPORT_MATRIX.md`](file:///docs/SUPPORT_MATRIX.md#L1-L47)
- [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L1-L105)
- [`scripts/verify.sh`](file:///scripts/verify.sh#L1-L496)

## Extended Sections (Optional)

### Full Dependency Taxonomy by Category

1. **System & Desktop Integration**:
   - `python3-gi`, `gir1.2-gtk-3.0`: GTK 3 PyGObject introspection bindings.
   - `zenity`: Lightweight GTK dialog engine for CLI scripts.
   - `libnotify-bin`: Desktop notification engine (`notify-send`).
   - `xdg-utils`: Desktop environment integration and default file opener.
2. **Typesetting & Document Processing**:
   - `typst` (musl precompiled binary, GitHub release asset with SHA-256 validation): Novel PDF typesetting engine.
   - `pandoc`: Markdown AST bridge to Typst, EPUB, and submission `.docx`.
   - `fonts-linuxlibertine`, `fonts-libertinus`, `fonts-ebgaramond`, `fonts-alegreya`, `fonts-sil-charis`, `fonts-sil-gentiumplus`, `fonts-bitter`, `fonts-cmu`: Standard open-source publishing fonts.
3. **Core Author Applications (Flatpak / APT)**:
   - `md.obsidian.Obsidian`: World Bible markdown wiki.
   - `io.gitlab.novelwriter.novelWriter`: Structural manuscript drafting.
   - `com.calibre_ebook.calibre`: Ebook inspection and formatting.
   - `focuswriter`: Fullscreen distraction-free draft canvas.
   - `libreoffice-writer`: Editorial collaboration and revision tracking.
4. **Data Protection & Versioning**:
   - `git`: Multi-tier version control snapshotting.
   - `tar`, `gzip`, `sha256sum`: Standalone backup archive creation and verification.
   - `deja-dup`, `duplicity`: Automated encrypted offsite 3-2-1 backups.
