# Ars Arcanum — Manuscript Revision Density & Churn Heatmap Guide
> **Engine**: `scripts/lib/revision_heatmap.py` | **CLI**: `arcanum revision-heatmap`, `arcanum churn`

---

## 1. Overview & Purpose

The **Manuscript Revision Density & Churn Heatmap Engine** provides quantitative, snapshot-based visibility into writing and revision activity across chapters. By comparing the active working draft against milestone snapshots (from `Backups/` or explicit snapshot directories), it calculates edit churn (insertions + deletions) and flags chapters experiencing structural instability or neglect.

### Core Capabilities
- **Line-Level Snapshot Comparison**: Compares active markdown files against previous drafts using standard library `difflib`.
- **Churn Metric Normalization**: Computes raw churn score ($I + D$) and normalized churn ratio $\frac{I + D}{\max(\text{words}, 1)}$.
- **Outlier Diagnostic Codes**:
  - `REV-101`: **Over-Revised Chapter** (churn ratio $> 3\times$ manuscript average).
  - `REV-102`: **Pristine / Untouched Draft** (zero insertions or deletions on chapters $> 50$ words with an active snapshot).
- **Offline CSP-Compliant HTML Heatmap**: Visual color-graded bars (green, amber, red) and summary analytics without network dependencies.

---

## 2. Diagnostic Codes Reference

| Code | Severity | Description | Remediation |
|:---|:---|:---|:---|
| `REV-101` | **WARNING** | **Over-Revised Chapter**: Churn ratio significantly exceeds the manuscript average, indicating rewriting loops or structural instability. | Lock scene goal and freeze draft scope before making further structural passes. |
| `REV-102` | **INFO** | **Pristine / Untouched Draft**: Chapter has a prior snapshot but zero line modifications despite surrounding revisions. | Review scene for continuity drift or outdated worldbuilding elements. |

---

## 3. CLI Command Reference

### Basic Churn Audit
```bash
# Scan manuscript against default Backups/ directory
arcanum revision-heatmap Manuscripts/Book-01/Draft-01

# Aliases
arcanum churn Manuscripts/Book-01/Draft-01
arcanum revision-density Manuscripts/Book-01/Draft-01
```

### Comparing Against a Specific Snapshot Directory
```bash
arcanum revision-heatmap Manuscripts/Book-01/Draft-02 --snapshot-dir Manuscripts/Book-01/Draft-01
```

### Exporting Standalone HTML Heatmap
```bash
arcanum revision-heatmap Manuscripts/Book-01/Draft-01 --export-html Reports/revision_heatmap.html
```

### Machine-Readable JSON Mode
```bash
arcanum revision-heatmap Manuscripts/Book-01/Draft-01 --json
```

---

## 4. Architectural Invariants

- **100% Offline & Zero-Pip**: Utilizes Python standard library `difflib`, `json`, `dataclasses`, and `re`.
- **Atomic File Writing**: HTML exports use `atomic_write()` from `_bootstrap.py`.
- **Strict Content Security Policy**:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
