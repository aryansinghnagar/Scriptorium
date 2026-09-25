#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Sovereign Studio Desktop Hub
(tests/test_studio_hub.py)
================================================================================
Validates data aggregation, static HTML dashboard compilation, CSP compliance,
REST/JSON API request handlers, and CLI invocation.
"""

import http.client
import json
import socketserver
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any

from scripts.lib.studio_hub import (
    HUB_VERSION,
    SovereignStudioHandler,
    analyze_structure_harmony,
    collect_studio_hub_data,
    export_static_studio_hub,
    extract_timeline_summary,
    generate_studio_hub_html,
    get_engine_catalog,
    main as studio_hub_main,
    scan_lore_entities,
    scan_manuscript_chapters,
)


class TestStudioHubEngine(unittest.TestCase):
    """Tests data scanning, telemetry metrics, and static HTML generation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create sample World directory
        self.world_dir = self.root / "World"
        self.world_dir.mkdir(parents=True, exist_ok=True)
        (self.world_dir / "world.yaml").write_text("name: Eldoria\n", encoding="utf-8")

        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True, exist_ok=True)
        (chars_dir / "Kaelen.md").write_text(
            "---\nname: Kaelen\ntags: [protagonist, mage]\naliases: [The Silver Blade]\n---\n"
            "# Kaelen\nA solitary spellblade wandering the shattered valleys.\n",
            encoding="utf-8",
        )

        magic_dir = self.world_dir / "Magic"
        magic_dir.mkdir(parents=True, exist_ok=True)
        (magic_dir / "RuneCasting.md").write_text(
            "---\nname: Rune Casting\ntags: [hard_magic, glyphs]\n---\n"
            "# Rune Casting\nMagic requires physical inscription into conductive silver.\n",
            encoding="utf-8",
        )

        # Create sample Manuscript directory
        self.ms_dir = self.root / "Manuscript"
        self.ms_dir.mkdir(parents=True, exist_ok=True)
        (self.ms_dir / "manuscript.yaml").write_text("title: The Silver Vale\n", encoding="utf-8")

        ch1_text = (
            "---\ntitle: The Awakening\npov: Kaelen\nstatus: Draft\nchrono_date: '1042-04-12'\ntime: Morning\n---\n"
            "# Chapter 1: The Awakening\n\n"
            "The dawn broke over the jagged spires of the Silver Vale. Kaelen drew his blade.\n"
            "@choice: [Investigate the rune vault] -> vault\n"
            "@choice: [Flee into the mist] -> mist\n"
        )
        (self.ms_dir / "01_Chapter_01.md").write_text(ch1_text, encoding="utf-8")

        ch2_text = (
            "---\ntitle: The Shattered Glyph\npov: Kaelen\nstatus: Revised\nchrono_date: '1042-04-12'\ntime: Noon\n---\n"
            "# Chapter 2: The Shattered Glyph\n\n"
            "Inside the vault, obsidian shards hummed with forbidden energy.\n"
            "@state: energy += 10\n"
        )
        (self.ms_dir / "02_Chapter_02.md").write_text(ch2_text, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_engine_catalog(self):
        catalog = get_engine_catalog()
        self.assertTrue(len(catalog) >= 10)
        engine_ids = [e["id"] for e in catalog]
        self.assertIn("zen_studio", engine_ids)
        self.assertIn("editorial_council", engine_ids)
        self.assertIn("local_rag", engine_ids)
        self.assertIn("branching_graph", engine_ids)
        self.assertIn("fine_tuning", engine_ids)

    def test_scan_manuscript_chapters(self):
        chapters = scan_manuscript_chapters(self.ms_dir)
        self.assertEqual(len(chapters), 2)
        ch1 = chapters[0]
        self.assertEqual(ch1["title"], "The Awakening")
        self.assertEqual(ch1["pov"], "Kaelen")
        self.assertEqual(ch1["choices_count"], 2)
        self.assertTrue(ch1["words"] > 0)

        ch2 = chapters[1]
        self.assertEqual(ch2["title"], "The Shattered Glyph")
        self.assertEqual(ch2["states_count"], 1)

    def test_scan_lore_entities(self):
        entities = scan_lore_entities(self.world_dir)
        self.assertEqual(len(entities), 2)
        names = [e["name"] for e in entities]
        self.assertIn("Kaelen", names)
        self.assertIn("Rune Casting", names)

        kaelen = next(e for e in entities if e["name"] == "Kaelen")
        self.assertEqual(kaelen["category"], "Characters")
        self.assertIn("protagonist", kaelen["tags"])

    def test_analyze_structure_harmony(self):
        chapters = scan_manuscript_chapters(self.ms_dir)
        harmony = analyze_structure_harmony(chapters)
        self.assertEqual(harmony["total_chapters"], 2)
        self.assertTrue(harmony["total_words"] > 0)
        self.assertEqual(len(harmony["pacing_curve"]), 2)
        self.assertEqual(harmony["pacing_curve"][-1]["percentage"], 100.0)

    def test_extract_timeline_summary_and_paradox(self):
        events = extract_timeline_summary(self.world_dir, self.ms_dir)
        self.assertEqual(len(events), 2)
        # In our setup, ch1 and ch2 have same actor Kaelen and same chrono_date '1042-04-12'
        # which triggers the bilocation paradox check
        self.assertTrue(any(e["paradox"] for e in events))

    def test_collect_studio_hub_data(self):
        data = collect_studio_hub_data(self.root)
        self.assertEqual(data["version"], HUB_VERSION)
        self.assertEqual(data["metrics"]["total_chapters"], 2)
        self.assertEqual(data["metrics"]["total_lore_entities"], 2)
        self.assertIn("Characters", data["metrics"]["lore_breakdown"])
        self.assertIn("Magic Systems", data["metrics"]["lore_breakdown"])

    def test_generate_studio_hub_html_and_csp(self):
        data = collect_studio_hub_data(self.root)
        html = generate_studio_hub_html(data, api_mode=False)

        # Check Content Security Policy declaration
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("default-src 'none'", html)
        self.assertIn("connect-src 'self'", html)

        # Check UI components
        self.assertIn("Ars Arcanum", html)
        self.assertIn("Sovereign Studio Hub", html)
        self.assertIn("The Awakening", html)
        self.assertIn("Kaelen", html)
        self.assertIn("Rune Casting", html)

    def test_export_static_studio_hub(self):
        out_file = self.root / "studio_hub.html"
        res = export_static_studio_hub(out_file, self.root)
        self.assertEqual(res, out_file)
        self.assertTrue(out_file.exists())
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("Overview Dashboard", content)

    def test_cli_json_and_static_export(self):
        static_target = self.root / "cli_dashboard.html"
        code = studio_hub_main([str(self.root), "--export-static", str(static_target)])
        self.assertEqual(code, 0)
        self.assertTrue(static_target.exists())

        code_json = studio_hub_main([str(self.root), "--json"])
        self.assertEqual(code_json, 0)


class TestStudioHubServerAPI(unittest.TestCase):
    """Tests the embedded HTTP server and REST endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp_dir.name)

        world_dir = cls.root / "World"
        world_dir.mkdir(parents=True, exist_ok=True)
        (world_dir / "world.yaml").write_text("name: TestCosmos\n", encoding="utf-8")
        (world_dir / "Hero.md").write_text("---\nname: Hero\ntags: [fighter]\n---\n# Hero\n", encoding="utf-8")

        ms_dir = cls.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "manuscript.yaml").write_text("title: TestStory\n", encoding="utf-8")
        (ms_dir / "01_Ch1.md").write_text("---\ntitle: Ch1\n---\n# Ch1\nStory text.\n", encoding="utf-8")

        cls.data = collect_studio_hub_data(cls.root)
        SovereignStudioHandler.data = cls.data
        SovereignStudioHandler.project_dir = cls.root

        socketserver.TCPServer.allow_reuse_address = True
        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), SovereignStudioHandler)
        cls.port = cls.httpd.server_address[1]

        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.temp_dir.cleanup()

    def _get(self, path: str) -> tuple[int, dict[str, str], bytes]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", path)
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        data = resp.read()
        conn.close()
        return resp.status, headers, data

    def _post_json(self, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, str], dict[str, Any]]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps(payload).encode("utf-8")
        conn.request("POST", path, body, {"Content-Type": "application/json", "Content-Length": str(len(body))})
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        data = json.loads(resp.read().decode("utf-8"))
        conn.close()
        return resp.status, headers, data

    def test_get_index_html(self):
        status, headers, data = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn(b"Ars Arcanum", data)

    def test_get_api_status(self):
        status, _, data = self._get("/api/status")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertIn("offline_sovereignty", json_data)

    def test_get_api_lore_and_chapters(self):
        status, _, data = self._get("/api/lore")
        self.assertEqual(status, 200)
        lore = json.loads(data.decode("utf-8"))
        self.assertTrue(len(lore) >= 1)

        status, _, data = self._get("/api/chapters")
        self.assertEqual(status, 200)
        chapters = json.loads(data.decode("utf-8"))
        self.assertTrue(len(chapters) >= 1)

    def test_post_api_query(self):
        status, _, res = self._post_json("/api/query", {"query": "Hero"})
        self.assertEqual(status, 200)
        self.assertEqual(res["query"], "Hero")
        self.assertTrue(res["total_matches"] >= 1)

    def test_post_api_council(self):
        status, _, res = self._post_json("/api/council", {"text": "The dark blade severed the arcane connection."})
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "success")
        self.assertIn("line_editor", res["critique"])


if __name__ == "__main__":
    unittest.main()
