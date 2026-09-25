# Ars Arcanum Offline Vector Cartography & Map Annotation Guide (`docs/CARTOGRAPHY.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Cartography Engine** (`scripts/lib/cartography.py`) is a zero-dependency, 100% offline vector map generator and interactive cartography viewer.

Writers and worldbuilders require spatial clarity to visualize kingdom borders, travel routes, and distances between citadels, ports, and ruins. The Cartography Engine converts markdown location notes into scalable vector graphics (SVG) maps and interactive HTML map viewers without requiring external mapping tools or GIS software.

---

## 2. World Lore Schema: Location Notes

Locations are extracted from `World/Locations/*.md` notes using YAML frontmatter:

```markdown
---
name: "Sun Citadel"
type: "capital"
faction: "Solar Hegemony"
biome: "plains"
x: 600
y: 400
---

# Sun Citadel

The golden capital seat of the Sun King, situated at the crossroads of the Grand Imperial Highway.
```

### Supported Frontmatter Attributes:
- `name` / `title`: Display name of the landmark.
- `type` / `location_type`: Classification (`capital`, `citadel`, `city`, `port`, `village`, `ruins`, `dungeon`, `mountain`, `forest`).
- `faction` / `allegiance`: Ruling or controlling power.
- `biome` / `terrain`: Biome fill (`plains`, `forest`, `mountain`, `desert`, `ocean`, `tundra`, `swamp`).
- `x` / `coord_x` / `lon`: Horizontal canvas coordinate (default coordinate space: $1200 \times 800$).
- `y` / `coord_y` / `lat`: Vertical canvas coordinate.

If `x` and `y` are omitted, the engine deterministically generates consistent canvas coordinates derived from the note's name hash.

---

## 3. Location Type Glyphs

The vector map automatically renders distinctive Unicode glyphs and color-coded halo rings for each landmark type:

| Type | Glyph | Biome Color Hint | Description |
| :--- | :---: | :---: | :--- |
| `capital` | 👑 | `#2d3748` | Sovereign seat of power or royal palace. |
| `citadel` | 🏰 | `#4a5568` | Military fortress, bastion, or keep. |
| `city` | 🏛️ | `#2d3748` | Major metropolis or trading hub. |
| `port` | ⚓ | `#0c4a6e` | Harbor, coastal docks, or naval yard. |
| `village` | 🏡 | `#2d3748` | Rural settlement, hamlet, or farming town. |
| `ruins` | 🏛️ | `#78350f` | Ancient collapsed temple or forgotten ruins. |
| `dungeon` | ⚔️ | `#1b4332` | Subterranean vault, catacombs, or mine. |
| `mountain`| 🏔️ | `#4a5568` | Impassable mountain peak or range. |
| `forest` | 🌲 | `#1b4332` | Dense forest, jungle, or magical woods. |

---

## 4. Vector SVG Cartography Features

1. **Grid Overlays**:
   - `hex`: Hexagonal wargame grid overlay with calculated hexagonal polygon coordinates.
   - `square`: Cartesian coordinate grid lines every 50px.
2. **Automated Trade Routes**:
   - Automatically computes Euclidean proximity between adjacent nodes ($< 450\text{px}$).
   - Draws dashed amber route lines with distance (miles) and travel march time (days).
3. **Cartographic Decorations**:
   - Vintage double-ruled gold/slate parchment borders.
   - 4-point directional Compass Rose (North, South, East, West).
   - High-contrast title banner.
   - Proportional scale bar (150 Miles / 240 km).

---

## 5. Interactive HTML5 Map Viewer

The engine compiles an offline HTML5 viewer featuring:
- **Zero-Dependency Pan & Zoom**: Smooth mouse drag panning, scroll wheel zooming ($0.5\times$ to $4.0\times$), and responsive reset.
- **Lore Sidebar & Search**: Real-time search filter matching names, factions, and types.
- **Node Focus**: Clicking any location card smoothly centers and zooms the camera directly on the landmark.

---

## 6. Command-Line Interface (CLI)

```bash
# Generate vector SVG map for a world
arcanum map [WORLD] --svg world_map.svg --grid hex

# Compile an interactive HTML map viewer
arcanum map [WORLD] --html world_map.html

# Square grid without automatic trade routes
arcanum map [WORLD] --grid square --no-routes --html viewer.html
```

---

## 7. Security & Offline Guarantee

The generated HTML map enforces strict Content Security Policies:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```
All vector coordinates, scripts, and styles are self-contained without external asset downloads.
