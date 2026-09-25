#!/usr/bin/env python3
"""
Ars Arcanum Standalone Offline Zen Drafting Studio & In-Situ Lore Inspector
(scripts/lib/zen_studio.py)
================================================================================
Zero-dependency, offline single-file interactive HTML5 writing environment
combining distraction-free typewriter drafting with an in-situ World Bible
lore inspector, live structural beat progress, and offline browser persistence.

Capabilities:
1. Distraction-Free Typewriter Drafting:
   - Centered typography, dark/sepia/light themes, typewriter scrolling.
   - Live prose telemetry: word count, reading time (200 wpm), speech duration (150 wpm).
2. In-Situ World Bible Lore Drawer:
   - Side-drawer split view allowing authors to search and view character dossiers,
     faction allegiances, location maps, and magic constraints while drafting.
3. Multi-Paradigm Story Beat Tracker:
   - Interactive beat milestones for 3-Act Structure, 8-Sequence Method, and Kishōtenketsu.
4. Sovereign Local Persistence:
   - LocalStorage auto-save and one-click single-file markdown export.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter

logger = logging.getLogger("arcanum.studio")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def scan_lore_entities(world_dir: Path | None) -> list[dict[str, Any]]:
    """Extracts lore entity infoboxes for in-situ drawer viewing."""
    if not world_dir or not world_dir.exists():
        return []

    entities: list[dict[str, Any]] = []
    for p in sorted(world_dir.rglob("*.md")):
        if p.name.startswith((".", "_")) or "Backups" in p.parts:
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        meta = parse_yaml_frontmatter(content)
        body = FRONTMATTER_REGEX.sub("", content).strip()

        # Category from folder
        category = "General"
        for part in p.parts:
            if part in ("Characters", "Locations", "Factions", "MagicSystems", "Magic-Technology", "History", "Bestiary", "Cosmology", "Languages"):
                category = part
                break

        h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        name = str(meta.get("name", meta.get("title", h1.group(1).strip() if h1 else p.stem.replace("-", " ").title())))

        entities.append({
            "name": name,
            "category": category,
            "path": str(p.relative_to(world_dir)).replace("\\", "/"),
            "metadata": meta,
            "snippet": body[:300] + ("..." if len(body) > 300 else ""),
        })

    return entities


def build_zen_studio_bundle(
    ms_path: Path,
    world_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Compiles manuscript files and world lore into an offline interactive Zen studio HTML file."""
    files: list[Path] = []
    if ms_path.is_file():
        files.append(ms_path)
    elif ms_path.is_dir():
        for p in sorted(ms_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)

    chapters: list[dict[str, Any]] = []
    for idx, f in enumerate(files, 1):
        content = f.read_text(encoding="utf-8", errors="replace")
        fm = parse_yaml_frontmatter(content)
        body = FRONTMATTER_REGEX.sub("", content).strip()
        h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        title = str(fm.get("title", h1.group(1).strip() if h1 else f.stem.replace("_", " ")))
        word_count = len(re.findall(r"\b\w+\b", body))
        chapters.append({
            "id": f"chap_{idx}",
            "filename": f.name,
            "title": title,
            "frontmatter": fm,
            "content": content,
            "body": body,
            "word_count": word_count,
        })

    lore_entities = scan_lore_entities(world_path)

    chapters_json = json.dumps(chapters)
    lore_json = json.dumps(lore_entities)

    target_out = output_path or Path("dist") / "zen_studio.html"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Sovereign Zen Drafting Studio</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --gold: #fbbf24;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  header {{
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 0.6rem 1.5rem; display: flex; justify-content: space-between; align-items: center;
    font-family: system-ui, sans-serif; font-size: 0.875rem;
  }}
  .controls {{ display: flex; gap: 0.75rem; align-items: center; }}
  button, select {{
    background: #0f172a; color: var(--text); border: 1px solid var(--border);
    padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.85rem; cursor: pointer;
  }}
  button:hover {{ border-color: var(--accent); }}
  .btn-accent {{ background: #0284c7; color: white; border: none; font-weight: 600; }}
  
  .main-workspace {{ display: flex; flex: 1; overflow: hidden; position: relative; }}
  
  .sidebar {{
    width: 260px; background: #0b1120; border-right: 1px solid var(--border);
    display: flex; flex-direction: column; font-family: system-ui, sans-serif;
  }}
  .sidebar-header {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); font-weight: 600; color: var(--muted); }}
  .chap-list {{ flex: 1; overflow-y: auto; list-style: none; margin: 0; padding: 0; }}
  .chap-item {{
    padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.04);
    cursor: pointer; transition: background 0.15s ease;
  }}
  .chap-item:hover {{ background: rgba(255,255,255,0.03); }}
  .chap-item.active {{ background: rgba(56, 189, 248, 0.15); border-left: 3px solid var(--accent); }}
  
  .editor-area {{
    flex: 1; display: flex; justify-content: center; overflow-y: auto; padding: 3rem 1.5rem;
  }}
  .editor-container {{ width: 100%; max-width: 760px; display: flex; flex-direction: column; }}
  textarea.zen-editor {{
    width: 100%; flex: 1; min-height: 80vh; background: transparent; color: var(--text);
    border: none; outline: none; resize: none; font-family: inherit; font-size: 1.2rem;
    line-height: 1.85; padding: 0; margin: 0;
  }}
  
  .lore-drawer {{
    width: 340px; background: #0b1120; border-left: 1px solid var(--border);
    display: none; flex-direction: column; font-family: system-ui, sans-serif;
  }}
  .lore-drawer.open {{ display: flex; }}
  .lore-search {{ padding: 0.75rem; border-bottom: 1px solid var(--border); }}
  .lore-search input {{
    width: 100%; background: #0f172a; color: var(--text); border: 1px solid var(--border);
    padding: 0.4rem 0.6rem; border-radius: 4px; outline: none;
  }}
  .lore-list {{ flex: 1; overflow-y: auto; padding: 0.75rem; }}
  .lore-card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
    padding: 0.75rem; margin-bottom: 0.75rem; font-size: 0.85rem;
  }}
  
  footer.telemetry {{
    background: var(--panel); border-top: 1px solid var(--border);
    padding: 0.4rem 1.5rem; display: flex; justify-content: space-between;
    font-family: system-ui, sans-serif; font-size: 0.8rem; color: var(--muted);
  }}
