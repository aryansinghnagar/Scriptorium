#!/usr/bin/env python3
"""
Ars Arcanum Unified Python CLI Dispatcher (scripts/lib/cli.py)
=============================================================
Provides modular command parsing, alias routing, and delegation to core and craft engines.
"""

import difflib
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VERSION = "4.0.0"

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent if SCRIPTS_DIR.name == "scripts" else SCRIPTS_DIR
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def print_banner():
    banner = f"""Ars Arcanum Unified CLI — v{VERSION}
An intuitive, fail-safe Linux writing and worldbuilding studio.

Usage:
  arcanum <command> [arguments...]
  ars-arcanum <command> [arguments...]

✍️  Core Authoring & Editorial Craft:
  hub [TARGET] [--port PORT]   Launch Sovereign Studio Desktop Hub & Telemetry Dashboard
  write [TARGET]               Open writing workspace in novelWriter or Obsidian (alias: open)
  studio [MS] [-w WORLD]       Standalone offline Zen drafting studio & in-situ lore drawer
  word [MS]                    Open manuscript in Microsoft Word / LibreOffice (alias: writer)
  docx <build|sync|import|open> Manage Word .docx manuscript synchronization
  new <type> <NAME> [opts]     Scaffold new project (type: manuscript | draft | world | universe | volume)
  draft <MS> [DRAFT_NAME]      Fork next manuscript draft version (alias: new draft, init-draft)
  compare <MS> [D_NEW] [D_OLD] Visual Redline changelog comparison between drafts (alias: diff, redline)
  save [TARGET] [-m "note"]    Save an instant Git version milestone (alias: snapshot)
  publish [MS] [options]       Compile to print PDF, EPUB, or DOCX (alias: export, compile)
  preflight [MS]               Pre-flight typesetting & compliance validator (PUB-101)
  matter build [MS]            Generate modular front matter and back matter files (PUB-103)
  query [MS]                   Scaffold submission package: query letter, synopsis, tracker (PUB-106)
  polish typography [TARGET]   Normalize smart curly quotes, em-dashes, and ellipses (PRO-104)
  rag <QUERY> [opts]           Sovereign local semantic retrieval & LLM context synthesis (alias: query-lore)
  branch <TARGET> [opts]       Multi-POV narrative thread & convergence subway map (PLT-103)
  words [MS] [--md|--json|--pov] Show live word counts and chapter analytics (alias: report, count)
  pace [MS] [--pov|--html]     Analyze dialogue/action density & prose rhythm
  tension [MS] [--html]        Model chapter tension curve & narrative arcs
  plot [MS] [--html|--matrix]  Multi-track plot grid & subplot pacing matrix (PLT-101)
  structure [MS] [-p PARADIGM] Story paradigm enforcer: 3-Act, 8-Sequence, Kishotenketsu (PLT-102)
  canvas [MS] [--html|--json]  Interactive visual story canvas & corkboard drag-and-drop
  timeline [MS|WORLD] [--html] Dual-track chronological vs narrative timeline synchronizer
  omnibus <UNIVERSE> [--html]  Compile multi-volume series omnibus with unified lore
  corpus <TARGET> [-f FORMAT]  Universal structured JSONL, SQLite & RAG dataset exporter
  ambient [PROFILE]            Focus soundscape loop player (PLT-106)
  portfolio [DIR] [--html]     Multi-manuscript catalog dashboard & drafting velocity (OPS-103)
  package [MS] [-t TARGET]     Multi-platform release packager: Reader, Submission, ARC (OPS-101)
  sprint [MS]                  Sovereign writing sprint timer & productivity analytics
  revision-heatmap [MS]        Manuscript revision density & churn heatmap

🪐 Universe, World Lore & Series Continuity:
  universe [NAME] [--list]     Create or list narrative universes in ~/Universes/
  world <NAME> [-u UNIVERSE]   Scaffold an Obsidian World Lore Vault
  cast [UNIVERSE] [--html|--md] Multi-volume Dramatis Personae & Universe Cast Matrix (alias: dramatis-personae)
  map <WORLD> [--html|--svg]   Interactive offline vector cartography & map editor (WOR-101)
  codex <WORLD> [--html]       Compile static offline World Wiki encyclopedia (WOR-102)
  series [TARGET] [--html]     Multi-book series continuity & character trait ledger (WOR-103)
  sim battle [options]         High-level tactical battle scenario planner (WOR-104)
  concordance <TARGET> [-b]    Generate Dramatis Personae & Glossary back-matter
  continuity [-w W -m MS]      Analyze character traits & narrative consistency (alias: check-continuity)
  faction [WORLD] [--html]     Geopolitical relationship matrix & diplomatic paradoxes
  economy [WORLD] [-m MS]      Macroeconomic currencies, commodity baskets & PPP rates
  causality [WORLD] [MS]       Multi-paradigm causal DAGs & time-travel validator
  ecology [WORLD] [--html]     Trophic energy pyramids (10% rule) & bestiary food-web
  magic-check [-w W -m MS]     Verify hard magic system constraints & axioms (advisory)
  magic-report [-w W]          Export comprehensive arcane constraint report
  prophecy [WORLD] [-m MS]     Prophecy lifecycle clauses & fulfillment verification
  genealogy <House|Char>       Compile dynastic lineage trees & Mermaid flowcharts
  lineage <House>              Display succession rank roster & claimants
  conlang <gen|mut|lex> <Lang> Conlang phonotactics, sound-law shift & lexicon
  calendar [WORLD] [--phases]  Multi-calendar/multi-era invariant chronology & arithmetic
  calc <subcommand>            Astrophysics, climate, battle, logistics & journey calculator
  audit <subcommand>           Prose audits: dialogue, echoes, voice, scenes, structure, tech, idioms, senses

🔒 Data Protection & Safety:
  backup <TARGET> [options]    Create a verified, standalone .tar.gz backup archive
  backup-dest <get|set|clear>  Configure secure secondary backup destination (alias: config backup-dest)
  restore <ARCHIVE> [options]  Restore a project from a verified backup archive

🩺 System Health & Tools:
  doctor [options]             Run unified health & toolchain diagnostics (alias: check)
  world-doctor <WORLD> [opts]  Run deep World Bible lore consistency checks
  cache <scan|wordcounts|clear> Manage mtime-keyed fast performance cache
  gui [--tab TAB]              Launch desktop Control Center (aliases: app, control-center)
  menu                         Launch interactive numbered terminal dashboard (alias: interactive)
  verify                       Run canonical 7-stage test harness
  setup [--dry-run]            Install core packages, typography fonts, and launchers
  uninstall [--dry-run]        Revert desktop launchers and system components

Global Options:
  -v, --version                Display Ars Arcanum version
  -h, --help                   Display this help menu
"""
    print(banner)


