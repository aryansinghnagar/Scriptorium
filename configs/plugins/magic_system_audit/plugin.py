#!/usr/bin/env python3
"""
Hard Magic System & Arcane Consistency Plugin for Ars Arcanum
=============================================================
Enforces Sanderson's First & Second Laws of Magic:
1. Limitations > Powers (Every ability must have a defined cost, limit, or weakness).
2. Predictable Cause and Effect.
"""

import re
from typing import Any


def hook_validate_entity(entity: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = []
    name = entity.get("name", "")
    content = entity.get("content", "")
    path = entity.get("path", "")

    # Only audit magic technology or magic discipline entries
    is_magic = "Magic" in path or "Spell" in path or "Arcane" in path or "Power" in path or "magic" in name.lower()
    if not is_magic and not re.search(r"\b(spell|mana|aether|arcane|sorcery|enchantment|incantation)\b", content, re.IGNORECASE):
        return diagnostics

    # 1. Limitation / Cost Check (Sanderson's Second Law)
    has_cost = bool(re.search(r"(cost|limitation|drawback|price|exhaustion|toll|reagent|cooldown|consequence|weakness)", content, re.IGNORECASE))
    if not has_cost:
        diagnostics.append({
            "severity": "warning",
            "message": f"Arcane entity '{name}' describes magical mechanics but defines no explicit Cost, Limitation, or Drawback (Sanderson's Second Law).",
            "target": name,
            "details": {"rule": "sandersons_second_law"},
        })

    # 2. Source / Conservation Check
    has_source = bool(re.search(r"(source|origin|conduit|focus|catalyst|reservoir|ambient|leylines|mana|aether)", content, re.IGNORECASE))
    if not has_source:
        diagnostics.append({
            "severity": "info",
            "message": f"Arcane entity '{name}' does not explicitly define its energy source or catalytic mechanism.",
            "target": name,
        })

    return diagnostics


def hook_validate_manuscript(manuscript: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    """Audits manuscript chapters for unexplained spontaneous magic resolution."""
    diagnostics = []
    chapters = manuscript.get("chapters", [])

    for ch in chapters:
        content = ch.get("content", "")
        title = ch.get("title", "")

        # Check for ungrounded miracle / deus ex machina tropes
        if re.search(r"\b(suddenly\s+discovered\s+a\s+new\s+power|miraculously\s+unlocked|burst\s+of\s+unlimited\s+power)\b", content, re.IGNORECASE):
            diagnostics.append({
                "severity": "warning",
                "message": f"Chapter '{title}' contains phrasing indicative of unheralded magical escalation ('burst of unlimited power'). Ensure foreshadowing exists.",
                "target": title,
            })

    return diagnostics
