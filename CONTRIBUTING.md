# Contributing to Scriptorium

Thank you for considering a contribution. Scriptorium is an open-source,
audit-verified project with strict quality gates and a standardized exit-code
contract. This guide is deliberately short and practical.

## Ground rules

- **Target platforms**: Linux Mint 21/22 (XFCE) and Debian 12/13. Everything
  else must degrade gracefully, not crash.
- **Design invariants** live in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
  [docs/ROADMAP.md](docs/ROADMAP.md) — read both before changing scripts. In
  particular: NUL-delimited filename handling, transactional directory
  scaffolding, the exit-code contract below, and "safe handling of arbitrary
  filenames" are non-negotiable.
- **Architecture history** is recorded as ADRs in
  [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
  If your change reverses or extends a recorded decision, add a new ADR rather
  than editing an old one.
- **No secrets, no personal paths**: never hardcode usernames, absolute home
  paths, or credentials. Standalone-world detection must stay structural
  (path prefix), not identity-based.

### Exit-code contract (N-01)

Scripts exit `0` on success and non-zero otherwise, with four documented
meanings. Each script's header comment remains the authoritative per-script
contract; when you add a script, document its codes there and keep them
within this table:

| Code | Meaning |
| :--- | :--- |
| `0` | success |
| `1` | runtime or diagnostic failure — the operation ran and failed, or reported findings |
| `2` | usage or environment error — bad option, unknown world, ambiguous world selection, missing dependency |
| `3` | nothing to act on — required argument absent with no GUI/TTY fallback, or the user aborted an interactive selection |

## Development setup

```bash
git clone https://github.com/aryansinghnagar/Scriptorium.git
cd Scriptorium
bash scripts/setup_scriptorium.sh --dry-run   # inspect what a real install does
```

You do not need the full toolchain to iterate: the test suites sandbox
`HOME` and unset `DISPLAY`, so they run headlessly with just `git`, `pandoc`,
and `python3` installed.

## Before you submit — the quality gate

Every change must pass all of these, in this order:

```bash
bash -n scripts/*.sh scripts/lib/*.sh scripts/scriptorium   # syntax
bash scripts/verify.sh                                       # 7-stage harness
bash tests/test_audit_fixes.sh
bash tests/test_deep_audit.sh
bash tests/test_concordance_edge_cases.sh
bash tests/test_audit_claude_improvements.sh
```

`verify.sh` is the project's core quality gate — it must be able to *fail*
(it fails closed by design; if you find a stage that cannot fail, that is a
bug worth reporting). When adding new scripts, wire them into the harness's
stage 1 and the CI lint lists.

New shell code should pass `shellcheck -S warning`. New Python code should
pass `python3 -m py_compile`. When crossing the shell/Python boundary, pass
data via **stdin or argv** — never interpolate values into `python3 -c`
source strings.

## Commit style

Conventional commits, atomic scopes — e.g. `fix(export): ...`,
`feat(concordance): ...`, `ci: ...`, `docs(meta): ...`. Reference the
affected component in parentheses and explain *why* in the body, not just
*what*.

## Submitting

1. Fork, branch from `main`.
2. Make your change; run the full quality gate above.
3. Open a pull request against `main` describing the motivation, the change,
   and the verification output (a pasted `ALL-CHECKS-PASS` goes a long way).

## Reporting bugs and security issues

- Ordinary bugs: GitHub issues with reproduction steps.
- **Security vulnerabilities**: follow the private-disclosure process in
  [SECURITY.md](SECURITY.md) — please do not open public issues for
  undisclosed vulnerabilities.
