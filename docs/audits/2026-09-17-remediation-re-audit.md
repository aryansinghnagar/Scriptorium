# Scriptorium Re-Audit Report — Remediation Verification

> **Committed record.** This is the verification record for the remediation
> series (baseline `9d34fae` → `5058055`), archived as committed at the time of
> the re-audit. The five findings it registered (N-01…N-05) were closed by the
> follow-up commits made the same day — see [CHANGELOG.md](../../CHANGELOG.md)
> and ADR-021 in [docs/meta/decisions.md](../meta/decisions.md). The original
> audit it verifies lives at
> [2026-09-16-external-audit.md](2026-09-16-external-audit.md).

**Repository:** `github.com/aryansinghnagar/Scriptorium` (branch `main`)
**Commit audited:** `5058055` (HEAD of the remediation series, pushed 2026-09-16)
**Baseline of the original audit:** `9d34fae` (22 findings: 1 High, 7 Medium, 11 Low, 3 Info)
**Re-audit date:** 2026-09-17
**Method:** fresh clone from GitHub, independent empirical re-verification (adversarial tests, harness breakage drills, full gate re-run, line-level review of all new code)

---

## 0. Re-Audit Verdict

**Overall grade: A (9.0 / 10) — up from B+ (7.5 / 10) at baseline.**

All 22 findings from the original audit are closed in the pushed tree — 21 fully remediated and verified, and Q-02 (CLI boilerplate) addressed in the deliberately lightweight form its roadmap allowed, with the tradeoff documented in ADR-020 and the quality gate centralized in CONTRIBUTING.md. The remediation series (10 atomic conventional commits, 26 files, +1,026 / −264 lines) landed on GitHub exactly as delivered, and every quality gate passes at CI parity on a fresh clone: `verify.sh` reports ALL-CHECKS-PASS, all three test suites pass, `bash -n` passes on every shell file, and `shellcheck 0.11.0 -S warning` — the exact CI invocation — passes with zero findings across scripts, lib, facade, and tests.

The re-audit also exercised the fixes adversarially rather than trusting the diffs: a hostile filename carrying Python-breaking quotes produces valid JSON instead of code injection; a crafted tarball with a `../` traversal member and a planted non-sample git hook are both refused with exit 1; an empty manuscript export now hard-fails instead of fabricating filler prose; and a deliberately broken script, JSON file, or schema file makes the verification harness exit 1 — the harness can finally fail, which was the point of F-02.

What keeps this from an A+: one Low documentation defect introduced by the remediation itself (the exit-code contract in CONTRIBUTING.md no longer matches the code), four Info-level polish items (commit authorship identity, two small consistency gaps, and minor GUI-thread residuals), and the honest caveat that two hardening paths (the Typst digest gate and the GTK async runtime) were verified structurally and by code review in this sandbox, not end-to-end at runtime — Typst and a display server are absent from the audit environment, exactly as in the original audit.

**New finding distribution: 0 High, 0 Medium, 1 Low, 4 Info.**

| Re-audit checks | Result |
| :--- | :--- |
| Fresh clone state | HEAD = `5058055`, clean tree, 98 tracked files, all 10 remediation commits present |
| `bash scripts/verify.sh` | **ALL-CHECKS-PASS** (Typst absent → stages 4 and 6d SKIP, environmental) |
| `tests/test_audit_fixes.sh` | **PASS** — 6/6 targeted tests |
| `tests/test_deep_audit.sh` | **PASS** — all 8 sections |
| `tests/test_concordance_edge_cases.sh` | **PASS** |
| `bash -n` (scripts + lib + facade + tests) | **PASS** — all files |
| `shellcheck 0.11.0 -S warning` (CI parity invocation) | **PASS** — 0 findings |
| Secrets scan (key/token/password/private-key patterns) | **0 true positives** |
| Committed artifacts (`__pycache__`, `.pyc`, archives, images) | **None** |
| Largest tracked file | `scripts/scriptorium_app.py`, 53 KB |
| Adversarial injection / traversal / hook-planting tests | **All refused correctly** |
| Harness breakage drills (3 defect classes) | **All fail the harness, exit 1** |

---

## 1. What Landed on GitHub

The pushed history is exactly the delivered remediation series. Between baseline `9d34fae` and current `5058055`:

