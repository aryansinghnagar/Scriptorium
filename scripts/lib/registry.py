#!/usr/bin/env python3
"""
Ars Arcanum Engine & Plugin Registry (scripts/lib/registry.py)
============================================================
Defines core vs craft engine classification, metadata registry, dynamic plugin
discovery, and capability introspection across CLI and GUI surfaces.
"""

import importlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EngineCategory(str, Enum):
    CORE = "core"
    CRAFT = "craft"
    UTILITY = "utility"


@dataclass
class AdvisoryResolution:
    """Creative resolution pathway for an advisory pattern."""
    mode: str  # "Hard Realism", "Speculative / Trope", "Creative Sovereignty"
    description: str


@dataclass
class EngineSpec:
    """Metadata specification for an Ars Arcanum engine / plugin module."""
    name: str
    category: EngineCategory
    title: str
    description: str
    module_name: str
    cli_command: str
    aliases: list[str] = field(default_factory=list)
    studio_tab: str | None = None
    default_enabled: bool = True
    enabled: bool = True
    logic_documentation: str = ""
    worldbuilding_relevance: str = ""
    storytelling_relevance: str = ""
    writing_relevance: str = ""
    advisory_guidance: list[dict[str, Any]] = field(default_factory=list)


# Canonical Engine Registry Definitions
_ENGINES: dict[str, EngineSpec] = {
    # --- Core Authoring, Diagnostics, & Pipeline ---
    "config": EngineSpec(
        name="config",
        category=EngineCategory.CORE,
        title="Project Configuration",
        description="Global and local workspace configuration, paths, and preferences",
        module_name="lib.config",
        cli_command="config",
        studio_tab="Tools",
        logic_documentation="Manages JSON/YAML workspace configurations, environment overrides, and secure backup destinations using atomic file operations.",
        worldbuilding_relevance="Stores default world vault paths, cosmological constants, and universe-level preferences.",
        storytelling_relevance="Configures target word count milestones, chapter formatting templates, and paradigm defaults.",
        writing_relevance="Customizes UI fonts, dark/sepia themes, and export directories.",
        advisory_guidance=[
            {"pattern": "Missing configuration key", "option_a": "Generate default configuration file", "option_b": "Inherit global environment variable", "option_c": "Use ephemeral in-memory fallback"},
        ],
    ),
    "cache": EngineSpec(
        name="cache",
        category=EngineCategory.CORE,
        title="Performance Cache",
        description="Fast mtime-keyed in-memory index for lore vaults and manuscripts",
        module_name="lib.cache",
        cli_command="cache",
        studio_tab="Tools",
        logic_documentation="Caches parsed markdown ASTs, word counts, and wikilink graphs using file modification timestamps (mtime) and SHA-256 digests for sub-millisecond query performance.",
        worldbuilding_relevance="Enables instantaneous searching across thousands of world lore entities without re-parsing disk files.",
        storytelling_relevance="Provides live, lag-free structural word counts and chapter analytics across multi-volume series.",
        writing_relevance="Maintains background typing speed without UI stuttering.",
        advisory_guidance=[
            {"pattern": "Stale cache detected", "option_a": "Trigger automatic cache invalidation on next read", "option_b": "Run background asynchronous cache refresh", "option_c": "Bypass cache with direct disk read"},
        ],
    ),
    "fs_utils": EngineSpec(
        name="fs_utils",
        category=EngineCategory.CORE,
        title="Atomic File System",
        description="Crash-safe atomic writes and storage operations",
        module_name="lib.fs_utils",
        cli_command="fs",
        studio_tab="Tools",
        logic_documentation="Guarantees zero data loss using POSIX atomic writes (temp file -> flush -> fsync -> os.replace -> parent dir fsync) with cross-platform file locking.",
        worldbuilding_relevance="Protects irreplaceable creative world lore against power cuts or sudden crashes.",
        storytelling_relevance="Safeguards manuscript drafts, version forks, and chapter re-orderings.",
        writing_relevance="Ensures every keystroke and autosave is durable on disk.",
        advisory_guidance=[
            {"pattern": "File lock contention", "option_a": "Wait with exponential backoff", "option_b": "Create conflict branch file (e.g. Chapter_conflict_2026.md)", "option_c": "Prompt user for manual lock override"},
        ],
    ),
    "migrate": EngineSpec(
        name="migrate",
        category=EngineCategory.CORE,
        title="Vault Migration",
        description="Schema upgrade engine for migrating older lore vaults and projects",
        module_name="lib.migrate",
        cli_command="migrate",
        aliases=["upgrade"],
        studio_tab="Tools",
        logic_documentation="Upgrades legacy Obsidian vaults, frontmatter schemas, and manuscript folders to current Ars Arcanum standards with zero data destruction.",
        worldbuilding_relevance="Preserves historical world lore notes across multi-year writing projects.",
        storytelling_relevance="Updates legacy chapter header formats to modern novelWriter / Markdown standards.",
        writing_relevance="Enables seamless project modernization without manual file editing.",
        advisory_guidance=[
            {"pattern": "Unrecognized legacy frontmatter", "option_a": "Migrate to standard YAML frontmatter schema", "option_b": "Preserve unmapped keys under custom_attributes", "option_c": "Leave legacy file untouched in archival branch"},
        ],
    ),
    "docx_sync": EngineSpec(
        name="docx_sync",
        category=EngineCategory.CORE,
        title="DOCX Bidirectional Sync",
        description="Three-way content hash sync with conflict branching for Microsoft Word / LibreOffice",
        module_name="lib.docx_sync",
        cli_command="docx",
        aliases=["word", "writer"],
        studio_tab="Editor",
        logic_documentation="Parses OpenXML ZIP/XML structures to bidirectionally synchronize Markdown manuscript chapters with Microsoft Word (.docx) documents, preserving formatting and comments.",
        worldbuilding_relevance="Allows non-technical collaborators to review world glossaries in Word.",
        storytelling_relevance="Enables round-trip editorial workflow with professional editors using Word Track Changes.",
        writing_relevance="Allows drafting in LibreOffice or Word while retaining Markdown canonical source of truth.",
        advisory_guidance=[
            {"pattern": "Simultaneous edit conflict in MD and DOCX", "option_a": "Branch into conflict file for manual side-by-side review", "option_b": "Prefer Markdown version as canonical source", "option_c": "Prefer DOCX version with Track Changes preserved"},
        ],
    ),
    "preflight": EngineSpec(
        name="preflight",
        category=EngineCategory.CORE,
        title="Typesetting Preflight Validator",
        description="Print-PDF compliance, image resolution, and trim size validation",
        module_name="lib.preflight",
        cli_command="preflight",
        aliases=["pre-flight"],
        studio_tab="Publishing",
        logic_documentation="Validates print-on-demand requirements (Amazon KDP, IngramSpark), spine width calculation based on page count and paper thickness, bleed margins, font embedding, and image DPI.",
        worldbuilding_relevance="Verifies world map image resolutions for crisp 300+ DPI print reproduction.",
        storytelling_relevance="Calculates final physical book thickness, signature layouts, and spine text fitting.",
        writing_relevance="Catches widow/orphan lines, bad page breaks, and unlinked footnotes before print submission.",
        advisory_guidance=[
            {"pattern": "Page count not multiple of 4/6 (POD signature)", "option_a": "Add blank backmatter note pages to round up", "option_b": "Adjust font leading / margins slightly", "option_c": "Proceed with printer automatic blank insertion"},
        ],
    ),
    "frontmatter_builder": EngineSpec(
        name="frontmatter_builder",
        category=EngineCategory.CORE,
        title="Frontmatter & Backmatter Builder",
        description="Generates copyright, dedication, epigraph, and biographical matter",
        module_name="lib.frontmatter_builder",
        cli_command="matter",
        aliases=["frontmatter", "backmatter"],
        studio_tab="Publishing",
        logic_documentation="Scaffolds modular frontmatter (half-title, title page, copyright notice, dedication, epigraph, table of contents) and backmatter (about author, teaser chapters, discussion questions).",
        worldbuilding_relevance="Injects in-universe historical quotes and epigraphs to enrich cosmological lore.",
        storytelling_relevance="Provides structural framing and thematic epigraphs that set chapter tone.",
        writing_relevance="Automates legal copyright notices, CIP data, and acknowledgments.",
        advisory_guidance=[
            {"pattern": "Missing copyright year or ISBN", "option_a": "Scaffold default copyright with current year", "option_b": "Insert placeholder ISBN for proof review", "option_c": "Leave blank for public domain / draft distribution"},
        ],
    ),
    "manuscript_diff": EngineSpec(
        name="manuscript_diff",
        category=EngineCategory.CORE,
        title="Draft Diff & Visual Redline",
        description="Comparative redline changelog and visual diffs between manuscript drafts",
        module_name="lib.manuscript_diff",
        cli_command="compare",
        aliases=["diff", "redline", "changelog"],
        studio_tab="Editor",
        logic_documentation="Computes Myers semantic diff algorithms between draft iterations (Draft-01 vs Draft-02), isolating word additions, deletions, paragraph moves, and dialogue changes.",
        worldbuilding_relevance="Tracks when specific lore terms or character names were altered across revisions.",
        storytelling_relevance="Highlights major scene cuts, restructured chapters, and dialogue tightenings.",
        writing_relevance="Generates side-by-side visual HTML redline views with word churn statistics.",
        advisory_guidance=[
            {"pattern": "Large block cut detected (>500 words)", "option_a": "Archive excised prose in Scraps/ folder for recycling", "option_b": "Review scene pacing to ensure no dropped plot threads", "option_c": "Accept cut as intentional tightening"},
        ],
    ),
    "typography_cleaner": EngineSpec(
        name="typography_cleaner",
        category=EngineCategory.CORE,
        title="Typography Cleaner",
        description="Normalizes smart curly quotes, em-dashes, and typographical ellipses",
        module_name="lib.typography_cleaner",
        cli_command="polish typography",
        aliases=["clean-typography", "polish"],
        studio_tab="Editor",
        logic_documentation="Applies Chicago Manual of Style (CMOS) and Oxford typographical rules: converts straight quotes (' \") to curly quotes (‘ ’ “ ”), double hyphens (--) to em-dashes (—), and triple periods (...) to true ellipses (…), with dialogue attribution comma splice checks.",
        worldbuilding_relevance="Handles in-universe punctuation rules (e.g. alien glottal stops vs quotation marks).",
        storytelling_relevance="Prevents jarring punctuation anomalies from pulling readers out of immersion.",
        writing_relevance="Gives prose a polished, traditionally published literary aesthetic in one click.",
        advisory_guidance=[
            {"pattern": "Unconventional dialogue punctuation (e.g. em-dash quotes or guillemets)", "option_a": "Normalize to standard CMOS quotation marks", "option_b": "Preserve European / custom dialogue conventions", "option_c": "Apply selectively per character dialect"},
        ],
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
        logic_documentation="Performs comprehensive graph topology sweeps across World Bible notes, detecting dangling wikilinks, orphaned dossiers, fuzzy name spelling variants (e.g. Kaelen vs Kaelin), and chronological conflicts.",
        worldbuilding_relevance="Maintains airtight world bible health across hundreds of interlinked lore notes.",
        storytelling_relevance="Prevents accidental continuity blunders and dropped worldbuilding concepts.",
        writing_relevance="Generates an offline HTML health report with 1-click suggested repairs.",
        advisory_guidance=[
            {"pattern": "Fuzzy spelling variant detected (e.g. Althea / Althaea)", "option_a": "Unify all references to primary spelling", "option_b": "Register variant as legitimate in-universe dialect alias", "option_c": "Retain as intentional distinct entities"},
        ],
    ),
    "concordance": EngineSpec(
        name="concordance",
        category=EngineCategory.CORE,
        title="Dramatis Personae & Glossary Generator",
        description="Compiles character indices and lore terms into publication-ready back-matter",
        module_name="lib.concordance",
        cli_command="concordance",
        aliases=["glossary"],
        studio_tab="Publishing",
        logic_documentation="Extracts lore entities from world dossiers, indexes their manuscript occurrences with chapter citations, and formats publication-ready Dramatis Personae and Glossary appendices.",
        worldbuilding_relevance="Transforms complex world notes into accessible reader companion guides.",
        storytelling_relevance="Allows epic fantasy/sci-fi readers to look up houses, ranks, and foreign terms without spoilers.",
        writing_relevance="Automates tedious manual backmatter indexing with typographical formatting.",
        advisory_guidance=[
            {"pattern": "Term cited in lore but never mentioned in manuscript", "option_a": "Exclude unused term from book backmatter", "option_b": "Include in extended world codex only", "option_c": "Retain in backmatter for atmospheric worldbuilding"},
        ],
    ),
    "diagnostics": EngineSpec(
        name="diagnostics",
        category=EngineCategory.CORE,
        title="System Diagnostics & Diagnostics Report",
        description="Toolchain validation, environment health checks, and redacted bug triage bundles",
        module_name="lib.diagnostics",
        cli_command="doctor",
        aliases=["check"],
        studio_tab="Diagnostics",
        logic_documentation="Inspects system environment, verifies 100% offline air-gap isolation, checks external optional tools (Git, Typst, Pandoc), and validates atomic file permissions.",
        worldbuilding_relevance="Verifies storage capacity and integrity for large multimedia lore repositories.",
        storytelling_relevance="Validates compilation toolchains before initiating final book exports.",
        writing_relevance="Provides peace of mind with 100% offline privacy and health verifications.",
        advisory_guidance=[
            {"pattern": "Optional compiler tool missing (e.g. Typst)", "option_a": "Use standard library Python/HTML fallback compiler", "option_b": "Install optional binary via system package manager", "option_c": "Export Markdown for manual external typesetting"},
        ],
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
        logic_documentation="Calculates relativistic kinematics (Brachistochrone 1g transit $t = (2c/a) \\cosh^{-1}(1 + ad/2c^2)$), Lorentz time dilation $\\gamma = 1/\\sqrt{1-v^2/c^2}$, Keplerian orbits $T^2 = 4\\pi^2 a^3 / (G M)$, Roche tidal limits, and multi-sun insolation.",
        worldbuilding_relevance="Calculates accurate planetary day lengths, orbital years, multi-moon tidal forces, and habitable star zones.",
        storytelling_relevance="Uses travel duration as pacing rails; communication light-lag creates information latency; time dilation creates emotional story stakes.",
        writing_relevance="Provides visceral zero-g, spin-gravity Coriolis, and relativistic visual sensory cues.",
        advisory_guidance=[
            {"pattern": "Relativistic FTL transit velocity specified without warp bubble", "option_a": "Cap velocity at sub-light (<1.0 c) with Lorentz dilation", "option_b": "Ground with Alcubierre warp field or hyperspace corridor", "option_c": "Retain uninhibited FTL as intentional space opera convention"},
            {"pattern": "Moon orbiting inside planetary Roche limit", "option_a": "Move moon orbit outside Roche radius to prevent breakup", "option_b": "Transform shattered moon into a majestic planetary ring system", "option_c": "Ground stability via monolithic ancient construct or arcane anchor"},
        ],
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
        logic_documentation="Simulates Milankovitch orbital cycles (eccentricity, obliquity, precession), solar flux insolation $S = L/(4\\pi d^2)$, atmospheric circulation cells (Hadley/Ferrel/Polar), Coriolis deflection, and orographic rain shadows.",
        worldbuilding_relevance="Determines realistic placement of deserts, rainforests, tundra, and temperate zones based on axial tilt and mountains.",
        storytelling_relevance="Sets weather hazards, seasonal agricultural campaigns, and migration pressures driving story conflicts.",
        writing_relevance="Enriches atmospheric sensory details: monsoon humidity, freezing katabatic mountain winds, arid desert salt breezes.",
        advisory_guidance=[
            {"pattern": "Coastal desert without cold ocean current or mountain rain shadow", "option_a": "Add offshore cold current or windward mountain range", "option_b": "Attribute aridity to ancient magical cataclysm or subterranean siphon", "option_c": "Retain as an exotic, wondrous geographical anomaly"},
        ],
    ),
    "cartography": EngineSpec(
        name="cartography",
        category=EngineCategory.CRAFT,
        title="Offline Vector Cartography",
        description="Interactive SVG map viewer and geographic waypoint network explorer",
        module_name="lib.cartography",
        cli_command="map",
        studio_tab="Worldbuilding",
        logic_documentation="Generates and renders interactive SVG vector maps with Voronoi territorial influence polygons, Dijkstra shortest travel path calculation, contour elevation layering, and waypoint staging.",
        worldbuilding_relevance="Maps mountain ranges, river drainage basins, national borders, and trade road networks.",
        storytelling_relevance="Visualizes character journey routes, tactical chokepoints (mountain passes, river bridges), and military frontlines.",
        writing_relevance="Provides exact journey day estimates and landscape horizons during drafting.",
        advisory_guidance=[
            {"pattern": "River bifurcates across flat plain away from coast", "option_a": "Merge rivers downstream following natural downhill gradient", "option_b": "Ground split via engineered royal canal locks or magical delta", "option_c": "Keep fantastical river split as a unique world feature"},
        ],
    ),
    "causality": EngineSpec(
        name="causality",
        category=EngineCategory.CRAFT,
        title="Causal Graph & Timeline Branches",
        description="Directed Acyclic Graph causality engine, timeline paradox detection, and multiverse trees",
        module_name="lib.causality",
        cli_command="causality",
        studio_tab="Worldbuilding",
        logic_documentation="Models narrative causality using Directed Acyclic Graphs (DAG), detects Closed Timelike Curves (CTC), evaluates Novikov self-consistency loops, and tracks multiverse timeline branch divergence.",
        worldbuilding_relevance="Establishes hard physical/metaphysical rules for time travel, prophecies, and precognition.",
        storytelling_relevance="Audits time-travel story logic, grandfather paradoxes, bootstrap paradoxes, and temporal loops.",
        writing_relevance="Helps authors keep track of causal ripples, memory echoes, and butterfly effects.",
        advisory_guidance=[
            {"pattern": "Ungrounded causal bootstrap paradox (information with no origin)", "option_a": "Provide origin event for the retrocausal information", "option_b": "Ground as a stable Novikov self-consistent ontological loop", "option_c": "Embrace the paradox as a deliberate cosmic mystery"},
        ],
    ),
    "conlang": EngineSpec(
        name="conlang",
        category=EngineCategory.CRAFT,
        title="Conlang Phonotactics & Lexicon",
        description="Phoneme inventory generator, sound-law shift simulator, and constructed vocabulary builder",
        module_name="lib.conlang",
        cli_command="conlang",
        studio_tab="Worldbuilding",
        logic_documentation="Generates phonotactic syllable structures (CV, CVC, CCV), enforces Sonority Sequencing, models historical sound-shift mutations (Grimm's Law), and parses Leipzig 3-line interlinear glosses.",
        worldbuilding_relevance="Creates distinct, culturally grounded naming conventions for characters, places, and relics.",
        storytelling_relevance="Brings linguistic diversity to life; language barriers and translation puzzles create story intrigue.",
        writing_relevance="Generates evocative names and authentic in-universe idioms with phonetic harmony.",
        advisory_guidance=[
            {"pattern": "Word violates language phonotactic syllable template", "option_a": "Adjust spelling to match phonotactic inventory", "option_b": "Classify word as ancient loanword or foreign dialect term", "option_c": "Retain spelling as an authorial artistic flourish"},
        ],
    ),
    "ecology": EngineSpec(
        name="ecology",
        category=EngineCategory.CRAFT,
        title="Ecology & Food Web Simulator",
        description="Trophic energy pyramid validator (Lindeman 10% efficiency) and apex predator sustainability",
        module_name="lib.ecology",
        cli_command="ecology",
        studio_tab="Worldbuilding",
        logic_documentation="Applies Raymond Lindeman's 10% trophic transfer efficiency, Lotka-Volterra predator-prey differential models, Kleiber's metabolic scaling ($P \\propto M^{0.75}$), and Square-Cube skeletal limits on megafauna.",
        worldbuilding_relevance="Calculates sustainable predator densities, herbivore grazing lands, and monster biome capacities.",
        storytelling_relevance="Scarcity of game drives hunter-gatherer migrations, monster attacks, and territorial conflicts.",
        writing_relevance="Provides authentic sensory descriptions of flora, fauna behavior, and foraging yields.",
        advisory_guidance=[
            {"pattern": "Colossal apex predator biomass exceeds available herbivore prey", "option_a": "Scale down predator pack size or expand prey territory", "option_b": "Ground feeding via magical ambient energy or geothermal vents", "option_c": "Retain giant monster as a rare mythical creature"},
        ],
    ),
    "economy": EngineSpec(
        name="economy",
        category=EngineCategory.CRAFT,
        title="Macroeconomics & Currencies",
        description="In-world fiat/specie exchange rates, purchasing power parity, and commodity price modeling",
        module_name="lib.economy",
        cli_command="economy",
        studio_tab="Worldbuilding",
        logic_documentation="Models Gresham's Law (coinage debasement), Purchasing Power Parity (PPP) commodity price baskets, trade arbitrage margins, and fractional reserve promissory notes.",
        worldbuilding_relevance="Establishes currency exchange rates, guild price-fixing, tax burdens, and black markets.",
        storytelling_relevance="Economic inequality, debt, tariffs, and contraband smuggling fuel plot stakes and character motivations.",
        writing_relevance="Provides realistic pricing for tavern meals, horse rentals, sword forging, and carriage fares.",
        advisory_guidance=[
            {"pattern": "Extreme commodity price disparity across open border markets", "option_a": "Rebalance prices toward equilibrium considering carriage costs", "option_b": "Explain gap by wartime blockade, banditry, or guild monopolies", "option_c": "Retain disparity to emphasize regional isolation"},
        ],
    ),
    "factions": EngineSpec(
        name="factions",
        category=EngineCategory.CRAFT,
        title="Geopolitical Factions & Diplomacy",
        description="Diplomatic relation matrices, tension paradox detection, and alliance networks",
        module_name="lib.factions",
        cli_command="faction",
        studio_tab="Worldbuilding",
        logic_documentation="Evaluates balance-of-power coalitions, diplomatic tension paradoxes, espionage network infiltration, and Lanchester square-law military strength ratios.",
        worldbuilding_relevance="Structures geopolitical factions, noble houses, knightly orders, and shadow syndicates.",
        storytelling_relevance="Powers political intrigue, betrayal, treaty negotiations, and shifting war alliances.",
        writing_relevance="Informs court dialogue, diplomatic etiquette, and heraldic protocol.",
        advisory_guidance=[
            {"pattern": "Faction simultaneously marked as active ally and at war", "option_a": "Update relationship to formal state of war or truce", "option_b": "Frame as a covert proxy conflict under public alliance", "option_c": "Retain as a fragile political double-game"},
        ],
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
        logic_documentation="Calculates Wright's inbreeding coefficient ($F$), evaluates succession laws (Salic, Primogeniture, Ultimogeniture, Tanistry, Gavelkind), resolves cadet branch cadency, and exports Mermaid family trees.",
        worldbuilding_relevance="Builds noble lineages, royal marriage alliances, and inheritance claim hierarchies.",
        storytelling_relevance="Drives succession crises, bastard claims, civil wars, and ancestral destiny arcs.",
        writing_relevance="Keeps generational relationships, honorific titles, and family kinship accurate.",
        advisory_guidance=[
            {"pattern": "Disputed succession claim between multiple primary heirs", "option_a": "Clarify legal succession law precedence", "option_b": "Use the disputed claim as the catalyst for dynastic civil war", "option_c": "Retain ambiguity as a central plot mystery"},
        ],
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
        logic_documentation="Calculates travel duration across terrain types (paved road, forest, mountain pass, swamp), pack animal feed ratios, high-altitude acclimatization, and wagon wheelwright repairs.",
        worldbuilding_relevance="Determines staging distance between coaching inns, royal relay post stations, and fortresses.",
        storytelling_relevance="Prevents travel teleportation; journey duration shapes character conversations and camping bonding scenes.",
        writing_relevance="Supplies realistic travel fatigue, blister care, foraging yields, and campfire sensory details.",
        advisory_guidance=[
            {"pattern": "Unrealistically fast foot travel speed (>50 km/day over rough mountains)", "option_a": "Increase travel duration to 4-5 days for realistic pacing", "option_b": "Ground travel speed via enchanted boots, post-horse relay, or magical draft", "option_c": "Retain accelerated travel for tight narrative velocity"},
        ],
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
        logic_documentation="Evaluates magic systems against Brandon Sanderson's Three Laws of Magic, tracks energy conservation, calculates sympathetic backlash, and monitors caster fatigue tier limits.",
        worldbuilding_relevance="Integrates arcane arts into society, military doctrine, education, and economy.",
        storytelling_relevance="Ensures magic creates satisfying problem-solving tension rather than unearned convenience.",
        writing_relevance="Provides visceral somatic magic details: burning blood, glowing glyphs, mana chills, spell exhaustion.",
        advisory_guidance=[
            {"pattern": "Spell cast without required reagent or exceeding caster tier", "option_a": "Enforce standard spell failure or severe magical backlash", "option_b": "Frame as a dangerous life-force sacrifice or divine breakthrough", "option_c": "Permit the surge as a pivotal dramatic miracle"},
        ],
    ),
    "pacing": EngineSpec(
        name="pacing",
        category=EngineCategory.CRAFT,
        title="Pacing & Dialogue Rhythm",
        description="Dialogue-to-narrative density ratio, sentence length variance, and scene momentum analyzer",
        module_name="lib.pacing",
        cli_command="pace",
        aliases=["tension"],
        studio_tab="Craft",
        logic_documentation="Analyzes prose mode distribution (Dialogue vs Action vs Monologue vs Exposition), Gary Provost sentence length waveforms, tension curve oscillations, and POV screen-time balance.",
        worldbuilding_relevance="Prevents lore dumps from stalling active narrative momentum.",
        storytelling_relevance="Balances fast-paced action sequences with reflective sequels and character bonding.",
        writing_relevance="Flags monotonous sentence structures and dialogue void syndrome.",
        advisory_guidance=[
            {"pattern": "Chapter dialogue density exceeds 80% without somatic action beats", "option_a": "Insert physical character actions, sensory environment cues, and pauses", "option_b": "Retain as a rapid-fire interrogation or tense courtroom debate", "option_c": "Keep stylized theatrical dialogue mode"},
        ],
    ),
    "plot_matrix": EngineSpec(
        name="plot_matrix",
        category=EngineCategory.CRAFT,
        title="Plot Grid & Subplot Matrix",
        description="Multi-threaded narrative grid tracking concurrent character arcs and mystery clues",
        module_name="lib.plot_matrix",
        cli_command="plot",
        studio_tab="Craft",
        logic_documentation="Builds multi-track 2D plot spreadsheets tracking concurrent A-plots, B-plots, mystery clues, Chekhov's guns, Sanderson's Promise-Progress-Payoff (P3) cycles, and character co-occurrence collisions.",
        worldbuilding_relevance="Ensures world events (wars, celestial transits) align with character chapters.",
        storytelling_relevance="Tracks foreshadowing fulfillment and prevents forgotten subplots across chapters.",
        writing_relevance="Provides structural clarity across complex, multi-threaded epics.",
        advisory_guidance=[
            {"pattern": "Chekhov gun introduced in early chapter without payoff by climax", "option_a": "Integrate payoff during climactic resolution", "option_b": "Frame as an intentional mystery clue carried into sequel volume", "option_c": "Keep as atmospheric background lore element"},
        ],
    ),
    "portfolio": EngineSpec(
        name="portfolio",
        category=EngineCategory.CRAFT,
        title="Portfolio & Drafting Velocity",
        description="Multi-manuscript word count tracker, sprint pacing, and catalog overview dashboard",
        module_name="lib.portfolio",
        cli_command="portfolio",
        studio_tab="Overview",
        logic_documentation="Aggregates multi-book catalog analytics, lifetime drafting velocity, release pipeline Gantt milestones, and writing streak heatmaps.",
        worldbuilding_relevance="Tracks master lore integration across multi-book shared universes.",
        storytelling_relevance="Monitors series-level narrative arcs and production schedules.",
        writing_relevance="Celebrates daily word count milestones and sustains creative momentum.",
        advisory_guidance=[
            {"pattern": "Drafting velocity lull detected (>14 days inactive)", "option_a": "Schedule a 15-minute low-pressure writing sprint", "option_b": "Switch focus to worldbuilding lore or character sketches", "option_c": "Acknowledge planned creative rest period"},
        ],
    ),
    "prophecy": EngineSpec(
        name="prophecy",
        category=EngineCategory.CRAFT,
        title="Prophecy Lifecycle Tracker",
        description="Tracks cryptic prophecy stanzas, interpretations, fulfillment conditions, and subversions",
        module_name="lib.prophecy",
        cli_command="prophecy",
        studio_tab="Worldbuilding",
        logic_documentation="Tracks cryptic prophecy stanzas, Delphic ambiguities, fulfillment milestones, Oedipal paradoxes, and deliberate thematic subversions across manuscript chapters.",
        worldbuilding_relevance="Grounds sacred religious scriptures, ancient oracle inscriptions, and mythological lore.",
        storytelling_relevance="Builds reader anticipation and dramatic irony through ambiguous prophecy clauses.",
        writing_relevance="Aids in crafting poetic, double-meaning prophetic verses and riddle stanzas.",
        advisory_guidance=[
            {"pattern": "Prophecy clause fulfilled too straightforwardly without thematic twist", "option_a": "Add Delphic double-meaning or ironic twist to fulfillment", "option_b": "Subvert the prophecy as a manufactured political fraud", "option_c": "Fulfill literally as a legendary validation of ancient truth"},
        ],
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
        logic_documentation="Audits Dwight Swain's Scene (Goal -> Conflict -> Disaster) and Sequel (Reaction -> Dilemma -> Decision) Motivation-Reaction Units (MRUs), in media res entries, and cliffhanger exits.",
        worldbuilding_relevance="Embeds world conflicts directly into immediate character stakes.",
        storytelling_relevance="Ensures every chapter advances plot and character transformation without dead weight.",
        writing_relevance="Eliminates 'talking heads in a void' and weak chapter endings.",
        advisory_guidance=[
            {"pattern": "Scene ends in clean triumph without new complication ('Yes, and')", "option_a": "Transform into Swain 'Yes, but' or 'No, and furthermore' disaster", "option_b": "Use victory to trigger higher external stakes from rival factions", "option_c": "Retain triumph as a earned moment of celebration"},
        ],
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
        logic_documentation="Scans prose across 8 sensory dimensions (Visual, Auditory, Olfactory, Gustatory, Tactile/Thermal, Kinesthetic/Proprioception, Equilibrium, Interoception) to prevent White Room Syndrome.",
        worldbuilding_relevance="Gives each fantasy/sci-fi location a unique sensory signature (tavern smoke, dungeon damp, desert sulfur).",
        storytelling_relevance="Enhances immersion during climaxes by intensifying sensory density.",
        writing_relevance="Flags visual-only exposition and reminds writers to engage smell, sound, and physical touch.",
        advisory_guidance=[
            {"pattern": "Scene has zero auditory or olfactory sensory grounding", "option_a": "Add atmospheric background sounds and scent profiles", "option_b": "Frame sensory absence as character dissociation or sterile environment", "option_c": "Keep sparse sensory style for brisk action velocity"},
        ],
    ),
    "series_continuity": EngineSpec(
        name="series_continuity",
        category=EngineCategory.CRAFT,
        title="Series Continuity Ledger",
        description="Tracks recurring character traits, scars, eye color, and gear across multi-volume series",
        module_name="lib.series_continuity",
        cli_command="series",
        studio_tab="Worldbuilding",
        logic_documentation="Tracks character physical traits (handedness, scars, eye color), relic chains of custody, biological aging across timeskips, and geopolitical world-state changes across multi-book sagas.",
        worldbuilding_relevance="Ensures multi-volume world lore remains coherent as empires rise and fall.",
        storytelling_relevance="Maintains character scars, trauma, and power progression across decades of story time.",
        writing_relevance="Prevents embarrassing retcons and continuity errors between Book 1 and Book 5.",
        advisory_guidance=[
            {"pattern": "Character eye color or handedness changed between volumes", "option_a": "Revert to Book 1 canonical trait", "option_b": "Ground change in story event (e.g. magical scarring, injury, disguise)", "option_c": "Acknowledge and retain as an intentional character transformation"},
        ],
    ),
    "structure": EngineSpec(
        name="structure",
        category=EngineCategory.CRAFT,
        title="Narrative Structure & Paradigms",
        description="Validates manuscript beats against 3-Act, Save the Cat, Hero's Journey, and Fichtean Curve",
        module_name="lib.structure",
        cli_command="structure",
        studio_tab="Craft",
        logic_documentation="Maps chapter word distributions against classical and modern storytelling frameworks: Three-Act Structure, Save the Cat, 8-Sequence Method, Hero's Journey, Fichtean Curve, and Kishōtenketsu (4-act twist without conflict).",
        worldbuilding_relevance="Aligns world discovery milestones with character paradigm shifts.",
        storytelling_relevance="Diagnoses sluggish midpoints, premature climaxes, and rushed resolutions.",
        writing_relevance="Provides structural confidence during outlining and developmental editing.",
        advisory_guidance=[
            {"pattern": "Midpoint transformation occurs at 68% instead of standard 50%", "option_a": "Rebalance chapter lengths toward symmetrical midpoint", "option_b": "Adopt asymmetrical 4-part Kishōtenketsu or Fichtean episodic pacing", "option_c": "Retain pacing as an intentional authorial tension curve"},
        ],
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
        logic_documentation="Evaluates Flesch-Kincaid grade level, passive voice constructions, nominalizations ('zombie nouns'), filter words ('she heard', 'he saw'), echo word repetitions within sliding windows, and said-bookisms.",
        worldbuilding_relevance="Ensures fantasy prose maintains an appropriate, immersive reading level.",
        storytelling_relevance="Tightens narrative voice, accelerates reader velocity, and eliminates psychic distance.",
        writing_relevance="Provides actionable line-editing recommendations that elevate draft quality.",
        advisory_guidance=[
            {"pattern": "High filter word density ('she realized', 'he noticed')", "option_a": "Strip filter words for direct psychic immersion", "option_b": "Retain filter words to emphasize deliberate detective observation", "option_c": "Preserve for distant narrator stylistic voice"},
        ],
    ),
    "tactical_sim": EngineSpec(
        name="tactical_sim",
        category=EngineCategory.CRAFT,
        title="Tactical Skirmish & Battle Simulator",
        description="Lanchester square-law combat model, terrain modifiers, morale decay, and casualty sim",
        module_name="lib.tactical_sim",
        cli_command="sim battle",
        aliases=["battle", "sim"],
        studio_tab="Worldbuilding",
        logic_documentation="Simulates Lanchester linear and square-law combat dynamics, terrain modifiers (castle walls, dense forest, river crossings), unit morale rout thresholds, and blow-by-blow narrative choreography logs.",
        worldbuilding_relevance="Determines realistic army sizes, siege durations, supply requirements, and military logistics.",
        storytelling_relevance="Choreographs dramatic duels and large-scale battle turning points with tactical realism.",
        writing_relevance="Supplies visceral combat beats: weapon reach advantages, shield bracing, fatigue, armor dents.",
        advisory_guidance=[
            {"pattern": "Small infantry militia defeats superior armored cavalry in open field without terrain advantage", "option_a": "Add terrain bottleneck (mud, pikes, trenches) to justify victory", "option_b": "Ground victory via surprise flanking, magical artillery, or cavalry panic", "option_c": "Retain outcome as heroic against-all-odds underdog victory"},
        ],
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
        logic_documentation="Analyzes character idiolects, lexical rarity scores, sentence length cadence, verbal tics, and conversational dominance to detect voice bleed across multiple POV characters.",
        worldbuilding_relevance="Reflects character social class, regional origins, and professional guilds through distinct dialogue registers.",
        storytelling_relevance="Ensures reader immediately knows who is speaking without relying on dialogue tags.",
        writing_relevance="Prevents all characters from sounding like the author.",
        advisory_guidance=[
            {"pattern": "Two POV characters share nearly identical vocabulary and sentence cadence (voice bleed)", "option_a": "Diversify idiolects with unique verbal tics, catchphrases, and sentence lengths", "option_b": "Frame shared voice as cultural upbringing or shared military academy training", "option_c": "Retain consistent authorial voice across ensemble cast"},
        ],
    ),
    "ambient": EngineSpec(
        name="ambient",
        category=EngineCategory.CRAFT,
        title="Ambient Focus & Binaural Beats",
        description="Local offline sound synthesis for deep writing focus (binaural beats, rain, fire, library)",
        module_name="lib.ambient",
        cli_command="ambient",
        studio_tab="Tools",
        logic_documentation="Synthesizes pure offline procedural soundscapes using Python standard library and Web Audio API: brown noise, pink noise, binaural alpha/theta waves, rain, fireplace, and quiet library ambiance.",
        worldbuilding_relevance="Creates deep auditory immersion matching the environment being drafted.",
        storytelling_relevance="Assists authors in entering deep flow states for focused writing sessions.",
        writing_relevance="100% offline audio generator requiring no internet or external media files.",
        advisory_guidance=[
            {"pattern": "Audio playback requested in headless terminal environment", "option_a": "Generate WAV audio file for external local media player", "option_b": "Launch Web Audio synthesis in browser Studio Hub", "option_c": "Display visual Pomodoro focus timer without sound"},
        ],
    ),
    "codex_export": EngineSpec(
        name="codex_export",
        category=EngineCategory.CRAFT,
        title="World Wiki Codex Export",
        description="Compiles world lore notes into a standalone, searchable offline HTML encyclopedia",
        module_name="lib.codex_export",
        cli_command="codex",
        studio_tab="Publishing",
        logic_documentation="Compiles World Bible markdown files into an ultra-fast, responsive, single-file offline HTML wiki with full-text search, spoiler sliders, and interactive relationship embeds.",
        worldbuilding_relevance="Creates an offline encyclopedia compendium for fans, beta readers, and tabletop GMs.",
        storytelling_relevance="Provides readers with an exploratory lore codex companion.",
        writing_relevance="Enables quick reference lookup of lore notes on tablets and secondary monitors.",
        advisory_guidance=[
            {"pattern": "World notes contain major late-story spoiler revelations", "option_a": "Enable reader spoiler slider to hide late-book lore", "option_b": "Segment secrets into GM/Author-only codex section", "option_c": "Export full unredacted codex for author reference"},
        ],
    ),
    "calendar": EngineSpec(
        name="calendar",
        category=EngineCategory.CRAFT,
        title="Custom Planetary Calendars & Moons",
        description="Multi-moon synodic phase tracker, celestial conjunctions, and fictional calendar math",
        module_name="lib.calendar",
        cli_command="calendar",
        studio_tab="Worldbuilding",
        logic_documentation="Models custom planetary calendars, multiple moon orbital phases, synodic conjunctions (syzygy), Metonic lunisolar cycle synchronization, and epoch offset conversions.",
        worldbuilding_relevance="Constructs bespoke calendar systems with unique week lengths, months, and festival days.",
        storytelling_relevance="Anchors prophecy countdowns and dramatic deadlines to rare celestial conjunctions.",
        writing_relevance="Provides in-universe date arithmetic and lunar phase lighting descriptions.",
        advisory_guidance=[
            {"pattern": "Unequal seasonal lengths caused by orbital eccentricity", "option_a": "Calculate precise Keplerian seasonal lengths for calendar", "option_b": "Attribute seasonal harmony to divine orbital intervention", "option_c": "Use harsh long winters as a central cultural story pillar"},
        ],
    ),
    "local_rag": EngineSpec(
        name="local_rag",
        category=EngineCategory.CORE,
        title="Sovereign Local Semantic Retrieval",
        description="Hybrid TF-IDF vector space and SQLite FTS5 lore query engine",
        module_name="lib.local_rag",
        cli_command="rag",
        aliases=["query-lore", "semantic-search", "lore-query"],
        studio_tab="Tools",
        logic_documentation="Zero-dependency hybrid TF-IDF vector space and SQLite FTS5 BM25 search engine with Reciprocal Rank Fusion (RRF), hierarchical parent-child chunking, and local LLM context synthesis.",
        worldbuilding_relevance="Answers complex lore queries instantly across tens of thousands of vault notes.",
        storytelling_relevance="Synthesizes relevant character backgrounds, magic constraints, and history before drafting.",
        writing_relevance="Empowers in-situ research without leaving the drafting cockpit.",
        advisory_guidance=[
            {"pattern": "Ambiguous search query returns multiple cross-domain entities", "option_a": "Apply domain category filter (e.g. Characters, Magic)", "option_b": "Use Reciprocal Rank Fusion to synthesize top matches", "option_c": "Display interactive search disambiguation list"},
        ],
    ),
    "branching_graph": EngineSpec(
        name="branching_graph",
        category=EngineCategory.CRAFT,
        title="Interactive Branching Narrative Graph",
        description="Topological choice DAG validator and multi-engine exporter (HTML, Ink, Twine, Mermaid)",
        module_name="lib.branching_graph",
        cli_command="branch",
        aliases=["branching", "gamebook", "interactive-fiction", "branch-graph", "subway-map"],
        studio_tab="Editor",
        logic_documentation="Parses choice directives (@choice, @state), validates choice graph topology, detects dead-ends/unreachable nodes, and exports interactive narrative subway maps.",
        worldbuilding_relevance="Maps interactive choose-your-own-path gamebooks and branching historical events.",
        storytelling_relevance="Visualizes multi-POV storyline splits, divergences, and climax convergences.",
        writing_relevance="Ensures all branching narrative paths are satisfying and structurally balanced.",
        advisory_guidance=[
            {"pattern": "Dead-end branch node without resolution or choice exit", "option_a": "Add resolution epilogue or redirect choice to convergence node", "option_b": "Frame branch as an intentional tragic failure ending", "option_c": "Keep as work-in-progress draft stub"},
        ],
    ),
    "studio_hub": EngineSpec(
        name="studio_hub",
        category=EngineCategory.CORE,
        title="Sovereign Studio Desktop Hub & Dashboard",
        description="Master unified desktop and web orchestrator dashboard unifying all 50+ craft engines",
        module_name="lib.studio_hub",
        cli_command="hub",
        aliases=["dashboard", "studio-hub", "gui-web"],
        studio_tab="Tools",
        logic_documentation="Master local-first web and desktop orchestrator providing live manuscript telemetry, lore entity cards, structural harmony curves, timeline paradox audits, and craft engine matrix.",
        worldbuilding_relevance="Central command cockpit unifying all 50 domain engines into an intuitive GUI.",
        storytelling_relevance="Displays real-time project metrics: words, reading hours, chapters, and paradoxes.",
        writing_relevance="Runs 100% offline with zero external network calls or cloud dependencies.",
        advisory_guidance=[
            {"pattern": "Port 8080 already bound by another process", "option_a": "Automatically increment to next available port (e.g. 8081)", "option_b": "Export standalone static HTML dashboard file", "option_c": "Launch desktop GTK window instead of web hub"},
        ],
    ),
    "writing_sprint": EngineSpec(
        name="writing_sprint",
        category=EngineCategory.CORE,
        title="Sovereign Writing Sprint & Session Analytics",
        description="Sprint session timer, WPM velocity analytics, daily streak tracking, and offline HTML productivity dashboard",
        module_name="lib.writing_sprint",
        cli_command="sprint",
        aliases=["writing-sprint", "pomodoro", "session"],
        studio_tab="Productivity",
        logic_documentation="Tracks focused writing sprint intervals, net new word counts, WPM typing velocity, daily streaks, time-of-day productivity heatmaps, and offline achievement quests.",
        worldbuilding_relevance="Measures worldbuilding note generation velocity and research sprints.",
        storytelling_relevance="Assists writers in breaking through drafting blocks and hitting volume milestones.",
        writing_relevance="Builds consistent daily writing habits with motivating offline progress reports.",
        advisory_guidance=[
            {"pattern": "Sprint target word count not reached during interval", "option_a": "Extend sprint timer by 5 minutes for completion", "option_b": "Log session words and celebrate net positive output", "option_c": "Reflect in session journal and take a restful break"},
        ],
    ),
    "revision_heatmap": EngineSpec(
        name="revision_heatmap",
        category=EngineCategory.CRAFT,
        title="Manuscript Revision Density & Churn Heatmap",
        description="Snapshot-based revision churn analyzer flagging over-revised (REV-101) and pristine-draft (REV-102) chapters",
        module_name="lib.revision_heatmap",
        cli_command="revision-heatmap",
        aliases=["churn", "revision-density", "draft-churn"],
        studio_tab="Diagnostics",
        logic_documentation="Analyzes historical snapshot diffs to compute sentence-level word churn ratios, distinguishing structural rewrites from polish edits and flagging over-revised vs pristine chapters.",
        worldbuilding_relevance="Shows which lore sections underwent the heaviest conceptual overhauls.",
        storytelling_relevance="Identifies 'problem chapters' that have been endlessly rewritten without progress.",
        writing_relevance="Helps authors step away from perfectionist over-editing and move forward.",
        advisory_guidance=[
            {"pattern": "Chapter flagged with excessive revision churn (>80% word replacement across 5+ drafts)", "option_a": "Perform fresh developmental outline review of the scene's core goal", "option_b": "Lock the chapter and proceed to drafting subsequent chapters", "option_c": "Accept high churn as necessary stylistic exploration"},
        ],
    ),
    "dramatis_personae": EngineSpec(
        name="dramatis_personae",
        category=EngineCategory.CRAFT,
        title="Multi-Volume Dramatis Personae & Universe Cast Matrix",
        description="Cross-volume character profile parser, manuscript POV/mention cross-referencer, lifecycle continuity auditor, and gallery generator",
        module_name="lib.dramatis_personae",
        cli_command="cast",
        aliases=["dramatis-personae", "dramatis", "characters-cast"],
        studio_tab="Worldbuilding",
        logic_documentation="Parses character dossiers, cross-references manuscript chapter POV screen-times, validates lifecycle states (Alive -> Missing -> Deceased -> Ascended), detects name phonetic collisions (e.g. Jon vs Joram), and exports HTML galleries.",
        worldbuilding_relevance="Maintains comprehensive universe cast matrices across noble houses, factions, and orders.",
        storytelling_relevance="Audits character screen-time, relationship chord networks, and long-term POV absence.",
        writing_relevance="Prevents similar-sounding character names that confuse readers.",
        advisory_guidance=[
            {"pattern": "Phonetically similar character names in same scene (e.g. 'Kaelen' and 'Kaelin')", "option_a": "Rename one character with distinct starting consonant", "option_b": "Establish in-universe naming tradition (e.g. cousins named after grandfather)", "option_c": "Retain names with clarifying nicknames / titles"},
        ],
    ),
    "story_canvas": EngineSpec(
        name="story_canvas",
        category=EngineCategory.CRAFT,
        title="Visual Story Canvas & Corkboard",
        description="Visual drag-and-drop narrative corkboard with live structural harmony recalculation",
        module_name="lib.story_canvas",
        cli_command="canvas",
        aliases=["corkboard", "story-map", "story-canvas"],
        studio_tab="Editor",
        logic_documentation="Provides an offline visual corkboard where authors can drag and drop chapter index cards, reordering disk files bidirectionally, while calculating tension and structural beat distributions in real-time.",
        worldbuilding_relevance="Pins location dossiers and artifact cards alongside relevant plot scenes.",
        storytelling_relevance="Enables intuitive visual restructuring of acts, sequences, and subplot pacing.",
        writing_relevance="Combines visual index cards with synopsis summaries for effortless chapter navigation.",
        advisory_guidance=[
            {"pattern": "Visual card reordering changes chapter narrative sequence on disk", "option_a": "Confirm atomic file renumbering on disk", "option_b": "Create virtual outline arrangement without touching disk files", "option_c": "Export new card order as an alternative draft outline"},
        ],
    ),
    "timeline_sync": EngineSpec(
        name="timeline_sync",
        category=EngineCategory.CRAFT,
        title="Dual-Track Timeline Synchronizer",
        description="Chronological vs narrative sequence synchronizer with flashback and paradox detection",
        module_name="lib.timeline_sync",
        cli_command="timeline",
        aliases=["timeline-sync", "sync-timeline"],
        studio_tab="Worldbuilding",
        logic_documentation="Synchronizes dual-track narrative sequence (reader's page order) against chronological in-universe dates, detecting impossible character bilocations, flashbacks, and timeline paradoxes.",
        worldbuilding_relevance="Builds thousands of years of historical annals aligned with in-universe calendar math.",
        storytelling_relevance="Manages nonlinear storytelling (flashbacks, parallel storylines, framing narratives).",
        writing_relevance="Ensures character biological ages, travel times, and seasons match narrative dates.",
        advisory_guidance=[
            {"pattern": "Character appears in two distant locations on the same chronological date (bilocation)", "option_a": "Adjust chapter narrative date or introduce travel interval", "option_b": "Ground bilocation via magical teleportation, twin sibling, or astral projection", "option_c": "Retain as an intentional non-linear storytelling perspective"},
        ],
    ),
    "omnibus": EngineSpec(
        name="omnibus",
        category=EngineCategory.CORE,
        title="Series Omnibus Compiler",
        description="Multi-volume master series compiler with unified Dramatis Personae and master timeline",
        module_name="lib.omnibus",
        cli_command="omnibus",
        aliases=["compile-omnibus", "series-omnibus"],
        studio_tab="Publishing",
        logic_documentation="Compiles multi-volume book series into deluxe single-volume omnibus editions with unified Dramatis Personae, master timeline appendices, and cross-volume continuity harmonization.",
        worldbuilding_relevance="Unifies lore glossaries across an entire trilogy or multi-book saga.",
        storytelling_relevance="Ensures smooth inter-book reading with 'The Story So Far' interstitial recaps.",
        writing_relevance="Formats deluxe Typst and EPUB3 box sets with persistent offline bookmarks.",
        advisory_guidance=[
            {"pattern": "Inconsistent term definitions across Book 1 and Book 3 in omnibus compilation", "option_a": "Harmonize to latest canonical definition in master glossary", "option_b": "Annotate term evolution as historical in-universe linguistic shift", "option_c": "Retain volume-specific glossaries in individual book sections"},
        ],
    ),
    "corpus_export": EngineSpec(
        name="corpus_export",
        category=EngineCategory.CORE,
        title="Universal Structured Corpus & RAG Exporter",
        description="Structured JSONL, SQLite FTS5 database, markdown summary digest exporter, and bidirectional vault restore",
        module_name="lib.corpus_export",
        cli_command="corpus",
        aliases=["corpus-export", "export-corpus", "rag-export", "corpus-restore"],
        studio_tab="Tools",
        logic_documentation="Exports complete universe lore and manuscript vaults into structured JSONL datasets, SQLite FTS5 relational databases, fine-tuning formats (Alpaca, ShareGPT), and cryptographically verified ZIP archives with bidirectional restoration.",
        worldbuilding_relevance="Backs up and structures massive worldbuilding vaults into machine-readable datasets.",
        storytelling_relevance="Enables structured data analysis of character appearances and scene interactions.",
        writing_relevance="Guarantees permanent data portability with zero vendor lock-in.",
        advisory_guidance=[
            {"pattern": "Export target archive already exists", "option_a": "Overwrite existing archive with new SHA-256 timestamped build", "option_b": "Create incremental delta export file", "option_c": "Prompt user for custom export destination"},
        ],
    ),
    "importer": EngineSpec(
        name="importer",
        category=EngineCategory.CORE,
        title="Batch Manuscript & Vault Importer",
        description="Batch importer for Scrivener, Word (.docx), and unstructured Markdown trees",
        module_name="lib.importer",
        cli_command="import",
        aliases=["importer", "import-manuscript"],
        studio_tab="Tools",
        logic_documentation="Converts external Scrivener projects, Word (.docx) documents, Google Docs, and raw Markdown folders into sovereign Ars Arcanum manuscript vaults with manifest metadata and novelWriter project files.",
        worldbuilding_relevance="Auto-seeds initial world dossiers from imported character and location names.",
        storytelling_relevance="Splits monolithic manuscript files into clean, ordered chapter structures.",
        writing_relevance="Provides seamless migration from proprietary writing apps to sovereign Ars Arcanum.",
        advisory_guidance=[
            {"pattern": "Monolithic manuscript file without chapter break headers", "option_a": "Auto-split at common chapter patterns (# Chapter, Act, scene breaks)", "option_b": "Import as single continuous chapter file", "option_c": "Prompt user for custom chapter delimiter regex"},
        ],
    ),
    "zen_studio": EngineSpec(
        name="zen_studio",
        category=EngineCategory.CORE,
        title="Zen Drafting Studio",
        description="Distraction-free typewriter drafting cockpit with in-situ lore drawer and beat tracker",
        module_name="lib.zen_studio",
        cli_command="studio",
        aliases=["zen", "zen-studio", "editor"],
        studio_tab="Editor",
        logic_documentation="Zero-dependency, single-file offline HTML5 typewriter drafting environment featuring dark/sepia/light themes, live reading/speech telemetry, in-situ world lore drawer, and LocalStorage autosave.",
        worldbuilding_relevance="Allows writers to search character dossiers and magic rules without breaking drafting flow.",
        storytelling_relevance="Provides live chapter word counts and reading time estimates while drafting.",
        writing_relevance="Delivers a distraction-free, pure typewriter focus environment with 100% offline privacy.",
        advisory_guidance=[
            {"pattern": "Drafting in Zen Studio with unsaved local buffer changes", "option_a": "Auto-save changes to browser LocalStorage and disk", "option_b": "Download standalone Markdown export file", "option_c": "Discard local buffer and restore canonical disk state"},
        ],
    ),
    "continuity": EngineSpec(
        name="continuity",
        category=EngineCategory.CRAFT,
        title="Semantic Continuity & Trait Linter",
        description="Local-first semantic narrative continuity analyzer cross-validating character traits across drafts",
        module_name="lib.continuity",
        cli_command="continuity",
        aliases=["check-continuity"],
        studio_tab="Diagnostics",
        logic_documentation="Extracts character physical traits (eyes, hair, titles, status) from World Bible files and sentence-level manuscript scenes, detecting character trait drift, impossible contradictions, and inter-scene inconsistencies.",
        worldbuilding_relevance="Ensures character traits established in lore dossiers are maintained in prose.",
        storytelling_relevance="Catches accidental continuity discrepancies before publication.",
        writing_relevance="Provides clear advisory alerts with multiple creative resolution pathways.",
        advisory_guidance=[
            {"pattern": "Character eye color asserted as green in scene but blue in World Bible", "option_a": "Correct scene prose to match World Bible canonical blue eyes", "option_b": "Ground color shift in story (e.g. illusion, colored contact, magical flare)", "option_c": "Update World Bible dossier if the author intentionally changed character design"},
        ],
    ),
}


