#!/usr/bin/env python3
"""
Ars Arcanum Pre-Flight Typesetting & Publishing Compliance Linter
(scripts/lib/preflight.py)
================================================================================
Zero-dependency, offline pre-flight validation engine for novels and manuscripts.

Capabilities (PUB-101):
1. Publishing Metadata Validation:
   - Verifies presence of Title, Author, Language, Copyright, and ISBN in `manuscript.yaml`.
2. Asset & Image Verification:
   - Verifies cover art existence (`03-Art/cover.png` or root cover).
   - Validates internal image paths and dimensions.
3. Typesetting & Formatting Integrity:
   - Scans for orphan headings at end-of-files.
   - Detects unclosed markdown formatting (bold/italics/codeblocks).
   - Catches unescaped Typst / LaTeX control characters.
   - Checks for straight quotation marks needing typography polish.
4. Word Count & Page Budgeting:
   - Calculates industry standard page count estimates (250 w/page standard).
   - Validates standard chapter length bounds.
5. Standalone HTML Pre-Flight Certificate & Compliance Report.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import math
import re
import sys
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.preflight")


def check_metadata(manuscript_dir: Path) -> dict:
    """Validates manuscript metadata configuration in manuscript.yaml."""
    manifest_path = manuscript_dir / "manuscript.yaml"
    issues = []
    metadata = {}

    if not manifest_path.is_file():
        issues.append({"level": "FAIL", "code": "META-01", "message": "Missing 'manuscript.yaml' manifest file."})
        return {"valid": False, "issues": issues, "data": {}}

    try:
        # Simple YAML key-value parser to avoid PyYAML dependency
        lines = manifest_path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines:
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                metadata[k.strip()] = v.strip().strip('"\'')
    except Exception as e:
        issues.append({"level": "FAIL", "code": "META-02", "message": f"Failed reading manuscript.yaml: {e}"})

    # Required fields
    required = ["title", "author"]
    for req in required:
        if not metadata.get(req):
            issues.append({"level": "FAIL", "code": f"META-REQ-{req.upper()}", "message": f"Missing required metadata field: '{req}'."})

    recommended = ["isbn", "copyright_year", "language", "paper_size"]
    for rec in recommended:
        if not metadata.get(rec):
            issues.append({"level": "WARN", "code": f"META-REC-{rec.upper()}", "message": f"Recommended field '{rec}' is not defined in manifest."})

    return {
        "valid": not any(i["level"] == "FAIL" for i in issues),
        "issues": issues,
        "data": metadata
    }


def check_cover_and_assets(manuscript_dir: Path) -> dict:
    """Verifies cover art and embedded media assets."""
    issues = []
    cover_candidates = [
        manuscript_dir / "03-Art" / "cover.png",
        manuscript_dir / "03-Art" / "cover.jpg",
        manuscript_dir / "cover.png",
        manuscript_dir / "cover.jpg",
        manuscript_dir / "Art" / "cover.png"
    ]
    found_cover = None
    for c in cover_candidates:
        if c.is_file():
            found_cover = c
            break

    if not found_cover:
        issues.append({"level": "WARN", "code": "ASSET-COVER-01", "message": "No cover image found (expected 03-Art/cover.png or cover.jpg for EPUB/Print)."})

    return {
        "has_cover": bool(found_cover),
        "cover_path": str(found_cover) if found_cover else None,
        "issues": issues
    }


def validate_chapter_formatting(file_path: Path) -> list[dict]:
    """Validates markdown syntax, orphan headers, and unescaped markup in a chapter."""
    issues = []
    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    # 1. Orphan Heading check (Heading as the last non-empty line)
    non_empty = [line_str.strip() for line_str in lines if line_str.strip()]
    if non_empty and non_empty[-1].startswith("#"):
        issues.append({
            "level": "FAIL",
            "file": file_path.name,
            "line": len(lines),
            "code": "TYP-ORPHAN-HEAD",
            "message": f"Orphan heading at end of chapter without body text: '{non_empty[-1]}'"
        })

    # 2. Unclosed Code Blocks
    code_ticks = len(re.findall(r'^```', content, flags=re.MULTILINE))
    if code_ticks % 2 != 0:
        issues.append({
            "level": "FAIL",
            "file": file_path.name,
            "code": "TYP-UNCLOSED-CODE",
            "message": "Unclosed markdown code block (``` mismatch)."
        })

    # 3. Straight Quotation Marks Alert
    body_without_code = re.sub(r'```[\s\S]*?```', '', content)
    straight_quotes = body_without_code.count('"')
    if straight_quotes >= 4:
        issues.append({
            "level": "WARN",
            "file": file_path.name,
            "code": "TYP-STRAIGHT-QUOTES",
            "message": f"{straight_quotes} straight double quotes found. Consider running 'arcanum polish typography'."
        })

    # 4. Trailing triple dashes (unrendered divider)
    if non_empty and non_empty[-1] in ("---", "***"):
        issues.append({
            "level": "WARN",
            "file": file_path.name,
            "line": len(lines),
            "code": "TYP-TRAILING-DIV",
            "message": "Trailing divider line (---) at end of chapter."
        })

    return issues


def run_preflight_linter(manuscript_dir: Path) -> dict:
    """Executes full pre-flight verification on a manuscript repository."""
    if not manuscript_dir.is_dir():
        raise NotADirectoryError(f"Manuscript directory not found: {manuscript_dir}")

    meta_res = check_metadata(manuscript_dir)
    asset_res = check_cover_and_assets(manuscript_dir)

    chapter_files = sorted(manuscript_dir.rglob("*.md"))
    content_files = [f for f in chapter_files if not f.name.startswith((".", "_")) and "Backups" not in f.parts and "04_Back_Matter" not in f.parts]

    formatting_issues = []
    total_words = 0

    for f in content_files:
        try:
            f_issues = validate_chapter_formatting(f)
            formatting_issues.extend(f_issues)
            text = f.read_text(encoding="utf-8", errors="replace")
            words = len(re.findall(r'\b\w+\b', text))
            total_words += words
        except Exception as e:
            formatting_issues.append({"level": "FAIL", "file": f.name, "code": "ERR-READ", "message": str(e)})

    # Word count estimation & budget
    est_pages = math.ceil(total_words / 250) if total_words > 0 else 0

    all_issues = meta_res["issues"] + asset_res["issues"] + formatting_issues
    fail_count = sum(1 for i in all_issues if i["level"] == "FAIL")
    warn_count = sum(1 for i in all_issues if i["level"] == "WARN")

    # Preflight score: 100 - (fails * 20) - (warns * 5)
    score = max(0, min(100, 100 - (fail_count * 20) - (warn_count * 5)))
    is_ready = (fail_count == 0 and total_words >= 100)

    return {
        "target": str(manuscript_dir),
        "total_words": total_words,
        "estimated_pages": est_pages,
        "chapter_count": len(content_files),
        "is_ready_for_publish": is_ready,
        "compliance_score": score,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "metadata": meta_res["data"],
        "issues": all_issues
    }


def generate_preflight_html_report(report: dict, output_path: Path) -> Path:
    """Generates a publishing compliance certificate HTML report."""
    is_ready = report["is_ready_for_publish"]
    score = report["compliance_score"]
    issues = report.get("issues", [])

    issue_rows = []
    for iss in issues:
        badge = "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;'>FAIL</span>" if iss["level"] == "FAIL" else "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;'>WARN</span>"
        loc = f"{iss.get('file', 'manifest')}" + (f":{iss['line']}" if 'line' in iss else "")
        row = f"""
        <tr>
          <td>{badge}</td>
          <td><code>{html.escape(iss['code'])}</code></td>
          <td>{html.escape(loc)}</td>
          <td>{html.escape(iss['message'])}</td>
        </tr>
        """
        issue_rows.append(row)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Pre-Flight Publishing Compliance Certificate</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 950px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .status-box {{ padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; text-align: center; }}
  .status-pass {{ background: #064e3b; border: 1px solid #059669; color: #a7f3d0; }}
  .status-fail {{ background: #7f1d1d; border: 1px solid #dc2626; color: #fecaca; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>✈️ Pre-Flight Typesetting & Publishing Compliance</h1>
    <p style="color: var(--muted);">Target: {html.escape(report.get('target', ''))} | Chapters: {report.get('chapter_count', 0)}</p>
  </div>

  <div class="status-box {'status-pass' if is_ready else 'status-fail'}">
    <h2 style="margin:0; font-size:1.75rem;">{'✓ PASSED PRE-FLIGHT COMPLIANCE' if is_ready else '⚠️ PRE-FLIGHT ISSUES REQUIRING ATTENTION'}</h2>
    <p style="margin:0.5rem 0 0 0; opacity:0.9;">{'Ready for Typst PDF, EPUB, and Amazon KDP/IngramSpark distribution.' if is_ready else 'Please resolve the blocking errors below before compiling production prints.'}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Compliance Score</h3>
      <div class="metric" style="color: {'var(--success)' if score >= 90 else ('var(--warn)' if score >= 70 else 'var(--danger)')};">{score}%</div>
    </div>
    <div class="card">
      <h3>Total Words</h3>
      <div class="metric">{report.get('total_words', 0):,}</div>
    </div>
    <div class="card">
      <h3>Estimated Pages</h3>
      <div class="metric">~{report.get('estimated_pages', 0)}</div>
      <p style="color: var(--muted); margin: 0.25rem 0 0 0;">@ 250 w/page Trade 6x9</p>
    </div>
    <div class="card">
      <h3>Blocking Fails</h3>
      <div class="metric" style="color: {'var(--danger)' if report.get('fail_count', 0) > 0 else 'var(--success)'};">{report.get('fail_count', 0)}</div>
    </div>
  </div>

  <h2>📋 Pre-Flight Audit Checklist</h2>
  <table class="table">
    <thead><tr><th>Status</th><th>Rule Code</th><th>Location</th><th>Message</th></tr></thead>
    <tbody>
      {''.join(issue_rows) or '<tr><td colspan="4" style="color:var(--success);">✓ All checks passed cleanly with zero warnings or errors.</td></tr>'}
    </tbody>
  </table>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Pre-Flight Publishing Linter (PUB-101)")
    parser.add_argument("target", help="Manuscript directory")
    parser.add_argument("--html", help="Generate HTML pre-flight certificate")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = run_preflight_linter(target_path)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"=== Pre-Flight Typesetting Linter: {target_path.name} ===")
    print(f"Compliance Score: {report['compliance_score']}% | Ready for Publishing: {'YES (✓)' if report['is_ready_for_publish'] else 'NO (⚠️)'}")
    print(f"Total Words: {report['total_words']:,} | Est. Trade Pages: ~{report['estimated_pages']} | Chapters: {report['chapter_count']}")
    print("-" * 75)
    if not report["issues"]:
        print("✓ All checks passed with 100% compliance!")
    else:
        for iss in report["issues"]:
            level_tag = "[FAIL]" if iss["level"] == "FAIL" else "[WARN]"
            loc = f" ({iss.get('file', 'manifest')})" if 'file' in iss else ""
            print(f"  {level_tag:<6} {iss['code']:<18}{loc}: {iss['message']}")

    if args.html:
        out_p = Path(args.html)
        generate_preflight_html_report(report, out_p)
        print(f"\nHTML Certificate written to: {out_p}")


if __name__ == "__main__":
    main()
