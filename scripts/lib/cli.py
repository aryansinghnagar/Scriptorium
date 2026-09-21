#!/usr/bin/env python3
"""
Ars Arcanum Unified Python CLI Dispatcher (scripts/lib/cli.py)
=============================================================
Provides modular command parsing and delegation to core and craft engines.
"""

import argparse
import importlib
import os
from pathlib import Path
import sys
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VERSION = "1.6.0"

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def print_banner():
    banner = f"""Ars Arcanum Unified CLI — v{VERSION}
An intuitive, fail-safe Linux writing and worldbuilding studio.

Usage:
  arcanum <command> [arguments...]
  ars-arcanum <command> [arguments...]

✍️  Core Authoring & Editorial Craft:
  write [TARGET]               Open writing workspace in novelWriter or Obsidian
  docx <build|sync|import>     Manage Word .docx manuscript synchronization
  compare [MS] [D_NEW] [D_OLD] Visual Redline changelog comparison between drafts (alias: diff)
  preflight [MS]               Pre-flight typesetting & compliance validator (PUB-101)
  barcode <ISBN>               Generate publication-grade ISBN-13 vector SVG/PNG barcode
  matter build [MS]            Generate modular front matter and back matter files
  polish typography [TARGET]   Normalize smart curly quotes, em-dashes, and ellipses
  read [TARGET] [--speak|--html] Offline neural audio proofreading & WebAudio player
  concordance <TARGET> [-b]    Generate Dramatis Personae & Glossary back-matter
  pace [MS] [--pov|--html]     Analyze dialogue/action density & prose rhythm
  tension [MS] [--html]        Model chapter tension curve & narrative arcs
  plot [MS] [--html|--matrix]  Multi-track plot grid & subplot pacing matrix
  structure [MS] [-p PARADIGM] Story paradigm enforcer (3-Act, Save the Cat, Hero's Journey)
  ambient [PROFILE]            Focus noise & binaural beat synthesizer
  portfolio [DIR] [--html]     Multi-manuscript catalog dashboard & drafting velocity

🪐 Universe, World Lore & Series Continuity:
  world-doctor <WORLD>         Run deep World Bible lore consistency checks
  map <WORLD> [--html|--svg]   Interactive offline vector cartography & map viewer
  codex <WORLD> [--html]       Compile static offline World Wiki encyclopedia
  series [TARGET] [--html]     Multi-book series continuity & character trait ledger
  sim battle [options]         Turn-based tactical skirmish & battle simulator
  faction [WORLD] [--html]     Geopolitical relationship matrix & diplomatic paradoxes
  economy [WORLD] [-m MS]      Macroeconomic currencies, commodity baskets & PPP rates
  causality [WORLD] [MS]       Causal DAGs, time-travel loop & multiverse branching engine
  ecology [WORLD] [--html]     Trophic energy pyramids (10% rule) & bestiary food-web
  magic-check [-w W -m MS]     Verify hard magic system constraints & tier limits
  prophecy [WORLD] [-m MS]     Prophecy lifecycle clauses & fulfillment verification
  genealogy <House|Char>       Compile dynastic lineage trees & Mermaid flowcharts
  conlang <gen|mut|lex> <Lang> Conlang phonotactics, sound-law shift & lexicon
  cipher <encode|decode|runes> In-world ciphers, Vigenere, Atbash & phonetic runes
  calendar [WORLD] [--phases]  Planetary calendar arithmetic & multi-moon syzygy
  calc <astro|climate|journey> Astrophysics, climate, and journey calculator
  audit <voice|style|idioms>   Prose audits: dialogue, voice, style, senses, idioms

🩺 System Health & Registry:
  doctor [--report|--json]     Run unified health, toolchain diagnostics & triage bundle
  migrate <VAULT>              Upgrade older vaults to modern schema format
  engines [--craft|--core]     List all registered core and craft engine plugins
"""
    print(banner)


