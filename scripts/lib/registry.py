#!/usr/bin/env python3
"""
Ars Arcanum Engine & Plugin Registry (scripts/lib/registry.py)
============================================================
Defines core vs craft engine classification, metadata registry, dynamic plugin
discovery, and capability introspection across CLI and GUI surfaces.
"""

from dataclasses import dataclass, field
from enum import Enum
import importlib
from typing import Any, Dict, List, Optional


class EngineCategory(str, Enum):
    CORE = "core"
    CRAFT = "craft"
    UTILITY = "utility"


@dataclass
class EngineSpec:
    """Metadata specification for an Ars Arcanum engine / plugin module."""
    name: str
    category: EngineCategory
    title: str
    description: str
    module_name: str
    cli_command: str
    aliases: List[str] = field(default_factory=list)
    studio_tab: Optional[str] = None
    default_enabled: bool = True
    enabled: bool = True


# Canonical Engine Registry Definitions
_ENGINES: Dict[str, EngineSpec] = {
    # --- Core Authoring, Diagnostics, & Pipeline ---
    "config": EngineSpec(
        name="config",
        category=EngineCategory.CORE,
        title="Project Configuration",
        description="Global and local workspace configuration, paths, and preferences",
        module_name="lib.config",
        cli_command="config",
    ),
    "cache": EngineSpec(
        name="cache",
        category=EngineCategory.CORE,
        title="Performance Cache",
        description="Fast mtime-keyed in-memory index for lore vaults and manuscripts",
        module_name="lib.cache",
        cli_command="cache",
    ),
    "fs_utils": EngineSpec(
        name="fs_utils",
        category=EngineCategory.CORE,
        title="Atomic File System",
        description="Crash-safe atomic writes and storage operations",
        module_name="lib.fs_utils",
        cli_command="fs",
    ),
    "migrate": EngineSpec(
        name="migrate",
        category=EngineCategory.CORE,
        title="Vault Migration",
        description="Schema upgrade engine for migrating older lore vaults and projects",
        module_name="lib.migrate",
        cli_command="migrate",
        aliases=["upgrade"],
    ),
    "docx_sync": EngineSpec(
        name="docx_sync",
        category=EngineCategory.CORE,
        title="DOCX Bidirectional Sync",
        description="Three-way content hash sync with conflict branching for Microsoft Word / LibreOffice",
        module_name="lib.docx_sync",
        cli_command="docx",
        studio_tab="Editor",
    ),
    "preflight": EngineSpec(
        name="preflight",
        category=EngineCategory.CORE,
        title="Typesetting Preflight Validator",
        description="Print-PDF compliance, image resolution, and trim size validation",
        module_name="lib.preflight",
        cli_command="preflight",
        studio_tab="Publishing",
    ),
    "barcode": EngineSpec(
        name="barcode",
        category=EngineCategory.CORE,
        title="ISBN-13 Barcode Generator",
        description="Vector SVG/PNG EAN-13 / Bookland ISBN barcode generation with checksum verification",
        module_name="lib.barcode",
        cli_command="barcode",
        studio_tab="Publishing",
    ),
    "frontmatter_builder": EngineSpec(
        name="frontmatter_builder",
        category=EngineCategory.CORE,
        title="Frontmatter & Backmatter Builder",
        description="Generates copyright, dedication, epigraph, and biographical matter",
        module_name="lib.frontmatter_builder",
        cli_command="matter",
        studio_tab="Publishing",
    ),
    "manuscript_diff": EngineSpec(
        name="manuscript_diff",
        category=EngineCategory.CORE,
        title="Draft Diff & Visual Redline",
        description="Comparative redline changelog and visual diffs between manuscript drafts",
        module_name="lib.manuscript_diff",
        cli_command="compare",
        aliases=["diff", "redline"],
        studio_tab="Editor",
    ),
    "tts_reader": EngineSpec(
        name="tts_reader",
        category=EngineCategory.CORE,
        title="Offline Neural Audio Proofreader",
        description="Local TTS synthesis and interactive WebAudio playback for proofreading",
        module_name="lib.tts_reader",
        cli_command="read",
        studio_tab="Editor",
    ),
    "typography_cleaner": EngineSpec(
        name="typography_cleaner",
        category=EngineCategory.CORE,
        title="Typography Cleaner",
        description="Normalizes smart curly quotes, em-dashes, and typographical ellipses",
        module_name="lib.typography_cleaner",
        cli_command="polish typography",
        aliases=["clean-typography"],
        studio_tab="Editor",
    ),
    "world_doctor": EngineSpec(
        name="world_doctor",
        category=EngineCategory.CORE,
        title="World Bible Doctor",
        description="Deep lore consistency, broken wikilink, orphan entity, and timeline chronology checker",
        module_name="lib.world_doctor",
        cli_command="world-doctor",
        aliases=["doctor-world"],
        studio_tab="Diagnostics",
    ),
    "concordance": EngineSpec(
        name="concordance",
        category=EngineCategory.CORE,
        title="Dramatis Personae & Glossary Generator",
        description="Compiles character indices and lore terms into publication-ready back-matter",
        module_name="lib.concordance",
        cli_command="concordance",
        studio_tab="Publishing",
    ),
    "diagnostics": EngineSpec(
        name="diagnostics",
        category=EngineCategory.CORE,
        title="System Diagnostics & Diagnostics Report",
        description="Toolchain validation, environment health checks, and redacted bug triage bundles",
        module_name="lib.diagnostics",
        cli_command="doctor",
        studio_tab="Diagnostics",
    ),

    # --- Craft & Specialized Worldbuilding Engines ---
    "astrophysics": EngineSpec(
        name="astrophysics",
        category=EngineCategory.CRAFT,
        title="Astrophysics & Orbital Mechanics",
        description="Relativistic brachistochrone, time dilation, and orbital mechanics calculator",
        module_name="lib.astrophysics",
        cli_command="calc astro",
        aliases=["astrophysics"],
        studio_tab="Worldbuilding",
    ),
    "climate": EngineSpec(
        name="climate",
        category=EngineCategory.CRAFT,
        title="Planetary Climate & Köppen Biomes",
        description="Solar insolation, atmospheric circulation cells, and orographic precipitation modeling",
        module_name="lib.climate",
        cli_command="calc climate",
        aliases=["climate"],
        studio_tab="Worldbuilding",
    ),
    "cartography": EngineSpec(
        name="cartography",
        category=EngineCategory.CRAFT,
        title="Offline Vector Cartography",
        description="Interactive SVG map viewer and geographic waypoint network explorer",
        module_name="lib.cartography",
        cli_command="map",
        studio_tab="Worldbuilding",
    ),
    "causality": EngineSpec(
        name="causality",
        category=EngineCategory.CRAFT,
        title="Causal Graph & Timeline Branches",
        description="Directed Acyclic Graph causality engine, timeline paradox detection, and multiverse trees",
        module_name="lib.causality",
        cli_command="causality",
        studio_tab="Worldbuilding",
    ),
    "cipher": EngineSpec(
        name="cipher",
        category=EngineCategory.CRAFT,
        title="In-World Ciphers & Runes",
        description="Vigenère, Atbash, Caesar, and custom phonetic rune script transcribers",
        module_name="lib.cipher",
        cli_command="cipher",
        studio_tab="Worldbuilding",
    ),
    "conlang": EngineSpec(
        name="conlang",
        category=EngineCategory.CRAFT,
        title="Conlang Phonotactics & Lexicon",
        description="Phoneme inventory generator, sound-law shift simulator, and constructed vocabulary builder",
        module_name="lib.conlang",
        cli_command="conlang",
        studio_tab="Worldbuilding",
    ),
    "ecology": EngineSpec(
        name="ecology",
        category=EngineCategory.CRAFT,
        title="Ecology & Food Web Simulator",
        description="Trophic energy pyramid validator (Lindeman 10% efficiency) and apex predator sustainability",
        module_name="lib.ecology",
        cli_command="ecology",
        studio_tab="Worldbuilding",
    ),
    "economy": EngineSpec(
        name="economy",
        category=EngineCategory.CRAFT,
        title="Macroeconomics & Currencies",
        description="In-world fiat/specie exchange rates, purchasing power parity, and commodity price modeling",
        module_name="lib.economy",
        cli_command="economy",
        studio_tab="Worldbuilding",
    ),
    "factions": EngineSpec(
        name="factions",
        category=EngineCategory.CRAFT,
        title="Geopolitical Factions & Diplomacy",
        description="Diplomatic relation matrices, tension paradox detection, and alliance networks",
        module_name="lib.factions",
        cli_command="faction",
        studio_tab="Worldbuilding",
    ),
    "genealogy": EngineSpec(
        name="genealogy",
        category=EngineCategory.CRAFT,
        title="Dynastic Lineage & Genealogy",
        description="Family tree compilation, succession rank calculator, and Mermaid lineage diagrams",
        module_name="lib.genealogy",
        cli_command="genealogy",
        aliases=["lineage"],
        studio_tab="Worldbuilding",
    ),
    "idioms": EngineSpec(
        name="idioms",
        category=EngineCategory.CRAFT,
        title="Cultural Idioms & Metaphors",
        description="World-specific idiomatic expression generator, metaphorical domain mapper, and prose scanner",
        module_name="lib.idioms",
        cli_command="audit idioms",
        aliases=["idioms"],
        studio_tab="Craft",
    ),
    "journey": EngineSpec(
        name="journey",
        category=EngineCategory.CRAFT,
        title="Travel & Logistics Calculator",
        description="Travel time, supply consumption, terrain difficulty, and pacing logistics",
        module_name="lib.journey",
        cli_command="calc journey",
        aliases=["journey"],
        studio_tab="Worldbuilding",
    ),
    "magic_system": EngineSpec(
        name="magic_system",
        category=EngineCategory.CRAFT,
        title="Magic System Constraints",
        description="Hard magic rule enforcement, mana costs, and user tier limit validator",
        module_name="lib.magic_system",
        cli_command="magic-check",
        aliases=["magic-report", "magic"],
        studio_tab="Worldbuilding",
    ),
    "pacing": EngineSpec(
        name="pacing",
        category=EngineCategory.CRAFT,
        title="Pacing & Dialogue Rhythm",
        description="Dialogue-to-narrative density ratio, sentence length variance, and scene momentum analyzer",
        module_name="lib.pacing",
        cli_command="pace",
        studio_tab="Craft",
    ),
    "plot_matrix": EngineSpec(
        name="plot_matrix",
        category=EngineCategory.CRAFT,
        title="Plot Grid & Subplot Matrix",
        description="Multi-threaded narrative grid tracking concurrent character arcs and mystery clues",
        module_name="lib.plot_matrix",
        cli_command="plot",
        studio_tab="Craft",
    ),
    "portfolio": EngineSpec(
        name="portfolio",
        category=EngineCategory.CRAFT,
        title="Portfolio & Drafting Velocity",
        description="Multi-manuscript word count tracker, sprint pacing, and catalog overview dashboard",
        module_name="lib.portfolio",
        cli_command="portfolio",
        studio_tab="Overview",
    ),
    "prophecy": EngineSpec(
        name="prophecy",
        category=EngineCategory.CRAFT,
        title="Prophecy Lifecycle Tracker",
        description="Tracks cryptic prophecy stanzas, interpretations, fulfillment conditions, and subversions",
        module_name="lib.prophecy",
        cli_command="prophecy",
        studio_tab="Worldbuilding",
    ),
    "scene_mechanics": EngineSpec(
        name="scene_mechanics",
        category=EngineCategory.CRAFT,
        title="Scene Mechanics & Tension",
        description="Analyzes goal, conflict, disaster, reaction, dilemma, and decision (MRU/Swain cycle)",
        module_name="lib.scene_mechanics",
        cli_command="tension",
        aliases=["scene"],
        studio_tab="Craft",
    ),
    "senses": EngineSpec(
        name="senses",
        category=EngineCategory.CRAFT,
        title="Sensory Immersion Heatmap",
        description="Distribution of visual, auditory, olfactory, tactile, and gustatory descriptive prose",
        module_name="lib.senses",
        cli_command="audit senses",
        aliases=["senses"],
        studio_tab="Craft",
    ),
    "series_continuity": EngineSpec(
        name="series_continuity",
        category=EngineCategory.CRAFT,
        title="Series Continuity Ledger",
        description="Tracks recurring character traits, scars, eye color, and gear across multi-volume series",
        module_name="lib.series_continuity",
        cli_command="series",
        studio_tab="Worldbuilding",
    ),
    "structure": EngineSpec(
        name="structure",
        category=EngineCategory.CRAFT,
        title="Narrative Structure & Paradigms",
        description="Validates manuscript beats against 3-Act, Save the Cat, Hero's Journey, and Fichtean Curve",
        module_name="lib.structure",
        cli_command="structure",
        studio_tab="Craft",
    ),
    "stylistics": EngineSpec(
        name="stylistics",
        category=EngineCategory.CRAFT,
        title="Stylistics & Readability Audits",
        description="Flesch-Kincaid grade level, passive voice detector, echo words, and dialogue tags",
        module_name="lib.stylistics",
        cli_command="audit style",
        aliases=["stylistics"],
        studio_tab="Craft",
    ),
    "tactical_sim": EngineSpec(
        name="tactical_sim",
        category=EngineCategory.CRAFT,
        title="Tactical Skirmish & Battle Simulator",
        description="Lanchester square-law combat model, terrain modifiers, morale decay, and casualty sim",
        module_name="lib.tactical_sim",
        cli_command="sim battle",
        aliases=["battle"],
        studio_tab="Worldbuilding",
    ),
    "voice": EngineSpec(
        name="voice",
        category=EngineCategory.CRAFT,
        title="Character Voice Profiler",
        description="Dialogue vocabulary uniqueness, sentence rhythm, and verbal tic consistency per POV",
        module_name="lib.voice",
        cli_command="audit voice",
        aliases=["voice"],
        studio_tab="Craft",
    ),
    "ambient": EngineSpec(
        name="ambient",
        category=EngineCategory.CRAFT,
        title="Ambient Focus & Binaural Beats",
        description="Local offline sound synthesis for deep writing focus (binaural beats, rain, fire, library)",
        module_name="lib.ambient",
        cli_command="ambient",
        studio_tab="Tools",
    ),
    "codex_export": EngineSpec(
        name="codex_export",
        category=EngineCategory.CRAFT,
        title="World Wiki Codex Export",
        description="Compiles world lore notes into a standalone, searchable offline HTML encyclopedia",
        module_name="lib.codex_export",
        cli_command="codex",
        studio_tab="Publishing",
    ),
    "calendar": EngineSpec(
        name="calendar",
        category=EngineCategory.CRAFT,
        title="Custom Planetary Calendars & Moons",
        description="Multi-moon synodic phase tracker, celestial conjunctions, and fictional calendar math",
        module_name="lib.calendar",
        cli_command="calendar",
        studio_tab="Worldbuilding",
    ),
}


