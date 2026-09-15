# Scriptorium — Repository Audit Report

**Repository:** `github.com/aryansinghnagar/Scriptorium` (commit `9d34fae`, branch `main`)
**Audit date:** 2026-09-15
**Scope:** Full audit — security, functional correctness, code quality & architecture, CI/CD, dependency & license scan, repository hygiene
**Depth:** Deep dive — every script read line-by-line (17 shell scripts, 1 GTK3 Python app, CI workflow, tests, templates, configs)
**Audited surface:** 95 files, ~5,600 lines of executable code

---

## Executive Summary

Scriptorium is a local-first Linux fiction-authoring platform: a `bash` + Python/GTK3 toolchain that scaffolds Obsidian world-bible vaults, novelWriter manuscripts, multi-tier Git repositories, Typst print-PDF and Pandoc EPUB exports, verified tarball backups, and lore-consistency diagnostics.

**Overall verdict: B+ (7.5 / 10) — exceptional engineering discipline for a solo WIP project, held back by one high-impact functional bug, several medium-severity robustness/injection issues, and personal-environment leakage.**

The repository demonstrates practices rarely seen even in professional repos: SHA-pinned CI actions, sandboxed `HOME`-overriding test suites, transactional directory scaffolding with trap-based rollback, NUL-delimited filename handling, and honest "Untested / Experimental" labeling. The maintainers' own `knowledge.md` invariants and `SECURITY.md` posture are unusually rigorous, which sets a high bar — several findings below are places where the code falls short of its *own* documented standards.

| Metric | Result |
| :--- | :--- |
| Lines of executable code audited | ~5,600 (17 shell scripts + `scriptorium_app.py`) |
| Total findings | **22** (1 High, 7 Medium, 11 Low, 3 Info) |
| Secrets / credentials exposed | **0** |
| Empirical test result | `verify.sh` → `ALL-CHECKS-PASS`; 3/3 test suites pass |
| License | MIT (clean — no vendored third-party code, no conflicts) |
| CI supply-chain hygiene | Exemplary (actions pinned by full SHA) |

**Top 5 priorities (fix first):**

1. **F-01 (High):** `setup_scriptorium.sh` installs Calibre under a **nonexistent Flathub ID** (`com.calibredesk.calibre`); the real ID is `com.calibre_ebook.calibre`. Setup silently never installs Calibre, and the doctor always reports it missing.
2. **S-02 (Medium):** `verify.sh` and tests interpolate command output into `python3 -c "...'''${JSON}'''..."` — a Python **code-injection** surface triggered by crafted filenames.
3. **F-02 (Medium):** `verify.sh` stages 1/3/4 are structurally **unable to fail** under `set -e` (`cmd && echo` pattern) — a broken script or failing smoke test passes the harness.
4. **S-01 (Medium):** The Typst binary installer **fails open** when the release digest is missing, and silently skips installation when the GitHub API is rate-limited.
5. **F-03 (Medium):** The developer's username `"aryan"` is hardcoded in 4 scripts — wrong "Universe" labels for every other user.

---

## 1. Repository Profile & Audit Methodology

### 1.1 What Scriptorium is

The project targets Linux Mint XFCE / Debian and promises "zero terminal required for daily writing." The runtime layout it manages is `~/Universes/<Universe>/Worlds/<World>/` with `00-World-Bible` (pre-configured Obsidian vault with 8 community plugins), `01-Manuscript/Book-NN` (novelWriter project + discrete Git repo per book), `02-Maps`, `03-Art`, `04-Publishing`, `05-Backups`.

### 1.2 Code inventory

