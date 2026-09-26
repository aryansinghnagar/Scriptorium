#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Speculative Fiction Studio (scripts/lib/ui_gtk3/studios/speculative.py)
========================================================================================
Provides Studio 3 tab interface housing the 18 craft, science, and worldbuilding modelers.
"""

from lib.ui_gtk3.common import Gtk


class SpeculativeStudioMixin:
    """Mixin providing Speculative Fiction & Craft Studio UI components and callbacks."""

    def create_speculative_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        tab_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        tab_box.set_border_width(14)

        # Header intro
        lbl_head = Gtk.Label(
            label="<b>🔮 Speculative Fiction & Editorial Craft Engine Matrix</b>\n"
                  "<span size='small' color='#666666'>100% offline, privacy-first domain calculation engines & prose linters for sci-fi, fantasy, and narrative craft.</span>",
            use_markup=True,
            xalign=0
        )
        tab_box.pack_start(lbl_head, False, False, 0)

        # Grid of Engine Cards
        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(12)
        grid.set_column_homogeneous(True)

        engines = [
            ("🚀 Astrophysics & Relativistic Flight", "Kinematics, time dilation, Hohmann orbits & lightspeed comms", self.open_astrophysics_dialog),
            ("⚡ Hard Magic System Constraints", "Arcane affinities, catalyst limits, fatigue & tier thresholds", self.open_magic_dialog),
            ("👑 Dynastic Lineage & Family DAG", "Succession conflicts, dynastic trees, Mermaid flowcharts & HTML DAGs", self.open_genealogy_dialog),
            ("🗣️ Conlang Phonotactics & Lexicon", "Syllable matrix, sound-law shift mutations & dictionary export", self.open_conlang_dialog),
            ("📈 Prose Mode Pacing & Tension", "Dialogue vs action density, tension curve & POV screen-time balance", self.open_pacing_dialog),
            ("🧭 Journey & Planetary Calendar", "Expedition terrain friction, multi-moon syzygy & orbital calendars", self.open_journey_calendar_dialog),
            ("⚔️ Faction Dynamics & War Logistics", "Lanchester power-laws, supply wagon radius & alliance paradoxes", self.open_factions_logistics_dialog),
            ("💰 In-World Economy & Tech Era", "Multi-currency PPP basket, price anomaly & tech anachronisms", self.open_economy_tech_dialog),
            ("⏳ Causal DAGs & Paradoxes", "Novikov self-consistency, grandfather paradoxes & timeline forks", self.open_causality_dialog),
            ("🌍 Climate & Bestiary Food-Web", "Insolation, orographic rain shadow & trophic energy pyramids", self.open_climate_ecology_dialog),
            ("🗣️ Prose Stylistics & Dialogue", "Said-bookisms, floating dialogue, echoes & attribution linter", self.open_stylistics_dialog),
            ("🎭 Character Voice Fingerprints", "Lexical diversity, readability grades & voice homogeneity checks", self.open_voice_dialog),
            ("✨ Smart Typography Normalizer", "Punctuation normalizer: curly quotes, em-dashes, ellipses", self.open_typography_dialog),
            ("🎬 Scene Mechanics & MRU Flow", "Goal-Conflict-Disaster & Motivation-Reaction Unit validation", self.open_scene_mechanics_dialog),
            ("📊 Multi-Track Plot Matrix", "Interactive 2D storyline grid mapping subplots across chapters", self.open_plot_matrix_dialog),
            ("📐 Story Paradigm Alignment", "Save the Cat, Hero's Journey, 3-Act structure pacing enforcer", self.open_structure_dialog),
            ("🎧 Focus Soundscapes & Noise", "Rainy library, cozy campfire, deep space drone synthesizer", self.open_ambient_dialog),
            ("🗺️ Multi-POV Narrative Subway Map", "Track character storyline splits and convergence points", self.open_branching_dialog),
            ("📖 Author Craft Guide & Advisory Matrix", "100% creative sovereignty documentation, worldbuilding logic & 3-path resolutions", self.open_craft_guide_dialog),
        ]

        for idx, (title, desc, cb) in enumerate(engines):
            col = idx % 3
            row = idx // 3
            card = self.create_engine_card(title, desc, cb)
            grid.attach(card, col, row, 1, 1)

        tab_box.pack_start(grid, True, True, 0)
        scrolled.add(tab_box)
        return scrolled

    def create_engine_card(self, title, desc, callback, btn_label="⚡ Launch Modeler"):
        frame = Gtk.Frame()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(10)

        lbl_t = Gtk.Label(label=f"<b>{title}</b>", use_markup=True, xalign=0)
        box.pack_start(lbl_t, False, False, 0)

        lbl_d = Gtk.Label(label=f"<small>{desc}</small>", use_markup=True, xalign=0)
        lbl_d.set_line_wrap(True)
        lbl_d.set_size_request(240, -1)
        box.pack_start(lbl_d, True, True, 0)

        btn = Gtk.Button(label=btn_label)
        btn.connect("clicked", lambda b: callback())
        box.pack_start(btn, False, False, 0)

        frame.add(box)
        return frame

    def on_magic_check_clicked(self, btn=None):
        self.open_magic_dialog()

    def on_genealogy_clicked(self, btn=None):
        self.open_genealogy_dialog()

    def on_conlang_clicked(self, btn=None):
        self.open_conlang_dialog()

    def on_calendar_clicked(self, btn=None):
        self.open_journey_calendar_dialog()

    def on_astrophysics_clicked(self, btn=None):
        self.open_astrophysics_dialog()

    def on_journey_clicked(self, btn=None):
        self.open_journey_calendar_dialog()

    def on_pacing_clicked(self, btn=None):
        self.open_pacing_dialog()

    def on_pov_clicked(self, btn=None):
        self.open_pacing_dialog()