def dispatch_subcommand(module_name: str, argv: list[str]) -> int:
    """Dynamically load module and run its main() function."""
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            old_argv = sys.argv
            sys.argv = [module_name, *argv]
            try:
                import inspect
                sig = inspect.signature(mod.main)
                res = mod.main(argv) if len(sig.parameters) > 0 else mod.main()
                return int(res) if res is not None and isinstance(res, (int, bool)) else 0
            finally:
                sys.argv = old_argv
        else:
            print(f"Error: Engine '{module_name}' does not expose main()", file=sys.stderr)
            return 1
    except SystemExit as se:
        return int(se.code) if se.code is not None and isinstance(se.code, int) else 0
    except Exception as e:
        print(f"Error executing '{module_name}': {e}", file=sys.stderr)
        return 1


def dispatch_script(script_name: str, argv: list[str]) -> int:
    """Dispatches a standalone script (Python or Bash)."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.is_file():
        script_path = PROJECT_ROOT / "scripts" / script_name
    if not script_path.is_file():
        print(f"Error: Script '{script_name}' not found.", file=sys.stderr)
        return 1

    if script_name.endswith(".py"):
        cmd = [sys.executable, str(script_path), *argv]
    else:
        # Bash script: find working bash executable on Windows or POSIX
        bash_exe = None
        if sys.platform == "win32":
            for c in [
                r"C:\Program Files\Git\bin\bash.exe",
                r"C:\Program Files\Git\usr\bin\bash.exe",
                r"C:\Program Files (x86)\Git\bin\bash.exe",
                shutil.which("bash"),
            ]:
                if c and os.path.isfile(c):
                    bash_exe = c
                    break
        bash_cmd = bash_exe or shutil.which("bash") or "bash"
        cmd = [bash_cmd, script_path.as_posix(), *argv]

    try:
        proc = subprocess.run(cmd)
        return proc.returncode
    except Exception as e:
        print(f"Error running '{script_name}': {e}", file=sys.stderr)
        return 1


def handle_engines_command(argv: list[str]) -> int:
    from lib.registry import EngineCategory, list_engines
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


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help", "help"):
        print_banner()
        return 0

    if argv[0] in ("-v", "--version", "version"):
        print(f"Ars Arcanum v{VERSION}")
        return 0

    cmd = argv[0].lower().strip()
    rest = argv[1:]

    # --- Core Authoring & Editorial Craft ---
    if cmd in ("write", "open"):
        return dispatch_script("lib/ui_controller.py", rest)

    if cmd in ("word", "writer", "word-processor"):
        return dispatch_subcommand("lib.docx_sync", ["open", *rest])

    if cmd in ("docx", "docx-sync", "sync-docx"):
        return dispatch_subcommand("lib.docx_sync", rest)

    if cmd in ("new", "create"):
        if not rest:
            print("Usage: arcanum new <manuscript|draft|world|universe|volume> <NAME> [options]", file=sys.stderr)
            return 2
        sub_type = rest[0].lower()
        sub_args = rest[1:]
        if sub_type in ("manuscript", "novel", "book"):
            return dispatch_script("arcanum", ["new", "manuscript", *sub_args])
        elif sub_type in ("draft", "revision"):
            return dispatch_script("arcanum", ["draft", *sub_args])
        elif sub_type in ("world", "lore", "vault"):
            return dispatch_script("arcanum", ["new", "world", *sub_args])
        elif sub_type in ("universe", "cosmos"):
            return dispatch_script("arcanum", ["new", "universe", *sub_args])
        elif sub_type in ("volume", "book-volume"):
            return dispatch_script("arcanum", ["add-volume", *sub_args])
        else:
            print(f"Unknown project type '{sub_type}'. Choose: manuscript, draft, world, universe, volume.", file=sys.stderr)
            return 2

    if cmd in ("draft", "drafts", "init-draft", "new-draft", "revision"):
        return dispatch_script("arcanum", ["draft", *rest])

    if cmd in ("compare", "diff", "redline", "changelog"):
        return dispatch_script("arcanum", ["compare", *rest])

    if cmd in ("save", "snapshot", "snap", "commit"):
        return dispatch_script("arcanum", ["snapshot", *rest])

    if cmd in ("publish", "export", "compile"):
        return dispatch_script("arcanum", ["export", *rest])

    if cmd in ("preflight", "pre-flight"):
        return dispatch_subcommand("lib.preflight", rest)

    if cmd in ("matter", "frontmatter", "backmatter"):
        if rest and rest[0] == "build":
            return dispatch_subcommand("lib.frontmatter_builder", rest)
        return dispatch_subcommand("lib.frontmatter_builder", ["build", *rest])

    if cmd in ("query", "synopsis", "agent"):
        return dispatch_script("init_query.py", rest)

    if cmd in ("polish", "clean-typography"):
        if rest and rest[0] == "typography":
            return dispatch_subcommand("lib.typography_cleaner", rest[1:])
        return dispatch_subcommand("lib.typography_cleaner", rest)

    if cmd in ("studio", "zen", "zen-studio", "editor"):
        return dispatch_subcommand("lib.zen_studio", rest)

    if cmd in ("corpus", "corpus-export", "export-corpus", "rag-export", "corpus-restore"):
        return dispatch_subcommand("lib.corpus_export", rest)

    if cmd in ("rag", "query-lore", "semantic-search", "lore-query"):
        return dispatch_subcommand("lib.local_rag", rest)

    if cmd in ("branch", "branching", "gamebook", "interactive-fiction", "branch-graph", "subway-map"):
        return dispatch_subcommand("lib.branching_graph", rest)

    if cmd in ("hub", "dashboard", "gui-web", "studio-hub"):
        return dispatch_subcommand("lib.studio_hub", rest)

    if cmd in ("causality", "causal", "time-travel", "ctc", "multiverse"):
        return dispatch_subcommand("lib.causality", rest)

    if cmd in ("prophecy", "oracle", "arcane-inscription", "prophecy-matrix"):
        return dispatch_subcommand("lib.prophecy", rest)

    if cmd in ("senses", "sensory", "immersion", "white-room"):
        return dispatch_subcommand("lib.senses", rest)

    if cmd in ("sprint", "writing-sprint", "pomodoro", "session"):
        return dispatch_subcommand("lib.writing_sprint", rest)

    if cmd in ("revision-heatmap", "churn", "revision-density", "draft-churn"):
        return dispatch_subcommand("lib.revision_heatmap", rest)

    if cmd in ("words", "wordcount", "report", "count", "stats"):
        return dispatch_script("arcanum", ["words", *rest])

    if cmd in ("pace", "pacing"):
        return dispatch_subcommand("lib.pacing", ["pace", *rest] if not (rest and rest[0] in ("pace", "tension", "pov")) else rest)

    if cmd in ("tension", "tension-arc"):
        return dispatch_subcommand("lib.pacing", ["tension", *rest] if not (rest and rest[0] in ("pace", "tension", "pov")) else rest)

    if cmd in ("plot", "plot-matrix", "subplot"):
        return dispatch_subcommand("lib.plot_matrix", rest)

    if cmd in ("structure", "beats", "paradigm"):
        return dispatch_subcommand("lib.structure", rest)

    if cmd in ("canvas", "corkboard", "story-map", "story-canvas"):
        return dispatch_subcommand("lib.story_canvas", rest)

    if cmd in ("timeline", "timeline-sync", "sync-timeline"):
        return dispatch_subcommand("lib.timeline_sync", rest)

    if cmd in ("omnibus", "compile-omnibus", "series-omnibus"):
        return dispatch_subcommand("lib.omnibus", rest)

    if cmd in ("ambient", "soundscape", "noise", "focus"):
        if rest and rest[0] == "generate":
            return dispatch_subcommand("lib.ambient", rest)
        return dispatch_subcommand("lib.ambient", ["generate", *rest])

    if cmd in ("portfolio", "catalog"):
        return dispatch_subcommand("lib.portfolio", rest)

    if cmd in ("package", "dist", "bundle"):
        return dispatch_script("package_distribution.py", rest)

    # --- Universe, World Lore & Series Continuity ---
    if cmd in ("universe", "init-universe", "cosmos"):
        return dispatch_script("arcanum", ["universe", *rest])

    if cmd in ("world", "init-world"):
        return dispatch_script("arcanum", ["world", *rest])

    if cmd in ("manuscript", "init-manuscript", "novel"):
        return dispatch_script("arcanum", ["manuscript", *rest])

    if cmd in ("volume", "add-volume", "add-book", "new-book"):
        return dispatch_script("arcanum", ["add-volume", *rest])

    if cmd in ("map", "cartography"):
        return dispatch_subcommand("lib.cartography", rest)

    if cmd in ("codex", "wiki"):
        return dispatch_subcommand("lib.codex_export", rest)

    if cmd in ("series", "series-continuity"):
        return dispatch_subcommand("lib.series_continuity", rest)

    if cmd in ("sim", "tactical-sim"):
        if rest and rest[0] == "battle":
            return dispatch_subcommand("lib.tactical_sim", ["sim", *rest[1:]])
        return dispatch_subcommand("lib.tactical_sim", rest)

    if cmd in ("cast", "dramatis-personae", "dramatis", "characters-cast"):
        return dispatch_subcommand("lib.dramatis_personae", rest)

    if cmd in ("concordance", "glossary"):
        return dispatch_subcommand("lib.concordance", rest)

    if cmd in ("continuity", "check-continuity"):
        return dispatch_subcommand("lib.series_continuity", rest)

    if cmd in ("faction", "factions"):
        return dispatch_subcommand("lib.factions", rest)

    if cmd in ("economy", "currencies"):
        return dispatch_subcommand("lib.economy", rest)

    if cmd in ("causality", "timeline"):
        return dispatch_subcommand("lib.causality", rest)

    if cmd in ("ecology", "foodweb"):
        return dispatch_subcommand("lib.ecology", rest)

    if cmd in ("magic", "magic-check"):
        if rest and rest[0] in ("check", "report"):
            return dispatch_subcommand("lib.magic_system", rest)
        return dispatch_subcommand("lib.magic_system", ["check", *rest])

    if cmd == "magic-report":
        return dispatch_subcommand("lib.magic_system", ["report", *rest])

    if cmd in ("prophecy", "prophecies"):
        return dispatch_subcommand("lib.prophecy", rest)

    if cmd == "genealogy":
        return dispatch_subcommand("lib.genealogy", rest)

    if cmd == "lineage":
        return dispatch_subcommand("lib.genealogy", ["lineage", *rest])

    if cmd in ("conlang", "lexicon"):
        return dispatch_subcommand("lib.conlang", rest)


    if cmd in ("calendar", "moons"):
        return dispatch_subcommand("lib.calendar", rest)

    if cmd in ("calc", "calculator"):
        if not rest:
            print("Usage: arcanum calc <transit|time-dilation|orbit|comms|journey|battle|logistics|climate|trade> [args...]", file=sys.stderr)
            return 2
        sub = rest[0].lower()
        sub_args = rest[1:]
        if sub in ("transit", "time-dilation", "orbit", "comms", "habitability", "astro", "astrophysics"):
            if sub in ("astro", "astrophysics"):
                return dispatch_subcommand("lib.astrophysics", sub_args)
            return dispatch_subcommand("lib.astrophysics", [sub, *sub_args])
        elif sub in ("journey", "expedition"):
            return dispatch_subcommand("lib.journey", sub_args)
        elif sub in ("battle", "sim", "tactical"):
            return dispatch_subcommand("lib.tactical_sim", ["sim", *sub_args])
        elif sub in ("logistics", "supply"):
            return dispatch_subcommand("lib.factions", ["logistics", *sub_args])
        elif sub in ("climate", "weather", "insolation"):
            return dispatch_subcommand("lib.climate", sub_args)
        elif sub in ("trade", "arbitrage", "ppp"):
            return dispatch_subcommand("lib.economy", ["trade", *sub_args])
        else:
            print(f"Unknown calc mode '{sub}'. Choose: transit, time-dilation, orbit, comms, journey, battle, logistics, climate, trade.", file=sys.stderr)
            return 2

    if cmd == "audit":
        if not rest:
            return dispatch_script("arcanum_doctor.sh", [])
        sub = rest[0].lower()
        sub_args = rest[1:]
        if sub in ("dialogue", "tags", "said-bookisms"):
            return dispatch_subcommand("lib.stylistics", ["dialogue", *sub_args])
        elif sub in ("echoes", "echo", "repetition"):
            return dispatch_subcommand("lib.stylistics", ["echoes", *sub_args])
        elif sub in ("rhythm", "readability"):
            return dispatch_subcommand("lib.stylistics", ["rhythm", *sub_args])
        elif sub in ("prose", "style", "stylistics"):
            return dispatch_subcommand("lib.stylistics", ["scan", *sub_args])
        elif sub in ("voice", "voice-bleed"):
            return dispatch_subcommand("lib.voice", sub_args)
        elif sub in ("scenes", "scene", "mru"):
            return dispatch_subcommand("lib.scene_mechanics", sub_args)
        elif sub in ("structure", "paradigm"):
            return dispatch_subcommand("lib.structure", sub_args)
        elif sub in ("idioms", "idiom", "eponyms"):
            return dispatch_subcommand("lib.stylistics", ["idiom", *sub_args])
        elif sub in ("senses", "sensory", "palette"):
            return dispatch_subcommand("lib.senses", sub_args)
        elif sub in ("tech", "technology", "anachronisms"):
            return dispatch_subcommand("lib.economy", ["tech", *sub_args])
        else:
            return dispatch_subcommand("lib.diagnostics", rest)

    # --- Data Protection & Safety ---
    if cmd in ("backup", "backup-world"):
        return dispatch_script("arcanum", ["backup", *rest])

    if cmd in ("backup-dest", "backup-destination"):
        return dispatch_subcommand("lib.config", ["backup-dest", *rest])

    if cmd in ("config", "settings", "preferences"):
        return dispatch_subcommand("lib.config", rest)

    if cmd in ("restore", "restore-world"):
        return dispatch_script("arcanum", ["restore", *rest])

    # --- System Health & Diagnostics ---
    if cmd in ("doctor", "check", "diagnostics"):
        return dispatch_subcommand("lib.diagnostics", rest)

    if cmd in ("world-doctor", "doctor-world"):
        return dispatch_subcommand("lib.world_doctor", rest)

    if cmd in ("cache", "cache-engine"):
        return dispatch_subcommand("lib.cache", rest)

    if cmd == "cache-clear":
        return dispatch_subcommand("lib.cache", ["clear", *rest])

    if cmd == "cache-scan":
        return dispatch_subcommand("lib.cache", ["scan", *rest])

    if cmd in ("migrate", "upgrade"):
        return dispatch_subcommand("lib.migrate", rest)


    if cmd == "engines":
        return handle_engines_command(rest)

    if cmd in ("gui", "control-center", "app", "ui"):
        return dispatch_script("arcanum_app.py", rest)

    if cmd in ("menu", "interactive", "dashboard-cli"):
        return dispatch_script("arcanum", ["menu", *rest])

    if cmd in ("verify", "test", "tests"):
        return dispatch_script("verify.sh", rest)

    if cmd == "setup":
        return dispatch_script("setup_arcanum.sh", rest)

    known_commands = [
        "write", "open", "new", "create", "save", "snapshot", "publish", "export",
        "preflight", "matter", "query", "polish", "typography",
        "plot", "structure", "ambient", "portfolio", "package", "map", "codex",
        "series", "sim", "draft", "drafts", "compare", "diff", "redline", "changelog",
        "words", "count", "report", "universe", "world", "manuscript", "volume",
        "add-volume", "concordance", "continuity", "check-continuity", "doctor",
        "check", "world-doctor", "backup", "backup-dest", "config", "restore", "cache",
        "calc", "magic-check", "magic-report", "genealogy", "lineage", "conlang",
        "faction", "economy", "causality", "causal", "time-travel", "ecology",
        "climate", "idioms", "senses", "sensory", "immersion",
        "prophecy", "oracle", "audit", "pace", "tension", "voice", "calendar", "journey",
        "gui", "control-center", "menu", "interactive", "verify", "setup", "uninstall",
        "version", "help", "docx", "word", "corpus", "studio", "zen",
        "rag", "query-lore", "branch", "branching",
        "hub", "dashboard", "gui-web", "studio-hub",
        "sprint", "writing-sprint", "revision-heatmap", "churn", "revision-density",
        "cast", "dramatis-personae", "dramatis", "characters-cast",
    ]

    matches = difflib.get_close_matches(cmd, known_commands, n=1, cutoff=0.55)
    if matches:
        print(f"Error: Unknown command '{cmd}'. Did you mean '{matches[0]}'?", file=sys.stderr)
    else:
        print(f"Error: Unknown command '{cmd}'.", file=sys.stderr)
    print("Run 'arcanum --help' for available commands and examples.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())