| # | Commit | Subject | Findings closed |
| :--- | :--- | :--- | :--- |
| 1 | `dfe2589` | fix(setup): install Calibre under its real Flathub ID | F-01 |
| 2 | `3d1524f` | fix(verify): fail-closed harness stages; doctor JSON via stdin | F-02, S-02 |
| 3 | `367f875` | fix(setup): fail closed when Typst release digest is unavailable | S-01 |
| 4 | `cddfdef` | fix(doctor): invoke subprocesses without `shell=True` | S-03 |
| 5 | `78e3dcb` | fix(app): scaffold universes and worlds off the GTK main thread | F-04 |
| 6 | `282fc9d` | refactor(scripts): extract shared `lib/worlds.sh`; remove identity-based heuristics | Q-01, F-03, F-05, Q-03 |
| 7 | `57eaa41` | fix(world): functional hardening batch | F-06, F-07, F-08, F-09, F-10, S-04, Q-04 |
| 8 | `5ca53db` | ci: pin Typst, least-privilege permissions, weekly drift run | C-02, C-03 |
| 9 | `a2d4736` | docs: audit report, ADR-020, CONTRIBUTING, privilege disclosure | H-01, S-05 |
| 10 | `5058055` | chore(lint): remove dead `PROJECT_ROOT` vars; tests join ShellCheck scope | C-01 |

Net diff: **26 files changed, +1,026 insertions, −264 deletions**; three new files (`AUDIT.md`, `CONTRIBUTING.md`, `scripts/lib/worlds.sh`); no deleted functionality; no new external dependencies. The working tree is clean, the single `main` branch matches `origin/main`, and no stray local state or build artifacts were pushed.

The commit messages are honest and specific — each names the finding IDs it closes and explains non-obvious choices (for example, why blanket-rejecting all `.git/hooks` members would false-positive on every legitimate backup, since `git init` ships `*.sample` hooks). That level of traceability is what made this re-audit cheap to perform: every claim in the history is independently checkable, and every one checked out.

---

## 2. Finding-by-Finding Verification (all 22)

Each row below was verified in the fresh clone by a combination of code inspection, greps across the tree, and — for every security-relevant or behavioral claim — an executed test. "Evidence" names the strongest check performed; all static claims were additionally covered by the full-gate re-run.