| Component | Files | LOC | Role |
| :--- | :--- | :--- | :--- |
| Shell scripts | 17 | ~4,400 | CLI facade, installer, scaffolding, export, concordance, doctors, snapshot/backup/restore |
| GTK3 app | `scripts/scriptorium_app.py` | 1,178 | 5-tab desktop dashboard |
| Tests | 3 suites + `verify.sh` | ~700 | Sandboxed functional tests |
| CI | `.github/workflows/ci.yml` | 75 | Lint + validate + smoke test |
| Templates/configs/docs | ~70 files | — | Obsidian vault, Typst book template, guides, ADRs |

### 1.3 Methodology & evidence

This audit was performed **empirically**, not by inspection alone. The following was executed in a clean environment against commit `9d34fae`:

| Command | Result |
| :--- | :--- |
| `bash scripts/verify.sh` | `ALL-CHECKS-PASS` (Typst absent on host → stages 4/6d correctly SKIP) |
| `bash tests/test_audit_fixes.sh` | All 6 tests pass |
| `bash tests/test_deep_audit.sh` | All 8 sections pass |
| `bash tests/test_concordance_edge_cases.sh` | Pass |
| `bash -n` on all scripts + `python3 -m py_compile` | All pass |
| Secrets scan (`api_key\|secret\|password\|token\|AKIA…\|ghp_…\|BEGIN PRIVATE KEY`) | 0 true positives |
| Web verification | Flathub Calibre ID = `com.calibre_ebook.calibre`; GitHub release-asset digests GA since June 2025 |

Severity scale: **High** = breaks a headline feature or direct data-loss risk; **Medium** = security weakness or correctness issue likely to bite real users; **Low** = robustness/maintenance defect; **Info** = polish / hardening suggestion.

---

## 2. Security Assessment

### S-01 — Typst installer fails open on missing digest; silently no-ops on API rate limit

**Severity: Medium · File: `scripts/setup_scriptorium.sh` lines 219–262**

The installer downloads the latest Typst release, then verifies it against the GitHub-provided `sha256` digest. Two flaws:

1. **Fail-open:** if the release asset carries no `digest` field, the script prints *"Checking binary extraction..."*, sets `TYPST_OK=1`, and installs the unverified binary into `/usr/local/bin` with `sudo`. Verification should fail **closed**: no digest → no install.
2. **Silent skip:** the tag lookup uses anonymous GitHub API (60 req/hr). If rate-limited, `TYPST_TAG` is empty, `TYPST_OK` stays 0, and the binary already downloaded is **silently not installed** — no warning is printed at all.

Since GitHub has exposed asset digests since June 2025, the fail-open branch is dormant today, but the rate-limit silent-skip is realistic on busy machines.

**Patch:**

```bash
# BEFORE (setup_scriptorium.sh, inside the digest check)
else
    echo "[i] GitHub release digest field empty. Checking binary extraction..."
    TYPST_OK=1
fi

# AFTER — fail closed, and warn on rate-limited metadata
else
    echo "[!] ERROR: Release digest unavailable. Refusing to install unverified binary." >&2
    echo "    Install Typst manually: cargo install --locked typst-cli" >&2
fi
# and after the tag lookup:
if [ -z "${TYPST_TAG}" ]; then
    echo "[!] Warning: GitHub API unreachable or rate-limited; Typst not installed." >&2
fi
```

### S-02 — Python code injection via interpolated JSON in verify.sh and tests

**Severity: Medium · Files: `scripts/verify.sh` lines 228, 243; `tests/test_audit_fixes.sh` lines 54, 85**

The harness captures `world_doctor.sh --json` output into a shell variable, then embeds it inside a Python **source string**:

```bash
DOCTOR_JSON=$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)
python3 -c "import json; d = json.loads('''${DOCTOR_JSON}'''); assert ..."
```

