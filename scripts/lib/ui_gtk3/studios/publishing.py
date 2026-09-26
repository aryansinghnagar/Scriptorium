#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Publishing & Typesetting Studio (scripts/lib/ui_gtk3/studios/publishing.py)
============================================================================================
Provides Studio 4 tab interface for print PDF typesetting (Typst), EPUB (Pandoc/Calibre),
submission DOCX, pre-flight linting, and frontmatter scaffolding.
"""

import logging
import subprocess
import webbrowser
from pathlib import Path

from lib.ui_gtk3.common import (
    HAS_GTK,
    PROJECT_ROOT,
    GLib,
    Gtk,
)

logger = logging.getLogger("arcanum.ui_gtk3.studios.publishing")


class PublishingStudioMixin:
    """Mixin providing Publishing & Typesetting Studio UI components and callbacks."""

    def create_publishing_tab(self):
        tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        tab.set_border_width(12)

        # Left Column: Compilation & Export Presets
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_col.set_size_request(340, -1)

        # Compilation Engine Card
        compile_frame = Gtk.Frame(label=" 🖨️ Publication Compiler ")
        compile_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        compile_box.set_border_width(10)

        compile_box.pack_start(Gtk.Label(label="Export Target Format:", xalign=0), False, False, 0)
        self.combo_export_fmt = Gtk.ComboBoxText()
        self.combo_export_fmt.append("pdf", "Print PDF (Typst Musl Engine)")
        self.combo_export_fmt.append("epub", "Ebook EPUB (Pandoc / Calibre)")
        self.combo_export_fmt.append("docx", "Standard Submission DOCX")
        self.combo_export_fmt.append("all", "All Formats (PDF + EPUB + DOCX)")
        self.combo_export_fmt.set_active_id("pdf")
        compile_box.pack_start(self.combo_export_fmt, False, False, 0)

        btn_compile = Gtk.Button(label="🚀 Compile Publication")
        btn_compile.get_style_context().add_class("suggested-action")
        btn_compile.connect("clicked", self.on_compile_clicked)
        compile_box.pack_start(btn_compile, False, False, 0)

        compile_frame.add(compile_box)
        left_col.pack_start(compile_frame, False, False, 0)

        # Publishing Utilities Card
        pub_tools_frame = Gtk.Frame(label=" 🏷️ Publishing & Compliance Utilities ")
        pub_tools_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        pub_tools_box.set_border_width(10)

        btn_preflight = Gtk.Button(label="🔍 Pre-Flight Typesetting Linter")
        btn_preflight.connect("clicked", lambda b: self.open_preflight_dialog())
        pub_tools_box.pack_start(btn_preflight, False, False, 0)

        btn_corpus = Gtk.Button(label="📦 Universal Structured Corpus Exporter")
        btn_corpus.connect("clicked", lambda b: self.open_corpus_dialog())
        pub_tools_box.pack_start(btn_corpus, False, False, 0)

        btn_fm = Gtk.Button(label="📚 Modular Front & Back Matter Builder")
        btn_fm.connect("clicked", lambda b: self.open_frontmatter_dialog())
        pub_tools_box.pack_start(btn_fm, False, False, 0)

        btn_query = Gtk.Button(label="📝 Query Letter & Agent Tracker")
        btn_query.connect("clicked", lambda b: self.open_query_dialog())
        pub_tools_box.pack_start(btn_query, False, False, 0)

        btn_pkg = Gtk.Button(label="📦 Multi-Platform Release Packager")
        btn_pkg.connect("clicked", lambda b: self.open_package_dialog())
        pub_tools_box.pack_start(btn_pkg, False, False, 0)

        btn_port = Gtk.Button(label="🌐 Executive Portfolio Dashboard")
        btn_port.connect("clicked", lambda b: self.open_portfolio_dialog())
        pub_tools_box.pack_start(btn_port, False, False, 0)

        pub_tools_frame.add(pub_tools_box)
        left_col.pack_start(pub_tools_frame, False, False, 0)

        tab.pack_start(left_col, False, False, 0)

        # Right Column: Compilation Output Log & Open Viewers
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        viewers_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_view_pdf = Gtk.Button(label="📖 Open PDF")
        btn_view_pdf.connect("clicked", self.on_open_pdf_clicked)
        viewers_bar.pack_start(btn_view_pdf, True, True, 0)

        btn_view_epub = Gtk.Button(label="📱 Open EPUB")
        btn_view_epub.connect("clicked", self.on_open_epub_clicked)
        viewers_bar.pack_start(btn_view_epub, True, True, 0)

        btn_view_docx = Gtk.Button(label="📄 Open DOCX")
        btn_view_docx.connect("clicked", self.on_open_docx_clicked)
        viewers_bar.pack_start(btn_view_docx, True, True, 0)

        right_col.pack_start(viewers_bar, False, False, 0)

        lbl_log = Gtk.Label(label="<b>Compiler Terminal Output:</b>", use_markup=True, xalign=0)
        right_col.pack_start(lbl_log, False, False, 0)

        scrolled, self.compile_log_buf = self._create_dialog_output_view()
        right_col.pack_start(scrolled, True, True, 0)

        tab.pack_start(right_col, True, True, 0)
        return tab

    def on_compile_clicked(self, btn):
        if not self.current_manuscript_path:
            self.show_error("No active manuscript selected.")
            return

        fmt = self.combo_export_fmt.get_active_id() or "pdf"
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        draft = self.combo_draft_list.get_active_id() if self.combo_draft_list else "Draft-01"

        import sys
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "lib" / "cli.py"),
            "export",
            self.current_manuscript_path,
            "--format", fmt,
            "--book", vol,
            "--draft", draft
        ]

        self.compile_log_buf.set_text(f"Compiling {Path(self.current_manuscript_path).name} ({fmt.upper()})...\n\n")
        self.set_status(f"Compiling publication {fmt.upper()}...")

        def _worker():
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300
            )
            out_str = res.stdout if res.returncode == 0 else f"Compilation Error (exit code {res.returncode}):\n{res.stderr}\n{res.stdout}"
            if HAS_GTK and GLib is not None:
                GLib.idle_add(lambda: self.compile_log_buf.set_text(out_str))
                GLib.idle_add(lambda: self._on_compile_done(res.returncode))

        self._start_worker(_worker)

    def _on_compile_done(self, returncode):
        if returncode == 0:
            self.set_status("Publication compiled successfully!")
        else:
            self.set_status("Compilation failed. Check log for details.")

    def on_open_pdf_clicked(self, btn):
        if not self.current_manuscript_path:
            return
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        ms_name = Path(self.current_manuscript_path).name
        pdf_path = Path(self.current_manuscript_path) / "04-Publishing" / "Print-PDF" / f"{ms_name}_{vol}.pdf"
        if pdf_path.exists():
            webbrowser.open(f"file://{pdf_path}")
        else:
            self.set_status(f"PDF not found at {pdf_path.name}. Compile it first.")

    def on_open_epub_clicked(self, btn):
        if not self.current_manuscript_path:
            return
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        ms_name = Path(self.current_manuscript_path).name
        epub_path = Path(self.current_manuscript_path) / "04-Publishing" / "Ebook" / f"{ms_name}_{vol}.epub"
        if epub_path.exists():
            webbrowser.open(f"file://{epub_path}")
        else:
            self.set_status(f"EPUB not found at {epub_path.name}. Compile it first.")

    def on_open_docx_clicked(self, btn):
        if not self.current_manuscript_path:
            return
        vol = self.combo_draft_vol.get_active_id() if self.combo_draft_vol else "Book-01"
        draft = self.combo_draft_list.get_active_id() if self.combo_draft_list else "Draft-01"
        docx_path = Path(self.current_manuscript_path) / vol / draft / f"{draft}_Manuscript.docx"
        if docx_path.exists():
            webbrowser.open(f"file://{docx_path}")
        else:
            self.set_status("DOCX manuscript not found. Sync or compile it first.")

    def _append_log(self, buffer_obj, text):
        if buffer_obj:
            buffer_obj.insert(buffer_obj.get_end_iter(), text)
