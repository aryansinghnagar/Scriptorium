# Ars Arcanum (Scriptorium) — Failure Log & Risk Register

## Failure Log & Incident Postmortems

### Incident 2026-09-21: Self-Referential Backup Digest Bug (Finding X-09)
- **Symptom**: `backup_world.sh` calculated SHA-256 after `tar -czf` without running an archive structure check. If tar suffered a truncated write, the partial archive would pass its own hash.
- **Root Cause**: Hash computation was executed over disk bytes without verifying exit codes or running `tar -tzf`.
- **Remediation**: Added `tar -tzf "${ARCHIVE_TAR}" >/dev/null` validation immediately after creation, aborting and deleting corrupt archives if validation fails.

### Incident 2026-09-21: Runtime Cache Git Pollution (Finding X-10)
- **Symptom**: `.arcanum_cache.json` and `.sync_state.json` were tracked by Git in newly initialized worlds and manuscript directories, causing merge conflicts across machines.
- **Root Cause**: `.gitignore` templates in `init_world.sh` and `init_manuscript.sh` omitted cache file patterns.
- **Remediation**: Added `.arcanum_cache.json`, `.sync_state.json`, and `*.lock` to template files, root `.gitignore`, and added auto-remediation to `scripts/lib/migrate.py`.

---

## Active Risk Register

| Risk ID | Description | Severity | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | Obsidian Plugin Hash Drift | High | `tests/test_supply_chain.py` running in CI on every commit | Mitigated |
| **R-02** | Backup Archive Corruption | Critical | `tar -tzf` pre-verification in `backup_world.sh` | Mitigated |
| **R-03** | WCAG Contrast Failure in Diffs | Medium | Palette refined & verified via `tests/test_wcag_contrast.py` | Mitigated |
| **R-04** | Multi-Tier Git Embedded Gitlink Dangling Pointers | High | Formalize `.gitmodules` submodule tracking in Phase 2 | Planned (P2-M4) |
| **R-05** | `world_doctor` Cyclomatic Complexity (74) | High | Decompose `check_world` into modular category checkers | Planned (P1-M2) |
