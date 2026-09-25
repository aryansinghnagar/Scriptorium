#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Authorial Ecosystem Interface & Studio Launchers
(tests/test_ecosystem_ui.py)
=============================================================================
Validates:
1. Desktop Launchers (*.desktop) syntax, TryExec, Categories, and Exec paths.
2. CLI and App launcher argument parsing (--tab, --check-ui, --gtk3, --adw).
3. GTK 3 & Libadwaita Studio tab index and navigation mappings.
4. Speculative Dialog definitions & callback integrity.
5. Offline standard library / PyGObject compliance (no external pip dependencies).
"""

import sys
import os
import shutil
import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
LAUNCHERS_DIR = REPO_ROOT / "launchers"


def find_bash():
    """Finds working bash executable on Windows or POSIX."""
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        shutil.which("bash"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return "bash"


BASH_EXE = find_bash()


class TestDesktopLaunchers(unittest.TestCase):
    """Tests for desktop launcher files in launchers/."""

    REQUIRED_LAUNCHERS = [
        "arcanum-control-center.desktop",
        "arcanum-worldbuilding.desktop",
        "arcanum-drafting.desktop",
        "arcanum-publishing.desktop",
        "arcanum-comparator.desktop",
        "arcanum-doctor.desktop",
    ]

    def test_all_required_launchers_exist(self):
        for launcher in self.REQUIRED_LAUNCHERS:
            path = LAUNCHERS_DIR / launcher
            self.assertTrue(path.is_file(), f"Missing required desktop launcher: {launcher}")

    def test_launchers_have_tryexec_bash(self):
        for desktop_file in LAUNCHERS_DIR.glob("*.desktop"):
            content = desktop_file.read_text(encoding="utf-8")
            self.assertIn("TryExec=bash", content, f"{desktop_file.name} missing 'TryExec=bash'")

    def test_launchers_categories_standardized(self):
        for desktop_file in LAUNCHERS_DIR.glob("*.desktop"):
            content = desktop_file.read_text(encoding="utf-8")
            self.assertIn(
                "Categories=Office;WordProcessor;Publishing;",
                content,
                f"{desktop_file.name} must have standard Categories=Office;WordProcessor;Publishing;"
            )

    def test_launchers_header_and_type(self):
        for desktop_file in LAUNCHERS_DIR.glob("*.desktop"):
            content = desktop_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("[Desktop Entry]"), f"{desktop_file.name} must start with [Desktop Entry]")
            self.assertIn("Type=Application", content, f"{desktop_file.name} must specify Type=Application")
            self.assertIn("Exec=", content, f"{desktop_file.name} must specify Exec=")
            self.assertIn("Name=", content, f"{desktop_file.name} must specify Name=")
            self.assertIn("Icon=", content, f"{desktop_file.name} must specify Icon=")


class TestArcanumAppCli(unittest.TestCase):
    """Tests for arcanum_app.py CLI options and argument handling."""

    def test_check_ui_output(self):
        cmd = [sys.executable, str(SCRIPTS_DIR / "arcanum_app.py"), "--check-ui"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Libadwaita / GTK 4:", res.stdout)
        self.assertIn("GTK 3 (PyGObject):", res.stdout)

    def test_tab_argument_validation(self):
        # Valid tab keywords should be accepted by argument parser
        valid_tabs = [
            "cosmos", "world", "drafting", "manuscript", "worldbuilding",
            "speculative", "publishing", "typesetting", "safety", "backups",
            "doctor", "diagnostics", "comparator", "redline"
        ]
        for tab in valid_tabs:
            cmd = [sys.executable, str(SCRIPTS_DIR / "arcanum_app.py"), "--tab", tab, "--help"]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(res.returncode, 0)

    def test_invalid_tab_argument_fails(self):
        cmd = [sys.executable, str(SCRIPTS_DIR / "arcanum_app.py"), "--tab", "nonexistent_studio_xyz"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("invalid choice", res.stderr)


class TestUiTabMapping(unittest.TestCase):
    """Tests for studio tab index mappings and method definitions."""

    def test_gtk3_app_tab_dispatch_methods(self):
        # Verify all speculative and craft dialog methods exist on ArcanumApp
        sys.path.insert(0, str(SCRIPTS_DIR))
        from lib.ui_gtk3 import ArcanumApp

        expected_dialog_methods = [
            "open_astrophysics_dialog",
            "open_magic_dialog",
            "open_genealogy_dialog",
            "open_conlang_dialog",
            "open_pacing_dialog",
            "open_journey_calendar_dialog",
            "open_factions_logistics_dialog",
            "open_economy_tech_dialog",
            "open_causality_dialog",
            "open_climate_ecology_dialog",
            "open_idioms_senses_dialog",
            "open_cipher_prophecy_dialog",
            "open_stylistics_dialog",
            "open_voice_dialog",
            "open_typography_dialog",
            "open_scene_mechanics_dialog",
            "open_plot_matrix_dialog",
            "open_structure_dialog",
            "open_ambient_dialog",
            "open_preflight_dialog",
            "open_barcode_dialog",
            "open_frontmatter_dialog",
            "open_query_dialog",
            "open_cartography_dialog",
            "open_codex_dialog",
            "open_series_continuity_dialog",
            "open_tactical_sim_dialog",
            "open_package_dialog",
            "open_portfolio_dialog",
            "open_tts_dialog",
        ]
        for method in expected_dialog_methods:
            self.assertTrue(hasattr(ArcanumApp, method), f"Missing dialog method {method} on ArcanumApp")

    def test_gtk3_all_6_studios_created(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        from lib.ui_gtk3 import ArcanumApp

        studio_creators = [
            "create_cosmos_tab",
            "create_manuscript_tab",
            "create_speculative_tab",
            "create_publishing_tab",
            "create_safety_tab",
            "create_doctor_tab",
        ]
        for creator in studio_creators:
            self.assertTrue(hasattr(ArcanumApp, creator), f"Missing tab creator {creator} on ArcanumApp")

    def test_adw_all_6_studios_defined(self):
        ui_adw_path = SCRIPTS_DIR / "lib" / "ui_adw.py"
        content = ui_adw_path.read_text(encoding="utf-8")

        adw_pages = [
            "_create_cosmos_page",
            "_create_drafting_page",
            "_create_speculative_page",
            "_create_publishing_page",
            "_create_safety_page",
            "_create_diagnostics_page",
        ]
        for page in adw_pages:
            self.assertIn(f"def {page}(", content, f"Missing Adw page creator {page} in ui_adw.py")


class TestArcanumCliFacade(unittest.TestCase):
    """Tests for unified arcanum CLI behavior."""

    def test_cli_zero_args_noninteractive_outputs_usage(self):
        cmd = [BASH_EXE, str(SCRIPTS_DIR / "arcanum")]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Ars Arcanum Unified CLI", res.stdout)
        self.assertIn("Usage:", res.stdout)

    def test_cli_help_mentions_menu_and_gui(self):
        cmd = [BASH_EXE, str(SCRIPTS_DIR / "arcanum"), "--help"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        self.assertIn("gui", res.stdout)
        self.assertIn("menu", res.stdout)

    def test_cli_calc_trade_execution(self):
        cmd = [
            BASH_EXE, str(SCRIPTS_DIR / "arcanum"), "calc", "trade",
            "--buy", "100", "--sell", "200", "--cargo", "10",
            "--distance", "50", "--json"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        self.assertIn('"is_profitable": true', res.stdout)
        self.assertIn('"gross_revenue":', res.stdout)

    def test_cli_words_md_flag(self):
        # Verify arcanum words --md works without errors
        cmd = [BASH_EXE, str(SCRIPTS_DIR / "arcanum"), "words", str(REPO_ROOT / "templates" / "manuscript"), "--md"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        self.assertIn("| Volume | Act | Chapter | Words | Status |", res.stdout)

    def test_all_12_speculative_subcommands_route(self):
        subcmds = [
            ["calc", "transit", "--help"],
            ["calc", "time-dilation", "--help"],
            ["calc", "orbit", "--help"],
            ["calc", "comms", "--help"],
            ["calc", "journey", "--help"],
            ["calc", "battle", "--help"],
            ["calc", "logistics", "--help"],
            ["calc", "climate", "--help"],
            ["calc", "trade", "--help"],
            ["magic-check", "--help"],
            ["genealogy", "tree", "--help"],
            ["genealogy", "lineage", "--help"],
            ["conlang", "generate", "--help"],
            ["pace", "--help"],
            ["tension", "--help"],
            ["calendar", "--help"],
            ["faction", "check", "--help"],
            ["economy", "check", "--help"],
            ["causality", "check", "--help"],
            ["climate", "--help"],
            ["ecology", "check", "--help"],
            ["audit", "idioms", "--help"],
            ["audit", "senses", "--help"],
            ["audit", "tech", "--help"],
            ["audit", "dialogue", "--help"],
            ["audit", "echoes", "--help"],
            ["audit", "voice", "--help"],
            ["audit", "scenes", "--help"],
            ["audit", "structure", "--help"],
            ["polish", "typography", "--help"],
            ["preflight", "--help"],
            ["barcode", "--help"],
            ["matter", "build", "--help"],
            ["query", "--help"],
            ["read", "--help"],
            ["tts", "--help"],
            ["plot", "--help"],
            ["structure", "--help"],
            ["ambient", "--help"],
            ["portfolio", "--help"],
            ["package", "--help"],
            ["map", "--help"],
            ["codex", "--help"],
            ["series", "--help"],
            ["sim", "battle", "--help"],
            ["cipher", "encode", "--help"],
            ["prophecy", "check", "--help"],
        ]
        for sub in subcmds:
            cmd = [BASH_EXE, str(SCRIPTS_DIR / "arcanum"), *sub]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(res.returncode, 0, f"Failed routing arcanum {' '.join(sub)}: {res.stderr}")


class TestSpeculativeDialogArgumentIntegrity(unittest.TestCase):
    """Verifies that all 12 speculative dialog command constructions match target CLI parsers."""

    def test_dialog_commands_contain_no_invalid_flags(self):
        ui_gtk3_dir = SCRIPTS_DIR / "lib" / "ui_gtk3"
        contents = [p.read_text(encoding="utf-8") for p in ui_gtk3_dir.glob("**/*.py")]
        contents.append((SCRIPTS_DIR / "lib" / "ui_gtk3.py").read_text(encoding="utf-8"))
        combined = "\n".join(contents)

        # Verify no invalid options in ui_gtk3 package dialogs
        self.assertNotIn("--window", combined, "ui_gtk3 should not pass unsupported --window to pacing.py")
        self.assertNotIn("--depth", combined, "ui_gtk3 should not pass unsupported --depth to genealogy.py")
        self.assertNotIn('"factions.py"), "audit"', combined, "factions.py should use 'check' or 'matrix', not 'audit'")
        self.assertNotIn('--orbit', combined, "climate.py should use --distance-au, not --orbit")


if __name__ == "__main__":
    unittest.main()
