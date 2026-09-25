# Ars Arcanum — Cosmos Archive Freeze & Cryptographic Provenance Guide
> **Engine**: `scripts/lib/archive_freeze.py` | **CLI**: `arcanum freeze`, `arcanum verify-archive`

---

## 1. Overview & Purpose

The **Cosmos Archive Freeze & Provenance Sealer** provides authors with an immutable, cryptographic seal over their entire worldbuilding vault, manuscript drafts, and configuration trees. By calculating deterministic SHA-256 and SHA-512 digests for every individual file alongside a master Merkle-style root hash, it establishes mathematical proof of authorship milestones, prevents bit-rot, and detects unauthorized modifications.

### Core Capabilities
- **Deterministic Cryptographic Hashing**: Hashes all canonical `.md`, `.yaml`, `.json`, and source files in sorted order.
- **Provenance Seal Generation**: Generates `PROVENANCE_SEAL.md` (human-readable attestation table with word counts and truncated hashes) and `ARCHIVE_MANIFEST.json` (machine-verifiable manifest).
- **Post-Freeze Audit & Tamper Detection**:
  - `FRZ-101`: **Checksum Mismatch / Tampered File**: File modified after freeze.
  - `FRZ-102`: **Missing File**: File recorded in manifest was deleted from disk.
  - `FRZ-103`: **Untracked File**: New file added to vault post-freeze.

---

## 2. CLI Command Reference

### Freezing a Cosmos or Manuscript Project
```bash
# Freeze working vault and write ARCHIVE_MANIFEST.json and PROVENANCE_SEAL.md
arcanum freeze Universes/Eldoria-Cosmos

# Custom output directory
arcanum freeze Manuscripts/Book-01 --output-dir Releases/Milestone-01
```

### Verifying Vault Integrity
```bash
# Verify vault files against an existing manifest
arcanum freeze Universes/Eldoria-Cosmos --verify ARCHIVE_MANIFEST.json

# Machine-readable JSON output for CI pipelines
arcanum freeze Universes/Eldoria-Cosmos --verify ARCHIVE_MANIFEST.json --json
```

---

## 3. Diagnostic Codes Reference

| Code | Severity | Description | Remediation |
|:---|:---|:---|:---|
| `FRZ-101` | **ERROR** | **Checksum Mismatch**: File content differs from recorded SHA-256 digest in the freeze manifest. | Investigate unauthorized file changes or restore previous version from backup. |
| `FRZ-102` | **ERROR** | **Missing File**: File present during freeze was deleted from disk. | Restore file from backup snapshot or re-freeze if deletion was intentional. |
| `FRZ-103` | **WARNING** | **Untracked File**: New file introduced to vault after freeze manifest generation. | Review new file and generate a fresh milestone freeze if intended. |

---

## 4. Architectural Invariants

- **100% Offline & Zero-Pip**: Uses standard library `hashlib`, `json`, `dataclasses`, and `re`.
- **Atomic File Writing**: Both manifest and seal files are written via `atomic_write()` from `_bootstrap.py`.
- **Reproducible Sorting**: Files are processed in canonical path-sorted order ensuring identical hashes across operating systems.
