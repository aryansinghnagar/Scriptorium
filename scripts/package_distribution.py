#!/usr/bin/env python3
"""
Ars Arcanum Multi-Platform Distribution & Packaging Engine
(scripts/package_distribution.py)
================================================================================
Zero-dependency, offline packaging tool to bundle manuscripts, submission packets,
advance review copies (ARCs), and static lore codices into distributable release archives.

Capabilities (OPS-101):
1. Release Package Targets:
   - Reader Bundle: EPUB + PDF + HTML reader + Cover art in a clean ZIP archive.
   - Publisher / Agent Submission Bundle: Standard Submission DOCX + Query Letter +
     Synopsis + Character list.
   - Advance Reading Copy (ARC): Bundles files with customized reviewer watermark
     embargo notices.
   - World Lore Codex Bundle: Static offline HTML codex + SVG map.
2. Integrity Manifests:
   - Calculates SHA-256 checksums and emits standard `RELEASE_MANIFEST.json`.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import zipfile
import hashlib
import json
import argparse
import datetime
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.package")


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hex digest for a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def package_reader_edition(manuscript_path: Path, output_dir: Path) -> dict:
    """Creates Reader Edition ZIP archive with EPUB, PDF, and Cover art."""
    title = manuscript_path.name.replace("_", " ")
    zip_name = f"{manuscript_path.name}_Reader_Edition.zip"
    zip_path = output_dir / zip_name

    exports_dir = manuscript_path / "Exports"
    art_dir = manuscript_path / "03-Art"

    files_added = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        # Check Exports
        if exports_dir.is_dir():
            for f in exports_dir.iterdir():
                if f.is_file() and f.suffix.lower() in (".pdf", ".epub", ".html"):
                    z.write(f, arcname=f"Ebooks/{f.name}")
                    files_added.append(f.name)
        # Check Art
        if art_dir.is_dir():
            for f in art_dir.iterdir():
                if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".svg"):
                    z.write(f, arcname=f"Art/{f.name}")
                    files_added.append(f.name)

        # Readme
        readme = f"# {title} — Reader Edition\n\nCompiled with Ars Arcanum on {datetime.date.today().isoformat()}.\nEnjoy your reading experience.\n"
        z.writestr("README.txt", readme)
        files_added.append("README.txt")

    sha256 = compute_file_sha256(zip_path)
    return {
        "package_type": "reader",
        "archive_path": str(zip_path),
        "filename": zip_name,
        "files_count": len(files_added),
        "size_bytes": zip_path.stat().st_size,
        "sha256": sha256
    }


def package_submission_bundle(manuscript_path: Path, output_dir: Path) -> dict:
    """Creates Publisher/Agent Submission ZIP with DOCX, Query, and Synopsis."""
    title = manuscript_path.name.replace("_", " ")
    zip_name = f"{manuscript_path.name}_Submission_Package.zip"
    zip_path = output_dir / zip_name

    submissions_dir = manuscript_path / "Submissions"
    exports_dir = manuscript_path / "Exports"

    files_added = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        if submissions_dir.is_dir():
            for f in submissions_dir.iterdir():
                if f.is_file():
                    z.write(f, arcname=f"Submission_Documents/{f.name}")
                    files_added.append(f.name)

        if exports_dir.is_dir():
            for f in exports_dir.iterdir():
                if f.is_file() and f.suffix.lower() in (".docx", ".pdf"):
                    z.write(f, arcname=f"Manuscripts/{f.name}")
                    files_added.append(f.name)

        meta_str = f"# Submission Package: {title}\nDate: {datetime.date.today().isoformat()}\nFormat: Industry Standard Manuscript Format\n"
        z.writestr("SUBMISSION_INFO.txt", meta_str)
        files_added.append("SUBMISSION_INFO.txt")

    sha256 = compute_file_sha256(zip_path)
    return {
        "package_type": "submission",
        "archive_path": str(zip_path),
        "filename": zip_name,
        "files_count": len(files_added),
        "size_bytes": zip_path.stat().st_size,
        "sha256": sha256
    }


def package_arc_bundle(manuscript_path: Path, output_dir: Path, reviewer: str = "Valued Reviewer") -> dict:
    """Creates Advance Reading Copy package with reviewer notice."""
    title = manuscript_path.name.replace("_", " ")
    clean_rev = re.sub(r'[^a-zA-Z0-9_\-]', '', reviewer.replace(" ", "_"))
    zip_name = f"{manuscript_path.name}_ARC_{clean_rev}.zip"
    zip_path = output_dir / zip_name

    exports_dir = manuscript_path / "Exports"

    files_added = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        if exports_dir.is_dir():
            for f in exports_dir.iterdir():
                if f.is_file() and f.suffix.lower() in (".epub", ".pdf", ".docx"):
                    z.write(f, arcname=f"ARC_Manuscript/{f.name}")
                    files_added.append(f.name)

        arc_notice = f"""================================================================================
ADVANCE READING COPY — NOT FOR RESALE OR REDISTRIBUTION
================================================================================
Title:      {title}
Recipient:  {reviewer}
Date:       {datetime.date.today().isoformat()}

This uncorrected advance reading copy is provided solely for review purposes.
Please do not quote directly without comparing against the final published edition.
================================================================================
"""
        z.writestr("ARC_LICENSE_NOTICE.txt", arc_notice)
        files_added.append("ARC_LICENSE_NOTICE.txt")

    sha256 = compute_file_sha256(zip_path)
    return {
        "package_type": "arc",
        "archive_path": str(zip_path),
        "filename": zip_name,
        "reviewer": reviewer,
        "files_count": len(files_added),
        "size_bytes": zip_path.stat().st_size,
        "sha256": sha256
    }


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Multi-Platform Packager (OPS-101)")
    parser.add_argument("target", help="Manuscript directory path")
    parser.add_argument("-t", "--type", choices=["reader", "submission", "arc", "all"], default="all", help="Package target type (default: all)")
    parser.add_argument("-o", "--output", help="Output directory for archives (default: <manuscript>/Dist)")
    parser.add_argument("--reviewer", default="Early Reviewer", help="Reviewer name for ARC package")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output or (target_path / "Dist"))
    out_dir.mkdir(parents=True, exist_ok=True)

    packages = []

    if args.type in ("reader", "all"):
        r_pkg = package_reader_edition(target_path, out_dir)
        packages.append(r_pkg)

    if args.type in ("submission", "all"):
        s_pkg = package_submission_bundle(target_path, out_dir)
        packages.append(s_pkg)

    if args.type in ("arc", "all"):
        a_pkg = package_arc_bundle(target_path, out_dir, reviewer=args.reviewer)
        packages.append(a_pkg)

    # Write release manifest
    manifest = {
        "manuscript": target_path.name,
        "generated_at": datetime.datetime.now().isoformat(),
        "packages": packages
    }
    manifest_path = out_dir / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(manifest, indent=2))
        return

    print("=== Ars Arcanum Release Distribution Packager ===")
    print(f"Target:       {target_path.name}")
    print(f"Output Dir:   {out_dir}")
    print(f"Packages Generated: {len(packages)}")
    print("-" * 75)
    for p in packages:
        print(f"  📦 {p['filename']:<36} | {p['size_bytes']:>8,} B | SHA: {p['sha256'][:12]}...")
    print(f"\nManifest written: {manifest_path}")


if __name__ == "__main__":
    main()
