# Deprecation & Schema Evolution Policy

This document defines the deprecation lifecycle, backward-compatibility commitments, and schema migration rules for **Ars Arcanum**.

---

## 1. Deprecation Lifecycle

Ars Arcanum adheres to Semantic Versioning (SemVer 2.0.0):

1. **Deprecation Notice**: Any feature, CLI flag, or configuration key scheduled for removal will be marked as deprecated in release notes and accompanied by a runtime warning for at least **one minor release cycle** before removal.
2. **Schema Stability**: File schemas (`universe.yaml`, `world.yaml`, `manuscript.yaml`) include an explicit `schema_version` attribute. Older schemas are automatically detected and upgraded via `arcanum migrate`.
3. **Removal in Major Versions**: Breaking architectural changes and removal of deprecated APIs/interfaces only occur across major version boundaries (e.g., `1.x.x` → `2.0.0`).

---

## 2. Deprecation Schedule

| Feature / Interface | Status | Deprecated In | Removal Target | Recommended Replacement |
| :--- | :--- | :--- | :--- | :--- |
| `05-Backups/` root directory | Deprecated | v1.6.0 | v2.0.0 | `Backups/` root directory (automatically aliased) |
| Hardcoded `maintainers@arsarcanum.local` Git authoring | Removed | v1.6.0 | v1.6.0 | Dynamic host Git identity / author profile |
| Unpinned Typst compiler invocation | Removed | v1.6.0 | v1.6.0 | Pinned Typst v0.13.0 with SHA-256 verification |
| In-place destructive DOCX sync | Removed | v1.6.0 | v1.6.0 | 3-way hash tracking & `.conflict.md` branch isolation |

---

## 3. Migration Commands

To safely upgrade manuscript projects and schemas:

```bash
# Scan manuscript or world bible for outdated schemas
arcanum doctor

# Migrate manuscript and world bible metadata to current schema
arcanum migrate --dry-run
arcanum migrate --apply
```
