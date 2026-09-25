# Ars Arcanum — Sovereign Studio Desktop Hub Guide

> `arcanum hub` · **v3.0.0 — The Sovereign Zenith Release** · 100% Offline · Zero-pip

---

## Overview

The **Sovereign Studio Desktop Hub** is a unified telemetry cockpit for your entire Ars Arcanum writing project. It aggregates real-time data from all 40+ craft engines — chapters, lore entities, timeline events, paradox alerts, and structural pacing harmony — into a single responsive offline HTML5 dashboard accessible from your browser.

The hub runs as an embedded local HTTP server using Python's standard library `http.server`, requires no external pip packages, and generates fully self-contained CSP-compliant HTML that never makes external network requests.

---

## Quick Start

```bash
# Open the Studio Hub for a Cosmos project directory
arcanum hub /path/to/My-Cosmos

# Use the current directory as project root
arcanum hub

# Custom port
arcanum hub /path/to/My-Cosmos --port 8765

# Export a single-file static HTML snapshot (no server)
arcanum hub /path/to/My-Cosmos --export-static ./hub-snapshot.html

# Print hub data as JSON (headless / CI mode)
arcanum hub /path/to/My-Cosmos --json

# Start the server without opening a browser
arcanum hub /path/to/My-Cosmos --no-browser
```

---

## CLI Reference

```
arcanum hub [TARGET] [OPTIONS]
arcanum dashboard [...]
arcanum gui-web [...]
arcanum studio-hub [...]

Arguments:
  TARGET                 Project directory (Cosmos root). Defaults to current directory.

Options:
  --port PORT            Port to bind the local HTTP server (default: 8749).
  --host HOST            Hostname to bind (default: 127.0.0.1).
  --no-browser           Start the server but do not open the system browser.
  --export-static FILE   Export a self-contained offline HTML snapshot and exit.
  --json                 Print hub telemetry data as JSON and exit (no server).
  -h, --help             Show this help message.
```

---

## Dashboard Panels

### 📖 Chapter Word-Count Telemetry
Live per-chapter word count bars showing total manuscript progress. Scans all `*.md` files recursively under any `Draft-*/` folder structure.

### 🏛️ Lore Entity Inventory
Entity counts by category (Characters, Factions, Places, Magic, Bestiary, Technology, Religions, Languages) parsed from sub-directory names in your World Bible.

### 🕰️ Timeline & Paradox Alerts
Event count and any detected bilocation paradoxes from `@time:` directives across all chapter scenes. Paradoxes are highlighted in amber as action items.

### 📐 Structural Pacing Harmony
Bar chart showing chapter word counts as a pacing curve overlay on a three-act structure model. Helps visualize tension rises and act breaks visually.

---

## REST API

The embedded local server exposes a lightweight REST API for programmatic integration:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Full interactive HTML dashboard |
| `GET` | `/api/hub` | Complete JSON telemetry bundle |
| `GET` | `/api/chapters` | Chapter list with word counts |
| `GET` | `/api/lore` | Lore entity category summary |
| `GET` | `/api/timeline` | Timeline events and paradox summary |
| `POST` | `/api/refresh` | Re-scan project directory and return fresh data |

### Example API call

```bash
curl http://127.0.0.1:8749/api/hub | python3 -m json.tool
```

---

## Static Export

The `--export-static` mode generates a single self-contained offline HTML file with all data baked into embedded JavaScript. This file can be shared, archived, or opened offline without a running server:

```bash
arcanum hub /path/to/My-Cosmos --export-static ./project-status.html
```

The exported HTML declares a strict Content Security Policy:
```
default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;
```
No external CDN scripts, remote fonts, or network requests are ever made.

---

## JSON / Headless Mode

The `--json` flag is designed for CI pipelines, shell scripting, and integration with external monitoring tools:

```bash
arcanum hub /path/to/My-Cosmos --json
```

Output structure:
```json
{
  "project_name": "Aethelgard",
  "total_chapters": 12,
  "total_words": 84210,
  "lore_entities": {"Characters": 8, "Places": 5, "Magic": 3},
  "timeline_events": 24,
  "paradox_count": 0,
  "pacing_harmony": 0.87,
  "generated_at": "2026-09-21T21:00:00"
}
```

---

## Engine Registration

The Studio Hub is registered in `scripts/lib/registry.py` as `"studio_hub"`:

```python
"studio_hub": EngineSpec(
    name="studio_hub",
    module="scripts.lib.studio_hub",
    commands=["hub", "dashboard", "gui-web", "studio-hub"],
    description="Sovereign Studio Desktop Hub & Telemetry Cockpit",
)
```

---

## Architecture Notes

- **Zero external dependencies**: Uses only `http.server`, `threading`, `json`, `pathlib`, `datetime`, and `socket` from the Python standard library.
- **Atomic project scan**: All filesystem reads complete before the first browser response; no concurrent filesystem mutations.
- **CSP-compliant HTML**: All generated HTML passes strict offline Content Security Policy with no inline `<script src>` or `<link rel=stylesheet href>` external references.
- **Thread safety**: `SovereignStudioHandler.data` and `SovereignStudioHandler.project_dir` are class-level attributes set before the server thread starts; `/api/refresh` re-scans synchronously and atomically replaces the class attribute.

---

## Architectural Decision Records

- **ADR-063**: Sovereign Studio Hub & Unified Offline Local Webview Architecture — see [`decisions.md`](../decisions.md).