def get_registry() -> dict[str, EngineSpec]:
    """Return the global engine dictionary."""
    return _ENGINES


def get_engine(name: str) -> EngineSpec | None:
    """Retrieve an engine specification by name, command, or alias."""
    name_clean = name.lower().strip()
    name_underscored = name_clean.replace("-", "_").replace(" ", "_")
    name_hyphenated = name_clean.replace("_", "-").replace(" ", "-")

    if name_clean in _ENGINES:
        return _ENGINES[name_clean]
    if name_underscored in _ENGINES:
        return _ENGINES[name_underscored]

    for spec in _ENGINES.values():
        all_names = {
            spec.name.lower(),
            spec.name.lower().replace("_", "-"),
            spec.cli_command.lower(),
            spec.cli_command.lower().replace(" ", "-"),
            spec.cli_command.lower().replace(" ", "_"),
        }
        for a in spec.aliases:
            all_names.add(a.lower())
            all_names.add(a.lower().replace("_", "-"))
            all_names.add(a.lower().replace("-", "_"))
        if name_clean in all_names or name_underscored in all_names or name_hyphenated in all_names:
            return spec

    for spec in _ENGINES.values():
        if spec.cli_command.lower().startswith(name_clean + " ") or spec.cli_command.lower().endswith(" " + name_clean):
            return spec
    return None


