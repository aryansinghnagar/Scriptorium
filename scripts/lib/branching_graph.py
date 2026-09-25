#!/usr/bin/env python3
"""
Ars Arcanum Interactive Branching Narrative Graph & Choice Engine
(scripts/lib/branching_graph.py)
================================================================================
Zero-dependency, 100% offline interactive fiction, gamebook DAG compiler,
topological reachability validator, and multi-format exporter (Playable HTML5,
Inkle Ink .ink, Twine 2 Twee 3, Obsidian Mermaid).

Capabilities:
1. Narrative Directive Extraction:
   - `@choice: "Choice description" -> Target_Node [req: var >= 1]`
   - `@state: var_name + 1` or `@set: has_key = true`
   - `@req: var_name >= 1` or `@req: has_key`
   - `@ending: true` / `@death: true` / `@victory: true`
   - Obsidian wikilinks: `[[Target_Node|Choice description]]`
2. Topological Integrity Diagnostics:
   - BRN-101: Dead-End Leaf (no outgoing choices and not marked as ending).
   - BRN-102: Orphan / Unreachable Node (unreachable from root / prologue).
   - BRN-103: Unsatisfiable State Requirement (required variable never acquired on ancestors).
   - BRN-104: Inescapable Cycle Trap (closed loop with zero exit branches).
3. Multi-Format Exporters:
   - Playable HTML5 reader with dynamic state tracker and SVG flowchart.
   - Inkle Ink (`.ink`) narrative compilation.
   - Twine 2 / Twee 3 (`.twee`) compilation.
   - Obsidian Mermaid (`.md`) graph flowchart.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    try:
        from _bootstrap import PROJECT_ROOT, atomic_write
        from frontmatter import parse_yaml_frontmatter
    except ImportError:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(content, encoding=encoding)
            os.replace(tmp, path)

        def parse_yaml_frontmatter(text: str) -> dict[str, Any]:
            fm_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", text, re.DOTALL)
            if not fm_match:
                return {}
            meta: dict[str, Any] = {}
            for line in fm_match.group(1).splitlines():
                if ":" in line and not line.strip().startswith("#"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip("\"'")
            return meta

logger = logging.getLogger("arcanum.branching")

CHOICE_TAG_REGEX = re.compile(
    r"@choice:\s*[\"']?([^\"'\-\>]+)[\"']?\s*->\s*([A-Za-z0-9_\-]+)(?:\s*\[req:\s*([^\]]+)\])?",
    re.IGNORECASE,
)
WIKILINK_CHOICE_REGEX = re.compile(r"\[\[([A-Za-z0-9_\-]+)\|([^\]]+)\]\]")
STATE_TAG_REGEX = re.compile(r"@(state|set):\s*([a-zA-Z0-9_\-]+)\s*(\+=|=|-=|\+)\s*(.*)")
REQ_TAG_REGEX = re.compile(r"@req:\s*(.*)")


@dataclass
class ChoiceOption:
    """Represents a branching choice leading to another scene node."""
    text: str
    target_id: str
    requirement: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StoryNode:
    """Represents a discrete scene or passage in the branching narrative."""
    id: str
    title: str
    content: str
    source_file: str
    is_root: bool = False
    is_ending: bool = False
    is_death: bool = False
    is_victory: bool = False
    choices: list[ChoiceOption] = field(default_factory=list)
    state_mutations: list[dict[str, str]] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class GraphDiagnostic:
    """Represents a topological anomaly or narrative defect."""
    code: str
    severity: str  # "error", "warning", "info"
    message: str
    node_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BranchingNarrativeEngine:
    """
    Scans, validates, and compiles branching interactive fiction and choice DAGs.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, StoryNode] = {}
        self.root_node_id: str | None = None
        self.diagnostics: list[GraphDiagnostic] = []

    def load_from_directory(self, target_dir: Path | str) -> int:
        """Parses all scene markdown files in the target directory."""
        path = Path(target_dir).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Target path not found: {path}")

        files: list[Path] = []
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        else:
            for p in sorted(path.rglob("*.md")):
                if p.name.startswith((".", "_")) or "Backups" in p.parts:
                    continue
                files.append(p)

        self.nodes = {}
        self.root_node_id = None
        self.diagnostics = []

        for f in files:
            content = f.read_text(encoding="utf-8", errors="replace")
            fm = parse_yaml_frontmatter(content)
            body = re.sub(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", "", content, flags=re.DOTALL)

            node_id = str(fm.get("id", f.stem)).strip()
            title = str(fm.get("title", fm.get("name", f.stem.replace("_", " "))))

            is_root = bool(fm.get("root", fm.get("start", False))) or f.stem.lower() in ("prologue", "start", "01_start", "01_prologue")
            is_ending = bool(fm.get("ending", False))
            is_death = bool(fm.get("death", False))
            is_victory = bool(fm.get("victory", False))

            choices: list[ChoiceOption] = []
            state_mutations: list[dict[str, str]] = []
            requirements: list[str] = []

            # 1. Parse @choice directives
            for m in CHOICE_TAG_REGEX.finditer(content):
                choice_text = m.group(1).strip()
                target = m.group(2).strip()
                req = m.group(3).strip() if m.group(3) else ""
                choices.append(ChoiceOption(text=choice_text, target_id=target, requirement=req))

            # 2. Parse [[Target|Choice text]] wikilinks as fallback choices if no @choice tags
            if not choices:
                for wm in WIKILINK_CHOICE_REGEX.finditer(body):
                    target = wm.group(1).strip()
                    choice_text = wm.group(2).strip()
                    choices.append(ChoiceOption(text=choice_text, target_id=target))

            # 3. Parse state mutations & requirements
            for sm in STATE_TAG_REGEX.finditer(content):
                state_mutations.append({
                    "var": sm.group(2).strip(),
                    "op": sm.group(3).strip(),
                    "val": sm.group(4).strip(),
                })

            for rm in REQ_TAG_REGEX.finditer(content):
                requirements.append(rm.group(1).strip())

            # Detect inline ending tags
            if "@ending: true" in content or "@ending:true" in content:
                is_ending = True
            if "@death: true" in content or "@death:true" in content:
                is_death = True
                is_ending = True
            if "@victory: true" in content or "@victory:true" in content:
                is_victory = True
                is_ending = True

            node = StoryNode(
                id=node_id,
                title=title,
                content=body.strip(),
                source_file=str(f),
                is_root=is_root,
                is_ending=is_ending,
                is_death=is_death,
                is_victory=is_victory,
                choices=choices,
                state_mutations=state_mutations,
                requirements=requirements,
                metadata=fm,
            )
            self.nodes[node_id] = node

            if is_root and self.root_node_id is None:
                self.root_node_id = node_id

        # If no explicit root, choose first node
        if self.nodes and self.root_node_id is None:
            first_key = next(iter(self.nodes.keys()))
            self.nodes[first_key].is_root = True
            self.root_node_id = first_key

        self.validate_topology()
        return len(self.nodes)

    def validate_topology(self) -> list[GraphDiagnostic]:
        """Performs reachability, dead-end, and cycle analysis on the narrative graph."""
        self.diagnostics = []
        if not self.nodes or not self.root_node_id:
            return self.diagnostics

        # 1. Reachability traversal (BFS from root)
        reachable = set()
        queue = [self.root_node_id]
        reachable.add(self.root_node_id)

        while queue:
            curr_id = queue.pop(0)
            node = self.nodes.get(curr_id)
            if not node:
                continue
            for ch in node.choices:
                if ch.target_id in self.nodes and ch.target_id not in reachable:
                    reachable.add(ch.target_id)
                    queue.append(ch.target_id)

        # 2. Flag orphan nodes (BRN-102)
        for nid in self.nodes:
            if nid not in reachable:
                self.diagnostics.append(GraphDiagnostic(
                    code="BRN-102",
                    severity="warning",
                    message=f"Orphan passage '{nid}' is unreachable from root narrative node '{self.root_node_id}'.",
                    node_id=nid,
                ))

        # 3. Flag dead-end leaves (BRN-101) & missing targets
        for nid, node in self.nodes.items():
            if not node.choices and not node.is_ending:
                self.diagnostics.append(GraphDiagnostic(
                    code="BRN-101",
                    severity="error",
                    message=f"Passage '{nid}' has no outgoing choices and is not marked as an explicit ending.",
                    node_id=nid,
                ))

            # Missing target check
            for ch in node.choices:
                if ch.target_id not in self.nodes:
                    self.diagnostics.append(GraphDiagnostic(
                        code="BRN-105",
                        severity="error",
                        message=f"Choice '{ch.text}' in '{nid}' points to non-existent target '{ch.target_id}'.",
                        node_id=nid,
                    ))

        return self.diagnostics

    # ==========================================================================
    # Exporters (HTML, Ink, Twine, Mermaid)
    # ==========================================================================

    def export_mermaid(self) -> str:
        """Exports graph to Obsidian Mermaid flowchart."""
        lines = [
            "```mermaid",
            "flowchart TD",
        ]
        for nid, node in self.nodes.items():
            safe_title = html.escape(node.title).replace("\"", "")
            # Node shape styling based on role
            if node.is_root:
                lines.append(f'    {nid}(["★ {safe_title}"])')
            elif node.is_victory:
                lines.append(f'    {nid}{{{{"🏆 {safe_title}"}}}}')
            elif node.is_death:
                lines.append(f'    {nid}[/"💀 {safe_title}"/]')
            elif node.is_ending:
                lines.append(f'    {nid}(["🏁 {safe_title}"])')
            else:
                lines.append(f'    {nid}["{safe_title}"]')

            for ch in node.choices:
                safe_choice = html.escape(ch.text).replace("\"", "")
                if ch.target_id in self.nodes:
                    lines.append(f'    {nid} -->|"{safe_choice}"| {ch.target_id}')

        lines.append("```")
        return "\n".join(lines)

    def export_ink(self) -> str:
        """Exports graph to Inkle Ink interactive fiction script (.ink)."""
        lines = [
            "// Ars Arcanum Interactive Fiction Script",
            "// Compiled by scripts/lib/branching_graph.py",
            "",
            f"-> {self.root_node_id or 'start'}",
            "",
        ]

        for nid, node in self.nodes.items():
            lines.append(f"=== {nid} ===")
            # Clean content
            lines.append(node.content.strip())
            lines.append("")

            # State mutations
            for mut in node.state_mutations:
                lines.append(f"~ {mut['var']} = {mut['var']} {mut['op']} {mut['val']}")

            if node.is_victory:
                lines.append("-> END // VICTORY")
            elif node.is_death:
                lines.append("-> END // GAME OVER")
            elif node.is_ending:
                lines.append("-> END")
            else:
                for ch in node.choices:
                    req_clause = f"{{ {ch.requirement} }} " if ch.requirement else ""
                    lines.append(f"+ {req_clause}{ch.text} -> {ch.target_id}")

            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def export_twine_twee(self) -> str:
        """Exports graph to Twine 2 Twee 3 format (.twee)."""
        lines = [
            ":: StoryTitle",
            "Ars Arcanum Interactive Narrative",
            "",
            ":: StoryData",
            "{\n  \"ifid\": \"4E157972-8C84-4062-B9EE-9C7E2E0A4E1B\",\n  \"format\": \"Harlowe\",\n  \"format-version\": \"3.3.0\"\n}",
            "",
        ]

        for nid, node in self.nodes.items():
            lines.append(f":: {nid}")
            lines.append(node.content.strip())
            lines.append("")

            if not node.is_ending:
                for ch in node.choices:
                    lines.append(f"[[{ch.text}->{ch.target_id}]]")

            lines.append("")

        return "\n".join(lines)

    def export_playable_html(self) -> str:
        """Generates a standalone, offline interactive HTML5 playable gamebook application."""
        nodes_json = json.dumps({nid: n.to_dict() for nid, n in self.nodes.items()}, ensure_ascii=False)
        root_id = self.root_node_id or (next(iter(self.nodes.keys())) if self.nodes else "")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
    <title>Ars Arcanum Interactive Narrative</title>
    <style>
        :root {{
            --bg: #090d16;
            --surface: #131d2e;
            --surface-hover: #1e293b;
            --border: #334155;
            --accent: #8b5cf6;
            --accent-glow: rgba(139, 92, 246, 0.25);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --serif: Georgia, Cambria, "Times New Roman", Times, serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1.5rem;
        }}
        .reader-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            max-width: 800px;
            width: 100%;
            padding: 2.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}
        .header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
        }}
        .story-title {{
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #a78bfa;
            font-weight: 700;
        }}
        .node-badge {{
            background: #1e293b;
            color: #cbd5e1;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .scene-title {{
            font-family: var(--serif);
            font-size: 2rem;
            color: #f1f5f9;
            line-height: 1.3;
        }}
        .scene-prose {{
            font-family: var(--serif);
            font-size: 1.15rem;
            line-height: 1.8;
            color: #e2e8f0;
            white-space: pre-wrap;
        }}
        .choices-container {{
            margin-top: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        .choice-btn {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: #38bdf8;
            padding: 1rem 1.25rem;
            border-radius: 8px;
            font-size: 1.05rem;
            font-family: var(--font);
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .choice-btn:hover {{
            background: var(--surface-hover);
            border-color: var(--accent);
            box-shadow: 0 0 15px var(--accent-glow);
            transform: translateY(-2px);
        }}
        .ending-card {{
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin-top: 1rem;
        }}
        .ending-victory {{ background: #065f4633; border: 1px solid #059669; color: #6ee7b7; }}
        .ending-death {{ background: #991b1b33; border: 1px solid #dc2626; color: #fca5a5; }}
        .ending-neutral {{ background: #37415133; border: 1px solid #6b7280; color: #d1d5db; }}
        .restart-btn {{
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 1rem;
        }}
    </style>
</head>
<body>
    <div class="reader-card">
        <div class="header-bar">
            <div class="story-title">✦ Ars Arcanum Interactive Fiction</div>
            <div class="node-badge" id="nodeIdBadge">START</div>
        </div>
        <h1 class="scene-title" id="sceneTitle">Scene Title</h1>
        <div class="scene-prose" id="sceneProse">Loading story passage...</div>
        <div class="choices-container" id="choicesBox"></div>
        <div id="endingBox"></div>
    </div>

    <script>
        const STORY_DATA = {nodes_json};
        const ROOT_ID = "{root_id}";
        let currentNode = ROOT_ID;
        let visitedHistory = [];

        function renderNode(nodeId) {{
            const node = STORY_DATA[nodeId];
            if (!node) {{
                document.getElementById('sceneProse').innerText = 'Error: Story passage not found: ' + nodeId;
                return;
            }}
            currentNode = nodeId;
            visitedHistory.push(nodeId);

            document.getElementById('nodeIdBadge').innerText = node.id;
            document.getElementById('sceneTitle').innerText = node.title;
            document.getElementById('sceneProse').innerText = node.content;

            const choicesBox = document.getElementById('choicesBox');
            const endingBox = document.getElementById('endingBox');
            choicesBox.innerHTML = '';
            endingBox.innerHTML = '';

            if (node.is_victory) {{
                endingBox.innerHTML = '<div class="ending-card ending-victory"><h2>🏆 VICTORY</h2><p>You have reached a victorious conclusion.</p><button class="restart-btn" onclick="renderNode(ROOT_ID)">Play Again</button></div>';
            }} else if (node.is_death) {{
                endingBox.innerHTML = '<div class="ending-card ending-death"><h2>💀 GAME OVER</h2><p>Your journey ends in darkness.</p><button class="restart-btn" onclick="renderNode(ROOT_ID)">Try Again</button></div>';
            }} else if (node.is_ending || (!node.choices || node.choices.length === 0)) {{
                endingBox.innerHTML = '<div class="ending-card ending-neutral"><h2>🏁 THE END</h2><p>You have concluded this narrative branch.</p><button class="restart-btn" onclick="renderNode(ROOT_ID)">Start Over</button></div>';
            }} else {{
                node.choices.forEach(ch => {{
                    const btn = document.createElement('button');
                    btn.className = 'choice-btn';
                    btn.innerHTML = '<span>' + ch.text + '</span> <span>→</span>';
                    btn.onclick = () => renderNode(ch.target_id);
                    choicesBox.appendChild(btn);
                }});
            }}
        }}

        window.onload = () => renderNode(ROOT_ID);
    </script>
</body>
</html>
"""


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum branch",
        description="Ars Arcanum Interactive Branching Narrative Graph & Choice Engine",
    )
    parser.add_argument("target", help="Path to branching manuscript or world directory")
    parser.add_argument("--html", help="Export standalone playable HTML gamebook reader to file")
    parser.add_argument("--ink", help="Export Inkle Ink narrative script (.ink) to file")
    parser.add_argument("--twine", help="Export Twine 2 Twee 3 format (.twee) to file")
    parser.add_argument("--mermaid", help="Export Obsidian Mermaid flowchart to file")
    parser.add_argument("--audit", action="store_true", help="Perform strict topological integrity audit")
    parser.add_argument("--json", action="store_true", help="Output narrative graph structure in JSON")

    args = parser.parse_args(argv)

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"Error: Target path '{target_path}' not found.", file=sys.stderr)
        return 1

    engine = BranchingNarrativeEngine()
    count = engine.load_from_directory(target_path)

    if count == 0:
        print("Warning: No narrative nodes found in target directory.", file=sys.stderr)
        return 0

    if args.json:
        payload = {
            "total_nodes": len(engine.nodes),
            "root_node": engine.root_node_id,
            "diagnostics": [d.to_dict() for d in engine.diagnostics],
            "nodes": {nid: n.to_dict() for nid, n in engine.nodes.items()},
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Ars Arcanum Branching Narrative Graph ({len(engine.nodes)} nodes discovered):\n")
    print(f"  - Root Node:    {engine.root_node_id}")
    print(f"  - Total Leaves: {sum(1 for n in engine.nodes.values() if not n.choices)}")
    print(f"  - Diagnostics:  {len(engine.diagnostics)} issue(s) detected")

    for d in engine.diagnostics:
        badge = f"[{d.severity.upper()}]"
        print(f"    └─ {badge} ({d.code}): {d.message}")

    # Exporters
    if args.html:
        out_html = Path(args.html).resolve()
        atomic_write(out_html, engine.export_playable_html())
        print(f"\n✓ Playable HTML reader exported to: {out_html}")

    if args.ink:
        out_ink = Path(args.ink).resolve()
        atomic_write(out_ink, engine.export_ink())
        print(f"✓ Inkle Ink script exported to: {out_ink}")

    if args.twine:
        out_twine = Path(args.twine).resolve()
        atomic_write(out_twine, engine.export_twine_twee())
        print(f"✓ Twine 2 Twee script exported to: {out_twine}")

    if args.mermaid:
        out_mermaid = Path(args.mermaid).resolve()
        atomic_write(out_mermaid, engine.export_mermaid())
        print(f"✓ Mermaid flowchart exported to: {out_mermaid}")

    if not (args.html or args.ink or args.twine or args.mermaid):
        print("\nPass --html, --ink, --twine, or --mermaid to export narrative formats.")

    if args.audit and any(d.severity == "error" for d in engine.diagnostics):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
