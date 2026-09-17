#!/usr/bin/env python3
"""
Scriptorium Modern GTK 4 / Libadwaita Presentation Layer (scripts/lib/ui_adw.py)
Implements adaptive modern desktop views, system dark-mode synchronization,
and responsive controls for GNOME / modern Linux desktops.
"""

import sys
import subprocess
import threading
import logging
from pathlib import Path

logger = logging.getLogger("scriptorium.ui_adw")

HAS_ADW = False
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw, GLib
    HAS_ADW = True
except (ImportError, ValueError):
    HAS_ADW = False

HOME_DIR = Path.home()
UNIVERSES_DIR = HOME_DIR / "Universes"
MANUSCRIPTS_DIR = HOME_DIR / "Manuscripts"
WORLDS_DIR = HOME_DIR / "Worlds"
SCRIPT_DIR = Path(__file__).resolve().parent.parent


class ScriptoriumAppAdw:
    """Modern Libadwaita desktop application for Scriptorium."""

    def __init__(self, application=None):
        if not HAS_ADW:
            raise RuntimeError("Libadwaita / GTK 4 is not available.")

        self.app = application
        self.window = Adw.ApplicationWindow(application=self.app, title="Scriptorium Studio")
        self.window.set_default_size(1100, 760)

        self.current_universe = None
        self.current_world_path = None
        self.current_manuscript_path = None

        # Main Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.window.set_content(main_box)

        # Header Bar with View Switcher Title
        header = Adw.HeaderBar()
        self.view_stack = Adw.ViewStack()
        
        view_switcher_title = Adw.ViewSwitcherTitle()
        view_switcher_title.set_stack(self.view_stack)
        view_switcher_title.set_title("Scriptorium")
        view_switcher_title.set_subtitle("Author & Worldbuilder Studio")
        header.set_title_widget(view_switcher_title)

        # Snapshot quick button
        snap_btn = Gtk.Button(label="📷 Snapshot")
        snap_btn.add_css_class("suggested-action")
        snap_btn.connect("clicked", self._on_quick_snapshot)
        header.pack_end(snap_btn)

        main_box.append(header)

        # View Switcher Bar (for adaptive narrow screens)
        view_switcher_bar = Adw.ViewSwitcherBar()
        view_switcher_bar.set_stack(self.view_stack)

        # Pages in ViewStack
        self.page_cosmos = self._create_cosmos_page()
        self.page_drafting = self._create_drafting_page()
        self.page_publishing = self._create_publishing_page()
        self.page_safety = self._create_safety_page()
        self.page_diagnostics = self._create_diagnostics_page()

        self.view_stack.add_titled_with_icon(self.page_cosmos, "cosmos", "Universes", "folder-symbolic")
        self.view_stack.add_titled_with_icon(self.page_drafting, "drafting", "Drafting", "document-edit-symbolic")
        self.view_stack.add_titled_with_icon(self.page_publishing, "publishing", "Publishing", "applications-office-symbolic")
        self.view_stack.add_titled_with_icon(self.page_safety, "safety", "Safety & Git", "security-high-symbolic")
        self.view_stack.add_titled_with_icon(self.page_diagnostics, "diagnostics", "Doctor", "system-search-symbolic")

        main_box.append(self.view_stack)
        main_box.append(view_switcher_bar)

        # Status Bar / Toast Overlay
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(main_box)
        self.window.set_content(self.toast_overlay)

    def _show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _create_cosmos_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="World Lore Vaults", description="Manage Obsidian worldbuilding vaults and universes")
        
        row_new_univ = Adw.ActionRow(title="Create New Universe", subtitle="Scaffold an overarching cosmos container")
        btn_u = Gtk.Button(label="New Universe")
        btn_u.set_valign(Gtk.Align.CENTER)
        btn_u.connect("clicked", lambda x: self._run_script_dialog("init_universe.sh", "Universe Name:"))
        row_new_univ.add_suffix(btn_u)
        group.add(row_new_univ)

        row_new_world = Adw.ActionRow(title="Create New World Vault", subtitle="Scaffold an Obsidian Lore Bible with full plugin suite")
        btn_w = Gtk.Button(label="New World")
        btn_w.set_valign(Gtk.Align.CENTER)
        btn_w.connect("clicked", lambda x: self._run_script_dialog("init_world.sh", "World Name:"))
        row_new_world.add_suffix(btn_w)
        group.add(row_new_world)

        page.add(group)
        return page

    def _create_drafting_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="Manuscript Projects", description="Drafting workspaces with structured Acts and scene metadata")

        row_new_ms = Adw.ActionRow(title="Create New Manuscript", subtitle="Scaffold 3-Act novelWriter & Markdown workspace")
        btn_ms = Gtk.Button(label="New Manuscript")
        btn_ms.set_valign(Gtk.Align.CENTER)
        btn_ms.connect("clicked", lambda x: self._run_script_dialog("init_manuscript.sh", "Manuscript Name:"))
        row_new_ms.add_suffix(btn_ms)
        group.add(row_new_ms)

        row_add_vol = Adw.ActionRow(title="Add Book / Volume", subtitle="Add auto-incremented volume to existing manuscript")
        btn_vol = Gtk.Button(label="Add Volume")
        btn_vol.set_valign(Gtk.Align.CENTER)
        btn_vol.connect("clicked", lambda x: self._run_script_dialog("add_book.sh", "Target Manuscript:"))
        row_add_vol.add_suffix(btn_vol)
        group.add(row_add_vol)

        page.add(group)
        return page

    def _create_publishing_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="Typesetting & Book Compilation", description="Sub-second Typst & Pandoc publishing pipeline")

        row_export = Adw.ActionRow(title="Export Complete Manuscript", subtitle="Build trade PDF, standard submission DOCX, and EPUB")
        btn_exp = Gtk.Button(label="Build Exports")
        btn_exp.add_css_class("suggested-action")
        btn_exp.set_valign(Gtk.Align.CENTER)
        btn_exp.connect("clicked", self._on_export_clicked)
        row_export.add_suffix(btn_exp)
        group.add(row_export)

        page.add(group)
        return page

    def _create_safety_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="Multi-Tier Git & Disaster Recovery", description="Version milestones and standalone encrypted backups")

        row_snap = Adw.ActionRow(title="Record Version Snapshot", subtitle="Atomic multi-tier Git milestone with message")
        btn_snap = Gtk.Button(label="Save Snapshot")
        btn_snap.set_valign(Gtk.Align.CENTER)
        btn_snap.connect("clicked", self._on_quick_snapshot)
        row_snap.add_suffix(btn_snap)
        group.add(row_snap)

        row_bak = Adw.ActionRow(title="Create Backup Tarball", subtitle="Standalone SHA-256 archive of worlds and manuscripts")
        btn_bak = Gtk.Button(label="Backup Now")
        btn_bak.set_valign(Gtk.Align.CENTER)
        btn_bak.connect("clicked", lambda x: self._run_bg([str(SCRIPT_DIR / "backup_world.sh")], "Backup created successfully"))
        row_bak.add_suffix(btn_bak)
        group.add(row_bak)

        page.add(group)
        return page

    def _create_diagnostics_page(self) -> Gtk.Widget:
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(title="Narrative Diagnostics & Continuity", description="Timeline validation, concordance generation & semantic checks")

        row_doc = Adw.ActionRow(title="Run World Doctor", subtitle="Verify link integrity, YAML schemas, and chronology")
        btn_doc = Gtk.Button(label="Scan Lore")
        btn_doc.set_valign(Gtk.Align.CENTER)
        btn_doc.connect("clicked", lambda x: self._run_bg([str(SCRIPT_DIR / "world_doctor.sh"), "--fast"], "World Doctor scan complete"))
        row_doc.add_suffix(btn_doc)
        group.add(row_doc)

        row_con = Adw.ActionRow(title="Build Concordance", subtitle="Generate Dramatis Personae & Glossary back-matter")
        btn_con = Gtk.Button(label="Generate")
        btn_con.set_valign(Gtk.Align.CENTER)
        btn_con.connect("clicked", lambda x: self._run_bg([str(SCRIPT_DIR / "generate_concordance.sh")], "Concordance generated"))
        row_con.add_suffix(btn_con)
        group.add(row_con)

        row_cont = Adw.ActionRow(title="Check Semantic Continuity", subtitle="Flag character trait & narrative claim discrepancies")
        btn_cont = Gtk.Button(label="Check Continuity")
        btn_cont.set_valign(Gtk.Align.CENTER)
        btn_cont.connect("clicked", self._on_check_continuity)
        row_cont.add_suffix(btn_cont)
        group.add(row_cont)

        page.add(group)
        return page

    def _on_quick_snapshot(self, widget):
        self._run_bg([str(SCRIPT_DIR / "save_snapshot.sh"), "-m", "Quick Snapshot via Adw Studio"], "Snapshot saved successfully")

    def _on_export_clicked(self, widget):
        self._run_bg([str(SCRIPT_DIR / "export_book.sh")], "Export build completed")

    def _on_check_continuity(self, widget):
        cont_script = SCRIPT_DIR / "lib" / "continuity.py"
        if cont_script.is_file():
            self._run_bg([sys.executable, str(cont_script)], "Continuity scan completed")
        else:
            self._show_toast("Continuity engine module not found.")

    def _run_script_dialog(self, script_name: str, prompt: str):
        # Trigger background execution or CLI dialog
        cmd = str(SCRIPT_DIR / script_name)
        self._run_bg([cmd], f"Executed {script_name}")

    def _run_bg(self, cmd: list, success_msg: str):
        def worker():
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode in (0, 3):
                    GLib.idle_add(self._show_toast, success_msg)
                else:
                    err = res.stderr.strip().splitlines()[-1] if res.stderr else "Operation failed"
                    GLib.idle_add(self._show_toast, f"Notice: {err}")
            except Exception as e:
                logger.error("Error executing command %s: %s", cmd, e)
                GLib.idle_add(self._show_toast, f"Error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def present(self):
        self.window.present()


def run_adw_app():
    if not HAS_ADW:
        return False
    app = Adw.Application(application_id="org.scriptorium.Scriptorium")
    
    def on_activate(application):
        win = ScriptoriumAppAdw(application)
        win.present()

    app.connect("activate", on_activate)
    return app.run([])
