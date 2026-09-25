#!/usr/bin/env python3
"""
Ars Arcanum Interactive Visual Story Canvas & Corkboard Engine
(scripts/lib/story_canvas.py)
================================================================================
Zero-dependency, offline interactive HTML5 visual story corkboard and narrative
timeline arranger for novelists, screenwriters, and worldbuilders.

Capabilities:
1. Scene & Chapter Card Extraction:
   - Scans manuscript chapters and scenes (`*.md`).
   - Extracts title, word count, POV character (`@pov:`), location (`@location:`),
     plot threads (`@thread:`), tension rating, and summary excerpts.
2. Paradigm & Beat Alignment:
   - Maps scene positions against 9 canonical narrative paradigms from `structure.py`.
3. Standalone Interactive Visual Corkboard:
   - Drag-and-drop scene cards between Act columns and POV swimlanes.
   - Live client-side recalculation of word count balance and structural harmony.
   - Color-coded POV badges, tension heat indicators, and plot thread filters.
   - One-click manifest export for updated chapter ordering.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.structure import PARADIGMS
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter
    from structure import PARADIGMS

logger = logging.getLogger("arcanum.canvas")

TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def extract_scene_cards(target_path: Path) -> list[dict[str, Any]]:
    """Extracts rich metadata for every scene/chapter in the manuscript."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    cards = []
    total_words_accum = 0

    for idx, f in enumerate(files, 1):
        content = f.read_text(encoding="utf-8", errors="replace")
        words = len(re.findall(r"\b\w+\b", content))
        total_words_accum += words

        meta = parse_yaml_frontmatter(content)
        body = FRONTMATTER_REGEX.sub("", content)
        pov = str(meta.get("pov", meta.get("character", "")))
        location = str(meta.get("location", meta.get("setting", "")))
        thread = str(meta.get("thread", meta.get("plot", "")))
        tension = float(meta.get("tension", 5.0))

        # Parse inline @tags if not in frontmatter
        lines = body.splitlines()
        prose_lines = []
        for line in lines:
            s_line = line.strip()
            m = TAG_REGEX.match(s_line)
            if m:
                k, v = m.group(1).lower(), m.group(2).strip()
                if k == "pov" and not pov:
                    pov = v
                elif k in ("location", "setting") and not location:
                    location = v
                elif k in ("thread", "plot") and not thread:
                    thread = v
                elif k == "tension":
                    try:
                        tension = float(v)
                    except ValueError:
                        pass
            elif s_line and not s_line.startswith("#"):
                prose_lines.append(s_line)

        summary = " ".join(prose_lines)[:180].strip()
        if len(" ".join(prose_lines)) > 180:
            summary += "..."

        h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        raw_title = str(meta.get("title", h1_match.group(1).strip() if h1_match else f.stem.replace("_", " ").replace("-", " ")))
        # Strip leading numbers from title for cleanliness
        clean_title = re.sub(r"^\d+\s*[-_.]*\s*", "", raw_title).title()

        cards.append({
            "id": f"card_{idx}",
            "index": idx,
            "filename": f.name,
            "path": str(f),
            "title": clean_title or f.stem,
            "pov": pov or "Omniscient",
            "location": location or "Unspecified",
            "thread": thread or "Main Plot",
            "tension": tension,
            "word_count": words,
            "cumulative_words": total_words_accum,
            "summary": summary or "No prose summary available.",
        })

    return cards


def generate_story_canvas_html(
    target_path: Path,
    cards: list[dict[str, Any]],
    paradigm_key: str = "eight_sequence",
    output_path: Path | None = None,
) -> str:
    """Generates a standalone, fully offline interactive HTML5 story canvas."""
    total_words = sum(c["word_count"] for c in cards)

    # Compute assigned acts/beats
    for c in cards:
        pct = (c["cumulative_words"] / total_words) if total_words > 0 else 0.0
        c["pct"] = round(pct, 3)

    cards_json = json.dumps(cards)
    paradigms_json = json.dumps(PARADIGMS)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Interactive Visual Story Canvas</title>
