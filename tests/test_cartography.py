#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Offline Vector Cartography Engine (scripts/lib/cartography.py).
Validates:
- WOR-101: World location parsing from Locations/*.md notes.
- Vector SVG map generation with hex/square grid and routes.
- Interactive HTML map viewer generation.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cartography import (
    parse_world_locations,
    get_default_locations,
    generate_vector_svg_map,
    generate_cartography_html_viewer,
    TYPE_ICONS,
)


class TestCartographyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name)
        (self.world_dir / "Locations").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_locations_from_markdown(self):
        loc1 = self.world_dir / "Locations" / "Sun_Citadel.md"
        loc1.write_text("""---
name: "Sun Citadel"
type: "capital"
faction: "Solar Hegemony"
x: 400
y: 300
biome: "plains"
---
The golden capital of the realm.
""", encoding="utf-8")

        locations = parse_world_locations(self.world_dir)
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]["name"], "Sun Citadel")
        self.assertEqual(locations[0]["type"], "capital")
        self.assertEqual(locations[0]["x"], 400.0)
        self.assertEqual(locations[0]["y"], 300.0)

    def test_parse_locations_fallback_default(self):
        empty_dir = Path(self.temp_dir.name) / "EmptyCosmos"
        locations = parse_world_locations(empty_dir)
        self.assertGreaterEqual(len(locations), 3)
        names = [loc["name"] for loc in locations]
        self.assertIn("Sun Citadel", names)

    def test_parse_locations_deterministic_pseudo_coords(self):
        loc1 = self.world_dir / "Locations" / "Hidden_Sanctuary.md"
        loc1.write_text("""---
name: "Hidden Sanctuary"
type: "citadel"
---
An isolated shrine hidden deep in the hills.
""", encoding="utf-8")
        locations = parse_world_locations(self.world_dir)
        self.assertEqual(len(locations), 1)
        self.assertIsNotNone(locations[0]["x"])
        self.assertIsNotNone(locations[0]["y"])
        self.assertGreater(locations[0]["x"], 0)
        self.assertGreater(locations[0]["y"], 0)

    def test_generate_vector_svg_map_hex_grid(self):
        locations = [
            {"id": "A", "name": "Citadel Alpha", "type": "citadel", "faction": "Alliance", "biome": "plains", "x": 200, "y": 200, "description": "Fortress"},
            {"id": "B", "name": "Port Beta", "type": "port", "faction": "Alliance", "biome": "ocean", "x": 500, "y": 300, "description": "Harbor"}
        ]
        svg = generate_vector_svg_map(locations, title="Test Realm", grid_mode="hex", show_routes=True)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("<polygon", svg)  # Hexagon polygons
        self.assertIn("Citadel Alpha", svg)
        self.assertIn("Port Beta", svg)
        self.assertIn("Test Realm", svg)

    def test_generate_vector_svg_map_square_grid(self):
        locations = [
            {"id": "A", "name": "Fort Alpha", "type": "citadel", "faction": "Alliance", "biome": "plains", "x": 100, "y": 100, "description": "Fort"}
        ]
        svg = generate_vector_svg_map(locations, title="Square Grid Realm", grid_mode="square", show_routes=False)
        self.assertIn("<line", svg)
        self.assertIn("Square Grid Realm", svg)

    def test_generate_vector_svg_map_no_routes(self):
        locations = [
            {"id": "A", "name": "Node A", "type": "village", "faction": "None", "biome": "plains", "x": 100, "y": 100, "description": "A"},
            {"id": "B", "name": "Node B", "type": "village", "faction": "None", "biome": "plains", "x": 200, "y": 200, "description": "B"},
        ]
        svg = generate_vector_svg_map(locations, title="No Routes", show_routes=False)
        self.assertNotIn("stroke-dasharray", svg)

    def test_generate_vector_svg_routes_and_milestones(self):
        locations = [
            {"id": "A", "name": "City One", "type": "city", "faction": "Guild", "biome": "plains", "x": 200, "y": 200, "description": "City 1"},
            {"id": "B", "name": "City Two", "type": "city", "faction": "Guild", "biome": "plains", "x": 350, "y": 250, "description": "City 2"},
        ]
        svg = generate_vector_svg_map(locations, title="Routes Realm", show_routes=True)
        self.assertIn("stroke-dasharray=\"6,4\"", svg)
        self.assertIn("mi (", svg)

    def test_generate_vector_svg_compass_rose_and_title(self):
        locations = get_default_locations()
        svg = generate_vector_svg_map(locations, title="Imperial Cosmos")
        self.assertIn("<text y=\"-33\"", svg)  # North compass rose
        self.assertIn("Imperial Cosmos", svg)
        self.assertIn("Ars Arcanum Vector Cartography", svg)

    def test_generate_html_cartography_viewer_csp(self):
        locations = [{"id": "A", "name": "Citadel Alpha", "type": "citadel", "faction": "Alliance", "biome": "plains", "x": 200, "y": 200, "description": "Fortress"}]
        out_html = self.world_dir / "realm_map.html"
        generate_cartography_html_viewer(locations, "Test Realm", out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("Test Realm Map Viewer", content)

    def test_generate_html_cartography_viewer_json_payload(self):
        locations = [{"id": "Loc1", "name": "Crystal Spires", "type": "capital", "faction": "Mages", "biome": "tundra", "x": 300, "y": 400, "description": "Spires"}]
        out_html = self.world_dir / "payload_map.html"
        generate_cartography_html_viewer(locations, "Payload Cosmos", out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Crystal Spires", content)
        self.assertIn("const locations =", content)

    def test_generate_html_cartography_viewer_editor_ui(self):
        locations = [{"id": "Loc1", "name": "Crystal Spires", "type": "capital", "faction": "Mages", "biome": "tundra", "x": 300, "y": 400, "description": "Spires"}]
        out_html = self.world_dir / "editor_ui.html"
        generate_cartography_html_viewer(locations, "Editor UI", out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("btn-pan", content)
        self.assertIn("btn-landmass", content)
        self.assertIn("btn-poi", content)
        self.assertIn("btn-route", content)
        self.assertIn("btn-boundary", content)
        self.assertIn("exportSVG()", content)

    def test_location_type_icons(self):
        self.assertEqual(TYPE_ICONS["capital"], "👑")
        self.assertEqual(TYPE_ICONS["citadel"], "🏰")
        self.assertEqual(TYPE_ICONS["port"], "⚓")
        self.assertEqual(TYPE_ICONS["mountain"], "🏔️")
        self.assertEqual(TYPE_ICONS["forest"], "🌲")

    def test_cartography_cli_html(self):
        out_html = self.world_dir / "cli_map.html"
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "lib" / "cartography.py"), str(self.world_dir), "--html", str(out_html)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(out_html.is_file())


if __name__ == "__main__":
    unittest.main()