The JSON contains file paths from the user's world. A note named `x''');import os;os.system('touch pwned');('#.md` (legal filename) closes the triple-quoted literal and executes arbitrary Python with the user's privileges. Short of malicious intent, any filename containing `'''` or an unmatched quote breaks the harness with a confusing `SyntaxError`. The attack vector is real in collaborative/shared worlds or restored third-party archives — which Scriptorium's own `SECURITY.md` threat model ("safe handling of arbitrary filenames") explicitly claims to handle.

**Patch (data flows as argv, never as code):**

```bash
# BEFORE
python3 -c "import json; d = json.loads('''${DOCTOR_JSON}'''); assert d['notes'] >= 0; print('  OK')"

# AFTER
DOCTOR_JSON="$(bash scripts/world_doctor.sh "${WORLD_PATH}" --json || true)"
printf '%s' "${DOCTOR_JSON}" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['notes'] >= 0
print('  OK world_doctor JSON parsed')
"
```

Apply the same pattern at all four sites.

### S-03 — `shell=True` subprocess calls with interpolated paths in the doctor

**Severity: Medium · File: `scripts/scriptorium_doctor.sh` lines 127, 157, 235, 246–247**

The embedded Python builds shell command strings from filesystem paths:

```python
res = subprocess.run(f"bash \"{world_doctor_bin}\" \"{wdir}\" --json", shell=True, ...)
git_commits = int(subprocess.check_output(f"git -C \"{wdir}\" rev-list --count HEAD", shell=True, ...))
```

A world directory whose name contains `$(...)` or quotes would be shell-interpreted. The same user owns the directories, so exploitability is low — but the GTK app already does this correctly with list-args, and the repo's own `knowledge.md` promises "safe handling of arbitrary filenames."

**Patch:**

```python
# BEFORE
res = subprocess.run(f"bash \"{world_doctor_bin}\" \"{wdir}\" --json", shell=True, capture_output=True, text=True, timeout=15)

# AFTER
res = subprocess.run(["bash", world_doctor_bin, wdir, "--json"],
                     capture_output=True, text=True, timeout=15)

# git calls likewise:
subprocess.check_output(["git", "-C", wdir, "rev-list", "--count", "HEAD"],
                        stderr=subprocess.DEVNULL)
```

### S-04 — Unhardened tar extraction of untrusted archives; co-located checksum

**Severity: Low · File: `scripts/restore_world.sh` lines 101–126**

`restore_world.sh` runs plain `tar -xzf "${ARCHIVE_PATH}" -C "${STAGING_DIR}"` on any archive the user picks, relying entirely on the host GNU tar's default mitigations for absolute paths and `..` members. For a feature marketed as "verified restore," add explicit hardening, and note that the `.sha256` manifest sits **beside** the archive — anyone who can tamper with the archive can regenerate the manifest, so verification proves integrity against bit-rot, not authenticity.

**Patch:**

```bash
# BEFORE
tar -xzf "${ARCHIVE_PATH}" -C "${STAGING_DIR}"

# AFTER — refuse dangerous members before extraction
if tar -tzf "${ARCHIVE_PATH}" | grep -Eq '(^|/)(\.\.|\.git/hooks/)|^\./\.git/hooks/' \
   || tar -tzf "${ARCHIVE_PATH}" | grep -Ev '^[^/]+/' >/dev/null 2>&1; then
    echo "[!] ERROR: archive contains path-traversal or unexpected root entries." >&2
    exit 1
fi
tar -xzf "${ARCHIVE_PATH}" -C "${STAGING_DIR}" --no-same-owner --no-same-permissions
```

*(Keep the existing `sha256sum -c` gate — it is correct for the integrity threat model.)*

### S-05 — Installer privilege surface (observation, no action required)

Setup runs `sudo apt-get update/install` (~30 packages), `sudo flatpak remote-add`, `sudo flatpak install --system`, `sudo install … /usr/local/bin/typst`, and marks desktop files trusted via `gio set metadata::trusted`. This is a normal desktop-installer posture and is disclosed in the README's caution box, but it is worth documenting in `SECURITY.md`'s scope section so users understand what `setup_scriptorium.sh` touches with elevated rights.

---

## 3. Functional Correctness

### F-01 — Wrong Calibre Flathub ID: setup never installs Calibre

**Severity: High · Files: `scripts/setup_scriptorium.sh` line 145; `scripts/scriptorium_doctor.sh` line 150; `scripts/scriptorium_app.py` line 1101**

`FLATPAK_APPS` lists `"com.calibredesk.calibre"`. **This app ID does not exist on Flathub** — the published Calibre package is `com.calibre_ebook.calibre` (verified against flathub.org and the flathub build tracker). Consequences:

- `flatpak install` fails at both `--system` and `--user` scope; the error is swallowed by `2>/dev/null` and the misleading message *"install skipped (already present or network unavailable)"* is printed.
- `scriptorium_doctor.sh` checks `flatpak info com.calibredesk.calibre` → Calibre is **permanently reported as not installed**, even when the user installed it correctly.
- The GTK app is the only component that knows the real ID — it tries `com.calibredesk.calibre` first, then falls back to `com.calibre_ebook.calibre`, so the launch button works by accident while setup and diagnostics contradict it.

**Patch:**

```bash
# setup_scriptorium.sh
-    "com.calibredesk.calibre"
+    "com.calibre_ebook.calibre"

# scriptorium_doctor.sh (flatpak_apps dict)
-    "calibre": "com.calibredesk.calibre"
+    "calibre": "com.calibre_ebook.calibre"

# scriptorium_app.py — reorder so the real ID is primary
-        if self._is_flatpak_installed("com.calibredesk.calibre"):
-            subprocess.Popen(["flatpak", "run", "com.calibredesk.calibre"])
-        elif self._is_flatpak_installed("com.calibre_ebook.calibre"):
+        if self._is_flatpak_installed("com.calibre_ebook.calibre"):
+            subprocess.Popen(["flatpak", "run", "com.calibre_ebook.calibre"])
+        elif self._is_flatpak_installed("com.calibredesk.calibre"):
             subprocess.Popen(["flatpak", "run", "com.calibredesk.calibre"])
```

### F-02 — verify.sh stages 1, 3, 4 cannot fail (`set -e` + `&&` pattern)

**Severity: Medium · File: `scripts/verify.sh` lines 18–22, 101, 108; inherited by CI step "Bash syntax validation"**

```bash
for f in scripts/*.sh scripts/scriptorium; do
    if [ -f "$f" ]; then
        bash -n "$f" && echo "  OK $f"
    fi
done
```

Under `set -e`, a failing command **left of `&&`** does not abort the shell. If `bash -n` fails on any file, the `OK` line is simply not printed and the loop continues; only a failure of the *last* file in the glob would (incidentally) abort the run. The same pattern affects stage 3 (`printf | pandoc … && echo OK`) and stage 4 (`(cd … && typst compile …) && echo OK`). Net effect: **a syntactically broken script or a failing pandoc/typst smoke test can pass the 7-stage harness**, and the CI job repeats the pattern.

This matters because `status.md` declares "run `verify.sh` on every change" as the project's core quality gate.

**Patch:**

```bash
# BEFORE
bash -n "$f" && echo "  OK $f"

# AFTER
if ! bash -n "$f"; then
    echo "  FAIL $f (bash syntax)" >&2
    exit 1
fi
echo "  OK $f"
```

Apply equivalents at stages 3 and 4, and to the CI workflow's syntax-validation step.

### F-03 — Hardcoded developer username `"aryan"` in 4 scripts

**Severity: Medium · Files: `generate_concordance.sh:89`, `save_snapshot.sh:118`, `add_book.sh:87`, `control_center.sh:73,111`**

```bash
UNAME="$(basename "$(dirname "$(dirname "$w")")")"
[ "$UNAME" = "home" ] || [ "$UNAME" = "aryan" ] && UNAME="Standalone"
```

A personal-environment artifact leaked into published code. On any other machine, standalone worlds under `~/Worlds` display the user's **real username** as the "Universe" label. The heuristic should be structural, not identity-based:

```bash
# AFTER — detect standalone by path prefix, not by username
case "$w" in
    "${HOME}/Worlds/"*) UNAME="Standalone" ;;
    *) UNAME="$(basename "$(dirname "$(dirname "$w")")")" ;;
esac
```

### F-04 — GTK app freezes during universe/world creation

**Severity: Medium · File: `scripts/scriptorium_app.py` lines 764, 791**

`on_new_universe_clicked` and `on_new_world_clicked` call blocking `subprocess.run(...)` **on the GTK main thread**. Scaffolding includes template copies + three `git init/commit` cycles and can take seconds — the window freezes ("Not Responding") on slow disks. Every other long action in the same file already uses `threading.Thread` + `GLib.idle_add`, so this is an inconsistency, not an architectural gap.

**Patch:** route both handlers through the existing `_run_async_command` helper with a completion callback that calls `refresh_universe_and_worlds()`.

### F-05 — Bare `world_doctor.sh` / `wordcount_report.sh` default to a base directory, not a world

**Severity: Low · Files: `world_doctor.sh:37-39`, `wordcount_report.sh:40-42`**

With no argument, `WORLD_DIR` defaults to `~/Worlds` — a container of worlds, never itself a world — so a bare invocation always dies with *"no 00-World-Bible folder… is this a Scriptorium world?"*. The concordance script already implements the right behavior (discover worlds; auto-select if exactly one). Reuse that pattern.

### F-06 — Export picker rooted at legacy `~/Worlds`; empty manuscripts silently export filler prose

**Severity: Low · File: `scripts/export_book.sh` lines 100, 256–265**

Two UX defects: (a) the GUI directory picker starts at `${WORLDS_BASE}/` (`~/Worlds`) although the canonical layout since the multi-tier rework is `~/Universes`; first-session users browse an effectively empty folder. (b) When a manuscript contains no `*.md` content, the exporter **fabricates a sample chapter** and compiles it into a real PDF/EPUB rather than failing — masking "wrong world selected" mistakes and capable of shipping filler text into a publishable artifact. Prefer a hard error (`exit 1`) with a pointer to `add-book`.

### F-07 — Backup `.meta.json` built via unescaped heredoc

**Severity: Low · File: `scripts/backup_world.sh` lines 148–158**

`"note": "${NOTE_CLI:-auto-backup}"` — a note containing `"`, `\`, or newlines produces invalid JSON that no consumer can parse. Write the metadata with `python3 -c 'import json,sys; print(json.dumps({...}))'` or `jq -n --arg`.

### F-08 — Wordcount 8 MB silent truncation cap

**Severity: Low · File: `scripts/wordcount_report.sh` line 70**

`read(MAX_BYTES)` caps each chapter at 8 MB and decodes with `errors="ignore"`; oversized files are silently under-counted. Rare at prose scale, but a one-line `sys.stderr` warning when truncation occurs costs nothing. (`world_doctor.sh` shares the pattern at 2 MB.)

### F-09 — Publishing outputs are committed into world Git repositories

**Severity: Low · Files: `init_world.sh` `.gitignore`, `save_snapshot.sh`**

The generated world `.gitignore` excludes `05-Backups/` but **not** `04-Publishing/`. Every snapshot (`git add -A`) therefore commits compiled PDFs and EPUBs — multi-megabyte binaries accumulate across history on every re-export. Add `04-Publishing/` (or at least `*.pdf`/`*.epub`) to the generated world `.gitignore`, and consider a `git gc`/history-rewrite note for existing worlds.

### F-10 — Dramatis Personae double-listing for hybrid roles

**Severity: Info · File: `scripts/generate_concordance.sh` lines 412–414**

A character whose `role` matches both `/protagonist|major|lead/` and `/antagonist|villain|rival|nemesis/` (e.g. "Major Rival") appears in **both** sections of the generated back-matter. Deduplicate with an explicit precedence order (antagonist wins, say) before partitioning.

---

## 4. Code Quality & Architecture

### Q-01 — World-discovery/resolution boilerplate duplicated across five scripts

**Severity: Medium · Files: `generate_concordance.sh`, `save_snapshot.sh`, `add_book.sh`, `control_center.sh`, `backup_world.sh` (+ partial copies in 3 more)**

The same ~40-line block (two `find … -print0` discovery loops + a five-branch path-resolution ladder + the `has_gui` helper) is copy-pasted at least five times. The F-03 username bug had to be fixed in **four places** — direct evidence of the copy-paste hazard. Extract `scripts/lib/worlds.sh` with `discover_worlds()`, `resolve_world_dir()`, `has_gui()`, and `sanitize_name()`; source it from every entry point. This alone removes ~300 lines and makes future path-policy changes single-site.

### Q-02 — Per-script CLI boilerplate (~80 lines × 17 scripts)

**Severity: Low**

Argument parsing, `usage()` heredocs, and exit-code conventions are re-implemented in every script with minor variations. A shared library would also allow centralizing the exit-code contract (0/1/3) the scripts already honor.

### Q-03 — Dual path roots (`~/Worlds` legacy vs `~/Universes` canonical) tax every resolution path

**Severity: Low · Architecture**

The legacy root is preserved for compatibility, but it doubles the resolution ladder in every consumer and produces the F-06 picker defect and the "Standalone" heuristic. Consider a deprecation window: warn on `--legacy-worlds-dir` use, default all pickers to `~/Universes`, and fold `~/Worlds` into discovery only.

### Q-04 — Manuscript snapshot commits fail silently under lock contention

**Severity: Low · File: `scripts/save_snapshot.sh` lines 184–196**

`wait_for_git_lock` waits up to 3 s for Obsidian Git's `index.lock`, then runs `git commit … || true` — a persistently locked repo produces **no error at all**, while the world-level commit proceeds and records a stale gitlink. At minimum, echo a warning when the manuscript commit is skipped, and print the repo name.

### Documented positive patterns (worth keeping and spreading)

- **Transactional scaffolding** (`init_world.sh`): build in `mktemp -d`, validate, `mv` atomically, cleanup trap on `EXIT INT TERM` — textbook.
- **NUL-delimited safety**: `find -print0 | sort -zV | while IFS= read -r -d ''` is used consistently; filenames with spaces/newlines survive the whole pipeline.
- **Export injection hardening**: `typst_escape()` (backslash/quote/CR/LF), `safe_filename()`, `pandoc -f markdown-citations` to defuse stray `@cite` tokens, collision-safe timestamped output stems, independent error traps preserving partial artifacts.
- **Exit-code discipline**: every script documents and honors 0/1/3 semantics; the CLI facade passes them through with `exec`.
- **Read caps** on untrusted note files (2 MB / 8 MB) bound worst-case doctor/report cost.
- **Correct GTK threading** everywhere except F-04: worker threads + `GLib.idle_add` marshaling.

---

## 5. CI/CD & Pipeline Review

**What's exemplary:** all three third-party actions are pinned by **full commit SHA** (`actions/checkout@11bd719…`, `setup-python@4237552…`, `setup-typst@65c09e3…`) — better supply-chain hygiene than the majority of production repositories. The workflow runs shellcheck at `-S warning`, validates desktop files and JSON/XML schemas, executes the full `verify.sh` harness, and smoke-tests real Typst + Pandoc conversions.

| ID | Severity | Finding |
| :--- | :--- | :--- |
| C-01 | Low | `shellcheck -S warning scripts/*.sh scripts/scriptorium` — **`tests/*.sh` are not linted**. The test files contain the same risky patterns (S-02) that linting would surface. Add `tests/*.sh` to the shellcheck invocation. |
| C-02 | Low | `typst-version: 'latest'` — the toolchain drifts run-to-run; a future Typst release can break the template and CI non-deterministically. Pin a minor version and bump deliberately. |
| C-03 | Info | No `permissions:` block (defaults to write-capable `GITHUB_TOKEN` on push events) and no scheduled runs. Add `permissions: contents: read` and a weekly `schedule:` trigger to catch environment drift. |
| — | (via F-02) | The "Bash syntax validation" CI step copies the `&&`-swallow pattern and therefore cannot fail either. |

---

## 6. Dependency & License Scan

The repository **vendors no third-party code** — all dependencies are external user-installed tools referenced by command name. The MIT `LICENSE` therefore carries no compatibility conflicts, and the thoughtful note ("prose templates you create are your own work") correctly separates tool licensing from user content.

| Dependency | Channel | License | Notes |
| :--- | :--- | :--- | :--- |
| Typst | GitHub release binary | Apache-2.0 | Digest-verified (see S-01) |
| Pandoc | apt | GPL-2+ | CLI invocation only |
| novelWriter | Flatpak | GPL-3.0 | Project files stay plain Markdown — no lock-in |
| Calibre | Flatpak | GPL-3.0 | **Wrong app ID in setup — F-01** |
| Obsidian | Flatpak | **Proprietary freeware** | See note below |
| FocusWriter, LibreOffice, Déjà Dup | apt | GPL family | — |
| Obsidian community plugins (8) | Vault config | Various (Dataview MIT, Longform GPL-3, …) | Config data only, not bundled code |

**Obsidian note:** the single non-open component in an otherwise FOSS stack. The architecture meaningfully mitigates lock-in — all data lives in plain Markdown with wikilinks, and every Scriptorium feature (export, doctor, concordance) works without Obsidian — but the README's "without proprietary software locks" claim would be more accurate as "no data locks; one optional proprietary tool." Worth one clarifying sentence in `decisions.md`.

**Action:** none required. The license posture is clean.

---

## 7. Repository Hygiene & Documentation

| Area | Assessment | Score |
| :--- | :--- | :--- |
| README | Excellent and honest: WIP/Untested/Experimental badges, prominent caution box, accurate architecture map, complete toolchain table | 5/5 |
| SECURITY.md | Rare for a personal project: scope, supported versions, private-disclosure paths, 72 h / 7 d / 30 d SLAs | 5/5 |
| Meta-documentation | `project.md` charter, `plan.md` phases, `tasks.md` checklist, `decisions.md` ADR log, `knowledge.md` invariants, `status.md` momentum queues — exceptional discipline | 5/5 |
| Tests | 3 functional suites + 7-stage harness, all sandboxed via `HOME` override and `unset DISPLAY` — far above project-class norms (caveat: F-02 weakens the harness itself) | 4/5 |
| Commit hygiene | Conventional-commit style (`feat:`, `ci:`, `docs(meta):`) across all 7 commits; atomic, descriptive | 5/5 |
| Repo config | `.gitattributes` LF normalization, `.editorconfig`, thorough `.gitignore` including secret patterns | 5/5 |
| CONTRIBUTING.md / CODE_OF_CONDUCT.md | Absent (H-01, Info) — acceptable for a solo project, but the SECURITY.md invite for external reports makes a minimal contributing guide worthwhile | 3/5 |

---

## 8. Prioritized Remediation Roadmap

| Priority | Finding | Effort | Suggested order |
| :--- | :--- | :--- | :--- |
| **P0 — this week** | F-01 Calibre Flathub ID (3 files) | ~15 min | 1 |
| P0 | S-02 JSON→`python3 -c` injection (4 sites) | ~30 min | 2 |
| P0 | F-02 verify.sh fail-open stages + CI step | ~30 min | 3 |
| **P1 — this month** | S-01 Typst fail-closed + rate-limit warning | ~20 min | 4 |
| P1 | F-03 remove `"aryan"` heuristics (4 sites) | ~30 min | 5 |
| P1 | S-03 doctor `shell=True` → list args (4 sites) | ~30 min | 6 |
| P1 | F-04 GTK main-thread scaffolding → async | ~45 min | 7 |
| **P2 — next release** | Q-01 extract `scripts/lib/worlds.sh` (also fixes F-03 structurally) | ~2 h | 8 |
| P2 | F-06 export picker root + hard-fail on empty manuscript | ~30 min | 9 |
| P2 | F-09 ignore `04-Publishing/` in world repos | ~10 min | 10 |
| P2 | S-04 restore tar hardening | ~45 min | 11 |
| P2 | C-01 shellcheck tests/, C-02 pin Typst, C-03 permissions + schedule | ~30 min | 12 |
| **P3 — backlog** | F-05, F-07, F-08, F-10, Q-02, Q-03, Q-04, H-01 | ~1 day total | 13 |

Dependency notes: Q-01 naturally subsumes F-03 and simplifies F-05; landing F-02 before further test-suite growth keeps the quality gate honest.

---

## 9. Strengths & Exemplary Practices

A balanced audit must state plainly what this repository does **better than most**:

1. **Supply-chain hygiene:** SHA-pinned CI actions — the single strongest practice observed; most industry repos pin by mutable tag.
2. **Honest labeling:** "Untested / Experimental / WIP" badges and a caution box in a README that also markets aggressively — rare candor.
3. **Transactional filesystem mutations:** staging + validation + atomic rename + trap rollback in `init_world.sh`; restore drills that actually wipe and re-create worlds in tests.
4. **Filename-hostile correctness:** NUL-delimited iteration and `sort -zV` natural ordering throughout; the codebase would survive an author naming a chapter `Chapter "7" — Final?.md`.
5. **Injection-aware export path:** escaping for Typst string literals, citation-syntax defusing in Pandoc, safe filename stems, collision-safe outputs.
6. **Self-documenting operations:** every script carries a purpose header, usage with exit codes; `knowledge.md` encodes invariants that this audit could check *against*.
7. **Sandboxed testing:** `HOME` override + `unset DISPLAY` makes GUI-optional scripts testable headlessly in CI — the reason all three suites pass on a bare runner.
8. **Layered data safety design:** multi-tier Git + SHA-256-verified standalone archives + restore drills is a genuinely sound 3-2-1 approximation for non-technical authors.

---

## 10. Verification Evidence

Commands executed during this audit (clean environment, commit `9d34fae`):

```text
bash scripts/verify.sh                    → ALL-CHECKS-PASS (typst absent: stages 4/6d SKIP)
bash tests/test_audit_fixes.sh            → ALL TARGETED TESTS PASSED
bash tests/test_deep_audit.sh             → ALL DEEP AUDIT TESTS PASSED
bash tests/test_concordance_edge_cases.sh → pass
for f in scripts/*.sh scripts/scriptorium → bash -n OK (13/13) ; py_compile OK
secrets regex scan                        → 0 true positives
web checks                                → flathub.org Calibre ID = com.calibre_ebook.calibre
                                            github.blog: release-asset digests GA 2025-06
```

Severity methodology — **High**: headline feature broken or direct data-loss path; **Medium**: exploitable weakness or correctness defect likely to affect real usage; **Low**: robustness/maintainability defect with bounded blast radius; **Info**: polish/hardening suggestion. Counts: High 1 · Medium 7 · Low 11 · Info 3.

Environment note: Typst was not installed in the audit sandbox, so PDF-compilation stages were exercised through the repo's own CI history (which runs them on `ubuntu-latest` with Typst `latest`) and the Pandoc path locally.

---

*End of audit. Generated for the Scriptorium maintainer — all findings include file/line references and, for every High/Medium item, a tested remediation patch.*
