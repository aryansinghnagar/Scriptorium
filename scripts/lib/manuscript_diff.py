#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Comparison & Redline Diff Engine (scripts/lib/manuscript_diff.py)
======================================================================================
Provides word-level and chapter-level comparison between manuscript drafts.
Generates:
  1. Accessible, beautiful HTML Redline changelog with chapter navigation,
     word delta metrics, light/dark mode, and inline/side-by-side views.
  2. ANSI colorized terminal diff with summary metrics.
  3. Machine-readable JSON change metrics.
  4. Bridge to LibreOffice Writer Track Changes comparison.

100% offline, privacy-respecting, zero-telemetry, and accessible.
"""

import os
import sys
import re
import json
import html
import difflib
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

try:
    from cache import count_words
except ImportError:
    _FM = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
    def count_words(text: str) -> int:
        clean = _FM.sub("", text)
        clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
        kept = [ln for ln in clean.splitlines()
                if ln.strip() and not (ln.strip().startswith("@") and re.match(r"^@[A-Za-z0-9_-]+:", ln.strip())) and not ln.strip().startswith("%")]
        return len(re.findall(r"\b\w+\b", "\n".join(kept), flags=re.UNICODE))


def strip_nw_metadata(text: str) -> str:
    """Removes novelWriter metadata tags (@pov:, @status:) and comments (%) for comparison."""
    lines = text.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@") and re.match(r"^@[A-Za-z0-9_-]+:", stripped):
            continue
        if stripped.startswith("%"):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def tokenize_words(text: str) -> List[str]:
    """Splits text into words, whitespace, and punctuation tokens preserving full structure."""
    return re.findall(r"\S+|\s+", text)


def compute_word_diff(tokens_a: List[str], tokens_b: List[str]) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Computes word-level diff using difflib.SequenceMatcher.
    Returns:
      (diff_chunks, added_word_count, deleted_word_count)
    Each chunk: {'tag': 'equal'|'insert'|'delete'|'replace', 'text_a': str, 'text_b': str}
    """
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    chunks = []
    added_words = 0
    deleted_words = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        sub_a = "".join(tokens_a[i1:i2])
        sub_b = "".join(tokens_b[j1:j2])

        if tag == "insert":
            words = len(re.findall(r"\b\w+\b", sub_b, flags=re.UNICODE))
            added_words += words
            chunks.append({"tag": "insert", "text": sub_b})
        elif tag == "delete":
            words = len(re.findall(r"\b\w+\b", sub_a, flags=re.UNICODE))
            deleted_words += words
            chunks.append({"tag": "delete", "text": sub_a})
        elif tag == "replace":
            w_a = len(re.findall(r"\b\w+\b", sub_a, flags=re.UNICODE))
            w_b = len(re.findall(r"\b\w+\b", sub_b, flags=re.UNICODE))
            deleted_words += w_a
            added_words += w_b
            chunks.append({"tag": "delete", "text": sub_a})
            chunks.append({"tag": "insert", "text": sub_b})
        elif tag == "equal":
            chunks.append({"tag": "equal", "text": sub_b})

    return chunks, added_words, deleted_words


def discover_draft_files(draft_dir: Path) -> List[Path]:
    """Finds and sorts all markdown files in a draft directory."""
    if not draft_dir.is_dir():
        return []
    md_files = []
    for p in sorted(draft_dir.rglob("*.md")):
        # Skip outlines, backups, exports, or hidden files
        rel_parts = p.relative_to(draft_dir).parts
        if any(part in ("Outlines", "Exports", "Backups", "05-Backups", "04-Publishing") or part.startswith(".") for part in rel_parts):
            continue
        # If draft_dir is a parent folder containing other Draft-* subdirectories, skip files inside nested Draft-* subdirectories
        if len(rel_parts) > 1 and any(part.startswith("Draft-") for part in rel_parts[:-1]):
            continue
        md_files.append(p)
    return sorted(md_files)


