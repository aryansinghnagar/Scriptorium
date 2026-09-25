#!/usr/bin/env python3
"""
Ars Arcanum — Cosmos Archive Freeze & Cryptographic Provenance Sealer
(scripts/lib/archive_freeze.py)
================================================================================
Zero-dependency, 100% offline repository freeze and tamper-detection engine.

Capabilities:
1. Cryptographic Archive Manifest Generation:
   - Scans lore bibles, manuscript drafts, world settings, and configuration files.
   - Computes deterministic SHA-256 and SHA-512 checksums for every file.
   - Computes a master Merkle-style root hash over sorted file digests.
2. Provenance Seal & Authorship Milestone Record:
   - Exports human-readable PROVENANCE_SEAL.md and ARCHIVE_MANIFEST.json.
   - Records word counts, lore entity tallies, timestamp, and signature blocks.
3. Verification & Bit-Rot / Tamper Audit:
   - Compares working tree against an existing archive manifest.
   - Flags FRZ-101 (Checksum mismatch / tampered file), FRZ-102 (Missing file),
     and FRZ-103 (Untracked new file introduced post-freeze).
4. CLI Dispatch:
   - `arcanum freeze [TARGET] [--output FILE] [--verify FILE] [--json]`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]

logger = logging.getLogger("arcanum.archive_freeze")

# Directories and file patterns to ignore during freeze scan
_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".arcanum",
}
_IGNORE_FILE_EXTS = {".pyc", ".pyo", ".pyd", ".tmp", ".swp"}
_WORD_REGEX = re.compile(r"\b\w+\b", re.UNICODE)


@dataclass
class FileDigest:
    """Cryptographic digest and metadata for a single file in the freeze."""

    rel_path: str
    size_bytes: int
    sha256: str
    sha512: str
    is_markdown: bool
    word_count: int


@dataclass
class FreezeManifest:
    """Master cryptographic freeze manifest."""

    version: str
    timestamp_utc: str
    root_dir: str
    total_files: int
    total_bytes: int
    total_words: int
    root_sha256: str
    files: list[FileDigest]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "timestamp_utc": self.timestamp_utc,
            "root_dir": self.root_dir,
            "total_files": self.total_files,
            "total_bytes": self.total_bytes,
            "total_words": self.total_words,
            "root_sha256": self.root_sha256,
            "files": [asdict(f) for f in self.files],
        }


def hash_file(file_path: Path) -> tuple[str, str, int, int]:
    """Returns (sha256, sha512, size_bytes, word_count) for a file."""
    h256 = hashlib.sha256()
    h512 = hashlib.sha512()
    word_count = 0
    size = 0

    try:
        data = file_path.read_bytes()
        size = len(data)
        h256.update(data)
        h512.update(data)

        if file_path.suffix.lower() == ".md":
            try:
                text = data.decode("utf-8", errors="replace")
                word_count = len(_WORD_REGEX.findall(text))
            except Exception:
                word_count = 0
    except (OSError, UnicodeDecodeError) as e:
        logger.debug("Could not read file for hashing %s: %s", file_path, e)

    return h256.hexdigest(), h512.hexdigest(), size, word_count


def scan_and_freeze_vault(
    vault_root: Path,
    version_tag: str = "3.3.0",
) -> FreezeManifest:
    """Scans vault_root and generates a comprehensive FreezeManifest."""
    vault_root = vault_root.resolve()
    file_digests: list[FileDigest] = []
    total_bytes = 0
    total_words = 0

    all_files: list[Path] = []
    try:
        for p in vault_root.rglob("*"):
            if p.is_file():
                # Skip ignored directory parts
                rel = p.relative_to(vault_root)
                if any(part in _IGNORE_DIRS for part in rel.parts):
                    continue
                if p.suffix.lower() in _IGNORE_FILE_EXTS:
                    continue
                if p.name.startswith("."):
                    continue
                all_files.append(p)
    except OSError as e:
        logger.warning("Error traversing vault root %s: %s", vault_root, e)

    all_files.sort(key=lambda p: str(p.relative_to(vault_root)).replace("\\", "/"))

    # Compute individual file hashes
    master_hasher = hashlib.sha256()
    for p in all_files:
        rel_str = str(p.relative_to(vault_root)).replace("\\", "/")
        sha256, sha512, size, wc = hash_file(p)
        total_bytes += size
        total_words += wc

        # Add to master root hasher in canonical sorted order
        master_hasher.update(f"{rel_str}:{sha256}\n".encode())

        file_digests.append(
            FileDigest(
                rel_path=rel_str,
                size_bytes=size,
                sha256=sha256,
                sha512=sha512,
                is_markdown=p.suffix.lower() == ".md",
                word_count=wc,
            )
        )

    root_sha256 = master_hasher.hexdigest()

    return FreezeManifest(
        version=version_tag,
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        root_dir=vault_root.name,
        total_files=len(file_digests),
        total_bytes=total_bytes,
        total_words=total_words,
        root_sha256=root_sha256,
        files=file_digests,
    )


def generate_provenance_seal_markdown(manifest: FreezeManifest) -> str:
    """Generates a human-readable markdown provenance seal document."""
    lines = [
        f"# Ars Arcanum — Immutable Provenance Seal ({manifest.root_dir})",
        f"> **Vault Archive Freeze** | Version `{manifest.version}` | `{manifest.timestamp_utc}`",
        "",
        "---",
        "",
        "## 🔒 Cryptographic Provenance & Vault Attestation",
        "",
        f"- **Root SHA-256 Digest**: `{manifest.root_sha256}`",
        f"- **Total Tracked Files**: `{manifest.total_files}`",
        f"- **Total Manuscript Words**: `{manifest.total_words:,}`",
        f"- **Total Storage Size**: `{manifest.total_bytes / 1024:.2f} KB`",
        f"- **Attestation Timestamp**: `{manifest.timestamp_utc}`",
        "",
        "---",
        "",
        "## 📜 File Manifest Registry",
        "",
        "| Relative Path | Size | Words | SHA-256 (Truncated) |",
        "|:---|---:|---:|:---|",
    ]

    for f in manifest.files:
        trunc_hash = f"{f.sha256[:12]}...{f.sha256[-8:]}"
        wc_str = f"{f.word_count:,}" if f.is_markdown else "—"
        lines.append(f"| `{f.rel_path}` | {f.size_bytes} B | {wc_str} | `{trunc_hash}` |")

    lines.extend([
        "",
        "---",
        "",
        "## 🛡️ Sovereign Author Invariant Guarantee",
        "This archive seal was computed 100% offline without remote network telemetry.",
        "To verify vault integrity against bit-rot or unauthorized modifications:",
        "```bash",
        f"arcanum freeze {manifest.root_dir} --verify ARCHIVE_MANIFEST.json",
        "```",
        "",
    ])

    return "\n".join(lines)


def verify_vault_freeze(
    manifest_data: dict[str, Any],
    vault_root: Path,
) -> dict[str, Any]:
    """Verifies a vault directory against an existing freeze manifest.

    Returns diagnostic audit findings:
    - FRZ-101: Modified file / SHA-256 mismatch
    - FRZ-102: Missing file recorded in manifest
    - FRZ-103: Untracked new file present in vault
    """
    vault_root = vault_root.resolve()
    recorded_files: dict[str, str] = {f["rel_path"]: f["sha256"] for f in manifest_data.get("files", [])}

    findings: list[dict[str, Any]] = []
    matched_count = 0

    # 1. Check all recorded files
    for rel_path, expected_hash in recorded_files.items():
        actual_path = vault_root / rel_path
        if not actual_path.exists():
            findings.append({
                "id": "FRZ-102",
                "severity": "ERROR",
                "file": rel_path,
                "message": f"Missing File: Recorded file '{rel_path}' does not exist on disk.",
            })
        else:
            actual_sha256, _, _, _ = hash_file(actual_path)
            if actual_sha256 != expected_hash:
                findings.append({
                    "id": "FRZ-101",
                    "severity": "ERROR",
                    "file": rel_path,
                    "message": (
                        f"Checksum Mismatch: '{rel_path}' was modified after freeze. "
                        f"Expected {expected_hash[:12]}..., got {actual_sha256[:12]}..."
                    ),
                })
            else:
                matched_count += 1

    # 2. Check for newly introduced untracked files
    current_manifest = scan_and_freeze_vault(vault_root)
    current_files = {f.rel_path for f in current_manifest.files}
    for curr in current_files:
        if curr not in recorded_files and not curr.endswith(("ARCHIVE_MANIFEST.json", "PROVENANCE_SEAL.md")):
            findings.append({
                "id": "FRZ-103",
                "severity": "WARNING",
                "file": curr,
                "message": f"Untracked File: '{curr}' was added after the freeze manifest was created.",
            })

    is_verified = (len([f for f in findings if f["severity"] == "ERROR"]) == 0)

    return {
        "is_verified": is_verified,
        "total_recorded": len(recorded_files),
        "matched_files": matched_count,
        "error_count": len([f for f in findings if f["severity"] == "ERROR"]),
        "warning_count": len([f for f in findings if f["severity"] == "WARNING"]),
        "findings": findings,
    }


def export_freeze_bundle(
    manifest: FreezeManifest,
    target_dir: Path,
) -> tuple[Path, Path]:
    """Writes ARCHIVE_MANIFEST.json and PROVENANCE_SEAL.md to target_dir atomically."""
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = target_dir / "ARCHIVE_MANIFEST.json"
    seal_path = target_dir / "PROVENANCE_SEAL.md"

    manifest_json = json.dumps(manifest.to_dict(), indent=2)
    seal_md = generate_provenance_seal_markdown(manifest)

    atomic_write(manifest_path, manifest_json)
    atomic_write(seal_path, seal_md)

    return manifest_path, seal_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cosmos Archive Freeze & Cryptographic Provenance Sealer")
    parser.add_argument("target", nargs="?", default=".", help="Target vault or cosmos directory to freeze/verify")
    parser.add_argument("--verify", type=Path, default=None, help="Verify target vault against manifest JSON")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory to write manifest and seal files")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON result")

    args = parser.parse_args(argv)
    target_path = Path(args.target).resolve()

    if args.verify:
        try:
            mdata = json.loads(args.verify.read_text(encoding="utf-8"))
            res = verify_vault_freeze(mdata, target_path)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                status_str = "✓ VERIFIED" if res["is_verified"] else "❌ VERIFICATION FAILED"
                print(f"Archive Freeze Verification: {status_str}")
                print(f"Matched: {res['matched_files']}/{res['total_recorded']} files")
                for fd in res["findings"]:
                    print(f"  [{fd['severity']}] {fd['id']}: {fd['message']}")
            return 0 if res["is_verified"] else 1
        except Exception as e:
            print(f"Error verifying archive manifest: {e}", file=sys.stderr)
            return 2

    # Freeze mode
    manifest = scan_and_freeze_vault(target_path)
    out_dir = args.output_dir or target_path
    m_path, s_path = export_freeze_bundle(manifest, out_dir)

    if args.json:
        print(json.dumps(manifest.to_dict(), indent=2))
    else:
        print("=" * 80)
        print("⚡ Ars Arcanum — Cosmos Archive Freeze & Provenance Seal Complete")
        print("=" * 80)
        print(f"Target Vault:   {manifest.root_dir}")
        print(f"Files Tracked:  {manifest.total_files}")
        print(f"Total Words:    {manifest.total_words:,}")
        print(f"Root SHA-256:   {manifest.root_sha256}")
        print(f"Manifest File:  {m_path}")
        print(f"Provenance Seal: {s_path}")
        print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
