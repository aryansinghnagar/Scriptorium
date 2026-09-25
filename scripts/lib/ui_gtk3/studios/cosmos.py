#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Cosmos & Worlds Studio (scripts/lib/ui_gtk3/studios/cosmos.py)
==============================================================================
Provides Studio 1 tab interface for managing Universes, Obsidian World Lore Vaults,
and starter demo universes.
"""

import logging
import subprocess
from pathlib import Path

from lib.ui_gtk3.cli_bridge import launch_external_app
from lib.ui_gtk3.common import (
    HAS_GTK,
    PROJECT_ROOT,
    UNIVERSES_DIR,
    WORLDS_DIR,
    GLib,
    Gtk,
)

logger = logging.getLogger("arcanum.ui_gtk3.studios.cosmos")


class CosmosStudioMixin:
    """Mixin providing Cosmos & Worlds Studio UI components and callbacks."""

    def create_cosmos_tab(self):
        tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        tab.set_border_width(12)

        # Left Column: Universe & World Lore Controls
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_col.set_size_request(320, -1)

        # Universe Scaffolding Card
        uni_frame = Gtk.Frame(label=" 🪐 Narrative Universe ")
        uni_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        uni_box.set_border_width(10)

        btn_new_uni = Gtk.Button(label="➕ Create New Universe")
        btn_new_uni.connect("clicked", self.on_new_universe_clicked)
        uni_box.pack_start(btn_new_uni, False, False, 0)
        uni_frame.add(uni_box)
        left_col.pack_start(uni_frame, False, False, 0)

        # World Scaffolding Card
        world_frame = Gtk.Frame(label=" 🗺️ World Lore Vaults ")
        world_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        world_box.set_border_width(10)

        btn_new_world = Gtk.Button(label="➕ Scaffold World Bible Vault")
        btn_new_world.connect("clicked", self.on_new_world_clicked)
        world_box.pack_start(btn_new_world, False, False, 0)

        btn_open_obsidian = Gtk.Button(label="🔮 Open World in Obsidian")
        btn_open_obsidian.get_style_context().add_class("suggested-action")
        btn_open_obsidian.connect("clicked", self.on_launch_obsidian)
        world_box.pack_start(btn_open_obsidian, False, False, 0)

        btn_open_folder = Gtk.Button(label="📂 Browse Lore Vault Directory")
        btn_open_folder.connect("clicked", self.on_open_world_folder_clicked)
        world_box.pack_start(btn_open_folder, False, False, 0)

        world_frame.add(world_box)
        left_col.pack_start(world_frame, False, False, 0)

        # Demo Cosmos Starter
        demo_frame = Gtk.Frame(label=" 🚀 Starter Demo Universe ")
        demo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        demo_box.set_border_width(10)
        btn_demo = Gtk.Button(label="✨ Generate Eldoria Demo Cosmos")
        btn_demo.connect("clicked", self.on_generate_demo_clicked)
        demo_box.pack_start(btn_demo, False, False, 0)
        demo_frame.add(demo_box)
        left_col.pack_start(demo_frame, False, False, 0)

        tab.pack_start(left_col, False, False, 0)

        # Right Column: Lore Stats & Structure Overview
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.card_chars = self.create_stat_card("Dossiers & Cast", "0", "Characters & Factions")
        self.card_locs = self.create_stat_card("World Atlas", "0", "Locations & Settlements")
        self.card_magic = self.create_stat_card("Arcane & Tech", "0", "Magic Systems & Rules")
        self.card_history = self.create_stat_card("Chronicles", "0", "Timeline Events")

        stats_grid = Gtk.Grid()
        stats_grid.set_column_spacing(10)
        stats_grid.set_row_spacing(10)
        stats_grid.attach(self.card_chars, 0, 0, 1, 1)
        stats_grid.attach(self.card_locs, 1, 0, 1, 1)
        stats_grid.attach(self.card_magic, 0, 1, 1, 1)
        stats_grid.attach(self.card_history, 1, 1, 1, 1)

        right_col.pack_start(stats_grid, False, False, 0)

        # World Lore Summary / Note View
        lbl_vault_info = Gtk.Label(label="<b>World Lore Vault Summary:</b>", use_markup=True, xalign=0)
        right_col.pack_start(lbl_vault_info, False, False, 0)

        scrolled, self.lore_summary_buf = self._create_dialog_output_view()
        right_col.pack_start(scrolled, True, True, 0)

        tab.pack_start(right_col, True, True, 0)
        return tab

    def on_new_universe_clicked(self, btn):
        dialog = Gtk.Dialog(title="Create New Narrative Universe", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Create Universe", Gtk.ResponseType.OK)
        dialog.set_default_size(440, 200)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        box.pack_start(Gtk.Label(label="Universe Name (e.g. Cosmere, Solar-Imperium):", xalign=0), False, False, 0)
        entry = Gtk.Entry()
        entry.set_text("New-Cosmos")
        box.pack_start(entry, False, False, 0)

        dialog.show_all()
        res = dialog.run()
        uni_name = entry.get_text().strip()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and uni_name:
            def _worker():
                cmd = [PROJECT_ROOT / "scripts" / "init_universe.sh", "--name", uni_name]
                subprocess.run(["bash", str(cmd)], capture_output=True, text=True)
                if HAS_GTK and GLib is not None:
                    GLib.idle_add(self.refresh_all_discovery)
            self._start_worker(_worker)

    def on_new_world_clicked(self, btn):
        dialog = Gtk.Dialog(title="Scaffold World Bible Vault", parent=self, flags=0)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Create World", Gtk.ResponseType.OK)
        dialog.set_default_size(460, 240)
        box = dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        box.pack_start(Gtk.Label(label="World Name (e.g. Roshar, Arrakis):", xalign=0), False, False, 0)
        entry_name = Gtk.Entry()
        entry_name.set_text("New-World")
        box.pack_start(entry_name, False, False, 0)

        box.pack_start(Gtk.Label(label="Universe:", xalign=0), False, False, 0)
        combo_uni = Gtk.ComboBoxText()
        for u in self.discovered_universes:
            combo_uni.append(u, u)
        if self.current_universe:
            combo_uni.set_active_id(self.current_universe)
        box.pack_start(combo_uni, False, False, 0)

        dialog.show_all()
        res = dialog.run()
        world_name = entry_name.get_text().strip()
        u_name = combo_uni.get_active_id() or self.current_universe or "Default-Universe"
        dialog.destroy()

        if res == Gtk.ResponseType.OK and world_name:
            def _worker():
                cmd = [str(PROJECT_ROOT / "scripts" / "init_world.sh"), "--name", world_name, "--universe", u_name]
                subprocess.run(["bash", cmd], capture_output=True, text=True)
                if HAS_GTK and GLib is not None:
                    GLib.idle_add(self.refresh_all_discovery)
            self._start_worker(_worker)

    def on_launch_obsidian(self, btn):
        if self.current_world_path:
            launch_external_app("obsidian", self.current_world_path)
            self.set_status(f"Opening {Path(self.current_world_path).name} in Obsidian...")
        else:
            self.show_error("No active World Lore Vault selected.")

    def on_open_world_folder_clicked(self, btn):
        target = self.current_world_path or str(WORLDS_DIR if WORLDS_DIR.exists() else UNIVERSES_DIR)
        try:
            import webbrowser
            webbrowser.open(f"file://{target}")
        except Exception as e:
            self.set_status(f"Could not open folder: {e}")

    def on_generate_demo_clicked(self, btn):
        demo_src = PROJECT_ROOT / "templates" / "demo-cosmos" / "Eldoria-Cosmos"
        if not demo_src.is_dir():
            self.show_error("Demo cosmos template not found.")
            return

        dest = UNIVERSES_DIR / "Eldoria-Cosmos"
        if dest.exists():
            self.set_status("Eldoria-Cosmos already exists in ~/Universes.")
            self.refresh_all_discovery()
            return

        def _worker():
            import shutil
            try:
                shutil.copytree(demo_src, dest)
                # Copy manuscript to ~/Manuscripts if present
                ms_src = demo_src / "Manuscripts" / "The-Silver-Chronicles"
                ms_dest = Path.home() / "Manuscripts" / "The-Silver-Chronicles"
                if ms_src.is_dir() and not ms_dest.exists():
                    ms_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(ms_src, ms_dest)
            except Exception as e:
                logger.warning("Error copying demo cosmos: %s", e)

            if HAS_GTK and GLib is not None:
                GLib.idle_add(self.refresh_all_discovery)
                GLib.idle_add(lambda: self.set_status("Eldoria Demo Cosmos generated successfully!"))

        self._start_worker(_worker)