def list_engines(category: EngineCategory | None = None, enabled_only: bool = True) -> list[EngineSpec]:
    """List engine specifications matching optional category and enabled filter."""
    res = []
    for spec in _ENGINES.values():
        if category is not None and spec.category != category:
            continue
        if enabled_only and not spec.enabled:
            continue
        res.append(spec)
    return res


def get_core_engines(enabled_only: bool = True) -> list[EngineSpec]:
    """Return all core platform engines."""
    return list_engines(category=EngineCategory.CORE, enabled_only=enabled_only)


def get_craft_engines(enabled_only: bool = True) -> list[EngineSpec]:
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


def get_engine_docs(name: str) -> dict[str, Any] | None:
    """Retrieve structured educational documentation and advisory guidance for an engine."""
    spec = get_engine(name)
    if not spec:
        return None
    return {
        "name": spec.name,
        "title": spec.title,
        "category": spec.category.value,
        "studio_tab": spec.studio_tab or "",
        "cli_command": spec.cli_command,
        "aliases": spec.aliases,
        "description": spec.description,
        "logic_documentation": spec.logic_documentation,
        "worldbuilding_relevance": spec.worldbuilding_relevance,
        "storytelling_relevance": spec.storytelling_relevance,
        "writing_relevance": spec.writing_relevance,
        "advisory_guidance": spec.advisory_guidance,
    }


