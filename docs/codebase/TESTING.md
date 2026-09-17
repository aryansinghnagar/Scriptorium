# Testing Patterns

## Core Sections (Required)

### 1) Test Stack and Commands

- **Primary test framework**: Custom Shell Test Harnesses with sub-process sandboxing, assertion helpers, and Python bytecode compilation tests.
- **Assertion/mocking tools**: Custom Bash assertions (`assert_eq`, `assert_file_exists`, exit code checks), sandboxed temporary directories (`mktemp -d`), `export HOME=...`, mock binaries, and Python YAML/XML parsers.
- **Commands**:

```bash
# 1. Run all test suites in sequence
bash scripts/verify.sh
bash tests/test_audit_fixes.sh
bash tests/test_deep_audit.sh
bash tests/test_concordance_edge_cases.sh
bash tests/test_audit_claude_improvements.sh

# 2. Run core 7-stage quality and regression harness
bash scripts/verify.sh

# 3. Run targeted edge case tests
bash tests/test_concordance_edge_cases.sh
bash tests/test_audit_fixes.sh

# 4. Run static syntax & linting checks
bash -n scripts/*.sh scripts/lib/*.sh scripts/scriptorium
shellcheck -S warning scripts/*.sh scripts/lib/*.sh scripts/scriptorium
python3 -m py_compile scripts/scriptorium_app.py
```

### 2) Test Layout

- **Test file placement pattern**: Dedicated `tests/` directory at the repository root containing test scripts and mock data fixtures.
- **Naming convention**: `test_<focus_area>.sh` (e.g. `test_audit_fixes.sh`, `test_deep_audit.sh`, `test_concordance_edge_cases.sh`, `test_audit_claude_improvements.sh`).
- **Setup files and where they run**:
  - `tests/fixtures/sample_universe/`: Mock universe with `universe.yaml` and `Universe-Index.md`.
  - `tests/fixtures/sample_world/`: Mock world lore vault with `world.yaml`, character notes, and locations.
  - `tests/fixtures/sample_manuscript/`: Mock manuscript project with `manuscript.yaml`, `Book-01`, `Book-02`, and `nwProject.nwx`.

### 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|-------|----------|----------------|-------|
| **Unit / Syntax** | Yes | Script syntax (`bash -n`), ShellCheck linting, Python compilation (`py_compile`), XML validation | Runs in Stage 1 & 2 of `verify.sh` and CI. |
| **Integration** | Yes | Scriptorium CLI dispatching (`scriptorium`), shared discovery (`lib/worlds.sh`), `setup.sh` and `uninstall.sh` dry-runs | Tests CLI arguments, options forwarding, and dry-run execution. |
| **E2E / Lifecycle** | Yes | Universe, World, and Manuscript creation, multi-volume scaffolding (`add-volume`), back-matter concordance, and Git snapshotting | Fully scaffolds sample projects in sandboxed `$HOME` and verifies structure. |
| **Disaster Recovery** | Yes | `backup_world.sh` archive generation and `restore_world.sh` drill | Compresses test projects, calculates SHA-256 digests, restores to clean folder, and verifies file parity. |
| **Diagnostics & Rules** | Yes | `world_doctor.sh` (multi-era timeline paradoxes, `WLD-108` lore drift), `scriptorium_doctor.sh` | Injects valid and broken timeline events to prove detection triggers. |

### 4) Mocking and Isolation Strategy

- **Main mocking approach**:
  - Sandboxed user environment: Every test harness assigns `TEST_HOME="$(mktemp -d)"` and sets `export HOME="${TEST_HOME}"`.
  - Headless execution guarantee: Tests explicitly unset `DISPLAY` and `WAYLAND_DISPLAY` to ensure CLI and headless fallback logic is exercised.
  - Mock external binaries: Tests create dummy scripts in a temporary `$PATH` to simulate environments where optional tools (like `typst` or `pandoc`) are missing.
- **Isolation guarantees**: All temporary directories, files, and Git repositories are scoped within `TEST_HOME` and destroyed on test exit via shell traps:
  ```bash
  trap 'rm -rf "${TEST_HOME}"' EXIT INT TERM
  ```
- **Common failure mode in tests**: Unquoted string paths with spaces or unexpected terminal escape sequences (addressed through strict quoting and `--no-ansi` flags in test scripts).

### 5) Coverage and Quality Signals

- **Coverage tool + threshold**: 100% test pass rate across all 5 test scripts (`verify.sh`, `test_audit_fixes.sh`, `test_deep_audit.sh`, `test_concordance_edge_cases.sh`, `test_audit_claude_improvements.sh`). Zero ShellCheck warnings allowed (`-S warning`).
- **Current reported coverage**: 100% pass across all test suites in local execution and GitHub Actions CI.
- **Known gaps/flaky areas**: Full Typst/Pandoc binary compilation is skipped in environments where `typst` or `pandoc` are not installed locally on the runner host (gracefully skipped via `SKIP` markers).

### 6) Evidence

- [`scripts/verify.sh`](file:///scripts/verify.sh#L1-L496)
- [`tests/test_audit_fixes.sh`](file:///tests/test_audit_fixes.sh#L1-L331)
- [`tests/test_deep_audit.sh`](file:///tests/test_deep_audit.sh#L1-L125)
- [`tests/test_concordance_edge_cases.sh`](file:///tests/test_concordance_edge_cases.sh#L1-L200)
- [`tests/test_audit_claude_improvements.sh`](file:///tests/test_audit_claude_improvements.sh#L1-L120)
- [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L1-L105)

## Extended Sections (Optional)

### CI Verification Matrix

GitHub Actions workflow [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) executes on every push and pull request to `main`:
1. Installs dependencies: `pandoc`, `shellcheck`, `python3`, `git`, `libxml2-utils`.
2. Installs pinned Typst binary (`v0.13.0` / latest musl).
3. Executes syntax & linting checks (`shellcheck`, `python3 -m py_compile`, `bash -n`).
4. Executes `scripts/verify.sh` quality harness.
5. Executes all four targeted regression test suites in `tests/`.