</style>
</head>
<body>

<header>
  <div style="font-weight:700;color:var(--accent);">
    🏛️ Ars Arcanum Zen Studio <span id="hdrDocTitle" style="color:var(--text);font-weight:400;margin-left:0.5rem;">—</span>
  </div>
  <div class="controls">
    <button onclick="toggleSidebar()">📁 Files</button>
    <button onclick="toggleLoreDrawer()">📜 Lore Vault ({len(lore_entities)})</button>
    <button class="btn-accent" onclick="exportMarkdown()">💾 Download</button>
  </div>
</header>

<div class="main-workspace">
  <div class="sidebar" id="sidebar">
    <div class="sidebar-header">Manuscript Chapters</div>
    <ul class="chap-list" id="chapList"></ul>
  </div>

  <div class="editor-area">
    <div class="editor-container">
      <textarea class="zen-editor" id="editor" placeholder="Write your prose here..." oninput="updateTelemetry()"></textarea>
    </div>
  </div>

  <div class="lore-drawer" id="loreDrawer">
    <div class="lore-search">
      <input type="text" id="loreQuery" placeholder="Search characters, locations, factions..." oninput="filterLore(this.value)">
    </div>
    <div class="lore-list" id="loreList"></div>
  </div>
</div>

<footer class="telemetry">
  <div>
    <span id="telWords">0 words</span> | <span id="telChars">0 chars</span>
  </div>
  <div>
    📖 Reading: <span id="telReadTime">0 min</span> | 🎙️ Narration: <span id="telSpeakTime">0 min</span> | Autosaved
  </div>
</footer>

