# Changelog

All notable changes to Scriptorium are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Finding IDs
(`F-xx`, `S-xx`, `Q-xx`, `C-xx`, `H-xx`, `N-xx`) reference the committed audit
trail in [docs/audits/](docs/audits/); scope decisions behind each wave are
recorded as ADR-020 and ADR-021 in [docs/meta/decisions.md](docs/meta/decisions.md).

## [Unreleased]

### Added
- `scripts/lib/worlds.sh` — shared world-discovery library (discover, resolve,
  universe labels, name sanitization, GUI detection), sourced by 11 entry-point
  scripts; removes ~300 lines of copy-pasted discovery logic and the
  identity-based "Standalone" heuristics (Q-01, F-03).
- `CONTRIBUTING.md` — ground rules, dev setup, the quality gate, exit-code
  contract, commit style, and submission flow (H-01).
- `SECURITY.md` — installer privilege-surface disclosure enumerating every
  `sudo` operation, plus the private vulnerability-reporting process (S-05).
- `CHANGELOG.md` — this file.
- CI hardening: least-privilege `permissions: contents: read`, Typst toolchain
  pinned to `0.13` with a documented bump policy, weekly drift run, and
  `tests/*.sh` joined to the ShellCheck scope (C-01, C-02, C-03).
- Audit trail committed under `docs/audits/`: the line-by-line external audit
  (22 findings) and the independent re-audit that verified the remediation
  (grade A, 9.0/10, zero regressions).
- Regression coverage: hostile-filename injection probe, archive
  traversal/hook-planting refusal, empty-manuscript export guard, hybrid-role
  Dramatis Personae dedup, multi-world resolution, and the legacy-root
  auto-select nudge (Test 7).

### Changed
- Repository root decluttered to the standard OSS entry set (README, CHANGELOG,
  LICENSE, CONTRIBUTING, SECURITY): planning/meta documents moved to
  `docs/meta/`, audit reports moved to date-stamped files under `docs/audits/`,
  and all cross-links updated (ADR-021).
- The exit-code contract is documented as the four values the code actually
  uses — 0 success, 1 runtime/diagnostic failure, 2 usage/environment error,
  3 nothing to act on — replacing the stale "0/1/3" wording (N-01).
- A bare invocation that auto-selects a single world living under the legacy
  `~/Worlds` root now prints the same deprecation nudge as by-name resolution;
  the message is centralized in `warn_if_legacy_root` (Q-03, N-03).
- GTK app threading polish: thread creation centralized in `_start_worker`
  with `daemon=True` so quitting mid-operation no longer leaves the process
  lingering; the five external-app launch chains (and their `flatpak info` /
  `which` probes) run on daemon workers instead of the GUI thread; snapshot
  default notes use `datetime.now()` instead of a `date` subprocess (F-04, N-04).
- The Typst installer requires a matching GitHub-published SHA-256 digest
  before `sudo install` and refuses otherwise; GitHub API rate-limiting now
  warns explicitly instead of silently skipping (S-01).
- Backup metadata is written with `json.dump` instead of an unescaped heredoc
  (F-07); wordcount reports an explicit warning when a file exceeds the 8 MB
  read cap instead of truncating silently (F-08); manuscript snapshotting
  surfaces git index-lock contention instead of dropping commits silently (Q-04).

### Fixed
- Calibre installs under its real Flathub ID `com.calibre_ebook.calibre`
  (the previous ID never existed, so setup could never install Calibre)
  across setup, doctor, uninstaller, app, and both compatibility docs (F-01).
- The verification harness fails closed: stages report failures instead of
  being swallowed by `set -e` + `cmd && echo` chains, and the CI
  syntax-validation step follows the same pattern (F-02).
- World-doctor JSON crosses the shell/Python boundary via stdin
  (`json.load(sys.stdin)`) instead of interpolation into `python3 -c` source,
  eliminating code injection through crafted filenames (S-02).
- All doctor subprocess invocations use list argv without `shell=True` (S-03).
- Archive restore is hardened: absolute paths, `..` traversal, unexpected root
  entries, and non-sample `.git/hooks` members are refused before extraction;
  extraction neutralizes ownership/permission restoration (S-04).
- Bare doctor/wordcount invocations discover worlds (auto-select when exactly
  one exists, list with universe labels and exit 2 when ambiguous) instead of
  defaulting to `~/Worlds`, which is a container of worlds (F-05).
- Exporting a fully empty manuscript hard-fails with "no manuscript content
  found" instead of fabricating sample prose (F-06).
- `04-Publishing/` outputs are ignored by the root and generated world
  `.gitignore`s so compiled PDFs/EPUBs stop accumulating in snapshot history (F-09).
- Hybrid roles (e.g. "Major Rival") appear exactly once in the Dramatis
  Personae under the documented precedence (F-10).

### Removed
- Dead legacy Calibre Flathub ID (`com.calibredesk.calibre`) from the app's
  launch chain — a branch that could never match (N-05).
- Hardcoded developer username (`"aryan"`) heuristics from all scripts,
  replaced by structural path-prefix detection (F-03).
- Four pre-existing dead `PROJECT_ROOT` variable declarations that would have
  failed the tightened ShellCheck gate (SC2034).

### Security
- CI actions pinned by full commit SHA; workflow limited to `contents: read`.
- Co-located `sha256.manifest` backups are documented as integrity-only
  (bit-rot protection), not authenticity — stated plainly in SECURITY.md and
  the backup code comments.
