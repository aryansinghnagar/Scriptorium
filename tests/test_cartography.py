#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Offline Vector Cartography Engine (scripts/lib/cartography.py).
Validates:
- WOR-101: World location parsing from Locations/*.md notes.
- Vector SVG map generation with hex/square grid and routes.
- Interactive HTML map viewer generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cartography import (
    parse_world_locations,
    generate_vector_svg_map,
    generate_cartography_html_viewer
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

    def test_generate_vector_svg_map(self):
        locations = [
            {"id": "A", "name": "Citadel Alpha", "type": "citadel", "faction": "Alliance", "biome": "plains", "x": 200, "y": 200, "description": "Fortress"},
            {"id": "B", "name": "Port Beta", "type": "port", "faction": "Alliance", "biome": "ocean", "x": 500, "y": 300, "description": "Harbor"}
        ]
        svg = generate_vector_svg_map(locations, title="Test Realm", grid_mode="hex", show_routes=True)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("Citadel Alpha", svg)
        self.assertIn("Port Beta", svg)
        self.assertIn("Test Realm", svg)

    def test_generate_html_cartography_viewer(self):
        locations = [{"id": "A", "name": "Citadel Alpha", "type": "citadel", "faction": "Alliance", "biome": "plains", "x": 200, "y": 200, "description": "Fortress"}]
        out_html = self.world_dir / "realm_map.html"
        generate_cartography_html_viewer(locations, "Test Realm", out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Test Realm Map Viewer", out_html.read_text(encoding="utf-8"))

    def test_cartography_cli_html(self):
        import subprocess
        out_html = self.world_dir / "cli_map.html"
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "lib" / "cartography.py"), str(self.world_dir), "--html", str(out_html)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(out_html.is_file())


if __name__ == "__main__":
    unittest.main()