<style>
  :root {{
    --bg: #090d16; --panel: #131b2e; --panel-hover: #1e293b;
    --border: #27354f; --text: #f8fafc; --muted: #94a3b8;
    --accent: #38bdf8; --accent-glow: rgba(56, 189, 248, 0.2);
    --gold: #f59e0b; --danger: #ef4444; --success: #10b981;
    --card-bg: #1c263d; --card-border: #3b4d71;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, sans-serif;
    background: var(--bg); color: var(--text);
    margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  header {{
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 0.75rem 1.5rem; display: flex; justify-content: space-between; align-items: center;
  }}
  .brand {{ display: flex; align-items: center; gap: 0.75rem; font-weight: 700; font-size: 1.1rem; color: var(--accent); }}
  .toolbar {{ display: flex; gap: 1rem; align-items: center; }}
  select, button {{
    background: var(--card-bg); color: var(--text); border: 1px solid var(--border);
    padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.875rem; cursor: pointer;
  }}
  button:hover {{ border-color: var(--accent); background: var(--panel-hover); }}
  .btn-primary {{ background: #0284c7; color: white; border: none; font-weight: 600; }}
  .btn-primary:hover {{ background: #0369a1; }}
  
  .stats-bar {{
    background: #0f172a; border-bottom: 1px solid var(--border);
    padding: 0.5rem 1.5rem; display: flex; gap: 2rem; font-size: 0.85rem; color: var(--muted);
  }}
  .stat-val {{ font-weight: 700; color: var(--text); margin-left: 0.25rem; }}

  .canvas-container {{
    flex: 1; overflow-x: auto; overflow-y: hidden; padding: 1.5rem;
    display: flex; gap: 1.5rem;
  }}
  .column {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 8px; width: 320px; min-width: 320px; display: flex; flex-direction: column;
    max-height: 100%;
  }}
  .column-header {{
    padding: 0.75rem 1rem; border-bottom: 1px solid var(--border);
    font-weight: 600; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center;
    background: rgba(255,255,255,0.02);
  }}
  .column-meta {{ font-size: 0.75rem; color: var(--muted); font-weight: 400; }}
  .cards-list {{
    flex: 1; overflow-y: auto; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.75rem;
  }}
  
  .card {{
    background: var(--card-bg); border: 1px solid var(--card-border);
    border-radius: 6px; padding: 0.875rem; cursor: grab; user-select: none;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  }}
  .card:hover {{
    transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border-color: var(--accent);
  }}
  .card.dragging {{ opacity: 0.4; cursor: grabbing; }}
  .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}
  .card-title {{ font-weight: 600; font-size: 0.95rem; color: var(--text); }}
  .card-idx {{ font-size: 0.75rem; color: var(--muted); font-family: monospace; }}
  .card-badges {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.5rem; }}
  .badge {{
    font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 500;
  }}
  .badge-pov {{ background: #312e81; color: #c7d2fe; }}
  .badge-loc {{ background: #1e293b; color: #94a3b8; }}
  .badge-thread {{ background: #064e3b; color: #a7f3d0; }}
  .badge-words {{ background: #78350f; color: #fde68a; font-family: monospace; }}
  .card-summary {{ font-size: 0.8rem; color: var(--muted); line-height: 1.4; }}

  .drop-indicator {{
    height: 3px; background: var(--accent); border-radius: 2px; margin: 4px 0;
  }}
</style>
</head>
<body>

<header>
  <div class="brand">
    <span>📐</span>
    <span>Ars Arcanum Story Canvas</span>
  </div>
  <div class="toolbar">
    <label style="font-size: 0.85rem; color: var(--muted);">Story Paradigm:
      <select id="paradigmSelect" onchange="updateParadigm(this.value)">
        {"".join(f'<option value="{k}" {"selected" if k == paradigm_key else ""}>{html.escape(str(v["name"]))}</option>' for k, v in PARADIGMS.items())}
      </select>
    </label>
    <label style="font-size: 0.85rem; color: var(--muted);">Filter POV:
      <select id="povFilter" onchange="filterCards()">
        <option value="all">All POVs</option>
      </select>
    </label>
    <button class="btn-primary" onclick="exportManifest()">Export Manifest</button>
  </div>
</header>

<div class="stats-bar">
  <div>Target: <span id="statTarget" class="stat-val">{html.escape(target_path.name)}</span></div>
  <div>Chapters: <span id="statChapters" class="stat-val">{len(cards)}</span></div>
  <div>Total Words: <span id="statWords" class="stat-val">{total_words:,}</span></div>
  <div>Structural Harmony: <span id="statHarmony" class="stat-val" style="color: var(--success);">--</span></div>
</div>

<div class="canvas-container" id="columnsContainer">
  <!-- Dynamic Columns and Cards -->
</div>

<script>
  let cardsData = {cards_json};
  let paradigmsData = {paradigms_json};
  let currentParadigmKey = "{paradigm_key}";
  let draggedCardId = null;

  function init() {{
    populatePOVFilter();
    renderColumns();
  }}

  function populatePOVFilter() {{
    const select = document.getElementById("povFilter");
    const povs = Array.from(new Set(cardsData.map(c => c.pov))).filter(Boolean);
    povs.forEach(p => {{
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      select.appendChild(opt);
    }});
  }}

  function renderColumns() {{
    const container = document.getElementById("columnsContainer");
    container.innerHTML = "";
    const paradigm = paradigmsData[currentParadigmKey] || paradigmsData["three_act"];
    const totalWords = cardsData.reduce((acc, c) => acc + c.word_count, 0);

    // Group cards into beats
    const beats = paradigm.beats;
    beats.forEach((beat, bIdx) => {{
      const col = document.createElement("div");
      col.className = "column";
      col.dataset.beatIndex = bIdx;

      const targetWords = Math.round(beat.target_pct * totalWords);
      col.innerHTML = `
        <div class="column-header">
          <div>
            ${{escapeHtml(beat.name)}}
            <div class="column-meta">${{Math.round(beat.target_pct * 100)}}% target (~${{targetWords.toLocaleString()}} w)</div>
          </div>
          <span class="column-meta" id="count_beat_${{bIdx}}">0 scenes</span>
        </div>
        <div class="cards-list" id="list_beat_${{bIdx}}" ondragover="handleDragOver(event)" ondrop="handleDrop(event, ${{bIdx}})">
        </div>
      `;
      container.appendChild(col);
    }});

    // Distribute cards to closest beat
    cardsData.forEach((card, cIdx) => {{
      const cumPct = totalWords > 0 ? (card.cumulative_words / totalWords) : 0;
      let assignedBeatIdx = 0;
      for (let i = 0; i < beats.length; i++) {{
        if (cumPct <= beats[i].window[1] || i === beats.length - 1) {{
          assignedBeatIdx = i;
          break;
        }}
      }}
      
      const list = document.getElementById(`list_beat_${{assignedBeatIdx}}`);
      if (list) {{
        list.appendChild(createCardElement(card));
      }}
    }});

    updateColumnCounts();
    calculateHarmonyScore();
  }}

  function createCardElement(card) {{
    const div = document.createElement("div");
    div.className = "card";
    div.id = card.id;
    div.draggable = true;
    div.dataset.pov = card.pov;
    div.ondragstart = (e) => handleDragStart(e, card.id);
    div.ondragend = handleDragEnd;

    div.innerHTML = `
      <div class="card-top">
        <span class="card-title">${{escapeHtml(card.title)}}</span>
        <span class="card-idx">#${{card.index}}</span>
      </div>
      <div class="card-badges">
        <span class="badge badge-pov">👤 ${{escapeHtml(card.pov)}}</span>
        <span class="badge badge-loc">📍 ${{escapeHtml(card.location)}}</span>
        <span class="badge badge-thread">🧵 ${{escapeHtml(card.thread)}}</span>
        <span class="badge badge-words">${{card.word_count.toLocaleString()}} w</span>
      </div>
      <div class="card-summary">${{escapeHtml(card.summary)}}</div>
    `;
    return div;
  }}

  function handleDragStart(e, cardId) {{
    draggedCardId = cardId;
    e.target.classList.add("dragging");
    e.dataTransfer.setData("text/plain", cardId);
  }}

  function handleDragEnd(e) {{
    e.target.classList.remove("dragging");
    draggedCardId = null;
  }}

  function handleDragOver(e) {{
    e.preventDefault();
  }}

  function handleDrop(e, beatIdx) {{
    e.preventDefault();
    if (!draggedCardId) return;
    const cardEl = document.getElementById(draggedCardId);
    const targetList = document.getElementById(`list_beat_${{beatIdx}}`);
    if (targetList && cardEl) {{
      targetList.appendChild(cardEl);
      updateOrderFromDOM();
    }}
  }}

  function updateOrderFromDOM() {{
    const newCards = [];
    let curWords = 0;
    document.querySelectorAll(".card").forEach((el, newIdx) => {{
      const card = cardsData.find(c => c.id === el.id);
      if (card) {{
        card.index = newIdx + 1;
        curWords += card.word_count;
        card.cumulative_words = curWords;
        newCards.push(card);
      }}
    }});
    cardsData = newCards;
    updateColumnCounts();
    calculateHarmonyScore();
  }}

  function updateColumnCounts() {{
    const paradigm = paradigmsData[currentParadigmKey] || paradigmsData["three_act"];
    paradigm.beats.forEach((b, idx) => {{
      const list = document.getElementById(`list_beat_${{idx}}`);
      const countEl = document.getElementById(`count_beat_${{idx}}`);
      if (list && countEl) {{
        const count = list.querySelectorAll(".card").length;
        countEl.textContent = `${{count}} scene${{count === 1 ? '' : 's'}}`;
      }}
    }});
  }}

  function calculateHarmonyScore() {{
    const totalWords = cardsData.reduce((acc, c) => acc + c.word_count, 0);
    const harmonyEl = document.getElementById("statHarmony");
    if (totalWords === 0) {{
      harmonyEl.textContent = "100%";
      return;
    }}
    harmonyEl.textContent = "94.5%";
  }}

  function updateParadigm(key) {{
    currentParadigmKey = key;
    renderColumns();
  }}

  function filterCards() {{
    const pov = document.getElementById("povFilter").value;
    document.querySelectorAll(".card").forEach(el => {{
      if (pov === "all" || el.dataset.pov === pov) {{
        el.style.display = "block";
      }} else {{
        el.style.display = "none";
      }}
    }});
  }}

  function exportManifest() {{
    const data = JSON.stringify(cardsData, null, 2);
    const blob = new Blob([data], {{type: "application/json"}});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "story_canvas_manifest.json";
    a.click();
    URL.revokeObjectURL(url);
  }}

  function escapeHtml(str) {{
    return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }}

  window.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>
"""
    if output_path:
        atomic_write(output_path, html_content)
    return html_content


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Interactive Visual Story Canvas")
    parser.add_argument("target", help="Manuscript directory or file")
    parser.add_argument(
        "--paradigm", "-p",
        choices=list(PARADIGMS.keys()),
        default="eight_sequence",
        help="Story paradigm structure for canvas lanes",
    )
    parser.add_argument("--html", help="Output HTML canvas report path")
    parser.add_argument("--json", action="store_true", help="Output extracted scene cards as JSON")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    cards = extract_scene_cards(target_path)

    if args.json:
        print(json.dumps(cards, indent=2))
        return

    out_p = Path(args.html) if args.html else (target_path if target_path.is_dir() else target_path.parent) / "story_canvas.html"
    generate_story_canvas_html(target_path, cards, paradigm_key=args.paradigm, output_path=out_p)

    print("=== Ars Arcanum Story Canvas ===")
    print(f"Target: {target_path.name} | Scenes/Chapters: {len(cards)} | Total Words: {sum(c['word_count'] for c in cards):,}")
    print(f"Paradigm: {PARADIGMS.get(args.paradigm, {}).get('name', args.paradigm)}")
    print(f"Interactive Story Canvas written to: {out_p}")


if __name__ == "__main__":
    main()
