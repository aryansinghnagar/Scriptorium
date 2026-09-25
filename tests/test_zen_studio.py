#!/usr/bin/env python3
"""
Test Suite: Standalone Offline Zen Drafting Studio
(tests/test_zen_studio.py)
================================================================================
Validates manuscript and lore scanning, single-file HTML5 bundle creation,
Content Security Policy compliance, in-situ lore drawer, word count calculation,
theme styling, and telemetry export methods.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.lib.zen_studio import (
    build_zen_studio_bundle,
    scan_lore_entities,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestZenStudio(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Mock World Lore
        self.world_dir = self.root / "Eldoria-Prime"
        self.chars_dir = self.world_dir / "Characters"
        self.locs_dir = self.world_dir / "Locations"
        self.chars_dir.mkdir(parents=True)
        self.locs_dir.mkdir(parents=True)

        (self.chars_dir / "Aeloria.md").write_text(
            """---
name: "Aeloria Vael"
type: "character"
---
# Aeloria Vael
Master of the crystal greatsword.
""",
            encoding="utf-8",
        )

        (self.locs_dir / "Sanctuary.md").write_text(
            """---
name: "High Sanctuary"
type: "location"
---
# High Sanctuary
The floating citadel.
""",
            encoding="utf-8",
        )

        # Mock Manuscript
        self.ms_dir = self.root / "Book-01" / "Draft-01"
        self.ms_dir.mkdir(parents=True)
        (self.ms_dir / "01_Ch1.md").write_text(
            """---
title: "The Fractured Spire"
chapter: 1
---
# The Fractured Spire

Dawn broke over the high parapets.
""",
            encoding="utf-8",
        )
        (self.ms_dir / "02_Ch2.md").write_text(
            """---
title: "Shadows in the Deep"
chapter: 2
---
# Shadows in the Deep

A cold mist rolled across the valley floor.
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Lore Entity Scanning                                            #
    # ------------------------------------------------------------------ #
    def test_scan_lore_entities(self):
        """scan_lore_entities must discover characters and locations with correct metadata."""
        entities = scan_lore_entities(self.world_dir)
        self.assertEqual(len(entities), 2)
        names = {e["name"] for e in entities}
        self.assertIn("Aeloria Vael", names)
        self.assertIn("High Sanctuary", names)

    # ------------------------------------------------------------------ #
    # 2. Multi-Chapter Bundle Verification                               #
    # ------------------------------------------------------------------ #
    def test_multi_chapter_bundle_content(self):
        """build_zen_studio_bundle must embed all chapters in the manuscript."""
        out_html = self.root / "zen_multi.html"
        bundle_path = build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")
        self.assertIn("The Fractured Spire", content)
        self.assertIn("Shadows in the Deep", content)

    # ------------------------------------------------------------------ #
    # 3. HTML Bundle Creation & Invariants                               #
    # ------------------------------------------------------------------ #
    def test_build_zen_studio_bundle(self):
        """build_zen_studio_bundle must write a valid HTML file with core components."""
        out_html = self.root / "zen_studio.html"
        bundle_path = build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)

        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")

        # Security & Invariants
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("Ars Arcanum — Sovereign Zen Drafting Studio", content)

        # Core Components
        self.assertIn("zen-editor", content)
        self.assertIn("lore-drawer", content)
        self.assertIn("The Fractured Spire", content)
        self.assertIn("Aeloria Vael", content)
        self.assertIn("exportMarkdown", content)
        self.assertIn("updateTelemetry", content)

    # ------------------------------------------------------------------ #
    # 4. Strict Content Security Policy                                  #
    # ------------------------------------------------------------------ #
    def test_zen_studio_csp_compliance(self):
        """Zen studio HTML must declare default-src 'none' and offline privacy isolation."""
        out_html = self.root / "zen_csp.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("default-src 'none'", content)
        self.assertIn("style-src 'unsafe-inline'", content)
        self.assertIn("script-src 'unsafe-inline'", content)

    # ------------------------------------------------------------------ #
    # 5. Zen Editor Textarea Workspace                                   #
    # ------------------------------------------------------------------ #
    def test_zen_studio_editor_area(self):
        """Bundle must include textarea.zen-editor with Georgia/serif styling."""
        out_html = self.root / "zen_editor.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("zen-editor", content)
        self.assertIn("editor-area", content)

    # ------------------------------------------------------------------ #
    # 6. Theme CSS Variables                                             #
    # ------------------------------------------------------------------ #
    def test_zen_studio_css_variables(self):
        """Bundle must define CSS root variables for themes and high contrast."""
        out_html = self.root / "zen_themes.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("--bg:", content)
        self.assertIn("--text:", content)
        self.assertIn("--accent:", content)

    # ------------------------------------------------------------------ #
    # 7. Lore Drawer Search and Entity Filtering                         #
    # ------------------------------------------------------------------ #
    def test_zen_studio_lore_search_filter(self):
        """Bundle JavaScript must include filterLore / query filtering logic."""
        out_html = self.root / "zen_lore_filter.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("loreQuery", content)
        self.assertIn("filterLore", content)
        self.assertIn("lore-drawer", content)

    # ------------------------------------------------------------------ #
    # 8. Word Count and Reading Time Telemetry                           #
    # ------------------------------------------------------------------ #
    def test_zen_studio_telemetry_elements(self):
        """Bundle must include telWords, telChars, and telReadTime telemetry spans."""
        out_html = self.root / "zen_telemetry.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("telWords", content)
        self.assertIn("telChars", content)
        self.assertIn("telReadTime", content)

    # ------------------------------------------------------------------ #
    # 9. Sidebar Chapter Navigation Controls                             #
    # ------------------------------------------------------------------ #
    def test_zen_studio_sidebar_navigation(self):
        """Bundle must include chapter sidebar list and toggleSidebar function."""
        out_html = self.root / "zen_sidebar.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("sidebar", content)
        self.assertIn("chapList", content)
        self.assertIn("toggleSidebar", content)

    # ------------------------------------------------------------------ #
    # 10. Standalone Studio Without World Lore                           #
    # ------------------------------------------------------------------ #
    def test_build_zen_studio_without_world(self):
        """build_zen_studio_bundle must function cleanly when world_path is None."""
        out_html = self.root / "zen_no_world.html"
        bundle_path = build_zen_studio_bundle(self.ms_dir, world_path=None, output_path=out_html)
        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")
        self.assertIn("The Fractured Spire", content)

    # ------------------------------------------------------------------ #
    # 11. Empty Manuscript Default Initialization                        #
    # ------------------------------------------------------------------ #
    def test_build_zen_studio_empty_manuscript(self):
        """Empty manuscript directory should compile clean empty studio HTML."""
        empty_ms = self.root / "Empty_Manuscript"
        empty_ms.mkdir()
        out_html = self.root / "zen_empty.html"
        bundle_path = build_zen_studio_bundle(empty_ms, world_path=None, output_path=out_html)
        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")
        self.assertIn("Ars Arcanum Zen Studio", content)

    # ------------------------------------------------------------------ #
    # 12. LocalStorage Persistence Logic                                 #
    # ------------------------------------------------------------------ #
    def test_zen_studio_localstorage_persistence(self):
        """Bundle must reference localStorage for draft auto-save recovery."""
        out_html = self.root / "zen_storage.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("localStorage", content)


if __name__ == "__main__":
    unittest.main()
