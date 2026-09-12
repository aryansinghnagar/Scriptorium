# Scriptorium Multi-Lens Audit — Deliverables

**Target**: github.com/aryansinghnagar/Scriptorium @ `1a048fb` (46 files; 5 shell scripts ≈ 721 LOC; Typst book template; Obsidian/novelWriter starter packs; desktop launchers; LeechBlock/Déjà-Dup/XFCE focus configs)

**Method**: three isolated lenses, run in parallel and cross-checked so no remediation conflicts:
Lens 1 — senior systems engineer (Unix philosophy, CLI ergonomics, portability, failure modes);
Lens 2 — strict AppSec engineer (injection vectors, unsanitized I/O, supply chain, error/signal handling);
Lens 3 — systems designer & worldbuilding-tooling specialist (data model fit for interconnected entities, authorial friction, high-value features).

Every defect listed below was **reproduced empirically** before being written down; every patch was verified with `git apply --check` on a pristine clone, then the fully patched tree re-ran the complete functional battery (ALL-CHECKS-PASS).

---

## Contents

| Path | What it is |
|---|---|
| `Ars-Scriptorium-Multi-Lens-Audit.pdf` | Consolidated audit report (this is the main deliverable) |
| `patches/01…08*.patch` | Remediation patch series, ordered, applies cleanly one-by-one |
| `evidence/01…05*.txt` + charts | Reproduction transcripts (pristine failures + patched-tree verification sweep) + supporting charts |

## Defect Ledger (summary)

| ID | Severity | Finding | Patch |
|---|---|---|---|
| SYS-01 | **Critical** | `book_template.typ` wraps `#pagebreak(to:"odd")` inside `block()` → Typst 0.12/0.13/0.14 refuse to compile ANY book with chapters; the repo's own Definition of Done is unmet | 01 |
| SYS-02 | **Critical** | Exporter collects only `Book-01/`; every later volume (Book-02…) is **silently omitted** from PDF and EPUB | 02 |
| SEC-01 | **High** | novelWriter tags outside the 7-name strip whitelist (`@time`, `@plot`, `@entity`, custom) become pandoc **citations** → `#cite(<…>)` → hard Typst abort ("no bibliography"); on the sed fallback path the same tags become fatal label references; tags leak into the EPUB | 02 |
| SYS-03 | **High** | `.desktop` launchers use `Exec=bash -c "path"`; `bash -c` re-parses its argument → any repo/home path with spaces makes all three launchers dead on arrival | 03 |
| SYS-04 | **Medium** | `shellcheck -S warning` (the repo's own CI gate) fails on the pristine tree (SC2188); no CI runs are visible on GitHub | 02 |
| SYS-05 | **Medium** | Exit-code anarchy: user aborts, missing tools and failed compiles all exit 0; the primary artifact (PDF) can fail while the script reports success | 02/04 |
| SYS-06 | **Medium** | Scripts are un-automatable: no flags, no `--help`, `init_world.sh` aborts when stdin is not a TTY; verify.sh/CI never exercise the actual world lifecycle (which is exactly why SYS-01/02 and SEC-01 survived) | 04/05 |
| SEC-02 | **Medium** | Typst binary installed to `/usr/local/bin` from `releases/latest` with **no digest verification** (supply chain) | 07 |
| SYS-07 | **Low** | `verify.sh` writes fixed-name artifacts to shared `/tmp` (predictable paths) | 05 |
| SYS-08 | **Low** | `flatpak remote-list` (deprecated alias), `gio set metadata::trusted` (dead on modern GLib), template `"serif"`/`"EB Garamond"` unknown-family warnings | 01/03 |
| SYS-09 | **Low** | `save_snapshot.sh` dies via `set -e` when git is absent; CLI snapshot notes impossible; stale clone URL `7-Scriptorium` | 04/06 |
| — | Retracted | "41 broken ttps:// links" was a substring-grep false positive (`ttps://` matches inside `https://`); no genuinely broken URLs exist | — |

**Security posture notes**: world-name sanitization is solid (whitelist `[A-Za-z0-9_-]`, 64-char cap, traversal and injection attempts neutralized — verified); Typst string escaping and collision-safe filenames are sound; hostile-name battery found no escape. The AppSec risk here is concentrated in *robustness*, not privilege: no setuid, no network services, single-user authoring tool.

## Domain Features (Lens 3, delivered)

| ID | Feature | Patch |
|---|---|---|
| D-01 | `world_doctor.sh` — World-Bible consistency checker: broken `[[wiki-links]]`, dangling typed frontmatter references (faction/origin/leader/…), orphan notes, duplicate identities, unrenamed-template detection; `--json` machine mode; O(files+links) single-pass index | 08 |
| D-02 | `scriptorium.yaml` world manifest — flat `key: value` schema (title/author), written by `init_world.sh`, read by `export_book.sh` (CLI flags > manifest > GUI > defaults) | 02/04 |
| D-03 | `wordcount_report.sh` — per-chapter/act/volume word counts + novelWriter `@status` breakdown; `--markdown` table for the Daily Writing Log | 08 |

## Verification Matrix

| Check | Pristine | Patched |
|---|---|---|
| `typst compile preview_sample.typ` (0.12/0.13/0.14) | FAIL ×3 | PASS ×3 |
| Export PDF (with @time/@plot tags present) | FAIL (citation abort) | PASS |
| Book-02 in exported EPUB/PDF | MISSING | PRESENT |
| @time/@plot/@entity leak into EPUB | YES | STRIPPED |
| `shellcheck -S warning` (CI gate) | FAIL (SC2188) | PASS |
| Spaced-path launcher invocation | FAIL | PASS |
| Exit codes (abort=3, error=1, ok=0) | all 0 | correct |
| Non-interactive `init_world.sh NAME` | abort | works |
| `verify.sh` functional lifecycle | n/a (static only) | ALL-CHECKS-PASS |

## Applying the patches

```bash
git clone https://github.com/aryansinghnagar/Scriptorium && cd Scriptorium
for p in /path/to/patches/*.patch; do git apply --check "$p" && git apply "$p"; done
bash scripts/verify.sh   # expect: ALL-CHECKS-PASS
```

Patches are ordered and cumulative; apply in filename order. Domain tools land in `scripts/` and require only bash + python3 (both already required by `verify.sh`).