def get_all_engine_docs() -> list[dict[str, Any]]:
    """Retrieve structured educational documentation for all registered engines."""
    return [
        {
            "name": spec.name,
            "title": spec.title,
            "category": spec.category.value,
            "studio_tab": spec.studio_tab or "",
            "cli_command": spec.cli_command,
            "aliases": spec.aliases,
            "description": spec.description,
            "logic_documentation": spec.logic_documentation,
            "worldbuilding_relevance": spec.worldbuilding_relevance,
            "storytelling_relevance": spec.storytelling_relevance,
            "writing_relevance": spec.writing_relevance,
            "advisory_guidance": spec.advisory_guidance,
        }
        for spec in _ENGINES.values()
    ]


def format_engine_doc(spec_or_name: EngineSpec | str) -> str:
    """Formats an engine's educational documentation for terminal CLI display."""
    if isinstance(spec_or_name, str):
        engine_obj = get_engine(spec_or_name)
        if not engine_obj:
            return f"No documentation available for engine: '{spec_or_name}'"
        spec = engine_obj
    else:
        spec = spec_or_name

    doc = [
        "══════════════════════════════════════════════════════════════════════════════",
        f" 🏛️  ARS ARCANUM CRAFT ENGINE: {spec.title.upper()}",
        f"     Category: [{spec.category.value.upper()}]  •  Command: 'arcanum {spec.cli_command}'",
        "══════════════════════════════════════════════════════════════════════════════",
        "\n📖 Overview:",
        f"   {spec.description}",
        "\n⚙️ Engine Logic & Scientific / Structural Foundations:",
        f"   {spec.logic_documentation}",
        "\n🌍 Worldbuilding Relevance:",
        f"   {spec.worldbuilding_relevance}",
        "\n📐 Storytelling & Narrative Architecture Relevance:",
        f"   {spec.storytelling_relevance}",
        "\n✍️ Prose Writing & Editorial Relevance:",
        f"   {spec.writing_relevance}",
    ]
    if spec.advisory_guidance:
        doc.append("\n💡 Advisory Mechanics & Creative Freedom Resolution Pathways:")
        doc.append("   (The system never forces conformity. All checks provide multiple creative choices:)")
        for idx, adv in enumerate(spec.advisory_guidance, 1):
            doc.append(f"\n   [{idx}] Pattern: {adv.get('pattern', 'Unconventional Choice')}")
            doc.append(f"       • Option A (Hard Realism): {adv.get('option_a', 'Standard convention')}")
            doc.append(f"       • Option B (Speculative Trope): {adv.get('option_b', 'In-world arcane/sci-fi grounding')}")
            doc.append(f"       • Option C (Author Sovereignty): {adv.get('option_c', 'Authorial creative freedom')}")
    doc.append("\n══════════════════════════════════════════════════════════════════════════════\n")
    return "\n".join(doc)



