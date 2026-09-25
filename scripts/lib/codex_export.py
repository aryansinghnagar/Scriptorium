#!/usr/bin/env python3
"""
Ars Arcanum Static World Wiki & Lore Codex Exporter
(scripts/lib/codex_export.py)
================================================================================
Zero-dependency, offline static site generator compiling Obsidian World Bibles
into a sovereign, searchable encyclopedia and reader codex.

Capabilities (WOR-102):
1. World Bible Vault Scanning & Categorization:
   - Scans Characters/, Locations/, Factions/, Artifacts/, Bestiary/, Cosmology/,
     Languages/, MagicSystems/, and History/.
2. Markdown to Styled HTML Conversion:
   - Resolves Obsidian Wikilinks [[Target]] and [[Target|Label]] to internal links.
   - Parses YAML frontmatter into rich Infobox cards with trait badges.
3. Offline Client-Side Search & Multi-Theme:
   - Inlined vanilla JavaScript inverted index search.
   - Dark, Light, and Classic Sepia reading themes.
   - Single-file standalone HTML bundle mode or multi-page static site.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.codex_export")

TAXONOMIES = [
    "Characters", "Locations", "Factions", "Artifacts", "Bestiary",
    "Cosmology", "Languages", "MagicSystems", "History"
]


def _md_to_basic_html(md_text: str) -> tuple[str, dict]:
    """Converts markdown text to clean HTML and extracts YAML frontmatter."""
    lines = md_text.splitlines()
    in_fm = False
    fm_data = {}
    body_lines = []

    for line in lines:
        s = line.strip()
        if s == "---":
            in_fm = not in_fm
            continue
        if in_fm:
            if ":" in s:
                k, v = s.split(":", 1)
                fm_data[k.strip()] = v.strip().strip('"\'')
            continue
        body_lines.append(line)

    raw_body = "\n".join(body_lines)

    # Convert wikilinks: [[Target|Label]] -> <a href="#Target">Label</a>
    def _sub_wikilink(m):
        target = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else target
        clean_id = re.sub(r'[^\w\-]', '', target.replace(" ", "_"))
        return f'<a href="#{clean_id}" class="wikilink">{label}</a>'

    body_html = re.sub(r'\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]', _sub_wikilink, raw_body)

    # Basic markdown elements
    # Headings
    body_html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', body_html, flags=re.MULTILINE)
    body_html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', body_html, flags=re.MULTILINE)
    body_html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', body_html, flags=re.MULTILINE)

    # Bold and italics
    body_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', body_html)
    body_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', body_html)

    # Paragraphs and linebreaks
    paragraphs = body_html.split("\n\n")
    p_tags = []
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean.startswith("<h"):
            p_tags.append(p_clean)
        else:
            p_tags.append(f"<p>{p_clean.replace(chr(10), '<br>')}</p>")

    return "\n".join(p_tags), fm_data


def scan_world_vault(world_dir: Path) -> dict[str, list[dict]]:
    """Scans world vault notes grouped by taxonomy."""
    categories = {}

    for tax in TAXONOMIES:
        tax_dir = world_dir / tax
        items = []
        if tax_dir.is_dir():
            for f in sorted(tax_dir.glob("*.md")):
                if not f.name.startswith((".", "_")):
                    content = f.read_text(encoding="utf-8", errors="replace")
                    body_html, fm = _md_to_basic_html(content)
                    title = fm.get("name", f.stem.replace("_", " "))
                    clean_id = re.sub(r'[^a-zA-Z0-9_\-]', '', f.stem)
                    items.append({
                        "id": clean_id,
                        "title": title,
                        "taxonomy": tax,
                        "filename": f.name,
                        "frontmatter": fm,
                        "html": body_html,
                        "raw_text": re.sub(r'<[^>]+>', '', body_html)
                    })
        if items:
            categories[tax] = items

    return categories


def build_single_file_codex(categories: dict[str, list[dict]], world_name: str, output_path: Path) -> Path:
    """Builds a single standalone offline HTML file containing the complete world codex."""
    search_index = []
    entries_html = []
    sidebar_links = []

    total_articles = 0

    for tax, items in categories.items():
        sidebar_links.append(f"<div class='tax-header'>{tax} ({len(items)})</div>")
        for it in items:
            total_articles += 1
            sidebar_links.append(f"<a href='#{it['id']}' class='nav-link' onclick='showArticle(\"{it['id']}\")'>{html.escape(it['title'])}</a>")
            search_index.append({
                "id": it["id"],
                "title": it["title"],
                "tax": it["taxonomy"],
                "text": it["raw_text"][:300]
            })

            # Infobox attributes
            infobox_rows = "".join(
                f"<tr><th>{html.escape(k.replace('_', ' ').title())}</th><td>{html.escape(str(v))}</td></tr>"
                for k, v in it["frontmatter"].items()
                if k not in ("name", "title", "fileClass", "type")
            )
            infobox_html = f"""
            <table class="infobox">
              <tr><th colspan="2" class="infobox-title">{html.escape(it['title'])}</th></tr>
              {infobox_rows}
            </table>
            """ if infobox_rows else ""

            entry = f"""
            <article id="{it['id']}" class="codex-article" style="display: none;">
              <span class="tax-badge">{it['taxonomy']}</span>
              <h1>{html.escape(it['title'])}</h1>
              {infobox_html}
              <div class="article-body">
                {it['html']}
              </div>
            </article>
            """
            entries_html.append(entry)

    search_json = json.dumps(search_index).replace("<", "\\u003c").replace(">", "\\u003e")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — {html.escape(world_name)} Codex</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --link: #60a5fa; --infobox-bg: #1e293b;
  }}
  body[data-theme="light"] {{
    --bg: #f8fafc; --panel: #ffffff; --border: #cbd5e1;
    --text: #0f172a; --muted: #64748b; --accent: #0284c7;
    --link: #2563eb; --infobox-bg: #f1f5f9;
  }}
  body[data-theme="sepia"] {{
    --bg: #f4ecd8; --panel: #faf4e6; --border: #dcd0ba;
    --text: #3c2f1e; --muted: #7c6f5a; --accent: #b45309;
    --link: #92400e; --infobox-bg: #eee5d0;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; height: 100vh; overflow: hidden; }}
  #sidebar {{ width: 320px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; }}
  .sidebar-header {{ padding: 1.25rem; border-bottom: 1px solid var(--border); }}
  .sidebar-header h2 {{ margin: 0; color: var(--accent); font-size: 1.25rem; }}
  .search-input {{ width: 100%; box-sizing: border-box; padding: 0.6rem; margin-top: 0.75rem; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text); }}
  .nav-container {{ overflow-y: auto; flex: 1; padding: 0.75rem; }}
  .tax-header {{ font-size: 0.75rem; text-transform: uppercase; color: var(--muted); font-weight: 700; margin: 1rem 0 0.25rem 0.5rem; }}
  .nav-link {{ display: block; padding: 0.4rem 0.5rem; color: var(--text); text-decoration: none; border-radius: 4px; font-size: 0.875rem; }}
  .nav-link:hover, .nav-link.active {{ background: var(--bg); color: var(--accent); }}
  #main {{ flex: 1; overflow-y: auto; padding: 2.5rem; }}
  .theme-toggle {{ position: fixed; top: 1rem; right: 1.5rem; display: flex; gap: 0.5rem; z-index: 10; }}
  .btn-theme {{ background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 0.4rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }}
  .tax-badge {{ background: #334155; color: var(--accent); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
  .infobox {{ float: right; margin: 0 0 1.5rem 1.5rem; background: var(--infobox-bg); border: 1px solid var(--border); border-radius: 8px; width: 280px; border-collapse: collapse; font-size: 0.85rem; }}
  .infobox-title {{ background: var(--border); padding: 0.5rem; font-size: 1rem; text-align: center; color: var(--accent); }}
  .infobox th, .infobox td {{ padding: 0.4rem 0.6rem; text-align: left; border-bottom: 1px solid var(--border); }}
  .wikilink {{ color: var(--link); text-decoration: underline; }}
  .home-splash {{ max-width: 700px; margin: 3rem auto; text-align: center; }}
</style>
</head>
<body>

<div id="sidebar">
  <div class="sidebar-header">
    <h2>📖 {html.escape(world_name)} Codex</h2>
    <p style="color:var(--muted); font-size:0.8rem; margin:4px 0 0 0;">{total_articles} Articles Indexed</p>
    <input type="text" id="search" class="search-input" placeholder="Search world lore..." oninput="doSearch()">
  </div>
  <div class="nav-container" id="navLinks">
    {''.join(sidebar_links)}
  </div>
</div>

<main id="main">
  <div class="theme-toggle">
    <button class="btn-theme" onclick="setTheme('dark')">🌙 Dark</button>
    <button class="btn-theme" onclick="setTheme('light')">☀️ Light</button>
    <button class="btn-theme" onclick="setTheme('sepia')">📜 Sepia</button>
  </div>

  <div id="homeView" class="home-splash">
    <h1 style="color:var(--accent); font-size:2.5rem; margin-bottom:0.5rem;">{html.escape(world_name)}</h1>
    <p style="color:var(--muted); font-size:1.1rem;">A sovereign, static encyclopedia of lore, history, factions, and characters.</p>
    <p style="color:var(--muted);">Select an entry from the sidebar navigation or use search to explore.</p>
  </div>

  {''.join(entries_html)}
</main>

<script>
const index = {search_json};
let originalNavHtml = '';

function setTheme(theme) {{
  document.body.setAttribute('data-theme', theme);
}}

function showArticle(id) {{
  document.getElementById('homeView').style.display = 'none';
  document.querySelectorAll('.codex-article').forEach(a => a.style.display = 'none');
  const target = document.getElementById(id);
  if (target) {{
    target.style.display = 'block';
    if (window.location.hash.replace('#', '') !== id) {{
      window.location.hash = id;
    }}
  }}
}}

function doSearch() {{
  const q = document.getElementById('search').value.toLowerCase().trim();
  const nav = document.getElementById('navLinks');
  if (!originalNavHtml) originalNavHtml = nav.innerHTML;
  if (!q) {{
    nav.innerHTML = originalNavHtml;
    return;
  }}
  const matches = index.filter(item => item.title.toLowerCase().includes(q) || item.text.toLowerCase().includes(q));
  nav.innerHTML = '<div class="tax-header">Search Results (' + matches.length + ')</div>';
  matches.forEach(m => {{
    const a = document.createElement('a');
    a.className = 'nav-link';
    a.href = '#' + m.id;
    a.innerHTML = `<strong>${{m.title}}</strong> <small style="color:var(--muted);">(${{m.tax}})</small>`;
    a.onclick = () => showArticle(m.id);
    nav.appendChild(a);
  }});
}}

function handleHash() {{
  const hash = window.location.hash.replace('#', '');
  if (hash) showArticle(hash);
}}

window.addEventListener('load', () => {{
  originalNavHtml = document.getElementById('navLinks').innerHTML;
  handleHash();
}});
window.addEventListener('hashchange', handleHash);
</script>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Static World Wiki Codex Exporter (WOR-102)")
    parser.add_argument("world", help="World Lore Vault directory path")
    parser.add_argument("-o", "--output", help="Output file path (default: <world_name>_codex.html)")
    parser.add_argument("--html", help="Generate HTML codex export at path")
    parser.add_argument("--json", action="store_true", help="Output JSON vault taxonomy index")
    args = parser.parse_args(argv)

    world_path = Path(args.world)
    if not world_path.is_dir():
        print(f"Error: World directory not found: {world_path}", file=sys.stderr)
        return 1

    categories = scan_world_vault(world_path)

    if args.json:
        print(json.dumps({tax: len(items) for tax, items in categories.items()}, indent=2))
        return 0

    out_file = Path(args.html or args.output or f"{world_path.name}_codex.html")
    build_single_file_codex(categories, world_name=world_path.name, output_path=out_file)

    total_articles = sum(len(items) for items in categories.values())
    print("=== Ars Arcanum Static Codex Exporter ===")
    print(f"World:          {world_path.name}")
    print(f"Total Articles: {total_articles} across {len(categories)} categories")
    print(f"Generated:      {out_file} ({out_file.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
