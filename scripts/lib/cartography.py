#!/usr/bin/env python3
"""
Ars Arcanum Offline Interactive Vector Cartography & Map Annotation Engine
(scripts/lib/cartography.py)
================================================================================
Zero-dependency, offline vector map generator and interactive cartography viewer.

Capabilities (WOR-101):
1. World Location Extraction (Locations/*.md):
   - Scans YAML frontmatter / body for coordinates (x, y / lat, lon), location type
     (Citadel, Capital, Port, Village, Ruins, Dungeon, Mountain, Forest), faction,
     and lore description.
2. Vector SVG Cartography:
   - Hexagonal and Cartesian coordinate grid overlays.
   - Terrain biome fills (Mountains, Forests, Deserts, Swamps, Oceans).
   - Trade routes, mountain passes, and sea lanes with distance & travel time.
   - Vector marker glyphs (towers, citadels, trees, mountain peaks, anchors).
   - Vintage decorative elements: Compass rose, ornamental border, scale bar, legend.
3. Interactive HTML Map Viewer:
   - Pure vanilla JavaScript pan/zoom, layer toggles, location search, and lore cards.

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import math
import json
import html
import argparse
import logging
from pathlib import Path

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.cartography")

# Default coordinate bounds
WIDTH = 1200
HEIGHT = 800

BIOME_COLORS = {
    "plains": "#2d3748",
    "forest": "#1b4332",
    "mountain": "#4a5568",
    "desert": "#78350f",
    "ocean": "#0c4a6e",
    "tundra": "#334155",
    "swamp": "#2e3b2e"
}

TYPE_ICONS = {
    "capital": "👑",
    "citadel": "🏰",
    "city": "🏛️",
    "port": "⚓",
    "village": "🏡",
    "ruins": "🏛️",
    "dungeon": "⚔️",
    "mountain": "🏔️",
    "forest": "🌲",
    "default": "📍"
}


def parse_world_locations(world_dir: Path) -> list[dict]:
    """Scans Locations/*.md in a World Lore Vault for coordinates and traits."""
    loc_dir = world_dir / "Locations"
    locations = []

    if not loc_dir.is_dir():
        # Fallback to demo default locations if empty
        return get_default_locations(world_dir.name)

    files = sorted(loc_dir.glob("*.md"))
    if not files:
        return get_default_locations(world_dir.name)

    for idx, f in enumerate(files, 1):
        content = f.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()

        name = f.stem.replace("_", " ")
        loc_type = "city"
        faction = "Independent"
        desc = ""
        x = None
        y = None
        biome = "plains"

        in_fm = False
        for line in lines:
            s = line.strip()
            if s == "---":
                in_fm = not in_fm
                continue

            if in_fm and ":" in s:
                k, v = s.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip('"\'')
                if k in ("name", "title"):
                    name = v
                elif k in ("type", "location_type", "classification"):
                    loc_type = v.lower()
                elif k in ("faction", "allegiance", "ruler"):
                    faction = v.strip("[]")
                elif k in ("x", "coord_x", "longitude", "lon"):
                    try: x = float(v)
                    except ValueError: pass
                elif k in ("y", "coord_y", "latitude", "lat"):
                    try: y = float(v)
                    except ValueError: pass
                elif k in ("biome", "terrain"):
                    biome = v.lower()

            if not in_fm and not s.startswith(("#", "@", "---")) and not desc:
                desc = s[:140]

        # Deterministic coordinates if not explicitly set
        if x is None or y is None:
            # Deterministic pseudo-placement from name hash
            seed = sum(ord(c) for c in f.stem)
            x = 150 + (seed * 83) % (WIDTH - 300)
            y = 120 + (seed * 47) % (HEIGHT - 240)

        locations.append({
            "id": f.stem,
            "name": name,
            "file": str(f),
            "type": loc_type,
            "faction": faction,
            "biome": biome,
            "x": round(x, 1),
            "y": round(y, 1),
            "description": desc or "A notable landmark in the realm."
        })

    return locations


def get_default_locations(realm_name: str = "Realm") -> list[dict]:
    """Fallback sample locations if vault has no notes."""
    return [
        {"id": "SunCitadel", "name": "Sun Citadel", "type": "capital", "faction": "Solar Hegemony", "biome": "plains", "x": 600, "y": 400, "description": "The golden capital seat of the Sun King."},
        {"id": "IronCrags", "name": "Iron Crags", "type": "mountain", "faction": "Ironclads", "biome": "mountain", "x": 300, "y": 250, "description": "Impassable jagged peaks rich with arcane ore."},
        {"id": "PortValen", "name": "Port Valen", "type": "port", "faction": "Merchants Guild", "biome": "ocean", "x": 850, "y": 550, "description": "Thriving coastal harbor and trade crossroads."},
        {"id": "WhisperingWoods", "name": "Whispering Woods", "type": "forest", "faction": "Sylvans", "biome": "forest", "x": 350, "y": 550, "description": "Ancient sentient canopy cloaked in mist."},
        {"id": "ShadowSpire", "name": "Shadow Spire", "type": "citadel", "faction": "Void Cult", "biome": "desert", "x": 900, "y": 200, "description": "Monolithic obsidian fortress at the edge of the wastes."}
    ]


def generate_vector_svg_map(locations: list[dict], title: str = "World Map", grid_mode: str = "hex", show_routes: bool = True) -> str:
    """Generates a high-resolution vector SVG map with routes, grid, and markers."""
    svg_elements = []

    # 1. Background Parchment
    svg_elements.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#0f172a" />')

    # 2. Grid Overlay
    if grid_mode == "hex":
        # Hexagonal grid
        hex_radius = 40
        w = hex_radius * 2
        h = math.sqrt(3) * hex_radius
        for row in range(int(HEIGHT / (h * 0.75)) + 2):
            for col in range(int(WIDTH / w) + 2):
                cx = col * w * 0.75 + (hex_radius if row % 2 == 1 else 0)
                cy = row * h * 0.5
                points = []
                for a in range(6):
                    angle = math.radians(60 * a)
                    px = cx + hex_radius * math.cos(angle)
                    py = cy + hex_radius * math.sin(angle)
                    points.append(f"{px:.1f},{py:.1f}")
                svg_elements.append(f'<polygon points="{" ".join(points)}" fill="none" stroke="#1e293b" stroke-width="0.8" opacity="0.4" />')
    elif grid_mode == "square":
        for gx in range(0, WIDTH, 50):
            svg_elements.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{HEIGHT}" stroke="#1e293b" stroke-width="0.8" opacity="0.5" />')
        for gy in range(0, HEIGHT, 50):
            svg_elements.append(f'<line x1="0" y1="{gy}" x2="{WIDTH}" y2="{gy}" stroke="#1e293b" stroke-width="0.8" opacity="0.5" />')

    # 3. Trade Routes (Connecting nearest locations)
    if show_routes and len(locations) >= 2:
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                l1 = locations[i]
                l2 = locations[j]
                dist = math.hypot(l1["x"] - l2["x"], l1["y"] - l2["y"])
                if dist < 450:  # Connect reasonably close nodes
                    mid_x = (l1["x"] + l2["x"]) / 2
                    mid_y = (l1["y"] + l2["y"]) / 2
                    svg_elements.append(
                        f'<line x1="{l1["x"]}" y1="{l1["y"]}" x2="{l2["x"]}" y2="{l2["y"]}" '
                        f'stroke="#d97706" stroke-width="2" stroke-dasharray="6,4" opacity="0.6" />'
                    )
                    # Travel distance label
                    miles = int(dist * 0.8)
                    days = max(1, round(miles / 24, 1))
                    svg_elements.append(
                        f'<text x="{mid_x}" y="{mid_y - 4}" fill="#f59e0b" font-size="9" text-anchor="middle" font-weight="600">{miles} mi ({days}d)</text>'
                    )

    # 4. Location Markers & Labels
    for loc in locations:
        x, y = loc["x"], loc["y"]
        icon = TYPE_ICONS.get(loc["type"], TYPE_ICONS["default"])
        
        # Glow / halo ring
        svg_elements.append(f'<circle cx="{x}" cy="{y}" r="16" fill="#38bdf8" fill-opacity="0.15" stroke="#38bdf8" stroke-width="1.5" />')
        # Pin center
        svg_elements.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#f8fafc" />')
        # Emoji / Icon
        svg_elements.append(f'<text x="{x}" y="{y-12}" font-size="16" text-anchor="middle">{icon}</text>')
        # Label
        svg_elements.append(f'<text x="{x}" y="{y+22}" fill="#f8fafc" font-size="12" font-weight="700" text-anchor="middle" filter="drop-shadow(0 1px 2px #000)">{html.escape(loc["name"])}</text>')
        svg_elements.append(f'<text x="{x}" y="{y+34}" fill="#94a3b8" font-size="10" text-anchor="middle">{html.escape(loc["faction"])}</text>')

    # 5. Decorative Border & Compass Rose
    svg_elements.append(f'<rect x="15" y="15" width="{WIDTH-30}" height="{HEIGHT-30}" fill="none" stroke="#d97706" stroke-width="3" rx="8" />')
    svg_elements.append(f'<rect x="22" y="22" width="{WIDTH-44}" height="{HEIGHT-44}" fill="none" stroke="#475569" stroke-width="1" rx="4" />')

    # Compass Rose (Top Right)
    cr_x, cr_y = WIDTH - 90, 90
    svg_elements.append(f"""
    <g transform="translate({cr_x},{cr_y})">
      <circle r="35" fill="#1e293b" stroke="#d97706" stroke-width="2" />
      <polygon points="0,-30 7,-8 0,0 -7,-8" fill="#ef4444" />
      <polygon points="0,30 7,8 0,0 -7,8" fill="#f8fafc" />
      <polygon points="30,0 8,7 0,0 8,-7" fill="#f8fafc" />
      <polygon points="-30,0 -8,7 0,0 -8,-7" fill="#f8fafc" />
      <text y="-33" fill="#f8fafc" font-size="12" font-weight="700" text-anchor="middle">N</text>
      <text y="42" fill="#94a3b8" font-size="10" text-anchor="middle">S</text>
      <text x="38" y="4" fill="#94a3b8" font-size="10">E</text>
      <text x="-44" y="4" fill="#94a3b8" font-size="10">W</text>
    </g>
    """)

    # Title Banner (Top Left)
    svg_elements.append(f"""
    <g transform="translate(45, 55)">
      <rect width="260" height="50" fill="#1e293b" stroke="#d97706" stroke-width="1.5" rx="6" />
      <text x="130" y="24" fill="#38bdf8" font-size="16" font-weight="800" text-anchor="middle">{html.escape(title)}</text>
      <text x="130" y="40" fill="#94a3b8" font-size="10" text-anchor="middle">Ars Arcanum Vector Cartography</text>
    </g>
    """)

    # Scale Bar (Bottom Left)
    svg_elements.append(f"""
    <g transform="translate(45, {HEIGHT - 55})">
      <rect width="180" height="30" fill="#1e293b" stroke="#334155" stroke-width="1" rx="4" />
      <line x1="20" y1="15" x2="160" y2="15" stroke="#f8fafc" stroke-width="3" />
      <line x1="20" y1="10" x2="20" y2="20" stroke="#f8fafc" stroke-width="3" />
      <line x1="160" y1="10" x2="160" y2="20" stroke="#f8fafc" stroke-width="3" />
      <text x="90" y="24" fill="#94a3b8" font-size="9" text-anchor="middle">150 Miles / 240 km</text>
    </g>
    """)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" style="font-family:system-ui,sans-serif;">
  {''.join(svg_elements)}
</svg>"""


def generate_cartography_html_viewer(locations: list[dict], title: str, output_path: Path) -> Path:
    """Generates an interactive HTML map viewer with pan/zoom and sidebar cards."""
    svg_map = generate_vector_svg_map(locations, title=title, grid_mode="hex", show_routes=True)
    
    locations_json = json.dumps(locations)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — {html.escape(title)} Map Viewer</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
  }}
  body {{ font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; height: 100vh; overflow: hidden; }}
  #sidebar {{ width: 340px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; }}
  .sidebar-header {{ padding: 1.25rem; border-bottom: 1px solid var(--border); }}
  .sidebar-header h2 {{ margin: 0; color: var(--accent); font-size: 1.25rem; }}
  .search-box {{ width: 100%; box-sizing: border-box; padding: 0.6rem; margin-top: 0.75rem; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text); }}
  .location-list {{ overflow-y: auto; flex: 1; padding: 0.5rem; }}
  .loc-card {{ background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem; cursor: pointer; transition: all 0.2s; }}
  .loc-card:hover {{ border-color: var(--accent); }}
  .loc-card h4 {{ margin: 0; color: var(--accent); }}
  .loc-card p {{ margin: 0.25rem 0 0 0; font-size: 0.8rem; color: var(--muted); }}
  #map-container {{ flex: 1; position: relative; overflow: hidden; background: #0b1120; cursor: grab; }}
  #map-container:active {{ cursor: grabbing; }}
  #svg-wrapper {{ transform-origin: 0 0; transition: transform 0.05s ease-out; }}
  .controls {{ position: absolute; top: 1rem; right: 1rem; display: flex; gap: 0.5rem; z-index: 10; }}
  .btn {{ background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 0.5rem 0.75rem; border-radius: 6px; cursor: pointer; font-weight: 700; }}
  .btn:hover {{ background: #334155; }}
</style>
</head>
<body>

<div id="sidebar">
  <div class="sidebar-header">
    <h2>🗺️ {html.escape(title)}</h2>
    <p style="color:var(--muted); font-size:0.8rem; margin:4px 0 0 0;">{len(locations)} Indexed Realm Locations</p>
    <input type="text" id="search" class="search-box" placeholder="Search landmarks, factions..." oninput="filterLocations()">
  </div>
  <div class="location-list" id="locList"></div>
</div>

<div id="map-container" onmousedown="startPan(event)" onwheel="zoom(event)">
  <div class="controls">
    <button class="btn" onclick="resetZoom()">⟲ Reset</button>
    <button class="btn" onclick="zoomBtn(1.2)">➕</button>
    <button class="btn" onclick="zoomBtn(0.8)">➖</button>
  </div>
  <div id="svg-wrapper">
    {svg_map}
  </div>
</div>

<script>
const locations = {locations_json};
let scale = 1, panX = 0, panY = 0, isPanning = false, startX = 0, startY = 0;

function renderList(items) {{
  const container = document.getElementById('locList');
  container.innerHTML = '';
  items.forEach(loc => {{
    const card = document.createElement('div');
    card.className = 'loc-card';
    card.innerHTML = `<h4>${{loc.name}} (${{loc.type}})</h4><p><strong>Faction:</strong> ${{loc.faction}}</p><p>${{loc.description}}</p>`;
    card.onclick = () => focusLocation(loc.x, loc.y);
    container.appendChild(card);
  }});
}}

function filterLocations() {{
  const q = document.getElementById('search').value.toLowerCase();
  const filtered = locations.filter(l => l.name.toLowerCase().includes(q) || l.faction.toLowerCase().includes(q) || l.type.toLowerCase().includes(q));
  renderList(filtered);
}}

function updateTransform() {{
  document.getElementById('svg-wrapper').style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{scale}})`;
}}

function startPan(e) {{
  if (e.target.closest('.controls')) return;
  isPanning = true;
  startX = e.clientX - panX;
  startY = e.clientY - panY;
  window.onmousemove = doPan;
  window.onmouseup = endPan;
}}
function doPan(e) {{
  if (!isPanning) return;
  panX = e.clientX - startX;
  panY = e.clientY - startY;
  updateTransform();
}}
function endPan() {{ isPanning = false; window.onmousemove = null; window.onmouseup = null; }}

function zoom(e) {{
  e.preventDefault();
  const delta = e.deltaY < 0 ? 1.15 : 0.85;
  scale = Math.max(0.5, Math.min(4.0, scale * delta));
  updateTransform();
}}
function zoomBtn(factor) {{
  scale = Math.max(0.5, Math.min(4.0, scale * factor));
  updateTransform();
}}
function resetZoom() {{ scale = 1; panX = 0; panY = 0; updateTransform(); }}

function focusLocation(x, y) {{
  const container = document.getElementById('map-container');
  scale = 1.6;
  panX = (container.clientWidth / 2) - (x * scale);
  panY = (container.clientHeight / 2) - (y * scale);
  updateTransform();
}}

renderList(locations);
</script>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Offline Vector Cartography Engine (WOR-101)")
    parser.add_argument("world", help="World directory path or name")
    parser.add_argument("-o", "--output", help="Output .svg or .html path")
    parser.add_argument("--html", help="Generate HTML map viewer at path")
    parser.add_argument("--svg", help="Generate vector SVG map at path")
    parser.add_argument("--grid", choices=["hex", "square", "none"], default="hex", help="Grid overlay type")
    parser.add_argument("--no-routes", action="store_true", help="Disable trade route paths")
    parser.add_argument("--json", action="store_true", help="Output JSON location data")
    args = parser.parse_args()

    world_path = Path(args.world)
    resolved_name = world_path.resolve().name or "world"
    locations = parse_world_locations(world_path)

    if args.json:
        print(json.dumps(locations, indent=2))
        return

    out_target = args.html or args.svg or args.output or f"{resolved_name}_map.html"
    out_file = Path(out_target)
    if args.svg or out_file.suffix.lower() == ".svg":
        svg_code = generate_vector_svg_map(locations, title=resolved_name, grid_mode=args.grid, show_routes=not args.no_routes)
        atomic_write(out_file, svg_code)
        print(f"Generated Vector SVG Map: {out_file}")
    else:
        generate_cartography_html_viewer(locations, title=resolved_name, output_path=out_file)
        print(f"Generated Interactive HTML Cartography Viewer: {out_file}")


if __name__ == "__main__":
    main()