| ID | Severity | Original finding | Verdict | Strongest evidence |
| :--- | :--- | :--- | :--- | :--- |
| F-01 | High | Wrong Calibre Flathub ID — setup never installs Calibre | **CLOSED** | Correct ID `com.calibre_ebook.calibre` present in setup, doctor, uninstaller, app, and both compatibility docs; zero references to the old ID outside a harmless launch-time fallback chain (see N-05) |
| S-01 | Medium | Typst installer fails open on missing digest | **CLOSED** | Digest-missing branch now prints "Refusing to install unverified binary" and leaves `TYPST_OK=0`; rate-limit path warns explicitly instead of silently skipping |
| S-02 | Medium | Python code injection via interpolated doctor JSON | **CLOSED** | `verify.sh` pipes JSON via stdin to `json.load(sys.stdin)`; adversarial note named `Evil'''{{import os}}.md` produces valid JSON with correct diagnostics (notes=10, 1 timeline error) |
| S-03 | Medium | `shell=True` with interpolated paths in doctor | **CLOSED** | All five call sites converted to list-argv form; `grep -rn "shell=True"` over scripts/ and tests/ returns nothing |
| F-02 | Medium | verify.sh stages structurally cannot fail | **CLOSED** | Breakage drills: corrupted script syntax, corrupted JSON config, and corrupted manual schema each make the harness exit 1 with a FAIL/traceback — reproduced for all three classes |
| F-03 | Medium | Hardcoded developer username `"aryan"` | **CLOSED** | Zero occurrences in code; Standalone/Universe detection is now structural (path prefix in `universe_label`) |
| F-04 | Medium | GTK app freezes during universe/world creation | **CLOSED** | Creation, snapshot, backup, restore, add-volume, diagnostics, and compile all dispatch to worker threads; all UI updates marshal through `GLib.idle_add` (residuals: N-04) |
| Q-01 | Medium | World-discovery logic copy-pasted across five scripts | **CLOSED** | `scripts/lib/worlds.sh` is the single source of truth (discover/resolve/label/sanitize/has_gui), sourced by 11 scripts; ~300 lines of duplication removed |
| S-04 | Low | Unhardened tar extraction of untrusted archives | **CLOSED** | Archive listing gate rejects absolute paths, `..` traversal, non-root-prefix entries, and non-sample `.git/hooks` members; extraction uses `--no-same-owner --no-same-permissions`; both crafted malicious archives refused with exit 1 |
| F-05 | Low | Bare doctor/wordcount default to a base directory | **CLOSED** | Bare invocation with multiple worlds lists them with universe labels and exits 2; exactly one world auto-selects; legacy-only layout resolves correctly |
| F-06 | Low | Empty manuscripts silently export fabricated prose | **CLOSED** | Fully empty book hard-fails with "no manuscript content found" and exit 1; no artifact fabricated (04-Publishing stays empty) |
| F-07 | Low | Backup `.meta.json` built via unescaped heredoc | **CLOSED** | Metadata now written with `json.dump` under a documented F-07 comment |
| F-08 | Low | Wordcount 8 MB silent truncation | **CLOSED** | Truncation now emits an explicit stderr warning naming the file and the cap |
| F-09 | Low | Publishing outputs committed into world Git repos | **CLOSED** | `/04-Publishing/` ignored in both the root `.gitignore` and the generated world `.gitignore`; migration path for existing worlds documented in ADR-020 |
| F-10 | Info | Dramatis Personae double-listing for hybrid roles | **CLOSED** | Precedence partition (antagonist > protagonist > supporting); "Major Rival" appears exactly once, under Antagonists |
| Q-02 | Low | Per-script CLI boilerplate (~80 lines × 17 scripts) | **CLOSED (lightweight, as designed)** | Shared discovery lib + centralized quality gate and boundary rules in CONTRIBUTING.md; full facade extraction consciously deferred with rationale — an acceptable scope decision, not a gap |
| Q-03 | Low | Dual path roots tax every resolution path | **CLOSED** | Documented resolution contract (path > universe > canonical basename > legacy root) in `worlds.sh`; legacy resolution prints a deprecation nudge to stderr (residual: N-03) |
| Q-04 | Low | Manuscript commits fail silently under lock contention | **CLOSED** | Lock-detection helper plus "never drop manuscript commits silently" handling in `save_snapshot.sh` |
| C-01 | Low | `tests/*.sh` not linted by CI | **CLOSED** | CI shellcheck invocation now covers `scripts/*.sh scripts/lib/*.sh scripts/scriptorium tests/*.sh`; verified at CI parity locally with 0 findings |
| C-02 | Low | `typst-version: 'latest'` toolchain drift | **CLOSED** | Pinned to `0.13` with an in-file rationale comment explaining when and how to bump deliberately |
| C-03 | Info | No `permissions:` block, no scheduled runs | **CLOSED** | `permissions: contents: read` plus weekly `schedule: cron '23 4 * * 1'` drift run |
| H-01 | Info | No CONTRIBUTING.md | **CLOSED** | Substantive guide: ground rules, dev setup, quality gate, commit style, submission flow — and it encodes the audit's own lessons (stdin/argv boundary rule, fail-closed harness expectation) |
| S-05 | — (observation) | Installer privilege surface disclosure | **ADDRESSED** | SECURITY.md now enumerates every `sudo` operation; the re-audit cross-checked each claim against `setup_scriptorium.sh` / `uninstall_scriptorium.sh` line-by-line — all accurate, including the digest-gated Typst install and the `gio set` launcher trust calls |

**Scorecard: 21 of 22 fully closed, 1 closed in its documented lightweight form (Q-02). Zero regressions of any original finding were detected.**

---

## 3. Adversarial Test Evidence

The re-audit did not accept "the tests pass" as proof that the security fixes work — the original audit's central criticism was that the harness itself could not fail. The following attacks were executed directly against the fresh clone.

**Injection probe (S-02).** A world was scaffolded in a sandboxed `HOME`, and a character note was created whose filename embeds a triple-quote payload and Python source (`Evil'''{{import os}}.md`, with matching front-matter). Under the baseline code this filename would terminate the interpolated `'''` string inside `python3 -c "..."` and execute attacker-controlled source. On the current tree, `world_doctor.sh --json` returns valid JSON (`notes: 10`, one timeline error for the hostile note itself, all expected keys present) — the payload never crosses the shell/Python boundary because the JSON now flows through stdin into `json.load(sys.stdin)`. The doctor's own exit code (1, because it found a diagnostic) is unrelated to the payload and behaved as documented.

