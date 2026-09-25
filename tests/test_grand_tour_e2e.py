"""
Master Grand Tour End-to-End Lifecycle Verification Harness
(tests/test_grand_tour_e2e.py)
================================================================================
Comprehensive 21-stage end-to-end integration test validating the entire
creative authoring and worldbuilding lifecycle of Ars Arcanum:

Stage 1:  Cosmos Universe & Manuscript Scaffolding
Stage 2:  Cosmos Lore Bible Population (Characters, Locations, Magic, Factions)
Stage 3:  Multi-Chapter Manuscript Drafting with Scene Tags & Branching Choices
Stage 4:  World Doctor Health Diagnostic Audit
Stage 5:  Dual-Track Timeline Synchronization & Paradox Detection
Stage 6:  Autonomous Multi-Perspective Editorial Council Critique
Stage 7:  Local Semantic Retrieval (RAG) Indexing & Lore Query
Stage 8:  Local AI Fine-Tuning Dataset Synthesis (Alpaca, ShareGPT, Modelfile)
Stage 9:  Interactive Branching Narrative DAG Compilation (HTML, Ink, Twine)
Stage 10: Universal Corpus Exporter (JSONL, SQLite FTS5, Markdown Digest)
Stage 11: Multi-Volume Series Omnibus & EPUB 3 Media Overlays
Stage 12: Release Distribution Packaging & ZIP Bundles
Stage 13: Sovereign Studio Desktop Hub Static Telemetry Compilation
Stage 14: Sovereign Writing Sprint & Session Velocity Analytics
Stage 15: Causal DAG Novikov Self-Consistency & Revision Density Heatmap
Stage 16: Cosmos Archive Freeze & Multi-Volume Dramatis Personae Synthesis
Stage 17: Sovereign Worldbuilding Codex & Arcane Mastery Verification
Stage 18: Story Craft, Prose Mechanics & Narrative Architecture Verification
Stage 19: Worldbuilding Sciences & Narrative Mechanics Expansion
Stage 20: Authoring Studios, Publishing Toolchains & Creative Scaffolding Expansion
Stage 21: Local Intelligence, Editorial Intelligence & Narrative Distribution Architecture

100% Offline — Zero Cloud Telemetry — Grade A+ Sovereign Authoring OS.
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from package_distribution import (
    package_arc_bundle,
    package_codex_bundle,
    package_reader_edition,
    package_submission_bundle,
)
from scripts.lib.ambient import generate_ambient_html_synthesizer, synthesize_wav
from scripts.lib.archive_freeze import (
    export_freeze_bundle,
    scan_and_freeze_vault,
    verify_vault_freeze,
)
from scripts.lib.barcode import export_barcode, validate_and_normalize_isbn
from scripts.lib.branching_graph import BranchingNarrativeEngine
from scripts.lib.calendar import (
    get_moon_phase,
    load_calendar_spec,
)
from scripts.lib.cartography import (
    generate_cartography_html_viewer,
    generate_vector_svg_map,
    parse_world_locations,
)
from scripts.lib.causality import audit_causality, extract_causal_nodes, generate_causality_html_report
from scripts.lib.climate import (
    calc_atmospheric_circulation,
    calc_orographic_rain_shadow,
    calc_planetary_insolation,
    generate_climate_html_report,
)
from scripts.lib.cipher import (
    cipher_vigenere,
    generate_rune_svg,
    text_to_runes,
)
from scripts.lib.codex_export import (
    build_single_file_codex,
    scan_world_vault,
)
from scripts.lib.concordance import generate_concordance
from scripts.lib.conlang import (
    generate_words,
    mutate_text,
)
from scripts.lib.corpus_export import (
    CorpusScanner,
    export_jsonl,
    export_markdown_summary,
    export_sqlite,
)
from scripts.lib.dramatis_personae import (
    cross_reference_manuscripts,
    generate_dramatis_personae_html,
    generate_dramatis_personae_markdown,
    scan_character_profiles,
)
from scripts.lib.ecology import (
    audit_ecosystem,
    extract_species_profiles,
    generate_ecology_html_report,
    generate_ecology_mermaid,
)
from scripts.lib.economy import (
    audit_technological_anachronisms,
    calc_trade_margin,
    extract_economy_profiles,
)
from scripts.lib.editorial_council import conduct_editorial_council, generate_council_html_dashboard
from scripts.lib.factions import (
    audit_faction_diplomacy,
    calc_campaign_logistics,
    calc_lanchester_battle,
    extract_faction_profiles,
)
from scripts.lib.fine_tuning import DatasetSynthesizer, export_fine_tuning_dataset
from scripts.lib.genealogy import (
    generate_mermaid_flowchart,
    load_characters_and_houses,
    validate_genealogy,
)
from scripts.lib.idioms import audit_manuscript_idioms, generate_idioms_html_report
from scripts.lib.journey import calculate_journey, generate_journey_html_report
from scripts.lib.local_rag import LocalLoreRetrievalEngine, generate_html_retrieval_viewer
from scripts.lib.magic_system import (
    generate_magic_html_report,
    run_magic_audit,
)
from scripts.lib.tts_reader import clean_prose_for_speech, generate_tts_html_player
from scripts.lib.media_overlay import (
    build_chapter_overlay,
    generate_smil_xml,
    generate_synchronized_player_html,
)
from scripts.lib.omnibus import compile_omnibus_manuscript, discover_series_volumes
from scripts.lib.pacing import generate_pacing_html_report, scan_manuscript_pacing
from scripts.lib.plot_matrix import generate_plot_html_report, scan_manuscript_plot_matrix
from scripts.lib.portfolio import generate_portfolio_html, scan_portfolio
from scripts.lib.revision_heatmap import (
    analyze_revision_churn,
    generate_revision_heatmap_html,
    scan_manuscript_snapshots,
)
from scripts.lib.scene_mechanics import generate_scene_mechanics_html, scan_manuscript_scenes
from scripts.lib.story_canvas import extract_scene_cards, generate_story_canvas_html
from scripts.lib.structure import generate_structure_html_report, scan_manuscript_structure
from scripts.lib.studio_hub import collect_studio_hub_data, export_static_studio_hub
from scripts.lib.stylistics import generate_stylistics_html_report, scan_text_or_path
from scripts.lib.tactical_sim import (
    DEFAULT_SIDE1,
    DEFAULT_SIDE2,
    run_monte_carlo,
    simulate_single_battle,
)
from scripts.lib.timeline_sync import (
    analyze_timeline_synchronization,
    extract_timeline_events,
    generate_timeline_html_report,
)
from scripts.lib.typography_cleaner import clean_target, normalize_typography_text
from scripts.lib.voice import generate_voice_html_report, scan_manuscript_voices
from scripts.lib.world_doctor import check_world
from scripts.lib.writing_sprint import (
    compute_daily_streak,
    compute_velocity_stats,
    end_sprint,
    generate_sprint_report_html,
    load_sessions,
    start_sprint,
)
from scripts.lib.zen_studio import generate_zen_studio_bundle


class TestGrandTourE2E(unittest.TestCase):
    """Executes the complete 20-stage Grand Tour authoring lifecycle."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_complete_grand_tour_lifecycle(self):
        # ---------------------------------------------------------------------
        # STAGE 1: Cosmos Universe & Manuscript Scaffolding
        # ---------------------------------------------------------------------
        cosmos_dir = self.root / "Aethelgard-Cosmos"
        cosmos_dir.mkdir(parents=True, exist_ok=True)
        (cosmos_dir / "universe.yaml").write_text(
            "name: Aethelgard Cosmos\nversion: '3.0.0'\nauthor: Master Loreweaver\n",
            encoding="utf-8",
        )

        world_dir = cosmos_dir / "Aethelgard-Prime"
        world_dir.mkdir(parents=True, exist_ok=True)
        (world_dir / "world.yaml").write_text(
            "name: Aethelgard Prime\nsetting_type: Hard Fantasy / Arcane Cybernetics\n",
            encoding="utf-8",
        )

        book_dir = cosmos_dir / "Manuscripts" / "Book-01-The-Obsidian-Crown"
        book_dir.mkdir(parents=True, exist_ok=True)
        (book_dir / "manuscript.yaml").write_text(
            "title: The Obsidian Crown\nvolume: 1\nseries: The Sunder Chronicle\nauthor: Master Loreweaver\n",
            encoding="utf-8",
        )

        ms_dir = book_dir / "Draft-01"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "manuscript.yaml").write_text(
            "title: The Obsidian Crown\nvolume: 1\nseries: The Sunder Chronicle\nauthor: Master Loreweaver\n",
            encoding="utf-8",
        )

        self.assertTrue((cosmos_dir / "universe.yaml").exists())
        self.assertTrue((world_dir / "world.yaml").exists())
        self.assertTrue((ms_dir / "manuscript.yaml").exists())

        # ---------------------------------------------------------------------
        # STAGE 2: Cosmos Lore Bible Population
        # ---------------------------------------------------------------------
        chars_dir = world_dir / "Characters"
        chars_dir.mkdir(parents=True, exist_ok=True)
        (chars_dir / "Lyra_Vael.md").write_text(
            "---\nname: Lyra Vael\ntitle: Arcane Chronomancer\ntags: [protagonist, chronomancer, outcast]\naliases: [The Weft-Walker]\n---\n"
            "# Lyra Vael\n\n"
            "Lyra Vael is an unlicensed chronomancer in the lower wards of [[Valenreach]]. "
            "She wields the forbidden discipline of [[Aetheric Resonance]] to perceive alternate timelines.\n",
            encoding="utf-8",
        )

        (chars_dir / "Lord_Malakar.md").write_text(
            "---\nname: Lord Malakar\ntitle: Grand Inquisitor\ntags: [antagonist, inquisitor]\naliases: [The Iron Eye]\n---\n"
            "# Lord Malakar\n\n"
            "Grand Inquisitor of the [[Silver Tribunal]], tasked with hunting rogue practitioners of [[Aetheric Resonance]].\n",
            encoding="utf-8",
        )

        places_dir = world_dir / "Places"
        places_dir.mkdir(parents=True, exist_ok=True)
        (places_dir / "Valenreach.md").write_text(
            "---\nname: Valenreach\ncategory: Capital City\ntags: [city, fortress, spire]\n---\n"
            "# Valenreach\n\n"
            "The fortified spire-city founded after the Cataclysm of Stars. Ruled by the [[Silver Tribunal]].\n",
            encoding="utf-8",
        )

        magic_dir = world_dir / "Magic"
        magic_dir.mkdir(parents=True, exist_ok=True)
        (magic_dir / "Aetheric_Resonance.md").write_text(
            "---\nname: Aetheric Resonance\ntags: [hard_magic, chronometry]\n---\n"
            "# Aetheric Resonance\n\n"
            "A hard magic system governing temporal manipulation.\n\n"
            "## Arcane Principles & Limitations\n"
            "1. Conservation of Entropy: Every second drawn forward accelerates physical aging in the caster.\n"
            "2. Conductive Medium: Requires refined stellar glass conduits.\n"
            "3. Costs: Causes severe neural degradation if overdrawn.\n",
            encoding="utf-8",
        )

        factions_dir = world_dir / "Factions"
        factions_dir.mkdir(parents=True, exist_ok=True)
        (factions_dir / "Silver_Tribunal.md").write_text(
            "---\nname: Silver Tribunal\ntags: [order, military, ruling_body]\n---\n"
            "# Silver Tribunal\n\n"
            "The supreme authority enforcing arcane non-proliferation across [[Valenreach]].\n",
            encoding="utf-8",
        )

        # ---------------------------------------------------------------------
        # STAGE 3: Multi-Chapter Manuscript Drafting with Directives
        # ---------------------------------------------------------------------
        ch1_text = (
            "---\n"
            "title: The Glass Spire\n"
            "pov: Lyra Vael\n"
            "status: Draft\n"
            "chrono_date: '1240-08-01'\n"
            "time: 1240-08-01 Dawn\n"
            "---\n"
            "# Chapter 1: The Glass Spire\n\n"
            "The rain over [[Valenreach]] fell in obsidian streaks. Lyra Vael adjusted the glass conduit on her gauntlet. "
            "Down in the sunken alleys, [[Lord Malakar]]'s hounds barked with synthetic fury.\n\n"
            "She touched the glyph, channeling [[Aetheric Resonance]]. The temporal flow shuddered.\n\n"
            "@choice: [Leap across the shattered viaduct] -> viaduct\n"
            "@choice: [Descend into the drainage conduit] -> sewer\n"
        )
        (ms_dir / "01_Chapter_01.md").write_text(ch1_text, encoding="utf-8")

        ch2_text = (
            "---\n"
            "title: The Viaduct Cross\n"
            "pov: Lyra Vael\n"
            "status: Draft\n"
            "chrono_date: '1240-08-02'\n"
            "time: 1240-08-02 Morning\n"
            "---\n"
            "# Chapter 2: The Viaduct Cross\n\n"
            "Lyra leaped into the rain. The stellar glass hummed, slowing gravity for a heartbeat. "
            "Across the gap, the banner of the [[Silver Tribunal]] flapped against the wind.\n\n"
            "@state: temporal_charge -= 15\n"
            "@req: temporal_charge > 5 -> safe_landing\n"
            "@choice: [Confront the vanguard] -> battle\n"
            "@choice: [Slip into the shadow alley] -> shadows\n"
        )
        (ms_dir / "02_Chapter_02.md").write_text(ch2_text, encoding="utf-8")

        # ---------------------------------------------------------------------
        # STAGE 4: World Doctor Diagnostic Audit
        # ---------------------------------------------------------------------
        doc_report = check_world(world_dir)
        self.assertIsNotNone(doc_report)
        self.assertEqual(doc_report.get("errors", 0), 0)

        # ---------------------------------------------------------------------
        # STAGE 5: Dual-Track Timeline Synchronization
        # ---------------------------------------------------------------------
        events = extract_timeline_events(ms_dir)
        self.assertTrue(len(events) >= 2)
        timeline_res = analyze_timeline_synchronization(events)
        self.assertEqual(timeline_res["total_events"], 2)
        self.assertEqual(len(timeline_res["paradoxes"]), 0)

        # ---------------------------------------------------------------------
        # STAGE 6: Autonomous Editorial Council Review
        # ---------------------------------------------------------------------
        critique = conduct_editorial_council(ms_dir, world_path=world_dir)
        self.assertGreater(critique.consensus_score, 0)
        self.assertEqual(len(critique.reviews), 4)
        self.assertGreater(critique.total_words, 0)

        # ---------------------------------------------------------------------
        # STAGE 7: Local Semantic Retrieval (RAG) Indexing & Query
        # ---------------------------------------------------------------------
        rag_engine = LocalLoreRetrievalEngine()
        rag_count = rag_engine.load_from_directory(world_dir)
        self.assertTrue(rag_count >= 3)
        rag_results = rag_engine.query("chronomancy stellar glass", top_k=3)
        self.assertTrue(len(rag_results) > 0)
        top_match = rag_results[0]
        self.assertIn("Aetheric_Resonance", top_match.chunk.doc_path)

        # ---------------------------------------------------------------------
        # STAGE 8: Local AI Fine-Tuning Dataset Synthesis
        # ---------------------------------------------------------------------
        ft_synthesizer = DatasetSynthesizer(cosmos_dir)
        ft_count = ft_synthesizer.scan_and_synthesize()
        self.assertTrue(ft_count >= 1)

        ft_out_dir = self.root / "fine_tuning_export"
        summary = export_fine_tuning_dataset(
            examples=ft_synthesizer.examples,
            output_dir=ft_out_dir,
            output_format="alpaca",
            val_split=0.2,
            generate_modelfile=True,
        )
        self.assertTrue((ft_out_dir / "train.jsonl").exists())
        self.assertTrue((ft_out_dir / "Modelfile").exists())
        self.assertTrue(summary["total_examples"] >= 1)

        # ---------------------------------------------------------------------
        # STAGE 9: Interactive Branching Narrative DAG Compilation
        # ---------------------------------------------------------------------
        branch_engine = BranchingNarrativeEngine()
        branch_count = branch_engine.load_from_directory(ms_dir)
        self.assertTrue(branch_count >= 1)

        html_gamebook = branch_engine.export_playable_html()
        ink_script = branch_engine.export_ink()
        twine_script = branch_engine.export_twine_twee()
        mermaid_graph = branch_engine.export_mermaid()

        branch_out_dir = self.root / "gamebook_export"
        branch_out_dir.mkdir(parents=True, exist_ok=True)
        (branch_out_dir / "gamebook.html").write_text(html_gamebook, encoding="utf-8")
        (branch_out_dir / "story.ink").write_text(ink_script, encoding="utf-8")
        (branch_out_dir / "story.twee").write_text(twine_script, encoding="utf-8")

        self.assertTrue((branch_out_dir / "gamebook.html").exists())
        self.assertTrue((branch_out_dir / "story.ink").exists())
        self.assertTrue((branch_out_dir / "story.twee").exists())
        self.assertIn("```mermaid", mermaid_graph)

        # ---------------------------------------------------------------------
        # STAGE 10: Universal Corpus Exporter (JSONL, SQLite, Markdown)
        # ---------------------------------------------------------------------
        corpus_out_dir = self.root / "corpus_export"
        corpus_scanner = CorpusScanner(cosmos_dir)
        corpus_scanner.scan()

        paths = export_jsonl(corpus_scanner, corpus_out_dir)
        export_sqlite(corpus_scanner, corpus_out_dir / "corpus.db")
        export_markdown_summary(corpus_scanner, corpus_out_dir / "_corpus_summary.md")

        self.assertTrue(paths["documents"].exists())
        self.assertTrue((corpus_out_dir / "corpus.db").exists())

        # Verify SQLite FTS5 index content
        conn = sqlite3.connect(corpus_out_dir / "corpus.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        self.assertTrue(doc_count >= 5)
        conn.close()

        # ---------------------------------------------------------------------
        # STAGE 11: Multi-Volume Series Omnibus & Media Overlays
        # ---------------------------------------------------------------------
        volumes = discover_series_volumes(cosmos_dir)
        self.assertTrue(len(volumes) >= 1)
        omnibus_report = compile_omnibus_manuscript(volumes, series_title="The Sunder Chronicle", author="Master Loreweaver")
        self.assertTrue(len(omnibus_report["markdown_content"]) > 0)
        self.assertTrue(omnibus_report["total_chapters"] >= 1)

        smil_out = self.root / "media_export" / "chapter_01.smil"
        smil_out.parent.mkdir(parents=True, exist_ok=True)
        overlay = build_chapter_overlay(ms_dir / "01_Chapter_01.md", "audio/chapter_01.mp3")
        smil_xml = generate_smil_xml(overlay)
        smil_out.write_text(smil_xml, encoding="utf-8")
        self.assertTrue(smil_out.exists())
        self.assertIn("<smil", smil_xml)

        # ---------------------------------------------------------------------
        # STAGE 12: Release Package Distribution & Manifest
        # ---------------------------------------------------------------------
        dist_out_dir = self.root / "dist_bundles"
        dist_out_dir.mkdir(parents=True, exist_ok=True)

        reader_pkg = package_reader_edition(ms_dir, dist_out_dir)
        sub_pkg = package_submission_bundle(ms_dir, dist_out_dir)
        arc_pkg = package_arc_bundle(ms_dir, dist_out_dir, reviewer="Grand Tour Reviewer")

        self.assertTrue(Path(reader_pkg["archive_path"]).exists())
        self.assertTrue(Path(sub_pkg["archive_path"]).exists())
        self.assertTrue(Path(arc_pkg["archive_path"]).exists())
        self.assertTrue(len(reader_pkg["sha256"]) > 20)

        # ---------------------------------------------------------------------
        # STAGE 13: Sovereign Studio Desktop Hub Static Telemetry Compilation
        # ---------------------------------------------------------------------
        hub_data = collect_studio_hub_data(cosmos_dir)
        self.assertEqual(hub_data["version"], "3.7.0")
        self.assertEqual(hub_data["metrics"]["total_chapters"], 2)
        self.assertTrue(hub_data["metrics"]["total_lore_entities"] >= 4)

        hub_static_file = self.root / "studio_hub.html"
        export_static_studio_hub(hub_static_file, cosmos_dir)
        self.assertTrue(hub_static_file.exists())
        html_text = hub_static_file.read_text(encoding="utf-8")
        self.assertIn("Ars Arcanum", html_text)
        self.assertIn("Aethelgard", html_text)
        self.assertIn("Content-Security-Policy", html_text)

        # ---------------------------------------------------------------------
        # STAGE 14: Sovereign Writing Sprint & Session Velocity Analytics
        # ---------------------------------------------------------------------
        sprint_state_file = ms_dir / ".arcanum" / ".sprint_state.json"
        sprint_log_file = ms_dir / ".arcanum" / ".sprint_log.jsonl"

        state = start_sprint(
            target_words=500,
            duration_minutes=25.0,
            manuscript_dir=ms_dir,
            state_file=sprint_state_file,
        )
        self.assertEqual(state["target_words"], 500)
        self.assertTrue(sprint_state_file.exists())

        completed_session = end_sprint(
            word_count=550,
            state_file=sprint_state_file,
            log_file=sprint_log_file,
        )
        self.assertFalse(sprint_state_file.exists())
        self.assertTrue(sprint_log_file.exists())
        self.assertEqual(completed_session.actual_words, 550)

        sessions = load_sessions(sprint_log_file)
        self.assertEqual(len(sessions), 1)
        velocity = compute_velocity_stats(sessions)
        self.assertEqual(velocity["total_sessions"], 1)
        self.assertEqual(velocity["total_words"], 550)

        streak = compute_daily_streak(sessions)
        self.assertEqual(streak["current_streak_days"], 1)

        sprint_html_out = self.root / "sprint_report.html"
        generate_sprint_report_html(velocity, streak, sessions, sprint_html_out)
        self.assertTrue(sprint_html_out.exists())
        sprint_html = sprint_html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", sprint_html)
        self.assertIn("Writing Sprint Dashboard", sprint_html)

        # ---------------------------------------------------------------------
        # STAGE 15: Causal DAG Novikov Self-Consistency & Revision Density Heatmap
        # ---------------------------------------------------------------------
        causal_events, causal_timelines = extract_causal_nodes(world_dir=world_dir, manuscript_dir=ms_dir)
        self.assertTrue(len(causal_events) >= 1)
        causal_findings = audit_causality(causal_events, causal_timelines)
        # Manuscript has linear scenes without causal loop violations
        critical_causal_errors = [f for f in causal_findings if f.get("severity") == "ERROR"]
        self.assertEqual(len(critical_causal_errors), 0)

        causal_html_out = self.root / "causality_report.html"
        generate_causality_html_report(
            {"world": "Eldoria", "events": causal_events, "timelines": causal_timelines, "findings": causal_findings},
            causal_html_out,
        )
        self.assertTrue(causal_html_out.exists())
        self.assertIn("Content-Security-Policy", causal_html_out.read_text(encoding="utf-8"))

        chapter_revision_stats = scan_manuscript_snapshots(ms_dir, snapshot_dir=None)
        self.assertTrue(len(chapter_revision_stats) >= 2)
        churn_data = analyze_revision_churn(chapter_revision_stats)
        self.assertTrue(churn_data["total_chapters"] >= 2)

        heatmap_html_out = self.root / "revision_heatmap.html"
        generate_revision_heatmap_html(
            {"manuscript": "The Obsidian Crown", "chapters": chapter_revision_stats, "findings": churn_data["findings"], "avg_churn_score": churn_data["avg_churn_score"], "total_chapters": churn_data["total_chapters"]},
            heatmap_html_out,
        )
        self.assertTrue(heatmap_html_out.exists())
        self.assertIn("Content-Security-Policy", heatmap_html_out.read_text(encoding="utf-8"))

        # ---------------------------------------------------------------------
        # STAGE 16: Cosmos Archive Freeze & Multi-Volume Dramatis Personae Synthesis
        # ---------------------------------------------------------------------
        # 16a: Cosmos Archive Freeze & Merkle-Root Cryptographic Provenance Seal
        freeze_manifest = scan_and_freeze_vault(cosmos_dir, version_tag="3.3.0")
        self.assertEqual(freeze_manifest.version, "3.3.0")
        self.assertEqual(len(freeze_manifest.root_sha256), 64)
        self.assertTrue(freeze_manifest.total_files >= 5)

        freeze_out_dir = self.root / "freeze_seal"
        manifest_path, seal_path = export_freeze_bundle(freeze_manifest, freeze_out_dir)
        self.assertTrue(manifest_path.exists())
        self.assertTrue(seal_path.exists())
        self.assertIn("PROVENANCE_SEAL", seal_path.name)

        verification_result = verify_vault_freeze(freeze_manifest.to_dict(), cosmos_dir)
        self.assertTrue(verification_result["is_verified"])
        self.assertEqual(verification_result["error_count"], 0)

        # 16b: Multi-Volume Dramatis Personae Extraction & Cast Gallery Synthesis
        discovered_chars = scan_character_profiles(world_dir)
        self.assertTrue(len(discovered_chars) >= 1)
        updated_chars, cast_findings = cross_reference_manuscripts(discovered_chars, cosmos_dir / "Manuscripts")
        self.assertTrue(len(updated_chars) >= 1)

        cast_md_out = self.root / "DRAMATIS_PERSONAE.md"
        cast_md = generate_dramatis_personae_markdown(list(updated_chars.values()), title="Aethelgard Dramatis Personae")
        cast_md_out.write_text(cast_md, encoding="utf-8")
        self.assertTrue(cast_md_out.exists())
        self.assertIn("##", cast_md)

        cast_html_out = self.root / "cast_gallery.html"
        generate_dramatis_personae_html(
            {"universe": "Aethelgard Cosmos", "characters": list(updated_chars.values()), "findings": cast_findings},
            cast_html_out,
        )
        self.assertTrue(cast_html_out.exists())
        cast_html_text = cast_html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", cast_html_text)
        self.assertIn("Dramatis Personae", cast_html_text)

        # ---------------------------------------------------------------------
        # STAGE 17: Sovereign Worldbuilding Codex & Arcane Mastery Verification
        # ---------------------------------------------------------------------
        # 17a: Static World Codex Generation
        categories = scan_world_vault(world_dir)
        self.assertTrue(len(categories) >= 1)
        codex_out = self.root / "aethelgard_codex.html"
        build_single_file_codex(categories, "Aethelgard Prime", codex_out)
        self.assertTrue(codex_out.exists())
        codex_content = codex_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", codex_content)
        self.assertIn("Lyra Vael", codex_content)

        # 17b: Hard Magic System Constraint & Arcane Audit
        magic_audit = run_magic_audit(str(world_dir), str(ms_dir))
        self.assertTrue(magic_audit["systems_registered"] >= 1)
        magic_html_out = self.root / "magic_matrix.html"
        generate_magic_html_report(magic_audit, magic_html_out)
        self.assertTrue(magic_html_out.exists())
        magic_html = magic_html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", magic_html)
        self.assertIn("Aetheric Resonance", magic_html)

        # 17c: In-World Cryptographic Ciphers & Phonetic Runes
        plain_secret = "DEFEND THE CITADEL"
        secret_enc = cipher_vigenere(plain_secret, key="MITHRIL")
        secret_dec = cipher_vigenere(secret_enc, key="MITHRIL", decode=True)
        self.assertEqual(secret_dec, plain_secret)
        rune_text = text_to_runes("Aethelgard Oath")
        rune_svg = generate_rune_svg(rune_text, title="Ancient Oath")
        self.assertIn("<svg", rune_svg)
        self.assertIn("ANCIENT OATH", rune_svg)

        # 17d: Dynastic Genealogy & Succession Lineage
        genealogy_chars = load_characters_and_houses(world_dir)
        self.assertTrue(len(genealogy_chars) >= 1)
        genealogy_findings = validate_genealogy(genealogy_chars)
        self.assertEqual(len([f for f in genealogy_findings if f["severity"] == "FATAL"]), 0)
        genealogy_mermaid = generate_mermaid_flowchart(genealogy_chars)
        self.assertIn("```mermaid", genealogy_mermaid)

        # 17e: Conlang Phonotactics & Historical Sound Shifts
        lang_profile = {
            "name": "Solaris",
            "consonants": ["p", "t", "k", "s", "m", "n", "l", "r"],
            "vowels": ["a", "e", "i", "o", "u"],
            "syllable_structures": ["CV", "CVC"],
            "forbidden_clusters": ["sr"],
        }
        gen_words = generate_words(lang_profile, count=5, num_syllables=2, seed=42)
        self.assertEqual(len(gen_words), 5)
        shifted = mutate_text("apata", ["p > b / V_V"], ["a", "e", "i", "o", "u"], ["p", "t", "k", "b", "d", "g"])
        self.assertEqual(shifted, "abata")

        # 17f: Geopolitical Faction Diplomacy & Lanchester Combat
        factions = extract_faction_profiles(world_dir)
        self.assertTrue(len(factions) >= 1)
        faction_findings = audit_faction_diplomacy(factions)
        self.assertEqual(len([f for f in faction_findings if f["severity"] == "ERROR"]), 0)
        combat_sim = calc_lanchester_battle(attacker_force=10000, defender_force=5000, law="square")
        self.assertEqual(combat_sim["victor"], "Attacker")
        logistics_sim = calc_campaign_logistics(infantry=5000, cavalry=1000, distance_km=100.0)
        self.assertTrue(logistics_sim["logistics_requirements"]["is_within_wagon_radius"])

        # 17g: Custom Planetary Calendars & Multi-Moon Synodic Cycles
        cal_spec = load_calendar_spec(world_dir)
        self.assertTrue(cal_spec["days_per_year"] > 0)
        m_phase = get_moon_phase(14, {"name": "Selene", "period": 28.0, "offset": 0.0})
        self.assertEqual(m_phase["phase_name"], "Full Moon")
        self.assertEqual(m_phase["glyph"], "🌕")

        # ---------------------------------------------------------------------
        # STAGE 18: Story Craft, Prose Mechanics & Narrative Architecture
        # ---------------------------------------------------------------------
        # 18a: In-World Economy & Purchasing Power Parity (PPP)
        (world_dir / "Economies").mkdir(parents=True, exist_ok=True)
        (world_dir / "Economies" / "Solar_Standard.md").write_text("""---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
tech_era: "medieval"
currencies:
  - "Solar Crown: 1.0"
  - "Silver Sovereign: 0.1"
commodity_basket:
  - "loaf_of_bread: 2"
  - "iron_sword: 25"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(world_dir)
        self.assertIn("Solar Standard Economy", econs)
        trade_res = calc_trade_margin(buy_price_per_ton=100.0, sell_price_per_ton=250.0, cargo_tons=20.0, distance_km_or_ly=150.0)
        self.assertTrue(trade_res["is_profitable"])
        tech_anach = audit_technological_anachronisms(ms_dir, baseline_era="medieval")
        self.assertIsInstance(tech_anach, list)

        # 18b: Overland & Naval Journey Modeler
        journey_res = calculate_journey(distance_km=120.0, terrain="mountains", mode="foot-normal", party_size=3)
        self.assertTrue(journey_res["total_days"] > 0)
        journey_html_out = self.root / "journey_plan.html"
        generate_journey_html_report(journey_res, journey_html_out)
        self.assertTrue(journey_html_out.exists())
        self.assertIn("Content-Security-Policy", journey_html_out.read_text(encoding="utf-8"))

        # 18c: Vector Cartography & Interactive Map Viewer
        locations = parse_world_locations(world_dir)
        self.assertTrue(len(locations) >= 1)
        map_svg = generate_vector_svg_map(locations, title="Aethelgard Map", grid_mode="hex")
        self.assertIn("<svg", map_svg)
        map_html_out = self.root / "aethelgard_map.html"
        generate_cartography_html_viewer(locations, "Aethelgard Map", map_html_out)
        self.assertTrue(map_html_out.exists())
        self.assertIn("Content-Security-Policy", map_html_out.read_text(encoding="utf-8"))

        # 18d: Narrative Pacing, POV Balance & Tension Arc Analytics
        pacing_rep = scan_manuscript_pacing(ms_dir)
        self.assertTrue(pacing_rep["total_chapters"] >= 1)
        pacing_html_out = self.root / "pacing_analysis.html"
        generate_pacing_html_report(pacing_rep, pacing_html_out)
        self.assertTrue(pacing_html_out.exists())
        self.assertIn("Content-Security-Policy", pacing_html_out.read_text(encoding="utf-8"))

        # 18e: Multi-Paradigm Story Structure & Beat Alignment
        struct_rep = scan_manuscript_structure(ms_dir, paradigm_key="three_act")
        self.assertTrue(len(struct_rep["beats"]) >= 5)
        struct_html_out = self.root / "structure_alignment.html"
        generate_structure_html_report(struct_rep, struct_html_out)
        self.assertTrue(struct_html_out.exists())
        self.assertIn("Content-Security-Policy", struct_html_out.read_text(encoding="utf-8"))

        # 18f: Character Voice Profiler & Dialogue Fingerprints
        voice_rep = scan_manuscript_voices(ms_dir)
        self.assertIsInstance(voice_rep["profiles"], dict)
        voice_html_out = self.root / "voice_fingerprints.html"
        generate_voice_html_report(voice_rep, voice_html_out)
        self.assertTrue(voice_html_out.exists())
        self.assertIn("Content-Security-Policy", voice_html_out.read_text(encoding="utf-8"))

        # 18g: Stylistics, Dialogue Mechanics & Readability Rhythm
        stylistics_rep = scan_text_or_path(ms_dir)
        self.assertTrue(stylistics_rep["total_files"] >= 1)
        stylistics_html_out = self.root / "stylistics_report.html"
        generate_stylistics_html_report(stylistics_rep, stylistics_html_out)
        self.assertTrue(stylistics_html_out.exists())
        self.assertIn("Content-Security-Policy", stylistics_html_out.read_text(encoding="utf-8"))

        # ---------------------------------------------------------------------
        # STAGE 19: Worldbuilding Sciences & Narrative Mechanics Expansion
        # ---------------------------------------------------------------------
        # 19a: Procedural Focus Soundscapes & WebAudio Synthesizer
        ambient_wav = self.root / "ambient_focus.wav"
        synthesize_wav(output_path=ambient_wav, duration_sec=1, noise_type="brown")
        self.assertTrue(ambient_wav.exists())
        ambient_html = self.root / "ambient_synth.html"
        generate_ambient_html_synthesizer(ambient_html)
        self.assertTrue(ambient_html.exists())
        self.assertIn("Content-Security-Policy", ambient_html.read_text(encoding="utf-8"))

        # 19b: Dynamic Tactical Combat & Monte Carlo Skirmish Simulator
        battle_res = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        self.assertIn(battle_res["winner"], (0, 1, 2))
        self.assertTrue(len(battle_res["log"]) > 0)
        mc_res = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, runs=10)
        self.assertEqual(mc_res["runs"], 10)

        # 19c: Motivation-Reaction Unit (MRU) Scene Mechanics
        scene_rep = scan_manuscript_scenes(ms_dir)
        self.assertTrue(scene_rep["total_scenes"] >= 1)
        scene_html = self.root / "scene_mechanics.html"
        generate_scene_mechanics_html(scene_rep, scene_html)
        self.assertTrue(scene_html.exists())
        self.assertIn("Content-Security-Policy", scene_html.read_text(encoding="utf-8"))

        # 19d: Multi-Track Plot Grid & Subplot Matrix
        plot_rep = scan_manuscript_plot_matrix(ms_dir)
        self.assertTrue(plot_rep["total_chapters"] >= 1)
        plot_html = self.root / "plot_matrix.html"
        generate_plot_html_report(plot_rep, plot_html)
        self.assertTrue(plot_html.exists())
        self.assertIn("Content-Security-Policy", plot_html.read_text(encoding="utf-8"))

        # 19e: Dual-Track Chronological vs Narrative Timeline Synchronizer
        timeline_events = extract_timeline_events(ms_dir)
        self.assertTrue(len(timeline_events) >= 1)
        timeline_rep = analyze_timeline_synchronization(timeline_events)
        timeline_html = self.root / "timeline_sync.html"
        generate_timeline_html_report(timeline_rep, timeline_html)
        self.assertTrue(timeline_html.exists())
        self.assertIn("Content-Security-Policy", timeline_html.read_text(encoding="utf-8"))

        # 19f: Planetary Climate, Orographic Rain Shadows & Köppen Biomes
        insolation = calc_planetary_insolation(stellar_luminosity=1.0, semi_major_axis_au=1.0)
        circulation = calc_atmospheric_circulation(rotation_period_hours=24.0)
        orography = calc_orographic_rain_shadow(mountain_elevation_m=3000.0, base_precip_mm=1000.0)
        climate_html = self.root / "climate_report.html"
        generate_climate_html_report({"insolation": insolation, "circulation": circulation, "orography": orography}, climate_html)
        self.assertTrue(climate_html.exists())
        self.assertIn("Content-Security-Policy", climate_html.read_text(encoding="utf-8"))

        # 19g: Trophic Food Web Ecology & Lindeman Efficiency
        (world_dir / "Bestiary").mkdir(parents=True, exist_ok=True)
        (world_dir / "Flora").mkdir(parents=True, exist_ok=True)
        (world_dir / "Bestiary" / "Mountain_Goat.md").write_text("""---
name: "Mountain Goat"
trophic_level: 2
habitat: "Highland"
dietary_prey:
  - "[[Highland Moss]]"
biomass_kg: 45.0
population_density: 20.0
---
""", encoding="utf-8")
        (world_dir / "Bestiary" / "Gryphon.md").write_text("""---
name: "Highland Gryphon"
trophic_level: 4
habitat: "Highland"
dietary_prey:
  - "[[Mountain Goat]]"
biomass_kg: 120.0
population_density: 0.5
---
""", encoding="utf-8")
        (world_dir / "Flora" / "Highland_Moss.md").write_text("""---
name: "Highland Moss"
trophic_level: 1
habitat: "Highland"
biomass_kg: 2000.0
population_density: 500.0
---
""", encoding="utf-8")
        species_rep = extract_species_profiles(world_dir)
        self.assertIn("Highland Gryphon", species_rep)
        eco_findings = audit_ecosystem(species_rep)
        self.assertIsInstance(eco_findings, list)
        eco_mermaid = generate_ecology_mermaid(species_rep)
        self.assertIn("flowchart TD", eco_mermaid)
        eco_html = self.root / "ecology_report.html"
        generate_ecology_html_report({"world": "Aethelgard", "species": species_rep, "findings": eco_findings}, eco_html)
        self.assertTrue(eco_html.exists())
        self.assertIn("Content-Security-Policy", eco_html.read_text(encoding="utf-8"))

        # 19h: Earth Idiom & Immersion Linter
        idiom_findings = audit_manuscript_idioms(ms_dir)
        self.assertIsInstance(idiom_findings, list)
        idiom_html = self.root / "idioms_report.html"
        generate_idioms_html_report({"manuscript": "Aethelgard", "findings": idiom_findings}, idiom_html)
        self.assertTrue(idiom_html.exists())
        self.assertIn("Content-Security-Policy", idiom_html.read_text(encoding="utf-8"))

        # ---------------------------------------------------------------------
        # STAGE 20: Authoring Studios, Publishing Toolchains & Creative Scaffolding Expansion
        # ---------------------------------------------------------------------
        # 20a: Back-Matter Concordance & Dramatis Personae Indexer
        concordance_res = generate_concordance(bible_dir=world_dir, ms_dir=ms_dir)
        self.assertGreaterEqual(concordance_res["characters_count"], 1)
        self.assertGreaterEqual(concordance_res["volumes_updated"], 1)
        self.assertTrue(any(Path(f).exists() for f in concordance_res["generated_files"]))

        # 20b: Sovereign Zen Drafting Studio & In-Situ Lore Drawer
        zen_out = self.root / "zen_studio.html"
        generate_zen_studio_bundle(ms_dir, world_path=world_dir, output_path=zen_out)
        self.assertTrue(zen_out.exists())
        zen_content = zen_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", zen_content)
        self.assertIn("Zen Studio", zen_content)

        # 20c: Visual Story Canvas & Multi-Paradigm Corkboard
        scene_cards = extract_scene_cards(ms_dir)
        self.assertGreaterEqual(len(scene_cards), 1)
        canvas_out = self.root / "story_canvas.html"
        generate_story_canvas_html(ms_dir, scene_cards, paradigm_key="three_act", output_path=canvas_out)
        self.assertTrue(canvas_out.exists())
        canvas_content = canvas_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", canvas_content)
        self.assertIn("Story Canvas", canvas_content)

        # 20d: Multi-Volume Series Omnibus Compiler
        omni_report = compile_omnibus_manuscript(volumes, series_title="The Sunder Chronicle", author="Master Loreweaver")
        self.assertTrue(len(omni_report["markdown_content"]) > 0)
        self.assertIn("Table of Contents", omni_report["markdown_content"])

        # 20e: Author Portfolio & Catalog Analytics Dashboard
        port_rep = scan_portfolio(cosmos_dir / "Manuscripts")
        self.assertGreaterEqual(port_rep["total_projects"], 1)
        self.assertIn("total_target_words", port_rep)
        port_html = self.root / "portfolio_hub.html"
        generate_portfolio_html(port_rep, port_html)
        self.assertTrue(port_html.exists())
        self.assertIn("Content-Security-Policy", port_html.read_text(encoding="utf-8"))

        # 20f: EPUB 3 SMIL Media Overlays & Synchronized Audio Player
        ch1_file = ms_dir / "01_Chapter_01.md"
        media_overlay_obj = build_chapter_overlay(ch1_file, index=1, wpm=150)
        self.assertEqual(media_overlay_obj.chapter_index, 1)
        player_html = self.root / "audio_player.html"
        generate_synchronized_player_html([media_overlay_obj], player_html)
        self.assertTrue(player_html.exists())
        self.assertIn("Content-Security-Policy", player_html.read_text(encoding="utf-8"))

        # 20g: Smart Typography Normalizer & Punctuation Engine
        raw_prose = '"Hello," he whispered... The war (1914-1918) ended--finally. Don\'t forget.'
        polished_prose, _typo_stats = normalize_typography_text(raw_prose)
        self.assertIn("“Hello,”", polished_prose)
        self.assertIn("ended—finally", polished_prose)
        self.assertIn("Don’t", polished_prose)
        clean_res = clean_target(ms_dir, in_place=False, make_backup=False)
        self.assertGreaterEqual(clean_res["summary"]["files_scanned"], 1)

        # 20h: ISBN-13 Vector SVG/PNG Barcode Engine
        clean_isbn_val = validate_and_normalize_isbn("978-0-345-39180-3")
        self.assertEqual(clean_isbn_val, "9780345391803")
        svg_barcode = self.root / "cover_barcode.svg"
        export_barcode(clean_isbn_val, svg_barcode)
        self.assertTrue(svg_barcode.exists())
        self.assertIn("<svg", svg_barcode.read_text(encoding="utf-8"))
        png_barcode = self.root / "cover_barcode.png"
        export_barcode(clean_isbn_val, png_barcode)
        self.assertTrue(png_barcode.exists())
        self.assertTrue(png_barcode.stat().st_size > 100)

        # ---------------------------------------------------------------------
        # STAGE 21: Local Intelligence, Editorial Intelligence & Narrative Distribution Architecture
        # ---------------------------------------------------------------------
        # 21a: Interactive Branching Narrative DAG Compilation
        branch_engine = BranchingNarrativeEngine()
        branch_count = branch_engine.load_from_directory(ms_dir)
        self.assertGreaterEqual(branch_count, 1)
        branch_html = self.root / "stage21_gamebook.html"
        branch_html.write_text(branch_engine.export_playable_html(), encoding="utf-8")
        self.assertTrue(branch_html.exists())
        self.assertIn("Content-Security-Policy", branch_html.read_text(encoding="utf-8"))

        # 21b: Local Semantic Retrieval (RAG) & Viewer Synthesis
        rag_engine = LocalLoreRetrievalEngine()
        rag_count = rag_engine.load_from_directory(world_dir)
        self.assertGreaterEqual(rag_count, 1)
        rag_results = rag_engine.query("Aetheric Resonance Spellblade", top_k=3)
        rag_html = self.root / "stage21_rag_viewer.html"
        rag_html.write_text(generate_html_retrieval_viewer("Spellblade Lore", rag_results), encoding="utf-8")
        self.assertTrue(rag_html.exists())
        self.assertIn("Content-Security-Policy", rag_html.read_text(encoding="utf-8"))

        # 21c: Multi-Perspective Autonomous Editorial Council Dashboard
        council_report = conduct_editorial_council(ms_dir, world_path=world_dir)
        self.assertGreaterEqual(council_report.consensus_score, 0)
        self.assertEqual(len(council_report.reviews), 4)
        council_dashboard = self.root / "stage21_council_dashboard.html"
        generate_council_html_dashboard(council_report, council_dashboard)
        self.assertTrue(council_dashboard.exists())
        self.assertIn("Content-Security-Policy", council_dashboard.read_text(encoding="utf-8"))

        # 21d: Local AI Fine-Tuning Synthesizer (Alpaca, ShareGPT, ChatML, Modelfile)
        dataset_synth = DatasetSynthesizer(cosmos_dir)
        synth_count = dataset_synth.scan_and_synthesize()
        self.assertGreaterEqual(synth_count, 1)
        ft_out_dir = self.root / "stage21_fine_tuning"
        ft_summary = export_fine_tuning_dataset(
            dataset_synth.examples,
            output_dir=ft_out_dir,
            output_format="chatml",
            val_split=0.2,
            generate_modelfile=True,
        )
        self.assertTrue((ft_out_dir / "train.jsonl").exists())
        self.assertTrue((ft_out_dir / "Modelfile").exists())
        self.assertGreaterEqual(ft_summary["total_examples"], 1)

        # 21e: Universal Structured Corpus & RAG Dataset Exporter
        corpus_scanner = CorpusScanner(cosmos_dir)
        corpus_scanner.scan()
        self.assertGreaterEqual(len(corpus_scanner.documents), 1)
        corpus_out_dir = self.root / "stage21_corpus_export"
        corpus_paths = export_jsonl(corpus_scanner, corpus_out_dir)
        self.assertTrue(corpus_paths["documents"].exists())
        corpus_db = corpus_out_dir / "stage21_corpus.db"
        export_sqlite(corpus_scanner, corpus_db)
        self.assertTrue(corpus_db.exists())
        corpus_summary_md = corpus_out_dir / "_corpus_summary.md"
        export_markdown_summary(corpus_scanner, corpus_summary_md)
        self.assertTrue(corpus_summary_md.exists())

        # 21f: Offline Neural TTS & Audio Proofreader
        tts_paragraphs = clean_prose_for_speech(
            (ms_dir / "01_Chapter_01.md").read_text(encoding="utf-8"),
            pronunciation_dict={"Aethelgard": "AY-thel-gard"},
        )
        self.assertGreaterEqual(len(tts_paragraphs), 1)
        tts_html = self.root / "stage21_audio_player.html"
        generate_tts_html_player(tts_paragraphs, title="Chapter 1 Proofread", output_path=tts_html)
        self.assertTrue(tts_html.exists())
        self.assertIn("Content-Security-Policy", tts_html.read_text(encoding="utf-8"))

        # 21g: Multi-Platform Release Distribution Packaging (Codex Bundle)
        codex_pkg = package_codex_bundle(cosmos_dir, self.root / "stage21_dist")
        self.assertTrue(Path(codex_pkg["archive_path"]).exists())
        self.assertEqual(codex_pkg["package_type"], "codex")
        self.assertGreater(len(codex_pkg["sha256"]), 20)

        # 21h: World Doctor Deep Integrity Audit
        doctor_findings = check_world(str(world_dir), manuscript_dir=str(ms_dir))
        self.assertGreaterEqual(doctor_findings["notes"], 1)
        self.assertEqual(len(doctor_findings["broken_links"]), 0)


if __name__ == "__main__":
    unittest.main()