def dispatch_subcommand(module_name: str, argv: List[str]) -> int:
    """Dynamically load module and run its main() function."""
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            return mod.main(argv) or 0
        else:
            print(f"Error: Engine '{module_name}' does not expose main()", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error executing '{module_name}': {e}", file=sys.stderr)
        return 1


def handle_engines_command(argv: List[str]) -> int:
    from lib.registry import get_core_engines, get_craft_engines, list_engines, EngineCategory
    category = None
    if "--core" in argv:
        category = EngineCategory.CORE
    elif "--craft" in argv:
        category = EngineCategory.CRAFT

    engines = list_engines(category=category)
    print(f"Ars Arcanum Registered Plugins & Engines ({len(engines)} total):\n")
    print(f"{'Category':<10} {'Name':<22} {'Command':<18} {'Title / Description'}")
    print("-" * 80)
    for eng in sorted(engines, key=lambda e: (e.category.value, e.name)):
        cat_badge = f"[{eng.category.value.upper()}]"
        print(f"{cat_badge:<10} {eng.name:<22} {eng.cli_command:<18} {eng.title}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help", "help"):
        print_banner()
        return 0

    if argv[0] in ("-v", "--version", "version"):
        print(f"Ars Arcanum v{VERSION}")
        return 0

    cmd = argv[0]
    rest = argv[1:]

    # Direct command dispatch routing
    if cmd in ("doctor", "check", "diagnostics"):
        return dispatch_subcommand("lib.diagnostics", rest)

    if cmd in ("world-doctor", "doctor-world"):
        return dispatch_subcommand("lib.world_doctor", rest)

    if cmd in ("concordance",):
        return dispatch_subcommand("lib.concordance", rest)

    if cmd in ("migrate", "upgrade"):
        return dispatch_subcommand("lib.migrate", rest)

    if cmd in ("barcode", "isbn"):
        return dispatch_subcommand("lib.barcode", rest)

    if cmd in ("preflight",):
        return dispatch_subcommand("lib.preflight", rest)

    if cmd in ("matter",):
        return dispatch_subcommand("lib.frontmatter_builder", rest)

    if cmd in ("compare", "diff", "redline"):
        return dispatch_subcommand("lib.manuscript_diff", rest)

    if cmd in ("read", "tts"):
        return dispatch_subcommand("lib.tts_reader", rest)

    if cmd in ("polish",):
        if rest and rest[0] == "typography":
            return dispatch_subcommand("lib.typography_cleaner", rest[1:])
        return dispatch_subcommand("lib.typography_cleaner", rest)

    if cmd in ("pace", "pacing"):
        return dispatch_subcommand("lib.pacing", rest)

    if cmd in ("tension", "scene"):
        return dispatch_subcommand("lib.scene_mechanics", rest)

    if cmd in ("plot", "matrix"):
        return dispatch_subcommand("lib.plot_matrix", rest)

    if cmd in ("structure", "beats"):
        return dispatch_subcommand("lib.structure", rest)

    if cmd in ("ambient", "focus"):
        return dispatch_subcommand("lib.ambient", rest)

    if cmd in ("portfolio", "catalog"):
        return dispatch_subcommand("lib.portfolio", rest)

    if cmd in ("map", "cartography"):
        return dispatch_subcommand("lib.cartography", rest)

    if cmd in ("codex", "wiki"):
        return dispatch_subcommand("lib.codex_export", rest)

    if cmd in ("series",):
        return dispatch_subcommand("lib.series_continuity", rest)

    if cmd in ("sim", "battle"):
        if rest and rest[0] == "battle":
            return dispatch_subcommand("lib.tactical_sim", rest[1:])
        return dispatch_subcommand("lib.tactical_sim", rest)

    if cmd in ("faction", "factions"):
        return dispatch_subcommand("lib.factions", rest)

    if cmd in ("economy", "currencies"):
        return dispatch_subcommand("lib.economy", rest)

    if cmd in ("causality", "timeline"):
        return dispatch_subcommand("lib.causality", rest)

    if cmd in ("ecology", "foodweb"):
        return dispatch_subcommand("lib.ecology", rest)

    if cmd in ("magic", "magic-check", "magic-report"):
        return dispatch_subcommand("lib.magic_system", rest)

    if cmd in ("prophecy", "prophecies"):
        return dispatch_subcommand("lib.prophecy", rest)

    if cmd in ("genealogy", "lineage"):
        return dispatch_subcommand("lib.genealogy", rest)

    if cmd in ("conlang", "lexicon"):
        return dispatch_subcommand("lib.conlang", rest)

    if cmd in ("cipher", "runes"):
        return dispatch_subcommand("lib.cipher", rest)

    if cmd in ("calendar", "moons"):
        return dispatch_subcommand("lib.calendar", rest)

    if cmd in ("docx",):
        return dispatch_subcommand("lib.docx_sync", rest)

    if cmd in ("engines", "plugins"):
        return handle_engines_command(rest)

    if cmd in ("calc",):
        if rest and rest[0] in ("astro", "astrophysics"):
            return dispatch_subcommand("lib.astrophysics", rest[1:])
        if rest and rest[0] in ("climate", "weather"):
            return dispatch_subcommand("lib.climate", rest[1:])
        if rest and rest[0] in ("journey", "logistics"):
            return dispatch_subcommand("lib.journey", rest[1:])
        if rest and rest[0] in ("battle", "sim"):
            return dispatch_subcommand("lib.tactical_sim", rest[1:])
        print("Usage: arcanum calc <astro|climate|journey|battle> [args...]", file=sys.stderr)
        return 2

    if cmd in ("audit",):
        if rest and rest[0] in ("voice",):
            return dispatch_subcommand("lib.voice", rest[1:])
        if rest and rest[0] in ("style", "stylistics"):
            return dispatch_subcommand("lib.stylistics", rest[1:])
        if rest and rest[0] in ("idioms",):
            return dispatch_subcommand("lib.idioms", rest[1:])
        if rest and rest[0] in ("senses",):
            return dispatch_subcommand("lib.senses", rest[1:])
        if rest and rest[0] in ("scenes", "tension"):
            return dispatch_subcommand("lib.scene_mechanics", rest[1:])
        print("Usage: arcanum audit <voice|style|idioms|senses|scenes> [args...]", file=sys.stderr)
        return 2

    print(f"Error: Unknown command '{cmd}'. Type 'arcanum --help' for available commands.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