**Traversal and hook-planting archives (S-04).** Two malicious archives were crafted by hand. The first contained a legitimate-looking world plus a planted `.git/hooks/pre-commit` executable; the second contained a member with a `../../` traversal path. `restore_world.sh` refused both with exit 1 and the correct specific error ("non-sample .git/hooks members … code-execution risk" / "absolute or path-traversal members"), and no file escaped the staging directory. The non-sample-hook discrimination matters: a naive blanket rejection of all hooks would break every honest backup, because `git init` ships `*.sample` hooks — the fix gets this right, and the code comment explains why.

**Empty-manuscript export (F-06).** With every chapter and back-matter file removed, `export_book.sh` exits 1 with "no manuscript content found" and leaves `04-Publishing/` empty — no fabricated sample chapter, no compiled filler artifact. (An intermediate run that still produced an EPUB turned out to be compiling legitimately generated back matter from a prior concordance run, not fabricating content — the guard correctly distinguishes "no content at all" from "content I did not author".)

**Hybrid-role dedup (F-10).** A character with role `Major Rival` (matching both the protagonist pattern `major` and the antagonist pattern `rival`) appears exactly once in the generated Dramatis Personae, under Antagonists & Rivals — the documented precedence.

**Fail-closed harness drills (F-02).** In a disposable copy of the repo, three defect classes were injected one at a time: (a) garbage appended to `add_book.sh` (syntax), (b) an intentionally corrupt `configs/leechblock_scriptorium_rules.json`, (c) a removed required section in `docs/AUTHOR_MANUAL.md`. Each run exited 1 with a specific failure message (bash syntax FAIL / JSON traceback / schema AssertionError). The project's core quality gate can now actually fail — and CONTRIBUTING.md explicitly tells future contributors that a stage that cannot fail is a bug worth reporting.

**Resolution behavior (F-05, Q-03).** With two canonical worlds and one legacy world present, bare `world_doctor.sh` and `wordcount_report.sh` both list all three with universe labels (`[U1]`, `[Standalone]`) and exit 2; with exactly one world, it auto-selects; resolving a legacy world by name prints the deprecation nudge to stderr and proceeds.

---

## 4. Security Posture After Remediation

The four security findings (S-01 through S-04) are closed, and the installer's privilege surface is now fully disclosed (S-05). The remaining posture is sound for the project's stated single-user, offline threat model:

- **Supply chain.** The Typst install path now requires a matching GitHub-published SHA-256 digest before `sudo install` runs, and refuses otherwise. The rate-limit path (anonymous GitHub API, 60 req/hr) warns instead of silently skipping. CI pins all three actions by full commit SHA and the Typst toolchain to `0.13`.
- **Injection surface.** No `shell=True` remains anywhere; the shell/Python data boundary is stdin/argv-only, and the boundary rule is now written down in CONTRIBUTING.md as a project invariant so it survives future contributors.
- **Archive handling.** Extraction is gated by a member allowlist of one root directory, traversal/absolute rejection, non-sample-hook rejection, and neutralized ownership/permission restoration.
- **Least privilege.** CI runs with `contents: read` only.

Two residual limitations are **documented and accepted**, and the re-audit confirms the documentation is accurate rather than hand-wavy: (1) the co-located `sha256.manifest` beside each backup proves integrity against bit-rot, not authenticity — anyone who can replace the archive can regenerate the manifest; the code comment and SECURITY.md both state this plainly. (2) Existing worlds created before F-09 still carry committed `04-Publishing` history; ADR-020 leaves history rewriting (`git filter-repo`) to each author's discretion rather than mandating a rewrite — a reasonable call for a tool that manages other people's creative work.

---

## 5. New Findings (this re-audit)

### N-01 — Exit-code contract drift: CONTRIBUTING says 0/1/3, the code now uses 0/1/2/3
**Severity: Low · `CONTRIBUTING.md` line 15 vs `world_doctor.sh`, `wordcount_report.sh`, `scriptorium_doctor.sh`**

