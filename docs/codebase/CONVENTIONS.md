# Coding Conventions

## Core Sections (Required)

### 1) Naming Rules

| Item | Rule | Example | Evidence |
|------|------|---------|----------|
| **Files (Shell)** | `snake_case.sh` with `.sh` suffix (except root CLI `scriptorium`) | `init_universe.sh`, `save_snapshot.sh` | [`scripts/init_universe.sh`](file:///scripts/init_universe.sh#L1-L10) |
| **Files (Python)** | `snake_case.py` with `.py` suffix | `scriptorium_app.py` | [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L10) |
| **Files (Launchers)** | `kebab-case.desktop` | `scriptorium-control-center.desktop` | [`launchers/scriptorium-control-center.desktop`](file:///launchers/scriptorium-control-center.desktop#L1-L10) |
| **Files (Templates)** | `Pascal-Case-Hyphenated.md` | `Character-Template.md`, `Timeline-Event-Template.md` | [`templates/world-bible/Characters/`](file:///templates/world-bible/Characters/Character-Template.md#L1-L10) |
| **Functions (Shell)** | `snake_case` | `discover_worlds()`, `warn_if_legacy_root()` | [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L53-L77) |
| **Methods (Python)** | `snake_case` (private prefixed with `_`) | `_on_export_clicked()`, `_refresh_scene_list()` | [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L500-L600) |
| **Classes (Python)** | `PascalCase` | `ScriptoriumApp`, `SceneMetadataDialog` | [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L40-L60) |
| **Constants & Envs** | `UPPER_SNAKE_CASE` | `SCRIPT_DIR`, `EXIT_STATUS`, `TYPST_ARCH` | [`scripts/export_book.sh`](file:///scripts/export_book.sh#L10-L35) |

### 2) Formatting and Linting

- **Formatter**: [`.editorconfig`](file:///.editorconfig#L1-L15) specifying UTF-8, line feed (`\n`), trailing whitespace removal, final newline insertion, tabs for shell scripts (`indent_style = tab`, `tab_width = 4`), and 4 spaces for Python/YAML.
- **Linter (Shell)**: ShellCheck enforcing zero warnings (`shellcheck -S warning`).
- **Linter (Python)**: Bytecode compilation (`python3 -m py_compile`).
- **Most relevant enforced rules**:
  1. Quoting all variable expansions (`"$VAR"`) to prevent word splitting and globbing.
  2. Safe positional argument extraction avoiding unquoted expansions.
  3. No string interpolation across shell/Python boundaries (data passed via `stdin` or `sys.argv`).
- **Run commands**:
  ```bash
  # Check shell syntax
  bash -n scripts/*.sh scripts/lib/*.sh scripts/scriptorium
  # Lint shell code
  shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/scriptorium
  # Validate Python compilation
  python3 -m py_compile scripts/scriptorium_app.py
  ```

### 3) Import and Module Conventions

- **Import grouping/order (Python)**:
  1. Standard library imports (`os`, `sys`, `re`, `shutil`, `subprocess`, `threading`, `datetime`, `pathlib`).
  2. PyGObject / GTK imports (`gi`, `gi.require_version("Gtk", "3.0")`, `from gi.repository import Gtk, GLib, Gdk, Pango`).
- **Shell library sourcing**:
  - Scripts dynamically compute directory: `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`.
  - Shared library is sourced relative to script directory: `source "${SCRIPT_DIR}/lib/worlds.sh"`.
- **Public exports/barrel policy**:
  - `scripts/lib/worlds.sh` exports canonical discovery and UI helper functions: `discover_universes`, `discover_worlds`, `discover_manuscripts`, `resolve_universe_dir`, `resolve_world_dir`, `resolve_manuscript_dir`, `universe_label`, `warn_if_legacy_root`, `sanitize_name`, `has_gui`.

### 4) Error and Logging Conventions

- **Standard 4-Value Exit Code Contract**:
  - `0`: Success — requested operation completed cleanly.
  - `1`: Runtime or diagnostic failure — operation ran but failed, or diagnostic pass found issues.
  - `2`: Usage or environment error — bad command line argument, unknown world name, unsupported OS.
  - `3`: Nothing to act on — clean working tree (no changes to snapshot), required argument missing in headless mode, or user aborted dialog.
- **Logging style**:
  - Prefix logs with recognizable category markers: `[INFO]`, `[OK]`, `[WARN]`, `[ERROR]`, `[STAGE]`.
  - In GTK UI, stream command stdout/stderr to the tab log view in real time.
- **Sensitive-data redaction rules**:
  - Never hardcode usernames, home paths, tokens, or personal identifiers.
  - Scriptorium scripts resolve user paths dynamically using `$HOME`.

### 5) Testing Conventions

- **Test file naming & placement**:
  - Test suites reside in `tests/` named `test_<feature_or_audit>.sh` (e.g. `tests/test_audit_fixes.sh`, `tests/test_deep_audit.sh`).
  - Fixtures reside in `tests/fixtures/` (`sample_universe/`, `sample_world/`, `sample_manuscript/`).
- **Mocking & Isolation strategy**:
  - Tests create isolated temporary homes: `TEST_HOME="$(mktemp -d)"` and export `HOME="${TEST_HOME}"`.
  - Unset `DISPLAY` and `WAYLAND_DISPLAY` during automated tests to guarantee headless CLI execution.
  - Cleanup registered via `trap 'rm -rf "${TEST_HOME}"' EXIT INT TERM`.
- **Coverage expectation**:
  - All 5 test suites must pass 100% cleanly without errors before commits or PR merges.

### 6) Evidence

- [`CONTRIBUTING.md`](file:///CONTRIBUTING.md#L8-L75)
- [`.editorconfig`](file:///.editorconfig#L1-L15)
- [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L25-L65)
- [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L80)
- [`scripts/verify.sh`](file:///scripts/verify.sh#L1-L80)

## Extended Sections (Optional)

### Conventional Commit Conventions

Scriptorium follows Conventional Commits with atomic scopes:
- `feat(concordance): implement automated dramatis personae generator`
- `fix(export): handle unquoted paths in pandoc bridge`
- `docs(manual): expand scene metadata inspector instructions`
- `ci(infra): add ShellCheck linting for test suites`