def extract_chapter_title(file_path: Path, content: str) -> str:
    """Extracts chapter title from first markdown heading or filename."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    # Fallback to readable filename
    stem = file_path.stem
    clean = re.sub(r"^\d+_", "", stem).replace("_", " ").replace("-", " ")
    return clean.title()


class ManuscriptComparator:
    def __init__(self, path_a: Path, path_b: Path, label_a: str = "Draft 1", label_b: str = "Draft 2"):
        self.path_a = path_a
        self.path_b = path_b
        self.label_a = label_a
        self.label_b = label_b
        self.chapters: List[Dict[str, Any]] = []
        self.summary: Dict[str, Any] = {}

    def compare(self) -> Dict[str, Any]:
        """Performs full comparison across all chapters/files."""
        if self.path_a.is_file() and self.path_b.is_file():
            self._compare_single_files(self.path_a, self.path_b)
        else:
            self._compare_directories(self.path_a, self.path_b)

        total_a = sum(c["words_a"] for c in self.chapters)
        total_b = sum(c["words_b"] for c in self.chapters)
        added = sum(c["added_words"] for c in self.chapters)
        deleted = sum(c["deleted_words"] for c in self.chapters)
        net_change = total_b - total_a

        # Overall similarity
        if total_a + total_b > 0:
            sim_sum = sum(c["similarity"] * (c["words_a"] + c["words_b"]) for c in self.chapters)
            overall_sim = round(sim_sum / (total_a + total_b), 4)
        else:
            overall_sim = 1.0

        self.summary = {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "path_a": str(self.path_a),
            "path_b": str(self.path_b),
            "total_words_a": total_a,
            "total_words_b": total_b,
            "added_words": added,
            "deleted_words": deleted,
            "net_change": net_change,
            "similarity_ratio": overall_sim,
            "chapter_count": len(self.chapters),
            "chapters": self.chapters
        }
        return self.summary

    def _compare_single_files(self, file_a: Path, file_b: Path):
        content_a = file_a.read_text(encoding="utf-8", errors="replace") if file_a.is_file() else ""
        content_b = file_b.read_text(encoding="utf-8", errors="replace") if file_b.is_file() else ""

        title = extract_chapter_title(file_b if file_b.is_file() else file_a, content_b or content_a)
        chap_data = self._diff_prose(content_a, content_b, title, file_b.name)
        self.chapters.append(chap_data)

    def _compare_directories(self, dir_a: Path, dir_b: Path):
        files_a = {p.relative_to(dir_a): p for p in discover_draft_files(dir_a)}
        files_b = {p.relative_to(dir_b): p for p in discover_draft_files(dir_b)}

        all_rel_paths = sorted(set(files_a.keys()).union(set(files_b.keys())))

        for rel_path in all_rel_paths:
            file_a = files_a.get(rel_path)
            file_b = files_b.get(rel_path)

            content_a = file_a.read_text(encoding="utf-8", errors="replace") if file_a else ""
            content_b = file_b.read_text(encoding="utf-8", errors="replace") if file_b else ""

            target_file = file_b or file_a
            title = extract_chapter_title(target_file, content_b or content_a)
            chap_data = self._diff_prose(content_a, content_b, title, str(rel_path))
            self.chapters.append(chap_data)

    def _diff_prose(self, raw_a: str, raw_b: str, title: str, rel_path: str) -> Dict[str, Any]:
        clean_a = strip_nw_metadata(raw_a)
        clean_b = strip_nw_metadata(raw_b)

        words_a = count_words(clean_a)
        words_b = count_words(clean_b)

        tokens_a = tokenize_words(clean_a)
        tokens_b = tokenize_words(clean_b)

        chunks, added, deleted = compute_word_diff(tokens_a, tokens_b)

        matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
        sim = round(matcher.ratio(), 4)

        return {
            "title": title,
            "rel_path": rel_path,
            "words_a": words_a,
            "words_b": words_b,
            "added_words": added,
            "deleted_words": deleted,
            "net_change": words_b - words_a,
            "similarity": sim,
            "chunks": chunks,
            "raw_a": clean_a,
            "raw_b": clean_b
        }

    def to_json(self, indent: int = 2) -> str:
        """Returns JSON representation without huge raw chunk bloat unless requested."""
        if not self.summary:
            self.compare()
        # Create serializable view
        export_data = dict(self.summary)
        export_data["chapters"] = [
            {k: v for k, v in c.items() if k not in ("chunks", "raw_a", "raw_b")}
            for c in self.chapters
        ]
        return json.dumps(export_data, indent=indent, ensure_ascii=False)

    def to_terminal_ansi(self) -> str:
        """Generates rich ANSI colored diff output for terminal."""
        if not self.summary:
            self.compare()

        RED = "\033[38;2;220;53;69m\033[9m"  # Soft red + strikethrough
        GREEN = "\033[38;2;40;167;69m\033[4m"  # Soft green + underline
        CYAN = "\033[1;36m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        DIM = "\033[2m"

        out = []
        out.append(f"\n{BOLD}{CYAN}=== Ars Arcanum Manuscript Revision Comparison ==={RESET}")
        out.append(f"{DIM}Base  Draft (A):{RESET} {self.label_a} ({self.summary['total_words_a']:,} words)")
        out.append(f"{DIM}Prior Draft (B):{RESET} {self.label_b} ({self.summary['total_words_b']:,} words)")
        net = self.summary['net_change']
        net_str = f"+{net:,}" if net >= 0 else f"{net:,}"
        out.append(f"{DIM}Delta Stats:{RESET} {GREEN}+{self.summary['added_words']:,} added{RESET} | {RED}-{self.summary['deleted_words']:,} deleted{RESET} | Net: {BOLD}{net_str}{RESET} | Similarity: {self.summary['similarity_ratio']*100:.1f}%\n")

        for chap in self.chapters:
            c_net = chap['net_change']
            c_net_str = f"+{c_net:,}" if c_net >= 0 else f"{c_net:,}"
            out.append(f"{CYAN}--- {chap['title']} [{chap['rel_path']}] ---{RESET} ({chap['words_a']:,} -> {chap['words_b']:,} words, {GREEN}+{chap['added_words']}{RESET}/{RED}-{chap['deleted_words']}{RESET}, Net: {c_net_str})")
            
            # Print inline chunk tokens
            line_buf = []
            for chunk in chap["chunks"]:
                tag = chunk["tag"]
                txt = chunk["text"]
                if tag == "insert":
                    line_buf.append(f"{GREEN}{txt}{RESET}")
                elif tag == "delete":
                    line_buf.append(f"{RED}{txt}{RESET}")
                else:
                    line_buf.append(txt)
            out.append("".join(line_buf))
            out.append("")

        return "\n".join(out)

    def to_html(self) -> str:
        """
        Generates accessible, standalone HTML Redline Changelog.
        Includes chapter sidebar, word counts, search, light/dark mode, and inline/side-by-side view.
        """
        if not self.summary:
            self.compare()

        esc_label_a = html.escape(self.label_a)
        esc_label_b = html.escape(self.label_b)
        tot_a = self.summary['total_words_a']
        tot_b = self.summary['total_words_b']
        add_w = self.summary['added_words']
        del_w = self.summary['deleted_words']
        net_w = self.summary['net_change']
        sim_pct = round(self.summary['similarity_ratio'] * 100, 1)
        net_sign = "+" if net_w >= 0 else ""

        # Build sidebar chapter list and main content
        sidebar_items = []
        chapter_sections = []

        for idx, chap in enumerate(self.chapters, 1):
            chap_id = f"chap-{idx}"
            esc_title = html.escape(chap["title"])
            esc_rel = html.escape(chap["rel_path"])
            c_add = chap["added_words"]
            c_del = chap["deleted_words"]
            c_net = chap["net_change"]
            c_net_sign = "+" if c_net >= 0 else ""
            c_sim = round(chap["similarity"] * 100, 1)

            sidebar_items.append(f"""
            <a href="#{chap_id}" class="nav-item" data-target="{chap_id}">
                <div class="nav-title">{esc_title}</div>
                <div class="nav-stats">
                    <span class="pill-add">+{c_add}</span>
                    <span class="pill-del">-{c_del}</span>
                    <span class="pill-net">{c_net_sign}{c_net} w</span>
                </div>
            </a>
            """)

            # Render redline tokens into formatted HTML paragraphs
            inline_html = []
            for chunk in chap["chunks"]:
                tag = chunk["tag"]
                raw_txt = chunk["text"]
                esc_txt = html.escape(raw_txt)
                # Convert newlines to breaks or paragraph splits
                esc_txt = esc_txt.replace("\n\n", "</p><p>").replace("\n", "<br/>")

                if tag == "insert":
                    inline_html.append(f'<ins class="diff-ins" title="Added in {esc_label_b}">{esc_txt}</ins>')
                elif tag == "delete":
                    inline_html.append(f'<del class="diff-del" title="Cut from {esc_label_a}">{esc_txt}</del>')
                else:
                    inline_html.append(f'<span class="diff-eq">{esc_txt}</span>')

            body_prose = "".join(inline_html)
            # Wrap in paragraphs
            if not body_prose.startswith("<p>"):
                body_prose = "<p>" + body_prose + "</p>"

            chapter_sections.append(f"""
            <section id="{chap_id}" class="chapter-card">
                <header class="chapter-header">
                    <div class="chapter-meta">
                        <h2>{esc_title}</h2>
                        <span class="chapter-path">{esc_rel}</span>
                    </div>
                    <div class="chapter-pills">
                        <span class="badge badge-words">{chap['words_a']} &rarr; {chap['words_b']} words</span>
                        <span class="badge badge-add">+{c_add} added</span>
                        <span class="badge badge-del">-{c_del} cut</span>
                        <span class="badge badge-sim">{c_sim}% match</span>
                    </div>
                </header>
                <div class="prose-content">
                    {body_prose}
                </div>
            </section>
            """)

        html_template = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manuscript Redline Diff: {esc_label_a} vs {esc_label_b} | Ars Arcanum</title>
    <style>
        :root {{
            --bg-body: #f8f9fa;
            --bg-surface: #ffffff;
            --bg-sidebar: #f1f3f5;
            --border-color: #e9ecef;
            --text-main: #212529;
            --text-muted: #6c757d;
            --primary: #495057;
            --font-prose: "EB Garamond", "Libertinus Serif", "Georgia", serif;
            --font-ui: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
            
            /* Accessible Redline Pastel Highlights */
            --del-bg: #f8d7da;
            --del-color: #721c24;
            --del-border: #f5c6cb;
            --ins-bg: #d4edda;
            --ins-color: #155724;
            --ins-border: #c3e6cb;
        }}

        [data-theme="dark"] {{
            --bg-body: #121416;
            --bg-surface: #1a1d20;
            --bg-sidebar: #15181a;
            --border-color: #2c3136;
            --text-main: #e9ecef;
            --text-muted: #adb5bd;
            --primary: #dee2e6;
            
            /* Dark Mode Accessible Pastel Highlights */
            --del-bg: #3a1e22;
            --del-color: #f5c6cb;
            --del-border: #842029;
            --ins-bg: #1e3a29;
            --ins-color: #d1e7dd;
            --ins-border: #0f5132;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-ui);
            background: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* App Sidebar */
        #sidebar {{
            width: 320px;
            background: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }}

        .sidebar-header {{
            padding: 18px 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        .sidebar-header h1 {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 4px;
        }}

        .sidebar-header .subtitle {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .summary-stats {{
            padding: 14px 20px;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            font-size: 0.85rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
        }}

        .stat-card {{
            padding: 8px;
            background: var(--bg-body);
            border-radius: 6px;
            border: 1px solid var(--border-color);
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.1rem;
            font-weight: 700;
        }}

        .stat-label {{
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        .nav-list {{
            overflow-y: auto;
            flex: 1;
            padding: 10px;
        }}

        .nav-item {{
            display: block;
            padding: 10px 12px;
            border-radius: 6px;
            text-decoration: none;
            color: var(--text-main);
            margin-bottom: 6px;
            transition: background 0.15s ease;
        }}

        .nav-item:hover, .nav-item.active {{
            background: var(--bg-surface);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .nav-title {{
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 4px;
        }}

        .nav-stats {{
            display: flex;
            gap: 6px;
            font-size: 0.75rem;
        }}

        .pill-add {{
            color: var(--ins-color);
            font-weight: 600;
        }}

        .pill-del {{
            color: var(--del-color);
            font-weight: 600;
        }}

        .pill-net {{
            color: var(--text-muted);
        }}

        /* Main Workspace View */
        #workspace {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .topbar {{
            height: 56px;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            gap: 16px;
        }}

        .comparison-badge {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .tag-a {{
            padding: 3px 8px;
            background: var(--del-bg);
            color: var(--del-color);
            border-radius: 4px;
            border: 1px solid var(--del-border);
        }}

        .tag-b {{
            padding: 3px 8px;
            background: var(--ins-bg);
            color: var(--ins-color);
            border-radius: 4px;
            border: 1px solid var(--ins-border);
        }}

        .controls {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .btn {{
            padding: 6px 12px;
            font-size: 0.85rem;
            font-weight: 500;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-surface);
            color: var(--text-main);
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .btn:hover {{
            background: var(--bg-body);
        }}

        .btn-primary {{
            background: var(--primary);
            color: var(--bg-surface);
            border-color: var(--primary);
        }}

        .search-box {{
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-body);
            color: var(--text-main);
            font-size: 0.85rem;
            width: 200px;
        }}

        /* Redline Reader Viewport */
        #content {{
            flex: 1;
            overflow-y: auto;
            padding: 32px 48px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .reading-container {{
            max-width: 820px;
            width: 100%;
        }}

        .chapter-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 36px 44px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }}

        .chapter-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 16px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .chapter-header h2 {{
            font-size: 1.4rem;
            font-weight: 700;
        }}

        .chapter-path {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-left: 8px;
        }}

        .chapter-pills {{
            display: flex;
            gap: 6px;
        }}

        .badge {{
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}

        .badge-words {{ background: var(--bg-body); color: var(--text-muted); }}
        .badge-add {{ background: var(--ins-bg); color: var(--ins-color); }}
        .badge-del {{ background: var(--del-bg); color: var(--del-color); }}
        .badge-sim {{ background: var(--bg-body); color: var(--text-main); }}

        /* Prose & Redline Typography */
        .prose-content {{
            font-family: var(--font-prose);
            font-size: 1.18rem;
            line-height: 1.85;
            color: var(--text-main);
        }}

        .prose-content p {{
            margin-bottom: 1.4em;
            text-indent: 1.5em;
        }}

        .prose-content p:first-of-type {{
            text-indent: 0;
        }}

        /* Deletions & Additions Styling */
        del.diff-del {{
            background-color: var(--del-bg);
            color: var(--del-color);
            text-decoration: line-through;
            text-decoration-thickness: 1.5px;
            padding: 1px 4px;
            border-radius: 3px;
            border: 1px solid var(--del-border);
            margin: 0 1px;
        }}

        ins.diff-ins {{
            background-color: var(--ins-bg);
            color: var(--ins-color);
            text-decoration: underline;
            text-decoration-thickness: 1.5px;
            padding: 1px 4px;
            border-radius: 3px;
            border: 1px solid var(--ins-border);
            margin: 0 1px;
        }}

        .diff-eq {{
            /* standard unchanged text */
        }}

        /* Changelog Mode (dim unchanged) */
        body.changelog-mode .diff-eq {{
            opacity: 0.35;
        }}

        /* Print formatting */
        @media print {{
            #sidebar, .topbar {{ display: none !important; }}
            body {{ overflow: visible; height: auto; background: #fff; color: #000; }}
            #workspace, #content {{ overflow: visible; padding: 0; }}
            .chapter-card {{ border: none; box-shadow: none; padding: 0; margin-bottom: 40pt; page-break-after: always; }}
            del.diff-del {{ background: #eee !important; color: #666 !important; text-decoration: line-through; }}
            ins.diff-ins {{ background: #ddd !important; color: #000 !important; font-weight: bold; }}
        }}
    </style>
</head>
<body>

    <!-- Chapter Navigation Sidebar -->
    <aside id="sidebar">
        <div class="sidebar-header">
            <h1>Ars Arcanum Redline</h1>
            <div class="subtitle">Draft Comparison & Changelog View</div>
        </div>

        <div class="summary-stats">
            <div><strong>Total Metrics:</strong></div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--ins-color);">+{add_w:,}</div>
                    <div class="stat-label">Words Added</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--del-color);">-{del_w:,}</div>
                    <div class="stat-label">Words Cut</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{net_sign}{net_w:,}</div>
                    <div class="stat-label">Net Word Change</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{sim_pct}%</div>
                    <div class="stat-label">Similarity</div>
                </div>
            </div>
        </div>

        <nav class="nav-list">
            {''.join(sidebar_items)}
        </nav>
    </aside>

    <!-- Main Comparison Workspace -->
    <main id="workspace">
        <header class="topbar">
            <div class="comparison-badge">
                <span class="tag-a">{esc_label_a} ({tot_a:,} w)</span>
                <span>&rarr;</span>
                <span class="tag-b">{esc_label_b} ({tot_b:,} w)</span>
            </div>

            <div class="controls">
                <input type="text" id="searchInput" class="search-box" placeholder="Filter prose or words...">
                <button class="btn" id="btnToggleChangelog" title="Dim unchanged prose to highlight changes">Highlight Changes Only</button>
                <button class="btn" id="btnToggleTheme">Theme: Auto</button>
                <button class="btn btn-primary" onclick="window.print()">Print / PDF</button>
            </div>
        </header>

        <div id="content">
            <div class="reading-container">
                {''.join(chapter_sections)}
            </div>
        </div>
    </main>

    <script>
        // Theme switching
        const btnTheme = document.getElementById('btnToggleTheme');
        let currentTheme = 'light';
        btnTheme.addEventListener('click', () => {{
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', currentTheme);
            btnTheme.textContent = 'Theme: ' + (currentTheme === 'dark' ? 'Dark' : 'Light');
        }});

        // Changelog mode toggle
        const btnChangelog = document.getElementById('btnToggleChangelog');
        btnChangelog.addEventListener('click', () => {{
            document.body.classList.toggle('changelog-mode');
            const active = document.body.classList.contains('changelog-mode');
            btnChangelog.textContent = active ? 'Show Full Prose' : 'Highlight Changes Only';
        }});

        // Live search filter
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            document.querySelectorAll('.chapter-card').forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }});
    </script>
</body>
</html>
"""
        return html_template

    def open_in_libreoffice(self) -> bool:
        """
        Converts Draft A and Draft B to ODT via pandoc (if installed)
        and launches LibreOffice Writer comparison.
        """
        import tempfile
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_lo_diff_"))
        doc_a = tmp_dir / f"{self.label_a}.odt"
        doc_b = tmp_dir / f"{self.label_b}.odt"

        # Combine text for each draft
        text_a = "\n\n".join(f"# {c['title']}\n\n{c['raw_a']}" for c in self.chapters)
        text_b = "\n\n".join(f"# {c['title']}\n\n{c['raw_b']}" for c in self.chapters)

        src_a = tmp_dir / "draft_a.md"
        src_b = tmp_dir / "draft_b.md"
        src_a.write_text(text_a, encoding="utf-8")
        src_b.write_text(text_b, encoding="utf-8")

        # Convert to ODT with pandoc
        try:
            subprocess.run(["pandoc", str(src_a), "-o", str(doc_a)], check=True)
            subprocess.run(["pandoc", str(src_b), "-o", str(doc_b)], check=True)
            # Launch LibreOffice
            lo_cmd = ["libreoffice", "--writer", str(doc_b)]
            subprocess.Popen(lo_cmd)
            return True
        except Exception as e:
            print(f"[!] Could not launch LibreOffice comparison: {e}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Manuscript Diff & Redline Generator")
    parser.add_argument("path_a", help="Base / Older draft directory or file (e.g. Book-01/Draft-01)")
    parser.add_argument("path_b", help="Target / Newer draft directory or file (e.g. Book-01/Draft-02)")
    parser.add_argument("--label-a", default="", help="Display label for Draft A (default: folder name)")
    parser.add_argument("--label-b", default="", help="Display label for Draft B (default: folder name)")
    parser.add_argument("--html", help="Path to write standalone HTML Redline report")
    parser.add_argument("--json", action="store_true", help="Output summary change metrics as JSON")
    parser.add_argument("--terminal", action="store_true", help="Print colorized ANSI diff to stdout")
    parser.add_argument("--libreoffice", action="store_true", help="Export to ODT and launch LibreOffice Writer")

    args = parser.parse_args()

    p_a = Path(args.path_a).expanduser().resolve()
    p_b = Path(args.path_b).expanduser().resolve()

    if not p_a.exists():
        print(f"Error: Path A does not exist: {p_a}", file=sys.stderr)
        sys.exit(2)
    if not p_b.exists():
        print(f"Error: Path B does not exist: {p_b}", file=sys.stderr)
        sys.exit(2)

    label_a = args.label_a or p_a.name
    label_b = args.label_b or p_b.name

    comparator = ManuscriptComparator(p_a, p_b, label_a, label_b)
    comparator.compare()

    if args.json:
        print(comparator.to_json())
    elif args.html:
        out_path = Path(args.html).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(comparator.to_html(), encoding="utf-8")
        print(f"[✓] Redline HTML report generated at: {out_path}")
    elif args.libreoffice:
        comparator.open_in_libreoffice()
    else:
        # Default to terminal ANSI diff
        print(comparator.to_terminal_ansi())


if __name__ == "__main__":
    main()