The remediation introduced `exit 2` for usage errors, ambiguous world selection, and missing dependencies — a genuinely better contract than the old "everything is 1 or 3". But CONTRIBUTING.md (added by the same remediation series) declares "the 0/1/3 exit-code contract" non-negotiable, while older scripts still use `exit 3` for the missing-argument/no-GUI case and the newer ones use `exit 2` for near-identitive usage errors. The codebase is internally consistent per-script but the documented contract no longer describes it. Fix is one line (document 0/1/2/3 with semantics: 0 success, 1 runtime/diagnostic failure, 2 usage/ambiguity/deps, 3 missing argument when no GUI/TTY) — or, if 2-vs-3 unification is preferred, a small sweep. Either way, the docs and code should not disagree about a contract the project calls non-negotiable.

### N-02 — Remediation commits carry a container identity
**Severity: Info · git history**

All ten remediation commits are authored as `Z User <z@container>`, not the maintainer's GitHub identity. The commits are now public on `main`. This is cosmetic — attribution metadata only — but if the maintainer wants the history to read as their own work (it is their repository), `git rebase -i --exec 'git commit --amend --reset-author --no-edit' 9d34fae` followed by a force-push fixes it in one step. GitHub will re-associate contributions once the author email matches the account. Alternatively, leave it: an honest record that an external audit produced the patch series.

### N-03 — Deprecation nudge misses the auto-select path
**Severity: Info · `scripts/lib/worlds.sh` `resolve_world_dir` vs caller auto-select**

The legacy-root deprecation note (Q-03) fires only when a world is resolved *by name* through `~/Worlds`. When a bare invocation auto-selects the single discovered world and that world happens to live in the legacy root, no nudge is printed. One `case` statement in the callers (or a `--warn-legacy` flag checked after auto-select) closes the gap. Functionally harmless; purely a consistency polish.

### N-04 — Worker threads are non-daemon; two cheap probes stay on the GUI thread
**Severity: Info · `scripts/scriptorium_app.py`**

F-04's core fix is correct: every long operation now runs on a worker thread and marshals UI updates through `GLib.idle_add` — the canonical pattern. Two residuals remain. The worker threads are created without `daemon=True`, so quitting the app mid-backup leaves the process alive until the subprocess finishes (the window closes, the process lingers seconds later). And the external-app launch buttons call `flatpak info` (tens to hundreds of milliseconds) synchronously on the main thread before spawning the app — a small stutter, not a freeze. Both are one-line fixes (`daemon=True`; move the probe into the spawned command or a thread).

### N-05 — Dead legacy Calibre ID in the app's launch chain
**Severity: Info · `scripts/scriptorium_app.py` lines 1117–1118**

`on_launch_calibre` tries the correct ID first, then falls back to `com.calibredesk.calibre` — an ID that has never existed on Flathub, so the branch can never match. Unlike the original F-01 (where the wrong ID was the *only* path and broke installation), this is harmless dead code kept as a compatibility shim. Deleting the `elif` (or keeping it with a comment saying it is intentionally inert) is optional tidying.

---

## 6. CI/CD, Dependencies, Hygiene

**CI verification.** The workflow was reviewed end-to-end. Actions pinned by full SHA (`checkout@11bd719…` v4.2.2, `setup-python@4237552…` v5.4.0, `setup-typst@65c09e3…` v4.0.1); Typst pinned to `0.13` with an in-file rationale; `permissions: contents: read`; weekly Monday drift run; shellcheck scope now includes `lib/` and `tests/`; the bash-syntax step and the harness were restructured to be fail-closed, eliminating the CI-side copy of the F-02 pattern. The local re-run of the exact CI shellcheck invocation (0.11.0, `-S warning`, same file list) passes with zero findings.

**Dependencies.** No new runtime dependencies were introduced by the remediation — `worlds.sh` uses bash builtins plus `find`, and the app uses the Python stdlib `threading` it already imported. The Typst digest gate now consumes the GitHub API asset `digest` field that the original audit web-verified as available since June 2025.

**Hygiene.** No build artifacts, caches, images, or archives are tracked; the largest tracked file is the 53 KB GTK app. The secrets scan over all tracked text files returns zero true positives (matches were documentation prose and the sanitize-`token` naming in `worlds.sh` comments). README links the new AUDIT.md, CONTRIBUTING.md, and SECURITY.md; ADR-020 records the remediation decisions with unusual candor, including the 04-Publishing migration path and the Obsidian licensing clarification ("no data locks; one optional proprietary tool") that the original audit requested.