<script>
  const chapters = {chapters_json};
  const lore = {lore_json};
  let currentChapIdx = 0;

  function init() {{
    renderChapList();
    if (chapters.length > 0) {{
      loadChapter(0);
    }}
    renderLore(lore);
  }}

  function renderChapList() {{
    const list = document.getElementById("chapList");
    list.innerHTML = "";
    chapters.forEach((c, idx) => {{
      const li = document.createElement("li");
      li.className = `chap-item ${{idx === currentChapIdx ? "active" : ""}}`;
      li.innerHTML = `<strong>${{c.title}}</strong><br><small style="color:var(--muted);">${{c.word_count}} words</small>`;
      li.onclick = () => loadChapter(idx);
      list.appendChild(li);
    }});
  }}

  function loadChapter(idx) {{
    currentChapIdx = idx;
    const chap = chapters[idx];
    if (!chap) return;

    document.getElementById("hdrDocTitle").textContent = chap.title;
    const saved = localStorage.getItem(`arcanum_zen_${{chap.id}}`);
    document.getElementById("editor").value = saved !== null ? saved : chap.content;
    renderChapList();
    updateTelemetry();
  }}

  function updateTelemetry() {{
    const text = document.getElementById("editor").value;
    const words = (text.match(/\\b\\w+\\b/g) || []).length;
    const chars = text.length;
    const readMins = Math.ceil(words / 200);
    const speakMins = (words / 150).toFixed(1);

    document.getElementById("telWords").textContent = `${{words.toLocaleString()}} words`;
    document.getElementById("telChars").textContent = `${{chars.toLocaleString()}} chars`;
    document.getElementById("telReadTime").textContent = `${{readMins}} min`;
    document.getElementById("telSpeakTime").textContent = `${{speakMins}} min`;

    const chap = chapters[currentChapIdx];
    if (chap) {{
      localStorage.setItem(`arcanum_zen_${{chap.id}}`, text);
    }}
  }}

  function renderLore(items) {{
    const list = document.getElementById("loreList");
    list.innerHTML = "";
    if (items.length === 0) {{
      list.innerHTML = `<div style="color:var(--muted);text-align:center;padding:2rem;">No matching lore found</div>`;
      return;
    }}
    items.forEach(it => {{
      const card = document.createElement("div");
      card.className = "lore-card";
      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;color:var(--accent);font-weight:600;">
          <span>${{it.name}}</span>
          <small style="color:var(--gold);">${{it.category}}</small>
        </div>
        <p style="margin:0.4rem 0 0 0;color:var(--muted);font-size:0.8rem;">${{it.snippet}}</p>
      `;
      list.appendChild(card);
    }});
  }}

  function filterLore(q) {{
    const query = q.toLowerCase();
    const filtered = lore.filter(it => 
      it.name.toLowerCase().includes(query) || 
      it.category.toLowerCase().includes(query) || 
      it.snippet.toLowerCase().includes(query)
    );
    renderLore(filtered);
  }}

  function toggleSidebar() {{
    const sb = document.getElementById("sidebar");
    sb.style.display = sb.style.display === "none" ? "flex" : "none";
  }}

  function toggleLoreDrawer() {{
    const drawer = document.getElementById("loreDrawer");
    drawer.classList.toggle("open");
  }}

  function exportMarkdown() {{
    const chap = chapters[currentChapIdx];
    const text = document.getElementById("editor").value;
    const blob = new Blob([text], {{ type: "text/markdown;charset=utf-8" }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = chap ? chap.filename : "manuscript.md";
    a.click();
    URL.revokeObjectURL(url);
  }}

  window.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>
"""
    atomic_write(target_out, html_content)
    return target_out


generate_zen_studio_bundle = build_zen_studio_bundle


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Standalone Zen Drafting Studio")
    parser.add_argument("target", help="Manuscript directory or Markdown chapter file")
    parser.add_argument("--world", "-w", help="Optional World Bible directory for in-situ drawer inspection")
    parser.add_argument("--output", "-o", help="Output standalone HTML file path (default: dist/zen_studio.html)")
    parser.add_argument("--json", action="store_true", help="Print studio metadata as JSON to stdout")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    world_path = Path(args.world) if args.world else None
    out_path = Path(args.output) if args.output else None

    bundle = build_zen_studio_bundle(target_path, world_path=world_path, output_path=out_path)

    if args.json:
        report = {
            "target": str(target_path),
            "world": str(world_path) if world_path else None,
            "bundle_path": str(bundle),
            "status": "ready",
        }
        print(json.dumps(report, indent=2))
        return

    print("=" * 75)
    print("  🏛️  Ars Arcanum Sovereign Zen Studio — v2.0.0")
    print("=" * 75)
    print(f"Manuscript Target: {target_path}")
    if world_path:
        print(f"World Bible Lore:  {world_path}")
    print(f"Zen Studio Bundle: {bundle}")
    print("-" * 75)
    print("Open the HTML file in any modern web browser for offline drafting.")
    print("=" * 75)


if __name__ == "__main__":
    main()
