#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Diagnostics & Doctor Studio (scripts/lib/ui_gtk3/studios/diagnostics.py)
========================================================================================
Provides Studio 6 tab interface for toolchain status badges, unified system health diagnostics,
and canonical 7-stage test harness verification.
"""

import logging
import subprocess
import sys

from lib.ui_gtk3.common import (
    HAS_GTK,
    PROJECT_ROOT,
    GLib,
    Gtk,
    _cached_which,
    _flush_tool_cache,
)

logger = logging.getLogger("arcanum.ui_gtk3.studios.diagnostics")


class DiagnosticsStudioMixin:
    """Mixin providing Diagnostics & System Health Studio UI components and callbacks."""

    def create_doctor_tab(self):
        tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        tab.set_border_width(12)

        # Left Column: Toolchain Badges & Diagnostic Triggers
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_col.set_size_request(340, -1)

        # External Toolchain Checklist
        tools_frame = Gtk.Frame(label=" 🧰 External Toolchain Status ")
        tools_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        tools_box.set_border_width(10)

        self.lbl_tool_git = self.create_badge_item("Git Version Control", "Checking...")
        self.lbl_tool_pandoc = self.create_badge_item("Pandoc AST Converter", "Checking...")
        self.lbl_tool_typst = self.create_badge_item("Typst Musl Compiler", "Checking...")
        self.lbl_tool_python = self.create_badge_item("Python 3 & Standard Lib", "Checking...")

        tools_box.pack_start(self.lbl_tool_git, False, False, 0)
        tools_box.pack_start(self.lbl_tool_pandoc, False, False, 0)
        tools_box.pack_start(self.lbl_tool_typst, False, False, 0)
        tools_box.pack_start(self.lbl_tool_python, False, False, 0)

        tools_frame.add(tools_box)
        left_col.pack_start(tools_frame, False, False, 0)

        # Diagnostic Actions
        action_frame = Gtk.Frame(label=" 🩺 System Health & Doctor ")
        action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        action_box.set_border_width(10)

        btn_doc = Gtk.Button(label="🩺 Run Unified Health Doctor")
        btn_doc.get_style_context().add_class("suggested-action")
        btn_doc.connect("clicked", lambda b: self.run_diagnostics())
        action_box.pack_start(btn_doc, False, False, 0)

        btn_verify = Gtk.Button(label="🧪 Run 7-Stage Test Harness")
        btn_verify.connect("clicked", lambda b: self.run_verify_harness())
        action_box.pack_start(btn_verify, False, False, 0)

        action_frame.add(action_box)
        left_col.pack_start(action_frame, False, False, 0)

        tab.pack_start(left_col, False, False, 0)

        # Right Column: Diagnostic Output Log
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        lbl_out = Gtk.Label(label="<b>Diagnostic Analysis & Doctor Report:</b>", use_markup=True, xalign=0)
        right_col.pack_start(lbl_out, False, False, 0)

        scrolled, self.doctor_log_buf = self._create_dialog_output_view()
        right_col.pack_start(scrolled, True, True, 0)

        tab.pack_start(right_col, True, True, 0)
        return tab

    def create_badge_item(self, name, status):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_name = Gtk.Label(label=f"<b>{name}:</b>", use_markup=True, xalign=0)
        lbl_status = Gtk.Label(label=status, xalign=1)
        box.pack_start(lbl_name, True, True, 0)
        box.pack_start(lbl_status, False, False, 0)
        box.status_label = lbl_status
        return box

    def update_toolchain_badges(self):
        tools = [
            ("git", self.lbl_tool_git),
            ("pandoc", self.lbl_tool_pandoc),
            ("typst", self.lbl_tool_typst),
            ("python3", self.lbl_tool_python),
        ]
        for cmd, badge in tools:
            path = _cached_which(cmd)
            if path:
                badge.status_label.set_markup("<span color='#2e7d32'><b>✓ Installed</b></span>")
            else:
                badge.status_label.set_markup("<span color='#d32f2f'><b>✗ Missing</b></span>")

    def run_diagnostics(self):
        _flush_tool_cache()
        self.update_toolchain_badges()
        self.doctor_log_buf.set_text("Running Ars Arcanum unified health diagnostics...\n\n")
        self.set_status("Running health diagnostics...")

        cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "lib" / "diagnostics.py")]

        def _worker():
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if HAS_GTK and GLib is not None:
                out = res.stdout if res.returncode == 0 else f"Diagnostics Error:\n{res.stderr}\n{res.stdout}"
                GLib.idle_add(lambda: self.doctor_log_buf.set_text(out))
                GLib.idle_add(lambda: self.set_status("Diagnostics completed."))

        self._start_worker(_worker)

    def run_verify_harness(self):
        self.doctor_log_buf.set_text("Executing canonical 7-stage verification harness...\n\n")
        self.set_status("Running verification harness...")

        cmd = [str(PROJECT_ROOT / "scripts" / "verify.sh")]

        def _worker():
            res = subprocess.run(["bash", *cmd], capture_output=True, text=True, timeout=600)
            if HAS_GTK and GLib is not None:
                out = res.stdout if res.returncode == 0 else f"Verification Failed:\n{res.stderr}\n{res.stdout}"
                GLib.idle_add(lambda: self.doctor_log_buf.set_text(out))
                GLib.idle_add(lambda: self.set_status("Verification run complete."))

        self._start_worker(_worker)
