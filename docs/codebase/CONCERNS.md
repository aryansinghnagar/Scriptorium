# Codebase Concerns

## Core Sections (Required)

### 1) Top Risks (Prioritized)

| Severity | Concern | Evidence | Impact | Suggested action |
|----------|---------|----------|--------|------------------|
| **Medium** | Flatpak App ID & Runtime Availability on Custom Linux Distributions | [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L235-L260), [`docs/COMPATIBILITY.md`](file:///docs/COMPATIBILITY.md#L24-L37) | Non-Mint/Debian distros without Flatpak/Flathub pre-configured will fail to install Obsidian or novelWriter unless Flatpak remote is initialized. | Maintain the `--force` flag fallback with clear guidance in `docs/SUPPORT_MATRIX.md`. |
| **Low** | Upstream Typst Breaking Syntax Changes across Major Versions | [`templates/typst/book_template.typ`](file:///templates/typst/book_template.typ#L1-L80) | Typst syntax evolution (e.g. `show` rules, font loading) could require template syntax adjustments when upgrading Typst binary majors. | Pin Typst binary version in CI and installer; maintain version test in `verify.sh`. |
| **Low** | Obsidian Community Plugin Format Drift | [`templates/world-bible/.obsidian/`](file:///templates/world-bible/.obsidian/community-plugins.json#L1-L15) | Third-party Obsidian plugins (Dataview, Metadata Menu) updating internal settings schemas. | Lock plugin configurations in `templates/world-bible/.obsidian/` and test via `world_doctor.sh`. |

### 2) Technical Debt

| Debt item | Why it exists | Where | Risk if ignored | Suggested fix |
|-----------|---------------|-------|-----------------|---------------|
| **Legacy `~/Worlds` root discovery backward compatibility** | Scriptorium originally stored worlds directly in `~/Worlds/` before introducing the 3-tier Universe hierarchy (`~/Universes/<Universe>/<World>`). | [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L50-L100) | Code complexity in discovery loop resolving both depth-2, depth-3, and legacy root paths. | Keep deprecation warning (`warn_if_legacy_root`) in place and provide migration wizard in GTK Control Center. |
| **Dual GUI Implementation (GTK 3 PyGObject vs Zenity)** | Zenity script exists as a minimal fallback when GTK 3 / Python 3 is unavailable. | [`scripts/control_center.sh`](file:///scripts/control_center.sh#L1-L120) vs [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L1-L150) | Feature divergence between GTK 3 app (5 tabs, visual scene inspector) and Zenity dialogs (simple list picker). | Maintain Zenity script purely as an emergency fallback while centralizing new features in `scriptorium_app.py`. |

### 3) Security Concerns

| Risk | OWASP category | Evidence | Current mitigation | Gap |
|------|----------------|----------|--------------------|-----|
| **Installer Privilege Surface (`sudo`)** | A05:2021 Security Misconfiguration | [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L130-L240), [`SECURITY.md`](file:///SECURITY.md#L12-L22) | `setup_scriptorium.sh` restricts `sudo` to explicitly named APT packages and verified `/usr/local/bin/typst` binary installation; full `--dry-run` simulation mode provided. | Scriptorium requires root only for initial system package provisioning; daily writing runs unprivileged. |
| **Arbitrary Archive Extraction in Restore Engine** | A01:2021 Broken Access Control | [`scripts/restore_world.sh`](file:///scripts/restore_world.sh#L1-L90) | `restore_world.sh` validates archive contents before extraction, refusing tarballs containing path traversal (`..`) sequences or git hook scripts. | None; fail-closed validation verified in test suite. |
| **Untrusted Binary Download (Typst)** | A08:2021 Software & Data Integrity Failures | [`scripts/setup_scriptorium.sh`](file:///scripts/setup_scriptorium.sh#L210-L270) | `setup_scriptorium.sh` validates SHA-256 digest against official GitHub API releases and aborts with `TYPST_OK=0` if digest is unavailable ([ADR-023](file:///docs/ARCHITECTURE.md#adr-023-forensic-audit-hardening--fail-closed-security-depth-3-universe-discovery-iso-8601-chronology-and-intra-manuscript-link-resolution)). | None; fail-closed behavior enforced. |

### 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---------|----------|-----------------|-------------|-----------------------|
| **World Doctor Full-Scan on Enormous Vaults** | [`scripts/world_doctor.sh`](file:///scripts/world_doctor.sh#L1-L577) | Shell-based regex parsing across hundreds of Markdown notes takes 1-2 seconds. | Vaults with >10,000 notes could see doctor passes slow down to 5-10 seconds. | Add optional Python-based accelerated scanner for multi-million word fantasy bibles. |
| **Live Word Count Tree Rollups in Desktop GUI** | [`scripts/scriptorium_app.py`](file:///scripts/scriptorium_app.py#L400-L550) | Word counts recalculated upon manuscript selection. | Instantaneous for standard multi-book manuscripts (100k-500k words); slight delay on massive omnibuses (>1M words). | Implement mtime-based word count caching in the Python GUI layer. |

### 5) Fragile/High-Churn Areas

| Area | Why fragile | Churn signal | Safe change strategy |
|------|-------------|-------------|----------------------|
| **`scripts/world_doctor.sh`** | Complex regex matching for multi-era timelines, ISO 8601 parsing, frontmatter YAML extraction, and `WLD-108` lore cross-references. | 10 commits in last 90 days | Always run `bash tests/test_concordance_edge_cases.sh` and `bash tests/test_audit_fixes.sh` before modifying regex rules. |
| **`scripts/save_snapshot.sh`** | Git concurrency retry handling, multi-tier repository indexing, and dirty working tree detection. | 10 commits in last 90 days | Run `bash scripts/verify.sh` Stage 6 to test multi-tier repository snapshotting across 0-world and multi-world projects. |
| **`scripts/lib/worlds.sh`** | Single source of truth for universe, world, and manuscript path discovery sourced by 11 scripts. | High central dependency | Verify all depth-2, depth-3, and legacy root discovery paths using `tests/test_audit_fixes.sh` Test 15. |
| **`scripts/scriptorium_app.py`** | PyGObject GTK 3 UI binding, multi-threading worker daemon management, and scene tag in-place editing. | 8 commits in last 90 days | Validate syntax with `python3 -m py_compile scripts/scriptorium_app.py` and test UI callbacks asynchronously. |

### 6) `[ASK USER]` Questions

1. `[ASK USER]` Would you like to add an optional, local lightweight semantic continuity checking engine (e.g. using local embeddings / small models) in a future release?
2. `[ASK USER]` Should the desktop GUI (`scripts/scriptorium_app.py`) support direct packaging as a Flatpak or Debian `.deb` package in addition to the repository setup installer?
3. `[ASK USER]` Are there any additional speculative fiction taxonomy domains (e.g. Flora/Herbalism, Astral Navigation, Genealogy Trees) you would like elevated from guide recommendations to core `fileClasses`?

### 7) Evidence

- [`docs/audits/2026-09-16-external-audit.md`](file:///docs/audits/2026-09-16-external-audit.md#L1-L466)
- [`docs/audits/2026-09-17-remediation-re-audit.md`](file:///docs/audits/2026-09-17-remediation-re-audit.md#L1-L224)
- [`scripts/world_doctor.sh`](file:///scripts/world_doctor.sh#L1-L577)
- [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh#L1-L247)
- [`scripts/save_snapshot.sh`](file:///scripts/save_snapshot.sh#L1-L233)

## Extended Sections (Optional)

### Historical Remediation Summary

All 22 findings from the September 2026 External Audit were remediated and verified in the subsequent Re-Audit (Grade A, 9.0/10 rating), resolving path traversal vulnerabilities, unmasked test harness stages, hardcoded paths, Flathub application IDs, and discovery logic duplication.