---

## 7. Updated Scorecard

| Dimension | Baseline (9d34fae) | Current (5058055) | Notes |
| :--- | :--- | :--- | :--- |
| Security | 6/10 | **9/10** | Injection surfaces eliminated; installer fail-closed; archive gate; residual: integrity-vs-authenticity (documented) |
| Functional correctness | 7/10 | **9.5/10** | F-01/F-02/F-05/F-06 verified fixed by execution; residual: N-04 polish |
| Code quality & architecture | 7/10 | **9/10** | Shared discovery lib, dedup, ADR-020; residual: Q-02 deliberately lightweight, N-01 contract drift |
| CI/CD & pipeline | 8/10 | **9.5/10** | Least privilege, pinned toolchain, drift schedule, tests linted |
| Repository hygiene & docs | 9/10 | **9.5/10** | CONTRIBUTING + disclosure added; residual: N-02 authorship |
| **Overall** | **B+ (7.5/10)** | **A (9.0/10)** | Weighted toward security and correctness |

The half-point held back from a perfect-adjacent score is deliberate: N-01 is a real (if trivial) documentation defect that the remediation introduced itself; two hardening paths (Typst digest gate at runtime, GTK async under a live display) were verified by code review and partial execution rather than full runtime exercise in this sandbox; and the Q-02 deferral, while reasonable, means the 17-script CLI boilerplate the original audit measured still exists. None of these blocks any reasonable use of the platform.

---

## 8. Recommendations (in priority order)

1. **Fix N-01 now** — one line in CONTRIBUTING.md (or a 2/3 unification sweep). A project that calls its exit-code contract non-negotiable should not ship docs contradicting it.
2. **Decide on N-02** — either reset authorship on the ten commits (single rebase command, requires force-push) or accept the external-audit attribution as an honest historical record.
3. **Apply the two one-line GUI polish fixes (N-04)** — `daemon=True` on worker threads; move the `flatpak info` probe off the click path.
4. **Close N-03 and N-05 opportunistically** — legacy nudge on auto-select; delete or annotate the dead Calibre `elif`.
5. **Keep the discipline that made this remediation verifiable** — finding-ID traceability in commits, ADRs for scope decisions, adversarial tests in the suites. The next auditor (or future you) inherits a repo where claims are checkable, which is precisely why this re-audit could be completed with confidence.

---

## 9. Verification Evidence Log

All commands executed against the fresh clone (`5058055`) on 2026-09-17:

| Command / check | Result |
| :--- | :--- |
| `git clone` (fresh) + `git status` | Clean tree; HEAD `5058055` = `origin/main`; 98 tracked files |
| `bash scripts/verify.sh` | ALL-CHECKS-PASS (stages 4, 6d SKIP — Typst not installed in sandbox) |
| `bash tests/test_audit_fixes.sh` | 6/6 targeted tests pass |
| `bash tests/test_deep_audit.sh` | All 8 sections pass |
| `bash tests/test_concordance_edge_cases.sh` | Pass |
| `bash -n` over `scripts/*.sh`, `scripts/lib/*.sh`, `scripts/scriptorium`, `tests/*.sh` | All pass |
| `shellcheck 0.11.0 -S warning scripts/*.sh scripts/lib/*.sh scripts/scriptorium tests/*.sh` | 0 findings (CI parity) |
| Hostile-filename injection probe (`Evil'''{{import os}}.md`) | Valid JSON; no code execution |
| Crafted traversal archive (`../../escaped.txt` member) | Refused, exit 1 |
| Crafted planted-hook archive (`.git/hooks/pre-commit`) | Refused, exit 1 |
| Empty-manuscript export | Hard-fail, exit 1, no fabricated artifacts |
| Hybrid role `Major Rival` in Dramatis Personae | Listed exactly once (Antagonists) |
| Harness breakage drills (syntax / JSON / schema) | Each exits 1 with specific error |
| Multi-world bare doctor/wordcount | Lists with labels, exit 2 |
| Legacy by-name resolution | Works + deprecation nudge on stderr |
| Secrets scan (api_key/secret/password/token/AKIA/ghp_/private-key) | 0 true positives |
| Tracked artifacts scan (`__pycache__`/`.pyc`/archives/images) | None |
| `git log` authorship check | 10 commits, `Z User <z@container>` (see N-02) |