def get_registry() -> Dict[str, EngineSpec]:
    """Return the global engine dictionary."""
    return _ENGINES


def get_engine(name: str) -> Optional[EngineSpec]:
    """Retrieve an engine specification by name or alias."""
    if name in _ENGINES:
        return _ENGINES[name]
    for spec in _ENGINES.values():
        if name in spec.aliases or name == spec.cli_command:
            return spec
    return None


def list_engines(category: Optional[EngineCategory] = None, enabled_only: bool = True) -> List[EngineSpec]:
    """List engine specifications matching optional category and enabled filter."""
    res = []
    for spec in _ENGINES.values():
        if category is not None and spec.category != category:
            continue
        if enabled_only and not spec.enabled:
            continue
        res.append(spec)
    return res


def get_core_engines(enabled_only: bool = True) -> List[EngineSpec]:
    """Return all core platform engines."""
    return list_engines(category=EngineCategory.CORE, enabled_only=enabled_only)


def get_craft_engines(enabled_only: bool = True) -> List[EngineSpec]:
    """Return all craft & specialized worldbuilding engines."""
    return list_engines(category=EngineCategory.CRAFT, enabled_only=enabled_only)


def is_engine_enabled(name: str) -> bool:
    """Check if an engine is enabled."""
    spec = get_engine(name)
    return spec.enabled if spec else False


def enable_engine(name: str) -> bool:
    """Enable a specific engine."""
    spec = get_engine(name)
    if spec:
        spec.enabled = True
        return True
    return False


def disable_engine(name: str) -> bool:
    """Disable a specific engine."""
    spec = get_engine(name)
    if spec:
        spec.enabled = False
        return True
    return False


def load_engine_module(name: str) -> Any:
    """Dynamically import and return the engine's Python module."""
    spec = get_engine(name)
    if not spec:
        raise ValueError(f"Unknown engine: '{name}'")
    return importlib.import_module(spec.module_name)
